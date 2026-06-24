# CHANGE-VALIDATION.md

> APPROVED dogfood manifest for the beads-skills repo (plan-015 E.1). Seeded by
> `change_validation.py infer`, reviewed, `website` build rows trimmed (deploy-only,
> not a validation gate), and approved. yf-plan §6.1.5 layer (b) now delegates here.
> Executable-only: `yf-drift-check` is excluded (prose/LLM trigger, not a runnable
> command). To roll delegation back to `validate-cmd`/notice, set `approved: no`.

## 0. Status

approved: yes

## 1. Tiers

### fast

| id | cmd | cwd | timeout |
|:--|:--|:--|--:|
| `cargo` | `cargo test --workspace` |  |  |
| `uv` | `uv run --with pytest python3 -m pytest _shared/test_sync.py -q` |  |  |
| `uv-run` | `uv run --with pytest python3 -m pytest skills/yf-beads-hygiene/scripts/test_beads_hygiene.py -q` |  |  |
| `uv-with` | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q` |  |  |
| `uv-skills` | `uv run skills/yf-change-validation/scripts/test_change_validation.py` |  |  |
| `uv-pytest` | `uv run --with pytest python3 -m pytest skills/yf-markdown-lint/scripts/test_markdown_lint.py -q` |  |  |
| `uv-yf` | `uv run skills/yf-plan/scripts/test_worktree.py` |  |  |
| `uv-research` | `uv run skills/yf-research/scripts/test_link_normalizer.py` |  |  |
| `uv-_shared` | `uv run _shared/sync.py --check` |  |  |

### full

| id | cmd | cwd | timeout |
|:--|:--|:--|--:|
|  | `cargo fmt --all -- --check` |  |  |
|  | `cargo clippy --workspace --all-targets -- -D warnings` |  |  |
|  | `cargo test --workspace` |  |  |
|  | `uv run --with pytest python3 -m pytest _shared/test_sync.py -q` |  |  |
|  | `uv run --with pytest python3 -m pytest skills/yf-beads-hygiene/scripts/test_beads_hygiene.py -q` |  |  |
|  | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q` |  |  |
|  | `uv run skills/yf-change-validation/scripts/test_change_validation.py` |  |  |
|  | `uv run --with pytest python3 -m pytest skills/yf-markdown-lint/scripts/test_markdown_lint.py -q` |  |  |
|  | `uv run skills/yf-plan/scripts/test_worktree.py` |  |  |
|  | `uv run skills/yf-research/scripts/test_link_normalizer.py` |  |  |
|  | `uv run _shared/sync.py --check` |  |  |

## 2. Signal Fingerprint

| source-path | parsed-value-or-hash |
|:--|:--|
| `Cargo.toml` | `sha256:dc1c5e47e979e216` |
| `.github/workflows/*.yml` | `sha256:5ebddf75ce6f6821` |
| `**/test_*.py` | `sha256:44ab2de06b1834b5` |
| `website/package.json` | `sha256:c8683533309d1abc` |
| `repo --check scripts` | `sha256:daa4d8b8c86cf102` |

## 3. Trigger Scope

| changed-path glob | scopes to (FAST ids) |
|:--|:--|
| `*.rs` | `cargo` |
| `**/*.rs` | `cargo` |
| `Cargo.toml` | `cargo` |
| `**/Cargo.toml` | `cargo` |
| `_shared/**` | `uv`, `uv-_shared` |
| `_shared/test_sync.py` | `uv` |
| `skills/yf-beads-hygiene/scripts/**` | `uv-run` |
| `skills/yf-beads-hygiene/scripts/test_beads_hygiene.py` | `uv-run` |
| `skills/yf-beads-upstream/scripts/**` | `uv-with` |
| `skills/yf-beads-upstream/scripts/test_upstream.py` | `uv-with` |
| `skills/yf-change-validation/scripts/**` | `uv-skills` |
| `skills/yf-change-validation/scripts/test_change_validation.py` | `uv-skills` |
| `skills/yf-markdown-lint/scripts/**` | `uv-pytest` |
| `skills/yf-markdown-lint/scripts/test_markdown_lint.py` | `uv-pytest` |
| `skills/yf-plan/scripts/**` | `uv-yf` |
| `skills/yf-plan/scripts/test_worktree.py` | `uv-yf` |
| `skills/yf-research/scripts/**` | `uv-research` |
| `skills/yf-research/scripts/test_link_normalizer.py` | `uv-research` |
