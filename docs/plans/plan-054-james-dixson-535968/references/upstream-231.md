---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #231: plan-053-james-dixson-4015d3 execution tracking

- **Number:** 231
- **Title:** plan-053-james-dixson-4015d3 execution tracking
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

The single coarse tracking issue for **plan-053** (`plan-053-james-dixson-4015d3`), per the
AGENTS.md one-tracker-per-plan convention.

- **Plan bundle:** [`docs/plans/plan-053-james-dixson-4015d3/`](docs/plans/plan-053-james-dixson-4015d3/)
- **Epic:** `yf-mol-bh8`
- **Landed:** merge `10660eb` on `main`

## Objective

Close the yf-plan execution engine's silent-data-loss and plan-stranding defects. Five of the
six **report success while losing or misrepresenting data**, so no configuration of the
existing gates surfaced them.

## Upstream rows

| Issue | Disposition | End state |
| :-- | :-- | :-- |
| #206 plan_extract drops detail lines | include | **CLOSED** |
| #207 resume-scan reports found on a burned epic | include | **CLOSED** |
| #208 update-status accepts out-of-vocabulary statuses | include | **CLOSED** |
| #209 issue beads carry no plan_dir | include | **CLOSED** |
| #210 pour_fidelity.py is not shipped | include | **CLOSED** |
| #214 REQ-PLAN-073 id collision | include | **CLOSED** |
| #189 six shipped scripts have no tests | partial | open |
| #188 suites assert structure, never payload fidelity | partial | open |

## Method

**SPEC-first**, mechanically enforced — every `REQ-*` landed in a commit that touches no
non-spec `skills/**` path, so the ordering is checkable on the merge-parent range and not
merely asserted.

**RED before GREEN** (D-4). Eleven controls, each **observed failing before its fix existed**
and green afterwards, as two distinct dated records. Two are driven against pinned negative
fixtures and say so on their face (`CTL_RED=1` in the record), because under SPEC-first a
control grading Epic 0's work is green on the live tree from the moment it exists.

**Class fixes over instance fixes** where a defect was the second occurrence of one mechanism
(D-3): #210 shipped a repo-level check anchored by a new `REQ-YF-EMBED-005`, justified by a
*mutation* — re-inserting plan-050's original bug makes the check go red — rather than by
volume.

## Verification

- 21 of 21 mechanical Success Criteria pass over the **merged** tree
- FULL validation tier over the merged tree: **51 of 51 rows pass**
  (`assets/full-tier-record.md`)
- whole-corpus `doc_lint`: 938 files, **0 errors**
- `check_skill_script_refs` over the whole tree: 187 invocations, **0 violations**

## Filed, not fixed

Six measured out-of-scope defects, each with its evidence: #225, #226, #227, #228, #229, #230.

`#230` is worth singling out: `bd close` **refuses and exits 0** when a bead is blocked by an
open dependency. It silently no-opped six of this plan's own closes, and was caught by an
observer comparing the ledger against the completion reports — this plan's own thesis class,
occurring in the tool the plan is tracked with.

## Remaining

Issue 7.4 (deploy — `yf self install --from-build --build`) is **not authorized** and its human
consent gate is unresolved.

