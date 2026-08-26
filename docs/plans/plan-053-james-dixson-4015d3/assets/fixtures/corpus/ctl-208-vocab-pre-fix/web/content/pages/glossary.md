Title: glossary
Slug: glossary
Subtitle: a cold-reader decoder for the yf workflow vocabulary

The yoshiko-flow skills, plans, and docs lean on a compact idiomatic vocabulary — most of it
borrowed from **beads** (`bd`) and the [yf-plan](/lifecycle/) lifecycle. This page defines the
recurring terms so a cold reader can follow a plan, a red-team review, or a land-the-plane
checklist without reverse-engineering the jargon. Each definition describes shipped behavior;
for the mechanics behind a term, follow the links into the [architecture](/architecture/) and
[lifecycle](/lifecycle/) pages.

## Beads and molecules

### formula

A `.formula.toml` template that declares a DAG of work — the epic, its child issues, the
gates, and the dependency edges between them — as a reusable, versioned shape. Formulas ship
inside a skill (`formulas/`) and are the source of truth for *what work exists and how it
connects*. A formula is a template, not live work: nothing is tracked until it is poured.

### molecule

A concrete, poured instance of a formula — the actual tree of beads created in a repo's
beads database. Where a formula is the blueprint, the molecule is the built structure: an epic
bead with its real child issues and gates, each with an id you can claim, update, and close.

### pouring beads / pour

Instantiating a molecule from a formula with `bd mol pour <formula>`: turning the
`.formula.toml` template into a concrete DAG of beads. The pour returns the new epic id and an
id-mapping for every step, which downstream code captures to wire agent metadata and dynamic
fan-out. In yf-plan, the pour is deferred to EXECUTE start — approval and intake happen first,
and only an executing plan has a poured molecule.

### wisp

A lightweight, ephemeral molecule created with `bd mol wisp` — the "vapor" counterpart to a
poured molecule. Wisps are used for transient tracking that should not persist as durable
plan structure, such as an investigation sub-tree during planning. A wisp is discarded when its
purpose ends via `bd mol burn <id> --force`, which cleanly removes it without leaving orphaned
beads behind.

## Gates and control flow

### gate

A first-class bead (`bd create -t gate`) that blocks downstream work until it is resolved with
`bd gate resolve`. Gates come in kinds: a mandatory **start gate** (a human approval that must
be resolved before a plan's execution beads become ready), **capability gates** (a human
confirms some precondition is true, often with a verification command), and the **reconcile
gate** (an automatic gate that opens once all execution beads are closed). A gate is how a plan
encodes "do not proceed past here until X holds."

### coordinator

The agent and dispatch loop that drives a poured molecule's bead DAG to completion. The
coordinator repeatedly finds ready beads (`bd ready`), claims and dispatches the work, closes
each bead as it finishes to unblock its dependents, and continues until the DAG is drained —
then triggers reconcile and hands off. It is designed to be re-invokable: a fresh coordinator
can resume a partially-completed molecule after a crash, sweep stuck beads, and pick up where
the last one left off.

### cascade-close

Closing every container bead — intermediate epics plus the top-level plan molecule — whose
children are all in a terminal state, working bottom-up (yf-plan's `close_cascade.py`). It
replaces a bare `bd close` on the epic so no intermediate container is left open under a
finished plan. The cascade is **fail-loud**: a container with any still-open child is a hard
failure that aborts the close rather than silently masking incomplete work.

### reconcile

The post-execution step that squares a plan's actual outcomes against what it set out to do —
incorporating any upstream issues that were folded in, and reconciling the plan record before
the plan is closed. Its gate (the reconcile gate) opens automatically once every execution bead
is closed, so reconcile runs after the work but before the final cascade-close and
complete-gate.

## Plan lifecycle terms

### intake

The yf-plan phase that freezes an approved plan for execution. Intake does **not** pour the
molecule — it records the approval by writing the content fingerprint and committing the plan,
deferring the pour and the whole bead DAG to EXECUTE start. Its job is to turn a reviewed,
approved plan into an execution-eligible one.

### red-team

The adversarial plan-review pass in yf-plan: an agent that is read-only with respect to the repository
under review (a sandbox spike outside it is authorized) performs a structured, skeptical
critique of a plan once its conformance check passes, and returns a verdict of **APPROVE**,
**REVISE**, or **INVESTIGATE-MORE**. The verdict drives the phase transition — only a final
`APPROVE` (with a passing portability audit) lets a plan reach `ready-for-approval`. A `REVISE`
keeps the plan in the PLAN phase and mandates a fresh red-team cycle after the concerns are
addressed; readiness always keys on the *last recorded* verdict.

### fingerprint

A content hash of the plan's reviewed material, written as a `**Fingerprint:**` header field at
intake, that binds the operator's approval to *exactly that content*. Because approval is
consent to reviewed content, any later edit changes the hash and the stored fingerprint no
longer matches — see stale-approved. The fingerprint, not a poured gate, is the
execution-eligibility token: EXECUTE only starts a plan whose fingerprint still matches.

### parked plan

A plan that is approved but has never been executed — the approval and fingerprint exist, but
no molecule was ever poured. yf-plan surfaces parked plans with a `⏸ PARKED` tag in `list` and
nudges about them at land-the-plane, so approved-but-forgotten work does not silently rot. A
parked plan is still execution-eligible; it is distinct from a stale-approved one.

### stale-approved

An approved plan whose content changed after approval, so its stored `**Fingerprint:**` no
longer matches the current content. A stale-approved plan **cannot** start execution: the
resume scan blocks EXECUTE until a fresh conformance → red-team → portability cycle re-approves
the plan (rewriting the fingerprint), or the operator explicitly overrides with `--force`. This
is the guardrail that stops silently-edited plans from being run as if still reviewed.

## Upstream tracking and session close

### landing the plane / land-the-plane

The session-close / pre-push wind-down performed before a session or plan closes: pushing
open and deferred beads upstream to the issue tracker, hoisting follow-ons, running final
validation, and general cleanup. It is the disciplined "before we walk away" pass that makes
in-flight work durable and visible — nothing important is left only in the ending
conversation. See [yf-beads-upstream](/architecture/) for the push mechanics.

### tombstone

The reversible close pattern (`bd close -r`, close-with-reason — never `bd delete`) used when a
bead's tracking is hoisted upstream to an issue tracker. The local bead is closed with a reason
that records where it went, leaving a recoverable marker rather than destroying history. Because
the close is reversible, a mistakenly-hoisted bead can be reopened; the tombstone is a
forwarding pointer, not a deletion.

### hoist

Moving a bead's tracking from the local beads database up to the issue tracker (GitHub, GitLab,
or Jira) as an upstream issue, then closing the local bead with a tombstone. At land-the-plane,
follow-on beads created during a session can be hoisted so the durable worklist lives upstream;
by default this is propose-with-confirm, and only a narrow, opt-in signal is ever hoisted
unattended.
