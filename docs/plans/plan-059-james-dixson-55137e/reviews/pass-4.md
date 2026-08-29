---
type: Review
okf_spec: OKF-PLAN
---
# Red-team pass 4 — plan-059-james-dixson-55137e

## Verdict: REVISE

**Answer to the commissioning question — "has the pattern of each round's fixes introducing new
defects stopped?" — is NO: it happened a fourth time, and this round the new defects are inside the
artifact pass 3 commissioned to prevent them.** All exit codes measured in the worktree from the
repo root, and in `main` for the population re-derivation. No residue.

## What pass 3 fixed correctly — verified, do not re-open

- **E2's `${SKILL_DIR}` repoint is correct and COMPLETE.** No `${SKILL_DIR}` survives in any gate
  `Test:` or criterion — only in the prose that explains the rule. Every rewritten path targets a
  script this plan modifies or creates, and **no invocation of an unmodified skill-as-tool was
  clobbered.** Verified the rewritten form runs from the repo root and that `TYPES_DIR` resolves to
  where Epic 2's `escalations.toml` lands.
- **E1's gate-1 rewrite is no longer a cycle.** It reads residue from Issues 1.1/1.2, neither of
  which it blocks.
- **E3's `promote = false` is sound.** `REQ-DATA-053` exists (`spec/data.md:369`), bypasses
  `STATUS_SEVERITY` **in both directions**, is implemented at check level
  (`doc_lint.py:964`), and `plan.toml:134,147` genuinely uses it.

## Blocking concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| F1 | **Two criteria assert finding-object keys the tool does not emit — both permanently unsatisfiable.** `plan_manager.py` findings are `{item, status, detail}`; SC2c pipes them through `.message` (**`jq` error, rc=5 on every bundle with findings**) and SC6c through `.check` (yields `length == 0` forever). Neither Issue 2.6 nor 5.4 commits to changing the shape. Pass 3's E2 defect in a new form. Also: `audit --json-output` emits **invalid JSON** on many bundles, so any criterion piping it to `jq` is fragile independent of the key name. | high |
| F2 | **`findings/verification-sweep.md` records a false exit code in its most load-bearing row.** It reports `SC2c -> rc=0, GREEN`; measured `rc=5`. That cell carries the sweep's entire headline — the polarity table, "16 of 17", and the section built on it. **The distinction may be good but currently has no measured instance.** | high |
| F3 | **SC0 is GREEN today — the green-before-the-work defect, fourth occurrence, inside the epic created to end it.** The sweep file already exists, so Epic 0's only mechanical criterion is discharged before Issue 0.1 runs. And `grep -qc 'rc='` asserts codes are *present*, not *correct* — **structurally incapable of detecting F2, the exact defect in the artifact it verifies.** | high |
| F4 | **Five assertions match a literal name no issue commits to producing, three of them introduced by pass 3's own fixes** — `REQ-DATA-SEVERITY-VOCAB` (and every id in `spec/data.md` is numeric, so an executor writes `REQ-DATA-074` and the gate is permanently red), `recommended-in-alternatives`, `--list-steps`, `judgement: not-fired`, `escalation-open`. **This is pass 3's E9 marked resolved as "every asserted key is now named": the KEYS were fixed, the STRING LITERALS were not.** | high |
| F5 | **The re-derived population is wrong — fourth form of the same error.** The plan says "the FIVE plans whose pass count exceeds 5". Re-derived by exactly that criterion: **seven** — `plan-026` (7) and `plan-029` (6) are silently excluded. The real and legitimate filter is EXP-001's **post-plan-045** qualifier, which pass 3's rewrite dropped. Rows reproduce exactly; **the population SENTENCE is false**, violating the finding's own Limit. | high |
| F6 | **The finding contradicts its own table three times and `plan.md` carries two rates.** The finding still reads *"The comparison is 5/6 vs 2/4"* three lines below a table saying 4/5 and 2/5 — reinstating **both** withdrawn denominators in one sentence — plus two `83%` and two `15/15`. `plan.md` says `4/5` at one line and `83%` at two others. | high |

## Non-blocking

