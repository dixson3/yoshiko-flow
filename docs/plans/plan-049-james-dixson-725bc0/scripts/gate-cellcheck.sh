#!/usr/bin/env bash
# gate-cellcheck.sh — plan-049 Issue 0.8. Capability gate:
# "the empty-cell and gate-completeness checks can fail".
#
# THESE CHECKS MUST EXIST AND BE FALSIFIABLE **BEFORE ANY DOCUMENT IS WRITTEN**. plan-047's
# empty-cell hole is what let a 90-finding class through, and EXP-006 measured it still
# intact and WIDER than recorded — a zero-row table also passes. Without an instrument that
# demonstrably reddens on those shapes, this plan's own corpus write would be unobservable
# in exactly the way it is trying to close.
#
# Driven in BOTH directions, because a check that fires on everything is as useless as one
# that fires on nothing:
#
#   POSITIVE   a criteria table with an empty required cell   -> doc_lint exit 1
#   POSITIVE   a zero-row criteria table                      -> doc_lint exit 1
#   POSITIVE   a gate with ALL THREE of Type/Condition/Test absent -> doc_lint exit 1
#   NEGATIVE   a conformant document                          -> doc_lint exit 0
#   NEGATIVE   the canonical `Type: human` + `Approvers: operator` Start Gate -> exit 0
#
# The negative arms are not decoration. The `Type` + ONE-OF predicate — the obvious reading —
# was MEASURED firing on 80 of 137 corpus gates, including all 49 Start Gates and the
# canonical template itself, which would make plan-050 unable to pass its own intake.
#
# EXIT CONTRACT (0/1/2), read by `gate-run.sh`:
#   0  capability PRESENT — every arm above behaved as stated
#   1  capability ABSENT  — a check or a fixture is missing, or an arm did not behave
#   2  HARNESS failure    — the runner itself could not execute
#
# A MISSING FIXTURE IS 1, NOT 2. The fixtures are part of the deliverable (Issues 3.1/3.2/3.2b),
# so their absence is the capability being absent — a correctly RED gate blocking 3.3. SC30
# requires this script be observed at exit **1** pre-work.

set -uo pipefail

ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || {
  echo "gate-cellcheck: HARNESS — not inside a git repository." >&2; exit 2; }
cd "$ROOT" || { echo "gate-cellcheck: HARNESS — cannot cd to repo root." >&2; exit 2; }

command -v uv >/dev/null 2>&1 || {
  echo "gate-cellcheck: HARNESS — \`uv\` is not on PATH." >&2; exit 2; }

LINT="_shared/doc_lint.py"
FIX="tests/fixtures/doc-checks"

[ -f "$LINT" ] || { echo "gate-cellcheck: HARNESS — ${LINT} is missing entirely." >&2; exit 2; }

# `<fixture-stem>:<expected-exit>`; the expectation is the whole assertion.
ARMS=(
  "m-empty-required-cell:1"
  "m-zero-row-criteria:1"
  "m-gate-all-three-absent:1"
  "control-conformant:0"
  "control-canonical-start-gate:0"
)

missing=0
for arm in "${ARMS[@]}"; do
  stem="${arm%%:*}"
  [ -f "${FIX}/${stem}/plan.md" ] || { echo "gate-cellcheck: CAPABILITY ABSENT — fixture ${FIX}/${stem}/plan.md is missing." >&2; missing=1; }
done
[ "$missing" -eq 0 ] || {
  echo "gate-cellcheck: the fixtures are part of the deliverable (Issues 3.1/3.2/3.2b)." >&2
  exit 1; }

fail=0
for arm in "${ARMS[@]}"; do
  stem="${arm%%:*}"; want="${arm##*:}"
  env -u VIRTUAL_ENV uv run "$LINT" --type plan --path "${FIX}/${stem}/plan.md" --json >/dev/null 2>&1
  got=$?
  if [ "$got" -eq 2 ]; then
    echo "gate-cellcheck: HARNESS — doc_lint returned INCONCLUSIVE on ${stem}." >&2
    exit 2
  fi
  if [ "$got" -ne "$want" ]; then
    echo "gate-cellcheck: CAPABILITY ABSENT — ${stem}: expected exit ${want}, got ${got}." >&2
    fail=1
  else
    echo "gate-cellcheck: ok ${stem} -> exit ${got}"
  fi
done

[ "$fail" -eq 0 ] || exit 1
echo "gate-cellcheck: CAPABILITY PRESENT — both checks fire on the three mutants and on neither control."
exit 0
