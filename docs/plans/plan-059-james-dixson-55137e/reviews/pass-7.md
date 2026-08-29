---
type: Review
okf_spec: OKF-PLAN
---
# Red-team pass 7 — plan-059-james-dixson-55137e

## Verdict: REVISE

Run under the operator's scoped convergence standard. **Pass 6's three fixes all verify, and the
same-root-cause sweep comes back CLEAN.** But executing every gate `Test:` and every clause-form
criterion as a single `bash -c` string — the method Issue 0.1 now mandates and that **nobody had yet
run over the current text** — surfaced two criteria that cannot go green on a correct
implementation.

## Pass-6 resolutions — verified by execution

- **Gate 2 composite**: the literal `Test:` extracted from `plan.md` and run as one `bash -c` —
  composite `rc=1` today (correct; the verbs don't exist). **The redirect restructuring is sound**:
  `doc_lint`'s expected exit 1 is off the `&&` chain, so a correct implementation reaches
  `escalation-raise`.
- **`gate_consistency.py`** -> `PASS`, 5 gates, **rc=0**.
- **SC4** -> `rc=1` today because `jq` finds no `escalation` key — **red for the correct reason, not
  aborted by `pipefail`.**
- `okf.py check` -> `ok: true`; `doc_lint` -> 0E/0W; `audit` -> rc=0; **`ready-check` -> rc=3 with
  the ONLY reason being "last red-team verdict is REVISE" — nothing else blocks approval.**
- **No dangling references after seven rounds**: every `Discharged-by`, `depends-on` and gate
  `Blocks` id resolves; **zero prose references to the deleted `SC2`.**

## The pipefail / non-zero-success sweep — CLEAN

Every remaining `| jq` under `pipefail`, every `&&` chain, every `!` negation checked, measured where
measurable. `audit` and `audit-close` **exit 0 even with findings present** (measured on plan-050's
26); `cell-vocabulary` ships at `R` so `doc_lint` stays 0; the `filed-issues.env` forms yield a clean
`rc=1` on a missing file with no `set -u` in play. **No surviving instance of pass 6's defect class.
All the reds are correct reds.**

## Blocking concerns

| # | Concern | Class | Severity |
| :-- | :-- | :-- | :-- |
| H1 | **SC6 asserts `judgement: not-fired` against a bundle where the trigger PROVABLY FIRES.** `review-loop-check` counts `reviews/pass-*.md` — 6 now, 7 once this pass lands, **and it only grows**. So `judgement-echo-check`, which Issue 5.1 defines as invoking the trigger and diffing `log.md`, takes the **fired** path every time; `added_line` reads `judgement: fired`, never `not-fired`. **False forever on a correct implementation** — and R1 names SC6 as the criterion the plan's highest risk gates on. | 3 | high |
| H2 | **SC3's verification MUTATES the bundle and makes SC6c unsatisfiable.** `recheck-criteria` executes clauses **in table order**. SC3 runs `escalation-resolve` — a **write verb** — on the live bundle, so `ESC-001.state` becomes `resolved`; SC6c then requires a still-`raised` escalation and is deterministically FALSE. **No issue creates a second escalation**, and Issue 2.5's own cross-reference list names SC3/SC5/SC2b/SC10 — **SC6c is missing from it, which is where the requirement was lost.** It escalates to **class 4** through SC0's all-rows-zero rule: an SC6c row of 1 makes SC0 false, `recheck-criteria` returns FAIL, and §6.4 halts. Second head: the close chain evaluates this table **at least three times**, so runs 2+ resolve an already-resolved entry — a transition outside the declared lifecycle that nothing declares idempotent. | 3 + 4 | high |

## Non-blocking

| # | Concern | Class | Severity |
| :-- | :-- | :-- | :-- |
| N1 | **SC0a is silently never evaluated at close** — `recheck-criteria` reports `skipped-self-reference`, because its guard scans the command string and SC0a's grep contains the literal `recheck-criteria`. Not FALSE, so it does not block — but the criterion certifying the sweep is **inert in the close chain**. | NONE | medium |
| N2 | **SC5's `.pushes == 1` is a literal over a topology-dependent side effect** — legitimately 0 when `YF_PARENT_PANE` is unset (Issue 4.4's human-present arm), and SC0 turns any such brittleness into a close blocker. | NONE | medium |
| N3 | **SC6b needs `--list-steps --json` to be the SOLE stdout** — measured `rc=5`, `jq` parse error, because pytest's session banner reaches stdout. | NONE | low |
| N4 | **Two criteria mutate committed bundle artifacts as a side effect** — SC3 (`escalations.md`) and SC6 (`log.md`, one line per run). | NONE | medium |
| N5 | Issue 0.3's `depends-on` names one leaf per epic where Epics 3 and 6 have several. The Reconcile Gate covers it. | NONE | low |

## Missing

> Nothing in the design layer. The remaining gap is the one H1 and H2 share: **three criteria verify
> a stateful property of the LIVE bundle that another criterion in the same table changes, or that
> the bundle's own history contradicts. Gate 2 already solved exactly this with the `mktemp -d` +
> `cp -R` pattern; the criteria table has not adopted it.**

## Gate Assessment

All five gates consistent (`gate_consistency.py` PASS, rc=0). Gate 1 reachable and greps a marker
Issue 1.1 writes verbatim. **Gate 2's composite chain is now correctly structured** — expected-
non-zero step off the `&&` chain, `${PLAN_DIR}`, forced-`review` status and outside-the-bundle
positive control all hold. No frontloading misses.

## Upstream Assessment

Unchanged and sound. Dispositions match what ships; `#269` correctly `partial`; `#273`'s tag present;
no supersedes claimed that isn't earned.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| H1 SC6 tests a path this bundle cannot take | high | Accepted. SC6 now runs against a **pruned scratch copy** with `reviews/pass-*.md` removed. **Verified by execution: pruned copy -> `cycles 0, escalates False`; live bundle -> `cycles 6, escalates True`.** New **SC6d** asserts the **fired** path on the live bundle — the half the current text could actually prove, and which was being asserted by accident rather than on purpose. | `main-session` | `resolved` |
| H2 SC3 mutates state SC6c reads | high | Accepted, and it is the sharper of the two. SC3 now runs against a **scratch copy**, leaving the live `ESC-001` in `raised` for SC6c and removing the non-idempotent re-run. Issue 2.5's cross-reference list gains SC6c. | `main-session` | `resolved` |
| N1 SC0a inert at close | NONE | Adopted anyway — the pattern is now `recheck[-]criteria`, which matches the file and defeats the self-reference guard. | `main-session` | `resolved` |
| N2 `.pushes == 1` brittle | NONE | Adopted anyway — now `.pushes >= 1 and .pushes < .raised`, which is **what batching actually means** and is topology-independent. | `main-session` | `resolved` |
| N3 `--list-steps` stdout | NONE | Adopted — Issue 5.3 now requires it to short-circuit before pytest and emit JSON as the sole stdout. | `main-session` | `resolved` |
| N4 criteria with side effects | NONE | Adopted as a **general rule** in Issue 0.1: no criterion's command may mutate the bundle it verifies. Both instances are removed by H1's and H2's scratch-copy forms. | `main-session` | `resolved` |
| N5 Issue 0.3 leaf list | NONE | Left — the Reconcile Gate covers it, as the reviewer notes. | `main-session` | `resolved` |
