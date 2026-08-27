#!/usr/bin/env bash
# SC33 — no shipped SKILL.md relies on `allowed-tools` for scoping.
#
# Measured: `allowed-tools` occurs ZERO times in either the pi or the opencode bundle format,
# while ten shipped SKILL.md files carry it. A skill relying on it to constrain what it may do
# is therefore UNCONSTRAINED under every harness but claude-code (REQ-YF-EMBED-006).
CHECK_NAME=check-allowed-tools
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
[ -d "${TREE}/skills" ] || ck_inconclusive "no skills/ under ${TREE}"
CK_RC=0

carriers="$(grep -rl '^allowed-tools:' "${TREE}/skills" --include='SKILL.md' 2>/dev/null || true)"
n=0; [ -n "${carriers}" ] && n="$(printf '%s\n' "${carriers}" | grep -c .)"
if [ "${n}" -ne 0 ]; then
  ck_fail "${n} shipped SKILL.md still declare(s) allowed-tools:"
  printf '%s\n' "${carriers}" | sed 's/^/  /' >&2
fi
grep -q 'REQ-YF-EMBED-006' "${TREE}/SPEC.md" 2>/dev/null \
  || ck_fail "REQ-YF-EMBED-006 (the allowed-tools decision-of-record) is absent from SPEC.md"
ck_done "no shipped SKILL.md relies on allowed-tools for scoping"
