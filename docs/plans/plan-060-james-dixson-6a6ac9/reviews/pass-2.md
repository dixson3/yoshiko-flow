---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 2 — VERDICT REVISE, narrowly. Eleven concerns, two high and both blocking: SC2b (the criterion added to fix pass 1) is unsatisfiable under the shell that evaluates it, and SC2 is an argparse error. All eleven resolved.'
---
# Review pass 2 — adversarial (red-team)

## Verdict: REVISE

Narrowly. **All 11 concerns resolved** by the main session; re-dispatched as pass 3.
**Date:** 2026-08-29
**Dispatched as:** sub-agent (REQ-AGENT-049), read-only with respect to the repository under review.
**Subject:** plan.md after the pass-1 revision (7 epics, 48 issues, 84 edges, 39 criteria).

The reviewer's own summary: *"The design is sound and pass 1's fourteen resolutions substantially
landed — I verified each one independently. But two criteria cannot pass, both in the exact class
this plan exists to eliminate, and one of them is the criterion added as the fix for pass 1's C1.
Both are one-line fixes; nothing structural is wrong."*

## Strengths

- **C1's primary fix landed and bites.** All 33 test-backed criteria route through
  `check-pytest-ran.sh`; **zero** `-k` direct-file criteria remain. The instrument distinguishes
  absent (exit 1), failed (exit 1, different message), selector-matched-nothing (rc 5 -> exit 1) and
  could-not-run (exit 2).
- **C10 — the epic split — is clean, and it was the highest-risk item.** All 48 issues, every
  `depends-on`, `Discharged-by` and `Resolved By` mechanically verified: **zero dangling, zero
  mis-pointed**. Every renumbered node spot-checked semantically.
- **The upstream table and inline annotations are bidirectionally consistent** — zero mismatch
  either direction.
- **C3 is gone from the executable surface**, including the `.d2` diagram source. EXP-005 records
  the withdrawal as an explicit CORRECTION block rather than silently editing.
- **C11's three figures re-measured correct independently** — 20 `_run_git` call sites, FULL = 57,
  `SKILL.md:1662`.
- **EXP-006 is the best finding in the bundle** — reproduces the operator's edge, identifies that the
  existing digest mechanism answers it conditionally on a schema change, and turns that into a
  fourth refutation of #301's ordering.
- **C4's honesty repair is real** — the convention is labelled, the rejected alternative recorded,
  and the first irreversible step is named in the order block itself.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **SC2b — the criterion added to fix pass 1's C1 — can never pass in the environment that evaluates it.** `recheck-criteria` runs each clause via `subprocess.run(["bash","-c",cmd])`, where `grep` resolves to `/usr/bin/grep` (BSD grep, GNU-compatible). Under BSD **and** GNU grep, `-L` changes only *output*, not exit status. Measured on the real three-file shape: all good -> exit **0**; one broken -> exit **0**; missing file -> 2. SC2b demanded exit **1**, so it is unsatisfiable — old SC30's defect reintroduced by C2's fix. `context.md` recorded the opposite measurement; that is **ugrep's** contract, and ugrep exists here only as an interactive shell function that `bash -c` never sees. | Replace with an implementation-independent form. Re-validate every grep-based criterion under `bash -c`. Correct the `context.md` note. |
