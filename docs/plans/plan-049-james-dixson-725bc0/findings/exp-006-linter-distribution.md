---
type: Finding
okf_spec: OKF-PLAN
id: exp-006
status: complete
---
# EXP-006 — Linter distribution after plan-048, and what the migration would retire

**Question:** Re-measure the report-only population (610 is flagged stale), and determine what the
D-2 migration actually retires.

## Approach Tested

All at `HEAD = 7a45e97`. Whole-repo lint decomposed by type/check/declared-severity/effective-
severity/bundle-status; per-type `files_checked` for all 17 schemas to get violation *rates*;
`plan_extract` over all 48 plans; **Simulation A** (monkey-patch `extractor_blocked → []`, i.e.
recover all 81); **Simulation B** (only the plans the 16 free relocations clear); a **relocation
experiment** placing each of the 5 distinct "free" shapes under `## Gates`; and a **hole probe**
calling `run_check()` directly on empty-celled and zero-row criteria tables.

## Result

**1. Reproduced figures.** **measured:** `PASS, files_checked: 731, errors: 0, warnings: 31,
report_only: 1340`, 17 types. The handoff's **1340 / 0 / 17 reproduce exactly**; `files_checked`
reads **731, not 726** — and the delta is accounted for: 5 of plan-048's own close-out artifacts
fall in selected paths. **The flagged-stale 610 is wrong by 2.2×.**

**2. Is `bundle_status` still 100% of the explanation? No — it is 57%.**

**measured:** all 1340 sit in `complete` bundles, **but** `declared_severity` splits
`{R: 576, W: 567, E: 197}`. **576 of 1340 (43%) are declared `R` at the schema level** and would be
report-only at *any* status. plan-047's "status explains 100%" no longer holds — a direct
consequence of Issue 2.9's rule. **The "history is not re-judged" argument now covers only 57%.**

**3. The overlap is exactly 144, and it is per-plan, not per-construct.**

**measured:** 81 constructs across 24 plans; `doc_lint` reports `R{1,1b,2a,2b,2c,3}-inconclusive` at
**24 files each = 144 findings**, over the same 24 plans. **144 of 1340 (10.7%)** is
unparsed-derived; the other **1196 (89.3%) have no relationship to the 81 whatsoever.**

> **A plan sheds its 6 inconclusive rows only when its `unparsed[]` reaches ZERO. Recovering 15 of
> a plan's 16 constructs retires nothing.** This is the conflation the brief warned about.

**4. What D-2 actually retires — measured, and it is negative.**

**measured:** the 16 free constructs span **five** plans (008=7, 010=3, 015=1, 018=2, 045=3) — not
the handoff's distribution. **plan-045 is the ONLY plan whose entire `unparsed[]` is free
constructs.**

- **Simulation B (unblock plan-045 only):** plan-relations **532 → 573**. Sheds 6 inconclusive rows,
  **gains 46 R1b + 1 R2b = 47**. **Net +41.**
- **Simulation A (recover all 81):** **532 → 884**; R1b **363 → 834 (+471)**. **Net +352.**

