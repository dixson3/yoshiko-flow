---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #195: beads docs describe dependency types that installed bd 1.1.2 does not have: waits-for and conditional-blocks

- **Number:** 195
- **Title:** beads docs describe dependency types that installed bd 1.1.2 does not have: waits-for and conditional-blocks
- **URL:** 
- **State:** OPEN
- **Labels:** type::bug, priority::high

## Body

MEASURED. beads.gascity.com/workflows/molecules documents four dependency types with
execution semantics:

  blocks              sequential
  parent-child        hierarchy
  conditional-blocks  B runs only if A fails
  waits-for           B waits for all A's dynamic children

Installed bd 1.1.2 (Homebrew) accepts NEITHER of the last two:

  $ bd dep add --help
  -t, --type string   Dependency type (blocks|tracks|related|parent-child|
                      discovered-from|until|caused-by|validates|relates-to|supersedes)
                      (default "blocks")

WHY THIS MATTERS HERE. Both absent types were load-bearing in a capability review of
bd's molecule/formula/wisp surface against yf-plan:

- `waits-for` was proposed as the JOIN for a fan-out review wisp (companion issue).
- `conditional-blocks` was proposed as the native expression of the RED/GREEN control
  pattern that plan-050 hand-rolled as redcheck.sh + gate-run.sh — a harness whose own
  silent-green defect is recorded as plan-050 RE-004/RE-005.

Both proposals were built on the docs and would have been unbuildable. The divergence
was caught only because a peer session checked `--help` instead of the docs.

ACTION FOR THIS REPO. Any yf work that plans against a bd primitive must verify it
against the INSTALLED binary's `--help`, not against beads.gascity.com. The docs site
describes a version ahead of, or divergent from, what `bd --version` reports. This is
the same shape as this repo's own three-artifacts problem (repo source vs embedded tree
vs installed skill): the documentation and the binary are separate artifacts that move
independently.

Candidate follow-ups: (a) record the verify-against-the-binary rule where beads-backed
planning reads it; (b) determine whether these types exist as formula-level constructs
materialized differently, or are simply unreleased; (c) report the divergence upstream
to beads.

VERIFIED PRESENT in 1.1.2, for contrast: `bd cook --dry-run` and `bd cook --mode=compile`
both exist and are usable as a compile-time DAG preflight.
