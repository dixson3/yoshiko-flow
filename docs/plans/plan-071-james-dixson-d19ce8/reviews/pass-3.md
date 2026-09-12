---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 3, EXECUTION] REVISE — 5 measured concerns: SC3 cannot go green (ugrep binary-match lines from __pycache__), bundle index drift, 6 shifted rows in pass-2 Resolutions, 018 placement ambiguity, findings-schema markers; all 20 SC rows RED for the right reason, arithmetic verified, 19/19 prior resolutions present"
plan: plan-071-james-dixson-d19ce8
pass: 3
mode: execution
---
# Plan Red-Team: plan-071-james-dixson-d19ce8

## Verdict: REVISE
**Mode:** execution

## Strengths
- Every checker the plan itself proposes for an execution pass (Issue 2.1) is green on the bundle except `okf.py reindex --check` (C2): doc_lint PASS, plan_extract `--strict` clean (0 unparsed), gate_consistency PASS, req-coverage covered, audit pass.
- All 20 runnable SC rows are RED today for a reason the plan's own execution removes — none is pre-green, none is a usage/126/127 error, and every `No such file` names a deliverable an Epics issue creates (2.4, 4.6, 1.3).
- Both arithmetic claims check out by execution: 41 − 6 − 3 = 32 verbs; 39 − 3 − 14 = 22 REQ-LAND ids (the six merge groups absorb 3+4+3+1+1+2 = 14).
- All 19 pass-1/pass-2 resolution edits are present in `plan.md` (chain property holds, 0 phantoms).
- The baseline gate is green (all three suites exit 0) and every test file an SC names exists except the two the plan creates.

## Executed

| # | Command | Exit | Result |
| :-- | :-- | --: | :-- |
| 1 | `doc_lint.py --path plan.md --json` | 0 | PASS, files_checked 2, 0 errors, 0 warnings |
| 2 | `plan_extract.py <dir> --json --strict` | 0 | epics 6, issues 23, edges 35, gates 5, criteria 21, risks 9, upstream 15, unparsed 0 |
| 3 | `gate_consistency.py <dir> --json` | 0 | PASS, gates 5, no findings |
| 4 | `check_amendment_log.py --plan plan-071…` | 2 | INCONCLUSIVE — no SPEC entry yet. **Expected pre-execution**, not a finding |
| 5 | `check-req-coverage.py <dir>` | 0 | 19 non-Epic-0 issues covered (2 direct, 4 transitive, 14 name-REQ, 1 bugfix) |
| 6 | `okf.py reindex --check <dir>` (verb exists; `--check` is the default) | **1** | drift: 7 bundle entries absent from `index.md` (see C2) |
| 7 | `plan_manager.py audit <dir> --json-output` | 0 | status pass; 4 `[R]` warnings on the two findings files (missing sections; `\*\*(measured\|inferred):\*\*` absent) |
| 8 | `plan_manager.py ready-check <dir> --json` | 3 | `ready: false`; reasons: `["last red-team verdict is REVISE (pass-2); a REVISE/INVESTIGATE-MORE blocks ready-for-approval until a later cycle returns APPROVE"]`; audit_status pass; malformed_review null |
| 9 | SC rows under `timeout 120 bash -c` | — | table below |
| 10 | Gate "allocated REQ ids are free" | 0 | as expected. Gate "plan-070 has landed": `git show main:…plan-070…/plan.md \| grep -q '^status: complete$'` → **1** (070 not landed today — expected) |
| 11 | Chain property greps | — | 19/19 claimed edits present (hit counts below) |
| 12 | `grep -c '@cli.command('` → **41**; `grep -Eo 'REQ-LAND-[0-9]+[a-z]*' … \| sort -u \| wc -l` → **39** | 0 | 41 − 6 − 3 = 32 ✓; 39 − 3 − 14 = 22 ✓ (039 absent from `landing.md` today: 0 hits) |
| 13 | Spot-checks | 0 | plan-031/plan-041 `plan.md:8: deliverable_class: ci-release` ✓; SKILL.md:1962 and :1977 both `plan_manager.py parked --json` ✓; SKILL.md:1705 `judgement-never-fired-report` ✓; plan-062 journal `history` ends `L_MIRRORED`, phase `l17_residual_mirroring` ✓ |

**Step 9 — SC rows** (host `grep` is ugrep 7.8.4):

