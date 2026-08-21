#!/usr/bin/env bash
# _beadsenv.sh — shared setup for the Epic-1 scenarios. NOT a fixture; sourced by them.
#
# Builds a THROWAWAY beads repo in $(mktemp -d), pours the real `plan-execute` molecule into
# it, and seeds a minimal plan bundle. Everything happens inside the temp dir; the live
# project DB is never touched. This is what makes the Epic-1 controls `probe` class: cheap,
# self-cleaning, and mutating nothing but their own scratch state.
#
# Exports: SCEN_DIR, PLAN_DIR, EPIC, START_GATE, START_GATE_BEAD, PLAN_ID
# Requires: YF_TREE (the checkout under test), bd on PATH.

set -uo pipefail

scen_fail() { echo "${SCEN_NAME:-scenario}: HARNESS — $*" >&2; exit 2; }

beadsenv_setup() {
  command -v bd >/dev/null 2>&1 || scen_fail "bd is not on PATH"
  [ -d "${YF_TREE}" ] || scen_fail "YF_TREE does not exist: ${YF_TREE}"

  SCEN_DIR="$(mktemp -d)"
  export SCEN_DIR
  # Both exit paths, so a probe leaves no residue however it ends.
  trap 'rm -rf "${SCEN_DIR}"' EXIT

  ( cd "${SCEN_DIR}" \
      && git init -q . \
      && git -c user.email=f@f -c user.name=f commit -q --allow-empty -m init ) \
    || scen_fail "could not create the scratch git repo"

  ( cd "${SCEN_DIR}" && bd init >/dev/null 2>&1 ) || scen_fail "bd init failed in the scratch repo"

  mkdir -p "${SCEN_DIR}/.beads/formulas"
  cp "${YF_TREE}/skills/yf-plan/formulas/plan-execute.formula.toml" \
     "${SCEN_DIR}/.beads/formulas/" || scen_fail "could not stage the plan-execute formula"

  PLAN_ID="plan-999-fixture-eeeeee"
  PLAN_DIR="docs/plans/${PLAN_ID}"
  mkdir -p "${SCEN_DIR}/${PLAN_DIR}"

  local pour
  pour="$(cd "${SCEN_DIR}" && bd mol pour plan-execute \
            --var objective="fixture scenario" --var plan_dir="${PLAN_DIR}" --json 2>&1)" \
    || scen_fail "bd mol pour failed: ${pour}"

  EPIC="$(printf '%s' "${pour}" | python3 -c 'import json,sys; d=json.load(sys.stdin); d=d[0] if isinstance(d,list) else d; print(d["new_epic_id"])')"
  START_GATE="$(printf '%s' "${pour}" | python3 -c 'import json,sys; d=json.load(sys.stdin); d=d[0] if isinstance(d,list) else d; print(d["id_mapping"]["plan-execute.start-gate"])')"
  START_GATE_BEAD="$(printf '%s' "${pour}" | python3 -c 'import json,sys; d=json.load(sys.stdin); d=d[0] if isinstance(d,list) else d; print(d["id_mapping"]["plan-execute.gate-start-gate"])')"
  [ -n "${EPIC}" ] && [ -n "${START_GATE}" ] && [ -n "${START_GATE_BEAD}" ] \
    || scen_fail "pour did not yield the epic + both gate beads"

  # A minimal, conformant plan.md carrying the **Epic:** field the verbs re-derive from.
  cat > "${SCEN_DIR}/${PLAN_DIR}/plan.md" <<PLANMD
---
type: Plan
okf_spec: OKF-PLAN
id: ${PLAN_ID}
author: fixture
created: 2026-08-21
status: executing
---
# Plan: fixture scenario

**ID:** ${PLAN_ID}
**Author:** fixture
**Created:** 2026-08-21
**Status:** executing
**Epic:** ${EPIC}

## Objective
fixture scenario
PLANMD
  : > "${SCEN_DIR}/${PLAN_DIR}/log.md"

  export PLAN_ID PLAN_DIR EPIC START_GATE START_GATE_BEAD
}

# bead_field <id> <field> -> the field's value, or the empty string
bead_field() {
  ( cd "${SCEN_DIR}" && bd show "$1" --json 2>/dev/null ) | python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
d = d[0] if isinstance(d, list) else d
print(d.get('$2') or '')
"
}

pm() {
  ( cd "${SCEN_DIR}" && env -u VIRTUAL_ENV uv run "${YF_TREE}/skills/yf-plan/scripts/plan_manager.py" "$@" )
}
