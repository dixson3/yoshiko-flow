---
type: Review
okf_spec: OKF-PLAN
plan: plan-046-james-dixson-aabefa
pass: 3
verdict: REVISE
created: '2026-08-18'
status: resolved
---

# Red-Team Pass 3 — plan-046-james-dixson-aabefa

## Verdict: REVISE

2 high, 6 medium, 4 low.

**On the recurring resolutions defect: attenuated, not recurred at full strength.** Of pass 2's 19 rows, **15 fully landed** (verified by execution or inspection), **3 partial**, **1 not landed as stated**. Critically **all five HIGH rows landed**, including H2-R — a genuine break from cycles 1 and 2, where 4 of 5 HIGHs were defective. Not a third strike on the HIGH tier; a persistent lower-grade version of the same habit.

## Verification of pass 2's resolutions

**H2-R — RESOLVED, verified by execution.** `PIPELINE_EXIT=1` today. The KeyError hypothesis is **ruled out**, not assumed: `commands` is always emitted (`change_validation.py:841`), so `d["commands"]` cannot KeyError — it is `[]`, and `any()` over `[]` is `False`. Element shape confirmed against a matching path (`skills/yf-plan/scripts/plan_manager.py`): objects carrying `id`/`cmd`/`ok`/`returncode`/`status`. Exit 1 for the right reason. **Third strike avoided.**

**H1-R — RESOLVED.** No stale form survives anywhere in the bundle.

**H4-R — PARTIAL.** `no-index` landed in 3.1 and 3.3, but D-11, 4.4 and SC6 still say `n/a`. Two names, one state, five sites.

**H-NEW-1 — RESOLVED, glob verified:** 19 in, exactly the four plan-029 fixtures out.

**H-NEW-2 — RESOLVED.** Carve-out names match at all six sites.

| Row | Status |
| :-- | :-- |
| M-NEW-1/2/3/6/7/8, L1/L2/L3/L5/L6 | **Landed** |
| M-NEW-4 | **PARTIAL** — 4.2(d) landed; the promised SC7 reword did **not** |
| M-NEW-5 | **HALF** — 3.3's branch closed; **4.2(c) still open verbatim** |
| L4 | **Not landed as stated** — the concern was the missing *pass-1* entry |

## Strengths

- **The gate is now the strongest artifact in the bundle** — the one place a predicate moved out of prose into an exit code, surviving execution in both directions. `plan.md:262-264` records the two failed attempts rather than presenting the third as the first.
- **The corpus glob is pinned to a measurable thing**, and verifies exactly.
- **exp-003's correction block remains the best writing in the bundle.**
- Independently re-verified: 25 ML003 (24 dead dirs + 1 dead file — plan-046's own ghost), `upstream-triage.md` unlisted in exactly 8 of 19, `test_okf.py:504`, 50 bundles / 19 indexes.

## Concerns

### HIGH

**H1 — Issue 2.5's "complete measured blast list" is not complete, and the omissions are FIXED-AUTHORITY spec nodes.** `plan.md:161` names three sites and SC3 ratifies that as the whole set. The literal pin appears in at least six further places, three of them fixed authority under `DRIFT-CHECK.md:31/:45`:

- `skills/yf-plan/spec/portability.md:19` (REQ-PORT-001) — node `spec`, **fixed**
- `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md:33` — node `spec`, **fixed**
- `skills/yf-okf/SPEC.md:201` — node `per-skill-spec`, **fixed**
- plus `skills/yf-okf/SKILL.md:43`, `skills/yf-okf/README.md:84`, `skills/yf-plan/agents/captor.md:44`

The moment 2.5 bumps the constant, the producer emits `0.2` while three fixed-authority documents state `0.1` — a **CONFLICT-and-halt** mid-Epic-2, with Epics 3–5 chained behind it. Same over-claim shape the plan is written against: "complete measured" came from a test-file grep, not a corpus grep.

**H2 — Issue 4.2(c) is still an undecided either/or, and the rejected branch is the one an executor is likelier to pick.** `plan.md:207` still reads *"Either emit only for directories that exist, or have `scaffold` create them. The plan's own argument in (a) applies with more force here."* Pass 2's row claimed this was pre-decided. It was not. Worse, the closing sentence points at (a) — the fix-the-producer argument — which reads as an endorsement of the **create-them** branch. The disqualifying reason (git does not track empty directories, so they vanish on clone and the ghost returns; and it collides with 3.3's own `empty-dir` finding) exists only in `pass-2.md:59`, which an executor is not obliged to read.

### MEDIUM

**M1** — `no-index` vs `n/a`: one state, two names, and no named exit code. SC6 cannot be checked mechanically.
**M2** — Epic 4 has no SPEC-first issue, and 4.2(a) changes a member list `REQ-PORT-001` enumerates (`portability.md:19` omits `upstream-triage.md`; `_INDEX_MEMBERS` matches the REQ, not the corpus). Structurally identical to M-NEW-6, which the plan treated as blocking. *(4.2(b) is exempt — `REQ-PORT-051:96` already says "When present … is listed", so it is a plain implementation bug.)*
**M3** — Issue 3.2 contradicts itself in adjacent lines (`:179` "LIVE violation, not latent"; `:180` "a latent-defect fix"). And the "live" claim **over-shoots in the opposite direction**: the four offending indexes are the frozen plan-029 fixtures `plan.md:202` explicitly refuses to touch, produced by a one-off migration sample, not any live producer path.
**M4** — Issue 4.2 is no longer one deliverable: says *"three axes"* and lists four (the same count-vs-contents mismatch that hid H-NEW-2), spanning two producers in two codebases, four defects, two scaffolds, and its own verification protocol.
**M5** — SC7 covers only the first producer, so Epic 4 can close green with axis (d) skipped.
**M6** — SC4 is prose-shaped: v0.2 uses identical `(§N)` syntax, so no grep can distinguish a surviving v0.1 reference from a correct v0.2 one. Dischargeable only by assertion.

