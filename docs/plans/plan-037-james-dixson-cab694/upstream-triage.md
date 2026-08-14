---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: reconcile user-scope skill installs, configurable plan roots, canonical .yf layout, yf-herdr import

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #114 — yf-plan: verify the PREMISES a plan rests on, not just its internal consistency (measurement vs inference)

> Split out of #113 as a distinct axis. #113 covers **structural** correctness — does the DAG hold together, is each precondition available when its step runs. This issue covers **factual** correctness ...

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

## #112 — yf-plan: red-team should check gate REACHABILITY, not just gate well-formedness

> ## The defect this would have caught

In `d3-pxe` plan-013, a capability gate was authored like this:

- **Condition:** operator has previewed `ansible-playbook host.yml --check --diff --tags otel_age...

**Disposition:**
**Notes:**

## #111 — Investigate `br` (beads_rust) and `ticket-rs` as beads alternatives

> ## Context

The `yf-*` skill family is wired deeply into `bd` (beads) semantics: the `bd ready` → `bd update --claim` → `bd close` loop, gate-typed dependency edges, `--json` parsing, `bd mol pour` fo...

**Disposition:**
**Notes:**

## #110 — herdr: leverage `herdr agent *` to launch and monitor agent sessions from a primary session

> ## Summary

herdr (terminal multiplexer for coding agents) exposes a socket API over its CLI that lets an agent running *inside* a herdr pane create panes, launch other coding agents into them, submit...

**Disposition:**
**Notes:**

## #109 — yf-plan: stale_approved is computed status-independently, so completed plans display "re-review before execute" forever

> `plan_manager.py list` (and `status`) tag a **completed** plan with:

```
⚠ STALE-APPROVED (re-review before execute)
```

For a plan in a terminal state this advice is not merely noisy, it is wrong: ...

**Disposition:**
**Notes:**

## #108 — yf-plan: deliberate-class heuristic false-positives ci-release on ordinary infra plans

> Follow-up to #89, which introduced the `ci-release` deliverable class (REQ-PLAN-069a).

`_classify_deliverable()` (`scripts/plan_manager.py`) suggested **`ci-release` with `confidence: high`** on two ...

**Disposition:**
**Notes:**

## #107 — yf-plan: make PLANS_DIR and INCUBATOR_PARENT configurable (currently hardcoded)

> ## Problem

`plan_manager.py` hardcodes both plan roots as module-level constants:

```python
PLANS_DIR = Path("docs/plans")
INCUBATOR_PARENT = Path("Incubator")
```

There is no config key, no env va...

**Disposition:**
**Notes:**

## #106 — yf-beads-upstream: SKILL.md Push step §3 instructs hand-running 'bd github push' — contradicts the never-hand-run safety invariant

> ## Summary

The `yf-beads-upstream` **companion rule** (`protocols/UPSTREAM_TRACKING.md`, always-loaded) states the safety invariant:

> **Route every upstream push through `/yf-beads-upstream` — do n...

**Disposition:**
**Notes:**

## #105 — yf-beads-upstream: enumerate silently returns 0 when bd auto-assigns an owner (owner_on_create unset) — must fail loud

> ## Summary

`upstream.py enumerate` (the land-the-plane push-candidate discovery) **silently returns `0 candidates`** in a repo where `bd create` auto-assigns an `owner`, whenever `custom.upstream.own...

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

## #101 — yf-change-validation: read canonical .yf/plan/config.local.json for validate-cmd seed

> ## Summary
`skills/yf-change-validation/scripts/change_validation.py:44` reads yf-plan's `validate-cmd` seed **only** from the legacy root `.yf-plan.local.json`, ignoring the canonical `.yf/plan/confi...

**Disposition:**
**Notes:**

## #100 — yf-plan plan_manager.py: align .yf/ layout to canonical short-name + canonical-first config read

> ## Summary
`skills/yf-plan/scripts/plan_manager.py` diverges from the canonical `.yf/<short>/` layout that the Rust `yf` binary emits, on **two** axes. Operator config set under the new layout is sile...

**Disposition:**
**Notes:**

## #98 — plan-034 execution tracking: post-plan-033 follow-ups (drift axis + codex budget + web docs)

> Coarse tracking issue for **plan-034-james-dixson-ac6633** (one issue per plan, per the project convention).

Post-plan-033 follow-ups, four epics:
1. **Per-harness settings-drift axis** (`yf-252c`) —...

**Disposition:**
**Notes:**

## #96 — plan-033 execution tracking: yf multi-harness provisioning (harness skills + tune + rules + revert)

> Coarse tracking issue for **plan-033-james-dixson-46aca2** (one issue per plan, per the repo Upstream Tracking convention).

**Plan folder:** \`docs/plans/plan-033-james-dixson-46aca2/\` (landed on \`...

**Disposition:**
**Notes:**

## #95 — plan-032 execution tracking: yf harness tune (settings alignment)

> Coarse tracking issue for **plan-032** (one issue per plan-scale effort, per AGENTS.md).

**Plan:** `docs/plans/plan-032-james-dixson-6cb87b/plan.md`
**Objective:** Add `yf harness tune --harness <nam...

**Disposition:**
**Notes:**

## #93 — Portable skill/scaffolding template derived from naba's agent-tools pattern
Labels: type::task, priority::low
> Deferred stretch from plan-009 (agent-tools SPEC). Author a portable skill/scaffolding template any harness-tool could adopt to implement the agent-tools SPEC (docs/specifications/agent-tools.md) — th...

**Disposition:**
**Notes:**

## #92 — OKF export-emit integration for yf-plan/research/incubator (deferred)
Labels: enhancement
> Deferred implementation tracker, split out from research #91 (OKF compliance-delta).

**Decision (2026-07-19): defer.** See \`docs/research/001-okf-compliance-delta/DECISION.md\`. Local bead: \`yf-uz5...

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
