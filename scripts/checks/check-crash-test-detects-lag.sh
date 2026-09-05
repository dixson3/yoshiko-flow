#!/usr/bin/env bash
# SC13a / SC13b — THE NEGATIVE CONTROL. Do the tests DETECT the defects they name?
#
# WHY THIS EXISTS, and why pinning selectors was not enough. plan-064 found TWO tests that
# passed against non-conforming code:
#
#   REQ-OKFH-008  `test_crash_recovery_all_states` HAND-CONSTRUCTED each journal state and never
#                 invoked `backfill`'s swap, so it mocked the call site it existed to observe.
#                 Applying the phase-ordering fix and re-running it produced BYTE-IDENTICAL
#                 output — insensitive to the production ordering by construction.
#   REQ-OKFH-010  `test_restore_round_trip` asserted on the op list `restore` RE-DERIVED from the
#                 filesystem — the very behaviour the requirement forbids — so it passed under
#                 both implementations.
#
# Pinning the new criteria to NEW test names prevents INHERITING a false green. It never DETECTS
# one. Only running the test against a deliberately broken tree does that, which is what this
# script is: a mutation check with a real exit code.
#
# THE MUTATION IS A FLAG FLIP, NEVER A RECONSTRUCTED REVERT. Both defects are reachable via one
# env var each (`OKFH_FORCE_LEGACY_PHASE_ORDER`, `OKFH_FORCE_LEGACY_DERIVATION`), retained in the
# engine for this purpose and documented there. A control whose mutant must be rebuilt with `sed`
# drifts from the code the moment either changes, and then silently tests nothing.
#
# THE ASSERTION IS TWO-SIDED. "Fails on the mutant" alone is satisfied by a test that always
# fails; "passes on the fixed tree" alone is the green we already have. Both, together, are what
# make the test an instrument.
#
# EXIT  0 the test fails on the mutant AND passes on the fixed tree  ·  1 it does not  ·  2 could not run
CHECK_NAME=check-crash-test-detects-lag
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

REQ="REQ-OKFH-008"
while [ $# -gt 0 ]; do
  case "$1" in
    --req) REQ="${2:-}"; shift 2 ;;
    *) ck_inconclusive "unknown argument: $1" ;;
  esac
done

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ck_need uv
SCRIPTS="${TREE}/skills/yf-okf-hygiene/scripts"
TESTS="${SCRIPTS}/test_okf_hygiene.py"
[ -f "${TESTS}" ] || ck_inconclusive "no test_okf_hygiene.py at ${TESTS}"
CK_RC=0

# THE SELECTORS ARE PINNED TO THE POST-REPLACEMENT NAMES (Issue 3.8). They must NEVER name
# `crash_recovery_all_states` or `restore_round_trip`: measurement shows neither can fail, so a
# control pinned to one is not a control.
case "${REQ}" in
  REQ-OKFH-008)
    SELECTOR='crash_s1_bundle_present or crash_s3_recorded_physical_s2 or crash_recovery_every_reachable_state_survives'
    MUTANT_ENV="OKFH_FORCE_LEGACY_PHASE_ORDER=1"
    WHAT="the phase-lag defect (each phase written AFTER the operation it names)"
    ;;
  REQ-OKFH-010)
    SELECTOR='restore_record_driven'
    MUTANT_ENV="OKFH_FORCE_LEGACY_DERIVATION=1"
    WHAT="non-record-drivenness (restore re-deriving ops from rglob + git ls-files)"
    ;;
  *) ck_inconclusive "unsupported --req ${REQ} (supported: REQ-OKFH-008, REQ-OKFH-010)" ;;
esac

run_tests() {  # $1 = extra env assignment or empty
  ( cd "${TREE}" && env ${1:-} uv run --with pytest --with pyyaml python3 -m pytest \
      "${TESTS}" -q -k "${SELECTOR}" >/dev/null 2>&1 ); echo $?
}

# --- SIDE 1: the FIXED tree. The test must PASS, or side 2 means nothing. ---------------
RC_FIXED="$(run_tests "")"
if [ "${RC_FIXED}" != "0" ]; then
  ck_fail "on the FIXED tree the ${REQ} test(s) exit ${RC_FIXED}, not 0 — the mutant arm below cannot be interpreted"
fi

# --- SIDE 2: the MUTANT. The test must FAIL. -------------------------------------------
# This is the arm the old tests could not satisfy: measured, `crash_recovery_all_states` and
# `restore_round_trip` both exited 0 here.
RC_MUTANT="$(run_tests "${MUTANT_ENV}")"
if [ "${RC_MUTANT}" = "0" ]; then
  ck_fail "with ${MUTANT_ENV} the ${REQ} test(s) STILL PASS — they do not detect ${WHAT}. This is a FALSE GREEN: the test is insensitive to the behaviour it names."
fi

# --- NON-VACUITY: the selector must actually have selected something. -------------------
COLLECTED="$( (cd "${TREE}" && uv run --with pytest --with pyyaml python3 -m pytest "${TESTS}" \
  -q -k "${SELECTOR}" --collect-only 2>/dev/null | grep -c '::') || true )"
if [ "${COLLECTED}" = "0" ]; then
  ck_inconclusive "the selector matched NO tests — a control over an empty set certifies vacuously"
fi

ck_done "${REQ}: fixed-tree=${RC_FIXED}, mutant=${RC_MUTANT}, tests-selected=${COLLECTED} — the test DETECTS ${WHAT}"
