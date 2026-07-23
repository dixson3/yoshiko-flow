---
type: Review
okf_spec: OKF-PLAN
---
# Review pass 5 — plan-033-james-dixson-46aca2

**Reviewer:** Red-Team (adversarial)
**Date:** 2026-07-22

## Verdict: APPROVE

Verification pass confirming the pass-4 REVISE (F1–F7) is genuinely and correctly resolved and the
revision introduced no new breakage. The dependency graph remains acyclic/forward-only after adding
Issues 1.5 and 6.3, REQ ids stay non-colliding, and the new capability gate is well-formed and
actually wired.

## Strengths

- **F1 fully closed, not papered over.** Pi rule target is no longer a shipped guess: Issue 1.5 is a
  genuine SPEC-resolving INVESTIGATE (ships no code; produces ONE concrete `REQ-YF-TUNE-020` target
  or a documented no-evidence conclusion); the capability gate `gate:pi-rule-target-verified` has a
  real Condition/Test/Unblock and Blocks Issue 6.3; `REQ-YF-TUNE-020` forbids a silent default and
  specifies the `--pi-rule-target {agents-md|append-system}` opt-in fallback with a loud notice;
  Issue 6.3 `depends-on: 6.2, 1.5, gate:pi-rule-target-verified` enforces it. The only remaining "or"
  is inside Investigation Findings quoting research-002's `[uncertain]` finding — correct provenance,
  not a shipped default.
- **F2** — `--revert` appears only on `yf harness tune`; Objective/Issue 1.1/Issue 2.1 each state
  "no `--revert` here"; Epic 8 owns it.
- **F3** — Issue 1.1 revises REQ-YF-CLI-001 and REQ-YF-TUNE-002 in addition to CLI-002.
- **F4** — all four ops are sub-verbs `yf harness skills install|upgrade|remove|status`; `--tune` is
  a flag on `install`; the whole top-level `yf skills` group is a deprecated alias until next major;
  no stranded verbs — "all harness ops under `yf harness`" is now literally true.
- **F5** — bare-install degraded state documented (warning + success-output note in Issue 2.2 /
  REQ-YF-INSTALL-008; Epic 9 docs callout; risk R14).
- **F6** — detection takes injected `PATH` for hermetic Tier-2 tests (Issue 2.3 / REQ-YF-INSTALL-009);
  the no-`--harness --tune` auto path prints the resolved target set and requires confirm /
  dry-run-then-apply (Issue 7.2 / R5).
- **F7** — codex `project_doc_max_bytes` size-budget follow-on filed in Epic 10.2.

## Concerns

None blocking. Two low observations, neither warranting REVISE:

| # | Severity | Observation | Action |
|:--|:---------|:------------|:-------|
| G1 | low | `REQ-YF-TUNE-020` is tagged by both Issue 6.2 (non-Pi target map) and Issue 6.3 (Pi target). | Intentional — one requirement, two tagged tests (non-Pi + Pi legs). Not a collision. No change. |
| G2 | low | The gate's Test admits two pass states (verified target OR documented opt-in fallback + queued follow-on). | Correctly mirrors the F1 two-outcome resolution + Epic 10.2 conditional follow-on. No change. |

## Missing

Nothing. All pass-4 "Missing" items are present: CLI-001/TUNE-002 revisions (F3), a single concrete
gated Pi target (F1), upgrade/remove/status relocated as sub-verbs (F4), the bare-install
behavior-change acknowledgment (F5/R14), and the codex size-budget follow-on (F7).

## Gate Assessment

Well-formed. Single human Start Gate appropriate. The new `gate:pi-rule-target-verified` capability
gate is correctly typed with a concrete Condition/Test/Unblock, names Issue 6.3 as blocked, and 6.3's
`depends-on` references it — it gates rather than merely declaring intent. No TOML-toolchain gate and
no reconcile gate remains correctly justified.

## Upstream Assessment

Sound and unchanged. #95 `related`; coarse one-tracking-issue contract honored; web beads
yf-8ayq/yf-ij06 reconciled locally; follow-ons (Pi config re-verification, doctor/drift axis, codex
size-budget, conditional Pi-rules-target verification) filed in Epic 10.2.

## Operator Resolutions

| Concern | Resolution | Status |
|:--------|:-----------|:-------|
| G1 (REQ-YF-TUNE-020 dual-tagged) | Intentional — one REQ, two tagged tests. No change. | resolved |
| G2 (gate Test two pass-states) | Mirrors the F1 two-outcome resolution. No change. | resolved |