| SC | expected | actual | pre-execution expectation |
| :-- | --: | --: | :-- |
| SC1 | 0 | 1 | RED expected (41 > 32) |
| SC2 | 0 | 1 | RED expected (39 ids, 760 lines) |
| SC3 | 0 | 1 | **RED for the wrong reason — see C1** |
| SC4 | 2 | 0 | RED expected (both formulas exist) |
| SC5 | 0 | 1 | RED expected (no REQ-AGENT-066 in contract test; suite itself exits 0) |
| SC6 | 0 | 2 | `No such file` — `test_ready_check_smoke.py`, named in Issue 2.4 → allowed |
| SC7 | 0 | 1 | RED expected (`fidelity` absent; `test_retrospective.py` exits 0) |
| SC8 | 0 | 2 | `No such file` — `findings/fidelity-baseline.md`, named in 1.3 → allowed |
| SC9 | 0 | 1 | RED expected (2 reading, 0 execution passes); names the new artifact |
| SC10 | 1 | 0 | RED expected (2 hits of `_land_l5_advisory_recheck`) |
| SC11 | 0 | 1 | RED expected (no `gate-consistency` in `test_close_contract.py`; both suites exit 0) |
| SC12 | 0 | 1 | RED expected — `UNWIRED check-cargo-test-ran.sh` (a real 4.5 target) |
| SC13 | 0 | 2 | `No such file` — `check-provably-necessary.py`, named in 4.6 → allowed |
| SC14 | manual | — | manual |
| SC14b | 0 | 1 | RED expected |
| SC15 | 1 | 0 | RED expected (8 registrations matched; 6 dead verbs measured registered) |
| SC16 | 0 | 1 | RED expected |
| SC17 | 0 | 2 | INCONCLUSIVE — expected pre-SPEC |
| SC18 | 0 | 1 | RED expected |
| SC19 | 0 | 1 | RED expected |
| SC20 | 0 | 1 | RED expected |

`recheck-criteria` unescapes `\|` (`plan_manager.py:3227`), so the table-cell form is what runs.

**Step 11 — chain property** (`grep -cE` on plan.md; all ≥1): P1C1 `D-10 \(revised at pass 1, C1\)`=1, `\^deliverable_class:`=1; P1C2 `verb wrapper is \*\*kept\*\*`=1; P1C3 `no capability gate declared`=1, `runs .gate_consistency.py. over the bundle`=1; P1C4 `41 − 6 dead`=1; P1C5 `landing-halt:`=4, `no-record`=2; P1C6 `plan-070 has landed`=4, `REQ-LAND-039. folds`=1; P1C7 `SC14b`=1, `300s to 60s`=1; P1C8 `test_close_contract.py. asserts the tuple`=1; P1C9 `__pycache__`=1, `\[!_\]\*`=1; P1C10 `enumeration list`=3, `five negative`=2; P1C11 `runs .recheck-criteria --json. itself`=1; P1C12 `count as 15`=2; P1C13 `explicit brief`=1. P2C1 `six dead verbs`=2, `= 32`=2; P2C2 `023\+031`=1, `024\+034\+026`=1, `14 absorbed`=2; P2C3 `ready-check. is bd-free`=1; P2C4 `SKILL.md:1962`=1, `SKILL.md:1705`=1; P2C5 `REQ-LAND-\[0-9\]\+\[a-z\]\*`=2 and old form `[0-9]\*`=0; P2C6 `formulas.md:61`=1, `FORMULA_COUNT_RE`=1; pass-2 Missing item `resolve it by hand as plan-068 did`=1.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | measured: SC3 can never go green as written. `grep -rhoE 'REQ-LAND-…' skills/yf-plan SPEC.md --exclude-dir=formulas` emits `Binary file skills/yf-plan/scripts/__pycache__/plan_manager.cpython-314.pyc matches` (×8) **on stdout**, so `comm -13` always returns non-empty → exit 1 regardless of tree correctness (`__pycache__/` is gitignored, untracked, and present in every working checkout that has run a test). Re-run with `-I` → exit 0; with `--exclude-dir=__pycache__` → exit 0. On the plan's own first metric data point this is a guaranteed L11 FALSE or a post-approval Verification edit — precisely one `sc_flipped_post_approval` event, manufactured by the criterion. | Change SC3's grep to `grep -rhoEI … --exclude-dir=formulas --exclude-dir=__pycache__`. Note in the row that it is an invariant (green today, red between 0.4 and 3.3), so its pre-execution green is by design. |
| C2 | medium | measured: `okf.py reindex --check <dir>` → exit 1, drift: `diagrams/loop-before-after.{d2,png}`, `findings/exp-001…`, `findings/exp-002…`, `references/`, `reviews/pass-1.md`, `reviews/pass-2.md` all "present in the bundle but absent from index.md". Issue 2.1 makes this checker part of every execution pass; the plan's own bundle fails it while `audit` passes (the two disagree on bundle conformance). | Main session runs `okf.py reindex --write <dir>` (dry-run reports `clean` with 7 `add-missing`) before intake; consider making `audit` surface reindex drift at `warn`. |
| C3 | low-medium | measured: pass-2.md `## Resolutions` has 12 data rows for 6 concerns; rows 1–6 have shifted columns (Concern cell = the chain-property "Verified" text, Severity cell = the pass-1 "Claimed" text, e.g. `\| C2 L250 "verb wrapper is kept"… \| gate-consistency kept; removed from 4.1/SC15 \| …`). doc_lint PASS on the file because `cell-vocabulary` binds only the first table under `## Concerns` — an instance of the plan's own declared-not-enforced class. | Delete the six shifted rows; consider extending `cell-vocabulary` to the Resolutions table's Severity column. |
| C4 | low-medium | measured: Issue 0.4 lists 018 inside merge group `002+003+018+036` (absorbed), while D-7 says "two ids (015, 018) are rewritten to describe what exists" (a survivor). EXP-001 line 50 says both. inferred: if 018 survives as rewritten, survivors = 23 and SC2's zero-slack ceiling is red on a correct tree. | State once where 018 goes (absorbed into the group-1 digest requirement, with its "re-preview" claim dropped as unimplemented) and make D-7's sentence match. |
| C5 | low | measured: `audit` emits four `[R]` findings on `findings/exp-00{1,2}.md` — missing sections `Approach Tested, Implications for Plan, Recommendations` and required pattern `\*\*(measured\|inferred):\*\*` absent (the files use unbolded `measured:`). Report-only; does not block intake. | Optional: bold the markers and add the three section headings so the findings match the schema they are graded against. |

