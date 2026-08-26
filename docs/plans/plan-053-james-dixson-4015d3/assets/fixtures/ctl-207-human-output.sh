#!/usr/bin/env bash
# ctl-207-human-output — the HUMAN `resume-scan` output names the epic state (#207).
#
# A FIXTURE per redcheck.sh's definition: exits 0 iff the asserted behaviour holds.
#
# THE SURFACE EXP-005 CALLED "WORSE THAN THE JSON". On a DANGLING ref the human path prints
#
#     Epic yf-BURNED (source: plan_md)
#       descendants: 0  counts: {}
#       open work remaining (non-closed, non-gate): 0
#       no stuck beads
#
# — which is exactly what a legitimately FINISHED plan prints. `epic_resolves` has been in the
# JSON since plan-044 and is never mentioned here, so the one surface an operator actually
# reads cannot distinguish "done" from "the pointer is dead".
#
# ASSERTED AGAINST A FIXTURE BUNDLE WITH A STALE POINTER (pass-2 C24). The earlier form tested
# a LIVE plan, which (a) tested the one case that was never broken, (b) hard-coded another
# repo's bead state, and (c) would pass on any constant containing the word "state".
#
# (c) IS WHY THERE ARE TWO ARMS. A banner printed unconditionally satisfies arm 1 and FAILS
# arm 2 — the output must DISTINGUISH the states, not merely mention that states exist.
#
# Tree under test: $YF_TREE (set by redcheck.sh).
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
: "${YF_TREE:=$(cd "${HERE}/../../../../.." && pwd)}"
PM="${YF_TREE}/skills/yf-plan/scripts/plan_manager.py"

[ -f "${PM}" ] || { echo "ctl-207-human: HARNESS — no plan_manager at ${PM}" >&2; exit 2; }
command -v bd >/dev/null 2>&1 || {
  echo "ctl-207-human: HARNESS — bd is not on PATH, so every epic would classify 'unknown'" >&2
  echo "ctl-207-human: and the stale-vs-none distinction this control asserts is unobservable." >&2
  exit 2; }

work="$(mktemp -d)"
trap 'rm -rf "${work}"' EXIT

_bundle() {  # _bundle <name> <epic-id-or-empty>
  local d="${work}/$1" epic="${2-}"
  mkdir -p "${d}"
  {
    printf -- '---\ntype: Plan\nokf_spec: OKF-PLAN\nid: %s\n' "$1"
    [ -n "${epic}" ] && printf 'epic: %s\n' "${epic}"
    printf -- '---\n# Plan: %s\n\n**ID:** %s\n**Status:** executing\n' "$1" "$1"
    [ -n "${epic}" ] && printf '**Epic:** %s\n' "${epic}"
    printf '\n## Objective\nfixture\n\n## Motivation\nfixture\n'
  } > "${d}/plan.md"
  echo "${d}"
}

# A pointer to a bead id that CANNOT exist. Not another plan's real epic — the whole point of
# C24 is that this fixture hard-codes no live bead state.
STALE_DIR="$(_bundle plan-207-stale-dddddd yf-BURNED-207-FIXTURE-DOES-NOT-EXIST)"
NONE_DIR="$(_bundle plan-207-none-eeeeee)"

_scan() { (cd "${YF_TREE}" && env -u VIRTUAL_ENV uv run "${PM}" resume-scan "$1" 2>&1); }

stale_out="$(_scan "${STALE_DIR}")"
none_out="$(_scan "${NONE_DIR}")"

bad=()

# ---- ARM 1: the stale bundle's HUMAN output must NAME the state -------------------------
if ! printf '%s' "${stale_out}" | grep -qi 'stale'; then
  bad+=("ARM 1: the human \`resume-scan\` output for a bundle whose pointer is DANGLING does \
not name the state. This is the surface an operator reads, and it currently prints the same \
'descendants: 0 / no stuck beads' a FINISHED plan prints. Got:
$(printf '%s' "${stale_out}" | sed 's/^/      /')")
fi

# It must also still report the epic id — naming the state must not replace the diagnosis.
if ! printf '%s' "${stale_out}" | grep -q 'yf-BURNED-207-FIXTURE-DOES-NOT-EXIST'; then
  bad+=("ARM 1: the output no longer reports the epic id it could not resolve. Naming the \
state must ADD to the diagnosis, not replace it.")
fi

# ---- ARM 2: THE DISTINGUISHING ARM ------------------------------------------------------
# A bundle with NO epic is a DIFFERENT state (`none`). If the word `stale` shows up here too,
# what arm 1 observed was a constant, not a state report. This arm is what makes arm 1 mean
# something, and it hard-codes no live bead state either.
if printf '%s' "${none_out}" | grep -qi 'stale'; then
  bad+=("ARM 2 (THE DISTINGUISHING ARM): a bundle with NO epic at all also reports 'stale'. \
Arm 1 therefore observed a CONSTANT, not a state report — which is precisely the failure \
pass-2 C24 identified in this control's earlier form. Got:
$(printf '%s' "${none_out}" | sed 's/^/      /')")
fi

# ...and arm 2 must still say something intelligible about being a fresh run.
if ! printf '%s' "${none_out}" | grep -qiE 'no epic|fresh run|none'; then
  bad+=("ARM 2: the no-epic bundle's output is not intelligible as 'nothing recorded yet'. \
Got:
$(printf '%s' "${none_out}" | sed 's/^/      /')")
fi

if [ "${#bad[@]}" -gt 0 ]; then
  echo "ctl-207-human: ${#bad[@]} failure(s):" >&2
  for b in "${bad[@]}"; do echo "ctl-207-human:   ${b}" >&2; done
  exit 1
fi
echo "ctl-207-human: the human resume-scan output names the stale state, and DISTINGUISHES it from 'none'"
