---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #100: yf-plan plan_manager.py: align .yf/ layout to canonical short-name + canonical-first config read

- **Number:** 100
- **Title:** yf-plan plan_manager.py: align .yf/ layout to canonical short-name + canonical-first config read
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary
`skills/yf-plan/scripts/plan_manager.py` diverges from the canonical `.yf/<short>/` layout that the Rust `yf` binary emits, on **two** axes. Operator config set under the new layout is silently ignored, and a single skill's runtime state is split across two directories.

## Evidence
Canonical layout (Rust ground truth): every skill's per-repo config is `.yf/<short>/config.local.json` and runtime state is `.yf/<short>/preflight.json`, where `<short>` is the `yf-`-stripped name (`plan`, not `yf-plan`), produced by `resolve_skill`/`skill_short_name` (`yf/src/preflight.rs:244-264`). `read_config` precedence (`preflight.rs:466-487`): canonical subdir first, legacy root dotfile as fallback. `state_path` (`preflight.rs:489-492`) is also short-name.

`plan_manager.py` disagrees:
- **`plan_manager.py:143`** — `STATE_DIR = Path(".yf") / SKILL_NAME` with `SKILL_NAME = "yf-plan"` (line 141) ⇒ writes state to **`.yf/yf-plan/`** (FULL name), e.g. `landing.lock` (line 2058). The binary writes `preflight.json` to **`.yf/plan/`** (SHORT). The same skill's state is thus split across two dirs.
- **`plan_manager.py:142`** — `CONFIG_FILE = Path(f".{SKILL_NAME}.local.json")` ⇒ reads config **only** from the legacy root `.yf-plan.local.json`; never reads canonical `.yf/plan/config.local.json`. An operator migrated (or freshly scaffolded) under the new layout has `landing-strategy` / `validate-cmd` / `execute.worktree` silently ignored.

## Requested change
1. Change `STATE_DIR` to the short name (`.yf/plan/`), matching the binary. Use the same `yf-`-stripped resolver rather than the full `SKILL_NAME`.
2. Make config read `.yf/plan/config.local.json` **first**, with the legacy `.yf-plan.local.json` as fallback (mirror `preflight.rs` `read_config` precedence).
3. Migrate any existing `.yf/yf-plan/` state to `.yf/plan/` (preflight does **not** auto-migrate today — `preflight.rs:1005-1009` only writes the `/.yf/` gitignore anchor; `yf migrate` is the operator-invoked mover). Consider adding preflight auto-migration for this case.

## Refs
Full analysis: `docs/plans/plan-035-james-dixson-74d7ae/findings/exp-02-yf-layout-reality.md`. Filed as an Epic-3 output of plan-035 (#99); docs in plan-035 document current reality with a forward-pointer to this issue rather than "correcting" the spec ahead of the code.

