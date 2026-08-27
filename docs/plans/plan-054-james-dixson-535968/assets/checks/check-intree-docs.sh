#!/usr/bin/env bash
# SC27 — every string named by Issues 4.3-4.8 is true. A CHECKLIST, not a judgement.
CHECK_NAME=check-intree-docs
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
CK_RC=0
_want() { # _want <file> <literal> <why>
  local f="${TREE}/$1"
  [ -f "${f}" ] || { ck_fail "$1 does not exist (${3})"; return; }
  grep -qF -- "$2" "${f}" || ck_fail "$1 does not carry '$2' (${3})"
}
_want README.md          'yf harness skills' 'Issue 4.3: the canonical form'
_want README.md          'opencode'          'Issue 4.3: names all five harnesses'
_want README.md          'pi'                'Issue 4.3: names all five harnesses'
_want docs/README.md     '.md'               'Issue 4.5: a navigable docs index'
_want CLAUDE.md          'yoshiko-flow'      'Issue 4.8: project renamed from beads-skills'
[ -f "${TREE}/docs/yf/preflight-contract.md" ] \
  && { grep -qF 'SCAFFOLD_VERSION' "${TREE}/docs/yf/preflight-contract.md" \
       && ! grep -qE 'SCAFFOLD_VERSION[^0-9]*1\b' "${TREE}/docs/yf/preflight-contract.md" \
       || ck_fail "docs/yf/preflight-contract.md still records SCAFFOLD_VERSION 1 (Issue 4.6: it is 3)"; } \
  || ck_fail "docs/yf/preflight-contract.md is missing (Issue 4.6)"
if [ -f "${TREE}/docs/recommended-settings.md" ]; then
  grep -qiE 'per-harness|drift axis' "${TREE}/docs/recommended-settings.md" \
    || ck_fail "docs/recommended-settings.md does not correct the per-harness drift axis (Issue 4.7)"
else
  ck_fail "docs/recommended-settings.md is missing (Issue 4.7)"
fi
ck_done "every in-tree doc string named by Issues 4.3-4.8 is present"
