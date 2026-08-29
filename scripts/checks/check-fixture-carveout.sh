#!/usr/bin/env bash
# SC6 / REQ-OKF-CHK-003 (#233) — `audit-close` reports NO `okf:` finding under a fixture path,
# WHILE STILL REPORTING on non-fixture paths.
#
# THE SECOND CLAUSE IS THE WHOLE CHECK. "No fixture findings" alone is satisfied by the OKF
# walk not running at all — by a crash, a mis-typed path, an exception swallowed by the
# audit's defensive `except`. Asserting that the walk is still ALIVE somewhere is what
# distinguishes a working carve-out from a dead check, and it is REQ-CLI-029(b)'s empty-
# inspection rule applied to a suppression rather than to an enumeration.
#
# THE LIVENESS ARM USES `--no-exclude` AS ITS POSITIVE CONTROL rather than requiring a
# non-fixture finding to exist. Measured on plan-053 after the fix: fixture findings 25 -> 0
# and non-fixture findings 0 -> 0 — the bundle is genuinely clean off the fixture path, so
# "some non-fixture finding exists" is UNSATISFIABLE there and would make SC6 permanently
# false. Turning the exclusions OFF and requiring the findings to COME BACK proves the walk
# reaches those paths, which is the property the second clause is really about.
#
# EXIT  0 carve-out holds AND the walk is demonstrably live  ·  1 either fails  ·  2 could not run
CHECK_NAME=check-fixture-carveout
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
PLAN_DIR="$(ck_plan_dir "${1:-}")" || exit $?
ck_need uv
MANAGER="${TREE}/skills/yf-plan/scripts/plan_manager.py"
[ -f "${MANAGER}" ] || ck_inconclusive "no plan_manager.py at ${MANAGER}"
CK_RC=0

# The bundle must actually CARRY a fixture corpus, or this check certifies nothing.
FIXTURE_FILES="$(find "${PLAN_DIR}" -path '*/assets/fixtures/*' -name '*.md' 2>/dev/null | wc -l | tr -d ' ')"
if [ "${FIXTURE_FILES}" -lt 1 ]; then
  ck_inconclusive "${PLAN_DIR} carries no assets/fixtures/**/*.md — nothing to carve out, this run would certify vacuously"
fi

AUDIT_JSON="$( (cd "${TREE}" && uv run "${MANAGER}" audit-close "${PLAN_DIR}" --json 2>/dev/null) )"
[ -n "${AUDIT_JSON}" ] || ck_inconclusive "audit-close produced no JSON"

count_okf() {   # $1 = "fixture" | "nonfixture"
  printf '%s' "${AUDIT_JSON}" | uv run python3 -c '
import json,sys
want=sys.argv[1]
d=json.load(sys.stdin)
n=0
for f in d.get("findings",[]):
    it=f.get("item","")
    if not it.startswith("okf:"): continue
    isfx = "assets/fixtures/" in it or "okf-migration-samples/" in it
    if (want=="fixture") == isfx: n+=1
print(n)
' "$1"
}

FX="$(count_okf fixture)"
[ -n "${FX}" ] || ck_inconclusive "could not parse the audit JSON"

# --- CLAUSE 1: no `okf:` finding under a fixture path -------------------------------
if [ "${FX}" -ne 0 ]; then
  ck_fail "audit-close reports ${FX} \`okf:\` finding(s) under a fixture path — the §3b carve-out is not reaching the audit walk (#233)"
fi

# --- CLAUSE 2: the walk is LIVE — turn the exclusions off and the findings return ----
# This is the positive control. Without it, clause 1 passes on an audit whose OKF walk
# crashed, was mis-pointed, or was removed.
OKF="${TREE}/skills/yf-plan/scripts/okf.py"
[ -f "${OKF}" ] || ck_inconclusive "no vendored okf.py at ${OKF}"
UNEXCLUDED="$( (cd "${TREE}" && uv run --with pyyaml "${OKF}" check "${PLAN_DIR}" --skill yf-plan --no-exclude --json 2>/dev/null) \
                | grep -c '"level": "error"' )"
EXCLUDED="$( (cd "${TREE}" && uv run --with pyyaml "${OKF}" check "${PLAN_DIR}" --skill yf-plan --json 2>/dev/null) \
                | grep -c '"level": "error"' )"

if [ "${UNEXCLUDED}" -le "${EXCLUDED}" ]; then
  ck_fail "--no-exclude produced ${UNEXCLUDED} error finding(s) vs ${EXCLUDED} excluded — the exclusions suppress NOTHING, so clause 1 above is vacuous"
fi

ck_done "no \`okf:\` finding under a fixture path (${FIXTURE_FILES} fixture file(s) present); the walk is live — --no-exclude restores ${UNEXCLUDED} error(s) vs ${EXCLUDED}"
