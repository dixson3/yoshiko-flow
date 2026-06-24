# Upstream #38: Reconcile policy: local beads = active work only; non-active work lives upstream (hygiene + upstream skills)

- **Number:** 38
- **Title:** Reconcile policy: local beads = active work only; non-active work lives upstream (hygiene + upstream skills)
- **URL:** 
- **State:** OPEN
- **Labels:** type::feature, priority::medium

## Body

Encode an operator policy into the beads skills so local/upstream stay reconciled automatically.

## Policy (operator-stated)

1. **Local beads are for actively-worked items only.** Everything else stays upstream until explicitly pulled down via a `/yf-plan` plan.
2. **Reconcile detects obsolete upstream issues.** A reconcile pass should surface upstream issues that may have been made obsolete — e.g. a merged plan's coarse tracking issue that is now delivered — and propose closing them (gated).
3. **Land-the-plane hoists follow-on beads.** A follow-on / discovered bead created *during plan execution* should be hoisted upstream and removed locally as part of land-the-plane, not left to linger on the local active worklist.

## Where it lands (two skills, orthogonal axes)

- **`yf-beads-hygiene`** — today audits graph *content* (orphaned/dangling edges). Add a **reconcile** pass (or sibling subcommand) that diffs local non-closed beads against upstream issues and flags: (a) local beads not actively worked that have/need an upstream home → propose hoist+close; (b) upstream issues likely obsolete (merged-plan coarse trackers) → propose close. Read-only-first, gated repair, consistent with the existing audit→repair discipline.
- **`yf-beads-upstream`** — extend the land-the-plane / close-time push so follow-on beads filed during execution are hoisted upstream and **removed locally** (not just pushed). Must respect the coarse-vs-granular granularity config (see #17).

## Carve / interaction

- Hygiene's existing axis = graph content integrity; this adds a local↔upstream *reconciliation* axis. Keep the safe-audit discipline (resolve via `bd show`, never blind `bd list`).
- Upstream skill owns the push/backend mechanics; hygiene proposes, upstream executes the hoist.

## Precedent

Manual reconcile done 2026-06-24: closed obsolete #35 (plan-012 delivered); hoisted local beads tr0→#27, 25d→#17, 3ma→#36, phd→#37 and closed them locally; kept only the active Epic 7 subtree local.

Plan-scale — warrants its own `/yf-plan`.
