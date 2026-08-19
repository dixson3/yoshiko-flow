---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #150: research 004: process-defect mining across 83 plan bundles

- **Number:** 150
- **Title:** research 004: process-defect mining across 83 plan bundles
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium

## Body

Coarse tracking issue for research 004 (precedent: #146 for research 003).

Bundle: docs/research/004-plan-process-defect-mining/ — commit 2adad77 on main.

QUESTION: across 83 plan bundles in five repos (yoshiko-flow 43, d3-pxe 16, pybridge 11, evri_py 9, emacs.d 4), where did a plan build something a LATER plan had to fix, and which of those remediations were preventable by a better process rather than by better execution?

METHOD: tooling-first. A remediation-pair extractor (scripts/remediation_pairs.py, 1106 lines) mined all bundles plus git history and bead graphs, emitting 83 candidate pairs at deliberately high recall; four retrieval clusters then confirmed or rejected each against both bundles. 136 first-party sources, no web leg by design. Retrievers were held blind to research 003 so any agreement would be independent corroboration rather than priming.

HEADLINE FINDING: a written rule that nothing executes is unreliably obeyed, and no exit code records the skip. Five of five clusters reached this independently on disjoint surfaces without naming it as the same thing. Sharpest form: a step with no exit code is not a step. The corpus's own line — 'Adding a sixth instruction to a five-instruction list that was partially ignored is a null change.'

16 defect classes ranked by recurrence. Top five:
1. M9 — remediation relationship exists only in prose (4/4 repos, 5 clusters)
2. M5 — prose-only enforcement does not bind (2/4 named + corpus-wide mechanical absence)
3. M6b — residue and stale internal cross-reference (4/4 eligible)
4. M10 — precise diagnosis, never routed into work (4/4)
5. M11 — real-target reality reachable only by running (4/4) — THE POSITIVE FINDING

Classes 1 and 2 are filed separately as #149.

THE PRESCRIPTIVE SIGNAL IS NOT 'ADD ANOTHER REVIEW PASS.' It is M11: a capability probe or spike placed BEFORE the work that depends on it, paired with a pre-registered risk and a written response (4 repos, 4 clusters).

TWO STRUCTURAL BOUNDS, carried in the report rather than buried:
- No bundle in the corpus declares what it fixes. 0 of 53 discovered-from bead edges connect two plan epics; no commit names a prior plan as a defect source. Every count is a LOWER BOUND over the recorded subset, never a prevalence. (This is also class M9 — the top defect is that the process cannot record the relationship the research was chartered to find.)
- yoshiko-flow is the skill fixing itself: self-selected and unusually articulate about its own defects. No class is general on yoshiko-flow evidence alone.

TWO METHOD EVENTS RECORDED RATHER THAN HIDDEN:
- The DAG extended at runtime (bead yf-mol-fsp.5) to re-mine 93 yoshiko-flow review passes the primary retriever had skipped. That repaired a comparability defect and reversed three false 'absent in yoshiko-flow' verdicts. Because the cluster was commissioned after triangulation it was never cross-checked, so every claim resting on it is marked [YFR-only] in the report.
- The red team returned 9 MUST-FIX items, all severity high, all applied. Most consequentially: M5 was restated from a claimed 5 repos to a demonstrated 2, and 'cost' was dropped as a ranking key because the corpus evidences cost for only 3 of 16 classes.

RECONCILIATION WITH RESEARCH 003: three findings independently corroborated by a different method (prose contracts do not bind; gate reachability; discovered-from is write-only — which 004 quantifies at 0 of 53). 003's weakest leg is 004's tenth-ranked class, found four repos wide by a project that did not know the claim existed.

Known follow-ups: #149 (M5/M9), plus a yf-research link_normalizer.py defect filed separately.
