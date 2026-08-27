Title: beads & the yf-beads-* skills
Slug: beads-concepts
Subtitle: what beads is, why yf builds on it, and how the five yf-beads-* skills divide the work

Beads (`bd`) is the task-tracking substrate under everything stateful in yoshiko-flow. A
[`/yf-plan`](/lifecycle/) plan, a `/yf-research` project, and any multi-session skill all
record their work as beads rather than scratch TODO lists — so work survives a crash or a new
session. That resumption is local to one clone; carrying work to a different machine goes through
the git-committed plan and a coarse upstream issue, not the bead database itself (see the
**upstream strategy** below). This page explains what beads is, why yf uses it, the beads
features yf leans on, the distinctive **upstream strategy**, and how the five `yf-beads-*`
skills each own a distinct slice of that story. For one-line definitions of the vocabulary,
see the [glossary](/glossary/).

## What beads is

`bd` is a **dependency-aware issue tracker** backed by a Dolt (versioned SQL) database that
lives per-repo under `.beads/`. Its unit of work is an **issue** — a "bead". Each bead has:

- a **type** — `task`, `epic` (a container that parents child issues), or `gate` (a blocker
  that must be resolved before downstream work proceeds);
- a **priority**;
- **dependencies** — directed edges to other beads (`bd dep`), so work has an order;
- a computed **ready** state — a bead is *ready* when every bead that blocks it is closed.
  `bd ready` returns exactly the beads that can be worked right now.

That ready computation is the heart of beads: instead of a flat checklist, you declare a DAG
of work with its constraints, and beads tells you what is actionable. Closing a bead unblocks
its dependents, so the frontier of ready work advances automatically as work completes.

## Why yf uses it

Every yf skill that tracks work uses `bd` — **never** markdown TODOs, `TodoWrite`, or inline
task lists. Beads gives yf three things a checklist cannot:

- **Durable, queryable state.** Work lives in a database, not in a conversation. A crashed or
  ended session resumes from bead state; `bd ready` / `bd show` reconstruct exactly where
  things stand.
- **Dependency ordering.** A plan or research project is a DAG with gates and edges. The ready
  computation drives execution order without a human re-deriving "what's next".
- **Multi-phase orchestration.** A [coordinator](/glossary/) loop drains the DAG to
  completion — find ready beads, dispatch, close, repeat — which is what lets `/yf-plan` and
  `/yf-research` span multiple sessions and recover cleanly.

## Why the yf skills guardrail beads behavior

Raw `bd` is a general-purpose tool. The `yf-beads-*` skills wrap it with guardrails so agent
use is safe, portable, and repeatable rather than ad-hoc:

- **Non-interactive discipline.** yf invokes `bd` with non-interactive flags so an aliased
  confirmation prompt can never hang an unattended run.
