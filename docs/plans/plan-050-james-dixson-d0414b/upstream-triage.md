---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: route research 004 process-defect classes into executable controls

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #183 — plan-049-james-dixson-725bc0 execution tracking
Labels: priority::medium
> 
Coarse tracking issue for `plan-049-james-dixson-725bc0` — *Rewrite the historical plan corpus
so the constructs plan-048 refuses become readable, and bind the document linter at the two
enforcement ...

**Disposition:**
**Notes:**

## #182 — yf-plan red-team: the read-only rule forbids the sandbox spike that catches specification defects

> ## The rule as written forbids the one technique that catches specification defects

`skills/yf-plan/agents/red-team.md` makes the reviewer read-only (REQ-AGENT-043), and the
dispatching prose in `SKI...

**Disposition:**
**Notes:**

## #181 — doc_lint: a bundle copied outside docs/plans/ returns a silent green, indistinguishable from clean

> ## Copying a bundle outside `docs/plans/` to verify it yields a silent green

A natural way to test "would this bundle pass at `status: review`?" is to copy it to a scratch
directory, force the status...

**Disposition:**
**Notes:**

## #180 — yf-plan: close-reconcile-step requires the reconcile gate resolved first — undocumented chain ordering

> ## `close-reconcile-step` requires the reconcile GATE resolved first — undocumented ordering

`SKILL.md` §6.4's close chain lists `close-reconcile-step` before `verify-reconcile`, cascade-close
and th...

**Disposition:**
**Notes:**

## #179 — yf-plan: the start-gate wrapper task is orphaned at pour and blocks cascade-close

> ## The start-gate wrapper task is orphaned at pour, and blocks cascade-close

`SKILL.md` §5.2a pours a gate-type formula step that yields **two** beads: a task wrapper
(`plan-execute.start-gate`, what...

**Disposition:**
**Notes:**

## #178 — yf-plan: generate the upstream-write authorization grant FROM the Upstream Issues table, not the draft list

> ## An upstream-write authorization grant should be GENERATED from the Upstream Issues table

plan-048 halted its own reconcile because the operator's authorization grant was **hand-listed from
the dra...

**Disposition:**
**Notes:**

## #177 — yf-plan red-team: no check that a numeric target is derivable from the plan's own scope rules

> ## A numeric target can be fixed-at-approval, falsifiable, and still contradict the plan's own rules

Every red-team pass in plan-047 verified that its residue target was **fixed at approval** — the
p...

**Disposition:**
**Notes:**

## #176 — plan-048-james-dixson-ed68a5 execution tracking

> Coarse tracking issue for `plan-048-james-dixson-ed68a5` — one issue per plan-scale effort, per the
repo's Upstream Tracking convention.

**Plan:** `docs/plans/plan-048-james-dixson-ed68a5/`

**Supers...

**Disposition:**
**Notes:**

## #174 — yf-plan: a review-phase validation pass — falsify every criterion, and cross-check every claim against the code that scores it

> **Proposes the mechanism for the defect family #173 diagnoses.** #173 records *what went wrong and why five red-team cycles missed it*, under an explicit "record, do not fix" instruction. This issue p...

**Disposition:**
**Notes:**

## #173 — yf-plan: success criteria and upstream dispositions are never checked against the engine that enforces them

> Filed from plan-046 execution, at operator instruction: **record, do not fix**.

## Two concrete defects, one family

### 1. A plan instruction contradicted the engine that enforces it

plan-046 Issue...

**Disposition:**
**Notes:**

## #171 — yf-okf: nested index.md generation, deferred behind a `description:` producer change (plan-046 D-9)

> Filed by plan-046 Issue 5.5(iv). This is the **deferred half of #140**, filed upstream so the deferral is visible to the issue tracker and not only to `skills/yf-okf/spec/OKF-YF-EXTENSIONS.md` §9a.

R...

**Disposition:**
**Notes:**

## #170 — OKF consumer round-trip fidelity is unverified — #92 carve-out 3 of 3

> Filed by plan-046 Issue 5.5(iii) as one of **three named carve-outs** from closing #92 as superseded.

**The gap, stated precisely.** yf demonstrates **producer → producer** fidelity only: it writes O...

**Disposition:**
**Notes:**

## #169 — OKF conformance gate for yf-research and yf-incubator — #92 carve-out 2 of 3

> Filed by plan-046 Issue 5.5(ii) as one of **three named carve-outs** from closing #92 as superseded.

**What this is.** yf-plan's bundles are conformance-gated: `plan_manager.py audit` runs the OKF en...

**Disposition:**
**Notes:**

## #168 — yf-okf: projection delivery mode (on-demand OKF export) — #92 carve-out 1 of 3

> Filed by plan-046 Issue 5.5(i) as one of **three named carve-outs** from closing #92 as superseded. #92's emit half shipped natively and its nested-tree half is #140; these three are what a clean clos...

**Disposition:**
**Notes:**

## #166 — yf-beads-extra: document that `bd ready` silently excludes whole categories — two loops have already been built on the assumption it does not

> Follow-on from plan-045 (#162). A generalization the plan fixed twice, instance-by-instance, without naming the class.

## The behaviour

`bd ready --help` states it plainly:

> Excludes in_progress, ...

**Disposition:**
**Notes:**

## #165 — SPEC `Verification:` lines are prose shaped like commands — a FULL tier can be all-green while a spec's own stated verification is false

> Follow-on from plan-045 (#162). Observed during execution; the specific instance was fixed, the class was not.

## What happened

plan-045 Epic 6 reported a green final sweep, measured: `cargo test` 4...

**Disposition:**
**Notes:**

## #164 — CHANGE-VALIDATION: `skills/*/SPEC.md` maps to `uv-herdr-launch`, so every skill's SPEC.md runs yf-herdr's launch test

> Follow-on from plan-045 (#162). Observed during execution; deliberately not fixed in-plan.

## The mapping

`CHANGE-VALIDATION.md` §3 carries:

```
| `skills/*/SPEC.md` | `uv-herdr-launch` |
```

