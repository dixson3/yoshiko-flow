#!/usr/bin/env bash
#
# provision_aws.sh — provision the yoshikoflow.sh static-site stack on AWS.
#
# Creates (idempotently, check-before-create per resource):
#   1. a PRIVATE S3 bucket `yoshikoflow.sh` (no public access, no website hosting)
#   2. a CloudFront Origin Access Control (OAC) + bucket policy granting only the
#      distribution read access
#   3. an ACM certificate in us-east-1 for yoshikoflow.sh (DNS-validated), the Route53
#      validation record, and a bounded wait for validation
#   4. a CloudFront viewer-request Function that rewrites pretty URLs to /index.html
#   5. a CloudFront distribution: OAC S3 origin, the Function on the default behavior, a
#      short-TTL behavior for /install.sh, and custom 403/404 -> /404.html error responses
#   6. a Route53 A/ALIAS record yoshikoflow.sh -> the distribution
#
# It is idempotent: every resource is looked up first and reused; captured ids are persisted
# to .aws-provision-state.json, so a re-run never requests a second certificate or builds a
# duplicate distribution. The distribution id is printed at the end for you to set as
# YOSHIKOFLOW_CF_DISTRIBUTION (local .envrc + GitHub repo secret) — the Makefile reads it there.
#
# THIS IS A BILLABLE OPERATION. It is gated behind the plan's go-live capability gate and is
# normally invoked as `make provision`. Nothing here is destructive; see
# docs/provisioning-runbook.md for the teardown/rollback inverse.
#
# Requires: awscli v2, jq. Uses the caller's default AWS credentials/profile.

set -euo pipefail

# ---- configuration ----------------------------------------------------------------------
# Account-specific values come from the environment — NEVER hardcoded in the repo. Locally
# they are exported from the repo's gitignored .envrc (direnv); the canonical copy lives as a
# GitHub repo secret (YOSHIKOFLOW_HOSTED_ZONE_ID).
DOMAIN="${YOSHIKOFLOW_SITE_DOMAIN:?set YOSHIKOFLOW_SITE_DOMAIN (the bare site host, e.g. yoshikoflow.sh) in .envrc or the GitHub repo secret}"
BUCKET="${DOMAIN}"
REGION="${AWS_REGION:-us-east-1}"  # bucket + everything else; ACM for CloudFront MUST be us-east-1
# Route53 public hosted-zone id for the parent domain — an account-specific reference, so it
# is required from the environment (local .envrc / GitHub repo secret YOSHIKOFLOW_HOSTED_ZONE_ID).
HOSTED_ZONE_ID="${YOSHIKOFLOW_HOSTED_ZONE_ID:?set YOSHIKOFLOW_HOSTED_ZONE_ID (the Route53 zone id) in .envrc or the GitHub repo secret}"
CF_ALIAS_ZONE_ID="Z2FDTNDATAQYW2"  # fixed, global CloudFront alias hosted-zone id (not account-specific)
OAC_NAME="yoshikoflow-sh-oac"
FUNCTION_NAME="yoshikoflow-index-rewrite"
CERT_WAIT_TIMEOUT="${CERT_WAIT_TIMEOUT:-1800}"   # seconds to wait for cert validation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
STATE_FILE="${WEB_DIR}/.aws-provision-state.json"
FUNCTION_CODE="${SCRIPT_DIR}/aws/index-rewrite.js"

log()  { printf '\033[1;36m==>\033[0m %s\n' "$*" >&2; }
warn() { printf '\033[1;33mWARN\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31mERROR\033[0m %s\n' "$*" >&2; exit 1; }

# state helpers (a flat JSON object of captured ids)
[ -f "${STATE_FILE}" ] || echo '{}' > "${STATE_FILE}"
state_get() { jq -r --arg k "$1" '.[$k] // empty' "${STATE_FILE}"; }
state_set() {
  local tmp; tmp="$(mktemp)"
  jq --arg k "$1" --arg v "$2" '.[$k]=$v' "${STATE_FILE}" > "${tmp}" && mv -f "${tmp}" "${STATE_FILE}"
}

