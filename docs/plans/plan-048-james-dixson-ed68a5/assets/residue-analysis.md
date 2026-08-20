---
type: Reference
okf_spec: OKF-PLAN
id: residue-analysis
description: Why the residue is 81, itemized (Issue 1.5)
---

# Residue analysis: measured 81 against an approval-fixed target of 54 (Issue 1.5)

## The headline

| Quantity | Baseline | After widening | Target (fixed at approval) | Verdict |
| :-- | --: | --: | --: | :-- |
| Corpus unparsed residue | 150 | **81** | **<= 54** | **MISSED by 27** |
| Plans carrying unparsed constructs | 33 of 48 | 24 of 48 | — | improved |
| Constructs recovered | 0 | **39** across 15 plans | — | — |
| Corpus documents modified | 0 | **0** | 0 | met |
| New dropped edges in previously-poured plans | — | **0** | 0 | met (SC1d) |

**The target is NOT re-derived.** 54 was fixed at approval and stays 54. This document records
why the measurement missed it; it does not move the goalposts to meet the measurement. The
capability gate `grammar widening is non-vacuous` is consequently **RED (exit 1 — capability
absent)**, which is the correct and intended behaviour of a gate whose target was fixed in
advance.

## Why 81 and not 54

The 54 target derives from EXP-001's estimate that **~96 of 150** constructs were "mechanically
recoverable". The widening recovers **69** (150 - 81). The 27-construct gap is not a shortfall
in implementation — all four declared recovery classes are implemented and tested. It is a
**conflict between two things the plan decided at different moments**:

- **EXP-001** counted a construct as recoverable if a mechanical rule *could* produce an edge
  from it.
- **Issues 1.4 and 1.4a**, written later, declared that several of those same classes must be
  **REFUSED**, because a rule that *can* produce an edge from them can equally produce the
  *wrong* edge.

The target inherited the first judgement; the implementation obeys the second. They are not
reconcilable by writing better code.

### The gap, itemized

| Refused class | Count | Why EXP-001 counted it recoverable | Why 1.4 / 1.4a refuse it |
| :-- | --: | :-- | :-- |
| `Blocks:` referent with a prose tail or trailing qualifier | 35 | a regex can strip the parenthetical | the qualifier may *narrow* the referent (`Epic 5 (decommission install.py)`); stripping it asserts it does not |
| `depends-on` with a prose tail, or `start-gate` | 22 | same strip | same ambiguity; `start-gate` names a pour artifact with no plan-issue referent at all |
| a whole gate block written inside `## Epics` | 16 | the fields parse fine *as gate fields* | recovering it means **relocating a section**, i.e. rewriting the document — barred by D-4, which is the decision that makes this whole plan hash-neutral |
| epic-level `- depends-on: Epic N` | 7 | expand to one edge per child issue | that is a **fan-out inference**, named explicitly as negative mutant 3 |
| dangling `depends-on` target | 1 | — | the target names no issue in the plan |
| **Total refused** | **81** | | |

Of these, the **16 gate-block-in-`## Epics`** constructs are the clearest case: they are
*perfectly parseable*, and refusing them is purely a consequence of D-4's no-document-rewrite
constraint. A plan permitted to move that section would recover all 16 for free. That is
plan-049's inheritance, not a defect here.

## The cost of all-or-nothing refusal, measured

Issue 1.4a requires that a partly-readable value be refused **whole**. That is not free, and
one plan pays for it visibly.

**plan-033 L511:** `- depends-on: 6.2, 1.5, gate:pi-rule-target-verified`

- **Before:** `6.2` and `1.5` materialized as edges; `gate:…` was reported unparsed.
- **After:** the whole declaration is refused; **two real edges are lost**, and
  `pour_fidelity` now reports plan-033 as `divergent` with two "invented" edges — bd carries
  edges the extractor no longer reads.

This looks like a regression and, on the edge count, it is one: net edge delta across the
corpus is **+11 recovered across 6 plans, -2 lost in plan-033**.

**It is nonetheless the right trade, for one reason that is easy to miss:** REQ-DATA-043 gates
every consumer at the **document** level. plan-033 has `unparsed[] != []`, so `pour_fidelity`
returns **INCONCLUSIVE (exit 2)**, not FAIL — the apparent divergence can never be consumed as
a verdict. The value-level refusal and the document-level gate are the same conservatism
applied twice, and the gate is what makes the refusal safe rather than merely lossy. Without
Issue 1.2's gate landed first, this refusal *would* have manufactured a false FAIL on plan-033.

## An address-space artifact, recorded so it is not mistaken for data

The raw before/after comparison shows plan-048 losing 62 edges. It has not. The "before" run
executes in the primary checkout and the "after" run in the execute worktree, and
`record-epic` writes plan-048's `**Epic:**` field **primary-side** by the §5.3 address-space
model. `pour_fidelity` skips a plan with no `**Epic:**` field, so plan-048 is simply absent
from the "after" population. Corrected net edge delta excluding plan-048: **+11 / -2**.

## What this means for the gate

`gate-grammar.sh` exits **1 — capability absent**. Per the gate's own Instructions, exit 1 is
the *only* reason a gate may be red, and this is that reason: the declared capability
(residue <= 54) is genuinely absent. It blocks **Issue 3.1** and nothing else.

The three other assertions the gate makes are all **met**: zero documents modified, the hand
audit adjudicated (39 rows across 15 plans, zero adverse findings), and no new dropped edge.
