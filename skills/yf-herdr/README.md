# yf-herdr

Delegates an approved `yf-plan` or gated `yf-research` project to a new herdr tab running a fresh
session of the **same agent kind**, then observes that subordinate and mines its deviations for
defects in the *planning* workflow.

- **`SKILL.md`** — trigger contract, launch procedure, observation contract, deviation taxonomy.
- **`SPEC.md`** — `REQ-HERDR-NNN` requirements and taxonomy provenance.

## Why it exists

`yf-plan` and `yf-research` both require a session boundary for execution — the fingerprint, not
conversation state, carries eligibility across it. Without this skill the operator opens a terminal,
starts an agent, and types the command by hand, and nothing watches the result.

The launch half is convenience. **The observation half is the point:** the parent session is the
only vantage point from which a plan's assumptions can be compared against what execution actually
hit, and that comparison is where planning-process defects become visible.

## Two things it deliberately will not do

- **Observe continuously.** A turn-based agent has no execution between operator turns. Observation
  happens at turn boundaries and on demand, and the skill says so rather than implying a watcher.
- **Resolve a gate, or auto-file an issue.** Gates exist to spend operator attention. Improvements
  are reported; filing waits for authorisation.

## Prerequisites

The **`herdr` binary** on `PATH`, and a session running inside a herdr-managed pane
(`HERDR_ENV=1`). Both are trigger preconditions, so where `herdr` is absent this skill is inert
rather than broken.

CLI semantics come from the third-party **`herdr` skill**, which this repo does not ship. That
relationship is a **prose soft-dep**, not a `depends-on-skill` entry — see SKILL.md
"Relationship to the `herdr` skill".

## Status

Active. Authored 2026-08-12 in user scope and imported into `dixson3/yoshiko-flow` by plan-037;
the pre-import snapshot is preserved under that plan's `references/user-scope/`. The deviation
taxonomy is seeded from real executions (plan-013, plan-014), three of which produced upstream
issues — yoshiko-flow#112, #113, #114.