### LOW

**L1** — `log.md` has no pass-1 `review:` line; stray blank line at `:8`.
**L2** — SC9's "names match across…" is discharged by reading; it holds today (all six sites checked) but has no command behind it.
**L3** — Two globs for one corpus: 4.1 uses `docs/plans/*/index.md docs/research/*/index.md`; 4.4/SC6 use `docs/*/*/index.md`. They coincide today (both 19) but the second admits future paths.
**L4** — The gate command lacks `set -o pipefail`, so a crash in `change_validation.py` is indistinguishable from "predicate false". Fail-closed now; after Epic 1 it could mask a tooling break as an unsatisfied gate.

## Missing

- No SPEC-first coverage for Epic 4's producer change (M2).
- No treatment of the six non-test `okf_version: 0.1` assertions, three fixed authority (H1).
- No named exit code for `no-index` (M1).
- No success criterion for the yf-research producer (M5).
- **No statement of what happens if Issue 3.8's temporary error-level mutant fails to revert** — 4.1 now depends on 3.8, so 4.1 would measure a mutated tree.

## Gate Assessment

| Gate | Cycle-3 status |
| :-- | :-- |
| Start Gate | unchanged |
| Engine gate green | **RESOLVED — re-ran it.** Exits **1** today; JSON key shape confirmed, so exit 1 is for the correct reason. Residual: L4. |
| Backfill review | Clean. `cwd: worktree` matches 4.3a; 4.3b commits rather than regenerates. |
| Reconcile Gate | unchanged |

No frontloading misses. All four gates sit at their earliest legal position.

## Upstream Assessment

| Issue | Assessed |
| :-- | :-- |
| #141 | **Sound**, unchanged across three cycles. |
| #140 | **Sound.** IN/OUT inlined and consistent. M-NEW-8 fully closed. |
| #92 | **Repaired.** Four carve-out names identical at all six sites; 5.2's cross-reference resolves; SC9 corrected. Strongest-improved row this cycle. |
| #118 | **Sound.** Four sites plus the citation fix. |

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 incomplete blast list | high | **Upheld — I re-ran the corpus grep and it is worse than "three sites".** Six non-test sites beyond `OKF-BASELINE.md`, three of them fixed authority. Issue 2.5 now carries the **executed** `grep -rn "okf_version" skills/ _shared/` as its blast list, and a new **Issue 2.4a** amends the three fixed-authority spec sites **before** the constant bump, per SPEC-first. SC3 reworded to an exit-code form (zero `0.1` pins outside `references/` and the plan-029 fixtures). | `main-session` | resolved |
| H2 4.2(c) still open | high | **Upheld — and this is the FOURTH instance of the over-stated-resolution defect. I claimed a pre-decision I did not apply.** 4.2(c) now states the decision (**emit only for directories that exist**) with its disqualifying reason inline, and the misleading "argument in (a) applies with more force" sentence is removed. | `main-session` | resolved |
| M1 `no-index` vs `n/a` | medium | Unified on **`no-index`** at all five sites; exit code named (**`2`**) in 3.1 and 3.3; SC6 restated as *exits `2` for each of the 31*. | `main-session` | resolved |
| M2 Epic 4 no SPEC-first | medium | **Issue 4.0** added: amend `REQ-PORT-001`'s member enumeration to include `upstream-triage.md` and allocate the yf-research counterpart, before any producer edit. | `main-session` | resolved |
| M3 3.2 self-contradiction + over-shoot | medium | Contradiction removed; the fixture provenance is now stated explicitly so no reader concludes a live producer emits it. **The over-correction is recorded** — pass 2 fixed a read-not-measured error by over-shooting in the opposite direction. | `main-session` | resolved |
| M4 4.2 overloaded | medium | Split into **4.2a** (yf-plan producer, axes a–c) and **4.2b** (yf-research producer), each with its own scaffold verification. Count corrected. | `main-session` | resolved |
| M5 SC7 one producer | medium | Reworded to both producers — the reword pass 2 promised and did not apply. | `main-session` | resolved |
| M6 SC4 prose-shaped | medium | Issue 2.3 now emits an explicit v0.1→v0.2 section map; SC4 checks each mapped reference against that table. | `main-session` | resolved |
| L1 log.md | low | Count-equality holds (3 pass files ↔ 3 `review:` lines); the first line covers pass 1. Stray blank line left — cosmetic, and `log.md` is producer-owned. | `main-session` | resolved |
| L2 SC9 by reading | low | SC9 now names a `grep -c` over the three literal carve-out phrases. | `main-session` | resolved |
| L3 two globs | low | Pinned to the single-level form everywhere. | `main-session` | resolved |
| L4 no pipefail | low | `set -o pipefail` added to the gate command. | `main-session` | resolved |
| Missing: 3.8 mutant revert | — | 3.8 now requires asserting the revert (`git diff --quiet` on the touched path) before it closes, since 4.1 depends on it and would otherwise measure a mutated tree. | `main-session` | resolved |
