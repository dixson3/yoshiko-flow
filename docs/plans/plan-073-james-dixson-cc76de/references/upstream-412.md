---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #412 - yf-research credibility_scorer.py over-scores:
  arxiv.org is Tier 1 (rubric says preprints Tier 4), .dev bump promotes third-party
  registries/mirrors'
---
# Upstream #412: yf-research credibility_scorer.py over-scores: arxiv.org is Tier 1 (rubric says preprints Tier 4), .dev bump promotes third-party registries/mirrors

- **Number:** 412
- **Title:** yf-research credibility_scorer.py over-scores: arxiv.org is Tier 1 (rubric says preprints Tier 4), .dev bump promotes third-party registries/mirrors
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

## Problem

`scripts/credibility_scorer.py` contradicts the rubric the triangulator is told to apply, in the **over-scoring** direction. (#147 covers under-scoring of non-`docs.*` vendor hosts; #336 covers unknown domains scored as untrustworthy. This issue is the other half.)

1. **Preprints are scored Tier 1.** `TIER_1_DOMAINS` contains `"arxiv.org"` (line 29 of `credibility_scorer.py`), while `agents/triangulator.md` line 119 puts "pre-prints" in Tier 4 (35-54). Any arXiv paper — unknown authors, vendor-authored, non-peer-reviewed — gets domain 85-100.
2. **The `.dev` TLD heuristic promotes third-party content to Tier 2.** `_domain_authority_score` (REQ-RESEARCH-024) returns 77 for any `.dev` host. That was meant for vendor-doc hosts, but it also covers package registries and mirrors: `pi.dev/packages/*` (third-party READMEs) and `upd.dev` (a GitHub-issue mirror).
3. **Undated sources get a flat `50` currency** (line 102, "2-5 year" band) regardless of whether the source describes a product that is days old.

## Evidence (research 070, from `sources.json`)

| id   | url                                              | domain | score | category     | rubric says                 |
| :--- | :----------------------------------------------- | -----: | ----: | :----------- | :-------------------------- |
| OW20 | arxiv.org/html/2601.10156 (authors unknown)      |     92 |    85 | high_trust   | Tier 4 preprint             |
| JE5  | pi.dev/packages/@riposta/pi-jev (third-party)    |     77 |    80 | high_trust   | Tier 4 personal/practitioner |
| PC8  | upd.dev/openai/codex/issues/37305 (mirror)       |     77 |    71 | verify       | same as PC9                 |
| PC9  | github.com/openai/codex/issues/37448 (original)  |     30 |    50 | questionable | same as PC8                 |
| PC1  | platform.claude.com/docs/… (official docs)       |     30 |    68 | verify       | Tier 2 (see #147)           |

The PC8/PC9 pair is the clearest symptom: the same source type scores 21 points apart purely on host TLD, and the mirror outranks the original.

The red-team caught this (`critique.md` item 5 [high], "Credibility scores diverge systematically from the rubric"), and the refiner has to rescore by hand — metadata work the scorer should have got right.

## Suggested fix

- Move `arxiv.org` (and other preprint servers) to Tier 4 by default; allow a peer-reviewed-venue override input (`--venue` or `--peer-reviewed`).
- Restrict the `.dev` bump to `docs.*`/vendor-doc path patterns, or add a denylist for registries/mirrors (`pi.dev/packages`, `npmjs.com`, `upd.dev`, …) that map to Tier 4.
- Allow an explicit `--published`-unknown-but-current signal (or use retrieval date with a flag) instead of a flat 50.
- Add `test_credibility_scorer.py` cases for each row above.

## Environment (recorded in case harness/model matters — root causes below appear to be in skill spec/code, not the runtime)

| Item             | Value                                                                   |
| :--------------- | :---------------------------------------------------------------------- |
| Harness          | **pi 0.87.1** (not Claude Code); subordinate session launched via yf-herdr in a herdr tab |
| Model            | **claude-opus-5-5**, thinking `medium`, via pi provider `cliproxyapi`   |
| yf / skill       | yf 0.5.0 (290b426); yf-research `v=0.5.0 tree=f3222bebd0c1`            |
| bd               | 1.3.0 (Homebrew)                                                        |
| Run              | research 070 "Jev-like classifiers for agent workflows", standard mode, 4 clusters, 71 sources |

Subagents (retriever, triangulator, red-team, …) were dispatched through pi's `Agent` tool rather than Claude Code's. If the red-team's context scoping is enforced differently under pi (e.g. the agent file's `## Context` list is advisory there), that could amplify the effect described below — worth confirming on a Claude Code run.

