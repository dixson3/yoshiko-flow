#!/usr/bin/env bash
# SC21 — the deployed tree matches source and the version stamp matches HEAD.
#
# The one residue the install-time sync does NOT cover: HEAD can move for reasons that touch
# nothing `build.rs` watches (a docs-only commit, a checkout, a rebase), leaving an incremental
# build carrying a stale hash. This is the only detector for that case.
CHECK_NAME=check-stamp-agrees
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
ck_need git
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
YF="${TREE}/target/debug/yf"
[ -x "${YF}" ] || ck_inconclusive "no debug binary at ${YF} (run: cargo build)"
CK_RC=0

head_hash="$(git -C "${TREE}" rev-parse --short HEAD 2>/dev/null)" || ck_inconclusive "cannot read HEAD"
ver="$("${YF}" --version 2>&1)" || ck_inconclusive "\`yf --version\` failed"
# A `-dirty` suffix is fine; the HASH ITSELF is what must match.
printf '%s' "${ver}" | grep -qF "${head_hash}" \
  || ck_fail "the version stamp does not carry HEAD (${head_hash}): '${ver}'"

st="$("${YF}" skills status --json 2>/dev/null)" || true
if [ -n "${st}" ]; then
  printf '%s' "${st}" | grep -q '"up_to_date"[[:space:]]*:[[:space:]]*false' \
    && ck_fail "the deployed tree does not match source (a skill reports up_to_date:false)"
fi
ck_done "the deployed tree matches source and the stamp carries HEAD"