command -v aws >/dev/null || die "awscli not found"
command -v jq  >/dev/null || die "jq not found"
[ -f "${FUNCTION_CODE}" ] || die "missing CloudFront function code: ${FUNCTION_CODE}"

log "AWS identity: $(aws sts get-caller-identity --query 'Arn' --output text)"

# ---- 1. private S3 bucket ---------------------------------------------------------------
if aws s3api head-bucket --bucket "${BUCKET}" 2>/dev/null; then
  log "bucket ${BUCKET} already exists — reusing"
else
  log "creating private bucket ${BUCKET}"
  # us-east-1 create-bucket must NOT pass a LocationConstraint.
  aws s3api create-bucket --bucket "${BUCKET}" --region "${REGION}" >/dev/null
fi
aws s3api put-public-access-block --bucket "${BUCKET}" \
  --public-access-block-configuration \
  BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true >/dev/null
aws s3api put-bucket-versioning --bucket "${BUCKET}" \
  --versioning-configuration Status=Enabled >/dev/null || true

# ---- 2. Origin Access Control -----------------------------------------------------------
OAC_ID="$(aws cloudfront list-origin-access-controls \
  --query "OriginAccessControlList.Items[?Name=='${OAC_NAME}'].Id | [0]" --output text 2>/dev/null || true)"
if [ -z "${OAC_ID}" ] || [ "${OAC_ID}" = "None" ]; then
  log "creating Origin Access Control ${OAC_NAME}"
  OAC_ID="$(aws cloudfront create-origin-access-control --origin-access-control-config \
    "Name=${OAC_NAME},Description=yoshiko-flow site OAC,SigningProtocol=sigv4,SigningBehavior=always,OriginAccessControlOriginType=s3" \
    --query 'OriginAccessControl.Id' --output text)"
else
  log "OAC ${OAC_NAME} already exists (${OAC_ID}) — reusing"
fi
state_set oac_id "${OAC_ID}"

# ---- 3. ACM certificate (us-east-1, DNS validation) -------------------------------------
CERT_ARN="$(state_get cert_arn)"
if [ -z "${CERT_ARN}" ]; then
  CERT_ARN="$(aws acm list-certificates --region "${REGION}" \
    --query "CertificateSummaryList[?DomainName=='${DOMAIN}'].CertificateArn | [0]" --output text 2>/dev/null || true)"
fi
if [ -z "${CERT_ARN}" ] || [ "${CERT_ARN}" = "None" ]; then
  log "requesting ACM certificate for ${DOMAIN} in ${REGION}"
  CERT_ARN="$(aws acm request-certificate --domain-name "${DOMAIN}" \
    --validation-method DNS --region "${REGION}" \
    --query 'CertificateArn' --output text)"
else
  log "ACM certificate exists (${CERT_ARN}) — reusing"
fi
state_set cert_arn "${CERT_ARN}"

# hard-check the cert is in us-east-1 (CloudFront reads certs only from us-east-1)
case "${CERT_ARN}" in
  arn:aws:acm:us-east-1:*) : ;;
  *) die "certificate ${CERT_ARN} is not in us-east-1; CloudFront requires us-east-1" ;;
esac

# upsert the DNS validation record (may take a moment to populate after request)
log "reading DNS validation record"
for _ in $(seq 1 30); do
  RR_JSON="$(aws acm describe-certificate --certificate-arn "${CERT_ARN}" --region "${REGION}" \
    --query 'Certificate.DomainValidationOptions[0].ResourceRecord' --output json 2>/dev/null || echo null)"
  [ "${RR_JSON}" != "null" ] && [ -n "${RR_JSON}" ] && break
  sleep 5
done
[ "${RR_JSON}" = "null" ] && die "ACM validation record not available after wait"
RR_NAME="$(echo "${RR_JSON}" | jq -r '.Name')"
RR_VALUE="$(echo "${RR_JSON}" | jq -r '.Value')"
log "upserting validation CNAME ${RR_NAME}"
aws route53 change-resource-record-sets --hosted-zone-id "${HOSTED_ZONE_ID}" --change-batch "$(cat <<JSON
{"Changes":[{"Action":"UPSERT","ResourceRecordSet":{
  "Name":"${RR_NAME}","Type":"CNAME","TTL":300,
  "ResourceRecords":[{"Value":"${RR_VALUE}"}]}}]}
