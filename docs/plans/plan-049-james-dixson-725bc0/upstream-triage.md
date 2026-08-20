---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: corpus migration write-phase and enforcement binding

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #140 — yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model

> ## Summary

`yf-plan` and `yf-research` bundles are OKF-shaped **only at the root**. `index.md` / `log.md` exist at the bundle root and nowhere below it, so every subdirectory requires a full content ...

**Disposition:** partial
**Notes:** IN: the readability half. OUT: nested index.md/log.md, the reindex/--fix verb, and the drift model — all route to #171. `include` would repeat the dishonesty #171 was filed to prevent.

## #149 — M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
Labels: type::task, priority::high
> Filed from research 004 (docs/research/004-plan-process-defect-mining, epic yf-mol-fsp, commit 2adad77).

Two defect classes that share one root cause: a step with no exit code is not a step.

M9 (ran...

**Disposition:** partial
**Notes:** IN: M5 (the enforcement binding). OUT: M9 — remediation edges in prose; measured 0 of 53 discovered-from edges connect two plan epics. Issue 4.6 records it.

## #135 — yf-plan: a measured literal in plan.md goes stale when the plan is inside its own measured corpus

> ## The pattern

A plan states a **measured number** as a literal in `plan.md` — a baseline, a corpus count, a signal count, an expected test tuple. The number then goes stale, because the corpus it wa...

**Disposition:** include
**Notes:** D-3, scoped: self-exclusion primary plus one in-flight rule at W. EXP-005 measured a naive check firing 41/41 with 39 correct-behaviour false positives; the scoped form measures 2/2/0.

## #171 — yf-okf: nested index.md generation, deferred behind a `description:` producer change (plan-046 D-9)

> Filed by plan-046 Issue 5.5(iv). This is the **deferred half of #140**, filed upstream so the deferral is visible to the issue tracker and not only to `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` §9a.

R...

**Disposition:** deferred
**Notes:** Blocked behind a `description:` producer change; a separate skill's axis. It is the declared deferred half of #140.

## #113 — yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)

> ## Observation

Across `d3-pxe` plan-013, four real defects were found in review. **All four are the same class**, and one escaped every pass:

| Found by | Defect |
| :-- | :-- |
| Conformance | Issu...

**Disposition:** partial
**Notes:** The residue drops further here and REQ-DATA-043 gives the walk a defined behaviour on unreadable plans. The walk itself stays out.

## #174 — yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it

> **Proposes the mechanism for the defect family #173 diagnoses.** #173 records *what went wrong and why five red-team cycles missed it*, under an explicit "record, do not fix" instruction. This issue p...

**Disposition:** partial
**Notes:** The enforcement binding closes more of the class; the falsify-every-criterion pass stays open.

## #102 — .markdown-lint-on-edit -> .yf/markdown-lint-on-edit: gitignore semantics + migrate.rs rename

> ## Summary
Move the markdown-lint opt-in marker `.markdown-lint-on-edit` → `.yf/markdown-lint-on-edit`, to consolidate under the `.yf/` sidecar. **No compiled code consumes the marker** (grep: zero hi...

**Disposition:** exclude
**Notes:** Unrelated axis.

## #145 — New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

> > **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-r...

**Disposition:** exclude
**Notes:** Adjacent; own plan.
