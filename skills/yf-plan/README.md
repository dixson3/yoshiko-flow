# yf-plan

Structured planning with beads-tracked execution and upstream issue reconciliation.

## Why yf-plan

Claude Code has a native plan mode, but it treats planning as a single-session, single-machine activity: the agent thinks, drafts a plan, and executes it — all in one context. That works for contained tasks. It breaks down when:

- **You need to investigate before committing.** A plan to adopt a new database should benchmark candidates, not guess. yf-plan runs investigation experiments in disposable worktrees during the planning phase, feeding findings back into plan design before any commitment is made.

- **Execution spans multiple environments.** Building a cross-platform tool means some tasks can only run on macOS, others on Windows, others in CI. Native plan mode assumes one machine, one session. yf-plan decomposes plans into epics with dependency-wired issues and gates — a capability gate can block issues that require a platform you don't have, while all other work proceeds. Push the repo, and someone on the right platform picks up where the gate left off.

- **Multiple people need to contribute.** yf-plan tracks execution state in beads, which are stored in the repo alongside the code. Push an in-progress plan upstream and collaborators can pull it into their own environments, claim ready beads, and execute their portion. The bead DAG ensures correct ordering without coordination overhead.

- **You want upstream issue context in the plan.** yf-plan scans GitHub/GitLab issues related to the objective, lets you triage them (include, exclude, partial, supersede), and wires them into the plan's epics. After execution, the reconcile phase automatically updates or closes those upstream issues with references to what was done.

- **Plans should be durable artifacts.** Native plan mode produces ephemeral output that vanishes with the session. yf-plan writes plans as markdown — versioned in git, reviewable in PRs, searchable in the future. Plans land under `docs/plans/` by default, or under `Incubator/<slug>/plans/` when the plan is scoped to a specific incubator (auto-detected from CWD, confirmed during scoping). The plan document records scoping decisions, investigation findings, approach rationale, and execution status.

### How it works

1. **Scope** — You state an objective. yf-plan scans for related upstream issues, asks scoping questions (interactively or via a questionnaire file), and identifies unknowns that need investigation.

2. **Investigate** — For each unknown, yf-plan spawns a sub-agent in a disposable worktree to run experiments. Findings are captured as structured markdown and fed into plan synthesis. Nothing from investigation worktrees lands in the project.

3. **Plan** — yf-plan synthesizes scope + findings into a structured plan document with epics, issues, dependency wiring, capability gates, and upstream issue linkage. You review, iterate, and approve.

4. **Intake** — On approval, yf-plan creates a beads molecule: a DAG of bead issues mirroring the plan's epics, with a start gate that can only be released in a new session. This is the handoff point.

5. **Execute** — In a new session, `/yf-plan execute` resolves the start gate and runs a coordinator loop: find ready beads, dispatch sub-agents, close beads, repeat. **By default the plan runs in an isolated git worktree** (`.worktrees/<plan-id>`, branch `<plan-id>`): code edits accumulate on that branch while bead tracking and the plan folder stay in the primary checkout (the shared Dolt DB resolves from the worktree via git-common-dir, so beads never diverge). Execution falls back to in-place automatically (not a git repo, beads not initialized, an unsafe worktree state, or the `execute.worktree:false` opt-out). Capability gates block work that requires unavailable resources while all other work continues. If a prior execute session crashed mid-run, the resume guard detects the existing epic (no duplicate pour), re-attaches the worktree (surfacing any dirty state), and an orphan sweep resets stuck `in_progress` beads to `open` — never auto-closing — before the loop resumes.