JSON
)" >/dev/null

log "waiting for certificate validation (timeout ${CERT_WAIT_TIMEOUT}s)"
if ! timeout "${CERT_WAIT_TIMEOUT}" aws acm wait certificate-validated \
     --certificate-arn "${CERT_ARN}" --region "${REGION}"; then
  die "ACM certificate did not validate within ${CERT_WAIT_TIMEOUT}s. Check the Route53 CNAME (${RR_NAME}) and re-run — this step is idempotent."
fi
log "certificate validated"

# ---- 4. CloudFront viewer-request Function ----------------------------------------------
FUNCTION_ARN="$(aws cloudfront describe-function --name "${FUNCTION_NAME}" \
  --query 'FunctionSummary.FunctionMetadata.FunctionARN' --output text 2>/dev/null || true)"
if [ -z "${FUNCTION_ARN}" ] || [ "${FUNCTION_ARN}" = "None" ]; then
  log "creating CloudFront Function ${FUNCTION_NAME}"
  aws cloudfront create-function --name "${FUNCTION_NAME}" \
    --function-config "Comment=yoshiko-flow pretty-URL index rewrite,Runtime=cloudfront-js-2.0" \
    --function-code "fileb://${FUNCTION_CODE}" >/dev/null
else
  log "Function ${FUNCTION_NAME} exists — updating code to match source"
  ETAG="$(aws cloudfront describe-function --name "${FUNCTION_NAME}" --query 'ETag' --output text)"
  aws cloudfront update-function --name "${FUNCTION_NAME}" --if-match "${ETAG}" \
    --function-config "Comment=yoshiko-flow pretty-URL index rewrite,Runtime=cloudfront-js-2.0" \
    --function-code "fileb://${FUNCTION_CODE}" >/dev/null
fi
# publish the LIVE stage from the latest DEVELOPMENT etag
DEV_ETAG="$(aws cloudfront describe-function --name "${FUNCTION_NAME}" --query 'ETag' --output text)"
aws cloudfront publish-function --name "${FUNCTION_NAME}" --if-match "${DEV_ETAG}" >/dev/null
FUNCTION_ARN="$(aws cloudfront describe-function --name "${FUNCTION_NAME}" \
  --query 'FunctionSummary.FunctionMetadata.FunctionARN' --output text)"
state_set function_arn "${FUNCTION_ARN}"

# ---- 5. CloudFront distribution ---------------------------------------------------------
S3_ORIGIN_DOMAIN="${BUCKET}.s3.${REGION}.amazonaws.com"
DIST_ID="$(state_get distribution_id)"
if [ -n "${DIST_ID}" ] && aws cloudfront get-distribution --id "${DIST_ID}" >/dev/null 2>&1; then
  log "distribution ${DIST_ID} already exists — reusing (not recreating)"
