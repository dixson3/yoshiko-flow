#!/usr/bin/env bash
# GATE: Upstream write  (Type: human — authorization is the operator's, not this script's).
#
# Capability: `gh` is authenticated, and Issue 10.3 has drafted at least 8 comment files —
# the coarse tracker (#175) plus the 7 non-exclude upstream rows (#113 #174 #149 #165 #125
# #135 #62). Emitting {comments, auth} makes a stubbed script INCONCLUSIVE rather than PASS.
#
# The drafted Test asserted only that SOME comment-*.md existed and was therefore already
# green before any work had been done (review M7).
set -o pipefail
# A failed source must be FATAL. Measured: without this guard, sourcing a missing
# _common.sh left `need`/`harness_fail` undefined, the script carried on regardless, and a
# genuine harness failure was reported as exit 1 — "capability absent". That is the exact
# misclassification the 0/1/2 discipline exists to prevent, found by running the falsification.
. "$(dirname "$0")/_common.sh" || {
    printf '{"harness_ok":false,"reason":"cannot source _common.sh"}\n'; exit 2; }

need jq
command -v gh >/dev/null 2>&1 || { jq -nc '{comments: 0, auth: false,
    reason: "gh not on PATH"}'; exit 1; }

REFS=docs/plans/plan-047-james-dixson-dec9ff/references
N=$(ls "$REFS"/comment-*.md 2>/dev/null | wc -l | tr -d ' ')
if gh auth status >/dev/null 2>&1; then AUTH=true; else AUTH=false; fi

jq -nc --argjson n "$N" --argjson a "$AUTH" '{comments: $n, auth: $a}'

[ "$N" -ge 8 ] && [ "$AUTH" = true ] || exit 1
exit 0
