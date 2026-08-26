---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #215: coordinator/bd: `started_at` is written for 86 of 225 plan beads and is not exposed by `bd list --json`

- **Number:** 215
- **Title:** coordinator/bd: `started_at` is written for 86 of 225 plan beads and is not exposed by `bd list --json`
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

**Measured:** plan-052 EXP-006 §1.

Beads carrying **both** `started_at` and `closed_at`: **86 of 225** (plan-048 alone: **0 of
39**). Separately, `bd list --json` **does not expose** `started_at` at all.

Two halves, and both are required for the field to be usable:

1. the coordinator must write `started_at` **unconditionally** when it claims a bead;
2. `bd list --json` must **expose** it, so a bulk read can see it without an N+1 of
   `bd show`.

Without both, no question about when work actually started — and therefore no concurrency
question — is answerable over this corpus.

*Filed by plan-052 as a deliberately deferred defect. Full enumeration:
`docs/plans/plan-052-james-dixson-fa8056/assets/deferred-defects.md`.*
