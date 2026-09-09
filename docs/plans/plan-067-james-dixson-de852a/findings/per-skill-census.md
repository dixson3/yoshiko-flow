---
type: Finding
okf_spec: OKF-PLAN
description: "EXP-004's census REBUILT under a stated node/edge definition. The threshold is re-derived, not inherited: nodes >= 5 publishes 11 of 20 and sits on a THREE-WAY TIE, which is a property of the corpus rather than of the choice."
id: per-skill-census
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# The per-skill census, rebuilt

## Why a rebuild rather than a citation

EXP-004 reported `RICH 5 · moderate 7 · TRIVIAL 8`, "`yf-drift-check` 3 nodes / 0 EDGES", and
`yf-plan` at 26 nodes / 6 edges. **Its prototype is lost and the finding never defines what
counts as a node or an edge**, so those numbers are model-dependent with the model gone — an
independent rebuild from the written finding got **9 trivial not 8**, **no zero-edge skill**, and
`yf-plan` at **34/33** against the reported 26/6. Inheriting a constant derived that way would
make the publication threshold unfalsifiable.

**measured** on the post-Epic-4 tree, through `web/plugins/skill_model.py` — the same reader the
site page uses (Issue 5.1), so the census cannot disagree with the page about a frontmatter fact.

## The definition (also stated in `plan.md`)

- A **NODE** is a distinct drawn box: the skill itself (1), plus one per distinct
  `depends-on-tool`, one per distinct `depends-on-skill`, one per distinct **reverse** dependent,
  and one CONTAINER box each for a non-empty `scripts/` (non-`test_` `.py`), `agents/`,
  `formulas/` and `protocols/` listing.
- An **EDGE** is one drawn arrow per external referent and one per non-empty container. Items
  *inside* a container are rows, not nodes — otherwise a script-heavy skill's node count measures
  its **file count** rather than its graph.

## The census

| skill | nodes | edges | tools | deps | rdeps | scripts | agents | formulas | protocols |
| :-- | --: | --: | --: | --: | --: | --: | --: | --: | --: |
| yf-plan | 10 | 9 | 3 | 2 | 0 | 13 | 8 | 4 | 2 |
| yf-research | 10 | 9 | 3 | 2 | 0 | 7 | 8 | 1 | 1 |
| yf-beads-extra | 9 | 8 | 1 | 0 | 7 | 0 | 0 | 0 | 0 |
| yf-beads-init | 8 | 7 | 3 | 1 | 1 | 1 | 0 | 0 | 1 |
| yf-beads-hygiene | 7 | 6 | 3 | 2 | 0 | 1 | 0 | 0 | 0 |
| yf-beads-upstream | 7 | 6 | 3 | 1 | 0 | 6 | 0 | 0 | 1 |
| yf-beads-authoring | 6 | 5 | 1 | 1 | 2 | 0 | 1 | 0 | 0 |
| yf-optimal-instructions | 6 | 5 | 1 | 1 | 0 | 1 | 1 | 0 | 1 |
| yf-markdown-pdf | 5 | 4 | 3 | 0 | 0 | 1 | 0 | 0 | 0 |
| yf-okf-hygiene | 5 | 4 | 2 | 1 | 0 | 2 | 0 | 0 | 0 |
| yf-skill-authoring | 5 | 4 | 1 | 0 | 1 | 1 | 4 | 0 | 0 |
| yf-change-validation | 4 | 3 | 1 | 0 | 0 | 1 | 0 | 0 | 1 |
| yf-incubator | 4 | 3 | 1 | 1 | 0 | 2 | 0 | 0 | 0 |
| yf-markdown-html | 4 | 3 | 2 | 0 | 0 | 1 | 0 | 0 | 0 |
| yf-markdown-lint | 4 | 3 | 1 | 0 | 0 | 1 | 0 | 0 | 1 |
| yf-okf | 4 | 3 | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| yf-diagram-authoring | 3 | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 0 |
| yf-drift-check | 3 | 2 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| yf-herdr | 3 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| yf-markdown-format | 3 | 2 | 1 | 0 | 0 | 2 | 0 | 0 | 0 |

## Three results the rebuild produces that the original did not

**1. `edges == nodes - 1` for EVERY skill.** These are **stars, not graphs**: a skill box with
spokes to its referents. The edge count therefore carries no information the node count does not,
which is why the threshold keys on nodes alone — and it also explains how EXP-004 could report
`yf-plan` at 26/6 and a rebuild at 34/33 without either being arithmetically wrong. They counted
different things.

**2. There is NO zero-edge skill under this definition.** EXP-004's "`yf-drift-check` 3 nodes / 0
EDGES" is an artifact of counting a container's contents as nodes while not drawing the container
edge. Here `yf-drift-check` is 3 nodes / 2 edges — its `agents/` and `protocols/` listings.

**3. The floor sits on a THREE-WAY TIE, exactly as pass-2 C11 warned** — though on different
members, which is the more useful confirmation: the tie is a property of the **corpus shape**, not
of any one model. At `nodes >= 5` the boundary members are `yf-markdown-pdf`, `yf-okf-hygiene` and
`yf-skill-authoring`. A one-node definitional difference reclassifies all three at once.

## The threshold

| threshold | publishes | boundary members |
| :-- | --: | :-- |
| `nodes >= 4` | 16 of 20 | 5-way tie |
| **`nodes >= 5`** | **11 of 20** | 3-way tie: yf-markdown-pdf, yf-okf-hygiene, yf-skill-authoring |
| `nodes >= 6` | 8 of 20 | 2-way tie: yf-beads-authoring, yf-optimal-instructions |
| `nodes >= 7` | 6 of 20 | 2-way tie |

**`nodes >= 5` is adopted, and the tie is recorded rather than engineered away.** It publishes 11,
against the 12 EXP-004's `RICH 5 + moderate 7` implied — close enough to say the two models agree
about the *shape* of the corpus while disagreeing about the counting, which is the honest summary.

The number that matters is not 11. It is that the threshold is **computed at build time from the
same shared model**, so a skill that grows past it gains a diagram automatically and a skill that
shrinks below loses one — neither requiring anyone to remember. A hand-maintained publication list
is the thing this replaces.
