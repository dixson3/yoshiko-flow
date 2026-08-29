---
type: Review
okf_spec: OKF-PLAN
---
# Red-team pass 3 — plan-059-james-dixson-55137e

## Verdict: REVISE

Everything executed, not read: both gate `Test:` lines run verbatim, `doc_lint`'s status-demotion
table read from source and measured at four statuses, `okf.py check` run against a scratch bundle
carrying the `sed` residue, both `test_close_contract.py` invocations run, `gh issue view 269/273`
read, and the command-vs-obligation counts re-derived in the main checkout. Sandbox removed.

**The direct answer to the commissioning question: the pass-2 fixes are real in two places and
relocated in three.** D2's `sed` fix is mechanically correct. D3's drop of Issue 6.1 is correct. But
**D1's fix converted a green gate into an unsatisfiable one**, D5's fix left the bundle carrying four
values for one number, and **D8's "verb nobody creates" defect has multiplied, not resolved.**

## Strengths

- **D2 was pass 2's sharpest finding and its repair holds up under measurement.** Confirmed:
  `review` -> FAIL/9 errors, `approved`/`executing`/`complete` -> PASS/0 errors/9 report-only, and
  `bundle_status()` walks to the nearest `plan.md`, so forcing the plan's status does reach a sibling
  document.
- **The `--type escalation` + `files_checked >= 1` double guard works.** An unknown type returns
  `INCONCLUSIVE, files_checked: 0` at exit 2, and both `jq -e` arms correctly return 1 on that shape.
- **Gate 2 fails today for the right reason** and removes its scratch dir on both paths.
- **The command-vs-obligation FINDING is now genuinely good** — states its population first, records
  both prior corrections rather than applying them silently, and its rejection of the 2/5 variant is
  better reasoning than pass 2 demanded. Rows 1 and 3 reproduce exactly in the main checkout.
- **D3's resolution strengthened the plan.** Refusing to override E-4's resolved default, in the plan
  whose purpose is to make escalations binding, is the right call.

## Concerns

