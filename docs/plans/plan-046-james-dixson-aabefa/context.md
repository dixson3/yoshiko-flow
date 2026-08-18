---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**`dixson3/yoshiko-flow`** — a repository of beads-backed skills for Claude Code and
compatible agent harnesses, plus `yf`, the Rust CLI kernel that installs and validates them.
It is **both the source and a consumer of its own skills**: `skills/` in this working tree is
the source, while the running session resolves an *installed* copy elsewhere.

Relevant to this plan specifically:

- **`_shared/okf.py`** is the canonical OKF bundle engine, **vendored byte-identical** to four
  skill copies (`yf-plan`, `yf-research`, `yf-incubator`, `yf-okf`) by `_shared/sync.py`, which
  is invoked **manually** — there is no hook and no CI step.
- **`skills/yf-okf/spec/OKF-BASELINE.md`** records upstream OKF **verbatim** and is a
  **fixed-authority** node in `DRIFT-CHECK.md`; `OKF-YF-EXTENSIONS.md` carries yoshiko-flow
  opinion. That separation is the discipline this plan must preserve.
- **SPEC-first is mechanically forced**, not merely policy: `DRIFT-CHECK.md` §7 marks spec
  nodes as fixed authority, so editing an implementation ahead of its requirement produces a
  CONFLICT rather than a FAIL.
- Validation is two-tiered (`CHANGE-VALIDATION.md` FAST / FULL); the Rust coverage gate
  (`yf/src/coverage.rs`) accepts **only** `REQ-YF-` ids and scans **only** `yf/src/**`, so every
  `REQ-OKF-*` in this plan is gated by nothing mechanical beyond the tests it ships with.

Stack: Rust (the `yf` kernel), Python 3.14 run via `uv` with PEP 723 inline dependencies
(the skill scripts), markdown + YAML frontmatter (the artifacts). Task tracking is `bd`
(beads) on Dolt in **server mode**, `dolt.local-only = true`, with `.beads/` git-excluded.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-18 -->

- `bd`: bd version 1.1.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.3 (507230998 2026-08-07 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.97.0 (2026-07-31)
- `glab`: glab 1.113.0 (d62881304)
- `claude`: 2.1.228 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-046-james-dixson-aabefa`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson (`james@yoshikostudios.com`) — repository owner and sole
  maintainer of `dixson3/yoshiko-flow`.
- Authority scope: full write authority on the repository and on upstream GitHub issues.
  Push and issue-close remain **operator-authorized per action** (yf-plan GR-PLAN-003), not
  delegated to the executing session.

## Runtime assumptions

- **OS / shell:** macOS (Darwin 25.5.0, arm64), `zsh`. Nothing in the plan is
  macOS-specific, but the tool versions above were captured there.
- **Network access is REQUIRED, and this is unusual for this repo.** Issue 2.1 fetches the
  OKF **v0.1** spec verbatim from a prior upstream commit of
  `GoogleCloudPlatform/knowledge-catalog`. A cold reader offline cannot execute Epic 2 as
  written. The **v0.2** spec is already vendored to `references/okf-spec-v0.2.md`, so only the
  v0.1 fetch has this dependency.
- **Credentials:** an authenticated `gh` for the v0.1 fetch and for Epic 5's issue
  close/file operations. No token is ever written to config — `gh` owns its own credential
  store.
- **Side effects, in ascending order of consequence:**
  - *Local, reversible:* Epic 4 rewrites ~19 existing `index.md` files in one mechanical pass.
    Reverted with `git checkout` on the affected paths; gated on operator consent regardless.
  - *Outward-facing:* Epic 5 closes #92 and #118 and files 3 new issues. Each is
    operator-authorized per action.
- **The skill-artifact constraint (AGENTS.md).** This plan edits `skills/yf-plan/README.md`
  and the shared engine **while running under yf-plan**. That is safe — the repo's `skills/`
  matches none of the resolver's six roots, so there is no self-modification hazard mid-run.
  **The one real constraint: do NOT run `yf skills install` or `yf self install` during
  execution.** `plan_manager.py` is re-invoked per call, so a mid-execution deploy takes effect
  in the same session for the *scripts* while `SKILL.md` prose stays loaded from invocation —
  a half-deployed session runs new scripts against old prose. Deploy at land-the-plane.
- **`bd` requires 1.1.2+** and a healthy Dolt server; `dolt.local-only = true`, so **never**
  propose `bd dolt push`.

## Adjacent-concept glossary

| Term | Meaning |
| :-- | :-- |
| **OKF** | Open Knowledge Format — an open spec for knowledge bundles (a directory of markdown with YAML frontmatter), published by `GoogleCloudPlatform/knowledge-catalog`. Currently **v0.2**; this repo's baseline is pinned to v0.1. |
| **Bundle** | An OKF directory: reserved `index.md` (listing) and `log.md` (history) plus *concept documents*. Every yf-plan and yf-research folder is one. |
| **Concept document** | Any non-reserved `.md` in a bundle. OKF's single MUST is that it carries a `type` key. |
| **Reserved filename** | `index.md` / `log.md`. Reserved at **every** level, which is why renaming them to `_index.md` is not an option. |
| **Baseline vs extensions** | `OKF-BASELINE.md` = what OKF says, verbatim. `OKF-YF-EXTENSIONS.md` = yoshiko-flow's opinion on top. Never mix. |
| **Vendoring / fan-out** | `_shared/okf.py` is copied byte-identical into four skills by `_shared/sync.py`. A "blast radius" of five files for any engine edit. |
| **Index drift** | An index listing a file that no longer exists (**ghost**) or omitting one that does (**missing**). A stale index asserts something false, which is worse than no index. |
| **Progressive disclosure** | OKF §8's stated rationale for index files: let a reader see what a directory holds before opening everything. |
| **FAST / FULL tier** | The two `CHANGE-VALIDATION.md` tiers — per-edit affected checks vs the once-per-land superset. |
| **Fixed authority** | A `DRIFT-CHECK.md` node kind. A conflict means the *derived* artifact is wrong; you never edit a spec to make an implementation fit. |
| **Coarse tracker** | One upstream GitHub issue per plan-scale effort, not one per bead — this repo's declared upstream granularity. |
| **Land the plane** | Session-close ritual: FULL-tier validation, push open beads upstream, deploy. |

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
