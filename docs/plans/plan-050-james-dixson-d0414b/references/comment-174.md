---
type: Reference
okf_spec: OKF-PLAN
id: comment-174
description: Drafted upstream comment for #174 (partial — stays OPEN)
---

# Draft comment → #174 (`partial`; **stays OPEN**)

> **`plan-050-james-dixson-d0414b` closed one named sub-case and produced direct evidence for
> the rest. The general falsification pass stays open.**
>
> ## The sub-case that closed
>
> `#177` — *is a numeric target derivable from the plan's own scope rules?* — was scoped in and
> then **dropped on evidence**. The falsification was the deliverable: the proposed check
> **passes both cases the issue was filed about**, and the first scanner's own denominator was
> wrong by a factor of 1.65. See the comment on `#177`.
>
> That is what this issue asks for, applied once, by hand.
>
> ## The evidence for why the general pass is still needed
>
> The same plan's execution produced **three defects that reading did not find and running
> did**, after thirteen review cycles and eleven independent red-team passes:
>
> | | What was believed | What running it showed |
> | :-- | :-- | :-- |
> | `RE-005` | the driven-red harness works | a **missing fixture** reported `RED observed` and exited **0** |
> | `RE-007` | `#180` is a violable ordering constraint | it is **not violable**; the defect is an `inconclusive` + exit 0 that nothing read |
> | `RE-009` | the new grant generator is correct | it was wrong **twice**, in the direction that looks conservative |
>
> All three were caught by a control that was **executed**, and two of them by an arm that
> exists only because a criterion demanded a *contrast* — an assertion that something must
> still **pass**, not just fail.
>
> The generalisable observation: the reviews that missed these were reading artifacts for
> *structure*, and every one of the three was a defect in *payload* — what the thing does when
> run. That is `#188`'s blind spot, stated from a second direction, and it is why the pass this
> issue proposes should be **executable rather than a reading protocol**.
>
> Adjacent: `#173` (the cross-check class) and `#188` / `#190`.
