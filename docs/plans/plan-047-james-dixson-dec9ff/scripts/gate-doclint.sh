#!/usr/bin/env bash
# GATE: doclint row executes and fail-closes.
#
# Capability: a `docs/plans/**` edit selects a non-empty FAST-tier command list containing
# `doclint`, and that command produced output. Satisfied by Epic 3 (the CHANGE-VALIDATION
# wiring), which itself needs Epic 1's minimal engine.
#
# It asserts on COMMAND PRESENCE and a non-empty `output_tail`, and NEVER on
# `status == "pass"`. Two measured reasons:
#   * a FAST tier with zero commands reports `{"status":"pass","commands":[]}` — reproduced
#     live on this tree pre-work, because §3 has no `docs/plans/**` glob (#164 class);
#   * the linter is expected to be RED against the un-normalized historical corpus for the
#     whole of Epic 4, so a `status == "pass"` assertion would gate on the wrong fact.
#
# `output_tail` is a PER-COMMAND key inside `commands[]` — verified against
# change_validation.py, whose TOP-LEVEL keys are tier/status/commands/first_failure.
set -o pipefail
# A failed source must be FATAL. Measured: without this guard, sourcing a missing
# _common.sh left `need`/`harness_fail` undefined, the script carried on regardless, and a
# genuine harness failure was reported as exit 1 — "capability absent". That is the exact
# misclassification the 0/1/2 discipline exists to prevent, found by running the falsification.
. "$(dirname "$0")/_common.sh" || {
    printf '{"harness_ok":false,"reason":"cannot source _common.sh"}\n'; exit 2; }

need jq
need uv
CV=skills/yf-change-validation/scripts/change_validation.py
[ -f "$CV" ] || harness_fail "change_validation.py not found at $CV"

PROBE=docs/plans/plan-047-james-dixson-dec9ff/plan.md
# A FAILING TIER IS NOT A HARNESS FAILURE. change_validation.py exits non-zero when the
# tier fails — which is precisely when the `doclint` row is doing its job. The first version
# of this line treated any non-zero as `harness_fail` (exit 2, no `commands` key emitted),
# so injecting a mutant drove the gate RED for a reason unrelated to what it measures.
# Found by running Issue 3.4's falsification; it is the same misclassification class as the
# `_common.sh` defect Issue 1.4 caught. Accept 0 and 1; anything else is a real harness fault,
# and an unparseable verdict is caught by the `has("commands")` check below either way.
RAW=$(uv run "$CV" run --tier fast --changed "$PROBE" --json 2>/dev/null)
case $? in
    0|1) : ;;
    *)   harness_fail "change_validation.py exited abnormally without a verdict" ;;
esac
printf '%s' "$RAW" | jq -e 'type == "object" and has("commands")' >/dev/null 2>&1 \
    || harness_fail "change_validation.py emitted no parseable verdict object"

# Narrow to the `doclint` command, then re-emit the engine's own shape so the gate `Test:`
# assertion (`.commands | length > 0 and (.[0].output_tail | length > 0)`) reads it directly.
OUT=$(printf '%s' "$RAW" | jq -c '{commands: [.commands[] | select(.id == "doclint")],
                                   tier: .tier, engine_status: .status,
                                   all_command_ids: [.commands[].id]}')
printf '%s\n' "$OUT"

printf '%s' "$OUT" | jq -e '.commands | length > 0 and (.[0].output_tail | length > 0)' \
    >/dev/null 2>&1 || exit 1     # capability ABSENT — the only legal reason to be red
exit 0
