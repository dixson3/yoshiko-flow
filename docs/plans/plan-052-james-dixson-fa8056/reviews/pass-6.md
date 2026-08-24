---
type: Review
okf_spec: OKF-PLAN
id: pass-6
description: Red-team pass 6 (confirming, sixth independent) — APPROVE; all eight pass-5 edits verified by execution, 0 high
---

# Red-team pass 6 (confirming)

## Verdict: APPROVE

**All eight pass-5 edits landed and were verified by execution, not by reading.** 0 high, 1 medium,
3 low. The medium is a specification gap *inside the P5-C1 class remedy itself* — surfaced by a
spike, one sentence to correct, not execution-blocking.

## Strengths (every claim re-derived by running something)

- **Mechanical properties re-confirmed after the sixth rewrite** — 8 epics / **31 issues / 49 edges /
  36 criteria / 5 gates / 11 risks / 22 upstream**, `unparsed: []`. Acyclic by DFS with 0 back-edges.
  **0.1 is the sole root and a strict ancestor of all 30 other issues.** 0 dangling `depends-on`,
  0 dangling `Discharged-by`, 0 issues discharging no criterion, **31/31 `touches:`**.
- **`audit` → `status: pass`.** `doc_lint` on `plan.md` → **PASS, 0 errors, 0 warnings, 0 report-only**.
- **All 36 criteria parse**; **0 `uv run` against a `.sh`** anywhere, so the `bash "$ctl"` rule is
  contradicted by no criterion.
- **Closure re-derived by IMPLEMENTING 0.2's `gen-controls.py` spec** — 29 asserted, 29 built,
  both differences empty, **0 controls with >1 builder**; sets from builder epic: **core 21 / ext 4 /
  land 4**.
- **Both gates re-verified transitively** — `core` blocks 10, behind-set **16**, violations **NONE**;
  `ext` blocks 4, behind-set **9**, **NONE**.
- **`upstream-write` verified by execution** — `grant --check` against the absent file exits **1**,
  `verdict: fail`. A touched file cannot satisfy it.
- **SC20's RED reproduced** — `verify-reconcile` → `verdict: fail`, **17/17** actionable rows failing.
- **R10/R11's writer count re-derived: exactly 5**, 10/10 pairs topologically independent — the plan
  states its own worst metric at its true value.
- **Both premises the REDs rest on still hold** — `closable --help` shows `[-h] [--json]` only;
  `ownership-report` does not exist.

## Reproduction of pass-5's eight concerns

**8 of 8 applied correctly. No edit was applied incorrectly.**

| # | Result | How verified |
| :-- | :-- | :-- |
| **P5-C1** | **LANDED** (all four parts) | 0.3 names both controls and their fixtures; `plan_extract` confirms SC1's `discharged_by: ['0.1','0.3','7.1']`; arm 3 present. **The sweep was re-implemented and run independently: `SC1 / ctl-req-landed / 0.3 ← 0.1` is the only inversion, `SC0c` and `SC1b` the only sole-discharger cases — the author's result reproduced EXACTLY** |
| **P5-C2** | **LANDED** | Three arms enumerated; floor and exit-1 rule explicitly disclaimed. **The INTERFACE arm does catch both**: `--fixture` is passed by three `ctl-205-*.sh` to `upstream.py`, absent from `--help`, so it falls to the commissioned disjunct which **3.2 satisfies verbatim**; `CTL_TXT` is named as commissioned in 0.2. A file-granular check saw neither |
| **P5-C3** | **LANDED** | `controls.txt` in 0.2's `touches:`. Hand-grep re-run over all 5 gates and all 36 cells: **exactly one hit — `upstream-authorization.txt`, which P5-C7 now explains. Zero unexplained** |
| **P5-C4** | **LANDED** | Fixture-location sentence present; 3.1's `touches:` carries `closable-fixture.json` |
| **P5-C5** | **LANDED** | Both bullets present; ordering names `ctl-empty-set-floor` and `ctl-baseline-pathspec` |
| **P5-C6** | **LANDED** | R11 rests on D-19, cites 0/5 and 0.301→0.362, records the correction |
| **P5-C7** | **LANDED** | Reads *"(widening the former `ctl-controls-closure`)"*; gate states the authorization file is operator-written |
| **P5-C8** | **LANDED** | 7.0 requires pinned fixtures, names `ctl-deploy-stamp` |

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| P6-C1 | med | **Arm 3, implemented verbatim, permanently fails on SC0c, SC1b and SC1 — making SC0 unsatisfiable as literally specified.** The reviewer wrote arm 3 as a script and ran it: **3 findings**, even under a deliberately generous predicate. The arm carries **no exemption for a stated-and-explained violation**, yet the plan contains one by design — SC1's own text says the inversion is real, permanent, and *"found by `ctl-harness-contract`'s third arm"*. SC0c/SC1b do state their RED path, but in **0.2's ordering rule**, not in the criterion cell the arm reads. Not execution-blocking — both gates get a real exit-1 RED and no issue stalls — but it is a defect **in the very remedy P5-C1 commissioned** |
| P6-C2 | low | 0.2 claims a *"COMPLETE file-and-interface contract in one place"* but omits two `gate-run.sh` subcommands — `verify-partition` (SC0b) and `self-test-broken` (SC3) appear only in criteria |
| P6-C3 | low | P5-C7's rename fix put a live `ctl-*` token into prose; a naive whole-document scan now returns **30** where the Verification-cells-only scan returns **29**. **Correct as specified** (0.2 forbids the naive scan), but the margin is one token wide and was created by a review fix |
| P6-C4 | low | Pass-5's `audit → findings: []` no longer reproduces — now **21 `warn`/`[R]` findings**, all on `findings/*.md` and `reviews/*.md` heading shapes. `status: pass`, exit 0, `plan.md` itself clean. Noted so the discrepancy is on the record rather than read as regression. Cosmetic: R11 precedes R10 |

