# Upstream #17: beads-upstream: machine-enforced upstream granularity config (coarse|granular)

- **Number:** 17
- **Title:** beads-upstream: machine-enforced upstream granularity config (coarse|granular)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Make upstream-push granularity a first-class `bd` config key the `beads-upstream` skill reads, instead of a per-repo documented convention.

## Problem

`custom.upstream.*` exposes only `enabled` and `backend`. Coarse-vs-granular (one tracking issue per plan-scale effort vs. one issue per execution bead) is currently a convention documented in this repo's `CLAUDE.md` (`## Upstream Tracking > Granularity`), but nothing enforces it — an agent must read `CLAUDE.md` and comply.

## Proposal

Add `custom.upstream.granularity` with values `coarse` | `granular`:

- `coarse` → at land-the-plane / close-time, create/update a single tracking issue linking the plan + epic; do NOT push granular sub-beads.
- `granular` → current behavior (push open/deferred beads).
- Unset → behaves as today (granular) for back-compat.

## Acceptance

- [ ] `bd config get custom.upstream.granularity` round-trips after `bd config set`.
- [ ] `beads-upstream` `SKILL.md` documents the key alongside `enabled`/`backend` and branches its push behavior on it.
- [ ] The close-time / land-the-plane trigger honors `coarse` (no granular sub-bead push) without an agent needing to read `CLAUDE.md`.
- [ ] `UPSTREAM_TRACKING.md` companion rule references the key so the close-time trigger contract reflects it.
- [ ] Back-compat: unset behaves as today.

## Context

Surfaced during plan-007 (drift-check) land-the-plane. Coarse was made this repo's default as a `CLAUDE.md` convention (commit 63e2429); this issue promotes that convention to enforced config. Tracked locally as bead `beads-skills-25d`.
