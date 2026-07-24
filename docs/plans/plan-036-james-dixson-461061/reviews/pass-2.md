---
type: Review
okf_spec: OKF-PLAN
plan: plan-036-james-dixson-461061
pass: 2
---
# Red-Team Review — pass-2 (re-review after REVISE)

**Plan:** plan-036-james-dixson-461061
**Date:** 2026-07-24

## Verdict: APPROVE

All seven pass-1 concerns (C1, C3, C4, C5, C6, C7 + M1-M3) are genuinely resolved and verified
against the real manifest (`DRIFT-CHECK.md`), the schema (`yf-drift-check/spec/schema.md`), and the
plugin (`skill_pages.py`). The revisions introduced no new high or medium concern.

## Per-concern confirmation
- **C1 (high) RESOLVED, schema-clean.** Three node-sourced edges `e-skill-page-desc` (`skill-md` →
  `skill-page`), `-readme` (`skill-readme` →), `-spec` (`per-skill-spec` →), name-paired; all three
  source nodes exist in live §1, the new `skill-page` node is added. Satisfies "every edge
  references §1 node IDs."
- **C3 RESOLVED.** `Contract = field-set-subset` (valid §3 term), `Check Category = behavioral`
  (valid §2 category), columns not conflated, matches `e-spec-readme` precedent.
- **C4 RESOLVED.** All four §6 touch-points named (three source globs + derived
  `web/content/skills/*.md`).
- **C5 RESOLVED.** Generated When-it-fires/When-to-skip blocks removed (folded into authored prose);
  generated block keeps only At-a-glance.
- **C6 RESOLVED.** Issue 3.1 §5 corrects the stale `e-web-skill-counts` sentence (verified live at
  DRIFT-CHECK.md L170).
- **C7 / M1 / M2 / M3 RESOLVED.** Dead-function + orphaned-constant removal (3.2), plugin-set
  Title/Subtitle (1.1), orphan-page ignore (R8), fail-closed new-skill onboarding (3.2).

## Strengths
- Keystone-first sequencing (mechanism → author → enforce) sound; mirrors plan-035.
- Rollout safety real: README-transform fallback during Epic 2 → hard failure in Epic 3, site never
  breaks mid-migration.
- `field-set-subset`/`behavioral` contract with contradiction-only verification follows the
  established `e-spec-readme` pattern; R7 over-strictness contained.
- Hybrid boundary crisp: mechanical facts generated (can't drift), drift-check scoped to prose.

## Residual low/cosmetic notes (non-blocking)
- Plugin docstring carries the same stale "never drift" claim — already inside Issue 1.1's "update
  the docstring" scope. **Folded:** narrative pillar 3 + R2 reconciled to the three `e-skill-page-*`
  edges; Issue 3.2 sweep extended to the orphaned `_DROP_SECTIONS`/`_MD_LINK` constants.

## Gate Assessment
Start gate (human/operator) appropriate. No-capability / no-reconcile justifications valid. Epic 3.3
exit gate well-specified and enforceable (full lint + 0-warning Pelican build with 18 pages/index/nav
+ scoped drift PASS over the three edges); ML003 carve-out bounded.

## Upstream Assessment
Compliant with AGENTS.md coarse convention: one `plan-036 execution tracking` issue at intake, no
per-bead pushes, no `resolves-upstream`. Precedent-aligned.

## Operator Resolutions
| ID | Resolution | Status |
|:---|:-----------|:-------|
| (low) narrative singular-edge shorthand | Reconciled pillar 3 + R2 to "three `e-skill-page-*` edges". | resolved |
| (low) orphaned constants after dead-code removal | Issue 3.2 sweep extended to `_DROP_SECTIONS` / `_MD_LINK`. | resolved |
| (low) plugin docstring stale claim | Already in Issue 1.1 docstring-update scope. | resolved |

**Status: APPROVE — plan is ready for the portability audit + ready-check.**
