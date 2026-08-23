---
type: Reference
okf_spec: OKF-PLAN
id: handoff-052
description: Generated handoff from plan-051 to its successor
---

# Handoff: plan-051 → plan-052

**This file is GENERATED.** `scripts/gen_handoff.py --check` regenerates it from
`plan.md`'s tables and `diff`s the result; a non-empty diff exits **1**. That is
SC14's whole point — *"generated, not hand-listed"* is a provenance claim with no
exit code, so the regeneration diff is the equivalent content check. Edit `plan.md`
or the generator, never this file.

## What plan-051 shipped

| Issue | Disposition | End state | What landed |
| :-- | :-- | :-- | :-- |
| #184 | `include` | **CLOSED** | resolved by 2.2 |
| #182 | `include` | **CLOSED** | resolved by 1.2, 1.2a |

## What stays OPEN for the successor

Every row below is still open upstream. A `partial` row received a comment
recording what plan-051 closed and what remains; a `deferred` row received none.

| Issue | Disposition | Title |
| :-- | :-- | :-- |
| #149 | `partial` | M5/M9: process rules that nothing executes, and remediation edges that exist only in prose |
| #165 | `partial` | SPEC `Verification:` lines are prose shaped like commands |
| #173 | `partial` | criteria and dispositions are never checked against the engine that enforces them |
| #174 | `partial` | a review-phase validation pass — falsify every criterion |
| #150 | `partial` | research 004: process-defect mining across 83 plan bundles |
| #177 | `exclude` | no check that a numeric target is derivable from the plan's own scope rules |
| #188 | `deferred` | test suites assert output STRUCTURE and never payload FIDELITY |
| #190 | `deferred` | require plans to ship tests at >= 80% coverage of code they write |
| #145 | `deferred` | New skill: yf-retrospective — measure escape rate |

## Success criteria and how each was verified

| # | Criterion | Discharged by |
| :-- | :-- | :-- |
| SC1 | Every behaviour change landed its `REQ-*` before its implementation issue closed — **one new id and two amendments**, enumerated | 0.1 |
| SC1b | The pre-fix baseline is recorded BEFORE any edit, re-measured rather than inherited | 0.3 |
| SC2 | Every control was observed RED on a fixture, recorded by an issue that is a `depends-on` ANCESTOR of its fix | 0.2, 1.1, 2.1, 3.1 |
| SC2b | Every control was then observed GREEN, and the two observations are distinct records | 1.2a, 2.2, 3.3, 1.4, 2.4, 3.4 |
| SC3 | **The dangling-pointer state fails, and the fixed state passes.** Rewording `red-team.md` without retargeting `spec/agents.md:73` is caught | 1.1, 1.2 |
| SC4 | The literal `Read-only — never writes files` survives at **zero** TRACKED sites, and every `Verification:` clause quoting an agent-file literal resolves | 1.2, 1.2a |
| SC4b | **The hand-enumerated edit set is CLOSED** — every surviving `never writes files` restatement under `skills/yf-plan/**` and `web/content/**` is an enumerated row in `assets/edit-set-182.md` with a stated disposition | 1.2, 1.2a |
| SC5 | The `e-spec-agent` drift edge exists and names the spec as fixed authority | 1.3 |
| SC6 | `SKILL.md` §3's Review section **names `Agent` as the dispatch mechanism** — the claim is about the TEXT, not about conduct (R2/R3: obedience has no exit code) — and the assertion is **section-scoped** | 2.2 |
| SC7 | The Phase-3 wisp **represents the review loop**, its arms are **sequential**, and it carries no counter | 2.3 |
| SC8 | `REQ-AGENT-049`'s `Verification:` line **and** both amended REQs' (`043`, `045`) are executable and green | 3.1, 3.2 |
| SC9 | The executable check is **non-rottable** — it fails if the spec and the test drift apart | 3.2 |
| SC10 | The new check runs at the point of change, on **each** side of the pair independently | 3.3 |
| SC11 | The FULL tier passes over the merged tree, **and all three fixtures are green on it** | 4.1 |
| SC12 | Every upstream row reached the end state its disposition requires | 4.4 |
| SC12b | The coarse tracker is filed THROUGH `/yf-beads-upstream`, so the epic carries it as `external_ref` | 4.3 |
| SC13 | #149's comment carries the **corrected** premise, not the issue's original framing | 4.2, 4.4 |
| SC13b | **#182's CLOSING comment records that D-1 narrowed the issue**, rather than closing it as if its framing were accepted | 4.2, 4.4 |
| SC14 | The handoff is **generated**, and a drift makes it fail | 4.5 |
| SC15 | Both out-of-scope defects are filed with their measurements | 4.6 |
| SC16 | The deployed tree matches source and the version stamp matches HEAD | 4.7 |

