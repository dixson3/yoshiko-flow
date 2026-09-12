---
type: Plan
okf_spec: OKF-PLAN
description: Freeze yf-plan mechanism growth and convert the review loop from reading
  to executing, with an approval-to-landing fidelity metric and subtraction of declared-but-unenforced
  layers
id: plan-071-james-dixson-d19ce8
author: james-dixson
created: '2026-09-10'
status: approved
deliverable_class: standard
fingerprint: d623f1066a0f9491c8f2319270f6eb0763b6e309db4d5f0a4db6118cfb4232d3
---
# Plan: Freeze yf-plan mechanism growth and convert the review loop from reading to executing, with an approval-to-landing fidelity metric and subtraction of declared-but-unenforced layers

**ID:** plan-071-james-dixson-d19ce8
**Author:** james-dixson
**Created:** 2026-09-10
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** d623f1066a0f9491c8f2319270f6eb0763b6e309db4d5f0a4db6118cfb4232d3

## Objective
Freeze yf-plan mechanism growth and convert the review loop from reading to executing, with an approval-to-landing fidelity metric and subtraction of declared-but-unenforced layers

## Motivation

Over roughly thirty days (plans 050 through 070) this repository ran a chain of plans that each
fixed "execution fidelity and completeness" defects in `yf-plan`. A second-opinion review of
that corpus (this session, 2026-09-10; six plans read by one reviewer, five by another, and an
architecture survey by a third) found one class rather than many local bugs, and a loop that
cannot see it:

- **One defect class, renamed at least six times.** Silent green, vacuous check, exit 0 on
  refusal, declared-not-enforced, phantom resolution, stub with no caller. Named by #181, #203,
  #230, #263, #392 and plan-060's RE-020. The words "vacuous" and "silent" appear in the
  retrospectives of every one of the 21 plans from 050 onward, and the frequency is not decaying.
