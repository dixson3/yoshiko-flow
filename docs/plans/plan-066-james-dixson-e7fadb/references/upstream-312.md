---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #312 - Process-audit stage: amend the poured DAG so the
  retrospective write, the landing protocol and preflight are BEADS, not paragraphs'
---
# Upstream #312: Process-audit stage: amend the poured DAG so the retrospective write, the landing protocol and preflight are BEADS, not paragraphs

- **Number:** 312
- **Title:** Process-audit stage: amend the poured DAG so the retrospective write, the landing protocol and preflight are BEADS, not paragraphs
- **URL:** 
- **State:** OPEN
- **Labels:** type::feature, priority::high

## Body

## Summary

Proposal: a **process-audit** stage that runs in conjunction with the bead pour, reviews the
poured DAG, and **amends it** so recurring process obligations — the retrospective write, the
landing protocol, preflight — become **beads that must be closed** rather than paragraphs an
agent may skip. The process beads are ephemeral wisps; the recurring sequences are
**parameterized formulas** poured at known boundaries.

Companion to #311 (execution modes). Successor in spirit to the closed #301 (landing protocol),
which delivered the landing *sequence* but as skill prose plus a script, not as a DAG the
coordinator must walk.

---

## Why this is worth doing now: the retrospective just became load-bearing

In #311's `multi-session` mode, each epic runs in its own child session that is **closed and
deleted** when the epic ends. `plan-retrospective.md` is then the **only artifact that survives
that deletion** — the sole inter-session channel for learnings. That promotes it from "useful
record" to "the mechanism", and a missed write stops being a documentation gap and becomes
**silent data loss**.

A write that must happen at every epic boundary, whose omission is invisible, is exactly the
thing that should be a bead.

---

## This has a measured antecedent, and it should be read before designing

**#197** already proposed the core move — *"attach a `verify` child to every plan-execute step
whose declared output matches a glob, so the verification obligation is a bead in the DAG rather
than a rule an agent is trusted to have honored"* — and named the fallback if bd `aspects` do not
exist: *"the same effect is reachable at injection time in SKILL.md §4.3 — at higher cost and
with the obligation still expressed in a script rather than the formula."*

**The process-audit stage proposed here IS that injection-time path, made explicit, mechanical,
and inspectable.** That is not a reason to discount it — #197's own evidence (plan-050 RE-006: a
retrospective append reported exit 0, was never re-read, and a commit message asserted an entry
that had not landed) is the same failure this addresses. But it means the design starts from a
known position, and the first question is whether `bd` aspects exist at all (#197 flags its own
premise as UNVERIFIED against bd 1.1.2).

**#198** supplies the hard constraint any DAG-amendment design must respect (measured, bd 1.1.2):

- **No `loop` / `repeat` / `while` / `iterate` primitive anywhere in `bd`.**
- `until`, `validates`, `tracks` do **not** gate readiness — **only `blocks` does**.
- Gate types are `human | timer | gh:run | gh:pr`; **no gate type re-runs a shell command**.
  yf-plan's capability gates carry `test:` in metadata that the *coordinator* executes — a
  yf-plan convention layered over bd, not a bd feature.
- `bd dep add` runs cycle checks, so **a cycle is unrepresentable by construction**.
- Both shipped formulas are **skeletons** that inject their steps at runtime. **The formula holds
  exactly one iteration; the coordinator owns the loop.**

That last point is the crux: loops are already **unrolled by re-pouring per cycle**. A
"loop-with-escape overlay" is therefore a *coordinator* feature, not a formula feature — unless
the formula substrate itself changes (see the companion issue on beads-agnostic formula
lifecycle).

---

## Proposed shape

### 1. The process-audit stage

Runs at pour time, after the plan molecule is poured (or against a dry-run of it). Two candidate
mechanics, both worth prototyping:

| Mechanic | How it works | Cost |
| :-- | :-- | :-- |
| **Second-stage pour** | Pour the plan molecule, then pour process wisps against the observed boundaries and `bd dep add` them into place | Amends a real DAG; a failed audit leaves a half-amended molecule |
| **Dry-run pour + inspect** | Render the DAG without committing it, inspect mechanically, then pour once with process beads already included | Atomic; needs a dry-run pour that faithfully reproduces the real one — and **#213 records that `bd distill` is non-idempotent against bd's own pour**, so this cannot be assumed |

