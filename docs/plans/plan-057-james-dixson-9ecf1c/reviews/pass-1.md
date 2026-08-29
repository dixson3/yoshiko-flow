---
type: Review
okf_spec: OKF-PLAN
id: pass-1
description: 'Red-team pass 1 of plan-057: all three declared anti-vacuity defences measured inert; 8 blockers, 9 observations, all resolved in place.'
---
# Red-team pass 1 — plan-057-james-dixson-9ecf1c

## Verdict: REVISE

> **All 17 concerns resolved by the main session.** Ready for pass 2.

**Date:** 2026-08-29 · **Reviewer:** delegated adversarial agent (read-only)

## Framing

plan-057 is the deferred half of plan-056, which took **nine** red-team passes whose recurring defect
class was **vacuity** — a criterion or check that cannot fail — found in nine distinct shapes. This pass
hunted those shapes here.

**The headline finding: all three of plan-057's declared anti-vacuity defence layers — the capability
gates, SC0, and the `recheck-criteria` engine fix — were measurably inert as written.** Each was
independently a blocker, and several were plan-056 defects reproduced verbatim in the plan written to
inherit their fixes.

## Strengths

- **The four-instrument derivation was mechanically complete** — independently extracting every
  instrument from the Verification column yielded exactly Issue 1.0's list, closing plan-056's
  four-times-recurring "instrument with no creating issue" defect.
- **DAG sound**: zero backward cross-epic edges; no gate's evidence produced inside its own `Blocks`;
  no gate placed later than its evidence requires.
- **R3's fingerprint honesty** — the plan says out loud that "30/30 byte-identical" is near-tautological
  and routes the real guarantee to three separate fail-closed preconditions.
- **The Backfill authorization gate is the best gate in the plan**: correct `Test: none` sentinel, and
  its `Instructions` redirect the operator off the tautological fingerprint.
- **Upstream dispositions are defensible**, including #170's two-ground `partial` correctly carrying
  EXP-006's "only ~100 of 1383 concepts inspected" caveat.

## Concerns

## Resolutions

