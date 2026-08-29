---
type: Plan
okf_spec: OKF-PLAN
id: plan-059-james-dixson-55137e
author: james-dixson
created: '2026-08-28'
status: reconciling
deliverable_class: standard
fingerprint: 2dcf24615fab68d963a9acf8041189b658fa6a9fe0c3e7ada9b39dbc31c2e7fa
epic: yf-mol-vltm
---
# Plan: Design yf-judgement: an automatically-triggered escalation path that raises a structured question to the nearest upstream controller when a plan stops converging, with the severity-vocabulary pin as its prerequisite deliverable and the severity-decay detector as an optional, second-order add-on

**ID:** plan-059-james-dixson-55137e
**Author:** james-dixson
**Created:** 2026-08-28
**Status:** reconciling
**Deliverable-class:** standard
**Epic:** yf-mol-vltm
**Fingerprint:** 2dcf24615fab68d963a9acf8041189b658fa6a9fe0c3e7ada9b39dbc31c2e7fa

## Objective
Design yf-judgement: an automatically-triggered escalation path that raises a structured question to the nearest upstream controller when a plan stops converging, with the severity-vocabulary pin as its prerequisite deliverable and the severity-decay detector as an optional, second-order add-on

## Motivation

Agent-driven plans sometimes stop converging: a review loop re-raises the same concern,
an execution bead is re-attempted, a fix is followed by another fix. Today the only two
things a yf session can do at that moment are **keep fixing** or **stop silently**. There
is no third move — *ask the controller that can settle it* — and the absence is measured,
not supposed:

- `yoshiko-flow#264` recorded a subordinate going `idle` at a phase boundary rather than
  asking, twice, under a contract that had already been tightened once. The operator's
  follow-up named the real defect: **a silent idle**, not stopping as such. The rule that
  actually holds is *"you may continue, or you may ask upstream; going idle without having
  asked is non-conformant"* — and the "ask upstream" arm has no implementation.
- `yf-research` 005 (114 plan bundles, 301 review passes, 7 repos) measured that the
  dominant category of operator input (T1, 45/119, the only category present in all 7
  repos) **arrives 80% of the time after a draft exists**. A pre-flight clarifying
  interview structurally cannot reach it; a mid-execution ask can.
- The same study measured that **questions are not recorded anywhere in the corpus** — only
  answers. So the cost of an ask, the counterfactual value of asking earlier, and the recall
  of any detector are all unmeasurable today, for want of an instrument that writes the
  question down.

Who is affected: every yf-plan execution and every `yf-herdr`-delegated session. What
triggered the work: `#269` (this skill's proposal, carrying research 005's findings) and
`#264`'s follow-up, which reframed its own wording fix as interim and routed the durable fix
here.

**This plan designs the escalation path first and the detector second, deliberately.** The
detector research 005 characterised is first computable at pass 3, silent on 68% of the
corpus, and shippable only under a severity predicate whose vocabulary is not yet pinned.
The escalation path is the half with corpus support behind it.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #269 | New skill: yf-judgement — detect when a plan needs OPERATOR JUDGEMENT and escalate a question | partial | **IN:** the escalation path, shipped as a capability inside `yf-plan`/`yf-herdr`. **OUT:** the severity-decay detector, answered **NO** on evidence (EXP-002), and the `skills/yf-judgement/` directory, which is deliberately not created. Was dispositioned `include` in an earlier draft; corrected at red-team pass 1 because only one of its three halves ships. A correction comment recording the refutation is posted on the issue. | 1.1, 2.1, 3.1 |
| #264 | yf-herdr: AUTONOMY clause does not survive a phase boundary | partial | The wording fix already landed and is validated separately (three-boundary natural experiment). This plan takes only the **durable** half its follow-up routed here: provenance-derived autonomy and the one-hop REQ-HERDR-024 generalisation. **N-hop is explicitly declined — see R7.** | 4.1 |
| #270 | yf-plan: `plan-review.formula.toml` has NEVER been poured — the only structural mid-burn review gate in yf has not fired in 27 review passes | deferred | Filed from this plan's escalation E-3 and scoped OUT by operator decision. Load-bearing here anyway: Issue 3.4 and SC7 keep the escalation payload movable onto that wisp **without redesign**, because fixing #270 upgrades this plan's trigger for free — which is the stated reason the weaker `review-loop-check` trigger is acceptable now. | 3.4 |
| #273 | The command-vs-obligation law | partial | **Filed by the operator DURING this plan's execution, from this plan's own EXP-001 — and it carries the WITHDRAWN framing.** It was written from the numbers this session reported before red-team passes 1 and 2 corrected them, so it states a per-event obligation rate and a "factor of five". Issue 6.4 corrects it to the per-plan unit (4/5 vs 2/5) over one stated population. Red-team pass 2 found this issue existed and was unrecorded here, which had made the original "file it" issue redundant and its success criterion green before execution. | 6.4 |
| #145 | New skill: yf-retrospective — measure escape rate and enforce a fix+prevention contract | partial | Not resolved here. Mined for synergies: **two of the six claimed do not hold** (EXP-003). Its finding 4 is this plan's hardest constraint. `plan-retrospective.md` is **rejected as the escalation surface** — append-only, no update verb — so `escalations.md` is a sibling, not an entry kind. The retrospective consumer half stays with #145. | 2.6 |
| #269 | plan-059 execution tracking (ADOPTED as this plan's coarse tracker) | tracker | **Adopted, not created** (Issue 0.2). `AGENTS.md` mandates ONE coarse tracking issue per plan-scale effort, and #269 already existed as this effort's proposal issue — so its body carries the tracker linkage rather than a competitor being filed alongside it. This row exists so `stamp-tracker` can find the tracker and stamp its URL onto the epic as `external_ref`, which is what makes the tracker visible to `upstream.py closable` (REQ-PLAN-073). Recorded as `TRACKER_ISSUE=269` in `assets/filed-issues.env`. **The `## Upstream Issues` section is fingerprint-excluded (REQ-PORT-040), so adding this row during execution cannot make the plan stale-approved.** | 0.2 |

## Investigation Findings

Four investigations, each dispatched to an isolated sub-agent so it could refute the scoping
decision that commissioned it. Full reports in `findings/`; this section carries only what changes
the design.

### EXP-001 — no mechanical trigger exists, but the real discriminator is not the one we assumed

**There is no automatic trigger point anywhere in yf.** Zero `PostToolUse`/`PreToolUse`/`FileChanged`
hooks, zero installed git hooks, and `yf-beads-init` *deliberately removes* the one hook mechanism
bd would provide. The four surfaces that read as mechanical — `yf-change-validation` FAST,
`yf-drift-check`, `doc_lint`, `yf-markdown-lint` — **are the prose rules**; nothing in the runtime
reads their globs on an edit.

**The measured discriminator is "prose that names a COMMAND" vs "prose that names an OBLIGATION",**
on one event with author, session and task held constant:

**Population, re-derived in the main checkout and identical for all three rows: the five
POST-PLAN-045 plans whose `reviews/pass-*.md` count exceeds the default bound of 5** — `plan-048`
(7), `050` (13), `052` (6), `054` (6), `055` (7). **The `post-plan-045` qualifier is load-bearing and
an earlier draft dropped it**: by the bare pass-count criterion the set is *seven*, adding `plan-026`
(7) and `plan-029` (6), which predate `review-loop-check` and could not have run it. `plan-056` is excluded: its bundle in `main` contains no `log.md` at all.

| recorder | rate | unit |
| :-- | --: | :-- |
| script writes it itself | **12 / 12 (100%)** | per event, over those 5 plans |
| prose instructs an agent to RUN A COMMAND | **4 / 5 (80%)** | per plan |
| prose instructs an agent to HONOUR AN OBLIGATION | **2 / 5 (40%)** | per plan |

