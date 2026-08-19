---
type: Finding
okf_spec: OKF-PLAN
id: exp-005
status: complete
---
# EXP-005 — #173 mechanical feasibility and the #173/#174 boundary

**Question:** Is #173 implementable as linter rules, what is the corpus's conformance today, and
where exactly does #173 end and #174 begin?

## Approach Tested

Read #173/#174 in full; read `plan_extract.py`, `doc_lint.py`, `plan.toml`, `plan_manager.py`
(`_verify_row`, `parse_upstream_rows`, `_readiness`), `spec/data.md` REQ-DATA-018,
`plan_template.py`. Prototyped five candidate rules over `plan_extract.extract()`, ran them across
all 47 plans, then ran a **seven-mutant falsification harness** against plan-047 plus a clean control.

## Result

### 1. The era mechanism already exists: `doc_lint.STATUS_SEVERITY`

- **measured:** `uv run _shared/doc_lint.py --type plan --json` → `PASS 47 files, E 0, W 0, R 371`;
  every finding carries `bundle_status: complete`.
- **measured:** the same `plan-046` with `status: review` substituted → `FAIL: 12 errors`, same
  checks, promoted `R`→`E`.
- **inferred:** `STATUS_SEVERITY` (`doc_lint.py:60-88`) maps `E`→`R` for
  `approved|executing|reconciling|complete` and `W`→`E` for `review|ready-for-approval`. All 47
  historical plans are `complete`, so **any new `E` check is automatically report-only across
  history and error-level only at intake.** No new mechanism, no backfill, no `--since` flag.

### 2. verdicts per rule

| Rule | Verdict | Extractor field |
| :-- | :-- | :-- |
| **R1** every `Discharged-by` token is an issue id in `## Epics` | **yes** | `criteria[].discharged_by` × `{issues[].id}` |
| **R1b** every issue is named by ≥1 criterion (reverse of REQ-DATA-018) | **partial** — needs a declared bookkeeping carve-out | same, reversed |
| **R2a** every `Resolved By` token is an existing issue id | **yes** | `upstream[].resolved_by` |
| **R2b** `exclude` resolves nothing; `include`/`partial` resolves something | **yes** | `.disposition` + `.resolved_by` |
| **R2c** disposition is a recognised literal | **yes** | `.disposition` |
| **R3** `plan_extract` and `plan_manager.parse_upstream_rows` agree | **yes** — *this is what actually closes #173 defect 2* | both parsers |

### 3. seven mutants, all firing, with a clean control

Control: unmutated plan-047 → `structural rules → PASS`, `R3 → PASS []`.

| Mutant | Rule fired |
| :-- | :-- |
| M1 `SC40` discharged-by `10.6`→`99.9` | R1 not-an-issue |
| M2 `SC1` discharged-by emptied | R1 empty |
| M3 inject `Issue 0.0z` | R1b named by no criterion |
| M4 `include` row `Resolved By`→`99.9` | R2a |
| M5 `exclude` row given `Resolved By: 1.1` | R2b |
| M6 disposition bolded `**partial**` | R3 FAIL `[('113','**partial**','partial')]` |
| M7 `include` row `Resolved By` emptied | R2b |

**M6 is the important one.** `plan_extract` does `.strip().strip("*")` and is immune to bolding,
but `plan_manager.parse_upstream_rows` (`:3908`) does only `.lower()` and **still returns
`'**partial**'` today** — so #173 defect 2 is live in the engine that halts reconciliation, and a
rule written over `plan_extract` alone is **vacuous against it**. Corpus scan: **plan-023 already
carries two bolded cells** (`#60 **defer**`, `#65 **supersede**`) — one historical `supersede` row
has been silently unverified.

### 4. corpus conformance (47 plans, all `complete`)

**R1/R1b are not measurable on 44 of 47 plans, because the input does not exist.**

- **measured:** only **3 of 47** plans have a *table* under `## Success Criteria` — plan-039,
  plan-040 (no 4th column) and plan-047. The other **44 use a numbered prose list**;
  `plan_extract` reports `0 criteria` for each.
- **measured:** `Discharged-by` present in **1 / 47** (plan-047).

| Rule | Pass | Fail | N/A (no criteria table) |
| :-- | --: | --: | --: |
| R1 | 1 | 2 (plan-039 14 empty cells, plan-040 17) | 44 |
| R1b | 1 | 2 | 44 |
| R2a | 47 | **0** | — |
| R2b | 46 | 1 (plan-016 `exclude` with `n/a (deferred)`) | — |
| R2c | 41 | 6 (`tracks-plan`, `file at land-the-plane`, `include (full model)`, `defer` ×2, `related`, `deferred` ×3) | — |
| R3 | 46 | 1 (plan-023) | — |

All failures are era-driven. **Zero would be error-severity under the existing status mapping.**

### 5. two extractor defects that would produce FALSE failures

Prerequisites, not nice-to-haves:

