---
type: Plan
okf_spec: OKF-PLAN
id: plan-051-james-dixson-2f499f
author: james-dixson
created: '2026-08-21'
status: review
---
# Plan: Land the descoped plan-050 work: the red-team sandbox-spike rule (#182), sub-agent dispatch for review (#184), and M9 remediation-edge attribution (#149) — each from plan-050's measured evidence

**ID:** plan-051-james-dixson-2f499f
**Author:** james-dixson
**Created:** 2026-08-21
**Status:** review

## Objective

Ship the **review contract** into the yf-plan skill, where it currently does not exist, and correct
one upstream issue whose premise this repo has already measured false.

Three pieces, in descending order of evidence:

1. **#184 — dispatch the red-team as a sub-agent.** `SKILL.md:315` (§2 INVESTIGATE) says **spawn**;
   `SKILL.md:489` (§3 REVIEW) says **perform**. Following §3 literally produces a main-session
   self-review — the drafter reviewing its own draft.
2. **#182 — authorize the sandbox spike.** `red-team.md:63` says only *"Read-only — never writes
   files"*. It never forbade a spike; the prohibition is a reasonable reading of silence. The defect
   is **under-specification**, which is why the fix is a clarification rather than a reversal.
3. **#149 — correct the record.** Comment only. exp-004 measured the issue's premise false and
   plan-050 never posted the correction.

**The policy is already ratified — it just does not ship.** `AGENTS.md` carries both halves and
this session exercised them hard. What is missing is the SPEC requirement and the skill text, so
every other consumer still gets the self-review.

