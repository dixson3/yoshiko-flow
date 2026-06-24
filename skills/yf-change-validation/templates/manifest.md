# CHANGE-VALIDATION.md (manifest template)

Copy this file to your repository root as `CHANGE-VALIDATION.md`, fill in the four
sections for your toolchain, then mark it approved (see §0). Until approved, the engine is a
silent no-op on an on-edit trigger and `run` returns a clean refusal — it never executes a
recorded command.

The engine reads this file mechanically; it carries no repo vocabulary of its own. You declare
the tiers, command rows, fingerprint signals, and trigger globs here. See the
`yf-change-validation` skill's `spec/schema.md` for the full schema contract and `spec/engine.md`
for the §0 approval gate and run semantics. `change_validation.py infer` drafts a real manifest
from this shape; an operator then reviews and hand-tunes it before flipping §0 to `yes`.

## 0. Status

`approved: no` — change to `approved: yes` once you have reviewed every section. An unapproved
manifest does not drive enforcement: on-edit triggers are a silent no-op and `run` returns a
structured `§0 approved: no` refusal rather than executing any command.

## 1. Tiers

Two ordered command lists. **Row order is run order.** Every `cmd` runs via shell (`sh -c`), so
`cd website && …`, `uv run --script …`, and project-pytest invocations all work as written.

Columns: `id` (optional — a short stable identifier §3 references; omit for FULL-only rows no §3
glob selects), `cmd` (**required** — the shell command string), `cwd` (optional — working
directory relative to repo root; defaults to repo root), `timeout` (optional — seconds; the
engine kills and FAILs the command after this so a hung test cannot wedge land-the-plane).

Executable-only: every row is a runnable shell command. Do **not** list `yf-drift-check` (or any
other prose/LLM trigger) as a row — it is not a shell command, it has no exit code to read as a
verdict, and it fires on its own orthogonal trigger. FULL must be a superset of CI ∪ repo-checks
(do not omit a suite CI runs or a `--check` script CI skips).

### fast

<!-- The affected-scoping tier: cheap, local checks an on-edit trigger runs.
     Worked example (cargo + pytest workspace):
| `cargo-check` | `cargo check --workspace` | | 120 |
| `pytest-core` | `uv run --script tests/core.py` | | 60 |
-->

| id | cmd | cwd | timeout |
|:--|:--|:--|--:|
|  |  |  |  |

### full

<!-- The complete cross-plan safety net: every CI suite plus every repo-check CI omits.
     Worked example:
| `cargo-test` | `cargo test --workspace` | | 600 |
| `pytest-all` | `uv run pytest` | | 600 |
| | `cd website && npm run build -- --check` | | 300 |
-->

| id | cmd | cwd | timeout |
|:--|:--|:--|--:|
|  |  |  |  |

## 2. Signal Fingerprint

One row per toolchain signal the recipe was inferred from. The value is the parsed value (e.g. a
workspace `members` list) or a stable hash (e.g. of the extracted CI `run:` steps). Reading and
comparing the fingerprint is pure file-read + parse — no command execution — so `check-drift` is
cheap enough for an on-edit trigger.

<!-- Worked example:
| `Cargo.toml` | `members=[crates/a, crates/b]` |
| `.github/workflows/ci.yml` | `sha256:9f2c…` (hash of extracted run: steps) |
-->

| source-path | parsed-value-or-hash |
|:--|:--|
|  |  |

## 3. Trigger Scope

Maps each changed-path glob to the subset of FAST command ids it selects. `run --tier fast
--changed <paths>` runs only the **union** of the ids every matched glob selects; with **no**
`--changed`, `run --tier fast` runs the whole FAST tier. Every id here must name a §1 FAST row
that exists (the manifest is referentially closed).

<!-- Worked example:
| `crates/**/*.rs` | `cargo-check` |
| `tests/**/*.py` | `pytest-core` |
-->

| changed-path glob | scopes to (FAST ids) |
|:--|:--|
|  |  |