That...

**Disposition:**
**Notes:**

## #163 — yf-herdr: multi-harness fan-out — dispatch bead work to secondary sessions of other agent kinds

> ## Scope

Dispatch bead work to **secondary sessions of other agent kinds** — codex, pi, opencode, and any
future `--kind` — rather than only to a `claude` subordinate. This is the half of #110 that
p...

**Disposition:**
**Notes:**

## #153 — Wire PYTHONPYCACHEPREFIX out of skills/ to zero the build.rs churn tax
Labels: type::task, priority::low
> Follow-up from plan-041 Issue 1.5 spike (finding E6). After plan-041 lands cargo:rerun-if-changed=../skills, one real 'uv run pytest' cycle forces a ~5.2s full recompile because cargo walks a watched ...

**Disposition:**
**Notes:**

## #152 — feature: yf auto-updates claude-code settings.json to disable recommended skills/tools (UPSTREAM)
Labels: type::feature, priority::medium
> Have yf automatically update claude-code settings appropriately, with the recommended competing skills/tools disabled (so the yf skills take precedence). This should be filed as an upstream GitHub iss...

**Disposition:**
**Notes:**

## #151 — yf-research: link_normalizer.py breaks composite/cluster-prefixed source ids
Labels: priority::medium, type::bug
> Discovered while packaging research 004. link_normalizer.py render_sources_md() uses sid = s.get('id') or s.get('original_id'). A multi-cluster research project carries cluster-local ids ('1','2',...)...

**Disposition:**
**Notes:**

