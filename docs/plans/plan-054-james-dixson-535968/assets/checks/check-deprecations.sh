#!/usr/bin/env bash
# SC34 — the changelog carries a Deprecations section naming BOTH retained aliases.
#
# D-3 keeps `yf skills` and `--surface` for this cycle (0.5.0, not 1.0.0, precisely so the
# release is not OBLIGATED to remove them). A retained deprecation nobody announces is a
# deprecation users discover by breakage.
CHECK_NAME=check-deprecations
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
CL="${TREE}/CHANGELOG.md"
[ -f "${CL}" ] || ck_inconclusive "no CHANGELOG.md at ${CL}"
CK_RC=0

grep -qiE '^#+ +deprecat' "${CL}" || ck_fail "CHANGELOG.md has no Deprecations section"
grep -q 'yf skills' "${CL}"       || ck_fail "the changelog does not name the retained \`yf skills\` alias group"
grep -q -- '--surface' "${CL}"    || ck_fail "the changelog does not name the retained \`--surface\` alias"
ck_done "the changelog announces both retained deprecations"
