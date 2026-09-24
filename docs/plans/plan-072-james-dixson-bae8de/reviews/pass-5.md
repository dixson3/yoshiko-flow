---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 5, execution] APPROVE: zero measured findings. All 35 prior resolutions re-verified by running their evidence; every checker green; all 13 clause-form SCs red pre-work and shown dischargeable; CC pricing exact (5.6e-17) including subagents"
plan: plan-072-james-dixson-bae8de
pass: 5
mode: execution
---
# Plan Red-Team: plan-072-james-dixson-bae8de

## Verdict: APPROVE
**Mode:** execution

## Strengths
- All five skill-shipped checkers exit 0: doc_lint, plan_extract `--strict`, gate_consistency, okf reindex `--check` and audit.
- Both repo checkers behave as intended:
  - `check-req-coverage.py --min-issues 20` exits 0. It covers 20 issues: 2 direct, 14 transitive, 5 name a REQ, and 1 (5.5) is `declared-bugfix`.
  - `check_amendment_log.py` is INCONCLUSIVE (exit 2) on the live tree, which is expected before execution. Against a sandbox SPEC.md carrying the entry Issue 0.3 describes (one bullet for each of the 5 ids) it exits 0. It exits 1 when `REQ-SCHEMA-002` is dropped, and exits 1 again when `REQ-YF-EMBED-007` is dropped. So it can tell a complete entry from an incomplete one in two positions.
- All 13 clause-form Success Criteria are red before any work runs. None passes on the untouched tree. SC7 and SC16 can also turn green when the work is done: SC7 exits 0 when the eval row is last and 1 when another row follows it. SC16 exits 0/0/1/0 for a $150 ledger, a $200 ledger, a $300 ledger with no ceiling file, and a $300 ledger with a $400 ceiling.
- The pass-4 C1 pricing is exact. The rates (input 4, cache-write 1h 8, cache-write 5m 5, cache-read 0.2, output 20 per Mtok) reproduce all 13 `modelUsage.costUSD` values to within 5.6e-17. Each completed run's transcript (main plus `subagents/`, deduplicated by `message.id`) matches its recorded `total_cost_usd` to within 5.6e-17. For D1-manual (session 6c33c43e…), the main transcript prices to $0.2878 and the subagent to $0.3854. The total, $0.6732, equals the recorded $0.6731752 (difference −1.1e-16). All 63 CC eval streams have a transcript on disk.
- The pass-4 C2 formula is correct. The two-stage q = Σ_{a≤1}Σ_{c≤2−a} Bin(3,p)(a)·Bin(3,p)(c) gives 0.0165 at N=240, p=0.95, and 0.2186 at p=0.90. These match the plan's ≈1.65% / 21.9% and Issue 2.3's 0.0165 ± 0.0005. None of the stale figures (≈1.7%, ~2%, 26%, 2.05%, 26.3%) remain in plan.md.
- The pass-4 C3 ordering holds. plan_extract reports 40 edges. The DAG ancestors of 2.5 are {0.1, 0.2, 0.3, 0.5, 0.6, 1.1, 1.2, 2.1, 2.2, 2.3, 2.4}, which includes every issue that adds a FULL row (0.3, 1.2, 2.3). The only other issue that mentions FULL is 5.2, and it runs FULL rather than adding a row; it is a descendant of 2.5, which is correct.

## Concerns
| # | Severity | Basis | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |

(none: this execution pass has zero `measured:` findings.)

