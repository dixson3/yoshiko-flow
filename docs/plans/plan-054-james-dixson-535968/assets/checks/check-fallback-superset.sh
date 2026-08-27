#!/usr/bin/env bash
# SC4b — CONTAINMENT: for every anchor `yf skill-dir` can resolve, the fallback resolves the
# same path.
#
# STATED AS CONTAINMENT, NOT EQUALITY, and the asymmetry is deliberate: D-1's fallback searches
# a cwd-INCLUSIVE superset of yf's own anchors, so it legitimately resolves in places `yf`
# does not. Equality would fail on exactly that intended behaviour.
CHECK_NAME=check-fallback-superset
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
YF="${TREE}/target/debug/yf"
[ -x "${YF}" ] || ck_inconclusive "no debug binary at ${YF} (run: cargo build)"
CK_RC=0
TMP="$(mktemp -d)" || ck_inconclusive "mktemp failed"
trap 'rm -rf "${TMP}"' EXIT

SRC="${TREE}/skills/yf-plan/SKILL.md"
[ -f "${SRC}" ] || ck_inconclusive "no yf-plan SKILL.md at ${SRC}"
# Extract by the REGION MARKERS. Keying on a `GIT_ROOT=` prefix was correct only for the old
# hand-written block; the generated one opens with the `yf skill-dir` call, so a prefix-based
# extraction silently produced an EMPTY block and the check reported INCONCLUSIVE forever.
block="$(awk '/BEGIN SKILL_DIR resolver/{f=1;next} /END SKILL_DIR resolver/{f=0} f' "${SRC}" \
          | sed -e '/^```/d')"
[ -n "${block}" ] || ck_inconclusive "could not extract a resolver block from ${SRC}"

checked=0
for root in ".claude/skills" ".agents/skills" ".pi/agent/skills" ".config/opencode/skills"; do
  home="${TMP}/$(printf '%s' "${root}" | tr '/.' '__')"
  mkdir -p "${home}/${root}/yf-plan"
  printf -- '---\nname: yf-plan\n---\n' > "${home}/${root}/yf-plan/SKILL.md"
  yf_out="$(cd "${TMP}" && HOME="${home}" "${YF}" skill-dir yf-plan 2>/dev/null)" || continue
  [ -n "${yf_out}" ] || continue
  checked=$((checked + 1))
  # CLEAR SKILL_DIR FIRST. The emitted resolver is ENV-VAR FIRST by design (Issue 1.7), so an
  # inherited SKILL_DIR short-circuits the whole block and the "fallback" never runs — the check
  # would then be comparing yf's answer against an ambient value and calling the difference a
  # containment failure. Measured: `recheck-criteria` runs criterion commands with a child env
  # that carries SKILL_DIR, and this check reported CONTAINMENT BROKEN at three anchors while
  # passing standalone. The variable under test must not be supplied by the tester.
  fb_out="$(cd "${TMP}" && env -u SKILL_DIR HOME="${home}" bash -c "${block}"$'\n''printf "%s" "$SKILL_DIR"' 2>/dev/null)" || true
  [ "${fb_out}" = "${yf_out}" ] \
    || ck_fail "containment broken at ${root}: yf resolved '${yf_out}' but the fallback resolved '${fb_out:-<nothing>}'"
done
[ "${checked}" -gt 0 ] || { ck_fail "\`yf skill-dir\` resolved at NO anchor, so containment is untestable — the verb is unimplemented"; exit "${CK_RC}"; }
ck_done "the fallback resolves the same path at all ${checked} anchor(s) yf resolves"
