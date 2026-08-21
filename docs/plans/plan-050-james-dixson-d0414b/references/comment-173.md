---
type: Reference
okf_spec: OKF-PLAN
id: comment-173
description: Drafted upstream comment for #173 (partial — stays OPEN)
---

# Draft comment → #173 (`partial`; **stays OPEN**)

> **`plan-050-james-dixson-d0414b` closed two named sub-cases. The general cross-check stays
> open.**
>
> This issue names the class: *success criteria and upstream dispositions are never checked
> against the engine that enforces them.* Two instances of it were closed by that plan, both by
> making the check executable rather than by writing it down:
>
> - **`#178`** — the upstream **grant** and the reconcile **verifier** were two separate prose
>   derivations of the same disposition→end-state rule. They now read **one table**
>   (`UPSTREAM_REQUIREMENTS`), and the shared read is asserted **behaviourally**: mutate one
>   entry in a throwaway copy, re-run both, and assert **both** verdicts change. The structural
>   forms — the table exists, the verifier imports it — were measured as **undetecting**.
> - **`#180`** — a §6.4 chain ordering constraint that existed only in prose now returns a
>   non-zero exit, **and its caller reads it**. The second half matters as much as the first:
>   `SKILL.md` captured the verb and only echoed it, so an exit code added alone would have
>   been unread.
>
> **This issue's own criterion was applied to the plan that cites it.** Each of its success
> criteria was checked against the code that scores it before approval — including
> `verify-reconcile`'s actual aggregate rule, which is why one criterion accepts an
> `inconclusive` verdict for exactly the `tracker` row rather than demanding `pass`. A
> criterion not checked against its scoring engine is this issue's class, inside a plan that
> lists it.
>
> What stays open is the **general** cross-check — a mechanical pass over every criterion
> against every enforcing engine. Two hand-worked instances are not that.
>
> Adjacent: `#174` (the falsification pass) and `#177` (dropped on evidence — see the comment
> there).
