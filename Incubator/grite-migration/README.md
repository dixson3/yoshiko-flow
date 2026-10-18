---
title: Grite Migration
created: 2026-10-18
tags:
- incubator
- beads
- grite
- migration
- issue-tracking
status: exploring
last_reviewed: 2026-10-18
priority: normal
aliases:
- grite-migration
type: Incubator
okf_spec: OKF-INCUBATOR
---

## Resume

- **Last reviewed**: 2026-10-18
- **State**: Initial investigation done. Two inventories, a gap analysis and a draft plan outline (P-0..P-2, A-1..A-5, B-1..B-4, C-1..C-2, D-1..D-3) are written. No plans have been scoped yet.
- **Next action**: The operator reviews `plans-outline.md` and answers Q1/Q2. Then scope P-0 (yf-plan integration-branch landing, on `main`) and P-1 (grite viability go/no-go) via `/yf-plan`.
- **Open threads**:
  - Q1/Q2: yf-plan has no integration-branch strategy, and plan-root placement is unresolved.
  - grite correctness defects (fresh-clone rebuild returns 0 events; worktrees share an actor) gate everything (P-1).
  - Shim provisionally rejected in favour of an intent-level `yf tracker` layer (03 §3).
- **Context to reload**: this README; `research/03-gap-analysis.md`; `plans-outline.md`; then 01 and 02 for evidence.

## Status

Exploring. The investigation found that grite 0.5.3 lacks issue types, statuses beyond open/closed, priority, a ready query, per-issue metadata, external refs, hierarchy edges, gates and formulas. It also has correctness defects that block adoption. A viability go/no-go (P-1) therefore comes before the build phases.

Setup: Long-running branch `grite-migration` was cut from local `main` at `a9e03f1`. It is checked out in the locked worktree `.worktrees/grite-migration`, and both stay in place until the migration is declared complete. Per-plan working branches and worktrees are cut from `grite-migration` and pruned as usual. This incubator lives on `grite-migration` and does not exist on `main` until the integration branch merges.

## Premise

Evaluate replacing beads (`bd`) with grite (neul-labs/grite) as the issue tracker underneath yoshiko-flow. Grite covers issue creation, tracking and dependencies, but it uses labels to classify issues and appears to have no gates and no formula/molecule (`bd mol pour`) system. yf workflow conventions that rely on those features must be rebuilt, as label/pattern conventions, as support scripts (formula pour, ephemeral work, upstream hoist to GitHub/GitLab/Jira), or a combination.

The migration runs in four phases, each made of one or more yf-plans executed against `grite-migration`:

- **A. Build** the grite tooling yf needs.
- **B. Integrate** that tooling alongside beads. yf stays usable throughout the transition.
- **C. Remove** beads tooling.
- **D. Optimize** yf for grite.

A beads shim (`bd`-shaped commands backed by grite) is one candidate for A/B. It has to be justified before it is accepted, and rejecting it is an acceptable outcome.

## Open questions

1. **Integration-branch support in yf-plan.** `plan_manager.py` supports only `landing-strategy ∈ {main, feature-branch}`. `main` cuts execute from the default branch and merges back to it. `feature-branch` cuts from `<plan-id>`. Neither can base on, or merge into, `grite-migration`. Options: (a) a prerequisite plan on `main` that adds an `integration-branch` strategy, such as `landing-strategy: branch:<name>`; (b) run grite plans with `feature-branch` and merge them into `grite-migration` by hand; (c) run yf-plan from inside the grite worktree. That only works if `_default_branch` can be pointed at `grite-migration`, and it cannot be today because it reads `origin/HEAD`.
2. **Plan folder location.** yf-plan writes plan folders primary-side, and the primary checkout is on `main`. Plans scoped to `Incubator/grite-migration/plans/` would then be written into a tree where this incubator does not exist. Options: also land the incubator on `main` (docs only), or make the plan root follow the integration branch.
3. **Coexistence model for phase B.** Should beads and grite be dual-written, or selected per repo by a backend switch? Which is the source of truth during the transition?
4. **Gate replacement.** Options: label conventions (`gate:human`, `gate:session`), a dedicated issue type, a blocking dependency on a "gate issue" that a script closes, or a combination.
5. **Formula replacement.** Options: a yf-owned formula engine (TOML → grite issues + deps + labels), or dropping formulas in favor of skill-scripted DAG creation. How are ephemeral (wisp) issues represented and garbage-collected?
6. **Shim qualification.** Which criteria would justify a `bd` shim? Candidates: number of call sites, how complete the `--json` output contract must be, and test cost. What is the rejection threshold?
7. **Upstream hoist.** Does grite sync with GitHub/GitLab/Jira natively, or must `yf-beads-upstream` be ported as a backend-neutral `yf-upstream`?
8. **Worktree semantics.** Does grite's store resolve to the same data from a worktree? yf-plan's INV-2 probe (`_bd_resolves_from`) depends on this.

## Decision log

- 2026-10-18 — Long-running branch `grite-migration` cut from local `main` (`a9e03f1`). Worktree `.worktrees/grite-migration` created and locked with `git worktree lock`, so `git worktree prune` will not remove it. — The operator required a persistent integration branch that stays usable throughout the transition.
- 2026-10-18 — Provisional: reject a `bd`-CLI-compatible shim; build an intent-level tracker layer with beads and grite backends instead. — A shim would have to reproduce bd's output quirks, could hide semantic differences behind exit 0, and cannot select a backend per repo. The conventions have to be built either way (03 §3). The phase A red team should re-examine this.
- 2026-10-18 — Provisional: add a viability go/no-go (P-1) before phase A. — grite's fresh-clone rebuild returns 0 events with `ok: true`, worktrees share an actor identity, and the project has been idle since 2026-07 (01).
- 2026-10-18 — Incubator created on `grite-migration`, not `main`. — Keeps grite research and plans out of `main` until validated. The cost is open question 2.

## Files

- [research/01-grite-capabilities.md](research/01-grite-capabilities.md) — grite 0.5.3 capability inventory, with a sandbox smoke session
- [research/02-yf-beads-touchpoints.md](research/02-yf-beads-touchpoints.md) — every yf dependency on bd, with live corpus counts
- [research/03-gap-analysis.md](research/03-gap-analysis.md) — capability mapping, shim qualification, threats
- [plans-outline.md](plans-outline.md) — prerequisite plans plus the phase A–D plan sequence

## Beads to file

<!-- empty until incubation → build -->
