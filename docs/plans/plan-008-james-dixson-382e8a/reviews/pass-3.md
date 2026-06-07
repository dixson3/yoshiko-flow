# Plan Red-Team: plan-008-james-dixson-382e8a — Pass 3 (confirming)

**Presented:** 2026-06-06
**Scope:** v4 — confirming pass verifying the pass-2 resolutions are sound.
**Conformance (pre-pass):** PASS
**Status:** FROZEN — APPROVE; no blocking concerns.

## Verdict: APPROVE

All five pass-2 resolutions verified sound against the real drift-check skill. No new defects
introduced. The plan converged.

## Strengths
- **§1 node triple is schema-legal with exact precedent.** `Kind: source, Authority: derived,
  Reachability: optional` verified against `spec/schema.md` REQ-SCHEMA-001 + `templates/
  manifest.md`; the existing `script` node (DRIFT-CHECK.md:30) uses that exact triple. The
  "analogous to a script" framing is precise.
- **`Reachability: optional` correctly suppresses the orphan check** (REQ-CHECK-004(a) fires
  the live-referencer test only on `required` nodes). M1 resolution correct.
- **Binary PNG node creates no verifier problem** (the riskiest new-issue candidate). The edge
  is `path-resolves` with README as the *derived* node (holds the `![](…)` ref) and the PNG as
  *source/target* — same role assignment as existing `e-agent-ref`/`e-template-ref`. The
  verifier reads the derived node's text and confirms the target file *exists*; it never parses
  PNG binary content. A binary node is only ever an existence target.
- **No glob collision.** The fixed `spec` authority globs `skills/*/spec/*.md` (markdown only);
  a new `skills/*/spec/*.png` node is disjoint — not swept into `e-spec-compliance`, §7
  unaffected (PNG node is `derived`).
- **REQ-ENGINE-006 fallback claim is accurate.** A generic "markdown image refs are
  path-resolves references" line carries no repo-specific ID/glob/path; `path-resolves` is
  engine vocabulary. engine.md permits illustrative prose. No REQ-ENGINE-006 / REQ-SCHEMA-003
  violation.
- **mtime-freshness reasoning technically correct.** git checkout normalizes mtimes, so
  cross-clone staleness detection is genuinely impossible; correctly demoted to a same-tree
  advisory WARN with the residual gap accepted in Risks.
- **§6 wiring matches schema** (REQ-SCHEMA-002); `e-readme-layout` `field-set-equal` coupling
  (M2) real and correctly flagged in 1.4/2.3.
- **Dependency graph is a clean DAG.** Epic 1 linear; Epic 2 fans from 1.5 → converges at 2.5;
  Epic 3 sequences 1.5/2.3 → 3.1(spike) → 3.2 → 3.3. Spike-gates-manifest ordering correct.

## Concerns
- **Edge-direction prose in 3.2 reads slightly against the node-role labels** — severity: low
  3.2 says the edge runs "from `README.md` … to the PNG node" (reference direction); the
  parenthetical correctly labels README as *derived*. Consistent with the `e-agent-ref`
  precedent but a literal reader could conflate "from/to" with the Source/Derived columns.
  Recommendation: at execution, set §2 row **Source Node = PNG node, Derived Node = README
  node** (mirroring `e-agent-ref`: source=target-of-reference, derived=holder-of-reference).
  No plan change required; executor wiring note (added to 3.2 for clarity).

## Missing
Nothing material. Pass-2's M1/M2/M3 all addressed in v4 and verified.

## Gate Assessment
Capability Gate valid, runnable, scoped to render-dependent issues (1.5, 2.x, 3.x). Issue 3.3
covers BOTH positive (valid ref → PASS) and negative (broken ref → FAIL/INCONCLUSIVE) cases
(M3 resolved). Issue 1.5 self-verify is objective. No gratuitous gates.

## Upstream Assessment
Unchanged and sound. #6 supersede note honestly lists carried/relocated/re-homed pieces; #7
exclude correct. Epic 3 + skill-authoring stay within the single coarse tracking-issue model
(AGENTS.md, precedent #13/#14/#16). No new upstream issues warranted.

## Operator Resolutions
| # | Concern | Severity | Resolution | Status |
|---|---------|----------|------------|--------|
| 1 | 3.2 edge-direction prose vs node-role labels | low | Executor wiring note added to Issue 3.2: §2 row Source=PNG node, Derived=README node (mirrors `e-agent-ref`). No structural change. | resolved |
