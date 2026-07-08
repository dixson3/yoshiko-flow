# Upstream Issue Triage: lifecycle-integrity hardening

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #69 — yf-plan: enforce a 'ready-for-approval' gate — re-run red-team after major revisions + complete portability audit before offering for approval

> ## Summary

yf-plan should not offer a plan for operator approval until it is genuinely *ready*. Two gates
must be **complete and green** before the approval prompt, and \"ready-for-approval\" should ...

**Disposition:**
**Notes:**

## #73 — yf-plan: cascade-close epic/child beads on plan completion
Labels: type::task, priority::medium
> ## Problem

When a plan reaches `Status: complete`, closing the plan (or the plan molecule) does **not** cascade closure to open epic/child beads. Leaf tasks get closed during execution, and the top-l...

**Disposition:**
**Notes:**
