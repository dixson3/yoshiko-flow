---
type: Review
okf_spec: OKF-PLAN
pass: 2
---
# Red-team pass 2 — plan-048-james-dixson-ed68a5

## Verdict: REVISE

## Part A — audit of pass-1's claimed resolutions

**7 of 12 landed as claimed; 3 partial; 2 did not land.**

| # | Landed? | Evidence |
| :-- | :-- | :-- |
| C1 | **PARTIAL** | gate-nowedge correctly fixed; **gate-relations is still a cycle, now explicit** (N1) |
| C2 | YES | gate `Blocks: 3.1`; SC2 absent |
| C3 | PARTIAL | issues + criteria present; SC1b's verification is a row-count, not correctness (N6) |
| C4 | PARTIAL | SC1/SC5/SC15/SC21 improved; **SC7 and SC20 still cannot fail** (N4, N7) |
| C5 | YES — measurement independently confirmed | 18/19 carry `depends-on-skill`; `yf-herdr` omits it deliberately (rationale at its line 240) |
| C6 | YES | `5.1a depends-on: 5.1, 2.4`; SC4 → 3.2 |
| C7 | PARTIAL | edges present; **SC10d is physically undischargeable** (N2) |
| C8 | YES | 6.5a present; gate `Blocks: 6.5, 6.5a` |
| C9 | **NO** | R7 says "41 issues"; plan has **44**. "46-vs-32" is in no file; "32" unsourced. D-12 has no gate row, no issue, no script |
| C10 | YES, and honestly | `okf.py migrate` verified to do README→index, phase-log→log, type stamping; 30/30 measurement confirmed |
| C11 | YES | table verified; `_verify_row` confirms unknown disposition → `inconclusive` |
| C12 | **NO** | log.md correct, but **seven `47`-literals remain** in the body against a corpus of 48, plus hardcoded 150/610/23.4% — contradicting the preamble it added |

## Mechanical checks (run fresh)

`plan_extract` exit 0, `unparsed: []`, `{epics:7, issues:44, edges:60, gates:7, criteria:26}`.
`doc_lint` PASS. `plan_manager audit` pass. `okf.py check` ok.
**`markdown_lint.py plan.md` → `plan.md:76: ML005 table row has 4 cells, expected 3` — 1 violation.**
DAG: no cycles, no dangling edges. **19 of 44 issues named by no criterion.**

## Strengths

- The two hardest pass-1 findings were fixed **properly**: gate-nowedge is a correct cycle break, and Epic 4's collapse is honest — `okf.py migrate` independently verified to do the work.
- C5's measurement holds under re-measurement; the `yf-herdr` outlier is real and deliberate. D-5 working.
- SC1c, SC1d, SC10c, SC12, SC15, SC16, SC17, SC18, SC19 are strong — each names a mutation and asserts an exit code. **SC1c is a better control than anything in plan-047.**
- The `deferred` analysis is correct: `_verify_row` (`plan_manager.py:2056`) returns `inconclusive` for any unrecognised literal.

## Concerns

| # | Sev | Concern |
| :-- | :-- | :-- |
| N1 | high | `relational checks can fail` **still a cycle, made explicit** — `Blocks: 3.2, 3.3` while its condition draws evidence "from the rules from 3.2/3.3". Pass-1 moved it *onto* the producers of its own evidence — strictly worse |
| N2 | high | **SC10d asserts an outcome no artifact can produce** — a deleted script returns 127 *from bash*; nothing maps 127→2, and `plan_manager.py` has no gate runner. Also SC10c uses bare `scripts/` which collides with the real top-level `scripts/` |
| N3 | high | **D-12's split gate is prose in a decisions table** — no gate row, no issue, no script, no criterion. plan-047 made D-13 real via Issue 10.0 + a script + a non-zero exit |
| N3b | high | **The D-12 row is malformed GFM** — unescaped `\|` inside a code span; `ML005` fires; the Rationale column is dropped when rendered. In the plan whose Issue 1.1 exists to fix escaped pipes, in a repo carrying `.markdown-lint-on-edit` |
| N4 | high | **SC7 is true by construction** — measured: `name`/`skill-group`/`depends-on-tool` are 19/19, and every research check is `W`. Only `files_checked > 0` can fail, which is SC16's job |
| N5 | med | **R4 names three mechanisms; two do not exist and one points at deleted Issue 4.7.** `okf.py migrate` is per-directory write-as-it-goes — no batch VERIFY, no retained originals |
| N6 | med | SC1b verifies bookkeeping, not correctness — 20 rows reading "correct" satisfy it |
| N7 | med | **"declared target" has no producer** — gate-grammar, 1.5, SC1 and SC20 all consume it; 1.4b never declares one. The executor sets the bar after seeing the measurement |
| N8 | high | **Epics 1 and 3 are disconnected from the land epic** — `6.2`, `6.3` and `6.6` have no Epic-1 or Epic-3 ancestor, so validation, re-measurement and deploy can run before the widening they grade. `3.5` does not depend on `3.2` |
| N9 | high | **No edge orders `0.2` before `3.3`/`3.4`** — after C11 this is load-bearing: 3.4 makes an unrecognised disposition `fail`, which would fire on this plan's own three `deferred` rows |
| N10 | med | 19 of 44 issues named by no criterion; **5.1a adds §3 trigger rows with no control that they select > 0 files** — reintroducing D-11's silent green. The plan violates R1b at 43% while shipping R1b |
| N11 | med | The stale-literal defect **is still present and now carries a claim of resolution on top of it** |
| N12 | low | R7's numbers unsourced: "41" ≠ 44; "32" is unsupported (plan-047 Epics 6/8/9 measure 25) |

