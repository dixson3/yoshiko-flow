---
type: Review
okf_spec: OKF-PLAN
id: pass-1
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
verdict: REVISE
---
# Red-team pass 1 — plan-066-james-dixson-e7fadb

**Verdict: REVISE** — 16 concerns (5 high, 2 medium-high, 6 medium, 3 low).

> Nine epics of sound reasoning sitting on a verification layer that this repo's own linter
> scores 17/17 non-conformant.

## Strengths

- The six corrections to #317 **hold under independent re-measurement** — 20 skills, 19 pages,
  groups 5/4/8/3, 5 formulas, `e-okf-version-pin` the only out-of-vocabulary §2 category, the P0
  reproducing, an empty stub passing. Nothing in the findings was overstated.
- The **code-side negative-control convention**, born from a measured false green, is the best
  thing in the plan.
- **SC2 is genuinely good.** Executed: empty stub → `hr=0, h2=1` fails; real page → `hr=1, h2=6`
  passes; site root → `0/0`, no false pass. The one conjunctive, executable, non-vacuous row.
- `gate_consistency.py` → `PASS, 6 gates, 0 findings`. No unopenable gate.

## Concerns

| # | Severity | Concern |
| :-- | :-- | :-- |
| C1 | high | **0 of 17 criteria are executable clauses** — `doc_lint` returns 17 `verification-clause` warnings. plan-065 shipped `plan065_checks.py` with one verb per criterion. A plan whose subject is "instruments that report success without doing the thing" regressed the corpus norm. |
| C2 | high | **SC13/SC14 are vacuously true today**, with zero work done — equally satisfied by never authoring the pages. Worse, SC13 omits `-r`: under system grep it exits **2** (`Is a directory`) having searched zero bytes, and a reader scores PASS. It only exits 1 on this machine because `grep` is aliased to ugrep. |
| C3 | high | **25 of 44 issues are named by no success criterion**, including **all six of Epic 3** (the entire manifest-repair half of Class B) and **all three of Epic 7**. |
| C4 | high | **The plan repeats #317's undercount one level up.** The checker corpus is `web/content/**`, so `README.md:105-106` — carrying the identical drifted harness matrix — is structurally unreachable, and absent from 4.4's site list. `AGENTS.md:78` names the same retired roots. SC7 would certify "all 15 sites repaired" while the repo's most-read document stays wrong. |
| C5 | high | **Issue 6.4 would author a page that never renders, silently.** Measured: created `web/content/concepts/glossary.md`, ran the gate's exact Test → exit **0**, **32 pages** (unchanged), zero warnings, nothing emitted. `pelicanconf.py` sets no `PAGE_PATHS`, so the default `["pages"]` excludes any new directory. **The plan's own thesis firing inside the plan.** |
| C6 | medium-high | **Issue 5.5 / SC12's `render.py check-dir` is vacuous.** Executed over the diagrams the plan calls wrong: `{"status":"ok","orphans":[],"stale_advisory":[]}`, exit 0. `render.py:154-169` exits non-zero **only on orphans**; staleness never affects exit code. And the human-read gate `Blocks: 5.5` — spending a human gate to unblock a check that passes today with no work. |
| C7 | medium-high | **SC3/SC10 depend on commit topology a squash destroys.** plan-064 landed as a single commit; 063/065 as `--no-ff` merges. Commit messages here are epic-level, so "Issues 2.3 and 3.4" cannot be located in a log. Meanwhile `check_amendment_log.py --plan` is a CV row for plans 060, 062, 063, 064 — 066 adds none. |
| C8 | medium | **Issue 0.1's "living-amendment-log entry" has no home.** Neither `spec/checks.md` nor `yf-drift-check/SPEC.md` has an amendment log; only root `SPEC.md` does, and it contains zero `REQ-CHECK-*` ids. |
| C9 | medium | **The "Checkers are fail-capable" gate is weaker than its own Condition** and has no vacuity floor. Its Test asserts exit 0; SC4 demands "one observed failure per checker" — that half is not in the gate. A harness that silently skips a checker exits 0 and opens it. |
| C10 | medium | **The "Build green" gate Test is unsatisfiable in an execute worktree.** It hardcodes `web/.venv/bin/pelican`; `web/.venv` is untracked and exists only in the primary checkout. The gate blocking Epics 4/5/6 fails with exit 127, and no issue creates the venv. |
| C11 | medium | **Issue 2.6 self-inflicts a red validation window.** It lands recipe rows for checkers that stay red until 4.9/5.3. `_validate_merged` tier 1 returns `fail` on any non-pass, blocking any intermediate land from 2.6 onward. |
| C12 | medium | **D6's bet is real but narrower than stated.** CV's FULL tier IS mechanically enforced by `_validate_merged`. But CI runs no tier (`grep change_validation .github/workflows/*` → nothing), and the FAST on-edit trigger is an always-loaded *prose* rule — the same class that produced 4-opportunities/0-catches. The coverage binds on the yf-plan land path only. |
| C13 | medium | **A declared `not_checked` class with no discharge mechanism.** `architecture.md:65`'s `utility (7) — skill authoring, drift checking, …` is a prose membership list with the same semantic-mis-assignment risk the plan declares unchecked for diagrams — but the human-read gate is scoped to PNGs only. |
| C14 | low-medium | #317 is `include`, but the only `resolves-upstream: #317` is on 1.2 marked `(partial)`. All five `include` rows carry `Resolved By: _TBD_` (R2a promotes to `E` at `reconciling`). |
| C15 | low | SC2 names "emitted `index.html`" — there are 33. No false pass at site root, so ambiguity not defect. |
| C16 | low | SC12 asserts what the plan's prose does **not** say — unfalsifiable by execution, vacuously true from the moment written. |

