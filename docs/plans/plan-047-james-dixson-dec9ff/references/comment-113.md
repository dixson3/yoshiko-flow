---
type: Reference
okf_spec: OKF-PLAN
id: comment-113-draft
disposition: partial
target: https://github.com/dixson3/yoshiko-flow/issues/113
status: DRAFTED — NOT POSTED (operator gated)
---

# Draft comment for #113 — execution-rehearsal review pass (topological DAG walk)

**Disposition: partial. #113 stays OPEN.**

plan-047 (Epics 0–5) delivers the substrate this pass requires: `_shared/plan_extract.py` reads
a `plan.md` into JSON — epics, issues, dependency edges with line numbers, gates (with the
`Test:` verbatim plus an `executable | fenced | sentinel` classification), criteria, risks and
upstream rows. It **fails loudly rather than degrading**: every construct it cannot parse lands
in `unparsed[]` with a line number and a reason.

Measured over the 47-plan corpus: **300 unparsed constructs across 33 plans** — 112
non-conformant column-0 bullets in `## Epics`, 74 orphaned sub-keys, 68 `Blocks:` referents
outside the newly-declared REQ-DATA-019 alphabet, 20 `depends-on` values carrying prose tails,
5 dangling `depends-on` targets, 3 non-epic `H3`s inside `## Epics`, 2 gates blocking
undeclared issues.

## Two execution-rehearsal findings, from executing plan-047 itself

Both are exactly the class a topological DAG walk would catch, and both have the same shape —
**the plan sequenced verification after construction where construction already required it**:

1. **A falsification step whose precondition is produced by a later issue.** Issue 3.4 injects a
   mutant and asserts the FAST tier reports `status: fail`. As sequenced, the linter was red on
   the historical corpus (320 errors across 169 files, all 46 bundles being `complete`), so a
   mutant-induced failure was **indistinguishable from the standing one** — the falsification
   was vacuous. Issue 4.2's status-aware promotion had to be forward-ported into Issue 3.1
   before 3.4 could observe anything.
2. **An epic that had already been emptied by its predecessors.** Epic 4 ("the full linter
   engine") ended up touching only its test file, because Epics 1–3 had necessarily pulled its
   engine features forward.

A walk over the declared `depends-on` edges before execution would have flagged both: in each
case a *verification* issue depends on a capability a *later-numbered* issue creates.

## What is still open here

The walk itself. #113's re-open trigger (two consecutive plans with structural escapes) is
**not** claimed to be met by this comment. What changed is that the walk is now buildable: the
DAG is machine-readable, the `depends-on` grammar is specified (REQ-DATA-019), and the
extractor reports what it cannot read instead of silently dropping it.

## Related, and worth reading together

The **pour-fidelity comparator** shipped in the same epic is the first consumer of this
extractor and already finds real ordering defects — a dropped `blocks` edge means a bead was
marked ready *before its declared predecessor*. It reports four populations separately, and one
of them corrects a figure from this repo's own investigation: the previously-reported **20
invented edges were substantially a parser artifact**. Splitting `invented` by whether the
document is machine-readable gives **0 invented edges in any cleanly-parsed plan**; all 127 sit
in documents whose declarations the grammar refuses. The plan↔bead identity population
(plans 006/007/036, which have no recoverable mapping) reproduces exactly.
