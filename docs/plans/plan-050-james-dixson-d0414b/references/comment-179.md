---
type: Reference
okf_spec: OKF-PLAN
id: comment-179
description: Drafted upstream comment for #179 (include, close)
---

# Draft comment → #179 (`include`; closes with this comment)

> **Fixed in `plan-050-james-dixson-d0414b`.**
>
> `REQ-PLAN-077` — `plan_manager.py resolve-start-gate <plan-dir>` resolves the start gate
> **and closes its wrapper task in the same step**, with a **generated** `close_reason`.
> `SKILL.md` §5.2a now calls it instead of a bare `bd gate resolve`.
>
> ## The defect was universal, not intermittent
>
> Measured across the live bead DB while building the fix (`EXP-002`): **49 of 49** wrapper
> beads ever produced by the `plan-execute` pour were closed **by hand**, with **29 distinct**
> improvised `close_reason` values. The modal reason accounts for 10 of the 49. That is not a
> flaky defect — it is a manual step performed every single time, re-improvised each time,
> with no mechanism and no exit code.
>
> The mechanism, for the record: the formula's one `type = "gate"` step expands into **two**
> beads — the gate, and a wrapper **task** that entry issues take as a `--deps` predecessor
> because `bd` rejects a task blocking an epic. `bd gate resolve` closes the gate. Nothing
> closed the wrapper. `close_cascade.py` then fail-louds on a non-terminal child under the
> molecule.
>
> ## The fix is at the pour/resolve seam, NOT in the cascade
>
> `close_cascade.py` was reporting correctly, so weakening `_bead_is_terminal` would have
> silenced a true fail-loud — the "succeeds visibly while doing nothing" class. Both halves
> are verified:
>
> - **structurally**: `git diff main -- skills/yf-plan/scripts/close_cascade.py` is empty, so
>   the whole file — `_bead_is_terminal` a fortiori — is byte-unchanged;
> - **behaviourally**: a negative control, `neg-179-open-wrapper`, pours a molecule, resolves
>   only the gate, and asserts `close_cascade.py` still exits non-zero on the genuinely open
>   wrapper. Run **before and after** the fix; exit 2 both times.
>
> ## Two implementation notes that cost real time
>
> - The wrapper is found by **parent edge, never by id prefix**. The pour allocates it a
>   *sibling* id (`yf-mol-jws`, not `<epic>.N`), so a prefix scan finds nothing and reports
>   success on an empty set.
> - The gate is taken from the wrapper's own `blocks` dependency, not by title: `Gate: human`
>   is the formula's generic title and would match any human gate under the same epic.
>
> ## "Generated" means derived, not constant
>
> The reason names the resolved gate and the plan and cites `REQ-PLAN-077`. A constant string
> would have ended the 29-way variance while carrying no more information than the variance
> did, so the control asserts the derivation rather than non-emptiness.
>
> Measured: `ctl-179-wrapper-close` 1 → 0 (pre-fix: `Error: No such command
> 'resolve-start-gate'`). Recorded in
> `docs/plans/plan-050-james-dixson-d0414b/assets/red-prework.md`, with the negative control's
> two arms in that bundle's `assets/neg-179-observations.md`.