**All three rows are drawn from one stated population, reproducible in the main checkout.** Getting
this right took three attempts and every one of them is recorded rather than quietly replaced —
draft 1 mixed *units*, draft 2 mixed *populations*, and draft 3 still had row 2 on a denominator of
6 while rows 1 and 3 used 4. **Direction, not magnitude:** two earlier drafts of this table
were wrong, first by comparing a per-event rate to a per-plan one (*"a factor of five"*), then by
drawing its rows from different populations. Both were caught by red-team passes and both are
recorded in `findings/finding-command-vs-obligation.md` rather than silently fixed. **The design
conclusions turn on the direction and on four independently-filed defects the law explains, not on
the ratio.**

Two corrections to the candidate list: **`yf_attempts` is struck** — zero occurrences across 1,245
beads, it is prose, and it is a controller self-report (C3-disqualified). **The concerns table
cannot carry the trigger** — 46% coverage across 5 incompatible header shapes. The **verdict line**
(100% from plan-024 on) and the **pass-file count** (100% by construction) can.

### EXP-002 — the detector's shippability condition FAILS, and the study's instrument is broken

**The strict `high` predicate does not survive the control read.** It fires on `yoshiko-flow/plan-029`
and `plan-033`, both deliberate re-scoping by their own phase logs. **`plan-026` was not the
exception — it is the one instance whose reviewer wrote `medium (blocking)` instead of `high`. The
severity normaliser was never the discriminator.**

Separately, **`finding_recurrence.py` systematically deletes HIGH severities, biased toward HIGH**
(prose-shadowing drops 11% of `high` table rows vs 3% of `low`; the id-column requirement rejects
the exact table shape `SKILL.md` currently mandates). Parser-free firing is **22/43, not 13/43**.
**Every D3 operating characteristic in §4.1–§4.3 rests on that parse.**

**The constructive result:** a HIGH at pass ≥ 3 is a thrash signal **only if pass ≥ 3 is not the
first review of a re-scoped plan** — already mechanically available in `log.md` as a `drafting:`
bullet between two `review-pass:` bullets. **That one guard excludes 3 of the 4 false positives.**

**Pinning the vocabulary is cheap and independently valuable**: `reviews/pass-N.md` is already typed
and linted, a vocabulary is already declared in prose three times, and nothing enforces it. Cost is
**one new `doc_lint` check kind at `R` severity — no migration.**

### EXP-003 — two of #269's six synergies do not hold

Claim **5 ("complementary in time") DOES NOT HOLD**: `yf-retrospective` competes for the **settled**
§6.4 hook; `yf-judgement` competes for the **§3/§5.3 hooks, which have no settled contract** — and
`review-loop-check` is a **landed incumbent on `yf-judgement`'s exact trigger.** The two skills touch
**the same retrospective rows**, not different phases.

Claim **6's "data-starved" half is STALE**: #145's *"empty corpus"* was true at 7 entries; measured
today it is **96 entries across 13 bundles in 3 repos**, with `asked`/`answered`/`frontloadable` at
**100% fill**. Research 005's *"the corpus records only answers"* is **already ~⅔ discharged by the
landed emit side, which the research did not credit.** The risk-transfer half holds.

Claim **3 holds for capture but not lifecycle** — `append_retrospective` is strictly append-only,
there is no update verb, and the corpus's one `(pending)` answer **is still pending.** Claim **1
holds and is proved a third time**: `retrospective_fields.py` is CI-validated, README-documented,
schema-referenced, and has **zero callers**.

Six missed synergies, of which two are load-bearing: **the taxonomy has four homes and #145's
promised `yf-drift-check` edge does not exist**; and **`REQ-HERDR-026` already shipped the batching
boundary** research 005 recommends.

### EXP-004 — there is no answer-return path

`AgentPromptWaitOptions` is `{until, timeout_ms}` only — **no message id, no correlation, no
response payload**; the `EventMatch` set contains **no metadata event**. A child can ask and a parent
can answer, but the child cannot block on, detect, or correlate an answer.

**One-hop escalation today is FIRE-AND-FORGET, and the durable form must be a written artifact.**
Corroborated: 4 of the 11 existing `stop` entries record an ask whose answer never arrived — **the
written record survived; a message channel would have left nothing.**

Measured session topology is **depth 1, fan-out 2**; a child knows **exactly one opaque pane id**
about its parent. **N-hop is not merely untested — its state is not representable in what is
seeded.** Three undocumented channel defects: `herdr agent prompt` **exits 0 on `agent_not_found`**;
the token channel is 16 keys × 32 chars and display-only; a push into a `blocked` parent is
swallowed.

**And the schema forces the dominant payload out of the record**: `plan-047 RE-009` had to spill its
three drafted options to `assets/split-proposal.md` because no field existed for them — T1, the
dominant category of operator input, written outside the record.

## Approach

### The verdict: SHIP THE PATH, PIN THE VOCABULARY, DO NOT SHIP THE DETECTOR

The honest outcome constraint S4 permitted is the outcome the evidence produced, and it is now
**better evidenced than when the operator offered it**. This plan ships two things and explicitly
declines a third:

| | Disposition | Why |
| :-- | :-- | :-- |
| **The escalation path** | **SHIP** | The half with corpus support. Its one blocking unknown (does a trigger exist?) resolved to *"a measurably best one does, at 4/5"*. |
| **The severity-vocabulary pin** | **SHIP, and it lands on its own** | Cheap (one check kind, no migration), independently valuable, and a hard prerequisite for anyone who later builds a findings-based predicate. **Its value does not depend on the detector**, which is why it is Epic 1 and not a sub-task of a detector epic. |
| **The severity-decay detector (D3)** | **DO NOT SHIP — NOT YET, and this is a finding, not a deferral** | Its shippability condition **failed** (EXP-002 (a)), and the instrument every published operating characteristic rests on is **broken and biased** (EXP-002 (d)). Shipping now would ship a detector whose measured properties are unknown. |

#### The detector epic dies here, and this section says so plainly

**The plan does not replace it with a weaker deliverable to fill the slot.** Epic 6 ships **no
artifact**: it repairs a measuring instrument and writes down what a future decision would need.
That is the whole of it, and SC9 exists to make the emptiness checkable rather than tacit.

**The re-scope guard is currently FITTED, and must not be presented as a repair.** It was derived
from the four false positives it excludes, so evaluating it on those four is circular. Stating what
would independently test it:

- **A held-out set exists and is affordable.** EXP-002 (d) found **9 bundles that fire under a
  parser-free reading and are silent under the study's instrument** — `d3-pxe/plan-015`, `016`,
  `018`, `019`, `pybridge/plan-006`, `yoshiko-flow/plan-046`, `051`, `052`, `056`. **None was ever
  hand-read, so none is in the derivation set.** That is a genuine held-out sample of 9.
- **But it has no TRUE/FALSE label, and the label is the expensive part.** Research 005 already
  names the defect this would otherwise repeat: *"the label and the discriminator were authored by
  the same agent with no held-out set."* So the label must be established **blind** — by a party who
  does not know whether the guard fires, before the guard is evaluated — or the exercise refits.
- **And passing would establish less than it sounds.** It would restore a plausible PPV. It would
  not touch the two facts that bound the detector's usefulness regardless: it is **first computable
  at pass 3**, and **recall has never been measured for anything**, so nothing bounds the episodes
  it misses.

**A hazard recorded for whoever runs that re-measurement.** Do not assert an expected firing count
as a literal. An earlier draft of this plan carried a criterion asserting `fires == 22 and
evaluable == 43`; both numbers are unsafe. **43 is a live denominator** — the corpus grows, and
**this very plan becomes a >=3-pass bundle**, so the figure was guaranteed to break for a reason
unrelated to the repair. And **22 came from a parser-free grep, a different instrument, not ground
truth** — asserting the repaired parser lands exactly there pre-judges the repair and creates a
Goodhart incentive to tune to it, in a plan whose R4 is about Goodhart. Assert a **property** against
a **frozen fixture corpus**, never a literal against a live one.

