---
type: Reference
okf_spec: OKF-PLAN
id: full-tier-record
description: The dated FULL-tier validation run over plan-053's MERGED tree (Issue 7.1, SC16)
---

# FULL-tier validation over the MERGED tree

## Why this is a RECORD and not a re-run

SC16 asserts on **this file** rather than re-executing the tier inside the criteria check.
Two measured defects forced that (pass-2 C19, pass-3 C38):

1. the criterion's earlier command path was wrong and measured exit 2 `Failed to spawn`;
2. `recheck-criteria` turns a `TimeoutExpired` into `status: inconclusive` and **continues** --
   never counted, never in `failed` -- while the FULL tier (`cargo clippy --workspace
   --all-targets`, `cargo test --workspace`, and ~48 more rows) far exceeds its 300 s default.

So **the plan's broadest criterion would have timed out, recorded inconclusive, and let
completion proceed at exit 0** -- this plan's own thesis defect, occurring inside this plan.
Follows plan-050's `assets/sc15-full-validation.md` precedent.

## Verdict

| Field | Value |
| :-- | :-- |
| **Date (UTC)** | 2026-08-26T02:10:34Z |
| **Command** | `uv run ${SKILL_DIR}/scripts/plan_manager.py validate-merged docs/plans/plan-053-james-dixson-4015d3 --json` |
| **Engine** | `change-validation` (tier `full`) |
| **Verdict** | **PASS** |
| **Rows** | 51 -- 51 pass, 0 non-pass |
| **First failure** | none |
| **Tree** | the MERGED state: `main` with `plan-053-james-dixson-4015d3-execute` merged `--no-ff`, staged and validated **before** the merge commit |
| **HEAD at run** | `827e543c5414ce331356209a0a50b9a6ec8972bb` (the merge target's tip before the merge commit) |

The tree validated is the **merged** one, per SS6.1's reordering (plan-009 INV-4): validating
pre-merge cannot catch class-(b) integration regressions, where each change is individually
green and broken only when integrated.

## Every row

| command | status | rc |
| :-- | :-- | --: |
| `cargo fmt --all -- --check` | pass | 0 |
| `cargo clippy --workspace --all-targets -- -D warnings` | pass | 0 |
| `cargo test --workspace` | pass | 0 |
| `cargo test -p yf --test install_sync_e2e` | pass | 0 |
| `uv run --with pytest python3 -m pytest _shared/test_sync.py -q` | pass | 0 |
| `uv run --with pytest python3 -m pytest skills/yf-beads-hygiene/scripts/test_beads_hygiene.py -q` | pass | 0 |
| `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q` | pass | 0 |
| `uv run skills/yf-beads-upstream/scripts/check_prescriptive_push.py` | pass | 0 |
| `uv run skills/yf-beads-upstream/scripts/check_gh_direct.py` | pass | 0 |
| `uv run skills/yf-change-validation/scripts/test_change_validation.py` | pass | 0 |
| `uv run --with pytest python3 -m pytest skills/yf-markdown-lint/scripts/test_markdown_lint.py -q` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_worktree.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_close_cascade.py` | pass | 0 |
| `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_stamp_tracker.py -q` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_complete_gate.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_review_verdict.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_config_tiers.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_classify_deliverable.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_close_contract.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_verify_reconcile.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_audit_close.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_reconcile_step_resolution.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_update_status_idempotent.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_cascade_root_resolution.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_epic_ref_audit.py` | pass | 0 |
| `uv run scripts/check_frontmatter.py` | pass | 0 |
| `uv run scripts/check_skill_script_refs.py` | pass | 0 |
| `uv run scripts/test_check_skill_script_refs.py` | pass | 0 |
| `uv run skills/yf-research/scripts/test_link_normalizer.py` | pass | 0 |
| `uv run skills/yf-research/scripts/test_credibility_scorer.py` | pass | 0 |
| `uv run _shared/sync.py --check` | pass | 0 |
| `uv run skills/yf-herdr/scripts/test_launch_contract.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_autonomy.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_gates.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_retrospective.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_cli_enumeration.py` | pass | 0 |
| `uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q` | pass | 0 |
| `uv run _shared/doc_lint.py` | pass | 0 |
| `uv run _shared/test_doc_lint.py` | pass | 0 |
| `uv run _shared/test_plan_extract.py` | pass | 0 |
| `uv run _shared/test_dag_guard.py` | pass | 0 |
| `bash docs/plans/plan-049-james-dixson-725bc0/scripts/gate-run.sh docs/plans/plan-049-james-dixson-725bc0/scripts/gate-dagguard.sh` | pass | 0 |
| `bash docs/plans/plan-049-james-dixson-725bc0/scripts/gate-run.sh docs/plans/plan-049-james-dixson-725bc0/scripts/gate-cellcheck.sh` | pass | 0 |
| `uv run _shared/test_pour_fidelity.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_review_count.py` | pass | 0 |
| `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_update_status_gate.py -q` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_upstream_requirements.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_gate_consistency.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_verify_beads.py` | pass | 0 |
| `uv run skills/yf-plan/scripts/test_retrospective_fields.py` | pass | 0 |
| `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh verify-partition` | pass | 0 |