## Missing

- **Still no control asserts the `bash "$ctl"` rule.** P5-C2 resolved this by *scoping the claim*
  rather than adding an assertion — honest, and SC3's `self-test-broken` exercises the dispatcher
  end-to-end. Carryable, unchanged.
- Nothing else. Every path, interface, fixture and predicate the gates and criteria depend on is now
  either declared in a `touches:` list or explicitly accounted for.

## Gate Assessment

| Gate | Reachable? | Verdict |
| :-- | :-- | :-- |
| `red-prework-core` | **Yes** — blocks 10, behind-set 16, **NONE** | **Sound. P5-C1's blocker is cleared.** All 21 core controls now have a construction yielding exit 1 |
| `red-prework-ext` | **Yes** — blocks 4, behind-set 9, **NONE** | Sound; earliest legal position |
| `upstream-write` | **Yes** | **Sound and now self-explaining** — verified by execution |
| Reconcile Gate | **Yes** | Sound; `jq` valid, exclusion intact, non-self-blocking |

**No frontloading miss. No gate depends on evidence produced inside — or transitively behind — its own `Blocks` set.**

## Upstream Assessment

Unchanged and sound. 22 rows; `verify-reconcile` → `verdict: fail`, 17/17 actionable rows failing
pre-execution — the correct RED for SC20. `grant` generates the proposal from the same table
`_verify_row` reads, **so the authorization and the reconciliation cannot drift**.

## Readiness statement

**Executable as written? YES.**

- **Execution-blocking: none.** Pass 5's sole blocker is fixed at both the instance and the class
  level, and the sweep was reproduced independently with an identical result.
- **Carryable: P6-C1 through P6-C4.** P6-C1 is worth one sentence before the Start Gate — free now,
  a `plan.md` edit at 7.1 otherwise.
- **On escalating the bound again: DO NOT.** Pass 5 was right that its concerns needed edits rather
  than opinions, and the edits landed. **Correct P6-C1 and proceed to execution.**

> **For the record, on why this pass was worth its cost:** not because the author's report was wrong
> — *every figure reported reproduced exactly, including the sweep*. It was worth it because
> **RUNNING arm 3 rather than reading it surfaced P6-C1, which four prose readings of the same three
> lines would not have.** That is the plan's own thesis holding at the last step.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| P6-C1 | med | **Fixed with the exemption clause you specified.** Arm 3 now reads: *an inversion or sole-discharger case is a finding **UNLESS the criterion OR ITS BUILDER ISSUE states how RED is obtained*** — naming the three stated cases (`SC1` in the criterion; `SC0c`/`SC1b` in 0.2's intra-issue-ordering rule). The clause records **why** it exists: without it the arm permanently fails on the plan's own three by-design cases and makes SC0 unsatisfiable, **measured at pass 6 by implementing the arm and running it**. The predicate stays live for any UNSTATED future case, which is the whole point of the arm | `main-session` | `resolved` |
| P6-C2 | low | **Fixed.** 0.2's dispatcher bullet now enumerates all five subcommands — `run <ctl-id>`, `verify-all`, `verify-set <core|ext|land>`, **`verify-partition`** and **`self-test-broken`** — so the *"COMPLETE contract in one place"* claim is now true rather than nearly true | `main-session` | `resolved` |
| P6-C3 | low | **Acknowledged; no change, as you recommended.** 0.2's spec already forbids the naive whole-document scan (*"ignoring prose globs"*), so the 30-vs-29 margin is **correct as specified**. Recorded here rather than silently accepted, because the margin was created by a review fix and is one token wide. The optional `gen-controls.py` warning on stray `ctl-*` tokens outside Verification cells is left to the implementer at 0.2 | `main-session` | `resolved` |
| P6-C4 | low | **Acknowledged; non-blocking and now on the record.** The 21 findings are all `[R]` report-only on `findings/*.md` and `reviews/*.md` heading shapes; `audit` is `status: pass`, exit 0, and `doc_lint` on `plan.md` is clean. The discrepancy with pass 5's `findings: []` is a difference in what the two passes measured, not a regression. R11-before-R10 ordering left as-is — cosmetic, and renumbering risks churning references | `main-session` | `resolved` |