| # | Concern | Severity | Blocks approval |
| :-- | :-- | :-- | :-- |
| E1 | **The first capability gate is now a CYCLE and can never resolve.** Its `Test:` asserts a `cell-vocabulary` finding; its `Blocks:` is `1.3, 1.5`; **Issue 1.3 IS the issue that implements `cell-vocabulary`.** Its own Instructions say so while blocking it. Two passes each made this gate "fail today" without checking it can ever go green — the plan traded a green gate for a deadlocked one. It also lacks gate 2's `files_checked >= 1` guard, so today's rc=1 is the #181 silent green on a nonexistent fixture. | high | **yes** |
| E2 | **Every gate `Test:` and 14 of 22 criteria invoke `${SKILL_DIR}` — the INSTALLED skill — which by this repo's own rules never receives the code these epics write.** `AGENTS.md` states the repo's `skills/` "is unreachable by the resolver" and forbids `yf skills install` mid-execution; `TESTING.md` requires exercising the modified repo copy. Here it inverts into a permanent **false RED**: after Epics 1–5 land, 13 gates/criteria still fail, and the only way to green them is the deploy the repo prohibits. **Neither prior pass raised this.** | high | **yes** |
| E3 | **Issue 2.2's `E` severity is demoted to `R` at the only status `escalations.md` ever lives at.** Escalations are authored during EXECUTE, where `ERROR -> REPORT`. So the schema's `E` checks — including the `recommended`-names-an-alternative rule the plan calls load-bearing — **cannot fail in production.** 2.2's rationale is backwards. The gate's `sed` is an unacknowledged admission. The fix exists and no issue names it: **`promote = false` (REQ-DATA-053)**, already used by `plan.toml`. | high | **yes** |
| E4 | **Epic 6's refusal is contradicted three times by the plan's own prose about the deleted Issue 6.1** — Approach ¶173 (*"it repairs a measuring instrument"*), ¶212 (*"Epic 6 creates the second"*), and **R6's mitigation**, which still cites 6.1 *and* the `43` literal the same Approach explicitly forbids. **SC9 — the criterion that exists to make the emptiness checkable — is `manual:` and would be discharged by reading exactly these contradicted paragraphs.** | high | **yes** |
| E5 | **The bundle carries FOUR values for the obligation rate, and instructs the executor to publish the one its own finding rejects.** Law table 2/4; #273 row 2/4; Issue 6.4 **2/5**; SC9b asserts #273's body contains **`2/5`**; `context.md` glossary still **17%**. Third pass, same number. | high | **yes** |
| E6 | **`plan.md`'s single-population claim is false and row 2 is not reproducible in main.** Row 2's denominator is 6 while rows 1 and 3 use 4. Measured in main: plans exceeding the bound are 048, 050, 052, 054, 055 = **5**, giving **4/5** — plan-056's bundle in main has no `log.md` at all. The exact population mismatch D5 raised, marked resolved, in a third form. | high | **yes** |
| E7 | **Two criteria are GREEN TODAY and one can never fail.** Measured: `test_close_contract.py` -> **rc=0** (SC6b), and `--assert-invocation escalation-raise` -> **rc=0** because **the unknown flag is swallowed** (SC4b). SC4b reports green whether or not Issue 5.3 implements it. C1/D1's defect class, in criteria introduced by pass 1's own fix. | high | **yes** |
| E8 | **Gate 2's positive control does not depend on the schema rule it exists to test, and may be unsatisfiable.** `.errors >= 1` is satisfied by *any* error finding — it tests "the linter emits errors", not the `recommended` rule. D9 taught SC1/SC1b to assert **by check name**; gate 2 was not given the same treatment. Worse, a layering contradiction: Issue 2.2 asks `escalation-raise` to validate on write, while the gate requires that verb to cheerfully write the invalid document. **If the verb validates, the gate dies at step 1.** | high | **yes** |
| E9 | **Criteria assert five JSON keys no issue commits to producing** — `.prior_entries_unchanged`, `.pushes` (and SC5 is discharged-by 3.3, which creates no verb), `.lines_added`/`.added_line`, and **`test_herdr_channel.py`, a file that exists nowhere**. D8 multiplied. SC3 and SC6 also remain **self-reports**: the verb under test reports on its own correctness. | high | **yes** |
| E10 | **The upstream-writes gate covers three of at least five writes, and one is already done** — the #269 correction comment was **posted at 2026-08-28T23:24Z**; the coarse tracker is likewise unblocked. | medium | no |
| E11 | **No issue creates gate 1's fixture** (`skills/yf-plan/fixtures/severity-vocabulary/`). Gate 1 has two independent reasons to stay red and no guard distinguishing them. | medium | no |
| E12 | **`sed -i.bak` leaves `plan.md.bak` in the scratch bundle and the tooling sees it** — `okf.py check` returns `REQ-OKF-CHK-002 warning: index missing: plan.md.bak`. The gate asserts on a bundle it has deliberately corrupted. (Same run surfaced `index missing: reviews/` on the real bundle.) | medium | no |
| E13 | **Gate 2 assumes the copied bundle has no `escalations.md`, likely false by the time it fires.** It blocks `epic:3`, so it runs after Epic 2 ships the verb — when this plan is its natural first user. If one exists, `ESC-001` is taken and `escalation-resolve` resolves the **wrong** entry. Silently order-dependent on an unstated precondition. | medium | no |
| E14 | **SC2d and SC9c are near-unfalsifiable** — `.state != null` passes for any existing issue number regardless of content, and both need network, which `context.md` says no epic needs. | medium | no |
| E15 | **E-4's own record would trip the plan's new check.** The log entry reads `disposition: raised` with `outcome: RESOLVED`. Whether "default confirmed with no answer" is `raised` or `resolved` is exactly SC3's lifecycle, and it is unspecified. | medium | no |
| E16 | **SC1b is tautological** — 1.4 ships at `R`, so asserting no `E`-severity finding is true by construction. **SC10 is similarly weak** — `has(...)` is satisfied by three nulls. | medium | no |
| E17 | **"factor of five" survives in the Approach**, in the very section that reasons from it — while SC9b asserts #273 must not contain it. | medium | no |
| E18 | **Stale counts** — "16 of 33" (is 15), "the 32 issues" (is 33), "15 of the 22" (is 14). | low | no |

## Missing

An issue creating gate 1's fixture; **a statement of which tree the gates and criteria execute
against**; `promote = false` on `escalations.toml`; an issue naming `test_herdr_channel.py` and the
four asserted keys; a gate edge covering the #269 comment and the coarse tracker; a precondition that
gate 2's copied bundle carries no `escalations.md`; and a reconciliation of Epic 6's refusal with R6
and Approach ¶173/¶212.

## Gate Assessment

Four gates for 33 issues is the right count, and **gate 2 is the best-constructed gate in the
bundle** — its remaining defects are refinements, not reconstruction. **Gate 1 is not repairable in
place: it is a cycle.** Better fix: move the `cell-vocabulary` assertion into SC1 and let the gate
assert only the SPEC residue 1.1/1.2 produce, which it does not block — that also restores the
frontloading the C10 fix intended. The upstream gate's `Blocks` set is incomplete. The Start Gate's
three-option Instructions remain the best prose in the bundle.

## Upstream Assessment

Dispositions sound, #273 recorded. Residual: the #269 correction comment is **already posted** and
the plan still schedules it; Issue 6.4 instructs publishing `2/5`, the figure the plan's own finding
rejects; and #270's `Resolved By` still lists 6.4, which files nothing about #270.

