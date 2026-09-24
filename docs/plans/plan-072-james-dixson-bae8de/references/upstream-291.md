---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #291 - yf-drift-check edge over the escape/stop taxonomy
  — #145''s announced mitigation does not exist'
---
# Upstream #291: yf-drift-check edge over the escape/stop taxonomy — #145's announced mitigation does not exist

- **Number:** 291
- **Title:** yf-drift-check edge over the escape/stop taxonomy — #145's announced mitigation does not exist
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

> Filed by plan-059 Issue 2.7 (`yf-judgement`), which found this mitigation announced but never
> built. Source bundle: `docs/plans/plan-059-james-dixson-55137e/`.

## The gap

`#145` announces a `yf-drift-check` edge over the escape/stop taxonomy as its mitigation for that
taxonomy fragmenting. **The edge does not exist.** `DRIFT-CHECK.md` declares no node for it, so
nothing checks that the taxonomy's homes agree, and the announced mitigation has been vapour since
it was written.

plan-059 makes this worse by one, which is why it is filing rather than merely noting: it adds a
fourth home.

## The escape/stop `taxonomy` has FOUR homes

| # | Home | What it carries |
| :-- | :-- | :-- |
| 1 | `plan-retrospective.md` / `REQ-PORT-052` | `escape_class`, `stop_class`, `adjudication` — the closed adjudication of a stop that already happened |
| 2 | `skills/yf-plan/scripts/retrospective_fields.py` | the executable domain check over those fields |
| 3 | `skills/yf-herdr/SPEC.md` §3 | the deviation taxonomy — whose *"Premise refuted at execution"* is the corpus's `reasoned-past-a-documented-fact` under a different string |
| 4 | `escalations.md` / `REQ-PORT-053`–`054` (**new, plan-059**) | the OPEN question, with a mutable `state` — deliberately a separate file, because a retrospective entry is append-only by design and an escalation's whole lifecycle is a state change |

Home 3 is the instructive one: two homes already carry **the same class under two different
names**, and nothing detected it. That is precisely what a drift edge is for.

## Requested

Add a `yf-drift-check` edge to `DRIFT-CHECK.md` binding these four nodes, so a class added to one
home and not the others is a reported finding rather than something a later plan discovers by
hand. Scope it to the taxonomy vocabulary only — not to the surrounding prose, which legitimately
differs per home.

## Explicitly NOT this issue

**The SEVERITY vocabulary is a different object** and is already pinned by `REQ-DATA-076`
(plan-059 Epic 1). Conflating the two was a live drafting error in plan-059 and is recorded here
so the next reader does not repeat it: pinning severities does not mitigate this at all.

## Related

- #145 (the announcement) · #269 (plan-059) · #264

