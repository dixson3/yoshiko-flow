---
type: Asset
okf_spec: OKF-PLAN
description: "Posted comment for upstream #263 (two-facts-one-signal META) — POSTED 2026-09-07; issue LEFT OPEN as a partial."
---
<!-- THE POSTED BODY IS EVERYTHING BELOW THIS COMMENT. The frontmatter above is
     bundle metadata (OKF REQ-OKF-003) and was NOT part of the upstream write:
     posted; #263 stays open. -->

## One instance closed by plan-066 — the META class STAYS OPEN

`plan-066-james-dixson-e7fadb` closed one instance of this class and, in passing, produced two
more data points for it.

### The instance

**The `optional`/`required` Reachability token enforces nothing.** Measured by A/B rather than
argued: flipping `skill-page` from `optional` to `required` is **byte-identical either side** —

```
BASELINE (optional)                    MUTATED (required)
  EDGE INSTANCES (intersection): 19      EDGE INSTANCES (intersection): 19
  source-only -> NOTHING CHECKED:        source-only -> NOTHING CHECKED:
    ['yf-okf-hygiene']                     ['yf-okf-hygiene']
```

The cause is structural: **edge pairing computes the INTERSECTION** of the two globs, so an
artifact missing from one side drops out of the pairing taking its own absence with it. A
reachability *token* cannot change that. The proposed remedy was therefore **dropped as inert**,
and the check was rebuilt as a **set difference** (`A \ B` FAILs, `B \ A` advisory) with a
vacuity floor.

### Two further instances found while doing it

1. **`e-okf-version-pin` carried a §3 *Contract* term in its §2 *Check Category* column**, so the
   edge selected **no check engine**. A vacuous check that looked configured.
2. **`e-skill-page-desc` scored 4 firing opportunities and 0 catches** — not because the edge was
   weak, but because it was **never dispatched**. Dispatched by hand it returned 3 FAILs with
   quoted evidence. *Coverage is not detection*, and a manifest edit cannot fix a dispatch gap.

### The general lever this plan added

`REQ-CHECK-009` now requires a mechanical gate to **declare what it does not cover** — by edge or
claim class, in a machine-readable `not_checked` field and in its documented contract — because
**a green with an undeclared boundary is indistinguishable from a green with none**. That is aimed
squarely at this class, though it does not exhaust it.

The META issue stays **open**: this is one instance plus a partial mitigation, not the class.
