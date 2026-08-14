---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #92: OKF export-emit integration for yf-plan/research/incubator (deferred)

- **Number:** 92
- **Title:** OKF export-emit integration for yf-plan/research/incubator (deferred)
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement

## Body

Deferred implementation tracker, split out from research #91 (OKF compliance-delta).

**Decision (2026-07-19): defer.** See \`docs/research/001-okf-compliance-delta/DECISION.md\`. Local bead: \`yf-uz5k\` (deferred).

## Scope (when revived)

Export-emit OKF integration: a thin per-skill emitter projecting conformant YAML frontmatter (mandatory \`type\` key) + whole-bundle nested \`index.md\` trees on demand, with \`okf_conformance_check.py\` wired as a gate. Keep each tool's native metadata as source of truth.

## Why deferred

- OKF is a **v0.1 draft**; one confirmed consumer (Google's Knowledge Catalog), **no confirmed non-Google adopter**.
- **No materialized demand** — no consumer wants yf-* plan/research/incubator folders as OKF bundles.
- True cost is a whole-bundle conformant tree (nested \`index.md\`), not a one-line \`type\` key.
- Extension-key round-trip fidelity is SHOULD-level and unverified.

## Revisit triggers

1. A concrete consumer wants a yf-* bundle as OKF.
2. OKF reaches a stable release **and** shows a non-Google production adopter.
3. We adopt an OKF-consuming tool in our own workflow.

On revival, promote to a \`/yf-plan\` effort (SPEC-first).
