#!/usr/bin/env bash
# SC32 — the emitted resolver HONOURS a pre-set SKILL_DIR rather than overwriting it.
#
# The scriptable half of preferring the harness's own base directory: a harness that already
# knows where the skill lives must be able to say so, and a resolver that clobbers the answer
# it was given is not a resolver.
CHECK_NAME=check-env-var-wins
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
[ -d "${TREE}/skills" ] || ck_inconclusive "no skills/ under ${TREE}"
CK_RC=0

TMP="$(mktemp -d)" || ck_inconclusive "mktemp failed"
trap 'rm -rf "${TMP}"' EXIT
PRESET="${TMP}/preset-skill-dir"; mkdir -p "${PRESET}"

# Extract the resolver block from a shipped SKILL.md and run it with SKILL_DIR pre-set.
SRC="${TREE}/skills/yf-plan/SKILL.md"
[ -f "${SRC}" ] || ck_inconclusive "no yf-plan SKILL.md at ${SRC}"
# Extract by the REGION MARKERS. Keying on a `GIT_ROOT=` prefix was correct only for the old
# hand-written block; the generated one opens with the `yf skill-dir` call, so a prefix-based
# extraction silently produced an EMPTY block and the check reported INCONCLUSIVE forever.
block="$(awk '/BEGIN SKILL_DIR resolver/{f=1;next} /END SKILL_DIR resolver/{f=0} f' "${SRC}" \
          | sed -e '/^```/d')"
[ -n "${block}" ] || ck_inconclusive "could not extract a resolver block from ${SRC}"

got="$(SKILL_DIR="${PRESET}" bash -c "${block}"$'\n''printf "%s" "$SKILL_DIR"' 2>/dev/null)" || true
if [ "${got}" != "${PRESET}" ]; then
  ck_fail "a pre-set SKILL_DIR was overwritten: expected '${PRESET}', got '${got:-<empty>}'"
  ck_fail "a resolver that clobbers the answer it was given cannot be told where the skill is"
fi
ck_done "the emitted resolver honours a pre-set SKILL_DIR"
