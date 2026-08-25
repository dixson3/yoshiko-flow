---
type: Plan
okf_spec: OKF-PLAN
id: plan-052-james-dixson-fa8056
author: james-dixson
created: '2026-08-23'
status: executing
deliverable_class: standard
fingerprint: f8bb106e39e99a49943197ecb19162a7e95712527bf1b40a7fe77f0deacc5ada
epic: yf-mol-f2q
---
# Plan: Give yf-plan's review-and-close loop a mechanical spine: a bead representation for the Phase 3 review loop, an end-state re-check of plan.md Success Criteria, and evidence-bearing close-out at land-the-plane

**ID:** plan-052-james-dixson-fa8056
**Author:** james-dixson
**Created:** 2026-08-23
**Status:** executing
**Deliverable-class:** standard
**Epic:** yf-mol-f2q
**Fingerprint:** f8bb106e39e99a49943197ecb19162a7e95712527bf1b40a7fe77f0deacc5ada

## Objective
Give yf-plan's review-and-close loop a mechanical spine: a bead representation for the Phase 3 review loop, an end-state re-check of plan.md Success Criteria, and evidence-bearing close-out at land-the-plane

## Motivation

**The trigger, stated as a measurement.** plan-051 shipped with success criterion `SC4b`
measured green at the issue that discharged it, and **false two epics later** — a file added
downstream matched its pattern and nothing re-ran the check. It was caught by an operator
re-measurement, not by anything the plan shipped. plan-051's own generated handoff draws the
general form: **"A criterion is only as good as the last time something re-ran it."**

**The same class, found again while scoping this plan.** `plan-051/scripts/gen_handoff.py:178`
counts retrospective entries with `re.findall(r"^###\s+(RE-\d+)")` — three hashes. The entries
are written `## RE-001`. So the generated handoff reports **0 entries where 6 exist**, and its
`--check` verb reports **OK**, because it regenerates the same wrong number and diffs it against
itself. plan-051's `SC14` ("the handoff is generated, and a drift makes it fail") is green on
false content.

That is one defect standing for the whole group: **a step with no exit code is not a step, and
an exit code that reads the wrong thing is worse than none** — it manufactures confidence.

**Who is affected.** Every plan run under `yf-plan`. The last two plans between them burned 18
review cycles and produced six defects that were caught by *running* something and none by
reading it.

**What this plan does about it.** Three seams, one thesis — give the review-and-close loop
artifacts with exit codes:

