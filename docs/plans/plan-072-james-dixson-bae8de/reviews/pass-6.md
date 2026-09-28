---
type: Review
okf_spec: OKF-PLAN
description: Red-team pass 6 (execution), recertifying the ESC-001 amendment (FULL-row timeout 28800 s, --deadline-seconds 25200). REVISE with 1 high (mechanical audit) and 3 low concerns
---
# Plan Red-Team: plan-072 pass 6 (recertification of the ESC-001 amendment, commit 3f72d97)

## Verdict: REVISE
**Mode:** execution

The amendment itself is consistent and correct, and nothing in it blocks. One measured blocker
sits outside the amendment: two assets committed after pass-5 have no frontmatter, so `audit`
exits 1 and `ready-check` exits 3, and the fingerprint cannot be refreshed until they are fixed.

## Strengths
- **Consistent across plan.md.** D3, Issue 2.5, SC7, 5.2 and R1 all state 28800 / 25200 / 150/h
  or the ~5.3 h figure. In plan.md, `` `timeout` 21600 `` returns 0 hits and `` `timeout` 28800 ``
  returns 2. Across the repo (excluding reviews, log and escalations), 21600 and 21000 have zero
  hits.
- **CHANGE-VALIDATION.md FULL tier is right.** The engine's own `parse_manifest` reads the last
  FULL row as `trigger-eval`, timeout 28800, flags `inconclusive-exit=4,stream`. Its command ends
  `--max-runs-per-hour 150 --max-backoff-seconds 1800 --deadline-seconds 25200`.
- **SC7 discriminates.** Run verbatim it exits 0. A mutant with the timeout set back to 21600 exits
  1, and a mutant with `stream` dropped exits 1.
- **The deadline becomes INCONCLUSIVE end to end.** `Throttle.acquire` refuses a run with
  `start + TIMEOUT_S > deadline`. `cmd_live` maps `throttle.exhausted` to exit 4, and a genuine
  `fail` cell takes precedence. The engine maps rc 4 on an `inconclusive-exit=4` row to
  INCONCLUSIVE. The harness suite passes 40/40 and the engine suite 33/33.
- **The arithmetic holds when there is no rate limit.** The margin is 28800 − 25200 = 3600 s, which
  is 24 × TIMEOUT_S. At 150/h, the last start comes at 17256 s for 720 runs and at 18984 s for
  720 + 72 confirmation runs. 18984 + 1800 (backoff bound) + 150 = 20934 s, which is under 25200.
- **The ESC-001 record is complete:** question, alternatives, recommended option, answer "lets do
  A", state resolved.

## Concerns
| # | Severity | Basis | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | measured: `plan_manager.py audit <bundle> --json-output` → exit 1; `ready-check` → exit 3 ("portability audit did not pass") | `assets/req-allocation.md` (2cdb5ab) and `assets/wording-lever.md` (1900c87) have no YAML frontmatter, so both fail REQ-OKF-003. Both were committed after pass-5. This blocks the post-APPROVE fingerprint refresh. | Add `type` / `okf_spec` / `description` frontmatter to both. Re-run `audit` (expect 0) and `ready-check`. |
| C2 | low-medium | measured: FakeClock simulation of `core.Throttle(150, 1800, deadline_s=25200)`. One 429 at run 10 → 527 starts; at run 200 → 622; at run 398 → 721 (all `deadline_hit`); at run 600 → 792, completes | "25200 s covers 720 runs" holds only when no 429 occurs. `rate_limited` halves `per_hour` permanently and `succeeded()` never restores it, so an early 429 makes the row INCONCLUSIVE even with backoff well under 1800 s. It fails safe, but D3 and Issue 2.5 understate the risk. | State it in D3 or R1, or file a follow-on for rate recovery. No change is needed to the deadline or timeout numbers. |
| C3 | low | measured: `grep -n '~3 h run' plan.md` → line 452 (SC14) | SC14 still says "~3 h run". It is the only stale duration left. | Change it to "~5.3 h at the ESC-001 throttle". |
| C4 | low | measured: mutant with `--deadline-seconds 25200` and `--max-runs-per-hour 150` removed from the row → SC7 exit 0 | SC7 pins the timeout cell but not the deadline or throttle flags. | Optional: add `'--deadline-seconds'` to SC7's `all(...)` tuple. |

## Measurements
| Check | Command | Exit | Note |
| :-- | :-- | --: | :-- |
| doc_lint | `doc_lint.py --path <bundle>/plan.md --json` | 0 | PASS, 0 findings |
| plan_extract | `plan_extract.py <bundle> --json --strict` | 0 | 6 epics, 26 issues, 40 edges, 6 gates, 17 criteria, 0 unparsed |
| gate_consistency | `gate_consistency.py <bundle> --json` | 0 | PASS, 6 gates |
| amendment log | `check_amendment_log.py --plan plan-072-james-dixson-bae8de` | 0 | |
| req coverage | `check-req-coverage.py --min-issues 20 <bundle>` | 0 | |
| okf reindex | `okf.py reindex --check <bundle> --json` | 0 | clean |
| audit | `plan_manager.py audit <bundle> --json-output` | 1 | C1 |
| ready-check | `plan_manager.py ready-check <bundle>` | 3 | audit only; `stale_approved: true` is expected |
| SC7 verbatim | from plan.md, `bash -c` | 0 | |
| SC7 mutant: timeout 21600 | sandbox copy | 1 | discriminates |
| SC7 mutant: drop `stream` | sandbox copy | 1 | discriminates |
| SC7 mutant: drop deadline and throttle | sandbox copy | 0 | C4 |
| harness tests | `test_skill_trigger_eval.py` | 0 | 40 passed |
| engine tests | `test_change_validation.py` | 0 | 33 passed |
| throttle sim, no 429 | FakeClock | 0 | 720 runs → last start 17256 s; 792 → 18984 s |
| SC1–SC6, SC8, SC16 | clause commands | 0 | |
| SC9 / SC10 / SC13 | clause commands | 1 | not yet dischargeable (Epics 3–5 pending) |
| prior resolutions p1–p5 | re-verified | — | all hold. p1 C7 holds in amended form (21600 → 0, 28800 → 2) |

## Missing
- No plan text says a rate-limit event permanently halves the rate (C2).
- The background baseline finished during this pass and wrote the `recorded` blocks. This pass
  wrote nothing to the repo.

## Gate Assessment
`gate_consistency` passes with 6 gates. The amendment touches no gate. The only re-approval
blocker is the audit (C1), which is mechanical.

## Upstream Assessment
The amendment does not affect upstream dispositions (3 entries, unchanged).

## Resolutions

**Status: all 4 concerns resolved by the main session. Frozen. Re-review: pass-7.**

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | Added `type`/`okf_spec`/`description` frontmatter (description JSON-quoted, since its text contains `:`) to `assets/req-allocation.md` and `assets/wording-lever.md`. `audit` → pass. | `main-session` | `resolved` |
| C2 | low-medium | Added to the D3 row: a rate-limit event halves the rate for the rest of the run, so a 429 in roughly the first 55% makes the row INCONCLUSIVE (fails safe), which halts L3. No change to the numbers. | `main-session` | `resolved` |
| C3 | low | SC14 now reads "a ~5.3 h run at the ESC-001 throttle". | `main-session` | `resolved` |
| C4 | low | SC7's `all(...)` tuple now also requires `'--deadline-seconds 25200'`. Verbatim run → exit 0 against the manifest. | `main-session` | `resolved` |