## Missing

- No issue or criterion covers `README.md` / `AGENTS.md` (C4).
- No `gate-plan066-amendment` or req-coverage CV rows, breaking a four-plan precedent (C7).
- No stated location for Issue 5.4's per-diagram read records.
- **Epic 7 is structurally a dumping ground** (three unrelated fixes, zero criteria) but defensible
  in content — 7.3's orthogonality is measured. Fix with criteria, not by unbundling.
- **Epic 6 has effectively no verification**: two vacuous greps, 6.3/6.4 covered by nothing, and
  6.4's output would not render.

## Gate Assessment

`gate_consistency.py` → `PASS, 6 gates, 0 findings`. Both flagged gates are **reachable** —
"Checkers are fail-capable" is satisfied by 2.5 in Epic 2, which it does not block; "Diagram human
read" by 5.4, not in its Blocks set. No cycle. The defects are *adjacent* to reachability: a
placement miss (C6), a Test weaker than its Condition (C9), and a Test that cannot run in the
worktree it will run in (C10).

## Upstream Assessment

Dispositions reasonable. Folding #104/#127/#363/#322 justified by D3, #104's inclusion measured
rather than assumed. #247/#263 as partials is right. Excludes clean. `gh` confirms #315/#316
CLOSED, so #317's sequencing precondition is genuinely satisfied. Only flaw is C14.

## Resolutions

