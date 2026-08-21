---
type: Reference
okf_spec: OKF-PLAN
id: sc15-full-validation
description: SC15 — the FULL validation tier over the merged tree (Issue 6.1)
---

# SC15 — the FULL tier over the merged tree

## Result

| Field | Value |
| :-- | :-- |
| Verb | `plan_manager.py validate-merged docs/plans/plan-050-james-dixson-d0414b --json` |
| Engine | **`change-validation`** (tier 1 of the layer-(b) precedence) |
| Tier | `full` |
| Commands | **45** |
| Passed | **45** |
| Failures | **0** |
| `first_failure` | `null` |
| Merged state | `main` at `cacb834` (bundle) + the staged `…-execute` merge, committed as `849003e` |

**SC15 is discharged: `validate-merged` reports 0 failures.**

## The order is the point

Phase 6 runs **merge-back first, then validate the MERGED state, then push** (plan-009
INV-4). The old order validated pre-merge, which cannot catch class-(b) integration
regressions — each change individually green, broken once integrated. So the merge of both
plan branches was **staged and left uncommitted** while this ran, and committed only on the
green.

## Which layer-(b) tier ran, and why that matters

The engine key reports `change-validation`, i.e. **tier 1**: this repo has an approved
root `CHANGE-VALIDATION.md` and the engine resolved. That is the real cross-plan safety net.

Had it fallen through to tier 3 — no engine, no `validate-cmd` — `validate-merged` would have
run **no layer-(b) suite at all** and emitted the cross-plan-not-checked notice, which must
never be presented as integration-safe. It did not: `validate_cmd_configured: false` is
recorded in the verdict, and the engine took precedence over it, as designed.

## What the 45 commands include

The FULL tier is the CI ∪ repo-checks superset. Relevant to this plan specifically:

- `cargo fmt --all -- --check`, `cargo clippy --workspace --all-targets -- -D warnings`,
  `cargo test --workspace`, `cargo test -p yf --test install_sync_e2e`
- `uv run _shared/sync.py --check` — every vendored copy byte-identical to its canonical
  (`doc_lint.py`, `plan_extract.py`, `SKILL.md`)
- `uv run _shared/test_doc_lint.py`, `_shared/test_plan_extract.py`,
  `_shared/test_dag_guard.py`, `_shared/test_pour_fidelity.py`
- `uv run _shared/doc_lint.py` — the whole-corpus lint
- `uv run skills/yf-plan/scripts/test_reconcile_step_resolution.py` (14 tests, three of them
  new for REQ-COMPLETE-004)
- `uv run skills/yf-plan/scripts/test_upstream_requirements.py` (13 tests, new for
  REQ-CLI-025 — SC8's behavioural mutation and SC10's coverage)
- `uv run skills/yf-plan/scripts/test_cli_enumeration.py` — REQ-CLI-006's set equality, which
  now has to account for the two verbs this plan added
