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
| [#177](https://github.com/dixson3/yoshiko-flow/issues/177) | no check that a numeric target is derivable from the plan's own scope rules | exclude | Closed out by plan-050 — the refutation comment was posted and D-6 dropped it on evidence. No action here | |
| [#188](https://github.com/dixson3/yoshiko-flow/issues/188) | test suites assert output STRUCTURE and never payload FIDELITY | deferred | plan-050's headline finding is direct evidence, but payload fidelity is a second independent axis, scoped OUT | |
| [#190](https://github.com/dixson3/yoshiko-flow/issues/190) | require plans to ship tests at >= 80% coverage of code they write | deferred | Same axis as #188 — deferred with it | |
| [#145](https://github.com/dixson3/yoshiko-flow/issues/145) | New skill: yf-retrospective — measure escape rate | deferred | Own plan. The emit side accumulates; a consumer built now reads a thin corpus | |

## Investigation Findings

Four experiments returned. **Two refuted parts of the approach hypothesis and one refuted a decision
this plan was about to inherit.** Full records in `findings/`.

| # | Question | Outcome |
| :-- | :-- | :-- |
| [EXP-001](findings/exp-001-dispatch-verification.md) | What can #184's `Verification:` line assert with an exit code? | **The behavioral claim has none, and cannot.** But `spec/agents.md` has **0 of 26** exit-code-decidable clauses today, and #184 has a real substrate the plan can use |
| [EXP-002](findings/exp-002-182-blast-radius.md) | What is #182's complete edit set? | **exp-006's "one line in one file" is wrong by ~7x** — 7 files minimum, 8 with the reviewer sibling. And the FAST tier passes green on the broken intermediate state |
| [EXP-003](findings/exp-003-executable-verification.md) | Does any SPEC `Verification:` line execute today? | **Yes — 1 of 251.** Prior art exists and is green, so #165 stays in scope. The "no prior art → drop it" branch is refuted |
| [EXP-004](findings/exp-004-redcheck-reuse.md) | Can plan-050's control harness be reused, and is a control possible? | **Reuse as-is, and a control is possible for ALL THREE subjects** — which **refutes plan-050's D-8** as written |
| [EXP-005](findings/exp-005-review-wisp.md) | Is a `plan-review` **wisp** buildable without `waits-for`, and is parallelism evidenced? | **BUILDABLE** (spiked and driven — `needs` is an array compiling to `blocks`), but **NO EVIDENCE** for parallel lenses. Ships **sequencing-only**; see D-7 |

### The four results that change the plan

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
| Sites pinning the literal `Read-only — never writes files` | **3** | `red-team.md:63`, `spec/agents.md:73`, **`spec/agents.md:97`** |
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

The plan is four epics plus reconciliation. Epics 1-3 are independent of each other and all depend on
Epic 0.

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
- Issue 0.1: Land the `REQ-*` requirements for every behaviour change here, **before any implementation issue starts** (AGENTS.md SPEC-first). **TWO new ids — `REQ-AGENT-049` (the red-team is DISPATCHED as a sub-agent) and `REQ-AGENT-052`** — plus **amendments** to `REQ-AGENT-043` (scope read-only to *the repository under review*; authorize the sandbox spike) and `REQ-AGENT-045` (the same carve-out for `reviewer.md`, per D-8). Use `049` and `052` specifically: measured, `050`, `051` and `060`-`064` are already taken and a spike arm silently picked up the pre-existing `050` and reported a false RED. Each new REQ's `Verification:` line must be **executable** per Epic 3 — do not write a prose line intending to fix it later, because that is the M5 defect this plan exists to close. Also add the root `SPEC.md` amendment-log entry (precedent: `SPEC.md:264`).
- Issue 0.2: Copy `redcheck.sh` and `gate-run.sh` **byte-for-byte** from plan-050's `assets/` into this bundle's `assets/`, changing only the header comment line — the same way plan-050 took `gate-run.sh` from plan-049. Do **not** rebuild and do **not** promote to `_shared/` (EXP-004: the portability contract requires a cold reader in a *different repo* to re-run the evidence from the bundle alone). **Write `assets/controls.txt` with exactly three ids: `ctl-182-spike`, `ctl-184-dispatch`, `ctl-165-executable`.** **Tighten `verify-all`'s count derivation to `grep -oE 'ctl-(165|182|184)-[a-z-]+'`** — the inherited generic pattern is contaminated by any prose naming another plan's control ids, which EXP-004 measured wedging the gate at 7-declared-vs-1-manifest. State the tightened pattern verbatim in this issue: an executor copies whatever the issue prints.
  - depends-on: 0.1
- Issue 0.3: Record the pre-fix baseline into `assets/`: `grep -c 'Agent'` over all 7 `agents/*.md` (expect **0**), the three sites pinning the literal `Read-only — never writes files`, and the corpus `Verification:` census (expect **251 / 1 executed**). Re-measure per D-5 rather than citing this plan's own drafting figures.
  - depends-on: 0.1

### Epic 1: The sandbox-spike rule (#182)
- Issue 1.1: Author the fixture `ctl-182-spike` with **two conjuncts** — (a) `red-team.md` authorizes a spike, and (b) **every double-quoted fragment in `REQ-AGENT-043`'s `Verification:` line is verbatim-present in the file it names**. Conjunct (b) is the substance: EXP-002's spike measured the FAST tier returning `pass, first_failure None` on the dangling state where `red-team.md` was reworded and the spec still pinned the old string. **Run `redcheck.sh record-red <fixture> ctl-182-spike` against the unfixed tree; this issue PRODUCES that record.**
  - depends-on: 0.2
- Issue 1.2: Apply the **7-file edit set**, SPEC-first: `spec/agents.md` (REQ text, `Rationale:` carrying the plan-049 provenance, and the **retargeted `Verification:`**), then `red-team.md:63`, `SKILL.md:486` and **`:516`** (`The agent never writes files` is over-broad against the amended REQ), `SPEC.md:65`/**`:390` (GR-PLAN-002)**, `web/content/skills/yf-plan.md:34`, `web/content/pages/workflows.md:172`, `web/content/pages/glossary.md:90`. Steps 3, 9 and 10 of EXP-002's ordered list have **nothing mechanical** behind them — enumerate by hand and say so. Use the portable core of `AGENTS.md:78-80`, **not** its verbatim text: the plan-049 anecdote does not travel to a foreign vault and belongs in `Rationale:`, and *"reviewers **and investigators**"* is wrong here since the investigator already gets a disposable worktree.
  - depends-on: 1.1
  - resolves-upstream: #182 (include)
- Issue 1.2a: Apply the same carve-out to `agents/reviewer.md:43` and `REQ-AGENT-045` (`spec/agents.md:95/97`), per **D-8**. `ctl-182-spike`'s conjunct (b) generalizes to it for free.
  - depends-on: 1.2
- Issue 1.3: Add the `DRIFT-CHECK.md` edge **`e-spec-agent`** (`spec` → `agent`, contract): *every `REQ-AGENT-*` `Verification:` clause quoting a literal from an `agents/*.md` file resolves to a string present in that file.* Per **D-9** this is the systemic fix behind 1.2's step 3 — EXP-002 measured that **no `spec → agent` edge exists at all**, which is why the dangling state is invisible.
  - depends-on: 1.2
- Issue 1.4: **Verify** — assert `assets/red-prework.md` contains both records for `ctl-182-spike`. Reads the file; runs no `redcheck.sh` verb.
  - depends-on: 1.2a, 1.3

### Epic 2: Sub-agent dispatch (#184)
- Issue 2.1: Author the fixture `ctl-184-dispatch` — the **`### Review` section** of `SKILL.md` names `` `Agent` ``. **Section-scoped, never whole-file**: measured, `grep -q 'Agent' SKILL.md` exits **0 today** on the un-fixed tree because `Agent` appears at `:21` in the frontmatter `allowed-tools:` list, so the whole-file form ships unable to fail. **Run `redcheck.sh record-red <fixture> ctl-184-dispatch`; this issue PRODUCES that record.**
  - depends-on: 0.2
- Issue 2.2: Rewrite `SKILL.md` §3 step 2 to **dispatch** the red-team via `Agent`, mirroring §2's `Spawn a sub-agent …` form at `:315`, and land `REQ-AGENT-049`'s text. Keep §3's *"Two passes, in order"* — the conformance→adversarial ordering is unchanged; what changes is who runs the adversarial pass.
  - depends-on: 2.1
  - resolves-upstream: #184 (include)
- Issue 2.3: Ship `skills/yf-plan/formulas/plan-review.formula.toml` — the Phase-3 wisp, giving the review loop the bead representation it is the only phase to lack. **Arms stay SEQUENTIAL (D-7):** conformance → red-team → resolve → gate, one reviewer per cycle, preserving the chain property in which each pass verifies the previous pass's resolutions. `needs` is an array and multi-parent fan-in works (EXP-005 drove it), but this plan **does not use fan-out**. **The counter does NOT move into the wisp** — see Non-goals. Scripted `bd mol burn` **must pass `--force` and must check output, not the exit code**: measured, a cancelled burn on a wisp with an open APPROVE gate exits **0**.
  - depends-on: 2.2
- Issue 2.4: **Verify** — assert `assets/red-prework.md` contains both records for `ctl-184-dispatch`.
  - depends-on: 2.3

### Epic 3: Executable `Verification:` lines (#165, narrow)
- Issue 3.1: Author the fixture `ctl-165-executable` — each of `REQ-AGENT-049` and `REQ-AGENT-052` has a `Verification:` line that is a whole-line backticked command **and that command exits 0 from the tree root**. **Run `redcheck.sh record-red <fixture> ctl-165-executable`; this issue PRODUCES that record.** Note the **redundancy caveat**: if the two REQs' Verification lines *are* Epic 1's and Epic 2's assertions, this control green ⟺ those two green, adding only the meta-property *"the line parses as a command"*. That is a real assertion — it is precisely the M5 defect #165 names — but it is **not independent evidence** and the plan does not present it as such.
  - depends-on: 0.2
- Issue 3.2: Write the pytest and register it, following `uv-yf-cli-enum` / `test_cli_enumeration.py` **verbatim as the template** (EXP-003: the only one of 251 clauses that closes the loop). Three parts, all required: assert the agent-template prose property the REQ declares; assert the REQ id exists in the spec **and that its `Verification:` line names this test** (the meta-assertion that makes it non-rottable); and carry a **vacuity guard** so a spec reshape fails loudly instead of silently checking nothing. **Naming a `test_*.py` in a Verification line is NOT execution** — 30 clauses already do that and it buys nothing mechanically.
  - depends-on: 3.1
  - resolves-upstream: #165 (partial)
- Issue 3.3: Add the `CHANGE-VALIDATION.md` §1 `fast` row and §3 glob rows on **both** `skills/yf-plan/spec/agents.md` and `skills/yf-plan/agents/*.md`, so amending either side without the other is a hard failure at the point of change. Both globs already exist in §3. **Word every REQ as a set/property assertion, never a count** — `REQ-CLI-006` drifted three times as a count and zero times as a set equality.
  - depends-on: 3.2
- Issue 3.4: **Verify** — assert `assets/red-prework.md` contains both records for `ctl-165-executable`.
  - depends-on: 3.3

### Epic 4: Reconcile and land
- Issue 4.1: Run the FULL validation tier over the **merged** tree and record the result. **Invoke `change_validation.py` with ONE `--changed` flag carrying all paths** — measured at source (`:946`), `--changed` is declared `nargs="*"` with no `action="append"`, so a repeated flag silently drops all but the last path.
  - depends-on: 1.4, 2.4, 3.4
- Issue 4.2: Draft the upstream comments **from the grant verb's enumeration**, not from a prose list. The #149 comment carries the **corrected premise** (26 `discovered-from` edges, 0 attributed on either endpoint — the relationship exists, only attribution is missing), plus C40 and the **no-seam** finding. The #165 comment carries the census (251 / 1) and the **two measured-false Verification commands** as evidence.
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
- Condition: the operator has authorized the upstream comments, the tracker creation, and the closes, against a grant generated by `plan_manager.py grant` rather than hand-derived
- Test: test -f docs/plans/plan-051-james-dixson-2f499f/assets/upstream-authorization.txt
- Blocks: 4.3, 4.4
- Instructions: generate the grant, present it in full (every issue number, every comment body verbatim, every close and its reason), then ask. Record the authorization to `assets/upstream-authorization.txt`. A green test can never substitute for consent — this gate is `human` and is never auto-resolved.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **The #182 edit set is enumerated by hand and three of its steps have no mechanical check.** A missed restatement ships a tree that contradicts itself and passes every gate | high | `ctl-182-spike`'s conjunct (b) covers the spec↔prose pin — the one EXP-002 proved FAST misses. D-9's `e-spec-agent` edge closes it systemically. The two `web/content/pages/*` sites remain hand-enumerated and are named individually in 1.2 rather than left to a glob |
| R2 | **A text-presence control is gameable by the token it checks for.** `ctl-184-dispatch` is satisfied by a comment or a prohibition containing the word `Agent` | med | Stated plainly in 2.1 and in `REQ-AGENT-049`'s honesty clause rather than papered over. The control's value is that it is currently **RED**, so it distinguishes before/after; it is not claimed to verify conduct |
| R3 | **The plan asserts a behavioural claim no exit code can reach.** "The red-team was dispatched" is not mechanically observable | med | D-6 narrows plan-050's D-8 rather than repeating or dropping it: the controls certify the **edit set**, never reviewer obedience. Candidate provenance mechanisms were evaluated and rejected with reasons — a frontmatter key is self-attestation, transcript mining fails ~half the existing corpus and is harness-local |
| R4 | **The `plan-review` wisp is new machinery in a plan that did not need it**, and a burnable wisp adjacent to a monotonic counter invites a later "simplification" | med | D-7 confines it to sequencing with sequential arms. The counter-stays-in-files rule is recorded as an explicit **non-goal**, with the `bd mol burn` reset mechanism named so the reason survives without this conversation |
| R5 | **A scripted `bd mol burn` silently no-ops.** Measured: cancelled burn on a wisp with an open APPROVE gate exits **0** | low | 2.3 mandates `--force` and mandates checking output rather than the exit code. Filed upstream by 4.6 so the fix is not private to this plan |
| R6 | **Cross-plan control names in `plan.md` wedge the capability gate.** Measured at 7-declared-vs-1-manifest | low | 0.2 tightens the derivation to `ctl-(165\|182\|184)-[a-z-]+` and states the pattern verbatim. Other plans' control ids live in `findings/`, which the derivation does not scan |
| R7 | **Deploying mid-execution runs new scripts against old prose** | low | 4.7 deploys at land-the-plane only, and asserts `yf --version` equals HEAD — the one detector for a stale stamp when HEAD moved for a reason `build.rs` does not watch |

## Success Criteria

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | Every behaviour change landed its `REQ-*` before its implementation issue closed — **two new ids and two amendments**, enumerated | the SPEC commit carries `REQ-AGENT-049` and `REQ-AGENT-052` plus amendments to `REQ-AGENT-043` and `REQ-AGENT-045`, and the root `SPEC.md` amendment-log entry; git log order puts that commit before each implementing commit. `050`/`051`/`060`-`064` are pre-existing and must not be reused | 0.1 |
| SC1b | The pre-fix baseline is recorded BEFORE any edit, re-measured rather than inherited | `assets/` carries the three figures with their commands: `grep -c 'Agent'` over the 7 `agents/*.md` (expect **0**), the sites pinning the retired literal, and the `Verification:` census. Per D-5 a figure cited from plan-050 without re-measurement is a defect, not a shortcut | 0.3 |
| SC2 | Every control was observed RED on a fixture, recorded by an issue that is a `depends-on` ANCESTOR of its fix | `assets/red-prework.md` carries a `record-red` non-zero exit per control with the verbatim command; the before/after ordering is carried by the DAG edges 1.1→1.2, 2.1→2.2, 3.1→3.2, not by a timestamp | 0.2, 1.1, 2.1, 3.1 |
| SC2b | Every control was then observed GREEN, and the two observations are distinct records | for each id in `assets/controls.txt`, both a non-zero `record-red` and a zero `assert-distinguishes` record exist — `redcheck.sh verify-all` asserts exactly this and exits 0/1/2 | 1.4, 2.4, 3.4 |
| SC3 | **The dangling-pointer state fails.** Rewording `red-team.md` without retargeting `spec/agents.md:73` is caught | apply that exact half-fix in a throwaway tree and assert `ctl-182-spike` exits **non-zero**. EXP-002 measured the FAST tier returning `pass` on this state, so a criterion resting on the tier alone would pass a broken tree | 1.1, 1.2 |
| SC4 | The literal `Read-only — never writes files` survives at **zero** sites, and every `Verification:` clause quoting an agent-file literal resolves | `grep -c` over the repo returns 0 outside `docs/plans/**` and `docs/research/**` (historical records, not surfaces); `ctl-182-spike` conjunct (b) exits 0 | 1.2, 1.2a |
| SC5 | The `e-spec-agent` drift edge exists and names the spec as fixed authority | the edge appears in `DRIFT-CHECK.md` §2/§3 with `spec` as authority and `skills/*/agents/*.md` in its §6 trigger scope | 1.3 |
| SC6 | `SKILL.md` §3 dispatches the red-team, and the assertion is **section-scoped** | `awk '/^### Review$/{f=1} f&&/^### Portability audit/{f=0} f' skills/yf-plan/SKILL.md \| grep -q 'Agent'` exits 0 **after**, and the same command exits 1 on the pre-fix tree. The whole-file form is explicitly rejected: it exits 0 today because `Agent` appears in the frontmatter `allowed-tools:` list | 2.2 |
| SC7 | The Phase-3 wisp exists, its arms are **sequential**, and it carries no counter | `plan-review.formula.toml` cooks (`bd cook --dry-run`) with no step having more than one `needs` entry, and no step or var records a review-cycle count | 2.3 |
| SC8 | **Both** new REQs' `Verification:` lines are executable and green | for each, the line is a whole-line backticked command; running it from the tree root exits 0. `ctl-165-executable` asserts exactly this | 3.1, 3.2 |
| SC9 | The executable check is **non-rottable** — it fails if the spec and the test drift apart | delete or rename the test in a throwaway tree and assert the meta-assertion fails; separately, reword the REQ's Verification line and assert it fails | 3.2 |
| SC10 | The new check runs at the point of change, on **both** sides of the pair | `change_validation.py run --tier fast --changed <spec path> <agent path>` (ONE flag, all paths) selects the new row for each side independently | 3.3 |
| SC11 | The FULL tier passes over the merged tree | `validate-merged` reports 0 failures | 4.1 |
| SC12 | Every upstream row reached the end state its disposition requires | `verify-reconcile --json`: assert `.verdict == "pass"`, **or** `inconclusive` with the inconclusive rows being exactly the one `tracker` row 4.3 adds. Exit 0 alone is insufficient — only `fail` halts, so `inconclusive` also exits 0 | 4.4 |
| SC12b | The coarse tracker is filed THROUGH `/yf-beads-upstream`, so the epic carries it as `external_ref` | `bd show <epic> --json` reports an `external_ref` naming the tracker, and `upstream.py closable` can see it. A tracker filed with a bare `gh issue create` records no mapping — how five earlier trackers went stale | 4.3 |
| SC13 | #149's comment carries the **corrected** premise, not the issue's original framing | the posted comment states the 26-edges / 0-attributed measurement and the no-seam finding, and says explicitly that the issue's own framing was refuted | 4.2, 4.4 |
| SC14 | The handoff is **generated**, and a drift makes it fail | regenerate from `plan.md`'s tables and `diff`; a non-empty diff exits 1 | 4.5 |
| SC15 | Both out-of-scope defects are filed with their measurements | two upstream issues exist, each carrying the command and output that established it | 4.6 |
| SC16 | The deployed tree matches source and the version stamp matches HEAD | `yf --version` git hash equals `git rev-parse --short HEAD`; deployed `SKILL.md` tree hashes match repo source | 4.7 |
