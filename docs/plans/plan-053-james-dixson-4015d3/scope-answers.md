---
type: Reference
okf_spec: OKF-PLAN
id: scope-answers
description: The scoping questions put to the operator and the answers given, preserved so the framing can be audited
---

# Scope answers

**Written in response to pass-1 C13**, which correctly observed that D-1..D-3 and D-5..D-7 were
operator answers to questions whose text existed only in the drafting conversation — so a
reviewer could corroborate the *substance* from findings but could not audit the *framing*.

Each block records the question, the options **as offered**, and the answer. Where an option
set was arguably steering, that is noted rather than hidden.

## Round 1 — before investigation

**Q1. #208 offers three remedies for out-of-vocabulary plan statuses. Which scope?**

1. *Warn + fail closed (Recommended)* — writer warns; `STATUS_SEVERITY` maps unrecognised to
   the strictest profile. No vocabulary change.
2. *Warn + fail closed + add a real status* — all of the above plus a genuine status in SPEC,
   the Phase Model line, `STATUS_SEVERITY`, `_is_parked` and the §5.1 filter.
3. *Fail closed only* — smallest; the stranding failure stays silent.

**Answer: 2.** → **D-1**

> **Framing note.** Option 2's description asserted that the vocabulary is *"a declared
> DRIFT-CHECK authority edge, so every consumer must move together."* **EXP-004 later measured
> that claim FALSE** — `e-status-values` is vacuous. The option set therefore overstated
> option 2's cost. The answer chose the *most* expensive option anyway, so the misstatement
> cannot have steered toward it; and EXP-004 additionally found a scope *reduction* (the §5.1
> filter is prose-only). Recorded because a reviewer should not have to take that on trust.

**Q2. #209: how should a poured issue bead point back to its bundle?**

1. *Both: metadata + header (Recommended)* · 2. *Provenance header only* (what the issue author
recommends) · 3. *Metadata stamp only*.

**Answer: 1.** → **D-2**

**Q3. #210 is the SECOND instance of a `_shared/` path naming an uninstalled file. Fix the
instance or the class?**

1. *Class: shipped-path check (Recommended)* · 2. *Instance only* · 3. *Class, across all
skills, including a sweep* (described as widest, scope unknown until measured).

**Answer: 1.** → **D-3**

## Round 2 — after the six experiments returned

**Q4. EXP-003's check catches 8 real breaks in `yf-diagram-authoring`. The check goes RED until
they are fixed or suppressed. In scope?**

1. *Fix all 8 in this plan (Recommended)* · 2. *Suppress now, follow-on bead* · 3. *Narrow the
check to `_shared/` only*.

**Answer: 1.** → **D-5**

**Q5. EXP-004 found `e-status-values` is vacuous. Fix it here?**

1. *Fix in this plan (Recommended)* · 2. *File it, fix separately* · 3. *Fix, and audit ALL
DRIFT-CHECK edges* (described as widest, unknown scope).

**Answer: 1.** → **D-6**

**Q6. EXP-002 found `pour_fidelity.py --strict` exits 0 on an empty scope. Fix before
shipping?**

1. *Fix before shipping (Recommended)* · 2. *Ship as-is, file the hole*.

**Answer: 1.** → **D-7**

## Standing framing caveat

In all six questions the option the drafter recommended was placed **first** and carried the
`(Recommended)` marker, and in all six it was the option chosen. A reviewer should treat these
as **drafter proposals the operator ratified**, not as independent operator judgements — with
the partial exception of Q1, where the operator chose an option the drafter had *not*
recommended.
