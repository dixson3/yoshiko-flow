# yoshikoflow.sh — provisioning runbook

The live site runs on **S3 (private) + CloudFront (OAC) + ACM + Route53**, all in the AWS
account that owns the `yoshikoflow.sh` public hosted zone (account `534185824505`, zone
`Z0201468FY30AYTNQWIO`). This runbook documents the gated, billable provisioning and its
teardown inverse. The mechanics live in [`scripts/provision_aws.sh`](../scripts/provision_aws.sh)
(idempotent, check-before-create); this doc is the human-facing companion.

## Prerequisites

- `awscli` v2 and `jq` installed.
- AWS credentials with rights to S3, CloudFront, ACM (us-east-1), and Route53, for the
  account that owns the `yoshikoflow.sh` public hosted zone.
- Account-specific config exported in the environment (never committed) — at minimum
  `YOSHIKOFLOW_SITE_DOMAIN` and `YOSHIKOFLOW_HOSTED_ZONE_ID` (the Route53 zone id). Locally
  these are set in the repo's gitignored `web/.envrc` (direnv, copied from
  [`.envrc.example`](../.envrc.example)); the canonical copies live as **GitHub repo secrets**.
  Optional overrides: `AWS_REGION`, `AWS_PROFILE`.
- The go-live capability gate released (this creates **billable** infrastructure).

## What gets created

| # | Resource | Notes |
|:--|:---------|:------|
| 1 | S3 bucket `yoshikoflow.sh` | **private** — public access fully blocked, no website hosting |
| 2 | CloudFront Origin Access Control + bucket policy | only the distribution can read the bucket |
| 3 | ACM certificate (us-east-1) | DNS-validated; CloudFront reads certs **only** from us-east-1 |
| 4 | CloudFront Function `yoshikoflow-index-rewrite` | viewer-request; rewrites pretty URLs to `/index.html` |
| 5 | CloudFront distribution | OAC S3 origin, short-TTL `/install.sh` behavior, 403/404 -> `/404.html` |
| 6 | Route53 A/ALIAS `yoshikoflow.sh` | points at the distribution |

Captured ids are persisted to `.aws-provision-state.json` (gitignored). Re-running is safe:
each resource is looked up and reused, so no second certificate or duplicate distribution is
ever created. At the end the script prints the CloudFront distribution id to set as
`YOSHIKOFLOW_CF_DISTRIBUTION` (local `.envrc` + `gh secret set YOSHIKOFLOW_CF_DISTRIBUTION …`) —
the Makefile and CI read it from the environment.

## Run it

```bash
cd web
make provision      # == ./scripts/provision_aws.sh
```

The certificate-validation wait is bounded (`CERT_WAIT_TIMEOUT`, default 1800s). If it times
out, fix the Route53 validation CNAME and re-run — the script resumes idempotently.

After provisioning, publish content:

```bash
make deploy         # s3_upload (site) + sync_installer (install.sh w/ short TTL) + invalidate
```

The distribution can take several minutes to finish deploying before the domain serves.

## Verify

```bash
curl -I https://yoshikoflow.sh/                       # 200 over HTTPS
curl -I https://yoshikoflow.sh/install/               # 200 (pretty-URL rewrite works)
curl -sI https://yoshikoflow.sh/does-not-exist        # 404 served from /404.html
curl --proto '=https' --tlsv1.2 -LsSf https://yoshikoflow.sh/install.sh | head
```

## Why the CloudFront Function is required

A private bucket read via OAC is **not** an S3 *website* endpoint, so it does not append
`index.html` to directory requests — only CloudFront's default-root-object rewrites `/`.
Because the site uses pretty, directory-style URLs (`/install/`), the viewer-request
Function ([`scripts/aws/index-rewrite.js`](../scripts/aws/index-rewrite.js)) appends
`index.html` to slash-terminated and extension-less paths. `/install.sh` (has an extension)
passes through untouched.

## Teardown / rollback

The provisioning is create-only; there is no automated destroy. To remove the stack (inverse
order of creation), for a distribution id `DID`, cert arn `CARN`:

```bash
# 1. Route53: delete the A/ALIAS (re-run change-resource-record-sets with Action=DELETE)
# 2. Disable then delete the distribution (must be disabled + fully deployed first):
aws cloudfront get-distribution-config --id DID          # capture ETag + config
# ...set Enabled=false, update-distribution --id DID --if-match ETag --distribution-config ...
# ...wait for Deployed, then:
aws cloudfront delete-distribution --id DID --if-match <new-etag>
# 3. Delete the CloudFront Function:
aws cloudfront delete-function --name yoshikoflow-index-rewrite --if-match <etag>
# 4. Delete the ACM certificate:
aws acm delete-certificate --certificate-arn CARN --region us-east-1
# 5. Empty + delete the bucket:
aws s3 rm s3://yoshikoflow.sh --recursive
aws s3api delete-bucket --bucket yoshikoflow.sh
# 6. Remove the ACM validation CNAME from Route53 (Action=DELETE).
```

Then delete the local `.aws-provision-state.json` and unset `YOSHIKOFLOW_CF_DISTRIBUTION`
(remove it from `.envrc` and `gh secret delete YOSHIKOFLOW_CF_DISTRIBUTION`).