## Missing
- Nothing measured beyond the above. All spot-checked `measured:` claims in plan.md reproduced (step 13). No `inferred:` premise an SC depends on was falsified by execution.

## Gate Assessment
- **allocated REQ ids are free** — measured exit 0 today; ONE-SHOT declared; no cycle.
- **plan-070 has landed** — measured exit 1 today (070 is `?? untracked`, not on `main`), which is the correct pre-070 state; decidable at execute start; blocks only 0.4/3.2. The Instructions carry the pass-2 hand-resolution note.
- **baseline suite is green** — measured: `test_land_apply.py`, `test_review_verdict.py`, `test_cli_enumeration.py` all exit 0 (plus `test_retrospective`, `test_gate_consistency`, `test_close_contract`, `test_review_agent_contract` exit 0). Reachable; Blocks covers every deleting issue.
- **Reconcile** — unchanged, R5 acknowledged.

## Upstream Assessment
Unchanged from pass 2; the #392 row (plan.md:72) records the D-10 and pass-1-C1 instances as claimed. C1 above (an SC whose command cannot discriminate) and C3 (a vocabulary check that binds one table) are two further `#392`/`#306`-class instances worth a clause in that row's In-list. No disposition changes required.

**Residue:** none in the repo. Only `--dry-run`/`--check` verbs were run against the bundle; scratch output went to the session scratchpad.

## Resolutions

**Status: all 5 resolved by the main session on 2026-09-10; pass 4 (execution) verifies.**

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 SC3 can never go green as written | high | SC3 grep now `-rhoEI` with `--exclude-dir=__pycache__`; row text notes it is an invariant (green today, red between 0.4 and 3.3, green after) | `main-session` | `resolved` |
| C2 `okf | medium | `okf.py reindex --write` run on the bundle before this pass file was written; index.md lists diagrams/, findings/, references/, reviews/ | `main-session` | `resolved` |
| C3 pass-2 | low-medium | The six shifted rows removed from pass-2.md's Resolutions table (they were chain-property rows the extractor mistook for concerns) | `main-session` | `resolved` |
| C4 Issue 0 | low-medium | 018 is absorbed into merge group 1 with its re-preview claim dropped; D-7 and EXP-001's recommendation line now say so | `main-session` | `resolved` |
| C5 `audit` emits four `[R]` findings on `findings/exp-00{1,2} | low | Findings files: markers bolded to `**measured:**`/`**inferred:**`, headings renamed to Approach Tested / Implications for Plan / Recommendations | `main-session` | `resolved` |
