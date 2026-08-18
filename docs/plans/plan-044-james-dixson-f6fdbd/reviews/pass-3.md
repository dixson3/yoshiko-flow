---
type: Review
okf_spec: OKF-PLAN
id: pass-3
plan: plan-044-james-dixson-f6fdbd
created: '2026-08-17'
verdict: APPROVE
status: resolved
---

# Red-Team Pass 3 — plan-044-james-dixson-f6fdbd

**Date:** 2026-08-17
## Verdict: APPROVE
**Status:** all 5 residual concerns resolved in-plan (no fourth cycle required)

## Pass-2 concern verification (all 8 verified in plan.md text, not merely claimed)

| # | Claim | Verified | Status |
| :-- | :-- | :-- | :-- |
| 1 | D-11 reversed to probe-first | D-11 (`plan.md:154`) reads "PROBED, not guessed"; `SPEC.md:1251-1254` precedent re-read and quoted accurately; `RULE_TARGETS` (`managed_block.rs:345`) still 4 rows, no `agents`. Issue 2.2 genuinely two-branch; 0.1 conditionalized; Criterion 5 reworded | resolved (residual below) |
| 2 | Gate Test = in-place scratch-branch apply | Gate `:419-434`. Underlying facts re-verified: `git check-ignore` → `.git/info/exclude:9:.beads/`, `git ls-files .beads` empty, `docs/plans/` tracked | resolved |
| 3 | 3.7 split into real issues | Both first-class (`:345-358`); `3.7b ← 3.7a`; gate `Blocks: 3.7b`; `3.8 ← 3.7b`. No cycle | resolved |
| 4 | harness-tune.md edit in 2.2 | `:256-260`, citing `doc_agreement.rs:169-184` and `:246` | resolved |
| 5 | D-10 scoped to claude-code + follow-on | D-10 `:153`; Criterion 5; Issue 4.3 `:390-392` | resolved |
| 6 | `embed.rs` as fourth surface | Issue 2.10 `:296-306`; risk row `:448`; `embed.rs:48-50` confirmed | resolved |
| 7 | 4.1 closure widened | `:380`; risk row `:449` | resolved |
| 8 | agents config-verdict declared | `:261-262`, `mod.rs:325` | resolved |

## Strengths

- **Dependency graph clean at 39 issues.** All edges enumerated: every `depends-on` resolves,
  acyclic, and the leaf set is **exactly** `{1.5, 1.7, 1.8, 2.7, 2.11, 3.6, 3.9}` — Issue 4.1's
  closure is precisely right, nothing over- or under-included, 4.3 the sole terminal node. Count
  recounts exactly (7+8+11+10+3 = 39).
- **The 14-bundle gate Test is runnable, for a reason pass 2 did not check.** `_resume_scan`
  (`plan_manager.py:3025-3100`) sets `total = len(descendants)` over *all* statuses. All 14 epics
  are `status: closed`, so `total > 0` after a correct remap is a real signal, not a trap.
- **3.7a's repair scope is correctly narrow.** `beads-skills-mol-*` appears in 24 files under
  `docs/plans/`, including historical records (`plan-040/references/tracker-backfill-map.md`,
  `plan-009/findings/`) that must **not** be rewritten. Scoping to two line kinds excludes them by
  construction, which is what makes `git checkout` a sufficient recovery.
- Issue 2.2's branch point is coherent under both outcomes on the axes that matter (2.3's
  `preflight.rs` fallout, Criterion 5, risk row `:447`).
- REQ-YF-TUNE-020 is already tagged in `yf/src`, so amending it needs no allowlist row — D-7's
  invariant is unaffected by the probe outcome.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| 1 | medium | **The post-probe SPEC amendment is owned in only one of 2.2's two outcomes.** 0.1 conditions the TUNE-020 amendment on the probe, but 0.1 executes *before* 2.2 (`2.2 ← 2.1 ← 0.7 ← 0.5/0.6 ← 0.1`), so the condition is unknowable at 0.1's execution time. Outcome **B** is owned (2.2 edits FLOW-008); outcome **A** is orphaned — adding a `RULE_TARGETS` row requires amending TUNE-020's enumeration (`SPEC.md:1249-1251` lists the three destinations) and no issue owns it. It also pushes a SPEC edit after Epic 0, which SPEC-first forbids without saying so. | Reword 0.1 to "TUNE-020's `agents` row is **deferred to Issue 2.2**"; give 2.2 explicit ownership under **both** branches (TUNE-020 enumeration under A, FLOW-008 wording under B), with the deferral noted in the amendment log. |
