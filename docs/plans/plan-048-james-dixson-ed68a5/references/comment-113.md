---
type: Reference
okf_spec: OKF-PLAN
id: comment-113-draft
disposition: partial
target: https://github.com/dixson3/yoshiko-flow/issues/113
---

# Drafted comment for #113 (partial)

> **DRAFT — not posted.** Posting is gated on the "Upstream write" capability gate.

---

`plan-048-james-dixson-ed68a5` has landed the **precondition** for the execution-rehearsal DAG walk this issue
proposes, but not the walk itself. #113 stays **OPEN**.

**What landed.** The extractor's reading grammar was widened so the historical corpus is
actually walkable. Corpus unparsed residue dropped **150 → 81** across 48 plans, and the
number of plans carrying *any* unparsed construct dropped **33 → 24**. Thirty-nine
constructs were recovered across 15 plans, in four classes: an `Issue N.M` noise-word
prefix inside `Blocks:`, `Epic N` → `epic:N`, column-0 `depends-on`/`resolves-upstream`
sub-keys, and a title parenthetical before the colon. **Zero corpus documents were
modified** — the widening is hash-neutral by construction.

**Why the walk is still blocked, honestly.** 81 constructs remain unreadable, and they are
refused *by design* rather than by omission:

| Refused class | Count |
| :-- | --: |
| `Blocks:` referent with a prose tail or trailing qualifier | 35 |
| `depends-on` with a prose tail, or the `start-gate` referent | 22 |
| a whole gate block written inside `## Epics` | 16 |
| epic-level `- depends-on: Epic N` fan-out | 7 |
| dangling `depends-on` target | 1 |

A DAG walk over a plan with a non-empty `unparsed[]` would be walking a knowably incomplete
graph. `REQ-DATA-043` (landed here) makes that explicit: **every** `plan_extract` consumer
must return **INCONCLUSIVE (exit 2)**, never FAIL, when `unparsed[] != []`. So the walk this
issue proposes now has a defined behaviour on 24 of 48 plans — it reports that it cannot
read them, rather than producing a confident wrong answer.

**The 20-vs-127 figure this issue carried is settled**, and #113's own thread already
records the correction. `pour_fidelity` over the merged tree reports **2 dropped edges in 2
plans** across 44 comparable plans, and separates "invented in cleanly parsed plans" from
"invented where the document is unreadable" — the latter is not a pour defect.

**Carried to plan-049:** **16 of the 81** refusals are a *free* recovery — the
gate-block-inside-`## Epics` class is perfectly parseable and is refused only because
recovering it means relocating a section, which `plan-048-james-dixson-ed68a5`'s D-4 forbids. A plan permitted to
write documents recovers all 16 at no analytical cost.

Plan: `docs/plans/plan-048-james-dixson-ed68a5/`.
