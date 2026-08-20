---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #151: yf-research: link_normalizer.py breaks composite/cluster-prefixed source ids

- **Number:** 151
- **Title:** yf-research: link_normalizer.py breaks composite/cluster-prefixed source ids
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

Discovered while packaging research 004. link_normalizer.py render_sources_md() uses sid = s.get('id') or s.get('original_id'). A multi-cluster research project carries cluster-local ids ('1','2',...) plus a composite uid ('cross-repo-corpus:1'); the normalizer knows nothing about uid, so it emits '### 1', '### 2' and 30 ids collide across clusters (four distinct sources are each id '1'), producing GitHub -1/-2 disambiguation suffixes. Measured in a sandbox copy: 295 of 295 citations broken. It also destroys hand-authored sources.md front matter, the citation-id mapping table, and the credibility-model narrative. Separately, link-citations is a no-op here: ID_RE ^[A-Za-z]{1,3}[0-9]+$ is built from the same numeric id field. Fix is small: prefer a short_id field, or derive one from uid's cluster prefix. Real bundle was never touched (diff-verified); research 004 met the anchors-resolve requirement without the tool.
