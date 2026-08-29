---
type: Concept
okf_spec: OKF-RESEARCH
id: 001-okf-compliance-delta
superseded_by: plan-046-james-dixson-aabefa — OKF-BASELINE.md reconciled from the
  OKF v0.1 facts this project distilled to upstream OKF v0.2, quoted directly from
  the vendored spec
date: 2026-07-19 · **Status:** Decided (document-only / deferred) · **Research:**
  [001-okf-compliance-delta](Summary.md) · **Tracking:** gh-91 (closed)
---

# Decision: OKF integration for yf-plan / yf-research / yf-incubator — defer

**Date:** 2026-07-19 · **Status:** Decided (document-only / deferred) · **Research:** [001-okf-compliance-delta](Summary.md) · **Tracking:** gh-91 (closed)

## Context

Research 001 mapped the compliance delta between what `yf-plan`, `yf-research`, and
`yf-incubator` emit and what the Open Knowledge Format (OKF) v0.1 SPEC requires, and
recommended an **export-emit** integration (keep each tool's native metadata as source of
truth; add a thin on-demand OKF frontmatter emitter). The recommendation was explicitly
framed as *provisional / least-regret*, contingent on three conditions the evidence left
open (Summary.md §Executive summary).

## Decision

**Do not implement any OKF integration now.** Record the research conclusion and file a
deferred implementation bead. Neither the minimal `type`-key conformance nor the full
export-emit emitter is built at this time.

## Rationale

- **OKF is a v0.1 draft** with one confirmed production consumer (Google's own Knowledge
  Catalog) and **no confirmed non-Google adopter**. Building to a moving draft risks
  reworking against spec churn.
- **No demand has materialized.** No source establishes any consumer wanting yf-* plan /
  research / incubator folders as OKF bundles (`[insufficient evidence]` in the report).
  Absent a concrete consumer, conformance buys nothing today.
- **Real cost exceeds the "add a `type` key" framing.** The export-emit path's true cost is
  a whole-bundle conformant tree (nested per-level `index.md`), not a one-line frontmatter
  edit — not worth paying speculatively.
- **Round-trip fidelity is unverified.** Extension-key preservation is SHOULD-level, not a
  guarantee, and is undemonstrated against any specific consumer.

## Revisit triggers

Reopen the deferred bead when **any** of these hold:

1. A concrete consumer (internal or external) wants a yf-* bundle as OKF.
2. OKF reaches a stable (non-draft) release **and** shows a non-Google production adopter.
3. We adopt an OKF-consuming tool in our own workflow.

## Consequences

- The provisional `scripts/okf_conformance_check.py` from the research remains as-is
  (reference checker), not wired into any skill gate.
- No change to `plan_manager.py` heading-based audit, the `**Field:**` prose convention, or
  the `README.md` / `_index.md` reserved-index names.
- Deferred implementation tracked as a bead (`--defer`) and, if revived, promoted to a
  `/yf-plan` effort (SPEC-first).
