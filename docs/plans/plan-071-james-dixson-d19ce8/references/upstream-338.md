---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #338 - yf-plan red-team runs NO mechanical checker —
  check_amendment_log and gate_consistency were both missed by review and caught later'
---
# Upstream #338: yf-plan red-team runs NO mechanical checker — check_amendment_log and gate_consistency were both missed by review and caught later

- **Number:** 338
- **Title:** yf-plan red-team runs NO mechanical checker — check_amendment_log and gate_consistency were both missed by review and caught later
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

## The gap

`agents/red-team.md` instructs the reviewer to run **no mechanical checker**. Grepping it for
every checker name this repo ships returns exactly one hit — an incidental remark about
`doc_lint`'s `cell-vocabulary` column-location behaviour at `:66`, not an instruction to run
anything.

Meanwhile the repo ships checkers that apply *directly to a plan bundle* and that a reviewer
could run in seconds:

| Checker | What it would have told a reviewer |
| :-- | :-- |
| `scripts/check_amendment_log.py --plan <id>` | whether the plan's DAG expresses SPEC-first ordering |
| `skills/yf-plan/scripts/gate_consistency.py <plan_dir>` | whether a gate names an issue it blocks |
| `skills/yf-plan/scripts/plan_extract.py --strict` | cycles, dangling edges, unparsed constructs |
| `scripts/checks/check_okf_index_drift.py` | bundle-index drift |
| `skills/yf-okf/scripts/okf.py reindex --check <plan_dir>` | the same, scoped to one bundle |

## Measured: this cost plan-062 twice

**Instance 1 — `check_amendment_log`, missed by SEVEN passes.** plan-062 ran seven red-team
passes. Every one of them checked the DAG: cycles, dangling `depends-on`, `Discharged-by`
resolution, issue-criterion coverage, gate reachability. **None ran `check_amendment_log`
against it.** The plan's own `SC13c` ran that script — but against `SPEC.md`, not the DAG.

The defect surfaced at *execution*, as `ESC-001`: assertion **A2 requires a DIRECT `depends-on`
path from every implementation issue to a REQ-naming Epic-0 issue**, and plan-062's ordering was
only transitive. A2 failed for **all 17 implementation issues**, `SC13c` could not pass, and the
executing session had to edit `plan.md`'s `## Epics` on an already-poured plan, add two matching
`bd` edges, and take a re-fingerprint — which required a fresh operator authorization because
the edit invalidated the approval.

**Instance 2 — `gate_consistency.py`, missed by two passes.** Pass 3 recorded, verbatim: *"The
repo's own `gate_consistency.py` returns FAIL on this plan and no pass has run it."* It returned
`verdict: FAIL` because a gate's Instructions named the issue it blocked. One wording change
made it PASS.

Two different checkers, two different passes, same shape: **an available mechanical check that
nobody pointed at the artifact it validates.**

## Why prose review cannot substitute

This is not a reviewer being careless. A2's requirement — *direct* rather than transitive
edges — is invisible to a human reading a DAG, because the transitive ordering **is** correct
and reads as correct. Only the checker distinguishes them. Likewise `gate_consistency`'s arm 1
is a mechanical string-vs-`Blocks`-set comparison no reader reliably performs.

The passes were not weak: they found 57 concerns, several by sandbox spike. The gap is
categorical, not one of effort.

## Suggested direction (not prescriptive)

- Add a **mandatory mechanical-sweep step** to `agents/red-team.md`: run every checker that
  accepts a plan bundle or plan id, and report each verdict in the pass file. Cheap, and it is
  the one part of a review that needs no judgement.
- Make `ready-check` (or the Phase-3 audit) run the bundle-applicable subset, so the gap cannot
  depend on a reviewer remembering. `check_amendment_log` already exposes `--plan`.
- Consider whether `check_amendment_log`'s A2 should be reachable from `plan_extract --strict`,
  so an ordering defect is caught at extraction rather than at execution.

Adjacent to the recurring finding this repository keeps rediscovering: a check that exists but
is never aimed produces the same silence as a check that does not exist.

## Provenance

Found during **plan-062** (`plan-062-james-dixson-c3e98f`, tracker #330) — instance 1 at
execution as `ESC-001`, instance 2 in `reviews/pass-3.md` as C31.

