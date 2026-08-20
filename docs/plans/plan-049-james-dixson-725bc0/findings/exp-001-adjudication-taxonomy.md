---
type: Finding
okf_spec: OKF-PLAN
id: exp-001
status: complete
---
# EXP-001 — Adjudication taxonomy for the 65 non-free constructs

**Question:** Of the 65 constructs plan-048 refused (excluding the 16 "free" relocations), which
are cheaply adjudicable, which need author intent, and which are unrecoverable?

## Approach Tested

Read the plan-048 handoff §1 and `assets/residue-analysis.md`; ran `plan_extract.py` over
`docs/plans/*/` and classified every `unparsed[]` entry by `reason` + `raw`; collapsed entries to
**distinct document lines** (refusal is per-value, so a line is one adjudication regardless of how
many entries it emits); read surrounding epic/gate context for every non-free construct; grepped
the extractor for the accepted referent alphabet; cross-checked each claimed gate against its
plan's `## Gates`.

## Result

**1. The residue reproduces exactly.** **measured:** `total 81, plans 24 of 48` — identical to
plan-048, with every class count matching (Blocks 35, depends-on 22, gate-block 16, fan-out 7,
dangling 1).

**2. The 65 are 51 adjudications, not 65.** **measured:** 67 distinct lines total, minus 16 free =
**51**. The 65-entry figure double-counts multi-referent lines (`plan-026 L387` emits 6 from one).

**3. The "16 free" set is measurably NOT what the handoff describes.**

- **measured:** distribution is `plan-008: 7, plan-010: 3, plan-045: 3, plan-018: 2, plan-015: 1` —
  five plans, not "plan-008 with singletons in 018 and 045".
- **measured:** only `plan-008` L269–275 is an actual relocatable gate block.
- **measured:** `plan-010`'s 3 are prose cross-references to gates that **already exist correctly**
  in `## Gates`. Relocating them yields **zero edges**.
- **measured:** `plan-018` L231 is `### Epic 6 (follow-on, NOT built in this plan)` — deliberately
  unbuilt scope. `plan-045` L459 is a prose section.
- **inferred:** only **7 of 16** are the free relocation the handoff promises; 8 are cosmetic;
  1 is a real repair that D-2's split cuts in half.

### The adjudication table (51 lines / 65 entries)

| Class | Entries | Lines | Cost | Edge yield |
| :-- | --: | --: | :-- | --: |
| `Blocks: reconcile step (<upstream #s>)` | 14 | 7 | **(a)** | 7 |
| `Blocks:` multi-referent + restating parenthetical | 6 | 4 | **(a)** | 13 |
| `Blocks: <id> (<restates title>)` | 3 | 3 | **(a)** | 3 |
| `depends-on: <id> (<rationale>)` | 3 | 3 | **(a)** | 3 |
| plan-015 orphan cluster | 2 | 2 | **(a)** | 2 |
| `Blocks:` "and"-joined / transitive qualifier | 6 | 5 | **(b)** | ~7 |
| **Epic-level `depends-on: Epic N`** | 6 | 6 | **(c)** | **0 safe** |
| **Issue-level `depends-on: Epic N`** | 9 | 5 | **(c)** | **0 safe** |
| `Blocks:` qualifier may NARROW | 5 | 5 | **(c)** | **0 safe** |
| Gate reference (`start-gate`, `gate:…`) | 7 | 7 | **(d)** | 0 |
| Names a non-issue (decision id) | 1 | 1 | **(d)** | 0 |
| `depends-on: —` (null) | 3 | 3 | (a)/null | 0 |
| **Totals** | **65** | **51** | | **~35** |

**Recoverable:** **23 adjudications** recover **~35 edges** from 35 of 65 entries (54%).
≈3–4 hours. The (c) fan-out family is 15 entries in only **3 plans** (005, 037, 038) — descoping
those removes 23% of the residue and **100% of the dangerous class**.

### Two sizing caveats

**All 24 residue plans are `status: complete`.** ~35 edges against a corpus of 927 have **no
operational consumer** — no bead will be poured from a complete plan again. The yield is real but
**archival**.

**The residue metric undercounts unreadability by roughly its own magnitude.** **measured:**
`plan-010` has 38 issues, **33 `depends-on:` declarations, 0 parsed edges, 7 unparsed entries**.
The trailing-inline form (`… (per-skill file list). depends-on: 1.1`) is neither parsed **nor
counted as residue**. Corpus-wide: **89 such declarations** across plan-006 (8), plan-007 (12),
plan-009 (15), plan-010 (33), plan-012 (21). **plan-006 and plan-007 report 0 unparsed and 0 edges
— the extractor calls them perfectly clean while 20 declarations go unread.**

## Implications for Plan

**1. D-4's DAG-invariance postcondition is VACUOUS for this plan's writes, and blind on the axis
that matters.** Every refused construct contributes **0 edges**, so no recovery can decrease the
count — **the postcondition is vacuously satisfied by all 51 writes and validates nothing.** And
the dangerous class fails on the *unguarded* side:

- **measured:** expanding the 11 fan-out lines by cross-product gives plan-005 **99 invented edges
  on a plan that currently reads 15 (+660%)**; plan-037 → 19 on 20; plan-038 → ~23 on 19.
  **~141 invented edges from 11 lines.**
- **inferred:** DAG-invariance **passes all 141 cleanly.** D-8 was designed against an observed
  *decrease* (20 emptied declarations). The residual hazard has the **opposite polarity**.

**2. Constructs where recovery would CHANGE rather than ADD an edge:**

- **plan-033 L511** `- depends-on: 6.2, 1.5, gate:pi-rule-target-verified` — the only construct
  where the document currently **disagrees with bd**. bd carries `6.2` and `1.5`; the extractor
  does not. An adjudicator rewriting it gate-only **deletes two edges bd holds**, and
  extractor-side invariance sees `0 → 0` and reports clean. **Invisible on both sides.**
- **plan-015 L210 + L215 + L220** — one repair, three fixes. Fixing L210's bold title adds issue
  B.3 and shifts every later ordinal. **L210 is inside the "free 16" while L215/L220 are in the
  65 — D-2's split cuts a single 3-line repair in half, and neither half is correct alone.**
- **plan-018 L231** — inside the "free 16". Recovering it **invents issues deliberately never
  built.** Exclude it from the relocation batch explicitly.

## Recommendations

1. **Add a paired UPPER-BOUND postcondition** — no plan's edge count may grow by more than the
   number of adjudicated lines in it — or the write phase is unguarded on the axis that matters.
2. **Re-cut D-2's free/adjudicated boundary** so the plan-015 cluster is one work item.
3. **Sequence:** build the upper bound → plan-015's 3-line cluster (the only repair yielding real
   edges on both paths) → the 7 `reconcile step` lines (single shape, zero ambiguity) → plan-029's
   4 lines (~13 edges) → **stop**. Descope the 15 fan-out and 8 gate-reference entries: the
   fan-outs are the dangerous class, and the gate references are **not recoverable by any document
   write** — the parser has no gate vocabulary for `depends-on` at all. That is REQ-DATA-019
   alphabet work, not migration work.
4. **Honest sizing.** ~35 of 65 recoverable in ~23 adjudications, landing **+3.8% edges on a
   corpus where every affected plan is `complete`**. Worth doing **only if the write-phase
   machinery and the corrected postcondition are the deliverable and the edges are a side effect.**
   If the goal is corpus readability, the **89-declaration inline-`depends-on:` dark matter** is
   larger, cheaper, entirely unambiguous — and currently reported as clean.
