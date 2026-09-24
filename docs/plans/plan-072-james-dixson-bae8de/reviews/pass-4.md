---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 4, execution] REVISE: all 32 prior resolutions re-verified and every checker green; 3 low concerns. CC spend misses subagent transcripts and two price classes, the false-FAIL formula doesn't match its figures, and FULL-row issues aren't ordered before the must-be-last eval row"
plan: plan-072-james-dixson-bae8de
pass: 4
mode: execution
---
# Plan Red-Team: plan-072-james-dixson-bae8de

## Verdict: REVISE
**Mode:** execution

## Strengths
- All five skill-shipped checkers exit 0: doc_lint, plan_extract `--strict`, gate_consistency, okf reindex `--check` and audit. Both repo checkers are now clean too. `check-req-coverage.py --min-issues 20` exits 0 (20 issues, 5.5 is `declared-bugfix`). `check_amendment_log.py` passes against a sandbox SPEC.md carrying the entry Issue 0.3 describes (exit 0, "5 amended id(s) … all 19 non-exempt … reach"). It fails correctly when one bullet is dropped (exit 1, `REQ-SCHEMA-002` missing). The checker can tell a correct entry from an incomplete one.
- All 13 clause-form Success Criteria are red before any work runs, and none is vacuously green. I also checked that they can turn green when the work is done:
  - SC7 exits 0 on a sandbox manifest with the flagged eval row last. It exits 1 when another row follows it.
  - SC16 exits 0 at $150 and at exactly $200. It exits 1 at $300 with no approved ceiling, and 0 at $300 once a $400 ceiling is recorded.
- The four allocated REQ ids appear nowhere outside plan-072. The current highest ids are SKAUTH-060, ENGINE-010 and YF-EMBED-006, so 061, 062, 011 and 007 are the next free ids.
- The pass-3 C5 transcript source holds on every run it was fitted to. For each of the 13 completed single-session CC runs, the deduplicated main-transcript totals equal `modelUsage` token for token. All 64 CC streams, including the 50 killed runs, have a transcript on disk. The stream/transcript output-count disagreement is real: 170 of 178 messages differ.
- One live call ($0.008) re-confirmed pass-2 C1's replacement: `Loaded 20 unique skills (… user: 0, project: 20 …)`, `permissionMode bypassPermissions`, 15 yf names in init.
- The spend-gate Test coerces `null`: a ledger of `null`, `0` and `150.5` exits 0, and a total of $400.5 exits 1. It exits 0 again once `spend-ceiling.txt` reads 500.

