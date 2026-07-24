---
type: Review
okf_spec: OKF-PLAN
---
# Red-Team Review — pass 2 (re-review after REVISE)

**Plan:** plan-035-james-dixson-74d7ae
**Date:** 2026-07-23
**Reviewer:** red-team (adversarial, read-only)

## Verdict: REVISE

Pass-1's six concerns and three missing items are almost entirely resolved and the revisions
are well-executed — context.md now grounds C1, C2's drift-direction is explicit, C3's
convention split is real, C4/C6/M1/M2/M3 all land, and the Epic 7.2 exit gate is now fully
specified. **One concern remains:** the VOICE.md dependency edge that C5's resolution *claims*
was preserved on the prose issues 4.2/5.2 is in fact absent from the plan — the C5
de-gating over-corrected and dropped the edge from the *prose* pages too, contradicting R4's
invariant ("VOICE.md gates every prose epic").

## Strengths
- C1 fully closed: context.md lists d2 0.7.1 / naba / pelican 4.11.0; gate justification enumerates the verified toolchain.
- C2 closed precisely: Issue 2.2 mandates document-current-reality + forward-pointer to 3.1 for yf-plan spec surfaces mirroring the live code bug — no spec-ahead-of-code drift.
- C3 closed: ~13 non-convention surfaces + the SURFACE_CONVENTION rewrite hived into Issue 2.3; on-edit fan-out noted.
- C4 closed: Issue 6.2 requires the comparison-table fact-check + date-stamp/omit star counts.
- C6 closed: Objective + Issue 2.1 state re-pour source = committed plan folder/formula, issue = coordination pointer.
- M1/M2/M3 closed: coarse plan-035 tracker at intake; Issue 5.3 status-enum follow-on bead; naba legibility notes on 4.1/5.1.
- Epic 7.2 exit gate: exact commands + zero-warning definition + ML003 false-positive carve-out.

## Concerns

| # | Severity | Concern | Recommendation |
|:--|:---------|:--------|:---------------|
| N1 | medium | C5's resolution claims `depends-on: 1.1` was kept on prose issues 4.2/5.2, but the plan shows 4.2 has only `depends-on: 4.1` and 5.2 only `depends-on: 5.1`. Neither prose page has any path to VOICE.md (Issue 1.1), yet both "Apply VOICE.md." The C5 de-gating over-corrected past the diagram issues into the prose issues, contradicting R4 ("VOICE.md gates every prose epic") and Design pillar 1. Every other prose issue (2.1/2.2/2.3/6.1) correctly carries `depends-on: 1.1`. | Add `depends-on: 1.1` to Issues 4.2 and 5.2 (retain 4.1/5.1). Restores R4's invariant and makes the C5 note truthful. |

## Missing
- None newly identified. M1–M3 from pass 1 are resolved.

## Gate Assessment
- Start Gate: correct. Reconcile Gate: correctly scoped.
- "No capability gate": now defensible (context.md confirms the toolchain).
- Epic 7.2 exit gate: now fully specified (exact commands, zero-warning def, ML003 carve-out).

## Upstream Assessment
- #97 (include → Epic 2): correct, unchanged.
- Three Epic-3 code-fix issues: precisely scoped; Issue 3.3 surfaces the gitignore + migrate.rs complications.
- Coarse plan-035 tracker: accounted for at intake (M1 resolved).

## Operator Resolutions

| # | Concern (short) | Resolution | Status |
|:--|:----------------|:-----------|:-------|
| N1 | VOICE.md gate missing on prose 4.2/5.2 | Added `depends-on: 1.1` to Issues 4.2 and 5.2 (diagram issues 4.1/5.1 remain un-gated per C5). R4 "gates every prose epic" invariant restored. | resolved |

**Final status:** the sole concern (N1) resolved in plan v3; re-run red-team for a fresh verdict.
