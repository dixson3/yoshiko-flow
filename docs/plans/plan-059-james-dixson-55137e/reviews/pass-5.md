---
type: Review
okf_spec: OKF-PLAN
---
# Red-team pass 5 — plan-059-james-dixson-55137e

## Verdict: REVISE

> **This hits the stop-class-4 bound and escalates.** The reviewer states: *"I am not comfortable
> with that outcome and I checked hard for a way to APPROVE — but two of the blockers below are
> measured, not argued, and one of them means the plan cannot reach `complete` through `yf-plan`'s
> own §6.4 chain."*

**Pass 4's frame was accepted and not re-litigated.** The architecture, the detector refusal, the
`escalations.md`-vs-retrospective decision and the scoping are sound and undisturbed. **PARTIAL GO is
still the right verdict on the design.** Every blocker is in the verification layer — **but pass 4's
closing claim that these are all one-line fixes is not true of this pass.**

## Strengths

- **Four of pass 4's six blockers are genuinely fixed, verified by execution.** F1: SC2c against
  `plan-050` (26 real findings, none about escalations) -> `rc=0`, and the audit payload **parses
  cleanly** — *pass 4's "invalid JSON" note was itself a mis-parse.* F3: SC0 measured `rc=1` and its
  `[45]` arm would genuinely catch F2's class. F5: re-derived — post-plan-045 with >5 passes is
  **exactly five**; by the bare criterion it is seven. F6: the withdrawn rates survive only inside
  the correction record.
- **The DAG is clean.** `0.1` is the single root; every epic reaches it; no cycle, no back-edge, and
  nothing in Epic 0 needs anything from Epic 1.
- **The verification sweep is a real instrument and it earned its place** — *"it is why four of six
  blockers were fixable at all. My blockers are found by extending it, not by contradicting it."*

## Blocking concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| B1 | **14 of 19 clause-form criteria are structurally unrunnable, and `recheck-criteria` HALTS COMPLETION on them.** `<placeholder>` tokens are bash **redirections**: the shell aborts on `no such file`, `jq` gets empty stdin and exits 4. **Measured: `recheck-criteria` -> verdict FAIL, rc=1**, which at §6.4 prints `FAIL-LOUD … do NOT set 'complete'` and exits 1. **So this plan cannot close.** Worse, SC0 forbids any recorded `4`/`5`, making it unsatisfiable by the repo's own re-check; and the sweep's `RC` block was produced by hand-substituting real bundles that are **recorded nowhere**, so "re-run at intake and diff" cannot be performed by a second party. Not house style — `plan-050`, `052`, `054` carry **zero** placeholder criteria. | high |
| B2 | **Gate 2 can never go green: the invalid `ESC-001` is never removed before `escalation-raise`.** Step 1 writes and lints the invalid document; step 2 raises a valid one into **the same file**; ids are append-only, so the invalid entry survives into step 3 and `.errors == 0` is false. The only other branch is worse — if `escalation-raise` validates on write (Issue 2.2 requires it), step 2 dies on the pre-existing entry. **On any correct implementation the gate is permanently red**, and it `Blocks: epic:3`. Pass 3's E1 class, in the gate pass 4 called the best-constructed in the bundle. | high |
| B3 | **SC0 is unreachable as scheduled.** F8's fix made `0.1` the single root, so its artifact necessarily records 17 RED rows — that is its purpose. SC0 asserts 17+ **zero** rows and is discharged by 0.1 alone. **F3 turned "green before the work" into "red forever", and F8 made the schedule that guarantees it.** | high |
| B4 | **F4 residue: `Ratified severity vocabulary:` is named by no issue.** Four of five literals are now verbatim in their producing issue; the fifth appears **only in the gate itself**. Gate 1 stays red after 1.1 and 1.2 close, and blocks 1.3/1.4/1.5. **Pass 4 recorded F4 `resolved` on the claim that *every* literal is named, and that claim is false.** | high |

## Non-blocking concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| N1 | **Two of pass 4's ten resolutions are recorded `resolved` with no corresponding edit.** F9: `plan.md:331` still reads "the 32 issues" (the count is 35). F10: **no banner exists** on `exp-001`, which still carries `15/15`, `5/6 (83%)`, `2/12 (17%)` and "A factor of five" at nine places with no correction pointer. *"In a plan whose thesis is that obligations decay, a `resolved` row with no artifact behind it is the finding, not the typo."* | medium |
| N2 | **`gate_consistency.py` FAILS this plan and the sweep never ran it** — exit 1, 5 arm-1 findings, all apparently heuristic false positives (the gates *enumerate* what they block, in Instructions). Not wired into `ready-check`, so it will not block intake. **Epic 0's title is "prove the instruments", and two landed instruments were never in the sweep.** | medium |
| N3 | **The Start Gate's ratified option has no durable home, in a plan about recording answers.** `resolve-start-gate` takes no note argument and `/yf-plan execute` is a new session, so the operator's choice survives only in the drafting conversation. | medium |
| N4 | **`detected_by`'s closed domain and `escalation-raise`'s flag names are unnamed literals** — same class as F4, in the gate most sensitive to it. | medium |
| N5 | **Issues 6.1 and 6.2 name no target artifact** — an executor must invent where the specification lands, and SC9 is `manual:`. | medium |
| N6 | **SC2 needs an invalid `escalations.md` fixture that no issue creates.** Gate 2 tests the same property properly, so SC2 may be redundant. | medium |
| N7 | **Upstream mapping residues** — `#273`'s Resolved-By names 6.4 but 6.4 carries no `resolves-upstream` tag; `#270`'s Resolved-By names 6.4, which has nothing to do with #270. `references/upstream-270.md` repeats the withdrawn `5/6` with no pointer. | low |
| N8 | `index.md` still describes the sweep as "16 of 17"; the artifact says 17 of 18. | low |
| N9 | `okf.py check` warns `index.md` omits `reviews/`. | low |
| N10 | **SC0's threshold is looser than its prose** (`17 -le` passes with one non-zero row), and the `RC` block covers 18 of 21 executable checks — `SC0b`, `SC2d`, `SC9c` are absent — so "every criterion" overstates what it records. | low |

