---
type: Plan
okf_spec: OKF-PLAN
description: 'Regenerate user-facing website/docs (#317): unbreak the pelican build,
  repair Class-A content defects at every site, and close the Class-B harvest/generation-pipeline
  defects'
id: plan-066-james-dixson-e7fadb
author: james-dixson
created: '2026-09-05'
status: investigating
---
# Plan: Regenerate user-facing website/docs (#317): unbreak the pelican build, repair Class-A content defects at every site, and close the Class-B harvest/generation-pipeline defects

**ID:** plan-066-james-dixson-e7fadb
**Author:** james-dixson
**Created:** 2026-09-05
**Status:** investigating

## Objective
Regenerate user-facing website/docs (#317): unbreak the pelican build, repair Class-A content defects at every site, and close the Class-B harvest/generation-pipeline defects

## Motivation

**The site does not build, and has not since plan-057.** Reproduced on this branch,
2026-09-05, against `main` at `77eb7fe`:

```
CRITICAL RuntimeError: skill_pages: no authored web/content/skills/<name>.md
for: yf-okf-hygiene. Every skill needs an authored page (add one under web/content/skills/).
```

`web/plugins/skill_pages.py` is fail-closed: it enumerates skills from frontmatter and raises
if any lacks an authored page. So this is not a gap in a published site — **it halts the
build**, and every claim about "what the site renders" is unfounded because it renders nothing.
`.github/workflows/web-deploy.yml` chains off a successful Release, so a release cut today
would carry the failure to the deploy step.

Two failure classes have been conflated, and separating them is the point of this plan:

- **Class A — content defects.** Docs contradict the code. Repaired by editing.
- **Class B — process defects.** The harvest/generation pipeline cannot see, or cannot carry,
  the facts it publishes. Repaired *only* by changing the pipeline.

Every Class-A fix is a one-time patch that silently re-drifts until the matching Class-B defect
is closed — which is why this plan closes Class B **first** and lets the new coverage find and
then verify the Class-A repairs.

`web/content/` was last touched 2026-08-26 (plan-054, *"make the website true"*). **Eight**
plans have landed since, so #317's Class-A table is a stale snapshot in one direction only: it
cannot know about drift introduced after it was written.

This is **Plan 3 of 3**. Siblings #315 (README layout contract, closed 2026-09-02) and #316
(OKF corpus backfill, closed 2026-09-06 by plan-065) are both complete, so the sequencing
precondition #317 declares is satisfied.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #317 | Plan 3/3: regenerate user-facing docs (the site does not currently BUILD) | include | The plan of record. Both its declared predecessors (#315, #316) are closed. | _TBD_ |
| #104 | web: prevent runaway Pelican devservers + add clean teardown | include | Folded per D3 — this plan runs `pelican` repeatedly and #317 flags it as likely to bite. | _TBD_ |
| #127 | web/concepts: define idiomatic workflow terms | include | Folded per D3. #317 records it as excluded originally but "may fold here". | _TBD_ |
| #363 | OKF-EXTENSION.md documentation remediation | include | Folded per D3 — same content-defect class, `docs/` surface. | _TBD_ |
| #322 | docs yf-okf-hygiene SKILL.md: the "31 legacy, 7 halt" figure | include | Folded per D3 — a skill-doc content defect the web skill page can inherit. | _TBD_ |
| #247 | Drift findings no declared edge covers | partial | This plan closes the four Class-B coverage gaps #317 enumerates, not all of #247's manifest gap. | _TBD_ |
| #263 | META: "two facts, one signal" | partial | The `optional`/`required` token defect (Class-B item 6) is an instance of this class. The META issue stays open. | _TBD_ |
| #273 | The command-vs-obligation law | exclude | Informs how checks are written; not itself in scope. | — |
| #312 | Process-audit stage: amend the poured DAG | exclude | Orthogonal — the enforcement half, on the yf-plan axis. | — |
| #365 | plan-065 execution tracking | exclude | A prior plan's tracker; unrelated to this work. | — |

## Scoping Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D1 | **Re-derive the defect inventory mechanically.** Build runnable checkers, run them over the current tree to produce the inventory. #317's Class-A table is used as a **negative-control set**: every row it names must be found by a checker, or that checker is blind. | The table is eight plans stale and can only under-report. A hand-verified repair of a stale list would assert coverage the plan never had. The negative control is what distinguishes "the checkers found nothing" from "the checkers cannot see". |
| D2 | **Class B before Class A** (after the P0 build unbreak). Close the coverage gaps first, then let the new coverage find and verify the Class-A repairs. | #317's own argument. The inverse order lands coverage green by construction, which proves nothing about whether it would have caught the defects it was written for. |
| D3 | **Fold in #104, #127, #363, #322** alongside #317. | #104 (devserver teardown) will bite: this plan runs pelican repeatedly. #127 (concepts glossary) is content this regeneration would otherwise leave undone. #363 and #322 are the same content-defect class on the `docs/` and `skills/` surfaces. |
| D4 | **Acceptance is a local clean build plus green checkers.** No deploy. | Matches #317's stated acceptance and keeps this a `standard` plan with no outward-facing write. Exercising `web-deploy.yml` publishes to yoshikoflow.sh and would need its own consent gate. |
| D5 | **The plan authors no engine fix for defects it merely finds.** A pipeline defect outside the four Class-B items in scope is filed, not fixed. | Bounds a plan whose subject is drift detection and would otherwise absorb every defect the new checkers surface. |

## Investigation Findings

### Planned experiments (pre-investigation checkpoint)

| # | Question | Why it can change the plan |
| :-- | :-- | :-- |
| EXP-001 | Of the claim classes #317's Class-A table names, which are **mechanically checkable** and which are irreducibly prose? Produce a census with a worked checker for at least one class. | **This experiment can refute D1.** If most claim classes are prose-only, "re-derive mechanically" buys a thin checker plus a manual sweep wearing a checker's clothes, and the scope must change to say so. |
| EXP-002 | For each of the six Class-B defects #317 asserts, does it reproduce against the **live** drift-check engine — and does the proposed remedy actually close it? Item 6 in particular claims `*`-glob pairing structurally cannot detect "zero instances on one side", and that flipping `optional`→`required` does **not** fix it. | If a defect does not reproduce it leaves scope; if a remedy does not close its defect, the epic is wrong. Item 6's claim is the one that decides whether a new existence check is needed at all. |
| EXP-003 | The build is **fail-closed on the first error**, so exactly one failure is currently observable. With a stub `yf-okf-hygiene` page in place, what else fails? Separately: what is #104's devserver failure mode, and does it bite a batch regeneration? | The P0 is scoped as "author one page". If the build fails again behind it, the P0 is an unknown-size epic, not a one-issue fix. |
| EXP-004 | How are the six `.png` files derived from their `.d2` sources — is there a committed target, is regeneration deterministic/reproducible, and does anything check `.d2` ↔ `.md` agreement? | #317 requires repairs "at all sites together, re-rendering affected PNGs". If regeneration is not reproducible, a diagram repair is unverifiable and needs a different discharge. |

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
