---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: README layout contract standardization and backfill

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #315 — Plan 1/3: standardize the README + code-adjacent documentation layout contract and backfill all 20 skills
Labels: type::task, priority::high
> > **Plan 1 of 3.** Split from a website/docs realignment audit that proved too large for one
> plan. Siblings: OKF corpus backfill, and user-facing documentation regeneration. This is the
> first to e...

**Disposition:**
**Notes:**

## #291 — yf-drift-check edge over the escape/stop taxonomy — #145's announced mitigation does not exist

> > Filed by plan-059 Issue 2.7 (`yf-judgement`), which found this mitigation announced but never
> built. Source bundle: `docs/plans/plan-059-james-dixson-55137e/`.

## The gap

`#145` announces a `yf-...

**Disposition:**
**Notes:**

## #273 — The command-vs-obligation law: prose naming a COMMAND is followed more reliably than prose naming an OBLIGATION — one mechanism behind #264, #270, #145's finding 4, and retrospective_fields.py

> > Measured by EXP-001 of plan-059 (`yf-judgement` design) and elevated to its own artifact because
> **it is not about `yf-judgement`**. Source:
> `docs/plans/plan-059-james-dixson-55137e/findings/fin...

**Disposition:**
**Notes:**

## #247 — Drift findings no edge covers: the manifest's own diagram is 22 edges stale, and install.sh/install.py do not exist

> ## Summary

plan-054's full 52-edge drift sweep surfaced findings that **no declared edge covers**. Each is
a gap in the manifest itself, not a failing edge.

### 1. The manifest's own diagram is 22 e...

**Disposition:**
**Notes:**

## #244 — README-contract drift: e-readme-layout fails 16/19 skills, and the manifest contract is stronger than anything enforcing it

> ## Summary

A full 52-edge `yf-drift-check` sweep at `dd9adc2` (plan-054 Issue 6.6) found **three
README-contract edges failing across 16 of 19 skills**, all pre-existing.

| Edge | Failing | Detail |...

**Disposition:**
**Notes:**

## #149 — M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
Labels: type::task, priority::high
> Filed from research 004 (docs/research/004-plan-process-defect-mining, epic yf-mol-fsp, commit 2adad77).

Two defect classes that share one root cause: a step with no exit code is not a step.

M9 (ran...

**Disposition:**
**Notes:**

## #127 — web/concepts: define idiomatic workflow terms (pouring beads, landing the plane, red-team, etc.)
Labels: type::task, priority::low, docs, web
> In the Concepts material, explain the idiomatic workflow vocabulary: 'pouring beads', 'landing the plane', 'red-team', and other recurring workflow-step terms. A glossary a cold reader can use to deco...

**Disposition:**
**Notes:**

## #104 — web: prevent runaway Pelican devservers + add clean teardown (port naba#21)

> ## Problem

The Pelican `-lr` (listen + autoreload) devserver leaks runaway processes. Two failure modes, both observed in sibling repos:

1. **Orphaned workers.** When the shell/session that ran `mak...

**Disposition:**
**Notes:**
