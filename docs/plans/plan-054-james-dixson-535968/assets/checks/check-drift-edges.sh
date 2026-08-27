#!/usr/bin/env bash
# SC38 — the two new drift edges exist AND are scoped.
CHECK_NAME=check-drift-edges
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
M="${TREE}/DRIFT-CHECK.md"
[ -f "${M}" ] || ck_inconclusive "no DRIFT-CHECK.md at ${M}"
CK_RC=0
grep -qF 'formulas.md' "${M}"     || ck_fail "no drift edge binds formulas.md to the shipped *.formula.toml set"
grep -qF 'formula.toml' "${M}"    || ck_fail "the formulas.md edge does not name the *.formula.toml source of truth"
grep -qF 'install.md' "${M}"      || ck_fail "no drift edge binds install.md to cli.rs"
grep -qF 'harness-tune.md' "${M}" || ck_fail "no drift edge binds harness-tune.md to cli.rs"
grep -qF 'cli.rs' "${M}"          || ck_fail "the install/harness-tune edges do not name cli.rs as the authority"
ck_done "both new drift edges exist and name their authorities"