| 2 | low | **`upstream-triage.md`'s #156 note still encodes the pre-reversal D-11** — "an `agents` `RULE_TARGETS` row is added first (D-11)". plan.md and the triage file now disagree on a decision the executor reads from both. | Restate as probe-first. |
| 3 | low | **Issue 2.4's five-descriptor assertion is undefined for `agents` under outcome B** — "rules land only on its declared surface" has no referent if `agents` is declared skills-only. | Add the outcome-B form: "no rules file is written anywhere for `agents`". |
| 4 | low | **Two stale cross-references from the pass-2 edits.** Risk row `:453` still cites "(3.7)" after the split. And `git checkout -- docs/plans/` (`:434`) would also discard uncommitted plan-044 bundle edits, since the trial apply happens in the live tree. | Update the citation; scope the recovery command to the 14 bundles, or require plan-044 be committed before the trial apply. |
| 5 | low | **Only `REQ-BUP-062` has a named test home.** Issue 3.1 points it at `test_upstream.py` (which does follow a `# --- REQ-BUP-0NN:` convention — rows for 054/056/057 confirmed). 060/061/063/064 get no equivalent, and exp-006 established the macro gate never reaches `REQ-BUP-*`. | State in 0.3 that each new `REQ-BUP-*` lands a tagged case in `test_upstream.py`. |

## Missing

Nothing structural. All four pass-2 "Missing" items are now present, and the gate instrument is
independently verified runnable.

## Gate Assessment

- **Start Gate** — appropriate.
- **Capability Gate: sandboxed-HOME cross-harness proof** — unchanged and still correct. Condition
  scoped to the three descriptors the test iterates, five-descriptor extension explicitly assigned
  to Issue 2.4. Non-vacuous, reachable, no cycle.
- **Capability Gate: 14-bundle repair dry-run** — both pass-2 defects fixed. Reachability clean
  (Condition keys on 3.7a's output; 3.7a is not itself blocked; `Blocks: 3.7b`). Test verified
  runnable.
- **Reconcile Gate** — standard, and no longer load-bearing now that 4.1 spans all seven leaves.

## Upstream Assessment

Dispositions sound and traceable; the pass-2 residual (three `resolves-upstream` issues outside
4.1's closure) is fully cleared. Only defect is the stale D-11 sentence in #156's triage note
(concern 2). #158's supersede remains correctly gated on a green `cargo test -p yf sync`, and
exp-005 Part B footnote 2 is explicitly and defensibly declined.

**Bottom line:** no high-severity concern remains; graph, gates and criteria are internally
consistent; no success criterion is unmeetable or vacuous. The one medium is a clause-level fix
best folded in before execution rather than a fourth review cycle.

## Operator Resolutions

| # | Concern | Resolution | Status |
| :-- | :-- | :-- | :-- |
| 1 | Post-probe SPEC amendment unowned under outcome A | Applied: 0.1 now **defers** the `agents` TUNE-020 row to Issue 2.2; 2.2 owns the SPEC edit under **both** branches (TUNE-020 enumeration under A, FLOW-008 wording under B), with the deferral recorded in the amendment log. | resolved |
| 2 | Triage #156 note encodes pre-reversal D-11 | Applied: note restated as probe-first, matching D-11. | resolved |
| 3 | 2.4 assertion undefined for `agents` under outcome B | Applied: 2.4 now names the outcome-B form — no rules file written anywhere for `agents`. | resolved |
| 4 | Stale "(3.7)" citation; over-broad recovery command | Applied: citation updated to 3.7a/3.7b; gate Instructions now require the plan-044 bundle be committed before the trial apply, so `git checkout -- docs/plans/` cannot discard in-flight bundle edits. | resolved |
| 5 | REQ-BUP-060/061/063/064 have no named test home | Applied: 0.3 now states each new `REQ-BUP-*` lands a tagged case in `test_upstream.py` under its existing `# --- REQ-BUP-0NN:` convention. | resolved |
