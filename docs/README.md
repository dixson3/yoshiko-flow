# `docs/` — index

Everything under `docs/` that a reader is expected to navigate to, in one place. This file
exists because the directory had **no entry point**: the diagrams and the four research reports
were reachable only by knowing they were there.

## Reference

| Document | What it answers |
| :-- | :-- |
| [`yf/preflight-contract.md`](yf/preflight-contract.md) | The `yf preflight` kernel contract — every status value, the JSON schema, the `prereqs-present` and `yf-version` cache semantics, and what `SCAFFOLD_VERSION` ensures at each version. |
| [`recommended-settings.md`](recommended-settings.md) | The per-harness config yf recommends, why each key is there, and which drift axes `yf doctor` ships. Reference prose — the machine-readable source of truth is each `yf/profiles/<harness>.json`. |
| [`MIGRATION.md`](MIGRATION.md) | Moving an existing project onto the current layout. |

## Diagrams

Authored as `.d2` and rendered to `.png`; the source sits beside every render, so a diagram is
edited rather than redrawn (see the `yf-diagram-authoring` skill).

| Diagram | Subject |
| :-- | :-- |
| [`diagrams/skill-ecosystem.png`](diagrams/skill-ecosystem.png) ([source](diagrams/skill-ecosystem.d2)) | How the shipped skills relate — which compose, which are triggers, which own an engine. |
| [`diagrams/drift-check-artifact-graph.png`](diagrams/drift-check-artifact-graph.png) ([source](diagrams/drift-check-artifact-graph.d2)) | The artifact graph `DRIFT-CHECK.md` declares: nodes, edges, and which side is authoritative. |

## Research

Each is a complete `yf-research` bundle — start at `Summary.md` for the findings, `sources.md`
for the evidence, and `artifacts/` for anything the work produced.

| Report | Question |
| :-- | :-- |
| [`research/001-okf-compliance-delta`](research/001-okf-compliance-delta/Summary.md) | How far the repo's artifact folders sit from the OKF baseline, and what closing the gap costs. Carries its own [`DECISION.md`](research/001-okf-compliance-delta/DECISION.md). |
| [`research/002-harness-global-rule-minimization`](research/002-harness-global-rule-minimization/Summary.md) | What the always-loaded rule surface must contain, and what can be cut without losing a trigger — the basis for the minimized managed block. |
| [`research/003-graph-engineering-hypothesis`](research/003-graph-engineering-hypothesis/Summary.md) | Whether plan structure is better modelled as a graph than as prose, and what that would buy. |
| [`research/004-plan-process-defect-mining`](research/004-plan-process-defect-mining/Summary.md) | The recurring defect classes mined from the plan corpus — the source of several requirements now in `SPEC.md`. |

Bundle 001 predates the OKF reserved-name convention and uses `_index.md`; 002–004 use
`index.md`. That inconsistency is [what 001 is about](research/001-okf-compliance-delta/Summary.md).

## Plans

[`plans/`](plans/) holds every `yf-plan` bundle, one directory per plan. They are **portable by
contract**: a cold reader in a different repository can understand a plan from its folder alone.
Use `yf-plan list` rather than reading the directory — it renders status, and tags plans that are
approved but never executed.