## Measurements
| Check | Command | Exit | Note |
| :-- | :-- | --: | :-- |
| doc_lint | `uv run $SKILL_DIR/scripts/doc_lint.py --path …/plan.md --json` | 0 | PASS, 0 findings, 2 files |
| plan_extract | `uv run $SKILL_DIR/scripts/plan_extract.py … --json --strict` | 0 | 1 plan, 26 issues, 40 edges |
| gate_consistency | `uv run $SKILL_DIR/scripts/gate_consistency.py … --json` | 0 | PASS, 6 gates, 4 evaluated |
| okf reindex | `uv run $SKILL_DIR/scripts/okf.py reindex --check … --json` | 0 | clean (0 ghost / 0 missing / 0 empty-dir) |
| audit | `uv run $SKILL_DIR/scripts/plan_manager.py audit … --json-output` | 0 | pass, okf_native |
| check-req-coverage | `uv run scripts/checks/check-req-coverage.py --min-issues 20 <plan_dir>` | 0 | 20 covered; 5.5 declared-bugfix |
| check-req-coverage (no floor) | same, without `--min-issues` | 0 | same |
| check_amendment_log | `uv run scripts/check_amendment_log.py --plan plan-072-…` | 2 | INCONCLUSIVE: no plan-072 entry yet (expected) |
| amendment spike (all 5 ids) | same, `--spec <mktemp SPEC.md + plan-072 entry>` | 0 | "5 amended id(s) … all 19 non-exempt … reach" |
| amendment spike (no SCHEMA-002) | same | 1 | FAIL names `REQ-SCHEMA-002` |
| amendment spike (no YF-EMBED-007) | same | 1 | FAIL names `REQ-YF-EMBED-007` |
| SC1 | per cell, `bash -c` | 1 | not-yet-dischargeable |
| SC1b | per cell | 1 | not-yet-dischargeable (0.1 creates `execute-base.txt`) |
| SC2 | per cell | 1 | not-yet-dischargeable (REQ grep guard) |
| SC3 | per cell | 2 | not-yet-dischargeable (1.2 creates the test file) |
| SC4 | per cell | 1 | not-yet-dischargeable (REQ/flag grep guard) |
| SC5 | per cell | 2 | not-yet-dischargeable (2.3 creates the file) |
| SC6 | per cell | 2 | not-yet-dischargeable (2.2 creates the script) |
| SC7 | per cell | 1 | not-yet-dischargeable; spike: 0 when last and flagged, 1 when a row follows |
| SC8 | per cell | 1 | not-yet-dischargeable |
| SC9 | per cell | 2 | not-yet-dischargeable |
| SC10 | per cell | 2 | not-yet-dischargeable |
| SC13 | per cell | 1 | not-yet-dischargeable |
| SC16 | per cell | 1 | not-yet-dischargeable; spike 0/0/1/0 ($150 / $200 / $300 / $300 with ceiling 400) |
| SC11, SC12, SC14, SC15 | manual | n/a | not runnable by design |
| spend-gate Test | the gate's Test in mktemp: absent / null+0+150.5 / 400.5 / 400.5 with ceiling 500 | 0/0/1/0 | null coerced; ceiling override honoured |
| CC rates vs modelUsage | python, 13 `modelUsage` entries over `raw/cc-*-[0-9]*.jsonl` | 0 | max abs err 5.55e-17; one model, `claude-opus-5-5` |
| CC transcripts vs costUSD | python, main + `subagents/`, deduplicated by `message.id` | 0 | 63 streams, 0 transcripts missing; 13 completed runs, max err 5.55e-17 |
| D1-manual pair | python, session from init `6c33c43e-5688-46fb-b7e3-8f20dc203dce` | 0 | main $0.2878 + subagent $0.3854 = $0.6732 vs recorded $0.6731752 |
| false-FAIL, two-stage | binomial, N=240 | 0 | p=0.95 → 0.0165; p=0.90 → 0.2186 |
| DAG ancestry of 2.5 | python over plan_extract edges | 0 | 0.3, 1.2, 2.3 all ancestors; 5.2 is a descendant |
| EXP-003 totals | python over `rescored.json` | 0 | CC 59/63, pi 57/63 (the Issue 2.3 assertions) |
| cost-model inputs | python over `run-{cc,pi}.jsonl` | 0 | CC trigger 20.4 s / near-miss 42.5 s → 31.4 s at a 50/50 mix; pi 9.8 / 33.9 → 21.8 s; 14%-mix means 23.6 / 13.3 s |
| REQ id freedom | `grep -rlF <id>` outside plan-072; highest existing ids | 0 | all four ids free; highest existing are YF-EMBED-006, SKAUTH-060, ENGINE-010 |
| in-place mode | `.yf/plan/config.local.json` | 0 | `{"execute.worktree": false}` |
| residue | `git status --porcelain` (repo); `clone-cc/.claude` | 0 | repo: only the pre-existing `.beads.gate.lock`; clone-cc staging empty; mktemp dirs and `/tmp/pe72.json` removed |

**Prior-resolution re-verification**

