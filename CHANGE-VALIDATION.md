# CHANGE-VALIDATION.md

> APPROVED dogfood manifest for the beads-skills repo (plan-015 E.1). Seeded by
> `change_validation.py infer`, reviewed, `website` build rows trimmed (deploy-only,
> not a validation gate), and approved. yf-plan §6.1.5 layer (b) now delegates here.
> Executable-only: `yf-drift-check` is excluded (prose/LLM trigger, not a runnable
> command). To roll delegation back to `validate-cmd`/notice, set `approved: no`.
>
> plan-042 (#157): added the `sync-e2e` row and `yf/profiles/**` trigger scope. The
> profiles had NO glob, so editing a `consent_required` entry — the flag the install-time
> consent gate keys on — fired no validation at all. The row names a **test target**
> (`--test install_sync_e2e`) rather than a name filter on purpose: a missing target is a
> hard error, whereas a **cargo** name filter matching nothing exits 0 and passes vacuously.
>
> plan-046 Issue 1.3 — **correction, measured.** The "passes vacuously" rationale above is
> **cargo-specific and must not be generalised to the `uv`/pytest rows.** Executed on this
> tree: `pytest -k <no-match>` exits **5** (`31 deselected`) and `pytest <missing-file>` exits
> **4** — neither is a vacuous pass. The real reason the pytest rows name an explicit **file**
> target is that exit **4** on a moved or renamed target is a loud failure, so vendored-copy
> drift cannot hide behind a green run.

> **Two `Incubator/*` §3 rows are a PERMANENT no-op in THIS repository, and are kept anyway**
> (plan-049 Issue 4.5). `Incubator/*/plans/**` and `Incubator/*/research/**` select nothing here
> — there is no `Incubator/` directory — and never will. They are **not dead rows**: this
> manifest schema is shared across vaults, and in an incubator-using vault both are load-bearing.
> Deleting them here would break those vaults to remove two lines that cost nothing. Their
> inertness is a fact to document, not work to schedule.
>
> Relatedly, and also settled: the **research** selection vacuity D-5 was filed for is **CLOSED**.
> plan-048's Issue 2.7 instantiated the research document types, so `doc_lint --path` now returns
> `files_checked: 1` for a real research file and `0` for a nonexistent one — the two are
> distinguishable, which was the whole concern. The residual "these checks cannot fail" is
> **REQ-DATA-045 policy, not a defect**: off the plan-bundle axis `bundle_status` is null, so an
> `E` has no softening available and every research check ships at `W` deliberately. Promoting
> one to `E` is permitted only with a measured corpus pass recorded beside it.

## 0. Status

approved: yes

## 1. Tiers

### fast

| id | cmd | cwd | timeout |
|:--|:--|:--|--:|
| `cargo-fmt` | `cargo fmt --all -- --check` |  |  |
| `cargo` | `cargo test --workspace` |  |  |
| `sync-e2e` | `cargo test -p yf --test install_sync_e2e` |  |  |
| `harness-e2e` | `cargo test -p yf --test harness_cross_e2e` |  |  |
| `uv` | `uv run --with pytest python3 -m pytest _shared/test_sync.py -q` |  |  |
| `uv-run` | `uv run --with pytest python3 -m pytest skills/yf-beads-hygiene/scripts/test_beads_hygiene.py -q` |  |  |
| `uv-with` | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q` |  |  |
| `bup-prescriptive-push` | `uv run skills/yf-beads-upstream/scripts/check_prescriptive_push.py` |  |  |
| `bup-gh-direct` | `uv run skills/yf-beads-upstream/scripts/check_gh_direct.py` |  |  |
| `bup-no-universe-fanout` | `uv run skills/yf-beads-upstream/scripts/check_no_universe_fanout.py --check-timeouts` |  |  |
| `bup-fanout-controls` | `uv run skills/yf-beads-upstream/scripts/test_check_no_universe_fanout.py` |  |  |
| `uv-skills` | `uv run skills/yf-change-validation/scripts/test_change_validation.py` |  |  |
| `uv-pytest` | `uv run --with pytest python3 -m pytest skills/yf-markdown-lint/scripts/test_markdown_lint.py -q` |  |  |
| `uv-yf` | `uv run skills/yf-plan/scripts/test_worktree.py` |  |  |
| `uv-yf-cascade` | `uv run skills/yf-plan/scripts/test_close_cascade.py` |  |  |
| `uv-yf-complete-gate` | `uv run skills/yf-plan/scripts/test_complete_gate.py` |  |  |
| `uv-yf-review-verdict` | `uv run skills/yf-plan/scripts/test_review_verdict.py` |  |  |
| `uv-yf-stamp-tracker` | `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_stamp_tracker.py -q` |  |  |
| `uv-yf-config-tiers` | `uv run skills/yf-plan/scripts/test_config_tiers.py` |  |  |
| `uv-yf-classify` | `uv run skills/yf-plan/scripts/test_classify_deliverable.py` |  |  |
| `uv-yf-close-contract` | `uv run skills/yf-plan/scripts/test_close_contract.py` |  |  |
| `uv-yf-intake-lint` | `uv run skills/yf-plan/scripts/test_intake_lint_binding.py` |  |  |
| `uv-yf-verify-reconcile` | `uv run skills/yf-plan/scripts/test_verify_reconcile.py` |  |  |
| `uv-yf-audit-close` | `uv run skills/yf-plan/scripts/test_audit_close.py` |  |  |
| `uv-yf-reconcile-step` | `uv run skills/yf-plan/scripts/test_reconcile_step_resolution.py` |  |  |
| `uv-yf-status-idem` | `uv run skills/yf-plan/scripts/test_update_status_idempotent.py` |  |  |
| `uv-yf-cascade-root` | `uv run skills/yf-plan/scripts/test_cascade_root_resolution.py` |  |  |
| `uv-yf-epic-ref` | `uv run skills/yf-plan/scripts/test_epic_ref_audit.py` |  |  |
| `frontmatter` | `uv run scripts/check_frontmatter.py` |  |  |
| `skill-script-refs` | `uv run scripts/check_skill_script_refs.py` |  |  |
| `skill-script-refs-tests` | `uv run scripts/test_check_skill_script_refs.py` |  |  |
| `uv-research` | `uv run skills/yf-research/scripts/test_link_normalizer.py` |  |  |
| `uv-research-cred` | `uv run skills/yf-research/scripts/test_credibility_scorer.py` |  |  |
| `uv-_shared` | `uv run _shared/sync.py --check` |  |  |
| `uv-herdr-launch` | `uv run skills/yf-herdr/scripts/test_launch_contract.py` |  |  |
| `uv-yf-autonomy` | `uv run skills/yf-plan/scripts/test_autonomy.py` |  |  |
| `uv-yf-gates` | `uv run skills/yf-plan/scripts/test_gates.py` |  |  |
| `uv-yf-retro` | `uv run skills/yf-plan/scripts/test_retrospective.py` |  |  |
| `uv-yf-cli-enum` | `uv run skills/yf-plan/scripts/test_cli_enumeration.py` |  |  |
| `uv-yf-review-agent` | `uv run skills/yf-plan/scripts/test_review_agent_contract.py` |  |  |
| `uv-okf` | `uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q` |  |  |
| `okf-hygiene-tests` | `uv run skills/yf-okf-hygiene/scripts/test_okf_hygiene.py` |  |  |
| `doclint` | `uv run _shared/doc_lint.py` |  |  |
| `doclint-tests` | `uv run _shared/test_doc_lint.py` |  |  |
| `plan-extract` | `uv run _shared/test_plan_extract.py` |  |  |
| `dag-guard` | `uv run _shared/test_dag_guard.py` |  |  |
| `gate-dagguard` | `bash docs/plans/plan-049-james-dixson-725bc0/scripts/gate-run.sh docs/plans/plan-049-james-dixson-725bc0/scripts/gate-dagguard.sh` |  |  |
| `gate-cellcheck` | `bash docs/plans/plan-049-james-dixson-725bc0/scripts/gate-run.sh docs/plans/plan-049-james-dixson-725bc0/scripts/gate-cellcheck.sh` |  |  |
| `gate-plan060-amendment` | `uv run scripts/check_amendment_log.py --plan plan-060-james-dixson-6a6ac9` |  |  |
| `gate-plan060-reqcoverage` | `uv run scripts/checks/check-req-coverage.py --min-issues 30 docs/plans/plan-060-james-dixson-6a6ac9` |  |  |
| `gate-plan060-figures` | `uv run scripts/checks/check-cited-figures.py docs/plans/plan-060-james-dixson-6a6ac9/assets/cited-figures.md --min-figures 6` |  |  |
| `uv-yf-land-manifest` | `uv run skills/yf-plan/scripts/test_land_manifest.py` |  |  |
| `pour-fidelity` | `uv run _shared/test_pour_fidelity.py` |  |  |
| `uv-yf-review-count` | `uv run skills/yf-plan/scripts/test_review_count.py` |  |  |
| `uv-yf-status-gate` | `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_update_status_gate.py -q` |  |  |
| `uv-yf-upstream-req` | `uv run skills/yf-plan/scripts/test_upstream_requirements.py` |  |  |
| `uv-yf-gate-consistency` | `uv run skills/yf-plan/scripts/test_gate_consistency.py` |  |  |
| `uv-recheck-criteria` | `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_recheck_criteria.py -q` |  |  |
| `uv-index-members` | `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_index_members.py -q` |  |  |
| `okf-index-drift` | `uv run scripts/checks/check_okf_index_drift.py --min-roots 30` |  |  |
| `uv-yf-verify-beads` | `uv run skills/yf-plan/scripts/test_verify_beads.py` |  |  |
| `uv-yf-retro-fields` | `uv run skills/yf-plan/scripts/test_retrospective_fields.py` |  |  |
| `gate-plan052` | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh verify-partition` |  |  |

### full

| id | cmd | cwd | timeout |
|:--|:--|:--|--:|
|  | `cargo fmt --all -- --check` |  |  |
|  | `cargo clippy --workspace --all-targets -- -D warnings` |  |  |
|  | `cargo test --workspace` |  |  |
|  | `cargo test -p yf --test install_sync_e2e` |  |  |
|  | `uv run --with pytest python3 -m pytest _shared/test_sync.py -q` |  |  |
|  | `uv run --with pytest python3 -m pytest skills/yf-beads-hygiene/scripts/test_beads_hygiene.py -q` |  |  |
|  | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q` |  |  |
|  | `uv run skills/yf-beads-upstream/scripts/check_prescriptive_push.py` |  |  |
|  | `uv run skills/yf-beads-upstream/scripts/check_gh_direct.py` |  |  |
|  | `uv run skills/yf-change-validation/scripts/test_change_validation.py` |  |  |
| `check-smoke-tier` | `uv run scripts/checks/check_smoke_tier.py` |  |  |
| `uv-recheck-criteria` | `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_recheck_criteria.py -q` |  |  |
| `uv-index-members` | `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_index_members.py -q` |  |  |
| `okf-index-drift` | `uv run scripts/checks/check_okf_index_drift.py --min-roots 30` |  |  |
|  | `uv run --with pytest python3 -m pytest skills/yf-markdown-lint/scripts/test_markdown_lint.py -q` |  |  |
|  | `uv run skills/yf-plan/scripts/test_worktree.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_close_cascade.py` |  |  |
|  | `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_stamp_tracker.py -q` |  |  |
|  | `uv run skills/yf-plan/scripts/test_complete_gate.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_review_verdict.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_config_tiers.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_classify_deliverable.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_close_contract.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_verify_reconcile.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_audit_close.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_reconcile_step_resolution.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_update_status_idempotent.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_cascade_root_resolution.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_epic_ref_audit.py` |  |  |
|  | `uv run scripts/check_frontmatter.py` |  |  |
|  | `uv run scripts/check_skill_script_refs.py` |  |  |
|  | `uv run scripts/test_check_skill_script_refs.py` |  |  |
|  | `uv run skills/yf-research/scripts/test_link_normalizer.py` |  |  |
|  | `uv run skills/yf-research/scripts/test_credibility_scorer.py` |  |  |
|  | `uv run _shared/sync.py --check` |  |  |
|  | `uv run skills/yf-herdr/scripts/test_launch_contract.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_autonomy.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_gates.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_retrospective.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_cli_enumeration.py` |  |  |
| `uv-okf` | `uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q` |  |  |
| `okf-hygiene-tests` | `uv run skills/yf-okf-hygiene/scripts/test_okf_hygiene.py` |  |  |
| `baseline-pin-drift` | `bash scripts/baseline-pin-drift.sh` |  |  |
| `doclint` | `uv run _shared/doc_lint.py` |  |  |
| `doclint-tests` | `uv run _shared/test_doc_lint.py` |  |  |
| `plan-extract` | `uv run _shared/test_plan_extract.py` |  |  |
| `dag-guard` | `uv run _shared/test_dag_guard.py` |  |  |
| `gate-dagguard` | `bash docs/plans/plan-049-james-dixson-725bc0/scripts/gate-run.sh docs/plans/plan-049-james-dixson-725bc0/scripts/gate-dagguard.sh` |  |  |
| `gate-cellcheck` | `bash docs/plans/plan-049-james-dixson-725bc0/scripts/gate-run.sh docs/plans/plan-049-james-dixson-725bc0/scripts/gate-cellcheck.sh` |  |  |
| `gate-plan060-amendment` | `uv run scripts/check_amendment_log.py --plan plan-060-james-dixson-6a6ac9` |  |  |
| `gate-plan060-reqcoverage` | `uv run scripts/checks/check-req-coverage.py --min-issues 30 docs/plans/plan-060-james-dixson-6a6ac9` |  |  |
| `gate-plan060-figures` | `uv run scripts/checks/check-cited-figures.py docs/plans/plan-060-james-dixson-6a6ac9/assets/cited-figures.md --min-figures 6` |  |  |
| `uv-yf-land-manifest` | `uv run skills/yf-plan/scripts/test_land_manifest.py` |  |  |
| `pour-fidelity` | `uv run _shared/test_pour_fidelity.py` |  |  |
| `uv-yf-review-count` | `uv run skills/yf-plan/scripts/test_review_count.py` |  |  |
| `uv-yf-status-gate` | `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_update_status_gate.py -q` |  |  |
| `uv-yf-upstream-req` | `uv run skills/yf-plan/scripts/test_upstream_requirements.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_gate_consistency.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_verify_beads.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_retrospective_fields.py` |  |  |
|  | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh verify-partition` |  |  |

## 2. Signal Fingerprint

| source-path | parsed-value-or-hash |
|:--|:--|
| `Cargo.toml` | `sha256:dc1c5e47e979e216` |
| `.github/workflows/*.yml` | `sha256:56499c620291d09a` |
| `**/test_*.py` | `sha256:660f81ba10290bc9` |
| `repo --check scripts` | `sha256:af52842d97019b3b` |

## 3. Trigger Scope

| changed-path glob | scopes to (FAST ids) |
|:--|:--|
| `*.rs` | `cargo-fmt`, `cargo` |
| `**/*.rs` | `cargo-fmt`, `cargo` |
| `Cargo.toml` | `cargo-fmt`, `cargo` |
| `**/Cargo.toml` | `cargo-fmt`, `cargo` |
| `yf/profiles/**` | `cargo`, `sync-e2e`, `harness-e2e` |
| `yf/profiles/*.json` | `cargo`, `sync-e2e`, `harness-e2e` |
| `yf/src/cmd/self_cmd/**` | `cargo-fmt`, `cargo`, `sync-e2e` |
| `yf/src/cmd/harness/**` | `cargo-fmt`, `cargo`, `sync-e2e`, `harness-e2e` |
| `yf/tests/harness_cross_e2e.rs` | `harness-e2e` |
| `yf/tests/install_sync_e2e.rs` | `sync-e2e` |
| `_shared/**` | `uv`, `uv-_shared` |
| `_shared/test_sync.py` | `uv` |
| `_shared/okf.py` | `uv-okf`, `uv-_shared` |
| `docs/plans/**` | `okf-index-drift` |
| `docs/plans/plan-060-james-dixson-6a6ac9/**` | `okf-index-drift`, `gate-plan060-amendment`, `gate-plan060-reqcoverage`, `gate-plan060-figures` |
| `scripts/checks/_figures.py` | `gate-plan060-figures` |
| `scripts/checks/check-cited-figures.py` | `gate-plan060-figures` |
| `SPEC.md` | `gate-plan060-amendment` |
| `skills/yf-plan/spec/**` | `gate-plan060-amendment` |
| `docs/research/**` | `okf-index-drift` |
| `Incubator/*/plans/**` | `okf-index-drift` |
| `Incubator/*/research/**` | `okf-index-drift` |
| `scripts/checks/check_okf_index_drift.py` | `okf-index-drift` |
| `skills/yf-plan/OKF-EXTENSION.md` | `okf-index-drift`, `uv-okf` |
| `skills/yf-plan/scripts/test_recheck_criteria.py` | `uv-recheck-criteria` |
| `skills/yf-plan/scripts/test_index_members.py` | `uv-index-members` |
| `skills/yf-plan/scripts/plan_manager.py` | `uv-recheck-criteria`, `uv-index-members`, `uv-yf-cli-enum`, `uv-yf-land-manifest` |
| `skills/yf-plan/scripts/test_land_manifest.py` | `uv-yf-land-manifest` |
| `_shared/test_okf.py` | `uv-okf` |
| `skills/yf-okf/scripts/**` | `uv-okf`, `uv-_shared` |
| `skills/yf-okf-hygiene/scripts/**` | `okf-hygiene-tests`, `uv-okf`, `uv-_shared` |
| `skills/yf-okf-hygiene/scripts/okf.py` | `uv-okf`, `uv-_shared` |
| `skills/yf-okf-hygiene/scripts/test_okf_hygiene.py` | `okf-hygiene-tests` |
| `skills/yf-okf/spec/OKF-BASELINE.md` | `baseline-pin-drift` |
| `scripts/baseline-pin-drift.sh` | `baseline-pin-drift` |
| `skills/yf-incubator/scripts/**` | `uv-okf`, `uv-_shared` |
| `skills/yf-plan/scripts/okf.py` | `uv-okf`, `uv-_shared` |
| `skills/yf-research/scripts/okf.py` | `uv-okf`, `uv-_shared` |
| `skills/yf-beads-hygiene/scripts/**` | `uv-run` |
| `skills/yf-beads-hygiene/scripts/test_beads_hygiene.py` | `uv-run` |
| `skills/yf-beads-upstream/scripts/**` | `uv-with`, `bup-prescriptive-push`, `bup-gh-direct`, `bup-no-universe-fanout`, `bup-fanout-controls` |
| `skills/yf-beads-upstream/scripts/test_upstream.py` | `uv-with` |
| `skills/yf-beads-upstream/SKILL.md` | `bup-prescriptive-push`, `uv-with`, `bup-gh-direct` |
| `skills/yf-change-validation/scripts/**` | `uv-skills` |
| `skills/yf-change-validation/scripts/test_change_validation.py` | `uv-skills` |
| `skills/yf-markdown-lint/scripts/**` | `uv-pytest` |
| `skills/yf-markdown-lint/scripts/test_markdown_lint.py` | `uv-pytest` |
| `skills/yf-plan/scripts/gate_consistency.py` | `uv-yf-gate-consistency` |
| `skills/yf-plan/scripts/test_gate_consistency.py` | `uv-yf-gate-consistency` |
| `skills/yf-plan/scripts/verify_beads.py` | `uv-yf-verify-beads` |
| `skills/yf-plan/scripts/test_verify_beads.py` | `uv-yf-verify-beads` |
| `skills/yf-plan/scripts/retrospective_fields.py` | `uv-yf-retro-fields` |
| `skills/yf-plan/scripts/test_retrospective_fields.py` | `uv-yf-retro-fields` |
| `skills/yf-plan/formulas/**` | `uv-yf-gates` |
| `skills/yf-beads-upstream/scripts/upstream_render.py` | `uv-with` |
| `docs/plans/plan-052-james-dixson-fa8056/assets/**` | `gate-plan052` |
| `skills/yf-plan/scripts/**` | `uv-yf`, `uv-yf-cascade`, `uv-yf-complete-gate`, `uv-yf-review-verdict`, `uv-yf-config-tiers`, `uv-yf-classify`, `uv-yf-stamp-tracker`, `uv-yf-close-contract`, `uv-yf-verify-reconcile`, `uv-yf-audit-close`, `uv-yf-reconcile-step`, `uv-yf-status-idem`, `uv-yf-cascade-root`, `uv-yf-epic-ref`, `uv-yf-autonomy`, `uv-yf-gates`, `uv-yf-retro`, `uv-yf-cli-enum`, `uv-yf-upstream-req`, `uv-yf-review-agent` |
| `skills/yf-plan/scripts/test_epic_ref_audit.py` | `uv-yf-epic-ref` |
| `skills/yf-plan/scripts/test_worktree.py` | `uv-yf` |
| `skills/yf-plan/scripts/test_close_cascade.py` | `uv-yf-cascade` |
| `skills/yf-plan/scripts/test_complete_gate.py` | `uv-yf-complete-gate` |
| `skills/yf-plan/scripts/test_review_verdict.py` | `uv-yf-review-verdict` |
| `skills/yf-plan/scripts/test_config_tiers.py` | `uv-yf-config-tiers` |
| `skills/yf-plan/scripts/test_classify_deliverable.py` | `uv-yf-classify` |
| `skills/yf-plan/scripts/test_close_contract.py` | `uv-yf-close-contract` |
| `skills/yf-plan/scripts/test_verify_reconcile.py` | `uv-yf-verify-reconcile` |
| `skills/yf-plan/scripts/test_audit_close.py` | `uv-yf-audit-close` |
| `skills/yf-plan/scripts/test_reconcile_step_resolution.py` | `uv-yf-reconcile-step` |
| `skills/yf-plan/scripts/test_update_status_idempotent.py` | `uv-yf-status-idem` |
| `skills/yf-plan/scripts/test_cascade_root_resolution.py` | `uv-yf-cascade-root` |
| `skills/yf-plan/scripts/test_autonomy.py` | `uv-yf-autonomy` |
| `skills/yf-plan/scripts/test_gates.py` | `uv-yf-gates` |
| `skills/yf-plan/scripts/test_retrospective.py` | `uv-yf-retro` |
| `skills/yf-plan/scripts/test_cli_enumeration.py` | `uv-yf-cli-enum` |
| `skills/yf-plan/scripts/test_review_agent_contract.py` | `uv-yf-review-agent` |
| `skills/yf-plan/scripts/test_upstream_requirements.py` | `uv-yf-upstream-req` |
| `skills/yf-plan/spec/cli.md` | `uv-yf-cli-enum` |
| `skills/yf-plan/spec/agents.md` | `uv-yf-review-agent` |
| `skills/yf-plan/SKILL.md` | `uv-yf-close-contract`, `uv-yf-audit-close`, `uv-yf-reconcile-step`, `uv-yf-gates`, `uv-yf-review-agent` |
| `skills/yf-plan/agents/*.md` | `uv-yf-gates`, `uv-yf-review-agent` |
| `skills/yf-herdr/**` | `uv-herdr-launch` |
| `skills/yf-herdr/SKILL.md` | `uv-herdr-launch` |
| `skills/yf-herdr/scripts/test_launch_contract.py` | `uv-herdr-launch` |
| `skills/*/SPEC.md` | `doclint`, `doclint-tests` |
| `skills/*/spec/*.md` | `cargo` |
| `skills/yf-plan/spec/*.md` | `cargo`, `uv-yf-close-contract`, `doclint`, `doclint-tests` |
| `skills/yf-plan/scripts/fixtures/classify/**` | `uv-yf-classify` |
| `skills/*/SKILL.md` | `frontmatter` |
| `skills/*/agents/*.md` | `frontmatter` |
| `scripts/check_frontmatter.py` | `frontmatter` |
| `skills/*/SKILL.md` | `skill-script-refs` |
| `skills/*/README.md` | `skill-script-refs` |
| `skills/*/agents/*.md` | `skill-script-refs` |
| `skills/*/protocols/*.md` | `skill-script-refs` |
| `skills/*/reference/*.md` | `skill-script-refs` |
| `skills/*/scripts/**` | `skill-script-refs` |
| `scripts/check_skill_script_refs.py` | `skill-script-refs`, `skill-script-refs-tests` |
| `scripts/test_check_skill_script_refs.py` | `skill-script-refs-tests` |
| `skills/yf-plan/agents/**` | `uv-yf-review-verdict` |
| `skills/yf-research/scripts/**` | `uv-research`, `uv-research-cred` |
| `skills/yf-research/scripts/test_link_normalizer.py` | `uv-research` |
| `skills/yf-research/scripts/test_credibility_scorer.py` | `uv-research-cred` |
| `docs/plans/**` | `doclint`, `doclint-tests`, `plan-extract`, `dag-guard` |
| `_shared/dag_guard.py` | `dag-guard`, `gate-dagguard` |
| `_shared/test_dag_guard.py` | `dag-guard`, `gate-dagguard` |
| `_shared/plan_extract.py` | `plan-extract`, `doclint`, `doclint-tests`, `dag-guard`, `gate-dagguard` |
| `_shared/doc_lint.py` | `doclint`, `doclint-tests`, `gate-cellcheck`, `uv-yf-intake-lint` |
| `_shared/document_types/*.toml` | `doclint`, `doclint-tests`, `gate-cellcheck`, `uv-yf-intake-lint` |
| `tests/fixtures/doc-checks/**` | `doclint-tests`, `gate-cellcheck` |
| `docs/plans/plan-049-james-dixson-725bc0/scripts/*.sh` | `gate-dagguard`, `gate-cellcheck` |
| `skills/yf-plan/scripts/plan_manager.py` | `uv-yf-intake-lint` |
| `skills/yf-plan/protocols/*.md` | `doclint-tests` |
| `docs/research/**` | `doclint`, `doclint-tests` |
| `Incubator/*/plans/**` | `doclint`, `doclint-tests` |
| `Incubator/*/research/**` | `doclint`, `doclint-tests` |
| `skills/*/spec/*.md` | `cargo`, `doclint`, `doclint-tests` |
| `_shared/doc_lint.py` | `doclint`, `doclint-tests` |
| `_shared/plan_extract.py` | `plan-extract`, `pour-fidelity` |
| `_shared/pour_fidelity.py` | `pour-fidelity` |
| `_shared/test_plan_extract.py` | `plan-extract` |
| `_shared/test_pour_fidelity.py` | `pour-fidelity` |
| `_shared/document_types/**` | `doclint`, `doclint-tests` |
| `_shared/test_doc_lint.py` | `doclint-tests` |
| `tests/fixtures/doclint/**` | `doclint-tests` |
| `skills/yf-plan/scripts/test_review_count.py` | `uv-yf-review-count` |
| `skills/yf-plan/scripts/test_update_status_gate.py` | `uv-yf-status-gate` |
