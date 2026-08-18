---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: autonomous execution and review, frontloaded gates, retrospective capture

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #110 — herdr: leverage `herdr agent *` to launch and monitor agent sessions from a primary session

> ## Summary

herdr (terminal multiplexer for coding agents) exposes a socket API over its CLI that lets an agent running *inside* a herdr pane create panes, launch other coding agents into them, submit...

**Disposition:** include
**Notes:** IN: the child->parent push channel, the parent handle handoff, and the mandatory autonomy contract (exp-005 verified all three live) -- Epic 5. OUT, and now tracked separately as #163: dispatching bead work to secondary sessions of other harness kinds. exp-005's own limit is the blocker -- the queuing that makes the push channel safe is Claude Code TUI behavior, not herdr's, and a non-claude --kind is untested. Disposition is include rather than partial because #110 AS FILED is satisfied by what landed plus what #163 now carries: the work is not dropped, it is relocated.

## #113 — yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)

> ## Observation

Across `d3-pxe` plan-013, four real defects were found in review. **All four are the same class**, and one escaped every pass:

| Found by | Defect |
| :-- | :-- |
| Conformance | Issu...

**Disposition:** exclude
**Notes:** Adjacent but distinct: #113 wants a PLAN-phase review pass; D-4's sweep is an EXECUTE-start precondition check. Different phase, different mechanism. The sweep reduces one class of what #113 targets without delivering it.

## #145 — New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

> > **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-r...

**Disposition:** partial
**Notes:** IN: the EMIT side only -- plan-retrospective.md, its schema, and the write sites (D-6/D-6a). Answers #145's own Open question 1. OUT: escape-rate measurement, adjudication, the fix+prevention contract, the frontloading consumer, and the DRIFT-CHECK.md yf-plan <-> yf-retrospective taxonomy edge (exp-004 item 5) -- a consumer built now would read an empty corpus. Epic 4.

## #149 — M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
Labels: type::task, priority::high
> Filed from research 004 (docs/research/004-plan-process-defect-mining, epic yf-mol-fsp, commit 2adad77).

Two defect classes that share one root cause: a step with no exit code is not a step.

M9 (ran...

**Disposition:** partial
**Notes:** IN: its thesis applied to this plan's own surface -- every stop becomes mechanical (D-3's counter, D-4's test_class, D-8's postcondition checks, and the pass-1 fifth stop class). OUT: the discovered-from remediation-edge work across the bead corpus. Epics 2, 3.
