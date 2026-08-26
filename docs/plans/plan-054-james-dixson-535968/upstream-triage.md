---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: release readiness v0.5.0 SKILL_DIR harness docs changelog website regression pi opencode

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #233 — yf-plan: audit-close's OKF walk has no fixture carve-out, so pinned negative fixtures fail it
Labels: bug
> Found at **plan-053**'s own close step, by running `audit-close`.

## Measured

```text
Counter({'fail': 26, 'warn': 19})
fail findings NOT in a pinned fixture tree: 1
```

**25 of 26 `fail` findings ...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #232 — yf-plan: Success-Criterion COMMANDS are never executed before approval — extend D-4's discipline from controls to criteria

> Found by **plan-053** (`plan-053-james-dixson-4015d3`) about itself. Not a code defect — a
process one, and the most valuable thing that plan produced.

## The measurement

plan-053 ran **five red-tea...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #231 — plan-053-james-dixson-4015d3 execution tracking

> The single coarse tracking issue for **plan-053** (`plan-053-james-dixson-4015d3`), per the
AGENTS.md one-tracker-per-plan convention.

- **Plan bundle:** [`docs/plans/plan-053-james-dixson-4015d3/`](...

**Disposition:** include
**Notes:** plan-053 is complete, deployed and reconciled; the tracker is its last open artifact. Closed by Issue 6.1.

## #230 — bd close REFUSES and EXITS 0 when the bead is blocked by an open dependency
Labels: bug
> Found by plan-053 during its own execution. **This is the defect class plan-053 exists to
close, occurring in the tool plan-053 is tracked with.**

## The defect

`bd close <id>` on a bead with an ope...

**Disposition:** deferred
**Notes:** An upstream `bd` defect, not ours to fix.

## #229 — redcheck.sh's YF_TREE default assumes plan-050's asset layout (#210's class, in the shared harness)
Labels: bug
> Found by plan-053 — and specifically by the guard plan-053 added at Issue 1.1(b), on its
**first real use**.

## The defect

The driven-red harness computes its tree-under-test as:

```bash
: "${YF_TR...

**Disposition:** deferred
**Notes:** A plan asset, not a shipped artifact.

## #228 — Bead provenance does not reach TITLE-BORNE citations (#209's larger class)

> Recorded by plan-053 as decision **D-13**, measured by EXP-006. Filed rather than papered over.

## The gap

plan-053 closed #209 by giving every poured issue bead a `plan_dir` metadata key and a
prov...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #227 — yf-incubator: STATUS_VALUES is dead code — #208's defect one skill over
Labels: bug
> Measured by plan-053 (EXP-004), re-verified on the merged tree.

## The defect

`skills/yf-incubator/scripts/incubator-index.py:47` defines a status vocabulary and **never
reads it**:

```console
$ gr...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #226 — plan_extract: a trailing declaration behind a LEADING code span yields no edge
Labels: bug
> Measured by plan-053 (EXP-001), re-verified on the merged tree.

## The defect

A **real** trailing declaration sitting behind a leading inline code span produces no edge:

```text
- Issue 1.2: second...

**Disposition:** include
**Notes:** Silent DAG-edge loss. Fixed by Issue 3.3, after 3.2's capture fix.

## #225 — plan_extract: a COLUMN-0 PARAGRAPH under an open issue is dropped silently (#206's third family member)
Labels: bug
> Measured by plan-053 (EXP-001), and re-verified **on the merged tree after both #206 fixes
landed** — so this is a surviving shape, not one those fixes were expected to reach.

## The defect

A column...

**Disposition:** include
**Notes:** Silent plan-content loss at intake. Fixed by Issue 3.2.

## #224 — Success criteria that use `grep -qv` are environment-dependent: under ugrep the criterion CANNOT FAIL, and a false 'green' survives repeated verification

> Filed by operator decision from the **plan-004** session in `dixson3/rc-files`. Sibling of #203 but a **different mechanism**: not "failure in output, success in `$?`", but *the same command returning...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #223 — bd mol pour / yf-plan intake: one plan issue poured TWICE — 26 task beads for 25 declared issues, byte-identical duplicate

> Filed by operator decision from the **plan-004** session in `dixson3/rc-files`.

## What happened

The §5.2a pour created **two beads for the same plan issue**. Measured immediately after Epic 1:

```...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #222 — yf-plan: the phase model has no slot for post-merge/post-teardown work, yet 6.2 teardown predictably invalidates worktree-rooted artifacts

> Filed by operator decision from the **plan-004** session in `dixson3/rc-files` (CLIProxyAPI local model gateway). Three instances, one root cause, all measured on a live machine.

## The class

**A be...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #221 — yf-plan: SC24-style criteria assert a MOVING fact (stamp == HEAD) where they should assert a DURABLE one
Labels: priority::medium, type::bug
> **Measured at plan-052's completion, and re-measured independently before filing:**

```
yf --version stamp: ed0803f
HEAD:               e94206a
```

`SC24` reads: *"The deployed tree matches source a...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #220 — yf-plan: the RED-observation ledger cannot distinguish a driven RED from a real failure (and `grant --check` does not verify amendments)
Labels: priority::medium, type::bug
> **Measured:** plan-052, at execution — by the plan's own §6.4 halt, on the plan's own harness.

## Finding 1 — the RED-observation ledger cannot distinguish a driven RED from a real failure

`assets/r...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #219 — yf-plan: `gate_consistency.py` does not check TEST/CONDITION FIDELITY
Labels: priority::medium, type::bug
> **Measured:** plan-052, at execution, by a human — **not** by the checker plan-052 shipped for
exactly this class of gate defect.

`skills/yf-plan/scripts/gate_consistency.py` (plan-052 Issue 4.2, the...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #217 — yf-change-validation: `change_validation.py` persists no run record
Labels: priority::medium, type::bug
> **Measured:** plan-052 EXP-004 §4 (recorded as D-13).

`change_validation.py` **persists nothing** about a run. There is no record of what ran, when,
against which tree, or with what verdict.

It is t...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #216 — coordinator: beads are closed in batches, making 84% of observed interval overlap an artifact
Labels: priority::medium, type::bug
> **Measured:** plan-052 EXP-006 §1 / I-5.

The coordinator closes beads in **batches** rather than when each unit of work finishes. That
collapses distinct work intervals onto a single timestamp, so **...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #215 — coordinator/bd: `started_at` is written for 86 of 225 plan beads and is not exposed by `bd list --json`
Labels: priority::medium, type::bug
> **Measured:** plan-052 EXP-006 §1.

Beads carrying **both** `started_at` and `closed_at`: **86 of 225** (plan-048 alone: **0 of
39**). Separately, `bd list --json` **does not expose** `started_at` at ...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #213 — bd: `distill` cannot reconstruct gate steps — non-idempotent against bd's own pour
Labels: priority::medium, type::bug
> **Measured:** plan-052 EXP-005, finding I-4(iii).

`bd distill` cannot reconstruct gate steps, so **pour -> distill -> pour does not round-trip**:
the gate is lost on the way back. distill is therefor...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #212 — bd: a `type = "gate"` step with no `[steps.gate]` pours as a plain task, with no diagnostic
Labels: priority::medium, type::bug
> **Measured:** plan-052 EXP-005, finding I-4(ii).

A formula step declaring `type = "gate"` but omitting the `[steps.gate]` table **pours as a
plain task**, silently. No warning, no error.

The result ...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #211 — bd: `distill --var` silently substitutes nothing and exits 0
Labels: priority::medium, type::bug
> **Measured:** plan-052 EXP-005, finding I-4(i).

A `bd distill --var` pass produced output with the **placeholders still intact** and returned
**exit 0**. A caller therefore cannot distinguish a succe...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #204 — yf-herdr: no teardown contract — a completed plan's subordinate tab is never closed, and only harvest-before-prune makes closing safe

> Filed by operator decision from the **plan-051** session. Related: #198 (the harvest→prune hazard, same ordering constraint), #203 (structural verification of an operation's result).

## The gap, meas...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #203 — Exit-code discipline: five instruments report failure in output and success in $? — promote the 0/1/2 contract repo-wide

> Filed by operator decision from the **plan-051** session. Related: #199, #198, #202, #173.

## The class

**An instrument reports failure in its OUTPUT and success in its EXIT CODE.** A scripted calle...

**Disposition:** include
**Notes:** Includes `yf skills status` returning Ok(()) unconditionally. Fixed by Issue 3.6.

## #202 — bd mol burn: a cancelled burn exits 0, so a scripted burn cannot detect it

> ## The defect

A cancelled `bd mol burn` **exits 0**. A scripted caller reading the exit code concludes the burn
succeeded when nothing was burned.

Without `--force`, `bd mol burn` prompts `Continue?...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #201 — change_validation.py: repeated --changed silently drops all but the last path

> ## The defect

`change_validation.py` declares `--changed` with `nargs="*"` and **no** `action="append"`, so a
caller passing the flag more than once silently keeps **only the last occurrence**. Every...

**Disposition:** include
**Notes:** A green covering half a change-set. Fixed by Issue 3.4.

## #195 — beads docs describe dependency types that installed bd 1.1.2 does not have: waits-for and conditional-blocks
Labels: type::bug, priority::high
> MEASURED. beads.gascity.com/workflows/molecules documents four dependency types with
execution semantics:

  blocks              sequential
  parent-child        hierarchy
  conditional-blocks  B runs...

**Disposition:** include
**Notes:** Ships actively misleading docs. Fixed by Issue 3.5.

## #192 — Evaluate a structure-first plan DSL with generated markdown — single source for plan.md, the bead pour, and cross-reference integrity

> ## Idea

Author plan **structure** in a machine-first artifact — YAML or a small DSL — holding epics, issues, dependency edges, gates, criteria, risks and the upstream table with its internal/external...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #191 — yf-plan: scaffold reviews/pass-N.md instead of hand-typing it — the shape check already fires, the authoring is what is missing

> ## The check already exists and works. That is the point.

`doc_lint`'s `required-sections` rule catches `## Missing (all now closed)` **every single time** — it fired on `pass-6.md`, on `pass-7.md`, ...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #190 — Require plans to ship tests for code they write, at >= 80% coverage of that code — with a recipe row that enforces it

> ## Proposed policy

**Code written as part of a plan ships with tests, at >= 80% coverage of the code that plan wrote.**

Today this is convention, unevenly applied, and enforced by nothing. #189 meas...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #189 — Six shipped scripts have no tests at all — including two CHANGE-VALIDATION checks and the beads repair engine

> ## Summary

Six shipped scripts have **no test file and are referenced by no test anywhere in the repo**. This is the coverage half of the problem; the blind-spot half — suites that exist but assert o...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #188 — Test suites assert output STRUCTURE and never payload FIDELITY — the blind spot #186/#187 lived in

> ## The defect class

Our test suites assert the **shape** of a tool's output and never the **fidelity of its content**. A tool can therefore corrupt every value it carries while every assertion stays ...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #185 — doc_lint: upstream-cells-filled cannot distinguish a skipped triage from a measured-empty one

> ## Summary

`doc_lint`'s `upstream-cells-filled` check (`skills/yf-plan/scripts/document_types/plan.toml`)
fires on a `## Upstream Issues` table with zero rows, with the rationale:

> a table with no ...

**Disposition:** include
**Notes:** Blocks approval in ANY fresh repo with no upstream issues. Fixed by Issue 3.1.

## #174 — yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it

> **Proposes the mechanism for the defect family #173 diagnoses.** #173 records *what went wrong and why five red-team cycles missed it*, under an explicit "record, do not fix" instruction. This issue p...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #173 — yf-plan: success criteria and upstream dispositions are never checked against the engine that enforces them

> Filed from plan-046 execution, at operator instruction: **record, do not fix**.

## Two concrete defects, one family

### 1. A plan instruction contradicted the engine that enforces it

plan-046 Issue...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #171 — yf-okf: nested index.md generation, deferred behind a `description:` producer change (plan-046 D-9)

> Filed by plan-046 Issue 5.5(iv). This is the **deferred half of #140**, filed upstream so the deferral is visible to the issue tracker and not only to `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` §9a.

R...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #170 — OKF consumer round-trip fidelity is unverified — #92 carve-out 3 of 3

> Filed by plan-046 Issue 5.5(iii) as one of **three named carve-outs** from closing #92 as superseded.

**The gap, stated precisely.** yf demonstrates **producer → producer** fidelity only: it writes O...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #169 — OKF conformance gate for yf-research and yf-incubator — #92 carve-out 2 of 3

> Filed by plan-046 Issue 5.5(ii) as one of **three named carve-outs** from closing #92 as superseded.

**What this is.** yf-plan's bundles are conformance-gated: `plan_manager.py audit` runs the OKF en...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #168 — yf-okf: projection delivery mode (on-demand OKF export) — #92 carve-out 1 of 3

> Filed by plan-046 Issue 5.5(i) as one of **three named carve-outs** from closing #92 as superseded. #92's emit half shipped natively and its nested-tree half is #140; these three are what a clean clos...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #166 — yf-beads-extra: document that `bd ready` silently excludes whole categories — two loops have already been built on the assumption it does not

> Follow-on from plan-045 (#162). A generalization the plan fixed twice, instance-by-instance, without naming the class.

## The behaviour

`bd ready --help` states it plainly:

> Excludes in_progress, ...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #165 — SPEC `Verification:` lines are prose shaped like commands — a FULL tier can be all-green while a spec's own stated verification is false

> Follow-on from plan-045 (#162). Observed during execution; the specific instance was fixed, the class was not.

## What happened

plan-045 Epic 6 reported a green final sweep, measured: `cargo test` 4...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #163 — yf-herdr: multi-harness fan-out — dispatch bead work to secondary sessions of other agent kinds

> ## Scope

Dispatch bead work to **secondary sessions of other agent kinds** — codex, pi, opencode, and any
future `--kind` — rather than only to a `claude` subordinate. This is the half of #110 that
p...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #151 — yf-research: link_normalizer.py breaks composite/cluster-prefixed source ids
Labels: priority::medium, type::bug
> Discovered while packaging research 004. link_normalizer.py render_sources_md() uses sid = s.get('id') or s.get('original_id'). A multi-cluster research project carries cluster-local ids ('1','2',...)...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #150 — research 004: process-defect mining across 83 plan bundles
Labels: priority::medium
> Coarse tracking issue for research 004 (precedent: #146 for research 003).

Bundle: docs/research/004-plan-process-defect-mining/ — commit 2adad77 on main.

QUESTION: across 83 plan bundles in five re...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #149 — M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
Labels: type::task, priority::high
> Filed from research 004 (docs/research/004-plan-process-defect-mining, epic yf-mol-fsp, commit 2adad77).

Two defect classes that share one root cause: a step with no exit code is not a step.

M9 (ran...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #147 — Source-scorer defect: domain_authority floors all non-docs.<vendor>.com hosts at 30
Labels: type::task, priority::medium
> Found during REFINE of research 003 (critique C-7). The credibility scorer used by yf-research assigns domain_authority=30 to every source whose host does not match docs.<vendor>.com. In research 003 ...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #145 — New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

> > **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-r...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #140 — yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model

> ## Summary

`yf-plan` and `yf-research` bundles are OKF-shaped **only at the root**. `index.md` / `log.md` exist at the bundle root and nowhere below it, so every subdirectory requires a full content ...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #127 — web/concepts: define idiomatic workflow terms (pouring beads, landing the plane, red-team, etc.)
Labels: type::task, priority::low, docs, web
> In the Concepts material, explain the idiomatic workflow vocabulary: 'pouring beads', 'landing the plane', 'red-team', and other recurring workflow-step terms. A glossary a cold reader can use to deco...

**Disposition:** partial
**Notes:** EXP-005: RESCOPE, do NOT close. The three named exemplars are present but the stated 'cold reader can decode the docs' criterion is measurably unmet — ten high-frequency terms are undefined. Issue 5.7 adds them.

## #126 — yf-voice: deferred local voice-skill hoist (reuse yf-drift-check trigger shape + voice-stylist/readability-critic agents)
Labels: type::task, priority::low, follow-on
> Deferred follow-on from plan-035 (VOICE.md). Hoist the repo-root VOICE.md into a local voice skill: reuse the yf-drift-check on-edit trigger shape to fire on human-facing prose edits, and adapt dixson...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #124 — web/concepts: new 'Concepts: beads & the yf-beads-* skills' document
Labels: type::task, priority::medium, docs, web
> New Concepts doc covering: what beads is; why we use it; why we have skills that override/guardrail beads behavior. Call out each beads feature we use (gates, formulas, epics, labels). Include a large...

**Disposition:** include
**Notes:** EXP-005: delivered, but carries a six-vs-five yf-beads-* miscount. Fixed by Issue 5.6, closed by 6.1.

## #123 — web: 'Managed files' reference section (AGENTS.md, CHANGE-VALIDATION.md, DRIFT-CHECK.md, ...)
Labels: type::task, priority::medium, docs, web
> A web/ section documenting the various managed files the skills produce/consume — AGENTS.md, CHANGE-VALIDATION.md, DRIFT-CHECK.md, .markdown-lint-on-edit, etc. Each managed file needs an explanation o...

**Disposition:** include
**Notes:** EXP-005: managed-files.md covers all four named files plus more. Closed by Issue 6.1.

## #122 — web/yf-plan+yf-research: document each subagent and each workflow step in detail
Labels: type::task, priority::medium, docs, web
> In web/, provide detailed documentation of yf-plan and yf-research: each subagent (role, inputs/outputs, dispatch) and each step of the multi-phase workflows....

**Disposition:** include
**Notes:** EXP-005: 15/15 subagents have named rows in workflows.md. Survived the skeptical read. Closed by Issue 6.1.

## #121 — Pi config tuning re-verification (plan-033 deferral REQ-YF-TUNE-017)
Labels: type::task, priority::medium, deferred, plan-033-followon
> plan-033 shipped Pi skills+rules but DEFERRED Pi config tuning: research-002 Q6 marks Pi's config surface (settings.json/permissions.json/mcp.json) [uncertain] (questionable-tier only), and rust-embed...

**Disposition:** partial
**Notes:** D-7: a CORRECT deferral, not fixed here. Pi's config surface is uncertain on a questionable-tier source; baking a guess into a released binary is worse. Issue 6.3 comments; release notes state --harness pi tunes rules+skills only.

## #120 — Codex project_doc_max_bytes (32 KiB) block-size-budget check for yf managed rule block (plan-033 R8/F7)
Labels: type::task, priority::medium, deferred, plan-033-followon
> Codex concatenates AGENTS.md sources capped at project_doc_max_bytes (32 KiB default; plan-033 codex.json raises it to 65536). A yf managed rule block in ~/.codex/AGENTS.md competes with operator cont...

**Disposition:** include
**Notes:** EXP-005: the suspected multi-file residual did NOT survive scrutiny — the issue itself scopes to a single file and REQ-YF-TUNE-027 records that as a chosen limitation. Clean close by Issue 6.1.

## #119 — Per-harness yf doctor/settings-drift axis for codex/opencode/pi (008/009 analogs, plan-033 deferral)
Labels: type::task, priority::medium, deferred, plan-033-followon
> plan-033 deferred the per-harness yf doctor read-only settings-drift axis + docs/recommended-settings.md drift gate (the REQ-YF-TUNE-008/009 analogs) for codex/opencode/pi. recommended-settings.md car...

**Disposition:** partial
**Notes:** EXP-005: axes delivered (REQ-YF-TUNE-026, observed live), but the close is GATED on correcting docs/recommended-settings.md:269-271, which still asserts the deferral. The -008 half is retired as out of scope; pi's settings axis rides on #121. Issues 4.7 then 6.2.

## #113 — yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)

> ## Observation

Across `d3-pxe` plan-013, four real defects were found in review. **All four are the same class**, and one escaped every pass:

| Found by | Defect |
| :-- | :-- |
| Conformance | Issu...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #111 — Investigate `br` (beads_rust) and `ticket-rs` as beads alternatives

> ## Context

The `yf-*` skill family is wired deeply into `bd` (beads) semantics: the `bd ready` → `bd update --claim` → `bd close` loop, gate-typed dependency edges, `--json` parsing, `bd mol pour` fo...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #104 — web: prevent runaway Pelican devservers + add clean teardown (port naba#21)

> ## Problem

The Pelican `-lr` (listen + autoreload) devserver leaks runaway processes. Two failure modes, both observed in sibling repos:

1. **Orphaned workers.** When the shell/session that ran `mak...

**Disposition:** deferred
**Notes:** Local dev ergonomics only; never reaches published content.

## #102 — .markdown-lint-on-edit -> .yf/markdown-lint-on-edit: gitignore semantics + migrate.rs rename

> ## Summary
Move the markdown-lint opt-in marker `.markdown-lint-on-edit` → `.yf/markdown-lint-on-edit`, to consolidate under the `.yf/` sidecar. **No compiled code consumes the marker** (grep: zero hi...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #93 — Portable skill/scaffolding template derived from naba's agent-tools pattern
Labels: type::task, priority::low
> Deferred stretch from plan-009 (agent-tools SPEC). Author a portable skill/scaffolding template any harness-tool could adopt to implement the agent-tools SPEC (docs/specifications/agent-tools.md) — th...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #90 — yf-change-validation: default recipe of actionlint + shellcheck for repos with .github/workflows
Labels: enhancement, type::task, priority::low
> **Lesson from pybridge plan-010 / the v0.1.33 release work.**

Every workflow / embedded-shell edit was validated pre-push with `actionlint` (which also runs `shellcheck` on `run:` blocks) + `yq` for ...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #62 — Propose yf-spec skill: build & manage specifications; yf-plan SPEC-first integration

> ## Proposal

Introduce a new **`yf-spec`** skill dedicated to building and managing specifications (the `SPEC.md` requirements surface: `REQ-*` ids, testable/non-testable classification, the living-am...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #60 — yf-beads-upstream: support mutually-exclusive requires:<platform> labels in worklist filtering + hoist

> ## Summary

Teach the `yf-beads-upstream` skill about platform-constraint labels (`requires:linux`,
`requires:macos`, `requires:windows`) so the **status / pull** worklist hides issues that
can't be w...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #59 — Follow-on (plan-018): on-disk content materialization seam + Windows targets

> Deferred scope from **plan-018** (decision 7 + Windows; not built in that plan).

## On-disk content materialization (decision 7)
Today rust-embed content deploys only to `.claude/skills` / `.agents/s...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #53 — Add Linear upstream tracking support
Labels: type::feature, priority::medium
> Add Linear as a supported upstream issue-tracking backend for beads (yf-beads-upstream), alongside the existing GitHub support. Push open/deferred beads to Linear; map beads issue IDs to Linear issues...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #52 — Add Jira upstream tracking support
Labels: type::feature, priority::medium
> Add Jira as a supported upstream issue-tracking backend for beads (yf-beads-upstream), alongside the existing GitHub support. Push open/deferred beads to Jira; map beads issue IDs to Jira issues....

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #51 — Add GitLab upstream tracking support
Labels: type::feature, priority::medium
> Add GitLab as a supported upstream issue-tracking backend for beads (yf-beads-upstream), alongside the existing GitHub support. Push open/deferred beads to GitLab issues; map beads issue IDs to GitLab...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #41 — yf-owned _shared/: make yf the install-time vendoring engine (embed _shared/, fan into consumers)
Labels: enhancement
> ## Summary

Deferred architecture option (c) from plan-016 (#15) scoping. Move the canonical shared-helper source under **`yf` ownership**: embed `_shared/` in the `yf` binary (`#[folder = "<parent>/_shared...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.

## #40 — PEP-723 micro-package route for shared Python helpers (longer-term alternative to _shared/ vendoring)
Labels: enhancement
> ## Summary

Longer-term alternative to the in-repo `_shared/` vendoring pattern (plan-014, extended by the #15 broader sweep) for consolidating duplicated Python helpers across yf skills: publish shar...

**Disposition:** deferred
**Notes:** D-6: deferred wholesale. Not observable by a user of the v0.5.0 release; including it would multiply the plan and delay a release whose entire point is user-facing accuracy.