| Pass·Concern | Evidence run | Result |
| :-- | :-- | :-- |
| p1 C1 | count of `--mode candidate --skills all --harness both --reps 3` in plan.md → 2; SC7 spike exit 0 | measured: holds |
| p1 C2 | `pooled 6-rep rate` → 1; two-stage recompute 0.0165 / 0.2186 | measured: holds |
| p1 C3 | `**unrouted**` → 2 | measured: holds |
| p1 C4 | `scripts/checks/fixtures/trigger-eval/` → 1; `rescored.json` totals 59/63 and 57/63 | measured: holds; 115,167-byte size not re-derived (inferred) |
| p1 C5 | `staging root is an explicit` → 1 | measured: holds |
| p1 C6 | `--permission-mode bypassPermissions` → 2 | measured: holds (no new live init call) |
| p1 C7 | `` `timeout` 21600 `` → 1; SC7 spike 0/1 | measured: holds |
| p1 C8 | `run-*.jsonl` recompute: 31.4 s and 21.8 s at a 50/50 mix; line 104 shows 2.4 h only as the pre-correction figure | measured: holds |
| p1 C9 | SC2 → exit 1 on the untouched tree; guard grep present | measured: holds |
| p1 C10 | `In one change-set` → 1 | measured: holds |
| p1 C11 | `sha256 of every staged file` → 1 | measured: holds |
| p1 C12 | `staging is cleared on reset` → 1 | measured: holds |
| p1 C13 | ``Only an explicit `--record` run writes it`` → 1 | measured: holds |
| p1 C14 | `UTF-16` → 4 | measured: holds |
| p2 C1 | `user: 0, project: <N>` → 2 | measured: holds in text; live load line not re-run this pass (pass-4 live measurement stands), inferred |
| p2 C2 | `stderr only` → 2 | measured: holds |
| p2 C3 | `inconclusive-exit=4` → 5 | measured: holds |
| p2 C4 | `assets/spend.jsonl` → 2 | measured: holds |
| p2 C5 | spend-gate Test spike 0/0/1/0 | measured: holds |
| p2 C6 | `every intent of each skill that lists it as a sibling` → 1 | measured: holds |
| p2 C7 | `three-tier\|crisp/satisfactory/loose` → 0; `2.4 h` only on line 104, framed as pre-correction | measured: holds |
| p2 C8 | `pi reports tokens only` → 1 | measured: holds |
| p2 C9 | `installed mode only` → 2 | measured: holds |
| p2 C10 | `pays for FULL **twice**` → 1 | measured: holds |
| p3 C1 | `check-req-coverage.py --min-issues 20` → 0, 5.5 `declared-bugfix`; `` `no-req-required` {5.5} `` → 1 | measured: holds |
| p3 C2 | amendment spikes 0 / 1 / 1; `one bullet per Epic-0 id`, `gate-plan072-amendment`, `gate-plan072-reqcoverage` → 1 each | measured: holds |
| p3 C3 | SC4 → exit 1 before work | measured: holds |
| p3 C4 | `--require-decision-for-noncrisp` → 3; `scripts/checks/test_skill_trigger_eval.py` → 2 | measured: holds |
| p3 C5 | transcript = costUSD on 13/13; 0 of 63 transcripts missing; `deduplicated by `message.id`` → 1 | measured: holds |
| p3 C6 | SC16 spike 0/0/1/0 | measured: holds |
| p3 C7 | superseded by p4 C2; the figures now match the formula | measured: holds |
| p3 C8 | SC7 spike 0 when last, 1 when a row follows | measured: holds |
| p4 C1 | `subagents/*.jsonl` → 1; `ephemeral_{1h,5m}_input_tokens` → 1; D1-manual pair $0.6732 = recorded; 5-class rates err 5.6e-17 | measured: holds |
| p4 C2 | two-stage expression present → 1; `0.0165 ± 0.0005` → 1; recompute 0.0165 / 0.2186 | measured: holds |
| p4 C3 | 40 edges; 0.3, 1.2, 2.3 are ancestors of 2.5; `after every other FULL row this plan adds` → 1; 0.3's in-place note → 1 | measured: holds |

## Missing
- None measured.
- inferred (low, non-blocking): I did not re-derive the p1 C4 fixture byte count or re-run the p2 C1 live CC load line this pass. A live call was avoidable, and the pass-4 live result ($0.008, `user: 0, project: 20`) stands.

## Gate Assessment
- **Harness-auth gate:** frontloaded, and it blocks 3.1, 3.2 and 2.5, which are the first live-eval issues. The Test is runnable. Sound.
- **Spend-ceiling gate:** its Test measured correctly on four ledgers: absent, null/0/150.5, 400.5, and 400.5 with a raised ceiling. It can be decided at any point in Epic 3, and the ledger's USD source is now exact, subagent runs included. Sound.
- **Split-decisions gate:** placed mid-DAG by necessity, since which skills need proposals is only known after Epic 3. It is a consent gate with an empty Test, covers accepted misses, and blocks 4.2. Sound.
- **Upstream-writes gate:** class-level consent, answerable at execute start. It covers 4.2, 5.4, 5.5 and 5.6. Sound.
- gate_consistency: PASS, 6 gates.

## Upstream Assessment
- #407 (include): resolved by 0.3, 1.1 and 3.2. Correct.
- #302 (exclude, evidence comment in 5.5): the exemption is declared and accepted by both SPEC-first checkers (measured). Sound.
- #189 (exclude): justified. This plan adds tests only for the new checker rules.
- The follow-ons 5.4 and 5.6 are out of scope and sit behind the upstream-writes gate. Correct.

## Resolutions

**Status: no concerns to resolve. Converged: an execution pass with zero measured findings.**

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
