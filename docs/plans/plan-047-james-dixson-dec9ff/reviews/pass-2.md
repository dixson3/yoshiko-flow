---
type: Review
okf_spec: OKF-PLAN
id: pass-2
---
# Red-team pass 2 — plan-047-james-dixson-dec9ff

## Verdict: REVISE

**Date:** 2026-08-18 · **Status:** all concerns resolved · **Brief:** verify pass-1's claimed
resolutions, not re-review from scratch.

## Resolution verification (the primary job)

| # | Pass-2 verdict |
| :-- | :-- |
| H1 | **PARTIALLY RESOLVED — new defect.** `scripts/` empty; all three script Tests exit **127**, not 1. The `d["commands"]` fix exists in no artifact |
| H2 | **PARTIALLY RESOLVED.** DAG clean; §1-row claim ✓. But the carve-outs gate's `Instructions:` ("satisfied by completing Epic 2") is still false — its script was authored by Issue 3.4, in Epic 3 |
| H3 | **PARTIALLY RESOLVED.** Hoist verified — 2.5/2.6 at positions 21–22 of 73 (was 63 of 68), no precondition violation. But D-9's text still said "the normalizer (Epic 7)" and #125's `Resolved By` still said "Issue 8.2" |
| H4, H5, H6 | **GENUINELY RESOLVED** |
| M1, M3, M4, M5, M7, M9, L2–L5 | **RESOLVED** |
| M2 | **NOT RESOLVED.** No `tracker` row, no `**Coarse tracker:**` line. `stamp_tracker` runs at **§5.2a, the pour** — an Epic-10 issue cannot make SC39 true |
| M6 | **RESOLVED IN TEXT, UNVERIFIABLE** — the script asserting it does not exist |
| M8 | **NOT RESOLVED — NEW HIGH DEFECT.** See N1 |
| M10 | **PARTIALLY.** Issue 8.3 + SC29 correct; D-2a still pointed at Issue 7.3 and SC22 |
| M11 | **PARTIALLY.** 3 of 4 converted; the Upstream-write Test was still inline, so SC12 was false and unachievable without staling the fingerprint post-approval |
| L1 | **RESOLVED in plan.md, NEW DEFECT elsewhere** — `log.md` recorded v1 as 72 issues / 40 criteria where pass-1 measured 68 / 30 |

Pass-1 "Missing": #2, #3, #4, #5 resolved; #1 (tracker) not resolved; #6 partial.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| N1 | **high** | **`REQ-DATA-020`–`023` collide with four live requirements** (`spec/data.md` lines 47, 62, 66, 70 — the config/state split). The M8 fix counted forward from `REQ-DATA-017` without reading the file, which is **not** in numeric order. The plan's own thesis committed inside the fix for it: an inference where a measurement was one grep away. Epic 0 is the DAG root, so every epic inherits the break |
| N2 | **high** | **`plan.md` has no `## Approach` and no `## Epics`** — REQ-DATA-011 requires both, `seed_plan_md` emits both, and all 46 other plans have both. Every `### Epic N:` block was nested under `## Investigation Findings`. The unrepaired scar of R12. Falsifies Issue 6.3's "`plan.md` — 0% drift today" and the plan's claim to be held to its own rules first |
| N3 | **high** | **The EXP-006 table row is truncated mid-sentence**, unterminated code span, no closing pipe. The experiment that produced D-2, D-2a, the fingerprint postcondition and R6 has no readable question statement. `yf-markdown-lint` does not catch it |
| N4 | **high** | **Gate scripts: exit 127 is not a pre-work failure.** Same class as H1 — the accident changed from `KeyError` to `command not found`. Three compounding problems: an **empty** `.sh` exits **0**, so the gate is trivially satisfiable by the gated party; SC10's "exits 1 on the pre-work tree" is unachievable; and the scripts were authored at 3.4, *after* their own conditions are made true, so neither could ever run against a tree where it should be red |
| N5 | medium | **Every stale cross-reference the restructure created** — all 7 non-`exclude` `Resolved By` cells wrong, plus `Issue 9.0`, `Issue 9.5`, "Epic 7", SC28/SC21/SC22 misreferences, and three in `context.md`. ~15 instances of the #135 class the plan dispositions |
| N6 | medium | **Issue 6.9b is in the wrong epic and lands too late.** Epic 6 is instantiation; 6.9b patches `_audit_plan` — an enforcement fix. It sat at ~58 of 73, **after** 2.5 makes `approved` refuse on a red `ready-check`, so the plan could wedge itself with the fix 37 issues away. Also a SPEC-first violation: it changes what REQ-PORT-006 means with no amendment |
| N7 | medium | **Issue 2.5 changes the `update-status` contract with no SPEC amendment.** Same SPEC-first violation, on the plan's self-declared highest-value fix |
| N8 | medium | **`reviews/pass-1.md` is unparseable; `ready-check` is red** — used `**Verdict:** REVISE` instead of the `## Verdict:` heading REQ-PLAN-071 requires. #116's defect, in the review record of a plan about document conformance |
| N9 | medium | **SC20's verification depends on artifacts no issue produces.** No issue creates the seeded bad instances, so an executor satisfies it by assertion. Count wrong three ways: says 10, lists 8, Epic 6 has 11 |
| N10 | low | **Criterion ids were renumbered, violating the plan's own Issue 0.3** ("insertable without renumbering"). Pass-1's SC1/2/3/14/15/21/22/28/29 now denote different criteria, so `pass-1.md` is unreadable against the current plan |
| N11 | low | `log.md` count disagreements; `index.md` missing `assets/`/`scripts/` and a `reviews/` description; carve-out gate says "9 vendored files" where D-11/2.1/SC7 say 6; `2.5 depends-on 2.6` has inverted numbering; "21 of 46" measured as 20; SC40 already passes today; `references/*` stated as 194 / 191 / 183 and never reconciled |

