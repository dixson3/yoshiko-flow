#!/usr/bin/env bash
# Issue 10.0 — the D-13 split-proposal renderer.
#
# TRIP CONDITION (mechanical, measured — not transcribed): `ls reviews/pass-*.md | wc -l` >= 4
# at the end of Epic 5. This is the same signal `_audit_plan` check #5 already uses.
#
# The originally-drafted second clause ("any Epic 0-5 issue reopened twice") was DROPPED at
# review (M9): `bd` exposes Dolt version history but no reopen counter, so it would have been
# manual archaeology across ~35 beads — a trip condition with no exit code, inside the
# mitigation for the plan's highest-severity risk.
#
# Emits {tripped, review_cycles, ...} and EXITS NON-ZERO WHEN TRIPPED, so the split is a gate
# rather than a request.
set -o pipefail
. "$(dirname "$0")/_common.sh" || {
    printf '{"harness_ok":false,"reason":"cannot source _common.sh"}\n'; exit 2; }

need jq
PLAN_DIR=docs/plans/plan-047-james-dixson-dec9ff
[ -d "$PLAN_DIR/reviews" ] || harness_fail "no reviews/ directory at $PLAN_DIR"

CYCLES=$(ls "$PLAN_DIR"/reviews/pass-*.md 2>/dev/null | wc -l | tr -d ' ')
THRESHOLD=4
TRIPPED=$([ "$CYCLES" -ge "$THRESHOLD" ] && echo true || echo false)

EPIC=$(grep -m1 '^\*\*Epic:\*\*' "$PLAN_DIR/plan.md" 2>/dev/null | awk '{print $2}')
REMAINING=0
if command -v bd >/dev/null 2>&1 && [ -n "$EPIC" ]; then
    REMAINING=$(bd list --all --limit 5000 --json 2>/dev/null \
        | jq --arg e "$EPIC" '[.[] | select(.id | startswith($e + "."))
              | select(.issue_type == "task") | select(.status != "closed")] | length' 2>/dev/null || echo 0)
fi

jq -nc --argjson t "$TRIPPED" --argjson c "$CYCLES" --argjson th "$THRESHOLD" \
       --argjson r "${REMAINING:-0}" --arg e "${EPIC:-}" \
  '{tripped: $t, review_cycles: $c, threshold: $th, remaining_open_issues: $r, epic: $e}'

[ "$TRIPPED" = true ] && exit 1
exit 0
