---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: OKF group

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #141 — yf-okf: reconcile OKF-BASELINE from v0.1 to OKF v0.2 (supersedes #128)

> ## Summary

`skills/yf-okf/spec/OKF-BASELINE.md` states it is *"Pinned to `okf_version: 0.1`"* and was distilled from research project `docs/research/001-okf-compliance-delta/`. Upstream `GoogleCloudP...

**Disposition:** include
**Notes:** Baseline to v0.2 verbatim + extension-layer AGREE/DIVERGE/ABSENT mapping. **No corpus frontmatter migration** (D-2) — exposure to both breaking changes measured at zero. Resolved by Issue 2.9. Subsumes the already-closed #128.

## #140 — yf-okf: enforce OKF structure below the bundle root (nested index.md/log.md), and adopt an index drift/regeneration model

> ## Summary

`yf-plan` and `yf-research` bundles are OKF-shaped **only at the root**. `index.md` / `log.md` exist at the bundle root and nowhere below it, so every subdirectory requires a full content ...

**Disposition:** partial
**Notes:** **IN:** root-scoped `reindex --check`/`--write`, the drift model, the root backfill, the two extension decisions. **OUT:** nested `index.md` (deferred, D-9 — filed upstream by 5.5), nested `log.md` (dropped permanently, D-4), promotion to error-level enforcement (recorded not executed). Resolved by Issue 4.5. `partial`, not `include`, because the title's own nouns are all in the OUT column.

## #92 — OKF export-emit integration for yf-plan/research/incubator (deferred)
Labels: enhancement
> Deferred implementation tracker, split out from research #91 (OKF compliance-delta).

**Decision (2026-07-19): defer.** See \`docs/research/001-okf-compliance-delta/DECISION.md\`. Local bead: \`yf-uz5...

**Disposition:** supersede
**Notes:** Emit half measurably shipped 2026-07-19 (8h39m *before* the deferral was recorded); nested-tree half is #140's content. **Three named carve-outs filed by Issue 5.5** — projection delivery mode; conformance gate for yf-research and yf-incubator; consumer round-trip fidelity. Closed by Issue 5.6 with the two falsified rationale bullets corrected.

## #118 — yf-plan README.md stale: still lists README.md as plan-folder orientation file (pre-OKF), contradicts index.md/log.md in SPEC REQ-PLAN-010 + SKILL.md
Labels: type::task, priority::medium
> Surfaced by plan-036 e-skill-page-readme drift check as a CONFLICT: skills/yf-plan/README.md lines ~97,144 describe 'README.md — orientation (file map, reading order)' but the OKF migration reserved i...

**Disposition:** include
**Notes:** Four sites, not the two the issue names: two stale README-as-orientation lines plus two omissions (`index.md`/`log.md` absent from both lists). The adjacent ~20-omission File Layout defect is filed separately by Issue 5.4. Resolved by Issue 5.3.
