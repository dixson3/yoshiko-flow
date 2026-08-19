---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: document-conformance engine instantiation, corpus normalization, enforcement binding

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #62 — Propose yf-spec skill: build & manage specifications; yf-plan SPEC-first integration

> ## Proposal

Introduce a new **`yf-spec`** skill dedicated to building and managing specifications (the `SPEC.md` requirements surface: `REQ-*` ids, testable/non-testable classification, the living-am...

**Disposition:** deferred
**Notes:** D-1: deferred with #165. Proposes a whole yf-spec skill.
## #113 — yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)

> ## Observation

Across `d3-pxe` plan-013, four real defects were found in review. **All four are the same class**, and one escaped every pass:

| Found by | Defect |
| :-- | :-- |
| Conformance | Issu...

**Disposition:** partial
**Notes:** The grammar widening is its precondition — the DAG becomes machine-readable. The walk itself is out of scope.
## #135 — yf-plan: a measured literal in plan.md goes stale when the plan is inside its own measured corpus

> ## The pattern

A plan states a **measured number** as a literal in `plan.md` — a baseline, a corpus count, a signal count, an expected test tuple. The number then goes stale, because the corpus it wa...

**Disposition:** deferred
**Notes:** D-1: deferred — was plan-047 Issue 7.3, inside the descoped Epic 7.
## #140 — yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model

> ## Summary

`yf-plan` and `yf-research` bundles are OKF-shaped **only at the root**. `index.md` / `log.md` exist at the bundle root and nowhere below it, so every subdirectory requires a full content ...

**Disposition:** deferred
**Notes:** D-13: the migration work moves to plan-049.
## #145 — New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

> > **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-r...

**Disposition:** exclude
**Notes:** Adjacent; own plan.

## #149 — M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
Labels: type::task, priority::high
> Filed from research 004 (docs/research/004-plan-process-defect-mining, epic yf-mol-fsp, commit 2adad77).

Two defect classes that share one root cause: a step with no exit code is not a step.

M9 (ran...

**Disposition:** deferred
**Notes:** D-13: the enforcement binding moves to plan-049.
## #164 — CHANGE-VALIDATION: `skills/*/SPEC.md` maps to `uv-herdr-launch`, so every skill's SPEC.md runs yf-herdr's launch test

> Follow-on from plan-045 (#162). Observed during execution; deliberately not fixed in-plan.

## The mapping

`CHANGE-VALIDATION.md` §3 carries:

```
| `skills/*/SPEC.md` | `uv-herdr-launch` |
```

That...

**Disposition:** exclude
**Notes:** Already fixed by plan-047 Issue 3.3.

## #165 — SPEC `Verification:` lines are prose shaped like commands — a FULL tier can be all-green while a spec's own stated verification is false

> Follow-on from plan-045 (#162). Observed during execution; the specific instance was fixed, the class was not.

## What happened

plan-045 Epic 6 reported a green final sweep, measured: `cargo test` 4...

**Disposition:** deferred
**Notes:** D-1: deferred. Different artifact axis — 226 SPEC clauses with their own grammar.

## #171 — yf-okf: nested index.md generation, deferred behind a `description:` producer change (plan-046 D-9)

> Filed by plan-046 Issue 5.5(iv). This is the **deferred half of #140**, filed upstream so the deferral is visible to the issue tracker and not only to `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` §9a.

R...

**Disposition:** exclude
**Notes:** Blocked behind a `description:` producer change; not this plan.
## #172 — yf-plan README.md File Layout block is stale — 29 omissions including SPEC.md, OKF-EXTENSION.md, and test-harness/

> Split out of #118 by plan-046 Issue 5.4. Same file, different defect — folding it into #118 would have made #118 unreviewable.

#118 was about `README.md` still naming `README.md` as the plan-folder o...

**Disposition:** include
**Notes:** README File Layout block, 29 omissions. A conformance instance the doc-type work touches anyway.
## #173 — yf-plan: success criteria and upstream dispositions are never checked against the engine that enforces them

> Filed from plan-046 execution, at operator instruction: **record, do not fix**.

## Two concrete defects, one family

### 1. A plan instruction contradicted the engine that enforces it

plan-046 Issue...

**Disposition:** partial
**Notes:** Defect 2 (bolded disposition fails OPEN) is mechanical and ships here (D-6). Defect 1 needs a prose read against `_verify_row` — that is #174. Stays OPEN per its own final comment.

## #174 — yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it

> **Proposes the mechanism for the defect family #173 diagnoses.** #173 records *what went wrong and why five red-team cycles missed it*, under an explicit "record, do not fix" instruction. This issue p...

**Disposition:** partial
**Notes:** #173's structural joins are a subset. The falsification pass and the criterion↔engine matrix stay open.
## #175 — plan-047: mechanically parseable yf artifact documents — templates, linters, normalizer, extractor

> Coarse tracking issue for **plan-047** (precedent: #167 for plan-046, #134 for plan-039).

**Bundle:** `docs/plans/plan-047-james-dixson-dec9ff/`

## Objective

Make yf artifact documents mechanically...

**Disposition:** supersede
**Notes:** plan-047's coarse tracker. Closed once plan-048's own tracker exists and links it (D-2).