| Scenario | report-only | Δ |
| :-- | --: | --: |
| baseline | **1340** | — |
| D-2 as written | **1381** | **+41** |
| D-2 honest (only plan-008's 7) | **1340** | **0** |
| full recovery of all 81 | **1692** | **+352** |

**measured:** relocating plan-008's block produces **two new** refusals, not one — so plan-008 goes
8 → 3 and never reaches zero. **Realized residue after all 16 relocations is 67, not 65.**

**5. The plan-047 EXP-003 trap reproduces — INSIDE the D-2 migration.**

Relocating each of the five distinct shapes:

| Construct | After relocation | `unparsed[]` |
| :-- | :-- | :-- |
| plan-008 gate block + 6 fields | fully parsed | 2 new |
| plan-010 `- **Capability Gate G1**:` with no H3 | **`gates: []` — silently vanishes** | **clean** |
| plan-010 under a synthesized H3 | `{type: null, condition: null, test: null}` | **clean** |
| plan-018 `### Epic 6 (NOT built…)` | `{type: null, condition: null, test: null}` | **clean** |
| plan-045 `### Skill-artifact isolation` | `{type: null, condition: null, test: null}` | **clean** |

**inferred:** only **7 of 16** are free in the handoff's sense. The other **9 are not gate blocks at
all** — relocating them is semantically wrong and mechanically produces **a content-empty gate the
extractor then reports clean**. **The single plan D-2 fully unblocks — plan-045 — is entirely in
this category.** Its "recovery" is the visible→invisible conversion, verbatim: the extractor stops
complaining because it stops looking.

**6. The empty-cell hole is intact, and wider than plan-047 recorded.**

**measured:** a criteria table with correct headers, correct ids and **empty `Verification` and
`Discharged-by` cells** → clean. With **zero data rows** → also clean. There is **no
`cell-non-empty` check kind anywhere** in `doc_lint.py`. One partial backstop: **R1b counts from the
issue side and does fire** — that is where plan-045's 46 new findings come from — so R1b defends
`Discharged-by`, but **nothing defends `Verification`**, and nothing defends a zero-row table.

**A larger lever:** R1b's carve-out is the self-declared `<!-- epic-kind: bookkeeping -->` comment,
**unverified**. Declaring every epic bookkeeping retires all 834 projected R1b findings at zero
authoring cost — the same exploit class one level up.

**7. Rules whose rate is evidence about the rule:** `disposition-alphabet-offered` **100.0%**
(30/30 — a constant carries zero information), `criteria-table-columns` 95.8%,
`finding/epistemic-marker` **94.6%** (plan-047's 99.2% rule, renamed and barely moved),
`criterion-ids` 91.7%, `finding/required-sections` 90.7%.

## Implications for Plan

1. **The two populations barely overlap, and the honest answer is the disappointing one.** 89.3% of
   findings never touch the extractor. The migration's entire linter-visible surface is 144 rows.
2. **In D-2 scope the migration makes the number WORSE (+41).** Sizing the epic on "retires
   findings" sizes it on a metric that moves the wrong way. The correct justification is **DAG
   readability**, which is real and separate — but must be stated as such.
3. **Handoff §1's "free at no analytical cost" is 44% true** — 7 of 16. Mechanically relocating the
   other 9 is **actively harmful**.
4. **D-8 does not catch this class.** A vacuous *gate* adds a node with no fields and no `blocks`
   edges — invariant satisfied, information destroyed. It bites on the very first epic the handoff
   recommends.
5. **Unblocking a plan is not a cleanup, it is an unmasking** — 6 quiet rows traded for 15–46 loud
   ones. With plan-049 named as the first plan graded by `plan-relations`, the interaction needs
   deliberate sequencing.

## Recommendations

1. **Do not write a success criterion against the report-only count.** Use the extractor-side figure:
   `unparsed[]` **81 → 67** (measured, not 65), and/or plans with `unparsed[] == []` **24 → 25**.
   State the +41 delta explicitly so no reviewer reads it as a regression.
2. **Split the "16 free" into 7 + 9 in the epic itself**, and record that plan-008's relocation
   *creates* two new refusals so it does not clear.
3. **Add a `cell-non-empty` check kind BEFORE any corpus write** — else plan-047's 90-finding
   exploit is available to plan-049's own normalizer with no instrument to detect its use.
4. **Add a gate-completeness check** (`Type` plus one of `Condition`/`Test`) in the **same
   change-set** as the relocations. Drive it with a mutant first.
5. **Strengthen D-8 to a CONTENT postcondition, not a count** — "gates may only increase" is
   satisfied by a vacuous gate.
6. **Retire or re-scope `disposition-alphabet-offered`** — at 30/30 it is a constant.
