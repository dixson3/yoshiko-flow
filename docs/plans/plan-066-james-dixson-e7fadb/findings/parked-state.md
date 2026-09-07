---
type: Finding
okf_spec: OKF-PLAN
description: "plan-066 is DELIBERATELY PARKED in `executing` at the Diagram human-read gate, which the operator declined on 2026-09-07. Successor: #373. Unmet: SC11 and SC17. This is not a crashed or abandoned run."
id: parked-state
plan: plan-066-james-dixson-e7fadb
created: 2026-09-07
---
# PARKED — not crashed, not abandoned

**Read this first if you found this bundle in `executing` and wondered whether something died.**

`plan-066-james-dixson-e7fadb` is **deliberately parked**. Epics 0-7 are complete, merged to
`main` and pushed. Epic 8 is intentionally unfinished behind a gate the operator chose to hold.

## How to tell this apart from a crash

| Signal | A crashed run | **This run** |
| :-- | :-- | :-- |
| Why it stopped | unknown / unrecorded | **recorded here and in `log.md`** |
| The blocking gate | often already resolved, or absent | `yf-mol-a927.12` **deliberately open** |
| Uncommitted work | dirty worktree, stranded edits | **clean; everything merged and pushed** |
| Upstream | half-written or absent | **reconciled and read back** (4 closed, 7 open) |
| Successor | none | **#373**, filed by the operator |

Nothing here needs recovery. The orphan sweep has nothing to reset; there are no stuck beads.

## The operator's verdict, recorded

On 2026-09-07 the operator **declined** the *Diagram human read* capability gate
(`yf-mol-a927.12`). The verdict was explicitly **not** that any diagram makes a false claim — the
six diagrams are factually correct and mechanically checked, and all six re-render
byte-identically under the pinned `d2 v0.8.2`. It is a **redesign request plus omissions**:

- **architecture** — add tool dependencies (`gh`, `pandoc`, `d2`, `bd`); show the
  workflows → utility dependency; restructure as a layered marketecture; break out per-skill
  diagrams.
- **formulas** — drop the meta-diagram; one diagram per formula, plus a skills/agents → formulas
  map.
- **phase-model + lifecycle** — **combine**, and add red-team cycles, execution, and
  land-the-plane.
- **install-matrix + tune-matrix** — **combine**.

Plus a `DRIFT-CHECK.md` amendment making **omissions FAIL**.

**The gate is operator-only.** It may not be resolved on any evidence, however green — including
the agent reads recorded in `diagram-reads.md`, which are evidence *for* the gate and never a
discharge of it.

## Successor: #373

*"Diagram set redesign + make DRIFT-CHECK omissions FAIL."* Already filed. **It needs its own plan
and its own scoping** — it is not resumed work on this one.

Two design decisions the operator fixed in #373, recorded because they differ from the obvious
approach:

1. **The omissions rule is a DECLARED REQUIRED SET, not a blanket
   `field-set-subset` → `field-set-equal` flip.** Omitting a *user-facing surface* — a slash verb,
   a shipped command, a documented behaviour like `land` or `closable`, a skill-group cluster —
   FAILs; **repo-dev internals may still be curated out**. A blanket flip would require every page
   to restate everything in its source and would redden many currently-green edges at once.
2. **Sequencing: land the rule change FIRST**, let it fail the current diagrams loudly, and use
   that failure list as the redesign's inventory. This is **D1's precedent from this plan** — the
   inventory is checker-derived rather than hand-listed, so it cannot silently under-report.

## The two unmet criteria

| # | Status | Why |
| :-- | :-- | :-- |
| **SC11** | `not-evaluated` | The manual diagram read. No command can decide it; the gate is held. |
| **SC17** | `FALSE` (exit 2) | `plan-retrospective.md` does not exist. Issue 8.3 is gated behind SC11 via 8.1. |

All 25 other criteria **hold**. FULL `CHANGE-VALIDATION` tier on the merged tree: **79 rows, 0
failing**.

## Why there is NO retrospective draft, deliberately

It would be natural to park the state in `plan-retrospective.md`. **That file is deliberately
absent.**

`SC17`'s checker (`plan066_checks.py retro-classes`) keys on that filename containing the strings
*content defect* / *process defect* and at least two counts. A parking note written there could
satisfy that predicate and **flip SC17 from FALSE to holds while Issue 8.3 has not run** — a green
asserting work that did not happen.

That is the precise defect class this plan exists to close, so the parking record lives here
instead. `plan-retrospective.md` is presence-optional by contract
(`REQ-PORT-ACT-RETROSPECTIVE`), and its absence is never an audit finding.

## What remains, and what must NOT be done

Still open: **8.1** (verification sweep), **8.3** (retrospective), **8.4** / **8.5** (already
posted upstream; the beads remain open pending 8.3), **8.4b**, and the reconcile step.

**8.4b is a trap worth naming.** Its hard guard — *HEAD is `main` and the plan branch is merged* —
is now **satisfied**, because the partial land merged and pushed. It is still blocked on **8.3**.
Do not read the guard's satisfaction as permission.

Until the operator opens the gate, do **not**:

- resolve `yf-mol-a927.12` on any evidence;
- run the §6.4 close chain;
- `update-status complete`;
- tear down the `plan-066-james-dixson-e7fadb-execute` branch or its worktree — 8.1 and 8.3 still
  have to run there.

## Recommendations

Resume by opening the gate, then running 8.1 → 8.3 → the remaining bookkeeping. Start #373 as its
own plan, not as a continuation of this one.
