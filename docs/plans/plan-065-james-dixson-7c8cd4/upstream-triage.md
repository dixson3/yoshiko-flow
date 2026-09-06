---
type: Reference
okf_spec: OKF-PLAN
description: Disposition of each candidate upstream issue, with the reasoning behind
  it — the triage record behind plan.md's Upstream Issues table.
---
# Upstream Issue Triage: Run the yf-okf-hygiene corpus backfill on the repaired engine

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #359 — Plan 2/3 (part 2): run the yf-okf-hygiene corpus backfill — 8 legacy-readme bundles, on the repaired engine

> **Prerequisite: #294 and the plan-064 engine repairs are landed** — commit `30fcbab`,
`plan-064: repair the yf-okf-hygiene backfill/restore engine`. This issue carries #316's
original acceptance crite...

**Disposition:** include
**Notes:** The primary issue. Carries #316's four acceptance criteria verbatim and adds the post-repair halt profile. Every criterion maps to one here: `legacy: 0` -> SC1; `restore` exercised on a real bundle -> SC4; `okf-index-drift` green -> SC3 (STRENGTHENED past the bare check, which measured green today with `no_index: 8`); explicit reporting of untransformable bundles -> SC5.

## #316 — Plan 2/3: run the yf-okf-hygiene corpus backfill — 8 legacy-readme bundles to the reserved index.md + log.md model
Labels: type::task, priority::high
> > **Plan 2 of 3.** Split from a website/docs realignment audit that proved too large for one
> plan. Siblings: #315 (README layout standardization, executes first) and the user-facing
> documentation ...

**Disposition:** include
**Notes:** The parent. #359 is explicitly 'part 2' and carries #316's criteria, so the two close together. Nothing in #316 is left undischarged by this plan.

## #295 — plan-057 follow-on: 8 unresolved backfill halts (SC19) and 4 ungranted reconcile comments (SC24)
Labels: type::task, priority::medium
> ## Deferred from plan-057: two criteria left FALSE by operator decision

plan-057 is `status: complete` at 28 of 30 criteria. The two outstanding are **not defects** — each needs an operator judgement...

**Disposition:** partial
**Notes:** **SC19 only.** #295 bundles two deferred plan-057 criteria: SC19 (these exact 8 backfill halts) and SC24 (4 ungranted reconcile comments). This plan discharges SC19 entirely and touches SC24 not at all, so #295 is UPDATED, never closed. Its D-5 note that the README is richer in plan-010 and plan-013 was independently confirmed by exp-001.

## #362 — yf-okf-hygiene: the _index.md legacy-variant transform route manufactures a hybrid under the yf-plan member
Labels: priority::medium, type::bug, follow-on
> Discovered by plan-064 Issue 4.1/4.5 while making the `backfill` dry run predictive (REQ-OKFH-011).

**Measured, before and after plan-064's changes:**

| legacy index | dry run | apply |
| :-- | :-- ...

**Disposition:** exclude
**Notes:** The `_index.md` legacy-variant route manufactures a hybrid and halts. Verified irrelevant here: **0 of the 8 targets are `_index.md`** (plan-064 EXP-004 measured the population as `{conformant: 61, legacy-readme: 8}`). Blocks nothing; stays open on its own axis.

## #361 — plan_extract.py --strict validates neither self-edges nor cycles in the plan DAG
Labels: priority::medium, type::bug, follow-on
> Red-team pass 4, C34, on plan-064. **Measured during that plan's own drafting**: a `depends-on`
self-edge (an issue declaring itself as its own predecessor) was introduced, passed
`plan_extract.py --s...

**Disposition:** exclude
**Notes:** `plan_extract.py --strict` validates neither self-edges nor cycles. A plan-064 follow-on on an unrelated axis. Its consequence IS felt here - it is why this plan's DAG was checked for self-edges, dangling refs and cycles by hand rather than trusted to `--strict` - but no extractor work happens in this plan.

## #322 — docs yf-okf-hygiene SKILL.md: the "31 legacy, 7 halt" figure reads as repo-agnostic and mis-sized a real plan 3.5x

> ## docs — `SKILL.md`'s "31 legacy bundles, of which 7 halt" reads as repo-agnostic and mis-sized a real plan 3.5x

Measured 2026-08-30 (plan-012, EXP-004).

### The defect

`yf-okf-hygiene/SKILL.md:18...

**Disposition:** exclude
**Notes:** Docs defect: `SKILL.md`'s '31 legacy, 7 halt' figure reads as repo-agnostic. Adjacent but separate; this plan changes no documentation figure. Worth noting the numbers here (8 legacy, 8 halting by default) differ again, which is further evidence for #322's point.
