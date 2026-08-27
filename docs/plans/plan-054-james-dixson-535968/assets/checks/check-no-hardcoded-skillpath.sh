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

# The `<!-- skill-script-refs: allow <why> -->` OPT-OUT MARKER IS HONOURED, because
# REQ-YF-EMBED-005 defines it: a deliberate reference to a THIRD-PARTY skill this repo does not
# ship is not the defect SC6 is about. The measured instance is yf-incubator's guarded
# `obsidian-lint` step, which carries the marker and an explicit "skip when absent" condition.
# A check that ignored the spec's own opt-out would be demanding a change the spec forbids.
raw="$(grep -rnE '(uv run|bash|python3?)[[:space:]]+\.?(claude|agents)/skills/' \
          "${TREE}/skills" --include='SKILL.md' --include='README.md' 2>/dev/null || true)"
hits=""
while IFS= read -r line; do
  [ -n "${line}" ] || continue
  file="${line%%:*}"; rest="${line#*:}"; lno="${rest%%:*}"
  # The marker sits on a line shortly above the invocation it licenses.
  start=$(( lno > 3 ? lno - 3 : 1 ))
  if sed -n "${start},${lno}p" "${file}" 2>/dev/null | grep -q 'skill-script-refs: allow'; then
    continue
  fi
  hits="${hits}${line}"$'\n'
done <<< "${raw}"
hits="$(printf '%s' "${hits}" | grep -v '^$' || true)"
if [ -n "${hits}" ]; then
  ck_fail "$(printf '%s\n' "${hits}" | grep -c .) hardcoded relative skill-path invocation(s):"
  printf '%s\n' "${hits}" | sed 's/^/  /' >&2
fi
ck_done "no hardcoded relative .claude/skills invocation in any SKILL.md or skill README.md"
