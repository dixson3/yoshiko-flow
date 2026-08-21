#!/usr/bin/env bash
# neg-179-open-wrapper — SC4. A NEGATIVE CONTROL, and a RAW SCENARIO, not a fixture.
#
# WHY IT IS NOT A FIXTURE. Issue 0.2 defines a fixture as a script that exits 0 iff the
# control's asserted behaviour holds, and `controls.txt` lists ONLY red->green controls. This
# scenario's assertion — "an open wrapper drives close_cascade.py non-zero" — is INVARIANT
# across Issue 1.2's fix. A *fixture* for it would exit 0 both before and after, while SC4
# wants the OBSERVED `close_cascade.py` EXIT ITSELF, which is non-zero on both sides
# (pass-8 C80). So it is run directly, its result recorded in assets/, and it never appears in
# controls.txt — the gate never asks it for a GREEN record.
#
# WHAT IT PROTECTS. R5: that fixing #179 at the pour/resolve seam does not mask a real cascade
# failure. Issue 1.2 explicitly forbids weakening `_bead_is_terminal`; this scenario is the
# behavioural check that it was not weakened anyway.
#
# EXIT: 0 = close_cascade.py exited NON-ZERO on a genuinely open child (the desired, invariant
# outcome). 1 = it exited 0, i.e. the cascade has been silenced. 2 = harness.
set -uo pipefail
SCEN_NAME=neg-179
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
# shellcheck source=/dev/null
. "${HERE}/_beadsenv.sh"

beadsenv_setup

# Resolve ONLY the gate, deliberately leaving the wrapper OPEN — the pre-fix world, and the
# genuinely-open-child case the cascade must always refuse.
( cd "${SCEN_DIR}" && bd gate resolve "${START_GATE_BEAD}" >/dev/null 2>&1 ) \
  || scen_fail "could not resolve the start gate"

wrap_status="$( bead_field "${START_GATE}" status )"
if [ "${wrap_status}" = "closed" ]; then
  echo "neg-179: VACUOUS — the wrapper is already closed, so there is no open child to" >&2
  echo "neg-179: refuse. This scenario asserts the cascade's behaviour on an OPEN one." >&2
  exit 2
fi

cascade_out="$( cd "${SCEN_DIR}" && env -u VIRTUAL_ENV uv run \
  "${YF_TREE}/skills/yf-plan/scripts/close_cascade.py" "${EPIC}" --plan "${PLAN_ID}" --json 2>&1 )"
crc=$?

echo "neg-179: close_cascade.py exit = ${crc} (wrapper status: ${wrap_status})"
if [ "${crc}" -eq 0 ]; then
  echo "neg-179: FAIL — the cascade exited 0 with a genuinely OPEN child under the molecule." >&2
  echo "neg-179: That is a silenced fail-loud, which R5 exists to catch: #179 must be fixed" >&2
  echo "neg-179: at the pour/resolve seam, NOT by weakening _bead_is_terminal." >&2
  printf '%s\n' "${cascade_out}" | sed 's/^/neg-179:   /' >&2
  exit 1
fi
echo "neg-179: the cascade still refuses an open child — invariant holds"
exit 0
