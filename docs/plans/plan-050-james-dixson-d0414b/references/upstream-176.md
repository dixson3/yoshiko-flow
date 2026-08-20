---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #176: plan-048-james-dixson-ed68a5 execution tracking

- **Number:** 176
- **Title:** plan-048-james-dixson-ed68a5 execution tracking
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Coarse tracking issue for `plan-048-james-dixson-ed68a5` — one issue per plan-scale effort, per the
repo's Upstream Tracking convention.

**Plan:** `docs/plans/plan-048-james-dixson-ed68a5/`

**Supersedes [#175](https://github.com/dixson3/yoshiko-flow/issues/175)**, plan-047's coarse
tracker. Per this plan's D-2, #175 is closed once this issue exists and links it: two epics
stamped onto one tracker breaks `upstream.py closable`'s per-`external_ref` grouping.

## Scope delivered (Epics 0–3 + landing)

**Epic 0 — SPEC-first.** `REQ-DATA-043` (the `unparsed[]`-gating contract),
`REQ-DATA-044` (the `plan-relations` check kind), `REQ-DATA-045` (no `E` severity off the
plan-bundle axis unless the corpus already passes). `REQ-DATA-019` gained an explicit
authoring-grammar vs reading-grammar split; `REQ-PLAN-074` gained the `deferred` end-state
contract (OPEN → pass with **no** plan-id-mention requirement, not-OPEN → fail).

**Epic 1 — extractor grammar widening.** Corpus unparsed residue **150 → 81** across 48
plans; plans carrying any unparsed construct **33 → 24**; **39** constructs recovered across
15 plans, every one hand-adjudicated with zero adverse findings. **Zero corpus documents
modified** — hash-neutral by construction.

**Epic 2 — document types.** `doc_lint` `files_checked` **180 → 726**, 3 declared types → 17,
**0** error-severity findings on the merged tree.

**Epic 3 — relational checks.** R1/R1b/R2a/R2b/R2c/R3 over `plan.md`, seven committed mutant
fixtures plus an unmutated control, and #173's defect 2 closed.

## Deferred to plan-049

The corpus migration write-phase and the enforcement binding (D-13's split), carrying
[#140](https://github.com/dixson3/yoshiko-flow/issues/140) and
[#149](https://github.com/dixson3/yoshiko-flow/issues/149). Scoped from
`references/handoff-049.md`, written while this execution's context was live.

**A free recovery is waiting there:** 16 of the remaining 81 unparsed constructs are
perfectly parseable and are refused only because recovering them means relocating a section,
which this plan's D-4 forbids.

## Notes worth carrying

- The residue target was **re-based 54 → 81 at execution**. The 54 was **misderived, not
  missed**: it inherited EXP-001's "~96 of 150 mechanically recoverable" estimate while
  Issues 1.4/1.4a — written later — declared several of those same classes must be
  **refused**. Seven red-team cycles all checked the target was *fixed at approval*; none
  checked it was *derivable from what the plan permits*.
- **R3 found a third naive table parser.** plan-013 row #17's title contains an escaped pipe
  `(coarse\|granular)`; `parse_upstream_rows` split on it, shifting the Disposition column
  to `granular)` so the row escaped verification entirely.

