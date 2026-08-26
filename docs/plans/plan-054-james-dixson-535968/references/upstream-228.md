---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #228: Bead provenance does not reach TITLE-BORNE citations (#209's larger class)

- **Number:** 228
- **Title:** Bead provenance does not reach TITLE-BORNE citations (#209's larger class)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Recorded by plan-053 as decision **D-13**, measured by EXP-006. Filed rather than papered over.

## The gap

plan-053 closed #209 by giving every poured issue bead a `plan_dir` metadata key and a
provenance header on its **description**. That reaches the description. It does **not** reach
citations that have migrated into bead **titles** — which is where this repository's newest
bundles actually put them.

## Measured

- This repository's **four newest bundles carry zero non-empty `detail`**.
- **plan-053 is itself such a bundle**: 0 of its 46 issues carried non-empty `detail` at pour
  time.

So plan-053 hit #209 during its own execution, and Epic 6 did not reach it. That is stated in
the plan's own D-13 rather than discovered afterwards.

## What #209's fix DID buy

On a bundle whose `detail` is empty, the provenance header becomes the **entire** description —
so a bead that previously carried nothing now carries its plan id and bundle path. That is a
real gain on an otherwise-blank description. It is simply not the larger class.

## The larger class

Citations living in bead **titles** are unreachable by a description-level remedy. Closing it
needs a decision about where citation content belongs at pour time, which is a design question
rather than a patch.

## Evidence

- `docs/plans/plan-053-james-dixson-4015d3/findings/exp-006-bead-provenance.md`
- `docs/plans/plan-053-james-dixson-4015d3/plan.md` § D-13
- `docs/plans/plan-053-james-dixson-4015d3/assets/deferred-defects.md` § D4

Filed by plan-053 Issue 7.2.

