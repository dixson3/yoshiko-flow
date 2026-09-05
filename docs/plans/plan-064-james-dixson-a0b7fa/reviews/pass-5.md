---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 5 - APPROVE. C30''s fix verified by EXECUTING it across
  three engine variants and both crash seams: Issue 3.9 closes the total-loss window
  pass 4 measured. One low-medium residual, already bound by the plan''s own text.'
plan: plan-064-james-dixson-a0b7fa
date: 2026-09-05
---
# Red-Team Pass 5: plan-064-james-dixson-a0b7fa

## Verdict: APPROVE

Cycle 5 was a confirmation pass, as pass 4 asked for. **All five of pass 4's resolutions
(C30-C34) verified by re-measurement, and C30's fix verified by executing it.** Issue 3.9,
implemented exactly as the plan specifies, closes the total-loss window pass 4 measured. No new
damage from the 3.9 insertion. One residual finding is recorded as risk the operator accepts — a
loud crash with **zero data loss** on a path the plan already covers normatively, not a blocker.

## Verification of pass 4's five resolutions

**C30 — the decisive one.** Sandbox spike: three variants of `okf_hygiene.py`, real
`backfill_one(apply=True)` driven to `SIGKILL` at both a journal-write seam and each `os.rename`
seam, then `recover()` in a fresh process.

| Variant | Crash seam | Journal | Physical state | `recover()` | Bundle after |
| :-- | :-- | :-- | :-- | :-- | :-- |
| **v0** shipped | after rename 1 | `S1` | bundle absent, staging+stash | `True`, "discarded staging; bundle untouched" | **GONE** (EXP-001 reproduced) |
| **v1** = 3.1 only | after `write("S3")` | `S3` | bundle absent, staging+stash | `True`, "completed cleanup" | **GONE** (C30 reproduced exactly) |
| **v2** = 3.1 + **3.9** | after `write("S3")` | `S3` | bundle absent, staging+stash | `True`, "completed cleanup" | **PRESENT, 6 files, transformed** |
| v2 | after rename 1 | `S2` | bundle absent | `True`, "rolled forward from staging" | PRESENT (no regression) |
| v2 | after rename 2 | `S3` | bundle present, stash | `True`, "completed cleanup" | PRESENT (no regression) |
| v2 | no crash | — | — | — | backfilled: `index.md` + `log.md` present, `README.md` gone |

**Issue 3.9's prescribed fix — `if not bundle.exists() and staging.exists(): os.rename(staging,
bundle)` ahead of the cleanup — is a 2-line change that closes the window without touching any
other path.** C30 is genuinely closed, by measurement rather than reading.

| Prior | Claim | Measurement | Holds? |
| :-- | :-- | :-- | :-- |
| C30 | 3.9 + 0.4 + 3.5's journal-write arm + SC11 close the window | Spike above. SC11's wording covers the window; 3.5's arm is correctly hung off the **journal-write** seam — the `os.rename` seam provably cannot reach it (both rename-seam runs are safe under v1) | **YES** |
| C31 | `5.4 depends-on: 4.5` | Now reads `4.5` | **YES** |
| C32 | 3.8 gains an edge to 2.8; `010` mutation is a flag flip | `3.8 depends-on: 2.8, 3.6`; Issue 2.2 keeps the `rglob` derivation behind a forceable internal fallback | **YES** |
| C33 | SC13b `Discharged-by: 2.8, 3.8` | Present | **YES** |
| C34 | Filed into 5.3's follow-on batch | Present in 5.3's text | **YES** |

## Strengths

- **No new damage, mechanically confirmed.** 44 issues / 45 edges with **0 self-edges, 0 dangling
  targets, 0 cycles, 0 duplicate ids**. Deltas from pass 4's 43/43 account exactly: +1 issue (3.9)
  and +1 edge (C32's `3.8 -> 2.8`). **Every issue appears in at least one `Discharged-by` cell, and
  every `Discharged-by` id is a real issue** — both directions checked.
- **Every instrument green or correctly red:** `plan_extract --strict` 0, `doc_lint` PASS with 0
  findings, amendment gate exit 2 (correct pre-execution), coverage gate exit 0 over 36 non-Epic-0
  issues, vendored gate 0, residue gate 0, SC11's rewritten selector exit 5.
- **The vendored gate's `Blocks` correctly omits 3.9** — 3.9 edits `okf_hygiene.py`, not
  `_shared/okf.py`, so no fan-out applies. The omission is right, not an oversight.
- **No stale cross-reference** to Epic 3's composition anywhere in `context.md`, `index.md`, or
  `findings/`.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C35 | low-medium | **A second window opens at `S2`, and it is not data loss.** Measured on v1 **and** v2: a crash after `write("S2")` but before rename 1 records `S2` while physically at `S1` (bundle **present**, staging present, no stash). `recover()`'s `S2` branch takes the roll-**forward** path `os.rename(staging, bundle)` onto the still-present bundle -> **uncaught `OSError errno 66`**. The bundle survives intact and untransformed; recover is idempotently stuck. This is the same over-approximation obligation Issue 0.4 states, one branch earlier — but Issue 3.3's text scopes its errno-66 wrap to "the S2 **stash-rollback**", which is the *other* line in that branch. Loud failure, zero loss, and SC11's own wording ("no unhandled errno-66") already fails it. |

## Missing

Nothing that blocks. The plan names both seams (rename and journal-write) and Issue 0.4 states the
general obligation, so C35 is **discoverable by an executor following the plan** rather than
requiring independent insight — the standard pass 4's residual-risk note asked for and did not have.

## Gate Assessment

All four capability gates re-measured: **reachable, acyclic, correctly frontloaded, unchanged and
unharmed by four rounds of insertion.** No consent gate, correctly. **No gate defect.**

## Upstream Assessment

Unchanged and sound across five passes. #316 `partial` with D6/D10 carrying the deferral honestly
and `Resolved By` pointing at 4.5/5.4/5.5; #294 `include` correctly attributed; #298 `exclude` still
states its tension rather than resolving it by fiat. C31's fix restores graph enforcement of R8's
anti-forgetting sequencing (`5.4 -> 4.5 -> 4.4`).

## Residual risk the operator accepts

1. **C35's `S2`-recorded/`S1`-physical window** — a crash there wedges `recover()` with an uncaught
   errno-66. Data is intact; the manual remedy is removing the staging copy and the journal entry.
2. **SC14, SC17, SC19 have no exit code** — three of twenty-one criteria are prose judgements,
   recorded honestly as `manual:`.
3. **R8 stands** — the follow-on transform may discover a fourth blocker EXP-001 never tested.
   Issue 4.5 probes the three known-untested surfaces, but that is mitigation, not elimination.

## Convergence judgement

Five passes descended one layer each: read the plan (1), ran the commands (2), ran the test (3),
ran the fix (4), **ran the fix to the fix (5)**. Pass 5 found nothing that reading pass 4's
resolutions would have missed, and the one new item is a low-medium already bound by the plan's own
text. That is the signature of a converged plan, not of exhausted reviewers.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C35 `S2`-recorded/`S1`-physical errno-66 | low-medium | Taken rather than deferred, because it is a one-line scope widening: **Issue 3.3 now covers BOTH lines of the `S2` branch** — the roll-forward `os.rename(staging, bundle)` as well as the stash-rollback — and requires `test_crash_s2_errno66` to be implemented on the **journal-write** seam, since the rename seam cannot reach this window either (the identical blindness pass 4 diagnosed for `S3`). This removes residual-risk item 1 rather than accepting it. | `main-session` | `resolved` |
