---
type: Finding
okf_spec: OKF-PLAN
id: exp-002
description: Measured runtime and cost of headless trigger-eval sessions on pi and claude-code, projected to the operator's D3 "FULL tier, always" decision
status: partial
created: '2026-09-24'
---
# EXP-002: eval cost and runtime, and D3 feasibility

## Approach Tested

Timing and cost from the 126 EXP-003 runs (stop-on-activation, ≤6 tool calls, ≤150 s),
run in parallel across the two harnesses. Projection: 20 skills × ~6 intents
(3 trigger + 3 near-miss) × 3 reps × 2 harnesses.

## Result

**measured:** EXP-003, 63 runs per harness:

| harness | mean s/run | wall for 63 runs | cost |
| :-- | :-- | :-- | :-- |
| claude-code | 23.6 | 24.7 min | $0.22 mean over the 13 runs that exited normally and reported `total_cost_usd`. Runs killed at activation report nothing |
| pi | 13.3 | 13.9 min | not reported (cliproxyapi reports `cost.total: 0`) |

Near-miss runs are the expensive ones: they can't stop early, so they run to the tool
cap (CC N1 ≈ 66 s).

**inferred:** projection for D3 (every skill, every FULL run): 20 × 6 × 3 = 360 runs per
harness. That's ≈ 2.4 h CC + 1.3 h pi, ≈ 2.4 h wall if the harnesses run in parallel and each
runs serially. CC cost ≈ 360 × ~$0.15–0.25 ≈ **$55–90 per FULL run** (an extrapolation from 13
reported runs, most of them near-misses or non-early exits, so treat it as a rough range).
Three or more reps are needed for a trigger rate, and the near-miss set can't be shrunk
without losing the negative routing that is the point of the exercise.

Other constraints found:
- **Credentials:** both harnesses need live model auth. A CI runner has none, so there
  the eval can only report INCONCLUSIVE, the same as the existing CI carve-out for the config
  half of `yf self install`.
- **Global config leaks in:** the runs used the operator's full global config, so results
  depend on the machine (installed skills, rules, MCP servers). That's realistic, but not
  reproducible.

## Implications for Plan

**D3 as stated (every skill on every FULL run) is ~2.4 h and on the order of $55–90 per
FULL run.** The FULL tier currently runs at every land-the-plane. That's a measured cost
the operator should re-decide with numbers in hand, not one the plan should silently
keep or drop.

Measured alternatives, to present to the operator:
1. **Hash-scoped FULL:** re-evaluate only skills whose description hash (or the intent file,
   or the harness version) changed since the last recorded result in `evals/triggers.json`.
   The rating stays derived from evidence. A no-description-change landing costs ~0.
2. **FULL always, reduced:** every skill but 1 rep on the happy path, 3 reps only on skills
   whose last rating was borderline.
3. **As decided:** everything, every FULL run.

## Recommendations

Bring option 1 to the operator as the default, with 3 as the explicit alternative, before
drafting epics. Capture the CC cost properly with a small run that doesn't kill sessions
early (let them finish at the 6-call cap) to tighten the $/run figure.
