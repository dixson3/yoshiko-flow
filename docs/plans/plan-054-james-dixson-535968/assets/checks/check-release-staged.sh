#!/usr/bin/env bash
# SC29 (amended at close) — the release is STAGED and validated at one commit, and the v0.5.0
# tag is DEFERRED rather than pushed.
#
# WHY THIS REPLACED check-tag-exists.sh. SC29 originally asserted the tag EXISTS, discharged by
# Issue 6.8. The operator descoped 6.8 — deferring the tag to a successor session so the
# harnesses can be verified manually under a real HOME — so the original criterion became false
# for a reason that is a DECISION, not a defect. `SKILL.md` §6.4 sanctions amending a criterion
# that no longer states what the plan means; leaving it would have halted the close chain at
# stop class 5 over work deliberately not done.
#
# THE ABSENCE OF THE TAG IS ASSERTED, NOT MERELY TOLERATED. A check that only verified the
# staged versions would pass equally well if someone HAD pushed the tag — which is precisely the
# irreversible, website-publishing act this plan is declining to perform. So it is checked.
#
# EXIT  0 staged and correctly untagged  ·  1 not  ·  2 could not run
CHECK_NAME=check-release-staged
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
ck_need git
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ROOT="$(git -C "${TREE}" rev-parse --show-toplevel 2>/dev/null)" || ck_inconclusive "not a git repository: ${TREE}"
CK_RC=0

# 1. Every version surface agrees on 0.5.0.
crate="$(awk -F'"' '/^version[[:space:]]*=/{print $2; exit}' "${ROOT}/yf/Cargo.toml" 2>/dev/null)"
[ "${crate}" = "0.5.0" ] || ck_fail "yf/Cargo.toml is '${crate}', not 0.5.0"
grep -qE '^## +v?\[?0\.5\.0' "${ROOT}/CHANGELOG.md" 2>/dev/null \
  || ck_fail "CHANGELOG.md carries no released 0.5.0 heading"
grep -q 'YOSHIKOFLOW_RELEASE = "v0.5.0"' "${ROOT}/web/pelicanconf.py" 2>/dev/null \
  || ck_fail "web/pelicanconf.py's YOSHIKOFLOW_RELEASE is not v0.5.0"
awk '/^name = "yf"$/{getline; if ($0 !~ /0\.5\.0/) exit 1}' "${ROOT}/Cargo.lock" 2>/dev/null \
  || ck_fail "Cargo.lock does not record yf 0.5.0"

# 2. The branch is fully pushed — the successor tags a commit that already exists upstream.
# `wc -l`, NOT `grep -c`. `grep -c` EXITS 1 WHEN THE COUNT IS ZERO, so a `|| echo unknown`
# fallback fires on the SUCCESS case and appends to a perfectly correct "0" — measured here,
# on the first run of this very check. Same family as the exit-code defects #203 is about.
if ! git -C "${ROOT}" rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
  ck_fail "no upstream configured — cannot confirm the branch is pushed"
else
  unpushed="$(git -C "${ROOT}" log --oneline '@{u}..HEAD' 2>/dev/null | wc -l | tr -d ' ')"
  [ "${unpushed}" = "0" ] \
    || ck_fail "${unpushed} commit(s) not pushed — the successor would tag a commit the remote does not have"
fi

# 3. NO v0.5.0 tag. This is the deferral, asserted.
if git -C "${ROOT}" rev-parse -q --verify 'refs/tags/v0.5.0' >/dev/null 2>&1; then
  ck_fail "a v0.5.0 tag EXISTS, but this plan descoped the tag push (Issue 6.8). If the tag was pushed deliberately, this criterion is the one that is now stale — amend it rather than deleting the tag"
fi

ck_done "release staged at $(git -C "${ROOT}" rev-parse --short HEAD): versions agree on 0.5.0, 0 unpushed, tag correctly deferred"
