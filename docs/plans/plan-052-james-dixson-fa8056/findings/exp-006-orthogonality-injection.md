---
type: Finding
okf_spec: OKF-PLAN
id: exp-006-orthogonality-injection
description: The orthogonality hypothesis is refuted. Artifact overlap is a 14-24x discriminator; topological independence is not significant. And the corpus has essentially no concurrency.
---

# EXP-006 — orthogonality REFUTED; artifact overlap is the lever; there is no concurrency to measure

**Independently corroborates EXP-007 from the defect side, with stronger statistics.**

## 1. There is no concurrency — decisive, and it must be said plainly

| Measure | Value |
| :-- | :-- |
| Beads with `metadata.plan` | 225 |
| Beads with **both** `started_at` and `closed_at` | **86** (plan-048: **0 of 39**) |
| Bead pairs with overlapping intervals | **37 of 1222 (3.0%)** |
| Mean concurrency (Σdurations ÷ union) | **1.10 / 1.19 / 1.53 / 1.11** |
| Of the 37 overlaps, closed within 5s of each other | **31 (84%)** — batch-close bookkeeping |

The 6 non-batch overlaps are **all plan-051** and **all involve one straggler bead**
(`yf-mol-3he.2.5`) left claimed while a strictly serial chain ran underneath it — `3.1`→`3.2`→
`3.3`→`4.1`→`4.2`→`4.3`, **perfectly abutting, zero gap, zero overlap**.

**A single coordinator runs beads serially. Genuine concurrent-execution pairs ≈ 0.** The corpus
cannot answer the concurrency question empirically, and will not under the current coordinator.

**Separate instrumentation defect:** `started_at` coverage is 86/225, and `bd list --json` does not
even expose it (`bd export --all` does). Without fixing this, no future concurrency experiment is
possible.

## 2. Most defects do not span two issues at all

212 concern rows across 22 `reviews/pass-*.md` in plans 049/050/051:

| Anchor shape | rows | % |
| :-- | --: | --: |
| **< 2 distinct anchors (single-site / intra-unit)** | **110** | **51.9%** |
| 1 issue + **non-issue artifact** (SC row, `context.md`, REQ, gate Condition) | 38 | 17.9% |
| **non-issue artifacts only, 0 issues** | 30 | 14.2% |
| ≥ 2 issues + artifact | 24 | 11.3% |
| ≥ 2 issues only | 10 | 4.7% |

**Only 34 of 212 (16%) name two or more plan issues.** And **32% anchor an issue to something that
is not a DAG node at all** — you cannot add an edge between "Issue 2.2a" and "SC6".

**A DAG-edge remedy is structurally incapable of addressing the largest defect class.**

## 3. The base-rate test — the null is NOT rejected

| Test | observed independent | expected (stratified) | z |
| :-- | :-- | :-- | --: |
| raw pair instances, conservative | 63/119 = 0.529 | 0.424 | 2.34 |
| raw pair instances, liberal | 105/222 = 0.473 | 0.406 | 2.04 |
| **unique pairs (dedup), conservative** | **42/85 = 0.494** | **0.430** | **1.20** |
| **unique pairs (dedup), liberal** | **59/130 = 0.454** | **0.405** | **1.13** |

The raw z ≈ 2 is an **artifact**: plan-050's capability-gate `Blocks`-set defect family is
re-reported across passes 1, 3, 4, 5, 6, 7, 8 and 12. **After deduplicating to unique pairs,
z ≈ 1.15 (p ≈ 0.25) — not significant.** The effect also **reverses sign in 2 of 3 plans**.

**Cross-validation with EXP-007.** The two experiments used different methods and produced an
**exactly matching base rate** — independent pairs across 049/050/051 = **48.2%** both ways
(re-verified by the main session). They **disagree in the direction** of the defect-pair deviation
(EXP-007: defects slightly *less* independent; EXP-006: slightly *more*) and **agree that neither
is significant** — which is precisely the signature of noise around a null.

