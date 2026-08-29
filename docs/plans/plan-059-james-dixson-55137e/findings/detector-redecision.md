---
type: Finding
okf_spec: OKF-PLAN
description: What a future plan would need in order to decide the severity-decay detector question — the re-scope guard stated as a predicate, and the blind labelling procedure over nine held-out bundles. Specification only; this plan ships no detector and writes no code.
---
# Making the severity-decay detector re-decidable

**NOTHING SHIPS FROM THIS DOCUMENT.** Epic 6 produces no artifact, no code, and no detector.
It writes down what a future decision would need, and files the re-measurement. That emptiness
is the deliverable, and SC9 exists to make it checkable rather than tacit.

**Why the detector was declined.** Its shippability condition **failed** (EXP-002 (a)), and the
instrument every published operating characteristic rests on is **broken and biased** (EXP-002
(d)) — the study's own parser was measured to **delete `high` severities** while being biased
toward them. Shipping now would ship a detector whose measured properties are unknown. That is a
**finding**, not a deferral: the specific missing objects are named below, and they do not exist
yet.

**The severity-vocabulary pin shipped anyway** (Epic 1, REQ-DATA-076), and this document is why
the two facts belong in one plan. The pin is the prerequisite research 005 named *for* a
detector; this plan declines the detector and keeps the pin, because the pin is independently
valuable to anyone who later builds a findings-based predicate. Split apart, Epic 1 would arrive
with no stated reason to exist and the next reader would re-derive the detector question from
scratch — which is the specific waste EXP-002 cost an hour of hand-reading to avoid.

## Approach Tested

**measured:** the re-scope guard was derived from four hand-read false positives; EXP-002 (d)
measured nine further bundles that fire under a parser-free reading and are silent under the
study's own instrument. **inferred:** that a blind label over those nine is the only affordable
test that is not a refit.

Two objects are specified below and **neither is built**: the re-scope guard as a predicate, and
the blind labelling procedure that could test it.

## Result

### 1. The re-scope guard, stated as a predicate

The guard exists to exclude a class of false positive: a plan whose severities appear to *decay*
across review passes because the plan **was re-scoped mid-review**, so pass N and pass N+1 are
reviewing materially different documents. A severity that "drops" between two different plans is
not decay; it is two measurements of two things.

**The predicate**, stated precisely enough to implement without re-deriving it:

> For a bundle whose `reviews/pass-*.md` count is ≥ 3, the firing candidate at pass `N` is
> **excluded** when `log.md` carries **no `drafting:` bullet** dated between the date of
> `pass-1.md` and the date of the firing pass `N`.

Two readings that are **not** what it says, recorded because both are the natural misreading:

- It is **not** "exclude when a `drafting:` bullet exists". The bullet is *evidence of re-scope*,
  and its presence is what makes the severity change legitimate to compare. The guard fires the
  candidate **through** when re-scoping happened.
- The window is anchored at **pass 1**, not at pass `N-1`. A re-scope between passes 1 and 2 is
  still a re-scope of the document pass `N` is reviewing.

#### 1a. It is FITTED, and this section is the disclosure

**The guard was derived from the four false positives it excludes.** Evaluating it on those four
is therefore circular, and any 2×2 computed over them is a description of the derivation set, not
a measurement. This is stated as prominently as the predicate itself because a guard whose
provenance is lost reads exactly like a validated one.

Research 005 already names the defect this would otherwise repeat: *"the label and the
discriminator were authored by the same agent with no held-out set."* Section 2 is the remedy;
until it is executed, **no operating characteristic of this guard may be quoted.**

#### 1b. Two bounds that survive even a successful re-validation

Stated here so that a future reader does not mistake a passing evaluation for a shippable
detector. Passing §2 would restore a plausible PPV. It would not touch either of these:

- **The detector is first computable at pass 3.** A plan that thrashes and is abandoned at pass 2
  is outside its reach entirely.
