#!/usr/bin/env bash
# SC13 — the README documents the canonical `yf harness skills` form and names all five harnesses.
#
# Measured today: README.md contains ZERO occurrences of `opencode`, `pi`, or `--harness`, and
# teaches a command spelling `cli.rs` marks deprecated.
CHECK_NAME=check-readme-harness
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
RM="${TREE}/README.md"
[ -f "${RM}" ] || ck_inconclusive "no README.md at ${RM}"
CK_RC=0

grep -q 'yf harness skills' "${RM}" || ck_fail "the README does not document the canonical \`yf harness skills\` form"
grep -q -- '--harness' "${RM}"      || ck_fail "the README never mentions --harness"
for h in claude-code codex opencode pi agents; do
  grep -q "${h}" "${RM}" || ck_fail "the README does not name the '${h}' harness"
done
ck_done "the README documents the canonical form and names all five harnesses"
