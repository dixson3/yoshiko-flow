#!/usr/bin/env bash
# SC20 — every defect discovered but not fixed is filed upstream WITH ITS MEASUREMENT.
#
# A deferral with no measurement is indistinguishable from a guess, and it is the measurement
# that lets the next reader decide whether the deferral still holds.
CHECK_NAME=check-deferred-filed
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
PLAN_DIR="$(ck_plan_dir)"
DEF="${PLAN_DIR}/assets/deferred-defects.md"
CK_RC=0
[ -f "${DEF}" ] || { ck_fail "assets/deferred-defects.md does not exist — nothing records what was discovered and not fixed"; exit "${CK_RC}"; }
rows="$(grep -cE '^\| *D[0-9]' "${DEF}" 2>/dev/null || true)"
[ "${rows:-0}" -gt 0 ] || ck_inconclusive "deferred-defects.md declares no D-rows — a check over an empty set certifies vacuously"
while IFS= read -r line; do
  id="$(printf '%s' "${line}" | awk -F'|' '{gsub(/ /,"",$2); print $2}')"
  printf '%s' "${line}" | grep -qE '#[0-9]+' \
    || ck_fail "${id}: no upstream issue number — a discovered defect that is not filed is lost"
  printf '%s' "${line}" | grep -qiE 'measur|observ|exit [0-9]|[0-9]+ (file|site|occurrence)' \
    || ck_fail "${id}: no measurement recorded — a deferral without one is indistinguishable from a guess"
done < <(grep -E '^\| *D[0-9]' "${DEF}")
ck_done "every deferred defect is filed upstream with its measurement"
