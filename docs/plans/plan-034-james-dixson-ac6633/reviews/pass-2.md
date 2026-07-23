---
type: Review
okf_spec: OKF-PLAN
---
# Red-team review — pass 2

**Plan:** plan-034-james-dixson-ac6633
**Date:** 2026-07-23

## Verdict: APPROVE

Re-review after the pass-1 REVISE concerns (C1–C5) were addressed. All five confirmed resolved and grounded in shipped code.

## C1–C5 resolution confirmation
- **C1 (single-file scope) — RESOLVED.** Budget check scoped to global `~/.codex/AGENTS.md`; single-file limitation documented in REQ-YF-TUNE-027 + warning text.
- **C2 (effective on-disk value) — RESOLVED.** Reads effective on-disk `project_doc_max_bytes` with 32768 default fallback, not the profile's 65536 (verified codex profile sets 65536, so pre-tune would under-warn). Absent-config 32768 path tested.
- **C3 (Epic 2 grounding) — RESOLVED.** Correctly grounded on `doctor/checks.rs::SettingsDriftCheck` (REQ-YF-TUNE-009), already harness-generic (only `from_env("claude-code")` wired at checks.rs:535); config-drift = registration+tests; `drift.rs`/REQ-008 clarified as separate CI test, left untouched.
- **C4 (rule_drift overlap) — RESOLVED.** Managed-block drift named distinctly + reported separately from the existing aggregate `rule_drift` (checks.rs:202); no-double-count test.
- **C5 (link-check command) — RESOLVED.** Epic 4 criterion names the `yf-markdown-lint` full audit over the new pages.

## Strengths
- Pi handling correct/consistent (`load_profile("pi")` returns None → config-drift scoped codex/opencode; managed-block drift codex/opencode/pi).
- SPEC-first sequencing intact; read-only safety; R1 correctly softened.
- Docs epic ordering (glossary first) + reconcile-and-extend hub avoid duplication.

## Concerns
None blocking. One **low** executor note (no plan change): during Issue 2.1, verify the codex/opencode profiles define usable settings-layer paths (`settings_path_at` for the resolved layers) so the seeded-drift test exercises a real on-disk config file, not only the deploy-time managed-block path.

## Missing
Nothing material — both pass-1 gaps (budget effective-value/scope; docs verification command) now specified.

## Gate Assessment
Appropriate/unchanged. Human start gate only; no capability gate (engines already harness-generic); no reconcile gate (no upstream incorporation). Test commands match CI. R6 captures the annotated-marker coverage exclusion.

## Upstream Assessment
Sound, coarse-granularity compliant. Upstream table correctly empty (six local beads closed at reconcile). yf-5p9x → #97 tombstone documented. Single coarse tracking issue at intake. Reminder: confirm the coarse issue is filed before land.

## Operator Resolutions

| # | Resolution | Status |
|:--|:--|:--|
| L1 | Executor note (no plan change): during Issue 2.1, confirm codex/opencode `settings_path_at` layers resolve to the harness's real config file so the seeded-drift test exercises a real on-disk layer. Carried into the Issue 2.1 execution brief. | resolved |

**Approved for the Phase 3 → INTAKE transition (pending portability audit + ready-check).**
