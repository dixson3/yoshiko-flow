---
type: Review
okf_spec: OKF-PLAN
---
# Red-Team Review — Pass 2

**Plan:** plan-032-james-dixson-6cb87b
**Presented:** 2026-07-22
**Status:** frozen

## Verdict: APPROVE

The pass-1 HIGH is genuinely resolved and all seven concerns plus five Missing items are fixed in
the plan text (verified against the codebase, not merely asserted in the pass-1 table). Two new
MEDIUM issues surfaced during revision; both were framed as non-blocking execution-time
clarifications and have been folded into the plan text (Issues 2.3, 4.2; Approach §1, §3).

## Strengths

- HIGH `permissions.deny` fix correct and load-bearing: kind-aware scalar/set-valued split, threaded
  through Approach §2, REQ scope, Issue 3.5, risk table, Success Criteria, with a dedicated union test.
- ALLOWLIST bridge (Issue 1.3) matches the real `yf/src/coverage.rs` mechanism, including the
  remove-when-tagged enforcement.
- Separate rust-embed root (2.2) correctly avoids the `#[folder="../skills"]` bogus-skill trap.
- Doctor extension seam is real (`yf/src/cmd/doctor/checks.rs` `Check`-trait registry); effective-
  merged-view + false-missing test present.
- Flag-gated-not-prompt, `--harness` forward-compat reframing, drift-test scoping, reversibility-as-
  follow-on all reflected in actual text.

## Concerns

- **[MEDIUM] `--repair` overloading collides with the existing doctor `--repair` contract.** `--repair`
  short-circuits all read-only axes to the beads-init repair (REQ-YF-PRE-007); `--prune-formulas` is
  the decouple precedent. FOLDED IN: the settings drift check is now report-only and explicitly
  decoupled from `--repair` (Approach §3, Issue 4.2).
- **[MEDIUM] Fenced block is JSONC with multi-line rationale comments; 2.3/2.4 applied two different
  strategies.** FOLDED IN: chose assert-agreement (JSONC-tolerant parse) only, dropped block
  regeneration; Issue 2.4 removed and merged into 2.3; comments stated as hand-authored (Approach §1,
  Issue 2.3, risk table).

## Missing

- No residual gaps. All five pass-1 Missing items present (doc-wire → 2.3; embed location → 2.2;
  array-union test → 3.5; malformed fail-safe → 3.2/3.4; reversal follow-on).

## Gate Assessment

Unchanged and appropriate: single mandatory human Start Gate, no over-gating. Coverage/CI expectation
handled by the ALLOWLIST bridge (Issue 1.3), verified against real `coverage.rs` enforcement.

## Upstream Assessment

Coarse single-issue convention; `yf-nl8i` / `yf-8ayq` / `yf-2gyv` named. Land-the-plane: confirm the
`yf-2gyv`-gated multi-harness follow-on AND the reversal/undo follow-on are filed as actual beads with
dependency edges, not merely referenced.

## Operator Resolutions

| # | Concern (severity) | Resolution | Status |
|:--|:-------------------|:-----------|:-------|
| 1 | `--repair` overloading (MED) | Settings drift check made report-only, decoupled from `--repair`; PRE-007 short-circuit untouched (Approach §3, Issue 4.2). | resolved |
| 2 | JSONC fenced-block strategy ambiguity (MED) | Single strategy: assert-agreement via JSONC-tolerant parse; block regeneration dropped; Issue 2.4 merged into 2.3; `//` comments stay hand-authored (Approach §1, Issue 2.3). | resolved |