| Concern | Severity | Detail | Resolution |
| :-- | :-- | :-- | :-- |
| C1 | high | **All three `auto` capability gates are INERT.** No `test_class: probe` pour directive. Measured: `grep -c 'test_class' plan.md` → 0; `plan_extract.py:110`'s `GATE_FIELD` cannot express the field; `test_gates.py:243` defaults an absent `test_class` to `manual`, which resolves INCONCLUSIVE and never FAILs. plan-056 pass-5 C41 reproduced verbatim. | **resolved** — plan-056's directive added flush against `Instructions:` on all three auto gates, with pass-6 C48's no-blank-line constraint stated in the text. |
| C2 | high | **SC0 used `bash -n`; measured, it reads INCONCLUSIVE (127), not FALSE.** `plan_manager.py:3103` maps 126/127 → `inconclusive`, counted in neither bucket. plan-056 pass-5 C40 had already reverted this exact form to `test -x`, calling it "a net regression". | **resolved** — SC0 rewritten to `test -x`, with plan-056's three residuals carried forward verbatim. |
| C3 | high | **`--require 12` is satisfiable with a new instrument missing.** Measured: 9 instruments today (`--require 9`→0, `--require 12`→1); semantics are `-lt`, i.e. a MINIMUM. | **resolved** — raised to `--require 14` (9 + 5) in both gate and SC0b, arithmetic stated in the cell, and Issue 1.0 now owes an equality assertion. |
| C4 | high | **R11's mitigation is not in force.** `HARNESS_INCOMPLETE`: 4 in the repo copy, **0** in `~/.claude/skills/yf-plan/scripts/plan_manager.py`. Installed tree is `yf 0.5.0 (206b2f7)`, predating plan-056. The predecessor gate proves plan-056 is `complete`; it proves nothing about which engine executes. plan-056 said this correctly; plan-057 dropped the sentence and asserted the opposite. | **resolved** — R11 rewritten to the measured fact; a new "Which tree the gates and criteria execute against" section added, adapted from plan-059. |
| C5 | high | **Epic 1 edits `_shared/okf.py` and no issue vendor-syncs it.** `CHANGE-VALIDATION.md` binds that path to `uv-_shared` (`sync.py --check`), so the FAST tier goes red on every subsequent edit. plan-056's Issue 1.7 is the precedent; `context.md` already said the step was not optional. | **resolved** — Issue 1.6 added (`depends-on: 1.5`) plus criterion SC5b. |
| C6 | high | **SC3's baseline is unreproducible AND already green.** Three independent extraction rules yield three triples (plan: 257/127/142; reviewer: 254/116/138; coordinator: 210/72/138) because no rule was written down. Separately, adding plan-058's bundle moved the ratio with zero index work — an open denominator makes SC3 green by arithmetic. | **resolved** — extraction rule stated in the criterion; re-measured to `138/210` (2026-08-29); denominator frozen to the 28 named bundles via `--frozen-set`. |
| C7 | high | **SC0's own claim was false** — it checked 5 `.sh` files and omitted 6 instruments its criteria invoke, including 2 of the 4 it creates. Measured: `check-skill-classified.sh` → **127**, `check-baseline-pin-contract.sh` → **127**, SC0 as written → **127**. Three class-A criteria invisible. plan-056 pass-3 C27 exactly. | **resolved** — SC0 now enumerates all 11 instruments. |
| C8 | high | **`context.md` sibling drift, every instrument green through it.** Three wrong decision ids (D-6→D-9, D-10→D-7, a spurious D-5), two nonexistent issue ids (6.6, 6.4 — this plan has four epics), and a claim that the backfill is "atomic per bundle" which the plan's own errno-66 measurement refutes. plan-056 pass-7 C52 / pass-8 C55. | **resolved** — all six corrected; the atomicity claim replaced with the journal mechanism, since an operator reads this file before authorizing the backfill gate. |
| C9 | med | **SC1 did not test what it said.** It read "names the `REQ-*`"; measured, **0** issues do, and the instrument passes on transitive Epic-0 dependency — green by construction. | **resolved** — restated to match the instrument, with the measured 0-direct/22-transitive split in the cell. |
| C10 | med | **SC19's command cannot see the 31st bundle** (`docs/research/001-okf-compliance-delta`, outside `--root docs/plans`), and `--min-roots 30` against 58 bundles is a guard wider than the thing it guards. | **resolved** — spans both roots; load-bearing assertion is now `--require-legacy 0`, not a root count. |
| C11 | med | **Harness gate `Blocks: epic:2` left two instrument consumers unguarded** (SC3 in Epic 1, SC21 in Epic 3); Issue 1.0 had no dependents at all. | **resolved** — widened to `1.1, 1.5, 3.1a, epic:2`. |
| C12 | med | **#189's `Resolved By` omits 3.5**, contradicting Issue 3.5's own `resolves-upstream:`. | **resolved** — `2.8, 2.10, 3.5`. |
| C13 | med | **SC8 was `manual:` and is the sole guard for a class that turned `main` red on 2026-08-29** (plan-058's `assets/` present-but-unindexed; FULL tier failed on `okf-index-drift`). | **resolved** — promoted to an executable criterion asserting either an `asset*.toml` schema or an `assets/**` exclude glob; adds a fifth instrument, propagated to Issue 1.0, SC0 and `--require 14`. |
| C14 | med | **Collision with plan-059** on the index generator (`_INDEX_MEMBERS`, `render_index`) and `document_types/`. | **resolved** — recorded as R12 with the measured non-collisions (plan-059 adds no `scripts/checks/` file, no recipe row, no selftest entry). |
| C15 | low | **SC7 green today, before any Epic-1 work** — `--min-roots 30` against 63 enumerated bundles. | **resolved** — floor raised to 60 plus a live RED-fixture assertion. |
| C16 | low | **Six instruments on disk are absent from the `INSTRUMENTS` array** — the empirical case for C3's equality fix. | **resolved** — named in Issue 1.0. |
| C17 | low | Epic 0 listed out of order (`0.1 0.2 0.3 0.5 0.4`); `index.md` did not list `reviews/`. | **resolved** — reordered; entry added. |

## Verified live during this pass

- `curl -sfI https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md` → **exit 0**, HTTP 200 (the old `knowledge-catalog` URL → exit 56). The network gate's `Test:` is sound.
- 30 depth-1 legacy READMEs, 39 unscoped — Issue 2.9's "depth-1 is load-bearing" confirmed.
- Exactly one live `_index.md` target (`docs/research/001-okf-compliance-delta`); the other is a frozen fixture.
- `verify-reconcile` exits 1 on four `partial` rows — the expected pre-execution state.

## Missing

- **A mechanical check of `context.md` against `plan.md`.** Two consecutive plans have now drifted here
  with every instrument green (C8; plan-056 pass-7 C52, pass-8 C55). A grep asserting every `D-\d+` and
  `\d+\.\d+` token in `context.md` resolves in `plan.md` would have caught all six defects.
- **A RED-fixture row per new instrument.** Issue 1.0 now names five, but the selftest rows are where
  "two-branch where it asserts a failure code" becomes executable.

## Gate Assessment

| Gate | Reachability | Verdict |
| :-- | :-- | :-- |
| Start | n/a | OK |
| Predecessor complete | `Test` self-contained; `Blocks: 1.1, 2.3` correct | Was **inert** (C1) — now poured `probe` |
| Backfill authorization | consent, `Test: none` sentinel, `Blocks: 2.9` | **Sound — the best gate in the plan.** Its `Instructions` correctly redirect the operator off the tautological fingerprint |
| Upstream network reachable | `Test` verified live: exit 0, HTTP 200 | Was **inert** (C1) — now poured `probe` |
| Verification harness ready | No cycle; evidence from 1.0, which it does not block | Was **inert** (C1) + off-by-one (C3) + `Blocks` too narrow (C11) — all three resolved |
| Reconcile | standard | OK |

No gate is placed later than its evidence requires — no frontloading miss. Every failure was in what the
gates *do* once reached, which is why they all read green to `gate_consistency.py` throughout.

## Upstream Assessment

Dispositions are defensible. #168 `exclude` (trigger not fired) and #169/#192 `deferred` are honest;
#170's two-ground `partial` correctly carries EXP-006's "only ~100 of 1383 concepts inspected" caveat
that plan-056 pass-2 C26 found dropped once already. `references/` contains all seven bodies. One defect
(C12): #189's `Resolved By` omitted 3.5, now corrected. `verify-reconcile` exits 1 on four `partial`
rows — the expected pre-execution state, correctly discharged by Issue 3.5.
