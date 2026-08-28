#!/usr/bin/env bash
# SC18b — the removal is REVERSIBLE. Seeds a directory, quarantines it, restores it, and asserts
# BYTE-EQUALITY. So "reversible" is MEASURED rather than asserted.
#
# WHY THIS IS A REQUIREMENT AND NOT A NICETY. An `apply` that cannot be undone is the
# "overwrites with no backup" hazard this plan excludes on surface grounds while otherwise
# building a second instance of it on the skills surface. The remover deletes directories under
# $HOME on the strength of a marker check; a wrong classification with no undo is unrecoverable.
#
# WHAT MAKES THE ASSERTION MEANINGFUL. Byte-equality of the RESTORED tree, not mere existence:
# a "restore" that recreated an empty directory would satisfy an existence check while having
# destroyed the contents. The check therefore compares full recursive content.
#
# EXIT  0 restore is byte-exact  ·  1 it is not  ·  2 could not run
CHECK_NAME=check-quarantine-restore
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"

TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
YF="${YF_BIN:-${TREE}/target/debug/yf}"
[ -x "${YF}" ] || ck_inconclusive "no yf binary at ${YF} (build it, or set YF_BIN)"
ck_need diff
CK_RC=0

SANDBOX="$(mktemp -d)" || ck_inconclusive "cannot create a sandbox"
# Clean up on EVERY exit path — a check that leaves residue under /tmp is a check that will
# eventually be blamed for someone else's failure.
trap 'rm -rf "${SANDBOX}"' EXIT

ROOT="${SANDBOX}/.config/opencode/skills"
mkdir -p "${ROOT}"

# Seed a genuinely yf-authored copy: a real deployed skill carries a valid marker, so it is the
# only thing that classifies `owned-and-unmodified` and is therefore the only thing `apply`
# will move. A hand-built fixture would be `no-marker` and the test would pass vacuously by
# moving nothing.
SRC=""
for cand in "${HOME}/.agents/skills" "${HOME}/.claude/skills"; do
  for d in "${cand}"/yf-*; do
    if [ -f "${d}/SKILL.md" ] && grep -q '<!-- yf-skills:' "${d}/SKILL.md" 2>/dev/null; then
      SRC="${d}"; break 2
    fi
  done
done
[ -n "${SRC}" ] || ck_inconclusive "no marked yf skill copy available to seed the fixture"

NAME="$(basename "${SRC}")"
cp -R "${SRC}" "${ROOT}/${NAME}" || ck_inconclusive "cannot seed the fixture"
BEFORE="${SANDBOX}/before"
cp -R "${ROOT}/${NAME}" "${BEFORE}"

# APPLY. `--root` is explicit so the check never touches the operator's real trees.
OUT="$("${YF}" harness skills prune-private --root "${ROOT}" --apply --json 2>&1)" || {
  ck_inconclusive "prune-private --apply failed: ${OUT}"
}

if [ -d "${ROOT}/${NAME}" ]; then
  ck_fail "apply did not remove ${NAME} from the root — nothing to restore"
  exit "${CK_RC}"
fi

QUARANTINE="$(printf '%s' "${OUT}" | sed -n 's/.*"quarantine": *"\([^"]*\)".*/\1/p')"
[ -n "${QUARANTINE}" ] || ck_inconclusive "the verdict carried no \`quarantine\` path"
[ -d "${QUARANTINE}" ] || ck_fail "the quarantine directory ${QUARANTINE} does not exist — the \
tree was UNLINKED rather than moved, which is the hazard this check exists for"

# RESTORE via the documented one-liner the verdict itself emits. Running the emitted command
# rather than a hand-written equivalent is the point: an undo the operator is handed but that
# does not work is worse than none.
RESTORE="$(printf '%s' "${OUT}" | sed -n 's/.*"restore": *"\(.*\)".*/\1/p' | sed 's/\\"/"/g')"
[ -n "${RESTORE}" ] || ck_inconclusive "the verdict carried no \`restore\` command"
if ! eval "${RESTORE}" 2>/dev/null; then
  ck_fail "the emitted restore command failed: ${RESTORE}"
fi

if [ ! -d "${ROOT}/${NAME}" ]; then
  ck_fail "the restore did not put ${NAME} back at ${ROOT}"
  exit "${CK_RC}"
fi

# BYTE-EQUALITY, not existence: a restore that recreated an empty directory would satisfy an
# existence check while having destroyed the contents.
if ! diff -r "${BEFORE}" "${ROOT}/${NAME}" >/dev/null 2>&1; then
  ck_fail "the restored tree is NOT byte-identical to the original:"
  diff -r "${BEFORE}" "${ROOT}/${NAME}" 2>&1 | head -20 >&2
fi

ck_done "quarantine -> restore round-trips ${NAME} byte-exactly (quarantine: ${QUARANTINE})"
