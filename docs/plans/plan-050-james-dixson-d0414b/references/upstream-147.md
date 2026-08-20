---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #147: Source-scorer defect: domain_authority floors all non-docs.<vendor>.com hosts at 30

- **Number:** 147
- **Title:** Source-scorer defect: domain_authority floors all non-docs.<vendor>.com hosts at 30
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::medium

## Body

Found during REFINE of research 003 (critique C-7). The credibility scorer used by yf-research assigns domain_authority=30 to every source whose host does not match docs.<vendor>.com. In research 003 that hit 31 of 90 entries, ~20 of them first-party vendor documentation (burr.apache.org, developers.llamaindex.ai, google.github.io, ai.pydantic.dev, reference.langchain.com, dspy.ai, microsoft.github.io). The rubric's 0-34 band is Tier 5 ('anonymous sources, content farms'), so first-party docs are scored as content farms purely on hostname shape: a ~40-point deflation on a 35%-weighted axis. Visible within one publisher: docs.langchain.com=77 vs reference.langchain.com=30. Effect: per-cluster medians and every verify-tier label on a first-party doc are understated, and reports that rank findings by evidence strength inherit the artifact. Research 003 discloses this rather than re-scoring (re-scoring after critique would silently re-rank the corpus). Fix belongs in the scorer: score domain authority against the rubric's tier definitions, not hostname shape.
