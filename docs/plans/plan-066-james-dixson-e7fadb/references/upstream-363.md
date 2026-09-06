---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #363 - OKF-EXTENSION.md documentation remediation: 3
  stale DRAFT banners, 2 dangling symbols, 2 shipped-but-open decisions (#247)'
---
# Upstream #363: OKF-EXTENSION.md documentation remediation: 3 stale DRAFT banners, 2 dangling symbols, 2 shipped-but-open decisions (#247)

- **Number:** 363
- **Title:** OKF-EXTENSION.md documentation remediation: 3 stale DRAFT banners, 2 dangling symbols, 2 shipped-but-open decisions (#247)
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::low, follow-on

## Body

Measured by plan-064 EXP-003. Routed to #247 rather than fixed in plan-064, because the subject
matter is disjoint (engine config under `skills/` vs. bundles under `docs/plans/`) and #318/#320/#321
are open P0/P1s in the `--skill` / member-resolution path that plan's backfill exercises.

**The drift, measured across the three `skills/*/OKF-EXTENSION.md` files:**

1. **3 stale `Status: DRAFT — proposal only` banners** — all three files still carry a plan-029
   DRAFT banner while plan-029 is `complete`.
2. **2 dangling symbols:**
   - `skills/yf-research/OKF-EXTENSION.md` cites `HEADER_TEMPLATE`, which was deleted from
     `index_manager.py` **in the same commit that created the file citing it**.
   - `skills/yf-plan/OKF-EXTENSION.md` cites `seed_readme`; the actual symbol is `seed_index`.
3. **2 shipped-but-"open" decisions** recorded as undecided in files where the decision has landed.

**Why nothing caught it:** `grep -i extension DRIFT-CHECK.md` returns nothing — no §1 node covers
any of the three files, so plan-054's full 52-edge sweep (the sweep that produced #247) could not
look. This is the same class of gap, in the same file, for the same reviewer.

**Adjacent gap, recorded rather than absorbed:** a **fifth** vendored `okf.py`
(`skills/yf-okf-hygiene/scripts/okf.py`) has no node and no edge — DRIFT-CHECK.md §1 declares four
`okf-copy-*` nodes for five copies. All six copies are byte-identical today, so it is uncovered but
happens to be in sync.

**Calibration, stated honestly:** a cross-ref edge here would have caught **none** of #319/#320/#321
(2xP0, 1xP1), which all live *inside* these files. This is a documentation-hygiene instrument, not a
P0 instrument.

**Note (plan-064 Issue 5.1):** the two missing `CHANGE-VALIDATION.md` §3 trigger rows for
`yf-research` and `yf-incubator` **have been added** — that was the honest slice. What remains here
is the `DRIFT-CHECK.md` node work and the content remediation above.

Evidence: `docs/plans/plan-064-james-dixson-a0b7fa/findings/exp-003-okf-extension-drift-nodes.md`
