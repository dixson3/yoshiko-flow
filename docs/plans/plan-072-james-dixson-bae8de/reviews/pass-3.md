---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 3, execution] REVISE: all 24 prior resolutions re-verified; 8 concerns, none high. The ledger's CC USD source would undercount (killed runs emit no result event), Issue 5.5 fails both SPEC-first checkers, four SCs depend on flags the Epics never create, and SC4 is green before any work"
plan: plan-072-james-dixson-bae8de
pass: 3
mode: execution
---
# Plan Red-Team: plan-072-james-dixson-bae8de

## Verdict: REVISE
**Mode:** execution

## Strengths
- All five bundle checkers that exist in the skill exit 0: doc_lint, plan_extract `--strict`, gate_consistency, okf reindex `--check` and audit.
- I re-verified all 24 prior `resolved` cells, and every one holds. The pass-2 C1 replacement was checked with one live call. I staged the 20 repo skills at `clone-cc/.claude/skills/` and ran with `--setting-sources project --permission-mode bypassPermissions --debug-file`. The debug log read `Loaded 20 unique skills (… user: 0, project: 20 …)`, init `permissionMode` was `bypassPermissions`, and init `skills` held 15 yf names. That matches the Approach text exactly.
- The spend-gate probe behaves as designed on an empty ledger (exit 0), a ledger just over the limit ($199.99 + $0.02, exit 1) and a $500 ledger (exit 1).
- The corrected D3 per-run figures reproduce from the bundled `run-*.jsonl`: CC is 20.4 s per trigger run and 42.5 s per near-miss run, so 31.4 s at a 50/50 mix. pi is 9.8 s and 33.9 s, so 21.8 s.
- `_validate_merged` turns every engine status other than `pass` into `fail` (`plan_manager.py`, the `result["status"] = "pass" if eng_status == "pass" else "fail"` line). `_change_validation_script` resolves the in-tree `skills/yf-change-validation` engine first, so at L3 the merged tree's engine, which will carry REQ-ENGINE-011, is the one that runs.
- Most Success Criteria are red before execution, as expected. The one exception is C3.

