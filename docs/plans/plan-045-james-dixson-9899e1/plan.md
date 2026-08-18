---
type: Plan
okf_spec: OKF-PLAN
id: plan-045-james-dixson-9899e1
author: james-dixson
created: '2026-08-17'
status: approved
deliverable_class: standard
fingerprint: 4954ac04905405e370806c149cc4e077725264ad9f39301951dd016d9fdb88fc
---
# Plan: Make plan execution and review autonomous by default, with human gates frontloaded: self-resolving review cycles, a non-stopping coordinator loop, an execute-start gate sweep, and push-based herdr delegation

**ID:** plan-045-james-dixson-9899e1
**Author:** james-dixson
**Created:** 2026-08-17
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** 4954ac04905405e370806c149cc4e077725264ad9f39301951dd016d9fdb88fc

## Objective
Make plan execution and review autonomous by default, with human gates frontloaded: self-resolving review cycles, a non-stopping coordinator loop, an execute-start gate sweep, and push-based herdr delegation

## Motivation

Across the last several plan executions the operator observed that plans **do not run
unattended**: they stop between epics rather than only at pre-declared human gates, and the
planning phase is equally conservative — each red-team cycle needs a manual acknowledgement
before the next one runs. The operator's requirement, stated directly:

> "when a plan is executed i want to have it run completely autonomously and only stop at human
> gates, further, ideally those human gates should be as 'frontloaded' as possible so the operator
> can answer questions/perform actions before the bulk of the coding work runs whenever possible…
> i want things to run autonomously as much as possible by default and only seek manual, operator
> acknowledgement when explicitly asked or when explicitly necessary."

This is a **class**, not a one-off — it reproduced across plans and in both phases — so per the
deviation-mining rule the fix belongs upstream in the skills, not in any single plan.

Diagnosis (this session, verbatim-cited, see Investigation Findings) found **three independent
textual causes** plus a fourth in the delegation layer. None is a model quirk; all four are
skill-text defects. One **corroborating observation (n=1, uncontrolled)**: plan-044 was
launched with a hand-written autonomy clause in its prompt and ran unattended across multiple
epics. No counterfactual exists — no plan-044 was launched *without* the clause — so this suggests
rather than demonstrates. The four textual causes are independently measured and stand without it.

Who is affected: every operator running `/yf-plan execute`, and every delegated herdr session.
The cost is not just interruption — a stop mid-DAG splits the work across context windows and
invites the operator to re-decide things the plan already settled.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#162](https://github.com/dixson3/yoshiko-flow/issues/162) | plan-045-james-dixson-9899e1 execution tracking | tracker | The single coarse tracking issue for this plan-scale effort (AGENTS.md convention). Stamped onto the epic as `external_ref` at pour (REQ-PLAN-073) | — |
| #110 | herdr: leverage `herdr agent *` to launch and monitor agent sessions from a primary session | partial | **In:** the child to parent push channel, the parent handle handoff, and the mandatory autonomy contract (exp-005 verified all three live). **Out:** #110's broader vision of dispatching bead work to secondary sessions of *other* harness kinds — that is a fan-out redesign, not an autonomy fix | Epic 5 |
| #145 | New skill: yf-retrospective — measure escape rate and enforce a fix+prevention contract | partial | **In:** the EMIT side only — `plan-retrospective.md`, its schema, and the write sites (D-6). Answers #145's own Open question 1 (*"where exactly does intra-plan capture write"*). **Out:** escape-rate measurement, adjudication, the fix+prevention contract, the frontloading consumer, **and the `DRIFT-CHECK.md` yf-plan ↔ yf-retrospective taxonomy edge** (exp-004 item 5, which #145 itself proposes as the split-taxonomy mitigation) — all stay with #145's skill. A consumer built now would read an empty corpus | Epic 4 |
| #149 | M5/M9: process rules that nothing executes, and remediation edges that exist only in prose | partial | **In:** its thesis applied to this plan's own surface — every stop becomes mechanical (D-3's counter, D-4's `test_class`, D-8's postcondition checks), so no rule here lacks an exit code. **Out:** the `discovered-from` remediation-edge work across the bead corpus | Epics 2, 3 |
| #113 | yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state) | exclude | Adjacent but distinct: #113 wants a **PLAN-phase review pass**; D-4's sweep is an **EXECUTE-start precondition check**. Different phase, different mechanism. The sweep reduces one class of what #113 targets without delivering it | — |

## Investigation Findings

Six dispatched experiments plus one observed incident, all in [findings/](findings/):
[exp-001](findings/exp-001-config-and-override-plumbing.md) config plumbing ·
[exp-002](findings/exp-002-attempt-counter-storage.md) attempt-counter storage ·
[exp-003](findings/exp-003-gate-sweep-feasibility.md) gate-sweep feasibility (**refuted D-4 as
scoped**) · [exp-004](findings/exp-004-retrospective-schema.md) retrospective schema ·
[exp-005](findings/exp-005-herdr-push-verification.md) herdr push verification ·
[exp-006](findings/exp-006-spec-amendment-surface.md) SPEC amendment surface ·
[exp-007](findings/exp-007-self-report-vs-verification.md) self-report vs verification.

**[exp-007](findings/exp-007-self-report-vs-verification.md) is not a dispatched experiment** — it
is a **live incident**, observed and independently verified during plan-044's execution. plan-044
reported that plan-045's bundle was *"uncommitted and… untracked"*; in fact **15 files / ~1,180
lines were committed under a plan-044 commit message and pushed to `origin/main`** — an in-flight,
unfingerprinted, unapproved bundle published to a shared branch. Content was intact; attribution
and publication state were not. The agent verified the half it thought to check (content equality)
and **asserted** the half it did not (tracking state) — both were one command away. It is the
fourth instance of one pattern: *an actor reports the outcome it intended rather than the outcome
it verified.* n=1 for the agent-reporting instance specifically, so it earns a cheap schema fix
(two fields and an entry kind), not an expensive mechanism.

