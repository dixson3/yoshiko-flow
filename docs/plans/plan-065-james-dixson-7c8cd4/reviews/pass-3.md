---
type: Review
okf_spec: OKF-PLAN
description: 'Review pass-3 - plan-065 red-team cycle 3, verdict REVISE, 15 concerns, no high; plan size flagged as a risk in itself'
---

# Review pass-3 — plan-065 (cycle 3)

## Verdict: REVISE

**Status: all 15 concerns resolved**, including C10's structural consolidation (44 -> 37 issues). Re-dispatched as pass-4.

**No high-severity concerns.** Pass-2's data-loss defect is genuinely fixed and was reproduced by
spike. What remains is one measured execution failure and a cluster of stale references the pass-2
remediation left behind.

## Strengths

- **C1's reordering landed and is correct**, verified by hand-extracted DAG *and* by spiking the
  reordered sequence: `restore --bundle --apply` on the uncommitted tree returns the bundle to its
  original file set.
- **C2's inverted assertion is now right** — the spike's hashes satisfy all three conjuncts.
- **DAG mechanically clean**: 44 issues / 51 edges, zero duplicates, self-edges, cycles, dangling
  refs, forward dependencies. `gate_consistency.py` PASS (5 gates). `doc_lint` PASS.
- **Every quantitative claim reproduces**: `bundles_checked 70, legacy 8, unclassifiable 0,
  hybrid-partial 0`; all 8 READMEs exactly 38 lines; plan-030 exactly 10 bullets and the only
  target with a pre-existing `log.md`; `test_okf_hygiene.py` 35 passed.
- **The rehearsal gate's pass-2 defect is RESOLVED**: with the commit moved to 4.5, Epic 3's
  `3.2 -> 3.3` is now the *same* sequence as `4.2 -> 4.4`. Verified by spike.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | medium-high | **MEASURED: Issue 4.4's re-apply omits `--reconcile-objective` and HALTS.** Sandbox: after `restore --bundle --apply`, a bare `backfill --apply` yields `mutated 0, halted 1, exit 1`; `post_reapply` stays at the reversed hash, so 0.4d's `post_backfill == post_reapply` fails and SC4 — #359's headline criterion — is undischargeable. With the flag: `mutated 1, halted 0`, byte-identical |
| C2 | medium | **Dangling `Issue 4.3a` references introduced by the C1 reorder** at plan.md:114 (D5) and :127. `4.3a` no longer exists; worse, :127 places the commit *inside* the apply step — the exact ordering the C1 fix inverted |
| C3 | medium | **SC10 undercounts the defects.** It says "three"; Issue 6.1 and the new gate both say four. Filing 3 of 4 satisfies SC10 — and the uncovered one is exp-003's silent-total-loss path, the discovery that motivated this cycle |
| C4 | medium | **SC13 undercounts the checkers** — "eight" vs Issue 0.5's ten. Observing 8 of 10 satisfies SC13; the uncovered two include 0.4h, which closes pass-2's destroyed-bundle blindness |
| C5 | medium | **C8's remedy built the instrument and never wired it.** 0.4g authors `plan065_negative_controls.py`, but SC13/SC14 are still `manual:` and no criterion references it — the only checker of ten with zero consumer |
| C6 | medium | **0.4f launders `FileNotFoundError` into evidence — the plan forbids this three lines away** (plan.md:336). Affects the same four checkers pass-2's C3 named. The problem was renamed, not removed |
| C7 | medium | **Three measured DAG ordering holes.** `4.5` and `4.3b` are both leaves; `5.1 depends-on 4.4` not 4.5, so all of Epic 5 can legally run before the backfill is committed. 4.3b and 4.4 are unordered, and 4.4's second record breaks 4.3b's `git status` assertion. 4.5 cites 4.3b without depending on it |
| C8 | low-medium | **The new upstream gate's condition names evidence produced inside its own Blocks set** — nothing drafts the four issue bodies except Issue 6.1, which the gate blocks. Also a frontloading miss: its floor is the Start Gate |
| C9 | low-medium | **MEASURED: SC9 is GREEN today**, contradicting the plan's own "Correction, measured" paragraph — the C10 remediation reindexed the bundle and fixed the drift. The paragraph showcasing R10 discipline is now itself an unrun colour claim |
| C10 | low-medium | **The plan is too large for what it does, and the growth is not going into coverage.** 44 issues / 51 edges / 5 gates / 10 one-shot scripts for 8 bundles with byte-identical boilerplate READMEs. **31 of 44 issues (70%) are named by no criterion and no gate**; orphans rose from 25/38. Three of this cycle's concerns are bookkeeping failures across a graph large enough to lose track of |
| C11 | low | 0.5's negative control for 0.4g is self-referential — its input is the file 0.5 writes |
| C12 | low | **No issue registers the checkers in `CHANGE-VALIDATION.md`**, unlike plan-060/062/063/064. "Re-checkable at completion" is hand-run-only, and the scripts become permanent unexercised residue |
| C13 | low | `--bundle` takes a path RELATIVE to the tree; an absolute path is refused (fail-safe). 4.4 says only "Pass NO `--root`" |
| C14 | low | 0.4c pins `bundles_checked == 70` exactly while 0.4h uses `>= 70`; any bundle created between drafting and execution fails 0.4c for an unrelated reason |
| C15 | low | 0.4h cites `okf_hygiene.py:981-983`; measured it is 977-978 |

