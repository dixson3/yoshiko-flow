---
type: Finding
okf_spec: OKF-PLAN
id: exec-001-full-tier-executed
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
---

# exec-001 — The FULL tier, EXECUTED (plan-046 Issue 1.6)

**Why this exists.** exp-001's largest honest limit was that it inferred the FULL tier's
behavior *from the manifest* rather than from an executed run. Issue 1.6 closes that limit the
only way it can be closed: by running it once and recording the result.

**Command** (repo tree, execution worktree `.worktrees/plan-046-james-dixson-aabefa`):

```bash
env -u VIRTUAL_ENV uv run skills/yf-change-validation/scripts/change_validation.py run --tier full --json
```

**Result:** `tier: full`, **`status: pass`**, **35 commands executed**,
`first_failure: null`. Run after Epic 1's Issues 1.1–1.5 landed, so the `uv-okf` row added by
Issue 1.2 is included in the executed set — the FULL tier is confirmed to carry it, not merely
declared to.

| id | cmd | status |
| :-- | :-- | :-- |
| `—` | `cargo fmt --all -- --check` | pass |
| `—` | `cargo clippy --workspace --all-targets -- -D warnings` | pass |
| `—` | `cargo test --workspace` | pass |
| `—` | `cargo test -p yf --test install_sync_e2e` | pass |
| `—` | `uv run --with pytest python3 -m pytest _shared/test_sync.py -q` | pass |
| `—` | `uv run --with pytest python3 -m pytest skills/yf-beads-hygiene/scripts/test_beads_hygiene.py -q` | pass |
| `—` | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q` | pass |
| `—` | `uv run skills/yf-beads-upstream/scripts/check_prescriptive_push.py` | pass |
| `—` | `uv run skills/yf-beads-upstream/scripts/check_gh_direct.py` | pass |
| `—` | `uv run skills/yf-change-validation/scripts/test_change_validation.py` | pass |
| `—` | `uv run --with pytest python3 -m pytest skills/yf-markdown-lint/scripts/test_markdown_lint.py -q` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_worktree.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_close_cascade.py` | pass |
| `—` | `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_stamp_tracker.py -q` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_complete_gate.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_review_verdict.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_config_tiers.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_classify_deliverable.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_close_contract.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_verify_reconcile.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_audit_close.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_reconcile_step_resolution.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_update_status_idempotent.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_cascade_root_resolution.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_epic_ref_audit.py` | pass |
| `—` | `uv run scripts/check_frontmatter.py` | pass |
| `—` | `uv run skills/yf-research/scripts/test_link_normalizer.py` | pass |
| `—` | `uv run skills/yf-research/scripts/test_credibility_scorer.py` | pass |
| `—` | `uv run _shared/sync.py --check` | pass |
| `—` | `uv run skills/yf-herdr/scripts/test_launch_contract.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_autonomy.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_gates.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_retrospective.py` | pass |
| `—` | `uv run skills/yf-plan/scripts/test_cli_enumeration.py` | pass |
| `uv-okf` | `uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q` | pass |

## What this does and does not establish

- **Establishes:** the FULL tier is runnable end to end on this tree; all 35
  rows execute; none fails. The `uv-okf` id appears in the executed list, so Issue 1.2's full-tier
  row is live rather than decorative.
- **Does not establish:** that FULL is a superset of CI. That claim lives in
  `CHANGE-VALIDATION.md`'s own framing and is not tested by this run.