## Gate Assessment

| Gate | Reachable | Note |
| :-- | :-- | :-- |
| Start Gate | yes | Combined approve-plus-ratify is workable in one turn; the answer has nowhere durable to go (N3). |
| Severity vocabulary recorded | **no** | B4 — no issue emits the marker it greps. Correctly frontloaded, no longer a cycle. |
| Escalation schema round-trips | **no** | B2 — cannot go green on any correct implementation. **Structurally the best-designed gate in the bundle; the defect is one unremoved file.** |
| Upstream writes authorized | yes | `Blocks` complete; no `Test:` is the honest call. |
| Reconcile Gate | yes | — |

## The lesson, quoted

> **Pass 4's closing claim — "every one of the six blockers is a one-line fix" — was true of pass 4's
> blockers and is not true of this pass's.** B1 is a property of ~14 criteria at once and touches how
> the plan is closed; B3 needs a new issue and a new edge. Both were invisible to five prose reads and
> took **thirty seconds** to find by running two verbs the plan already depends on. That is the same
> lesson Epic 0 exists to teach, arriving one level up: **the sweep proved the criteria the author
> chose to run, and the two instruments it omitted are the two that halt the plan.** Widening Issue
> 0.1 from "every gate `Test:` and every criterion" to **"every landed instrument that reads this
> bundle"** is the change that would end the recurrence, and it is worth spending the escalation to
> make.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| B1 placeholders halt completion | high | **Accepted on the DEFECT; its stated CONSEQUENCE is corrected.** The placeholder defect is real: a `<token>` is a bash redirection, so the clause **errors (exit 4) rather than evaluating**. All 15 are replaced with concrete paths, and the three genuinely-unknown issue numbers route through `assets/filed-issues.env`. **But "the plan as written cannot reach `complete`" does not follow.** Measured after the fix: `recheck-criteria` still returns FAIL/rc=1 — because 17 progress criteria are *correctly* FALSE before the work is done, and it is a **§6.4 completion-time** step being run at drafting. Two controls settle it: `plan-052`, a **complete** plan, returns the same rc=1 FAIL; and this bundle's own results now **cross-validate exactly** with the independent sweep — `SC2c` holds, 17 FALSE, 5 `manual:` not-evaluated. The fix converted 15 clauses from *unrunnable* to *honestly false*, which is the real gain. | `main-session` | `resolved` |
| B2 gate 2 can never go green | high | Accepted. The invalid document is written and linted **outside the bundle**, so the valid raise starts from a clean `escalations.md`. | `main-session` | `resolved` |
| B3 SC0 unreachable as scheduled | high | Accepted. New Issue 0.3 re-runs the sweep at reconcile time, depending on the terminal issue of each epic; SC0 is discharged by 0.3 and asserts the **diff** (every row non-zero at intake is now zero) rather than an absolute count. | `main-session` | `resolved` |
| B4 marker named by no issue | high | Accepted. Issue 1.1 now names the literal verbatim. | `main-session` | `resolved` |
| N1 resolutions with no edit | medium | **Accepted, and it is the most important row in this table.** Both edits made. The pass-4 rows are annotated to record that they were marked resolved before the artifact changed — a `resolved` row with no artifact behind it is exactly the defect this plan exists to name, committed by this plan's own review bookkeeping. | `main-session` | `resolved` |
| N2 instruments omitted from the sweep | medium | Accepted, and adopted as the structural fix. Issue 0.1 is widened from "every gate `Test:` and every criterion" to **"every landed instrument that reads this bundle"**, enumerating `gate_consistency.py`, `recheck-criteria`, `okf.py check`, `pour_fidelity.py` and `audit-close`. | `main-session` | `resolved` |
| N3 ratified option has no home | medium | Accepted. Issue 1.2 reads the choice from `log.md`, and takes recommended **(b)** with the default recorded when absent — the same `on_no_answer` discipline Issue 2.5 specifies. | `main-session` | `resolved` |
| N4 unnamed vocabulary and flags | medium | Accepted. Issue 2.5 enumerates the `detected_by` members and the `escalation-raise` flag names. | `main-session` | `resolved` |
| N5 6.1/6.2 name no artifact | medium | Accepted. Both now name their target file. | `main-session` | `resolved` |
| N6 SC2 fixture uncreated | medium | Accepted. SC2 is **removed as redundant** — gate 2 tests the property properly, and a criterion needing an uncreated fixture is the defect B1 describes. | `main-session` | `resolved` |
| N7 upstream residues | low | Accepted. | `main-session` | `resolved` |
| N8 stale sweep count in index | low | Accepted. | `main-session` | `resolved` |
| N9 `reviews/` unindexed | low | Accepted. | `main-session` | `resolved` |
| N10 SC0 threshold and coverage | low | Accepted; folded into B3's diff-based rewrite. | `main-session` | `resolved` |
