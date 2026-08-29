---
type: Review
okf_spec: OKF-PLAN
id: pass-2
description: "Red-team pass 2 — REVISE. 6 blockers. Pass 1's repairs verified by EXECUTION: most sound, but Issue 1.7's premise was refuted, SC3's frozen set contradicted itself, and R11 went stale within hours."
---
# Red-team pass 2: plan-057-james-dixson-9ecf1c

## Verdict: REVISE

> **All 18 concerns resolved by the main session.** Re-dispatched as pass 3.

**Date:** 2026-08-29 · **Reviewer:** delegated adversarial agent (read-only)

This pass was aimed at **pass 1's repairs**, not at re-deriving pass 1. In the predecessor that
was the dominant failure mode: six times a concern was marked `resolved` and was not.

## Strengths

**Ten of pass 1's repairs verified SOUND by execution**, not by reading:

- **The pour directive parses.** `plan_extract.py` returns `unparsed: []` and all three `auto` gates
  carry the full directive in their `instructions`, each ending `…stalls into stop class 2.` — no
  blank-line truncation, which is the specific way plan-056 pass-6 lost it.
- **SC0 is falsifiable today**: the verbatim command exits **1**; all paths spelled correctly.
- **`--require 14` arithmetic correct** (9 rows in `INSTRUMENTS`, 5 new), exits 1 today.
- **`context.md` is clean** — every `D-\d+`, `\d+\.\d+` and `SC\d+` token resolves.
- DAG: DFS over 30 edges, **no cycles**; every one of 29 issues has ≥1 criterion; `gate_consistency`
  PASS; `okf.py check` OK; `doc_lint` PASS on all 11 bundle documents.
- **R12's measured non-collisions confirmed**: plan-059 adds 0 `scripts/checks/` files, 0 recipe
  rows, 0 selftest entries.

## Concerns

## Resolutions