## Missing

- A command specification for 4.4's re-apply (C1) — the most consequential omission
- An issue drafting the four upstream issue bodies the new gate names (C8)
- DAG edges ordering 4.3b and 4.5 against 4.4 and Epic 5 (C7)
- Any criterion or gate naming Issue 4.5 — the commit creating D5's revert boundary is discharged by nothing
- A `CHANGE-VALIDATION.md` registration for the new checkers (C12)

## Gate Assessment

Five gates; `gate_consistency.py` PASS; none unsatisfiable.

**Sandbox rehearsal green** — now reachable and correctly positioned; pass-2's "certifies a
different sequence" defect is **resolved**, verified by spike. **Corpus apply authorization** —
sound, at its reachability floor. **Upstream write authorization** — the right gate to add, closing
pass-2's real asymmetry, but its condition names evidence no issue produces (C8) and its floor is
the Start Gate. **Start / Reconcile** — standard.

## Upstream Assessment

Dispositions unchanged and sound. **The residual sits on the primary issue for the third cycle
running**: #359's most specific criterion — "`restore` exercised on a real bundle" — is the one C1
breaks. Materially better than pass 2, where SC4 was dischargeable only by an operation that
destroyed the bundle: the failure is now **loud** rather than silent. But it is still an
undischargeable headline criterion, and a one-word fix.

