---
type: Reference
okf_spec: OKF-PLAN
id: comment-177
description: Drafted upstream comment for #177 (partial — stays OPEN). Records EXP-001's refutation so the next attempt does not rebuild the same inadequate scanner.
---

# Draft comment → #177 (`partial`; **stays OPEN**)

> **`plan-050-james-dixson-d0414b` scoped this in, then DROPPED it on evidence. Recording the
> refutation so the next attempt does not rebuild the same scanner.**
>
> No check ships. What ships is the measurement that says why.
>
> ## What was tried
>
> A static check over `plan.md` that distinguishes a **derivable** numeric target in a Success
> Criterion from a **fixed literal** — the thing this issue asks for.
>
> ## Why it was dropped: the control green-lights its own motivating instances
>
> Two measurements, both on the live corpus:
>
> 1. **The first scanner's own figures were wrong, and are retained here as the error rather
>    than deleted.** It reported "6 numeric targets in 101 SC rows". A repaired filter counts
>    **167** SC rows over `docs/plans/*/plan.md` at `fb79b44` — the original denominator was a
>    large undercount, so every rate derived from it was meaningless.
> 2. **The successor check PASSES both cases this issue was filed about.** A
>    citation-presence check — "a numeric target must cite where it came from" — was built and
>    run against `plan-049`'s **SC23 and SC31**, the two criteria that motivated the issue. It
>    passes both. A control that green-lights its own motivating instances is a control that
>    ships unable to fail.
>
> The underlying reason is not an implementation gap: **derivability is not decidable from the
> document alone.** `81` is textually identical whether it was measured or guessed. Nothing in
> `plan.md` distinguishes them, and no static reading of that file can.
>
> ## What the tractable form looks like
>
> A **producer-side citation contract** — the plan is required to record, at authoring time,
> where each numeric target came from — rather than a consumer-side detector inferring it
> afterwards. That is a different deliverable with its own design, and it is not what this
> issue currently asks for.
>
> This issue stays **OPEN** with that reframing. Full finding:
> `docs/plans/plan-050-james-dixson-d0414b/findings/exp-001-target-derivability.md`.
>
> Related and now closed by the same plan: `#178` (the grant generator), `#179`, `#180`,
> `#181`, `#186`, `#187`.
