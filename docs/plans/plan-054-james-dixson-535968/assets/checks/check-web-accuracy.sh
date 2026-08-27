#!/usr/bin/env bash
# SC28 — every string named by Issues 5.2-5.6 is true. A CHECKLIST, as SC27.
CHECK_NAME=check-web-accuracy
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
[ -d "${TREE}/web" ] || ck_inconclusive "no web/ under ${TREE}"
CK_RC=0
_page() { find "${TREE}/web" -name "$1" -type f 2>/dev/null | head -1; }
_want() { # _want <page-name> <literal> <why>
  local f; f="$(_page "$1")"
  [ -n "${f}" ] || { ck_fail "$1 not found under web/ (${3})"; return; }
  grep -qiF -- "$2" "${f}" || ck_fail "$1 does not carry '$2' (${3})"
}
_want install.md    '--no-sync'                 'Issue 5.2: the install-time sync is default-on'
_want install.md    '--allow-permissions-write' 'Issue 5.2: the consent gate exits non-zero without it'
_want lifecycle.md  'yf harness skills'         'Issue 5.3: the deprecated spelling is replaced'
_want architecture.md 'opencode'                'Issue 5.4: five harnesses, not two surfaces'
_want architecture.md 'pi'                      'Issue 5.4: five harnesses, not two surfaces'
# Issue 5.3's set is DERIVED, not listed: re-run the grep rather than trusting a count.
# A DOCUMENTED DEPRECATION NOTICE IS NOT THE DEFECT. The criterion is "no page TEACHES the
# deprecated spelling as canonical" — a line that names `yf skills install` in order to say it is
# deprecated is the page doing its job, and a bare occurrence-count check cannot tell the two
# apart. Measured: a blind sweep over every occurrence destroyed install.md's deprecation note,
# leaving it asserting that the CANONICAL command was slated for removal. So lines that also
# carry the word `deprecated` are excluded.
stale="$(grep -rn 'yf skills install' "${TREE}/web" 2>/dev/null \
         | grep -vi 'deprecated' | cut -d: -f1 | sort -u || true)"
if [ -n "${stale}" ]; then
  ck_fail "$(printf '%s\n' "${stale}" | grep -c .) web file(s) still teach the deprecated \`yf skills install\` spelling:"
  printf '%s\n' "${stale}" | sed "s|^${TREE}/|  |" >&2
fi
ck_done "every website string named by Issues 5.2-5.6 is present"
