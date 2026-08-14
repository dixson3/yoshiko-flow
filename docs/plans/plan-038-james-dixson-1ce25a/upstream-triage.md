---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: upstream push invariant enforcement, closable verb, hand-run bd backend

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #128 — yf-okf skill: add reference/link to the Google OKF spec
Labels: type::task, priority::low, docs
> The yf-okf skill should include a reference/link to the Google OKF (Open Knowledge Framework) spec it derives from....

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

## #125 — yf-plan: optional status-enum hardening for update-status (currently free-form, no validation)
Labels: type::task, priority::low, follow-on
> Follow-on from plan-035 (5.2 honesty fix). plan_manager.py update-status is a free-form writer with no enum guard — a typo'd status writes silently; the 9-value vocabulary (scoping..complete) is doc/s...

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

## #118 — yf-plan README.md stale: still lists README.md as plan-folder orientation file (pre-OKF), contradicts index.md/log.md in SPEC REQ-PLAN-010 + SKILL.md
Labels: type::task, priority::medium
> Surfaced by plan-036 e-skill-page-readme drift check as a CONFLICT: skills/yf-plan/README.md lines ~97,144 describe 'README.md — orientation (file map, reading order)' but the OKF migration reserved i...

**Disposition:**
**Notes:**

## #117 — yf-beads-upstream: push is write-only — no verb proposes CLOSING upstream issues whose work is done

> ## Summary

`yf-beads-upstream` can **create and update** upstream issues but has no path that ever proposes **closing** one. Every verb runs in the push direction; nothing reconciles the reverse edge...

**Disposition:**
**Notes:**

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

## #106 — yf-beads-upstream: SKILL.md Push step §3 instructs hand-running 'bd github push' — contradicts the never-hand-run safety invariant

> ## Summary

The `yf-beads-upstream` **companion rule** (`protocols/UPSTREAM_TRACKING.md`, always-loaded) states the safety invariant:

> **Route every upstream push through `/yf-beads-upstream` — do n...

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
