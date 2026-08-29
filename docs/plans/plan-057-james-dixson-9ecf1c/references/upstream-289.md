---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #289 - yf-plan: no instrument compares a plan''s cited
  figures against its own commands'' output'
---
# Upstream #289: yf-plan: no instrument compares a plan's cited figures against its own commands' output

- **Number:** 289
- **Title:** yf-plan: no instrument compares a plan's cited figures against its own commands' output
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/289
- **State:** OPEN
- **Labels:** type::feature, priority::medium

## Body

## The defect

Every measured figure in a `plan.md` is **hand-transcribed** from a command run at authoring time. Nothing re-runs that command and diffs the stated value against its output. A figure is therefore correct only until the corpus changes — which it does on every plan that lands.

The plan already carries both halves an instrument would need:

- the **Verification** column gives the command
- the **criterion cell** gives the claimed figure

Nothing compares them.

## Why file it now

It was named under `## Missing` in **four consecutive red-team passes of plan-057** (passes 2, 3, 4, 5) and never closed, and it cost at least one defect in every one of them:

| Pass | What went stale |
| :-- | :-- |
| 2 | SC3's baseline triple was **unreproducible** — three extraction rules gave three answers, because no rule was ever recorded. SC1's figures wrong. `58` → 59 bundles, `63` → 64 enumerated. |
| 3 | SC1's "verbatim" quote went stale **from pass 2's own deletion** — in the same pass that pinned it. |
| 4 | Issue 1.0 carried `five`/`four` leftovers from a 4→5→6→7 growth — **in the issue that owns the anti-off-by-one arithmetic**. The `assess` census said 9; measured 11. |
| 5 | Issue 3.1 said `~144`, SC20 said `~147`, measured **152** — two approximations of one quantity, three lines apart in the same document. |

Five independent reviewers each re-measured by hand and each found a *different* stale figure. The defect survives because catching it depends on a human re-running a command and comparing — exactly the class of check this repo mechanizes everywhere else.

## Evidence

```
$ grep -c 'instrument-output diff' docs/plans/plan-057-james-dixson-9ecf1c/reviews/pass-{2,3,4,5}.md
1   1   1   1

$ grep -ro 'knowledge-catalog' . --exclude-dir=.git | wc -l
152          # while plan.md said ~144 in one place and ~147 in another
```

## Proposed shape

A checker that, for each Success Criterion whose cell states a measured figure, re-runs the Verification command and diffs the stated value against the output. Exit `0` agree · `1` disagree · `2` could not run (INCONCLUSIVE — a statement about the instrument, not the plan), matching `scripts/checks/_common.sh`.

The hard part is **extracting the claimed figure from prose**, which is why this is an issue rather than a one-line addition. A narrower first slice that would still have caught every row in the table above: assert that any `N/M`, `X of Y`, or `~N` appearing in a criterion cell **also appears in the output of that cell's own command**.

## Why it is not being fixed in plan-057

Deliberate. Inventing a sixth new instrument *after* pass 5 returned APPROVE would restart the review cycle on unreviewed text — the plan grew 4 → 5 → 6 → 7 instruments across passes, and each addition needed its own arithmetic propagated to four surfaces (`--require`, the gate `Test`, SC0b prose, SC0's `test -x` list). It belongs upstream as its own effort.

Recorded in that plan's retrospective as **RE-001** (`docs/plans/plan-057-james-dixson-9ecf1c/plan-retrospective.md`), `detected-by: mechanical-check`.

## Related

- plan-057 (`docs/plans/plan-057-james-dixson-9ecf1c/`) — reviews `pass-2.md` … `pass-5.md`, `## Missing` in each
- The `manual:` → executable promotions in the same plan are the same instinct applied to a different axis

🤖 Generated with [Claude Code](https://claude.com/claude-code)