else
  log "creating CloudFront distribution for ${DOMAIN}"
  CALLER_REF="yoshikoflow-sh-$(date +%s)"
  DIST_CONFIG="$(cat <<JSON
{
  "CallerReference": "${CALLER_REF}",
  "Aliases": {"Quantity": 1, "Items": ["${DOMAIN}"]},
  "DefaultRootObject": "index.html",
  "Origins": {"Quantity": 1, "Items": [{
    "Id": "s3-${BUCKET}",
    "DomainName": "${S3_ORIGIN_DOMAIN}",
    "OriginAccessControlId": "${OAC_ID}",
    "S3OriginConfig": {"OriginAccessIdentity": ""}
  }]},
  "DefaultCacheBehavior": {
    "TargetOriginId": "s3-${BUCKET}",
    "ViewerProtocolPolicy": "redirect-to-https",
    "Compress": true,
    "CachePolicyId": "658327ea-f89d-4fab-a63d-7e88639e58f6",
    "FunctionAssociations": {"Quantity": 1, "Items": [
      {"EventType": "viewer-request", "FunctionARN": "${FUNCTION_ARN}"}
    ]},
    "AllowedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"],
      "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]}}
  },
  "CacheBehaviors": {"Quantity": 1, "Items": [{
    "PathPattern": "/install.sh",
    "TargetOriginId": "s3-${BUCKET}",
    "ViewerProtocolPolicy": "redirect-to-https",
    "Compress": true,
    "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
    "AllowedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"],
      "CachedMethods": {"Quantity": 2, "Items": ["GET", "HEAD"]}}
  }]},
  "CustomErrorResponses": {"Quantity": 2, "Items": [
    {"ErrorCode": 403, "ResponsePagePath": "/404.html", "ResponseCode": "404", "ErrorCachingMinTTL": 60},
    {"ErrorCode": 404, "ResponsePagePath": "/404.html", "ResponseCode": "404", "ErrorCachingMinTTL": 60}
  ]},
  "Comment": "yoshikoflow.sh static site",
  "Enabled": true,
  "HttpVersion": "http2and3",
  "ViewerCertificate": {
    "ACMCertificateArn": "${CERT_ARN}",
    "SSLSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021"
  }
}
JSON
)"
  # CachePolicyId notes: 658327ea… = AWS managed "CachingOptimized"; 4135ea2d… = AWS
  # managed "CachingDisabled" (used for /install.sh — freshness handled by the short
  # Cache-Control we upload + explicit invalidation on each publish).
  CREATE_OUT="$(aws cloudfront create-distribution --distribution-config "${DIST_CONFIG}")"
  DIST_ID="$(echo "${CREATE_OUT}" | jq -r '.Distribution.Id')"
  state_set distribution_id "${DIST_ID}"
fi

DIST_DOMAIN="$(aws cloudfront get-distribution --id "${DIST_ID}" \
  --query 'Distribution.DomainName' --output text)"
DIST_ARN="$(aws cloudfront get-distribution --id "${DIST_ID}" \
  --query 'Distribution.ARN' --output text)"
state_set distribution_domain "${DIST_DOMAIN}"

# ---- 2b. bucket policy (now that we have the distribution ARN) --------------------------
log "applying bucket policy granting only distribution ${DIST_ID}"
aws s3api put-bucket-policy --bucket "${BUCKET}" --policy "$(cat <<JSON
{"Version":"2012-10-17","Statement":[{
  "Sid":"AllowCloudFrontServicePrincipalReadOnly",
  "Effect":"Allow",
  "Principal":{"Service":"cloudfront.amazonaws.com"},
  "Action":"s3:GetObject",
  "Resource":"arn:aws:s3:::${BUCKET}/*",
  "Condition":{"StringEquals":{"AWS:SourceArn":"${DIST_ARN}"}}
}]}
JSON
)" >/dev/null

# ---- 6. Route53 A/ALIAS -----------------------------------------------------------------
log "upserting A/ALIAS ${DOMAIN} -> ${DIST_DOMAIN}"
aws route53 change-resource-record-sets --hosted-zone-id "${HOSTED_ZONE_ID}" --change-batch "$(cat <<JSON
{"Changes":[{"Action":"UPSERT","ResourceRecordSet":{
  "Name":"${DOMAIN}","Type":"A",
  "AliasTarget":{"HostedZoneId":"${CF_ALIAS_ZONE_ID}","DNSName":"${DIST_DOMAIN}","EvaluateTargetHealth":false}}}]}
JSON
)" >/dev/null

log "provisioning complete."
log "  bucket:        ${BUCKET}"
log "  OAC:           ${OAC_ID}"
log "  certificate:   ${CERT_ARN}"
log "  function:      ${FUNCTION_ARN}"
log "  distribution:  ${DIST_ID} (${DIST_DOMAIN})"
log "  A/ALIAS:       ${DOMAIN}"
log ""
log "Set the distribution id so the Makefile + CI can invalidate CloudFront:"
log "  .envrc:      export YOSHIKOFLOW_CF_DISTRIBUTION=${DIST_ID}"
log "  repo secret: gh secret set YOSHIKOFLOW_CF_DISTRIBUTION --body ${DIST_ID}"
log ""
log "Next: \`make deploy\` to publish the site + install.sh. The distribution may take"
log "several minutes to finish deploying before ${DOMAIN} serves."
