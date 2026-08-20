---
type: Reference
okf_spec: OKF-PLAN
id: edge-audit
description: Hand audit of the 39 recovered edges (Issue 1.4b / SC1b)
---

# Hand audit of recovered edges (Issue 1.4b — SC1b)

**SC1b:** for a sample of **>= 20 recovered constructs across >= 10 plans**, each recovered edge
matches the author's evident intent, with **zero adverse findings** — or each adverse finding
traced to a named class-D/E refusal.

This audit adjudicates the **whole population**, not a sample: 39 recoveries across 15 plans.
Auditing all of them costs no more than sampling and removes the question of whether the sample
was favourable.

**Adverse findings:** 0

## Method

Every row is reproducible from `plan_extract` output — the `recovered[]` array carries the
before/after pair for each recovery:

```bash
uv run _shared/plan_extract.py docs/plans/*/ --json \
  | python3 -c 'import json,sys;[print(d["plan_id"],r) for d in json.load(sys.stdin) for r in d.get("recovered",[])]'
```

Adjudication asks one question per row: **does the recovered edge match what the author
evidently meant?** Not "is the recovery plausible" — a plausible wrong edge is the failure
mode R1 names, and it is worse than no edge at all.

## A defect this audit found in its own instrument

The first run of this audit reported **43** recoveries across **17** plans. That was wrong, and
the audit is what caught it.

`Blocks:` values are refused **whole** when any referent is unreadable (Issue 1.4a). But the
recovery *log* was written per-token, as each referent resolved — so it recorded recoveries
inside values that were then refused. Six rows were affected:

| Plan | Line | Value | Logged | Actually materialized |
| :-- | :-- | :-- | :-- | :-- |
| plan-027 | 244 | `Blocks: Epics 2, 3 (Rust implementation)` | `epic:2` | nothing |
| plan-029 | 395 | `Blocks: Issues 3.1, 4.1, 5.1 — i.e. **all implementation…**` | `3.1` | nothing |
| plan-029 | 408 | `Blocks: Issues 2.1, 2.2 (assessment …), 3.3, 4.2, 5.2` | `2.1` | nothing |
| plan-037 | 331 | `Blocks: Epics 2, 3, 4` | `epic:2` | nothing |
| plan-038 | 313 | `Blocks: Epic 3, Epic 5` (see note) | — | `epic:3`, `epic:5` |
| plan-046 | 287 | `Blocks: Epic 2, Epic 3` (see note) | — | `epic:2`, `epic:3` |

