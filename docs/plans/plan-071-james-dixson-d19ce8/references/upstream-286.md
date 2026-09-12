---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #286 - yf-plan: red-team passes need a CONVERGENCE STANDARD
  after the first cycles — an open brief on a converged plan manufactures concerns
  and grows it'
---
# Upstream #286: yf-plan: red-team passes need a CONVERGENCE STANDARD after the first cycles — an open brief on a converged plan manufactures concerns and grows it

- **Number:** 286
- **Title:** yf-plan: red-team passes need a CONVERGENCE STANDARD after the first cycles — an open brief on a converged plan manufactures concerns and grows it
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

> Measured across two plans in one session (plan-058, plan-059). Filed because the result lives
> inside plan-059's bundle, which is about a different skill, so nothing would ever apply it.

## The measurement

`yf-plan`'s red-team pass is dispatched with an **open brief** — find what is wrong. Measured on
plan-059, ten cycles, same reviewer agent definition, same plan:

| Passes | Brief | Concerns per pass | Plan size |
| :-- | :-- | :-- | :-- |
| 1–5 | **open** | 15, 17, 18, 10, 14 | **grew** |
| 6–10 | **scoped** (below) | 3, 2, 2, 1, 0 | **shrank** |

**Identical cycle budget, opposite trend.** The variable was the brief.

The scoped standard used from pass 6:

> APPROVE unless the defect is in the **blocking class** — wrong behavior, data loss, an unpassable
> gate, an unclosable plan, or a misleading instruction to an executor. Nits go in
> Strengths/Missing **without changing the verdict**.

**Reproduced directionally on plan-058**: it ran passes 1–3 on an open brief (16, 9, 15 concerns,
plan growing 27 → 35 → 37 issues), then adopted the same standard at pass 4 and got **one blocking
one-line fix with the plan size unchanged**, then APPROVE at pass 5.

n=2 plans. Not a law — but the direction is consistent and the mechanism is legible.

## Why an open brief is the wrong instrument on a converged plan

A reviewer given "find what is wrong" and a plan with nothing seriously wrong will **produce
findings anyway**, because returning nothing reads as not having looked. Those findings are real
observations — they are simply **not defects**, and acting on them adds scope. That is what "the
plan grew" means: passes 1–5 of plan-059 added epics and criteria in response to concerns that
would not have stopped a competent executor.

The scoped brief does not suppress the observations. It **relocates** them: nits still get recorded
under Strengths/Missing, they just stop changing the verdict and stop generating issues.

## Why this is not "just raise the review-cycle limit"

The obvious reading of a plan hitting its bound is that the bound is too low. **This measurement
says otherwise.** plan-059 hit the `stop_class: 4` bound at 5 cycles and the operator raised it to
10 — but what fixed the trend was the brief, applied at the same moment. Had the default simply been
10, passes 6–10 would have run under the brief that was producing 14–18 concerns, and the plan would
have hit 10 with more sprawl and a later escalation.

**Raising the bound would have delayed the intervention that worked.** The bound is a forcing
function to spend an operator turn, not a quality threshold — and it did its job.

## Proposed change

1. **After N passes (N=3 on this evidence), dispatch the red-team with the blocking-class standard
   rather than an open brief.** The threshold is a judgement call; the class list is the substance.
2. **Carry the standard in the escalation payload.** `review-loop-check` currently escalates with a
   bare count — *"cycles 5/5, escalates=true"* — which asks the operator to decide with no
   alternatives and no recommendation. It should offer *"raise the bound, or scope the brief;
   recommended: scope the brief"*. In this session the scoped standard was supplied ad hoc by the
   parent session and would not have existed otherwise.
3. **Consider requiring a stated reason on a raise**, recorded in `log.md`, so raising is a decision
   with evidence rather than a nudge. Suggested only after (2) lands — the payload is where the
   leverage is.

Note that (2) is structurally the same shape as `yf-judgement`'s escalation artifact (#269, Epic 2/3):
a structured question with named alternatives, a recommendation, and an `on_no_answer`. If that
lands, this becomes a consumer of it rather than a parallel mechanism.

## Caveat

n=2 plans, one session, one operator, and in both cases the same parent session supplied the
standard. The reviewer agent definition was unchanged, which is what makes the brief the isolated
variable — but a third plan under a different operator would be worth having before treating the
threshold as settled.

## Related

- #269 — `yf-judgement`; the escalation payload this should consume
- #273 — command-vs-obligation; an instruction's *form* changing compliance, same family

🤖 Generated with [Claude Code](https://claude.com/claude-code)