## Concerns
| # | Severity | Basis | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |
| C1 | low-medium | measured: python over `~/.cache/plan072-eval/raw/cc-*.jsonl` and `~/.claude/projects/-Users-james--cache-plan072-eval-clone-cc/` → exit 0. For `cc-D1-manual` the main `<sid>.jsonl` totals price to $0.288 against the recorded `costUSD` $0.673. The rest is in `<sid>/subagents/agent-*.jsonl`: 52,014 cache-write tokens, all `ephemeral_5m`, priced at $5.00/Mtok when solved from the residual. In the 13 eval runs, `costUSD` minus the three fitted classes leaves a residual of exactly $4.00/Mtok × `input_tokens` | **The ledger's CC USD misses subagent tokens, and its rate table lacks two price classes.** REQ-SKAUTH-062 reads only `~/.claude/projects/<slug>/<session-id>.jsonl`. When the model calls `Agent`, as the D1 run did at tool call 4, inside the 6-call cutoff, those tokens go to a sibling `subagents/` directory, and the ledger undercounts that run by 57%. The fitted table has one cache-write rate ($8, the 1h class) and no input rate. So "fitted exactly (max error 0.0)" is inaccurate: the residual is 4e-5 per run. Issue 2.3's exact-reproduction test would fail at that point, but nothing tests the subagent path or the 5m class. None of the 63 eval runs used `Agent`, so the practical exposure is small. It is still a way for D9's ceiling to under-enforce without anything going red. | In REQ-SKAUTH-062 and Issue 2.2, sum `<session-id>.jsonl` plus `<session-id>/subagents/*.jsonl`, each deduplicated by `message.id`. Price cache writes by `usage.cache_creation.ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens`. Add `input` ($4) and `cache_write_5m` ($5) to `trigger_eval_rates.json`. Add an Issue 2.3 fixture built from the D1-manual transcript pair, asserting $0.673. |
| C2 | low | measured: binomial in python → exit 0. The plan's formula 1 − (1 − P[≤2 of 6 correct])^N gives **2.05% / 26.3%** at N=240, p=0.95/0.90. The two-stage rule (≤1 of 3 correct, then ≤2 of 6 pooled) gives **1.65% / 21.9%** | **The false-FAIL formula doesn't produce the numbers printed beside it.** The ≈1.7% / 22% figures are the exact two-stage values, but the formula drops the first stage. `--report` is specified to print "the implied rate", and an implementer who codes the formula as written will print different numbers from those in the SPEC. | State the two-stage expression: Σ over a≤1, a+c≤2 of Bin(3,a)·Bin(3,c). Or keep the formula as a conservative upper bound and change the figures to ≈2.1% / 26%. |
| C3 | low | measured: DAG closure over the Epics `depends-on` lines → none of 0.3, 1.2, 2.3 is an ancestor of 2.5. SC7 spike: the eval row followed by one more FULL row → exit 1 | **Three issues that add FULL rows can close after the issue that must stay last.** 0.3 (`gate-plan072-*`), 1.2 (`frontmatter-tests`) and 2.3 (`trigger-eval-tests`) each add a FULL row. Nothing orders them before 2.5. If any of them appends at the end of the table, the precedent in the manifest, the eval row stops being last and SC7 goes red. The failure is loud, not silent, but it is a predictable rework loop. | Add `1.2, 2.3` to 2.5's `depends-on`. 0.3 is already satisfiable earlier, so it can be listed too. Or state in 0.3, 1.2 and 2.3 that FULL rows are inserted above the eval row. |