1. **`_table_rows` does not honour GFM-escaped pipes.** It splits on raw `|`; plan-047's `SC4`
   contains an escaped pipe, shifting every column. As-shipped the prototype reported 8 findings on
   plan-047 — **all artifacts**; with a `(?<!\\)\|` splitter, plan-047 scores 0. Not a corner case:
   `plan_template.py:54`'s seeded Risks row is `high \| med \| low`, so **every plan from the
   template carries an escaped pipe by construction.** `doc_lint.first_table` has the identical
   defect, currently unexposed.
2. **A non-empty `unparsed[]` makes the issue-id set incomplete**, so "names an issue that does not
   exist" is unsound. plan-037's `- **Issue 2.2 (#100): …` form is never extracted, and the naive
   R2a run reported 4 dangling `Resolved By` findings that are **all false**. **33 of 47 plans have
   non-empty `unparsed[]` (150 entries).** R1/R1b/R2a must gate: `unparsed[] != []` →
   **INCONCLUSIVE (exit 2)**, never FAIL.

### 6. relations that LOOK checkable but are not

- **"the issue *really* discharges the criterion"** — pure semantic judgement. #174's matrix cell.
  plan-047's EXP-002 measured the inference at ~10% yield / ~73% precision. **Not checkable.**
- **#173's own defect 1** ("plan Issue 4.5 says *close #140*, engine says `partial` stays OPEN") —
  a claim in an issue's **prose body** contradicting `_verify_row`'s contract. No extractor field
  holds it. Needs prose read against the branch table — **squarely #174**. A structural rule here
  would be a control that checks nothing.
- **"the criterion is falsifiable against the pre-work tree"** — requires *executing* the
  `Verification` cell. No runner exists. **#174 Part 1.**
- **`Discharged-by` as plain `E` at `drafting`** — `STATUS_SEVERITY` leaves `E` as `E` there, so it
  would hard-fail a half-written plan. Must be `severity = "W"`.
- **R1b without a declared bookkeeping carve-out** is a false-positive generator — a plan with a
  genuine bookkeeping epic legitimately has no criterion. Without a declared marker the rule
  **silently trains authors to write fake criteria.**

### The #173 / #174 boundary

| | Closes with plan-048 | Stays open (#174) |
| :-- | :-- | :-- |
| #173 defect 2 (bolded disposition fails OPEN) | **Yes** — R3 + normalize `parse_upstream_rows` + unknown-disposition→`fail` in `_verify_row`. #173 names this fix literally. | — |
| #173 defect 1 (plan says "close #140", engine says stay OPEN) | **No** | Needs prose vs `_verify_row`; #174 concedes "no command at review time surfaces this" |
| #173's generalization | **Structurally yes** (the joins) | **Semantically no** (falsification, `file:line`, REQ double-allocation) |

**The line falls at "does the referent exist and is it shape-consistent" (#173, plan-048) vs
"is the claim true / non-vacuous" (#174).**

> **Tension with D-3, flagged for the operator:** #173's own last comment reads *"This issue stays
> open as the evidence; #174 carries the design"* — which reads as the operator having already
> decided #173 stays open. D-3 says plan-048 includes #173. These may conflict.

## Implications for Plan

**D-3's reasoning holds** — 047 did build the substrate. Three things change the shape:

1. **The rules fit no existing `run_check` kind.** All six current kinds take only `text`.
   Cross-section referential checks need a **new kind** that calls `plan_extract.extract()`. Real
   epic-sized work, not a `plan.toml` row.
2. **The two extractor fixes are hard prerequisites.** Ship without them and 8 of plan-047's own
   findings are false, including 7 fabricated R1b violations — a control that fails on nothing real.
3. **R2c/R3 have immediate value at near-zero era cost** — but `deferred` appears 3× in plan-047
   alone, suggesting the *recognised set* may be wrong rather than the plans. It would fire on
   plan-048 itself.

## Recommendations

1. Scope the epic as: **extractor prerequisites → new `plan-relations` check kind → R1/R1b/R2a/R2b/R2c
   at `severity = "W"` → R3 + `parse_upstream_rows` normalization + `_verify_row`
   unknown-disposition→`fail`.**
2. **Declare `W`, not `E`,** for R1/R1b. `STATUS_SEVERITY` promotes at `review`. Do not build a
   second era mechanism.
3. **Land the seven mutants as committed fixtures** under `tests/fixtures/doclint/plan/`, each
   asserting FAIL, plus unmutated plan-047 asserting PASS. Without the control, M6 passes trivially.
4. **Operator rulings needed before drafting:** (a) is `deferred` a legitimate disposition (3 uses
   in plan-047) or a defect? (b) does #173 close with plan-048, or stay open as evidence per its own
   final comment, with plan-048 closing only the defect-2 half?
5. Do not scope the falsification rule, `file:line` resolution, or semantic discharge into plan-048.

**Absence of a problem, recorded:** R2a has **zero real violations** across all 47 plans once
extractor artifacts are excluded. Worth shipping (it has a firing mutant and is free once the join
exists), but it will not find anything historically.
