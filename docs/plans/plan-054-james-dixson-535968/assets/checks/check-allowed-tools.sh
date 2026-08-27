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

# THE CRITERION IS "RELIES ON ... FOR SCOPING", NOT "DECLARES". An earlier draft of this check
# demanded ZERO carriers, which contradicts both SC33's own wording and REQ-YF-EMBED-006, whose
# text RETAINS the key for claude-code's benefit and forbids only DEPENDING on it for a
# portability, safety or scoping guarantee. Deleting the key would have removed a real
# claude-code benefit to satisfy a check that had over-read its own criterion.
#
# So: a carrier is fine, an UNANNOTATED carrier is not. Each must record the claude-only caveat,
# so no author can mistake the list for a cross-harness constraint.
carriers="$(grep -rl '^allowed-tools:' "${TREE}/skills" --include='SKILL.md' 2>/dev/null || true)"
if [ -n "${carriers}" ]; then
  while IFS= read -r f; do
    [ -n "${f}" ] || continue
    grep -q 'REQ-YF-EMBED-006' "${f}" \
      || ck_fail "${f#${TREE}/} declares allowed-tools with no claude-only caveat — nothing stops an author reading it as a cross-harness scoping guarantee"
  done <<< "${carriers}"
fi
grep -q 'REQ-YF-EMBED-006' "${TREE}/SPEC.md" 2>/dev/null \
  || ck_fail "REQ-YF-EMBED-006 (the allowed-tools decision-of-record) is absent from SPEC.md"
ck_done "no shipped SKILL.md relies on allowed-tools for scoping"
