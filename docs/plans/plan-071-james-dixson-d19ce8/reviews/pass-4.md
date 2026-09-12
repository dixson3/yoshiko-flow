---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 4, EXECUTION] APPROVE — all five pass-3 resolutions verified by execution; every bundle checker green; 19 of 20 SC rows RED for the right reason, SC3 green by declared invariant; 2 non-blocking notes"
plan: plan-071-james-dixson-d19ce8
pass: 4
mode: execution
---
# Plan Red-Team: plan-071-james-dixson-d19ce8

## Verdict: APPROVE
**Mode:** execution

## Strengths
- All five pass-3 resolutions verified by execution, not by reading the Resolutions table: SC3 exits 0 and its row text declares the invariant; `okf.py reindex` reports `clean`; pass-2 Resolutions has exactly 6 data rows with Severity cells `high, medium-high, medium, low-medium, low, low`; 018 sits in merge group `002+003+018+036` in Issue 0.4, is absent from the rewrite list `012, 017a, 020, 021, 022, 030, 037, 038`, and D-7 (plan.md:182) says "absorbed"; `audit` emits zero `[R]`/warn findings.
- Every bundle checker Issue 2.1 prescribes for an execution pass is green: doc_lint PASS on plan.md and pass-3.md, plan_extract `--strict` 0 unparsed / 0 recovered, gate_consistency PASS (5 gates), check-req-coverage "every non-Epic-0 issue is covered", markdown_lint clean on all 8 bundle files.
- 19 of 20 runnable SC rows are RED today for the reason the plan's execution removes; SC3 is green by declared invariant. No row exits 126/127, times out, or hits a usage/unrecognized error; every `No such file` (SC6, SC8, SC13) names a deliverable an Epics issue creates (2.4, 1.3, 4.6).
- Both gate tests behave as the plan states: REQ-free → 0, plan-070 → 1 (070 not on `main`).
- Review-count invariant holds: 3 `- review-pass:` lines, 3 `pass-*.md` files.

## Executed

| # | Command | Exit | Result |
| :-- | :-- | --: | :-- |
| 1a | SC3 command (unescaped) under `bash -c` | 0 | green today; `grep -c 'an invariant: green today' plan.md` → 1 |
| 1b | `okf.py reindex <dir>` | 0 | `reindex …: clean` |
| 1c | pass-2 `## Resolutions` data rows | — | 6 rows; all Severity cells in closed vocabulary |
| 1d | `grep -c absorbed plan.md` | 0 | 2; 018 in group 1 (Issue 0.4), not in rewrite list; D-7 line 182 matches |
| 1e | `plan_manager.py audit <dir> --json-output` | 0 | status pass; `[R]` count 0, warn count 0 |
| 2 | `doc_lint.py --path plan.md --json` | 0 | PASS, files_checked 2, no findings |
| 2 | `doc_lint.py --path reviews/pass-3.md --json` | 0 | PASS, files_checked 1 |
| 2 | `plan_extract.py <dir> --json --strict` | 0 | epics 6, issues 23, edges 35, gates 5, criteria 21, risks 9, upstream 15, reqs 13, unparsed 0 |
| 2 | `gate_consistency.py <dir> --json` | 0 | PASS, gates 5, findings [] |
| 2 | `scripts/checks/check-req-coverage.py <dir>` | 0 | 19 issues: 2 direct, 4 transitive, 14 name-REQ, 1 bugfix |
| 2 | `plan_manager.py ready-check <dir> --json` | 3 | `ready: false`; reason `last red-team verdict is REVISE (pass-3); …` |
| 3 | 20 SC rows under `timeout 120 bash -c` | — | table below |
| 4 | Gate "allocated REQ ids are free" | 0 | as expected |
| 4 | Gate "plan-070 has landed" | 1 | as expected today |
| 5 | `markdown_lint.py --rules ML001,…,ML010` × 8 files | 0 | all `clean` |
| 6 | `grep -c '^- review-pass:' log.md` vs `ls reviews/pass-*.md \| wc -l` | — | 3 = 3 |

**Step 3 — SC rows** (repo root, `timeout 120 bash -c`):

