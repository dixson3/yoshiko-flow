#!/usr/bin/env bash
# gate-dagguard.sh — plan-049 Issue 0.8. Capability gate: "the DAG guard can fail".
#
# THE CLAIM UNDER TEST IS ABOUT THE INSTRUMENT, NOT THE CORPUS. It is deliberately NOT
# "the corpus is unchanged" — plan-048's postcondition made that claim and EXP-002 measured
# it PASSING the exact harm it was written for (the 23-emptied-declaration replay: exit 0,
# edges up 2, residue down 22, so the destruction read as an improvement). A control that
# cannot be shown to FAIL on its own motivating harm is not a weak control; it is not a
# control. So this gate opens only when the guard is demonstrated to FAIL on two mutants and
# PASS on a real migration:
#
#   mutant A  23 emptied `depends-on:` declarations   -> guard must exit 1, failing layer L3
#   mutant B  edge-target substitution                -> guard must exit 1 (L2+L3)
#   mutant D  a real 48-bundle `okf.py migrate`       -> guard must exit 0  (false-positive control)
#
# EXIT CONTRACT (0/1/2), read by `gate-run.sh`:
#   0  capability PRESENT — the guard failed A and B and passed D
#   1  capability ABSENT  — the guard does not exist yet, or does not distinguish the mutants
#   2  HARNESS failure    — the runner itself could not execute
#
# THE ABSENT-DELIVERABLE CASE IS 1, NOT 2, AND THAT IS THE POINT. Before Issue 1.1 lands,
# `_shared/dag_guard.py` does not exist. That is the capability being ABSENT — a red gate,
# correctly blocking 2.1 and 3.3 — not a broken harness. Returning 2 here would leave the
# gate UNRESOLVED and the plan would read as stalled. SC30 requires this script be observed
# at exit **1** pre-work, not 2 and not 127.

set -uo pipefail

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "gate-dagguard: HARNESS — not inside a git repository." >&2; exit 2; }
cd "$ROOT" || { echo "gate-dagguard: HARNESS — cannot cd to repo root." >&2; exit 2; }

command -v uv >/dev/null 2>&1 || {
  echo "gate-dagguard: HARNESS — \`uv\` is not on PATH; cannot run the guard." >&2; exit 2; }

GUARD="_shared/dag_guard.py"
TESTS="_shared/test_dag_guard.py"

if [ ! -f "$GUARD" ]; then
  echo "gate-dagguard: CAPABILITY ABSENT — ${GUARD} does not exist (Issue 1.1 ships it)." >&2
  exit 1
fi
if [ ! -f "$TESTS" ]; then
  echo "gate-dagguard: CAPABILITY ABSENT — ${TESTS} does not exist, so the guard has not" >&2
  echo "gate-dagguard: been shown to FAIL on mutants A and B (Issues 1.2/1.3/1.4)." >&2
  exit 1
fi

# The mutant suite is the capability. It exits 0 when every mutant assertion holds and 1 when
# any does not; both are statements ABOUT THE GUARD, so both map straight through. Anything
# else is the runner failing, which is a 2.
env -u VIRTUAL_ENV uv run "$TESTS"
rc=$?
case "$rc" in
  0) echo "gate-dagguard: CAPABILITY PRESENT — the guard fails A and B and passes D."; exit 0 ;;
  1) echo "gate-dagguard: CAPABILITY ABSENT — a mutant assertion did not hold (see above)." >&2; exit 1 ;;
  *) echo "gate-dagguard: HARNESS — the mutant suite exited ${rc}, outside 0/1." >&2; exit 2 ;;
esac
