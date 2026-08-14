---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #101: yf-change-validation: read canonical .yf/plan/config.local.json for validate-cmd seed

- **Number:** 101
- **Title:** yf-change-validation: read canonical .yf/plan/config.local.json for validate-cmd seed
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary
`skills/yf-change-validation/scripts/change_validation.py:44` reads yf-plan's `validate-cmd` seed **only** from the legacy root `.yf-plan.local.json`, ignoring the canonical `.yf/plan/config.local.json`. Low severity (a one-time inference seed), but it should honor the canonical location.

## Evidence
Canonical config precedence (Rust `read_config`, `yf/src/preflight.rs:466-487`): `.yf/<short>/config.local.json` first, legacy root dotfile as fallback. `change_validation.py:44` (`VALIDATE_CMD_CONFIG`) reads legacy-only.

## Requested change
Read `.yf/plan/config.local.json` first for the validate-cmd seed, with the legacy `.yf-plan.local.json` as fallback — mirror the binary's precedence.

## Refs
`docs/plans/plan-035-james-dixson-74d7ae/findings/exp-02-yf-layout-reality.md`. Epic-3 output of plan-035 (#99).

