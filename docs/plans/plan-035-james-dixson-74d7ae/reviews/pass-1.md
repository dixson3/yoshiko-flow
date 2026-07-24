---
type: Review
okf_spec: OKF-PLAN
---
# Red-Team Review — pass 1

**Plan:** plan-035-james-dixson-74d7ae
**Date:** 2026-07-23
**Reviewer:** red-team (adversarial, read-only)

## Verdict: REVISE

The plan is well-grounded — six findings with file:line citations, a defensible docs-only
boundary, and a coherent epic DAG. But several concerns need resolution before approval, the
sharpest being that the plan's own accuracy (the thing it exists to enforce) slips in two
places: a capability claim unsupported by its cited evidence, and a doc-correction direction
that risks manufacturing new spec↔code drift.

## Strengths
- Evidence is exceptional — every accuracy claim traces to a finding with concrete file:line
  oracles (EXP-01 beads/upstream, EXP-02 `.yf/` layout), each naming its reconciliation anchor.
- The docs-only boundary is genuinely holdable for the code-drift; Epic 3 files issues only.
- EXP-05 correctly kills the single-session strawman, names claude-protocol as the honest
  closest analog, and lands the real differentiator (content-bound fingerprint).
- Risks R1–R7 are plausible and each maps to a finding.

## Concerns

| # | Severity | Concern | Recommendation |
|:--|:---------|:--------|:---------------|
| C1 | high | Plan justifies "No capability gate" with "d2 + naba present per context.md", but context.md's tool inventory lists only bd/git/uv/python/gh/glab/claude — d2, naba, pelican are absent. The exit gate (Pelican build) and diagram epics depend on tools the snapshot doesn't confirm. In a plan about docs matching reality, citing evidence that doesn't contain the claim is the exact defect being hunted. | Verify d2/naba/pelican installed and add to context.md, OR add a capability gate for the diagram+build toolchain. Do not ship the "per context.md" citation as-is. |
| C2 | medium | Epic 2.2 correcting yf-plan `spec/data.md` to canonical paths can introduce NEW spec↔code drift: the SPEC currently says `.yf/yf-plan/preflight.json` (full-name) because that is what `plan_manager.py` writes. "Correcting" the spec to short-name while code (deferred to 3.1) still emits full-name makes the spec describe behavior the code lacks — a likely yf-drift-check trip. Plan does not say which way to correct. | Issue 2.2 must specify, for yf-plan spec surfaces that mirror the code bug, either "document current reality with a forward-pointer to issue 3.1" or "state canonical + annotate pending 3.1." Reconcile direction with Epic 3.1. |
| C3 | medium | Epic 2.2 scope under-counted ("~9 surfaces"); EXP-02's table is closer to ~16 files across 6 skills, and the yf-skill-authoring SURFACE_CONVENTION is a substantive rewrite, not a path swap. Bundled into one VOICE-gated issue it is a large uneven unit; editing skill SPEC/SKILL/convention files fires yf-skill-authoring / yf-drift-check on-edit. | Reconcile the "~9" figure with EXP-02's fuller enumeration; split 2.2 (e.g. the SURFACE_CONVENTION rewrite as its own issue); note the expected on-edit skill-trigger fan-out. |
| C4 | medium | Issue 6.2 acceptance omits the fact-check + star-count-rot mitigations EXP-05 twice demands (comparison table "needs a fact-check pass"; star counts "drift fast — date-stamp or omit"). R5 covers strawman but not numeric rot. | Add to 6.2 acceptance: date-stamp or omit star counts; run the comparison-table fact-check pass before landing. |
| C5 | low | VOICE.md gates the diagram issues (4.1, 5.1) unnecessarily — diagrams are d2/naba with terse labels, not prose. Spurious serialization. | Drop `depends-on: 1.1` on 4.1/5.1 (keep it on prose issues 4.2/5.2); let diagram authoring run parallel to VOICE.md. |
| C6 | low | Objective's "re-poured/hydrated from that issue" is imprecise — EXP-01 is explicit that cross-machine re-pour is from the git-committed plan folder/formula, *coordinated by* the coarse issue; the issue is not the transfer medium. This is the exact subtle inaccuracy Issue 2.1 must avoid re-introducing. | Tighten Objective + Issue 2.1 so re-pour source = committed plan folder, issue = coordination pointer. |