SC10's "three" would let the plan close #359 having filed three of four defects — and the unfiled
one would be the silent `git checkout` path, the most dangerous of the four and the only one this
plan discovered. That is an outward-facing loss, not a bookkeeping one.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | medium-high | **Accepted — the single most consequential omission.** Issue 4.4 now writes both commands explicitly: reverse with `restore --record findings/backfill-record.json --bundle docs/plans/plan-030-james-dixson-65526e --apply`, re-apply with `backfill --reconcile-objective --apply --record findings/reapply-record.json`. The flag is marked MANDATORY with the measured consequence of omitting it (`mutated 0, halted 1, exit 1`), and plan-030 is named as the bundle since it is the only non-divergent target post-Epic-2. | `main-session` | `resolved` |
| C2 | medium | **Accepted.** Both dangling `4.3a` references replaced with `4.5`; verified zero remain. The `:127` sentence restated so the commit is explicitly AFTER 4.4's restore round-trip, never inside the apply step. | `main-session` | `resolved` |
| C3 | medium | **Accepted — this would have been an outward-facing loss, not a bookkeeping one.** SC10 restated as FOUR and now names the fourth defect (`restore`'s unchecked `git checkout` return code) inside the criterion text, so it cannot be the one silently dropped. | `main-session` | `resolved` |
| C4 | medium | **Accepted.** Resolved structurally by C10's consolidation: there is now ONE script with ten subcommands, so SC13 counts subcommands and cannot drift from a script inventory. | `main-session` | `resolved` |
| C5 | medium | **Accepted — the instrument was built and never wired.** SC13 is now command-form (`plan065_checks.py negative-controls`), discharged by Issue 0.4. The `manual:` cell is gone. | `main-session` | `resolved` |
| C6 | medium | **Accepted — the problem had been renamed, not removed.** Issue 0.5 is now explicitly scoped to the four TREE-PROPERTY subcommands only (`audit-strict`, `bundle-shape`, `phaselog-bullets`, `index-drift-strict`), and must REJECT `reason == "input absent"` as a FALSE report. SC14 restated to match. The six artifact-reading subcommands are exempt by construction, stated as such. | `main-session` | `resolved` |
| C7 | medium | **Accepted; all three holes fixed and verified by ancestor computation.** `4.4 depends-on 4.3, 4.3b`; `4.5 depends-on 4.4, 4.3b`; `5.1 depends-on 4.5`. Measured after the fix: 4.5 is an ancestor of 5.1, 4.4 and 4.3b are ancestors of 4.5. Only the terminal issue 6.2 is now a leaf. | `main-session` | `resolved` |
| C8 | low-medium | **Accepted.** Added Issue 5.6 writing `findings/upstream-drafts.md` (four bodies + the exact close set), which sits OUTSIDE the gate's Blocks set; the gate's Instructions now point at it. `6.1 depends-on 5.6` verified. | `main-session` | `resolved` |
| C9 | low-medium | **Accepted, and the irony is recorded rather than quietly deleted.** SC9 measured green (`status: pass`) and `check_okf_index_drift.py` exits 0. The paragraph now states both with the commands that produced them, and notes that the earlier RED claim was true when written and false when read because the reindex landed in between — a colour claim is only true of a tree at a moment. | `main-session` | `resolved` |
| C10 | low-medium | **Accepted — this was the right call and I took the recommended cut.** Ten one-shot scripts collapsed into ONE `plan065_checks.py` with ten subcommands; the missing-input contract and negative-control harness are implemented once. Epic 0 went from 12 issues to 6. Plan: 44 -> 37 issues, 51 -> 48 edges, with identical assertion coverage and one criterion ADDED (SC15). Orphan issues fell 31/44 (70%) -> 23/37 (62%). | `main-session` | `resolved` |
| C11 | low | **Accepted.** Issue 0.4 now states that the `negative-controls` subcommand's own control runs against a synthesized `--input` fixture, since its real input is the file that issue writes. | `main-session` | `resolved` |
| C12 | low | **Accepted — without it the scripts are permanent unexercised residue.** Added Issue 0.6 registering `plan065_checks.py` in `CHANGE-VALIDATION.md` (FULL-tier rows plus a §4 path mapping), matching what plan-060/062/063/064 each did, and new SC15 asserting the registration exists. | `main-session` | `resolved` |
| C13 | low | **Accepted.** Issue 4.4 now states the `--bundle` value is the record's RELATIVE path and that an absolute path is refused. | `main-session` | `resolved` |
| C14 | low | **Accepted.** `apply-result` now asserts `bundles_checked >= 70`, taking its real strictness from the `8 rows with action == backfilled` assertion, so a bundle created between drafting and execution cannot fail it for an unrelated reason. | `main-session` | `resolved` |
| C15 | low | **Accepted.** Line range corrected to `okf_hygiene.py:977-978`. | `main-session` | `resolved` |
