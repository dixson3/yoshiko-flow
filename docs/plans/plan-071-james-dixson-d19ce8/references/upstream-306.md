---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #306 - The phantom resolution cell: a review Resolutions
  entry can DESCRIBE an edit that was never made, and guarding the write does not
  guard the claim about the write'
---
# Upstream #306: The phantom resolution cell: a review Resolutions entry can DESCRIBE an edit that was never made, and guarding the write does not guard the claim about the write

- **Number:** 306
- **Title:** The phantom resolution cell: a review Resolutions entry can DESCRIBE an edit that was never made, and guarding the write does not guard the claim about the write
- **URL:** 
- **State:** OPEN
- **Labels:** type::bug, priority::high

## Body

Found three times during **plan-060**'s review cycle, twice *consecutively after a guard was added for
it*. It is [#263](https://github.com/dixson3/yoshiko-flow/issues/263)'s class in the **process layer**
rather than the tooling layer, and it is the only defect plan-060 found that it did not also fix.

## The defect

`reviews/pass-N.md`'s Resolutions table is written by **the party that made the changes**, and it is
the artifact the *next* red-team pass reads to decide what has already been addressed. Nothing checks
that a resolution cell describes an edit that exists.

Measured, three instances in one plan:

| # | Cell claimed | Reality |
| :-- | :-- | :-- |
| pass-5 C4 | *"A forward-pointer is added at the superseded paragraph"* | no forward-pointer anywhere in that section |
| pass-6 C5 | *"The 37s are marked \"AT THE TIME. Now 0\""* | `grep -c "AT THE TIME" plan.md` -> **0** |
| pass-6 C3 | *"`asked_of` now says so rather than being blank"* | true for ESC-001, **blank for ESC-002** |

In each case the *substance* had partly landed in different words, so these were **recording**
defects rather than missing fixes. That is what makes them dangerous: the plan was fine and the
record of why it was fine was false.

## Why the obvious guard does not work — this is the load-bearing part

After the first instance, every subsequent edit was made with an **assert-guarded** string replace
(`assert old in t` before `t.replace(old, new)`), and the resolution cell said so. The very next pass
found another phantom cell **immediately below that assertion**.

> **An assert on the edit string cannot catch a resolution cell that DESCRIBES A DIFFERENT EDIT than
> the one made. Guarding the write does not guard the CLAIM ABOUT the write.**

The assert proves *an* edit landed. It says nothing about whether the sentence written in the
Resolutions table is a true description of that edit. When a fix lands in different words than
planned — which is normal and often better — the guard passes and the cell goes stale in the same
motion.

## Why it matters more than a bookkeeping nit

- **The next reviewer trusts it.** `red-team.md` dispatches read prior passes to avoid re-raising
  settled concerns. A false "resolved" is an invitation to skip exactly the thing that was not done.
- **`REQ-PORT-006`'s count-equality does not touch it.** It asserts `count(reviews/pass-*.md) ==
  count(log.md review-pass: bullets)` — file *presence*, never cell *content*. All three instances
  above occurred with count-equality green.
- **`doc_lint` does not touch it.** The `review` document type checks sections and verdict grammar,
  not whether a Resolutions cell corresponds to reality. All three passed `doc_lint` 0/0.
- **It is self-concealing.** The artifact that would tell you a fix was missed is the artifact
  asserting it was made.

## Directions worth investigating

1. **Require a resolution cell to cite a checkable anchor** — a grep-able string, a file:line, or a
   test name — rather than prose. Then a mechanical check can verify the anchor exists. This is the
   `Verification:`-line doctrine (`spec/cli.md:35`, *"Verification: **executed**, not asserted"*)
   applied to the review record, which is currently the one prose surface in the plan bundle with no
   executable binding at all.
2. **Have the next pass verify the previous pass's resolutions as a required step.** plan-060's
   passes 4–7 did this *by instruction in the dispatch prompt* and it caught all three instances —
   but it was ad hoc each time, not part of `red-team.md`. Making it a standing element of the agent
   contract costs one paragraph.
3. **Consider whether the resolver should write the cell at all.** The concern-raiser could record
   the verification, inverting the party. That is a larger change and may not be worth it, but it is
   the structural version of the fix and mirrors the reasoning in
   [#301](https://github.com/dixson3/yoshiko-flow/issues/301) about separating who decides from who
   records.

## Relationship to existing issues

- [#250](https://github.com/dixson3/yoshiko-flow/issues/250) is the closest relative — *"a resolution
  can be RECORDED as done and never written to plan.md"* — and is about the **plan** not receiving
  the fix. This issue is about the **review record** misdescribing a fix that partly did land, which
  survives #250's remedy: the plan is correct and the record is not.
- [#263](https://github.com/dixson3/yoshiko-flow/issues/263) names the class. Two facts — *a fix
  landed* and *the description of the fix is accurate* — share one signal, and the permissive
  consumer (the next reviewer) reads "resolved".

## Provenance

plan-060 (`docs/plans/plan-060-james-dixson-6a6ac9`), review passes 5, 6 and 7. Each instance was
caught by a red-team pass explicitly instructed to verify the prior pass's resolutions, never by any
mechanical check. Filed at operator direction so it does not close with the plan.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