All 16 resolved by the main session under the autonomous default.

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | high | **Accepted.** Added Issue 0.4 authoring `scripts/checks/plan066_checks.py` (one verb per criterion, `plan065_checks.py` precedent) and rewrote all criteria as executable clauses. `doc_lint` verification-clause warnings: **17 → 0**. | `main-session` | `resolved` |
| C2 | high | **Accepted.** SC13/SC14 are now conjunctive and positive — assert the authored file exists AND makes the correct positive claim, then keep the negative grep as a second leg with `-r` and an asserted exit 1. Both are now discharged by a checker verb, not by a reader scoring a grep. | `main-session` | `resolved` |
| C3 | high | **Accepted.** Added SC12 (Epic 3 manifest rows, incl. 'every §6 row names an edge that exists' — also mechanising R6), SC19 (Epic 7), SC15 (Epic 6 renders), SC21/SC22/SC23/SC24. Uncovered issues **25 → 11**, and the 11 remaining are instrument-building steps now documented as deliberately uncovered with the reason. | `main-session` | `resolved` |
| C4 | high | **Accepted — this was the sharpest finding.** The checker corpus is now a PARAMETER covering `web/content/** + README.md + AGENTS.md` (Issues 2.1, 2.2); Issue 4.4 names both files with the `prune_private.rs:487` / `harness_desc.rs:381` ground truth; Issue 3.2 adds `README.md`'s harness table to the node; SC7 restated. New risk **R14** records the class. | `main-session` | `resolved` |
| C5 | high | **Accepted.** Issue 6.4 must author under a rendered path or amend `PAGE_PATHS` in the same issue; new Issue 6.5 asserts every Epic-6 page emitted a non-trivial `index.html`; SC15 discharges 6.1-6.5. New risk **R15**. The measurement is quoted in the issue text so the next author cannot re-derive it the hard way. | `main-session` | `resolved` |
| C6 | medium-high | **Accepted.** Dropped `5.5` from the 'Diagram human read' gate's Blocks (now `8.1` only). Issue 5.5 restated as ORPHAN DETECTION ONLY with the `render.py:154-169` evidence; old SC12's byte-equality-abstention row deleted (see C16) and replaced by SC24. | `main-session` | `resolved` |
| C7 | medium-high | **Accepted.** SC3 is now `check_amendment_log.py --plan plan-066-…` → exit 0, and Issue 0.5 adds the `gate-plan066-amendment` + req-coverage CV rows with §3 globs, restoring the 060/062/063/064 precedent. SC10 no longer reads commit topology at all — it compares the PNG encoding signature (colortype/`sRGB`/IDAT) across all six, which survives a squash land. | `main-session` | `resolved` |
| C8 | medium | **Accepted.** Issue 0.1 now names the ROOT `SPEC.md` as the amendment-log target and requires reconciling the `REQ-CHECK-*` id namespace with `check_amendment_log.py`'s root-`SPEC.md` assumption. | `main-session` | `resolved` |
| C9 | medium | **Accepted.** The gate Test is now `test_negative_controls.py --all --min-checkers 4`, and Issue 2.5 requires the harness to PRINT AND ASSERT a per-checker observed-failure count. The floor is in the Test, not only in SC4. | `main-session` | `resolved` |
| C10 | medium | **Accepted.** Issue 1.2 now bootstraps the environment first (`uv run --with-requirements web/requirements.txt`, or an explicit venv step), and the gate Test is `plan066_checks.py build-clean` with an explicit instruction not to hardcode `web/.venv`. | `main-session` | `resolved` |
| C11 | medium | **Accepted.** Issue 2.6 now depends on 4.9 and 5.3, so the recipe rows land green. Verified no cycle: the 'Checkers are fail-capable' gate is satisfied by 2.5 and does not block Epic 2, so 2.5 → gate → Epic 4 → 4.9 → 2.6 is acyclic (re-checked mechanically, 0 cycles over 57 edges). | `main-session` | `resolved` |
| C12 | medium | **Accepted.** D6 and R5 now state the boundary explicitly — FULL tier is mechanically enforced by `_validate_merged`, but CI runs no tier and the FAST trigger is itself prose, so coverage binds on the land path only. New Issue 2.8 adds the CI job; new SC20 asserts it. | `main-session` | `resolved` |
| C13 | medium | **Accepted.** Issue 2.1 now parses the enumerated GROUP-MEMBER NAMES at `architecture.md:65`, not only the integer — the reviewer is right that these are machine-readable, unlike a rendered PNG. SC9 renamed to `group-membership` and covers both the diagram and the prose list. | `main-session` | `resolved` |
| C14 | low-medium | **Accepted.** Added `resolves-upstream: #317 (include)` to Issue 8.5, which also now requires filling the `Resolved By` column for all five include rows before close. The 5 remaining R2b warnings are expected until reconcile. | `main-session` | `resolved` |
| C15 | low | **Accepted.** SC2 now names `output/skills/yf-okf-hygiene/index.html` explicitly and asserts `>= 2 <h2>` rather than `>= 1`. | `main-session` | `resolved` |
| C16 | low | **Accepted.** The old SC12 (asserting what the plan's prose does *not* say — unfalsifiable and vacuously true when written) is DELETED. The prohibition lives in Issue 5.5's text, and SC24 now makes a positive, executable claim about orphans instead. | `main-session` | `resolved` |
