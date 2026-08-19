#!/usr/bin/env bash
# Regenerate the pre-work / post-work gate `Test:` records (plan-047 Issue 1.4, SC9d).
#
# WHY THIS IS A COMMITTED SCRIPT AND NOT AN AD-HOC SHELL FUNCTION
# ---------------------------------------------------------------
# The first run of the ad-hoc version was driven by a `declare -a` array indexed from 0 —
# under **zsh**, arrays are 1-indexed, so the first iteration ran with an EMPTY gate name.
# It wrote `assets/gate-prework/.txt`, a record of an EMPTY command reporting `exit: 0`,
# and that file was **committed** (9663a0d).
#
# That artifact is trap #164 — the zero-commands green — reproduced *inside the directory
# whose entire purpose is to prove gates fail for the right reason*. It was inert (the
# resolver never reads it, and the four real records were correct), but it is exactly the
# shape that fools a later auditor: a file that looks like evidence and asserts nothing.
#
# The cleanup was itself instructive: `rm -f gate-prework/*.txt` did NOT remove it, because
# a leading-dot filename is not matched by `*` in zsh. A silent artifact survived the sweep
# meant to catch it.
#
# So: this script REFUSES an empty gate name, refuses a name with no matching script, and
# refuses to write outside the intended directory. An unset variable is a loud failure.
set -euo pipefail

PD=docs/plans/plan-047-james-dixson-dec9ff
OUT="$PD/assets/gate-prework"
cd "$(git rev-parse --show-toplevel)"

record() {
    local n=${1:-} T=${2:-}
    [ -n "$n" ] || { echo "FATAL: empty gate name — refusing to write '$OUT/.txt'" >&2; exit 2; }
    [ -n "$T" ] || { echo "FATAL: empty Test string for gate '$n'" >&2; exit 2; }
    [ -f "$PD/scripts/gate-$n.sh" ] || { echo "FATAL: no script for gate '$n'" >&2; exit 2; }

    local out rc sc
    out=$(eval "$T" 2>/tmp/gp.err) && rc=0 || rc=$?
    bash "$PD/scripts/gate-$n.sh" >/tmp/gp.out 2>/dev/null && sc=0 || sc=$?
    {
        echo "# Pre-work RED run — gate: $n   (plan-047 Issue 1.4 / SC9d)"
        echo "# Recorded: $(date -u +%Y-%m-%dT%H:%M:%SZ)   tree: $(git rev-parse --short HEAD)"
        echo "#"
        echo "# The command below is the gate \`Test:\` STRING as the resolver executes it — NOT"
        echo "# the bare script. The PIPELINE is what runs, so the pipeline is what is archived."
        echo "#"
        echo "# Exit-code discipline (_common.sh): 0 = capability present · 1 = capability absent ·"
        echo "# 2 = the harness could not run. A gate is only allowed to be red for reason 1."
        echo; echo "\$ $T"
        echo "pipeline exit: $rc"
        echo "script-alone exit: $sc   <-- 1 = capability ABSENT (the only legal red)"
        echo; echo "--- script stdout (the JSON verdict) ---"; cat /tmp/gp.out
        echo "--- pipeline stdout (jq -e) ---"; echo "$out"
        echo "--- stderr (tail 5) ---"; tail -5 /tmp/gp.err
    } > "$OUT/$n.txt"
    printf '%-11s pipeline=%s script=%s\n' "$n" "$rc" "$sc"
}

record doclint    "set -o pipefail; bash $PD/scripts/gate-doclint.sh | jq -e '.commands | length > 0 and (.[0].output_tail | length > 0)'"
record carveouts  "set -o pipefail; bash $PD/scripts/gate-carveouts.sh | jq -e '.carved_findings == 0 and .control_fired == true'"
record normalizer "set -o pipefail; bash $PD/scripts/gate-normalizer.sh | jq -e '.diff_bytes > 0 and .fingerprints_moved == 0'"
record upstream   "set -o pipefail; bash $PD/scripts/gate-upstream.sh | jq -e '.comments >= 8 and .auth == true'"
