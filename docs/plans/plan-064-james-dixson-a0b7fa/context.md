---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` is the source repository for the `yf-*` family of beads-backed agent skills
(`yf-plan`, `yf-research`, `yf-okf`, `yf-okf-hygiene`, `yf-drift-check`, and others), plus the
`yf` Rust CLI that installs them into each supported harness.

Stack: Python 3 helper scripts run via `uv` with PEP 723 inline dependencies (no project
virtualenv to activate), a Rust binary under `yf/`, and `bd` (beads, Dolt-backed) for all task
tracking. Markdown is plain GFM throughout.

Three non-obvious properties a cold reader needs:

- **The repository is both the source and a consumer of its own skills.** Editing `skills/`
  changes nothing about the running session — the repo source, the binary-embedded tree, and the
  session-installed skill are three artifacts that move independently. `skills/` is not one of
  the roots the `SKILL_DIR` resolver searches.
- **Shared Python is VENDORED, not imported.** Skills must stay independently installable, so
  `_shared/*.py` is copied into each consumer by `_shared/sync.py`. One hand edit to
  `_shared/okf.py` fans out to 5 skill copies, and the FAST validation tier gates on the copies
  being in sync. **This plan edits `_shared/okf.py`, so that fan-out is directly load-bearing.**
- **SPEC-first.** A behavior change lands its `SPEC.md` requirement (new `REQ-*` id, revised
  wording, amendment-log entry) *before* the code. This plan's Epic 0 exists for that reason.

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
- Plan directory: `docs/plans/plan-064-james-dixson-a0b7fa`

## Operator identity

- Git user: `james-dixson` (james@yoshikostudios.com)
- Role: repository owner and sole maintainer; authority to approve plans, authorize pushes to
  `origin/main`, and file/close issues on `dixson3/yoshiko-flow`.
- Authority scope: **outward-facing writes remain operator-gated.** Pushes, `gh issue create` /
  `close`, and `land --apply` require explicit per-act authorization; an executing session never
  self-authorizes them.

## Runtime assumptions

- **OS / shell:** macOS (Darwin 25.5.0), **zsh 5.9** — not bash. zsh does not word-split unquoted
  parameter expansions and its arrays are 1-based. Write constructs that behave identically in
  both shells; verify loop effects by reading writes back, never by exit code.
- **`git` work tree required.** Several deliverables (the `_vcs_ignored` helper, the `restore`
  refusals) are *defined* in terms of version-control state, and one of them — the fail-open
  path — is specifically about behavior when `git` is **absent**. Tests must cover both.
- **Network / credentials:** `gh` authenticated against `dixson3/yoshiko-flow` is needed only for
  Epic 5's issue writes. Epics 0-4 are fully offline.
- **Side-effect permissions:** Epics 0-4 write only inside the repository and to temp dirs.
  **No epic in this plan runs `okf_hygiene.py backfill --apply` against the real corpus** — the
  transform is deferred (D6). Apply-path testing happens in sandboxes.
- **Beads:** `bd` >= 1.1.0 with a healthy local DB; the repo is Dolt local-only, so propose
  `git push` alone and never `bd dolt push`.
- **Deployment:** `yf self install` must NOT run mid-execution. Redeploy is a land-the-plane step
  from a clean `main` in sync with `origin`, after the FULL tier passes on the merged tree.

## Adjacent-concept glossary

| Term | Meaning |
| :-- | :-- |
| **OKF** | Open Knowledge Format — the artifact-folder model yf skills emit: a reserved `index.md` (bundle listing) and `log.md` (newest-first history), plus typed frontmatter on every member. |
| **bundle** | One artifact folder (a plan, research project, or incubator) treated as a portable unit. |
| **member** | A non-reserved file inside a bundle. `index.md` and `log.md` are reserved and are never members. |
| **`legacy-readme`** | A bundle still carrying the pre-OKF `README.md` orientation file instead of `index.md`. The 8 bundles #316 targets. |
| **index drift** | Disagreement between a bundle's `index.md` and its actual members: `ghost` (listed but absent), `missing` (present but unlisted). |
| **the swap** | `backfill`'s two-rename commit: `bundle -> .okf-stash`, then `staging -> bundle`. The window both journal defects live in. |
| **residue** | Untracked build output (`__pycache__/`, `*.pyc`) inside a bundle. The subject of #294. |
| **FAST / FULL tier** | `CHANGE-VALIDATION.md` validation tiers — FAST runs on edit over changed paths; FULL is the once-per-land superset. |
| **vendored copy** | A committed duplicate of a `_shared/` file, regenerated by `_shared/sync.py`, never hand-edited. |

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
