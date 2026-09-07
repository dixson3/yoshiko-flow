---
type: Finding
okf_spec: OKF-PLAN
description: "Evidence for the code-side negative-control convention: TWO measured instances where a control caught a checker defect that reasoning had missed. Both are false greens, and neither was reachable by a doc-side control."
id: negative-control-evidence
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
---
# The code-side negative control has now earned its keep TWICE

## Approach Tested

**measured:** both instances below are recorded from real command output during this plan —
the first during investigation (EXP-001), the second during execution (Issue 2.5). Neither was
predicted by review; both were found by running a control.

## Result

The convention this plan adopted is: **mutate the SOURCE OF TRUTH under docs that PASS, and
require the checker to FAIL.** It is stated in the Approach section of `plan.md` and enforced by
the *Checkers are fail-capable* capability gate. Here is why it is worth its cost.

| # | When | Checker | What the control caught | Why a DOC-SIDE control could not have |
| --: | :-- | :-- | :-- | :-- |
| 1 | investigation, EXP-001 | `check_web_harness_paths` (prototype "checker B") | Returned `PASS (0 mismatches), EXIT=0` against a tree with **15 real defects**. The shared root `.agents/skills` *contains* the harness id `agents`, so a repaired row scanned as `{pi, agents}`, was judged ambiguous, and was **silently skipped**. | The docs were **already wrong** and the checker was **already silent**. Breaking a doc further changes nothing — there was no green state to disturb. |
| 2 | execution, Issue 2.5 | `check_web_harness_paths` (shipped) | With docs repaired to green, retargeting `pi`'s `user_skills_subpath` in `harness_desc.rs` left the checker at **exit 0**. It tested membership in the **union** of every harness's subpaths, so `.agents/skills` was still "a live value" while the docs had become wrong for `pi`. | The mutation is **only expressible on the code side** — the defect is a disagreement between docs and a source of truth that only the source of truth can be moved. |

**Both are FALSE GREENS, and both are on the same checker.** That is not a coincidence about
this one file: it is the shape of the class. A checker that attributes, resolves, or looks up
before comparing has a silent-skip path, and a silent skip is indistinguishable from a pass.

## What instance 2 changed in the shipped code

The fix was not a patch to the control; it was a correction to the checker's **comparison
operator**. It now reads the scope off the path's anchor prefix (`~/` = user,
`<git-root>/` = project) and compares against `desc[harness][user_skills_subpath]` or
`[project_skills_subpath]` — the genuine `(scope, field)` **tuple** the plan's pass-2 C12
mandated. The union test I had written was that same flat-denylist defect in mirror image:
C12 warned against a denylist that matches for the wrong reason, and a union **allowlist**
passes for the wrong reason.

Post-fix: **4/4 checkers OBSERVED TO FAIL**, `pre=0, post=1` on each.

## Implications for Plan

1. **The convention is load-bearing, not ceremonial.** Two for two, and both instances were
   invisible to prose review — including four red-team passes that read the plan closely enough
   to catch two phantom resolutions.
2. **A checker's first green is not evidence.** Neither defect was visible in any output; both
   required constructing a state in which the checker *should* fail and observing whether it did.
3. **Record this in the retrospective as PROCESS evidence** (Class B), not as a content defect.
   It is an argument about how instruments are validated, and it generalizes past this plan.

## Recommendations

Keep the code-side control as the default for any new checker in this repository, and keep the
`--min-checkers` vacuity floor inside the test rather than only in the criterion — a harness that
silently skips a checker is the same failure mode one level up.
