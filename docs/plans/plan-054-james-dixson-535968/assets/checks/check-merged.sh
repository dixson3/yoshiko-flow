#!/usr/bin/env bash
# SC37 — the execute branch is merged, and the merged tree is the one every later issue validated.
CHECK_NAME=check-merged
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
ck_need git
PLAN_DIR="$(ck_plan_dir)"
PLAN_ID="$(basename "${PLAN_DIR}")"
ROOT="$(git -C "${PLAN_DIR}" rev-parse --show-toplevel 2>/dev/null)" || ck_inconclusive "not a git repository"
CK_RC=0
BR="${PLAN_ID}-execute"
if ! git -C "${ROOT}" rev-parse -q --verify "refs/heads/${BR}" >/dev/null 2>&1; then
  # A torn-down branch is the POST-merge state, so absence alone is not a failure — but then
  # main must actually carry the work.
  git -C "${ROOT}" log --oneline main 2>/dev/null | grep -qF "${PLAN_ID}" \
    || ck_fail "${BR} does not exist and main carries no ${PLAN_ID} commit — nothing was merged"
  ck_done "the execute branch is merged (branch torn down, main carries the work)"
fi
git -C "${ROOT}" merge-base --is-ancestor "${BR}" main 2>/dev/null \
  || ck_fail "${BR} is not an ancestor of main — the execute branch is not merged"
ck_done "the execute branch is merged into main"
