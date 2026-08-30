---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 4 — VERDICT REVISE. One high concern in material no prior pass saw: Issue 1.9''s prescribed plumbing is tracked-only and enumerates ZERO for the artifact class the issue itself names. All five concerns resolved.'
---
# Review pass 4 — adversarial (red-team)

## Verdict: REVISE

One **high** concern, in the material no prior pass saw. **All 5 concerns resolved** by the main
session; re-dispatched as pass 5.

**Date:** 2026-08-29
**Dispatched as:** sub-agent (REQ-AGENT-049), read-only with respect to the repository under review.
**Subject:** plan.md after the pass-3 revision plus the operator's grep-divergence finding
(7 epics, 49 issues, 86 edges, 41 criteria).

## Strengths

- **Pass-3 C1 genuinely landed.** The `steps` object now carries **twenty** keys, checked name-by-name
  against the L-order: `l0_lock_acquire`…`l19_redeploy`, one-to-one, no gaps, no aliases. The
  non-skippable set (L0-L6 + L16) is coherent **and complete** — the reviewer probed the complement:
  skipping L7 is self-detecting (L10 halts), L12/L19 skips are recoverable, so nothing else belongs.
- **C2 landed verbatim.** **C3's argument survives the correction, and the reviewer checked the
  reasoning rather than the assertion**: the "fourth reason #301 is wrong" claim turns on the *merge*
  position (L2 here, post-close there), which the L16 finding does not touch.
- **C4-C7 verified present.**
- **Bidirectional integrity is perfect at the new sizes** — 49 issues, 86 `depends-on`, 41 criteria,
  75 `Discharged-by`; zero dangling in either direction; zero issues discharging nothing. 18 table
  rows == 18 `references/` files exactly; all 14 inline annotations match disposition included.
- **Round-4 vacuity sweep clean — no new unsatisfiable criterion.** Every runnable criterion re-run
  under `bash -c` matched the recorded values exactly. **Rounds 1 and 2 each introduced one; rounds 3
  and 4 did not.**
- **SC10b is not vacuous** — `check-pytest-ran.sh` returns 2 for the absent file and 1 for a
  nonexistent test name.
- **Mechanically green:** `gate_consistency` PASS (5 gates, zero findings), `doc_lint` 0/0.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **Issue 1.9's prescribed enumeration tools are tracked-only, and enumerate ZERO for the artifact class the issue itself names.** 1.9 requires every cross-tree fact — "plan directories, residual beads, **unposted comment drafts**, changed paths" — be gathered via `git ls-files` / `git -C <worktree>` / `git worktree list --porcelain`. `git ls-files` lists the **index**, not the disk. Measured live: `git ls-files docs/plans/plan-060-…` returns **0** from the primary checkout *and* **0** from the worktree, while `status --porcelain` shows `??` — the entire bundle under review is untracked. **Draft comment bodies are untracked BY CONSTRUCTION at `--dry-run` time**, because the plan-folder writes are not committed until L16 — D-2's whole point. So `draft_present` would read absent for drafts that exist, and **an omission from enumeration is silent — it is not a `skip`**, so the "every skip is surfaced" guarantee does not cover it. 1.9 replaces gitignore-blindness with tracked-blindness, unremarked, in the one issue whose entire subject is enumeration completeness. SC10b does not catch it: its fixture passes with a tracked file. | Amend 1.9: where the fact is **presence on disk**, require `git ls-files --others --exclude-standard`, `git status --porcelain=v2`, or a scoped listing — and say that `git ls-files` alone trades one under-report for another. Extend SC10b's fixture to an **untracked** draft inside the gitignored worktree. Add the shell-independent reason too: under `/usr/bin/grep` — what `subprocess.run(["bash","-c",…])` actually gets — a recursive search across both roots **double-counts**. R13 is rated high with a mitigation aimed at Python code that was never exposed to R13's stated mechanism. |
| C2 | medium | **The C3 correction did not propagate to the issue that implements it.** Issue 3.5 still says three sites and prescribes one uniform "write the journal state, **restore**, and HALT". Three consequences: (a) 0.2/3.1 require "one state per conflict site", so the set is under-determined at three-or-four and the L16 state is commissioned by **no issue**; (b) `restore` is precisely the wrong verb for an L16 rejection, whose contract is retry-never-revert; (c) SC19/SC38 bind to "every *enumerated* state", so a missing L16 state is silently satisfiable. **Same shape as pass 3's C1** — corrected in the prose, left uncorrected at the site an implementer copies. | Amend 3.5 to enumerate four sites with per-site recovery, and name the L16 state in 0.2's state-set clause. |
| C3 | medium | **SC31 does not test the thing C3 added** — "push-rejection" singular, while 4.10 requires five rows. The test name `test_conflict_matrix_covers_all_four_sites` compounds it: its "four" is a *different* four from the Approach's four **sites**, since target-moved is a staleness case, not a conflict site. A matrix with one push-rejection row satisfies SC31 as written. | Name five cases and rename the test. |
| C4 | low | **A duplicated paragraph left by the C3 edit** — the corrected paragraph was inserted and the pre-edit one left immediately below it, making the same argument twice in near-identical words. | Delete the second. |
| C5 | low | **The guard-routed count went stale again when SC10b was added** — the record says 31; measured, **32**, with 32 distinct test names and no duplicates. This is the exact bookkeeping row pass 3's C7 corrected. | 31 -> 32, with a note that SC10b is the addition. |