## 4. The 2×2 that actually explains the data

Defect density per issue pair, pooled over 049/050/051:

| | artifact **overlap** | artifact **disjoint** |
| :-- | --: | --: |
| **path-CONNECTED** | 25/69 = **0.362** | 18/725 = 0.025 |
| **INDEPENDENT** | 34/113 = **0.301** | 8/627 = 0.013 |

- **Artifact overlap raises defect density 14×–24×, inside BOTH strata.**
- **Within the overlap stratum, independent pairs are LESS defect-dense than connected ones**
  (0.301 vs 0.362; liberal 0.363 vs 0.551; same in plan-050 and plan-051 alone).

**So adding an edge between two overlapping issues moves the pair from the 0.301 cell to the 0.362
cell — the wrong direction.** Overlap is the signal; the DAG edge is not.

## 5. The single decisive case — the edge already existed

plan-051 `RE-003` is the corpus's **only** recorded execution-phase cross-issue invalidation:

> *"Issue 3.2 (commit `1eb9bae`) added `scripts/test_review_agent_contract.py`, whose line 145
> quotes 'never writes files' inside an assertion message… **A criterion discharged at 1.2a was
> invalidated by a later epic.**"*

**Re-verified by the main session against plan-051's extracted DAG:**

```
direct edges from 3.2: ['1.2a', '3.1']
3.2 reaches 1.2a (3.2 runs AFTER 1.2a): True
```

**`3.2 depends-on 1.2a` is a DIRECT DECLARED EDGE.** 3.2 ran strictly after 1.2a and the defect
landed anyway. **Sequencing guarantees the second unit runs later — not that it re-checks the
first unit's criterion.** The retrospective names the real gap itself: *"nothing in this plan
re-checks `plan.md` CRITERIA at completion."*

**Would an edge have prevented the 5 independent-pair defects? 0 of 5.** Three are
gate-`Blocks`-set contradictions (an edge between gate-blocked siblings is meaningless or would
cycle with the gate); one is intra-text; one is an epic-header declaration.

## 6. Incidental but worth recording

**Pour fidelity is 100% on plans 047–051** — the declared DAG and the poured bead DAG are
byte-identical (75/62/60/41/27 edges each way, `only-declared: []`, `only-bead: []`).

## 7. The honest caveat

**The artifact-overlap measure is partially circular**: it is derived from issue prose, and the
same prose influences whether a reviewer names two issues in one concern. The commit-file
cross-check (13.8% strong attribution) is too sparse to break the circularity.

**Label the overlap effect INFERRED, WEAKLY CORROBORATED. The independence null-result, by
contrast, is a direct base-rate comparison and is solid.**

## 8. Implications

| # | Implication |
| :-- | :-- |
| I-1 | **Reject "the DAG is missing edges it should have had."** Replace with: *the plan bundle has a cross-artifact invariant surface that nothing re-checks*. Evidence: RE-003, where the edge existed and the defect landed |
| I-2 | **The remedy is the completion-time criteria re-check (#199), not new edges** — and this experiment reached that conclusion independently of EXP-003 |
| I-3 | **Artifact-overlap declaration is an ATTENTION signal at intake, not a sequencing constraint.** Report overlapping pairs in **both** strata; do not propose edges |
| I-4 | **Gate-`Blocks`-set consistency is the highest-yield single check this data supports** — 3 of 5 independent-pair defects plus plan-050's repeat-offender family are "the gate's Condition contradicts the issues in its Blocks set." It is one mechanical predicate over `plan_extract`'s gate objects |
| I-5 | **Instrument the coordinator** to write `started_at` unconditionally and close beads when work finishes, not in batches — otherwise no concurrency question is ever answerable |
| I-6 | **Drop any plan step premised on measuring parallel-execution races on 047–051.** There are none to measure |
