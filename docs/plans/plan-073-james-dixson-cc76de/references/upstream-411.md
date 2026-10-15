---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #411 - yf-research red-team runs before packager generates
  sources.md — every citation reported as a broken link'
---
# Upstream #411: yf-research red-team runs before packager generates sources.md — every citation reported as a broken link

- **Number:** 411
- **Title:** yf-research red-team runs before packager generates sources.md — every citation reported as a broken link
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

## Problem

The red-team runs before the packager, but the synthesizer is required to emit citation links that only resolve after packaging. The red-team has no way to know this, so it reports every citation as a broken link.

- `agents/synthesizer.md` rule 2: citation format is `[ID](sources.md#id)`.
- `agents/packager.md` step 4: "Generate `sources.md` from `sources.json` so GFM citation anchors resolve" (`link_normalizer.py all`).
- Pipeline order: synthesize → **critique** → refine → **package**. `sources.md` does not exist when the red-team runs.

## Evidence (research 070)

- Red-team `critique.md` item 4 [high]: "Broken links: every in-text citation targets `sources.md`, which does not exist." Its suggested fix was to rewrite all links to point at the `## Sources` section — i.e. to undo the synthesizer's mandated format.
- If the refiner follows that fix, the packager's `link_normalizer.py` and the synthesizer contract diverge.

This happens on every run, not only this one.

## Suggested fix (pick one)

1. Generate `sources.md` at the end of synthesize (`link_normalizer.py build-sources`), and have packager re-run it idempotently. Red-team and refiner then see resolvable anchors. (Interacts with #337's frontmatter/slug defects.)
2. Or state in `agents/red-team.md` that `sources.md` is packager-generated and link resolution is out of scope until package; move link resolution into a post-package check (see also #344).

## Environment (recorded in case harness/model matters — root causes below appear to be in skill spec/code, not the runtime)

| Item             | Value                                                                   |
| :--------------- | :---------------------------------------------------------------------- |
| Harness          | **pi 0.87.1** (not Claude Code); subordinate session launched via yf-herdr in a herdr tab |
| Model            | **claude-opus-5-5**, thinking `medium`, via pi provider `cliproxyapi`   |
| yf / skill       | yf 0.5.0 (290b426); yf-research `v=0.5.0 tree=f3222bebd0c1`            |
| bd               | 1.3.0 (Homebrew)                                                        |
| Run              | research 070 "Jev-like classifiers for agent workflows", standard mode, 4 clusters, 71 sources |

Subagents (retriever, triangulator, red-team, …) were dispatched through pi's `Agent` tool rather than Claude Code's. If the red-team's context scoping is enforced differently under pi (e.g. the agent file's `## Context` list is advisory there), that could amplify the effect described below — worth confirming on a Claude Code run.

