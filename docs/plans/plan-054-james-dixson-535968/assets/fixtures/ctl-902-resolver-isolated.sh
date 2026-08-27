#!/usr/bin/env bash
# ctl-902-resolver-isolated — grades REQ-YF-CLI-005 / plan-054 Issue 1.1.
#
# A PLAN-LOCAL control (reserved 9xx range, no upstream issue): the release cannot ship
# without it, but no filed issue grades it.
#
# ASSERTED BEHAVIOUR (post-fix): `yf skill-dir <name>` resolves an installed skill under a
# harness destination `yf` itself installs to, IN ISOLATION from claude-code.
#
# THE DEFECT THIS EXISTS FOR (EXP-002, reproduced live in real pi and opencode): the
# `SKILL_DIR` `find` idiom embedded in 19 files searches six roots, and neither
# `~/.pi/agent/skills` nor `~/.config/opencode/skills` is among them. On a pi-only machine
# every script-backed skill dies at `ERROR: <skill> directory not found`; on a mixed machine
# it silently resolves to the CLAUDE-CODE copy, so a skill's prose and its scripts come from
# different trees. The install reports success either way.
#
# WHY THE HOME IS ISOLATED, AND WHY THAT IS THE ENTIRE POINT. Run against a normal HOME this
# would pass today by ACCIDENT — `~/.claude/skills` exists there, so the claude-code copy
# answers and the pi gap is invisible. That accidental green is the live defect itself. So
# the fixture builds a HOME containing a pi destination AND NO CLAUDE-CODE ONE.
#
# EXIT  0 resolved to the pi destination  ·  1 not resolved, or resolved elsewhere  ·  2 could not run
set -uo pipefail

# YF_TREE SELF-RESOLUTION (added at close). A fixture is invoked TWO ways: by `redcheck.sh`,
# which exports YF_TREE, and DIRECTLY by its Success Criterion's Verification command, which does
# not. Exiting 2 on an unset YF_TREE made every criterion that invokes a fixture directly
# UNSATISFIABLE — SC7, SC7b, SC8, SC23 and SC24 could never pass, in either direction. That is a
# criterion that cannot be met, which is worse than one that cannot fail: it halts the close
# chain over nothing.
#
# So resolve it the way redcheck.sh does: the plan's execution worktree while its branch is still
# UNMERGED, else the repo root. A genuinely unresolvable tree is still INCONCLUSIVE.
if [ -z "${YF_TREE:-}" ]; then
  _fx_here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  _fx_plan="$(cd "${_fx_here}/../.." && pwd)"
  _fx_root="$(git -C "${_fx_plan}" rev-parse --show-toplevel 2>/dev/null)" || _fx_root=""
  _fx_id="$(basename "${_fx_plan}")"
  if [ -n "${_fx_root}" ] && [ -d "${_fx_root}/.worktrees/${_fx_id}" ] \
     && ! git -C "${_fx_root}" merge-base --is-ancestor "${_fx_id}-execute" main 2>/dev/null; then
    YF_TREE="${_fx_root}/.worktrees/${_fx_id}"
  else
    YF_TREE="${_fx_root}"
  fi
  export YF_TREE
  unset _fx_here _fx_plan _fx_root _fx_id
fi
[ -n "${YF_TREE:-}" ] || { echo "ctl-902: INCONCLUSIVE — YF_TREE is not set" >&2; exit 2; }
YF="${YF_TREE}/target/debug/yf"
[ -x "${YF}" ] || { echo "ctl-902: INCONCLUSIVE — no debug binary at ${YF} (run: cargo build)" >&2; exit 2; }

TMP="$(mktemp -d)" || { echo "ctl-902: INCONCLUSIVE — mktemp failed" >&2; exit 2; }
trap 'rm -rf "${TMP}"' EXIT

FAKE_HOME="${TMP}/home"
PI_SKILLS="${FAKE_HOME}/.pi/agent/skills"
mkdir -p "${PI_SKILLS}/yf-plan"
printf -- '---\nname: yf-plan\n---\n' > "${PI_SKILLS}/yf-plan/SKILL.md"
# Deliberately NO ~/.claude/skills — an accidental claude-code hit is the failure mode.
[ -e "${FAKE_HOME}/.claude/skills" ] && { echo "ctl-902: INCONCLUSIVE — sandbox is not isolated" >&2; exit 2; }

out="$(cd "${TMP}" && HOME="${FAKE_HOME}" "${YF}" skill-dir yf-plan 2>&1)"; rc=$?

# ORDER IS LOAD-BEARING: THE UNRECOGNISED-SUBCOMMAND TEST RUNS FIRST.
#
# `clap` exits **2** for an unknown subcommand, and REQ-YF-CLI-005 also assigns **2** to "the
# lookup could not be performed". The two collide on the exit code alone, so branching on
# `rc == 2` first classified the PRE-IMPLEMENTATION STATE — the plain red this control exists
# to record — as INCONCLUSIVE, which `record-red` refuses to write. The fixture would then
# have been unrecordable for the entire window in which it is supposed to be red. The
# stderr text is what separates the two facts, so it is read before the code.
if printf '%s' "${out}" | grep -qiE 'unrecognized subcommand|unexpected argument|invalid subcommand'; then
  echo "ctl-902: FAIL — \`yf skill-dir\` does not exist yet (REQ-YF-CLI-005 unimplemented)." >&2
  exit 1
fi
if [ "${rc}" -eq 2 ]; then
  echo "ctl-902: INCONCLUSIVE — \`yf skill-dir\` reported it could not perform the lookup: ${out}" >&2
  exit 2
fi
if [ "${rc}" -ne 0 ]; then
  echo "ctl-902: FAIL — \`yf skill-dir yf-plan\` did not resolve under a pi-only HOME (exit ${rc})." >&2
  echo "ctl-902: this is the pi-only machine EXP-002 reproduced: every script-backed skill dies." >&2
  exit 1
fi
case "${out}" in
  *"/.pi/agent/skills/yf-plan"*)
    echo "ctl-902: resolved to the pi destination under an isolated HOME"; exit 0 ;;
  *)
    echo "ctl-902: FAIL — resolved to '${out}', which is not the pi destination." >&2
    echo "ctl-902: resolving somewhere else under a pi-only HOME is the silent-wrong-tree half" >&2
    echo "ctl-902: of the defect, not a pass." >&2
    exit 1 ;;
esac
