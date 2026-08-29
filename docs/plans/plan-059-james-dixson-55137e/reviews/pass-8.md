---
type: Review
okf_spec: OKF-PLAN
---
# Red-team pass 8 — plan-059-james-dixson-55137e

## Verdict: REVISE

Run under the operator's scoped convergence standard. **Pass 7's two fixes both verify by execution,
and its defect class is NEARLY swept out** — two instances survive, one of them in a criterion pass
7's own fix rewrote. **Both are one-line repairs, and everything else in this pass is refinement.**

## Verified by execution

- **All 25 criteria and both auto gates run as single `bash -c` strings.** `recheck-criteria` -> 25
  total, 20 clause-form, **19 FALSE / 1 TRUE (SC2c)** — matching the sweep's cross-validation
  exactly. **Every red is a correct red** (verb absent, marker absent, issue not yet edited); no
  composite is structurally red except the two below.
- **Pass 7's N1 fix works** — SC0a is now genuinely *evaluated* (`actual_exit: 1`, `status: FALSE`)
  rather than `skipped-self-reference`. The `recheck[-]criteria` bracket defeats the guard.
- **SC1b is satisfiable** — `plan-027/reviews/pass-1.md` has `errors: 0` today **and** carries **four
  `med` cells**, so both halves of the conjunction hold once `cell-vocabulary` exists.
- **SC2c green for the right reason.** `gate_consistency.py` PASS, rc 0. **`ready-check`'s only
  reason remains the outstanding REVISE.**
- **No dangling references after eight rounds** — all 25 `Discharged-by` ids and all `depends-on` ids
  resolve; **all 36 issues are discharged by at least one criterion**; zero `SC2` references.

## Blocking concerns

| # | Concern | Class | Severity |
| :-- | :-- | :-- | :-- |
| J1 | **SC5 cannot go green — BOTH halves fail.** `.pushes < .raised`: Issue 2.5 raises **exactly one** escalation, so with `raised = 1`, `pushes >= 1 and pushes < 1` is **unsatisfiable**. `.pushes >= 1`: `context.md` states the design *"degrades to a written artifact with **no push** when `YF_PARENT_PANE` is unset"* — so SC5 is red in the plan's own **declared degraded topology** regardless of count. Pass 7's N2 named this brittleness and the rewrite **retained** it while adding a second impossibility. | 3 + 4 | high |
| J2 | **SC0a asserts an `RC` row label that no issue produces, and that mismatches the producing issue's own spelling.** The string `gate-consistency` occurs **exactly once in the whole plan — inside SC0a itself.** Issue 0.1 names the instrument `gate_consistency.py`, so a faithful executor writes `RC gate_consistency 0` and SC0a is red forever. **Every other asserted literal is deliberately pinned in its producing issue; this is the one that escaped — and it is the criterion certifying the sweep.** The sweep's own Recommendation 3 predicted this class and was never implemented. | 5 + 3/4 | high |

## Non-blocking (class NONE)

| # | Concern | Severity |
| :-- | :-- | :-- |
| M1 | **SC0 is self-referential and only converges on a fixpoint.** Issue 0.1 sweeps every non-`manual:` criterion including SC0, which reads the file the sweep writes: evaluated in one pass, SC0 reads the *old* block, and `RC SC0 1` lands in the *new* one. Passable, but nothing says so. | medium |
| M2 | **SC6d mutates the live bundle it verifies** — falsifying Issue 0.1's own new no-mutation rule from within the same document. `judgement-echo-check` appends to `log.md` by construction, and the close chain evaluates the table >= 3 times. | medium |
| M3 | **SC6c requires `ESC-001` to remain `raised`, which Issue 2.5's own lifecycle pushes against** — if the operator answers it, the natural outcome for a real question, SC6c goes to 0 and SC0 turns that into a close blocker. | medium |
| M4 | **SC9b's literals are a formatting trap** — `test("4/5")` is a regex, and #273's table renders the same fact spaced (`5 / 6`). Satisfiable via Issue 6.4's unspaced parenthetical, but the natural copy-across is red. | low |
| M5 | SC1's fixture **filename** is not named by Issue 1.6 (only the directory). | low |
| M6 | SC2b is discharged by 2.1–2.4, none of which creates `escalations.md` — 2.5 does. Traceability only. | low |
| M7 | `verification-sweep.md` still carries a stale `RC SC2` row for the criterion deleted at pass 5. | low |

## Gate Assessment

Five gates, `gate_consistency.py` PASS. Gate 1 red today for the stated reason and greps a literal
Issue 1.1 writes verbatim. **Gate 2's composite rc 1 today, correctly** — the redirect restructuring
holds, `${PLAN_DIR}` is used, and the forced-`review` status and outside-the-bundle positive control
are both sound. The upstream gate correctly declares no `Test:`. **No frontloading misses, no
reachability cycles.**

## Upstream Assessment

Unchanged and sound. **#273 verified live** — its body still carries the withdrawn *"A factor of
five"* and the `5 / 6` / `2 / 12` per-event framing, **exactly as Issue 6.4 describes, so that
issue's work is real and its disposition honest.**

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| J1 SC5 unsatisfiable both halves | high | Accepted. Now `.raised >= 2 and .pushes <= 1` — satisfied by the degraded no-herdr topology (`pushes = 0`) **and** by a real batched push, and it is what batching actually asserts. **Issue 2.5 now raises TWO escalations**: `ESC-001` left deliberately `raised` as SC6c's fixture, `ESC-002` resolved. That single change discharges J1 and M3 together. | `main-session` | `resolved` |
| J2 `gate-consistency` label produced by nothing | high | Accepted. Issue 0.1 now pins **both** instrument-row literals — `recheck-criteria` and `gate-consistency` — with the reason stated (the script is spelled with an underscore, so the natural transcription would leave SC0a red forever). | `main-session` | `resolved` |
| M1 SC0 fixpoint | NONE | Adopted. Issue 0.3 records `SC0` and `SC0a` **last**, against the rewritten block. | `main-session` | `resolved` |
| M2 SC6d mutates the live bundle | NONE | Adopted — SC6d moves to an **unpruned** scratch copy, which fires identically while touching nothing live. **A rule the plan states and then breaks is worse than one it never states.** | `main-session` | `resolved` |
| M3 SC6c's fixture is unstable | NONE | Adopted via J1's two-escalation fix: `ESC-001` is declared SC6c's fixture and **must not be answered** even if the operator answers the underlying question. | `main-session` | `resolved` |
| M4 SC9b spacing trap | NONE | Adopted — `test("4 ?/ ?5")`. | `main-session` | `resolved` |
| M5 fixture filename | NONE | Adopted — Issue 1.6 names the full path SC1 greps. | `main-session` | `resolved` |
| M6 SC2b traceability | NONE | Adopted — 2.5 added to the discharge list. | `main-session` | `resolved` |
| M7 stale sweep row | NONE | Adopted — deleted rather than left to self-clear. | `main-session` | `resolved` |
