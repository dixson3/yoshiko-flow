# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (aka `beads-skills`) is a Rust + Python repository providing beads-backed
agent **skills** for Claude Code plus a single compiled CLI, **`yf`**, that installs,
upgrades, verifies, and runs preflight for those skills. Stack: a Rust workspace
(`yf/` crate; `clap`, `rust-embed`, `serde`, `sha2`) whose binary **embeds the `skills/`
tree at build time** (rust-embed) so install needs no repo clone; Python skill-helper
scripts run via `uv` (PEP-723 inline deps). Distribution today is **cargo-dist (`dist`)
v0.32.0** → GitHub Releases + a Homebrew tap (`dixson3/homebrew-tap`); `release.yml` is
cargo-dist-generated and must not be hand-edited (regenerate via `dist generate` from
`[workspace.metadata.dist]` in the workspace `Cargo.toml`). Task tracking is **beads (`bd`)**
with a local Dolt DB; upstream issues live on GitHub (`dixson3/yoshiko-flow`, coarse
granularity — one tracking issue per plan). This plan is the consumer-side vendor-install
work; the production pipeline (cargo-dist) is left intact.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-06-30 -->

- `bd`: bd version 1.0.5 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.25 (1fc7de7c4 2026-06-26 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.95.0 (2026-06-17)
- `glab`: glab 1.105.0 (45c9976d)
- `claude`: 2.1.195 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-018-james-dixson-1d39eb`

## Operator identity

- Git user: `james-dixson` (James Dixson; GitHub `dixson3`)
- Organization: Yoshiko Studios LLC · contact: `dixson3@gmail.com`
- Authority scope: repo owner/maintainer — sole approver for plan gates, release cuts, and
  upstream issue dispositions on `dixson3/yoshiko-flow`. Push to `main` and tag releases is
  operator-authorized (conservative git authority: the pipeline reports a handoff; it does not
  push or cut a release without explicit authorization).

## Runtime assumptions

- **OS/arch:** authored on macOS arm64 (`d3-mbp-m5.local`, Apple Silicon). Execution targets
  macOS (arm64+x86_64) and Linux (x86_64+aarch64); Windows is planned-but-not-built.
- **Shell:** `zsh` is the operator default (relevant to the installer's PATH edit, though this
  plan uses cargo-dist's generated installer which handles shell detection).
- **Toolchain:** a Rust toolchain (`cargo`/`rustc`) for building `yf`; **`dist` (cargo-dist)
  0.32.0 must be installed** to regenerate `release.yml` (gated by the `dist-toolchain`
  capability gate — it is NOT installed at authoring time). `gh` authenticated to GitHub.
- **Network:** `yf self update` and the installer fetch from GitHub Releases (public repo, no
  token needed; a `User-Agent` is required for the API fallback). Builds/tests are offline-capable.
- **Side effects:** writes under `~/.local/bin`, `~/.config/yf`, `~/.cache/yf`,
  `~/.local/share/yf`, and user-scope skill dirs (`~/.claude`, `~/.agents`); edits a shell
  profile's PATH (via the installer). Releases are tag-triggered and operator-authorized.
- **Testing constraint:** `yf self update`'s download→extract→swap path cannot be exercised by a
  plain run against the current latest (v0.3.2) — it requires a forced path against a `.tar.gz`
  release (pre-release tag or local fixture), since v0.3.2 predates the `unix-archive` flip.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
