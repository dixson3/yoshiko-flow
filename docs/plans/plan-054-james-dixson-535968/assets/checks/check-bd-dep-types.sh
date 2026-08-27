#!/usr/bin/env bash
# SC25 — the beads dependency-type documentation names only types the installed bd accepts,
# and the verify-against-the-binary rule is recorded where beads-backed planning reads it.
#
# #195, MEASURED: beads.gascity.com documents four dependency types with execution semantics,
# and installed bd 1.1.2 accepts NEITHER `conditional-blocks` NOR `waits-for`. Both absent
# types were load-bearing in a capability review and both proposals would have been
# unbuildable; the divergence was caught only because a peer session read `--help` instead of
# the docs. #195's stated action for THIS repo is (a) record the verify-against-the-binary
# rule where beads-backed planning reads it — so this check asserts that, not merely absence.
#
# BOTH SETS ARE DERIVED. The accepted set comes from the INSTALLED binary's own `--type` line
# and the claimed set from the shipped docs, with NO hardcoded vocabulary on either side. An
# earlier draft of this check carried a literal probe list, which made it vacuous by
# construction: a doc naming a type outside that list was invisible to it, which is exactly
# the class of type #195 is about.
CHECK_NAME=check-bd-dep-types
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ck_need bd
CK_RC=0

# The accepted set, straight out of the installed binary.
accepted="$(bd dep add --help 2>&1 \
            | grep -oE 'Dependency type \(([a-z|-]+)\)' \
            | sed -E 's/Dependency type \((.*)\)/\1/' | tr '|' '\n' | sort -u)"
[ -n "${accepted}" ] || ck_inconclusive "could not derive the accepted type set from \`bd dep add --help\` — cannot judge"

# The claimed set: a `--type`/`-t` value on a line that is a `bd dep` invocation.
#
# THE `bd dep` SCOPING IS REQUIRED, not tidiness. `-t` is overloaded across bd's surface:
# `bd create -t epic` and `bd create -t gate` set the ISSUE type, which has an entirely
# different vocabulary. An unscoped grep flagged `epic`, `gate` and even `json` as bogus
# DEPENDENCY types — three false positives that would have made this check untrustworthy in
# the same breath as it complained about untrustworthy documentation.
claimed="$(grep -rhE -- 'bd[[:space:]]+dep' "${TREE}/skills" --include='*.md' 2>/dev/null \
           | grep -oE -- '(--type|[[:space:]]-t)[[:space:]]+[a-z][a-z-]+' \
           | awk '{print $NF}' | sort -u || true)"
while IFS= read -r t; do
  [ -n "${t}" ] || continue
  printf '%s\n' "${accepted}" | grep -qxF "${t}" \
    || ck_fail "a shipped skill doc names dependency type '${t}', which the installed bd does not accept"
done <<< "${claimed}"

# (a) The verify-against-the-binary rule must be RECORDED where beads-backed planning reads it.
rule_home=""
for cand in "${TREE}/skills/yf-beads-extra/SKILL.md" "${TREE}/skills/yf-beads-authoring/SKILL.md"; do
  [ -f "${cand}" ] || continue
  if grep -qiE 'installed binary|--help.*not.*docs|verify against the installed|docs site describes a version' "${cand}"; then
    rule_home="${cand}"; break
  fi
done
[ -n "${rule_home}" ] \
  || ck_fail "no beads skill records #195's verify-against-the-INSTALLED-binary rule — the docs site and the binary are separate artifacts that move independently"
ck_done "documented dependency types are accepted by the installed bd, and the verify-against-the-binary rule is recorded"
