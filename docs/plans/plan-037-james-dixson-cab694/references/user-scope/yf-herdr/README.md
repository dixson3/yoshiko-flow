---
type: Reference
okf_spec: OKF-PLAN
id: yf-herdr-readme-user-scope
retrieved: '2026-08-13'
source: file://~/.claude/skills/yf-herdr/README.md
vendored: true
vendored_note: >-
  Verbatim copy of the user-scope `yf-herdr` skill as it stood when plan-037 hoisted it into this repository.
---

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

## Status

Draft, authored 2026-08-12 in user scope for hoisting into `dixson3/yoshiko-flow`. The deviation
taxonomy is seeded from real executions (plan-013, plan-014), three of which produced upstream
issues — yoshiko-flow#112, #113, #114.
