#!/usr/bin/env bash
# SC15 — the glossary defines every term the ten-term measurement found undefined.
#
# #127 is RESCOPED, not closed (EXP-005): its own stated criterion — "a cold reader can decode
# the docs" — is measurably unmet while ten high-frequency terms have no definition.
CHECK_NAME=check-glossary-terms
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
CK_RC=0

G="$(find "${TREE}/web" -name 'glossary.md' -type f 2>/dev/null | head -1)"
[ -n "${G}" ] || ck_inconclusive "could not locate the website glossary under ${TREE}/web"

# The ten terms EXP-005 measured undefined, TRANSCRIBED FROM THE FINDING'S OWN TABLE
# (findings/exp-005-stale-issue-verification.md), with each term's measured file count:
#
#   preflight 50 · OKF bundle 48 · worktree 29 · fail-closed 28 · silent no-op 25
#   discovered-from 23 · epistemic rules 11 · session boundary 11 · stuck-bead sweep 10 · descope 5
#
# The list is written down rather than derived because "which terms a cold reader cannot decode"
# is a judgement, not a computation.
#
# AN EARLIER DRAFT OF THIS CHECK CARRIED AN INVENTED LIST while asserting it was "the MEASUREMENT
# ITSELF". It was not: it named terms like `pour`, `wisp` and `molecule` that the glossary ALREADY
# defined, so it would have gone green while every genuinely-undefined term stayed undefined —
# a vacuous criterion of exactly the kind this plan exists to remove. Corrected against the
# finding it claimed to be quoting.
for t in "preflight" "OKF bundle" "worktree" "fail-closed" "silent no-op" \
         "discovered-from" "epistemic rules" "session boundary" "stuck-bead sweep" "descope"; do
  grep -qiF "${t}" "${G}" || ck_fail "the glossary does not define '${t}'"
done
ck_done "the glossary defines all ten measured terms"