## Measurements
| Check | Command | Exit | Note |
| :-- | :-- | --: | :-- |
| doc_lint | `uv run $SKILL_DIR/scripts/doc_lint.py --path …/plan.md --json` | 0 | PASS, 0 findings, 2 files |
| plan_extract | `uv run $SKILL_DIR/scripts/plan_extract.py … --json --strict` | 0 | 1 plan, 26 top-level records |
| gate_consistency | `uv run $SKILL_DIR/scripts/gate_consistency.py … --json` | 0 | PASS, 6 gates, 4 evaluated |
| okf reindex | `uv run $SKILL_DIR/scripts/okf.py reindex --check … --json` | 0 | clean |
| audit | `uv run $SKILL_DIR/scripts/plan_manager.py audit … --json-output` | 0 | pass, okf_native |
| check-req-coverage | `uv run scripts/checks/check-req-coverage.py --min-issues 20 …` | 0 | 20 issues covered; 5.5 declared-bugfix |
| check-req-coverage (no floor) | same, without `--min-issues` | 0 | same result |
| check_amendment_log | `uv run scripts/check_amendment_log.py --plan plan-072-…` | 2 | INCONCLUSIVE: no plan-072 entry yet (expected) |
| amendment spike (full entry) | same, with `--spec <sandbox SPEC.md, entry naming all 5 ids>` | 0 | 5 ids covered, 19 reach |
| amendment spike (4 of 5) | same, with `REQ-SCHEMA-002` omitted | 1 | discriminates |
| SC1 | per cell | 1 | not-yet-dischargeable |
| SC1b | per cell | 1 | not-yet-dischargeable (`execute-base.txt` created in 0.1) |
| SC2 | per cell | 1 | not-yet-dischargeable (REQ grep guard) |
| SC3 | per cell | 2 | not-yet-dischargeable (1.2 creates the file) |
| SC4 | per cell | 1 | not-yet-dischargeable (was 0 at pass 3; now guarded) |
| SC5 | per cell | 2 | not-yet-dischargeable (2.3 names the file) |
| SC6 | per cell | 2 | not-yet-dischargeable (2.2 names the verbs) |
| SC7 | per cell | 1 | not-yet-dischargeable; spike 0 when the row is last and flagged, 1 when a row follows (C3) |
| SC8 | per cell | 1 | not-yet-dischargeable |
| SC9 | per cell | 2 | not-yet-dischargeable |
| SC10 | per cell | 2 | not-yet-dischargeable |
| SC13 | per cell | 1 | not-yet-dischargeable |
| SC16 | per cell | 1 | not-yet-dischargeable; spike 0/0/1/0/0 for $150 / $200 / $300 / $300 with ceiling 400 / null |
| SC11, SC12, SC14, SC15 | manual | n/a | not run |
| spend gate spike | the gate's Test in mktemp: null+0+150.5 / 400.5 / 400.5 with ceiling 500 | 0 / 1 / 0 | null coerced; holds |
| REQ id freedom | `grep -rlF <id>` outside plan-072, plus the highest existing ids | 0 | all four free and next in sequence |
| CC transcript vs modelUsage | python, 13 completed eval runs | 0 | token-exact match 13/13 |
| CC rate fit residual | python, `costUSD` − (8·cw + 0.2·cr + 20·out)/1e6 | 0 | residual = $4/Mtok × input on all 13 (C1) |
| CC subagent run | python, `cc-D1-manual` main vs `subagents/` transcripts | 0 | main $0.288 vs `costUSD` $0.673; 52,014 5m-write tokens at $5/Mtok (C1) |
| Agent use in eval runs | python tool-name count over 63 CC eval streams | 0 | 0 `Agent`/`Task` calls; exposure small |
| stream vs transcript output | python, 178 messages | 0 | 170 differ; the transcript is the right source |
| false-FAIL recompute | binomial, N=240 | 0 | formula 2.05%/26.3%; two-stage 1.65%/21.9% (C2) |
| DAG closure | python over Epics `depends-on` | 0 | 0.3, 1.2, 2.3 are not ancestors of 2.5 (C3) |
| CC load line (live) | `claude -p "Reply ok." --setting-sources project --permission-mode bypassPermissions … --debug-file` in clone-cc, 20 staged | 0 | `user: 0, project: 20`; bypassPermissions; 15 yf in init; $0.0082. Staging removed |
| residue | `git status --porcelain` (repo; clone-cc) | 0 | repo: only the pre-existing `.beads.gate.lock`; clone-cc: empty; mktemp dirs removed |

**Prior-resolution re-verification**