## Missing

- A producer for the "declared target" (N7)
- Any executable / gate row / issue for D-12 (N3)
- A non-vacuity control for 5.1a's new §3 rows (N10)
- A gate runner that distinguishes 127 from 2 (N2)
- Edges `3.5→3.2`, `3.3/3.4→0.2`, `6.2/6.3/6.6→Epics 1 and 3` (N8, N9)
- **Still absent since pass 1:** a stated position on `pour_fidelity.py` under the widened grammar

## Gate Assessment

| Gate | Blocks | Evaluable from a predecessor? | Verdict |
| :-- | :-- | :-- | :-- |
| Start Gate | — | n/a | fine |
| grammar widening non-vacuous | 3.1 | yes | **sound** — C1/C2 genuinely fixed |
| relational checks can fail | 3.2, 3.3 | **no — cycle, now explicit** | **N1, blocking** |
| normalizer aggregate diff | 4.2 | yes | **sound** |
| intake binding does not wedge | 5.3 | yes | **sound — the best of the C1 repairs** |
| Upstream write | 6.5, 6.5a | yes | sound |
| Reconcile Gate | reconcile step | yes | fine |

## Upstream Assessment

Improved and largely sound; `deferred` makes D-7 load-bearing and SC9 falsifiable. Two residuals:
the #173 row's `Resolved By` is `3.4` while the comment SC21 grades is posted by 6.5a, so the
posting obligation is invisible to the plan's own relational rules; and the `deferred` rows depend
on 0.2 landing before 3.3/3.4 (N9).

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| N1 | high | Gate re-pointed to `Blocks: 3.4` — the downstream consumer whose ancestry already contains 3.3 | `main-session` | resolved |
| N2 | high | Added Issue 0.6a shipping a gate-runner wrapper that maps any non-{0,1,2} exit to 2 with an explicit harness message; SC10d restated against it; SC10c's path normalized to the plan-dir form | `main-session` | resolved |
| N3 | high | Added Issue 3.6 (split-gate evaluation: emits `{tripped, review_cycles}`, exits non-zero on trip), its script in 0.6, and SC23 | `main-session` | resolved |
| N3b | high | Pipe escaped; `markdown_lint.py` re-run to zero violations; D-12 moved below D-11 | `main-session` | resolved |
| N4 | high | SC7 restated as a mutant drive — remove `skill-group` from one SKILL.md, assert exit 1, unmutated corpus exit 0 | `main-session` | resolved |
| N5 | med | R4 rewritten against what 4.1/4.2 actually deliver; the stranded 4.7 reference removed | `main-session` | resolved |
| N6 | med | SC1b now requires the per-construct before/after edge pair reproducible from `plan_extract`, and an explicit adverse-count statement | `main-session` | resolved |
| N7 | med | Issue 1.4b now owns "declare the residual target"; 6.3 cross-references it; SC20's targets named | `main-session` | resolved |
| N8 | high | Added `6.2 depends-on 1.5, 3.5, 5.1a, 2.1b`; `3.5 depends-on 3.2`; `6.6 depends-on 6.5a` | `main-session` | resolved |
| N9 | high | Added `3.3 depends-on 0.2` and `3.4 depends-on 0.2` | `main-session` | resolved |
| N10 | med | Added SC24 (5.1a's new §3 rows select > 0 files) and SC25 (2.1b's fixture drives exit 1); declared a bookkeeping-epic marker on Epic 0 so the plan satisfies the R1b it ships | `main-session` | resolved |
| N11 | med | Body figures restated as point-in-time measurements with their measurement date; the preamble's absolute claim scoped to the criteria table; R7 corrected to 44 | `main-session` | resolved |
| N12 | low | R7's comparison sourced: plan-047 Epics 6+8+9 measure **25**; plan-045's 46 is the record | `main-session` | resolved |
