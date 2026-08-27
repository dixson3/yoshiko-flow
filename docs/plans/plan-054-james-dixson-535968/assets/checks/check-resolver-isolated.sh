#!/usr/bin/env bash
# SC3 — SKILL_DIR resolves under a HOME containing ONLY the pi root, and only the opencode root.
#
# BOTH ISOLATED HOMES ARE REQUIRED. Run against a normal HOME this passes today by ACCIDENT:
# ~/.claude/skills exists, so the claude-code copy answers and the gap is invisible. That
# accidental green IS the live defect (EXP-002 reproduced it in both harnesses).
CHECK_NAME=check-resolver-isolated
. "$(dirname "${BASH_SOURCE[0]}")/_common.sh"
TREE="$(ck_tree)" || ck_inconclusive "cannot resolve the tree under test"
YF="${TREE}/target/debug/yf"
[ -x "${YF}" ] || ck_inconclusive "no debug binary at ${YF} (run: cargo build)"
CK_RC=0

TMP="$(mktemp -d)" || ck_inconclusive "mktemp failed"
trap 'rm -rf "${TMP}"' EXIT

_probe() {
  # _probe <label> <relative-skills-root>
  # SPLIT DELIBERATELY. A single `local a=… b="${a}"` declares every name before any
  # assignment lands, so the later reference reads an UNSET local and `set -u` aborts the
  # whole check with "unbound variable" — an INCONCLUSIVE dressed as a crash.
  local label="$1"
  local root="$2"
  local home="${TMP}/${label}"
  mkdir -p "${home}/${root}/yf-plan"
  printf -- '---\nname: yf-plan\n---\n' > "${home}/${root}/yf-plan/SKILL.md"
  [ -e "${home}/.claude/skills" ] && { ck_fail "${label} sandbox is not isolated"; return; }
  local out rc
  out="$(cd "${TMP}" && HOME="${home}" "${YF}" skill-dir yf-plan 2>&1)"; rc=$?
  if printf '%s' "${out}" | grep -qiE 'unrecognized subcommand|unexpected argument'; then
    ck_fail "${label}: \`yf skill-dir\` does not exist (REQ-YF-CLI-005 unimplemented)"; return
  fi
  if [ "${rc}" -ne 0 ]; then
    ck_fail "${label}: did not resolve under a ${label}-only HOME (exit ${rc}) — this is the machine on which every script-backed skill dies"; return
  fi
  case "${out}" in
    *"${root}/yf-plan"*) : ;;
    *) ck_fail "${label}: resolved to '${out}', not the ${label} destination — resolving to the claude-code copy is the silent-wrong-tree half of the defect, not a pass" ;;
  esac
}
_probe pi       ".pi/agent/skills"
_probe opencode ".config/opencode/skills"
ck_done "SKILL_DIR resolves under a pi-only and an opencode-only HOME"