The audit's output must be **inspectable and diffable** — "the audit ran" is not a result; "here
are the N edges it added and why" is.

### 2. Process beads are ephemeral wisps

Consistent with existing practice (`plan-investigate` is a wisp, burned after use). Two
constraints inherited from #198, both load-bearing:

- **A wisp is burnable, so nothing durable may live inside one.** #198's constraint on the
  review-cycle counter generalises: any *ledger* stays in files; the wisp only orchestrates. A
  retrospective-write bead may **require** the write, but the retrospective file remains the
  record.
- **`bd mol burn` exits 0 on "Canceled"** (#202) — a scripted burn needs `--force` and must check
  output, not the exit code.

### 3. Recurring sequences become parameterized formulas

The landing protocol is the strongest candidate: #301 delivered 20 ordered L-steps with declared
preconditions and a journal. That is a **sequence that must happen identically every time** —
precisely what a parameterized formula is for. Poured as e.g. `Epic N — Plan Epilogue`.

By symmetry, #311's execution preflight is the **prologue** candidate (`Epic 0 — Plan Prologue`):
branch check → worktree check → create-if-absent → re-check → pour. The operator is explicitly
open to a formula-driven preflight **if warranted** — that "if" is the deliverable, not a
foregone conclusion. Preflight is also load-bearing now for the same reason the retrospective is.

### 4. What the audit inserts, minimally

- a **retrospective-write** bead at each epic boundary and each gate boundary;
- the **epilogue** molecule at plan end;
- the **prologue** molecule at plan start (if §3 concludes it is warranted).

---

## Open questions

1. **Do bd `aspects` exist?** #197's premise is explicitly unverified against bd 1.1.2. First
   step: `bd formula show` / `bd cook --dry-run` against an aspect-bearing formula. If they do
   not exist, the injection-time path is the only path — which is fine, but say so.
2. **Is a dry-run pour faithful?** #213 says `distill` cannot reconstruct gate steps and is
   non-idempotent against bd's own pour. If dry-run ≠ real pour, mechanical inspection of the
   dry-run proves nothing about what gets poured. This may decide mechanic (1) vs (2) outright.
3. **How does a process bead avoid being the vacuous check?** A `retrospective-write` bead that
   closes on `test -f plan-retrospective.md` passes on an empty file, or on a copy of the previous
   plan's. Per #263, that is the failure mode where **the check's failure looks like a clean
   result**. The bead's close condition must be provably able to fail against a realistic bad
   input — an empty append, a duplicate entry, a stale file.
4. **Does the executor get to close its own process bead?** #293 records that a `Type: human`
   consent gate can be closed by the executor asserting its own authorization, and #304 records
   the residue #301 did not close. A process bead the executor both causes and closes inherits
   that whole class.
5. **Does this reduce or increase total prose obligation?** The honest limit from #198 applies
   unchanged: *"a bead cannot stop a session from claiming it dispatched something."* What it
   buys is that **"what is next" comes from `bd ready` rather than from an actor's memory of what
   it intended.** That is the claim to test, and it is narrower than "this makes the process
   reliable".

---

## Related

- #301 (closed) — the landing protocol this would parameterize
- #311 — execution modes; the reason the retrospective and preflight became load-bearing
- #197 — the antecedent proposal (verification obligation as a bead), UNVERIFIED premise
- #198 — why the loop cannot live in the formula; the counter-stays-in-files constraint
- #270 — `plan-review.formula.toml` has never been poured in 27 review passes: evidence that a
  formula's *existence* is not its *execution*, which this stage would have to detect
- #145 — yf-retrospective; the retrospective's own quality contract, impacted by this
- #263 — the vacuous-check class every process bead's close condition must survive
- #273 — the command-vs-obligation law: prose naming a COMMAND is followed more reliably than
  prose naming an OBLIGATION. A bead is the strongest form of "a command", which is the
  underlying reason to expect this to work

