# Upstream Issue Triage: beads infra local-only hardening

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #58 — Define + enforce a canonical 'minimal local' beads profile (embedded/local-server, per-project, local-only, worktree-shared) via yf preflight

> ## Summary

Define a single **canonical "minimal local" beads profile** and have `yf preflight`
**confirm / enforce / correct** it for every beads-backed skill (`yf-plan`, `yf-research`,
and any call ...

**Disposition:**
**Notes:**

## #67 — Migrate legacy root-level skill configs (.<skill>.local.json) into the .yf/ namespace

> ## Problem

Skill **config** and skill **state** currently live in two different places with inconsistent conventions:

- **Config** (per-machine, gitignored, operator-authored): root-level dotfiles —...

**Disposition:**
**Notes:**

## #66 — yf-beads-init: gitignore .beads/interactions.jsonl in repair's gitignore top-up (canonicalization #39 gap)

> ## Problem

The `yf-beads-init` canonicalization repair (`yf doctor --repair`, REQ-BINIT-023 / #39)
untracks the pinned runtime set with `git rm --cached`:

`.beads/interactions.jsonl`, `.beads/embedd...

**Disposition:**
**Notes:**

## #57 — yf-beads-upstream: close-time Safety invariant reads as a hand-CLI recipe, inviting raw bd github push over /yf-beads-upstream

> ## Summary

The always-loaded close-time trigger in `yf-beads-upstream/protocols/UPSTREAM_TRACKING.md`
correctly says to **invoke `/yf-beads-upstream`** at land-the-plane, but the adjacent
**Safety in...

**Disposition:**
**Notes:**

## #60 — yf-beads-upstream: support mutually-exclusive requires:<platform> labels in worklist filtering + hoist

> ## Summary

Teach the `yf-beads-upstream` skill about platform-constraint labels (`requires:linux`,
`requires:macos`, `requires:windows`) so the **status / pull** worklist hides issues that
can't be w...

**Disposition:**
**Notes:**

## #65 — plan-019: Preflight yf self-update offer + preflight cache version-invalidation

> Coarse tracking issue for **plan-019** (one issue per plan, per the repo upstream convention). Landed to `main` — implementation, tests, and coverage gate all green.

**Plan:** `docs/plans/plan-019-ja...

**Disposition:**
**Notes:**