## Risks the successor inherits

| # | Risk | Severity |
| :-- | :-- | :-- |
| R1 | **The #182 edit set is enumerated by hand and three of its steps have no mechanical check.** A missed restatement ships a tree that contradicts itself and passes every gate | high |
| R2 | **A text-presence control is gameable by the token it checks for.** `ctl-184-dispatch` is satisfied by a comment or a prohibition containing the word `Agent` | med |
| R3 | **The plan asserts a behavioural claim no exit code can reach.** "The red-team was dispatched" is not mechanically observable | med |
| R4 | **The `plan-review` wisp is new machinery in a plan that did not need it**, and a burnable wisp adjacent to a monotonic counter invites a later "simplification" | med |
| R5 | **A scripted `bd mol burn` silently no-ops.** Measured: cancelled burn on a wisp with an open APPROVE gate exits **0** | low |
| R6 | **Cross-plan control names in `plan.md` wedge the capability gate.** Measured at 7-declared-vs-1-manifest | low |
| R7 | **Deploying mid-execution runs new scripts against old prose** | low |

## Out-of-scope defects filed upstream (Issue 4.6)

*Declared exemption from the tables-only rule: these live in prose, in no table.*

- **`change_validation.py`'s `--changed` repeated-flag drop** — `--changed` is declared with `nargs="*"` and **no** `action="append"`, so `--changed A --changed B` silently validates only `B`. Confirmed at source. A validation-coverage hole affecting every caller.
- **`bd mol burn`'s exit-0-on-cancel with an open gate** — A cancelled burn on a wisp with an open APPROVE gate exits **0**, so a scripted burn cannot tell success from cancellation by exit code. Callers must pass `--force` and check the OUTPUT, not the exit code.

## Non-goals — do NOT re-add these

*Declared exemption: prose bullets, in no table.*

- **The review-cycle counter stays in FILES** — `len(glob('reviews/pass-*.md'))`, monotonic. A wisp is burnable, so a counter inside one is resettable by `bd mol burn`.
- **No parallel review lenses** (D-7). Buildable and spiked; declined for lack of evidence — 29 review passes across four plans, all sequential.
- **No molecule for plan drafting** — it is conversational; beads are pure overhead.
- **No `bd mol bond` for plan chaining** — this generated handoff with its `--check` regeneration diff is already a stronger guarantee than a bond edge.
- **M9 itself, the payload-fidelity group (#188/#190), and #165's corpus sweep.**

## Process findings (from `plan-retrospective.md`)

*Declared exemption: a separate file, not a table.*

`plan-retrospective.md` carries **0** entries.

**The one that generalizes:** a criterion (`SC4b`) was measured green at the issue
that discharged it and was **false two epics later**, because a file added
downstream matched its pattern. Nothing re-checked it — the end-state mandate
covered only criteria that had *fixtures*, and it was caught by an operator
re-measurement rather than by anything the plan shipped. **A criterion is only as
good as the last time something re-ran it.** A successor should re-check every
criterion at completion, not only the ones with a control behind them.
