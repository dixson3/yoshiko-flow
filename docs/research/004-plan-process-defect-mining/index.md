---
okf_version: '0.1'
---

# Research Index: Process-defect mining across 83 plan bundles: remediation pairs and refactor opportunities in yf-plan / yf-research

- [scripts/remediation_pairs.py](scripts/remediation_pairs.py) - [tooling] Remediation-pair extractor: inventory (83/83 bundles reconciled) + candidate pairs (83 candidates, per-signal evidence, no scores)
- [artifacts/cluster-yf-corpus.md](artifacts/cluster-yf-corpus.md) - [retrieve] yf-corpus: 15 findings, 12 confirmed / 7 rejected pairs, 8 defect classes (27 sources)
- [artifacts/cluster-cross-repo-corpus.md](artifacts/cluster-cross-repo-corpus.md) - [retrieve] cross-repo: 9 defect classes with presence/absence matrix, ~15 confirmed / 6 rejected (30 sources)
- [artifacts/cluster-execution-telemetry.md](artifacts/cluster-execution-telemetry.md) - [retrieve] execution telemetry: 53 discovered-from edges, 0 cross-plan-epic; trend downward LOW confidence (15 sources)
- [artifacts/cluster-history-and-upstream.md](artifacts/cluster-history-and-upstream.md) - [retrieve] history+upstream: 4 confirmed pairs, 4 never-planned defect classes (28 sources)
- [sources.json](sources.json) - [retrieve] Merged source ledger, keyed by composite `uid` (`<cluster>:<n>`): 136 first-party sources across 6 clusters (100 scored at triangulate; the 35 `yf-corpus-reviews` rescored at refine; 1 `refine-verification`)
- [artifacts/triangulation.md](artifacts/triangulation.md) - [triangulate] 18 merged defect classes, 3 overlap candidates split not merged, 5 contradictions adjudicated, 16 insufficient-evidence items; 100 sources scored (67 high_trust)
- [artifacts/cluster-yf-corpus-reviews.md](artifacts/cluster-yf-corpus-reviews.md) - [retrieve] Supplementary: 93 yf review passes mined; resolves M2b/M6a/M6b in yf, adds M6c + M14b, refutes the weak-on-commands calibration (35 sources)
- [Summary.md](Summary.md) - [synthesize] Final report (refined): 16 ranked defect classes + owning surfaces, 2 structural bounds, 003 reconciliation, 20 tabled unknowns (295 citations, 0 unresolved anchors)
- [sources.md](sources.md) - [synthesize] Source ledger: 136 first-party sources, one heading per source, cluster-prefixed short ids (`XR`/`YF`/`YFR`/`ET`/`HU`/`RF`) mapped to `sources.json`'s composite `uid`s
- [artifacts/critique.md](artifacts/critique.md) - [critique] Red-team: 9 must-fix (2 repo-count errors, cost unevidenced, single-cluster flags absent at point of use, 1 uncited claim, blind not attested end-to-end)
- [diagrams/defect-class-taxonomy.png](diagrams/defect-class-taxonomy.png) - [package] Diagram: 16 ranked defect classes + 2 non-defect rows mapped onto owning skill surfaces (source: [diagrams/defect-class-taxonomy.d2](diagrams/defect-class-taxonomy.d2))
- [diagrams/evidence-pipeline.png](diagrams/evidence-pipeline.png) - [package] Diagram: evidence pipeline — 4 clusters to triangulation to synthesis, with the fifth cluster's out-of-band path (source: [diagrams/evidence-pipeline.d2](diagrams/evidence-pipeline.d2))
- [plan.yaml](plan.yaml)
- [diagrams/defect-class-taxonomy.d2](diagrams/defect-class-taxonomy.d2)
- [diagrams/evidence-pipeline.d2](diagrams/evidence-pipeline.d2)