**Pre-investigation checkpoint — the four diagnosed causes (evidence gathered this session):**

1. **Review cycles.** `yf-plan` SKILL.md Phase 3 grants autonomy to the conformance step
   ("resolve the listed gaps and re-run before proceeding — this is a mechanical gate, not a
   phase transition") and the very next step ends "Present the red-team verdict and concerns to
   the operator." The REVISE branch's "address concerns" has **no subject**, and is
   disambiguated toward the operator four more times, plus normatively in
   `spec/agents.md` REQ-AGENT-043. The `pass-N.md` **"Operator Resolutions"** table reifies it
   as a data structure. The correct pattern already exists in `agents/reviewer.md`
   ("**the main session** resolves the gaps").
2. **Execution.** In `agents/coordinator.md`, "Wait for operator" is the **only** explicit wait
   and is the loop's documented exit; because loop step 2 treats a failing gate test as
   "mark blocked, skip", an ordinary unsatisfiable gate routes straight there. "Report blocked
   gates" appears **5×** across the skill; "continue to the next bead" appears **0×**.
   Completion is written as a control transfer ("hand back to RECONCILE") although SKILL.md
   states "The coordinator IS the main session" — it hands back to itself.
3. **Gate frontloading.** Exhaustive grep for `frontload|up front|as early|gate placement`
   returns **zero hits**; the only topological rule (`agents/red-team.md`) prescribes the
   opposite ("gate the mutating step"). But the mechanism exists unused: the Start Gate is
   `Type: human` yet resolved non-interactively at execute start, and a capability gate whose
   `Test:` passes is auto-resolved and never prompts. **Nothing evaluates capability-gate tests
   at execution start** — they are only checked deep in the DAG.
4. **herdr delegation.** Child→parent push works **today** (`herdr agent prompt <pane-id>` with
   `--wait` omitted; `--wait` is opt-in and the only blocking behavior). But the launch recipe
   carries no autonomy clause, the fix exists only as advisory prose under `## Observe`
   ("If autonomy is wanted, say so explicitly") read *after* the prompt is composed, grep for
   `autonom` in yf-herdr SPEC.md returns **no match**, and the child is never told the parent
   exists. Polling is normative in REQ-HERDR-021.

## Approach

The thesis is **two-sided**. Only the first half was in the original scoping; exp-007 forced the
second:

1. **Autonomy is the default; stopping is the exception that must be justified** — and every stop
   must be *mechanical* (an exit code or a counter), never a judgement call, per #149's thesis
   that a step with no exit code is not a step.
2. **Autonomy is only safe where every claim of success is mechanically verified** — because
   **every stop was also an incidental checkpoint** at which a human saw real state. Removing
   stops removes the only verification the system had, unless something mechanical replaces it.

Without the second half this plan makes the system *faster at being confidently wrong.* The
evidence is a four-instance pattern (exp-007): a `--repair` step that printed `ok` without
checking its postcondition (what plan-044 existed to fix); a coordinator that closes every bead
`--reason "Completed"` with **no failure branch at all** (exp-002); a herdr push whose success
return is acknowledgement of **injection, not submission** (exp-005); and an agent that
**narrated** its own side-effects instead of verifying them (exp-007). Three are machine-layer;
the fourth is the agent-reporting layer, which no existing check covers.

### Scoping decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D-1 | Autonomy is **configurable** (`.yf-plan.local.json`) with an **autonomous default**, plus a **per-invocation override** | Mirrors `landing-strategy` / `execute.worktree`; keeps a cautious escape hatch for a risky plan without making caution the default |
| D-2 | The **irreducible stop set** is **five** classes: (1) outward-facing/irreversible writes; (2) a capability gate whose `Test:` fails; (3) destructive local ops; (4) scope ambiguity **only after a mechanical threshold**; (5) **ADDED after pass-1 — a declared mechanical check that fails**: validation FAIL, audit/`ready-check` fail, merge conflict at §6.1, dirty worktree, corrupted bead DB | Everything else becomes report-and-continue. Class 5 was missing and Issue 4.3's own write-site list proved it — four of its sites fit none of the original four. Class 5 is an **exit code**, so it costs the thesis nothing, and the two lists are now derivable from each other |
| D-3 | The ambiguity threshold counts **consecutive failed resolution attempts on the same bead**, resets on success, `N` configurable | Mechanical and per-bead; it is exactly the loop where an agent thrashes. Without a counter, "scope ambiguity" is a loophole that re-admits arbitrary stopping |
| D-4 | **REVISED after exp-003.** Gates become **structured beads** at creation (`gate_type`, `test`, `test_class`, `cwd` in metadata) so the sweep reads fields instead of parsing prose. The execute-start sweep then runs **only the SAFE-PROBE class** (~3s for the twelve **read-only** probes exp-003 timed; cheapness is *definitional* for the broadened class, enforced by classification and 3.6's `build` opt-out) and batches everything else into **ONE prompt** before any coding. `Type: human` gates are **never** auto-resolved | The scoped design was refuted: only 33% of live gates yield a runnable command; 59% are human-typed where a green test is explicitly not consent (auto-resolving would have granted publish authorization on **at least three** historical gates); most `auto` gates are *designed* to fail at t=0 because they assert the plan's own deliverables |
| D-7 | Fix the standalone bug exp-003 found: **`bd ready` never returns gate beads**, so `coordinator.md` loop step 2 has never fired | In scope because the coordinator loop is already being rewritten, and a sweep sharing one evaluate-gate routine with the lazy path requires the lazy path to work |
| D-5 | herdr child pushes to parent on **epic completion**, **blocker/failed gate/halt**, and **plan completion/abort** — never per bead | Per-bead would emit tens of messages for a plan-044-sized DAG and flood the parent's context |
| D-6 | `plan-retrospective.md` is **emit-only** here: this plan defines the schema and writes entries. Analysis and the frontloading consumer stay with #145 | A consumer built today would read an empty corpus. Emit first, accumulate, then build the reader |
| D-6a | **ADDED after exp-007.** The schema gains **`detected_by`** (`self-report` / `operator` / `mechanical-check`) and **`evidence`** (the command + output substantiating any state claim, or the literal `unverified`), and covers a **`deviation`** entry kind alongside `stop` | A retrospective built from an agent's own account **would have recorded the observed incident incorrectly** — it would have faithfully transcribed a false claim. An entry's trust level is a property of *who found it*, and the recorder is usually the subject. A state assertion with no evidence is a narration, not a finding. And the incident was a **non-stop** — a stop-only schema is blind to exactly the class autonomy makes more common |
| D-8 | **Every autonomy grant in this plan ships with its mechanical postcondition check.** All four pairings, named: **2.4** (review loop) → **2.4a** `max_review_cycles`; **2.6** (coordinator continue) → **2.7** verify-before-`bd close` + **2.8** `yf_attempts`; **3.5** (gate sweep) → a green probe is never consent; **5.2** (herdr autonomy) → **5.4** token stamp, since `agent_prompted` is injection, not delivery | The generalization of `REQ-YF-DOCTOR-006` — which plan-044 wrote for exactly this shape one layer down — to the agent layer. This is the second half of the thesis, and it is what makes the plan safe rather than merely faster |

## Epics

### Epic 0: SPEC-first amendments

SPEC-first is **mechanically forced** here, not merely policy: `DRIFT-CHECK.md` §7 marks `spec` and
`per-skill-spec` as **fixed authority**, so a SKILL.md-first change would FAIL the `skill-md` node
rather than update the spec (exp-006).

- Issue 0.1: `skills/yf-plan/spec/agents.md` — **amend** `REQ-AGENT-043` and `REQ-AGENT-061` to make
  the resolver **actor-agnostic** (drop "as the operator resolves concerns"; keep the read-only
  clause, which is also GR-PLAN-002). **Add** `REQ-AGENT-064`: under autonomy the coordinator
  continues to the next ready bead, reports at epic boundaries without stopping, and halts only on
  the D-2 stop set. Leave `REQ-AGENT-011` untouched — it is already pro-autonomy.
- Issue 0.2: `skills/yf-plan/spec/phases.md` — **amend** `REQ-RESUME-001` so autonomy defaults to
  the safe **resume** branch without an `AskUserQuestion` prompt. **"never fabricating a second
  epic" must survive verbatim.** Leave `REQ-PHASE-005` and `REQ-SESSION-001` untouched — plan
  approval and start-gate consent are legitimate and out of scope (exp-006).
  - depends-on: 0.1
- Issue 0.3: `skills/yf-plan/spec/portability.md` — **amend** `REQ-PORT-008` for the table rename;
  **add** a REQ for `plan-retrospective.md`'s shape and a REQ for its entry field set including
  `detected_by` and `evidence` (D-6a). Both carry a **REQ-PORT-ACT-OKF-style activation gate** so
  absence never fails any of the 44 existing bundles. **Also amend `spec/data.md` REQ-DATA-002**,
  which enumerates the bundle layout file-by-file — adding the file without it is spec drift on a
  fixed-authority node (pass-1 C6).
  - depends-on: 0.1
- Issue 0.4: `skills/yf-plan/spec/cli.md` — **add** `REQ-CLI-021` (a `config resolve --json` verb,
  the first of its kind, in its **flat `config-resolve`** form) and `REQ-CLI-022` (the retrospective
  append verb); **amend** `REQ-CLI-006`'s subcommand enumeration **and its `Verification:` line**,
  which greps `@cli.command` for a count — a click *group* would not be counted, so the amended
  count and its verification would disagree by construction (pass-1 C9). The flat form keeps the
  existing grep; exp-001 confirms nothing forces a group. Reconcile plan-044's note on this REQ
  recording that it added no subcommand. Start at **021** — plan-044 took 020 — and **grep-verify
  each id at authoring time** rather than trusting exp-006's table, which has a known error
  (pass-1 C13).
  - depends-on: 0.1
- Issue 0.5: `skills/yf-herdr/SPEC.md` — **add** `REQ-HERDR-015` (§2.2 Launch governs **prompt
  content**: the autonomy directive, the push contract, and the parent handle are mandatory, not
  advisory) and `REQ-HERDR-026` (observation is **push-primary**, polling the fallback for a silent
  or `blocked` child). **Amend** `REQ-HERDR-020`/`021` accordingly. Write the autonomy predicate
  *against* `REQ-HERDR-024`'s existing line — *"settled by existing approved plan content"* — rather
  than inventing a new one. Leave `REQ-HERDR-023`/`024`/`032` untouched.
  - depends-on: 0.1
- Issue 0.6: `skills/yf-plan/OKF-EXTENSION.md` — add the `Retrospective` §1 vocabulary row and the
  §1a `plan-retrospective.md → Retrospective` glob row **above** the `*` catch-all. Skipping this
  costs a permanent `okf.py check` warning on every bundle.
  - depends-on: 0.3
- Issue 0.7: Drift pass — reconcile `GUARDRAILS.md`, `README.md`, and the per-skill READMEs so the
  edges a `SKILL.md`/`SPEC.md` edit fires resolve in the same change-set.
  - depends-on: 0.2, 0.4, 0.5, 0.6
- Issue 0.8: **Explicit verification.** Run `cargo test --workspace` and the yf-plan Tier-1 suite,
  and record the result. Epic 0 edits `spec/*` and `SPEC.md`, which match **no** CHANGE-VALIDATION
  §3 glob — this is its only signal (exp-006).
  - depends-on: 0.7

### Epic 1: Close the validation blind spot

Deliberately **before** the implementation epics: exp-006 measured that an autonomy change confined
to `yf-herdr/SKILL.md` + `SPEC.md` + `yf-plan/spec/*` fires **only `frontmatter`** — a vacuous pass.
Landing coverage first means Epics 2-5 are actually validated as they land.

- Issue 1.1: **Author first (pass-1 C5).** A source-parsing test for the yf-herdr launch contract,
  on the `test_close_contract.py` pattern (which already parses SKILL.md source): assert the launch
  prompt template carries the autonomy directive, the push contract, and the parent handle.
  **yf-herdr ships no scripts and has no test suite today** — this is its first mechanical check.
  Ordered before the glob because a §3 row must name an id that already exists in §1.
  - depends-on: 0.8
- Issue 1.2: `CHANGE-VALIDATION.md` §1 row for 1.1's script + §3 trigger-scope rows for
  `skills/yf-herdr/**` and `skills/*/SPEC.md`, **each naming that id**. Follow plan-042's precedent:
  name a **test target**, never a name filter — *"a missing target is a hard error, whereas a name
  filter matching nothing exits 0 and passes vacuously."*
  - depends-on: 1.1
- Issue 1.3: Decide `skills/*/spec/*.md` explicitly (pass-1 C5): either map it to a named id or
  **drop the glob** and rely on Issue 0.8's `cargo test --workspace`, which the risk table already
  concedes is the honest answer for spec-only edits. Do not leave it mapped to `frontmatter`, the
  vacuous id 1.2 itself warns against. Then re-approve the §2 fingerprint.
  - depends-on: 1.2

### Epic 2: The autonomy core — review loop and coordinator

- Issue 2.1: `_resolve_autonomy()` in `plan_manager.py`, modeled verbatim on
  `_resolve_landing_strategy` (~10 lines; the three-tier reader already merges unknown keys, and
  there is no schema to update). Levels + default; written to `.yf/plan/config.local.json`.
  - depends-on: 1.3
- Issue 2.2: The `config resolve --json` verb (REQ-CLI-021), emitting each key's effective value
  **and its `source`** (flag / config.local / config.json / legacy / default). Honors the
  conventions exp-001 measured: `--json-output`/`--json` alias, **JSON to stdout on every path
  including failure** (REQ-CLI-016), exit 0 for a pure read.
  - depends-on: 2.1
- Issue 2.3: Wire the per-invocation override. **Detection is necessarily prose** — there is no argv
  in a slash-command path (exp-001). Follow the `capture --retro` seam: prose detects the token, the
  script validates and resolves it, the coordinator consumes only resolved JSON. Echo the resolved
  value into `log.md` so a misdetection is auditable.
  - depends-on: 2.2
- Issue 2.4: **Review loop.** Give the red-team branch the conformance branch's wording — *the main
  session* resolves concerns and re-runs until APPROVE, no operator acknowledgement per cycle. Fix
  the four sites that disambiguate "address concerns" toward the operator. The correct pattern
  already exists in `agents/reviewer.md`.
  - depends-on: 1.3
- Issue 2.4a: **The review loop's mechanical bound (pass-1 C2).** D-3's `yf_attempts` lives in bd
  metadata and is incremented in the coordinator loop — but 2.4 grants autonomy in **Phase 3, before
  intake, before the pour, before any bead exists**, so that counter structurally cannot reach it.
  Add a Phase-3-scoped **`max_review_cycles`**, resolved by the same `_resolve_autonomy()` /
  `config-resolve` machinery, counted by **`len(glob('reviews/pass-*.md'))`** — already on disk, and
  a faithful cycle count because REQ-PLAN-032 guarantees each full REVISE cycle yields exactly one
  pass file. (**Not** `_plan_review_line_count`, which counts `log.md` bullets — a *different*
  number that can and does diverge, as pass-2 concern A demonstrated live.)

  Two semantics this counter needs and `yf_attempts` does not, because it is **monotonic** — pass
  files are never deleted:
  - **Escalation exit.** At `N` the loop escalates (stop class 4) and the plan sits in `review`
    with a REVISE verdict — a legal state, not a wedge, since REQ-PLAN-030 only bars
    `ready-for-approval`. The operator's exit is a **per-invocation `max_review_cycles` raise**,
    echoed to `log.md` per 2.3 so the override is auditable.
  - **No auto-reset.** Without that raise every subsequent cycle re-escalates immediately. That is
    deliberate: a plan that has burned `N` review cycles should not silently resume.

  Without this the plan's headline change is the exact unbounded-autonomy shape D-8 forbids.
  - depends-on: 2.4
- Issue 2.5: Rename the `pass-N.md` **Operator Resolutions** table to **Resolutions** with an
  `actor` column. Measured free: the literal string appears in **zero** `.py` files; no parser, no
  test, no fingerprint code touches it (exp-006).
  - depends-on: 2.4
- Issue 2.6: **Coordinator loop.** Add the missing counter-instruction: continue to the next ready
  bead without operator input; **an epic boundary is a report, not a stop.** Rewrite "hand back to
  RECONCILE" / "control returns to the SKILL.md main session" as internal transitions — SKILL.md
  says *"The coordinator IS the main session"*, so it hands back to itself. Today "report blocked
  gates" appears 5x and "continue to the next bead" 0x.
  - depends-on: 2.3
- Issue 2.7: **The failure branch (new).** Loop step 6 closes **unconditionally** with
  `--reason "Completed"` — a failed bead is recorded as succeeded, and there is no retry concept at
  all (exp-002). Add an explicit failure path using bd's built-in `blocked` status, and — per **D-8**
  — **verify the postcondition before closing** rather than closing and asserting success.
  - depends-on: 2.6
- Issue 2.8: **The attempt counter.** `yf_attempts` in bd metadata, written **only** via
  `--set-metadata` / `--unset-metadata` (merge is measured-true but undocumented; `--set-metadata`
  states per-key intent and is immune to a semantics change). Increment **on detected failure**, not
  at claim — incrementing at claim would make Ctrl-C, OOM and reboots count as attempts. Reset
  unconditionally on any transition into `closed`. Escalate only at `N`; below `N` the loop
  **re-queues, not stops**.
  - depends-on: 2.7
  - resolves-upstream: #149 (partial — the mechanical-threshold half; the remediation-edge work is out)
- Issue 2.9: Surface `yf_attempts` in `resume-scan`'s `stuck` records — the metadata is already
  loaded there, so it is a one-line change, and the existing detector is status-based and cannot
  distinguish a first crash from a fifth.
  - depends-on: 2.8
- Issue 2.10: Tests — the four false-escalation classes exp-002 enumerated (crash-vs-failure,
  cross-resume accumulation, double-count on re-claim, query type mismatch), plus a review-loop test
  asserting `count(pass-*.md) == count(log.md review: lines)` still holds across an autonomous
  REVISE cycle (8 existing assertions depend on it), **and an assertion that the loop escalates at
  `max_review_cycles` rather than iterating unbounded** (2.4a). Registers its own CHANGE-VALIDATION
  §1 row, §3 glob and §2 fingerprint re-approval — three edits, not one (pass-1 C4).
  - depends-on: 2.9, 2.5, 2.4a

### Epic 3: Gates — structure, sweep, and the lazy-path bug

- Issue 3.1: **Structure the gate bead at creation.** Add
  `--metadata '{"gate_type":…,"test":…,"test_class":"probe|build|consent|manual","cwd":…}'` to
  §5.2a. This is the single change that converts the sweep from brittle to mechanical: today only
  **33%** of live gates yield a runnable command to a regex, and `Type:` is on **3 of 113** beads.
  **Without this, do not build the sweep.** Define the vocabulary explicitly: **`probe` means cheap
  AND self-cleaning, not read-only** (pass-2 concern E) — a probe may create and remove its own
  scratch state and must leave none behind on either exit path; anything mutating shared or operator
  state is `consent`, never `probe`. 3.5 auto-runs the whole `probe` class, so this definition is
  load-bearing. Worked example: this plan's own herdr gate creates and closes a `--no-focus`
  throwaway tab — that is **its own scratch state**, removed on both exit paths, so it is `probe`;
  a test that wrote to the operator's existing config would be `consent`.
  - depends-on: 1.3
- Issue 3.2: Fix §5.2a's `--description` to emit **real newlines** (`printf` or `$'…'`) — bash
  double quotes store a literal `\n`, which has already corrupted 3 of 113 gate beads.
  - depends-on: 3.1
- Issue 3.3: **D-7 — fix the lazy path.** `bd ready` never returns gate beads, so `coordinator.md`
  loop step 2 has **never fired**. Enumerate via `bd gate list` / `bd list --type gate
  --include-gates` — **and paginate or pass an explicit `--limit`**: measured on this repo,
  `bd gate list --all --json` returns **50** records while `--limit 1000` returns **113**. The
  default caps below the corpus **with no error and exit 0** (pass-3 C-2). A sweep that silently
  sees 50 of 113 gates is exactly the vacuous-green class this plan exists to eliminate.
  - depends-on: 3.2
- Issue 3.4: One shared **evaluate-gate routine** used by both the eager sweep and the lazy loop, so
  the two cannot diverge. §6.1.5 already names gate-`Test:` execution as "layer (a)" — the sweep is
  a relocation of it from lazy to eager, not a second implementation.
  - depends-on: 3.3
- Issue 3.5: **The execute-start sweep**, placed between `worktree ensure` and §5.3 — after, because
  the address-space model routes *code* tests to the worktree and *plan-folder* tests primary-side,
  and the sweep cannot route until the worktree exists. Classify all gates; run **only the
  `probe` class** (~3s for the twelve read-only probes exp-003 timed — see D-4 on the broadened
  class); batch everything else into **ONE prompt**; then run everything the
  failed gates do not block. **`gate_type: human` is never auto-resolved** — a green test is not
  consent, and auto-resolving would have granted publish authorization on **at least three** historical gates. A
  non-command test yields **INCONCLUSIVE, not FAIL**.
  - depends-on: 3.4
- Issue 3.6: `--sweep-gates=probe|all` (default `probe`), so the multi-minute `build` class is
  opt-in and execute start does not inherit a cost §6.1.5 explicitly reserves for once-per-land.
  - depends-on: 3.5
- Issue 3.7: **The gate-placement principle** (the frontloading half of the objective): hoist human
  gates to the earliest point their condition is decidable. Add to `planner.md`; keep
  `red-team.md`'s cycle rule as the constraint, and reconcile its *"gate the mutating step"* line,
  which currently prescribes the opposite. **No such guidance exists anywhere today.**
  - depends-on: 3.6
- Issue 3.8: Tests — parse round-trip on structured gates, the `bd ready` enumeration fix, probe/
  consent classification, a negative test that a `human` gate is never auto-resolved, **and a count
  assertion that the enumeration returns the full corpus rather than the default page** (C-2). Registers its own CHANGE-VALIDATION §1 row, §3 glob and §2 fingerprint re-approval — three edits, not one (pass-1 C4).
  - depends-on: 3.7

### Epic 4: Retrospective emit

- Issue 4.1: A **local** `append_retrospective()` in `plan_manager.py`, mirroring `okf.append_log`'s
  create-if-absent + idempotence contract. **Do NOT generalize `append_log`** — it is vendored in
  four copies behind byte-identical `e-okf-copy-*` drift edges. **Also add the `_INDEX_MEMBERS`
  bullet** so `index.md` lists the new file — without it the plan's own cold-reader contract is
  violated by the very file it adds (pass-1 C6).
  - depends-on: 1.3
- Issue 4.2: The schema — `## RE-NNN` sections with a **two-column key/value table** per entry
  (a table dodges the REQ-OKF-010 bold-label trap, which is invisible to `plan_manager.py audit`
  but fails `/yf-okf check`). Fields: `when` · `stop_class` · `asked` · `answered` ·
  `frontloadable` · **`detected_by`** · **`evidence`** · `escape_class` · `adjudication` · `origin` ·
  `culpability` · `prevention` · `cost`. Entry kinds: **`stop` and `deviation`** (D-6a). Verbatim
  quotes **must be fenced** — an unfenced `/Users/` path is a hard REQ-PORT-007 audit failure.
  - depends-on: 4.1
- Issue 4.3: Wire the write sites, highest-volume first: the coordinator's blocked-gate halt, §3
  review resolution, audit/ready-check failures, the §5.2 resume and dirty-worktree paths, §6.1.5
  validate failures, §6.4 chain halts, and **every `--force` override** (which already logs a reason
  — mirror it). Exclude §6.2 push authorization: that is a consent gate by design, not friction.
  - depends-on: 4.2
- Issue 4.4: A close-time **advisory** §6.4 step reporting the entry count, positioned above the
  `set-deliverable-class` dual-write per REQ-COMPLETE-001's read-before-write constraint. It must
  honor REQ-COMPLETE-003's JSON envelope or `test_close_contract.py` fails CI. **Advisory, never
  halting** — halting stays with #145's skill.
  - depends-on: 4.3
- Issue 4.5: Backfill the **first real entries** from this session's own observed events: the
  plan-044 gate-Instructions staleness, the exp-007 misreport, this plan's own
  self-modification-hazard overstatement (refuted by `TESTING.md:14`, which already said so), and
  the **three** resolutions-table over-claims that passes 2, 3 and 4 each caught — all as
  `deviation` entries, `detected_by: operator`, `prevention: process step`. Proves the schema
  against real data rather than invented data.
  - depends-on: 4.4
  - resolves-upstream: #145 (partial — the EMIT side only; measurement and the consumer stay with #145)
- Issue 4.6: Tests — schema shape, the two traps (unfenced path → fail; bold label → `/yf-okf check`
  fail), idempotence, and **absence-is-not-a-failure** for a bundle with no retrospective. Registers its own CHANGE-VALIDATION §1 row, §3 glob and §2 fingerprint re-approval — three edits, not one (pass-1 C4).
  - depends-on: 4.5

### Epic 5: herdr — push-primary delegation

- Issue 5.1: **Seed the parent handle.** `--env YF_PARENT_PANE="$HERDR_PANE_ID"` on `tab create`
  (measured to reach the agent process and its grandchildren), and restate it in the prompt text.
  Prefer the **pane id** over the name: `HERDR_PANE_ID` is injected automatically and is stable,
  while `name` exists only for `agent start`-ed agents and goes stale on rename.
  - depends-on: 1.3
- Issue 5.2: Make the autonomy + push contract a **required launch-prompt template**, not advisory
  prose under `## Observe`. Today the recipe is a bare `herdr agent prompt "<name>" "/yf-plan
  execute <plan-id>"` — a parent following it literally produces the stop-after-every-epic behavior
  the skill's own trap warns about. Bake it into `-- --append-system-prompt` as well (measured free:
  3.016s vs a 3.061s control), so it survives the child's context compaction.
  - depends-on: 5.1
- Issue 5.3: Push triggers per D-5 — epic completion, blocker/failed gate/halt, plan completion or
  abort. **Never per bead** — tens of messages for a plan-044-sized DAG, enough to flood the parent's context. **`--wait` is forbidden**: it
  reintroduces lockstep, and `--wait --until idle` is measurably *wrong* for claude, timing out at
  120s on a turn that completed (a claude turn settles at `done`, never `idle`).
  - depends-on: 5.2
- Issue 5.4: **D-8 pairing.** `agent_prompted` is acknowledgement of **injection, not submission** —
  one measured push returned success and was never submitted. Pair every push with an idempotent
  `herdr pane report-metadata --token` stamp on the child's own pane, readable back via `pane get` /
  `agent get` / `agent list`. A push costs the parent a turn; a token write costs nothing, so the
  pull path becomes a genuine backstop rather than a parallel mechanism. (CLI gotcha: `<PANE_ID>`
  must come **first**, despite the usage string.)
  - depends-on: 5.3
- Issue 5.5: Recast observation as **push-primary, polling fallback** for a silent or `blocked`
  child. The skill currently treats "cannot watch continuously" as a law of nature — true for
  **pull**; the child can speak.
  - depends-on: 5.4
  - resolves-upstream: #110 (partial — the push channel and autonomy contract; the multi-harness fan-out is out)
- Issue 5.6: **Test the one untested risk:** a push into a **`blocked` parent**. The existing trap is
  stated child-ward but applies symmetrically. If the push is swallowed, the token side-channel from
  5.4 is the mitigation — confirm it is sufficient. Registers its own CHANGE-VALIDATION §1 row, §3 glob and §2 fingerprint re-approval — three edits, not one (pass-1 C4).
  - depends-on: 5.5

### Epic 6: Cleanup and close

- Issue 6.1: Drop the provably low-information prompts (D-1 §5): the intake deliverable-class confirm
  (the skill's own text calls its confidence *"effectively always low here, which makes it useless
  for deciding"*), the upstream-tracking ask that fires even when config is already detected, and
  the incubator confirm when CWD auto-detect is unambiguous.
  - depends-on: 2.10
- Issue 6.2: Reconcile the **four stale #100 doc sites** — `SPEC.md` §3, `spec/cli.md` REQ-CLI-005,
  `spec/data.md` REQ-DATA-021 (*"`ignore-skill` … is the only config key"* — six exist), and
  SKILL.md's "Config vs state" paragraph. #100 is **closed and delivered in code**; only the docs lag,
  and any config-touching plan trips drift-check on them.
  - depends-on: 6.1
- Issue 6.2a: **Promote the skill-artifact invariant into the always-loaded surface.** `TESTING.md`
  already states it verbatim and has since plan-021 — *"Editing `skills/<skill>/…` does **not**
  hot-swap the running skill — so a plan/research executing its own rework is safe (no
  self-modification mid-run)"* — but `AGENTS.md` routes there only *"when developing deep/integration
  test plans or test scripts"*, a trigger that never fires for a planner reasoning about execution
  safety. Measured: `AGENTS.md` has **0** mentions of the resolver or `~/.claude/skills`, and its
  "Syncing local yf" section covers repo ↔ **binary**, not repo ↔ **session**.

  Add to `AGENTS.md` (always-loaded, so it reaches every session) a short **three-artifact** note:
  repo source · the `yf` binary's embedded tree · the session's installed skill — with the
  `SKILL_DIR` search path showing the repo's `skills/` matches **none** of its six roots, the
  resulting safety invariant, and the one real constraint (**no deploy mid-execution**, because
  `plan_manager.py` is re-invoked per call while `SKILL.md` prose is loaded once). Cross-link
  `TESTING.md` rather than restating its Tier-1/Tier-2 content.

  **This is a discoverability fix, not new content** — the failure it prevents was reasoning from
  first principles past a documented fact. This plan's own draft asserted a self-modification hazard
  that `TESTING.md:14` refutes; the operator caught it. Recorded as a `plan-retrospective.md`
  entry in Issue 4.5 (`detected_by: operator`, `prevention: process step`).
  - depends-on: 6.2
- Issue 6.3: Final sweep — `cargo test --workspace`, the full Tier-1 suites, `/yf-okf check` on a
  bundle carrying a retrospective, and confirmation that every new test script has its §1 row, §3
  glob and re-approved §2 fingerprint.
  - depends-on: 3.8, 4.6, 5.6, 6.2a

### Skill-artifact isolation (pass-1 C10, corrected pass-3)

This plan edits `skills/yf-plan/**` and `skills/yf-herdr/**` — the **source** of the skills it runs
under. That is not the same artifact as the running skill, and the distinction is structural, not
procedural:

- The `SKILL_DIR` resolver searches `~/.claude/skills`, `~/.agents/skills`,
  `$GIT_ROOT/.{claude,agents}/skills`, and relative `.{claude,agents}/skills`. **The repo's
  `skills/` directory matches none of them** — it is unreachable by the resolver, not merely
  stale. Everything the session touches (`SKILL.md` prose, `agents/*.md`,
  `uv run ${SKILL_DIR}/scripts/plan_manager.py`) resolves to the **installed** copy.
- Testing is sandboxed-`HOME` per `TESTING.md` Tier-2, so exercising the modified skill never
  touches the real user-scope install either.

**The only real constraint: no `yf skills install` / `yf self install` mid-execution.** Deployment
happens at §6.2 land-the-plane, after the work is merged and validated. The reason it matters is
narrow but non-obvious: **`plan_manager.py` is re-invoked per call**, so a mid-execution deploy
would take effect in the *same* session for the scripts — unlike `SKILL.md` prose, which is loaded
once at invocation.

*(An earlier draft claimed this plan "rewrites the skill executing it" and posited a hazard window
between an Epic-2 merge and Epic 3. Both were wrong: the resolver cannot reach the repo path, and
§6.1 merges **once** at RECONCILE after every bead closes — there is no mid-execution merge.)*

**A corrupted bead DB mid-run routes to `yf-beads-init`** (verify, then repair) before the
coordinator relies on `bd` again — the always-loaded beads rule requires verification, and stop
class 5 covers the halt if repair fails.

## Gates

### Start Gate (mandatory)

- Type: human
- Approvers: operator

### Capability Gate: herdr probe surface

- Type: auto
- gate_type: auto · test_class: probe · cwd: repo-root
- Condition: `herdr` is on PATH, this session is herdr-managed, and a throwaway tab **can actually
  be created and closed** without touching a live agent.
- Test: creates and closes a real `--no-focus` throwaway tab, asserting write access — not merely
  `herdr agent list`, which proves only read (pass-1 C7).
- Blocks: Issue 5.1
- Instructions: Epic 5 cannot be exercised outside a herdr session. **Deferral is a mechanism, not
  an intention (pass-1 C1):** on FAIL, `bd close -r "descoped: herdr unavailable"` beads 5.1–5.6 —
  the reversible tombstone — so Issue 6.3's dependency resolves and the Reconcile Gate can still
  fire, and write a `stop_class: environment` retrospective entry. **The failed gate bead itself is
  left OPEN as the record** — do not force-close it; `bd close` requires `-f` for an unsatisfied
  gate, and an open gate with no open dependents is the honest artifact of a deferred epic
  (pass-2 concern H). **Without the tombstone step the plan cannot complete:** 6.3 would never
  become ready and the auto reconcile gate would never fire.

### Capability Gate: bd gate corpus readable

- Type: auto
- gate_type: auto · test_class: probe · cwd: repo-root
- Condition: the live gate corpus can be enumerated, so Issue 3.1's structured form can be validated
  against real prose gates.
- Test: `bd gate list --all --json` returns a **non-empty** corpus — a bare exit-0 does not
  establish the Condition, since a repo with zero gates also exits 0 (pass-1 C7).
- Blocks: Issue 3.1
- Instructions: read-only. If it fails, `yf-beads-init` verify/repair first.

> **Both capability gates are deliberately `probe`-class and frontloaded** — this plan applies its
> own D-4 rule to itself. Neither is `consent`-class, so neither can be satisfied by a green test
> standing in for operator authority.
>
> **Honest scope (pass-1 C7):** both were **green when authored**, so on this machine the
> frontloading machinery is not exercised by its own instance. Each Test was strengthened to
> actually establish its Condition — a Test narrower than its Condition is verbatim the
> SMOKE-CHECK-ONLY defect exp-003 documented and Issue 3.5 exists to prevent. Reproducing that
> defect in this plan's own gates would have been the sharpest possible irony.

### Reconcile Gate

- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| Risk | Mitigation |
| :-- | :-- |
| **Autonomy makes the system faster at being confidently wrong** — the central risk, and the reason the thesis is two-sided | D-8: every autonomy grant ships with its mechanical postcondition check (2.7 verify-before-close, 5.4 token pairing, 3.5 no-consent-from-green). Without Epic 2's failure branch, Epic 2's autonomy is net-negative |
| **"Scope ambiguity" becomes a loophole that re-admits arbitrary stopping** | D-3's counter is mechanical and per-bead (2.8). An escalation requires `yf_attempts >= N`; below N the loop must re-queue. Prose judgement alone can never trigger stop class 4 |
| **The counter fabricates escalations** | Increment on **detected failure**, never at claim — the four measured false-escalation classes are each tested in 2.10. Prefer the undercount: it delays escalation rather than inventing it |
| **A gate sweep silently grants consent** | `gate_type: human` is never auto-resolved (3.5); `Type:` absent → **default to human**; structure precedes sweep (3.1 before 3.5), and without 3.1 the sweep is not built at all |
| **Epic 0 is validation-dark** — `spec/*` and `SPEC.md` match no CHANGE-VALIDATION glob | Issue 0.8's explicit `cargo test --workspace`, and **Epic 1 lands coverage before the implementation epics** so 2-5 are validated as they land |
| **yf-herdr is unprovable today** — no scripts, no tests, one vacuous `frontmatter` row | Issue 1.2 gives it its first mechanical check, on the `test_close_contract.py` source-parsing pattern |
| **Renaming the Resolutions table breaks something** | Measured free (exp-006): zero `.py` references. The real coupling is `_plan_review_line_count`'s count-equality, asserted at 8 sites — 2.10 tests it explicitly across an autonomous REVISE cycle |
| **`plan-retrospective.md` newly fails 44 existing bundles** | The audit's presence checks are a **closed hand-written list**, so absence is a non-event. 0.3's REQs carry an activation gate, and **no presence check is added** (4.6 tests absence-is-not-a-failure) |
| **A prose-detected `--checkpoint` is misread** | Identical in kind to today's `--force`, which is also prose-detected. Mitigated the same way: the resolved value is echoed into `log.md` (2.3), so a misdetection is auditable after the fact |
| **The retrospective records a false claim faithfully** | D-6a's `detected_by` + `evidence` fields; a state assertion with no evidence is a narration, not a finding (exp-007) |
| **A push into a `blocked` parent is swallowed** | The one untested risk, explicitly tested in 5.6, with the 5.4 token side-channel as the standing mitigation |
| Plan is large (7 epics, **46** issues, 2 skills + 2 manifests) | Epics 3, 4 and 5 are independent after Epic 1 and can land as separate merges; Epic 5 is separately gated and droppable if herdr is unavailable |

## Success Criteria

1. `/yf-plan execute` on a plan with no failing gates runs **to completion without a single operator
   interaction**, with epic boundaries reported and not stopped at.
2. A red-team `REVISE` is resolved and re-run **without operator acknowledgement**, and the loop
   iterates to `APPROVE` on its own **within `max_review_cycles`**, escalating at `N` rather than
   iterating unbounded. `count(reviews/pass-*.md) == count(log.md review: lines)` still holds across
   every autonomous cycle, including the escalation.
3. The **five** stop classes are the **only** paths that halt an autonomous run, and each is
   mechanical — no halt is reachable by prose judgement alone: (1) a declared outward-facing/
   irreversible write; (2) a capability gate whose `Test:` exits non-zero; (3) a declared
   destructive local operation; (4) `yf_attempts >= N` **or** `max_review_cycles >= N` (the
   execution-phase and plan-phase counters); (5) a declared mechanical check that exits non-zero —
   validation, audit/`ready-check`, merge conflict, dirty worktree, corrupted bead DB. **Every stop class has at
   least one Issue 4.3 write site**, with two documented exceptions: §6.2 push consent (excluded
   from 4.3 by design — it is a consent gate, not friction) and the `deviation`-kind sites, which
   are not stops at all (pass-3 C-4).
4. A bead that fails is **not** closed as `Completed` — it takes the failure branch, increments
   `yf_attempts`, and re-queues. Verified for each of the four false-escalation classes.
5. `bd ready`-based gate handling actually fires — the lazy path is exercised by a test that fails
   against today's code.
6. **All human gates are surfaced in ONE prompt before any coding work**, and `gate_type: human`
   gates are never auto-resolved. Probe-class sweep completes in seconds, not minutes (measured basis: exp-003's twelve read-only probes at ~3s total).
7. `autonomy` resolves through `flag > config.local > config.json > legacy > default`, and
   `config resolve --json` reports each key's value **and its source**.
8. A delegated herdr child runs to completion without stopping, pushes at epic boundaries,
   blockers and completion, and its parent learns of each **without polling**. `--wait` appears
   nowhere in the child's push path. **(N/A if the herdr probe gate fails and Epic 5 is tombstoned
   — the deferral branch the gate's own Instructions define; pass-3 C-6.)**
9. `plan-retrospective.md` is written on every stop **and** every deviation, carries `detected_by`
   and `evidence` on each entry, and its **absence never fails** any of the 44 existing bundles.
10. A `/yf-okf check` on a bundle carrying a retrospective is clean — no REQ-OKF-010 label
    collision, no unregistered-type warning, no REQ-PORT-007 dangling-ref failure.
11. yf-herdr has at least one mechanical test; `skills/*/SPEC.md` and `skills/yf-herdr/**` fire a
    non-vacuous FAST-tier id; and `skills/*/spec/*.md` **either** fires a non-vacuous id **or** is
    recorded as deliberately out of FAST scope, covered by Issue 0.8's `cargo test --workspace`.
    (SC11 must not foreclose the drop branch Issue 1.3 explicitly authorizes — pass-3 C-1.)
12. `cargo test --workspace`, `cargo clippy --workspace --all-targets -- -D warnings`, and every
    Tier-1 suite are green; the four stale #100 doc sites are reconciled; and `AGENTS.md` carries
    the three-artifact skill-isolation note (Issue 6.2a).
