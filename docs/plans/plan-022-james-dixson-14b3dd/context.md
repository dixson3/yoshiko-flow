---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (aka `beads-skills`) is a collection of beads-backed Claude Code **skills**
(`skills/yf-*`), a `yf` Rust CLI kernel (preflight/doctor/self-update), shared Python helpers
under `_shared/` (vendored into consumers via `_shared/sync.py`), and per-skill `SPEC.md`
requirement docs. Skills are Python (`uv run`, PEP-723 inline deps) + markdown instruction
files; the kernel is Rust (`cargo`). The installed skills are **rust-embed-baked older copies**,
so any change under `skills/` must be tested against the **in-repo** copy under a sandboxed
`HOME` (see `TESTING.md` Tier-2 mechanical drive), never the installed copy. Task tracking is
**beads (`bd`), local-only** — no Dolt remote; upstream issue tracking is coarse GitHub issues
(`gh`, one per plan). SPEC-first is mandatory (AGENTS.md): the `SPEC.md`/`REQ-*` edit lands
before implementation.

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
- Plan directory: `docs/plans/plan-022-james-dixson-14b3dd`

## Operator identity

- Git user: `james-dixson` (James Dixson, GitHub `dixson3`)
- Contact: james@yoshikostudios.com
- Role/authority: project owner and maintainer of `dixson3/yoshiko-flow`; full authority over
  the skills, specs, and upstream issue tracker. Attribution default MIT / Yoshiko Studios LLC.

## Runtime assumptions

- **OS/shell:** macOS (darwin), zsh. Paths and non-interactive shell flags per the beads
  usage mandates (`rm -f`, `HOMEBREW_NO_AUTO_UPDATE=1`, etc.).
- **Toolchain:** `bd` **≥ 1.1.0** (the certification target; installed build is 1.1.0), `uv`,
  `git`, `gh` authenticated, `cargo` for the `yf` kernel. The plan itself certifies against
  1.1.x but **retains a bd<1.1.0 documentation branch** (Epic 1) — do not assume a hard floor.
- **Beads:** local-only Dolt (server mode here), **no Dolt remote** (removed during scoping).
  Never `bd dolt push`. Upstream tracking via `gh` only.
- **Network/credentials:** `gh` auth for issue filing; the EXP-001-style embedded fixture work
  needs internet to fetch/build an older bd (from-source `go install` or GitHub releases).
- **Side effects:** edits under `skills/`, `_shared/`, `spec/`; a micro-experiment (Issue 4.2)
  and Tier-2 mechanical drives run against **throwaway** temp repos/HOMEs — never the live
  `.beads/`. Test drives must use the in-repo skill copy, not the installed rust-embed copy.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
