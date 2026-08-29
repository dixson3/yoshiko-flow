---
type: Review
okf_spec: OKF-PLAN
---
# Red-team pass 1 — plan-059-james-dixson-55137e

## Verdict: REVISE

Dispatched as an isolated sub-agent per REQ-AGENT-049. The agent read the full bundle, recovered
research 005 §7–9 from the `research/005-thrash-detection` branch, and ran the plan's own gate and
success-criteria commands in a sandbox copy. Sandbox removed; repository unmodified.

## Strengths

- **The PARTIAL GO is better supported than the plan claims, on one axis it undersells.** Research
  005 §8.2 grades *N-hop* channel shape "Untested" — but the same row says *"the corpus's own
  mechanism is one-hop: a reviewer drafts the fork and the operator resolves it at a review boundary
  that already exists."* That is precisely what Epics 2–3 build. **The plan is formalising the
  corpus's own measured mechanism, not extrapolating past it.** The charge that the plan smuggles a
  supported premise into an unsupported conclusion does not hold on the one-hop design; it would
  have held on an N-hop design, which R7 correctly declines.
- **EXP-001/002 genuinely refuted their commissioning premise** and the plan followed the refutation
  rather than absorbing it.
- **Write-then-notify is forced, not chosen.**
- The load-bearing counts were independently reproduced: 5 of 6 post-045 bundles crossing the bound
  carry echoes; `plan-050`=7, `052`=1, `054`=2, `055`=2; `stop_class: 4` in 050 and 052 only.

## Concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| C1 | Both capability gate `Test:` commands already exit as required, today, before any work exists. The `auto` gate `Blocks: epic:3` and is already green, so **Epic 3 is effectively ungated**. | high |
| C2 | **SC6's verification does not test SC6.** A verb that exits 0 when nothing happened is indistinguishable from a verb nobody ran — the plan's own complaint, reproduced in its own remedy. Epic 5 terminates (no recursion) but **only at Issue 5.1**; 5.2 and 5.3 are refuted by the plan's own cited precedent, since `retrospective_fields.py` has a `CHANGE-VALIDATION.md` row, a tagged test, README and schema references — **and zero callers.** | high |
| C3 | **"Epic 6 ships no artifact" is false.** Issue 6.1 is a real code change to `finding_recurrence.py`. And SC9's verification (`plan_extract --strict`) exits 0 today on the un-executed plan — it tests parseability, not either clause of its criterion. R6 is rated `high` and its whole mitigation is the false claim. | high |
| C4 | **The escalation path's own untested premise gets no instrumentation-closure, while the detector's does.** §8.4 says the cost-ratio assumption must be *instrumented*; the plan builds the recording surface and **no issue or criterion ever reads it.** That asymmetry is the slot-filling risk one level up. | medium |
| C5 | **The command-vs-obligation law compares two different units of analysis.** 83% is per-plan-at-least-once (5 of 6 plans); 17% is per-event (12 escalations → 2 entries). At one unit it is **2 of 4 plans = 50%**, so the factor of five becomes ~1.7 on n=4. None of the artifact's four stated limits is this one. | medium |
| C6 | **The escalation log's "3 of 4" is an overcount.** E-2's own row reads `disposition: n/a` and says the session *could not* have raised it. The honest figure is **2 of 3**, both the same event shape, self-recorded by the author of the design they support. | medium |
| C7 | **SC1, SC2 and SC2c pass vacuously.** The vocabulary check ships at `R`, and `doc_lint`'s exit is `1 if errors else 0` — so SC1 exits 0 whether the check is implemented, broken or absent. SC2 exits 0 on `files_checked: 0`. SC2c's criterion says "no finding of any severity" but audit exit 0 tolerates advisory findings. | medium |
| C8 | **No epic creates a `yf-judgement` skill, and this is never stated.** Every artifact lands inside `yf-plan` or `yf-herdr`. That is probably correct — the command-vs-obligation law argues against a new invocation surface — but an executor reading the objective will create one. Relatedly #269 is `include` when only one of its three halves ships. | medium |
| C9 | **`escalation-resolve` introduces an in-place mutable bundle artifact — a new capability class with no risk row.** Every existing bundle write verb is append-or-regenerate. It interacts with index regeneration and with concurrent sessions, which D-5 establishes are a live hazard here. Separately R5's *mitigation* addresses the **severity** vocabulary while R5's *risk* is the **escape/stop taxonomy** — different vocabularies — and the "recorded as a follow-on" drift-check edge is recorded by **no issue**. | medium |
| C10 | **The severity-vocabulary gate sits later than its evidence requires.** Every input already exists in EXP-002. As placed it spends an operator turn mid-run, and the whole plan serialises behind an Epic-1 chain containing a human gate. | medium |
| C11 | **Epic 4 is SPEC-only**, violating `AGENTS.md` SPEC-first's "then write code + a tagged test". Issue 4.2 records a *measured, testable* fact and ships it as prose. And **SC4b — the plan's genuinely novel contribution, resting on the thinnest evidence — has no mechanical verification at all.** Highest-risk cell, lowest verification. | medium |
| C12 | **The plan's empirical basis is not present on this branch.** `index.md` names the research bundle "in this repo"; in this worktree and on `main` it does not exist. Every §7/§8/§9 citation is unresolvable for a cold reader. | medium |
| C13 | `upstream-triage.md` records **no dispositions** — all three fields blank — while `index.md` advertises it as the record behind the table. Audit passes anyway. | low |
| C14 | **#270 is load-bearing** for Issue 3.4 and SC7 but has **no upstream row**. Nor does any issue file the command-vs-obligation law upstream, though its own recommendation says to. No issue creates the coarse tracker. | low |
| C15 | **The plan's own risk table uses `med`** — one of the 45 unnormalised tokens this plan exists to pin. A live instance of EXP-002's stated residual. | low |

