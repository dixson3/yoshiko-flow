`/yf-plan` turns an objective into two durable things: a versioned plan folder under `docs/plans/`, and a beads-tracked DAG of execution work. It replaces the harness's native plan mode, which treats planning as a single-session, single-machine activity — think, draft, execute, all in one context. That model works for a contained task. It breaks the moment the work needs investigation before commitment, spans more than one machine, or has to survive the end of the session.

## When it fires

`/yf-plan` runs on the explicit command and on planning-intent language — "let's design", "let's plan", "how should we build", "let's architect". It **overrides** the native plan mode: where the harness would enter its own plan/act flow, `/yf-plan` takes over instead.

Reach for it when a piece of work has any of these properties:

- **It needs investigation before you commit.** A plan to adopt a new database should benchmark candidates, not guess.
- **Execution spans environments.** Some tasks only run on macOS, others on Windows, others in CI. One session on one machine cannot cover them.
- **More than one person contributes.** Collaborators pull an in-progress plan into their own clones and work their portion.
- **The plan itself should be a durable artifact** — versioned in git, reviewable in a pull request, and searchable next year.

Skip it for a quick contained edit that fits in one turn. That is what the native mode is for, and `/yf-plan` does not try to displace it there.

## The phase model

A plan moves through a fixed phase machine. Everything up to intake happens in one session; execution begins in a new one.

```
UPSTREAM → SCOPE ↔ INVESTIGATE → PLAN → INTAKE
                                          │
                                  === session boundary ===
                                          │
                                      EXECUTE → RECONCILE → COMPLETE
```

There is no `EXECUTE → PLAN` transition. A scope change that needs epic surgery re-enters `PLAN` before intake — the phase machine forbids re-planning mid-execution.

| Phase | What happens |
| :--- | :--- |
| **SCOPE** | You state an objective. `/yf-plan` scans for related upstream issues, asks scoping questions (inline for three or fewer, via a `scope-answers.md` questionnaire otherwise), and identifies unknowns that need investigation. |
| **INVESTIGATE** | For each unknown, a sub-agent runs an experiment in a disposable worktree. Each result is written to `findings/exp-NNN-*.md` before the next sub-agent spawns. Nothing from an investigation worktree lands in the project. |
| **PLAN** | Scope plus findings are synthesized into a plan document — epics, dependency-wired issues, capability gates, upstream linkage. Two review passes run in order: a mechanical **conformance** check (`PASS` / `INCOMPLETE`), then an adversarial **red-team** (`APPROVE` / `REVISE` / `INVESTIGATE-MORE`). Both agents are read-only with respect to the repository under review — a sandbox spike outside it is authorized; only the main session writes files. |
| **INTAKE** | On approval, `/yf-plan` writes a content **fingerprint** over the plan's reviewed sections, auto-commits the plan folder locally, lands it per the landing strategy, and files a single upstream tracking issue. No beads are poured yet — the fingerprint is the execution-eligibility token. |
| **EXECUTE** | In a new session, `/yf-plan execute` pours the bead DAG, resolves the start gate, and runs the coordinator loop: find ready beads, dispatch sub-agents, close beads, repeat. |
| **RECONCILE** | After execution, the branch is merged back, the merged state is re-validated, and — on authorization — the push happens and upstream issues are updated. |
| **COMPLETE** | Containers cascade-close bottom-up; the plan is marked `complete`. |

## Approval is bound to what you reviewed

At approval, `/yf-plan` records a **fingerprint** — a content hash over the plan's reviewed sections. The frontmatter, the `**Field:**` lines, the phase log, the `reviews/` directory, and the `## Upstream Issues` section are all positionally excluded, so ordinary bookkeeping never disturbs it.

If the plan's content changes after approval, the stored fingerprint goes stale. A **stale-approved** plan cannot execute until a fresh conformance → red-team → portability cycle re-approves it. The plan that runs is the plan you approved, or the review cycle runs again. An explicit `--force` overrides this and is logged to the phase log.

The approval prompt itself is gated. A `ready-check` verifies both preconditions — the last recorded red-team verdict is `APPROVE`, and the portability audit passes — before you are ever asked to approve. Approval is consent to an already-verified plan, not "approve, then verify."

## Execution runs in an isolated worktree

