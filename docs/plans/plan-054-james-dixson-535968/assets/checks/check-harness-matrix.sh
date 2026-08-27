#!/usr/bin/env bash
# SC22 — the five-harness matrix is asserted PER HARNESS.
#
# Named explicitly: pi's name transform, pi's `Deferred` config verdict, codex's budget cap,
# and `--revert` for all five. Every existing multi-harness assertion is a filesystem-path
# assertion under a fake HOME, which is exactly the gap that let D-1's defect ship (D-4).
CHECK_NAME=check-harness-matrix
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
E2E="$(find "${TREE}/yf" "${TREE}/tests" -name 'harness_cross_e2e.rs' -type f 2>/dev/null | head -1)"
[ -n "${E2E}" ] || ck_inconclusive "could not locate harness_cross_e2e.rs"
CK_RC=0
grep -qiE 'name_?transform|NameTransform' "${E2E}" || ck_fail "no assertion covers pi's name transform"
grep -qiE 'deferred'                       "${E2E}" || ck_fail "no assertion covers pi's Deferred config verdict"
grep -qiE 'project_doc_max_bytes|budget'   "${E2E}" || ck_fail "no assertion covers codex's block-size budget cap"
for h in claude-code codex opencode pi agents; do
  grep -qF "${h}" "${E2E}" || ck_fail "the matrix does not cover the '${h}' harness"
done
grep -qF -- 'revert' "${E2E}" || ck_fail "no --revert assertion in the matrix"
ck_done "the five-harness matrix asserts each named axis"