## Concerns
| # | Severity | Basis | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |
| C1 | medium | measured: `uv run scripts/checks/check-req-coverage.py docs/plans/plan-072-…` → exit 1, `5.5  UNCOVERED`; a sandbox copy of SPEC.md with a complete plan-072 entry, then `uv run scripts/check_amendment_log.py --plan plan-072-… --spec <copy>` → exit 1, `A2 … no depends-on path … ['5.5']` | **Issue 5.5 fails both repo SPEC-first checkers, and it would still fail after execution.** Its only dependency is 0.1, which names no REQ. Its text names no REQ and carries neither the declared bug-fix phrase nor a `no-req-required` declaration. This failure does not depend on anything execution produces. It is a defect in the plan text now. | Declare 5.5 exempt in both vocabularies. Add `**No new REQ**: bookkeeping comment on #302 (no-req-required)` to its body, and add a plan-level `` `no-req-required` {5.5} `` line. `exempt = declared or BASELINE` replaces the baseline set, which is harmless here because this plan has no 4.6 or 4.7. |
| C2 | medium | measured: sandbox SPEC.md whose plan-072 entry names only `REQ-YF-EMBED-007` → `check_amendment_log.py` exit 1, `amended without an amendment-log bullet: REQ-ENGINE-011, REQ-SCHEMA-002, REQ-SKAUTH-061, REQ-SKAUTH-062` | **The Epics text puts four of the five amendment bullets where the checker cannot see them.** A1 derives its id set from every REQ named in an Epic-0 body, which gives five ids including `REQ-SCHEMA-002` from 0.6. It then reads only the root `SPEC.md` plan-072 entry. Issues 0.4 and 0.6 place their amendment entries in the skill SPECs. Issue 0.3's root entry "cites #407", and 0.5's root line records only the FULL row. Precedent is to name skill-SPEC ids in the root entry: the plan-06x root entries cite `REQ-SCHEMA-002` and `REQ-ENGINE-008`. | In 0.3, state that the root `SPEC.md` plan-072 entry carries a bullet for each of the five ids, pointing to the skill SPEC that owns the text. Optionally add `gate-plan072-amendment` and `gate-plan072-reqcoverage` rows, following the plan-060 to 067 precedent. |
| C3 | medium | measured: SC4 `uv run skills/yf-change-validation/scripts/test_change_validation.py` → exit 0 before any work (30 existing tests) | **SC4 is already green (#384).** Issue 2.1 adds tests to an existing, passing file, so the criterion cannot tell 2.1's work from the prior state of the repo. | Prefix SC4 with a clause the work creates, e.g. `grep -q 'inconclusive-exit' skills/yf-change-validation/scripts/test_change_validation.py && grep -q 'REQ-ENGINE-011' skills/yf-change-validation/scripts/change_validation.py && uv run …test_change_validation.py`. |
| C4 | medium | measured: `grep -n -F -- '<flag>' plan.md` for `--min-trigger`, `--min-nearmiss`, `--require-rated`, `--forbid`, `--require-decision-for-noncrisp` and `test_skill_trigger_eval` → found only on SC lines 404–409, never in Epics | **SC5, SC6, SC9 and SC10 depend on a path and on flags that the Epics text never creates.** Issue 2.2 lists the harness's flags explicitly, and that list omits all five flags above. Issue 2.3 never names `scripts/checks/test_skill_trigger_eval.py`. A harness built to the Epics text would make SC6, SC9 and SC10 fail with an argparse usage error (exit 2), and SC5 would fail with a spawn error. | Add the five flags to Issue 2.2's list, with their semantics: `--report` computes the rating from `triggers.json`, and `--forbid` takes rating names. Name the test file path in Issue 2.3. |
| C5 | medium-high | measured: over `~/.cache/plan072-eval/run-cc.jsonl`, 50 of 63 CC runs have `cost_usd: null` (all 39 `target` stops and all 11 `max_tools` stops). In `raw/cc-*.jsonl`, 50 of 64 streams have no `result` event, and 161 of 353 assistant `usage` events repeat an earlier `message.id` with identical values. `assets/exp-003/runner.py:87` reads `total_cost_usd`. In a sandbox, the spend-gate Test on a `{"cc_usd": null}` ledger raises `TypeError` → exit 1 | **The D9 ledger's USD source is unspecified, and both obvious implementations are wrong.** Issue 2.2 is "promoted from runner.py", which takes cost from the `result` event. Runs killed at activation, the normal case, emit no `result` event, so the ledger would record about 21% of the real CC spend and the $200 ceiling would effectively never trip. The operator's decision would then go unenforced while every check reads green. Summing assistant `usage` naively overcounts instead, because duplicated events are about 46% of the total. Separately, the gate Test's `.get('cc_usd', 0)` guards only a missing key. A pi row written as `cc_usd: null` crashes the gate. It fails closed, but the operator gets a traceback that looks like "at the ceiling". | In REQ-SKAUTH-062 and Issue 2.2, specify that CC USD is computed from per-message `usage`, deduplicated by `message.id`, times the published list rates, and is never taken from `total_cost_usd`. pi rows write `cc_usd: 0`. In Issue 2.3, add a fixture with a killed run and duplicated message ids, and assert the deduplicated token total. Make the gate Test coerce `None` to 0. |
| C6 | low-medium | measured: sandbox ledger `{"cc_usd": 500}`, then SC16 `test -s …/spend.jsonl` → exit 0 | **SC16 reports "stayed within the approved ceiling" but only checks that the ledger is non-empty.** A ledger that ran $300 past a ceiling nobody approved passes. | Use the spend gate's own probe as SC16's command (it reads `spend-ceiling.txt`), or reword the criterion to "ledger exists". |
| C7 | low | measured: binomial recompute over 240 cells → 1.65% at 95% per-run reliability, 21.9% at 90% | The stated false-FAIL rates (~2% and ~26%) do not name the number of cells they assume. 26% corresponds to about 290 cells. Issue 2.4 allows 6 or more intents per skill, so the real cell count is not fixed, and the rate that goes into REQ-SKAUTH-062 is wrong for 240 cells. | State the rate as a function of cell count, e.g. "≈1.7%/22% at 240 cells", and have `--report` print the real cell count. |
| C8 | low | inferred: SC7's command is a single `grep -F` for the row's command string | SC7's criterion says the row is "last, streamed, with a timeout", but the grep would also pass if the row sat in FAST, anywhere in the list, with no flags or timeout. | Extend SC7 to parse §1 `full` and check that the last row carries `inconclusive-exit=4,stream` and `21600`, or narrow the criterion's wording to what the grep checks. |

## Measurements
| Check | Command | Exit | Note |
| :-- | :-- | --: | :-- |
| doc_lint | `uv run $SKILL_DIR/scripts/doc_lint.py --path …/plan.md --json` | 0 | PASS, 0 findings |
| plan_extract | `uv run $SKILL_DIR/scripts/plan_extract.py … --json --strict` | 0 | 6 epics |
| gate_consistency | `uv run $SKILL_DIR/scripts/gate_consistency.py … --json` | 0 | PASS, 6 gates, 4 evaluated |
| check_amendment_log | `uv run scripts/check_amendment_log.py --plan plan-072-james-dixson-bae8de` | 2 | INCONCLUSIVE: no plan-072 entry yet (expected before execution) |
| amendment_log spike (full entry) | same command with `--spec <sandbox SPEC.md naming all 5 ids>` | 1 | A2 fails on 5.5 (C1) |
| amendment_log spike (Epics-text entry) | same command with the sandbox entry naming only EMBED-007 | 1 | A1 is missing 4 ids (C2) |
| check-req-coverage | `uv run scripts/checks/check-req-coverage.py …/plan-072…` | 1 | 5.5 UNCOVERED (C1) |
| okf reindex | `uv run $SKILL_DIR/scripts/okf.py reindex --check … --json` | 0 | clean |
| audit | `uv run $SKILL_DIR/scripts/plan_manager.py audit … --json-output` | 0 | pass |
| SC1 | per cell | 1 | not-yet-dischargeable |
| SC1b | per cell | 1 | not-yet-dischargeable (`execute-base.txt` is absent; created in 0.1) |
| SC2 | per cell | 1 | not-yet-dischargeable (the REQ grep guard works) |
| SC3 | per cell | 2 | not-yet-dischargeable (1.2 creates the file) |
| SC4 | per cell | 0 | **green before any work** (C3) |
| SC5 | per cell | 2 | spawn error; the path is not named in Epics (C4) |
| SC6 | per cell | 2 | the script is absent; the flags are not in 2.2 (C4) |
| SC7 | per cell | 1 | not-yet-dischargeable |
| SC8 | per cell | 1 | not-yet-dischargeable |
| SC9 | per cell | 2 | the script is absent; the flags are not in 2.2 (C4) |
| SC10 | per cell | 2 | the script is absent; the flag is not in 2.2 (C4) |
| SC11, SC12, SC14, SC15 | manual | n/a | not run |
| SC13 | per cell | 1 | not-yet-dischargeable |
| SC16 | per cell | 1 | not-yet-dischargeable; passes on an over-ceiling ledger (C6) |
| spend gate Test | the gate's `python3 -c …` in the repo | 0 | empty ledger → below the ceiling |
| spend gate spike | the same Test in mktemp: null / missing key / 199.99+0.02 / 500 | 1 / 0 / 1 / 1 | a null value crashes with TypeError (C5) |
| CC cost source | python scan of `run-cc.jsonl` and `raw/cc-*.jsonl` | 0 | 50/63 costs null; 161/353 usage events duplicated (C5) |
| D3 per-run recompute | python over bundled `assets/exp-003/run-{cc,pi}.jsonl` | 0 | CC 31.4 s, pi 21.8 s: holds |
| false-FAIL recompute | binomial, 240 cells | 0 | 1.65% / 21.9% (C7) |
| CC load line (live 1) | `claude -p "Reply ok." --setting-sources project --permission-mode bypassPermissions … --debug-file` | 0 | **void**: BSD `cp -R dir/` staged the directories' contents, so `project: 0`. $0.18 |
| CC load line (live 2) | the same command, with 20 skills staged correctly | 0 | `user: 0, project: 20`, `bypassPermissions`, init shows 15 yf names. $0.008. Staging removed; `git status` of clone-cc is empty |
| prior-pass resolution greps | `grep -F` in plan.md for each of the 22 text-edit resolution anchors | 0 | all present |
| residue | `git status --porcelain` (repo) | 0 | only the pre-existing `.beads.gate.lock` |

**Prior-pass resolution re-verification**

| Pass·Concern | Evidence run | Result |
| :-- | :-- | :-- |
| p1 C1 | `grep -F '--mode candidate --skills all --harness both --reps 3' plan.md` | measured: holds |
| p1 C2 | grep `pooled 6-rep rate`, plus binomial recompute | measured: holds (the rate figure is C7) |
| p1 C3 | grep `**unrouted**` | measured: holds |
| p1 C4 | grep `scripts/checks/fixtures/trigger-eval/` | measured: holds. The 115,167-byte count was not re-derived, so that part is inferred |
| p1 C5 | grep `staging root is an explicit` | measured: holds |
| p1 C6 | grep `--permission-mode bypassPermissions`, plus live call 2 showing init `bypassPermissions` | measured: holds |
| p1 C7 | grep ``timeout` 21600``; read of `_validate_merged` (non-pass → fail) | measured: holds |
| p1 C8 | recompute from bundled run files: 31.4 / 21.8 s | measured: holds |
| p1 C9 | grep of the SC2 guard; SC2 → exit 1 | measured: holds |
| p1 C10 | grep `In one change-set` | measured: holds |
| p1 C11 | grep `sha256 of every staged file` | measured: holds |
| p1 C12 | grep `staging is cleared on reset` | measured: holds |
| p1 C13 | grep ``Only an explicit `--record` run writes it`` | measured: holds |
| p1 C14 | grep `UTF-16` (4 hits) | measured: holds |
| p2 C1 | live call 2: `user: 0, project: 20`, init 15 yf | measured: holds |
| p2 C2 | grep `stderr only` | measured: holds |
| p2 C3 | grep `inconclusive-exit=4` (4 hits) | measured: holds |
| p2 C4 | grep `assets/spend.jsonl` | measured: holds (the cost source is C5) |
| p2 C5 | the spend gate Test: 0 on an empty ledger, 1 over the ceiling | measured: holds |
| p2 C6 | grep `every intent of each skill that lists it as a sibling` | measured: holds |
| p2 C7 | grep for `three-tier`, `crisp/satisfactory/loose`, `2.4 h` | measured: holds. One hit remains, at line 104, and it is framed as the pre-correction figure |
| p2 C8 | grep `pi reports tokens only` | measured: holds |
| p2 C9 | grep `installed mode only` | measured: holds |
| p2 C10 | grep `pays for FULL **twice**` | measured: holds |

## Missing
- How the ledger's CC USD figure is derived, given that killed runs emit no `result` event (C5).
- A declared REQ exemption for Issue 5.5 (C1), and a root-SPEC amendment bullet for each of the five Epic-0 ids (C2).
- An Epics-level home for the harness's `--report`, `--forbid`, `--require-*` and `--min-*` flags and for its test file (C4).
- The plan adds no `gate-plan072-*` recipe rows, which the plan-060 to 067 plans carry. That is optional, but without them C1 and C2 would be caught only by a review pass.

## Gate Assessment
- **Harness-auth gate:** not re-run, to save live spend. Pass 2 measured it valid. It blocks 3.1, 3.2 and 2.5, and is frontloaded. Sound.
- **Spend-ceiling gate:** the probe works and can be decided at any point in Epic 3. Its soundness depends on the ledger's USD figure, which is C5. As things stand it would read green under an undercounting ledger and crash on a null `cc_usd` value.
- **Split-decisions gate:** placed mid-DAG by necessity. It covers accepted misses. Sound.
- **Upstream-writes gate:** a consent for classes of write, frontloaded, covering 4.2, 5.4, 5.5 and 5.6. Sound.

## Upstream Assessment
- #407 (include): resolved by 0.3, 1.1 and 3.2. Correct.
- #302 (exclude, with an evidence comment in 5.5): the disposition is sound, but 5.5 needs the REQ-exemption declaration (C1).
- #189 (exclude): justified.
- The follow-ons 5.4 and 5.6 are correctly out of scope and are covered by the upstream-writes gate.

## Resolutions

**Status: all 8 resolved by the main session on 2026-09-24, each with measured evidence. None changes an operator decision. The Missing items (cost source, 5.5 exemption, root bullets, verb home, gate rows) are covered by C5, C1, C2, C4 and C2. Pass 4 is an execution pass.**

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | medium | Issue 5.5 now carries `**No new REQ**: … (no-req-required)`, and a plan-level `` `no-req-required` {5.5} `` declaration sits above Epic 0. measured: `check-req-coverage.py --min-issues 20` → exit 0, and 5.5 is `declared-bugfix`. | `main-session` | resolved |
| C2 | medium | Issue 0.3 now requires the root plan-072 entry to carry one bullet per Epic-0 id (5), each pointing to its owning skill SPEC, and it adds `gate-plan072-amendment` and `gate-plan072-reqcoverage` rows (FAST+FULL) with §3 scope. measured: `check_amendment_log.py --spec <sandbox with that entry>` → exit 0, "5 amended id(s) all carry … all 19 non-exempt … reach". This removed a stray `REQ-ENGINE-008` mention the check had picked up from the plan's own precedent note. | `main-session` | resolved |
| C3 | medium | SC4 is prefixed with `grep -q REQ-ENGINE-011 change_validation.py && grep -q inconclusive-exit test_change_validation.py`, so it is red before any work. | `main-session` | resolved |
| C4 | medium | Issue 2.2 lists the offline verbs `--validate-intents --min-trigger --min-nearmiss`, `--report`, `--require-rated`, `--forbid` and `--require-decision-for-noncrisp` with their semantics. Issue 2.3 names `scripts/checks/test_skill_trigger_eval.py`, and each verb gets a violating-fixture test. | `main-session` | resolved |
| C5 | medium-high | The CC token source is the session **transcript** (`--session-id`, read after exit, deduplicated by `message.id`). It is never `result` and never the raw stream. measured: stream 8 output vs transcript 204 for the same message, and SIGINT/SIGTERM both yield no `result`. USD = tokens × per-class rates fitted **exactly** (max err 0.0) from the 13 recorded `modelUsage.costUSD`: $8/Mtok cache-write, $0.20 cache-read, $20 output. They are stored in `trigger_eval_rates.json`; an unknown model → INCONCLUSIVE. `cc_usd` is never null. The gate Test coerces `None` → 0. Issue 2.3 adds killed-run, duplicated-id and rate-reproduction fixtures. | `main-session` | resolved |
| C6 | low-medium | SC16 now runs the ledger-vs-ceiling probe as well as `test -s`. Discharged by 3.0 and 3.3. | `main-session` | resolved |
| C7 | low | The false-FAIL rate is restated as the formula 1 − (1 − P[≤2/6 correct])^N, ≈1.7%/22% at N=240, and `--report` prints the real N and rate. R3 is updated to match. | `main-session` | resolved |
| C8 | low | SC7 now parses the `### full` table and requires its **last** row to carry the command, `inconclusive-exit=4`, `stream` and `21600`, written without `|` characters so it fits the table. measured: exit 1 today, 0 with the row last and flagged, 1 without the flags, 1 when another row follows it. | `main-session` | resolved |
