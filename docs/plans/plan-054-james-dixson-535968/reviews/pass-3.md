---
type: Review
okf_spec: OKF-PLAN
id: pass-3
description: Red-team pass 3 (third independent, via Agent) — plan-054
---

# Red-team pass 3

## Verdict: REVISE

**Frozen-snapshot check: PASS** — `1d3a06e539eb…` at start and end, identical. Pass 2's
moving-target defect is closed; this is a review of a stable artifact.

**12 of 14 pass-2 resolutions reproduced.** C26 and C36 did not. All 8 pass-3 concerns are now resolved.

## Strengths

Verified by execution, not read:

- **The DAG, gates, upstream layer and control naming are now genuinely solid.** `anc(6.5a)=52/57`,
  `anc(6.8)=56/57`, 0 cycles, 0 edges to unknown ids, `unparsed: []`.
- **C23 held under adversarial re-derivation** — derived set == named set == 8/8, and no
  self-scraping literal survives. `reviews/` is confirmed not a risk: `_derive_manifest` greps
  `${PLAN_MD}` only.
- **C27's class is closed, not just its instances** — all 13 `resolves-upstream` declarations
  agree with both the disposition column and `Resolved By`; zero mismatches on an independent
  cross-check. `#154 → exclude` is **verified skipped in source** (`plan_manager.py:2996`), not
  assumed.
- Upstream state confirmed live via `gh`. **The gate layer is the strongest part of this plan.**

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| N1 | high | **SC9 and SC10 are vacuous greens — a zero-match `cargo test` filter exits 0.** Measured: `-- revert_through_symlink --exact` → `running 0 tests … ok`, **exit 0**; a deliberately bogus name also exits 0. Neither function exists, and neither Issue 2.3 nor 2.4 commits to those names. Cargo has no `--fail-if-no-tests`. **This is pass-2's own headline pattern inverted into a deterministically-PASSING one, which is strictly worse because it never announces itself** |
| N2 | high | **Issue 1.5's site count is still wrong, by ~2×, and SC6 is fleet-wide while 1.5 is two-skill.** Measured: **32 invocation sites across 4 skills and 8 files** — `yf-markdown-format` 11, `yf-markdown-pdf` **10**, `yf-markdown-html` **8**, `yf-markdown-lint` 3. Two entire skills are unnamed in the plan. SC6 asserts the property fleet-wide, so **it fails after 1.5 completes as scoped** |
| N3 | high | **1.5 injects `${SKILL_DIR}` into four skills that have no resolver at all.** Measured: all four markdown skills contain **zero** `SKILL_DIR` occurrences, and none is among 1.3's 19 emission targets (that count is otherwise correct). After substitution they reference an unset variable — `uv run ${SKILL_DIR}/scripts/md2pdf.py` expands to `uv run /scripts/md2pdf.py`. Consequence: the consumer set becomes 23 while SC5's script is literally named `check-sync-emits-19.sh` — **a hardcoded count baked into a filename**, the exact defect 0.8 bans |
| N4 | high | **SC2b is unsatisfiable: nothing in the plan ever records a GREEN.** `verify-all` requires per control both a `record-red` non-zero record and an `assert-distinguishes` zero record. `assert-distinguishes` appears **once in the whole plan** — inside 0.6's enumeration of the harness's verbs. No issue runs it. SC2b is discharged-by 6.6, which will exit 1 forever |
| N5 | med | **SC30/0.9's diff fails by construction** — 0.7 authors 8 fixtures, only 4 are referenced by criteria, so a symmetric diff reports 4 extras and exits 1. Naive scraping also picks up bare directory refs and `controls.txt`. SC30's title also overclaims: SC16, SC19, SC9/SC10 and SC17 name no `assets/` path and are invisible to it |
| N6 | med | **SC1's named instrument is already green and has no temporal dimension.** `cargo test -p yf --bins coverage` → 5 passed today. `coverage.rs`'s own docstring says it proves a test *names* a REQ id — it would stay green if a REQ were added *after* its implementation |
| N7 | med | **0.1 is used as a generic epic-root proxy, and C25's inversion made that expensive and semantically false.** 19 issues declare `depends-on: 0.1`, including every doc issue in Epics 4/5. Rewriting `README.md` now serializes behind fixture authoring for parsing defects. Sharper sub-case: **0.7 authors fixtures before 0.2–0.5 specify the contracts they assert** — a SPEC-first inversion introduced by the C25 fix |
| N8 | low | Risk rows are out of order — R1…R9, R11, R13, R12, R10 |

## Missing

1. An issue that runs `redcheck.sh assert-distinguishes` (N4).
2. Resolver blocks for the four markdown skills 1.5 rewrites (N3).
3. Named `#[test]` function names inside Issues 2.3/2.4 matching SC9/SC10 (N1).
4. A criterion instrument for SC9/SC10 that can fail when the test is absent (N1).

