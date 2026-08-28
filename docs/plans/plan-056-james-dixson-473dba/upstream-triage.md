---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: OKF cluster

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #140 — yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model

> ## Summary

`yf-plan` and `yf-research` bundles are OKF-shaped **only at the root**. `index.md` / `log.md` exist at the bundle root and nowhere below it, so every subdirectory requires a full content ...

**Disposition:** partial
**Notes:** Root-tier enforcement + drift model IN. Nested index.md OUT (re-scoped via #171). Issue stays open: REQ-OKF-CHK-002 (promotion to error-level) has no other tracker home.

## #165 — SPEC `Verification:` lines are prose shaped like commands — a FULL tier can be all-green while a spec's own stated verification is false
Labels: priority::high
> Follow-on from plan-045 (#162). Observed during execution; the specific instance was fixed, the class was not.

## What happened

plan-045 Epic 6 reported a green final sweep, measured: `cargo test` 4...

**Disposition:** partial
**Notes:** One instance discharged: REQ-PORT-010's `Verification:` line becomes an executed CHANGE-VALIDATION row. The general class stays open.

## #168 — yf-okf: projection delivery mode (on-demand OKF export) — #92 carve-out 1 of 3

> Filed by plan-046 Issue 5.5(i) as one of **three named carve-outs** from closing #92 as superseded. #92's emit half shipped natively and its nested-tree half is #140; these three are what a clean clos...

**Disposition:** exclude
**Notes:** Parked by operator decision. Trigger not fired — measured: no consumer anywhere on this machine; bp/docs/plans holds 3 yf bundles but has no AGENTS.md sentinel so no OKF tool can resolve it.

## #169 — OKF conformance gate for yf-research and yf-incubator — #92 carve-out 2 of 3

> Filed by plan-046 Issue 5.5(ii) as one of **three named carve-outs** from closing #92 as superseded.

**What this is.** yf-plan's bundles are conformance-gated: `plan_manager.py audit` runs the OKF en...

**Disposition:** deferred
**Notes:** Parked as filed by operator decision. Measured counter-evidence: yf-research's UNGATED indexes are the corpus's best (3 of 28 bundles supply 32 of 107 unique descriptions) while yf-plan's GATED ones are 57% boilerplate. The gate checks shape; shape is not what makes an index useful.

## #170 — OKF consumer round-trip fidelity is unverified — #92 carve-out 3 of 3

> Filed by plan-046 Issue 5.5(iii) as one of **three named carve-outs** from closing #92 as superseded.

**The gap, stated precisely.** yf demonstrates **producer → producer** fidelity only: it writes O...

**Disposition:** deferred
**Notes:** **Carried whole to plan-057**, which dispositions it `partial` and owns both halves — the untestable write half and the read half evidenced over only ~100 of 1383 concept documents. This plan performs no work on it. (Re-dispositioned at red-team pass 7: this file still said `include` after the D-17 split, disagreeing with plan.md.)

## #171 — yf-okf: nested index.md generation, deferred behind a `description:` producer change (plan-046 D-9)

> Filed by plan-046 Issue 5.5(iv). This is the **deferred half of #140**, filed upstream so the deferral is visible to the issue tracker and not only to `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` §9a.

R...

**Disposition:** partial
**Notes:** Re-scoped. IN: make `description:` a producer contract (currently emergent convention — 0/498 pre-047 vs 133/432 post-047, unstamped and unrequired by any schema). OUT: generating nested index.md; the leverage is per-file entries in the ROOT index, which 6 bundles already demonstrate.

## #173 — yf-plan: success criteria and upstream dispositions are never checked against the engine that enforces them
Labels: priority::medium
> Filed from plan-046 execution, at operator instruction: **record, do not fix**.

## Two concrete defects, one family

### 1. A plan instruction contradicted the engine that enforces it

plan-046 Issue...

**Disposition:** exclude
**Notes:** Filed 'record, do not fix'. Criteria-vs-engine cross-checking is a different axis from OKF structure.

## #174 — yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it
Labels: priority::medium
> **Proposes the mechanism for the defect family #173 diagnoses.** #173 records *what went wrong and why five red-team cycles missed it*, under an explicit "record, do not fix" instruction. This issue p...

**Disposition:** exclude
**Notes:** Review-phase validation pass — separate mechanism, separate plan.

## #189 — Six shipped scripts have no tests at all — including two CHANGE-VALIDATION checks and the beads repair engine
Labels: priority::medium
> ## Summary

Six shipped scripts have **no test file and are referenced by no test anywhere in the repo**. This is the coverage half of the problem; the blind-spot half — suites that exist but assert o...

**Disposition:** deferred
**Notes:** Not this plan's cluster. Taken as a CONSTRAINT, re-aimed after the D-17 split at what this plan actually builds: Issue 1.9's eight harness scripts ship with a RED-fixture selftest (SC35), so they do not become scripts 7-14 of the untested set. (`yf-okf-hygiene` moved to plan-057 with D-2/D-9.)

## #192 — Evaluate a structure-first plan DSL with generated markdown — single source for plan.md, the bead pour, and cross-reference integrity

> ## Idea

Author plan **structure** in a machine-first artifact — YAML or a small DSL — holding epics, issues, dependency edges, gates, criteria, risks and the upstream table with its internal/external...

**Disposition:** deferred
**Notes:** Structure-first plan DSL. Interaction recorded: if #192 is ever pursued, index generation becomes a by-product — which is a further reason this plan re-scopes #171 rather than building nested indexes.

## #233 — yf-plan: audit-close's OKF walk has no fixture carve-out, so pinned negative fixtures fail it
Labels: bug, priority::medium
> Found at **plan-053**'s own close step, by running `audit-close`.

## Measured

```text
Counter({'fail': 26, 'warn': 19})
fail findings NOT in a pinned fixture tree: 1
```

**25 of 26 `fail` findings ...

**Disposition:** include
**Notes:** Subsumed by the doc_lint <-> OKF reconciliation. Its real defect is that the OKF walk has no path-exclusion concept, which doc_lint already solved twice (finding.toml CARVE-OUT 1 and 2).

## #244 — README-contract drift: e-readme-layout fails 16/19 skills, and the manifest contract is stronger than anything enforcing it

> ## Summary

A full 52-edge `yf-drift-check` sweep at `dd9adc2` (plan-054 Issue 6.6) found **three
README-contract edges failing across 16 of 19 skills**, all pre-existing.

| Edge | Failing | Detail |...

**Disposition:** exclude
**Notes:** README-contract drift is a different edge and a different contract.

## #246 — Drift CONFLICTs: REQ-DATA-044 says R* is uniformly W but the schema ships two E close-out checks

> ## Summary

plan-054's full 52-edge drift sweep at `dd9adc2` returned **three CONFLICTs** — cases where the
evidence says the **fixed authority** is the stale side. Per `DRIFT-CHECK.md` §7 these are
r...

**Disposition:** include
**Notes:** A conformance defect INSIDE the doc_lint layer: REQ-DATA-044 declares R* uniformly W while plan-relations.toml ships two E close-out checks. Directly in the reconciliation's path — those two E checks are the only ones that survive status demotion.

## #247 — Drift findings no edge covers: the manifest's own diagram is 22 edges stale, and install.sh/install.py do not exist

> ## Summary

plan-054's full 52-edge drift sweep surfaced findings that **no declared edge covers**. Each is
a gap in the manifest itself, not a failing edge.

### 1. The manifest's own diagram is 22 e...

**Disposition:** partial
**Notes:** IN: its §1 mechanism only — a declared listing with no generator is the same defect as index drift, so one generator/checker serves both. OUT: the rest of the drift residue.

## #265 — CRITICAL: recheck-criteria reports PASS when criteria were never judged — inconclusive rows are counted in neither bucket
Labels: type::bug, priority::critical

> Filed BY this plan's red-team pass 3, not found at the scoping scan — which is why it has no entry from
> the initial triage and is appended here. `recheck-criteria` counts `inconclusive` rows in neither
> `failed` nor `evaluated`, so one green criterion yields `verdict: PASS` while any number go unjudged.

**Disposition:** include
**Notes:** Affects every plan in the repo, not only this one. Fixed here by Issues 0.13 (the `REQ-PLAN-080` amendment) and 1.10 (the engine change), and closed at reconcile by Issue 4.3. Third shape of the collapsed-signal class tracked by #263.
