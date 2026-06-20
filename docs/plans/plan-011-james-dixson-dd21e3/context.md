# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`beads-skills` is the source repo for **Yoshiko Flow (`yf`)** — a family of portable,
cross-harness agent skills plus a single Rust CLI (`yf`) that installs/upgrades/verifies
them. The skills live as embedded text trees under `skills/yf-*/` (each a `SKILL.md` +
optional `protocols/*.md` companion rules + `manifest.json`); the `yf` binary embeds the
entire `skills/` tree at build time (`build.rs` + `embed.rs`) so install needs no network or
clone. Rust crate is at `yf/` (Cargo workspace; `cargo build`/`test`/`clippy`/`fmt`).
Issue tracking is **beads** (`bd`, Dolt-backed). Planning is **bdplan** (this skill).
The repo is its own drift-check reference instance (`DRIFT-CHECK.md` at root binds
`SPEC.md` ↔ `README.md` ↔ skill docs). This plan changes how `yf skills install` surfaces
companion rules — from one file per protocol to a single aggregated `YOSHIKO_FLOW.md`.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-06-19 -->

- `bd`: bd version 1.0.5 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.21 (5aa65dd7a 2026-06-11 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.94.0 (2026-06-10)
- `glab`: glab 1.102.0 (b5a548b3)
- `claude`: 2.1.178 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/beads-skills`
- Working directory at plan creation: `/Users/james/workspace/dixson3/beads-skills`
- Plan directory: `docs/plans/plan-011-james-dixson-dd21e3`

## Operator identity

- Git user: `james-dixson` (James Dixson, Yoshiko Studios LLC; `dixson3@gmail.com` /
  `james@yoshikostudios.com`; GitHub `dixson3`).
- Role/authority: sole maintainer of this repo and the published `dixson3/yoshiko-flow`.
  Full authority over scope, approval, and merge/push. Attribution convention for new
  modules/LICENSE: MIT, current year, Yoshiko Studios LLC.

## Runtime assumptions

- macOS (Darwin, Apple Silicon), `zsh`. Rust toolchain present (`cargo`); `uv` for the
  bdplan Python helpers; `bd` ≥ 1.0.5; `git`; `gh` (GitHub upstream).
- All changes are local-repo edits + Rust build/test — no network required except for the
  optional land-the-plane `gh issue` + `git push`, which are conservative (operator-authorized).
- Side effects are confined to this repo. The `yf` rule-install code under test writes to a
  caller-supplied `--target` (tests use a temp dir), never to the real `~/.claude/rules`
  during tests.
- Push authority is **conservative**: execution automates local work; `bd dolt push` / `git
  push` run only on explicit operator authorization.

## Adjacent-concept glossary

- **Protocol / companion rule** — an always-loaded `protocols/*.md` file a skill ships
  (e.g. `PLANS.md`); installed into the rules dir as a behavioral trigger contract.
- **Aggregate / `YOSHIKO_FLOW.md`** — the new single `yf`-managed rule file this plan
  introduces, holding all protocols as fenced sections.
- **Fence / section** — a paired `<!-- yf-flow: … -->` … `<!-- yf-flow:end … -->` block
  wrapping one protocol's verbatim body inside the aggregate.
- **Reconcile-prune** — dropping aggregate sections whose protocol is no longer embedded or
  is `deprecated:true`.
- **Marker** — the existing `<!-- yf-skills: v=… tree=… -->` integrity line in deployed
  `SKILL.md` (`marker.rs`); `flow.rs` is its analog for the aggregate rule file.
- **Manifest** — `protocols/manifest.json`: per-protocol `sha256` + `version` +
  `previous_versions` + `deprecated`, the basis for preflight verdicts.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
