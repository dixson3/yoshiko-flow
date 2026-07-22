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

Native plan mode produces output that disappears with the session. yoshiko-flow writes work as
first-class artifacts: `/yf-plan` writes plans as markdown under `docs/plans/`, and tracks
execution in **beads** — an issue database committed next to the code. Because the state is in
the repo, it's versioned in git, reviewable in a PR, and searchable next year. Nothing important
lives only in a chat transcript.

## Resumable across sessions and machines

Work that spans environments can't assume one machine and one context. `/yf-plan` decomposes a
plan into epics of dependency-wired issues with **gates**: a capability gate can block the tasks
that need a platform you don't have while all other work proceeds. Push the repo, and someone on
the right platform — or you, tomorrow, in a new session — picks up exactly where the gate left
off. If a run crashes mid-execution, the next session detects the in-progress work, resets the
stuck items, and continues; it never silently loses or double-does work.

## Investigate before you commit

A plan to adopt a new database should benchmark candidates, not guess. `/yf-plan` runs
investigation experiments in disposable worktrees *during* planning, feeding findings back into
the design before anything is committed to. The same instinct — gather evidence, then decide —
drives [`/yf-research`](/skills/yf-research/), which turns a question into a cited, resumable
report rather than a one-shot answer.

## Portable by design — replacing the ephemeral native mechanisms

yoshiko-flow deliberately **replaces** the harness built-ins that trap state in a single vendor:

- **Planning** — `/yf-plan` overrides native plan mode with a scoped, reviewable, resumable
  pipeline whose plans are durable files.
- **Task tracking** — `bd` (beads) replaces the native TODO list. Beads are portable, ordered by
  a real dependency graph, and pushable upstream.
- **Memory** — durable decisions go to `AGENTS/` rules or beads, not a Claude-only memory store,
  so another clone, machine, or agent harness can see them.

The skills install into whichever harness you use (Claude Code by default, or the `.agents`
surface), so the same portable workflow follows you across tools.

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