**And the parser repair itself is NOT this plan's to make.** `finding_recurrence.py` lives only in
the research bundle on the unmerged `research/005-thrash-detection` branch, and escalation E-4's
resolved outcome is explicit: the repair is scoped in **only if the detector epic survives**. It does
not. An earlier draft carried it as Issue 6.1 anyway — **a silent override of the plan's own resolved
escalation, in the plan whose purpose is to make escalations binding.** It is dropped, and Epic 6
writes no code at all.

**So the honest finding is: the detector needs a corpus and a labelling procedure that do not exist
yet.** Not "defer until convenient" — the specific missing objects are a blind hand-audit label over
9 held-out bundles and an instrument that does not delete the severities it measures. **Epic 6 specifies
both and creates neither** — the instrument repair belongs to the research bundle, per escalation
E-4's resolved default. **Whether anyone then builds the detector is a decision for a
future plan with that evidence in hand, and this plan takes no position on it.**

This is reinforced rather than weakened by EXP-001's result: **there is no mechanical trigger
anywhere in yf**, so even a well-characterised detector would be invoked by the same prose that
carries everything else. A detector is not the scarce component. **The invocation path is**, and
that is what Epics 3 and 5 buy.

### The architecture: WRITE-THEN-NOTIFY, never ask-and-await

Forced by EXP-004: no answer-return primitive exists. **The escalation IS an artifact; the push is a
notification about it.** Three consequences that are requirements, not preferences:

1. **Every escalation carries `on_no_answer`.** Fire-and-forget is the actual semantics; a design
   omitting it pretends to a round-trip herdr cannot deliver. *Measured in this session's own
   dogfooding: E-3 and E-4 were both sendable only because each stated its default.*
2. **Every escalation carries `alternatives` (≥2) and a `recommended` naming one of them.** This is
   the dominant operator input (T1, 45/119, the only category in all 7 repos) and the existing
   schema **structurally forces it out of the record.** `recommended` is stored **separately from**
   `answer` — the `writing` convention's defaults were destroyed by their own resolutions.
3. **Delivery is verified structurally, never by exit code.** `herdr agent prompt` returns
   `agent_not_found` **at exit 0**.

### The trigger: bind to a COMMAND, at a boundary, on second-party residue

Per EXP-001's command-vs-obligation gap, the trigger must be **a command an agent runs whose exit code carries
the escalation** — never an obligation. So `yf-judgement` **extends `review-loop-check`** (measured
4/5 on an existing invocation path) rather than adding a `/yf-judgement` slash command (measured
rate of a fresh path: 0). **A new manually-invoked surface is precisely what #145 finding 4
forbids.**

**A second trigger, which neither #269 nor #264 lists, is added on this session's own evidence.**
Three of the four escalation-worthy moments here came from **a second party returning a result whose
consequence exceeded this session's authority** — the operator (E-2) and two sub-agents (E-3, E-4).
**Not one arose from the session noticing it was stuck.** That is consensus C3 arriving from a
direction 005 did not measure: the escalation-worthy events are **not self-observable at all.** So
the `Agent`-returns-findings boundary is a first-class trigger point.

**Both triggers are boundaries, so escalations batch** — riding `REQ-HERDR-026`'s three existing
push classes, which EXP-003 found already shipped the batching requirement 005 recommends. **The
propagation budget is then a property of the existing trigger set, not new machinery.**

### Why Epics 1, 4 and 6 are in this plan rather than three plans

**Raised twice in review and answered here rather than left implicit.** Epic 1 lands independently,
Epic 4 is a self-contained `yf-herdr` SPEC change, and Epic 6 ships nothing — 15 issues in three
separably-landable groups. The coupling argument:

- **Epic 1 exists because of Epic 6's refusal, and only this plan knows that.** The severity pin is
  the prerequisite research 005 named for a detector; **this plan declines the detector and keeps the
  pin anyway.** Split apart, Epic 1 arrives with no stated reason to exist and the next reader
  re-derives the detector question from scratch — which is the specific waste EXP-002 cost an hour of
  hand-reading to avoid.
- **Epic 4 is the other half of Epic 3's contract.** The escalation payload and the predicate that
  routes it are one design: `on_no_answer` is required *because* EXP-004 found no answer-return path,
  and REQ-HERDR-024's third arm exists *because* this session's own E-1 showed the predicate was
  missing "look". Landing the payload without the predicate ships a message with no addressee rule.
- **Epic 6 must land with Epics 1–3 or its refusal is unfalsifiable.** "We declined the detector" is
  only checkable against a plan that shows what it built instead. SC9 tests exactly that relation.

**Epic 1 may still be split out and landed first** if the operator prefers a smaller first change;
nothing in Epics 2–5 depends on it except through Issue 1.1's SPEC edit. That is a scheduling
decision, and it is the operator's.

### Epic 0 exists because three review passes each shipped a locally-correct, globally-unchecked repair

Red-team pass 3's closing recommendation, adopted as a deliverable rather than as a one-off fix:

> **The single highest-leverage change is not another round of edits: it is to run every gate
> `Test:` and every non-`manual:` success criterion once as written, in the tree they will execute
> in, and record the exit code beside each.**

Measured, that sweep would have caught four of pass 3's own findings mechanically — a gate that could
never go green, a verification surface pointed at a tree that never receives the code, two criteria
green before the work began, and a fixture no issue creates. **It is the only step in this bundle
that had never been performed on the full set.**

It is **Issue 0.1 rather than a one-time act** for the reason this whole plan is about: a sweep run
once during drafting is an obligation, and the command-vs-obligation gap says obligations decay. As
an issue with a recorded artifact it re-runs before intake, and its output
(`findings/verification-sweep.md`) is the evidence a reviewer can check instead of re-deriving.

**Each of the three review rounds produced a repair that was right in itself and wrong in context** —
pass 1 fixed one of two gates and certified both; pass 2's fix made a gate red without checking it
could go green; pass 3 found criteria added by pass 1's own fix that had never once been executed.
Epic 0 is the structural answer to that pattern.

### Which tree the gates and criteria execute against — and why `${SKILL_DIR}` is WRONG here

**Stated because red-team pass 3 found every gate `Test:` and 14 of 22 criteria pointed at the wrong
tree, and neither earlier pass caught it.**

`${SKILL_DIR}` resolves to the **installed** skill (`~/.claude/skills/yf-plan`). `AGENTS.md` is
explicit that the repo's `skills/` directory "is unreachable by the resolver, not merely stale", and
that **no `yf skills install` may run mid-execution**. Every artifact Epics 1–5 produce lands in the
repo tree. So a verification written against `${SKILL_DIR}` is a **permanent false RED**: it fails
after the work is done, and the only way to green it is the deploy the repo prohibits.

This is `TESTING.md`'s Tier-2 rule with its sign flipped. The documented hazard is a false GREEN —
*"validating an edit by exercising the installed copy tests the old skill"*. **The same fact produces
a false RED when the check asserts a behaviour the new code introduces**, and that is the case here.

**Rule for this plan: every verification of code this plan writes invokes
`uv run skills/yf-plan/scripts/<script>.py`, from the repo root.** `${SKILL_DIR}` appears only where
the plan invokes an *unmodified* skill as a tool. The two are not interchangeable and the distinction
is load-bearing.

### No `skills/yf-judgement/` directory is created

**Stated explicitly because the objective sentence promises a "skill" and nothing in the issue list
builds one.** Every artifact lands inside `yf-plan` (`plan_manager.py`, `doc_lint.py`,
`OKF-EXTENSION.md`, `review.toml`) or `yf-herdr` (SPEC). **`yf-judgement` ships as a CAPABILITY, not
as an invocation surface** — because the command-vs-obligation law forbids exactly that: a new
manually-invoked surface is what #145's finding 4 predicts will never be invoked, and this plan
would be adopting the defect it spent an experiment measuring.

An executor reading the objective without this paragraph would scaffold `skills/yf-judgement/`,
which is why it is here rather than implied.

### The #270 seam

