---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: Replace bd-backend push with gh-direct issue creation

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #133 — yf-beads-upstream design: replace 'bd <backend> push' with gh-direct issue creation across push/hoist/land (bd reads beads, gh writes issues)

> ## Proposal

Change the upstream mechanism to: **`bd` reads bead content, `gh` creates and updates issues, `bd update --external-ref` records the mapping.** Apply across all three write paths — `push`...

**Disposition:** include

**Notes:** The core swap; all four of its open decisions resolved at scoping.

## #117 — yf-beads-upstream: push is write-only — no verb proposes CLOSING upstream issues whose work is done

> ## Summary

`yf-beads-upstream` can **create and update** upstream issues but has no path that ever proposes **closing** one. Every verb runs in the push direction; nothing reconciles the reverse edge...

**Disposition:** include

**Notes:** Coarse signal discharged via #131's stamp rather than a per-plan plan.md-status reader (no plans-root coupling). Closes the 'partial' in REQ-BUP-052.

## #131 — yf-plan: stamp the coarse tracker URL onto the plan epic so closable can see it
Labels: enhancement
> Follow-up filed by plan-038 (Issue 4.5). **File-only** — implementing it is `yf-plan`'s scope, not `yf-beads-upstream`'s.

## Problem

`yf-beads-upstream closable` (shipped in plan-038, `REQ-BUP-052`)...

**Disposition:** include

**Notes:** Stamp relocated from the filed §4.5 to Phase 5 after the pour - there is no epic id at intake.

## #132 — yf-beads-upstream: BACKEND_AUTH has no jira entry — --backend jira emits GITHUB_TOKEN
Labels: type::task, priority::medium, upstream-followup
> Found by the plan-038 drift-check. BACKEND_AUTH maps only github and gitlab; push_command_sequence() falls back to ('gh','GITHUB_TOKEN') for any other backend, so 'upstream.py push --backend jira' emi...

**Disposition:** supersede

**Notes:** Mooted, not fixed: the whole --backend surface and BACKEND_AUTH are removed.

## #51 — Add GitLab upstream tracking support
Labels: type::feature, priority::medium
> Add GitLab as a supported upstream issue-tracking backend for beads (yf-beads-upstream), alongside the existing GitHub support. Push open/deferred beads to GitLab issues; map beads issue IDs to GitLab...

**Disposition:** exclude

**Notes:** Reframed, not rejected - becomes 'add a backend to a gh-direct architecture'. Left OPEN with a comment.

## #52 — Add Jira upstream tracking support
Labels: type::feature, priority::medium
> Add Jira as a supported upstream issue-tracking backend for beads (yf-beads-upstream), alongside the existing GitHub support. Push open/deferred beads to Jira; map beads issue IDs to Jira issues....

**Disposition:** exclude

**Notes:** As #51.

## #53 — Add Linear upstream tracking support
Labels: type::feature, priority::medium
> Add Linear as a supported upstream issue-tracking backend for beads (yf-beads-upstream), alongside the existing GitHub support. Push open/deferred beads to Linear; map beads issue IDs to Linear issues...

**Disposition:** exclude

**Notes:** As #51.

## #60 — yf-beads-upstream: support mutually-exclusive requires:<platform> labels in worklist filtering + hoist

> ## Summary

Teach the `yf-beads-upstream` skill about platform-constraint labels (`requires:linux`,
`requires:macos`, `requires:windows`) so the **status / pull** worklist hides issues that
can't be w...

**Disposition:** exclude

**Notes:** Label SEMANTICS in enumerate/hoist; adjacent to this plan's label EMISSION but a separate feature.

## #111 — Investigate `br` (beads_rust) and `ticket-rs` as beads alternatives

> ## Context

The `yf-*` skill family is wired deeply into `bd` (beads) semantics: the `bd ready` → `bd update --claim` → `bd close` loop, gate-typed dependency edges, `--json` parsing, `bd mol pour` fo...

**Disposition:** exclude

**Notes:** Different question. Mildly informed by this plan: gh-direct narrows the bd surface a replacement must match.
