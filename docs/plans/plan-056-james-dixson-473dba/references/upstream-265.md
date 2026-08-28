---
type: Reference
okf_spec: OKF-PLAN
description: "Upstream issue #265 — CRITICAL: recheck-criteria reports PASS when criteria were never judged — inconclusive rows are counted in neither bucket"
---
# Upstream #265: CRITICAL: recheck-criteria reports PASS when criteria were never judged — inconclusive rows are counted in neither bucket

- **Number:** 265
- **Title:** CRITICAL: recheck-criteria reports PASS when criteria were never judged — inconclusive rows are counted in neither bucket
- **URL:** https://github.com/dixson3/yoshiko-flow/issues/265
- **State:** OPEN
- **Labels:** type::bug, priority::critical

> Filed BY this plan's red-team pass 3 rather than found at scoping, so it has no triage entry from
> the initial scan. Body captured verbatim after filing.

## Body

Plan: plan-056-james-dixson-473dba | Bundle: docs/plans/plan-056-james-dixson-473dba (repo-relative)

`recheck-criteria` is the REQ-PLAN-080 completion gate in yf-plan SKILL.md §6.4 — the step that
re-checks a plan's Success Criteria before it may close. Its aggregate rule counts `inconclusive`
rows in NEITHER `failed` NOR `evaluated`, so a plan whose instruments do not exist closes green.

Measured on plan_manager.py:2945-2969:

    if failed:          -> FAIL, exit 1
    if evaluated == 0:  -> INCONCLUSIVE, exit 2 (warn, never halts)
    else:               -> PASS, exit 0, "all {evaluated} evaluated criterion/criteria hold"

And at :2915, exit 126/127 (command not found / not executable) maps to `inconclusive`.

So ONE criterion that holds is sufficient to produce `verdict: PASS` while every other criterion
was never run. Reproduced in a sandbox:

  1 criterion `true` + 2 criteria naming missing scripts  -> PASS, exit 0
  the same, with the `true` row removed                   -> INCONCLUSIVE, exit 2

The reason string is literally true and reads as though everything passed.

Measured live on plan-056 during its own review: 44 criteria, 37 class-A, 11 evaluated, 26
inconclusive because their instruments do not exist yet. Had the 10 currently-FALSE criteria been
green, the close chain would have reported PASS on 1 of 37 class-A criteria actually judged.

`evaluated_fraction` IS emitted by the engine (0.25 here) and is consumed by nothing. SKILL.md
§6.4 branches on the exit code alone.

This defeats REQ-PLAN-080's own stated rationale — "a criterion is only as good as the last time
something re-ran it" — with a criterion nothing can run. It affects every plan in the repo, and it
is the third shape of the same collapsed-signal class tracked by #263: two facts (a criterion
holds / a criterion could not be judged) sharing one verdict.

Suggested remedy: a class-A criterion that is `inconclusive` AT COMPLETION must not be silently
equivalent to one that holds. Either add a blocking `harness_incomplete` state, or a
`--require-evaluated N` threshold, or fold an unjudged class-A criterion into `failed` at the
completion binding specifically (leaving mid-flight runs advisory).

Found by plan-056 red-team pass 3.
