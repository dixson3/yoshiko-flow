---
type: Finding
okf_spec: OKF-PLAN
id: exp-007-orthogonality-test
description: An orthogonality test is buildable on one signal only — and topological independence does NOT predict defect injection. The lever is single-writer ownership, not resequencing.
---

# EXP-007 — buildable, predictive on ONE signal, and it refutes the actionable half of the framing

**Verdict: half-confirmed, half-refuted — and the half that fails is the half you would act on.**

## 1. THE REFUTATION — resequencing is not the lever

The framing was: *fan-out requires orthogonality → test the sequence → iterate the DAG topology.*
Measured against 140 documented defect pairs across plans 049/050/051:

| | ordered (a dependency path exists) |
| :-- | --: |
| **Defect pairs** | 79 / 140 = **56.4%** |
| **All pairs (base rate)** | 794 / 1534 = **51.8%** |

**No discrimination at all.** Defect pairs are *not* enriched for topological independence.

**Re-verified by the main session** — the four highest-profile injected defects, checked against
plan-050's own extracted DAG:

```
0.2 <-> 7.1   ordered=True     (C93 — controls.txt ownership)
2.2 <-> 2.2a  ordered=True     (C92 — test_doc_lint.py / DOC-LINT.md)
0.1 <-> 7.3   ordered=True     (C95)
```

C93's own text is the mechanism in one line: *"0.2 is its sole writer; 7.1 named `ctl-186`/
`ctl-187` but never added them"* — **against an edge `7.1 depends-on 0.2` that already exists.**

**These are shared-artifact-OWNERSHIP defects, and they happened just as often in pairs the DAG
had already sequenced. Adding an edge would not have prevented a single one of them.**

## 2. The reframe that follows

**Do not build an orthogonality gate over independent pairs.** Build a **single-writer ownership**
check over **all** pairs:

> *artifact X is named by issues {A, B}; exactly one must own the write.*

Filtering to topologically-independent pairs **discards 56% of the real defects**. Keep topology
as a **severity modifier**, never as a filter.

## 3. Issues do not declare what they touch — the same blocker EXP-003 found

```
plan       issues  w/detail  w/resolved-path   coverage
plan-047       77        69               25        22%
plan-048       39         0               17        41%
plan-049       43         0               13        30%
plan-050       28         0               16        54%
plan-051       23         0               20        78%
TOTAL         210        69               91      43.3%
```

**Re-verified: `detail` is empty for 28 of 28 issues in plan-050.** The corpus writes one long
single-line bullet, so all prose lives in `title`. This independently reproduces plan-050's own
C99 (*"35 bullets, 0 carrying prose"*).

Prose-scraping is **not** a substitute: of 163 path-shaped tokens, 70 resolve to exactly one file,
**34 resolve to 2–8 files**, 40 resolve to none — and no rule can separate *a file this issue
edits* from *a file this issue cites as evidence*.

**The authoring change is non-breaking — spiked and measured.** A `- touches:` sub-key bullet
parses today with `--strict` exit **0** and `unparsed: []`, so authors can adopt it before any
tooling change; promoting it to a first-class `touches[]` field sits beside the existing
`depends-on` / `resolves-upstream` handling.

## 4. Signals — one works, and the one that "obviously" should does NOT

Ablation over decidable pairs, with hypergeometric one-sided p-values:

| Signal | base rate | recall | precision | lift | p |
| :-- | --: | --: | --: | --: | --: |
| **S1 shared declared paths** | 15.2% | 43.5% | **58.8%** | **2.86x** | **3.4e-11** |
| S2 `CHANGE-VALIDATION` rows | 78.6% | 91.3% | 23.9% | 1.16x | **0.85** |
| S3 `DRIFT-CHECK` edges | 6.5% | 13.0% | 40.9% | 1.99x | — |
| **S1 + S3** | 17.3% | 47.8% | 56.9% | 2.77x | **7.2e-12** |
| S4 shared upstream refs | — | — | — | — | fired **0** times |

**S2 is at chance (p = 0.85) and must be EXCLUDED.** Diagnosed: recipe rows are far too coarse —
`doclint`/`doclint-tests` alone produce the coupling in 60–91 of each plan's coupled pairs,
because every `.md` under `skills/*/spec/` or `docs/plans/**` selects them. Including S2 pushes
the base rate to 78.6%: **a metric that flags 4 pairs in 5 trains the operator to ignore it.**

This corrects my own brief, which predicted S2 would be a strong signal. It also revises EXP-004's
implication: **`_scoped_ids()` does not need a CLI verb** — exposing it would ship the one signal
that does not discriminate.

**The pooled headline (45% recall at 17.2% base rate) is misleading and must not be quoted.** On
the decidable subset the lift is 0.98–1.53x, because 95–99% of decidable pairs score COUPLED. Only
the ablated S1+S3 numbers are honest.

## 5. The exit contract — a COVERAGE FLOOR, not a per-pair guard

| verdict | condition | exit |
| :-- | :-- | --: |
| `ORTHOGONAL` | coverage ≥ floor **and** no flagged pair | 0 |
| `COUPLED` | coverage ≥ floor **and** ≥ 1 flagged pair | 1 |
| `INCONCLUSIVE` | **coverage < floor — the metric has NO INPUT.** Never "orthogonal" | 2 |

Per-pair INCONCLUSIVE is necessary but **not sufficient**: a plan where 60 of 77 issues declare no
path can still yield a few clean decidable pairs and read green. At an 80% floor the prototype
returns **exit 2 on all five plans** — the correct answer today. Per `doc_lint`'s two-vocabulary
lesson, callers branch on the **verdict**, and `2` maps to `warn`, never a hard gate.

**Ambiguous resolution must be surfaced, not silently over-attributed** — `red-prework.md` in
plan-050 resolves to *both* the 050 and 051 bundles, manufacturing coupling. Same
false-confidence class, opposite direction.

## 6. Plan-level probe (secondary)

The metric extends to two `plan.md` files by taking the union of per-issue paths:

```
plan-050 x plan-051:  shared=12  jaccard=0.19   <- highest in corpus
plan-047 x plan-049:  shared= 4  jaccard=0.06   <- lowest
```

Face validity: plan-050 × plan-051 are literally a split of one plan (D-9). But *"validate the
integration tests first, on merge"* needs something that **does not exist**: `change_validation.py
run --tier full` runs over **one** merged tree, and there is no verb taking two worktrees and
validating their union before either lands. There is also no cross-plan artifact-ownership
register. **Defer as its own effort.**

## 7. Implications

| # | Implication |
| :-- | :-- |
| I-1 | **Reframe from orthogonality-and-resequencing to SINGLE-WRITER OWNERSHIP over all pairs.** 56.4% vs 51.8% is no signal; the ownership check is what would have caught C30/C92/C93/C95 |
| I-2 | **Land the `- touches:` authoring change first** — non-breaking, spiked. Without it the check is permanently INCONCLUSIVE. Same shape as EXP-003's #199a-before-#199b |
| I-3 | **Ship S1 + S3 only. Exclude S2 and S4, with the measured reason recorded** (`p = 0.85`, base rate 78.6%) so a later round does not re-add the row signal because it looks authoritative |
| I-4 | **Fail-closed on a coverage floor**; map exit 2 to `warn`; surface `dropped_ambiguous` |
| I-5 | **Never quote the pooled recall figure as evidence of usefulness** — report ablated numbers with base rates or none |