This is the **half-complete edge list hazard relocated into the audit log**. The edge list was
always correct — nothing wrong was ever materialized — but an auditor reading the log would
have adjudicated six edges that do not exist, and signed off on a recovery the extractor never
performed. Recoveries are now **staged** and committed only when the whole value resolves;
`_shared/test_plan_extract.py` pins it ("a recovery inside a REFUSED Blocks value is not logged
as recovered").

## Adjudicated rows

| # | Plan | Line | Class | Before | After | Intent match |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | `plan-007` | 180 | title-parenthetical | `Issue 1.6(firing surface)` | `Issue 1.6` | ✅ |
| 2 | `plan-007` | 185 | title-parenthetical | `Issue 1.7(portability probe)` | `Issue 1.7` | ✅ |
| 3 | `plan-007` | 200 | title-parenthetical | `Issue 2.3(discovered)` | `Issue 2.3` | ✅ |
| 4 | `plan-007` | 231 | blocks-epic-ref | `Epic 2` | `epic:2` | ✅ |
| 5 | `plan-007` | 231 | blocks-epic-ref | `Epic 3` | `epic:3` | ✅ |
| 6 | `plan-011` | 238 | blocks-issue-prefix | `Issue 5.1` | `5.1` | ✅ |
| 7 | `plan-012` | 231 | col0-subkey | `- resolves-upstream: #32 (include)` | `  - resolves-upstream: #32 (include)` | ✅ |
| 8 | `plan-012` | 247 | col0-subkey | `- resolves-upstream: #31 (include)` | `  - resolves-upstream: #31 (include)` | ✅ |
| 9 | `plan-012` | 264 | col0-subkey | `- resolves-upstream: #29 (include)` | `  - resolves-upstream: #29 (include)` | ✅ |
| 10 | `plan-012` | 273 | col0-subkey | `- resolves-upstream: #30 (include)` | `  - resolves-upstream: #30 (include)` | ✅ |
| 11 | `plan-012` | 298 | col0-subkey | `- resolves-upstream: (none — operator…` | `  - resolves-upstream: (none — operat…` | ✅ |
| 12 | `plan-012` | 329 | col0-subkey | `- resolves-upstream: (none — operator…` | `  - resolves-upstream: (none — operat…` | ✅ |
| 13 | `plan-013` | 232 | title-parenthetical | `Issue D.4(reconcile step)` | `Issue D.4` | ✅ |
| 14 | `plan-014` | 167 | title-parenthetical | `Issue C.2(reconcile step)` | `Issue C.2` | ✅ |
| 15 | `plan-015` | 272 | title-parenthetical | `Issue E.2(#25)` | `Issue E.2` | ✅ |
| 16 | `plan-015` | 281 | title-parenthetical | `Issue E.4(reconcile step)` | `Issue E.4` | ✅ |
| 17 | `plan-016` | 221 | title-parenthetical | `Issue D.1(reconcile step)` | `Issue D.1` | ✅ |
| 18 | `plan-037` | 198 | title-parenthetical | `Issue 2.2(#100)` | `Issue 2.2` | ✅ |
| 19 | `plan-037` | 206 | title-parenthetical | `Issue 2.3(#107)` | `Issue 2.3` | ✅ |
| 20 | `plan-037` | 214 | title-parenthetical | `Issue 2.4(#101)` | `Issue 2.4` | ✅ |
| 21 | `plan-037` | 341 | blocks-issue-prefix | `Issues 2.2` | `2.2` | ✅ |
| 22 | `plan-038` | 236 | title-parenthetical | `Issue 3.4(#105 residual)` | `Issue 3.4` | ✅ |
| 23 | `plan-038` | 313 | blocks-epic-ref | `Epic 3` | `epic:3` | ✅ |
| 24 | `plan-038` | 313 | blocks-epic-ref | `Epic 5` | `epic:5` | ✅ |
| 25 | `plan-038` | 322 | blocks-issue-prefix | `Issues 3.3` | `3.3` | ✅ |
| 26 | `plan-041` | 462 | blocks-issue-prefix | `Issue 4.1a` | `4.1a` | ✅ |
| 27 | `plan-041` | 462 | blocks-issue-prefix | `Issue 4.4` | `4.4` | ✅ |
| 28 | `plan-042` | 394 | blocks-issue-prefix | `Issue 3.8` | `3.8` | ✅ |
| 29 | `plan-042` | 394 | blocks-issue-prefix | `Issue 3.3` | `3.3` | ✅ |
| 30 | `plan-042` | 394 | blocks-issue-prefix | `Issue 4.1` | `4.1` | ✅ |
| 31 | `plan-043` | 430 | blocks-issue-prefix | `Issue 1.3` | `1.3` | ✅ |
| 32 | `plan-043` | 430 | blocks-issue-prefix | `Issue 2.2` | `2.2` | ✅ |
| 33 | `plan-044` | 428 | blocks-issue-prefix | `Issue 2.4` | `2.4` | ✅ |
| 34 | `plan-044` | 446 | blocks-issue-prefix | `Issue 3.7b` | `3.7b` | ✅ |
| 35 | `plan-045` | 502 | blocks-issue-prefix | `Issue 5.1` | `5.1` | ✅ |
| 36 | `plan-045` | 520 | blocks-issue-prefix | `Issue 3.1` | `3.1` | ✅ |
| 37 | `plan-046` | 287 | blocks-epic-ref | `Epic 2` | `epic:2` | ✅ |
| 38 | `plan-046` | 287 | blocks-epic-ref | `Epic 3` | `epic:3` | ✅ |
| 39 | `plan-046` | 299 | blocks-issue-prefix | `Issue 4.3b` | `4.3b` | ✅ |

## Findings

**Adverse findings: 0.** Every recovered edge matches the author's evident intent.

Three observations that are **not** adverse, recorded so the absence of an adverse finding is
not mistaken for an absence of scrutiny:

1. **A title parenthetical carrying an upstream reference is dropped, not promoted.**
   `- Issue E.2 (#25): …` (plan-015 L272), `Issue 2.2 (#100)` (plan-037 L198) and three
   siblings put a `#N` in the parenthetical. The recovery yields the id `E.2` — correct — and
   **drops** the `#N` rather than promoting it to `resolves_upstream`. That is deliberate: a
   `#N` in a title is a human annotation, and reading it as a *declared disposition* would
   invent an upstream edge the author never wrote in the `resolves-upstream` key. The id
   recovery is what the class claims; the parenthetical's content is out of its scope. Net
   position is still a strict improvement — before the widening the whole issue was invisible.

2. **Two plan-012 `col0-subkey` recoveries recover nothing.** L298 and L329 read
   `- resolves-upstream: (none — operator-requested; rolls into the coarse tracking issue)`.
   The sub-key is recovered and attached to its issue, then yields **no** upstream entry
   because there is no `#N` to find. The log records a recovery that materialized an empty
   list. This is benign — the author's intent was explicitly *none* — but it means the
   recovery count is not identical to an edge count, and no criterion should treat it as one.

3. **`Epics 2` (singular referent, plural noun) recovers only where the rest of the value is
   readable.** plan-038 L313 (`Epic 3, Epic 5`) and plan-046 L287 (`Epic 2, Epic 3`) recover
   fully. plan-037 L331 (`Epics 2, 3, 4`) and plan-027 L244 (`Epics 2, 3 (Rust
   implementation)`) are refused whole. The asymmetry is correct and is the point of 1.4a: in
   `Epics 2, 3, 4` the bare `3` and `4` are epic references only by **inference from the
   neighbouring token**, not by any property of the token itself.

## Refused classes (adjudicated as correctly refused)

Each is a named class-D/E refusal, reported with a line number and never repaired:

| Class | Count | Example | Why refusal is right |
| :-- | :-- | :-- | :-- |
| `Blocks:` referent with a prose tail or trailing qualifier | 35 | `- Blocks: Epic 5 (decommission install.py)` | the qualifier may or may not narrow the referent; no rule distinguishes the cases |
| `depends-on` with a prose tail, or the `start-gate` referent | 22 | `- depends-on: 1.5 (skill must exist first)` | same ambiguity; `start-gate` names a pour artifact, not a plan issue |
| a gate block written inside `## Epics` | 13 + 3 | plan-008's `### Capability Gate: d2 present` and its six field bullets | recovering it means relocating a whole section, which is a document rewrite — barred by D-4 |
| epic-level `- depends-on: Epic N` | 7 | plan-005 L238 | an epic fan-out is not an issue edge; expanding it invents one edge per child |
| dangling `depends-on` target | 1 | plan-015 `B.4 -> B.3` | the target names no issue in the plan |

**Total refused: 81.** See `docs/plans/plan-048-james-dixson-ed68a5/assets/residue-analysis.md`
for why this exceeds the approval-fixed target of 54.
