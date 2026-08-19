# Issue 3.5 — FULL tier run (recorded)

Recorded: 2026-08-19  tree: worktree plan-047-james-dixson-dec9ff-execute

```
tier   : full
status : pass
commands: 39
first_failure: None
```

## Per-command result

| id | cmd | rc | status |
| :-- | :-- | --: | :-- |
| `_(no id)_` | `cargo fmt --all -- --check` | 0 | pass |
| `_(no id)_` | `cargo clippy --workspace --all-targets -- -D warnings` | 0 | pass |
| `_(no id)_` | `cargo test --workspace` | 0 | pass |
| `_(no id)_` | `cargo test -p yf --test install_sync_e2e` | 0 | pass |
| `_(no id)_` | `uv run --with pytest python3 -m pytest _shared/test_sync.py -q` | 0 | pass |
| `_(no id)_` | `uv run --with pytest python3 -m pytest skills/yf-beads-hygiene/scripts/test_beads_hygiene.py -q` | 0 | pass |
| `_(no id)_` | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-beads-upstream/scripts/check_prescriptive_push.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-beads-upstream/scripts/check_gh_direct.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-change-validation/scripts/test_change_validation.py` | 0 | pass |
| `_(no id)_` | `uv run --with pytest python3 -m pytest skills/yf-markdown-lint/scripts/test_markdown_lint.py -q` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_worktree.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_close_cascade.py` | 0 | pass |
| `_(no id)_` | `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_stamp_tracker.py -q` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_complete_gate.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_review_verdict.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_config_tiers.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_classify_deliverable.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_close_contract.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_verify_reconcile.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_audit_close.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_reconcile_step_resolution.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_update_status_idempotent.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_cascade_root_resolution.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_epic_ref_audit.py` | 0 | pass |
| `_(no id)_` | `uv run scripts/check_frontmatter.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-research/scripts/test_link_normalizer.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-research/scripts/test_credibility_scorer.py` | 0 | pass |
| `_(no id)_` | `uv run _shared/sync.py --check` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-herdr/scripts/test_launch_contract.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_autonomy.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_gates.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_retrospective.py` | 0 | pass |
| `_(no id)_` | `uv run skills/yf-plan/scripts/test_cli_enumeration.py` | 0 | pass |
| `uv-okf` | `uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q` | 0 | pass |
| `doclint` | `uv run _shared/doc_lint.py` | 0 | pass |
| `doclint-tests` | `uv run _shared/test_doc_lint.py` | 0 | pass |
| `uv-yf-review-count` | `uv run skills/yf-plan/scripts/test_review_count.py` | 0 | pass |
| `uv-yf-status-gate` | `uv run --with pytest --with click --with pyyaml python3 -m pytest skills/yf-plan/scripts/test_update_status_gate.py -q` | 0 | pass |

## A defect this run found

The FIRST full run failed at `uv-yf-status-gate` (rc=1). The cause was a **cwd-dependence**
in a test written earlier in this plan: `test_update_status_gate.py`'s fixture substituted
the literal string `**Status:** approved`, which silently did nothing once the live bundle
moved to `executing` — so the fixture stopped setting the status it depended on and the test
was passing, from `scripts/`, for an incidental reason.

That is precisely the class Issue 7.2 exists to fix (clauses that pass only from the skill
dir), reproduced in new code — and it is why running the FULL tier from the repo root once
is worth its multi-minute cost. Fixed with an anchored regex substitution plus an assertion
that the fixture actually set the status; both invocation paths now pass.

Second run: **39 commands, 0 failing, status `pass`, exit 0.**
