#!/usr/bin/env bash
# SC30 — every criterion command naming an assets/ path resolves to a file that exists.
#
# THE DIFF IS DIRECTIONAL — referenced ⊆ present, NEVER symmetric. An added criterion must not
# be able to outrun its script, but a deliberately-unreferenced fixture is not a defect and a
# symmetric diff would fail on one. Bare directory refs and controls.txt are excluded: neither
# is a script.
CHECK_NAME=check-criteria-scripts-exist
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
PLAN_DIR="$(ck_plan_dir)"
PLAN_MD="${PLAN_DIR}/plan.md"
[ -f "${PLAN_MD}" ] || ck_inconclusive "no plan.md at ${PLAN_MD}"
CK_RC=0

referenced="$(grep -oE 'assets/(checks|fixtures)/[A-Za-z0-9._-]+\.sh' "${PLAN_MD}" | sort -u)"
[ -n "${referenced}" ] || ck_inconclusive "the derivation matched no assets/ script reference in plan.md — a check over an empty set certifies vacuously"

missing=0
while IFS= read -r rel; do
  [ -n "${rel}" ] || continue
  if [ ! -f "${PLAN_DIR}/${rel}" ]; then
    ck_fail "referenced but absent: ${rel}"
    missing=$((missing + 1))
  fi
done <<< "${referenced}"
[ "${missing}" -eq 0 ] && ck_pass "all $(printf '%s\n' "${referenced}" | grep -c .) referenced assets/ script(s) exist"
exit "${CK_RC}"
