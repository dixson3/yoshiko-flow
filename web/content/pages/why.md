Title: Why yoshiko-flow
Slug: why
Subtitle: durable, portable, resumable work — instead of ephemeral single-session agents

AI coding agents are good at contained, single-session tasks: think, act, done. But real work
rarely fits in one session on one machine. It spans days, environments, and people; it needs to
be investigated before it's committed to; and it should leave durable artifacts a teammate — or
a future you — can pick up. The native mechanisms most agent harnesses ship (plan mode, a
built-in TODO list, session memory) are **ephemeral and harness-locked**: they vanish when the
session ends and can't travel to another tool, machine, or collaborator.

**yoshiko-flow is a bet that the state of your work belongs in your repo, not in a vendor's
session.** Every stateful skill records what it's doing as durable, portable artifacts —
[beads](/architecture/) issues stored alongside the code, versioned markdown plans, incubator
notes — so work survives a crash, resumes in a fresh session, moves between machines, and is
reviewable in a pull request.

[`/yf-plan`](/skills/yf-plan/) is the flagship, and it embodies most of these ideas, so it makes
a good lens. The principles below generalize to every skill.

## Durable state lives in the repo

Many coding agents ship a plan mode, and its output is ephemeral — it disappears when the session
ends. yoshiko-flow writes work as first-class artifacts instead: `/yf-plan` writes plans as
markdown under `docs/plans/`, and tracks
execution in **beads** — an issue database committed next to the code. Because the state is in
the repo, it's versioned in git, reviewable in a PR, and searchable next year. Nothing important
lives only in a chat transcript.

## Resumable across sessions and machines

Work that spans environments can't assume one machine and one context. `/yf-plan` decomposes a
plan into epics of dependency-wired issues with **gates**. A capability gate blocks the tasks
that need a platform you don't have, while all other work proceeds.

Two kinds of resumption follow, and they run on different mechanisms:

- **Same clone, new session.** The bead database is a local Dolt database under `.beads/`. It
  survives a crash or a closed session. The next session reads it, resets any stuck in-progress
  items, and continues — it never silently loses or double-does work.
- **Across machines.** The bead database is local-only and gitignored, so pushing the repo does
  **not** carry it. What travels is the git-committed **plan folder** plus a coarse **upstream
  tracking issue** — one issue per plan, filed at land-the-plane. A capable machine reads the
  committed plan, re-pours its beads locally, and works the gate that blocked the first machine.

There is no live shared bead state across machines. Two clones do not see each other's in-flight
beads, claims, or gate resolutions. Cross-machine handoff moves through the git-committed plan and
the upstream issue, which point a capable clone at the work — they do not transfer the bead
database itself.

## Investigate before you commit

A plan to adopt a new database should benchmark candidates, not guess. `/yf-plan` runs
investigation experiments in disposable worktrees *during* planning, feeding findings back into
the design before anything is committed to. The same instinct — gather evidence, then decide —
drives [`/yf-research`](/skills/yf-research/), which turns a question into a cited, resumable
report rather than a one-shot answer.

## Portable by design — replacing the ephemeral native mechanisms

yoshiko-flow deliberately **replaces** the harness built-ins that trap state in a single vendor:

- **Planning** — many coding agents have a plan mode. `/yf-plan` replaces the native one with a
  scoped, reviewable, resumable pipeline whose plans are durable files.
- **Task tracking** — `bd` (beads) replaces the native TODO list. Beads are portable, ordered by
  a real dependency graph, and pushable upstream.
- **Memory** — durable decisions go to `AGENTS/` rules or beads, not a Claude-only memory store,
  so another clone, machine, or agent harness can see them.

The skills install into whichever harness you use (Claude Code by default, or the `.agents`
surface), so the same portable workflow follows you across tools.

Replacing native built-ins is the low bar. Many coding agents already ship a plan mode, and other
planning frameworks investigate before building and keep their state in files. What sets `/yf-plan`
apart is narrower and concrete:

- its bead state is single-machine and non-portable by design — cross-machine handoff moves through
  the committed plan folder and a coarse upstream issue, not a shared database;
- approval binds to the reviewed plan, so a plan that changed after sign-off cannot silently execute;
- execution is re-validated against the merged tree, not only the branch it was written on;
- upstream issues are reconciled after the work lands.

A fuller framework comparison sets these against the wider field.

## Where yf-plan sits in the field

The planning landscape is crowded, and most of it is right. Spec-first development, PRD-to-task
graphs, agent-team methods, plan/act modes, and context-rot loops have all converged on the same
good instincts: decide before you build, keep state in files, decompose into a dependency graph,
verify separately, and survive long runs. yf-plan agrees with the field on every one of those.
The tools worth measuring against are real:

- **[GitHub Spec Kit](https://github.com/github/spec-kit)** — the spec-driven-development
  flagship, and widely adopted. A Markdown specification is the executable center of the workflow,
  and a resumable workflow engine persists state across human review gates.
- **[Kiro](https://kiro.dev/) (AWS)** — an enterprise spec-driven IDE and CLI. A prompt becomes
  `requirements.md`, `design.md`, and `tasks.md`; it adds automated-reasoning contradiction checks
  on requirements and a dependency-graph executor that runs tasks in concurrent waves.
- **[BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD)** — a multi-agent agile team.
  Specialized personas (Analyst, PM, Architect, Scrum Master, Dev, QA) drive a four-phase SDLC,
  and a Scrum Master agent shards a monolithic PRD into per-story files so the Dev agent loads
  only what a story needs.
- **[Taskmaster](https://github.com/eyaltoledano/claude-task-master)** — parses a PRD into a
  dependency-ordered `tasks.json` graph that the agent consults every session, giving a long build
  an explicit, durable "what's next."
- **[Aider architect mode](https://aider.chat/docs/usage/modes.html)** — splits reasoning from
  editing across two models. An architect model describes the solution; an editor model turns it
  into precise file edits, measurably improving edit accuracy with no project scaffolding.
- **[Cline / Roo Plan-Act](https://docs.cline.bot/core-workflows/plan-and-act)** — a read-only
  Plan mode explores and strategizes with no file writes, then carries full context into an Act
  mode that executes. Roo adds per-mode tool and file permissions.
- **[The Ralph loop](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)** —
  restarts the same agent with a fresh context each iteration. Each pass reads durable state from
  disk, does exactly one task, verifies it, commits, and exits, making the iteration rather than
  the chat session the unit of work.
- **[GSD](https://github.com/chudeemeke/get-stuff-done)** — runs Plan, Execute, and Verify each in
  its own fresh session, keeps all state in files, and spawns parallel sub-agents with isolated
  contexts so the main context stays lean.
- **[grill-me](https://agentpatterns.ai/agent-design/grill-me-technique/)** — inverts the flow:
  the agent interrogates your plan one decision at a time, one question per turn, surfacing hidden
  assumptions before any code commits to them.
- **[claude-protocol](https://github.com/weselow/claude-protocol)** — the honest closest analog.
  It tracks tasks in the same `bd` (beads) database yf-plan uses, runs one task per worktree per
  PR, and enforces discipline with hooks that block rather than instruct: edits on `main` blocked,
  completion without a checked checklist blocked.

Spec Kit, Kiro, Taskmaster, Aider, Cline, and Roo are widely adopted; BMAD and the Ralph loop are
heavily discussed; GSD, grill-me, and claude-protocol are niche (as of 2026-07). Adoption signals
move fast, so treat these as direction, not scoreboard.

**The sharpest difference is narrow and checkable: approval is bound to a content fingerprint, and
that binding is enforced across the session boundary.** At approval, `/yf-plan` records a hash over
the plan's reviewed sections. If the content later changes, the stored fingerprint goes stale and
execution hard-blocks until a fresh review cycle re-approves it. No surveyed framework binds
approval to reviewed content this way. Elsewhere the plan is a living file the agent can edit
between sign-off and execution; in yf-plan, the plan that runs is the plan you approved, or the
review cycle re-runs.

The rest of the differences are combinations the field has in parts but not together:

| Capability | Spec Kit | Kiro | BMAD | Taskmaster | Cline/Roo | Aider | Ralph | GSD | claude-protocol | yf-plan |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Plan/act separation | Phases | Phases | Phases | Loop | Modes | Modes | Loop | Phases | Phases | Phases (2-way) |
| Spec/PRD as durable artifact | Yes | Yes | Yes | Yes (PRD) | No | No | — | Yes | — | Yes (SPEC-first, REQ-ID'd) |
| Task graph / DAG | tasks.md | Waves | Stories | tasks.json | — | No | tasks.json | Plans/waves | Beads | Beads DAG + typed gates |
| Resumable across sessions | Workflow resume | Spec sync | Files | Files | No | No | Files+git | Files | Files | Yes, fingerprint-gated |
| Adversarial / consistency review | analyze/converge | Property tests + reasoning | QA agent | — | — | — | Test gate | Verifier phase | Reviewer agent | Red-team verdict gates phase |
| Worktree-per-task isolation | — | — | — | Tags (approx) | — | — | — | — | Yes (1/task) | Yes (WT + pinned base) |
| Merged-state re-validation | — | — | — | — | — | — | — | — | — | Yes (merge-first) |
| Upstream issue reconcile | tasks to issues (1-way) | — | — | — | — | — | — | — | — | 2-way triage to resolve |
| Portable / cross-harness state | Agent-agnostic | No (IDE) | Web bundles | Editor-agnostic | No | No | — | Files | No (CC hooks) | OKF bundle + audit |
| Approval bound to reviewed content | — | — | — | — | — | — | — | — | — | Yes (fingerprint hard-gate) |

The table is a directional read of each project's primary documentation as of 2026-07, and its
cells compress nuance. Spec Kit's `analyze`/`converge` gates and Kiro's reasoning checks are real
consistency checks, for instance, but neither binds approval to a content hash. yf-plan's own cells
are verified against its `SKILL.md`.

## A shared kernel that gates every skill

One CLI — [`yf`](/architecture/) — installs the skills, embeds them in a single binary, and runs
a shared **preflight** gate before any beads-backed skill does work. Preflight answers "is this
skill ready to run here?" uniformly, instead of each skill reinventing environment checks. See
the [skill lifecycle](/lifecycle/) for how install → preflight → invoke → execute fits together.

## SPEC-first, so behavior and docs don't drift

Behavior changes land as a specification requirement *first*, then code and a tagged test against
it. Generated surfaces are derived from a single source of truth — the [skills catalog](/skills/)
on this site is generated from each skill's own `SKILL.md`, so counts and descriptions can never
drift from what ships. The same discipline runs internally via drift checks that verify docs,
spec, and implementation still agree.

## Work rejoins the team

Solo output that never reaches the team is lost work. `/yf-plan` can scan your issue tracker,
triage related issues into the plan, and — after execution — reconcile them: closing or updating
the upstream issues with references to what was actually done. Work flows out to collaborators
and back again without manual bookkeeping.

## Where to go next

- **[Architecture](/architecture/)** — the `yf` kernel, embedded skills, beads, and upstream
  tracking, and how they fit together.
- **[Skill lifecycle](/lifecycle/)** — install → preflight → invoke → coordinate/execute.
- **[Skills](/skills/)** — every skill, with the full exposition on why it exists and how it
  works, drawn from its own docs.
- **[yf-plan](/skills/yf-plan/)** — the flagship that embodies most of these ideas.
