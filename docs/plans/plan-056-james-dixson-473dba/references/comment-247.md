---
type: Reference
okf_spec: OKF-PLAN
description: "Draft upstream comment for #247 — the declared-listing-with-no-generator mechanism shipped; the rest of the drift findings stay open."
---
**Partial. §1's mechanism shipped; the remaining findings stay open.**

This issue's §1 observation — *a declared listing with no generator is the same defect as index
drift* — is exactly right, and plan-056 acted on it by building **one** generator/checker that
serves both:

- **`REQ-OKF-CHK-004`** — the corpus index-drift driver, wired into `CHANGE-VALIDATION.md` in the
  FAST and FULL tiers. It enumerates bundle roots by **depth-1 glob** (never `rglob`, which would
  descend into a bundle's own fixture corpora and treat each as a root), **hard-errors on a
  nonexistent enumerated root** so a typo can never be demoted into a clean verdict, and emits
  `bundles_checked` with a `--min-roots` floor so a driver that read nothing cannot report clean.
- **`REQ-PLAN-081`** — the producer half: `reindex_write` at intake/execute-start/close and a public
  `index-add` verb, so a declared listing has a generator that is actually reachable.

**The ordering was the hard part, and it is recorded.** Wiring the gate before the producer fix and
the corpus repair would have made the FAST tier fire red on every subsequent edit — *including the
edits performing the repair*. So the gate row depends on the producer fix and on the corpus repair
by explicit DAG edges, and the corpus was measured clean (62 bundles, 0 drifting) before the row was
added.

**The rest of this issue is not discharged** — it names a broader set of drift findings no edge
covers, and only the §1 mechanism was in scope.

Plan: `docs/plans/plan-056-james-dixson-473dba/`
