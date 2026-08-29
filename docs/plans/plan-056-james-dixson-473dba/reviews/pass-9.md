---
type: Review
okf_spec: OKF-PLAN
id: pass-9
description: "Red-team pass 9 — APPROVE. Every count re-derived mechanically and exact; the design layer has not moved since pass 7. Five single-line factual corrections, none blocking."
---

# Red-team pass 9: plan-056-james-dixson-473dba

## Verdict: APPROVE

> **All 5 concerns and the notes resolved.** Every correction was one recommended by this approving
> pass; none touched the DAG, the gate, a severity, or a criterion's rule.

Nothing at the design layer moved. Every remaining item is a single-line factual or wording correction
plus one clarifying sentence; none blocks execution.

## Strengths

**Count extraction re-run mechanically — C58's six corrections are all exact.** Script-derived from
`plan.md` (issue-id regex, comma-split `depends-on`, transitive closure): 35 issues, 22 criteria, 36
edges (23 `depends-on` lines comma-expanded), 24 non-Epic-0, **13 direct**
(`1.1 1.2 1.6 1.8 1.9 1.10 2.1 2.3 2.5 2.6 3.1 3.2 4.1`), **23 transitive**, sole non-transitive `2.4`.
Zero dangling targets.

**D-1's corpus basis re-derived live rather than trusted:** `doc_lint --json` -> 1114 files, 1643
findings, **1603 at `bundle_status: complete`**, `errors: 0`, PASS; findings with
`declared_severity ∈ {E,W}` demoted to `R` = **392, exactly**. `grep -c '^\[\[checks\]\]'` over
`document_types/*.toml` = **48**, with `promote = false` on the two `E` close-outs — 46/2 holds. Totals
differ from the plan's dated figures only by corpus growth since 2026-08-28, which the plan instructs
re-measuring.

**All six of pass 8's fixes landed.** C57 verified by reading the engine, not the prose: `recheck-criteria`
runs `subprocess.run(["bash","-c",cmd])` and `_RECHECK_CLAUSE` is greedy between first and last backtick,
so SC11c's whole `A && B` span is captured and short-circuits correctly — exit 0 requires both rows.
**A near-miss worth recording:** the self-reference guard is `"recheck-criteria" in cmd`, and
SC11c/SC36 name `test_recheck_criteria` with **underscores**, so they are not silently skipped. A
hyphenated filename would have been.

Line citations spot-checked and all correct: `plan_manager.py:2945-2969`, `:784`, `test_gates.py:243`,
`_common.sh`'s exit contract, `plan-relations.toml:7`, `doc_lint.py:339` in both copies,
`test_okf.py:966`. `--require 9` re-confirmed as the self-excluding maximum; the "glob reaches 6 of 10"
claim checks out against `redcheck.sh:299`.

## Concerns

### C61 — `check-recipe-row.sh`'s argument means two different things in SC11 and SC11c. [LOW-MEDIUM]

SC11 passes `okf-index-drift`, a §1 **row id** Issue 3.2 names explicitly. SC11c passes
`test_recheck_criteria` / `test_index_members`, which Issue 3.2a never declares as ids — every existing
yf-plan test row is id'd `uv-yf-cli-enum`, `uv-okf`. **An id-only implementation makes SC11c FALSE**
once 3.2a follows the file's convention; **a cmd-substring implementation makes SC11 FALSE**, since
`okf-index-drift` (hyphens) never appears in `check_okf_index_drift.py` (underscores). A whole-row-line
grep satisfies both — but nothing says so. **The only item here with an execution consequence.**

### C62 — EXP-006 says `1567` three times; its own categorisation sums to `1563`. [LOW-MEDIUM]