- **Review has near-zero recall on that class; execution has near-total recall.** Every
  landing-chain defect since plan-062 (#327, #340, #364, #388, #389, #352, #353) was found by
  *running*, none by the 27 review passes over plans 062/063/068. plan-068 pass 4 recorded that a
  further reading pass had negative value. plan-050 pass 5 measured that delegated review did not
  lower the fix-injection rate. #286 records that an open brief on a converged plan manufactures
  concerns. The skill still spends 5 to 13 passes per plan reading.
- **Mechanism grew 3 to 5x while the defect rate stayed flat.** `plan_manager.py` 3,170 → 10,649
  lines, `spec/` 608 → 3,184 lines, REQ ids ~167 → 256, `_land_*` functions 0 → 47, between
  2026-08-10 and HEAD. Upstream issues opened in ISO weeks 33-37: 285; closed: 128. The script's
  history is 65 near-append-only commits (+11,300 / −663). Nothing removed the layer that failed.
- **The land chain is only ever tested by landing.** Every plan since 062 halted or crashed while
  landing itself; each halt became the next plan's scope. plan-070's own `context.md` says it will
  deadlock on the gate it fixes.
- **The review loop's enforcement layer is dead code.** `formulas/plan-review.formula.toml` has
  no pour caller. Since plan-045 the main session resolves the red-team's concerns itself and
  re-dispatches without acknowledgement.

**The underspecified goal.** The implicit goal is *approval should predict a clean landing*, and
nothing measures it. The system measures concerns per pass, REQ coverage and pass-file counts. It
does not measure the two numbers that matter: success criteria that flip or are amended after
approval, and halts after the first irreversible write. Both are at or near 100% per plan.

**Operator direction (verbatim, this session):** freeze the mechanism; convert the review loop
from reading to executing; adopt the fidelity metric; subtract before adding; "prune the REQ-LAND
requirements — they are likely an accreted patch log"; "similar for the defunct checks in
plan_manager.py"; "reduce the code to only what is provably necessary".

Who is affected: every operator running `/yf-plan`, and every future plan in this repository,
which currently pays a review tax that does not buy landing fidelity.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#397](https://github.com/dixson3/yoshiko-flow/issues/397) | plan-071-james-dixson-d19ce8 execution tracking | tracker | The single coarse tracking issue for this plan-scale effort (AGENTS.md convention); stamped onto the epic as `external_ref` at pour (REQ-PLAN-073) | — |
| [#323](https://github.com/dixson3/yoshiko-flow/issues/323) | red-team: EXECUTE each success criterion at review time | include | The execution pass smoke-runs and evaluates every clause-form criterion | 2.1, 2.4 |
| [#338](https://github.com/dixson3/yoshiko-flow/issues/338) | red-team runs NO mechanical checker | include | The execution pass runs every shipped bundle checker; the brief names them | 2.1 |
| [#384](https://github.com/dixson3/yoshiko-flow/issues/384) | a criterion can be green before its Discharged-by issues ran; commands never smoke-run | include | Smoke-run at `ready-check`; `not-yet-dischargeable` reporting is out (execution-time, not review-time) — **partial** on defect 1, **include** on defect 2 | 2.4 |
| [#286](https://github.com/dixson3/yoshiko-flow/issues/286) | red-team passes need a CONVERGENCE STANDARD | include | Reading passes are capped at two; passes 3+ are execution-only with a closed finding vocabulary | 2.1, 2.2 |
| [#392](https://github.com/dixson3/yoshiko-flow/issues/392) | META: declared in prose, acted on by code | partial | **In:** the backlog lens is applied to yf-plan's own review loop, the REQ-LAND set and the manager's checks (Epics 3, 4); this plan's own draft D-10 — a corpus grep declared in prose and never run — the pass-1 C1 resolution cell that described an edit only half made (#306), the draft SC3 whose grep could never go green (pass-3 C1), and a `cell-vocabulary` check that binds only the first table in a review file (pass-3 C3) are recorded as further instances. **Out:** the remaining members (#388/#389/#266/#387) — plan-070 owns #388/#389 | 0.4, 4.6, 4.7 |
| [#364](https://github.com/dixson3/yoshiko-flow/issues/364) | recheck-criteria runs without the criteria preamble env | include | The one real oracle must evaluate what it is pointed at; preamble env established at every binding | 4.3 |
| [#325](https://github.com/dixson3/yoshiko-flow/issues/325) | gate_consistency.py returns PASS on gates it cannot evaluate | include | Two facts, one signal: no-gates (PASS) vs none-evaluable (INCONCLUSIVE); engine runs at `ready-check` first, chain row is a regression guard | 2.4, 4.4 |
| [#356](https://github.com/dixson3/yoshiko-flow/issues/356) | executable criterion can false-fail on an empty collection | partial | **In:** the smoke-run classifies an empty-collection false-fail as an authoring defect at review time. **Out:** a grammar extension | 2.4 |
| [#358](https://github.com/dixson3/yoshiko-flow/issues/358) | a criterion must assert what the PLAN DID, not what the WORLD IS | partial | **In:** the fidelity metric counts a post-approval flip caused by external state as an authoring defect, not a regression. **Out:** a criterion-class taxonomy | 1.2 |
| [#306](https://github.com/dixson3/yoshiko-flow/issues/306) | the phantom resolution cell | partial | **In:** the execution pass re-verifies every prior pass's `resolved` cell by running its claimed edit's evidence. **Out:** a write-guard | 2.1 |
| [#390](https://github.com/dixson3/yoshiko-flow/issues/390) | an inference recorded as a measurement survived six passes | include | Execution-pass findings carry `measured:` with command+exit; an `inferred:` finding cannot block | 2.1, 2.2 |
| [#289](https://github.com/dixson3/yoshiko-flow/issues/289) | no instrument compares cited figures against commands | exclude | Already shipped by plan-060 as `scripts/checks/check-cited-figures.py`; the execution pass merely runs it | — |
| [#328](https://github.com/dixson3/yoshiko-flow/issues/328) | apply the measurement-ordering argument exhaustively | exclude | A red-team heuristic for reading passes; this plan reduces reading passes rather than improving them | — |
| [#312](https://github.com/dixson3/yoshiko-flow/issues/312) | process-audit stage: make retrospective/landing/preflight BEADS | exclude | Adds mechanism; contradicts the freeze. Revisit after one clean landing | — |
| [#395](https://github.com/dixson3/yoshiko-flow/issues/395) | bd mol pour drops the formula's declared gate type | exclude | plan-070's domain (gate metadata); not touched here | — |

## Investigation Findings

### Pre-investigation checkpoint (written before dispatch)

**Scoping decisions so far.**

- D-1 **Provably necessary is the retention standard.** A verb, check, formula, agent step or
  REQ stays only if (a) it sits on a live call path from `SKILL.md`, an `agents/*.md`, the land
  executor or `CHANGE-VALIDATION.md`, **and** (b) a test exists that makes it fail on a fixture
  (a negative control). Anything failing either leg is deleted, not deprecated.
- D-2 **Freeze.** This plan adds no new `plan_manager.py` verb and no new `REQ-LAND-*` id. Any
  new requirement it needs is a rewrite of an existing id or lives outside the LAND family.
  The freeze is checked mechanically (SC on verb count and REQ-LAND count not increasing).
- D-3 **Two reading passes, then execution.** The red-team brief gets a pass-index rule: passes
  1 and 2 may be prose; pass 3 and every later pass must run commands and may raise only
  `measured:` findings. The `max-review-cycles` default stays 5.
- D-4 **The metric is two numbers, recorded where the retrospective already writes.**
  `retrospective-append` gains no new verb; a `--kind fidelity` entry carries
  `sc_flipped_post_approval` and `halts_post_irreversible`. `retrospective-report` prints them.
- D-5 **plan-070 is not touched.** #388/#389/#393/#394/#395 stay with plan-070; this plan lands
  after it or independently of it, never on top of its files.
- D-6 **The plan applies its own rule to itself.** Its review runs two reading passes and then
  an execution pass; its landing records the fidelity numbers as the first data point.

**Approach hypothesis.** The defect class is unreachable by reading and reachable by execution;
the mechanism has grown past what any landing exercises; therefore (1) convert review to
execution, (2) delete everything not provably necessary, (3) measure whether approval now
predicts landing. If the metric does not move after three plans, the hypothesis is wrong.

**Experiments.**

| Exp | Question | Refutes |
| :-- | :-- | :-- |
| EXP-001 | Is the REQ-LAND-001..039 set a coherent design or a patch log? What is the minimal load-bearing subset? | D-1 as applied to the spec, if most ids turn out load-bearing and tested |
| EXP-002 | Which manager verbs and sibling checks are dead, vacuous, advisory-only or duplicated? How much of the corpus can `recheck-criteria` actually see? | D-1 as applied to code, if the prune list is small |

### EXP-001 — REQ-LAND coherence ([findings/exp-001-req-land-coherence.md](findings/exp-001-req-land-coherence.md))

- measured: 39 ids (001–038 + 017a; 027 is a hole; **REQ-LAND-039 does not exist in the tree**, plan-070 allocates it unlanded). `spec/landing.md` is 760 lines of which 141 (19%) are normative "shall" text and ~365 (48%) are rationale, amendment or argumentative prose. The "amendment log" is inline bold paragraphs, not blockquotes (8 `>` lines total).
- measured: 10 commits, four plans (060, 062, 063, 068). plan-069/070 never touched the file. **The plan premise "060/062/063/068/069/070" was two plans too long.**
- measured: every Verification-named test exists (36/36). No id is untested by that standard.
- measured: **two ids describe behaviour that does not exist.** REQ-LAND-015's gate-close `route_record` stamp has no writer (#393, reader at `plan_manager.py:6796`). REQ-LAND-018's "re-preview immediately before merge" has no code in `_land_l2_merge`; staleness is caught only via the digest's `predicted_tree`.
- measured: five ids are verbatim restatements (003, 005, 007, 009, 025); four are patch-log entries with no forward requirement (016, 027, 028, 031). `LAND_EXECUTOR` has 15 keys against a spec that says "twenty steps"; `_land_l8_to_l15_close_chain` is misnamed (L12/L13 have separate keys).
- inferred: **a coherent core of ~22 behaviours wrapped in defect narrative.** Pruning is compression and merge, not deletion of behaviour. Proposed set after pass-2 C2 recount: 22 ids, ~300 lines (delete 3, absorb 14 into six merge groups, rewrite the rest as forward requirements).
- Refutes: nothing in D-1. Confirms the freeze must first reconcile 015 and 018 to what exists, or it locks in spec-vs-impl disagreement.

### EXP-002 — manager dead/vacuous audit ([findings/exp-002-manager-dead-vacuous-audit.md](findings/exp-002-manager-dead-vacuous-audit.md))

- measured: 41 `@cli.command` verbs. **8 have no live caller** (`ownership-report`, `escalation-report`, `verify-beads`, `gate-consistency`, `index-add`, `judgement-echo-check`, `grant`, `attest-validation`). **4 live verbs cannot fail by construction** (`audit-close`, `retrospective-report`, `judgement-never-fired-report`, `classify-deliverable`). `parked` duplicates a `list` filter.
- measured: in `_land_l8_to_l15_close_chain`, **exit 2 never halts for any verb**; L5 reports `pass` regardless of return code; L14 `pour_fidelity` is the only step where INCONCLUSIVE halts.
- measured (two runs): with a 60s whole-verb bound 6 of 11 recent bundles time out; with `--timeout 10` per criterion over 22 bundles **71% of 515 criteria evaluate** — 10 completed plans FAIL, 6 INCONCLUSIVE, 4 HARNESS_INCOMPLETE, 2 PASS. **`recheck-criteria` is a working oracle**; its defects are the never-halting exit-2 arm, a 300s default per-criterion timeout, and a duplicate L5 run. Ten landed plans have criteria that are FALSE today (rot vs. noise uncorroborated).
- measured: the close chain is encoded **three times** (SKILL.md §6.4 bash, `LAND_CLOSE_CHAIN`, `land_rehearsal._REHEARSAL_PM_VERBS`) with no test joining them. Three test files (`test_escalations.py`, `test_judgement_trigger.py`, `test_severity_vocabulary.py`) run in no CV row or CI. `harness-selftest.sh` plus 16 checks and 6 more `check-*.sh` have no caller.
- measured: `plan-review.formula.toml` and `verify-artifact.formula.toml` have **zero pour/wisp callers**.
- measured: `gate_consistency.py` returns PASS on zero gates (#325) yet FAILs on plan-068 (4 findings) and plan-070 (3) — a real detector nothing on a live path consumes. `repair_dangling_epics.py`, 17 `scripts/checks/*.sh` and 5 `scripts/checks/*.py` are wired into no CI, CV row or test.
- Left to plan-070: `_gate_is_resolved` collapse (#394), `route_record` writer (#393). Out of scope: `check_gh_direct.py` needles (#281, yf-beads-upstream).
- Refutes: nothing in D-1. Confirms the prune list is large enough (~1,150 lines) that the freeze is substantive.

### Pre-review smoke of this plan's own criteria (main session, 2026-09-10)

Every SC command was run under `bash -c` from the repo root before the first red-team pass. measured: 20 rows, all clause-form; no exit 126/127, no usage error. 13 rows RED as expected pre-change; SC4/SC10/SC15 RED (the artifacts they assert absent still exist); SC17 INCONCLUSIVE (no amendment-log entry yet). **Three rows were GREEN before any change** (SC5, SC7, SC16 ran existing test files) and were tightened to require the new case by name. Four rows (SC6, SC8, SC9, SC13) fail on `No such file` for artifacts the plan creates — the case Issue 2.4's smoke rule must allow, so the rule was written against it.

## Approach

![Review and landing loop: before and after](diagrams/loop-before-after.png)

Three moves, in this order: **specify the subtraction first**, **make the review execute**, **then
delete**. Every epic after Epic 0 depends on an Epic 0 issue that names its requirement, so the
SPEC-first rule and `check_amendment_log` A2 both hold by construction.

Decisions (D-1 to D-6 are from scoping; D-7 onward come from the findings):

- **D-1 Provably necessary is the retention standard** (scoping). Live call path **and** a
  fixture-failing test, or it is deleted. Applied to verbs, sibling scripts, formulas, chain
  steps and REQ-LAND ids alike.
- **D-2 Freeze.** No new `plan_manager.py` verb, no new `REQ-LAND-*` id, no new land step. The
  freeze has exactly **one declared exception** (D-9). It is measured by SC1/SC2, not promised.
- **D-3 Two reading passes, then execution.** Red-team passes 1 and 2 may be prose. Pass 3 and
  later run commands and may raise only `measured:` findings. An execution pass with zero measured
  findings is the convergence standard (#286). `max-review-cycles` default stays 5.
- **D-4 The metric is two numbers, computed not transcribed.** `sc_flipped_post_approval` = SC
  rows whose `Verification` cell differs between the fingerprinted approved `plan.md` and the
  landed one, plus rows FALSE at L11. `halts_post_irreversible` = the count of `- landing-halt: <phase> <verb>` bullets in the bundle's
  `log.md` whose phase is at or after `L_PUSHED_1`, plus conflict-state entries. The bullet is
  written by `land --apply`'s existing halt path **before** it returns (pass-1 C5: the journal
  under `/.yf/` is gitignored, cleared at the terminal green state, and records only progress
  states — plan-062's ends at `L_MIRRORED` with no trace of the L18 crash — so it cannot be the
  source). `landing-halt:` is an inert token like `intake:`. The intake commit is findable by its
  fixed subject `<plan-id>: INTAKE approved (awaiting /yf-plan execute)` (48 exist).
  `retrospective-report --fidelity` derives both; `retrospective-append --kind fidelity` records them.
- **D-5 plan-070 lands first.** #388/#389/#393/#394/#395 stay there. A `probe` capability gate
  ("plan-070 has landed") blocks 0.4 and 3.2, so `spec/landing.md` is rewritten once, on top of
  070's amendments, and 070's `route_record` writer/reader pair is preserved. Ordering also removes
  R4's hazard for free (pass-1 C12): 070 lands through the unchanged chain, so its 15 prose criteria
  never meet the new INCONCLUSIVE halt; migrating them after approval would itself count as 15
  `sc_flipped_post_approval` events.
- **D-6 The plan applies its rule to itself.** Its own review is two reading passes then an
  execution pass (SC9); its landing is the metric's first post-change data point.
- **D-7 The REQ-LAND prune is compression and merge, not behaviour deletion** (EXP-001). 39 →
  22 ids (39 − 3 deleted − 14 absorbed). 015 is kept as plan-070 implemented it; 018 is **absorbed** into the group-1 digest requirement with its unimplemented "re-preview before merge" claim dropped (pass-3 C4). Behaviour a test pins is kept.
- **D-8 INCONCLUSIVE from a halting chain verb halts.** Today only L14 does this. A landing that
  cannot evaluate its own criteria is not a clean landing; the grammar becomes mandatory at
  `ready-check` (every SC row clause-form or `manual:`), so the halt is reachable only by a plan
  approved before this change. That is deliberate and named in R4.
- **D-9 The single freeze exception: one repo check that enforces the freeze.**
  `scripts/checks/check-provably-necessary.py` asserts every registered verb has a live caller
  and a test, and every REQ-LAND id has an existing Verification test. It ships with five negative
  controls (including "the only test hit is an enumeration list") and a `CHANGE-VALIDATION.md` FAST row. Without it the freeze is prose (#392).
- **D-10 (revised at pass 1, C1) The deliverable-class subsystem stays.** The draft proposed
  deleting it "if the corpus has never used it"; the red-team ran the grep the draft only described
  and found **plan-031 and plan-041 carry `deliverable_class: ci-release` in frontmatter**. The
  premise was false, and it was declared in prose rather than measured before approval — an
  instance of #392 inside this plan. Issue 4.2 is re-scoped to give `attest-validation` (an
  operator-offered remediation verb with no test) a test, and to anchor any future corpus grep on
  frontmatter (`^deliverable_class:`) with the plan's own directory excluded, never on a needle the
  scanned document quotes. **Operator-offered remediation verbs** (`attest-validation`,
  `clear-epic`) count as having a live call path under D-1 when `SKILL.md` instructs the operator
  to run them; they still need leg (b), a test.
- **D-11 Out of scope, named.** `check_gh_direct.py` needles (#281, another skill); a
  `not-yet-dischargeable` criterion state (#384 defect 1, execution-time); #312's bead-ification
  (adds mechanism); recheck-criteria's >60s runtime (halved by deleting L5; a per-row timeout
  already exists).

## Epics

### Epic 0: SPEC-first — the requirements every later epic implements
- Issue 0.1: Amend `REQ-PLAN-030` (review shape) and add `REQ-AGENT-066` (the execution-pass contract): passes 1–2 may read; pass ≥3 runs the shipped bundle checkers and every clause-form criterion, emits `Mode: reading|execution` in `pass-N.md`, and raises only `measured:` findings with command + exit code; `inferred:` findings cannot be `high`. Amendment-log entries in `SPEC.md` and `skills/yf-plan/SPEC.md`. **Cited, not amended:** REQ-AGENT-049, REQ-AGENT-043.
- Issue 0.2: Add `REQ-PLAN-084` (the approval-to-landing fidelity metric: the two derived numbers, their sources, and the `fidelity` retrospective kind) and `REQ-PLAN-085` (`ready-check` requires every Success Criteria row to be clause-form or `manual:` and smoke-runs every command; INCONCLUSIVE from a halting close-chain verb halts). Amendment-log entries.
- Issue 0.3: Add `REQ-PLAN-086` (the freeze and retention standard D-1/D-2/D-9 as a requirement, pinning the verb-count ceiling **32** and REQ-LAND-count ceiling **22** that `check-provably-necessary.py` reads; the arithmetic — 41 − 6 dead − `audit-close` − `parked` − `judgement-never-fired-report` = 32 — is stated in the requirement so slack of zero is visible). Amendment-log entry.
- Issue 0.4: Rewrite `skills/yf-plan/spec/landing.md` to the EXP-001 pruned set **on top of plan-070's landed amendments** (the "plan-070 has landed" gate blocks this issue; `REQ-LAND-039` folds into the merged 004 L6 row and 070's amendments to 004/006/015/017a are carried into their merged destinations): keep 001, 006, 010, 013, 014, 017, 019, 026, 035 verbatim; merge 002+003+018+036 → one re-derivation/digest requirement; 004+005+025+023+031 → the order table (023/031's L18 rules become that row's text); 006+007+008+009 → one journal requirement; 011+029 → one resume requirement; 032+033 → one L16 requirement; 024+034+026 → one dry-run contract (mutates nothing, halting findings); rewrite 012, 017a, 020, 021, 022, 030, 037 (keep the `DERIVED:` fence), 038 as forward requirements; delete 016, 027, 028; keep 015 as plan-070 implemented it (writer + reader). State "20 logical steps, 15 executor keys" once. Every retained id keeps a one-line `Verification:` naming an existing test. Arithmetic: 39 ids − 3 deleted − 14 absorbed by the six merge groups = **22** survivors (the verbatim-keep list is 001, 006, 010, 013, 014, 017, 019, 035 plus the merged 026; 039 arrives inside 004's row). Target ≤22 ids, ≤350 lines. Amendment-log entry listing every merged/deleted id and its destination.
  - depends-on: 0.3

### Epic 1: The fidelity metric
- Issue 1.1: Extend `RETROSPECTIVE_KINDS` with `fidelity` and give `retrospective-append` the two fields `--sc-flipped-post-approval` and `--halts-post-irreversible` (integers, required for that kind). Tests: the kind is accepted, a missing field is refused, the entry renders as the existing two-column table. **No new verb** (REQ-PLAN-084).
  - depends-on: 0.2
- Issue 1.2: Add `retrospective-report --fidelity <plan_dir>`: derives `sc_flipped_post_approval` by diffing the `Verification` column between `git show <approval-commit>:plan.md` (the commit `commit-plan` made at intake) and the working `plan.md`, plus rows FALSE in the latest `recheck-criteria` output; and **runs `recheck-criteria --json` itself** with the plan's preamble env (pass-1 C11: no step persists L11's output, so there is no file to read); derives `halts_post_irreversible` by counting `- landing-halt:` bullets in `log.md` at or after `L_PUSHED_1`. The bullet is emitted by `land --apply`'s existing halt path (each halting `fail` step: phase, verb, `irreversible` flag) before the journal is cleared — an edit inside `_land_execute`, not a new step. Where a bundle predates the bullet the report says `no-record`. Prints both and, with `--record`, calls the Issue 1.1 writer. Tests with a fixture bundle carrying one flipped cell and a journal with one post-L6 halt (REQ-PLAN-084).
  - depends-on: 1.1
- Issue 1.3: Baseline. Run the Issue 1.2 derivation over plans 060–070 and write `findings/fidelity-baseline.md` (one row per plan: id, approval commit, sc flipped, halts post-L6, **current `recheck-criteria` verdict at `--timeout 10`**, source). Where no `landing-halt:` record exists (all of 060–070 predate it), record `no-record`, never a zero; the `source` column says which of `log.md` / `plan-retrospective.md` / `no-record` each number came from. The verdict column records the EXP-002 rot signal (10 FAIL / 22) so a later plan can adjudicate rot vs. noise.
  - depends-on: 1.2

### Epic 2: The review loop executes
- Issue 2.1: Rewrite `agents/red-team.md` per REQ-AGENT-066: a `## Mode` rule keyed on the pass index (count of existing `pass-*.md` + 1); the execution-pass procedure — run `doc_lint --path plan.md`, `plan_extract --strict`, `gate_consistency.py`, `check_amendment_log.py`, `check-req-coverage.py`, `okf.py reindex --check`, `audit`, then every clause-form SC command with a 60s bound, recording exit codes; re-verify every `resolved` cell in prior passes by running the evidence it names (#306); a finding table with a `measured|inferred` column; an execution pass with zero measured findings returns `APPROVE`. Emit `**Mode:** reading|execution` under the verdict line.
  - depends-on: 0.1
- Issue 2.2: `SKILL.md` Phase 3: replace the open-ended "resolve and re-dispatch until APPROVE" narrative with the two-then-execute shape, the `Mode:` line, and the #390 vocabulary rule (a cross-artifact claim is `measured:` with command + output or it is labelled `inferred:`). Keep `max-review-cycles` at 5.
  - depends-on: 0.1
- Issue 2.3: `test_review_agent_contract.py` pins REQ-AGENT-066 (the `Mode` rule, the checker list, the `measured|inferred` column) with a negative control: a copy of `red-team.md` missing the rule fails the test.
  - depends-on: 2.1
- Issue 2.4: `ready-check` enforces REQ-PLAN-085: runs `gate_consistency.py` over the bundle (FAIL blocks readiness; pass-1 C3 — the engine's first look must be pre-approval, not L8 after the push); every SC row clause-form or `manual:` (reuse `doc_lint`'s `_verification_clause_ok`, do not write a second grammar), and each command is smoke-run under `bash -c` with a 30s bound — exit 126/127, a timeout, or `usage:` / `unrecognized arguments` / `command not found` on stderr fails with the row id; a `No such file` is a failure **unless the missing path is named in the plan's `## Epics` text** (a declared deliverable that does not exist yet — measured on this plan: SC6, SC8, SC9, SC13 reference files Issues 2.4, 1.3, 2.1, 4.6 create). The allow-list is derived from `plan_extract.py` output, never hand-listed. New `test_ready_check_smoke.py` with a passing fixture and three failing fixtures (prose cell, `command not found`, argparse usage error).
  - depends-on: 0.2
- Issue 2.5: Delete `formulas/plan-review.formula.toml` and `formulas/verify-artifact.formula.toml`; remove them from `plan066_checks.py`/`plan067_checks.py` `SHIPPED_FORMULAS`, `test_retrospective_fields.py KNOWN`, the ctl-270-seam case in `test_judgement_trigger.py`, `README.md`, the web formula pages/diagram source, and `web/content/pages/formulas.md:61` ("The five shipped formulas" → "three"), which `scripts/checks/check_web_counts.py`'s `FORMULA_COUNT_RE` compares against `len(census["formulas"])`. `bd formula list` in a sandbox `bd init` shows neither. **No new REQ** — this is a bug fix to REQ-PLAN-030's shipped shape (an unpoured formula is dead code).
  - depends-on: 0.1

### Epic 3: The REQ-LAND prune, code side
- Issue 3.1: Rename `_land_l8_to_l15_close_chain` → `_land_l8_to_l11_close_chain`; update `LAND_EXECUTOR`, `derive_land_launchers.py`, `check_land_seam.py`, `land_rehearsal.py`, `test_land_*.py` and `lander.md`. Retag every test whose name or docstring cites a merged or deleted REQ-LAND id to the surviving id (mapping from Issue 0.4's amendment entry). `test_landing_spec_enumerates_steps_and_journal_states` additionally pins the id count ≤22.
  - depends-on: 0.4
- Issue 3.2: REQ-LAND-015 continuity after plan-070. `audit-close` is deleted by Issue 4.3, so `_land_route_record_findings` needs a surviving caller: move its call into `land --dry-run` facts (which already read the epic via `_land_epic_from_bd`; `ready-check` is bd-free and stays so — pass-2 C3), keep plan-070's negative control green, and record `REQ-LAND-015 branch: reader relocated to <site>` in `log.md`.
  - depends-on: 0.4, 4.3
- Issue 3.3: `SKILL.md` §6.0/§6.4 and `spec/phases.md` "Landing" section: replace every reference to a merged or deleted REQ-LAND id; `grep -o 'REQ-LAND-[0-9a]*' skills/ SPEC.md | sort -u` is a subset of the retained set.
  - depends-on: 3.1

### Epic 4: The manager prune
- Issue 4.1: Delete the six dead verbs (`ownership-report` + `_ownership_pairs`, `escalation-report`, `verify-beads`, `index-add`, `judgement-echo-check` + `_judgement_echo`, `grant` + `_grant_actions_for`/`_grant_proposal`/`_grant_coverage`) and their test files/cases (`attest-validation` survives per D-10 and gets its test in 4.2); merge `parked` into `list --parked` and rewrite its two callers at `SKILL.md:1962` and `:1977`; update `spec/cli.md` REQ-CLI-006's enumeration line and `test_cli_enumeration.py`; remove the verbs from the web CLI page so `check_cli_to_page.py` stays green (REQ-PLAN-086).
  - depends-on: 0.3
- Issue 4.2: D-10 (revised). The subsystem stays (measured at pass 1: plan-031, plan-041 are `ci-release`). Give `attest-validation` a test (`test_complete_gate.py`: the attestation it writes satisfies `complete-gate`; a malformed attestation does not), so it meets D-1 leg (b). Record the measurement `D-10 measured: 2 ci-release bundles (plan-031, plan-041); subsystem retained` in `log.md` (REQ-PLAN-086).
  - depends-on: 0.3
- Issue 4.3: Close-chain honesty: delete `_land_l5_advisory_recheck` and its `LAND_EXECUTOR`/journal entries; delete `audit-close` (same engine as `audit`) from the chain and as a verb; merge `judgement-never-fired-report` into `retrospective-report` (one advisory report; the escalation summary becomes a section; rewrite its caller at `SKILL.md:1705` and its `LAND_CLOSE_CHAIN` row); in `_land_l8_to_l11_close_chain` a halting verb's exit 2 halts (`halt_class: inconclusive`) per REQ-PLAN-085; lower `recheck-criteria`'s default per-criterion `--timeout` from 300s to 60s (pass-1 C7: no SC in this plan runs a multi-minute command; SC14 is `manual:` for that reason); tests in `test_land_apply.py` for the exit-2 halt and for L5's absence.
  - depends-on: 0.2, 3.1
- Issue 4.4: `gate_consistency.py` distinguishes two facts it currently collapses (#325, pass-1 C3): **no capability gate declared** → PASS, `gates: 0`, exit 0 (a legitimate plan, e.g. plan-069); **gates declared but none has an issue-kind `Blocks`** → exit 2 INCONCLUSIVE with `evaluated/total`. The existing `gate-consistency` verb wrapper is **kept** (it is the chain's only way to run the engine) and wired into `LAND_CLOSE_CHAIN` as halting in `audit-close`'s former row — a **regression guard**, because Issue 2.4 already ran the engine at `ready-check` before approval. `test_gate_consistency.py:109` asserts both cases; `test_close_contract.py` asserts the tuple `("gate-consistency", ..., True)`. **No new REQ** — a bug fix to a shipped check under REQ-PLAN-085's halting rule.
  - depends-on: 4.3
- Issue 4.5: Delete `repair_dangling_epics.py`, `harness-selftest.sh` and every `scripts/checks/*` file that is neither named in `CHANGE-VALIDATION.md`, `.github/workflows/*`, or a `test_*.py`, **nor imported/sourced by a file that is** (`_common.sh`, `_figures.py`, `_web_corpus.py` stay; `_*` and `__pycache__` are excluded from the sweep — pass-1 C9) (the EXP-002 list: the 16 checks the selftest wraps, 6 further caller-less `check-*.sh`, `check-assets-decided.py`, `check-backfill-audit-delta.py`, `check-description-coverage.py`, `check-index-boilerplate-ratio.py`, `plan066_checks.py`). Wire the three unrun yf-plan test files (`test_escalations.py`, `test_judgement_trigger.py`, `test_severity_vocabulary.py`) into a CV row or delete them with the code they test. Anything a spec still cites gets its citation updated in the same change (REQ-PLAN-086).
  - depends-on: 0.3
- Issue 4.6: D-9. `scripts/checks/check-provably-necessary.py`: for every `@cli.command` in `plan_manager.py` require ≥1 call site in `SKILL.md`/`agents/*.md`/`LAND_CLOSE_CHAIN`/`LAND_EXECUTOR`/`CHANGE-VALIDATION.md` and ≥1 **invocation-form** reference in a `test_*.py` (`plan_manager.py <verb>` inside an argv list or a `CliRunner.invoke`; a bare mention in an enumeration list such as `test_cli_enumeration.py` does not count — pass-1 C10); for every `REQ-LAND-*` id in `spec/landing.md` require the `Verification:` test to exist as a `def`; read the ceilings from REQ-PLAN-086. Exit 0/1/2. Five negative-control fixtures (dead verb, verb whose only test hit is an enumeration list, REQ with missing test, verb-ceiling exceeded, REQ-LAND-ceiling exceeded). Add a FAST row to `CHANGE-VALIDATION.md` scoped to `skills/yf-plan/**`.
  - depends-on: 4.1, 4.3, 3.1, 4.7
- Issue 4.7: One source for the close chain. `LAND_CLOSE_CHAIN` is the source; `land_rehearsal._REHEARSAL_PM_VERBS` is derived from it (import, not copy); `test_close_contract.py` gains an assertion that SKILL.md §6.4's verb order equals `LAND_CLOSE_CHAIN` followed by the L12–L15 steps, with a negative control that reorders one SKILL.md line. **No new REQ** — a bug fix to REQ-COMPLETE-001's shipped shape (#392 double-enumeration).
  - depends-on: 4.3

### Epic 5: Land under the new rule
- Issue 5.1: FULL tier green on the merged tree (`change_validation.py run --tier full`), every test file under `skills/yf-plan/scripts/` green, and SC1–SC14 measured green in this checkout before `land --dry-run`. Record the measurements in `log.md`. **No new REQ** — this is the plan's own validation step.
  - depends-on: 1.3, 2.3, 2.4, 2.5, 3.2, 3.3, 4.2, 4.4, 4.5, 4.6, 4.7

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: allocated REQ ids are free
- Type: auto
- Condition: `REQ-AGENT-066`, `REQ-PLAN-084`, `REQ-PLAN-085`, `REQ-PLAN-086` appear in no file that holds `REQ-*` ids
- Test: for id in REQ-AGENT-066 REQ-PLAN-084 REQ-PLAN-085 REQ-PLAN-086; do if grep -rq "$id" skills/yf-plan/spec skills/yf-plan/SPEC.md SPEC.md; then echo "TAKEN: $id"; exit 1; fi; done
- Blocks: 0.1, 0.2, 0.3
- Instructions: ONE-SHOT — evaluate before Epic 0 lands; exits 1 by design afterwards. On TAKEN, renumber in plan.md before pouring.
- test_class: probe
- cwd: repo-root

### Capability Gate: plan-070 has landed
- Type: auto
- Condition: plan-070-james-dixson-810177 is `complete` on `main`, so `spec/landing.md` carries its amendments before this plan rewrites the file
- Test: git show main:docs/plans/plan-070-james-dixson-810177/plan.md 2>/dev/null | grep -q '^status: complete$'
- Blocks: 0.4, 3.2
- Instructions: Land plan-070 first (`/yf-plan execute plan-070-james-dixson-810177`, then its `land`; if its reconcile gate is poured `human` per its own R2, resolve it by hand as plan-068 did). This gate is world-state by design — it orders two plans — and is decidable at execute start, so the sweep frontloads it.
- test_class: probe
- cwd: repo-root

### Capability Gate: baseline suite is green before deletion begins
- Type: auto
- Condition: The land and review suites pass on the execute branch before any verb or chain step is removed
- Test: uv run skills/yf-plan/scripts/test_land_apply.py && uv run skills/yf-plan/scripts/test_review_verdict.py && uv run skills/yf-plan/scripts/test_cli_enumeration.py
- Blocks: 3.1, 4.1, 4.3, 2.5, 4.5
- Instructions: `build` class — run with `--sweep-gates=all` or as the first step of Issue 3.1. A red baseline means a regression already exists and must be named before this plan deletes anything, or a deletion will be blamed for it.
- test_class: build
- cwd: repo-root

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **Merge collision with plan-070.** Both touch `plan_manager.py`'s close chain and `spec/landing.md` (070 adds REQ-LAND-039 and amends 004/006/015/017a; 071 rewrites the file). | high | D-5 (revised): the "plan-070 has landed" gate blocks 0.4 and 3.2, so the rewrite happens once, on top of 070's amendments; 039 has a destination in the merge map. If the operator chooses to run 071 first anyway, the gate fails loudly at execute start rather than at merge time. |
| R2 | **Web check ripple.** Deleting formulas and verbs changes counts that `check_web_counts`, `check_cli_to_page` and `check_required_set` compare; FAST/FULL go red mid-execution. | med | Issues 2.5 and 4.1 own the web-side edits in the same change. FULL runs once at 5.1 on the merged tree. |
| R3 | **D-10 deletes a subsystem someone intends to use.** The ci-release completion gate has a spec and tests; removing it on "never used" may be premature. | med | The decision is measured (Issue 4.2), reversible (git), and flagged for the red-team to challenge. If any bundle carries `ci-release`, nothing is deleted. |
| R4 | **INCONCLUSIVE-halts blocks landings of plans approved before this change** whose criteria are prose (plan-070 today: 0 of 15 evaluable). | low | Removed by ordering: the D-5 gate lands 070 through the unchanged chain before this plan deploys. `ready-check`'s mandatory grammar means no future plan reaches L11 in that state. Migrating 070's criteria instead would count as 15 post-approval flips under D-4. |
| R5 | **This plan lands through the installed (old) skill** — the three-artifacts rule. Its own reconcile gate is a #388 instance if poured before 070 lands. | med | Pour-time metadata is set by hand per the existing §5.2a snippet; if the gate is poured `human`, the operator resolves it. Redeploy only at land-the-plane. |
| R6 | **Test churn.** Deleting verbs removes tests that `CHANGE-VALIDATION.md` rows name; the FAST tier goes red on the deletion commit. | med | Each deletion issue edits the CV row in the same commit. Issue 4.6's check is added last, after the tree it measures exists. |
| R7 | **The freeze check is itself vacuous** — a caller-count check that matches prose mentions or enumeration lists certifies dead verbs as live/tested. | high | Invocation-form matching on both legs (`plan_manager.py <verb>` in argv or `CliRunner.invoke`, or the `LAND_*` tables), five negative controls, and the check reads its ceilings from the spec rather than a constant beside the code (#392 "derived not transcribed"). |
| R8 | **The metric is gamed by amending criteria before landing** so nothing "flips". | med | The diff is against the intake commit, so an amendment is exactly what is counted. A `manual:` conversion counts as a flip. |
| R9 | **Two reading passes are too few for a plan this size** and the execution pass has no reading judgement. | low | The execution pass still reads: it must re-verify prior resolutions and may raise `inferred:` findings at `medium` or below. #286 measured the opposite risk (manufactured concerns) as the live one. |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | The verb count did not grow and dead verbs are gone: at most 32 `@cli.command` registrations remain (41 at scoping − 6 dead − `audit-close` − `parked` − `judgement-never-fired-report` = 32, slack zero) | `test $(grep -c '@cli.command(' skills/yf-plan/scripts/plan_manager.py) -le 32` → exit 0 | 4.1, 4.3 |
| SC2 | The REQ-LAND set is pruned to at most 22 ids and `spec/landing.md` to at most 350 lines | `test $(grep -Eo 'REQ-LAND-[0-9]+[a-z]*' skills/yf-plan/spec/landing.md \| sort -u \| wc -l) -le 22 && test $(wc -l < skills/yf-plan/spec/landing.md) -le 350` → exit 0 | 0.4 |
| SC3 | No merged or deleted REQ-LAND id survives anywhere outside `spec/landing.md` (an invariant: green today, red between Issues 0.4 and 3.3, green after; `-I` and `--exclude-dir=__pycache__` because ugrep prints binary-match lines on stdout — pass-3 C1) | `test -z "$(comm -13 <(grep -Eo 'REQ-LAND-[0-9]+[a-z]*' skills/yf-plan/spec/landing.md \| sort -u) <(grep -rhoEI 'REQ-LAND-[0-9]+[a-z]*' skills/yf-plan SPEC.md --exclude-dir=formulas --exclude-dir=__pycache__ \| sort -u))"` → exit 0 | 3.1, 3.3 |
| SC4 | The unpoured review formulas are deleted | `ls skills/yf-plan/formulas/plan-review.formula.toml skills/yf-plan/formulas/verify-artifact.formula.toml` → exit 2 | 2.5 |
| SC5 | The red-team brief carries the execution-pass contract and a brief without it fails the contract test | `grep -q 'REQ-AGENT-066' skills/yf-plan/scripts/test_review_agent_contract.py && uv run skills/yf-plan/scripts/test_review_agent_contract.py` → exit 0 | 2.1, 2.3 |
| SC6 | `ready-check` refuses a prose criterion and an unrunnable command, and passes a clause-form plan | `uv run skills/yf-plan/scripts/test_ready_check_smoke.py` → exit 0 | 2.4 |
| SC7 | The `fidelity` retrospective kind is accepted with both numbers and refused without them | `grep -q 'fidelity' skills/yf-plan/scripts/test_retrospective.py && uv run skills/yf-plan/scripts/test_retrospective.py` → exit 0 | 1.1, 1.2 |
| SC8 | The baseline covers plans 060–070 with one row each | `test "$(grep -c '^\| plan-0[67][0-9]' docs/plans/plan-071-james-dixson-d19ce8/findings/fidelity-baseline.md 2>/dev/null \|\| echo 0)" -ge 11` → exit 0 | 1.3 |
| SC9 | This plan's own review had at most two reading passes and at least one execution pass (pass 3 is driven by an explicit brief because the installed red-team brief predates Issue 2.1; the dispatch prompt is recorded in `log.md`) | `test $(grep -l '^\*\*Mode:\*\* reading' docs/plans/plan-071-james-dixson-d19ce8/reviews/pass-*.md \| wc -l) -le 2 && test $(grep -l '^\*\*Mode:\*\* execution' docs/plans/plan-071-james-dixson-d19ce8/reviews/pass-*.md \| wc -l) -ge 1` → exit 0 | 2.1 |
| SC10 | L5's duplicate criteria run is gone and a halting verb's exit 2 halts the chain | `grep -c '_land_l5_advisory_recheck' skills/yf-plan/scripts/plan_manager.py` → exit 1 | 4.3 |
| SC11 | `gate_consistency.py` separates no-gates (PASS) from none-evaluable (INCONCLUSIVE), and the chain row is halting | `grep -q 'gate-consistency' skills/yf-plan/scripts/test_close_contract.py && uv run skills/yf-plan/scripts/test_gate_consistency.py && uv run skills/yf-plan/scripts/test_close_contract.py` → exit 0 | 4.4, 4.7 |
| SC12 | Every non-helper file under `scripts/checks/` is wired into CV, CI, a test, or a wired check | `for f in scripts/checks/[!_]*.py scripts/checks/[!_]*.sh; do b=$(basename "$f"); grep -rq "$b" CHANGE-VALIDATION.md .github skills/yf-plan/scripts/test_*.py scripts/checks/[!_]*.py scripts/checks/[!_]*.sh --exclude="$b" 2>/dev/null \|\| { echo "UNWIRED $b"; exit 1; }; done` → exit 0 | 4.5 |
| SC13 | The freeze check passes on this tree and fails on each of its four negative-control fixtures | `uv run scripts/checks/check-provably-necessary.py --self-test` → exit 0 | 4.6 |
| SC14 | The FULL validation tier is green on the merged tree | manual: FULL is multi-minute and would time out under `recheck-criteria`'s per-row bound (pass-1 C7); Issue 5.1 runs it and records `FULL tier: exit 0` in `log.md` | 5.1 |
| SC14b | Issue 5.1's FULL-tier evidence line exists | `grep -c 'FULL tier: exit 0' docs/plans/plan-071-james-dixson-d19ce8/log.md` → exit 0 | 5.1 |
| SC15 | The six dead verbs, `audit-close` and `judgement-never-fired-report` are gone from the registration set | `grep -cE '@cli.command\("(ownership-report\|escalation-report\|verify-beads\|index-add\|judgement-echo-check\|grant\|audit-close\|judgement-never-fired-report)"' skills/yf-plan/scripts/plan_manager.py` → exit 1 | 4.1, 4.3 |
| SC16 | SKILL.md §6.4, `LAND_CLOSE_CHAIN` and the rehearsal verb list agree, and a reordered SKILL.md line fails the contract test | `grep -q 'LAND_CLOSE_CHAIN' skills/yf-plan/scripts/test_close_contract.py && uv run skills/yf-plan/scripts/test_close_contract.py` → exit 0 | 4.7 |
| SC17 | Every REQ id named in Epic 0 carries an amendment-log bullet under this plan's entry, and every implementation issue reaches an Epic 0 REQ | `uv run scripts/check_amendment_log.py --plan plan-071-james-dixson-d19ce8` → exit 0 | 0.1, 0.2, 0.3, 0.4 |
| SC18 | SKILL.md Phase 3 describes the two-then-execute shape and the `Mode:` line | `test $(grep -c 'Mode:' skills/yf-plan/SKILL.md) -ge 2 && grep -q 'execution pass' skills/yf-plan/SKILL.md` → exit 0 | 2.2 |
| SC19 | The REQ-LAND-015 reader's relocated call site is recorded in the log | `grep -c 'REQ-LAND-015 branch:' docs/plans/plan-071-james-dixson-d19ce8/log.md` → exit 0 | 3.2 |
| SC20 | The D-10 corpus measurement and its outcome are recorded in the log | `grep -c 'D-10 measured:' docs/plans/plan-071-james-dixson-d19ce8/log.md` → exit 0 | 4.2 |
