---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: Freeze yf-plan mechanism growth; convert review loop from reading to executing; fidelity metric; subtract unenforced layers

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #395 — `bd mol pour` drops the formula's declared gate type — REQ-DATA-040 verifies a field the poured bead never carries (metadata null on 153 of 232 gates)

> `REQ-DATA-040` cites a declaration `bd mol pour` never carries. Measured while investigating #388 (plan-070 EXP-001).

The `plan-execute` formula's start-gate step declares `[steps.gate] type = "human...

**Disposition:**
**Notes:**

## #392 — META: 'declared in prose, acted on by code' — one class behind #388, #389, #266, #387 and yf-z6xt; the remedy is DERIVED-not-transcribed plus negative controls

> **Thesis:** a large share of this repo's recurring defects sit at one seam — **a fact declared in
prose, acted on by code that never reads that prose.** The two halves drift, and nothing executes
to n...

**Disposition:**
**Notes:**

## #390 — process: an inference recorded as a measurement survived six review passes; and pipeline-masked exit codes produced two false defect claims

> Two small process defects observed while planning and landing plan-068. Both are single instances
with cheap prompt-level fixes; filing together because they share a root — **an unevidenced claim
that...

**Disposition:**
**Notes:**

## #384 — yf-plan: a success criterion can be reported green before its Discharged-by issues have run, and criteria commands are never smoke-run

> Evidence from a live `yf-plan` run (d3-pxe plan-021, 7 epics / 24 issues, 4 red-team cycles). Two related defects in the same class: **a criterion that is green while asserting nothing.**

## Defect 1...

**Disposition:**
**Notes:**

## #364 — recheck-criteria at the completion binding runs without the plan's criteria preamble env — all 12 criteria meaningless: 8 false FAILS and 3 silent false PASSES

> > **Corrected 2026-09-05.** The original filing claimed SC16 was a control that used no preamble
> variable. That was wrong — SC16 uses `$YR`, and so do **all 12** executable criteria. The
> corrected...

**Disposition:**
**Notes:**

## #358 — yf-plan criteria: a success criterion must assert what the PLAN DID, not what the WORLD IS — external-state legs are falsifiable by concurrent fleet sessions

> ## Summary

A yf-plan success criterion can assert a property of the **world** rather than a property of **what
the plan did**. Such a criterion is falsifiable by a third party the plan does not contr...

**Disposition:**
**Notes:**

## #356 — yf-plan criteria: an executable criterion can false-fail on an empty collection, and both-directions validation does not catch it

> ## Summary

An executable success criterion in a yf-plan criteria table can **fail for a reason unrelated to
what it asserts**, and the both-directions validation yf-plan already prescribes does not c...

**Disposition:**
**Notes:**

## #338 — yf-plan red-team runs NO mechanical checker — check_amendment_log and gate_consistency were both missed by review and caught later
Labels: bug
> ## The gap

`agents/red-team.md` instructs the reviewer to run **no mechanical checker**. Grepping it for
every checker name this repo ships returns exactly one hit — an incidental remark about
`doc_l...

**Disposition:**
**Notes:**

## #328 — red-team: apply the measurement-ordering argument exhaustively, not opportunistically (d3-pxe plan-020 RE-002)

> Process finding from **d3-pxe plan-020** (`plan-retrospective.md` RE-002). Filed against yoshiko-flow because the defect is in the red-team agent's reasoning pattern, not in the plan that surfaced it....

**Disposition:**
**Notes:**

## #325 — `gate_consistency.py` returns PASS on gates it cannot evaluate — a vacuous check
Labels: bug
> ## What happened

Run against plan-061's bundle during its drafting, `gate_consistency.py` reported:

```
PASS, gates: 4, findings: []
```

At that moment **two of those four gates were unsatisfiable*...

**Disposition:**
**Notes:**

## #323 — yf-plan red-team: EXECUTE each success criterion at review time — reviewing a criterion is not executing it

> ## The gap

`yf-plan`'s red-team verifies that a success criterion is **well-formed and non-vacuous**. It does not verify that the criterion is **satisfiable**, or that it **survives the plan's own mu...

**Disposition:**
**Notes:**

## #312 — Process-audit stage: amend the poured DAG so the retrospective write, the landing protocol and preflight are BEADS, not paragraphs
Labels: type::feature, priority::high
> ## Summary

Proposal: a **process-audit** stage that runs in conjunction with the bead pour, reviews the
poured DAG, and **amends it** so recurring process obligations — the retrospective write, the
l...

**Disposition:**
**Notes:**

## #306 — The phantom resolution cell: a review Resolutions entry can DESCRIBE an edit that was never made, and guarding the write does not guard the claim about the write
Labels: type::bug, priority::high
> Found three times during **plan-060**'s review cycle, twice *consecutively after a guard was added for
it*. It is [#263](https://github.com/dixson3/yoshiko-flow/issues/263)'s class in the **process la...

**Disposition:**
**Notes:**

## #289 — yf-plan: no instrument compares a plan's cited figures against its own commands' output
Labels: type::feature, priority::medium
> ## The defect

Every measured figure in a `plan.md` is **hand-transcribed** from a command run at authoring time. Nothing re-runs that command and diffs the stated value against its output. A figure i...

**Disposition:**
**Notes:**

## #286 — yf-plan: red-team passes need a CONVERGENCE STANDARD after the first cycles — an open brief on a converged plan manufactures concerns and grows it

> > Measured across two plans in one session (plan-058, plan-059). Filed because the result lives
> inside plan-059's bundle, which is about a different skill, so nothing would ever apply it.

## The me...

**Disposition:**
**Notes:**
