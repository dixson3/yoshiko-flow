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

### abandoned plan

A plan deliberately stopped. `abandoned` is a terminal status, reachable from any
non-`complete` status and leaving by exactly one edge — back to `drafting`. There is
deliberately **no** `abandoned → complete` edge: a plan that was stopped did not finish.
yf-plan tags it `⏹ ABANDONED` in `list`. It is **not** execute-eligible and **not** parked —
the parked nudge's text is literally "run /yf-plan execute", which is exactly wrong here. It
exists because there was previously no legal state for "approved but deliberately not
executing", so an operator invented one and `update-status` accepted it silently (#208).

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

Moving a bead's tracking from the local beads database up to the GitHub issue tracker as an
upstream issue, then closing the local bead with a tombstone. At land-the-plane,
follow-on beads created during a session can be hoisted so the durable worklist lives upstream;
by default this is propose-with-confirm, and only a narrow, opt-in signal is ever hoisted
unattended.

## Execution, artifacts, and failure vocabulary

The terms below appear constantly across the shipped skills and had no definition here. Each
entry's count is how many files under `skills/` use it.

### preflight

*(50 files)* The shared readiness gate a beads-backed skill runs **before** it does any work,
rather than each skill reimplementing the same probes. `yf preflight <skill>` checks system
dependencies and the minimum `bd` version, verifies the skill's companion rule against the
embedded manifest, and ensures the gitignore scaffold — returning a single authoritative
`status` the skill branches on. It is **read-only** with respect to your beads configuration: it
reports a problem and routes you to `/yf-beads-init`, and never repairs on its own. Parse the
`status` field, not the exit code.

### OKF bundle

*(48 files)* An artifact **folder** — not a single file — laid out so a cold reader in a
different repository can understand it from the folder alone. Every `yf-plan` plan, `yf-research`
project and `yf-incubator` topic is one. A bundle carries reserved files at its root (`index.md`
listing its contents, `log.md` a newest-first history) alongside the artifact of record and its
supporting material. **Portability is the point**: the drafting conversation is gone, so
everything load-bearing has to be *in the folder*.

### worktree / execute branch

*(29 files)* A separate git working directory (`.worktrees/<plan-id>`) on its own branch
(`<plan-id>-execute`), cut from a **pinned** base rather than from whatever happened to be
checked out. Plan execution edits project code there while the plan folder and all bead tracking
stay in the primary checkout — so only code changes accumulate on the plan branch, and the
primary stays usable. At the end the branch is merged back and the merged tree is re-validated.

### fail-closed

*(28 files)* On uncertainty, **refuse** rather than proceed. A fail-closed check that cannot
determine whether a condition holds reports that it could not tell and stops, instead of
assuming the favourable answer. The opposite — fail-open — is how a broken instrument turns into
a green result: the check could not run, nothing said so, and the caller read success.

### silent no-op

*(25 files)* A trigger that, when its precondition is absent, does **nothing and says nothing**
— no prompt, no nag, no offer to bootstrap. Most yf triggers are opt-in per repository, and the
opt-out is silence: with no approved manifest or marker file, the trigger simply never fires.
This is a deliberate contract, not an oversight; a trigger that announced its own absence on
every edit would be worse than the check it is offering.

### discovered-from

*(23 files)* A beads dependency type recording that one issue was **found while working on**
another. It captures provenance — where a piece of work came from — rather than ordering, and
unlike `blocks` it does not gate readiness. It is what distinguishes genuine follow-on work
discovered mid-execution from disposable scratch.

### epistemic rules

*(11 files)* The evidence standard every `yf-research` agent works under: **absence is a valid
finding**, direct quotes are preferred over paraphrase, and no assertion goes uncited. They exist
because the failure mode of research is not usually a wrong answer — it is a confident answer
with nothing behind it.

### session boundary

*(11 files)* The point where one agent session ends and a new one begins. It is load-bearing
because some gates can **only** be resolved on the far side of it: a `yf-plan` start gate is
released in a fresh `/yf-plan execute` session, not in the session that wrote the plan. What
carries across the boundary is what was written to disk — which is why plan folders are portable
by contract.

### stuck-bead sweep

*(10 files)* The resume-time pass that finds beads a crashed session left claimed or
`in_progress` and **resets** them to open so they can be worked again. It runs strictly before
the ready loop, so reconciliation cannot fire on a resumed-but-incomplete plan. It never
auto-closes anything: no reliable signal separates disposable scratch from real
`discovered-from` work, so anything it cannot positively classify is reported for a human.

### descope

*(5 files)* To deliberately remove work from a plan's scope — recording the decision and its
reason — rather than silently dropping it or quietly leaving it unfinished. A descoped item is
still a decision with an owner: it is either filed upstream or explicitly declared a non-goal.

### escalation

A question raised **to** the controlling operator when something exceeds the running session's
authority — a finding that refutes a scoping decision, a needed outward-facing write, or an issue
that turns out to be unexecutable as written. Recorded as a `## ESC-NNN` entry in the plan
bundle's `escalations.md`, each carrying its alternatives, a recommended default, and **what
happens if no answer arrives**.

The contract is **write-then-notify, never ask-and-await**: the artifact *is* the escalation, and
the session keeps working on everything the answer does not block. So an unanswered question has
a defined outcome rather than a stalled run. It is a `yf-plan` mechanism — there is no separate
judgement skill.

### autonomy level

How often an execution run stops to consult. **Autonomous** is the default: the coordinator moves
to the next ready bead without asking, and an epic boundary is a **report, not a stop**.
**Checkpointed** consults at those points instead. `/yf-plan execute --autonomous` and
`--checkpoint` override the configured level for one run.

Autonomy never widens **authority**. Under either level the run halts on the same declared stop
classes, and a `human` gate is never auto-resolved however green its test — a green test
establishes that a *condition holds*, never that a *person authorized* something.

### negative control

A deliberate check that an instrument can **fail**. You construct a state in which a checker
*should* report a problem and confirm that it does; a checker never observed to fail is not
evidence, because a checker that has silently stopped looking is indistinguishable from one that
has found nothing.

The strong form is a **code-side** control: mutate the **source of truth** underneath docs that
currently pass, and require the checker to go red. A doc-side control — breaking a doc and
watching the checker complain — cannot catch a checker that was already silent while the docs
were already wrong.

### vacuity floor

A minimum-input assertion that turns *"I inspected nothing"* into a loud failure. A check over an
empty set passes trivially, so without a floor **"clean" and "never read" are the same
observation**. Flags like `--min-skills` or `--min-checkers` name the floor; falling below it is
reported as **inconclusive**, never as a pass.

### aspect

A formula that **weaves into another formula's steps at cook time** rather than being poured as a
molecule of its own. It declares no steps to run on its own and is attached by the consumer,
through the consumer's own `[compose] aspects`. No shipped formula is an aspect today: the former
`verify-artifact` example was removed with the unpoured `plan-review` formula (plan-071), so the
shipped-formula count contains workflows only.

### closable

The propose-only report of which upstream issues have all their mapped beads closed. It emits
`gh issue close` commands for confirmation and **never closes anything**, because closing an
upstream issue is an outward-facing write.

Its signal is **per-bead**, resolved through the `external_ref` recorded at push time — so a
hand-filed coarse tracker, which carries no bead mapping, is invisible to it. A clean run
therefore does not mean nothing needs closing.
