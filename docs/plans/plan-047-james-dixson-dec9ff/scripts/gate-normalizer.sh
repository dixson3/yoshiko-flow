#!/usr/bin/env bash
# GATE: normalizer aggregate diff  (Type: human — the Test is a PRECONDITION, never consent).
#
# Capability: Issue 8.8a has rendered a non-empty aggregate hash-neutral diff to
# assets/normalizer-aggregate.diff, and the normalizer's own report says NO content
# fingerprint moved. `fingerprints_moved` is the key REQ-DATA-025 pins (Issue 0.6) — pinned
# in the SPEC before this gate was allowed to depend on it.
#
# Both must hold AND the operator must authorize. A green Test establishes that a condition
# holds; it can never establish that a human authorized applying a 46-plan rewrite.
set -o pipefail
# A failed source must be FATAL. Measured: without this guard, sourcing a missing
# _common.sh left `need`/`harness_fail` undefined, the script carried on regardless, and a
# genuine harness failure was reported as exit 1 — "capability absent". That is the exact
# misclassification the 0/1/2 discipline exists to prevent, found by running the falsification.
. "$(dirname "$0")/_common.sh" || {
    printf '{"harness_ok":false,"reason":"cannot source _common.sh"}\n'; exit 2; }

need jq
PLAN_DIR=docs/plans/plan-047-james-dixson-dec9ff
DIFF="$PLAN_DIR/assets/normalizer-aggregate.diff"
REPORT="$PLAN_DIR/assets/normalizer-report.json"

if [ ! -f "$DIFF" ]; then
    jq -nc '{diff_bytes: 0, fingerprints_moved: null,
             reason: "aggregate diff not rendered yet (Issue 8.8a)"}'
    exit 1                                   # capability ABSENT — not a harness failure
fi
BYTES=$(wc -c < "$DIFF" | tr -d ' ')

if [ ! -f "$REPORT" ]; then
    jq -nc --argjson b "$BYTES" '{diff_bytes: $b, fingerprints_moved: null,
             reason: "normalizer report not emitted yet (Issue 8.1/8.7)"}'
    exit 1
fi
jq -e 'has("fingerprints_moved")' "$REPORT" >/dev/null 2>&1 \
    || harness_fail "normalizer report exists but carries no fingerprints_moved key"

MOVED=$(jq '.fingerprints_moved' "$REPORT")
jq -nc --argjson b "$BYTES" --argjson m "$MOVED" \
   '{diff_bytes: $b, fingerprints_moved: $m}'

[ "$BYTES" -gt 0 ] && [ "$MOVED" -eq 0 ] || exit 1
exit 0
