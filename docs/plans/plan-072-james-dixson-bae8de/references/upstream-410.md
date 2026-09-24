---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #410 - yf-research red-team: quote check reads only sources.json,
  but synthesizer quotes from cluster artifacts — false ''untraceable quote'' [high]
  findings'
---
# Upstream #410: yf-research red-team: quote check reads only sources.json, but synthesizer quotes from cluster artifacts — false 'untraceable quote' [high] findings

- **Number:** 410
- **Title:** yf-research red-team: quote check reads only sources.json, but synthesizer quotes from cluster artifacts — false 'untraceable quote' [high] findings
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

## Problem

The red-team's quote-fidelity check is structurally guaranteed to produce false "untraceable quote" findings, because it is given a narrower evidence set than the synthesizer that wrote the quotes.

- `agents/red-team.md` `## Context` lists only `Summary.md` and `sources.json`.
- `agents/retriever.md` step 4 stores **one** `quote` (+ `snippet`) per source in `sources.json`, but step 5 writes **multiple** per-claim blockquotes into `artifacts/cluster-<name>.md`.
- `agents/synthesizer.md` builds `Summary.md` blockquotes from the cluster artifacts / `triangulation.md`.

So any source quoted more than once, or quoted with a passage other than its single stored `quote`, cannot be verified by the red-team.

## Evidence (research 070)

- Red-team `critique.md` item 1 [high]: "44 of 71 direct quotes cannot be traced to `sources.json`" (25 exact, 2 near, 44 no match).
- Parent-side re-check with the same normalization (Unicode quotes/dashes, emphasis, whitespace, split on `...`): **69 of 71** blockquotes appear verbatim in `artifacts/cluster-*.md`. The one remaining is a Go code line (`v.SetDefault(...)`) that the regex could not normalize — not a fabrication signal.
- Net effect: a [high] item that reads as possible fabrication, consuming refine effort, when the true defect is evidence-file incompleteness.

## Relationship to #335

Complementary, not a duplicate. #335 is a *false negative* (red-team certified a paraphrase as verbatim). This is a *false positive* from the same root: the red-team does not verify quotes against the same text the synthesizer quoted from.

## Suggested fix (pick one)

1. Make `sources.json` the single evidence store: retriever/triangulator write every blockquoted passage to a `quotes: []` array per source; synthesizer may only quote from that array. Red-team then checks against it. (Also closes #335's gap.)
2. Or give the red-team read access to `artifacts/cluster-*.md` for **quote verification only** (keep `plan.yaml` excluded for the bias rationale).

Option 1 is preferable: the shipped report's evidence file then actually supports its quotes for any later reader.

## Environment (recorded in case harness/model matters — root causes below appear to be in skill spec/code, not the runtime)

| Item             | Value                                                                   |
| :--------------- | :---------------------------------------------------------------------- |
| Harness          | **pi 0.87.1** (not Claude Code); subordinate session launched via yf-herdr in a herdr tab |
| Model            | **claude-opus-5-5**, thinking `medium`, via pi provider `cliproxyapi`   |
| yf / skill       | yf 0.5.0 (290b426); yf-research `v=0.5.0 tree=f3222bebd0c1`            |
| bd               | 1.3.0 (Homebrew)                                                        |
| Run              | research 070 "Jev-like classifiers for agent workflows", standard mode, 4 clusters, 71 sources |

Subagents (retriever, triangulator, red-team, …) were dispatched through pi's `Agent` tool rather than Claude Code's. If the red-team's context scoping is enforced differently under pi (e.g. the agent file's `## Context` list is advisory there), that could amplify the effect described below — worth confirming on a Claude Code run.

