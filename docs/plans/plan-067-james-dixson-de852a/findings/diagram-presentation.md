---
type: Finding
okf_spec: OKF-PLAN
description: "The RESTYLED set re-presented for plan-067's Diagram human-read gate — the gate that rejected the first set. Per-diagram, what changed against the two reference images. This document is NOT a read and does not discharge the gate."
id: diagram-presentation
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# The restyled diagram set — re-presented for the second read

> **THIS DOCUMENT IS NOT A READ, AND IT DOES NOT DISCHARGE THE GATE.** It is the material the
> gate needs. **The gate that rejected the first set is the gate that must accept the second**
> — an agent read is evidence, never a discharge.
>
> **This is plan-067's own gate.** Issue 6.4 then presents to **plan-066's**, which is a
> different gate and a later step (6.4 `depends-on` 7.8, so it structurally cannot present a
> rejected set).

## What was rejected, and what that told us

The first 20-diagram set was **fully green** — every checker at 0, every PNG byte-identical to a
fresh render. It was rejected anyway: **nodes too wordy**, and `architecture.d2` did not read as
a layered stack. That is the plan's highest-value process finding and is recorded in
[plan-retrospective.md](../plan-retrospective.md): *a second fully-green artifact set failing a
human read*. Green is not the same as good, and no mechanical gate was ever going to say so.

The operator supplied two reference images, preserved at `assets/style-reference/`. Per D8 they
are **normative for LAYOUT**; the **skill census stays normative for CONTENT**.

## What changed, per diagram

| Diagram | px | h/w | What changed |
| :-- | :-- | --: | :-- |
| `architecture.png` | 2596 x 2968 | 1.14 | **Rebuilt as the reference stack.** Bands bottom-to-top (tools → runtimes → beads → utility → markdown → workflows), one bare-name box per member, **no edges**, no sublabels, no counts. Was 7036 x 7554 with 36 edges. |
| `architecture-deps.png` | 3532 x 5080 | 1.44 | **NEW.** The relations the stack sheds — the 8-token tool layer, the `yf` subcommand paths, and all **twelve** `depends-on-skill` edges including the workflows→utility relation `#373` names by hand. |
| `lifecycle.png` | 8556 x 13362 | 1.56 | 25 sublabels expanded into child boxes; the `APPROVE / REVISE / INVESTIGATE-MORE` verdict set hoisted into three real nodes. |
| `install-matrix.png` | 8980 x 4472 | 0.50 | 14 sublabels expanded. |
| `formulas-map.png` | 4386 x 3888 | 0.89 | 6 sublabels expanded. |
| `formulas/plan-execute.png` | 6978 x 5690 | 0.82 | 11 sublabels expanded. |
| `formulas/plan-investigate.png` | 8698 x 1424 | 0.16 | 6 sublabels expanded. |
| `formulas/plan-review.png` | 9336 x 2342 | 0.25 | 8 sublabels expanded; **both** verdict sets hoisted — `conformance → PASS / INCOMPLETE` with INCOMPLETE looping back, `red-team → APPROVE / REVISE / INVESTIGATE-MORE` with REVISE routing to `resolve`. |
| `formulas/verify-artifact.png` | 7766 x 3056 | 0.39 | 7 sublabels expanded. |
| `formulas/yf-research.png` | 9450 x 1636 | 0.17 | 10 sublabels expanded. |
| `skills/*.png` (11) | 2064-4074 wide | 0.32-1.19 | **Restyled by RE-RUNNING the generator, not by editing.** The three-line skill node became bare boxes: name, `skill-group`, invocation, one per sub-verb. |

## Against `red-team-chain.png` specifically

That image is the **anti-pattern**: a node carrying `step: red-team`, `type: task · needs:
[conformance]`, two more prose lines, and the verdict set `APPROVE | REVISE | INVESTIGATE-MORE`
— all in one label. Every one of those is now its own box, and the verdict set is three nodes
with edges. **887 labels scanned across 21 diagrams; zero state enumerations remain.**

## What the checks establish, so the read can skip it

- All **21** PNGs sha256-identical to a fresh render under the unchanged `d2 v0.8.2 --theme 0
  --layout elk`. **No pin changed.**
- `architecture.d2` is edge-free, carries all **20** census skills spelled from frontmatter, and
  has no sublabel or parenthetical count.
- Membership survives, asserted **positively**: `groups_checked == 4 == len(census.groups)`, and
  no checker lost claim coverage.
- Every checker exits 0; the generated set matches a fresh generation; the site builds clean
  under `--fatal warnings`.
- **Six** negative controls observed to fail against code-side mutations under passing docs,
  including the two doors the restyle opened.

## What NO check can see — the read is for this

- **Whether the stack now reads as a stack.** That is the whole objection, and it is a
  judgement.
- **Whether the expanded child boxes are an improvement or merely a different shape.** 95
  sublabels became child boxes; the content was preserved deliberately rather than deleted, and
  that is a defensible call the reader may disagree with.
- **Label placement, overlap, truncation.** Nothing above measures whether two labels collide.

## Three things worth your attention, stated rather than buried

1. **`lifecycle.png` GREW** — 4364 x 11602 → 8556 x 13362. Expanding sublabels into boxes costs
   area. It is the largest diagram in the set and may still be the wrong shape; splitting it
   further was not in Epic 7's scope.
2. **`architecture-deps.png` at 1.44:1 is the best of three measured layouts** (`right` 3532 x
   5080; `down` 14782 x 1188 at 10:1; a tightened-grid variant 9728 x 1612). It is dense by
   nature — 35 edges — and dense is what the split bought the stack.
3. **The wide per-formula diagrams** (`plan-investigate` at 0.16, `yf-research` at 0.17) are
   linear chains, so width is inherent. Whether they read well at that aspect is a judgement.

## Outcome

On acceptance this gate closes and Issue 6.4 presents to **plan-066's** gate; plan-066's
`diagram-reads` record is updated, its gate opens, its Issues 8.1/8.3 run, it reaches `complete`,
and `#317` closes. On rejection, say what to change — the first rejection produced Epic 7, and a
second would produce the same kind of thing. **Neither this document nor any agent resolves
this gate.**