## On scope

**The Epics 1/4/6 coupling argument is sound as far as it goes but does less work than it appears.**
It justifies co-location of a *narrative*, not co-execution of a *dependency graph* — after D13
re-rooted Epic 4 there is literally no edge between it and anything else. **Not a blocker:** the
paragraph is candid and its split escape-hatch is the right resolution.

## The closing recommendation, quoted because it is the most valuable line in the pass

> **The single highest-leverage change is not another round of edits: it is to run every gate `Test:`
> and every non-`manual:` success criterion once as written, in the tree they will execute in, and
> record the exit code beside each.** Doing that would have caught E1, E2, E7 and E11 mechanically,
> and it is the only step in this bundle that has never been performed on the full set.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| E1 gate 1 is a cycle | high | Accepted. The `cell-vocabulary` assertion moves to SC1; gate 1 now asserts only the SPEC residue Issues 1.1/1.2 produce — which it does not block — and gains a `files_checked` guard. | `main-session` | `resolved` |
| E2 `${SKILL_DIR}` is the wrong tree | high | Accepted; **the most consequential finding of the pass and neither prior pass raised it.** Every verification of code this plan writes now targets `skills/yf-plan/scripts/` per TESTING.md's Tier-2 rule, and the Approach states the rule and why. | `main-session` | `resolved` |
| E3 `E` demoted at `executing` | high | Accepted. Issue 2.2 now specifies **`promote = false`** (REQ-DATA-053), the mechanism that already exists and that no issue named. The gate's `sed` becomes a belt-and-braces, not the load-bearing fix, and 2.2's backwards rationale is corrected. | `main-session` | `resolved` |
| E4 Epic 6 contradicted in prose | high | Accepted. All three passages and R6's mitigation rewritten; the `43` literal removed from R6. | `main-session` | `resolved` |
| E5 four values, publishes the rejected one | high | Accepted. One value everywhere; Issue 6.4 and SC9b both carry the reproducible figure; `context.md`'s glossary corrected. | `main-session` | `resolved` |
| E6 row 2 population false | high | Accepted, and **re-derived independently**: 5 plans exceed the bound in main (048, 050, 052, 054, 055). All three rows now use that one population — 12/12, 4/5, 2/5 — reproducible in the main checkout. | `main-session` | `resolved` |
| E7 two criteria green today | high | Accepted. SC6b and SC4b now assert against the repo-tree test and on a named behaviour that does not exist yet. | `main-session` | `resolved` |
| E8 positive control tests the linter | high | Accepted. The gate now writes the invalid document **directly** rather than through `escalation-raise` — removing the layering contradiction — and asserts **by check name**. | `main-session` | `resolved` |
| E9 five uncommitted keys | high | Accepted. Every asserted key is now named in its issue's text, `test_herdr_channel.py` is named in Issue 4.2b, SC5's discharge moves to 3.3+3.5, and SC3/SC6's self-report shape is replaced by external observation. | `main-session` | `resolved` |
| E10 gate misses two writes | medium | Accepted. `Blocks` widened; the #269 comment recorded as **already posted**, not scheduled. | `main-session` | `resolved` |
| E11 no fixture issue | medium | Accepted. Issue 1.6 now creates the fixture directory explicitly. | `main-session` | `resolved` |
| E12 `sed -i.bak` residue | medium | Accepted. Replaced with a redirect-and-move that leaves no `.bak`. | `main-session` | `resolved` |
| E13 gate 2 order dependence | medium | Accepted. The gate removes any pre-existing `escalations.md` from its scratch copy first. | `main-session` | `resolved` |
| E14 near-unfalsifiable issue checks | medium | Accepted. Both assert on body content, and are marked as the only network-dependent verifications. | `main-session` | `resolved` |
| E15 E-4's record trips the new check | medium | Accepted. The lifecycle is specified in Issue 2.5: an escalation whose recommended default was taken **without an answer** is `resolved`, with `answer` recording the default. | `main-session` | `resolved` |
| E16 SC1b tautological | medium | Accepted. SC1b asserts the finding is **present at `R`**; SC10 asserts non-null values. | `main-session` | `resolved` |
| E17 "factor of five" survives | medium | Accepted. Removed from the Approach. | `main-session` | `resolved` |
| E18 stale counts | low | Accepted. Corrected. | `main-session` | `resolved` |
| — the closing recommendation | — | **Adopted as a deliverable, not just a fix.** The full mechanical sweep is run over every gate `Test:` and every non-`manual:` criterion, the exit codes recorded in `findings/verification-sweep.md`, and the sweep is added to the plan as Issue 0.1 so it re-runs before intake rather than being a one-off. | `main-session` | `resolved` |
