---
type: Review
okf_spec: OKF-PLAN
---
# Red-team pass 9 — plan-059-james-dixson-55137e

## Verdict: REVISE

**One blocking defect, one word wide.** Pass 8's two blockers both verify fixed by execution. The
class pass 8 opened — *an asserted literal no issue produces, mismatching the producing issue's own
spelling* — has **one more instance, in the sibling position**. Everything else is refinement.

## Verified by execution

- **Pass 8's J1 (SC5) is fixed and satisfiable in BOTH topologies.** `.raised >= 2 and .pushes <= 1`:
  no-herdr gives `pushes = 0`; a batched push gives 1. Issue 2.5's two escalations give `raised = 2`,
  and SC6c's `length == 1` is exactly satisfied by the single still-`raised` entry.
- **Pass 8's J2 is fixed** — both instrument literals now occur in Issue 0.1 **and** SC0a, matching
  character-for-character (`gate-consistency`, hyphen, not the script's underscore).
- **Full sweep re-run as single `bash -c` strings**: 25 criteria (20 clause-form, 5 `manual:`) and
  both auto gates. **19 FALSE / 1 TRUE (SC2c), gates rc 1 / rc 1** — and `recheck-criteria` agrees
  exactly. **SC0a is genuinely evaluated, not `skipped-self-reference`.** `gate_consistency.py` PASS.
- **Every red is a correct red.** rc 4 = `jq` on empty stdin because the verb does not exist yet;
  rc 5 = the pytest-banner error Issue 5.3 exists to fix; rc 2 = the file Issue 4.2b creates.
- **Network dependence is exactly four, as `context.md` states** — SC0b, SC2d, SC9b, SC9c. No other
  criterion touches the network.
- **Graph integrity after nine rounds:** 36 issues, **zero** dangling `depends-on`, **zero** dangling
  `Discharged-by`, **every** issue discharged by at least one criterion.

## Blocking concern

| # | Concern | Class | Severity |
| :-- | :-- | :-- | :-- |
| K1 | **Gate 2 forces a `doc_lint` type the plan never creates: `--type escalation` vs Issue 2.2's `escalations.toml`.** `doc_lint.load_schemas` requires a schema's `type` to equal its **file stem** (`doc_lint.py:164`), and an unknown `--type` returns **INCONCLUSIVE, not FAIL**. Measured: `--type escalation` -> `{"verdict":"INCONCLUSIVE","reason":"no schema for type 'escalation'"}`. Issue 2.2 writes `escalations.toml` -> stem `escalations`; gate 2 invokes the **singular** twice in its `Test:` and once in its Instructions. **A faithful executor leaves gate 2 unresolvable forever**, and it `Blocks: epic:3`. It propagates: gate 2's sweep row stays non-zero, so SC0's all-rows-zero rule makes it a close blocker. The **plural is convention-correct** — all 17 existing schema stems equal their document's base name. | 3 + 4 | high |

## Non-blocking (class NONE)

| # | Concern | Severity |
| :-- | :-- | :-- |
| P1 | **The `RC <label> <code>` row grammar is asserted by SC0/SC0a but specified by no issue.** Issue 0.1 pins the two *labels* but not the *shape*; an executor writing a markdown table leaves both red. **The last unpinned literal in Epic 0.** | medium |
| P2 | SC6d asserts `judgement: fired`, which no issue names — and `test("judgement: fired")` does **not** match `judgement: not-fired`, so they are genuinely independent literals. | low |
| P3 | SC2d requires the filed body to contain `taxonomy`; Issue 2.7 does not ask for it. | low |
| P4 | SC4's JSON key `escalation` is not pinned by Issue 3.1. | low |
| P5 | SC4b asserts `--assert-invocation escalation-raise`, but Issue 3.2 never names that verb. | low |
| P6 | SC3's `--answer` flag is not named by Issue 2.5 (which pins every `escalation-raise` flag but no `escalation-resolve` one). | low |
| P7 | **SC8b is the one criterion needing `herdr` on PATH, and `context.md`'s degraded clause does not carve it out** — it claims a machine without `herdr` can execute every epic. | low |

## Gate Assessment

Five gates, `gate_consistency.py` PASS. **Gate 2 is red today for the reason it advertises AND for
K1 — the two are distinguishable:** the redirect-off-the-`&&`-chain restructuring, `${PLAN_DIR}`, the
forced-`review` status and the outside-the-bundle positive control are all sound and verified.
**Only the type token is wrong.** No frontloading misses, no reachability cycles.

## Upstream Assessment

Unchanged and sound after nine rounds.

## Bottom line, quoted

> With `--type escalations` substituted, I have **nothing blocking left** — every other finding in
> this pass is a `low`/`medium` traceability pin that would not stop a competent executor or prevent
> close.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| K1 `--type escalation` singular | high | Accepted; **verified against the script before fixing.** `--type escalation` returns `INCONCLUSIVE: no schema for type 'escalation'`, and `doc_lint.py:164` enforces `type == stem`; all 17 existing stems equal their document base name. Both `Test:` occurrences and the Instructions now read `--type escalations`, and **Issue 2.2 pins the stem** with the reason — the same prophylaxis Issue 0.1 received for `gate-consistency`. Note the failure mode is *worse* than red: an unknown type is **INCONCLUSIVE**, so the gate would have been unresolvable rather than merely failing. | `main-session` | `resolved` |
| P1 `RC` row grammar unpinned | NONE | Adopted — Issue 0.1 now specifies `RC <label> <exit-code>` at line start. | `main-session` | `resolved` |
| P2 `judgement: fired` unpinned | NONE | Adopted — Issue 5.1 pins both literals and states they are independent. | `main-session` | `resolved` |
| P3 `taxonomy` unpinned | NONE | Adopted — Issue 2.7 records it in the body. | `main-session` | `resolved` |
| P4 `escalation` key unpinned | NONE | Adopted — Issue 3.1 names the top-level key. | `main-session` | `resolved` |
| P5 `escalation-raise` unnamed in 3.2 | NONE | Adopted. | `main-session` | `resolved` |
| P6 `--answer` unnamed | NONE | Adopted — Issue 2.5 now pins `escalation-resolve`'s flag too. | `main-session` | `resolved` |
| P7 `herdr` carve-out | NONE | Adopted — `context.md` states the exception and Issue 4.2b must **skip, not fail**, when `herdr` is absent. An overclaim is worth correcting even at `low`. | `main-session` | `resolved` |
