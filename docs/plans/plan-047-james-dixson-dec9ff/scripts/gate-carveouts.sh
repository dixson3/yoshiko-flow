#!/usr/bin/env bash
# GATE: carve-outs detectable.
#
# Capability: the linter reports ZERO findings inside all four carved regions, AND a
# positive control run with the carve-out globs disabled exits 1. The control is an
# EXECUTED STEP of this script, not prose in the Condition — the drafted gate tested 2 of 3
# regions and ran no control at all.
#
# Four carved regions (REQ-DATA-027 / plan-047 Epic 2):
#   1. docs/plans/*/findings/okf-migration-samples/**   87 fixture files (whole bundles)
#   2. skills/**/fixtures/**                            17 test-fixture plan.md files
#   3. vendored references/* carrying source:/retrieved:
#   4. references/** structural exclusion (GFM-only, no type schema)
set -o pipefail
# A failed source must be FATAL. Measured: without this guard, sourcing a missing
# _common.sh left `need`/`harness_fail` undefined, the script carried on regardless, and a
# genuine harness failure was reported as exit 1 — "capability absent". That is the exact
# misclassification the 0/1/2 discipline exists to prevent, found by running the falsification.
. "$(dirname "$0")/_common.sh" || {
    printf '{"harness_ok":false,"reason":"cannot source _common.sh"}\n'; exit 2; }

need jq
need uv
LINT=_shared/doc_lint.py
[ -f "$LINT" ] || harness_fail "doc_lint.py not found at $LINT"

CARVED_RE='(findings/okf-migration-samples/|/fixtures/|/references/)'

WITH=$(uv run "$LINT" --json 2>/dev/null)
case $? in 0|1) : ;; *) harness_fail "doc_lint exited non-zero without a verdict (excludes on)";; esac
printf '%s' "$WITH" | jq -e 'has("findings")' >/dev/null 2>&1 \
    || harness_fail "doc_lint emitted no parseable verdict (excludes on)"

WITHOUT=$(uv run "$LINT" --no-exclude --json 2>/dev/null)
case $? in 0|1) : ;; *) harness_fail "doc_lint exited non-zero without a verdict (control)";; esac
printf '%s' "$WITHOUT" | jq -e 'has("findings")' >/dev/null 2>&1 \
    || harness_fail "doc_lint emitted no parseable verdict (control)"

CARVED=$(printf '%s' "$WITH"    | jq --arg re "$CARVED_RE" '[.findings[] | select(.path | test($re))] | length')
CTRL=$(printf   '%s' "$WITHOUT" | jq --arg re "$CARVED_RE" '[.findings[] | select(.path | test($re))] | length')
FIRED=$([ "$CTRL" -gt 0 ] && echo true || echo false)

jq -nc --argjson c "$CARVED" --argjson f "$FIRED" --argjson ctrl "$CTRL" \
   '{carved_findings: $c, control_fired: $f, control_findings: $ctrl}'

[ "$CARVED" -eq 0 ] && [ "$FIRED" = true ] || exit 1   # capability ABSENT
exit 0
