#!/usr/bin/env bash
# SC4 — the six-root `find` idiom survives at ZERO sites under skills/.
#
# `find` is REPLACED, not extended (D-1 as amended at pass-1 C8): EXP-001 measured it exiting
# 1 on a missing root EVEN WHEN IT FOUND THE TARGET, masked today by `| head -1`. Widening the
# root list guarantees a missing root on most machines, and #203 proposes mandating
# `set -o pipefail` — so a retained fallback would ship a resolver that fails the moment this
# same release's exit-code discipline takes effect.
CHECK_NAME=check-no-legacy-find
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
[ -d "${TREE}/skills" ] || ck_inconclusive "no skills/ under ${TREE}"
CK_RC=0

# `! grep -q`, never `grep -qv` (#224).
hits="$(grep -rlE 'find[[:space:]]+~/\.claude/skills[[:space:]]+~/\.agents/skills' "${TREE}/skills" 2>/dev/null || true)"
if [ -n "${hits}" ]; then
  ck_fail "the six-root \`find\` idiom survives at $(printf '%s\n' "${hits}" | grep -c .) site(s):"
  printf '%s\n' "${hits}" | sed 's/^/  /' >&2
fi
ck_done "the six-root find idiom is gone from skills/"
