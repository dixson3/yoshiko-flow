---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**yoshiko-flow** is a repository of beads-backed skills for coding agents, plus the Rust `yf` CLI
that installs them into five harnesses (claude-code, agents, codex, opencode, pi). It is **both
the source and a consumer of its own skills**, which is the single most important fact for a cold
reader: editing `skills/` changes nothing about the `yf` currently running until a rebuild and
redeploy. See `AGENTS.md` -> "Three artifacts, not one".

The artifacts this plan operates on are **OKF bundles** — the versioned directories under
`docs/plans/<plan-id>/` and `docs/research/<NNN>-<slug>/`. A conformant bundle carries a reserved
`index.md` (orientation/listing) and `log.md` (newest-first phase history) plus typed frontmatter.
A **legacy** bundle instead carries a `README.md` and keeps its phase history inline in `plan.md`.
This plan converts the last 8 legacy bundles to the conformant model.

Stack: Python 3.14 helper scripts run via `uv` with PEP 723 inline dependencies; Rust for the `yf`
binary; `bd` (beads, Dolt-backed) for all task tracking; `gh` for upstream issues.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-09-05 -->

- `bd`: bd version 1.2.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.9 (9f9286029 2026-09-01 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.100.0 (2026-09-03)
- `glab`: glab 1.116.0 (e8436ca8a)
- `claude`: 2.1.259 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-065-james-dixson-7c8cd4`

## Operator identity

- Git user: `james-dixson`
- Role: repository owner and sole maintainer of `dixson3/yoshiko-flow`.
- Authority scope: full — may authorize outward-facing writes (`git push`, `gh issue
  create/close/comment`) and destructive local operations. **The executing agent may not
  self-authorize any of these**; each requires an explicit grant at the moment it is needed.

## Runtime assumptions

- **Shell is zsh**, not bash. zsh does **not** word-split unquoted parameter expansions, and its
  arrays are 1-based. Write constructs that behave identically in both shells; verify loops by
  reading their writes back, never by exit code. See `AGENTS.md` -> "Shell".
- **macOS (darwin)**. `mktemp -d` returns a path under `/var/folders/...` whose realpath is
  `/private/var/folders/...`. That divergence is not cosmetic here — it is the proximate cause of
  the `restore --root` defect this plan deliberately excludes (D3).
- **Network access is required** only for the `gh` calls in Epic 6. Everything else — the audit,
  the transform, the rehearsal, the round-trip — is fully local and offline.
- **Credentials**: `gh` is authenticated against `dixson3/yoshiko-flow`. No token is ever handled
  by a skill; `gh` owns its own credential store.
- **`bd` is local-only** (`dolt.local-only = true`). Propose `git push` alone; never `bd dolt push`.
- **Side effects**: this plan rewrites 8 tracked bundles in place. It writes no engine code (SC12).
  Rollback is `git revert` of a single commit (D5). `okf_hygiene.py backfill --apply` must NEVER be
  run against the real corpus without the operator gate in Epic 4.
- **A `uv run` inside a git worktree** needs `env -u VIRTUAL_ENV` so uv resolves the worktree's own
  environment rather than an inherited one.

## Adjacent-concept glossary

| Term | Meaning |
| :-- | :-- |
| **OKF** | Open Knowledge Format — the bundle model: reserved `index.md` + `log.md` + typed frontmatter |
| **bundle** | one artifact directory (`docs/plans/plan-NNN-.../`), the unit this plan transforms |
| **legacy-readme** | a bundle still carrying `README.md` instead of `index.md`/`log.md` — the 8 targets |
| **backfill** | the three-step legacy transform (stage -> two-rename swap -> cleanup) with a crash journal |
| **objective-divergence** | a halt: the legacy `README.md` `>` objective differs from `plan.md`'s H1 |
| **phase-log-loss** | a halt: dates in `plan.md`'s phase log absent from the staged `log.md` |
| **`--reconcile-objective`** | opt-in mode adopting `plan.md`'s H1 as authoritative on a divergence |
| **saturating label** | a verdict that reads the same for one finding or fifty — why `warn` is not a signal (D6) |
| **land the plane** | the session-close ritual: push, reconcile upstream, close out |

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
