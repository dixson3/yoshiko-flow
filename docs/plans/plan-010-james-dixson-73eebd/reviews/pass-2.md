# Plan Red-Team: plan-010-james-dixson-73eebd — pass 2

**Verdict:** REVISE
**Date:** 2026-06-14
**Status:** resolved (all concerns addressed in plan v3; operator approval pending)

Second red-team cycle. Pass-1's two high-severity resolutions (INV-1 self-rename, Epic 6 backing
G1/G2) verified to hold. The material added since (Epic 0/G0, Epic 6, Epic 7, the `yf` rename)
introduced new coherence gaps — one in the gate model — addressed below.

## Strengths

- Pass-1 high resolutions verified against real skill internals: `SKILL_DIR` find resolves the
  installed `bdplan` copy first; `bd`/`plan_manager.py` run primary-side; deferring the two
  self-renames to a Phase-6 worktree step keeps the orchestrator stable. Legacy `.state/bdplan/` is
  the correct current path for Issue 2.7/3.6.
- Epic 6 backing G1/G2 is real (closure parity golden-file, tree-hash/prune, `bd status` classifier,
  three-state preflight fixtures); G1/G2 `Depends on` specific 6.x issues.
- G0 blocks entry *leaf issues* (not epics) — mechanically correct for bdplan's task→epic rule.
- The `yf` rename is clean: zero stray `yflow` that should be `yf`; marker/state/config/formula all
  consistently `yf`; exp-003 IP check thorough.
- Dual-integrity model (tree-marker vs per-rule manifest) survives the rename; only the marker
  string changes.

## Concerns

1. **The G0→PLAN "re-planning loop" is not a native bdplan EXECUTE-phase capability** — severity:
   high. bdplan has no EXECUTE→PLAN transition (EXECUTE → RECONCILE → COMPLETE). G0 as a
   mid-execution capability gate that, on a scope-changing outcome, edits already-intake'd beads,
   re-runs the PLAN-phase conformance/portability scripts, and re-wires deps is an out-of-band
   manual op the skill neither models nor enforces (the coordinator never invokes
   `plan_manager.py audit`). Labeling it "RECONCILE" collides with Phase 6's actual meaning.
   Recommendation: (a) move SPEC.md + GUARDRAILS.md + sign-off **out of EXECUTE** — author and seal
   them pre-intake so the Epic 1–7 beads are created against a sealed spec (eliminates the loop and
   the chicken/egg in Concern 3); or (b) keep G0 in-execution but state a scope-changing outcome
   **aborts to a `/bdplan continue` PLAN revision + re-intake**, not an in-place amend. Drop
   "RECONCILE."

2. **"Tests anchor to SPEC, not code" is overstated; GUARDRAILS.md is inert prose** — severity:
   medium. Issue 6.5 (every testable REQ maps to ≥1 test) is a real forward control, but nothing
   mechanically ensures a test verifies its named REQ rather than current behavior. GUARDRAILS.md
   has no consumer at all — no test, no drift edge, no review fails if the implementation crosses a
   guardrail; as written it is documentation, not a guardrail.
   Recommendation: soften Success Criterion 8 to the REQ-coverage claim 6.5 actually enforces; add
   ≥1 concrete guardrail check (a `DRIFT-CHECK.md` SPEC↔GUARDRAILS↔README edge, or a sign-off
   checklist item re-reading GUARDRAILS against the shipped surface).

3. **Chicken/egg: SPEC must exist before Epic 1/6 beads reference REQ ids, but it's authored in
   EXECUTE** — severity: medium. Epic 6 beads are created at intake before any REQ exists; SC8 is
   unverifiable at intake. Recommendation: resolved by Concern 1(a) — author SPEC pre-intake.

4. **Epic 7.2 "finalize after Epics 1, 3" is prose, not a dependency edge** — severity: medium. The
   bead's only real dep is 7.1, so the DAG marks it ready before Epics 1/3 finalize names/commands,
   risking docs against pre-rename names. Recommendation: add real `depends-on` edges from 7.2 to
   Epic 1's terminal issue (1.7) and Epic 3's (3.5/3.7).

5. **Epic 7.3 deploy "operator-pending" is a soft TODO, not a gate** — severity: low. No gate bead/
   condition/test/approver; 7.3 completes with a placeholder, so SC9 can be met by a disabled
   workflow. Recommendation: make D5 a real `Gate G4 (human)` blocking deploy *enablement*, or scope
   7.3 to "scaffold disabled workflow only" + an out-of-plan follow-up.

## Missing

- Where SPEC/GUARDRAILS authoring sits in the phase machine (Concern 1/3).
- Any verification that consumes GUARDRAILS.md (Concern 2).
- Real dep edges for Epic 7 content ordering (Concern 4).
- Cosmetic: Issue 3.2 inline list still omits `incubator` from the "7 edges" (count is right).

## Gate Assessment

Five gates, not over-gated; G1/G2 now properly test-backed (pass-1 hollow-gate resolved); G0 blocks
entry leaf issues correctly. Two model problems: G0's EXECUTE→PLAN loop mislabeled RECONCILE
(Concern 1, high); D5 deploy is a gate in spirit but unmodeled (Concern 5, low). G3 well-formed.

## Upstream Assessment

Unchanged and sound: #14 supersede justified; #15 partial specific; Issue 5.3 specifies close-#14 /
comment-#15; coarse single tracking issue matches policy. No new upstream exposure from Epics 0/6/7.

## Operator Resolutions

| #   | Concern                                  | Severity | Resolution                                                                                                                                                                                                                                                                                                                                     | Status   |
| :-- | :--------------------------------------- | :------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- |
| 1   | G0 EXECUTE→PLAN loop not bdplan-native   | high     | Adopted option (a): SPEC.md + GUARDRAILS.md are a **pre-intake deliverable** authored during PLAN and sealed by an operator **sign-off milestone (the former G0) before INTAKE**; downstream epics are shaped against the sealed spec; the EXECUTE→PLAN loop and the "RECONCILE" label are removed. Epics 1–7 are intaked only after sign-off. | resolved |
| 2   | GUARDRAILS inert; SPEC-anchor overstated | medium   | Added a `DRIFT-CHECK.md` manifest edge **SPEC ↔ GUARDRAILS ↔ README** (Issue 5.x) so spec/guardrail/doc drift is caught; Success Criterion 8 softened to REQ-coverage (what 6.5 enforces); sign-off checklist re-reads GUARDRAILS against the shipped surface.                                                                                 | resolved |
| 3   | Chicken/egg SPEC vs REQ ids at intake    | medium   | Resolved by #1 — SPEC sealed pre-intake, so REQ ids exist before Epic 6 beads are created and SC8 is verifiable.                                                                                                                                                                                                                               | resolved |
| 4   | Epic 7.2 prose ordering                  | medium   | Added real `depends-on` edges: 7.2 → 1.7 (commands final) and → 3.5 (repo-internal/catalog rename final).                                                                                                                                                                                                                                      | resolved |
| 5   | D5 deploy unmodeled                      | low      | Added **Capability Gate G4 (human)** blocking deploy-workflow *enablement* (condition: operator confirms target repo/branch/domain; test: workflow references a resolved `baseUrl`/`CNAME`); Issue 7.3 scaffolds a **disabled** workflow until G4.                                                                                             | resolved |
| 6   | incubator omitted from 3.2 inline list   | cosmetic | Added `incubator` to the Issue 3.2 enumerated edges.                                                                                                                                                                                                                                                                                           | resolved |