## Missing

A statement that no `yf-judgement` skill directory is created; any instrumentation closing §8.4's
cost-ratio assumption; a risk row for in-place bundle mutation; an issue discharging R5's
"recorded as a follow-on"; mechanical verification for Issue 4.2 and SC4b; a `deferred` row for
#270 and an issue filing the command-vs-obligation law; and `escalations.md`'s interaction with
`yf-okf` conformance.

## Gate Assessment

Gate count is appropriately small — two capability gates for a 6-epic plan is restraint, and the
reviewer would not add a third. **The defect is entirely in the `Test:` lines.** Both capability
gates are reachable and neither creates a cycle. The severity gate's `Instructions` are
"genuinely decision-grade"; the escalation gate's `Instructions` describe the right test and the
`Test:` line does not implement it.

## Upstream Assessment

**#269 `include` → should be `partial`**: the detector half is refused, the skill half is not
built, and only the escalation half ships. **#264 `partial`** is well-scoped with N-hop declined
for a measured reason, **but Epic 4 delivers SPEC prose with no implementation or test**, so
"resolved by 4.1" is weaker than it reads. **#145 `partial`** is the strongest of the three —
EXP-003 tested the claims against landed code and returned two refutations. **#270 absent.** No
issue creates or updates the coarse tracking issue required by `AGENTS.md`.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 gate tests cannot fail | high | Already fixed before this pass was read — conformance pass 1 raised the same defect independently. Human gate now declares NO `Test:` (a green command cannot establish ratification); auto gate runs a self-cleaning `mktemp` probe that raises, resolves and lints a real escalation, and **fails today**. | `main-session` | `resolved` |
| C2 SC6 vacuous; 5.2/5.3 refuted | high | Accepted in full. SC6's verification now asserts a `log.md` content delta on the not-fired path rather than an exit code; the Approach states 5.1 is load-bearing and 5.2/5.3 are defence in depth. | `main-session` | `resolved` |
| C3 Epic 6 ships an artifact; SC9 vacuous | high | Accepted. Claim reworded to "no detector and no deliverable any criterion depends on; it repairs one instrument". SC9 split into a grep-based mechanical check and an honest `manual:` half. R6's mitigation rewritten. | `main-session` | `resolved` |
| C4 no cost-ratio instrumentation | medium | Accepted. New Issue 3.5 records raised/answered/`on_no_answer`-taken per escalation, discharged by new SC10. | `main-session` | `resolved` |
| C5 unit mismatch in the law | medium | **Accepted — this is the most consequential correction in the pass.** Restated at one unit (per-plan, 5/6 vs 2/4); "factor of five" and "the finding the whole design keys on" removed; the unit mismatch added as a fifth stated limit. Design conclusions re-derived and shown to survive. | `main-session` | `resolved` |
| C6 escalation log overcount | medium | Accepted. Corrected to 2 of 3 throughout, and the second-party trigger now cites EXP-001's independent 81-entry `detected_by` census rather than resting on a self-recorded n. | `main-session` | `resolved` |
| C7 SC1/SC2/SC2c vacuous | medium | Accepted. All three now assert JSON fields (`report_only >= 1`, `files_checked >= 1 and errors == 0`, `findings == []`) rather than exit codes. | `main-session` | `resolved` |
| C8 no skill dir; #269 disposition | medium | Accepted. Approach states no `skills/yf-judgement/` is created and why; #269 changed to `partial` with an explicit in/out boundary. | `main-session` | `resolved` |
| C9 mutable artifact; R5 mismatch | medium | Accepted. New R9 covers in-place mutation with write-temp-then-rename plus an idempotence test; R5's mitigation rewritten to address the escape/stop taxonomy; new Issue 2.7 files the drift-check-edge follow-on. | `main-session` | `resolved` |
| C10 gate frontloading miss | medium | Accepted. Ratification hoisted into the Start Gate's approval turn with the three candidate vocabularies and their rejection counts; Issue 1.2 reduced to recording the decision. | `main-session` | `resolved` |
| C11 Epic 4 SPEC-only; SC4b unverified | medium | Accepted. Issue 4.2 gains a test asserting the exit-0 behaviour; SC4b adopts the `test_close_contract.py` parse-and-assert pattern, converting `manual:` into a removal-detecting exit code. | `main-session` | `resolved` |
| C12 research basis absent on branch | medium | Accepted. `index.md` now states the branch and PR; the passages the Approach reasons from are vendored to `references/research-005-extract.md`. | `main-session` | `resolved` |
| C13 empty upstream-triage | low | Accepted. Dispositions and reasoning filled in, mirroring D-2. | `main-session` | `resolved` |
| C14 #270 row; law not filed | low | Accepted. `deferred` row added for #270; new Issue 6.4 files the command-vs-obligation law; coarse-tracker creation noted as the §4.5 intake step it already is. | `main-session` | `resolved` |
| C15 risk table uses `med` | low | Accepted, with appreciation. Normalised to the full tokens. | `main-session` | `resolved` |