- **Recall has never been measured, for anything.** Nothing bounds the episodes it misses, so
  even a perfect PPV says nothing about coverage.

### 2. The blind labelling procedure

**The label is the expensive part, and it must be established BLIND** — by a party who does not
know whether the guard fires on a bundle, **before** the guard is evaluated on it. Otherwise the
exercise refits and produces a number that looks like a measurement.

#### 2a. The nine held-out bundles

EXP-002 (d) found **nine bundles that fire under a parser-free reading and are silent under the
study's instrument**. **None was ever hand-read, so none is in the derivation set** — this is a
genuine held-out sample:

| # | Bundle |
| :-- | :-- |
| 1 | `d3-pxe/plan-015` |
| 2 | `d3-pxe/plan-016` |
| 3 | `d3-pxe/plan-018` |
| 4 | `d3-pxe/plan-019` |
| 5 | `pybridge/plan-006` |
| 6 | `yoshiko-flow/plan-046` |
| 7 | `yoshiko-flow/plan-051` |
| 8 | `yoshiko-flow/plan-052` |
| 9 | `yoshiko-flow/plan-056` |

#### 2b. The procedure

1. **Freeze the corpus.** Snapshot the nine bundles at a named commit. Every subsequent step
   reads the snapshot, never the live tree.
2. **Label blind.** A party who has **not** run the guard hand-reads each bundle's review passes
   and records, per bundle, whether the severities genuinely decayed and whether the plan was
   re-scoped mid-review — with the quoted cells behind each judgement.
3. **Seal the labels** before the guard is run. The seal is what makes step 4 a test rather than
   a fit.
4. **Run the repaired guard** over the snapshot and compare against the sealed labels.
5. **Report the 2×2 with its denominator named**, and report recall as **unmeasured** unless a
   negative sample was also labelled.

#### 2c. Assert a PROPERTY against a FROZEN corpus — never a literal against a live one

A hazard recorded for whoever runs this. **Do not assert an expected firing count as a literal.**
An earlier draft of plan-059 carried a criterion asserting `fires == 22 and evaluable == 43`, and
both numbers are unsafe:

- **`43` is a live denominator.** The corpus grows — and plan-059 itself becomes a ≥3-pass
  bundle — so the figure was guaranteed to break for a reason unrelated to the repair.
- **`22` came from a parser-free grep**, a *different instrument*, not ground truth. Asserting
  that a repaired parser lands exactly there pre-judges the repair and creates a Goodhart
  incentive to tune to it — in a plan whose R4 is about Goodhart.

## Implications for Plan

### 3. The parser repair is a PREREQUISITE, and it is NOT this plan's to make

`finding_recurrence.py` — the instrument whose parse deletes `high` severities — lives **only in
the research bundle**, on the unmerged branch `research/005-thrash-detection` (PR #267). It is
not in this repository on this branch or on `main`.

**Escalation E-4's resolved outcome is explicit: the repair is scoped in only if the detector
epic survives.** It does not survive. An earlier draft of plan-059 carried the repair as Issue 6.1
anyway — **a silent override of the plan's own resolved escalation, inside the plan whose entire
purpose is to make escalations binding.** It was dropped, and Epic 6 writes no code at all.

So the ownership is: **the research bundle owns the parser repair**, and it is a *prerequisite* of
§2, not a step within it. A re-measurement run against the unrepaired parser would reproduce the
bias it exists to remove.

## Recommendations

### 4. What a future plan would therefore need, in order

1. The parser repair, landed in the research bundle (owner: research 005 / PR #267).
2. The frozen nine-bundle snapshot (§2a).
3. The sealed blind labels (§2b steps 2–3).
4. Only then: an evaluation of the re-scope guard, reported as a property against the frozen
   corpus, with recall stated as unmeasured.

**Whether anyone then builds the detector is a decision for that future plan with that evidence in
hand. This plan takes no position on it.**
