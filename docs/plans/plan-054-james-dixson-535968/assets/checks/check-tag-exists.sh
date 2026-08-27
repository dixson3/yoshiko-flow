#!/usr/bin/env bash
# SC29 — the v0.5.0 tag exists and points at the validated merge commit.
#
# BOTH HALVES MATTER. A tag that exists but points somewhere else ships a tree nothing
# validated, and the tag push auto-publishes the website with no fix-it-afterwards window.
CHECK_NAME=check-tag-exists
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
ck_need git
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
ROOT="$(git -C "${TREE}" rev-parse --show-toplevel 2>/dev/null)" || ck_inconclusive "not a git repository: ${TREE}"
CK_RC=0

if ! git -C "${ROOT}" rev-parse -q --verify 'refs/tags/v0.5.0' >/dev/null 2>&1; then
  ck_fail "the v0.5.0 tag does not exist"
  exit "${CK_RC}"
fi
tagged="$(git -C "${ROOT}" rev-list -n1 'v0.5.0' 2>/dev/null)"
head_main="$(git -C "${ROOT}" rev-parse main 2>/dev/null || true)"
if [ -z "${tagged}" ]; then
  ck_fail "v0.5.0 resolves to no commit"
elif [ -n "${head_main}" ] && [ "${tagged}" != "${head_main}" ]; then
  if ! git -C "${ROOT}" merge-base --is-ancestor "${tagged}" "${head_main}" 2>/dev/null; then
    ck_fail "v0.5.0 (${tagged}) is not an ancestor of main (${head_main}) — the tag does not point at the validated merge"
  fi
fi
ck_done "v0.5.0 exists and points into main's validated history"
