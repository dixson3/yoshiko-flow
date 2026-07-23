---
type: Review
okf_spec: OKF-PLAN
---
# Review pass 3 — plan-033-james-dixson-46aca2

**Reviewer:** Red-Team (adversarial)
**Date:** 2026-07-22

## Verdict: APPROVE

Triggered by a material scope addition after the pass-2 APPROVE: **Epic 7 (Code-accurate web docs +
diagrams)** — Issues 7.1 (install matrix page), 7.2 (tune/deploy matrix page + diagrams), 7.3
(doc↔code assert-agreement test) — plus Objective capability 4, Approach pillar 5, Risk R10, new
`REQ-YF-TUNE-022/023`, and Success-Criteria additions. The new epic is sound, correctly wired, and
code-grounded; the pass-1 (C1–C5) and pass-2 resolutions are untouched. Decisive approve, two low
notes only.

## Strengths

- **7.3 agreement test is genuinely implementable — precedent verified in code.**
  `yf/src/cmd/harness/drift.rs` already does exactly this for REQ-YF-TUNE-008: a `#[test]` reads a
  `CARGO_MANIFEST_DIR`-relative doc and diffs it against the embedded profile, failing CI on
  divergence. A 7.3 test reads `../web/content/pages/{install,harness-tune}.md` the identical way.
  Code is the oracle, the doc is the checked artifact — correct direction.
- **Install-matrix description matches `dest.rs` exactly** (`<anchor>/.<surface>/{skills,rules}`,
  anchor = `$HOME`/git-root, surface = `.claude`/`.agents`; REQ-YF-INSTALL-002). No drift.
- **Dependency wiring is right.** 7.1→1.2 only (documenting install needs just the SPEC REQ; install
  code already exists). 7.2→{4.3, 5.2, 7.1} (the tune/deploy/revert matrix cannot be accurately
  documented or code-derived until deploy-rules, the manifest, and `--revert` exist). 7.3→7.2.
  Acyclic, forward-only.
- **Bead reconciliation coherent, not scope creep.** yf-8ayq + yf-ij06 are local web-docs beads on
  the same `web/content/pages` surface and topic Epic 7 owns; folding them grounds two vague standing
  asks in code-truth.
- **SPEC-first preserved; no REQ collision.** 022/023 land in Issue 1.2 before Epic 7 code; SPEC max
  is 011, plan adds 012–023 contiguously.
- **No-reconcile-gate call unaffected.** yf-8ayq/yf-ij06 are local `bd` beads (no upstream link), not
  upstream-issue incorporations; #95 stays correctly `related`.

## Concerns

| # | Severity | Concern | Recommendation / resolution |
|:--|:---------|:--------|:----------------------------|
| E1 | low | The tune matrix said "× scope" / "project-scope forms," but the code has THREE tune scopes (User, ProjectLocal→`settings_local_filename`, ProjectCommitted→`settings_filename`). A collapsed project row would let 7.3 check only a subset of the fields the code resolves. | Resolved in-plan: Issue 7.2 now enumerates all three scope rows (user / project-local / project-committed) so the agreement test checks both filename fields. |
| E2 | low | 7.1's matrix uses abstract anchors; `dest.rs` pure helpers take a symbolic anchor, so 7.3 must assert templated structure (dot_dir + suffix joins), not env-resolved absolute paths, and must exclude the `--target` override branch. | Resolved in-plan: Issue 7.3 implementer notes now say assert structural invariants (`Surface::dot_dir` + `/skills`,`/rules`) scoped to the no-`--target` matrix, and cite `drift.rs` as the reusable pattern. |

## Missing

Nothing material. Epic 6.1 (`docs/recommended-settings.md`, repo prose) and Epic 7 (`web/` Pelican
site) are distinct doc surfaces — no double-authoring. Web images dir + d2 0.7.1 present, so the
diagram criterion is feasible. Advisory: if yf-8ayq's specific "back-referenced from every skill
page" sub-goal isn't carried by Epic 7, record that at reconcile/close so it isn't silently dropped
(the "reconciled … where they overlap" wording already implies a close-time judgment call).

## Gate Assessment

Unchanged and correct. Start Gate (human/operator) appropriate. No capability gate (`toml`/
`toml_edit` ordinary Cargo deps); no reconcile gate (#95 `related`; the two folded beads are local,
not upstream incorporations). Epic 7 SPEC-first enforced structurally via 7.1→1.2.

## Upstream Assessment

Sound and unchanged by Epic 7. #95 correctly `related`; one coarse tracking issue at intake.
Epic 7's reconciliation targets are LOCAL beads (yf-8ayq, yf-ij06) — a within-repo `bd` close, not
an upstream push. Deferred follow-ons (per-harness doctor/drift axis; Pi first-party re-verification)
remain slated for Issue 6.2.

## Operator Resolutions

| Concern | Resolution | Status |
|:--------|:-----------|:-------|
| E1 (three tune scopes) | Issue 7.2 now enumerates user / project-local / project-committed rows per harness. | resolved |
| E2 (structural-invariant agreement test) | Issue 7.3 implementer notes: assert `Surface::dot_dir`+suffix structure, exclude `--target`, reuse `drift.rs`. | resolved |