## Strengths

- **The DAG survived the restructure intact** — 0 duplicate ids, 0 dangling `depends-on`, 0 cycles,
  0 backward-epic edges, **0 cut violations**, so D-13's Epic-5 split point is a genuine cut line.
  Verified by parse, not by reading.
- **Issue 6.9b's premise is a real measurement, reproduced** on a scratch copy: one transition + one
  pass record → `expected 2 pass-*.md, found 1` on a correct bundle.
- **The hoist of 2.5/2.6 is sound** — no precondition violation.
- **The Upstream-write gate is genuinely non-vacuous now** — executed, exit 1.
- **The #165 overclaim guard is genuinely resolved** — pass-1's sharpest upstream concern.

## Gate Assessment

All three script gates **BROKEN** at exit 127 (script absent, authored after their own conditions,
satisfiable by an empty file). Upstream-write **fixed** but still the only inline quoted Test.
Reachability: no cycles; every Condition's evidence produced strictly upstream of its `Blocks` set.

## Upstream Assessment

Dispositions remain sound (5 partials OPEN, 2 includes CLOSED). **Every `Resolved By` cell stale**,
and `verify-reconcile` reads that column. **The tracker gap persists and is worse**: Issue 10.5
*documents* the failure mode without creating the row — the plan diagnoses its own defect and does
not fix it.

## Operator Resolutions

| # | Resolution | Status |
| :-- | :-- | :-- |
| N1 | **Verified independently before accepting** — `020`–`023` are live. Re-allocated to `018`, `019`, `024`–`027` against `grep -rhoE 'REQ-DATA-[0-9]+' skills/ \| sort -u`. Issue 0.9 now runs that grep **first**, and records why counting forward is wrong | resolved |
| N2 | **Verified and root-caused: the same bug as R12, second instance.** `t.index("## Epics")` matched a backticked `## Epics` *inside the EXP-006 table row*, cutting the rest of that row, the entire six-finding summary, the Corrections table, and all of `## Approach`. All restored; the EXP-006 row reworded to avoid a literal `## Epics` so it cannot recur | resolved |
| N3 | Row restored from `findings/exp-006-…` | resolved |
| N4 | **Issue 1.4 added in Epic 1**, before Epic 3 makes the conditions true. Scripts now emit a JSON verdict with named keys so a stub is INCONCLUSIVE not PASS, and each script's pre-work exit code + stderr is committed to `assets/gate-prework/` as auditable falsification evidence. SC9d asserts all three properties | resolved |
| N5 | `Resolved By` regenerated **from the parsed `resolves-upstream:` annotations**; all prose issue/epic/criterion references swept | resolved |
| N6 | Split: SPEC half → Issue 0.9b (Epic 0); implementation → Issue 2.7 (Epic 2), **ordered before 2.5** so the plan cannot wedge itself | resolved |
| N7 | **Issue 0.9a** allocates `REQ-DATA-028` for the intake refusal + override flag, ahead of 2.6/2.5 | resolved |
| N8 | `## Verdict: REVISE` heading added to `pass-1.md`; `ready-check` now parses it and correctly blocks on REVISE | resolved |
| N9 | **Issue 6.0** added — commits one malformed fixture per schema-bearing type. SC20 corrected to 8 issues and now requires the committed fixture | resolved |
| N10 | **Accepted, not fixed.** Renumbering pass-1's ids again would compound the problem. Recorded here: pass-1 criterion references are read against pass-1's own table, not the current plan. Issue 0.3's insertable-id rule applies from approval forward | accepted |
| N11 | `log.md` counts corrected; `index.md` regenerated with `assets/`/`scripts/`; carve-out gate restated as "6 vendored `.md` files plus 3 non-md sidecars"; no-fingerprint count now derived at run time rather than transcribed; `references/*` reconciled | resolved |
| M2 | **`tracker` row added** to the Upstream Issues table plus a `**Coarse tracker:**` field, so `stamp-tracker` finds it at the pour. Filing the issue itself is an outward-facing write and is flagged for operator authorization at INTAKE | resolved |
| M11 | Upstream-write Test converted to `scripts/gate-upstream.sh`; SC12 now asserts all four match `^bash .*\.sh$` | resolved |

**Blocking set N1–N4, M2, M8: all resolved.** Re-review required per REQ-PLAN-030.