## Gate Assessment

All five gates pass `gate_consistency`. Reachability is sound — the RED gate blocks a clean 1:1
onto the 8 controls and its evidence producer 0.1 (via 0.7 ← 0.6) sits outside the Blocks set.
The two human gates on 6.8 are correctly placed for an irreversible, auto-publishing write, and
C31's INCONCLUSIVE-blocks posture is consistent between gate and R8.

**N4 is not a gate defect** — `verify-red-all`, the gate's verb, needs only RED records. It is
SC2b, a completion criterion, that is stranded.

## Upstream Assessment

**Materially improved and now mechanically coherent.** 23 rows, 22 non-`exclude`, zero
disposition mismatches across all 13 declarations. Live `gh` confirms #154 CLOSED; #119, #121,
#127, #229, #231 OPEN as claimed; no plan-054 tracker exists, matching the note. The residual
`verify-reconcile` failures are entirely work-not-yet-done and clear through execution.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| N1 | high | **Reproduced independently before fixing** — `cargo test … -- <bogus> --exact` prints `running 0 tests … ok` and exits **0**. SC9/SC10 repointed to `check-cargo-test-ran.sh <fn>`, which asserts the run actually executed the test rather than trusting the exit code. The `#[test]` names are now stated **inside Issues 2.3 and 2.4** (`revert_through_symlink_preserves_link_and_clears_block`, `opencode_read_layers_surface_shadowed_keys`) and the criteria name the same strings, so criterion and authoring issue cannot drift. SC16 also reports `holds` today but is **deliberately** a regression guard — like SC7 it asserts a property that must not break, and unlike SC7 it needs no paired positive because 'the FULL tier still passes' is the whole claim. | `main-session` | `resolved` |
| N2 | high | Re-measured in the main session and confirmed at **32 invocation sites across 8 files in FOUR skills** — `yf-markdown-format` 11, `yf-markdown-pdf` 10, `yf-markdown-html` 8, `yf-markdown-lint` 3. Both prior figures (14, then 16) were wrong and named only two skills. **1.5 is now a DERIVED sweep**, not a count: the set comes from `grep -rlE '\.claude/skills/[A-Za-z0-9_-]+/scripts/' skills/`. The literal figure is retained only as a dated measurement, not as the definition. | `main-session` | `resolved` |
| N3 | high | Confirmed: all four markdown skills carry **zero** `SKILL_DIR` occurrences. **1.3's emission set widened 19 → 23** to include them, so `${SKILL_DIR}` is defined before 1.5 substitutes it. SC5's script renamed `check-sync-emits-all.sh` and the criterion now states the count is **derived, never embedded** — a literal baked into a filename was the same drift defect 0.8 bans. | `main-session` | `resolved` |
| N4 | high | Confirmed: `assert-distinguishes` appeared exactly once in the plan, inside 0.6's enumeration of the harness's verbs. Added **Issue 0.8a**, which obliges each fix issue to run `redcheck.sh assert-distinguishes <fixture> <control>` on its post-fix tree and then verifies every control carries BOTH records. SC2b's `Discharged-by` repointed to `0.8a, 6.6`, and 0.8a wired into 6.5a's predecessors — re-measured, zero escapees from `anc(6.8)`. | `main-session` | `resolved` |
| N5 | med | SC30 and Issue 0.9 both restated as a **DIRECTIONAL** check — *referenced ⊆ present*, never symmetric — since 0.7 deliberately authors 8 fixtures while only 4 are named by criteria. Bare directory references and `controls.txt` are excluded. SC30's wording narrowed to 'every criterion command **that names an `assets/` path**', with the `cargo` / `uv run` / `manual:` criteria declared explicitly out of its reach rather than silently missed. | `main-session` | `resolved` |
| N6 | med | SC1 restated to assert the **specific new REQ ids from 0.2–0.5** are present in `SPEC.md`, marked `(testable)`, and named by a tagged test — so `check-req-coverage.sh` is **RED on today's tree** and can only go green through this plan's work. The criterion now also records why bare `coverage.rs` is insufficient: it proves a test *names* a REQ id and has no temporal dimension. | `main-session` | `resolved` |
| N7 | med | Epic 0 restructured. **0.2–0.5 (the SPEC issues) are now roots**, `0.7 ← 0.2, 0.3, 0.4, 0.5, 0.6`, and `0.1 ← 0.7` — so fixtures are written against landed requirements, closing the SPEC-first inversion the C25 fix introduced. Every Epic 4/5 documentation issue and 6.1/6.3 were **repointed off 0.1**; re-measured, only the five Epic 3 fix issues still depend on it, which is semantically correct since those are the fixes the RED baseline is for. | `main-session` | `resolved` |
| N8 | low | Risk rows reordered R1…R13. | `main-session` | `resolved` |
