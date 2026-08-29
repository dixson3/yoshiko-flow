---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**`yoshiko-flow`** (working directory historically `beads-skills`) is the source repository for
the `yf-*` family of agent skills — `yf-plan`, `yf-research`, `yf-beads-upstream`,
`yf-beads-hygiene`, `yf-change-validation` and others — plus the `yf` Rust CLI that embeds and
deploys them.

Stack: **Python 3.11+** skill scripts run via `uv run` with PEP 723 inline dependency metadata
(no project virtualenv, no `requirements.txt`); a **Rust/cargo** workspace under `yf/` that
`rust-embed`s the `skills/` tree at compile time; **`bd` (beads)** as the sole task tracker;
**`gh`** for all upstream issue operations.

Two non-obvious properties a cold reader must know:

1. **The repo is both the SOURCE and a CONSUMER of its own skills.** Editing `skills/<name>/`
   changes nothing about the skill the current session is running — there are three independent
   artifacts (repo source, binary-embedded tree, session-installed copy). See `AGENTS.md`
   §"Three artifacts, not one". The corollary that matters for this plan: **do not run
   `yf skills install` or `yf self install` mid-execution**; deploy at land-the-plane only.
2. **SPEC-first is mandatory.** A `REQ-*` requirement lands (or is staged ahead of code in the
   same change-set) *before* the behavior change it governs. Epic 0 of this plan exists for that
   reason and is not optional sequencing.

Validation is recorded in a repo-root `CHANGE-VALIDATION.md` (approved), whose FAST tier runs the
`yf-beads-upstream` pytest suite plus two contract-check scripts on any edit under
`skills/yf-beads-upstream/scripts/**`.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-28 -->

- `bd`: bd version 1.2.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.6 (7938ca5d5 2026-08-25 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.98.0 (2026-08-20)
- `glab`: glab 1.115.0 (c3612c8de)
- `claude`: 2.1.247 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-058-james-dixson-0e36fd`

## Operator identity

- Git user: `james-dixson` (James Dixson, `james@yoshikostudios.com`)
- Role: sole maintainer and operator of `dixson3/yoshiko-flow`; owns the upstream GitHub repo.
- Authority scope: full authority over this repository's code, SPEC and plan corpus. **Approval
  of this plan, authorization of any upstream write (push / PR / issue create / issue close), and
  resolution of the Pruning Authorization gate are the operator's alone** and are never delegated
  to an executing session.

## Runtime assumptions

- **OS / shell:** macOS (darwin 25.5.0), `zsh`. Nothing in the plan is macOS-specific; the
  `du`/`bd`/`gh` invocations are portable to Linux.
- **`bd` must be >= 1.1.0 and the repo's beads DB healthy.** The plan's measurements assume a
  populated universe; on a fresh repo the fan-out is fast and the defect is invisible. Reproducing
  EXP-001 requires a comparable universe (this one: 1,801 beads).
- **Network:** required only for `gh` (upstream issue reads at triage, and the upstream writes at
  intake/reconcile). Epic 1's fix, Epic 2's tests and Epic 3's check are all **offline** — the
  test suite stubs every subprocess.
- **Credentials:** `gh` owns its own credential store; the skill handles no token and none is
  written to config. No secret is required by, or may be added by, this plan.
- **Side-effect permissions.** Execution edits files under `skills/yf-beads-upstream/` and
  `CHANGE-VALIDATION.md` in a git worktree. Three actions are **out of the executing session's
  authority** and must be brought to the operator: any upstream write, any `bd`-DB-destructive
  operation, and Epic 4's prune (which additionally requires its own consent gate).
- **Concurrency (live at authoring time).** Four sessions share this checkout via git worktrees.
  This plan is authored and executed in `.worktrees/plan-058-upstream-fix` on branch
  `plan-058-james-dixson-0e36fd`. **Never `git checkout`/`git switch` in the shared root** — doing
  so previously landed one session's commits on another's branch.

## Adjacent-concept glossary

| Term | Meaning |
| :-- | :-- |
| **bead** | One tracked work item in `bd` (beads). This repo's universe is 1,801 of them, 37 open. |
| **universe** | Every bead ever created, closed included — what `bd list --all --json` returns. |
| **fan-out** | The defect: one subprocess spawned per bead, serially, over the universe. |
| **N+1** | The general shape — one bulk query followed by one per-row query for data the bulk query already returned. |
| **`external_ref`** | A bead field holding the URL of the upstream GitHub issue it is mirrored to. Absent on most beads *by design* (coarse granularity). |
| **coarse granularity** | This repo's upstream convention: ONE tracking issue per plan-scale effort, never one per execution bead (`AGENTS.md`). |
| **hoist** | Push a bead upstream *and* close it locally with a reversible tombstone. A plain `push` leaves it open and mirrored. |
| **tombstone** | The reversible `bd close -r` marker a hoist leaves behind; `unhoist` reverses it. |
| **`close_reason`** | Free prose recorded when a bead closes. Frequently carries decision rationale, not just a marker — load-bearing for Epic 4. |
| **gate** | A first-class bead blocking work until a condition is met. `probe`/`build`/`consent`/`manual` classes differ in whether a sweep may run them unattended. |
| **fail-closed** | The contract that an unverified upstream write halts *before* any destructive follow-on stage. |
| **FAST / FULL tier** | `CHANGE-VALIDATION.md`'s two validation tiers — per-edit vs once-per-land. |
| **Dolt** | The versioned SQL database backing `bd`. A DELETE creates a new commit; history is not reclaimed. |

## Additional context

**The measurements in `findings/` are machine- and corpus-specific.** They were taken on the host
and date in the snapshot header above, against a 1,801-bead universe. The *equivalence* result
(EXP-002) is a property of the data model and travels; the *timings* (334 s, 0.186 s/call) scale
with universe size and machine, and a cold reader on a different corpus should re-measure rather
than quote them.

**The reproduction is safe to re-run.** `upstream.py push --issues <id>` **without** `--apply`
writes nothing — `create_or_update` returns before any write when `apply` is false
(`upstream.py:930`). That was verified by reading the code before running it, and is why EXP-001b
could be executed against the live repository.

**Why the harness is vendored.** `assets/exp001-equivalence-harness.py` and its logs are copied
into this bundle deliberately: the findings cite them as the evidence for the load-bearing
equivalence claim, and a cold reader in another repo must be able to re-run the claim rather than
take it on trust.
