# Research Index: OKF (Open Knowledge Format) compliance-delta for yf-plan / yf-research / yf-incubator artifacts

> **SUPERSEDED (plan-046, 2026-08-18).** This project distilled OKF **v0.1**. Upstream shipped
> **v0.2**, which §13 states *"supersedes OKF v0.1"*, and `skills/yf-okf/spec/OKF-BASELINE.md` has been
> reconciled to v0.2 against a verbatim vendored copy of the upstream spec. **Read this project as a
> record of v0.1 and of how the baseline was first derived — not as a current statement of what OKF
> requires.** Where a claim here is unchanged in v0.2 the baseline still cites it; where v0.2 changed
> a fact, the baseline cites v0.2 directly and marks the v0.1 finding wrong-after. The measured
> v0.1↔v0.2 delta is `docs/plans/plan-046-james-dixson-aabefa/findings/exec-002-v01-verbatim-delta.md`.
>
> One claim here is now **measurably false** and is corrected rather than merely aged: *"No non-Google
> production adopter is confirmed."* plan-046 exp-004 verified **four** non-Google repositories
> carrying literal OKF bundles, two of them at v0.2.

| Timestamp | Phase | Artifact | Description |
|:----------|:------|:---------|:------------|
| 2026-07-19T23:09 | decision | [DECISION.md](DECISION.md) | Decision: defer OKF integration (document-only) — v0.1 draft, no confirmed non-Google adopter, no materialized demand. Deferred impl bead yf-uz5k. Tracking gh-91. |
| 2026-07-17T23:34 | tooling | scripts/okf_conformance_check.py | OKF conformance checker (provisional SPEC ruleset; per-file frontmatter/type/reserved-file/citation/link deltas) |
| 2026-07-18T00:07 | triangulate | [artifacts/triangulation](artifacts/triangulation.md) | Cross-cluster triangulation of OKF spec, ecosystem, and local-artifact evidence (27 sources) |
| 2026-07-18T00:07 | critique | [artifacts/critique](artifacts/critique.md) | Adversarial critique pass: force-of-claim, absence findings, credibility caveats |
| 2026-07-18T00:07 | synthesize | [Summary](Summary.md) | Final report: compliance-delta table, Q1-Q3 + S1-S3 answers, recommendation (export-emit path) |
| 2026-07-18T00:07 | package | [sources](sources.md) | Human-readable source list with verbatim normative quotes and credibility framing |
| 2026-07-18T00:07 | package | diagrams/okf-compliance-delta.png | Compliance-delta matrix (7 OKF rules x 3 yf-* tools) + 3 integration paths, export-emit highlighted |
| 2026-07-18T00:08 | retrieve | [artifacts/cluster-okf-spec-primary](artifacts/cluster-okf-spec-primary.md) | 5 primary sources: OKF SPEC v0.1 draft rules (frontmatter type, okf_version, reserved files, citations, links, metadata model) |
| 2026-07-18T00:08 | retrieve | [artifacts/cluster-ecosystem-interop](artifacts/cluster-ecosystem-interop.md) | 14 web sources: OKF adoption (Google-only), nascent tooling, comparable formats, what compliance unlocks |
| 2026-07-18T00:08 | retrieve | [artifacts/cluster-local-artifacts](artifacts/cluster-local-artifacts.md) | 8 local sources: yf-plan/research/incubator bundle layouts, frontmatter usage, plan_manager audit checks |