- **Local-only, never-push-via-git posture.** The beads DB is treated as a local artifact, not
  a git-shared one (see [upstream strategy](#the-upstream-strategy) below). yf never commits or
  pushes the DB as the mechanism for sharing work.
- **Verify-before-use config health.** Before relying on `bd` in a repo, yf verifies the beads
  config is *functional*, not merely present, and repairs it if wedged — rather than trusting a
  bare `bd status` exit code, which can report an error with a success code.
- **Defensive `--json` parsing and transactional intake** so scripted `bd` use does not silently
  corrupt the graph.

These guardrails are why the direct-CLI knowledge is codified in skills instead of re-learned
every time an agent scripts `bd`.

## The beads features yf uses

### Gates

A **gate** is a first-class bead (`bd create -t gate`) that blocks downstream work until it is
resolved with `bd gate resolve`. yf uses three kinds:

- a mandatory **start gate** — a human approval that must be resolved before a plan's execution
  beads become ready;
- **capability gates** — a human confirms a precondition holds, often paired with a verification
  command;
- the **reconcile gate** — an automatic gate that opens once all execution beads are closed, so
  post-execution reconcile runs after the work but before the final close.

A gate is how a plan encodes "do not proceed past here until X holds."

### Formulas & molecules

A **formula** (`.formula.toml`) is a template that declares a DAG of work — the epic, its child
issues, the gates, and the edges between them — as a reusable, versioned shape. It ships inside a
skill (`formulas/`) and is the source of truth for *what work exists and how it connects*.
Nothing is tracked until it is **poured**.

**Pouring** (`bd mol pour <formula>`) instantiates a concrete **molecule** — the actual tree of
beads in the repo's database, each with a real id you can claim, update, and close. The pour
returns the new epic id and an id-mapping for every step, which downstream code captures to wire
agent metadata and dynamic fan-out. A lightweight, ephemeral molecule is a **wisp** (`bd mol
wisp`), used for transient tracking that should not persist as durable structure; it is discarded
with `bd mol burn <id> --force`, which removes it without leaving orphaned beads behind.

### Epics

An **epic** is a container bead that parents child issues. It groups a sub-DAG under one bead so
the tree has structure beyond flat dependency edges. yf closes containers with **cascade-close**
semantics: every container whose children are all terminal is closed bottom-up, and a container
with any still-open child is a fail-loud error rather than a silently-masked incomplete branch.

### Labels & metadata

Beads carry **labels** for tagging (for example, marking work `deferred-validation`) and **JSON
metadata** for structured attachments — upstream issue links, the agent file a coordinator should
dispatch for a given bead, and similar wiring. yf uses labels to select cohorts of beads and
metadata to bind a bead to the machinery that acts on it.

## The upstream strategy

This is the part of yf's beads usage that most differs from naive `bd` use, so it is worth
stating carefully.

### The DB is local

The beads database is **per-repo and local** — it lives in `.beads/` and is typically a
local-only Dolt database with **no remote**. yf explicitly configures repos local-only and never
adds a Dolt remote or runs `bd dolt push` on them. The DB is not a shared-over-git artifact:
yf **never pushes beads via git** as the way to share work. Two agents on two clones do not see
each other's in-flight beads — and that is by design.

Cross-machine handoff therefore does not move the database. It moves the git-committed **plan
folder** and a coarse **upstream issue**; a capable clone re-pours the plan's beads locally from
those. The upstream issue is a coordination pointer, not the medium that transfers bead state.
There is no live, shared bead state across machines — no shared ready-frontier, claims, or gate
resolutions. The `bd dolt push` mechanism that *could* replicate the DB is deliberately left
unused: yf configures every repo local-only with no Dolt remote.

### Follow-on work goes upstream, coarsely

If the DB is local, how does work that outlives a clone become visible to the team? It is
**captured upstream in the issue tracker** (GitHub, GitLab, or Jira) at
[land-the-plane](/glossary/). Crucially, yf does this at **coarse granularity**: one tracking
issue per plan-scale effort (e.g. per `/yf-plan` plan), linking the plan and its epic — **not**
one issue per execution bead. The granular sub-beads stay local; only the plan-scale summary is
mirrored upstream unless finer tracking is explicitly requested.

This is the opposite of a naive approach that would `bd dolt sync` the whole database — which
would re-import every upstream issue as a duplicate bead and push the entire local graph. yf
pushes only **scoped**, **push-only**, **dry-run-first** selections, and routes every push through
the [yf-beads-upstream](/skills/yf-beads-upstream/) skill rather than hand-run `bd <backend>`
commands. The issue mirror is also **orthogonal** to Dolt replication: mirroring *issues* to a
tracker is a different operation from `bd dolt push` replicating the *database*.

### The tombstone pattern

When a bead's tracking is **hoisted** upstream — moved from the local DB to an issue tracker — the
local bead is closed with a reversible **tombstone** (`bd close -r`, close-with-reason, never `bd
delete`). The reason records where the work went, leaving a recoverable forwarding pointer rather
than destroying history. Because the close is reversible, a mistakenly-hoisted bead can be
reopened. At land-the-plane this hoist is **propose-with-confirm** by default, and only a narrow,
opt-in signal is ever hoisted unattended.

## How the five yf-beads-* skills divide the work

Each `yf-beads-*` skill owns a distinct aspect of using beads well. They form a layered support
stack under the workflow skills.

- **beads** — the canonical **routine loop**: `bd ready` → `bd update --claim` → `bd close`.
  This is the baseline every other beads skill builds on; the everyday find-work / claim / close
  cadence lives here.
- **[yf-beads-extra](/skills/yf-beads-extra/)** — the **direct-CLI gotcha layer**: issue-type and
  gate semantics, dependency-edge mutation (`bd dep`), defensive `--json` parsing, transactional
  bulk intake (`bd batch`), and the exact `bd mol pour` output shape. Reach for it when scripting
  `bd` directly or recovering a malformed graph.
- **[yf-beads-authoring](/skills/yf-beads-authoring/)** — conventions for **building
  beads-backed skills**: formula authoring, the `bd mol pour` lifecycle, dynamic fan-out, agent
  metadata wiring, the coordinator dispatch loop, and crash/resume resilience.
- **[yf-beads-init](/skills/yf-beads-init/)** — **verify / initialize / repair** a functioning
  beads config; the shared dependency-verification home every beads skill's preflight routes
  through, including the wedged-migration repair.
- **[yf-beads-hygiene](/skills/yf-beads-hygiene/)** — **read-only-first audit + gated repair** of
  the dependency graph's *content*: orphaned beads, dangling edges, and correct gate-edge
  classification so a cleanup never un-gates live work.
- **[yf-beads-upstream](/skills/yf-beads-upstream/)** — configurable **upstream tracking**: push
  open and deferred beads to the issue tracker at land-the-plane, and treat upstream issues as the
  authoritative worklist on status/pull.

The split is deliberate: config health (`init`) is separate from graph content (`hygiene`), which
is separate from routine use (`beads`), scripting gotchas (`extra`), skill construction
(`authoring`), and the team-visible mirror (`upstream`). A workflow skill composes them rather
than reimplementing any one.

## Where to go next

- **[architecture](/architecture/)** — where beads sits in the `yf` kernel and skill tree.
- **[lifecycle](/lifecycle/)** — how a plan's beads flow from pour to cascade-close.
- **[glossary](/glossary/)** — one-line definitions for every term above.