Escalation E-3 resolved: making `plan-review.formula.toml` pour is **out of scope**, filed as
**#270**. This plan binds to `review-loop-check` and **keeps the escalation payload movable onto
that wisp without redesign** — #270 records that fixing the formula upgrades this trigger for free,
which is the reason the weaker trigger is acceptable now. **Epic 3 names that seam explicitly and
SC7 tests it.**

### The self-observation requirement

The operator's question, adopted as binding: *"If `yf-judgement` ships a trigger, ask what would
detect ITS trigger never firing."*

**The plan is otherwise on track to reproduce the exact defect it cites.** Four instances are on
record — `closable`, `plan_manager.py audit`, `retrospective_fields.py`, and #270's formula — and
**every one was found by hand, late, by someone who went looking.** EXP-001 measured that
`review-loop-check` is auditable **only because the script writes its own echo — "an accident of
design, not a general property."** Epic 5 makes that accident deliberate. **A trigger whose
non-firing is indistinguishable from a quiet period is not shippable** (SC6).

**Issue 5.1 is the load-bearing element; 5.2 and 5.3 are defence in depth, and the plan says so
rather than implying three equal remedies.** Only 5.1 operates at the top row of the
command-vs-obligation table — the script writes its own echo, so nothing has to remember. The other
two are weaker **by this plan's own evidence**:

- **5.2** fronts the report with a wrapper verb so `test_close_contract.py` enumerates it. That test
  detects an **added** step that ignores the envelope; it does **not** detect a **removed** step, and
  it never establishes that §6.4 was run.
- **5.3** is a tagged test, and **nothing mechanical runs it** — CI runs `cargo fmt/clippy/test` only,
  with zero `uv` rows, and its only other caller is `CHANGE-VALIDATION.md`, which EXP-001 established
  is prose.
- **The plan's own counter-example refutes both directly:** `retrospective_fields.py` has a
  `CHANGE-VALIDATION.md` recipe row, a tagged test, a README line and a schema reference — **and zero
  callers.** Enumeration-by-test demonstrably did not prevent the exact defect Epic 5 exists to
  prevent.

They are kept because defence in depth is cheap, **not** because they close the gap. SC6 is
therefore discharged by 5.1 alone and asserts a `log.md` content delta on the not-fired path;
SC6b carries 5.2 and 5.3 separately, so a reader can see which claim rests on what.

## Epics
### Epic 0: Prove the instruments before trusting them
- Issue 0.1: Run **every landed instrument that reads this bundle** — every gate `Test:`, every non-`manual:` Success Criterion, plus `recheck-criteria`, `gate_consistency.py`, `okf.py check`, `pour_fidelity.py` and `audit-close` — **as written, in the tree they execute in**, and record the exit code beside each in `findings/verification-sweep.md`. **Write one row per instrument in the exact grammar `RC <label> <exit-code>` at line start** (SC0 and SC0a grep that shape and no issue had specified it; a markdown table would leave both red), and **label the instrument rows with the literals `recheck-criteria` and `gate-consistency`** (SC0a greps them; the script is spelled `gate_consistency.py` and a faithful executor would otherwise write the underscore form and leave SC0a red forever). **Run each gate `Test:` and each clause-form criterion as a single `bash -c` string and record its COMPOSITE exit code**, and assert that **no criterion's command mutates the bundle it verifies** — a verification with a side effect changes the state a later row reads, which `recheck-criteria`'s in-table-order execution makes a live hazard — red-team pass 6's two blockers lived in the *composition* of a chain, not in any single instrument, and a per-instrument sweep cannot see them. The widening from "criteria" to "instruments" is red-team pass 5's structural finding: **the two instruments the first sweep omitted are the two that halt the plan**, and both take seconds to run
- Issue 0.2: Create the coarse upstream tracking issue required by `AGENTS.md`, linking the plan folder and its epic, and record its number in `assets/filed-issues.env` as `TRACKER_ISSUE`
  - depends-on: 0.1
- Issue 0.3: Re-run the full instrument sweep at reconcile time and rewrite the `RC` block, so the plan is proved at the END and not only at the start. **Record `SC0` and `SC0a` LAST, against the rewritten block** — both read the file the sweep writes, so evaluating them against the old block would write their own failure into the new one and leave them permanently red
  - depends-on: 1.6, 2.7, 3.5, 4.4, 5.4, 6.4


### Epic 1: Pin the severity vocabulary (SPEC-first; lands independently)
- Issue 1.1: Add the `REQ-DATA-*` requirement declaring the closed severity vocabulary and the cell grammar, with the living-amendment-log entry, and **write the ratified tokens on a single line beginning with the literal `Ratified severity vocabulary: ` in `skills/yf-plan/spec/data.md`** — gate 1 greps that exact marker
  - depends-on: 0.1
  - resolves-upstream: #269 (partial)
- Issue 1.2: Decide and record the vocabulary's membership — whether `medium-high` and a qualifier suffix (`medium (blocking)`) are legal
  - depends-on: 1.1
- Issue 1.3: Implement the `cell-vocabulary` check kind in `doc_lint.py`, locating the column by header name rather than position
  - depends-on: 1.2
- Issue 1.4: Add the `[[checks]]` block to `review.toml` at `R` severity, in both the `_shared/` and vendored copies
  - depends-on: 1.3
- Issue 1.5: Amend `REQ-AGENT-041` and `red-team.md`'s output template to emit one severity shape
  - depends-on: 1.2
- Issue 1.6: Create `skills/yf-plan/fixtures/severity-vocabulary/off-vocabulary-med.md` (SC1 greps that exact path) — an off-vocabulary fixture that is **schema-clean apart from the off-vocabulary cell** — any other `E` finding would make `doc_lint` exit 1 and turn SC1 red for an unrelated reason, and add a tagged test asserting the check reports and never fails a historical bundle
  - depends-on: 1.4

### Epic 2: The escalation artifact
- Issue 2.1: Add the `REQ-*` requirements for `escalations.md` — presence-optional, `type: Escalation`, cloning REQ-PORT-ACT-RETROSPECTIVE's activation pattern verbatim
  - depends-on: 1.1
  - resolves-upstream: #269 (partial)