| Pass·Concern | Evidence run | Result |
| :-- | :-- | :-- |
| p1 C1 | `grep -cF -- '--mode candidate --skills all --harness both --reps 3' plan.md` → 2 | measured: holds |
| p1 C2 | grep `pooled 6-rep rate` → 1; binomial recompute | measured: holds (formula wording is C2) |
| p1 C3 | grep `**unrouted**` → 2 | measured: holds |
| p1 C4 | grep `scripts/checks/fixtures/trigger-eval/` → 1 | measured: holds; 115,167-byte count not re-derived (inferred) |
| p1 C5 | grep `staging root is an explicit` → 1 | measured: holds |
| p1 C6 | grep `--permission-mode bypassPermissions` → 2; live init `bypassPermissions` | measured: holds |
| p1 C7 | grep `` `timeout` 21600 `` → 1; SC7 spike exit 0 | measured: holds |
| p1 C8 | grep: line 104 shows 2.4 h only as the pre-correction figure | measured: holds (pass-3 recompute of 31.4/21.8 s stands) |
| p1 C9 | SC2 → exit 1 on the untouched tree | measured: holds |
| p1 C10 | grep `In one change-set` → 1 | measured: holds |
| p1 C11 | grep `sha256 of every staged file` → 1 | measured: holds |
| p1 C12 | grep `staging is cleared on reset` → 1 | measured: holds |
| p1 C13 | grep ``Only an explicit `--record` run writes it`` → 1 | measured: holds |
| p1 C14 | grep `UTF-16` → 4 | measured: holds |
| p2 C1 | live call: `user: 0, project: 20`, 15 yf in init | measured: holds |
| p2 C2 | grep `stderr only` → 2 | measured: holds |
| p2 C3 | grep `inconclusive-exit=4` → 5 | measured: holds |
| p2 C4 | grep `assets/spend.jsonl` → 2 | measured: holds |
| p2 C5 | spend gate spike 0 / 1 / 0 | measured: holds |
| p2 C6 | grep `every intent of each skill that lists it as a sibling` → 1 | measured: holds |
| p2 C7 | `grep -nE 'three-tier\|crisp/satisfactory/loose\|2\.4 h'` → only line 104, framed as pre-correction | measured: holds |
| p2 C8 | grep `pi reports tokens only` → 1 | measured: holds |
| p2 C9 | grep `installed mode only` → 2 | measured: holds |
| p2 C10 | grep `pays for FULL **twice**` → 1 | measured: holds |
| p3 C1 | `check-req-coverage.py --min-issues 20` → 0, 5.5 `declared-bugfix`; amendment spike → 0 | measured: holds |
| p3 C2 | amendment spike: full entry → 0, 4-of-5 → 1; grep `one bullet per Epic-0 id`, `gate-plan072-amendment`, `gate-plan072-reqcoverage` → 1 each | measured: holds |
| p3 C3 | SC4 → exit 1 before work | measured: holds |
| p3 C4 | Epics-section grep: all five verbs and `scripts/checks/test_skill_trigger_eval.py` present | measured: holds |
| p3 C5 | transcript = `modelUsage` on 13/13; gate coerces null | measured: holds for single-session runs; incomplete for subagent runs and two price classes (C1) |
| p3 C6 | SC16 spike 0/0/1/0 | measured: holds |
| p3 C7 | recompute: figures match the two-stage rule, not the stated formula | measured: holds for the figures; the formula is inconsistent (C2) |
| p3 C8 | SC7 spike: 0 last+flagged, 1 when a row follows | measured: holds |

## Missing
- Subagent transcripts and the 5m-cache/input price classes in the CC spend derivation (C1).
- Ordering between the issues that add FULL rows and Issue 2.5 (C3).
- inferred (low, non-blocking): CHANGE-VALIDATION §1 warns that a row reading an in-flight plan's `docs/plans/<id>/` path is not satisfiable from an execute *worktree*. The `gate-plan072-*` rows are satisfiable here only because `execute.worktree: false`, which I measured in `.yf/plan/config.local.json`. A one-line note in 0.3 would stop a later reader from treating that as a violation.

## Gate Assessment
- **Harness-auth gate:** not re-run; the live `claude -p` call above exited 0. It is frontloaded and blocks 3.1, 3.2 and 2.5. Sound.
- **Spend-ceiling gate:** the probe measured correct on null, over-ceiling and raised-ceiling ledgers, and it can be decided at any point in Epic 3. Its accuracy depends on the ledger's USD figure, which C1 shows can undercount runs that dispatch a subagent.
- **Split-decisions gate:** mid-DAG by necessity, and it covers accepted misses. Sound.
- **Upstream-writes gate:** class-level consent, frontloaded, and it covers 4.2, 5.4, 5.5 and 5.6. Sound.

## Upstream Assessment
- #407 (include): resolved by 0.3, 1.1 and 3.2. Correct.
- #302 (exclude, with an evidence comment in 5.5): 5.5's exemption now satisfies both SPEC-first checkers (measured). Sound.
- #189 (exclude): justified.
- The follow-ons 5.4 and 5.6 are correctly out of scope and covered by the upstream-writes gate.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | low-medium | | | unresolved |
| C2 | low | | | unresolved |
| C3 | low | | | unresolved |
