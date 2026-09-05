---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 4 - REVISE. C24 confirmed closed by spike, but executing
  Issue 3.1''s prescribed fix revealed it opens a NEW total-loss window at S3 that
  today''s buggy code does not have, and no specified test arm can reach it.'
plan: plan-064-james-dixson-a0b7fa
date: 2026-09-05
---
# Red-Team Pass 4: plan-064-james-dixson-a0b7fa

## Verdict: REVISE

One **high** concern, measured by sandbox spike: **Issue 3.1's fix, applied exactly as written,
opens a NEW total-loss window that today's buggy code does not have — and none of the plan's
specified test arms can reach it.** Pass 3's C24 is genuinely closed; this is a different, deeper
defect that surfaced only because pass 4 was the first pass to *execute* the prescribed fix
rather than read it.

## Verification of pass 3's six resolutions (re-measured)

| Prior | Claim | Measurement | Holds? |
| :-- | :-- | :-- | :-- |
| C24 | 3.6 mandates a swap-driven REPLACE; 3.8 pins to it | **Spike built it.** Subprocess drives real `backfill_one(apply=True)` with `os.rename` wrapped to `SIGKILL` after rename 1. Buggy tree -> journal `S1`, `recover` returns `recovered: True, "discarded staging; bundle untouched"`, **bundle GONE -> test FAILS**. Fixed tree -> journal `S2`, "rolled forward from staging", **bundle present -> PASSES**. The negative control is genuinely implementable. | **YES** |
| C25 | `5.4 depends-on: 4.5` | **`plan.md:303` reads `depends-on: 4.4`** — the self-edge repair reverted it. See C31. | **NO** |
| C26 | SC13 split into SC13a/SC13b | Both parse as distinct criteria. Coherent, with one gap (C33). | **YES** |
| C27 | 1.5->SC4, 2.5->SC8, 3.5->SC12 | All three present. | **YES** |
| C28 | `4.6 depends-on: 4.5` | Correct. | **YES** |
| C29 | vendored gate `Blocks` extended | Present. | **YES** |

**No hidden structural defect behind the green `--strict`:** 43 issues, 43 edges, **0 self-edges,
0 dangling, 0 cycles, 0 duplicate ids**. All gates re-measured green; all five sampled pytest
criteria exit 5 (correctly red, correctly quoted); `doc_lint` PASS with 0 findings.

## Strengths

- **C24 is genuinely closed, and the spike proves it rather than asserting it.** The replacement
  test is implementable exactly as Issue 3.6 now specifies: driving the real `backfill_one` swap
  through the `SIGKILL` seam **fails** on the buggy tree and **passes** on the fixed one — the
  discrimination the old hand-built test could not make.
- **The mechanical surface is measurably clean.** 43 issues / 43 edges with 0 self-edges, 0
  dangling targets, 0 cycles, 0 duplicate ids; `doc_lint` PASS with 0 findings; every sampled
  pytest criterion correctly red at exit 5 with its `-k` expression properly quoted.
- **All four capability gates re-measured green and unharmed by three rounds of insertion** —
  reachable, acyclic, correctly frontloaded, with `Blocks` sets that now cover the added issues.
- **The upstream dispositions have held across four passes.** D6/D10 carry the deferral honestly,
  and the #298 exclusion still states its tension rather than resolving it by fiat.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C30 | high | **Issue 3.1's second half introduces a data-loss regression, measured both directions.** 3.1 writes `S3` **before** `os.rename(staging, bundle)`. A crash in that window records `S3` while the physical state is `S2` (bundle absent, staging + stash present). `recover()`'s `S3/S4` branch assumes the swap completed and **`rmtree`s both stash and staging** -> bundle destroyed, `recovered: True`. Spike, fixed tree, kill after `Journal.write("S3")`: `{'recovered': True, 'phase': 'S3', 'action': 'completed cleanup'}`, **BUNDLE PRESENT AFTER RECOVER: False**. The same window on **today's shipped code is SAFE**. Issue 0.4's over-approximation amendment implies every branch must tolerate a physical phase one behind, but **no Epic-3 issue changes the `S3/S4` branch**. Worse, the plan cannot detect it: every crash arm drives the **`os.rename` seam**, which structurally cannot fire between a journal write and the next rename. EXP-001's exact defect class, relocated from `S1` to `S3` by the plan's own fix. |
