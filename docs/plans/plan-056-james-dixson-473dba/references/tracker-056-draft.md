---
type: Reference
okf_spec: OKF-PLAN
description: "DRAFT closing comment for the coarse tracker #271 — what plan-056 shipped, what it measured, and what it carried forward. NOT POSTED."
disposition: tracker
target: "#271"
---
**plan-056 is complete.** 35 issues across 5 epics; **17 of 17 runnable success criteria pass and
19 of 19 class-A criteria were judged** (`recheck-criteria` verdict `PASS`); the FULL validation
tier is green.

## The problem, restated

Both structural validation layers were **gates that could not fail**, and the OKF issue cluster
proposed building more structure on top of them.

- `doc_lint` demotes `E` and `W` to `R` at every terminal status, and essentially every historical
  bundle is terminal. **46 of 48 checks were structurally incapable of a non-zero exit.**
- `okf.py reindex` appeared in **zero** `CHANGE-VALIDATION.md` rows, **zero** CI steps and **zero**
  `plan_manager.py` call sites. Root-index drift had been fixed nine days earlier and had already
  **regressed in 9 of 30 index-bearing bundles**. Nothing noticed.

## What changed, measured

| | before | after |
| :-- | :-- | :-- |
| Drifting bundles | 8 of 31 index-bearing | **0** |
| `reindex` gate bindings | 0 rows, 0 CI steps, 0 call sites | FAST **and** FULL |
| `reindex` exit contract | 3-way; a typo read as a benign skip | 5-way; `no-such-path` split out, `check_markers` wired |
| `audit-close` on plan-053 | 25 fixture findings | **0**, walk still live (`--no-exclude` restores 28) |
| Verification instruments | — | 10, each red on a per-instrument sabotaged fixture |

## SPEC-first (Epic 0)

Eleven amendments landed **before** any implementation: `REQ-OKF-011` amended;
`REQ-OKF-CHK-003`/`-004`, `REQ-DATA-074`/`-075`, `REQ-PLAN-081`, `REQ-CLI-028`/`-029` added;
`REQ-DATA-044` and `REQ-PLAN-080` amended.

## Three defects reproduced RED before being fixed

1. **#265** — the pre-fix engine returns `PASS`, exit 0, *"all 1 evaluated criterion/criteria
   hold"* at `evaluated/class_a = 1/2`. Fixed with `HARNESS_INCOMPLETE` as a **third, distinct**
   verdict.
2. **#233** — `audit-close` on plan-053: 25 fixture findings → 0.
3. **The index-reparenting bug** — the pre-fix predicate demonstrably moves a group's children
   under the newly added member.

## Two stale figures corrected

- D-1's unsourced *"~423 findings"* → a reproducible **392** (`findings/exec-001`), of which
  **197 are truly `E`**.
- *"`description:` on 0 of 423 nested files"* → **165 of 983**, re-measured 2026-08-28, corrected
  in all 8 occurrences across 4 shipped files. This **weakens** the premise those specs used to
  defer nested index generation, and they now say so rather than continuing to assert absence.

## Upstream

Closed **#233**, **#246**, **#265**. Commented partial on **#140**, **#165**, **#171**, **#247**.
**#170** carried whole to plan-057. `verify-reconcile` exits 0 with all 11 substantive rows passing.

## Carried forward

**12 follow-on beads**, three of them found *during* execution: `plan_extract.py` drops a
`(REQ-*)` parenthetical between an issue id and its colon; `test_config_tiers.py` reads the
developer's real gitignored config; and the index-entry regex cannot see em-dash- or table-form
entries — which is why `docs/research/005`'s *drift* was a **separator artifact**, not missing
content, and was repaired without appending bare bullets beside the richest index in the corpus.

## The fix fired on the plan that shipped it

`recheck-criteria` returned **`HARNESS_INCOMPLETE`** during this plan's own §6.4 close — the third
verdict Issue 1.10 added for #265 — because SC11c went unjudged at a 300s timeout. Under the
pre-fix engine that row would have been `inconclusive`, counted in neither `failed` nor
`evaluated`, and the chain would have reported `PASS`. The halt was **not overridden**: the cause
was fixed (`check-recipe-row.sh` now caches on a tree fingerprint, 1:58 cold → 0.065s warm) and the
chain re-run to a real PASS with every class-A criterion judged.

**It fired because the chain was run against the repository copy.** A by-the-book §6.4 resolves
`${SKILL_DIR}` to the *installed* skill, which is still pre-fix — measured: `HARNESS_INCOMPLETE`
appears 5 times in `skills/yf-plan/scripts/plan_manager.py` and **0 times** in
`~/.claude/skills/yf-plan/scripts/plan_manager.py`, because installing mid-execution is forbidden.
So the protection is real but **route-dependent**, and that window was covered independently by a
capability gate whose `Test:` halts on an exit code outside the verdict arithmetic entirely. The
successor plan inherits the fixed engine on both routes once the skills are deployed.

Plan: `docs/plans/plan-056-james-dixson-473dba/` · Epic: `yf-mol-xbp` · PR #272
