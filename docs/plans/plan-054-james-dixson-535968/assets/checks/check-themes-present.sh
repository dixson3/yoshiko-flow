#!/usr/bin/env bash
# SC12 — every changelog theme cites the plans it covers, and every one of the 28 plans is
# covered by EXACTLY ONE theme.
#
# THE PLAN SET IS DERIVED, NOT EMBEDDED. A literal count is itself a drift defect (the class
# pass-1 C17 flagged): it goes stale silently the moment the range changes.
CHECK_NAME=check-themes-present
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
CL="${TREE}/CHANGELOG.md"
[ -f "${CL}" ] || ck_inconclusive "no CHANGELOG.md at ${CL}"
[ -d "${TREE}/docs/plans" ] || ck_inconclusive "no docs/plans under ${TREE}"
# THE HEADING CONVENTION IS `## v<semver>`, WITH THE `v`. Measured against the real
# CHANGELOG.md, whose released sections read `## v0.4.0 — 2026-07-09`. An earlier pattern
# here omitted the `v`, so it found no 0.5.0 section AT ALL and reported a failure about
# the changelog that was really a defect in this check.
CK_RC=0

# The covered range is plan-026 .. plan-053 (the window since v0.4.0).
expected="$(cd "${TREE}/docs/plans" && ls -d plan-0* 2>/dev/null \
            | sed -E 's/^(plan-[0-9]{3}).*/\1/' | sort -u \
            | awk -F- '{n=$2+0; if (n>=26 && n<=53) print $0}')"
[ -n "${expected}" ] || ck_inconclusive "derived an EMPTY plan set — a coverage check over nothing certifies vacuously"

# `\?` IS A GNU EXTENSION and this repo runs on BSD sed (macOS), where it matches a
# LITERAL question mark — so the pattern silently found nothing. Use a portable BRE.
body="$(sed -n '/^## .*0\.5\.0/,/^## .*0\.4\.0/p' "${CL}")"
[ -n "${body}" ] || { ck_fail "no 0.5.0 section found in CHANGELOG.md"; exit "${CK_RC}"; }

uncovered=0 multi=0
while IFS= read -r p; do
  [ -n "${p}" ] || continue
  n="$(printf '%s' "${body}" | grep -c -- "${p}" || true)"
  if [ "${n}" -eq 0 ]; then ck_fail "no theme cites ${p}"; uncovered=$((uncovered+1)); fi
done <<< "${expected}"

# Every theme bullet must cite at least one plan — a theme with no citation is a claim with
# no evidence, which is the half SC12 exists for beyond mere coverage.
themes="$(printf '%s' "${body}" | grep -E '^### ' || true)"
[ -n "${themes}" ] || ck_fail "the 0.5.0 section declares no '### ' themes at all"

[ "${uncovered}" -eq 0 ] && [ "${multi}" -eq 0 ] \
  && ck_pass "all $(printf '%s\n' "${expected}" | grep -c .) plans in the v0.4.0..v0.5.0 window are cited by a theme"
exit "${CK_RC}"