- Issue 2.2: Write the `escalations.toml` schema to both the `_shared/` and vendored paths. **The schema stem — and therefore its `type` key and the `--type` token gate 2 invokes — is `escalations`, PLURAL**, matching the document base name per the `document_types/` convention that all 17 existing schemas follow; `doc_lint.py:164` hard-rejects a schema whose `type` differs from its file stem, and an unknown `--type` returns INCONCLUSIVE rather than failing, so the singular would leave gate 2 permanently unresolvable rather than red. (Issue 2.1's `type: Escalation` is the OKF **frontmatter** vocabulary — a separate axis, unaffected.) The schema validating every closed domain and asserting `recommended` names one of `alternatives`. **Name the rule check `recommended-in-alternatives`** (gate 2 asserts on that literal), **declare the checks `E`, AND set `promote = false` (REQ-DATA-053), as `plan.toml` already does.** Both halves are required and an earlier draft had the rationale backwards: `escalations.md` is authored during EXECUTE, and `STATUS_SEVERITY` demotes `ERROR -> REPORT` at `executing` — **the only status the artifact ever lives at** — so a bare `E` could never fail in production and the `recommended`-names-an-alternative rule would be unenforceable exactly where it matters. `promote = false` exempts the type from status-driven severity rewriting, which is the mechanism that already exists and that no issue had named
  - depends-on: 2.1
- Issue 2.3: Add the `OKF-EXTENSION.md` §1 vocabulary row and §1a glob row, covering both the `docs/plans/*` and `Incubator/*/plans/*` roots
  - depends-on: 2.1
- Issue 2.4: Add the `_INDEX_MEMBERS` entry and the generator, calling `_stamp_okf_type` and `_ensure_index_lists_member`
  - depends-on: 2.3
- Issue 2.5: Implement `escalation-raise` and `escalation-resolve`. Flags: `escalation-raise` takes `--question`, `--alternative` (repeatable), `--recommended`, `--on-no-answer`, `--detected-by` — the names gate 2 invokes; `escalation-resolve` takes `--answer`, the name SC3 invokes. `--detected-by` is a `click.Choice` over exactly `self-report | operator | mechanical-check`. Ids are append-only; `state` is mutable over `raised -> answered -> resolved -> withdrawn`. **Raise this plan's own escalations into its own bundle: `ESC-001`, left DELIBERATELY `raised` as SC6c's fixture, and `ESC-002`, resolved.** Two are required and neither is decorative — SC5 proves batching, which needs `raised >= 2`, and SC6c proves an open escalation produces a close-time signal, which needs exactly one still `raised`. **`ESC-001` must not be answered even if the operator answers the underlying question**; record any real answer on a further entry. Read by SC2b, SC3, SC5, **SC6c**, SC10 — an earlier draft's cross-reference list omitted SC6c, which is where a deterministic contradiction entered. `escalation-resolve` emits `prior_entries_unchanged` **computed from a pre/post hash of the entries it did not touch**, never from its own assertion. **Specify the lifecycle edge E-4 exposed:** an escalation whose recommended default was taken **without an answer arriving** is `resolved`, with `answer` recording the default that was taken and by whom — not left `raised`, which would make every fire-and-forget escalation trip Issue 5.4's close-time warning
  - depends-on: 2.2, 2.4
- Issue 2.6: Assert the audit writes nothing — `escalations.md` is added to no presence list, and record why `plan-retrospective.md` was rejected as the escalation surface
  - depends-on: 2.4
  - resolves-upstream: #145 (partial)
- Issue 2.7: File the missing `yf-drift-check` edge as a follow-on issue, so #145's announced mitigation stops being vapour, **recording in the body that the escape/stop `taxonomy` has four homes** (SC2d greps that word); record its number in `assets/filed-issues.env` as `DRIFT_EDGE_ISSUE`
  - depends-on: 2.1

### Epic 3: Bind the trigger to a command, at a boundary
- Issue 3.1: Extend `review-loop-check` to emit the payload **under the top-level JSON key `escalation`** (SC4 asserts `has("escalation")`), preserving its exit-3 contract
  - depends-on: 2.5
  - resolves-upstream: #269 (partial)
- Issue 3.2: Add the second-party-result trigger at the `Agent`-returns-findings boundary, invoking **`escalation-raise`** — the verb `--assert-invocation` looks for
  - depends-on: 2.5
- Issue 3.3: Implement the push as one line naming the artifact, batched to `REQ-HERDR-026`'s three existing classes, and emit `pushes` (the count actually sent for a boundary) so batching is observable rather than asserted
  - depends-on: 3.1
- Issue 3.3b: Pair every push with an idempotent token stamp, so the parent's poll is a genuine backstop rather than a restatement of the push
  - depends-on: 3.3
- Issue 3.3c: Verify delivery structurally rather than by exit code, because `herdr agent prompt` returns `agent_not_found` at exit 0
  - depends-on: 3.3
- Issue 3.4: Name and test the #270 seam — the payload must move onto the `plan-review` wisp gate without redesign
  - depends-on: 3.1
- Issue 3.5: Implement `escalation-report`, emitting `raised`, `answered`, `no_answer_taken` and `pushes`. **`raised` is the CUMULATIVE count of escalations ever raised, not the count currently in `state: raised`** — SC5 needs `>= 2` (both entries) while SC6c needs exactly one *currently* raised, and the two are only consistent under this reading — recording per escalation when it was raised, whether it was answered, and whether `on_no_answer` was taken — the instrumentation research 005 §8.4 names as the missing half
  - depends-on: 3.1

### Epic 4: yf-herdr SPEC amendments (one-hop only)
- Issue 4.1: Amend `REQ-HERDR-024` with a decision procedure for a PUSHED question, not only a `blocked` one, and add the third arm — look, answer, forward
  - depends-on: 0.1
  - resolves-upstream: #264 (partial)
- Issue 4.2: Add a REQ recording that `herdr agent prompt` returns `agent_not_found` at exit 0, so delivery is verified structurally
  - depends-on: 4.1
- Issue 4.2b: Add `skills/yf-herdr/scripts/test_herdr_channel.py` asserting that exit-0 behaviour against a nonexistent target, so the SPEC claim has code behind it. No file of that name exists today
  - depends-on: 4.2
- Issue 4.3: Add #264's proposed sibling to `REQ-HERDR-025` — `working` shall not be read as evidence of phase advancement
  - depends-on: 4.1
- Issue 4.4: Record provenance-derived autonomy: `YF_PARENT_PANE` set implies a controller exists, so continue-or-ask; unset implies a human is present
  - depends-on: 4.1

### Epic 5: Make yf-judgement observable in its own absence
- Issue 5.1: Make the trigger write its own echo unconditionally, on both the fired and not-fired paths. **The echo line begins with the literal `judgement: not-fired` on the not-fired path and `judgement: fired` on the fired path** — SC6 and SC6d assert on those exact strings, and `test("judgement: fired")` does **not** match `judgement: not-fired`, so the two are genuinely independent literals. Implement `judgement-echo-check` to emit `lines_added` and `added_line` **computed by diffing `log.md` before and after it invokes the trigger itself**, so the report is an external observation rather than the trigger's self-assertion
  - depends-on: 3.1
- Issue 5.2: Add the never-fired report to the §6.4 advisory chain, fronted by the `plan_manager.py` wrapper verb **`judgement-never-fired-report`** (SC6b greps the substring `judgement` in `--list-steps` output) so `test_close_contract.py` enumerates it
  - depends-on: 5.1
- Issue 5.3: Add `test_close_contract.py --assert-invocation <verb>` and `--list-steps --json` — the latter must **short-circuit before pytest and emit JSON as the SOLE stdout**, since pytest's session banner otherwise corrupts the stream (measured: `jq` parse error, rc=5), which **exit non-zero on an unrecognised verb** (today the flag is silently swallowed and the bare suite passes, so the criterion is green before the work), plus a tagged test that fails if the trigger is removed from its invocation site
  - depends-on: 5.1
- Issue 5.4: Emit a `W` finding with `item` **`escalation-open`** from the close-time chain when any escalation is still `state: raised` at `reconciling` or `complete`, so an unanswered question has a failure signal
  - depends-on: 2.5, 5.1

### Epic 6: Make the detector re-decidable — NO ARTIFACT SHIPS, and no code is written
- Issue 6.1: Specify the `log.md` re-scope guard as a predicate — no `drafting:` bullet between pass 1 and the firing pass — and record that it is FITTED to the four false positives it was derived from. **Target artifact: `findings/detector-redecision.md` in this bundle**
  - depends-on: 1.1
- Issue 6.2: Specify the blind labelling procedure and name the nine held-out bundles, recording that the parser repair is a PREREQUISITE OWNED BY THE RESEARCH BUNDLE and not by this plan. **Target artifact: the same `findings/detector-redecision.md`**
  - depends-on: 6.1
- Issue 6.3: File the re-measurement as a gated follow-on issue, recording that the hand-audit label must be re-established **blind** before any 2x2 is quoted and naming the **held-out** set; record its number in `assets/filed-issues.env` as `REMEASURE_ISSUE`
  - depends-on: 6.2
- Issue 6.4: Correct upstream issue #273 to the per-plan unit over one stated population (4/5 vs 2/5 across the five post-plan-045 plans exceeding the bound), replacing the withdrawn per-event framing and the withdrawn "factor of five"
  - depends-on: 6.1
  - resolves-upstream: #273 (partial)

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator
- Instructions: Approval of this plan also RATIFIES THE SEVERITY VOCABULARY, in the same operator turn. Every input to that decision already exists in `findings/exp-002-severity-vocabulary-census.md` and nothing produced during execution adds to it, so deferring it to a mid-run gate would spend a second operator turn for no new evidence — and would serialise the whole plan behind an Epic-1 chain containing a human gate. Choose one: (a) `high|medium|low` only — rejects 42 of the 45 observed tokens; (b) plus the `medium-high`/`low-medium` family — the corpus uses these deliberately; (c) (b) plus a legal qualifier suffix such as `medium (blocking)`. Recommended: (b), which admits the deliberate uses while still excluding every downgraded-severity and free-text cell. **RESOLVED 2026-08-29: the operator approved with option (b).** `high` | `medium` | `low` plus the `medium-high` / `low-medium` family; **(c) declined — a qualifier suffix is not legal**, because `medium (blocking)` is precisely the token that fired the detector on `plan-026`. Both halves of this gate were satisfied in one operator turn, as these Instructions require.

### Capability Gate: severity vocabulary membership recorded
- Type: auto
- Condition: The vocabulary ratified at the Start Gate is written into the SPEC as an explicit token list under the literal marker `Ratified severity vocabulary:`, so the downstream check has a declared set to read
- Test: set -o pipefail; grep -qE '^Ratified severity vocabulary: ' skills/yf-plan/spec/data.md
- Blocks: 1.3, 1.4, 1.5
- Instructions: **This gate asserts ONLY the SPEC residue that Issues 1.1 and 1.2 produce — neither of which it blocks.** An earlier draft asserted a `cell-vocabulary` finding from `doc_lint` while blocking the very issue that implements it — a gate whose condition depended on evidence produced inside its own `Blocks` set, i.e. a deadlock that could never resolve. Two review passes each made this gate "fail today" without checking it could ever go green; red-team pass 3 caught the cycle. The `cell-vocabulary` assertion now lives in **SC1**, where it belongs. The DECISION is made at the Start Gate; this gate confirms it was WRITTEN DOWN, which is the only part of a ratification a command can establish. **It greps a literal MARKER, not a `REQ-*` id** — every id in `spec/data.md` is numeric and sequential, so an assertion naming one would guess a number the executor has not yet allocated and stay red forever.

### Capability Gate: escalation schema round-trips
- Type: auto
- Condition: An INVALID escalation is rejected and a VALID one accepted, in a scratch bundle, at a status where the linter's findings are not demoted
- Test: set -o pipefail; D=$(mktemp -d) && cp -R "${PLAN_DIR}" "$D/b" && rm -f "$D/b/escalations.md" && sed 's/^status: .*/status: review/' "$D/b/plan.md" > "$D/p" && mv "$D/p" "$D/b/plan.md" && printf -- '---\ntype: Escalation\nokf_spec: OKF-PLAN\n---\n# Escalations\n\n## ESC-001\n\n| Field | Value |\n| :-- | :-- |\n| `question` | q |\n| `alternatives` | a; b |\n| `recommended` | NOT-AN-ALTERNATIVE |\n| `on_no_answer` | a |\n| `detected_by` | mechanical-check |\n| `state` | raised |\n' > "$D/invalid.md"; uv run skills/yf-plan/scripts/doc_lint.py --type escalations --path "$D/invalid.md" --json > "$D/inv.json"; jq -e '.files_checked >= 1 and ([.findings[]|select(.check=="recommended-in-alternatives")]|length >= 1)' < "$D/inv.json" && uv run skills/yf-plan/scripts/plan_manager.py escalation-raise "$D/b" --question q --alternative a --alternative b --recommended a --on-no-answer a --detected-by mechanical-check --json > "$D/raise.json" && uv run skills/yf-plan/scripts/doc_lint.py --type escalations --path "$D/b/escalations.md" --json > "$D/ok.json" && jq -e '.files_checked >= 1 and .errors == 0' < "$D/ok.json"; rc=$?; rm -rf "$D"; exit $rc
- Blocks: epic:3
- Instructions: This test FAILS TODAY and is meant to — the verbs it calls do not exist until Issues 2.2–2.5 land, which is what makes it a gate rather than a green rubber stamp. It copies an EXISTING valid bundle rather than calling `init`, because `init` takes no `--plans-root` and would write into the live tree. **`${PLAN_DIR}` is the gate's own bundle, supplied at pour time** — an earlier draft hard-coded `docs/plans/plan-059-…`, which breaks if the bundle moves to an incubator root or the gate runs from anywhere but the repo root. **Three things in this line are load-bearing and each closes a measured defect.** (1) `sed`ing the scratch copy's `status:` to `review` — `doc_lint`'s `STATUS_SEVERITY` demotes `{W,E} -> R` at `approved`/`executing`/`complete`, and this gate fires mid-execution, so **without the forced status `.errors == 0` CANNOT FAIL** and the whole assertion collapses to "the type has a schema". Measured: a stripped `plan.md` yields 8 errors at `review` and 0 at `approved`. (2) The **positive control**, which asserts **by check name** (`recommended-in-alternatives`), not merely `errors >= 1` — the latter is satisfied by *any* error finding and would test "the linter emits errors", not the rule the plan calls load-bearing. It also **writes the invalid document directly, to a path OUTSIDE the bundle (`$D/invalid.md`)**. Both halves are required: writing it directly avoids the layering contradiction (Issue 2.2 requires `escalation-raise` to validate on write, so routing the positive control through it would kill a *correct* implementation at step 1); and keeping it outside the bundle is what lets step 3 assert `.errors == 0` at all — **ids are append-only, so an invalid `ESC-001` written INTO the bundle would survive the valid raise and make the gate permanently red on every correct implementation.** Red-team pass 5 caught that; four passes had read past it because the gate is red today for the reason it advertises. **(3) The positive control is REDIRECTED to a file and read by a separate `jq`, deliberately OFF the `&&` chain** — `doc_lint` exits **1** whenever an `E` finding is present, which is exactly what this step demands, so under `set -o pipefail` its expected success would abort the chain before `escalation-raise` ever ran. Red-team pass 6 measured that: `jq` printed `true` and the chain still returned 1. **A command whose success exit is non-zero must not be a link in an `&&` chain.** The scratch copy's own `escalations.md` is removed first, since this plan is the natural first user of the verb and a pre-existing `ESC-001` would make the resolve step target the wrong entry. And the status rewrite uses a redirect-and-move rather than `sed -i.bak`, which leaves a `plan.md.bak` that `okf.py check` reports as an unindexed bundle member. (3) **The `--type escalations` flag:** `doc_lint` routes by path glob, so a bundle under `$(mktemp -d)` is `not-selected` and a bare `--path` lint returns `files_checked: 0, verdict: PASS, exit 0` **for any content whatsoever** — the #181 silent green, which would have re-introduced the very defect this gate was rewritten to remove, merely displaced until Epic 2 landed. The `jq -e` assertion is the second half of the same guard: it fails the gate on `files_checked: 0` even if the type routing is later broken. It is `test_class: probe` under the §5.2d vocabulary: it creates and removes its own scratch bundle on both exit paths and touches no operator state. A schema whose `recommended` need not name one of its `alternatives` is not a schema, so the lint step is the load-bearing half.

### Capability Gate: upstream writes authorized
- Type: human
- Approvers: operator
- Condition: The operator has authorized this plan's batch of outward-facing GitHub writes
- Blocks: 2.7, 6.3, 6.4, 0.2
- Instructions: `context.md` declares issue create/comment a **stop class**, operator-authorized individually and never batched. Four issues file or edit GitHub issues — see this gate's `Blocks` set. **The #269 correction comment is NOT among them — it was already posted at 2026-08-28T23:24Z** and an earlier draft still scheduled it. Without this gate the autonomous executor either halts three times with nothing to resolve against, or writes upstream unauthorized. **This gate declares no `Test:` deliberately** — a green command can never establish authorization, so the sweep reports INCONCLUSIVE, which is the honest reading. Present the exact `gh` commands and their bodies before resolving.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **`yf-judgement`'s own trigger is never invoked** — the defect this plan exists to avoid, now recorded four times including inside the machinery being inherited. | high | Epic 5 in full. Bind to an existing 4/5 invocation path (Epic 3) rather than a fresh 0% one; write the echo on the not-fired path too (5.1); front the report with a `plan_manager.py` verb so CI enumerates it (5.2); fail a test if the call site is removed (5.3). **SC6 gates on it.** |
| R2 | **Two skills, one append-only write verb.** `yf-judgement`'s open questions and `yf-retrospective`'s closed adjudications would share a non-updatable stream, and `retrospective-report` would count an unanswered question as a recorded event. | high | Separate file with its own mutable `state` (Epic 2). `escalations.md` is never a retrospective entry kind. |
| R3 | **The escalation channel silently fails.** `agent_not_found` at exit 0; a push into a `blocked` parent is swallowed; the token channel is display-only. | high | Structural delivery verification (3.3) plus the SPEC record (4.2). **The artifact is durable regardless** — this is why write-then-notify is the architecture and not a preference. |
| R4 | **Goodhart, in a NEW direction #269 treats as inherited.** #145's actor has no escape hatch; `yf-judgement`'s does — an agent that can escalate instead of finishing has an incentive to reclassify difficulty as under-specification. | medium | `detected_by` is a `click.Choice` and second-party residue is required (C3); `evidence` defaults to the literal `unverified` so an unsubstantiated escalation is self-identifying; Epic 5's echo makes the escalation RATE visible, not just the escalations. |
| R5 | **The escape/stop TAXONOMY gains a fourth home** — `plan-retrospective.md`, `retrospective_fields.py`, `yf-herdr` SPEC §3, and now `escalations.md` — and #145's promised `yf-drift-check` edge does not exist. | medium | **Issue 2.7 files the missing edge**, so it stops being vapour. Note the distinction an earlier draft blurred: **Epic 1 pins the SEVERITY vocabulary, which is a different object from this taxonomy** and does not mitigate it. The `yf-herdr` §3 collision (its *"Premise refuted at execution"* is the corpus's `reasoned-past-a-documented-fact` under another string) is recorded in 4.1. |
| R6 | **The detector is later shipped on the broken numbers.** Every published D3 characteristic rests on a parse measured to delete HIGH, biased toward HIGH. | high | **Epic 6 ships no detector and writes no code.** It specifies the re-scope guard (6.1), the blind labelling procedure and the nine held-out bundles (6.2), and files the re-measurement (6.3) recording that **no 2x2 may be quoted until the hand-audit label is re-established** and that **no expected firing count may be asserted as a literal**. *Two earlier drafts got this wrong: one contained a real code change to a file not in this repository, overriding escalation E-4's resolved default; the other left R6 citing that issue and the `43` literal the Approach forbids.* SC9 tests the accurate claim. |
| R9 | **`escalation-resolve` mutates a row inside a committed markdown artifact — a new capability class in this repo.** Every existing bundle write verb is append-or-regenerate, and `append_retrospective` is append-only *deliberately*. It interacts with index regeneration and with concurrent sessions, which D-5 establishes are a live hazard here. | medium | Write-temp-then-rename, never in-place truncation; an idempotence test asserting `escalation-resolve` never reorders or drops prior entries; ids stay append-only so a lost mutation is detectable rather than silent. |
| R7 | **N-hop is built on a topology that does not exist.** Measured depth 1, fan-out 2; a child knows one opaque pane id. | medium | N-hop is **out of scope and labelled a bet**. Only the two free seams ship — a bundle-scoped `id` and `asked_of` — so the generalisation is additive rather than a redesign. **No hop counter is seeded.** |
| R8 | **This plan corrects research 005 on the operator's own branch.** | low | Escalation E-4 raised; default is that plan-059 does not edit PR #267 and files one issue instead. |

## Success Criteria

**Every clause below uses a CONCRETE path — no `<placeholder>` tokens.** Red-team pass 5 measured
that a `<placeholder>` is a bash **redirection**: the shell aborts before anything runs, `jq` gets
empty stdin, and the exit is `4`. Measured consequence: `recheck-criteria` returned **verdict FAIL,
rc=1**, which at §6.4 prints `FAIL-LOUD … do NOT set 'complete'` — **the plan could not close.**

The three genuinely-unknown values (issue numbers not yet filed) are sourced from
`assets/filed-issues.env`, which Issues 0.2, 2.7 and 6.3 write as they file. Every piped clause
begins `set -o pipefail`, because `doc_lint` exits **2 with `errors: 0`** when it cannot run, and
without it the pipeline's status would be `jq`'s alone.

**Corpus comparison, re-derived after the operator flagged an earlier overstatement.** An earlier
draft claimed comparable bundles carry *"zero"* placeholder criteria. **That is false.** Measured
over the Success Criteria tables of `plan-050`, `052`, `054` and `055`: **2 of 115 clause-form rows
carry a `<token>` (1.7%)** — and at least one, `plan-050`'s `SC6` (`--path <an empty selected
file>`), is the same latent defect. plan-059 carried **15 of 21 (71%)**. The real claim is a **~40x
rate difference**, not an absence.

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC0a | **The intake sweep covers every landed instrument, not only the criteria the author chose to run** — red-team pass 5's structural finding was that the two instruments the first sweep omitted are the two that halt the plan. The `recheck[-]criteria` bracket is deliberate: `recheck-criteria`'s self-reference guard scans the executed command string, so a literal mention would make this row silently `skipped-self-reference` rather than evaluated | `set -o pipefail; grep -qE '^RC recheck[-]criteria ' docs/plans/plan-059-james-dixson-55137e/findings/verification-sweep.md && grep -qE '^RC gate-consistency ' docs/plans/plan-059-james-dixson-55137e/findings/verification-sweep.md` -> exit 0 | 0.1 |
| SC0 | **Every landed instrument that reads this bundle has been re-run after execution and every recorded row that was non-zero at intake is now zero** — and no recorded code is a `click`/`jq` usage error | `set -o pipefail; test -s docs/plans/plan-059-james-dixson-55137e/findings/verification-sweep.md && ! grep -qE '^RC [A-Za-z0-9_.-]+ [1-9]' docs/plans/plan-059-james-dixson-55137e/findings/verification-sweep.md` -> exit 0 | 0.3 |
| SC0b | The coarse upstream tracker required by `AGENTS.md` exists and names this plan | `set -o pipefail; . docs/plans/plan-059-james-dixson-55137e/assets/filed-issues.env && gh issue view "$TRACKER_ISSUE" --json body \| jq -e '.body \| test("plan-059")'` -> exit 0 | 0.2 |
| SC1 | The severity vocabulary is declared in SPEC, ratified at the Start Gate, recorded under its marker, and **mechanically checked by name** | `set -o pipefail; uv run skills/yf-plan/scripts/doc_lint.py --type review --path skills/yf-plan/fixtures/severity-vocabulary/off-vocabulary-med.md --json \| jq -e '[.findings[]\|select(.check=="cell-vocabulary")]\|length >= 1'` -> exit 0 | 1.1, 1.2, 1.3, 1.4 |
| SC1b | The check **reports on a real historical bundle and never fails it** — it ships at `R`, so an assertion that no `E` finding exists would be true by construction | `set -o pipefail; uv run skills/yf-plan/scripts/doc_lint.py --type review --path docs/plans/plan-027-james-dixson-a59656/reviews/pass-1.md --json \| jq -e '.errors == 0 and ([.findings[]\|select(.check=="cell-vocabulary")]\|length >= 1)'` -> exit 0 | 1.6 |
| SC1c | The red-team emits exactly one severity shape, so the pin binds new passes and not only old tables | manual: the emission template is prose an agent follows; only a live review pass can show which shape it wrote | 1.5 |
| SC2b | `escalations.md` is routed **by path**, listed in `index.md`, and typed — never falling through to `Concept`, and never returning the #181 silent green | `set -o pipefail; uv run skills/yf-plan/scripts/doc_lint.py --classify --path docs/plans/plan-059-james-dixson-55137e/escalations.md --json \| jq -e '.class == "selected"'` -> exit 0 | 2.1, 2.2, 2.3, 2.4, 2.5 |
| SC2c | A bundle with **no** `escalations.md` produces no escalation-related audit finding of any severity — verified against a bundle that carries **26 real findings**, so the assertion is not vacuously true over an empty array | `set -o pipefail; uv run skills/yf-plan/scripts/plan_manager.py audit docs/plans/plan-050-james-dixson-d0414b --json-output \| jq -e '[.findings[]\|select((.item + " " + .detail) \| test("escalation"))]\|length == 0'` -> exit 0 | 2.6 |
| SC2d | #145's announced `yf-drift-check` edge is filed, and its body names the edge | `set -o pipefail; . docs/plans/plan-059-james-dixson-55137e/assets/filed-issues.env && gh issue view "$DRIFT_EDGE_ISSUE" --json body \| jq -e '.body \| test("drift-check") and test("taxonomy")'` -> exit 0 | 2.7 |
| SC3 | The lifecycle `raised -> answered -> resolved` is expressible **without a second entry**, with ids append-only and prior entries provably untouched. **Runs against a SCRATCH COPY** — `recheck-criteria` executes clauses **in table order**, so resolving the live `ESC-001` here would leave SC6c (which requires a still-`raised` escalation) deterministically false, and SC0's all-rows-zero rule would turn that into a completion blocker. It also removes a non-idempotent re-run: the close chain evaluates this table at least three times | `D=$(mktemp -d) && cp -R docs/plans/plan-059-james-dixson-55137e "$D/b" && uv run skills/yf-plan/scripts/plan_manager.py escalation-resolve "$D/b" ESC-001 --answer x --json > "$D/o.json"; jq -e '.state == "resolved" and .prior_entries_unchanged == true' < "$D/o.json"; rc=$?; rm -rf "$D"; exit $rc` -> exit 0 | 2.5 |
| SC4 | The trigger carries an **escalation payload**, not merely the exit code it already had. **No `pipefail`, and the verb is redirected rather than piped** — `review-loop-check` exits **3** by contract on the escalating path, which Issue 3.1 preserves, so a piped `pipefail` form would assert `exit 0` against a verb whose success is 3 and be false forever | `uv run skills/yf-plan/scripts/plan_manager.py review-loop-check docs/plans/plan-050-james-dixson-d0414b --json > /tmp/rlc.json; jq -e 'has("escalation") and .escalation.on_no_answer != null' < /tmp/rlc.json` -> exit 0 | 3.1 |
| SC4b | The second-party-result trigger is present at its invocation site, and `--assert-invocation` **rejects an unknown verb** rather than swallowing it | `set -o pipefail; uv run skills/yf-plan/scripts/test_close_contract.py --assert-invocation escalation-raise && ! uv run skills/yf-plan/scripts/test_close_contract.py --assert-invocation no-such-verb` -> exit 0 | 3.2, 5.3 |
| SC5 | Escalations **batch**: two or more raised, **at most one** push. Both earlier forms were unsatisfiable — `== 1` is a literal over a side effect that is legitimately **0** when `YF_PARENT_PANE` is unset (Issue 4.4's human-present arm), and `>= 1 and < .raised` retained that *and* added a second impossibility, since Issue 2.5 raised exactly one escalation so `pushes < 1` could never hold alongside `pushes >= 1`. `.pushes <= 1` is satisfied by the degraded no-herdr topology **and** by a real batched push, which is what makes it topology-independent | `set -o pipefail; uv run skills/yf-plan/scripts/plan_manager.py escalation-report docs/plans/plan-059-james-dixson-55137e --json \| jq -e '.raised >= 2 and .pushes <= 1'` -> exit 0 | 2.5, 3.3, 3.5 |
| SC5b | The push is verified **structurally**, and a stamped token makes the parent's poll an independent backstop | manual: `herdr agent prompt` returns `agent_not_found` at exit 0, so the check is that the code reads the returned payload rather than `$?` — an inspection of the call site | 3.3b, 3.3c |
| SC6 | **`yf-judgement`'s own non-firing is distinguishable from a quiet period** — verified as a `log.md` CONTENT DELTA on a **PRUNED SCRATCH COPY**, because on the live bundle the trigger provably FIRES (`review-loop-check` counts `reviews/pass-*.md`, which only grows) and `added_line` would read `judgement: fired` forever | `D=$(mktemp -d) && cp -R docs/plans/plan-059-james-dixson-55137e "$D/b" && rm -f "$D"/b/reviews/pass-*.md && uv run skills/yf-plan/scripts/plan_manager.py judgement-echo-check "$D/b" --json > "$D/o.json"; jq -e '.lines_added == 1 and (.added_line \| test("judgement: not-fired"))' < "$D/o.json"; rc=$?; rm -rf "$D"; exit $rc` -> exit 0 | 5.1 |
| SC6d | The **fired** path also echoes — on an UNPRUNED scratch copy, which fires identically (the pass files are copied) while touching nothing live. `judgement-echo-check` invokes the trigger and so appends to `log.md` by construction, and the close chain evaluates this table at least three times; running it against the live bundle would violate Issue 0.1's own no-mutation rule | `D=$(mktemp -d) && cp -R docs/plans/plan-059-james-dixson-55137e "$D/b" && uv run skills/yf-plan/scripts/plan_manager.py judgement-echo-check "$D/b" --json > "$D/o.json"; jq -e '.lines_added == 1 and (.added_line \| test("judgement: fired"))' < "$D/o.json"; rc=$?; rm -rf "$D"; exit $rc` -> exit 0 | 5.1 |
| SC6b | The never-fired report is enumerated by the close contract **by name** — the bare suite passes today, so asserting its exit code alone proves nothing | `set -o pipefail; uv run skills/yf-plan/scripts/test_close_contract.py --list-steps --json \| jq -e '[.steps[] \| select(test("judgement"))] \| length >= 1'` -> exit 0 | 5.2, 5.3 |
| SC6c | **An escalation still `raised` at close produces a signal** — the plan's own thesis applied to its own artifact | `set -o pipefail; uv run skills/yf-plan/scripts/plan_manager.py audit-close docs/plans/plan-059-james-dixson-55137e --json \| jq -e '[.findings[]\|select(.item=="escalation-open")]\|length == 1'` -> exit 0 | 5.4 |
| SC7 | The escalation payload moves onto the #270 `plan-review` wisp gate **without redesign** | manual: #270 is out of scope, so the seam is proved by inspection against the formula's gate step, not by running it | 3.4 |
| SC8 | The one-hop predicate has **three arms — look, answer, forward** — and covers a PUSHED question, not only a `blocked` one | manual: a SPEC wording change; conformance is a read of REQ-HERDR-024, not an exit code | 4.1 |
| SC8b | The three undocumented channel facts are recorded in SPEC **and the testable one has a test** | `uv run skills/yf-herdr/scripts/test_herdr_channel.py` -> exit 0 | 4.2, 4.2b, 4.3, 4.4 |
| SC9 | **Epic 6 writes NO code and ships NO artifact** — it specifies a future decision and files issues | manual: epic emptiness is a property of the epic STRUCTURE, not of any command's exit code. Verified by confirming Epic 6's four issues produce only specifications and filed issues, and that no issue outside Epic 6 names the detector | 6.1, 6.2 |
| SC9b | The command-vs-obligation law is corrected upstream **at the per-plan unit over one stated population** | `set -o pipefail; gh issue view 273 --json body \| jq -e '.body \| test("4 ?/ ?5") and test("2 ?/ ?5") and (test("factor of five") \| not)'` -> exit 0 | 6.4 |
| SC9c | The re-measurement is filed **with its blind-labelling precondition in the body** | `set -o pipefail; . docs/plans/plan-059-james-dixson-55137e/assets/filed-issues.env && gh issue view "$REMEASURE_ISSUE" --json body \| jq -e '.body \| test("blind") and test("held-out")'` -> exit 0 | 6.3 |
| SC10 | The cost-ratio premise the escalation path rests on is **instrumented**, closing research 005 §8.4's own prescription | `set -o pipefail; uv run skills/yf-plan/scripts/plan_manager.py escalation-report docs/plans/plan-059-james-dixson-55137e --json \| jq -e '.raised != null and .answered != null and .no_answer_taken != null'` -> exit 0 | 3.5 |