## Missing

Nothing new of substance. The three items pass 3 left standing remain accepted and are not
re-raised. One observation rather than a gap: **C1's live demonstration — this plan's own bundle
being untracked at review time — is the cheapest possible fixture for SC10b, and it is sitting in
the repository right now.**

## Gate Assessment

**Clean, re-verified mechanically.** `gate_consistency.py` PASS over 5 gates, zero findings. Issue
1.9 sits in Epic 1, outside every gate's `Blocks` set, so it introduces no reachability question. The
first capability gate's evidence still sits outside `Blocks: 4.1`; both `reconcile step` gates remain
at the last anchor their evidence permits. **No cycles, no frontloading misses.**

## Upstream Assessment

**Clean in both directions, re-measured.** 18 table rows == 18 `references/` files, exact set match;
all 14 inline annotations agree with the table including disposition; zero dangling ids. Issue 1.9's
new `#263 (partial)` annotation fits well — *"a content grep that reports 0 where the answer is 5 is
precisely #263's two-facts-one-signal class."* `#301 -> include -> CLOSED "as amended"` remains
stated in Issue 4.4.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 — 1.9's plumbing is tracked-only | high | **Accepted; both sub-claims re-measured before fixing.** `git ls-files` returns **0** for this bundle's 36 files from both checkouts; `--others --exclude-standard` returns **36**. The double-count is real too: under `/usr/bin/grep`, 6 logical paths return **twice** across the two roots. Issue 1.9 is rewritten to pick the plumbing **by which question is asked** — tracked-ness (`ls-files`) vs presence-on-disk (`ls-files --others --exclude-standard`, `status --porcelain=v2`, scoped listing) — states that `git ls-files` alone trades one under-report for another, records BOTH shell-dependent and shell-independent reasons with the note that only (b) reaches `land`'s Python path, and states that **an omission from enumeration is silent because it is not a `skip`**. SC10b's fixture now requires an **untracked** draft inside a **gitignored** worktree — both blindnesses at once. R13's mitigation names the shell-independent reason. `criteria-validation.md` gains a third section recording all three divergences and their directions: under-report (gitignore-blind), under-report (tracked-blind), **over-report** (double-count) — only the first being a shell artifact. | `main-session` | `resolved` |
| C2 — the correction did not reach Issue 3.5 | medium | **Accepted, and the "same shape as pass 3's C1" observation is the useful part — this is twice now.** Issue 3.5 is rewritten to enumerate **four** sites with **per-site** recovery, stating explicitly that `restore` is wrong for one of them: L1/L2 capture-then-`merge --abort`; L6 rebase, re-validate, retry; **L16 rebase and retry, NEVER revert**, because comments are posted, beads closed and `status: complete` written by then. Issue 0.2's state-set clause now names all four states including L16. | `main-session` | `resolved` |
| C3 — SC31 tests a different "four" | medium | **Accepted.** SC31 now names **five** cases (L1, L2, L6 rejection, L16 rejection, target-moved staleness) and the test is renamed `test_conflict_matrix_covers_four_sites_and_staleness`, so the criterion's "four" and the Approach's "four sites" refer to the same set. | `main-session` | `resolved` |
| C4 — duplicated paragraph | low | **Accepted.** The pre-edit paragraph is deleted; one occurrence of the argument remains. | `main-session` | `resolved` |
| C5 — guard-routed count stale again | low | **Accepted.** 31 -> **32**, verified by counting guard-routed SC rows and distinct test names (both 32). The record now notes that **this row has gone stale twice**, and that a derived count in prose is exactly the shape Issue 0.10's re-measurement instrument exists to catch — the recurrence is recorded rather than just corrected. | `main-session` | `resolved` |