| C31 | medium | **C25 regressed during the self-edge repair.** `plan.md:303` still reads `5.4 depends-on: 4.4` while 5.4's text and R8 both require 4.5. The pass-3 resolution table asserts the fix; the file disagrees. |
| C32 | medium | **Issue 3.8's `--req REQ-OKFH-010` arm is under-specified and unreachable in the graph.** (a) The `008` arm names its mutation exactly; the `010` arm names no seam — "a `restore` that re-derives from the filesystem" is a whole-function revert of 2.2, not a 2-line swap. (b) 3.8's only edge is `3.6`, whose closure never reaches **2.8**, so 3.8 becomes ready with no `010` replacement test to point at. |
| C33 | low | **SC13b's `Discharged-by` is `2.8` alone, but the script and its `--req` arm are authored by 3.8** — the C27 class reintroduced by the C26 fix. |
| C34 | low | **`plan_extract.py --strict` validates neither self-edges nor cycles.** Pass 3's self-edge was caught only as a `check-req-coverage.py` side effect. No live instance today — a tool gap, not a plan defect. Out of scope for plan-064. |

## Missing

- **A crash seam that is not `os.rename`.** Every crash arm hangs off the rename seam. C30's window
  lives *between* a journal write and a rename, so the plan's instrument is blind to it by
  construction — the same "instrument calibrated against the wrong call site" diagnosis Issue 3.6
  now carries, one layer down.

## Gate Assessment

All four gates re-measured: **reachable, no cycles, correctly frontloaded, unchanged from pass 3.**
SPEC gate exit 2 (correct pre-execution); coverage gate exit 0 over 35 non-Epic-0 issues;
vendored-copies gate exit 0 with `Blocks` now covering the inserted issues; residue gate exit 0.
Correctly no consent gate. **No gate defect in this pass.**

## Upstream Assessment

Unchanged and sound. #316 `partial` with D6/D10 carrying the deferral honestly; #294 `include` with
a correct `Resolved By`; #298 `exclude` with the tension stated rather than resolved by fiat. C31
means R8's anti-forgetting sequencing is still not graph-enforced.

## Convergence judgement

**This is not repair churn.** The C4->C14, C15->C24, C25->self-edge chain is real, but each pass
probed one layer deeper: pass 1 read the plan, pass 2 ran the commands, pass 3 ran the *test*,
pass 4 ran the *fix*. C30 was not reachable by any cheaper method — it required building the thing
and killing it. The mechanical surface is measurably clean, and C31-C34 are one-line edits.

I would have approved on C31-C34 alone. **C30 is the blocker**: shipping a `recover()` that
destroys a bundle while reporting `recovered: true` is the precise failure EXP-001 refuted the
premise with, and the plan would be introducing it as a *fix*. Cycle 5 should be a confirmation
pass, not a discovery pass.

**Residual risk if approved as-is:** the executor must independently notice that over-approximation
obliges the `S3/S4` branch to roll forward, because no issue text says so and no specified test arm
fails if they don't.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C30 3.1 opens a new S3 loss window | high | **Verified at source before acting:** the `if phase in ("S3","S4")` branch `rmtree`s stash and staging and returns "completed cleanup" **without ever checking whether the bundle exists**. New **Issue 3.9** makes the branch presence-tolerant — if the bundle is absent and staging exists, complete rename 2 before cleanup — and states plainly that 3.1's fix would otherwise relocate EXP-001's defect from `S1` to `S3`. Issue 0.4 extended to state the obligation the over-approximation creates: **every** `recover()` branch must tolerate a physical phase one step behind its recorded phase. Issue 3.5 gains `test_crash_s3_recorded_physical_s2`, a **journal-write seam** arm, with the reason recorded: the `os.rename` seam cannot reach that window by construction. SC11 rewritten to cover "any journalled window", discharged by 3.1/3.3/3.5/3.9. | `main-session` | `resolved` |
| C31 C25 regressed | medium | Fixed by line index rather than string match — the earlier edit matched only one of two identical `- depends-on: 4.4` lines, which is exactly how the regression happened. Re-ran the self-edge/cycle/dangling scan afterward: all clean. | `main-session` | `resolved` |
| C32 `--req` arm under-specified | medium | Issue 3.8 now requires **both** mutations be reproducible by a flag flip, not a reconstructed revert: for `010`, Issue 2.2 keeps its `rglob` + `git ls-files` derivation behind an internal fallback the script can force. Edge added — `3.8 depends-on: 2.8, 3.6`; verified reachable. | `main-session` | `resolved` |
| C33 SC13b Discharged-by | low | `2.8, 3.8`. | `main-session` | `resolved` |
| C34 extractor tool gap | low | **Accepted as out of scope and filed rather than absorbed** — a follow-on bead against `plan_extract.py` for an edge-sanity pass (self-edge, cycle, dangling target) under `--strict`. Recorded in Issue 5.3's follow-on batch so it is not lost. | `main-session` | `resolved` |