By default, execution runs in a git worktree at `.worktrees/<plan-id>`, on branch `<plan-id>-execute`, cut from a **pinned base** — `main`, or a feature branch — never ambient HEAD. Two address spaces coexist:

- **Code edits** accumulate on the worktree branch.
- **Bead tracking and the plan folder** stay in the primary checkout.

The shared bead database resolves from the worktree via git-common-dir, so beads never diverge across the two spaces. Execution falls back to in-place automatically when a worktree is not viable — not a git repo, beads not initialized, an unresolvable base, an unsafe worktree state, or the `execute.worktree: false` opt-out.

**Capability gates** block work that needs a resource you do not have while all other work continues. A gate is a first-class `-t gate` bead, resolved with `bd gate resolve`; blocked gates are reported only after every unblocked bead has drained.

**Crash recovery** is one guard. If a prior execute session died mid-run, `resume-scan` detects the existing epic (no duplicate pour), re-attaches the worktree and surfaces any dirty state, and an orphan sweep resets stuck `in_progress` beads back to `open` — never auto-closing — before the loop resumes.

## Reconcile merges first, then validates, then pushes

`RECONCILE` lands the branch in a fixed order:

1. Acquire the single-machine landing lock.
2. Bring the pinned base current and merge `<plan-id>-execute` back with `git merge --no-ff`.
3. Run merged-state validation — the plan's gate `Test:` commands plus a configured project `validate-cmd`.
4. On failure, halt with the lock still held.
5. On pass, release the lock and report a conservative git handoff.

Re-validating the *merged* tree catches regressions that only appear once concurrent changes integrate — a bare green on the branch is never presented as integration-safe. When no `validate-cmd` is configured, reconcile emits a prominent "cross-plan not checked" notice rather than a silent pass.

Git authority is conservative for the remote. `/yf-plan` reports the proposed `git` and `bd dolt push` commands and pushes only on explicit authorization. The one carve-out is a **local** commit at the plan-to-execute boundary, scoped to the plan folder (never `git add -A`) and refused on the default branch.

## Portable plan folders

Every plan folder is an OKF bundle — a self-contained artifact a cold reader in another repo can understand from the folder alone. At intake, a mechanical portability audit (`plan_manager.py audit`) enforces that it contains:

- the reserved `index.md` (bundle listing) and `log.md` (newest-first phase history);
- `context.md` — a project environment snapshot with tool inventory, paths, and operator identity;
- a `## Motivation` section (or a `motivation.md`);
- `references/upstream-<N>.md` for every non-excluded upstream issue;
- `reviews/pass-<N>.md` for every review cycle, one-to-one with the log's review lines;
- no dangling external references.

The audit is the last step of `PLAN`, before the approval prompt — so approval consents to an already-portable plan. It is idempotent; run `/yf-plan capture` mid-drafting to audit and draft missing files without changing status.

## Work rejoins the team

`/yf-plan` scans GitHub or GitLab for issues related to the objective and lets you triage each one — include, exclude, partial, or supersede. The dispositions are wired into the plan's epics. After execution, the reconciler updates or closes those upstream issues with references to what was actually done, so solo output flows back to collaborators without manual bookkeeping. Upstream tracking is coarse by default: one issue per plan, filed at intake — see [yf-beads-upstream](/skills/yf-beads-upstream/).

## Usage

| Command | Effect |
| :--- | :--- |
| `/yf-plan init` | Consent-only per-project setup (prerequisite check). |
| `/yf-plan <objective>` | Start a new plan. |
| `/yf-plan continue [<plan-id>]` | Resume an open plan. |
| `/yf-plan capture [<plan-id>] [--retro]` | Audit portability and draft missing contract files; `--retro` also mines the current session. No status change. |
| `/yf-plan execute [<plan-id>]` | Begin execution — requires a new session. |
| `/yf-plan status [<plan-id>]` | Show progress, including any stale or parked flags. |
| `/yf-plan list` | List all plans. |

Plans land under `docs/plans/<plan-id>/` by default, or under `Incubator/<slug>/plans/<plan-id>/` when scoped to a specific [incubator](/skills/yf-incubator/) (auto-detected from the working directory, confirmed during scoping). Plan-id numbering is global across both roots.

`/yf-plan` is a beads-backed skill; it shares the `bd` support layer with [yf-research](/skills/yf-research/) and runs through the same `yf preflight` gate before it acts.