## Missing
- **M1:** No coarse plan-035 tracking issue disposition (AGENTS.md mandates one per plan-scale effort; precedent #13/#14/#16). Clarify to avoid a gap or a duplicate.
- **M2:** No follow-on bead for the `update-status` validation gap (Epic 5.2 documents the non-enum-enforced status vocabulary; EXP-03 rec #4 offers optional hardening). Consider a `discovered-from` follow-on bead (mirrors yf-voice pattern in 1.2).
- **M3:** naba flair reproducibility/legibility unaddressed (R7 covers d2-source drift, not whether naba stylization preserves the light-mode/white-bg convention). One-line acceptance note.

## Gate Assessment
- Start Gate (human/operator): correct.
- Reconcile Gate (auto → blocks #97 reconcile step): correctly scoped.
- "No capability gate": **not yet defensible** — see C1. Resolve before approval.
- Epic 7.2 exit gate under-specified: names no exact Pelican command, no availability confirmation, no "0 warnings" definition net of the known plan-034 ML003 false positives.

## Upstream Assessment
- #97 (include → resolved by Epic 2): correct and well-justified; EXP-01 confirms docs-only fix with a named anchor; the "no live cross-machine bead sharing" note answers #97's ask.
- Three newly-filed code-fix issues (Epic 3): precisely scoped, cite EXP-02 evidence; per-skill granularity is an operator-approved exception. Issue 3.3 correctly surfaces the two non-obvious complications.
- Gap: coarse plan-035 tracking issue not accounted for (see M1).

## Operator Resolutions

| # | Concern (short) | Resolution | Status |
|:--|:----------------|:-----------|:-------|
| C1 | d2/naba/pelican not in context.md | Verified installed (d2 0.7.1, naba, pelican 4.11.0); added all three to context.md tool inventory; "no capability gate" justification now cites verified inventory. | resolved |
| C2 | 2.2 could create new spec↔code drift | Issue 2.2 revised: yf-plan spec surfaces that mirror the code bug DOCUMENT CURRENT REALITY (full-name) with a forward-pointer to issue 3.1, never "correct" ahead of code. | resolved |
| C3 | 2.2 scope under-counted (~9 vs ~16) | Corrected to ~16 surfaces across 6 skills; split the yf-skill-authoring SURFACE_CONVENTION rewrite into its own Issue 2.3; noted the on-edit skill-trigger fan-out. | resolved |
| C4 | 6.2 omits fact-check + star-rot | Issue 6.2 acceptance now requires date-stamping/omitting star counts and a comparison-table fact-check pass before landing. | resolved |
| C5 | VOICE.md over-gates diagrams | Dropped `depends-on: 1.1` from 4.1/5.1 (kept on 4.2/5.2); diagrams run parallel to VOICE.md. | resolved |
| C6 | Objective re-pour wording imprecise | Objective + Issue 2.1 tightened: re-pour source = committed plan folder/formula; the issue is the coordination pointer, not the state-transfer medium. | resolved |
| M1 | coarse plan-035 tracker | Added: the coarse plan-035 tracking issue is filed at intake per AGENTS.md (distinct from the 3 code-fix issues); noted in Approach + Success Criteria. | resolved |
| M2 | update-status validation follow-on | Added Issue 5.3: file a `discovered-from` follow-on bead for the optional status-enum hardening. | resolved |
| M3 | naba legibility note | Added acceptance note to 4.1/5.1: naba flair must preserve light-mode/white-bg legibility vs the base d2 render. | resolved |

**Final status:** all concerns resolved in plan v2; re-run red-team for a fresh verdict.
