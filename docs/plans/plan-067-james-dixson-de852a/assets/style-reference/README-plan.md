---
type: Asset
okf_spec: OKF-PLAN
description: "The operator-supplied reference images that define the diagram style spec (D8), preserved in-bundle so a cold reader can act on the spec rather than infer it."
id: style-reference
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# Diagram style references

Supplied by the operator at the Diagram human-read gate, which **rejected** the first
20-diagram set. These two images ARE the specification; D8 is their prose restatement, and
where the two disagree **the images win**.

## `architecture-reference.png` — the positive example

A **layered stack with no edges at all**. Reading bottom to top: external tools
(`bd`, `gh`, `pandoc`, `xelatex`, `herdr`) → runtimes (`uv`, `bash`) → `yf-beads-*` →
`yf-markdown-*` / `yf-okf-*` / `yf-herdr` → `yf-plan`, `yf-research` → `yf-incubator`.

What to copy:

- **One box per member.** Membership is shown by **tiling**, never by a text list inside a
  group box.
- **Bare-name labels.** `bd`, `uv`, `yf-plan`. No sublabel, no description, no version, no
  parenthetical count.
- **Width-proportional tiling** — boxes fill their band.
- **No arrows.** Layering carries the relationship.

## `red-team-chain.png` — the negative example

One node carrying five lines:

```
step: red-team
type: task · needs: [conformance]
DISPATCH agents/red-team.md AS A SUB-AGENT
never in the main session
APPROVE | REVISE | INVESTIGATE-MORE
```

Two distinct defects, and they need different fixes:

1. **Metadata crammed into a label** (`step:`, `type:`, `needs:`, the instruction) — delete it
   or move it to the page prose. A diagram is not a data sheet.
2. **A STATE ENUMERATION inside a node** (`APPROVE | REVISE | INVESTIGATE-MORE`). These are
   states with transitions between them. **Hoist them into the diagram** as real nodes and draw
   the flow — that is what the diagram is for, and burying it in a label is the whole reason the
   set was rejected.

## Why this is recorded rather than remembered

The first set passed every mechanical check — 20/20 byte-identical renders, all checkers exit 0,
`not_checked == 0` — and was still rejected. **No check can see that a diagram is unreadable.**
That is precisely what the human gate exists for, and it is the second time in this plan pair that
a fully-green artifact set failed a human read.
