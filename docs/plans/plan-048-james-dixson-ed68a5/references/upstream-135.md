---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #135: yf-plan: a measured literal in plan.md goes stale when the plan is inside its own measured corpus

- **Number:** 135
- **Title:** yf-plan: a measured literal in plan.md goes stale when the plan is inside its own measured corpus
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## The pattern

A plan states a **measured number** as a literal in `plan.md` — a baseline, a corpus count, a signal count, an expected test tuple. The number then goes stale, because the corpus it was measured over **includes the plan being written**, or because the document grew after the measurement.

Observed **four times in one plan** (plan-039, #134), each caught by a different mechanism, one of them only at execution:

| # | Where | Stated | Actual | Caught by |
| :-- | :-- | :-- | :-- | :-- |
| 1 | Issue 3.2 harness expectation | `FP=2`, `29→12` | `FP=8`, `40→22` | red-team pass 2 (H2) — figures were cumulative for a *different* fix ordering than the plan adopted |
| 2 | SC6 self-test | "returns `standard`" | `ci-release`, 5 signals | red-team pass 2 (H1) |
| 3 | SC6 self-test, **after the fix** | "at most one residual signal" | 3 signals | red-team pass 3 (C1) — the H1 remedy's own prose added new matches |
| 4 | Issue 3.1 baseline | `TP=1 FP=16 TN=0 FN=0`, n=17 | `FP=17`, n=18 | **execution** — the plan joined its own labeled corpus when `deliverable_class` was written at intake §4.1.5 |

Instance 3 is the sharpest: the fix for a stale count **introduced a new stale count**, because the remedy's explanatory prose was itself inside the measured region.

## Why the existing guard did not hold

plan-039 **diagnosed this failure mode and encoded the rule** — Issue 3.2's *"corpus counts are re-derived by the harness, never transcribed"* and risk R10's *"assert properties, not counts, against a document still being edited"*.

It then violated that rule once more, in Issue 3.1, and nothing caught it until execution. The rule existed, was written down in the same document, and did not prevent the fourth instance. That is what makes this a process gap rather than an authoring slip: **prose guidance inside a plan does not bind the plan's other sections.**

## Why it matters

A stale literal makes a deliverable **fail on correct work**. Instance 4 would have had the executor write `assert FP == 16` into a regression harness that correctly measures 17 — a red suite with no way to tell whether the fix is broken or the number is. Under time pressure the natural remedy is to weaken the assertion or tune the fix toward the stated number, which is precisely backwards.

Self-inclusion is not an edge case. Every `yf-plan` plan that measures anything about plans will include itself in the corpus the moment `deliverable_class` is written at intake.

## Suggested directions

Not prescriptive.

- **A red-team checklist item.** *"Does any success criterion or issue state a measured literal? Is the measured population one this plan is a member of, or one this plan's own text is scanned by? If so, is it re-derived rather than transcribed?"* Cheap, and fits alongside the premise check (REQ-AGENT-048) — same family: a number is a measurement whose validity can expire.
- **Mechanical detection.** A conformance check flagging numeric literals in Success Criteria / issue bodies that look like measurement tuples (`FP=`, `n=`, `NN/NN`), asking for a re-derive note. Noisier, but catches what prose does not.
- **A convention** that measured figures live in `findings/` with a date/commit stamp and are *referenced* from `plan.md`, never copied — making the single-source-of-truth structural.

## Related

- #113 — execution-rehearsal. Distinct axis: this is a claim expiring, not a precondition missing.
- #114 — premise verification. **Closest relative:** #114 asks whether a finding is measured or inferred; this asks whether a measurement is *still true*. A measurement can be correct when taken and false when read.

Filed from plan-039 delegation observation ([tracker #134](https://github.com/dixson3/yoshiko-flow/issues/134)).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

