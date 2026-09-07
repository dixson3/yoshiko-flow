---
type: Plan
okf_spec: OKF-PLAN
description: 'Diagram set redesign (#373): restack architecture as a layered marketecture
  with per-skill and per-formula diagrams, combine phase-model+lifecycle and install+tune,
  evaluate archify vs d2->png as the rendering toolchain, and amend DRIFT-CHECK so
  omissions FAIL'
id: plan-067-james-dixson-de852a
author: james-dixson
created: '2026-09-07'
status: investigating
---
# Plan: Diagram set redesign (#373): restack architecture as a layered marketecture with per-skill and per-formula diagrams, combine phase-model+lifecycle and install+tune, evaluate archify vs d2->png as the rendering toolchain, and amend DRIFT-CHECK so omissions FAIL

**ID:** plan-067-james-dixson-de852a
**Author:** james-dixson
**Created:** 2026-09-07
**Status:** investigating

## Objective
Diagram set redesign (#373): restack architecture as a layered marketecture with per-skill and per-formula diagrams, combine phase-model+lifecycle and install+tune, evaluate archify vs d2->png as the rendering toolchain, and amend DRIFT-CHECK so omissions FAIL

## Motivation

**Split from plan-066 at its Diagram human-read gate.** The operator read the six regenerated
PNGs and did not accept them — not because any diagram makes a false claim, but because the set
needs restructuring and because several real relationships are **absent**.

That distinction is the whole reason this plan has two halves.

`DRIFT-CHECK.md:207` holds that a page which **"curates or omits repo-dev detail PASSes — only an
affirmative contradiction FAILs"**. Under that rule an omission is invisible *by construction*.
The measured cost: `land`, retrospectives, the escalation surface, autonomy levels and `closable`
went undocumented across multiple releases and **nothing ever complained**; `architecture.d2`
omitted the entire `workflows` skill group while passing every check. plan-066 repaired those as
editorial work precisely because no edge could have flagged them.

**So a redesign alone re-drifts.** The rule change is what keeps the new diagrams complete.

The six diagrams plan-066 landed are **factually correct and mechanically checked** — the
`beads group` membership bug (count 8 while listing the *workflows* skills), the retired
`lowercase-hyphen,max64` annotation, the absent workflows group and the three-vs-five formula
count are all repaired. This plan is not a correction to them. It is a better set.

**plan-066 is parked in `executing` with its diagram gate shut** and #317 open pending a
retrospective that is gated behind that read. This plan owns the handoff that unblocks it.

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

## Scoping Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D1 | **Spike archify AND d2 on one diagram, then decide the toolchain on measurement.** Build the marketecture restack both ways and test whether the checkers can still see it. | plan-066 wired mechanical coverage to the **`.d2` artifact specifically**: `check_web_counts.py` greps `.d2` label text for counts and member ids; the `web-diagram-src` node and the CHANGE-VALIDATION §3 globs key on `*.d2`; SC10 asserts a byte-identical `d2 --theme 0 --layout elk` render. All four need a new anchor under archify, and whether an archify artifact is *greppable* and *deterministic* is measurable rather than arguable. Adopting on preference risks silently undoing plan-066's Class-B work. |
| D2 | **Land the omissions-FAIL rule FIRST; its failures become the redesign's work inventory.** | D1's precedent from plan-066, where a checker-derived inventory found 4 defect sites the source issue never listed and corrected an undercount from ~4 to 26. The inverse order lands the rule green by construction, proving nothing about whether it would have caught the omissions it was written for. |
| D3 | **All 20 per-skill diagrams**, one per skill. | Uniform and complete; every skill page can embed its own. Accepts the larger artifact count and maintenance surface as the cost of not having to adjudicate which skills "earn" a diagram. |
| D4 | **The omissions rule is a DECLARED REQUIRED SET, not a blanket subset→equal flip.** Omitting a user-facing surface (slash verb, shipped command, documented behavior, a `skill-group` cluster) FAILs; repo-dev internals may still be curated out. | A blanket flip requires every page to restate everything in its source, including detail a user-facing page deliberately curates out, and would redden many currently-green edges at once. The declared set preserves curation while closing the hole that let five real features go undocumented. |
| D5 | **This plan unblocks plan-066 at the end.** A dedicated issue hands off: redesigned diagrams land → operator reads → plan-066's gate opens → its 8.1/8.3 run → plan-066 completes and #317 closes. | Leaving plan-066 parked with no declared route to closure is the shape that produced five stale trackers in this repo (#103, #95, #96, #98, #134). |

## Investigation Findings

### Planned experiments (pre-investigation checkpoint)

| # | Question | Why it can change the plan |
| :-- | :-- | :-- |
| EXP-001 | Build the **marketecture restack** in BOTH archify and d2. Are the factual claims (skill counts, group membership, tool dependencies) **mechanically extractable** from each artifact? Is output **deterministic** enough for a byte or structural criterion? What would `check_web_counts` have to become for each? | **This experiment decides D1 and can refute it in either direction.** If archify output is not greppable or not deterministic, adopting it silently undoes plan-066's diagram coverage. If d2 cannot express the layered stack legibly, the redesign is blocked on toolchain regardless of checkability. |
| EXP-002 | What exactly must the **declared required set** contain, and is it derivable rather than hand-maintained? Enumerate the user-facing surfaces a page must document — slash verbs, shipped commands, `skill-group` clusters — and determine whether each has a machine-readable source of truth. | If the set must be hand-authored, D4 reintroduces the hand-maintained-list weakness `check_amendment_log`'s own docstring calls its soundness limit. That changes what the rule can honestly claim. |
| EXP-003 | Run the proposed rule against the CURRENT corpus. How many pages and diagrams fail, and what is the actual work inventory? | D2 makes this inventory the plan's work list. If it is enormous the scope must change; if it is empty the rule is vacuous and does not do what it is for. |
| EXP-004 | For 20 per-skill diagrams: what is the **generation** model — hand-authored, generated from `SKILL.md` frontmatter (`depends-on-tool`, `depends-on-skill`), or hybrid? What does each cost to keep current? | D3 commits to 20 artifacts. If they are hand-authored they become 20 new drift surfaces, which is what this plan exists to reduce. Generated-from-frontmatter would make them incapable of drifting — a materially different plan. |

_Findings below as they land._

## Approach
_To be determined after scoping and investigation._

## Epics
_To be determined._

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
