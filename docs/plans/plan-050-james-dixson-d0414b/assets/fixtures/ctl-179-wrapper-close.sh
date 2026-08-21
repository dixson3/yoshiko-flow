#!/usr/bin/env bash
# ctl-179-wrapper-close — REQ-PLAN-077 / #179. SC3.
#
# A FIXTURE per Issue 0.2's definition: EXITS 0 IFF THE ASSERTED BEHAVIOUR HOLDS. The asserted
# behaviour is SC3's: pour a molecule, resolve the start gate, and the WRAPPER TASK is `closed`
# carrying a GENERATED close_reason.
#
# Pre-fix there is no mechanism at all — `bd gate resolve` closes the gate and nothing closes
# the wrapper — so this is RED. EXP-002 measured the consequence: 49 of 49 wrapper beads ever
# poured were closed BY HAND, with 29 distinct improvised reasons.
#
# NOTE THE DIRECTION. This fixture is a red->green control and IS in controls.txt. Its sibling
# `neg-179-open-wrapper` is a RAW SCENARIO whose assertion is invariant across the fix, so it is
# NOT a fixture and NOT in controls.txt — see Issue 1.1 and pass-7 C67.
set -uo pipefail
SCEN_NAME=ctl-179
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
# shellcheck source=/dev/null
. "${HERE}/_beadsenv.sh"

beadsenv_setup

# THE BEHAVIOUR UNDER TEST: one step that resolves the gate AND closes the wrapper.
out="$(pm resolve-start-gate "${PLAN_DIR}" --json 2>&1)"
rc=$?
if [ "${rc}" -ne 0 ]; then
  echo "ctl-179: \`resolve-start-gate\` exited ${rc}" >&2
  printf '%s\n' "${out}" | sed 's/^/ctl-179:   /' >&2
  exit 1
fi

gate_status="$(bead_field "${START_GATE_BEAD}" status)"
wrap_status="$(bead_field "${START_GATE}" status)"
wrap_reason="$(bead_field "${START_GATE}" close_reason)"

fail=0
if [ "${gate_status}" != "closed" ]; then
  echo "ctl-179: the GATE bead ${START_GATE_BEAD} is '${gate_status}', expected 'closed'" >&2
  fail=1
fi
if [ "${wrap_status}" != "closed" ]; then
  echo "ctl-179: the WRAPPER task ${START_GATE} is '${wrap_status}', expected 'closed'." >&2
  echo "ctl-179: this is #179 exactly — \`bd gate resolve\` closes the gate and nothing" >&2
  echo "ctl-179: closes the wrapper, so close_cascade.py later fail-louds on a non-terminal" >&2
  echo "ctl-179: child under the molecule." >&2
  fail=1
fi
if [ -z "${wrap_reason}" ]; then
  echo "ctl-179: the wrapper carries an EMPTY close_reason — the reason must be GENERATED," >&2
  echo "ctl-179: not improvised (49 of 49 were hand-written, with 29 distinct values)." >&2
  fail=1
else
  # GENERATED means DERIVED FROM THE SCENARIO, not merely non-empty: a constant string would
  # satisfy a non-emptiness check while carrying no information about what was resolved.
  case "${wrap_reason}" in
    *"${START_GATE_BEAD}"*) ;;
    *) echo "ctl-179: close_reason does not name the gate that was resolved" >&2
       echo "ctl-179:   got: ${wrap_reason}" >&2
       fail=1 ;;
  esac
  case "${wrap_reason}" in
    *REQ-PLAN-077*) ;;
    *) echo "ctl-179: close_reason does not cite the contract it discharges (REQ-PLAN-077)" >&2
       echo "ctl-179:   got: ${wrap_reason}" >&2
       fail=1 ;;
  esac
fi

# GUARD THE GUARD: the scenario must really have poured a wrapper distinct from the gate,
# or every assertion above would be vacuous.
if [ "${START_GATE}" = "${START_GATE_BEAD}" ]; then
  echo "ctl-179: VACUOUS — the pour yielded one bead, not the gate/wrapper pair" >&2
  exit 2
fi

[ "${fail}" -eq 0 ] && echo "ctl-179: gate resolved and wrapper closed in one step, reason generated: ${wrap_reason}"
exit "${fail}"
