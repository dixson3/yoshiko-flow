#!/usr/bin/env bash
# check-migration-dryrun.sh — the migration-apply gate's Test (plan-055).
#
# The gate it serves is a DECLARED DESTRUCTIVE LOCAL OPERATION, so this check exists to make
# "the operator reviewed the dry-run" mechanically checkable rather than attested.
#
# THREE-VALUED, and the third value is the point:
#   0  every `delete` entry is `owned-and-unmodified`, `undetermined` is empty, and `delete`
#      is NON-EMPTY
#   1  the evidence says something bad: a `delete` entry that is not `owned-and-unmodified`,
#      a NON-EMPTY `undetermined`, or an EMPTY `delete` set
#   2  INCONCLUSIVE — the artifact is missing or unparseable, i.e. the evidence COULD NOT BE
#      READ AT ALL
#
# 1 vs 2 are different facts and collapsing them was the defect this spelling fixes: "the
# dry-run says a foreign directory is queued for deletion" and "there is no dry-run" are not
# the same finding, and only the first is a statement about the migration.
#
# THE EMPTY-DELETE-SET FAILURE IS DELIBERATE. A remover that silently found nothing would
# otherwise present as a green gate — vacuous certification, the same class as a `cargo test`
# filter matching zero tests. plan-055 EXP-007 measured 76 of 76 live deployed copies
# classifying `owned-and-unmodified`, so on a correctly built plan the set is non-empty and this
# arm does not fire spuriously.
#
# USAGE: check-migration-dryrun.sh <path-to-migration-dryrun.json>
CHECK_NAME=check-migration-dryrun
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

ARTIFACT="${1:-}"
[ -n "${ARTIFACT}" ] || ck_inconclusive "usage: check-migration-dryrun.sh <migration-dryrun.json>"
[ -f "${ARTIFACT}" ]  || ck_inconclusive "no dry-run artifact at ${ARTIFACT} — the evidence could not be read"
ck_need jq
jq -e . "${ARTIFACT}" >/dev/null 2>&1 || ck_inconclusive "${ARTIFACT} is not parseable JSON"

# The three keys are REQUIRED. A schema that declares no `undetermined` cannot express the
# finding this gate is contracted to fail on, so an absent key is INCONCLUSIVE, never a pass.
for key in delete kept undetermined; do
  jq -e "has(\"${key}\")" "${ARTIFACT}" >/dev/null 2>&1 \
    || ck_inconclusive "${ARTIFACT} has no \`${key}\` key — wrong schema; cannot judge the delete set"
  jq -e "(.${key} | type) == \"array\"" "${ARTIFACT}" >/dev/null 2>&1 \
    || ck_inconclusive "\`${key}\` is not an array in ${ARTIFACT}"
done

CK_RC=0

n_delete="$(jq '.delete | length' "${ARTIFACT}")"
if [ "${n_delete}" -eq 0 ]; then
  ck_fail "the \`delete\` set is EMPTY — a remover that found nothing must not present as a green gate"
fi

bad="$(jq -r '[.delete[] | select(.outcome != "owned-and-unmodified")] | .[] | "\(.path) [\(.outcome)]"' "${ARTIFACT}")"
if [ -n "${bad}" ]; then
  ck_fail "a \`delete\` entry is not \`owned-and-unmodified\`:"
  printf '  %s\n' ${bad} >&2
fi

n_undet="$(jq '.undetermined | length' "${ARTIFACT}")"
if [ "${n_undet}" -ne 0 ]; then
  ck_fail "\`undetermined\` is non-empty (${n_undet}) — an unjudgeable directory blocks the apply:"
  jq -r '.undetermined[] | "  \(.path): \(.reason)"' "${ARTIFACT}" >&2
fi

# Advisory, never a failure: D-2f's divergence flag. A kept directory shadowing a shared-root
# skill is exactly the hazard the migration removes, but keeping it is still the correct act.
shadow="$(jq -r '[.kept[]? | select(.shadows_shared_root == true)] | length' "${ARTIFACT}")"
if [ "${shadow}" -ne 0 ]; then
  echo "${CHECK_NAME}: NOTE — ${shadow} kept director(y/ies) shadow a shared-root skill (D-2f); review each:" >&2
  jq -r '.kept[]? | select(.shadows_shared_root == true) | "  \(.path) [\(.outcome)] \(.reason)"' "${ARTIFACT}" >&2
fi

ck_done "${n_delete} director(y/ies) queued for deletion, all \`owned-and-unmodified\`; \`undetermined\` empty"
