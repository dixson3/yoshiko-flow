#!/usr/bin/env bash
# SC6 — no SKILL.md or skill README.md invokes a script by a hardcoded relative
# `.claude/skills/` path.
#
# Discovered beyond the scoped set: two skills carry 14 such sites that bypass SKILL_DIR
# ENTIRELY, so no amount of resolver work reaches them. A hardcoded `.claude/skills/...` is
# doubly wrong under this release — it names one harness out of five, and it is relative to a
# cwd the skill does not control.
CHECK_NAME=check-no-hardcoded-skillpath
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
[ -d "${TREE}/skills" ] || ck_inconclusive "no skills/ under ${TREE}"
CK_RC=0

hits="$(grep -rnE '(uv run|bash|python3?)[[:space:]]+\.?(claude|agents)/skills/' \
          "${TREE}/skills" --include='SKILL.md' --include='README.md' 2>/dev/null || true)"
if [ -n "${hits}" ]; then
  ck_fail "$(printf '%s\n' "${hits}" | grep -c .) hardcoded relative skill-path invocation(s):"
  printf '%s\n' "${hits}" | sed 's/^/  /' >&2
fi
ck_done "no hardcoded relative .claude/skills invocation in any SKILL.md or skill README.md"
