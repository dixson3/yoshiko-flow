---
type: Review
okf_spec: OKF-PLAN
---
# Review pass 2 — plan-033-james-dixson-46aca2

**Reviewer:** Red-Team (adversarial)
**Date:** 2026-07-22

## Verdict: APPROVE

All five pass-1 concerns (C1–C5) are genuinely and correctly reflected in plan v2, the new R7
(codex 32 KiB cap) is present, and the Pi-removal revision introduced no broken wiring, orphaned
REQ ids, or contradictions. A decisive approve, not a grudging one. Verified against the real code
(`merge.rs` `Change` variants, `profile.rs` rust-embed) and against research-002 (Pi `[uncertain]`,
config-is-enforcement-only, the 32 KiB `project_doc_max_bytes` cap).

## Strengths

- **C1 delta-replay now technically coherent and code-grounded.** Approach pillar 1, Issue 2.1, and
  R1 describe one design: parse `config.toml` → `toml_edit::DocumentMut` (trivia/key-order) AND
  separately derive a `serde_json::Value` for the merge decision only; run the unchanged `merge()`;
  replay only `MergeReport` deltas (`ScalarAdded`/`ScalarForced`/`SetUnioned`) onto the
  `DocumentMut`; serialize *that document*, never the `Value`. Verified those three variants are
  exactly `Change::is_mutation`; TOML datetimes survive because they never enter the delta set. The
  type-fidelity note is present; the comment-survival test is retained and only passable under
  delta-replay.
- **C3 Pi removal complete and consistent.** Pi deferred everywhere it was implemented (Objective,
  Epics 1/3/4/6, Success Criteria, R2, R5); former Issue 3.3 gone (Epic 3 = codex 3.1 + opencode
  3.2); every Pi mention is now a deferral tracked by `REQ-YF-TUNE-016` + the Epic 6.2 follow-on.
- **C4 revert guard fully specified.** Touched-since-tune guard (compare on-disk value to recorded
  yf-written value; differ → conservative-keep + report) in pillar 4, Issue 5.2, R4. Manifest path
  explicit (`.yf/harness-tune-manifest.json`, project-scope `.yf/` gitignored). Manifest records
  both prior and yf-written value — the data the guard needs.
- **C5 resolved:** Epic 4.1 is `depends-on: 1.2` only.
- **R7 added** and grounded in research S-CX-1's 32 KiB cap, with the minimized-bundle mitigation.
- **Dependency wiring + REQ coverage survive cleanly.** REQs 012–021 each map to a tagged test
  (016 appropriately test-free as a deferral requirement); Epic-1 REQ-landing precedes every
  implementation issue transitively; no orphaned ids, no dangling edges; acyclic, forward-only.

## Concerns

| # | Severity | Concern | Recommendation |
|:--|:---------|:--------|:---------------|
| D1 | low | C2 provenance is resolved (enumerated `protocols/*.md` sources + bundle↔source agreement assertion, tagged REQ-017, testable). Soft spot: the "minimization classifier … re-derives automatically" framing oversells what the code will be — irreducibility classification is a curatorial judgment, not an autonomous oracle. | No plan change required. Addressed in-plan by an Implementer note added to Issue 4.1: the "classifier" is a curated selection guarded by the agreement test; a new `protocols/` rule fails loudly as unclassified for human triage rather than being auto-classified. |
| D2 | low | Risk-table numbering was out of sequence (R9 between R6 and R7). | Fixed: risks renumbered R1–R9 in order (codex-cap → R7, SPEC-drift → R8, merge.rs → R9). |

## Missing

Nothing material. Both pass-1 "Missing" items folded in (type-fidelity note in multiple places;
codex 32 KiB interaction as R7). The Epic 6.2 Tier-2 sandboxed-`HOME` integration test is named as
the success-criteria verification for revert round-trip correctness.

## Gate Assessment

Unchanged and correct. Start Gate (human/operator) appropriate. No capability gate (`toml`/
`toml_edit` ordinary Cargo deps) and no reconcile gate (#95 `related`) — both justified. SPEC-first
enforced structurally via `depends-on` edges to Epic 1; wiring intact after Pi removal.

## Upstream Assessment

Sound. #95 correctly `related` (predecessor); one coarse tracking issue filed at intake referencing
#95 (AGENTS.md coarse mandate, #13/#14/#16 precedent). Closing beads `yf-8agh` + `yf-up7s` real and
dependency-linked to closed `yf-2gyv`. Two deferred follow-ons (per-harness doctor/drift axis; Pi
first-party re-verification) slated for Issue 6.2.

## Operator Resolutions

| Concern | Resolution | Status |
|:--------|:-----------|:-------|
| D1 (classifier framing) | Implementer note added to Issue 4.1 clarifying curated-selection-guarded-by-agreement-test (no autonomous oracle). | resolved |
| D2 (risk numbering) | Risks renumbered R1–R9 in sequence. | resolved |
