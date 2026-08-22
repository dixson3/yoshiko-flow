---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #188: Test suites assert output STRUCTURE and never payload FIDELITY — the blind spot #186/#187 lived in

- **Number:** 188
- **Title:** Test suites assert output STRUCTURE and never payload FIDELITY — the blind spot #186/#187 lived in
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## The defect class

Our test suites assert the **shape** of a tool's output and never the **fidelity of its content**. A tool can therefore corrupt every value it carries while every assertion stays green.

## The measurement that names it

`_shared/test_plan_extract.py` — the suite for the extractor that #186 and #187 were filed against:

```
$ grep -c 'check(' _shared/test_plan_extract.py
62
$ grep -n 'title' _shared/test_plan_extract.py
# only id-recovery cases; ZERO assertions that an extracted title equals its source text
```

**62 assertions, none of them about payload fidelity.** Every one is structural — edges, ids, ordering, classification, recovery logging, unparsed reporting.

The suite's **first** assertion is:

> `an inline-code depends-on: is NOT read as an edge`

So it covers `mask_inline_code`'s *parsing* purpose thoroughly — and never notices that the same masking **blanks the title it carries**. That is #186 exactly, sitting inside the one blind spot of a 62-assertion suite.

#187 is the same blind spot from the other side: nothing asserts the extractor emits what `SKILL.md` §5.2a needs from it, so a missing `detail` field is invisible.

## It is not one suite

The same shape, three places:

| Instance | Structure asserted | Payload never asserted |
| :-- | :-- | :-- |
| #186 / #187 | edges, ids, `unparsed: []` | does the title equal its source? is `detail` present? |
| #181 (`doc_lint`) | `files_checked` counts *how many* files were checked | was the *right* file checked? |
| plan-047's six findings | a control ran and exited 0 | did it *look at* anything? |

This repo already has a name for the general form — *"a control that reports clean while checking nothing"* — and research 004 ranks it as class **M1**, "succeeds visibly while doing nothing". What is new here is that it applies to our **test suites** and not only to our runtime controls.

## Why it is worth a rule rather than a one-off fix

Fixing #186 and #187 closes two instances. The blind spot stays, in every other extractor and filter we ship, because nothing in our test conventions asks for the missing assertion.

## Proposed countermeasure — round-trip / identity assertions

Cheap, mechanical, and directly aimed at the gap:

- **For every extractor**: assert that a field carried through **equals its source**. One assertion per carried field, driven by a fixture whose source text is known.
- **For every filter or selector**: assert the selected set is **non-empty on a known-positive input** — the `files_checked >= 1` arm that `doc_lint`'s suite does have and that saved SC42, and the arm #181's silent green lacks.
- **For every producer consumed by another documented step**: assert the produced object carries the fields that step needs. #187 is precisely a producer/consumer contract nobody asserted.

Suggested home: a convention in `TESTING.md`, plus a review-time check that a new extractor ships at least one identity assertion.

## Provenance

Diagnosed while resolving #186/#187 into `plan-050-james-dixson-d0414b`; recorded in that plan's `plan-retrospective.md` as **RE-003**, escape class `structure-tested-payload-untested`.

Notably, **plan-050's own pass-8 red team saw #186's symptom and dismissed it** — "plan_extract blanks backtick spans inside issue titles; plan-049 shows identical behaviour, so it is pre-existing engine behaviour, not this plan's." Correct that it was pre-existing; wrong that it was benign. An independent reviewer looked straight at a critical defect and classified it as background noise, which is worth carrying into the fix for this class.