Explicitly NOT in scope: M9 itself (#149's substance), the payload-fidelity group (#188/#190), the
corpus-wide `Verification:` sweep (#165 beyond this plan's own two REQs), and #145.

## Motivation

**A rule that lives in one repo's `AGENTS.md` is not a rule the skill has.** Every yf-plan consumer
outside this repository still runs `SKILL.md` §3 as written, which never dispatches. The drafter
reviews its own draft, and a concern the drafter cannot see is a concern the review cannot raise.

The evidence is first-party and unusually direct — plan-050 is the experiment. Its concerns per
review pass ran **5 → 4 → 11 → 17 → 14**, and the discontinuity lands exactly at pass 3, the first
`Agent`-dispatched pass. Passes 1-2 were main-session self-review and advanced the plan to
`ready-for-approval`; three independent passes then returned REVISE.

The spike half has its own instance: plan-050's pass-11 refuted the plan's "single call site" claim
about `plan_extract.py` **by building it**, and execution later confirmed both sites were corrupt.
Reading four passes had not found it.

**And the counter-evidence is recorded here rather than omitted.** Eleven independent red-team
passes found **none** of the three defects that *running a control* found during plan-050's
execution. Independent review is a large improvement over self-review; it is not the strongest lever
measured. This plan ships the improvement it has evidence for and does not overclaim it.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#184](https://github.com/dixson3/yoshiko-flow/issues/184) | red-team is never dispatched as a sub-agent — the drafter reviews its own draft | include | **D-2.** The §2-vs-§3 asymmetry is verbatim: `SKILL.md:315` says **spawn**, `:489` says **perform**. Measured RED: `Agent` appears **0** times across all 7 `agents/*.md`. Needs a **NEW** `REQ-AGENT-*` — none of 040-048 says who RUNS the review | 2.2 |
| [#182](https://github.com/dixson3/yoshiko-flow/issues/182) | the read-only rule forbids the sandbox spike that catches specification defects | include | **D-1.** exp-006 **narrows** this issue: `red-team.md:63` says only "never writes files" — it never forbade a spike. Under-specification, not a wrong rule. One line, **plus `spec/agents.md:73`**, whose Verification clause pins the exact string | 1.2, 1.2a |
| [#149](https://github.com/dixson3/yoshiko-flow/issues/149) | M5/M9: process rules that nothing executes, and remediation edges that exist only in prose | partial | **D-3.** **IN:** a comment correcting the refuted premise — **26** `discovered-from` edges, **0** attributed on either endpoint, so the relationship exists and only attribution is missing; plus C40 and the no-seam finding. **OUT:** M9 itself | 4.2 |
| [#165](https://github.com/dixson3/yoshiko-flow/issues/165) | SPEC `Verification:` lines are prose shaped like commands | partial | **D-4.** **IN:** this plan's own new/amended `Verification:` lines must be **executable**. **OUT:** the corpus-wide sweep. Folded in because otherwise this plan ships two requirements nothing executes — the exact M5 defect it exists to fix | 3.2 |
| [#173](https://github.com/dixson3/yoshiko-flow/issues/173) | criteria and dispositions are never checked against the engine that enforces them | partial | #182's and #184's REQs are checked against the surface that enforces them, as worked instances. The general cross-check stays open | 4.2 |
| [#174](https://github.com/dixson3/yoshiko-flow/issues/174) | a review-phase validation pass — falsify every criterion | partial | #182 closes a named sub-case: the spike is the technique that catches what reading cannot. The general falsification pass stays open | 4.2 |
| [#150](https://github.com/dixson3/yoshiko-flow/issues/150) | research 004: process-defect mining across 83 plan bundles | partial | **IN:** two more ranked classes delivered as worked instances. **OUT:** M9, the M11 probe mechanism, the remaining classes | 4.2 |
| [#177](https://github.com/dixson3/yoshiko-flow/issues/177) | no check that a numeric target is derivable from the plan's own scope rules | exclude | plan-050 posted the refutation comment and dropped it on evidence (**plan-050's** D-6, not this plan's). The issue remains **OPEN** upstream — verified — and `exclude` requires no upstream action, so it is out of scope here rather than closed (pass-1 C14) | |
| [#188](https://github.com/dixson3/yoshiko-flow/issues/188) | test suites assert output STRUCTURE and never payload FIDELITY | deferred | plan-050's headline finding is direct evidence, but payload fidelity is a second independent axis, scoped OUT | |
| [#190](https://github.com/dixson3/yoshiko-flow/issues/190) | require plans to ship tests at >= 80% coverage of code they write | deferred | Same axis as #188 — deferred with it | |
| [#145](https://github.com/dixson3/yoshiko-flow/issues/145) | New skill: yf-retrospective — measure escape rate | deferred | Own plan. The emit side accumulates; a consumer built now reads a thin corpus | |

## Investigation Findings

Five experiments returned. **Two refuted parts of the approach hypothesis and one refuted a decision
this plan was about to inherit.** Full records in `findings/`.

| # | Question | Outcome |
| :-- | :-- | :-- |
| [EXP-001](findings/exp-001-dispatch-verification.md) | What can #184's `Verification:` line assert with an exit code? | **The behavioral claim has none, and cannot.** But `spec/agents.md` has **0 of 26** exit-code-decidable clauses today, and #184 has a real substrate the plan can use |
| [EXP-002](findings/exp-002-182-blast-radius.md) | What is #182's complete edit set? | **exp-006's "one line in one file" is wrong by ~7x** — 7 files minimum, 8 with the reviewer sibling. And the FAST tier passes green on the broken intermediate state |
| [EXP-003](findings/exp-003-executable-verification.md) | Does any SPEC `Verification:` line execute today? | **Yes — 1 of 251.** Prior art exists and is green, so #165 stays in scope. The "no prior art → drop it" branch is refuted |
| [EXP-004](findings/exp-004-redcheck-reuse.md) | Can plan-050's control harness be reused, and is a control possible? | **Reuse as-is, and a control is possible for ALL THREE subjects** — which **refutes plan-050's D-8** as written |
| [EXP-005](findings/exp-005-review-wisp.md) | Is a `plan-review` **wisp** buildable without `waits-for`, and is parallelism evidenced? | **BUILDABLE** (spiked and driven — `needs` is an array compiling to `blocks`), but **NO EVIDENCE** for parallel lenses. Ships **sequencing-only**; see D-7 |

### The five results that change the plan

**1. D-8 is wrong about the edit set, and this plan must not inherit it verbatim.** plan-050's D-8
says #182's fix *"has no exit code and cannot have one."* EXP-004 built the control and ran a
**half-fix arm**: editing `red-team.md:63` alone **breaks** `spec/agents.md:73`, whose `Verification:`
clause pins the literal string — and the fixture catches it with exit 1. D-8 is right about
*behaviour* (no exit code for "a reviewer obeyed a rule") and wrong about *edit-set completeness*.
Carried verbatim, this plan would under-claim and skip a control it can build. **See D-1.**

**2. #182's blast radius is 7 files, and mostly invisible to automation.** EXP-002's spike measured
the decisive case: with `red-team.md` reworded and `spec/agents.md:73` still pinning a string that no
longer exists (`grep -c` → **0**), the FAST tier returns **pass, first_failure None**. FULL is the
same command set, so it does too. Three of the twelve edit steps have **nothing mechanical** behind
them. There is also **no `spec → agent` edge** in `DRIFT-CHECK.md` at all — the same class pass-4's
C24 flagged on plan-050.

**3. Executable-`Verification:` prior art exists — 1 of 251 clauses.** `REQ-CLI-006` /
`test_cli_enumeration.py` is green in 0.02s, wired at `CHANGE-VALIDATION.md:80` with §3 globs on
**both** the script and the spec file. Two further instances sit on the agent-prose axis this plan
needs, one of them (`test_gates.py:349`) already asserting prose in `red-team.md` — the very file
#182 changes. **This plan follows a three-instance precedent; it invents nothing.**

**4. #165's class claim is confirmed by execution, and is larger than this plan.** Ten literal
Verification commands were hand-run; **two are false today in a FULL-tier-green tree** — a stale
`skills/optimal-instructions/` path and a stale `.agents/skills/` path. Those go to #165 as evidence,
not into this plan's scope.

### Re-measured figures (D-5)

| Figure | Value | Note |
| :-- | --: | :-- |
| Exit-code-decidable `Verification:` clauses in `spec/agents.md` | **0 of 26** | the one clause carrying a command exits 0 with a match |
| `Verification:` clauses corpus-wide / of those, executed | **251 / 1** | 0.4% |
| Files in #182's minimum consistent edit set | **7** | 8 including the `reviewer.md` sibling |
| Sites carrying the literal `Read-only — never writes files` | **4** | `red-team.md:63`, **`agents/reviewer.md:43`**, `spec/agents.md:73`, `spec/agents.md:97`. Corrected at pass 1: the drafting figure said 3 and omitted `reviewer.md:43`, which carries the identical sentence — the stale-literal class **D-5 exists to prevent, occurring inside D-5's own table** (pass-1 C9) |
| `Agent` occurrences across all 7 `agents/*.md` | **0** | #184's RED |
| Free `REQ-AGENT-*` ids | **049, 052-059** | `050`, `051`, `060`-`064` are taken |
| Harness roots deployed on this machine | **2** | `~/.claude`, `~/.agents`; codex/opencode/pi absent |
| `gate-run.sh` copies in the corpus, materially drifted | **3** | plan-048, -049, -050 |

### The beads-capability reconciliation (cross-session, VERIFIED not accepted)

A parallel session reconciled `bd` 1.1.2's surface against yf-plan's usage. **Its structural finding
holds and two of its named primitives do not exist.** Re-verified here against the installed `bd`:

| Claim | Verdict |
| :-- | :-- |
| Phase 3 has **no bead representation** — Phase 2 is a wisp, Phase 5 a pour, Phase 3 a prose loop | **TRUE.** Only two formulas ship: `plan-investigate`, `plan-execute` |
| `bd cook --dry-run` / `--mode=compile` previews a resolved DAG | **TRUE.** `--dry-run` exists; `--mode=compile` is the **default** |
| `mol bond` / `squash` / `progress` are unused in every skill | **TRUE** — 0 hits (`mol distill` has 2 prose hits, not 0) |
| **`waits-for` dep type** (the proposed join) | **DOES NOT EXIST** |
| **`conditional-blocks` dep type** | **DOES NOT EXIST** |

`bd dep add --type` accepts exactly `blocks, tracks, related, parent-child, discovered-from, until,
caused-by, validates, relates-to, supersedes`. **EXP-005 answered this by building it**: the formula schema's `needs` is an **array**, multi-parent
fan-in is first-class, and a poured wisp held `join` un-ready until all three arms closed. `waits-for`
would have been a synonym for the multi-parent `blocks` set. Measured separately: `until` and
`validates` do **not** gate readiness, so neither is the join under another name.

**One argument corrected.** The recommendation claims parallel fan-out *"is the substance of #184"*,
citing plan-050's 5 → 4 → 11 → 17 → 14 concerns-per-pass. That series measures **independence**, not
**parallelism** — all eleven passes were sequential and single-reviewer. It is the same shape as
plan-050's resolution-vs-review conflation: a real result read as support for an adjacent claim it
does not test. EXP-005 tested the parallel claim on its own evidence and found **none** — 29 review passes across
four plans, **all sequential, one reviewer each**. The parallel-lens dimension is declined (D-7).

### NON-GOAL — the review-cycle counter stays in FILES

**Recorded as an explicit non-goal so a later cycle does not "simplify" it back in.** The bound is
`len(glob('reviews/pass-*.md'))`, deliberately file-based and **monotonic** (REQ-PLAN-030;
REQ-PORT-006's count-equality against `log.md`'s `review-pass:` bullets). A wisp is **ephemeral and
burnable** — moving the bound inside one makes it **resettable by `bd mol burn`**, restoring exactly
the unbounded self-resolving loop D-8 forbids. If any wisp ships, it orchestrates **dispatch only**;
the file remains the ledger.

Also non-goals, filed upstream for a later plan rather than scoped here: modelling plan drafting as a
molecule (it is conversational — beads are pure overhead); `bd mol bond` for plan-to-plan chaining
(`handoff-051.md` is generated with a `--check` regeneration diff that exits 1, already stronger than
a bond edge); and `mol distill` / formula aspects.

### Two defects found by the experiments, both out of scope

- **`change_validation.py:946`** declares `--changed` with `nargs="*"` and **no** `action="append"`,
  so `--changed A --changed B` silently validates only `B`. **Confirmed at source**, not taken on
  report. A validation-coverage hole affecting every caller. → file upstream.
- The two false `Verification:` commands above. → evidence on #165.

## Approach

**SPEC-first, control-first, then the edit set.** Every behaviour change lands its `REQ-*` before its
implementation (AGENTS.md), and every control is observed **RED before its fix** and GREEN after —
the harness is copied byte-for-byte from plan-050 rather than rebuilt (EXP-004).

The plan is four epics plus reconciliation. Epics 1-3 are independent of each other **up to the shared red-prework gate** — all depend on Epic 0,
and the gate's Condition spans all three controls and Blocks 1.4, 2.4 and 3.4, so no epic *completes*
until every control is green (pass-1 C17).

### Decisions

| # | Decision | Basis |
| :-- | :-- | :-- |
| D-1 | **#182 is a clarification, not a reversal.** `red-team.md:63` never forbade a spike; the prohibition is a reading of silence | EXP-006 (plan-050), re-verified in EXP-002 |
| D-2 | **#184 needs a NEW `REQ-AGENT-*`, not an amendment.** No existing REQ says who RUNS the review | EXP-001: `REQ-AGENT-020` is the *investigator*; grep for dispatch on the review axis returns nothing |
| D-3 | **#149 gets a correcting comment only.** M9 itself stays out | exp-004 (plan-050) refuted the premise; EXP-002-adjacent measurement found no script seam |
| D-4 | **#165 is scoped to THIS plan's own two REQs.** The corpus-wide sweep stays #165's | EXP-003: 251 clauses, 1 executed — the class is far larger than this plan |
| D-5 | **Re-measure every inherited figure.** No literal is cited from plan-050 without re-measurement | plan-048 D-5, plan-049 D-7, plan-050 D-5 each caught a stale inherited literal at execution |
| D-6 | **plan-050's D-8 is NARROWED, not inherited and not dropped.** It says #182's fix *"cannot have an exit code"*; measured, it can — on **edit-set completeness**. It cannot on **reviewer obedience** | EXP-004's half-fix arm: editing `red-team.md:63` alone breaks `spec/agents.md:73` and the fixture exits 1 |
| D-7 | **The `plan-review` wisp ships for SEQUENCING ONLY. Arms stay sequential.** The parallel-lens dimension is declined | EXP-005: buildable (spiked), but zero evidence — 29 passes across 4 plans, none concurrent — and fan-out would break the chain property that produced most of plan-050's yield |
| D-8 | **`reviewer.md:43` IS in scope.** It carries the identical literal, pinned by REQ-AGENT-045 | EXP-002/EXP-004: rewording only red-team leaves the two agents contradicting each other on one constraint, and `AGENTS.md` says *"reviewers"* plural |
| D-9 | **A new `DRIFT-CHECK.md` edge `e-spec-agent` ships here**, not as a follow-on | EXP-002 measured **no `spec → agent` edge exists at all**, which is why FAST passes green on the dangling state. It is the systemic fix behind the single riskiest edit step |

### Non-goals, stated so a later cycle does not re-add them

- **The review-cycle counter stays in FILES.** `len(glob('reviews/pass-*.md'))`, monotonic
  (REQ-PLAN-030 / REQ-PORT-006). A wisp is burnable, so a counter inside one is **resettable by
  `bd mol burn`** — the unbounded self-resolving loop D-8 (plan-050) forbids. The wisp orchestrates
  dispatch; the file remains the ledger.
- **No parallel review lenses** (D-7). **No molecule for plan drafting** — it is conversational.
  **No `bd mol bond` for plan chaining** — `handoff-NNN.md`'s `--check` regeneration diff already
  exits 1, a stronger guarantee than a bond edge would be.
- **M9 itself, the payload-fidelity group (#188/#190), and #165's corpus sweep.**

## Epics

<!-- Epic numbering is 0..4 and contiguous. Issue ids use the `N.M[a-z]` insertable form so a
     later revision never renumbers — renumbering is this corpus's top recurring defect class. -->

### Epic 0: SPEC-first, and the control harness
- Issue 0.1: Land the `REQ-*` requirements for every behaviour change here, **before any implementation issue starts** (AGENTS.md SPEC-first). **ONE new id — `REQ-AGENT-049` (the red-team is DISPATCHED as a sub-agent)** — plus **amendments** to `REQ-AGENT-043` (scope read-only to *the repository under review*; authorize the sandbox spike) and `REQ-AGENT-045` (the same carve-out for `reviewer.md`, per D-8). Use `049` specifically: measured, `050`, `051` and `060`-`064` are already taken and a spike arm silently picked up the pre-existing `050` and reported a false RED. **A second reservation (`052`) was dropped at pass 1**: it was carried over from EXP-004's recommendation, written before **D-1** narrowed #182 to an *amendment* of `043`/`045`, so there is no third behaviour change needing an id. An id with no stated requirement is a criterion satisfiable while its substance is absent — the defect class this plan exists to close, inside its own SPEC-first epic (pass-1 C1). **Each REQ's `Verification:` line must take ONE target shape, specified here because Epics 1 and 3 otherwise demand incompatible ones** (pass-2 C22): a **whole-line backticked command whose ARGUMENTS are the double-quoted agent-file literals** — e.g. `` `grep -qF "<new phrase>" skills/yf-plan/agents/red-team.md && grep -qF "<new phrase>" skills/yf-plan/agents/reviewer.md` ``. That single shape is executable (Epic 3 / #165) **and** carries quoted fragments naming a file, which is what `ctl-182-spike`'s conjunct (b) checks. Measured at pass 2: a bare `` `uv run …test_*.py` `` line contains **no** quoted fragments, so conjunct (b) reports `fragments-checked=0` and exits **0 on the dangling tree** — the state it exists to catch. Do not write a prose line intending to fix it later; that is the M5 defect this plan exists to close. **0.1 OWNS the `Verification:` retarget for `043`/`045`; `red-team.md`/`reviewer.md` are reworded at 1.2/1.2a, so those commands are RED from 0.1 until 1.2a lands the new phrases — that is the intended SPEC-first order, not a defect** (pass-3 C30). Nothing else may rewrite those lines. Also add the **root** `SPEC.md` amendment-log entry (precedent: root `SPEC.md:264`). **Every `SPEC.md` citation in this plan is path-qualified** — root and `skills/yf-plan/` are different files and both are edited here (pass-1 C18).
- Issue 0.2: Copy `redcheck.sh` and `gate-run.sh` **byte-for-byte** from plan-050's `assets/` into this bundle's `assets/`, changing only the header comment line — the same way plan-050 took `gate-run.sh` from plan-049. **Re-spike the copied harness into `assets/` before first use** and record it: plan-050's RE-005 documents that `redcheck.sh` once reported *"RED observed"* with **exit 0** for a MISSING fixture, and that this was caught only by self-spiking before use. EXP-004 confirms the fix is in the shipped script, but 0.2's own portability argument — a cold reader must re-run the evidence from the bundle alone — applies to the harness's trustworthiness too. Do **not** rebuild and do **not** promote to `_shared/` (EXP-004: the portability contract requires a cold reader in a *different repo* to re-run the evidence from the bundle alone). **Write `assets/controls.txt` with exactly three ids: `ctl-182-spike`, `ctl-184-dispatch`, `ctl-165-executable`.** **Tighten `verify-all`'s count derivation to `grep -oE 'ctl-(165|182|184)-[a-z-]+'`** — the inherited generic pattern is contaminated by any prose naming another plan's control ids, which EXP-004 measured wedging the gate at 7-declared-vs-1-manifest. State the tightened pattern verbatim in this issue: an executor copies whatever the issue prints. **Measured at pass 1, both patterns currently derive 3 against a 3-line manifest** — the tightening is insurance, not a live fix, and R6's 7-vs-1 figure was EXP-004's synthetic arm, not this bundle. Note the opposite failure mode: a control for an issue number outside {165, 182, 184} becomes **invisible** to the derivation, so adding one requires widening the pattern (pass-1 C16).
  - depends-on: 0.1
- Issue 0.3: Record the pre-fix baseline into `assets/`: `grep -c 'Agent'` over all 7 `agents/*.md` (expect **0**), the **four** sites carrying the literal `Read-only — never writes files` (`red-team.md:63`, `reviewer.md:43`, `spec/agents.md:73`, `:97`) — re-grep rather than copying this list, and the corpus `Verification:` census **recorded with its VERBATIM PATHSPEC** so the figure is reproducible — a pass-3 reconstruction returned **257** against `plan.md`'s drafting literal of 251, and EXP-003 never recorded its pathspec, so the difference is unresolvable rather than wrong (pass-3 C34). 4.2 quotes THIS record, never the drafting literal. Re-measure per D-5 rather than citing this plan's own drafting figures.
  - depends-on: 0.1

### Epic 1: The sandbox-spike rule (#182)
- Issue 1.1: Author the fixture `ctl-182-spike` with **two conjuncts** — (a) `red-team.md` authorizes a spike, and (b) **for each `grep -qF "<literal>" <path>` pair in `REQ-AGENT-043`'s retargeted `Verification:` line, `<literal>` occurs in `<path>`**. The pairing is positional and mechanical — no prose parsing, no fragment→file inference, no ellipsis handling. **The ellipsis rule, the printed `writes.*?at presentation` pattern and the fragment→file table are all DELETED** (pass-3 C30): they described the *pre-fix prose* shape of that line, which 0.1 has already replaced with the command shape, so authoring against them targets a state the DAG destroys before 1.1 runs. Three prior spikes measured every prose-shape reading as broken — literal-vs-regex (pass 1), whitespace (pass 2), and ownership (pass 3, which measured 1/1/1 under two readings and a false RED under the third). **Self-check before recording RED:** assert each `<literal>` returns >=1 against a hand-fixed copy of its `<path>`; a literal that matches nothing anywhere makes the RED false. **Stated redundancy:** under the command shape conjunct (b) is equivalent to *running* the command, i.e. to `ctl-165-executable`'s assertion for `043`. That is acceptable and 3.1 books it — but it is said here rather than discovered at execution. Conjunct (b) is the substance: EXP-002's spike measured the FAST tier returning `pass, first_failure None` on the dangling state where `red-team.md` was reworded and the spec still pinned the old string. **Run `redcheck.sh record-red <fixture> ctl-182-spike` against the unfixed tree; this issue PRODUCES that record.**
  - depends-on: 0.2
- Issue 1.2: Apply the **7-file edit set**, SPEC-first: `spec/agents.md` (REQ **text** and `Rationale:` carrying the plan-049 provenance — **NOT** the `Verification:` line, which 0.1 owns; pass-3 C30), then `red-team.md:63`, `SKILL.md:486` and **`:516`** (`The agent never writes files` is over-broad against the amended REQ), **`skills/yf-plan/SPEC.md`**`:65`/**`:389-390` (GR-PLAN-002)**, `web/content/skills/yf-plan.md:34`, `web/content/pages/workflows.md:172`, `web/content/pages/glossary.md:90`. **Two further sites are named with an explicit NO-EDIT disposition** so the enumeration is complete rather than silently narrowed (pass-1 C15): `workflows.md:180` (the red-team row's `Read-only? Yes` column), **`workflows.md:179` (the reviewer row's same column)** and `workflows.md:64` (*"Review is two ordered read-only passes"*) — both stay true under the amended REQ, since read-only **with respect to the repository** still holds. **Write the ordered edit list into `assets/edit-set-182.md`**, one row per site with *what catches a miss*, and mark the unmechanized rows inline. EXP-002 **recommended** such a list but does not contain one, so an index into it resolves to nothing (pass-1 C3). Three sites have **nothing mechanical** behind them — `spec/agents.md`'s retargeted `Verification:` (EXP-002 measured FAST returning `pass` on the dangling state) and the two `web/content/pages/*` restatements, which are not DRIFT-CHECK nodes and carry no CV row. Name those three in the file rather than by index. Use the portable core of `AGENTS.md:78-80`, **not** its verbatim text: the plan-049 anecdote does not travel to a foreign vault and belongs in `Rationale:`, and *"reviewers **and investigators**"* is wrong here since the investigator already gets a disposable worktree.
  - depends-on: 1.1
  - resolves-upstream: #182 (include)
- Issue 1.2a: Apply the same carve-out to `agents/reviewer.md:43` and `REQ-AGENT-045` (`spec/agents.md:95/97`), per **D-8**. `ctl-182-spike`'s conjunct (b) generalizes to it for free. **Ownership boundary (pass-3 C35):** the shared restatements — `workflows.md:172`, `skills/yf-plan/SPEC.md:65`, `web/content/skills/yf-plan.md:34` — cover *both* agents and are edited at **1.2**; 1.2a adds only `agents/reviewer.md:43` and `spec/agents.md:95/97`. **Then run `redcheck.sh assert-distinguishes <fixture> ctl-182-spike` against the fixed tree and record the zero observation** — this issue PRODUCES that record. Without it the capability gate's Condition names an observation no issue makes, so `verify-all` can only ever exit 1 and SC2b is undischargeable (conformance Gap 1).
  - depends-on: 1.2
- Issue 1.3: Add the `DRIFT-CHECK.md` edge **`e-spec-agent`** (`spec` → `agent`, contract): *every `REQ-AGENT-*` `Verification:` clause quoting a literal from an `agents/*.md` file resolves to a string present in that file.* Per **D-9** this is the systemic fix behind 1.2's step 3 — EXP-002 measured that **no `spec → agent` edge exists at all**, which is why the dangling state is invisible.
  - depends-on: 1.2
- Issue 1.4: **Verify** — assert `assets/red-prework.md` contains both records for `ctl-182-spike`. Reads the file; runs no `redcheck.sh` verb.
  - depends-on: 1.2a, 1.3

### Epic 2: Sub-agent dispatch (#184)
- Issue 2.1: Author the fixture `ctl-184-dispatch` — the **`### Review` section** of `SKILL.md` names `` `Agent` ``. **Section-scoped, never whole-file**: measured, `grep -q 'Agent' SKILL.md` exits **0 today** on the un-fixed tree because `Agent` appears at `:21` in the frontmatter `allowed-tools:` list, so the whole-file form ships unable to fail. **Run `redcheck.sh record-red <fixture> ctl-184-dispatch`; this issue PRODUCES that record.**
  - depends-on: 0.2
- Issue 2.2: Rewrite `SKILL.md` §3 step 2 to **dispatch** the red-team via `Agent`, mirroring §2's `Spawn a sub-agent …` form at `:315`, and land `REQ-AGENT-049`'s text. Keep §3's *"Two passes, in order"* — the conformance→adversarial ordering is unchanged; what changes is who runs the adversarial pass. **Then run `redcheck.sh assert-distinguishes <fixture> ctl-184-dispatch` against the fixed tree and record the zero observation** — this issue PRODUCES that record. It lives HERE, not in 2.3: 2.3's deliverable is the wisp, which R4 concedes the plan did not need, so attaching a gate producer to it would let a descope silently wedge the gate (pass-1 C10).
  - depends-on: 2.1
  - resolves-upstream: #184 (include)
- Issue 2.3: Ship `skills/yf-plan/formulas/plan-review.formula.toml` — the Phase-3 wisp, giving the review loop the bead representation it is the only phase to lack. **Arms stay SEQUENTIAL (D-7):** conformance → red-team → resolve → gate, one reviewer per cycle, preserving the chain property in which each pass verifies the previous pass's resolutions. `needs` is an array and multi-parent fan-in works (EXP-005 drove it), but this plan **does not use fan-out**. **The counter does NOT move into the wisp** — see Non-goals. Scripted `bd mol burn` **must pass `--force` and must check output, not the exit code**: measured, a cancelled burn on a wisp with an open APPROVE gate exits **0**.
  - depends-on: 2.2
- Issue 2.4: **Verify** — assert `assets/red-prework.md` contains both records for `ctl-184-dispatch`.
  - depends-on: 2.3

### Epic 3: Executable `Verification:` lines (#165, narrow)
- Issue 3.1: Author the fixture `ctl-165-executable` — each of `REQ-AGENT-049`, `REQ-AGENT-043` and `REQ-AGENT-045` has a `Verification:` line that is a whole-line backticked command **and that command exits 0 from the tree root**. (`052` was dropped at pass 1 — see 0.1.) **Run `redcheck.sh record-red <fixture> ctl-165-executable`; this issue PRODUCES that record.** Note the **redundancy caveat**: if the two REQs' Verification lines *are* Epic 1's and Epic 2's assertions, this control green ⟺ those two green, adding only the meta-property *"the line parses as a command"*. That is a real assertion — it is precisely the M5 defect #165 names — but it is **not independent evidence** and the plan does not present it as such. **Second honesty note (pass-1 C19):** at 3.1 the RED has **two independent causes**, not one: the named test does not exist yet, **and** the retargeted `043`/`045` commands grep for phrases `red-team.md`/`reviewer.md` do not carry until 1.2/1.2a, so they exit **1**. An earlier draft claimed the command conjunct was "already green" and the RED came *solely* from the missing test — measured false at pass 3, and in the plan's own favour, which is the direction that matters (pass-3 C33). The real limitation stands: because 0.1 already fixes the line's shape, this control never observes the *"prose shaped like a command"* defect #165 names. Record that in `red-prework.md` alongside the observation rather than letting the record imply otherwise.
  - depends-on: 0.2
- Issue 3.2: Write the pytest and register it — **ONE parameterized test with one case per REQ in {`REQ-AGENT-049`, `REQ-AGENT-043`, `REQ-AGENT-045`}**, spanning both agent files, and a vacuity guard asserting the **case set equals that set** (a set assertion, per 3.3's own never-a-count rule). SC8 requires three REQs across two files; a singular test would discharge it while covering one (pass-2 C25). Follow `uv-yf-cli-enum` / `test_cli_enumeration.py` **verbatim as the template** (EXP-003: the only one of 251 clauses that closes the loop). Three parts, all required: assert the agent-template prose property the REQ declares; assert the REQ id exists in the spec **and that its `Verification:` line names this test** (the meta-assertion that makes it non-rottable); and carry a **vacuity guard** so a spec reshape fails loudly instead of silently checking nothing. **Naming a `test_*.py` in a Verification line is NOT execution** — 30 clauses already do that and it buys nothing mechanically.
  - depends-on: 3.1, 1.2a
  - resolves-upstream: #165 (partial)
- Issue 3.3: Add the `CHANGE-VALIDATION.md` §1 `fast` row and §3 glob rows on **both** `skills/yf-plan/spec/agents.md` and `skills/yf-plan/agents/*.md`, so amending either side without the other is a hard failure at the point of change. Both globs already exist in §3. **Word every REQ as a set/property assertion, never a count** — `REQ-CLI-006` drifted three times as a count and zero times as a set equality. **Then run `redcheck.sh assert-distinguishes <fixture> ctl-165-executable` against the fixed tree and record the zero observation** — this issue PRODUCES that record.
  - depends-on: 3.2
- Issue 3.4: **Verify** — assert `assets/red-prework.md` contains both records for `ctl-165-executable`.
  - depends-on: 3.3

### Epic 4: Reconcile and land
- Issue 4.1: Run the FULL validation tier over the **merged** tree and record the result. **Then RE-RUN all three fixtures against the merged tree and assert each exits 0.** The red→green records are evidence of a *transition*, written once and never re-evaluated: `verify-all` reads `red-prework.md`, the fixtures are not CV recipe rows, and the FULL tier does not touch them — so a later epic can silently undo an earlier one's green with nothing detecting it (pass-2, Missing). This is the end-state check the transition records cannot be. **Invoke it as `uv run skills/yf-plan/scripts/plan_manager.py validate-merged <plan_dir> --json`, and do NOT pass `--changed`** — measured at source, `change_validation.py:820` gates `--changed` on `tier == "fast"`, and `plan_manager.py:3529` hard-codes the FULL invocation with no `--changed` at all, so the flag cannot reach this run (pass-3 C31). The repeated-flag defect is real and stays filed at 4.6; it affects no invocation this plan makes.
  - depends-on: 1.4, 2.4, 3.4
- Issue 4.2: Draft the upstream comments **from the grant verb's enumeration**, not from a prose list. The #149 comment carries the **corrected premise** (26 `discovered-from` edges, 0 attributed on either endpoint — the relationship exists, only attribution is missing), plus C40 and the **no-seam** finding. The #165 comment carries the census **as recorded by 0.3, not the drafting literal** (pass-3 C34): a reconstruction at pass 3 returned **257** rather than `plan.md`'s 251, and since EXP-003 never recorded its exact pathspec the difference is unresolvable — which is precisely what D-5 forbids shipping. 0.3 records the figure **with its verbatim pathspec** so it is reproducible; 4.2 quotes 0.3 and the **two measured-false Verification commands** as evidence. **The two `include` rows get CLOSING comments too** (pass-2 C23): #182's must state that **D-1 narrowed the issue rather than accepting its framing** — the issue body claims the rule is drawn as *"never write, edit, or create any file"*, which the tree does not say — and #184's records the measured RED. Pass 1 said that correction *"must reach the closing comment, not just the plan"*, and it was wired to nothing. **All FIVE `partial` rows get a comment — #149, #165, #173, #174 and #150** — because `plan_manager.py`'s `_verify_row` maps `partial` → `requires_mention: True` and returns `fail: "no comment mentions <plan_id>"` otherwise, and `verify-reconcile` runs at 4.4, i.e. **after** the outward writes have begun (pass-1 C4; the code's docstring records this exact failure from plan-048/#172). #173 and #174 record which named sub-case this plan closed and what stays open; #150 records the two ranked classes delivered. **Reconcile `grant`'s enumeration against the Upstream Issues table BEFORE the gate is presented**, so a missing row is caught while it is still cheap.
  - depends-on: 4.1
- Issue 4.3: File the coarse tracker through `/yf-beads-upstream` so the epic carries it as `external_ref` — a tracker filed with a bare `gh issue create` is invisible to `upstream.py closable`, which is how five earlier trackers went stale.
  - depends-on: 4.2
- Issue 4.4: Post the comments and close the `include` rows, **after** the Upstream-write gate resolves. Verify each write structurally — a returned URL on create, a clean exit on edit, `gh issue view` confirming end state. An exit 0 is not proof.
  - depends-on: 4.3
- Issue 4.5: Generate `references/handoff-052.md` from this plan's own tables with a `--check` regeneration diff that exits 1 on drift. A typed list does not discharge it.
  - depends-on: 4.4
- Issue 4.6: File the two out-of-scope defects upstream: `change_validation.py`'s `--changed` repeated-flag drop, and `bd mol burn`'s **exit-0-on-cancel** with an open gate.
  - depends-on: 4.4
- Issue 4.7: Deploy at land-the-plane — `yf self install --from-build --build`, then assert `yf --version` hash equals HEAD. Never mid-execution.
  - depends-on: 4.5, 4.6

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: red-prework recorded
- Type: auto
- Condition: every control in `assets/controls.txt` has BOTH a `record-red` observation with a non-zero exit and an `assert-distinguishes` observation with a zero exit, and the manifest's line count equals the number of control ids this plan declares
- Test: bash docs/plans/plan-051-james-dixson-2f499f/assets/gate-run.sh docs/plans/plan-051-james-dixson-2f499f/assets/redcheck.sh verify-all
- Blocks: 1.4, 2.4, 3.4
- Instructions: exit 0 = all controls distinguished. Exit 1 = at least one control lacks a record — read `assets/red-prework.md` and re-run the missing verb; do NOT hand-write a record. Exit 2 = INCONCLUSIVE, the harness could not run (missing fixture, missing script) — repair the harness, which leaves the gate UNRESOLVED rather than failed. No engine executes this Test automatically; the coordinator runs it at the gate.

### Capability Gate: Upstream write
- Type: human
- Approvers: operator
- Condition: the operator has authorized the upstream comments, the tracker creation, and the closes, against a grant generated by `plan_manager.py grant` rather than hand-derived
- Test: test -f docs/plans/plan-051-james-dixson-2f499f/assets/upstream-authorization.txt
- Blocks: 4.3, 4.4
- Instructions: generate the grant, present it in full (every issue number, every comment body verbatim, every close and its reason), then ask. Record the authorization to `assets/upstream-authorization.txt`. A green test can never substitute for consent — this gate is `human` and is never auto-resolved.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Condition: every non-gate execution bead under this plan's epic is closed
- Test: bd list --all --include-gates --json | jq -e '[.[]|select(.metadata.plan=="plan-051-james-dixson-2f499f" and .issue_type!="gate" and .status!="closed")]|length==0'
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **The #182 edit set is enumerated by hand and three of its steps have no mechanical check.** A missed restatement ships a tree that contradicts itself and passes every gate | high | `ctl-182-spike`'s conjunct (b) covers the spec↔prose pin — the one EXP-002 proved FAST misses. **Issue 3.3's `CHANGE-VALIDATION.md` `fast` row is the MECHANICAL closure**; D-9's `e-spec-agent` edge is the prose-agreement **backstop**, not the gate — `yf-drift-check` has no runnable command and is never a CV recipe row, so a declared edge executes nothing (pass-1 C7). The two `web/content/pages/*` sites remain hand-enumerated and are named individually in 1.2 rather than left to a glob |
| R2 | **A text-presence control is gameable by the token it checks for.** `ctl-184-dispatch` is satisfied by a comment or a prohibition containing the word `Agent` | med | Stated plainly in 2.1 and in `REQ-AGENT-049`'s honesty clause rather than papered over. The control's value is that it is currently **RED**, so it distinguishes before/after; it is not claimed to verify conduct |
| R3 | **The plan asserts a behavioural claim no exit code can reach.** "The red-team was dispatched" is not mechanically observable | med | D-6 narrows plan-050's D-8 rather than repeating or dropping it: the controls certify the **edit set**, never reviewer obedience. Candidate provenance mechanisms were evaluated and rejected with reasons — a frontmatter key is self-attestation, transcript mining fails ~half the existing corpus and is harness-local |
| R4 | **The `plan-review` wisp is new machinery in a plan that did not need it**, and a burnable wisp adjacent to a monotonic counter invites a later "simplification" | med | D-7 confines it to sequencing with sequential arms. The counter-stays-in-files rule is recorded as an explicit **non-goal**, with the `bd mol burn` reset mechanism named so the reason survives without this conversation |
| R5 | **A scripted `bd mol burn` silently no-ops.** Measured: cancelled burn on a wisp with an open APPROVE gate exits **0** | low | 2.3 mandates `--force` and mandates checking output rather than the exit code. Filed upstream by 4.6 so the fix is not private to this plan |
| R6 | **Cross-plan control names in `plan.md` wedge the capability gate.** Measured at 7-declared-vs-1-manifest | low | 0.2 tightens the derivation to `ctl-(165\|182\|184)-[a-z-]+` and states the pattern verbatim. Other plans' control ids live in `findings/`, which the derivation does not scan |
| R7 | **Deploying mid-execution runs new scripts against old prose** | low | 4.7 deploys at land-the-plane only, and asserts `yf --version` equals HEAD — the one detector for a stale stamp when HEAD moved for a reason `build.rs` does not watch |

## Success Criteria

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | Every behaviour change landed its `REQ-*` before its implementation issue closed — **one new id and two amendments**, enumerated | the SPEC commit carries `REQ-AGENT-049` plus amendments to `REQ-AGENT-043` and `REQ-AGENT-045`, and the root `SPEC.md` amendment-log entry; git log order puts that commit before each implementing commit. `050`/`051`/`060`-`064` are pre-existing and must not be reused | 0.1 |
| SC1b | The pre-fix baseline is recorded BEFORE any edit, re-measured rather than inherited | `assets/` carries the three figures with their commands: `grep -c 'Agent'` over the 7 `agents/*.md` (expect **0**), the sites pinning the retired literal, and the `Verification:` census. Per D-5 a figure cited from plan-050 without re-measurement is a defect, not a shortcut | 0.3 |
| SC2 | Every control was observed RED on a fixture, recorded by an issue that is a `depends-on` ANCESTOR of its fix | `assets/red-prework.md` carries a `record-red` non-zero exit per control with the verbatim command; the before/after ordering is carried by the DAG edges 1.1→1.2, 2.1→2.2, 3.1→3.2, not by a timestamp | 0.2, 1.1, 2.1, 3.1 |
| SC2b | Every control was then observed GREEN, and the two observations are distinct records | for each id in `assets/controls.txt`, both a non-zero `record-red` and a zero `assert-distinguishes` record exist — `redcheck.sh verify-all` asserts exactly this and exits 0/1/2 | 1.2a, 2.2, 3.3, 1.4, 2.4, 3.4 |
| SC3 | **The dangling-pointer state fails, and the fixed state passes.** Rewording `red-team.md` without retargeting `spec/agents.md:73` is caught | **two arms, both required**, stated against the COMMAND shape: in a throwaway tree with `spec/agents.md`'s `Verification:` retargeted (0.1 done) but `red-team.md` still carrying the old wording (1.2 not done), assert `ctl-182-spike` exits **non-zero**; then apply 1.2/1.2a's rewording and assert the SAME fixture exits **zero**. One arm alone is satisfied by a control that is unconditionally non-zero — which is exactly what the plan specified before pass-1 C2 (pass-1 C5). EXP-002 measured the FAST tier returning `pass` on the half-fix state, so a criterion resting on the tier alone would pass a broken tree | 1.1, 1.2 |
| SC4 | The literal `Read-only — never writes files` survives at **zero** TRACKED sites, and every `Verification:` clause quoting an agent-file literal resolves | verbatim, **run from the REPO ROOT**: `git grep -c 'Read-only — never writes files' -- ':!docs/plans' ':!docs/research'` returns **no matches** (exit 1). The cwd is normative — the `:!docs/plans` pathspec is repo-root-relative, so running it inside the bundle silently fails to exclude the bundle and reports this plan's own prose as a surviving site. Measured at pass 2 from the root: exactly the 3 source files, 4 occurrences. The instrument is **`git grep`, not `grep`**: measured at pass 2, an untracked `.agent-shell/transcripts/*.md` carries the literal 4 times, so a plain `grep` makes this criterion unpassable for a reason unrelated to the work (pass-2 C24). Historical plan and research bundles are records, not surfaces. Then `ctl-182-spike` conjunct (b) exits 0 | 1.2, 1.2a |
| SC4b | **The hand-enumerated edit set is CLOSED** — every surviving read-only restatement is an enumerated row with a stated disposition | from the repo root, `git grep -lniE 'read-only\|never writes? files' -- 'skills/yf-plan/**' 'web/content/**'` returns a path set that is a **SUBSET** of the row set in `assets/edit-set-182.md`. A subset assertion, not a count (3.3's rule). This converts 1.2's hand enumeration from unverifiable prose into a checkable closure: SC4's literal grep covers only **4 of 9** sites, and `SKILL.md:486/516`, `skills/yf-plan/SPEC.md:65/389-390` and the three `web/content/*` restatements are covered by no grep, no CV row and no drift edge (pass-3 C32, raised at passes 2 and 3). Pass 3 swept it and found the enumeration already complete — `workflows.md:251` is the **yf-research** table and correctly out of scope — so this should pass; it simply was not asserted | 1.2, 1.2a |
| SC5 | The `e-spec-agent` drift edge exists and names the spec as fixed authority | the edge appears in `DRIFT-CHECK.md` §2/§3 with `spec` as authority and `skills/*/agents/*.md` in its §6 trigger scope | 1.3 |
| SC6 | `SKILL.md` §3's Review section **names `Agent` as the dispatch mechanism** — the claim is about the TEXT, not about conduct (R2/R3: obedience has no exit code) — and the assertion is **section-scoped** | `awk '/^### Review$/{f=1} f&&/^### Portability audit/{f=0} f' skills/yf-plan/SKILL.md \| grep -q 'Agent'` exits 0 **after**, and the same command exits 1 on the pre-fix tree. The whole-file form is explicitly rejected: it exits 0 today because `Agent` appears in the frontmatter `allowed-tools:` list. **Second clause, less gameable:** the section must match the imperative dispatch form used at `SKILL.md:315` (`Spawn a sub-agent …` / `Read \`${SKILL_DIR}/agents/red-team.md\``), not a bare token — measured, a bare-token check is GREEN on both `<!-- Agent -->` and *"Do NOT use the Agent tool here"* (pass-1 C8) | 2.2 |
| SC7 | The Phase-3 wisp **represents the review loop**, its arms are **sequential**, and it carries no counter | `bd cook --dry-run` succeeds AND its emitted step-id set **equals** the named set {conformance, red-team, resolve, gate} in a chain with the gate terminal — a **set** assertion, per 3.3's own never-a-count rule. THEN the negatives: no step has more than one `needs` entry, and no step or var records a review-cycle count. The positive clause is required because two negatives are **vacuously true of an empty formula** — a zero-step file cooks, has no multi-`needs` step and records no counter (pass-1 C6). **Stated limit (pass-2 C28):** four empty steps with the right ids in the right order would still satisfy this. Under **D-7** that is close to the whole deliverable — the wisp is scoped to *sequencing*, so step identity and order ARE the substance — but each non-gate step must additionally carry a non-empty description | 2.3 |
| SC8 | `REQ-AGENT-049`'s `Verification:` line **and** both amended REQs' (`043`, `045`) are executable and green | for each of the three, the line is a whole-line backticked command; running it from the tree root exits 0. `ctl-165-executable` asserts exactly this | 3.1, 3.2 |
| SC9 | The executable check is **non-rottable** — it fails if the spec and the test drift apart | delete or rename the test in a throwaway tree and assert the meta-assertion fails; separately, reword the REQ's Verification line and assert it fails | 3.2 |
| SC10 | The new check runs at the point of change, on **each** side of the pair independently | **TWO separate single-path invocations** — `run --tier fast --changed skills/yf-plan/spec/agents.md` and `run --tier fast --changed skills/yf-plan/agents/red-team.md` — each with the new id present in `.commands[].id`. A single two-path run demonstrates only the union and is satisfied when just one glob matched (pass-1 C11). The one-flag caution belongs to 4.6's upstream report, not to any run this plan makes — `--changed` is FAST-only (pass-3 C31) | 3.3 |
| SC11 | The FULL tier passes over the merged tree, **and all three fixtures are green on it** | `plan_manager.py validate-merged <plan_dir> --json` returns `status: "pass"` — the verb 4.1 invokes, named identically (pass-2 C29). Assert the **status string**, not a failure count: the verb emits `status: pass\|fail` and exits 3 on non-pass (pass-3 C31). `CHANGE-VALIDATION.md:39` is `approved: yes`, so tier 1 fires and a vacuous tier-3 `pass` is not reachable here. **Plus** each of the three fixtures re-run against the merged tree exits 0 | 4.1 |
| SC12 | Every upstream row reached the end state its disposition requires | `verify-reconcile --json`: assert `.verdict == "pass"`, **or** `inconclusive` with the inconclusive rows being exactly the one `tracker` row 4.3 adds. Exit 0 alone is insufficient — only `fail` halts, so `inconclusive` also exits 0 | 4.4 |
| SC12b | The coarse tracker is filed THROUGH `/yf-beads-upstream`, so the epic carries it as `external_ref` | `bd show <epic> --json` reports an `external_ref` naming the tracker, and `upstream.py closable` can see it. A tracker filed with a bare `gh issue create` records no mapping — how five earlier trackers went stale | 4.3 |
| SC13 | #149's comment carries the **corrected** premise, not the issue's original framing | the posted comment states the 26-edges / 0-attributed measurement and the no-seam finding, and says explicitly that the issue's own framing was refuted | 4.2, 4.4 |
| SC13b | **#182's CLOSING comment records that D-1 narrowed the issue**, rather than closing it as if its framing were accepted | the posted close comment on #182 quotes the issue's *"never write, edit, or create any file"* claim and states that `red-team.md:63` never said it — the defect was under-specification. A close that silently accepts a false premise leaves the next attempt to rebuild from it (pass-2 C23) | 4.2, 4.4 |
| SC14 | The handoff is **generated**, and a drift makes it fail | regenerate from `plan.md`'s tables and `diff`; a non-empty diff exits 1 | 4.5 |
| SC15 | Both out-of-scope defects are filed with their measurements | two upstream issues exist, each carrying the command and output that established it | 4.6 |
| SC16 | The deployed tree matches source and the version stamp matches HEAD | `yf --version` git hash equals `git rev-parse --short HEAD`; deployed `SKILL.md` tree hashes match repo source | 4.7 |
