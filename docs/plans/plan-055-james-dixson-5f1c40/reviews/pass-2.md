---
type: Review
okf_spec: OKF-PLAN
id: pass-2
description: Red-team pass 2 — verdict REVISE, resolution verification plus 17 concerns (8 high)
---

# Red-team pass 2

## Verdict: REVISE
## Resolution verification

Each pass-1 resolution was checked against the **current** `plan.md` text rather than trusted from
the table (the #250 precedent: resolutions recorded as done and never written, twice in one plan).

| # | Claimed | **Actual** |
| :-- | :-- | :-- |
| C1 | resolved | **partially-fixed** — ten criteria call the guard, but see H1/H2 |
| C2 | resolved | **genuinely-fixed** — 4.6, SC14 and the Deferred table are mutually consistent |
| C3 | resolved | **partially-fixed** — table fixed; issue-level annotations were not (H6) |
| C4 | resolved | **fixed-but-introduced-two-new-defects** (H3, H4) |
| C5 | resolved | **partially-fixed + new defect** (H5) |
| C6 | resolved | **genuinely-fixed** |
| C7 | resolved | **partially-fixed** — Issue 0.8 has **zero dependents** (H2) |
| C8 | resolved | **partially-fixed** — 0.3 fixed, **0.5 has the identical defect** (M5) |
| C9 | resolved | **fixed-but-introduced-a-new-defect** (H7) |
| C10 | resolved | **genuinely-fixed** |
| C11 | resolved | **genuinely-fixed** |
| C12 | resolved | **partially-fixed + new defect** (H8) |

## Strengths

- **C2, C6, C10, C11 are clean fixes** with no contradiction found elsewhere. 4.6's reasoning is the
  strongest paragraph added this pass.
- **D-2f naming the D-2b/D-2e tension explicitly is real intellectual honesty**, and the symlink
  example is live and load-bearing.
- **The DAG is acyclic with no dangling referents**, verified programmatically over all 37 issues.
- The new Deferred section closes every pass-1 Missing item at the prose level.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| H1 | **high** | **The ten C1-fix criteria omit the issue that creates their script**, violating the plan's own stated rule at line 318. All ten call `scripts/checks/check-cargo-test-ran.sh`, created only by Issue 0.8; no `Discharged-by` lists 0.8. SC14 already sets the precedent |
| H2 | **high** | **Issue 0.8 is an unordered orphan — dependents = `[]`.** R10 asserts it lands "before Epic 4 touches them"; that ordering is prose, enforced nowhere. 4.1 can legally run first, which means Epic 4 edits plan-054's completed bundle — the exact violation 0.8 exists to prevent. Also 0.8 updates a `CHANGE-VALIDATION.md` row that 4.6 deletes, with no edge |
| H3 | **high** | **5.2a ships the quarantine AFTER 5.2 performs the removal.** `5.2a depends-on: 5.2`, and 5.2a has zero dependents, so the order is remove-then-make-reversible. SC18b would go green on a mechanism that did not exist when the migration ran. **R9's mitigation text is inaccurate as the DAG is written** |
| H4 | **high** | **"Drive-verify BEFORE removing" is unachievable, per this plan's own measurement.** EXP-002: with private trees present, pi resolves `.pi/agent/skills` **3/3** and opencode `.config/opencode` **4/5**. The pre-removal verification 5.2 demands **cannot pass**. The C4 fix traded a real hazard for an impossible precondition |
| H5 | **high** | **`undetermined` is not plumbed into the two places that are CONTRACTS.** Issue 0.3 still specifies `REQ-YF-MARK-006` as **three** outcomes — in a SPEC-first repo the source of truth says three while the implementation says four. Issue 5.1's schema declares no `undetermined` key, yet the gate is contracted to fail when it is non-empty: the check reads a missing key and either errors or passes vacuously |
| H6 | **high** | **The `resolves-upstream:` annotations still say `(include)` where the table now says `partial`** — 0.4, 3.1, 3.3 (#238); 4.8, 4.9 (#239); and 4.6 still annotates #256 despite being dropped from its `Resolved By`. Not cosmetic: `UPSTREAM_REQUIREMENTS` maps `include → CLOSED`, `partial → OPEN`, so an executor closes #238/#239 and `verify-reconcile` then fails — the late-halt-after-outward-facing-writes mode |
| H7 | **high** | **SC8 is unsatisfiable.** `lowercase-hyphen,max64` occurs in `SPEC.md` at three lines; 847/851 are the live requirement, but **line 180 is inside the living amendment log**, which 0.6 treats as append-only. A whole-file grep matches forever. Meanwhile 2.3 never mentions SPEC:851's actual validation clause |
| H8 | **high** | **The migration gate's `Test` names a script no issue creates.** `check-migration-dryrun.sh` appears on line 274 and nowhere else. Pass 1 concluded "no gate names a script no issue creates"; **the C12 fix reintroduced exactly that defect** |
| M1 | medium | **No issue writes `check_smoke_tier.py`** — 4.6 *registers* it; 0.8 enumerates three other files. An unowned deliverable on the land gate |
| M2 | medium | **Spike-measured: promoting `_common.sh` silently changes `ck_tree()`** from the execution worktree to the primary repo root. At `scripts/checks/`, the `.worktrees/<plan_id>` probe never matches, so all ten `check-cargo-test-ran.sh` criteria would grep the **primary** tree where the new functions do not exist → `ck_fail`. The C1 instrument becomes fail-closed but unrunnable. Same arithmetic breaks the smoke's transcript path |
| M3 | medium | **After 4.6 the smoke is registered in NO tier at all.** Five issues rewrite a script no recipe invokes. Defensible, but unstated |
| M4 | medium | **5.4 does not depend on 1.6 or 4.7** though SC20 discharges on both; reconcile can run before either files anything |
| M5 | medium | **C8's fix was applied to 0.3 but not 0.5**, which still names no id. Separately the derivation will **over-collect** — it picks up `REQ-YF-TUNE-029`, `REQ-YF-MARK-001/002/003` etc. that the plan *cites but must not amend*, so SC1 fails for the wrong reason |
| M6 | medium | **The live-harness gate over-blocks 4.5** — a source edit needing no authenticated harness — making SC13b unreachable and contradicting 4.3's explicit purpose. `5.2 depends-on 4.5` already dominates the path |
| M7 | medium | **Epic 1 rests on an EXP-004 claim the finding itself grades `inferred`.** Unchecked falsifier: does a recomputed marker-stripped hash over a **live deployed** copy actually equal `marker_hash`? If deployment residue escapes the ignore-list, every directory classifies `owned-but-modified`, `delete` is empty, and the gate — which fails on an empty delete set — hard-blocks at 5.1 |
| L1 | low | **Epic 5 mutates live `$HOME` before 5.3 validates and before merge-back.** If 5.3 fails and the branch is abandoned, the machine is migrated while `main` still targets private roots, so the next install re-creates them — re-establishing R3's divergence |
| L2 | low | **`name_transform` is dropped on a version-scoped, partly-inferred measurement.** The `max64` arm specifically was never exercised, though SPEC:851 requires validation against long names |

## Missing

1. A stated rollback path for **mid-execution abandonment** (L1).
2. A **measurement of the current classification of the four live trees** (M7) — the gate's verdict is fully determined by it and it is unknown.
3. An explicit note that the reworked smoke is unregistered (M3).
4. Owning issues and contracts for `check-migration-dryrun.sh` and `check_smoke_tier.py` (H8, M1).

## Gate Assessment

| Gate | Reachable? | Assessment |
| :-- | :-- | :-- |
| Start Gate | n/a | Standard |
| live-harness drivability | Yes | Improved — `codex login status` is genuinely falsifiable. **`Blocks: 4.5` over-blocks** (M6) |
| migration apply | **No — `Test` names a script no issue creates** (H8) | Structure still sound and the exit-2-vs-1 split is a real improvement, but the Test is unrunnable and its `undetermined` clause reads a key the schema does not declare (H5). Does not block 5.2a, where reversibility actually lands (H3) |
| Reconcile Gate | Yes | 5.4's `depends-on` under-specifies what reconcile must find (M4) |

**The gate layer REGRESSED this pass.** Pass 1 recorded "no gate names a script no issue creates"; that is no longer true.

## Upstream Assessment

| Issue | Table | Annotations | Verdict |
| :-- | :-- | :-- | :-- |
| #257 | include → 2.2, 5.2 | `(include)` | Consistent — sound |
| #238 | **partial** | 0.4/3.1/3.3 `(include)` | **Contradiction (H6)** — the IN/OUT note is excellent; the annotations undo it |
| #239 | **partial** | 4.8/4.9 `(include)` | **Contradiction (H6)** |
| #256 | include → 4.2, 4.3 | 4.6 still `(include)` | **Contradiction (H6)** |
| #121 / #243 / #240 | exclude | — | Sound; #243 now correctly re-characterized |
| #255 | deferred | — | Sound |

## Bottom line

> The reasoning improved materially this pass. **But eight of the twelve resolutions are partial or
> introduced a new defect, and the two most important fixes are structurally inverted:** the
> quarantine that makes the migration reversible ships *after* the removal (H3), and the
> pre-removal verification the same fix demands is impossible against this plan's own measurement
> of pi (H4). Two criteria and one gate are now unsatisfiable rather than vacuous — safer, but not
> shippable.

## Recommendations

1. Add `0.8` to the ten cargo-guard criteria and give it real dependents (H1, H2).
2. Invert the 5.2/5.2a edge and restructure to quarantine → verify → commit-or-restore (H3, H4).
3. Plumb `undetermined` into `REQ-YF-MARK-006` and the 5.1 artifact schema (H5).
4. Change the five `resolves-upstream:` annotations to `(partial)` and drop 4.6's (H6).
5. Scope the SPEC grep to the requirement stanza, away from the append-only amendment log (H7).
6. Give `check-migration-dryrun.sh` and `check_smoke_tier.py` owning issues and contracts (H8, M1).
7. Re-base `ck_tree`/`ck_plan_dir` as part of the promotion — it is not a file move (M2).
8. Measure the live-tree classification before relying on it (M7).

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 | high | `0.8` added to all ten cargo-guard `Discharged-by` cells; verified programmatically — 10 criteria cite the guard, **0 missing 0.8** | `main-session` | `resolved` |
| H2 | high | `depends-on: 0.8` added to 1.5, 2.4, 2.5, 3.4, 4.1, 4.2, 4.6, 4.8, 4.9, 5.1, 5.2a. **Verified: 0.8 now has 11 dependents** (was `[]`) | `main-session` | `resolved` |
| H3 | high | **Edge inverted.** 5.2a (quarantine mechanism) now `depends-on: 1.5, 2.2, 0.8`; 5.2 (the migration) `depends-on: 5.1, 4.5, 5.2a`. Verified: reversibility ships before the irreversible act. **The first attempt at this edit silently failed to apply and was caught by re-reading the DAG rather than trusting the edit** — the #250 defect, in this session's own work | `main-session` | `resolved` |
| H4 | high | **Concern accepted in full; the C4 fix was wrong.** 5.2 restructured to **quarantine-move → drive-verify → commit-or-restore**, with EXP-002's pi 3/3 and opencode 4/5 measurements quoted in the issue body as the reason a pre-move verification fails *by construction* | `main-session` | `resolved` |
| H5 | high | 0.3 rewritten to **four** outcomes so the SPEC matches the implementation; 5.1's schema extended to `{delete, kept[…, shadows_shared_root], undetermined}`; test renamed `marker_gated_removal_four_outcomes` | `main-session` | `resolved` |
| H6 | high | All five annotations changed to `(partial)`; 4.6's `#256` annotation dropped | `main-session` | `resolved` |
| H7 | high | `check-transform-gone.sh` scoped to `REQ-YF-INSTALL-007`'s stanza only, with the amendment-log collision named in 2.3's body; 2.3 also removes SPEC's long-name validation clause | `main-session` | `resolved` |
| H8 | high | `check-migration-dryrun.sh` authored by 0.8, with its full exit contract stated (2 unparseable / 1 bad-or-empty delete / 1 non-empty undetermined / 0 otherwise) | `main-session` | `resolved` |
| M1 | medium | 4.6 now **authors** `check_smoke_tier.py` and states its predicate and its exit-2 case | `main-session` | `resolved` |
| M2 | medium | **Spike accepted.** 0.8's body now states this is a **re-basing, not a file move**, and requires `ck_tree`/`ck_plan_dir` to move to `git rev-parse --show-toplevel` + explicit `YF_PLAN_ID`, and the smoke's transcript path to an explicit argument | `main-session` | `resolved` |
| M3 | medium | Deferred table gains an explicit row: the reworked smoke is **operator-invoked only** until 4.7 lands | `main-session` | `resolved` |
| M4 | medium | `5.4 depends-on: 5.3, 1.6, 4.7` | `main-session` | `resolved` |
| M5 | medium | 0.5 now names `REQ-YF-INSTALL-007`; 0.7's derivation scoped to **Epic 0 issue bodies only** with an explicit `cited-not-touched` exclusion list | `main-session` | `resolved` |
| M6 | medium | Live-harness gate `Blocks: 5.2` only | `main-session` | `resolved` |
| M7 | medium | **Measured rather than argued.** `yf harness skills status` across all four roots: **76 of 76 copies `ok` / `unmodified: true`** — the falsifier is refuted, the delete set is non-empty, and the gate will not spuriously hard-block. Recorded as `findings/exp-007-live-tree-classification.md` and folded into 1.1 as a re-measurement | `main-session` | `resolved` |
| L1 | low | Deferred table gains a mid-execution-abandonment row with the recovery sequence (restore, then reinstall from `main`) | `main-session` | `resolved` |
| L2 | low | D-7 reworded to **belt-and-braces removal on a 0.84.3-scoped measurement**, and 2.3's tests gain a **>64-character probe** — the one arm EXP-002 never exercised | `main-session` | `resolved` |

**All 17 concerns resolved. This file is now FROZEN.**