| Concern | Severity | Detail | Resolution |
| :-- | :-- | :-- | :-- |
| C1 | high | **Issue 1.7's premise is FALSE, refuted by execution.** It claimed `_write_upstream_reference` "emits no frontmatter at all". Measured: `plan_manager.py:1044-1050` calls `_stamp_okf_type(..., description=...)` 26 lines below the template the pass-1 measurement stopped at, and a sandbox run of the real function emits `type`/`okf_spec`/`description`. The producer was fixed by plan-056 Epic 2 (`97237c8`, 2026-08-28); plan-057's 7 reference files simply predate it. | **resolved** — Issue 1.7 and SC5c deleted. The observation was real, the diagnosis was not: stale files, not a live producer bug. Deleting it also closes an unnecessary `plan_manager.py` edit adjacent to plan-059's — the collision R12 exists to avoid. |
| C2 | high | **SC3 cannot run**: `assets/sc3-frozen-bundles.txt` does not exist, no issue creates it, the path was bundle-relative against a repo-root invocation rule, and the 28 names were written nowhere. | **resolved** — asset written with all 25 names and the extraction rule; path bundle-qualified; Issue 1.0 now owns it and the `--baseline`/`--frozen-set` flag surface. |
| C3 | high | **SC3's frozen set contradicted its own baseline.** The 210/72/138 triple *includes* plan-056's and plan-057's entries while the same sentence said they were excluded. And the ratio over all 29 bundles is already **143/232 = 0.616**, better than the 0.657 baseline, with zero index work. | **resolved** — frozen to the 25 bundles `plan-031`…`plan-055`, all predating plan-056; re-measured **126/184 = 0.6848**. Bundles created after the baseline are excluded by construction. |
| C4 | high | **SC0b's prose said 13, its command said 14** — an off-by-one in the criterion whose stated purpose is killing off-by-ones. | **resolved** — and now 15, after SC0c added a sixth instrument. |
| C5 | high | **SC5c invoked `test_plan_manager.py`, which does not exist** and which no issue creates; the directory holds 24 per-feature test files and no monolith. | **resolved** — subsumed by C1 (deleted). |
| C6 | high | **R11 and the tree section went stale within hours.** They assert `HARNESS_INCOMPLETE` is 4 in the repo and 0 installed. The operator deployed after pass 1: `yf --version` = `ad6acc7` == HEAD, both copies read 4, byte-identical. | **resolved** — rewritten to the current fact, recording that the cell has now been wrong in *both* directions, plus the new consequence (unjudged class-A criteria now BLOCK at completion) and the condition (holds only while the installed tree matches). |
| C7 | med | `--require 14` is sound only while the array is exactly 14, and **nobody owns the six on-disk-but-unenumerated instruments** — plan-056's Issue 1.9 authored a different eight. | **resolved** — Issue 1.0 states the array stays at 15 for this plan and routes the six to a follow-on, with the arithmetic for why enumerating them now either fails the gate or re-opens the vacuity. |
| C8 | med | "6 existing hand-nested bundles" is stale — measured **33** across both roots; plan-059's is the largest and newest. | **resolved** — SC5 re-scoped to every nested bundle the rule selects. |
| C9 | med | **SC19's entire CLI surface is unowned**: repeatable `--root`, `--maxdepth`, `--require-legacy`, `--min-roots`, `--json` appear in no issue. | **resolved** — Issue 2.2 now owns it, with `--require-legacy` called out as the load-bearing flag. |
| C10 | med | **SC12's `backfill.json` is unowned and unlocated.** | **resolved** — Issue 2.4 emits it at `assets/backfill.json`. |
| C11 | med | **SC7 is still green today** (`--min-roots 60` and even `64` exit 0), and its falsifiability was delegated to a RED row nobody creates — the existing one is a nonexistent-root fixture. | **resolved** — Issue 1.4 now owns replacing that row with a fixture carrying a genuinely unlisted nested file. |
| C12 | low | SC1's figures do not match the instrument's own output (`5 direct`, `24 transitive`, not `0/22`). | **resolved** — quoted verbatim, and labelled an invariant like SC5b. |
| C13 | low | SC0's residuals named Issue 2.1 for a `chmod +x` it does not owe; `Discharged-by` omitted 2.2. | **resolved** — 1.0 / 2.2 / 2.8. |
| C14 | low | Stale counts: 58 → **59** bundles; 63 → **64** enumerated. | **resolved**. |
| C15 | low | **Nothing verified the pour directive was HONOURED.** `test_class` is a bead field; the directive is prose to the coordinator. | **resolved** — SC0c added, asserting the poured `auto` gates carry `test_class: probe`. A directive nobody checks is the same defect class as the missing directive pass 1 found. |
| C16 | low | Risk rows ran R1…R10, R12, R11. | **resolved** — and the first repair attempt moved R12 *into the criteria table*, breaking `criteria-table-columns` and `criterion-ids`; caught by re-running the audit rather than by reading. |
| C17 | low | Three `manual:` criteria remained (SC20, SC22, SC23), all grep-able. | **resolved** — promoted to executable greps. Only SC8's descriptive text still contains the word. |
| C18 | low | Creating the SC3 asset makes `assets/` non-empty and enumerable, turning `okf-index-drift` red — the exact class SC8 was promoted for. | **resolved** — `index.md` entry added in the same pass; drift re-verified 0. |

## Missing

- **A mechanical `plan.md` ↔ instrument-output check.** Three separate stale-figure defects this pass
  (C3, C12, C14) are all "a number in the criterion disagrees with what the command prints." One
  criterion that re-runs the instrument and diffs the stated triple would catch the whole class.
- **An owner for the six drifted `INSTRUMENTS` rows** — deferred to a follow-on rather than closed.

## Gate Assessment

| Gate | Verdict |
| :-- | :-- |
| Start | OK |
| Predecessor complete | **Sound** — directive parses in full, `Test` self-contained |
| Backfill authorization | **Sound.** `Test: none` sentinel, human type → SURFACE regardless. Still the best gate in the plan |
| Upstream network reachable | **Sound** — directive parses; evidence outside `Blocks` |
| Verification harness ready | **Sound today**, but its soundness was an unowned invariant until C7; `Blocks` transitively covers 1.2–1.6 with 1.0 correctly unblocked |
| Reconcile | OK |

No cycles over 30 edges, no frontloading miss, every issue covered by ≥1 criterion.

## Upstream Assessment

Unchanged and defensible. `verify-reconcile` → exit 1, `"4 of 6 upstream row(s) did not reach the end
state"` — the expected pre-execution state, discharged by 3.5. #189's `Resolved By` now agrees with
3.5's `resolves-upstream` (pass-1 C12 confirmed fixed). All seven reference bodies present — and,
contra the deleted Issue 1.7, all seven **do** carry `description:` frontmatter.
