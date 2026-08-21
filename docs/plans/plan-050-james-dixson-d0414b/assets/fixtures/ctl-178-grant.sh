#!/usr/bin/env bash
# ctl-178-grant — REQ-CLI-025 / #178. SC9.
#
# A FIXTURE per Issue 0.2's definition. The asserted behaviour: the grant round-trip REJECTS
# plan-048's ACTUAL recorded grant with the `#172` close omitted, and ACCEPTS the amended one.
#
# THIS IS A REAL RECORDED FAILURE, NOT A SYNTHETIC ONE. plan-048 halted its own reconcile on
# exactly this: the grant was hand-derived from the Upstream Issues table, `#172`'s close was
# missed, and the omission surfaced only at `verify-reconcile` — after the outward-facing
# writes had already begun. The amendment that repaired it is still on disk and names the
# cause: "Its omission from the original list was an oversight in THIS FILE, not a decision to
# withhold." The fixture replays the pre-amendment text verbatim, sliced from the real file at
# authoring time.
#
# THE CONTRAST ARM IS MANDATORY. Without it the fixture is satisfied by a checker that rejects
# EVERYTHING — a grant generator that never approves is not a generator.
#
# Against the unfixed tree there is no `grant` verb, so this is RED.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
PM="${YF_TREE}/skills/yf-plan/scripts/plan_manager.py"
BUNDLE="${YF_TREE}/docs/plans/plan-048-james-dixson-ed68a5"
OMITTED="${HERE}/corpus/ctl-178-grant-omitted.txt"
AMENDED="${HERE}/corpus/ctl-178-grant-amended.txt"

[ -f "${PM}" ]      || { echo "ctl-178: HARNESS — no plan_manager at ${PM}" >&2; exit 2; }
[ -d "${BUNDLE}" ]  || { echo "ctl-178: HARNESS — no plan-048 bundle at ${BUNDLE}" >&2; exit 2; }
[ -f "${OMITTED}" ] || { echo "ctl-178: HARNESS — no recorded grant at ${OMITTED}" >&2; exit 2; }
[ -f "${AMENDED}" ] || { echo "ctl-178: HARNESS — no amended grant at ${AMENDED}" >&2; exit 2; }

# GUARD THE GUARD, on the corpus itself: the two texts must differ in the way the control
# claims, or every assertion below is theatre.
if grep -q '#172' "${OMITTED}"; then
  echo "ctl-178: VACUOUS — the 'omitted' grant names #172; it is not the pre-amendment text" >&2
  exit 2
fi
if ! grep -q '#172' "${AMENDED}"; then
  echo "ctl-178: VACUOUS — the 'amended' grant does not name #172" >&2
  exit 2
fi

run_check() {
  ( cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${PM}" grant "${BUNDLE}" --check "$1" --json 2>&1 )
}

fail=0

# ---- arm 1: the omitted grant must be REJECTED, naming #172's close --------------------
out="$( run_check "${OMITTED}" )"; rc=$?
if [ "${rc}" -eq 0 ]; then
  echo "ctl-178: the round-trip ACCEPTED plan-048's grant with #172's close omitted." >&2
  echo "ctl-178: that is the exact defect #178 was filed for, and the exact grant that" >&2
  echo "ctl-178: halted plan-048's own reconcile." >&2
  fail=1
fi
if ! printf '%s' "${out}" | python3 -c '
import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(1)
u = d.get("uncovered") or []
sys.exit(0 if any(str(x.get("issue")) == "172" and x.get("kind") == "close" for x in u) else 1)
' 2>/dev/null; then
  echo "ctl-178: the verdict does not name #172's CLOSE as uncovered." >&2
  echo "ctl-178: coverage must be judged PER ACTION — plan-048's omission was a close on an" >&2
  echo "ctl-178: issue the grant already mentioned, which a per-ISSUE check would pass." >&2
  printf '%s' "${out}" | head -c 400 | sed 's/^/ctl-178:   /' >&2
  fail=1
fi

# ---- arm 2: the amended grant must be ACCEPTED ----------------------------------------
out2="$( run_check "${AMENDED}" )"; rc2=$?
if [ "${rc2}" -ne 0 ]; then
  echo "ctl-178: the round-trip REJECTED plan-048's AMENDED grant (exit ${rc2})." >&2
  echo "ctl-178: a generator that never approves is not a generator — this arm is what" >&2
  echo "ctl-178: stops arm 1 from being satisfied by a checker that rejects everything." >&2
  printf '%s' "${out2}" | python3 -c '
import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    print(sys.stdin.read()[:400]); raise SystemExit
for u in (d.get("uncovered") or []):
    print(f"  uncovered: #{u.get(\"issue\")} {u.get(\"kind\")} — {u.get(\"reason\")}")
' 2>/dev/null | sed 's/^/ctl-178:   /' >&2
  fail=1
fi

# ---- arm 3: every disposition literal has exactly one table entry (SC10's structural half)
# `plan_manager.py` imports click/pyyaml, so the probe must run under an environment that
# has them — a bare `python3` raises ModuleNotFoundError and the arm would fail for a reason
# unrelated to the property. (Measured on the first run: it did exactly that.)
arm3="${HERE}/corpus/_arm3_set_equality.py"
if ! ( cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run --with click --with pyyaml \
        python3 "${arm3}" "${PM}" ) 2>&1 | sed 's/^/ctl-178:   /' >&2; then
  echo "ctl-178: UPSTREAM_REQUIREMENTS and UPSTREAM_DISPOSITIONS are not the same set." >&2
  echo "ctl-178: a disposition with no entry falls through to the unrecognised-literal" >&2
  echo "ctl-178: branch — a generator silently omitting a disposition is #181's defect" >&2
  echo "ctl-178: class in a new place." >&2
  fail=1
fi

[ "${fail}" -eq 0 ] && echo "ctl-178: the omitted grant is rejected naming #172's close; the amended one is accepted; every disposition has exactly one table entry"
exit "${fail}"
