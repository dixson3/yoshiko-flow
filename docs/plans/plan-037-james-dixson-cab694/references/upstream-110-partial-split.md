---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #110 — partial split (drafted by Issue 3.7)

Drafted at Issue 3.7; **posted at the authorized reconcile step (§6.3)**, not by the issue
itself. #110 stays **open**.

## Comment to post on dixson3/yoshiko-flow#110

> **Partial delivery — plan-037.** plan-037 delivered the **skill surface** of this issue and
> deliberately left the primitive it actually proposes open. Recording the split so the remaining
> scope is unambiguous.
>
> **Delivered — the `yf-herdr` skill.** A first-class repo skill (`skills/yf-herdr/`) that
> delegates an *already-approved* `yf-plan` or *already-gated* `yf-research` project to a new
> herdr tab running a fresh session of the **same agent kind**, then observes that subordinate and
> mines its deviations for defects in the planning workflow. Concretely:
>
> - `skills/yf-herdr/{SKILL.md,README.md,SPEC.md}` — trigger contract (four conditions, checked in
>   order), launch procedure, the turn-boundary observation contract, and the deviation taxonomy.
>   Requirements are `REQ-HERDR-001..041`.
> - Registered in the root macro spec's §4 catalog (spec key `HERDR`, group `utility`), the frozen
>   install-parity golden, the project README index, and an authored page at `/skills/yf-herdr/`.
> - Uses `herdr agent list` to resolve the parent's agent kind and `agent_status` to observe the
>   subordinate — i.e. it *consumes* `herdr agent *` for a single, one-deep delegation.
>
> **Still open — the `herdr agent *` fan-out primitive.** What this issue proposes is broader than
> one delegation: coordinator loops dispatching work to **secondary full sessions** instead of
> in-process subagents. `yf-herdr` does not do that. It launches **at most one** subordinate per
> plan or research project and refuses a second — two sessions racing one bead DAG is a corruption
> hazard, not a parallelism win (REQ-HERDR-014). Generalizing to N secondary sessions needs a
> different mechanism than the one shipped here: bead-level work partitioning, a claim protocol
> that survives multiple writers, and an answer to what happens when two sessions land on the same
> branch. None of that was in plan-037's scope.
>
> Keeping this issue **open** for that primitive.
>
> Plan: `docs/plans/plan-037-james-dixson-cab694/`.

## Why this is a `partial`, not an `include`

The plan's Upstream Issues table records #110 as **partial** for exactly this reason: the skill
surface and the fan-out primitive are separable, and only the first was built. Closing #110 on the
strength of the skill import would silently discard the larger request.
