---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #149 - M5/M9: process rules that nothing executes, and
  remediation edges that exist only in prose'
---
# Upstream #149: M5/M9: process rules that nothing executes, and remediation edges that exist only in prose

- **Number:** 149
- **Title:** M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::high

## Body

Filed from research 004 (docs/research/004-plan-process-defect-mining, epic yf-mol-fsp, commit 2adad77).

Two defect classes that share one root cause: a step with no exit code is not a step.

M9 (rank 1) — the remediation relationship exists only in prose. 0 of 53 discovered-from bead edges connect two plan epics; no commit anywhere in the 5-repo corpus names a prior plan as the source of a defect it fixes; every remediation pair confirmed by the research was confirmed from Motivation prose. Consequence: a plan whose author did not write down that it was fixing a predecessor is invisible to every method available, so no prevalence rate over the plan corpus is computable. This is simultaneously the top-ranked defect and the hard recall bound on the research that found it. Evidence: 4 of 4 measurable repos, 5 of 5 clusters, high confidence. Near-miss precedent: evri_py plan-004 carries a hand-written **Predecessor:** frontmatter field, but 'predecessor' does not distinguish fixes from follows.

M5 (rank 2) — prose-only enforcement does not bind. A written rule that nothing executes is UNRELIABLY obeyed (not deterministically broken: the same prose reconciled correctly for two other plans, so the variable is agent diligence), and no exit code records the skip. Named instances in 2 of 4 measurable repos (yoshiko-flow, d3-pxe): a reconciler step that existed and was ignored, a plan violating a rule it had itself just written, a repo convention a plan hand-rolled around. Plus a corpus-wide mechanical absence: a stuck-bead sweep specified in yoshiko-flow and recorded as firing in no bundle in any repo. Note the honest scoping — this was restated from a claimed 5 repos to a demonstrated 2 after red-team MF-3; it ranks second on CLUSTER breadth (5 of 5), not on repo generality.

Why they are one issue: M9 is M5 applied to the process's own bookkeeping. Both are cases where the system relies on a human or agent remembering to write something down, with no mechanical artifact and no verdict.

Corroboration: research 003 reached the M5 root independently by a different method (architectural audit rather than defect mining), concluding REQ-AGENT-046 is a prose contract whose Verification clause is a documentation check with no test asserting it fires. 004 upgrades that from observation to measured recurrence.

Owning surfaces named by the research:
- M9 → bundle schema / plan_manager.py; yf-okf
- M5 → yf-plan gate model; yf-change-validation (exit-code verdict); the always-loaded rules surface

NOT a recommendation to add another review pass. The corpus's better-evidenced positive is M11: a capability probe or spike placed BEFORE the work that depends on it, with a pre-registered risk and a written response (4 repos, 4 clusters).

Full report: docs/research/004-plan-process-defect-mining/Summary.md
Red-team critique (9 MUST-FIX, all applied): artifacts/critique.md

---

## Worked example, observed live (2026-08-17)

An unplanned instance of M5, produced by the session that filed this issue, roughly twenty minutes after filing it. Recorded because it is a complete instance with all three parts present — the prose step, the missing exit code, and the silent non-firing.

**The step.** While pushing two beads upstream, the agent wrote a wait-loop to block until the push finished:

    until grep -qE "Push complete|error|Error" "$OUTPUT"; do sleep 3; done

**What actually happened.** The push failed. GitHub returned HTTP 503 and the skill fail-closed, writing:

    HTTP 503: No server is currently available to service your request.
    FAIL-CLOSED: yf-nl8i: gh issue create failed: command failed (1): gh issue create ...

**Why the step did not fire.** The failure text says "failed". The guard matched "Push complete", "error", and "Error" — none of which appear. The condition could never become true, so the loop slept and grepped every 3 seconds indefinitely. It ran ~7 minutes and was found only because a human asked "is there something still running in the background", then stopped via TaskStop.

**Why it is M5 and not an ordinary bug.** The guard is a rule expressed as a string-match assertion about vocabulary the author never checked against a real failure. It has no exit code and no negative control: it was never run against a failing push, so nothing could reveal that its failure branch was unreachable. It "succeeded" in the only sense available to it — it did not crash. This is the same shape as the report's headline: a step with no exit code is not a step.

**Why it is also M2a (blind gate) and M1 (succeeds visibly while doing nothing).** The loop is a gate whose evidence it cannot see, and a check that consumes wall-clock time while verifying nothing.

**Cost.** Low in this instance and stated exactly, because the report's discipline is that cost is only reported where evidenced: one idle shell for ~7 minutes. No data loss — the push result was read directly from the output file, and the successful retry (#152, #153) was a separate command. The counterfactual cost is the point, not the actual: had the loop been the thing gating a destructive follow-on rather than a convenience wait, an unreachable failure branch would have meant a hang instead of a halt.

**What would have caught it.** Not another review pass. A negative control — running the guard once against a known-failing input — which is precisely the practice the report found in yoshiko-flow plan-039 (reviewers ran the criterion, reported its exit code, and demanded a negative control) and the M11 positive it recommends: exercise the check before depending on it.

**Provenance note.** This example is first-party and self-reported by the agent that caused it; it is a demonstration of the class, not additional evidence of its prevalence. It does not change any count in the report, which remains 2 named repos for M5.
