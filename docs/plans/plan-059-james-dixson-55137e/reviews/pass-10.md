---
type: Review
okf_spec: OKF-PLAN
---
# Red-team pass 10 — plan-059-james-dixson-55137e

## Verdict: APPROVE

**No defect falls in the blocking class.** Pass 9's blocker and all seven pins verify applied by
execution and by grep. **The asserted-literal set is now closed** — all 62 literals across both auto
gates and all 25 criteria were enumerated and traced to a producing issue.

## Verified by execution

- **Pass 9's K1 is fixed.** `--type escalations` occurs 2x in gate 2's `Test:`; the singular occurs
  **0x** in any executable. Mechanism confirmed: `doc_lint.py:164` raises `Inconclusive` when a
  schema's `type` differs from its file stem, and all 17 existing stems follow the convention. Gate 2
  today returns `INCONCLUSIVE: no schema for type 'escalations'` — **the correct red for a schema
  Issue 2.2 has not yet written**, and it resolves the moment `escalations.toml` lands.
- **All seven pins applied** — the `RC <label> <exit-code>` grammar (0.1), `judgement: fired` (5.1),
  `taxonomy` (2.7), the `escalation` JSON key (3.1), `escalation-raise` (3.2), `--answer` (2.5), and
  `context.md`'s SC8b/`herdr` skip-not-fail carve-out.
- **Full sweep, every clause as a single `bash -c` string**: 20 clause-form criteria ->
  **19 FALSE / 1 TRUE (SC2c)**; gate 1 rc 1; gate 2 red for its advertised reason. **Every red is a
  correct red** — rc 4 = `jq` on empty stdin (verb absent), rc 5 = the pytest banner Issue 5.3 fixes,
  rc 2 = the file Issue 4.2b creates, rc 1 = an absent marker / env-file / upstream edit.
  `gate_consistency.py`: **PASS, 5 gates.**
- **SC1b's fixture checked directly**, because it is the one criterion resting on a corpus file no
  issue produces: `plan-027/reviews/pass-1.md` exists, lints `errors: 0`, and carries **four `med`
  cells** — off-vocabulary under **all three** Start-Gate options, with a `Severity` header column
  for Issue 1.3's by-name locator. **Genuinely satisfiable, not vacuous, and not option-dependent.**
- **Graph integrity after ten rounds**: 36 issues, 25 criteria, **zero** dangling `depends-on`,
  **zero** dangling `Discharged-by`, **zero** dangling gate `Blocks`, and every issue discharged.

## The literal-closure sweep — the set is CLOSED

| Category | Count |
| :-- | --: |
| Pinned verbatim in a producing issue | **45 of 62** |
| Pinned in substance (grammar + label composed; regex tolerant of spacing) | 6 |
| **Not this plan's to produce** — pre-existing corpus bundles or landed `doc_lint`/`gh` surface | 10 |
| **Under-determined** (passable) | **1** — SC6b |

## Concerns — all class NONE

| # | Concern | Severity |
| :-- | :-- | :-- |
| Q1 | **SC6b asserts a step name matching `judgement`, but Issue 5.2 never named its wrapper verb.** Same *shape* as passes 8 and 9, but **materially weaker**: those had a wrong-by-default spelling actively pulling the executor away; here the assertion is a permissive substring, the epic is titled "Make yf-judgement observable", and Issue 5.1's `judgement-echo-check` already carries the token — **a correct implementation lands on it by default rather than against the grain.** | medium |
| Q2 | **Gate 2's Instructions still said `--type escalation` in item (3).** The executable `Test:` was correct; only the prose gloss retained it. **Pass 9's resolution row claimed the Instructions were updated; they were not.** | low |
| Q3 | **`escalation-report`'s `raised` key is cumulative while `state: raised` is current**, and only Issue 2.5's parenthetical distinguished them — Issue 3.5, which *produces* the key, did not. | low |
| Q4 | Gate 2's Instructions contained two items numbered `(3)`. | low |

## Missing

**Nothing.** The `manual:` criteria each state why an exit code cannot establish the claim, *"which
is the honest reading rather than a gap."*

## Gate Assessment

Five gates, `gate_consistency.py` PASS, no reachability cycles, no frontloading misses. **Gate 2's
four load-bearing constructions all verify sound** — the forced `review` status, the by-check-name
positive control written outside the bundle, the redirect off the `&&` chain, and `${PLAN_DIR}` at
pour time. The upstream-writes gate's deliberate absence of a `Test:` is correct: *a green command
cannot establish authorization.*

## Upstream Assessment

Unchanged and sound after ten rounds. Five upstream issues, four `partial` with explicit in/out
boundaries, one `deferred` with its seam named (Issue 3.4) and tested (SC7).

## Bottom line, quoted

> After ten passes the plan is internally consistent, its instrument set is closed, its graph is
> clean, and **every red I ran is a red for a reason an issue in this plan removes.** The three
> residual findings are traceability pins and one stale word; none would cause a competent executor
> to build the wrong thing, none makes a gate or criterion unpassable, and none prevents close.
> **APPROVE.**

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| Q1 SC6b's verb unnamed | medium | Adopted. Issue 5.2 now names **`judgement-never-fired-report`**. Taken despite being passable, because it is the third instance of one class and the cost is a word. | `main-session` | `resolved` |
| Q2 stale singular in the gloss | low | Adopted — **and it is the more instructive of the two.** Pass 9's resolution row said the Instructions were updated and they were not: **the same record-without-verifying defect this plan has now committed three times in its own review bookkeeping** (pass 4's two unmade edits, the `exp-001` banner's three failed anchors, and this). Verified after fixing: **0 singular occurrences, 3 plural.** | `main-session` | `resolved` |
| Q3 `raised` cumulative vs current | low | Adopted — Issue 3.5 now states it at the key's producer, where SC5's `>= 2` and SC6c's `== 1` are only consistent under that reading. | `main-session` | `resolved` |
| Q4 duplicate `(3)` | low | Adopted. | `main-session` | `resolved` |
