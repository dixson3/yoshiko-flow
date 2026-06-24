# Upstream Issue Triage: reconcile policy granularity upstream hygiene

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #17 — beads-upstream: machine-enforced upstream granularity config (coarse|granular)

> Make upstream-push granularity a first-class `bd` config key the `beads-upstream` skill reads, instead of a per-repo documented convention.

## Problem

`custom.upstream.*` exposes only `enabled` and ...

**Disposition:**
**Notes:**

## #38 — Reconcile policy: local beads = active work only; non-active work lives upstream (hygiene + upstream skills)
Labels: type::feature, priority::medium
> Encode an operator policy into the beads skills so local/upstream stay reconciled automatically.

## Policy (operator-stated)

1. **Local beads are for actively-worked items only.** Everything else st...

**Disposition:**
**Notes:**