Including the literal *"Full categorisation (sums to 1567)"*. The breakdown is 1169+317+32+26+9+10 =
**1563**, which is what `plan.md` says in both places. Pass 2 recorded "1563/1567 reconciled throughout"
— true of `plan.md`, never applied to the finding. **Third false-`resolved` of this kind** (cf. pass 4's
M8, pass 8's C56).

### C63 — Motivation still reads "1603 of 1634 findings", two lines above "1642". [LOW-MEDIUM]

Pass 5's C47 updated the file count and the second sentence and left the denominator in the
parenthetical. 1634 has been wrong since pass 5.

### C64 — Issue 0.8's re-measurement is narrower than the claim it supports. [LOW-MEDIUM]

It says "correct **every** shipped instance … 5 occurrences across 4 files". `grep -rn '423' skills/
_shared/` returns **8 across the same 4 files** — the 5 named plus `SPEC.md:311` ("would write 423
assertions"), `OKF-YF-EXTENSIONS.md:395` ("producing 423 entries"), `test_okf.py:967`. All three are
equally stale derivations. SC27 is manual, so nothing mechanical catches the shortfall.

### C65 — the `check-pytest-ran.sh` routing count is given three times, in three values, and none is right. [LOW]

SC35 says "7 of 22" (C58's correction); Issue 1.8 says "**20** criteria route through this" and "the
critical path of **12** criteria". Mechanically **6 criteria invoke it** — SC36, SC4, SC7, SC8, SC10b,
SC28. The 7th is SC0, which only `test -x`'s its path; **if presence counted, all ten instruments would
gain the same +1 and "busiest" would be vacuous.** 20 and 12 are pre-split figures from the 33-criteria
era that C58's sweep did not reach. So: correcting five numbers did not break a sixth, but it moved the
numerator in the wrong direction and left two worse ones a few lines away.

## Notes (no change required)

- `index.md` says "Each found the criteria layer vacuous in a different shape" and lists six; passes 7-8
  found **sibling drift**, not criteria vacuity. Scope the sentence to passes 1-6.
- D-1 hard-codes "the **9** regressed bundles" while Issue 3.4 deliberately says "name the enumeration,
  not a count". Live now: **8 drifting of 31** — plan-056's own and plan-057 are clean, `research/005-*`
  has regressed again. 3.4's form is correct and SC10's `--min-roots 30` still floors, with one bundle
  of headroom.
- Issue 1.9 says plan-055 "copied `_common.sh` and three checks"; Issue 1.8 says "beside six". Both true
  of different moments, unreconciled one issue apart.
- #169's "3 of 28 / 32 of 107 / 57% boilerplate" is the one figure pair traceable to no finding and no
  review. Re-derived live the substance holds (4 of 31 research bundles supply 33 of 84 unique index
  descriptions, all irreducible) — only the citation is missing.

## Missing

Nothing blocking. The two standing gaps are already filed in Issue 4.2 — nothing verifies sibling
artifacts against `plan.md`, and nothing verifies a gate's `Instructions:` survive extraction.

## Gate Assessment

Unchanged and sound. All three producers (1.8, 1.9, 3.1) sit outside `Blocks: [3.2, 3.3, 3.4]`, so
`--require 9` is satisfiable; `gate_consistency` PASS; the `test_class: probe` / `cwd: worktree` directive
is present verbatim and **verified necessary** — `test_gates.py:243` does default an absent `test_class`
to `manual`, which resolves INCONCLUSIVE.

## Upstream Assessment

15 rows / 15 triage sections / 15 reference files, zero disposition mismatches, re-verified pairwise.
C56's #189 re-aim is congruent across both files. No change.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C61 `check-recipe-row.sh` argument semantics undefined | low-medium | Fixed, and this was the one item with an execution consequence. Issue 1.9 now defines the contract: **`check-recipe-row.sh <token>` matches a §1 row whose `id` equals the token OR whose `cmd` contains it** — a whole-row-line match — with the reason stated, that an id-only implementation makes SC11c false while a cmd-only one makes SC11 false, because `okf-index-drift` never appears in `check_okf_index_drift.py`'s underscored filename. Issue 3.2a now declares the two row ids (`uv-recheck-criteria`, `uv-index-members`) following the file's existing `uv-*` convention, the way Issue 3.2 declares `okf-index-drift`. | `main-session` | `resolved` |
| C62 EXP-006 1567 vs its own 1563 | low-medium | Fixed — all three `1567` occurrences in `exp-006` corrected to **1563**, including the literal "Full categorisation (sums to 1567)". Pass 9 is right that this is the third false-`resolved` of its kind: pass 2 recorded "1563/1567 reconciled throughout", which was true of `plan.md` and never applied to the finding the number came from. | `main-session` | `resolved` |
| C63 Motivation 1634 denominator | low-medium | Fixed — the Motivation's parenthetical now reads **1603 of 1642**, agreeing with the sentence two lines below. Pass 5's C47 updated the file count and the second sentence and left the denominator; it has been wrong since. | `main-session` | `resolved` |
| C64 Issue 0.8 count 5 vs 8 | low-medium | Fixed and widened. Issue 0.8 now says **8 occurrences across 4 files**, citing the exact command, and distinguishes the five coverage-claim forms from **three equally-stale derived counts** (`SPEC.md:311`, `OKF-YF-EXTENSIONS.md:395`, `test_okf.py:967`) that the earlier enumeration missed by counting one variant form and not the others. | `main-session` | `resolved` |
| C65 routing count wrong in three places | low | Fixed in all three places, and pass 9 corrected **my** correction. Measured: **6 criteria invoke it** (SC4, SC7, SC8, SC10b, SC28, SC36). My pass-8 "7 of 22" counted SC0, which only `test -x`'s the path — and as pass 9 observes, if presence counted then all ten instruments gain the same +1 and "busiest" becomes vacuous. Issue 1.8's "20 criteria" and "critical path of 12" were pre-split figures from the 33-criteria era that C58's five-count sweep did not reach; both re-derived. | `main-session` | `resolved` |
| N3 index.md scoping; D-1 hard-coded 9; 1.8/1.9 reconciliation; #169 citation | note | All four. `index.md` now scopes the vacuity claim to passes 1-6 and names passes 7-8's distinct class (sibling drift with every instrument green). D-1 no longer hard-codes 9 — it defers to Issue 3.4's enumeration and records 8 today, since the set is live. Issues 1.8 and 1.9 reconciled on the `_common.sh` history (three checks in plan-055's Epic 0; six in that directory today). #169's uncited figure pair was left as-is: pass 9 re-derived it live and the substance holds, so the gap is a missing citation rather than a wrong number, and inventing a citation would be worse than the omission. | `main-session` | `resolved` |
