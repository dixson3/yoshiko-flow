---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: fix upstream.py push fan-out #268

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #268 — CRITICAL: yf-beads-upstream push is unusable — owner-claim warning fans out one `bd show` per bead over the ENTIRE closed universe (~360s, presents as a silent hang)

> ## Severity: CRITICAL — the routed upstream write path does not complete

`upstream.py push` **never returns** on a repo of ordinary size. It is the path
`UPSTREAM_TRACKING.md` mandates for every upst...

**Disposition:** include

**Notes:** The whole of this plan. Epics 1-3 address the issue's three-defect diagnosis in full —
the fan-out (direction 2, chosen over direction 1 because making the warning cheap preserves
REQ-BUP-049's whole-universe semantics that scoping it would narrow), the unbounded `run()`
(direction 3), and recurrence prevention. Direction 4 (make the warning lazy/opt-in) is
**declined**: once the derivation is 0.0018 s there is nothing to defer.

Two corrections to the issue as filed, both measured and both recorded in `findings/`:

1. The `cmd_enumerate` impact the issue lists as *"likely affected identically — unverified"* is
   **confirmed** (`upstream.py:603`, the same `collect_parent_edges` call).
2. The issue's own direction 3 implies bounding `run()` would have surfaced this. **It would not
   have** — 1,801 individually-fast calls (0.186 s) trip no defensible per-call bound. The defect
   is real and independently worth fixing; the causal claim is not. Epic 2 says so explicitly.

Resolved-By: 1.1, 1.3, 2.1.