1. **The Phase-3 review loop has no bead representation** (#198). It is prose an agent may skip,
   with a dispatch->record ordering that nothing enforces.
2. **Nothing re-checks `plan.md` Success Criteria at completion** (#199). A criterion discharged
   mid-plan rots silently, which is `SC4b` exactly.
3. **Close-out is manual and its signal is wrong in both directions** (#205). Measured on this
   repo: 1553 beads, 62 mapped — `closable` sees ~4% of the tracker; and a closed bead is taken
   as proof of done work, which #153 refuted three days ago.

Plus the two "prose that nothing executes" instances that share the thesis: formula aspects
(#197) and retrospective `prevention:` fields (#196).

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #198 | yf-plan Phase 3: give the review loop a bead representation | include | **NARROWED by EXP-001** — the gate is a stall point, not a verification primitive. What survives is dispatch verifiability: the exit test reads the file the child wrote | 6.1 |
| #199 | nothing re-checks plan.md Success Criteria at completion | include | **The plan's centre of gravity** (D-21). Split: authoring (1.2) then re-runner (2.2) | 1.2, 2.2 |
| #205 | close-out is manual and the closable signal is wrong in BOTH directions | include | Narrowed to P0/P1/P2 — three changes needing **zero new records**. The run-record prerequisite is filed, not built (D-13) | 3.2, 3.3 |
| #197 | formula aspects: make classify -> lint -> verify a bead that must be closed | include | **RETARGETED by EXP-005** from `plan-execute` (1 declared step, unweavable) to `plan-review` (4 steps) plus injection-time emission | 5.1, 5.2 |
| #196 | retrospective prevention: fields are prose that nothing executes | include | **RE-SCOPED by EXP-005** — distill is refuted as the mechanism; reduces to a `prevention_formula` + `prevention_vars` schema change (~20 lines) | 5.3 |
| #113 | execution-rehearsal review pass (topological DAG walk against running state) | partial | **PULLED IN at D-27, gate-`Blocks`-set consistency ONLY.** Its four cited defects are EXP-006's dominant class. The rest of the rehearsal pass stays open | 4.2 |
| #192 | structure-first plan DSL with generated markdown | partial | **Commented, not scoped (D-29).** Three independent findings converge on it; plan-052 ships narrow sub-keys instead, and records that a third ad-hoc field is the signal the general form should win | — |
| #194 | fan out the red-team into parallel review lenses | exclude | **CLOSED as declined** at scoping — no execution issue required, so this row claims none. plan-052's own EXP-002 supplied the second independent measurement D-3 required: concerns are not lens-clustered, and 75% serial dependence makes fan-out **unsound**. Three reopen conditions recorded, all required | EXP-002 |
| #203 | exit-code discipline: five instruments report failure in output and success in `$?` | partial | This plan applies the 0/1/2 contract to every step it ships. The repo-wide sweep stays open | 2.3 |
| #173 | criteria and dispositions are never checked against the engine that enforces them | partial | #199 closes a named sub-case; the general cross-check stays open | 2.2 |
| #174 | a review-phase validation pass — falsify every criterion | partial | #199, #198 and the gate check close named sub-cases; the general falsification pass stays open | 2.2, 4.2 |
| #149 | M5/M9: process rules that nothing executes | partial | #197 and #196 are worked instances of M5. M9 stays out | 5.1, 5.3 |
| #150 | research 004: process-defect mining across 83 plan bundles | partial | Two more ranked classes worked; the rest stay unscheduled | 5.1, 5.3 |
| #202 | `bd mol burn`: a cancelled burn exits 0 | partial | **Used as EVIDENCE** for the counter decision (D-2), not fixed here | 7.2 |
| #145 | New skill: yf-retrospective | deferred | Own plan. #196 is the narrower buildable piece; the measurement skill still reads a thin corpus | — |
| #188 | test suites assert output STRUCTURE and never payload FIDELITY | deferred | plan-051 non-goal, inherited. `gen_handoff.py`'s miscount is a fresh instance and is worked here, not swept | — |
| #190 | require plans to ship tests at >= 80% coverage of code they write | deferred | plan-051 non-goal, inherited | — |
| #165 | SPEC `Verification:` lines are prose shaped like commands | deferred | The corpus sweep stays out; this plan writes executable clauses for its OWN new REQs | — |
| #191 | scaffold reviews/pass-N.md instead of hand-typing it | exclude | Adjacent to #198 but separable — authoring vs representation. Not scoped (D-1) | — |
| #177 | no check that a numeric target is derivable from the plan's own scope rules | exclude | **CLOSED as wontfix** at scoping — refuted by plan-050 EXP-001 (`81` is textually identical whether measured or guessed) and declined by three successive plans. plan-052 did not investigate it; the close is housekeeping, not a deliverable | — |
| #201 | `change_validation.py`: repeated `--changed` silently drops all but the last path | exclude | Real bug, unrelated seam | — |
| #204 | yf-herdr: no teardown contract | exclude | Sibling of #205 and shares the harvest-before-prune constraint, but is a yf-herdr lifecycle change | — |
| #218 | plan-052-james-dixson-fa8056 execution tracking | tracker | The coarse tracker, filed THROUGH `/yf-beads-upstream` so epic `yf-mol-f2q` carries it as `external_ref` (SC23 asserts that END STATE, never the route) | 7.3 |
| #211 | bd: `distill --var` silently substitutes nothing and exits 0 | deferred | Filed by 7.2/7.3 as deferred defect D1 (EXP-005 I-4(i)) | 7.3 |
| #212 | bd: a `type = "gate"` step with no `[steps.gate]` pours as a plain task | deferred | Deferred defect D2 (EXP-005 I-4(ii)) | 7.3 |
| #213 | bd: `distill` cannot reconstruct gate steps | deferred | Deferred defect D3 (EXP-005 I-4(iii)) | 7.3 |
| #214 | yf-plan: `REQ-PLAN-073` id collision | deferred | Deferred defect D4 (D-18), re-confirmed on the tree at execution time | 7.3 |
| #215 | coordinator/bd: `started_at` written for 86 of 225 beads, not exposed by `bd list --json` | deferred | Deferred defect D5 (D-26 / EXP-006 §1) | 7.3 |
| #216 | coordinator: batched closes make 84% of interval overlap an artifact | deferred | Deferred defect D6 (D-26 / EXP-006 I-5) | 7.3 |
| #217 | yf-change-validation: `change_validation.py` persists no run record | deferred | Deferred defect D7 (D-13 / EXP-004 §4) | 7.3 |

## Scoping decisions

| # | Decision | Basis |
| :-- | :-- | :-- |
| D-1 | **Scope is the spine (#198/#199/#205) plus the "prose that nothing executes" pair (#197/#196).** #191, #177, #201, #204 excluded | Operator decision at scoping. plan-050 burned 13 review cycles on 28 issues; a narrower scope is the measured-cheaper shape |
| D-2 | **The review-cycle counter STAYS IN FILES** — `len(glob('reviews/pass-*.md'))`, monotonic. The sub-DAG may mediate the loop, but must not hold the bound | Operator decision, honoring plan-051's declared non-goal. A wisp is burnable, so a counter inside one is resettable — and #202 measured that a scripted `bd mol burn` **cannot detect its own cancellation by exit code**, so the reset would be silent |
| D-3 | **#194 is revived as an EXPERIMENT ONLY (EXP-002), not as scoped work** | Operator decision. plan-051's D-7 declined it on measurement (29 review passes across four plans, all sequential). The herdr-child-session mechanism is *different* from what was spiked, so the arithmetic is worth re-measuring — but the experiment is allowed to refute the revival |
| D-4 | **Every step this plan ships carries the 0/1/2 exit contract** (pass / fail / INCONCLUSIVE) and every caller READS `$?` | #203. plan-050's `RE-007` and plan-051's `RE-005` are both "an exit code nothing reads" |
| D-5 | **`gen_handoff.py`'s `^###` miscount is IN SCOPE as a worked instance**, not swept into #188 | Found while scoping this plan. It is #199's thesis in miniature: a self-consistency check green on false content |

## Open questions for INVESTIGATE

Recorded before the experiments run, so a finding can refute the scoping decision that
commissioned it.

| Exp | Question | Can it refute? |
| :-- | :-- | :-- |
| EXP-001 | Can bd 1.1.2 express the operator's `start-gate -> stage -> exit-gate` sub-DAG with a **bounded, non-resettable** loop? Which of the five gate types (`human`, `timer`, `gh:run`, `gh:pr`, `bead`) can a script resolve, and what does the audit trail record? | Yes — if no gate type supports a scripted resolve with an honest audit record, #198's mechanism changes shape |
| EXP-002 | Do herdr child sessions change D-7's arithmetic for #194? Tool-call isolation was **not** what plan-051 spiked | Yes — a refutation closes #194 with a second, independent measurement |
| EXP-003 | Across the recent corpus, how many `## Success Criteria` **Verification** cells are machine-runnable as written? #199's re-check is only buildable if the answer is not ~0 | Yes — if the cells are prose, #199 needs an authoring change before a checker |
| EXP-004 | What evidence predicate is actually available at close-out to replace "bead closed"? Commit-touched-paths, a green recipe row, a discharged criterion — which is reconstructable from `bd` + `git` alone? | Yes — if none is reconstructable, #205's part (c) is not buildable this plan |
| EXP-005 | Is `bd mol distill` usable for #196's pourable remediation shape, and what is the minimal formula? Referenced once in this repo, used **zero** times in any execution path | Yes |


### Second investigation round — orthogonality (operator-directed)

EXP-002's 75% measured **review-pass** serial dependence, where overlap is 100% *by
construction* (each pass reviews the prior pass's fixes). **The EXECUTION fan-out injection rate
is unmeasured.** These two experiments measure it, and are written to be able to return "the
corpus cannot answer this."

| Exp | Question | Can it refute? |
| :-- | :-- | :-- |
| EXP-006 | Does defect injection fall when concurrently-eligible units of work are **orthogonal** (no overlap in code or interfaces)? Classify documented injected defects by whether the involved issues were topologically independent — **against the base rate**, since if most pairs are independent then defects between independent pairs proves nothing | Yes — if defects are mostly **intra-issue**, orthogonality is the wrong lever entirely |
| EXP-007 | Can a mechanical **orthogonality test** be built that predicts injection risk and guides DAG iteration during planning? Prototype it against `plan_extract` + `CHANGE-VALIDATION`'s `_scoped_ids()` + `DRIFT-CHECK` edges | Yes — likely outcome is "needs an authoring change first" (issues do not declare touched paths), exactly parallel to EXP-003's finding for #199 |

**Recorded risk for EXP-007: the false-comfort mode.** An orthogonality test reporting "all
clear" on a DAG that then injects defects is **worse than no test** — it manufactures confidence,
which is the defect class this whole plan attacks. The experiment must specify the INCONCLUSIVE
condition (no declared paths ⇒ no input ⇒ `2`, never "orthogonal").

### Deferred scope question — plan-level integration (NOT yet an experiment)

The operator observes the same shape **between concurrent plans in separate worktrees**, where
sequencing is not controllable and the proposal is to *validate and fix integration tests first,
on merge*. This is recorded rather than scoped: it is likely a **separate plan**, and EXP-007
carries only a short secondary probe of whether the metric extends plan-to-plan. Resolve at
drafting.

## Investigation Findings

**All five returned. Every one refuted something**, and two refuted a premise this plan was
built on, and two refuted the upstream issues themselves. That is why they were dispatched to
agents that did not carry the drafting conversation.

| Exp | Verdict | The finding that changes the plan |
| :-- | :-- | :-- |
| [EXP-001](findings/exp-001-bd-subdag-loop.md) | expressible, **modified** | **A gate is NOT a verification primitive.** `bd` records **no resolver identity for any gate resolution** — `--actor` and `BEADS_ACTOR` are both accepted and both discarded; there is no `closed_by`. A script that skips the work and resolves the gate produces a **byte-identical** database state. **#198's central claim must be corrected** |
| [EXP-002](findings/exp-002-parallel-lenses-refuted.md) | **NO — refuted** | Concerns do **not** cluster by lens (4–6 of 6 lenses per substantive pass). And **75% of review passes (15/20) found a defect inside the previous pass's own fix**, so fan-out is **unsound**, not merely unhelpful. #194 closes as declined |
| [EXP-003](findings/exp-003-verification-cells.md) | **0 of 155 — refuted** | **No `Verification` cell in the corpus is a whole-line executable command.** The missing artifact is the **predicate**, not the command: plan-051's SC4 passes on exit **1** and SC6 on exit **0**, and that polarity exists nowhere but the prose. #199 must **split** into authoring (#199a) then re-runner (#199b) |
| [EXP-004](findings/exp-004-closeout-evidence.md) | 3 buildable, 3 not | **The false positive is a TYPED bug — a *hoist tombstone*, written by `upstream.py` in a fixed format and read back as completion. 5 of 47 mapped-closed beads, and #147 is a LIVE false positive right now.** Separately: `change_validation.py` has **one file write in 970 lines** and it writes the manifest — so "a recipe row ran green" **has no record to gate on** |
| [EXP-005](findings/exp-005-distill-and-aspects.md) | split | **Aspects EXIST** (`[compose] aspects`, cooked and poured green) — but they weave at cook time over **formula-declared steps only**, and `plan-execute` declares **1** step. #197's proposal cannot work; its own fallback is the only route. #196 is **refuted as scoped** and shrinks to ~20 lines |

### Decisions forced by the findings

| # | Decision | Basis |
| :-- | :-- | :-- |
| D-6 | **#198's §2 claim that the parent "structurally cannot fabricate the verdict" is WITHDRAWN.** What is load-bearing is the file the child wrote, re-read independently — not the gate. The gate is a stall point and a legible record | EXP-001 §1, re-measured by the main session |
| D-7 | **One gate per stage** (the previous stage's `blocks` edge *is* the start gate), with a **custom `await_type`** (`exit:conform`) rather than `human`, and **on bound-hit the exit gate stays OPEN** so a refusal cannot masquerade as a completed stage | EXP-001 §5 |
| D-8 | **#194 is CLOSED as declined**, with EXP-002 as the second independent measurement. Three specific conditions to reopen are recorded, all three required | EXP-002 §5, D-3 |
| D-9 | **#199 splits: #199a (authoring — a machine-recoverable clause AND a declared expected predicate, plus a first-class `manual` disposition) precedes #199b (the completion-time re-runner).** #199b covers newly-authored plans only; 46 of 53 bundles have no `Verification` column to retrofit | EXP-003 §7 |
| D-10 | **`Discharged-by` is OUT of scope — 0 of 155 dangling.** `doc_lint` R1 already enforces it. The plan's own brief was stale on this point | EXP-003 §5 |
| D-11 | **Do not rebuild the parser or the linter.** `plan_extract.extract()` already returns `verification` and `discharged_by`; `doc_lint` already owns the column/id/non-empty checks. Exactly one thing is missing: a **grammar for the cell's content** and an executor for it | EXP-003 §6 |
| D-12 | **Ship P0 + P1 + P2 for #205 and nothing further.** P0 = suppress hoist tombstones; P1 = render each proposal's evidence (`close_reason` + discharged criteria); P2 = promote the existing `plan-relations` R1/R2a off `severity = "W"` at the close-out binding. **All three need zero new records** | EXP-004 §2/§5 |
| D-13 | **The run-record is OUT of scope and becomes its own upstream issue.** It is the shared prerequisite for both the recipe-row predicate (P5) and the criterion-re-check predicate (P6), and `change_validation.py` persists nothing today | EXP-004 §4 |
| D-14 | **Commit correlation (P4) is DEAD as a gate** — 9.5% strong hit rate, no commit names a bead id, and closing-keyword discipline is absent (20 hits in 576 commits, one a negation). It may be *rendered* under P1, labelled unreliable | EXP-004 §2 |
| D-15 | **The tracker check asserts the END STATE, not the route.** plan-051 has **no `tracker` row**, so `stamp-tracker` returned `skipped` and the stamp came from `/yf-beads-upstream` as a side effect — a check written against the declared route would report a false green on plan-051 itself | EXP-004 §3 |
| D-16 | **#197 re-scoped: `plan-review` gets `[compose] aspects` (zero script change); `plan-execute` gets injection-time `bd create` in §4.3.** The formula route is impossible for `plan-execute` — 1 declared step | EXP-005 Part B |
| D-17 | **#196 reduced to a schema change**: add `prevention_formula` (enum-checked) + `prevention_vars`, leave `prevention` as prose. **Do not distill** — measured lossy for gates, and its `--var` silently substitutes nothing on any value not starting AND ending with a word character, exiting 0 | EXP-005 Part A |
| D-18 | **Four defects to FILE, not fix** (declared out-of-scope, with measurements): three bd defects from EXP-005 I-4, plus the **`REQ-PLAN-073` id collision** (`SPEC.md:345` roots-configurability vs `spec/phases.md:150` stamp-tracker) | EXP-004 I-5, EXP-005 I-4 |


### Round-2 findings — the orthogonality hypothesis is REFUTED by two independent experiments

| Exp | Verdict | The finding |
| :-- | :-- | :-- |
| [EXP-006](findings/exp-006-orthogonality-injection.md) | **REFUTED** | **There is no concurrency to measure** (mean 1.10–1.53; 84% of "overlap" is batch-close bookkeeping). **Only 16% of concerns name two issues; 32% anchor an issue to a NON-DAG artifact.** Topological independence: **z ≈ 1.15, not significant** after deduplication. **Artifact overlap is a 14–24× discriminator in BOTH strata** |
| [EXP-007](findings/exp-007-orthogonality-test.md) | buildable, **1 signal** | Defect pairs 56.4% ordered vs **51.8% base — no discrimination**. Only **shared declared paths** predicts (2.86x, p=3.4e-11); **`CHANGE-VALIDATION` rows are at chance (p=0.85)**. Issues declare no touch-set — 43% prose coverage, `detail` empty for **28/28** in plan-050 |

**The two agree on the null and disagree on its sign** — EXP-007 found defect pairs slightly *less*
independent, EXP-006 slightly *more*, neither significant. That is the signature of noise around a
null. Their base rates match **exactly** (48.2% independent across 049/050/051), computed by
different methods and re-verified by the main session.

**The decisive single case.** plan-051 `RE-003` — the corpus's only execution-phase cross-issue
invalidation — had the edge **already present**: `3.2 depends-on 1.2a` is a direct declared edge,
re-verified. 3.2 ran strictly after 1.2a and the defect landed anyway. **Sequencing guarantees the
second unit runs later, not that it re-checks the first unit's criterion.**

| # | Decision | Basis |
| :-- | :-- | :-- |
| D-19 | **REJECT "the DAG is missing edges."** Resequencing is not the lever: 0 of 5 independent-pair defects would have been prevented by an edge, and within the overlap stratum an edge moves a pair the WRONG way (0.301 → 0.362 defect density) | EXP-006 §4/§5, EXP-007 §1 |
| D-20 | **The lever is SINGLE-WRITER ARTIFACT OWNERSHIP, evaluated over ALL pairs** — not orthogonality over independent pairs, which discards 56% of real defects. Topology becomes a severity modifier | EXP-007 I-1, EXP-006 §4 |
| D-21 | **This CONVERGES on #199.** Two independent experiments reached "the remedy is a completion-time criteria re-check, not new edges." #199 is now the plan's centre of gravity, not one of three peers | EXP-006 I-2, EXP-003 |
| D-22 | **`- touches:` authoring change is the shared prerequisite** — non-breaking, spiked (`--strict` exit 0, `unparsed: []`). Same shape as #199a-before-#199b. **Two mechanisms now block on one missing authoring discipline** | EXP-007 §3 |
| D-23 | **Signals: shared declared paths + `DRIFT-CHECK` edges ONLY.** Exclude `CHANGE-VALIDATION` rows (p=0.85, base rate 78.6%) and shared upstream refs (fired 0 times), **with the measured reason recorded** so a later round does not re-add the row signal because it looks authoritative. Revises EXP-004: `_scoped_ids()` needs **no** CLI verb | EXP-007 §4 |
| D-24 | **Gate-`Blocks`-set consistency is the highest-yield single check the data supports** — one mechanical predicate over `plan_extract`'s gate objects, covering 3 of 5 independent-pair defects plus plan-050's repeat-offender family. **Candidate scope addition** | EXP-006 I-4 |
| D-25 | **The artifact-overlap effect is labelled INFERRED, WEAKLY CORROBORATED** — it is derived from issue prose, and the same prose influences whether a reviewer names two issues together (partial circularity); commit attribution at 13.8% cannot break it. **The independence null-result is solid** and is stated as such | EXP-006 §7 |
| D-26 | **Two instrumentation defects to FILE:** `started_at` is written for only 86 of 225 plan beads (plan-048: 0 of 39) and is not exposed by `bd list --json`; and the coordinator closes beads in batches, making 84% of all interval overlap an artifact. Without both, no concurrency question is ever answerable | EXP-006 §1/I-5 |
| D-27 | **#113 is PULLED IN, scoped to the gate-`Blocks`-set consistency check only** — one mechanical predicate over `plan_extract`'s gate objects. Highest measured yield in the dataset: 3 of 5 independent-pair defects plus plan-050's repeat-offender family. Room exists because EXP-005 shrank #196 and #197 | Operator decision; EXP-006 I-4 |
| D-28 | **#194 and #177 are CLOSED**, with their measurements and reopen conditions recorded upstream. #194 as declined (plan-052's own EXP-002); #177 as wontfix (plan-050 EXP-001, declined by three plans) | Operator decision |
| D-29 | **Ship narrow sub-keys (`- touches:`, a `Verification` predicate clause), NOT the #192 DSL** — additive and reversible, and measured non-breaking. Changing the plan grammar inside a plan whose subject is review-loop integrity would mean altering the artifact under test mid-test. #192 carries the convergence and the reopen signal | Operator decision; EXP-007 §3 |

## Approach

**One thesis, stated as the findings measured it:** *a step with no exit code is not a step, and
an exit code that reads the wrong thing is worse than none.*

The investigation reshaped this plan substantially. Three things it does **not** do, each because
a measurement forbade it:

- **No new DAG edges as a defect remedy** (D-19). plan-051's `RE-003` had the edge `3.2 depends-on
  1.2a` **already present** and the defect landed anyway. Sequencing guarantees the second unit
  runs later, not that it re-checks the first unit's criterion.
- **No parallel review lenses** (D-8, #194 closed). 75% serial dependence makes fan-out unsound.
- **No claim that a gate makes a verdict unfabricatable** (D-6). `bd` records **no resolver
  identity** — `--actor` and `BEADS_ACTOR` are both accepted and discarded.

What survives is a **sequenced** plan: an authoring grammar, then the consumers that grammar makes
possible. Epic 1 must precede Epics 2 and 4 for a reason that recurred twice independently — a
checker with no machine-readable input is permanently INCONCLUSIVE, which is the *correct* verdict
and a useless one.

**This plan dogfoods its own grammar.** Every Success Criterion below is written in the
`Verification` clause form Epic 1 ships. That is deliberate: today's corpus figure is **0 of 155**,
and a plan about executable verification whose own criteria are prose would reproduce the defect it
exists to fix.

### The Verification clause grammar (shipped by 1.2, used by this document)

| Form | Meaning |
| :-- | :-- |
| `` `<command>` → exit 0 `` | must succeed (PASS) |
| `` `<command>` → exit 1 `` | must FAIL specifically — a real negative, not merely "not zero" |
| `` `<command>` → exit 2 `` | must be INCONCLUSIVE — the instrument could not run |
| `` `<command>` → exit non-zero `` | permitted only where 1 and 2 are genuinely equivalent for the claim |
| `manual: <why it cannot be mechanized>` | first-class, not a failure. Prevents fake commands written to satisfy a gate |

**The grammar is THREE-valued because D-4's contract is** (pass-1 M1). A two-valued form would let
`→ exit non-zero` be satisfied by an INCONCLUSIVE — so a criterion asserting *"the harness is not a
silent green"* would pass **while the harness was broken**. Every command is run from the repo root
unless the clause says otherwise, and the extractor **unescapes GFM table pipes** (`\|` → `|`,
`\\` → `\`) before execution (pass-1 M2).

The polarity marker is the load-bearing part: plan-051's SC4 passes on exit **1** and SC6 on exit
**0**, and today that fact exists nowhere but prose.

## Epics

Every issue declares `- touches:`. **Each control lives in its OWN file** under
`assets/controls/`, so every control-builder is the single writer of the paths it touches — pass-2
C7 measured the previous shape at **9 writers on one file, 28 of 36 pairs topologically
independent**, which is the worst single-writer violation in the corpus by the plan's own lever.

### Epic 0: SPEC-first, harness, baselines
- Issue 0.1: Land the four `REQ-*` — `REQ-DATA-070` (Verification clause grammar), `REQ-DATA-071` (`touches[]`), `REQ-PLAN-080` (completion-time re-check), `REQ-BUP-070` (hoist-tombstone suppression) — each with an executable `Verification:` line, BEFORE any implementation commit
  - touches: `skills/yf-plan/spec/data.md`, `skills/yf-plan/spec/phases.md`, `skills/yf-beads-upstream/SPEC.md`
- Issue 0.2: Build the harness and **declare its COMPLETE file-and-interface contract in one place** — pass 4's `RE-002` remedy, because four passes were each refuted by *a global property repaired at the one site the reviewer named*. The contract, all of it here rather than scattered across builders:
  - **Dispatcher** `assets/gate-run.sh` (0/1/2) with subcommands **`run <ctl-id>`, `verify-all`, `verify-set <core|ext|land>`, `verify-partition`, `self-test-broken`**, invoking each control as **`bash "$ctl"`** — never `uv run`, never bare exec, so no control depends on an exec bit.
  - **Generator** `assets/gen-controls.py` producing `assets/controls.txt` (columns `id`, `set`) by scanning `plan.md`'s Verification cells for `ctl-*` — **ignoring prose globs like `ctl-199b-*`, which is how a hand-count reached 28 for a true 27** — and globbing `assets/controls/`. The `set` column is **DERIVED FROM THE BUILDER'S EPIC** (0-4 core, 5-6 ext, 7 land), never hand-assigned.
  - **RED-observation ledger** `assets/red-observations.tsv`, **APPENDED BY `gate-run.sh` on every `run`** and READ by `verify-all` / `verify-set`. Named here because both gate Conditions and SC2 require *a recorded RED observation*, and pass 4 measured that no artifact and no writer existed.
  - **Controls-file override** `CTL_TXT` (env), so a control can point the dispatcher at an alternative set — required by `ctl-empty-set-floor`, which otherwise cannot construct an empty set to observe.
  - **NON-EMPTINESS FLOOR:** `gate-run.sh` exits **2 (INCONCLUSIVE), never 0**, on an empty or unreadable set, and the closure control asserts a DERIVED lower bound — every issue whose `touches:` names `assets/controls/*.sh` must contribute >= 1 id.
  - **UNCOMMISSIONED-INTERFACE RULE, harness-wide:** a control observing an interface a later issue ships MUST map that observation to **exit 1 (a real negative)**; the callee's argparse **exit 2 must never escape**. Exit 2 is reserved for the *instrument itself* failing. This is stated ONCE here rather than per-builder — the class, not the instance.
  - **Control fixtures** are constructed inline in `$(mktemp -d)` by the control and leave no residue, **EXCEPT** where a fixture is a declared repo path (`assets/closable-fixture.json`), which must appear in its builder's `touches:`.
  - **A MISSING declared artifact is exit 1** (a real negative); an **unreadable or malformed** one is exit 2 (instrument failure). Under the exit-1 rule that distinction is load-bearing.
  - **Intra-issue ordering:** where a control and the thing it checks are built by the SAME issue (`ctl-empty-set-floor`, `ctl-baseline-pathspec`), the RED observation is recorded to the ledger **before** that issue's implementation step.
  - **`ctl-harness-contract`** (widening the former `ctl-controls-closure`) asserts, mechanically and **exactly these three arms** — scoped deliberately, because pass 5 measured a broader claim catching only 1 of the 4 defects it was credited with:
    1. **FILE arm** — every file `gate-run.sh` reads or writes appears in some issue's `touches:`. The *"demonstrated present on the tree"* fallback applies **only to paths OUTSIDE this bundle's `assets/`**; anything under `assets/` must be declared.
    2. **INTERFACE arm** — for each `ctl-*.sh`, every subcommand, flag or env var it passes to a repo script must appear in that script's `--help` **or** be named as commissioned in some issue. This is the arm that catches `--fixture` and `CTL_TXT`; a file-granular check cannot.
    3. **BUILDER-PRECEDES-FIXER arm** — for every control criterion, the builder issue must not have any other discharger among its own **ancestors**; where it is the sole discharger, the criterion must state how RED is obtained. **This is the predicate that would have found `ctl-req-landed` without a reviewer naming it.** An inversion or sole-discharger case is a **finding UNLESS the criterion OR ITS BUILDER ISSUE states how RED is obtained** — the three stated cases are `SC1` (in the criterion), and `SC0c` / `SC1b` (in this issue's intra-issue-ordering rule above). Without this exemption the arm permanently fails on the plan's own three by-design cases and makes SC0 unsatisfiable — measured at pass 6 by implementing the arm and running it.
  The **non-emptiness floor** is asserted separately by `ctl-empty-set-floor` (SC0c), and the **exit-1 mapping rule** is enforced by the gate Conditions themselves — neither is claimed here.
  Re-spike the dispatcher against a deliberately broken fixture
  - depends-on: 0.1
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/gen-controls.py`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls.txt`, `docs/plans/plan-052-james-dixson-fa8056/assets/red-observations.tsv`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-harness-contract.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-empty-set-floor.sh`
- Issue 0.3: Record every pre-fix baseline WITH its verbatim pathspec; build its THREE controls. **BOTH `ctl-spec-first-order` AND `ctl-req-landed` are GREEN on the live tree at this point** — 0.1 is this issue's ancestor and has already landed all four `REQ-*` — so each is driven RED against a **pinned negative fixture** (respectively: a recorded history where an impl commit precedes the SPEC commit; a fixture spec tree with one `REQ-*` absent). A control that cannot be RED proves nothing
  - depends-on: 0.2
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/baseline-pre-fix.md`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-baseline-pathspec.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-req-landed.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-spec-first-order.sh`
- Issue 0.4a: Build the two handoff controls and observe them RED against `gen_handoff.py`'s `^###` miscount
  - depends-on: 0.2
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-handoff-count.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-handoff-drift.sh`
- Issue 0.4: Fix the `^###` miscount and make the handoff check sensitive to CONTENT
  - depends-on: 0.4a
  - touches: `docs/plans/plan-051-james-dixson-2f499f/scripts/gen_handoff.py`

### Epic 1: The authoring grammar — shared prerequisite
- Issue 1.1: Build `ctl-199a-grammar` and `ctl-class-a-fraction` RED; the grammar fixture MUST include a piped command so the unescape rule is exercised. `ctl-class-a-fraction` is **GREEN on this plan's own table (97.2%)**, so it is driven RED against a **pinned prose-cell fixture**
  - depends-on: 0.2, 0.3
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-199a-grammar.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-class-a-fraction.sh`
- Issue 1.2: Ship the three-valued `Verification` grammar, the `manual` disposition and the GFM pipe-unescape rule in CANONICAL `_shared/`, vendored copy synced
  - depends-on: 1.1
  - resolves-upstream: #199 (include)
  - touches: `_shared/doc_lint.py`, `_shared/document_types/plan.toml`, `skills/yf-plan/scripts/doc_lint.py`
- Issue 1.3: Build `ctl-touches-subkey`, `ctl-touches-coverage` and `ctl-ownership-inconclusive` RED. `ctl-touches-coverage` is **GREEN on this plan (100%)**, so it is driven RED against a **pinned fixture with a `touches:`-less issue**
  - depends-on: 0.2, 0.3
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-touches-subkey.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-touches-coverage.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-ownership-inconclusive.sh`
- Issue 1.4: Promote `- touches:` to a first-class `touches[]` field in CANONICAL `_shared/plan_extract.py`, vendored copy synced
  - depends-on: 1.3
  - touches: `_shared/plan_extract.py`, `skills/yf-plan/scripts/plan_extract.py`
- Issue 1.5: Ship `ownership-report` — single-writer ownership over ALL pairs, REPORT-ONLY, on shared declared paths (S1) and DRIFT-CHECK edges (S3) only; `CHANGE-VALIDATION` rows (S2, p=0.85) and shared upstream refs (S4, fired 0 times) EXCLUDED with the measurement in a code comment. **The INCONCLUSIVE floor is 80% path coverage, stated numerically**
  - depends-on: 1.4
  - touches: `skills/yf-plan/scripts/plan_manager.py`

### Epic 2: Completion-time criteria re-check
- Issue 2.1: Build the five `ctl-199b-*` controls RED — `rot`, `inconclusive`, `fields`, `recursion`, `halt`
  - depends-on: 0.2, 0.3
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-199b-rot.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-199b-inconclusive.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-199b-fields.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-199b-recursion.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-199b-halt.sh`
- Issue 2.2: Ship `recheck-criteria` with the 0/1/2 contract and two distinct fields — `class_a_fraction`, `evaluated_fraction`. **`YF_RECHECK_DEPTH` is the LOAD-BEARING guard; the name-check is BEST-EFFORT and scans the EXECUTED COMMAND STRING ONLY, never the criterion row.** The depth rule is stated as a rule about what each depth MAY DO: **depth 0 and depth 1 evaluate; depth 2 returns exit 2 (INCONCLUSIVE) without executing.** That makes the four fixture-driven controls (SC6/SC8/SC9/SC10) valid standalone AND under the close chain, where they run at depth 1
  - depends-on: 1.2, 2.1
  - resolves-upstream: #199 (include)
  - touches: `skills/yf-plan/scripts/plan_manager.py`
- Issue 2.3: Make the §6.4 close chain call `recheck-criteria` as a HALTING step that exits non-zero FROM THE VERB, as `verify-reconcile` already does
  - depends-on: 2.2
  - resolves-upstream: #203 (partial)
  - touches: `skills/yf-plan/SKILL.md`

### Epic 3: Close-out evidence
- Issue 3.1: Build `ctl-205-tombstone`, `ctl-205-promote` and `ctl-205-fixture-flag` RED against a PINNED fixture snapshot, never live `bd` state. **Each RED must be a REAL NEGATIVE (exit 1) against the fixture, never an argparse exit 2 from the not-yet-existing `--fixture` flag** — an uncommissioned interface reads as INCONCLUSIVE, which the gates now refuse
  - depends-on: 0.2, 0.3
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-205-tombstone.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-205-promote.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-205-fixture-flag.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/closable-fixture.json`
- Issue 3.2: P0 — **add the `--fixture` flag to `closable`** (it does not exist today: `closable --help` shows `[-h] [--json]` only), suppress hoist tombstones, and ANNOTATE the row rather than dropping it
  - depends-on: 3.1
  - resolves-upstream: #205 (include)
  - touches: `skills/yf-beads-upstream/scripts/upstream.py`
- Issue 3.3: P1 — render EVERY proposal's mapped beads, their `close_reason`, AND the criteria they discharge, AND wire it into `cmd_closable`, which builds and prints its report inline
  - depends-on: 3.2
  - resolves-upstream: #205 (include)
  - touches: `skills/yf-beads-upstream/scripts/upstream_render.py`, `skills/yf-beads-upstream/scripts/upstream.py`, `skills/yf-beads-upstream/scripts/test_upstream.py`
- Issue 3.4: P2 — promote `plan-relations` R1/R2a at the CLOSE-OUT binding only, in canonical `_shared/`
  - depends-on: 3.3
  - touches: `_shared/document_types/plan-relations.toml`

### Epic 4: Gate-Blocks-set consistency
- Issue 4.1: Build `ctl-113-gate` RED with TWO positive and TWO negative fixtures, PLUS a third negative reproducing the **PRE-FIX** `red-prework-core` (pass-2 C2: the six core controls' dischargers inside the Blocks set) AND a **positive** fixture asserting the CURRENT gate passes — regression protection in both directions. The current gate is clean under both arms, so a negative reproducing it cannot exist
  - depends-on: 0.2, 0.3
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-113-gate.sh`
- Issue 4.2: Ship the predicate, resolving INDIRECTION: no issue in a gate's `Blocks` may be named in its `Condition`/`Test`/`Instructions` as producing its evidence, **AND no control the Condition requires may have all its dischargers inside — or transitively behind — that `Blocks` set**
  - depends-on: 4.1
  - resolves-upstream: #113 (partial)
  - touches: `skills/yf-plan/scripts/gate_consistency.py`, `skills/yf-plan/scripts/plan_manager.py`, `skills/yf-plan/scripts/test_gate_consistency.py`

### Epic 5: Obligations that execute (SEVERABLE)
- Issue 5.0: Build `ctl-aspect-weave`, `ctl-197-injection` and `ctl-196-enum` RED
  - depends-on: 0.2, 0.3
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-aspect-weave.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-197-injection.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-196-enum.sh`
- Issue 5.1: Ship a `verify-artifact` aspect attached to `plan-review` via `[compose] aspects` — NEVER a top-level `aspects` key, which is silently ignored
  - depends-on: 5.0
  - resolves-upstream: #197 (include)
  - touches: `skills/yf-plan/formulas/verify-artifact.formula.toml`, `skills/yf-plan/formulas/plan-review.formula.toml`
- Issue 5.2: Emit injection-time verify beads for `plan-execute`, whose formula declares 1 step and cannot be woven
  - depends-on: 5.1
  - resolves-upstream: #197 (include)
  - touches: `skills/yf-plan/scripts/verify_beads.py`, `skills/yf-plan/scripts/plan_manager.py`, `skills/yf-plan/scripts/test_verify_beads.py`
- Issue 5.3: Add `prevention_formula` (enum-checked against `bd formula list`) and `prevention_vars`, leaving `prevention` as prose
  - depends-on: 5.0, 0.1
  - resolves-upstream: #196 (include)
  - touches: `skills/yf-plan/scripts/retrospective_fields.py`, `skills/yf-plan/scripts/test_retrospective_fields.py`, `skills/yf-plan/scripts/plan_manager.py`, `_shared/document_types/plan-retrospective.toml`

### Epic 6: Dispatch verifiability (SEVERABLE)
- Issue 6.0: Build `ctl-198-freshness` RED — a stale prior pass file must NOT satisfy the exit test
  - depends-on: 0.2, 0.3
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-198-freshness.sh`
- Issue 6.1: Make the review exit test read the file the child wrote and prove it is FRESH; state in `red-team.md` that a gate resolution carries NO resolver identity and is a record, not a guarantee
  - depends-on: 6.0, 1.2
  - resolves-upstream: #198 (include)
  - touches: `skills/yf-plan/agents/red-team.md`

### Epic 7: Reconcile and land
- Issue 7.0: Build the four land-set controls RED — `ctl-cv-rows`, `ctl-deferred-count`, `ctl-tracker-endstate`, `ctl-deploy-stamp`. **Each RED is obtained against a PINNED fixture, never against live machine state** — `ctl-deploy-stamp` is RED today only because the installed stamp happens to be stale, which a `yf self install` before this issue would silently reverse
  - depends-on: 0.2, 0.3
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-cv-rows.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-deferred-count.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-tracker-endstate.sh`, `docs/plans/plan-052-james-dixson-fa8056/assets/controls/ctl-deploy-stamp.sh`
- Issue 7.1: Land the `CHANGE-VALIDATION.md` recipe rows and trigger-scope globs for everything this plan ships, THEN run the FULL tier over the merged tree and re-run every control on it
  - depends-on: 0.4, 1.5, 2.3, 3.4, 4.2, 5.2, 5.3, 6.1, 7.0
  - touches: `CHANGE-VALIDATION.md`
- Issue 7.2: Enumerate the SEVEN deferred defects in `assets/deferred-defects.md` and file each — 3 bd defects (EXP-005 I-4), the `REQ-PLAN-073` id collision, 2 coordinator instrumentation defects (D-26), the `change_validation` run-record (D-13) — and generate the upstream authorization PROPOSAL
  - depends-on: 7.1
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/deferred-defects.md`, `docs/plans/plan-052-james-dixson-fa8056/assets/upstream-grant-proposal.md`
- Issue 7.3: Post upstream comments and closes per the disposition table; file the coarse tracker THROUGH `/yf-beads-upstream`; AND record the `tracker` row — the row cannot exist before the issue is filed, which is why SC23 asserts the END STATE
  - depends-on: 7.2
  - touches: `docs/plans/plan-052-james-dixson-fa8056/plan.md`
- Issue 7.4: Generate the handoff with a check sensitive to CONTENT
  - depends-on: 7.3
  - touches: `docs/plans/plan-052-james-dixson-fa8056/references/handoff-053.md`
- Issue 7.5: Rebuild, deploy, and verify the installed tree AFTER the final commit
  - depends-on: 7.4
  - touches: `docs/plans/plan-052-james-dixson-fa8056/assets/sc-deploy.md`

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: red-prework-core
- Type: auto
- Condition: every control whose set column reads core in the GENERATED assets/controls.txt has a recorded RED observation with EXIT 1 — an exit 2 is INCONCLUSIVE and does NOT satisfy this gate
- Test: bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh verify-set core
- Blocks: 0.4, 1.2, 1.4, 1.5, 2.2, 2.3, 3.2, 3.3, 3.4, 4.2
- Instructions: EVERY core control is built by a builder outside this Blocks set — 0.3, 0.4a, 1.1, 1.3, 2.1, 3.1, 4.1. That closure is asserted mechanically by ctl-harness-contract, not by this sentence; pass 2 measured the previous hand-maintained claim false in both directions
- gate_type: auto
- test_class: probe
- cwd: worktree

### Capability Gate: red-prework-ext
- Type: auto
- Condition: every control whose set column reads ext in the GENERATED assets/controls.txt has a recorded RED observation with EXIT 1 — an exit 2 is INCONCLUSIVE and does NOT satisfy this gate
- Test: bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh verify-set ext
- Blocks: 5.1, 5.2, 5.3, 6.1
- Instructions: split from core so Epics 5-6 stay severable (R8) and Epic 1 never waits on an Epic 5 control. Builders 5.0 and 6.0 sit outside this Blocks set
- gate_type: auto
- test_class: probe
- cwd: worktree

### Capability Gate: upstream-write
- Type: human
- Condition: the operator has written an authorization file covering every action the generated proposal requires
- Test: uv run skills/yf-plan/scripts/plan_manager.py grant docs/plans/plan-052-james-dixson-fa8056 --check docs/plans/plan-052-james-dixson-fa8056/assets/upstream-authorization.txt --json
- Blocks: 7.3
- Instructions: outward-facing and NOT hoistable. 7.2 generates the PROPOSAL; assets/upstream-authorization.txt is WRITTEN BY THE OPERATOR AND BY NO ISSUE, which is why it appears in no touches list. Verified at pass 2 by execution — an absent or empty file exits 1 with verdict fail, so a touched file cannot satisfy it
- gate_type: human
- test_class: consent
- cwd: repo-root

### Reconcile Gate
- Type: auto (all execution beads closed)
- Condition: every non-gate execution bead under this plan's epic, EXCLUDING the reconcile step itself, is closed
- Test: bd list --all --include-gates --json | jq -e '[.[]|select(.metadata.plan=="plan-052-james-dixson-fa8056" and .metadata.plan_issue != null and .issue_type!="gate" and ((.title|startswith("Reconcile:"))|not) and .status!="closed")]|length==0'
- Blocks: reconcile step
- Instructions: the exclusion is REQUIRED and was verified load-bearing at pass 1 by running the jq against live bd (REQ-AGENT-046). AMENDED AT EXECUTION (operator-detected): the Test lacked `.metadata.plan_issue != null` and so counted the SEVEN deferred-defect beads Issue 7.3 files, which are OPEN BY DESIGN because they track upstream issues #211-#217 that are open upstream — they never close, so the gate could never open. Those beads are `parent=-`, which protects cascade-close (it walks the epic tree) but NOT this Test, which keys on `metadata.plan` and never looks at parentage. The CONDITION was already correct — it says `under this plan's epic` — so this was a Test/Condition FIDELITY defect, not a Condition change. Discriminator measured on live bd: of 43 beads stamped `plan=plan-052`, 31 carry `metadata.plan_issue` (every execution bead, REQ-DATA-026/D-10) and 12 do not (the reconcile step, the 7 defect beads, and 4 gates). The `startswith("Reconcile:")` clause is retained as redundant-but-defensive

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **The ownership check ships on a partially circular measurement** | high | 1.5 ships **report-only**, never a gate, and states the circularity in its output |
| R2 | **`recheck-criteria` covers only newly-authored plans** — the criteria table exists in 5 of 53 bundles | high | Declared limit in 2.2; `evaluated_fraction` reported as a NUMBER every run |
| R3 | **`manual:` becomes the universal escape hatch** | high | `class_a_fraction` reported separately; SC7 asserts a floor via a NON-recursive tool |
| R4 | **The corpus is unmigrated, so the re-check is INCONCLUSIVE everywhere and reads as broken** | med | Exit 2 maps to `warn`, never a hard gate (REQ-DATA-057 precedent), asserted by SC8 |
| R5 | **A control is satisfied by the token it checks for** | med | 4.1 requires two positive, two negative AND a third negative reproducing this plan's own gate; 0.2 re-spikes the harness against a broken fixture (SC3) |
| R6 | **Deploying mid-execution runs new scripts against old prose** | med | Deploy only at 7.5 |
| R7 | **This plan edits the skill it executes under** | med | `SKILL_DIR` cannot reach the repo's `skills/`; the constraint is R6 |
| R8 | **Scope is 8 epics / 31 issues / 49 edges, MEASURED by `plan_extract` and re-measured after every rewrite** (hand-counts were wrong THREE times: 7/24, 31-for-30, 47-for-49 — which is why SC0 makes the control set generated rather than counted) | med | Epics 5 and 6 are severable — no dependents outside their epics except 7.1. Severing needs **FOUR** edits, not three — pass 4 simulated it and found the documented recipe fails `doc_lint` R1: remove 5.x/6.x from 7.1's `depends-on`, delete SC14–SC17, drop `red-prework-ext`, **and remove 5.0/6.0 from SC0/SC0b/SC2's `Discharged-by`**, which P3-C2's fix added |
| R9 | **A `Verification` command dies on a GFM-escaped pipe.** The count is DERIVED, not asserted — an earlier literal ("9") was measured false (actual 4) after a rewrite | med | 1.2 ships the unescape rule; 1.1's fixture exercises a piped command (SC5) |
| R11 | **ACCEPTED RESIDUAL RISK: all 10 pairs of the five `plan_manager.py` writers are topologically INDEPENDENT** — the plan's own validated 2.86x lever firing at maximum on its own DAG, and `ownership-report` is itself generated by one of the five | med | **Accepted deliberately, on D-19 — because NO EFFECTIVE REMEDY EXISTS.** EXP-006 measured that 0 of 5 independent-pair defects would have been prevented by an edge, and that within the overlap stratum an edge moves defect density the WRONG way (0.301 → 0.362). Resequencing is refuted, so acceptance is the correct disposition, not a concession. *(Corrected at pass 5: this row previously justified acceptance with D-25's weak-corroboration label, which attaches to EXP-006's overlap inference — not to EXP-007's shared-declared-paths signal at p=3.4e-11, which is what this risk is actually about. The reasoning now matches R10 and D-20.)* |
| R10 | **`plan_manager.py` has multiple writers across topologically independent issues** — the plan's own validated lever (2.86x, p=3.4e-11) flags it | med | The `gate-run.sh` case was **fixed structurally** (9 writers → 1, each control in its own file). **`plan_manager.py` was NOT: pass 3 measured that the 2-writer figure was an artifact of OMITTING the call sites** — the new modules had no declared binding, and adding one restores the count. The call sites are now declared, so the true figure is **5 writers** (1.5, 2.2, 4.2, 5.2, 5.3). This is **surfaced, not eliminated**, and is stated at its real value rather than at the value that flattered the metric |

## Success Criteria

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC0 | **The asserted control set, the built control set and `assets/controls.txt` are ONE object** — closure is generated, never hand-maintained. Pass 2 measured the hand-maintained version at 25 asserted / 14 built / 11 orphaned | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-harness-contract` → exit 0 | 0.2, 0.3, 0.4a, 1.1, 1.3, 2.1, 3.1, 4.1, 5.0, 6.0, 7.0 |
| SC0b | `core ∪ ext ∪ land == all`, and `verify-all` FAILS if any asserted control id is absent from the generated file | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh verify-partition` → exit 0 | 0.2, 0.3, 0.4a, 1.1, 1.3, 2.1, 3.1, 4.1, 5.0, 6.0, 7.0 |
| SC0c | **An EMPTY or unreadable control set is INCONCLUSIVE, never green.** Spiked at pass 3: `∅ == ∅ == ∅` satisfied closure, `verify-all` over an empty file exited 0, and `∅∪∅∪∅ == ∅` satisfied the partition — all three flagship criteria green while nothing was checked | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-empty-set-floor` → exit 0 | 0.2 |
| SC1 | Every `REQ-*` id this plan introduces EXISTS on the merged tree. **Its builder 0.3 has 0.1 among its ancestors, so the live tree is already green there** — the ONLY builder/fixer inversion in the plan, found by `ctl-harness-contract`'s third arm. RED is therefore obtained from a **pinned fixture spec tree with one `REQ-*` absent**, and the merged-tree assertion is discharged at 7.1 | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-req-landed` → exit 0 | 0.1, 0.3, 7.1 |
| SC1b | Every baseline figure is recorded WITH the verbatim pathspec that produced it | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-baseline-pathspec` → exit 0 | 0.3 |
| SC1c | The commit touching `skills/*/spec/**` or `skills/*/SPEC.md` PRECEDES the first commit touching any OTHER `skills/**` path — checked **PRE-MERGE and PRE-SQUASH at 7.1**. The earlier form ("before the first `skills/**` commit") was false by construction: 0.1's own touches are all under `skills/**` | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-spec-first-order` → exit 0 | 0.3, 7.1 |
| SC2 | **Every control in the generated set** was observed RED with a NON-ZERO exit — no literal count appears anywhere | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh verify-all` → exit 0 | 0.2, 0.3, 0.4a, 1.1, 1.3, 2.1, 3.1, 4.1, 5.0, 6.0, 7.0 |
| SC3 | The harness FAILS on a deliberately broken fixture, with a real negative rather than an INCONCLUSIVE | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh self-test-broken` → exit 1 | 0.2 |
| SC4 | `gen_handoff.py`'s retrospective count is CORRECT, and a wrong extractor makes it fail | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-handoff-count` → exit 0 | 0.4a, 0.4 |
| SC5 | A prose cell FAILS the shape check, a clause-form cell passes, and a clause containing a GFM-escaped pipe survives unescaping | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-199a-grammar` → exit 0 | 1.1, 1.2 |
| SC5b | `- touches:` is a FIRST-CLASS field returned by `plan_extract` | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-touches-subkey` → exit 0 | 1.3, 1.4 |
| SC5c | **This plan's own issues declare `touches:` at 100%** — no slack, because it is 100% today and a budget cannot detect the degradation it exists to prevent | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-touches-coverage` → exit 0 | 1.3, 1.4 |
| SC6 | `recheck-criteria` reports `class_a_fraction` AND `evaluated_fraction` as distinct numbers, run against a FIXTURE plan | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-199b-fields` → exit 0 | 2.1, 2.2 |
| SC6b | **Depth 0 and depth 1 evaluate; depth 2 returns exit 2 (INCONCLUSIVE) without executing** — asserted on DEPTH, not on a name match, because every clause routes through `gate-run.sh` and no clause contains the literal `recheck-criteria` | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-199b-recursion` → exit 0 | 2.1, 2.2 |
| SC7 | **This plan's own criteria are >= 90% class-(a)**, measured by a NON-recursive tool reading `plan_extract` output | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-class-a-fraction` → exit 0 | 1.1, 1.2 |
| SC8 | An INCONCLUSIVE re-check maps to `warn` and never hard-fails completion | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-199b-inconclusive` → exit 0 | 2.1, 2.2 |
| SC9 | A criterion true at discharge and FALSE at completion is CAUGHT — plan-051's SC4b reproduced | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-199b-rot` → exit 0 | 2.1, 2.2 |
| SC10 | A failing re-check HALTS the close chain — observed on a fixture, not a token grepped from prose | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-199b-halt` → exit 0 | 2.1, 2.3 |
| SC11 | `closable` emits NO close proposal for an issue whose only closed beads are hoist tombstones | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-205-tombstone` → exit 0 | 3.1, 3.2 |
| SC11b | **The `--fixture` flag EXISTS** — it does not today, and pass 2 caught two criteria depending on an uncommissioned interface | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-205-fixture-flag` → exit 0 | 3.1, 3.2 |
| SC12 | **EVERY** proposal renders its mapped beads' `close_reason` AND the criteria they discharge — a present-but-empty key does not discharge it | `uv run skills/yf-beads-upstream/scripts/upstream.py closable --fixture docs/plans/plan-052-james-dixson-fa8056/assets/closable-fixture.json --json \| jq -e '(.issues\|length) > 0 and all(.issues[]; (.beads\|length)==0 or (((.close_reasons\|length) > 0) and ((.discharges\|length) > 0)))'` → exit 0 | 3.3 |
| SC12b | R1/R2a gate at the CLOSE-OUT binding ONLY — authoring-time severity unchanged | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-205-promote` → exit 0 | 3.1, 3.4 |
| SC13 | A gate is CAUGHT when an issue in its `Blocks` produces its evidence **or** when a required control's dischargers all sit inside or transitively behind that `Blocks` set — the second arm is what pass 2's C2 needed and C8 showed a name-match cannot see | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-113-gate` → exit 0 | 4.1, 4.2 |
| SC14 | The `verify-artifact` aspect weaves over ALL FOUR `plan-review` steps, and a top-level `aspects` key is shown NOT to weave | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-aspect-weave` → exit 0 | 5.0, 5.1 |
| SC15 | `plan-execute` gets its verify beads at INJECTION time | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-197-injection` → exit 0 | 5.0, 5.2 |
| SC16 | `prevention_formula` is enum-checked; an unknown name is REJECTED | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-196-enum` → exit 0 | 5.0, 5.3 |
| SC17 | The review exit test reads the file the child wrote AND proves it is FRESH | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-198-freshness` → exit 0 | 6.0, 6.1 |
| SC18 | `ownership-report` returns INCONCLUSIVE below **80% path coverage** — the floor is a NUMBER, and it never reports "orthogonal" on no input | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-ownership-inconclusive` → exit 0 | 1.3, 1.5 |
| SC18b | `ownership-report` is REPORT-ONLY and states its own circularity | `uv run skills/yf-plan/scripts/plan_manager.py ownership-report docs/plans/plan-052-james-dixson-fa8056 --json \| jq -e '.report_only == true'` → exit 0 | 1.5 |
| SC19 | The FULL tier passes over the merged tree AND carries recipe rows for everything this plan ships | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-cv-rows` → exit 0 | 7.0, 7.1 |
| SC20 | Every upstream row reached the end state its disposition requires | `uv run skills/yf-plan/scripts/plan_manager.py verify-reconcile docs/plans/plan-052-james-dixson-fa8056 --json \| jq -e '.verdict == "pass"'` → exit 0 | 7.3 |
| SC21a | **All SEVEN deferred defects are filed** — the count is derived from `assets/deferred-defects.md`, produced by 7.2 | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-deferred-count` → exit 0 | 7.0, 7.2 |
| SC21b | Each filed defect carries its measurement | manual: whether a measurement is present AND correct is a reader judgement over issue prose. Split from SC21a deliberately — the count is checkable and IS checked; only the substance is waived | 7.2 |
| SC22 | The handoff is generated AND its check is sensitive to content | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-handoff-drift` → exit 0 | 0.4a, 7.4 |
| SC23 | The coarse tracker is filed THROUGH `/yf-beads-upstream` so the epic carries it as `external_ref` — asserted as an END STATE, never against the `stamp-tracker` route | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-tracker-endstate` → exit 0 | 7.0, 7.3 |
| SC24 | The deployed tree matches source and the stamp matches HEAD, verified AFTER the final commit and a rebuild | `bash docs/plans/plan-052-james-dixson-fa8056/assets/gate-run.sh run ctl-deploy-stamp` → exit 0 | 7.0, 7.5 |
