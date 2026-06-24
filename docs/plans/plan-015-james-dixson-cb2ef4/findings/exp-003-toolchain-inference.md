# Exp 003 — toolchain inference signals + worked two-layer recipe

**Question:** What signals should the inference engine read, how do they map to a *layered*
(fast/affected vs full) recipe, and how is toolchain drift detected cheaply?

## Headline findings

1. **CI workflow files are the highest-fidelity seed.** `.github/workflows/*.yml` `run:` steps
   record exactly what the maintainer gates on (precise flags). Adopt verbatim; skip disabled
   (`if: ${{ false }}`) and tag-only (`on: [v*]`) jobs.
2. **The FULL tier must be a SUPERSET of CI, not a mirror.** This repo's `ci.yml` runs only cargo
   (fmt/clippy/test) — it **omits** the 6 `uv` pytest suites and `_shared/sync.py --check`. So a
   CI-only seed is immediately incomplete — a *standing, already-true* example proving the
   "seed-by-inference then operator-augment + re-propose" design is necessary.
3. **Drift detection is pure file-read + parse** (no command execution) → cheap enough for an
   on-edit trigger, matching drift-check's firing model.

## This repo's signals → commands

- **Rust** (`Cargo.toml`, workspace `members=["yf"]`, resolver 2; `ci.yml:41-47`):
  `cargo fmt --all -- --check` · `cargo clippy --workspace --all-targets -- -D warnings` ·
  `cargo test --workspace`. (`release.yml` is publish-only — exclude.)
- **Python** (no `pyproject.toml`; PEP-723 scripts via `uv run`, no `conftest.py`). 6 suites:
  `_shared/test_sync.py`, `skills/yf-beads-hygiene/scripts/test_beads_hygiene.py`,
  `skills/yf-beads-upstream/scripts/test_upstream.py`,
  `skills/yf-markdown-lint/scripts/test_markdown_lint.py`,
  `skills/yf-plan/scripts/test_worktree.py`, `skills/yf-research/scripts/test_link_normalizer.py`.
  **Two idioms** (per-file): `uv run --with pytest python3 -m pytest <f> -q` (the four with no
  inline deps) vs `uv run <f>` (the two carrying inline `dependencies`). The engine must read each
  PEP-723 header — it cannot assume one pytest command.
- **Repo-specific**: `uv run _shared/sync.py --check` (plan-014 vendoring drift). Markers:
  `.markdown-lint-on-edit` (opt-in active), `DRIFT-CHECK.md` (approved; §6 drives yf-drift-check).
  No `Makefile`/`justfile`.
- **JS/docs**: `website/package.json` (Docusaurus; `npm ci && npm run build`) — but `docs-deploy.yml`
  is **double-disabled** (`if: ${{ false }}`). Treat as opt-in, not default-tier.

## General inference precedence

**CI `run:` steps > named runner targets (just/make) > manifest-derived defaults.** CI wins on
*flags*; the manifest/glob-scan wins on *what exists* (e.g. the Python suites CI omits). Mapping
table: Cargo.toml→fmt/clippy/test (`--workspace` iff `[workspace]`); package.json scripts→`npm
ci`+`test`/`build`/`lint`; pyproject→pytest/ruff; PEP-723-without-pyproject→read header per file;
just/Make→enumerate `test`/`lint`/`check`/`build` targets; repo `--check` scripts→adopt documented
invocation; markers→wire the corresponding skill.

## Worked two-layer recipe (this repo)

- **FAST (affected / per-edit):** changed `*.rs`/`Cargo.*` → `cargo test --workspace`; changed
  `skills/<s>/scripts/*.py` or `_shared/*.py` → only that suite (its header command); changed
  `active_set.py`/`beads_hygiene.py`/`upstream.py` → `uv run _shared/sync.py --check`; changed `*.md`
  → markdown-lint subset; path matching a `DRIFT-CHECK.md` §6 glob → yf-drift-check scoped edges.
- **FULL (pre-push / land-the-plane = CI ∪ repo-checks):** `cargo fmt --all -- --check` ·
  `cargo clippy --workspace --all-targets -- -D warnings` · `cargo test --workspace` · all 6 Python
  suites (per-header command) · `uv run _shared/sync.py --check` · yf-drift-check full · (opt-in,
  gated) `cd website && npm ci && npm run build`.

## Drift detection — per-signal fingerprint

Record `{source_path, parsed_value_or_hash}` per signal; re-parse + compare on trigger:

| Signal | Cheap diff |
| :-- | :-- |
| Workspace members | recorded `members` vs current parse |
| CI `run:` steps | hash of extracted steps (skip `if:false`/tag-only) vs recorded |
| Python suite set | `glob('**/test_*.py')` set-diff vs recorded |
| PEP-723 headers | per-file `requires-python`/`dependencies` presence diff (idiom flips) |
| Runner migration | presence-set diff of `justfile`/`Makefile`/`pyproject.toml` |
| package.json scripts | `scripts` keys diff |
| Markers | existence bit (`.markdown-lint-on-edit`, `DRIFT-CHECK.md`) |
| Repo `--check` scripts | discovered check-command set diff |

On mismatch → **re-propose** the affected tier (operator-confirmed; never auto-rewrite — matches
the repo's propose-not-fix posture). The recorded 6-suites-vs-CI delta is the canonical worked
example of a standing re-proposal.
