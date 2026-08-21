---
type: Reference
okf_spec: OKF-PLAN
id: comment-180
description: Drafted upstream comment for #180 (include, close) — carries the CORRECTED defect shape
---

# Draft comment → #180 (`include`; closes with this comment)

> **Fixed in `plan-050-james-dixson-d0414b` — and the diagnosis in this issue was wrong.**
>
> Read the correction first, because the fix that shipped is not the fix this issue asks for.
>
> ## The original diagnosis was refuted by its own control
>
> This issue — and `plan-050`'s own plan document, through thirteen review cycles and eleven
> independent red-team passes — describes `close-reconcile-step` as **able** to close the
> reconcile bead ahead of the Reconcile Gate, i.e. a violable ordering constraint that needed
> enforcing.
>
> It is not violable. `bd` itself refuses:
>
> ```
> cannot close <bead>: blocked by open issues [<gate>] (use --force to override)
> ```
>
> That was measured while building `ctl-180-chain-order`, the control this fix ships with. The
> control was written to observe the ordering being violated; it could not observe that,
> because the ordering cannot be violated.
>
> ## What the defect actually is
>
> One layer up, and worse than the filed version:
>
> 1. `close-reconcile-step` discovered the refusal **accidentally**, deep inside its own close
>    attempt, and reported it as `verdict: "inconclusive"` with **exit 0**.
> 2. `SKILL.md` §6.4 captured the verb as `RSTEP=$(… close-reconcile-step …)` and **only
>    echoed it** — `$?` was never read.
>
> So an ordering violation produced a soft, non-halting "could not close" that nothing looked
> at, and the §6.4 chain walked on to cascade-close and `update-status complete` **with the
> reconcile step still open**. An accidental refusal reported softly is not an assertion.
>
> ## The fix — both halves, because either alone is vacuous
>
> - **`REQ-COMPLETE-004`** (`skills/yf-plan/spec/phases.md`): `close-reconcile-step` asserts
>   gate-before-close **explicitly, first**, returning `verdict: "fail"` and a **non-zero**
>   exit, and closing nothing. It is `REQ-COMPLETE-001` constraint 2 made mechanical.
> - **The caller**: `SKILL.md` §6.4 now captures `RSTEP_RC=$?` and FAIL-LOUDs on non-zero.
>
> Shipping only the first would have been the same defect in its second form — a step whose
> exit code nothing reads. `test_reconcile_step_resolution.py` asserts **the caller** as well
> as the verb (`test_skill_md_reads_the_close_reconcile_step_exit_code`), plus the
> unresolved-gate halt and its contrast arm: 14 tests, up from 11.
>
> ## Measurement
>
> `ctl-180-chain-order`, against a throwaway beads repo with a real `plan-execute` pour:
>
> | | exit | verdict | reconcile bead |
> | :-- | --: | :-- | :-- |
> | before | **0** | `inconclusive` | left open, silently |
> | after | **1** | `fail` | left open, loudly |
>
> Both observations are recorded in
> `docs/plans/plan-050-james-dixson-d0414b/assets/red-prework.md`.
>
> ## Why this correction is in the comment rather than quietly dropped
>
> The plan's control refuted the plan's own diagnosis, and that is the plan working — it is
> what "observe the control RED before trusting it GREEN" is for. Recording only "fixed" would
> have left a false account of the bug on this issue, false in a way that reads as correct.
> The correction is recorded as `RE-007` in
> `docs/plans/plan-050-james-dixson-d0414b/plan-retrospective.md`; `plan.md` itself was
> deliberately left unedited, since it is approved and its fingerprint is execution
> eligibility.
