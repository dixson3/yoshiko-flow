#!/usr/bin/env bash
# SC35 — the live regression ran against the DEPLOYED tree, and the transcript records WHICH
# TREE each harness read.
#
# The tree identity is the whole claim. EXP-002 measured both pi and opencode resolving to the
# CLAUDE-CODE copy while reporting success, so a transcript that does not name the tree cannot
# distinguish a real pass from that exact failure.
CHECK_NAME=check-deployed-tree
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
PLAN_DIR="$(ck_plan_dir)"
CK_RC=0
T="$(find "${PLAN_DIR}/assets" -name '*harness*transcript*' -o -name '*live-regression*' 2>/dev/null | head -1)"
[ -n "${T}" ] || { ck_fail "no live-regression transcript under assets/ — SC35 has nothing to read"; exit "${CK_RC}"; }
for h in pi opencode; do
  grep -qi "${h}" "${T}" || ck_fail "the transcript does not cover ${h}"
  grep -qiE "${h}.*(skills|SKILL_DIR|/\.pi/|/\.config/opencode/)" "${T}" \
    || ck_fail "the transcript does not record WHICH TREE ${h} read — without it a pass is indistinguishable from resolving to the claude-code copy"
done
ck_done "the transcript covers both harnesses and names the tree each read"
