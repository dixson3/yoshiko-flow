# exec-001 — an INHERITED FAST/FULL-tier red, measured at Epic 0

**Status:** open at Issue 0.3; resolved by Issue 3.3.
**Class:** the R2 landing hazard, instantiated. Not caused by this plan.

## What

`uv run _shared/test_doc_lint.py` — the `doclint-tests` recipe row, present in **both** the
FAST and the FULL tier — fails on:

```
FAIL SC41: `criteria-cells-filled` has a measured blast radius of 0 over the corpus
           — {'criteria-cells-filled': 1, 'upstream-cells-filled': 5, 'gate-completeness': 1}
```

The single firing bundle is **`plan-069-james-dixson-9d2878`**: its `## Success Criteria` table
carries the header and alignment rows and **zero data rows**, with no declared absence. The
check's own message states the reason a zero-row table is a finding rather than a pass — *"a
table with no rows satisfies every column and id check while asserting nothing."*

## Why it is inherited, and how that was established

`git diff --stat 42bb27dd -- docs/plans/plan-069-james-dixson-9d2878/` is **empty**: the bundle
is byte-identical to the recorded execute base (`assets/execute-base.txt`). It landed in
`f437289 plan-069: seed Plan B of the landing-chain split`, one commit before this plan's base.
So the red exists **on `main`** and is reproducible there; nothing in Epic 0 or Epic 1 caused it.

The `landing.md` FAST-tier probe is what surfaced it: `spec/landing.md`'s §3 trigger scope
routes to `doclint-tests`, so the first SPEC edit of this plan ran a checker whose input is the
**whole plan corpus** rather than the changed file.

## Why it matters to THIS plan specifically

It is **R2 made concrete**. `land`'s **L3** runs `validate-merged` at the **FULL** tier and
**halts with the lock held** on fail. A red that lives on `main` is therefore a guaranteed L3
halt for this plan's own landing — and for plan-069's after it — regardless of whether this
plan's own work is green.

This is precisely the shape the plan's R2 row predicts: *"the two most recent commits on `main`
are both plan-066 landing halts."* The mechanism differs (a corpus checker rather than the
close chain) but the consequence is identical: the landing route is blocked by state the plan
did not create.

## Disposition

**Fixed at Issue 3.3, not here.** Issue 3.3 already owns verifying plan-069's `plan.md` text
against the eight relocated items, so it is the issue that legitimately edits that file; adding
the declared-absence note in Epic 0 would put a plan-069 bundle write inside a SPEC-first epic
that has no other reason to touch it.

The fix is the one the check names: declare the absence, or seed the criteria. plan-069 is at
`status: scoping`, so a **declared absence** is the honest form — its Success Criteria are
genuinely not yet written, and saying so is different from leaving a table that asserts nothing
while passing every column check.

## Boundary, stated rather than implied

Two other checks fire on the corpus at non-zero radius and are **expected**, asserted by the
same test as non-zero: `upstream-cells-filled` at 5 (all the zero-row shape) and
`gate-completeness` at 1 (plan-006's `### Reconcile Gate` / `- Not needed` idiom, which
plan-049 Issue 3.2 decided explicitly **should** fire). Neither is a regression and neither is
this plan's to change.
