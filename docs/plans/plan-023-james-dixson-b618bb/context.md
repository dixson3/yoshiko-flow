# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (aka `beads-skills`) — beads-backed Claude Code **skills** (`skills/yf-*`), a `yf`
Rust CLI kernel (`yf/src/`; preflight/doctor/self-update/migrate), shared Python helpers under
`_shared/` (vendored into consumers via `_shared/sync.py`), and per-skill `SPEC.md` docs. Skills
are Python (`uv run`, PEP-723 inline deps) + markdown; the kernel is Rust (`cargo`, package `yf`).
The installed skills/kernel are **rust-embed-baked older copies**, so any change under `skills/` or
`yf/` must be tested against the **in-repo** build / a sandboxed `HOME` (TESTING.md Tier-2), never
the installed copy. Task tracking is **beads (`bd`), local-only** — this repo runs a **per-repo
local Dolt server** (`dolt_mode: server`), no Dolt remote; upstream issue tracking is coarse GitHub
issues (`gh`, one per plan). SPEC-first is mandatory (AGENTS.md). This plan directly hardens that
local-only beads model (the profile `yf preflight` asserts, config placement, gitignore hygiene).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-05 -->

- `bd`: bd version 1.1.0 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.26 (396ef7ce4 2026-06-30 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.96.0 (2026-07-02)
- `glab`: glab 1.106.0 (fc1869c7)
- `claude`: 2.1.201 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-023-james-dixson-b618bb`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`)
- Contact: james@yoshikostudios.com
- Role/authority: project owner and maintainer of `dixson3/yoshiko-flow`; full authority over the
  skills, `yf` kernel, specs, and upstream issue tracker. Attribution default MIT / Yoshiko Studios LLC.

## Runtime assumptions

- **OS/shell:** macOS (darwin), zsh; non-interactive shell flags per the beads mandates.
- **Toolchain:** `bd` ≥ 1.1.0, `uv`, `git`, `gh` authenticated, `cargo` for the `yf` kernel (Epic 1
  and Epic 2 both change Rust in `yf/src/`; a `cargo build`/`cargo test` is required).
- **Beads:** this repo runs a **per-repo local Dolt server** (`dolt_mode: server`) — the plan's
  canonical profile, so this repo is *conformant*, not a repair fixture. Local-only, no Dolt remote;
  never `bd dolt push`.
- **Network/credentials:** `gh` auth for issue reconcile; no network needed for build/test.
- **Side effects:** edits under `yf/src/`, `skills/`, `_shared/`, `SPEC.md`; profile/config
  fixtures run against **throwaway** temp repos/HOMEs — never the live `.beads/`. Test against the
  in-repo build, not the installed rust-embed copy.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