| SC | expected | actual | expectation |
| :-- | --: | --: | :-- |
| SC1 | 0 | 1 | RED expected (41 registrations) |
| SC2 | 0 | 1 | RED expected (39 ids / 760 lines) |
| SC3 | 0 | 0 | GREEN by declared invariant — not a defect |
| SC4 | 2 | 0 | RED expected (both formulas exist) |
| SC5 | 0 | 1 | RED expected |
| SC6 | 0 | 2 | `No such file` — `test_ready_check_smoke.py`, Issue 2.4 → allowed |
| SC7 | 0 | 1 | RED expected |
| SC8 | 0 | 2 | `No such file` — `findings/fidelity-baseline.md`, Issue 1.3 → allowed (see C2) |
| SC9 | 0 | **0** | GREEN today — see C1 |
| SC10 | 1 | 0 | RED expected (2 hits) |
| SC11 | 0 | 1 | RED expected |
| SC12 | 0 | 1 | RED expected — `UNWIRED check-cargo-test-ran.sh` |
| SC13 | 0 | 2 | `No such file` — `check-provably-necessary.py`, Issue 4.6 → allowed |
| SC14 | manual | — | manual |
| SC14b | 0 | 1 | RED expected (0 hits) |
| SC15 | 1 | 0 | RED expected (8 registrations) |
| SC16 | 0 | 1 | RED expected |
| SC17 | 0 | 2 | INCONCLUSIVE — no SPEC entry yet, expected |
| SC18 | 0 | 1 | RED expected |
| SC19 | 0 | 1 | RED expected |
| SC20 | 0 | 1 | RED expected |

## Concerns
| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | low-medium | measured: SC9 exits 0 today (pass-3 showed it RED at 0 execution passes; pass-3.md now carries `**Mode:** execution`). The row explicitly names the artifact and states pass 3 was driven by an explicit brief, so it is not a defect under the brief's rule — but SC9 no longer discriminates Issue 2.1's delivery: it would stay green if `agents/red-team.md` were never rewritten. Non-blocking. | Either accept SC9 as a plan-process criterion (as written) and rely on SC5's contract test for 2.1, or add a clause to SC9 that names something only the rewritten brief produces (e.g. the pass-N.md carries the `measured\|inferred` column heading). |
| C2 | low | inferred: SC8's failure surface today is `test: -ge: unary operator expected` (a bash builtin error following grep's `No such file`). Issue 2.4's `ready-check` classifies `No such file` against the Epics allow-list; this row emits both a `No such file` line and a non-`usage:` builtin error, so the classifier must key on the former. Not a defect today. | Optionally guard the row: `test "$(grep -c … 2>/dev/null \|\| echo 0)" -ge 11`, so a missing file yields a clean numeric red. |

## Missing
- Nothing measured. No `inferred:` premise an SC depends on was falsified; all pass-3 resolutions reproduce by execution.

## Gate Assessment
- **allocated REQ ids are free** — measured exit 0; ONE-SHOT declared; no cycle.
- **plan-070 has landed** — measured exit 1 (070 untracked, not on `main`); decidable at execute start; blocks only 0.4/3.2.
- **baseline suite is green** — verified in pass 3 (all three suites exit 0); Blocks set unchanged since.
- **Reconcile** — unchanged; R5 acknowledged.

## Upstream Assessment
Unchanged from pass 3. No disposition changes required.

**Residue:** none in the repo. Scratch output (`run_sc.py`, `audit.json`, `extract.json`) written to the session scratchpad only; a transient `/tmp/mdl.out` was removed.

## Resolutions

**Status: APPROVE. Both non-blocking notes actioned by the main session on 2026-09-10.**

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 SC9 exits 0 today and no longer discriminates Issue 2.1's delivery | low-medium | Accepted as a plan-process criterion (it measures this plan's own review shape, D-6); Issue 2.1's delivery is discriminated by SC5's contract test, which names REQ-AGENT-066 | `main-session` | `resolved` |
| C2 SC8's failure surface is a bash builtin error after grep's No such file | low | SC8 guarded with `\|\| echo 0` so a missing baseline yields a clean numeric red | `main-session` | `resolved` |