6. **Reconcile** — After execution, in worktree mode yf-plan brings the base current, merges the plan branch back (`git merge --no-ff`) under a single-machine landing lock, and **re-validates the merged state** (the plan's gates plus a configured project `validate-cmd`) before any push — catching regressions that only appear once concurrent changes integrate. It then reports a conservative git handoff (proposed `git`/`bd dolt push` commands, pushed only on explicit authorization), tears the worktree down, and—once the push is authorized—updates upstream issues per the triage dispositions set during scoping.

The worktree execution lifecycle (two address spaces, §5.2→§6.2):

![yf-plan worktree execution lifecycle](spec/worktree-execute-lifecycle.png)

## Prerequisites

Checked at runtime by `scripts/plan_manager.py check`:

| Tool | Version | Install |
|:-----|:--------|:--------|
| `uv` | any | https://docs.astral.sh/uv/ |
| `bd` | >= 1.0.5 | https://github.com/gastownhall/beads |
| `git` | any | system package manager |

Optional:

- `gh` — GitHub CLI (for upstream issue tracking)
- `glab` — GitLab CLI (for upstream issue tracking)

The repo installer (`install.sh`) installs the `PLANS.md` companion rule alongside the skill, to a rules dir anchored by scope and surface — `--scope user` (default) → `~/.<surface>/rules/` (global, shared by every project), `--scope project` → `<git-root>/.<surface>/rules/` (`.claude` or `.agents` per `--surface`). `/yf-plan init` handles consent-only per-project setup (prerequisite check, the prereq-missing opt-out); it does not install the rule. The idempotent scaffold (the `docs/plans` dir + the `/.yf-plan.local.json` and `/.state/` gitignore anchors) is ensured automatically by preflight on every healthy `check`.

## Install

Via the repo-level installer (installs the skill + its companion rule):

```bash
./install.sh                       # all skills -> ~/.claude/{skills,rules}/
./install.sh --scope project       # -> <git-root>/.claude/{skills,rules}/
./install.sh --surface agents      # -> ~/.agents/{skills,rules}/
./install.sh --force yf-plan        # reinstall yf-plan, overwriting its rule
```

Or per-skill: copy the `skills/yf-plan` directory to `~/.claude/skills/yf-plan` and its `protocols/PLANS.md` to `~/.claude/rules/PLANS.md`.

## Usage

```
/yf-plan init                     Initialize yf-plan for this project
/yf-plan <objective>              New plan
/yf-plan continue [<plan-id>]     Resume open plan
/yf-plan capture [<plan-id>] [--retro]   Audit portability and draft missing contract files; --retro also mines the current session's conversation (no status change)
/yf-plan execute [<plan-id>]      Begin execution (new session required)
/yf-plan status [<plan-id>]       Show progress
/yf-plan list                     List all plans
```

Also triggers on planning-intent language: "let's design", "let's plan", "how should we build", "let's architect".

## Phase Model

```
UPSTREAM --> SCOPE <--> INVESTIGATE --> PLAN --> INTAKE
                                                  |
                                          === session boundary ===
                                                  |
                                              EXECUTE --> RECONCILE --> COMPLETE
```

Plans are scoped, investigated, and approved in one session. Execution starts in a new session via `/yf-plan execute`. Reconcile updates linked upstream issues after push.

### Portability contract

At intake, every plan folder is subject to a mechanical portability audit (`plan_manager.py audit`). A plan folder must contain:

- `README.md` — orientation (file map, reading order)
- `context.md` — project environment snapshot (tool inventory with hostname+date header, paths, operator identity, runtime assumptions)
- A `## Motivation` section in `plan.md` or a `motivation.md` file
- `references/upstream-<N>.md` for every non-excluded upstream issue (full body)
- `reviews/pass-<N>.md` for every review cycle (1:1 with phase-log review lines)
- No dangling external refs (absolute paths or `../` outside fenced/inline code)

A cold reader in a different repo, with no access to the drafting conversation, must be able to understand the plan from the folder alone. The audit runs as the **last step of Phase 3 (PLAN)** — after red-team approval, before transition to intake. It is idempotent: safe to run repeatedly as the operator iterates on gaps via `/yf-plan capture`. Override with explicit `--force` on approval (logged to the phase log). See `spec/portability.md` for full requirements and the activation date.

## File Layout

```
SKILL.md                     Claude Code skill entry point (includes all phases inline)
spec/
  phases.md                  Phase model and status value requirements
  cli.md                     Invocation, pre-flight, and plan_manager.py interface
  agents.md                  Agent roles, inputs, outputs, and behavioral constraints
  data.md                    Plan identity, plan.md schema, config, formulas
  prerequisites.md           Required/optional tools, bootstrap flow, install URLs
  portability.md             Portability contract, audit semantics, activation date
  worktree-execute-lifecycle.d2   d2 source for the worktree execution lifecycle diagram
  worktree-execute-lifecycle.png  Rendered lifecycle diagram (referenced from SKILL.md)
agents/
  coordinator.md             Drives execution DAG to completion
  investigator.md            Runs single experiment in disposable worktree
  planner.md                 Synthesizes scope + findings into plan
  reconciler.md              Updates upstream issues per dispositions
  reviewer.md                Conformance/completeness plan check (PASS|INCOMPLETE), runs first
  red-team.md                Adversarial plan review before approval (drives the phase transition)
  captor.md                  Drafts missing portability-contract files for /yf-plan capture
formulas/
  plan-execute.formula.toml  Beads molecule for execution pipeline
  plan-investigate.formula.toml  Beads molecule for investigation wisp
scripts/
  plan_manager.py            Plan CRUD, prerequisite checking, portability audit, crash-recovery resume scan, worktree lifecycle (ensure/path/teardown), landing lock, merged-state validation (run via uv)
  test_worktree.py           Unit tests for the worktree verb cluster + landing lock + validate-merged (run via uv)
  manifest_update.py         Vendored manifest hash/version helper (run via uv)
protocols/
  PLANS.md                   Planning protocol (installed to the scope+surface rules dir, e.g. ~/.claude/rules/PLANS.md or <git-root>/.claude/rules/PLANS.md, by install.sh)
  manifest.json              Hash manifest for PLANS.md
```

Per-plan folder layout after `/yf-plan init` (plan root is either `docs/plans/` or `Incubator/<slug>/plans/` depending on the answer to the scoping incubator question; numbering is global):

```
<plan-root>/<plan-id>/
  plan.md                    The plan (status, phase log, objective, motivation, approach, epics, gates, risks, success criteria)
  README.md                  Orientation and file map for cold readers
  context.md                 Project environment snapshot at plan-authoring time
  findings/                  Investigation experiment results
  references/                Inlined upstream issue bodies (one file per non-excluded issue)
  reviews/                   Reviewer verdicts (one file per review pass)
  diagrams/                  d2 diagrams (.d2 source + .png render) per diagram-authoring
  assets/                    Attachments and generated artifacts (not diagrams)
  scope-answers.md           Scoping questionnaire (complex scoping only)
  upstream-triage.md         Upstream triage working file
```
