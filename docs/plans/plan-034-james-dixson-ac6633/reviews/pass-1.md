---
type: Review
okf_spec: OKF-PLAN
---
# Red-team review — pass 1

**Plan:** plan-034-james-dixson-ac6633
**Date:** 2026-07-23

## Verdict: REVISE

## Strengths
- SPEC-first correctly sequenced (Epic 1 lands REQ-YF-TUNE-026/027 before code; Epics 2–3 depend on it; each impl issue ships a tagged test; revises REQ-YF-TUNE-011 note + amendment-log).
- Pi handled correctly (config-drift codex/opencode only — pi has no config profile; rule-block drift codex/opencode/pi).
- Scope well-bounded and honest (yf-5p9x hoisted to #97, out of scope; no-INVESTIGATE justified).
- Read-only safety framing; warn-only budget check.
- Docs epic avoids duplication via reconcile-and-extend hub; glossary ordered first.

## Concerns

| # | Severity | Concern | Recommendation |
|:--|:--|:--|:--|
| C1 | medium | Budget check models a single file, but the codex cap is on the **concatenation** of AGENTS.md sources — each file can be under-cap while the concatenation is over (false-negative-prone). | Scope the check explicitly to the global `~/.codex/AGENTS.md` and document the limitation in REQ-YF-TUNE-027 + warning text, OR sum discoverable concatenation inputs. Decide in SPEC wording. |
| C2 | medium | "against the codex `project_doc_max_bytes` value" is ambiguous — using the profile default (65536) when the operator never ran tune (on-disk still 32768) under-warns exactly when truncation is likely. | REQ-YF-TUNE-027 must read the **effective on-disk** `project_doc_max_bytes` with a documented `32768` default fallback, not the embedded profile value. |
| C3 | medium | Epic 2 grounding is imprecise: it cites `harness/drift.rs` + the recommended-settings reference-baseline, which is REQ-YF-TUNE-008 (a CI doc↔profile test), NOT the doctor axis. The real axis is `doctor/checks.rs::SettingsDriftCheck` (REQ-YF-TUNE-009), already harness-generic — only `from_env("claude-code")` is wired. Config-drift is mostly registration+tests, not a "new TOML surface." | Correct grounding to `doctor/checks.rs::SettingsDriftCheck` + `audit.rs`; note config-drift is primarily `from_env("codex")`/`from_env("opencode")` registration + tests; reserve "new surface" for rule-block drift (2.2). Lowers R1. |
| C4 | low-medium | Unreconciled overlap: `doctor/checks.rs` already emits a `rule_drift` report (aggregate rule-section drift). Epic 2.2 adds a second differently-scoped managed-block drift — risks two overlapping "rule drift" reports. | In Issue 2.2 state how the new per-harness managed-block drift integrates with / is named distinctly from the existing `rule_drift` axis. |
| C5 | low | "No broken links" success criterion has no named enforcement command. | Name a concrete link-check (yf-markdown-lint full audit or a Pelican link check) in the criterion, or accept manual verification explicitly. |

## Missing
- The effective-value / concatenation-scope decision for the budget check (C1/C2) — the plan's one genuine design decision, under-specified.
- Named verification mechanism for the docs epic (C5).

## Gate Assessment
Appropriate. Mandatory human start gate only; no capability gate (engines exist + already harness-generic); no reconcile gate (no upstream incorporation). Test commands valid (cargo fmt + clippy -D warnings + test --workspace, matching CI). R6 correctly captures the annotated-marker coverage exclusion.

## Upstream Assessment
Sound and compliant with the coarse-granularity convention. Upstream table correctly empty (six local beads closed at reconcile). yf-5p9x hoist to #97 + tombstone documented. Single coarse tracking issue at intake is correct. Process note: confirm the coarse issue is actually filed at intake before land.

## Operator Resolutions

| # | Resolution | Status |
|:--|:--|:--|
| C1 | Adopt option (a): scope the budget check to the global `~/.codex/AGENTS.md`; document the single-file limitation in REQ-YF-TUNE-027 + warning text. Summing arbitrary project/cwd AGENTS.md the operator controls is out of yf's lane. | resolved |
| C2 | REQ-YF-TUNE-027 + Issue 3.1 revised to read the **effective on-disk** `project_doc_max_bytes` with a documented `32768` (codex default) fallback. | resolved |
| C3 | Approach pillar 1 + Epic 2 grounding corrected to `doctor/checks.rs::SettingsDriftCheck` (REQ-YF-TUNE-009), noting config-drift is primarily `from_env(codex/opencode)` registration + tests; `drift.rs`/REQ-008 clarified as the separate CI test. R1 softened. | resolved |
| C4 | Issue 2.2 revised to name the new check distinctly (per-harness **managed-block** drift) and state it is reported separately from the existing aggregate `rule_drift` axis. | resolved |
| C5 | Epic 4 success criterion names the concrete link check: `yf-markdown-lint` full audit over the new pages. | resolved |
