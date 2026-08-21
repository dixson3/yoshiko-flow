#!/usr/bin/env bash
# ctl-180-chain-order — REQ-COMPLETE-004 / #180. SC5.
#
# A FIXTURE per Issue 0.2's definition. The asserted behaviour: `close-reconcile-step` REFUSES,
# with a non-zero exit, when the plan's Reconcile Gate is still UNRESOLVED.
#
# Pre-fix the ordering exists only in the author's head: the verb closes the reconcile bead
# happily against incomplete execution and exits 0. Two consecutive plans hit that, worked
# around it by hand and filed it; a third was told to expect it at launch and hit it anyway.
#
# THE SECOND HALF OF THE DEFECT IS THE CALLER. SKILL.md §6.4 captured this verb as
# `RSTEP=$(… close-reconcile-step …)` and only echoed it — it never checked `$?`. An exit code
# nothing reads is the same "a step with no exit code is not a step" class in its second form,
# so Issue 1.3 must change both. This fixture asserts the exit code; `test_close_contract.py`
# plus Issue 1.4 cover the caller.
set -uo pipefail
SCEN_NAME=ctl-180
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
# shellcheck source=/dev/null
. "${HERE}/_beadsenv.sh"

beadsenv_setup

# Seed the reconcile pair the §6.4 chain operates on: an UNRESOLVED gate and the bead that
# must not be closed ahead of it.
rgate="$( cd "${SCEN_DIR}" && bd create "Gate: Reconcile upstream" \
  --description "Blocks reconciliation until execution complete." \
  -t gate --parent "${EPIC}" --json 2>/dev/null \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); d=d[0] if isinstance(d,list) else d; print(d["id"])' )"
[ -n "${rgate}" ] || scen_fail "could not create the reconcile gate"

rstep="$( cd "${SCEN_DIR}" && bd create "Reconcile: update upstream issues" \
  --description "Update upstream issues per plan dispositions." \
  -t task -p 1 --parent "${EPIC}" --deps "${rgate}" --json 2>/dev/null \
  | python3 -c 'import json,sys; d=json.load(sys.stdin); d=d[0] if isinstance(d,list) else d; print(d["id"])' )"
[ -n "${rstep}" ] || scen_fail "could not create the reconcile step"

# GUARD THE GUARD: the gate must genuinely be unresolved, or the assertion is vacuous.
gstatus="$( bead_field "${rgate}" status )"
if [ "${gstatus}" = "closed" ]; then
  echo "ctl-180: VACUOUS — the reconcile gate is already closed; there is no ordering to violate" >&2
  exit 2
fi

out="$( pm close-reconcile-step "${PLAN_DIR}" --json 2>&1 )"
rc=$?

verdict="$( printf '%s' "${out}" | python3 -c '
import json,sys
try:
    print(json.loads(sys.stdin.read()).get("verdict",""))
except Exception:
    print("")
' 2>/dev/null )"

after="$( bead_field "${rstep}" status )"

fail=0
if [ "${rc}" -eq 0 ]; then
  echo "ctl-180: \`close-reconcile-step\` exited 0 with the reconcile gate UNRESOLVED (${gstatus})." >&2
  echo "ctl-180: the §6.4 chain ordering constraint is not enforced — it is prose." >&2
  fail=1
fi
if [ "${verdict}" != "fail" ]; then
  echo "ctl-180: verdict was '${verdict}', expected 'fail' — REQ-COMPLETE-003 requires the" >&2
  echo "ctl-180: envelope on stdout on every path, including this one." >&2
  fail=1
fi
if [ "${after}" = "closed" ]; then
  echo "ctl-180: the reconcile bead ${rstep} was CLOSED anyway. Refusing must mean not acting." >&2
  fail=1
fi

[ "${fail}" -eq 0 ] && echo "ctl-180: close-reconcile-step refused (exit ${rc}, verdict ${verdict}); ${rstep} left ${after}"
exit "${fail}"
