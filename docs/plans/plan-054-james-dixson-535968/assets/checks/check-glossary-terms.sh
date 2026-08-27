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

# The ten terms EXP-005 measured undefined. This list is the MEASUREMENT ITSELF, which is why
# it is written down rather than derived: re-deriving "which terms a cold reader cannot decode"
# is a judgement, not a computation, and silently re-deriving it would let the criterion drift
# to whatever the tree happens to define.
for t in "land the plane" "pour" "wisp" "molecule" "bead" "gate" "harness" "surface" "aggregate" "managed block"; do
  grep -qiF "${t}" "${G}" || ck_fail "the glossary does not define '${t}'"
done
ck_done "the glossary defines all ten measured terms"
