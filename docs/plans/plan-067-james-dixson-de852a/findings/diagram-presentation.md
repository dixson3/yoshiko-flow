---
type: Finding
okf_spec: OKF-PLAN
description: "The RESTYLED set re-presented for plan-067's Diagram human-read gate — the gate that rejected the first set. Per-diagram, what changed against the two reference images. This document is NOT a read and does not discharge the gate."
id: diagram-presentation
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# The restyled diagram set — re-presented for the second read

> ## ACCEPTED by the OPERATOR, 2026-09-07
>
> **The operator accepted this set.** Not this document, not the agent that built it, and not the
> session that executed the plan. The reads recorded in this bundle were **evidence**; the
> acceptance is theirs.
>
> **`lifecycle.png`'s height was accepted KNOWINGLY, as a recorded trade — not overlooked.**
> It is **8556 x 13362**, grown from 11602px, because expanding 95 sublabels into child boxes
> added **vertical structure**: the fix for wordiness worked against the aspect ratio. That
> regression was flagged before the read, on the exact dimension the FIRST read had objected to,
> and it was accepted anyway with the trade understood. A future reader should see a **decision**
> here, not an oversight — and should not "fix" it without asking, because the shorter version is
> the wordy one.
>
> The gate that rejected the first set is the gate that accepted this one.

> **THIS DOCUMENT WAS NOT THE READ, AND DID NOT DISCHARGE THE GATE — the operator's
> read did, on 2026-09-07.** What follows is the material as it was presented, preserved
> unchanged so the acceptance can be audited against what was actually in front of them. It is the material the
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
[plan-retrospective.md](plan-retrospective.md): *a second fully-green artifact set failing a
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

## What the split bought, in numbers

The two figures worth putting side by side, because they are the trade Issue 7.0b made:

| Diagram | px | h/w | Read as |
| :-- | :-- | --: | :-- |
| `architecture.png` | **2596 x 2968** | 1.14 | an **overview** — readable at one screen width |
| `architecture-deps.png` | **3532 x 5080** | 1.44 | a **reference** — allowed to be tall, because nobody reads it as an overview |
| *(the single diagram it replaced)* | *7036 x 7554* | *1.07* | *both at once, which is what was rejected* |

**That is the whole argument for the split.** One canvas answering "what is there" and "what
depends on what" has to be big enough for the second question while being read for the first. Two
canvases let each be sized for its own job: the stack shrank to **13% of the original area**, and
the relations moved somewhere that being dense is not a defect.

## Against `red-team-chain.png` specifically

That image is the **anti-pattern**: a node carrying `step: red-team`, `type: task · needs:
[conformance]`, two more prose lines, and the verdict set `APPROVE | REVISE | INVESTIGATE-MORE`
— all in one label. Every one of those is now its own box, and the verdict set is three nodes
with edges. **887 labels scanned across 21 diagrams; zero state enumerations remain.**

## What the checks establish, so the read can skip it

- All **21** PNGs sha256-identical to a fresh render under `d2 v0.9.0 --theme 0 --layout elk`.
  **The pin moved AFTER this read, and the pictures did not** — re-pinned **v0.8.2 → v0.9.0** on 2026-09-09; geometry measured identical 21/21, the differences being glyph-edge antialiasing, so the pictures are the accepted ones. Re-pinned on the operator's
  decision; no third read was required, and the measurement is why.
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

1. **`lifecycle.png` GOT WORSE, on a dimension you had already questioned.** 4364 x 11602 →
   **8556 x 13362**. This is the one place the second set is worse than the first: expanding 95
   sublabels into child boxes added **vertical structure**, so the fix for wordiness worked
   *against* the aspect ratio. The nodes are no longer wordy; the diagram is taller than ever.
   It is the largest artifact in the set by area.

   **Two remedies are plausible and NEITHER has been started**, because which one is right
   depends on what you object to: **split the combination back into two diagrams** (undoing
   Issue 4.2, which merged `phase-model` and `lifecycle` — the merge was right on content and may
   be wrong on scale), or **restructure it horizontally**. If your verdict is "everything except
   lifecycle", say which and it becomes one issue.
2. **`architecture-deps.png` at 1.44:1 is the best of three measured layouts** (`right` 3532 x
   5080; `down` 14782 x 1188 at 10:1; a tightened-grid variant 9728 x 1612). It is dense by
   nature — 35 edges — and dense is what the split bought the stack.
3. **The wide per-formula diagrams** (`plan-investigate` at 0.16, `yf-research` at 0.17) are
   linear chains, so width is inherent. Whether they read well at that aspect is a judgement.

## Outcome — RESOLVED

**Accepted 2026-09-07 by the operator.** plan-067's Diagram human-read gate (`yf-mol-gtcy.10`)
is resolved on their authority. Issue 6.4 then presents to **plan-066's** gate; plan-066's
`diagram-reads` record is updated, its gate opens, its Issues 8.1/8.3 run, it reaches `complete`,
and `#317` closes. On rejection, say what to change — the first rejection produced Epic 7, and a
second would produce the same kind of thing. **Neither this document nor any agent resolves
this gate.**