| # | Concern | Severity |
| :-- | :-- | :-- |
| F7 | `context.md`'s *"No epic needs network"* is now false — Issue 0.2 files a GitHub issue; and four criteria are network-dependent, not three. | medium |
| F8 | **Nothing depends on Epic 0.** No issue lists `depends-on: 0.1`, so "the sweep re-runs before intake" is an **obligation** — the exact form this plan's own law predicts decays. **Epic 0's justification argues it must be a command, then ships it as a bead nothing waits on.** | medium |
| F9 | `plan.md` "the 32 issues" — the count is 35. Pass 3's E18, stale again after Epic 0. | low |
| F10 | `findings/exp-001-trigger-point-survey.md` still carries 15/15, 5/6, 2/12 and "a factor of five" with **no correction pointer**, while the plan's protocol is that corrections are recorded rather than silently replaced. A cold reader hitting EXP-001 first gets the withdrawn numbers. | low |

## Gate assessment

Gate 1 is reachable and correctly frontloaded but red for the wrong reason (F4). **Gate 2 remains
the best-constructed gate in the bundle**; its only defect is the unnamed check id. The
upstream-writes gate's `Blocks` set is now complete, and declaring no `Test:` for a human
authorization gate is the honest call.

## Upstream assessment

**E5 is genuinely resolved on this axis** — `upstream-triage.md`, `context.md` and the `#273` row are
mutually consistent and no longer contradict Issue 6.4 or SC9b. `references/upstream-273.md`
correctly preserves the as-filed withdrawn framing.

## On the whole plan

> **The design is still coherent; it is not a patchwork.** The write-then-notify architecture, the
> command-vs-obligation trigger choice, the refusal to ship the detector, and the
> no-`skills/yf-judgement/` decision all still follow from EXP-001/002/004 and none was disturbed by
> four rounds of surgery. **Every one of the six blockers is a one-line fix to a verification
> string** — none touches an epic, a dependency edge, or a scoping decision. **PARTIAL GO remains the
> right verdict.**

> **But the recurrence is now structural and should be named as such.** Each round adds or rewrites
> criteria by hand, and **nothing checks a criterion against the actual output shape of the tool it
> names.** F1 and F4 are the same root cause; F2 and F3 are that root cause reaching the instrument
> built to catch it.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| F1 wrong finding-object keys | high | Accepted. Both rewritten against `{item, status, detail}`; SC2c now runs against a bundle that **has** findings, and Issue 5.4 commits to emitting `item: escalation-open`. | `main-session` | `resolved` |
| F2 sweep records a false code | high | **Accepted with a correction, and the correction improved the result.** Run 1's `rc=0` was *accurate for the command as run* — against this bundle the audit emits an **empty** findings array, so `select` never evaluated `.message`. The sweep did not misreport; **its READING was wrong** — it took a vacuous green for a verified invariant. Repairing the query per F1 and re-measuring against `plan-050` (26 findings, none about escalations) yields `rc=0` **for the right reason**, so SC2c is now a genuinely verified invariant. Both runs are recorded in the artifact. | `main-session` | `resolved` |
| F3 SC0 green today | high | Accepted. SC0 now asserts **17+ zero rows AND no `4`/`5` usage codes** — which makes it structurally capable of detecting F2's class, and red today (measured `rc=1`). | `main-session` | `resolved` |
| F4 unnamed string literals | high | Accepted. Every literal is now named verbatim in the issue that produces it, and gate 1 greps a **marker** (`Ratified severity vocabulary:`) rather than a `REQ-*` id — because ids are numeric and sequential, so asserting one guesses a number the executor has not allocated. Added to the sweep's recommendations as a mechanical check. | `main-session` | `resolved` |
| F5 population sentence false | high | Accepted, re-derived independently. The `post-plan-045` qualifier is restored to both the plan and the finding, with the reason stated: by the bare criterion the set is **seven**, and `plan-026`/`plan-029` predate `review-loop-check` and could not have run it. | `main-session` | `resolved` |
| F6 two rates in the bundle | high | Accepted. Swept: `83%`, `15/15`, `5/6` and `2/4` now appear **only** inside the correction record that withdraws them. | `main-session` | `resolved` |
| F7 network claim false | medium | Accepted. Corrected, with the four network-dependent criteria enumerated. | `main-session` | `resolved` |
| F8 nothing depends on Epic 0 | medium | **Accepted — the best non-blocking catch in the pass.** Issues 1.1 and 4.1 now `depends-on: 0.1`, making **0.1 the single root**: proving the instruments genuinely gates all work, which is the epic's own title. The plan no longer argues for a command and ships an obligation. | `main-session` | `resolved` |
| F9 stale count | low | Accepted. | `main-session` | `resolved` |
| F10 EXP-001 has no correction pointer | low | Accepted. A superseded-numbers banner now heads that table, pointing at the artifact that records all four drafts. | `main-session` | `resolved` |
