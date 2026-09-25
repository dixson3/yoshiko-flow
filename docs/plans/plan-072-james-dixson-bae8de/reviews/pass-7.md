---
type: Review
okf_spec: OKF-PLAN
description: "[red-team pass 7, execution] REVISE: all 4 pass-6 resolutions and all 35 prior resolutions measured holding; 1 low concern, index.md lacks the pass-6 entry (reindex --check exit 1)"
---
# Plan Red-Team: plan-072 pass 7 (recertification of the pass-6 resolutions, commit d0d3ecb)

## Verdict: REVISE
**Mode:** execution

All four pass-6 resolutions hold when their evidence is run. The ESC-001 amendment still holds
after d0d3ecb, and every prior resolution holds. One measured finding remains, and it is
mechanical: `okf.py reindex --check` exits 1 because d0d3ecb added `reviews/pass-6.md` without an
`index.md` entry.

## Strengths
- **C1 holds.** `audit` → exit 0. Both assets carry a parseable `---` block with `type: Asset`,
  `okf_spec: OKF-PLAN` and a JSON-quoted `description`. `check_frontmatter.py` → exit 0.
- **C2 holds.** The D3 row carries the rate-halving sentence (pass-6 C2).
- **C3 holds.** SC14 reads "a ~5.3 h run at the ESC-001 throttle".
- **C4 holds, and SC7 now discriminates on the deadline.** SC7 verbatim → exit 0. Removing
  `--deadline-seconds 25200` from the last FULL row → exit 1 (in pass-6 this mutant exited 0).
  Timeout 21600 → exit 1.
- **The amendment still holds.** `21600` appears 0 times in plan.md and CHANGE-VALIDATION.md.
  `parse_manifest` reads the last FULL row as `trigger-eval`, timeout 28800,
  `{inconclusive-exit=4, stream}`, with a command ending `--max-runs-per-hour 150
  --max-backoff-seconds 1800 --deadline-seconds 25200`.
- **The baseline output breaks nothing.** All 20 `triggers.json` and both `assets/*.jsonl` parse.
  The harness suite passes 40/40 and the engine suite 33/33.
- **`ready-check` shows exactly the expected state:** its only reason is the pass-6 REVISE, and
  `stale_approved: true`. Audit passes, 17 criteria are checked with 0 failures, and
  `gate_consistency` passes.

## Concerns
| # | Severity | Basis | Concern | Recommendation |
| :-- | :-- | :-- | :-- | :-- |
| C1 | low | measured: `okf.py reindex --check <bundle> --json` → exit 1, `verdict: drift`, `missing` `reviews/pass-6.md` | d0d3ecb committed `reviews/pass-6.md` with no `index.md` entry. `audit` and `ready-check` do not catch this; only `reindex --check` does. | Add the pass-6 entry (and the pass-7 entry) to `index.md`, re-run `reindex --check`, and expect exit 0. |

## Measurements
| Check | Command | Exit | Note |
| :-- | :-- | --: | :-- |
| doc_lint | `doc_lint.py --path <bundle>/plan.md --json` | 0 | PASS |
| plan_extract | `plan_extract.py <bundle> --json --strict` | 0 | 0 unparsed |
| gate_consistency | `gate_consistency.py <bundle> --json` | 0 | PASS, 6 gates |
| amendment log | `check_amendment_log.py --plan plan-072-james-dixson-bae8de` | 0 | |
| req coverage | `check-req-coverage.py --min-issues 20 <bundle>` | 0 | |
| okf reindex | `okf.py reindex --check <bundle> --json` | 1 | C1 |
| audit | `plan_manager.py audit <bundle> --json-output` | 0 | pass |
| ready-check | `plan_manager.py ready-check <bundle> --json` | 3 | only the pass-6 REVISE reason; `stale_approved: true` (both expected) |
| SC7 verbatim | from plan.md, `bash -c` | 0 | |
| SC7 mutant: no `--deadline-seconds 25200` | sandbox copy | 1 | discriminates |
| SC7 mutant: timeout 21600 | sandbox copy | 1 | discriminates |
| SC1–SC8, SC16 | clause commands | 0 | |
| SC9, SC10, SC13 | clause commands | 1 | not yet dischargeable (Epics 3–5) |
| harness / engine tests | the two suites | 0 | 40 / 33 passed |
| prior resolutions p1–p4 (35) | one check each | 0 | all hold |
| pass-6 resolutions C1–C4 | evidence above | 0 | all hold |

## Missing
- `index.md` lacks the pass-6 entry (C1), and will need the pass-7 entry too.
- `.beads.gate.lock` is untracked at the repo root. It is bd runtime state and must not be
  committed at landing.

## Gate Assessment
`gate_consistency` passes: 6 gates, 0 findings. No gate is touched. The SC16 spend probe exits 0
on the current ledger.

## Upstream Assessment
Unchanged: 3 entries. No disposition is affected.

## Resolutions

**Status: resolved by the main session. Frozen. Re-review: pass-8.**

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | low | Added the pass-6 and pass-7 entries to `index.md`. `okf.py reindex --check` → `clean`. | `main-session` | `resolved` |
