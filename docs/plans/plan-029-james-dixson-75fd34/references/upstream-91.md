---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #91: research 001: OKF compliance-delta for yf-plan / yf-research / yf-incubator artifacts

- **Number:** 91
- **Title:** research 001: OKF compliance-delta for yf-plan / yf-research / yf-incubator artifacts
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Coarse tracking issue for completed research **001 — OKF (Open Knowledge Format) compliance-delta** for `yf-plan` / `yf-research` / `yf-incubator` artifacts. Run via `/yf-research coordinate 001`; the full multi-phase pipeline (tooling → retrieve×3 → triangulate → synthesize → critique → refine → package) is complete and the epic is closed.

## Question

Exactly where do yf-plan plan folders, yf-research research dirs, and yf-incubator artifacts diverge from the OKF SPEC, which gaps are mechanical vs conceptual, and which integration path (native-compliant frontmatter / export-emit / document-only) is recommended?

## Findings

- **OKF v0.1 is a draft** (GoogleCloudPlatform/knowledge-catalog, self-labeled "not an official Google product") with **one confirmed production consumer** (Google's Knowledge Catalog) and no confirmed non-Google adopter. A nascent third-party linter/validator/MCP ecosystem exists (hobby-scale, published within weeks of the June launch).
- **Hard-conformance bar is low:** the only MUST is that every non-reserved `.md` opens with parseable YAML frontmatter carrying a non-empty `type`. `okf_version`, reserved `log.md`, `# Citations` numbering, and `/`-absolute links are all SHOULD-level and largely unexercised even in Google's own reference bundles.
- **Only two conceptual gaps:** (1) yf-plan and yf-research emit **no frontmatter** (metadata lives as bold `**Field:**` prose / plain GFM); (2) **divergent reserved index filename** (`README.md` / `_index.md` vs OKF's `index.md`). yf-incubator already emits frontmatter but lacks a `type` key. Everything else is mechanical or a non-gap.
- **Extension keys** are *SHOULD*-preserved (not MUST — a red-team pass corrected an initial over-claim), so existing plan/incubator metadata can ride along, though round-trip fidelity is unverified against any specific consumer.

## Recommendation

**Export-emit path**, framed as **least-regret** (not a fidelity-guaranteed win) for a v0.1 draft with at most one adopter: keep each tool's native metadata model as source of truth and add a thin OKF emitter that projects a conformant frontmatter view on demand. Contingent on SHOULD-level preservation being acceptable, demand materializing, and accepting the emitter's real whole-bundle build cost (nested per-level `index.md`).

## Artifacts

- Report: `docs/research/001-okf-compliance-delta/` (`Summary.md`, `sources.md` with 27 cited sources, compliance-delta matrix diagram, per-phase artifacts, provisional `okf_conformance_check.py`)
- Committed in `98be96a`.
- Beads: epic `yf-mol-2av` (closed) and its pipeline sub-beads — local-only, not mirrored per-bead (coarse granularity).

