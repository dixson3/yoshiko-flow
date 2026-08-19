---
type: Reference
okf_spec: OKF-PLAN
id: comment-173-draft
disposition: partial
target: https://github.com/dixson3/yoshiko-flow/issues/173
---

# Drafted comment for #173 (partial — issue stays OPEN)

> **DRAFT — not posted.** Posting is gated on the "Upstream write" capability gate.

---

`plan-048-james-dixson-ed68a5` closes **defect 2 only**. **#173 stays OPEN**, per its own final comment
("stays open as the evidence; #174 carries the design") — and **defect 1 is deferred to
[#174](https://github.com/dixson3/yoshiko-flow/issues/174)**, which is where the design for
it belongs.

The boundary `plan-048-james-dixson-ed68a5` used: **"does the referent exist and is it shape-consistent"**
(mechanical, landed here) versus **"is the claim true"** (needs an LLM judge, → #174).

## Defect 2: a bolded disposition silently escaped verification — FIXED

`parse_upstream_rows` returned the literal `'**partial**'` for a bolded cell, which matched
no branch in `_verify_row` and so escaped verification entirely. Measured live: plan-023
carries two such cells.

- Disposition cells are now **normalized** (emphasis stripped, lowercased) before matching.
- An **unrecognised** disposition is now `fail`, not `inconclusive` — a literal no producer
  offers is a typo in the table, and a fail-loud step must not silently pass one.
- **R3, a two-parser-agreement rule**, now asserts that `plan_extract` and
  `parse_upstream_rows` read every disposition cell identically. `verify-reconcile` is
  fail-loud, so two parsers disagreeing on row shape is a fail-loud *false positive* — the
  most expensive failure kind available here.

**R3 earned its keep on its first live run.** It found a *third* naive table parser:
plan-013 row #17's title contains `(coarse\|granular)`, a GFM-escaped pipe. A naive
`split("|")` turns that into two cells, shifting every later cell left by one — so the
**Disposition** column read `granular)` and the row escaped verification. `plan-048-james-dixson-ed68a5`
fixed the escaped-pipe split in `plan_extract._table_rows` and `doc_lint.first_table`;
`parse_upstream_rows` was the one that was missed, and only the two-parser rule surfaced it.
Corpus-wide R3 disagreements are now **0**, verified non-vacuous.

**A note on how R3 itself nearly shipped broken**, since #173 is a record of exactly this
failure class: R3 reported a clean corpus **twice** while checking nothing — first because a
source-slice omitted a helper, so every call raised, was swallowed, and returned `None`
("not checked" rendered as "agreed"); then because it joined `#113` against `113`, sharing
zero keys. Both are the *check that cannot fail* defect, inside the rule written to catch a
two-parser split. Three tests now pin its non-vacuity, and a `None` view reports
**UNVERIFIED** rather than clean.

## Also landed: the relational rule family

`R1`/`R1b` (criterion ↔ issue), `R2a`/`R2b`/`R2c` (upstream row consistency), all at
severity `W` with `STATUS_SEVERITY` promotion **declared off** — stated in the SPEC rather
than inherited, because a promoted R1b would hard-fail every future plan unless every issue
were named by a criterion, which trains authors to write fake criteria.

## What stays open

**Defect 1 — whether a criterion's claim is actually true — is not addressed here** and
routes to #174. `plan-048-james-dixson-ed68a5` ships only the mechanical half.

Plan: `docs/plans/plan-048-james-dixson-ed68a5/`.
