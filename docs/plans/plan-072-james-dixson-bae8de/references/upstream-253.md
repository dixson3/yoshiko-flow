---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #253 - Verification predicates keyed on a TERM catch
  cross-references, not edits: two false signals in one plan, one of them a criterion
  that could not see the surface it was written for'
---
# Upstream #253: Verification predicates keyed on a TERM catch cross-references, not edits: two false signals in one plan, one of them a criterion that could not see the surface it was written for

- **Number:** 253
- **Title:** Verification predicates keyed on a TERM catch cross-references, not edits: two false signals in one plan, one of them a criterion that could not see the surface it was written for
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::medium

## Body

## Observed — twice, in opposite directions

`d3-pxe` plan-019 amended a large normative `SPEC.md`. Two verification predicates keyed on a term misfired — one **false positive**, one **false negative**.

### False positive: a section that looked amended and was not

A check asserted a SPEC section received no amendment, implemented as a whole-file diff grepped for that section's requirement IDs. It reported **5 changed lines**, apparently a violation of a deliberate non-edit.

All five were **cross-references** — citations to those requirement IDs *from other sections*. The section's own body was byte-identical (293 lines both sides), which a section-scoped `awk` extract confirmed in one command.

Cost: two extra verification rounds and a near-miss on reporting a violation that did not exist.

### False negative: a criterion blind to its own target

A success criterion verified SPEC no longer referenced a retired DNS name, via `grep -n "agents\.dixson3\.net" SPEC.md`.

The surface it was written for spells the name **`agents`** — in a list rendered as `` `agents`, `dashboard` — all `.dixson3.net` ``. The pattern could not match it. The criterion would have passed on a document still containing the thing it asserted was gone.

Caught by pass-3 (P3-L2) only because a reviewer read the file rather than trusting the predicate.

## The shared cause

A term appears in a document for **several different reasons** — as a definition, as a citation, as prose, inside a code span, split across a rendered list. A predicate keyed on the term cannot distinguish them, so it is wrong in both directions:

- it counts citations as edits (false positive);
- it misses renderings that do not match the literal (false negative).

## Proposed fix

For SPEC-shaped documents with stable section headers:

- **assert against a section-scoped extract, not a whole-file grep.** `awk '/^### 7\.11/{f=1} f{print} /^### 7\.12/{exit}'` then `diff -w` is one line and answers the actual question ("did this section's body change?").
- when a criterion asserts a **name** is gone, assert the **containing line's text** directly rather than the name pattern, or enumerate the permitted remaining occurrences by line number.
- prefer `diff -w` when the document is table-aligned — table realignment produces whole-row `-`/`+` pairs that look like content changes. In this plan an amendment log showed 20 deleted rows that were **pure realignment plus one appended row** (20 → 21, zero deletions under `-w`).

## Where it belongs

`yf-plan`'s conformance/red-team guidance on writing Success Criteria verifications, and anywhere the skill suggests grep-based assertions.

## Evidence

`d3-pxe` — `docs/plans/plan-019-james-dixson-cdd9ff/reviews/pass-3.md` (P3-L2), and the SC1 verification as finally written.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
