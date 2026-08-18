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
> hard error, whereas a name filter matching nothing exits 0 and passes vacuously.

## 0. Status

approved: yes

## 1. Tiers

### fast

| id | cmd | cwd | timeout |
|:--|:--|:--|--:|
| `cargo-fmt` | `cargo fmt --all -- --check` |  |  |
| `cargo` | `cargo test --workspace` |  |  |
| `sync-e2e` | `cargo test -p yf --test install_sync_e2e` |  |  |
| `uv` | `uv run --with pytest python3 -m pytest _shared/test_sync.py -q` |  |  |
| `uv-run` | `uv run --with pytest python3 -m pytest skills/yf-beads-hygiene/scripts/test_beads_hygiene.py -q` |  |  |
| `uv-with` | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q` |  |  |
| `bup-prescriptive-push` | `uv run skills/yf-beads-upstream/scripts/check_prescriptive_push.py` |  |  |
| `bup-gh-direct` | `uv run skills/yf-beads-upstream/scripts/check_gh_direct.py` |  |  |
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
| `uv-yf-verify-reconcile` | `uv run skills/yf-plan/scripts/test_verify_reconcile.py` |  |  |
| `uv-yf-audit-close` | `uv run skills/yf-plan/scripts/test_audit_close.py` |  |  |
| `uv-yf-reconcile-step` | `uv run skills/yf-plan/scripts/test_reconcile_step_resolution.py` |  |  |
| `uv-yf-status-idem` | `uv run skills/yf-plan/scripts/test_update_status_idempotent.py` |  |  |
| `uv-yf-cascade-root` | `uv run skills/yf-plan/scripts/test_cascade_root_resolution.py` |  |  |
| `uv-yf-epic-ref` | `uv run skills/yf-plan/scripts/test_epic_ref_audit.py` |  |  |
| `frontmatter` | `uv run scripts/check_frontmatter.py` |  |  |
| `uv-research` | `uv run skills/yf-research/scripts/test_link_normalizer.py` |  |  |
| `uv-research-cred` | `uv run skills/yf-research/scripts/test_credibility_scorer.py` |  |  |
| `uv-_shared` | `uv run _shared/sync.py --check` |  |  |
| `uv-herdr-launch` | `uv run skills/yf-herdr/scripts/test_launch_contract.py` |  |  |
| `uv-yf-autonomy` | `uv run skills/yf-plan/scripts/test_autonomy.py` |  |  |
| `uv-yf-gates` | `uv run skills/yf-plan/scripts/test_gates.py` |  |  |

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
|  | `uv run skills/yf-research/scripts/test_link_normalizer.py` |  |  |
|  | `uv run skills/yf-research/scripts/test_credibility_scorer.py` |  |  |
|  | `uv run _shared/sync.py --check` |  |  |
|  | `uv run skills/yf-herdr/scripts/test_launch_contract.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_autonomy.py` |  |  |
|  | `uv run skills/yf-plan/scripts/test_gates.py` |  |  |

## 2. Signal Fingerprint

| source-path | parsed-value-or-hash |
|:--|:--|
| `Cargo.toml` | `sha256:dc1c5e47e979e216` |
| `.github/workflows/*.yml` | `sha256:56499c620291d09a` |
| `**/test_*.py` | `sha256:83751fe1dd548349` |
| `repo --check scripts` | `sha256:af52842d97019b3b` |

## 3. Trigger Scope

| changed-path glob | scopes to (FAST ids) |
|:--|:--|
| `*.rs` | `cargo-fmt`, `cargo` |
| `**/*.rs` | `cargo-fmt`, `cargo` |
| `Cargo.toml` | `cargo-fmt`, `cargo` |
| `**/Cargo.toml` | `cargo-fmt`, `cargo` |
| `yf/profiles/**` | `cargo`, `sync-e2e` |
| `yf/profiles/*.json` | `cargo`, `sync-e2e` |
| `yf/src/cmd/self_cmd/**` | `cargo-fmt`, `cargo`, `sync-e2e` |
| `yf/src/cmd/harness/**` | `cargo-fmt`, `cargo`, `sync-e2e` |
| `yf/tests/install_sync_e2e.rs` | `sync-e2e` |
| `_shared/**` | `uv`, `uv-_shared` |
| `_shared/test_sync.py` | `uv` |
| `skills/yf-beads-hygiene/scripts/**` | `uv-run` |
| `skills/yf-beads-hygiene/scripts/test_beads_hygiene.py` | `uv-run` |
| `skills/yf-beads-upstream/scripts/**` | `uv-with`, `bup-prescriptive-push`, `bup-gh-direct` |
| `skills/yf-beads-upstream/scripts/test_upstream.py` | `uv-with` |
| `skills/yf-beads-upstream/SKILL.md` | `bup-prescriptive-push`, `uv-with`, `bup-gh-direct` |
| `skills/yf-change-validation/scripts/**` | `uv-skills` |
| `skills/yf-change-validation/scripts/test_change_validation.py` | `uv-skills` |
| `skills/yf-markdown-lint/scripts/**` | `uv-pytest` |
| `skills/yf-markdown-lint/scripts/test_markdown_lint.py` | `uv-pytest` |
| `skills/yf-plan/scripts/**` | `uv-yf`, `uv-yf-cascade`, `uv-yf-complete-gate`, `uv-yf-review-verdict`, `uv-yf-config-tiers`, `uv-yf-classify`, `uv-yf-stamp-tracker`, `uv-yf-close-contract`, `uv-yf-verify-reconcile`, `uv-yf-audit-close`, `uv-yf-reconcile-step`, `uv-yf-status-idem`, `uv-yf-cascade-root`, `uv-yf-epic-ref`, `uv-yf-autonomy`, `uv-yf-gates` |
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
| `skills/yf-plan/SKILL.md` | `uv-yf-close-contract`, `uv-yf-audit-close`, `uv-yf-reconcile-step`, `uv-yf-gates` |
| `skills/yf-plan/agents/*.md` | `uv-yf-gates` |
| `skills/yf-herdr/**` | `uv-herdr-launch` |
| `skills/yf-herdr/SKILL.md` | `uv-herdr-launch` |
| `skills/yf-herdr/scripts/test_launch_contract.py` | `uv-herdr-launch` |
| `skills/*/SPEC.md` | `uv-herdr-launch` |
| `skills/*/spec/*.md` | `cargo` |
| `skills/yf-plan/spec/*.md` | `cargo`, `uv-yf-close-contract` |
| `skills/yf-plan/scripts/fixtures/classify/**` | `uv-yf-classify` |
| `skills/*/SKILL.md` | `frontmatter` |
| `skills/*/agents/*.md` | `frontmatter` |
| `scripts/check_frontmatter.py` | `frontmatter` |
| `skills/yf-plan/agents/**` | `uv-yf-review-verdict` |
| `skills/yf-research/scripts/**` | `uv-research`, `uv-research-cred` |
| `skills/yf-research/scripts/test_link_normalizer.py` | `uv-research` |
| `skills/yf-research/scripts/test_credibility_scorer.py` | `uv-research-cred` |