| C2 | high | **SC2 is an argparse error and therefore also unsatisfiable.** `check-req-coverage.py` takes a **positional** `plan_dir`; SC2 passed `--plan`. Measured: `error: unrecognized arguments: --plan`, exit 2. SC1's `check_amendment_log.py --plan …` *is* correct — the two scripts take different forms, which is what invited the copy. | Rewrite to the positional form. Adopt a standing rule: every criterion whose command exists today is executed once before approval. |
| C3 | medium | **The decision document's `steps` vocabulary does not reconcile with the L-order, and it makes the merge skippable.** Nine coarse keys — one `push` for a two-push order, no key for the down-merge, the FULL tier or the advisory recheck — while SC3 requires every step label enumerated. Worse, `merge: skip` is legal, which is not *narrowing the landing* but a different operation. | Pin the key set one-to-one with the L-labels and declare a non-skippable set; enforce it in `--validate-decision`. |
| C4 | medium | **Nothing asserts the rehearsal succeeded — and the rehearsal is R1's entire mitigation.** SC36 asserts only that the origin was not the live repo. A rehearsal that halted at L2 satisfies every criterion in the plan. | Add a criterion asserting the rehearsal reached a green terminal journal state. |
| C5 | low-medium | **The step count is stated three ways and none matches the list** — "eighteen steps", "the eighteen-step order", "nineteen step labels", against twenty actual labels. SC3 asserts a count against a spec that will be written to a different count. | Pin one number and one label set. |
| C6 | low-medium | **SC34 lost its negative half.** Its prose claims SKILL.md "no longer carries the empty expression" but verifies only the positive grep. Pass 1's C12 asked for positive *paired with* negative; the revision swapped rather than paired. | Pair them, validated under `bash -c`. |
| C7 | low-medium | **Pass-1 C12's prose/verification mismatch survived the renumbering under a new id.** SC27 reads "After a complete rehearsal landing…" but is verified by a Tier-1 unit test and discharged by 4.6/4.10, not 6.1. | Reword to what the unit test proves. |
| C8 | low | **The schema still carries the exact overclaim EXP-006 tells the plan to avoid** — "`--dry-run` performs no write of any kind", when `merge-tree --write-tree` creates an unreferenced ODB object. Also `exp-006` cites SC5 where the criterion is now SC6. | Add the ODB caveat to the schema; fix the cross-reference. |
| C9 | low | **New and uncorrected figure drift, in the plan whose Issue 0.10 builds the drift detector.** `UPSTREAM_REQUIREMENTS` is at `plan_manager.py:2676`; `plan.md` and `exp-003` cite `:2679`. `upstream-triage.md` still carries the retracted `SKILL.md:1707`. | Correct both; make 0.10's instrument sweep the whole bundle. |
| C10 | low | **`check-pytest-ran.sh`'s INCONCLUSIVE is collapsed into "criterion FALSE" by the criteria layer, and the plan claims #263 on exactly this axis.** That is the safe direction and the plan cannot fix `recheck-criteria` — but a plan asserting `inconclusive` is never coerced should not leave its own criteria layer doing so unremarked. | One sentence in Issue 0.9 stating the collapse and its direction. |
| C11 | low | **The EXP-005 CORRECTION block's scope is narrower than the stale text.** It names row 2 only; the F3 evidence row still asserts the refuted herdr-allow-list claim. | Extend the correction's scope to name the F3 row. |

## Missing

- **No criterion binds the rehearsal's outcome** (C4) — the only real hole.
- **The journal state set is still not enumerated anywhere in the bundle.** Issue 0.2 says it must
  be, but no candidate set appears, so SC3/SC19/SC38 and Issues 3.1/6.3 bind to whatever 0.2 writes.
- **No issue body names a single test function**, and Issue 4.10 does not name its file.
- **SC3 is discharged by an Epic-0 issue but verified by a test in a file Epic 3 creates** — harmless
  because criteria are re-checked at completion, but noted.
- **#301's reconcile body should say "closed as amended"** — raised in pass 1, still absent from 4.4.

## Gate Assessment

All four gates plus the Start Gate are **reachable, correctly worded and correctly placed** — pass
1's C7 is fully repaired. The first merge-and-push gate's renumbering landed correctly (old 3.5 ->
4.1), its evidence sits entirely outside its Blocks set, and its Condition's "20 call sites" figure
re-measured **true**. Both capability gates 2 and 3 now sit at `reconcile step`, the earliest anchor
their evidence permits. The per-landing runtime grants for *other* plans correctly moved out of the
plan-gate grammar into `spec/landing.md`. No frontloading misses.

## Upstream Assessment

