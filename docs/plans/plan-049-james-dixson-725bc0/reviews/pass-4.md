---
type: Review
okf_spec: OKF-PLAN
pass: 4
---
# Red-team pass 4 — plan-049-james-dixson-725bc0

## Verdict: REVISE

## Part A — pass-3 resolutions

H1, H3, M2, Missing and all of L1–L9 **landed**. **H2 PARTIAL — `context.md:72` still said "nine"**
(the replacement spanned a line wrap and silently no-opped). M1's text landed but made SC13
unfalsifiable (H2 below).

**Pipe repair verified clean** — every table in every bundle file re-parsed by unescaped-pipe split:
**zero column-count mismatches, zero raw `|` inside any code span in any table row.**

## Part B — mechanical verification

7 epics, **43 issues**, **60 edges**, 6 gates, **41 criteria**, `unparsed: []`; zero cycles, zero
dangling, zero duplicate ids, `0.1` the only unnamed issue. `doc_lint` PASS on all five bundle files;
`audit` all-pass; `okf.py check` OK; `markdown_lint` clean on all 19.

Premises re-measured: `unparsed[]` **81 across 24 of 49** ✓; **137 gates, 49 Start Gates**, and the
"80 of 137" figure reproduces exactly ✓; the 89 declarations reproduce to the entry ✓;
`disposition-alphabet-offered` 30/31 ✓; every code anchor line-exact ✓.

## Strengths

- **Gate reachability and frontloading clean, re-derived by ancestor closure.** Both wrapper scripts
  are ancestors of everything all three gates block. Both human gates correctly `human`-typed —
  `SKILL.md:1137` guarantees a green `test -f` cannot auto-resolve them.
- **The Reconcile Gate vacuity genuinely closed** — the jq driven through all three populations.
- **SC27 is genuinely falsifiable:** the preamble-scoped grep returns **0** today while the unscoped
  grep returns 2. The scoping is load-bearing, not cosmetic.
- The plan's own `## Epics` carries two prose `depends-on:` code spans; **neither is followed by an
  id**, so Issue 2.1's widening cannot invent an edge in this plan.

## Concerns

| # | Sev | Concern |
| :-- | :-- | :-- |
| H1 | **high** | **The vendored engine is a silent green, and no criterion detects it.** Built as specified and run against a real typed `plan.md`: `{"verdict":"PASS","files_checked":0}`. Cause: `doc_lint.py:47` computes `REPO_ROOT` from `__file__.parent.parent`, so a vendored copy resolves the root to the *skill dir*. Two transitive deps also missing (`plan_template`, `plan_extract`). **SC15 checks only that the file exists; SC17 expects `not-a-typed-document`, which the broken copy also emits.** Epic 4 would land a green binding that enforces nothing — the precise defect the plan was written to close |
| H2 | **high** | **SC13 cannot fail.** The fixture path it names is a **flat file**, which has no sibling `plan.md`, so `bundle_status()` returns null, `STATUS_SEVERITY` never applies, and it **exits 0 today, before any fix**. Measured both shapes: `<dir>/plan.md` → exit 1; the named flat path → exit 0. A vacuous criterion on the plan's own load-bearing self-trip fix |
| M1 | med | **`context.md` still says "nine" — fourth consecutive cycle of this exact drift**, and it contradicts `context.md`'s own Runtime-assumptions section eleven lines above |
| M2 | med | **Issue 3.2's "and nothing else" is measurably wrong** — the all-absent predicate fires on **two** gates: plan-008's stub **and plan-006 L194**, `### Reconcile Gate` / `- Not needed — no upstream issues incorporated`. A live authoring idiom, and the same false-positive shape one level down |
| M3 | med | **Issue 0.9 mutates the fingerprinted span after approval.** The marker sits inside `## Epics`, which is inside the fingerprint span, so stripping it mid-run flips the hash and every later `status`/`resume` prints STALE-APPROVED. Advisory, but a plausible unattended halt |
| M4 | med | **`skills/<name>/` is an unresolved placeholder** in Issues 4.1 and 4.3; `sync.py`'s consumer lists are hand-authored, so the executor must *choose* — a scope decision, not an implementation detail |
| L1–L7 | low | three/four-layer residue in `index.md` and the EXP-002 row; SC37's first branch already satisfied (30/31); `index.md` not updated for `assets/` and `scripts/`; two drafting literals drifted (731→752, 1340→1341); Issue 4.4's "bundle gate scripts" ambiguous; 21 of the 89 declarations use lettered ids, unmentioned; declaration order inverted in four places |

## Missing

**A criterion that proves the deployed engine works** — H1 restated. Every enforcement criterion
(SC15–SC18) is satisfiable by an engine returning `files_checked: 0` on everything. **The
false-positive control Epic 1 has (mutant D) and Epic 3 gained (3.2b) is exactly what Epic 4 lacks.**

**Nothing else is silently deferred** — each `partial`/`deferred` row checked against its recording
issue, and every finding recommendation against its scheduling issue.

## Gate Assessment

Clean. All six gates parse; reachability re-derived by ancestor closure; no cycles, no frontloading
misses; the exit-2 wording matches the skill's INCONCLUSIVE semantics; the Reconcile Gate's
population assertion verified working.

## Upstream Assessment

**Sound and consistent across all three surfaces**, full untruncated titles, one reference file per
row. R2b measures **zero** errors at `review`, confirming Issue 0.3's premise. The Upstream-write
gate correctly requires the grant be generated from the table.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 | high | Issue 4.1 extended to the **full transitive set** (`plan_extract.py`, `plan_template.py`, `renderable_fences.py`, `document_types/`) and to **root resolution by git discovery or explicit `--root`**; new **SC42** requires the **vendored** copy, run from a deployed vault against a real typed document, to report `files_checked >= 1` **and reproduce the `_shared/` verdict** | `main-session` | resolved |
| H2 | high | SC13's fixture path corrected to `tests/fixtures/doclint/plan-relations/<bundle>/plan.md` with `status: review`, driven `--type plan-relations --path`; the criterion now asserts **exit 1 pre-fix and exit 0 post-fix from the same invocation** | `main-session` | resolved |
| M1 | med | `context.md` corrected to **eight** — this time with an assert, since the prior replacement spanned a line wrap and silently no-opped | `main-session` | resolved |
| M2 | med | Issue 3.2 corrected to **two**, naming plan-006's "Not needed" idiom and requiring an explicit exempt-or-fire decision; **SC41 extended to cover 3.2's blast radius** | `main-session` | resolved |
| M3 | med | Issue 0.9 states the expected fingerprint drift and that the STALE-APPROVED warning is advisory and expected, with the re-stamp path named | `main-session` | resolved |
| M4 | med | `skills/<name>/` resolved to **`skills/yf-plan/`** in both issues | `main-session` | resolved |
| L1–L7 | low | three/four-layer note added at both sites; SC37 given the 30/31 baseline and a strict-decrease requirement; `index.md` gains `assets/` and `scripts/`; Issue 6.2 notes the drifting literals; 4.4 disambiguated to this plan's scripts; 2.1 states lettered-id handling; declaration order left as-is (the DAG is correct; renumbering would churn every cross-reference) | `main-session` | resolved |