## #150 — research 004: process-defect mining across 83 plan bundles
Labels: priority::medium
> Coarse tracking issue for research 004 (precedent: #146 for research 003).

Bundle: docs/research/004-plan-process-defect-mining/ — commit 2adad77 on main.

QUESTION: across 83 plan bundles in five re...

**Disposition:**
**Notes:**

## #149 — M5/M9: process rules that nothing executes, and remediation edges that exist only in prose
Labels: type::task, priority::high
> Filed from research 004 (docs/research/004-plan-process-defect-mining, epic yf-mol-fsp, commit 2adad77).

Two defect classes that share one root cause: a step with no exit code is not a step.

M9 (ran...

**Disposition:**
**Notes:**

## #147 — Source-scorer defect: domain_authority floors all non-docs.<vendor>.com hosts at 30
Labels: type::task, priority::medium
> Found during REFINE of research 003 (critique C-7). The credibility scorer used by yf-research assigns domain_authority=30 to every source whose host does not match docs.<vendor>.com. In research 003 ...

**Disposition:**
**Notes:**

## #145 — New skill: yf-retrospective — measure escape rate (intra-plan + post-release) and enforce a fix+prevention contract

> > **Written to be read cold.** The evidence below was gathered in one session (2026-08-16) and this issue is the only record of it. Nothing here requires that conversation.

## Proposal

A new **`yf-r...

**Disposition:**
**Notes:**

## #140 — yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model

> ## Summary

`yf-plan` and `yf-research` bundles are OKF-shaped **only at the root**. `index.md` / `log.md` exist at the bundle root and nowhere below it, so every subdirectory requires a full content ...

**Disposition:**
**Notes:**

## #127 — web/concepts: define idiomatic workflow terms (pouring beads, landing the plane, red-team, etc.)
Labels: type::task, priority::low, docs, web
> In the Concepts material, explain the idiomatic workflow vocabulary: 'pouring beads', 'landing the plane', 'red-team', and other recurring workflow-step terms. A glossary a cold reader can use to deco...

**Disposition:**
**Notes:**

## #126 — yf-voice: deferred local voice-skill hoist (reuse yf-drift-check trigger shape + voice-stylist/readability-critic agents)
Labels: type::task, priority::low, follow-on
> Deferred follow-on from plan-035 (VOICE.md). Hoist the repo-root VOICE.md into a local voice skill: reuse the yf-drift-check on-edit trigger shape to fire on human-facing prose edits, and adapt dixson...

**Disposition:**
**Notes:**

## #124 — web/concepts: new 'Concepts: beads & the yf-beads-* skills' document
Labels: type::task, priority::medium, docs, web
> New Concepts doc covering: what beads is; why we use it; why we have skills that override/guardrail beads behavior. Call out each beads feature we use (gates, formulas, epics, labels). Include a large...

**Disposition:**
**Notes:**

## #123 — web: 'Managed files' reference section (AGENTS.md, CHANGE-VALIDATION.md, DRIFT-CHECK.md, ...)
Labels: type::task, priority::medium, docs, web
> A web/ section documenting the various managed files the skills produce/consume — AGENTS.md, CHANGE-VALIDATION.md, DRIFT-CHECK.md, .markdown-lint-on-edit, etc. Each managed file needs an explanation o...

**Disposition:**
**Notes:**

## #122 — web/yf-plan+yf-research: document each subagent and each workflow step in detail
Labels: type::task, priority::medium, docs, web
> In web/, provide detailed documentation of yf-plan and yf-research: each subagent (role, inputs/outputs, dispatch) and each step of the multi-phase workflows....

**Disposition:**
**Notes:**

## #121 — Pi config tuning re-verification (plan-033 deferral REQ-YF-TUNE-017)
Labels: type::task, priority::medium, deferred, plan-033-followon
> plan-033 shipped Pi skills+rules but DEFERRED Pi config tuning: research-002 Q6 marks Pi's config surface (settings.json/permissions.json/mcp.json) [uncertain] (questionable-tier only), and rust-embed...

**Disposition:**
**Notes:**

## #120 — Codex project_doc_max_bytes (32 KiB) block-size-budget check for yf managed rule block (plan-033 R8/F7)
Labels: type::task, priority::medium, deferred, plan-033-followon
> Codex concatenates AGENTS.md sources capped at project_doc_max_bytes (32 KiB default; plan-033 codex.json raises it to 65536). A yf managed rule block in ~/.codex/AGENTS.md competes with operator cont...

**Disposition:**
**Notes:**

## #119 — Per-harness yf doctor/settings-drift axis for codex/opencode/pi (008/009 analogs, plan-033 deferral)
Labels: type::task, priority::medium, deferred, plan-033-followon
> plan-033 deferred the per-harness yf doctor read-only settings-drift axis + docs/recommended-settings.md drift gate (the REQ-YF-TUNE-008/009 analogs) for codex/opencode/pi. recommended-settings.md car...

**Disposition:**
**Notes:**

## #113 — yf-plan: add an execution-rehearsal review pass (topological DAG walk against running state)

> ## Observation

Across `d3-pxe` plan-013, four real defects were found in review. **All four are the same class**, and one escaped every pass:

| Found by | Defect |
| :-- | :-- |
| Conformance | Issu...

**Disposition:**
**Notes:**

## #111 — Investigate `br` (beads_rust) and `ticket-rs` as beads alternatives

> ## Context

The `yf-*` skill family is wired deeply into `bd` (beads) semantics: the `bd ready` → `bd update --claim` → `bd close` loop, gate-typed dependency edges, `--json` parsing, `bd mol pour` fo...

**Disposition:**
**Notes:**

## #104 — web: prevent runaway Pelican devservers + add clean teardown (port naba#21)

> ## Problem

The Pelican `-lr` (listen + autoreload) devserver leaks runaway processes. Two failure modes, both observed in sibling repos:

1. **Orphaned workers.** When the shell/session that ran `mak...

**Disposition:**
**Notes:**

## #102 — .markdown-lint-on-edit -> .yf/markdown-lint-on-edit: gitignore semantics + migrate.rs rename

> ## Summary
Move the markdown-lint opt-in marker `.markdown-lint-on-edit` → `.yf/markdown-lint-on-edit`, to consolidate under the `.yf/` sidecar. **No compiled code consumes the marker** (grep: zero hi...

**Disposition:**
**Notes:**

## #93 — Portable skill/scaffolding template derived from naba's agent-tools pattern
Labels: type::task, priority::low
> Deferred stretch from plan-009 (agent-tools SPEC). Author a portable skill/scaffolding template any harness-tool could adopt to implement the agent-tools SPEC (docs/specifications/agent-tools.md) — th...

**Disposition:**
**Notes:**

## #90 — yf-change-validation: default recipe of actionlint + shellcheck for repos with .github/workflows
Labels: enhancement, type::task, priority::low
> **Lesson from pybridge plan-010 / the v0.1.33 release work.**

Every workflow / embedded-shell edit was validated pre-push with `actionlint` (which also runs `shellcheck` on `run:` blocks) + `yq` for ...

**Disposition:**
**Notes:**

## #62 — Propose yf-spec skill: build & manage specifications; yf-plan SPEC-first integration

> ## Proposal

Introduce a new **`yf-spec`** skill dedicated to building and managing specifications (the `SPEC.md` requirements surface: `REQ-*` ids, testable/non-testable classification, the living-am...

**Disposition:**
**Notes:**

## #60 — yf-beads-upstream: support mutually-exclusive requires:<platform> labels in worklist filtering + hoist

> ## Summary

Teach the `yf-beads-upstream` skill about platform-constraint labels (`requires:linux`,
`requires:macos`, `requires:windows`) so the **status / pull** worklist hides issues that
can't be w...

**Disposition:**
**Notes:**

## #59 — Follow-on (plan-018): on-disk content materialization seam + Windows targets

> Deferred scope from **plan-018** (decision 7 + Windows; not built in that plan).

## On-disk content materialization (decision 7)
Today rust-embed content deploys only to `.claude/skills` / `.agents/s...

**Disposition:**
**Notes:**

## #53 — Add Linear upstream tracking support
Labels: type::feature, priority::medium
> Add Linear as a supported upstream issue-tracking backend for beads (yf-beads-upstream), alongside the existing GitHub support. Push open/deferred beads to Linear; map beads issue IDs to Linear issues...

**Disposition:**
**Notes:**

## #52 — Add Jira upstream tracking support
Labels: type::feature, priority::medium
> Add Jira as a supported upstream issue-tracking backend for beads (yf-beads-upstream), alongside the existing GitHub support. Push open/deferred beads to Jira; map beads issue IDs to Jira issues....

**Disposition:**
**Notes:**

## #51 — Add GitLab upstream tracking support
Labels: type::feature, priority::medium
> Add GitLab as a supported upstream issue-tracking backend for beads (yf-beads-upstream), alongside the existing GitHub support. Push open/deferred beads to GitLab issues; map beads issue IDs to GitLab...

**Disposition:**
**Notes:**

## #41 — yf-owned _shared/: make yf the install-time vendoring engine (embed _shared/, fan into consumers)
Labels: enhancement
> ## Summary

Deferred architecture option (c) from plan-016 (#15) scoping. Move the canonical shared-helper source under **`yf` ownership**: embed `_shared/` in the `yf` binary (`#[folder = "../_shared...

**Disposition:**
**Notes:**

## #40 — PEP-723 micro-package route for shared Python helpers (longer-term alternative to _shared/ vendoring)
Labels: enhancement
> ## Summary

Longer-term alternative to the in-repo `_shared/` vendoring pattern (plan-014, extended by the #15 broader sweep) for consolidating duplicated Python helpers across yf skills: publish shar...

**Disposition:**
**Notes:**