Mechanically clean: nine dispositioned issues, fourteen `resolves-upstream:` annotations, zero
mismatches in either direction, zero dangling ids. #280's deferral is no longer treated as neutral —
*"the cleanest of the pass-1 repairs after C1"*. #204's partial remains honest. #301 -> `include` ->
CLOSED still needs "as amended".

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 — SC2b unsatisfiable under `bash -c` | high | **Accepted; verified independently before fixing.** `bash -c 'command -v grep'` -> `/usr/bin/grep`, "BSD grep, GNU compatible 2.6.0-FreeBSD"; the old form measured 0/0/2 for all-good/one-bad/missing. SC2b now uses a `grep -lF … \| wc -l` count comparison, measured under `bash -c` at exit 0 (all-good) and exit 1 (one-bad). `context.md`'s note is rewritten to name BOTH greps and to record that the earlier validation used a shell that never evaluates criteria — the error is kept, not erased. New `assets/criteria-validation.md` carries the execution record. | `main-session` | `resolved` |
| C2 — SC2 argparse error | high | **Accepted.** Reproduced (`error: unrecognized arguments: --plan`, exit 2). SC2 now uses the positional form, measured at exit 0. The standing rule is adopted in Issue 0.9, and all six runnable criteria were executed under `bash -c` — SC2/SC4/SC33 pass; SC1/SC13/SC34 are **not-yet-true**, and the record distinguishes that from unsatisfiable. | `main-session` | `resolved` |
| C3 — `steps` vocabulary vs the L-order; merge skippable | medium | **Accepted.** `decision-schema.md` gains a section pinning the `steps` keys one-to-one with L0-L19 and declaring **L1-L6 non-skippable**, with the reason stated: skipping the merge is not narrowing the landing but a different operation, contradicting the plan's own thesis. `--validate-decision` enforces it. | `main-session` | `resolved` |
| C4 — nothing asserts the rehearsal succeeded | medium | **Accepted.** New **SC36b** asserts the rehearsal reached a green terminal journal state having executed every enabled step, so a rehearsal halting at L2 no longer satisfies R1's mitigation. | `main-session` | `resolved` |
| C5 — step count stated three ways | low-medium | **Accepted.** The fractional `L4.5` is retired: the order is renumbered to a single contiguous **L0-L19** (twenty labels), and every count in the Approach, Issue 0.2, the gate Instructions and SC3 now reads the same set. | `main-session` | `resolved` |
| C6 — SC34 lost its negative half | low-medium | **Accepted.** SC34 now pairs the positive grep with the negative, so deleting the block no longer satisfies it. Measured not-yet-true (exit 1) today, as it should be. | `main-session` | `resolved` |
| C7 — SC27 prose/verification mismatch carried forward | low-medium | **Accepted.** SC27 reworded to what its unit test proves. | `main-session` | `resolved` |
| C8 — schema carries the overclaim EXP-006 forbids | low | **Accepted.** The schema now states that `--dry-run` changes no ref, file or working-tree state, and that `--write-tree` **does** create an unreferenced ODB tree object — phrased as EXP-006 F1 phrases it. `exp-006`'s SC5 cross-reference corrected to SC6. | `main-session` | `resolved` |
| C9 — new figure drift, uncorrected | low | **Accepted.** `:2679` -> `:2676` in `plan.md` and `exp-003`. The stale `SKILL.md:1707` was fixed **at source** — #303's issue body was corrected to 1662/1672 with an in-place note, then the references regenerated, so the retracted citation cannot propagate again. Issue 0.10's instrument is to sweep the whole bundle. | `main-session` | `resolved` |
| C10 — INCONCLUSIVE collapsed by the criteria layer, unremarked | low | **Accepted.** Issue 0.9 now states the collapse, its fail-closed direction, and that it is a property of `recheck-criteria`'s binary clause grammar rather than of this plan. `assets/criteria-validation.md` restates the not-yet-true vs unsatisfiable distinction the collapse would otherwise hide. | `main-session` | `resolved` |
| C11 — EXP-005 correction scope too narrow | low | **Accepted.** The CORRECTION block now explicitly names the F3 candidate-table evidence row that still asserted the refuted herdr-allow-list claim. | `main-session` | `resolved` |
