---
type: Finding
okf_spec: OKF-PLAN
description: "Operator-requested trial: the SAME full-content-load architecture diagram built twice, once in archify and once in d2. Both artifacts exist; the real checker passes the .d2 (exit 0) and FAILs the archify .json (exit 1) and .html (exit 1). Verdict is PENDING OPERATOR."
id: archify-trial
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# archify-trial — the same diagram, built twice

## What this is, and what it is not

An **operator-requested trial**, not a decision. Epic 3 was commissioned to build one diagram
twice — once as an archify `architecture` spec, once as `.d2` — at the **full declared content
load**, and to report the comparison. **This document resolves no gate.** Section "Verdict:
PENDING OPERATOR" lays the three options out neutrally.

It also is not a re-run of `exp-001-archify-vs-d2.md`. That experiment recorded four
disqualifiers, and **three of the four were later refuted** — headless raster export
(`visual-check` produces PNGs, exercised below), vendorability, and the showcase quality gate.
Only the network-font observation is re-measured here, and only in passing. Nothing below leans
on a refuted claim.

## Content load — what both artifacts carry

**measured:** both builds carry the identical declared load: **8** external tools, **20** skills
in **4** groups, the full `yf` subcommand-path set, **18** `depends-on-tool` edges, **12**
`depends-on-skill` edges, and one `uv` substrate edge. Node/edge totals are equal by
construction: archify **43 components / 32 connections**; the `.d2` carries the same 43 leaf
nodes plus 6 container nodes and the same 31 dependency edges plus 3 structural edges.

**measured:** `uv` is drawn as a **shared substrate** in BOTH artifacts — one dashed edge plus a
label naming the exclusions — not as 16 separate arrows. The exclusion set is
`yf-beads-authoring`, `yf-beads-extra`, `yf-diagram-authoring`, `yf-drift-check`.

## The 10-vs-12 correction

**measured:** re-derived from `skills/*/SKILL.md` `depends-on-skill` frontmatter, the
skill-to-skill edge count is **12, not 10**:

```
yf-beads-authoring->yf-beads-extra    yf-beads-hygiene->yf-beads-extra
yf-beads-hygiene->yf-beads-init       yf-beads-init->yf-beads-extra
yf-beads-upstream->yf-beads-extra     yf-incubator->yf-beads-extra
yf-okf-hygiene->yf-okf                yf-optimal-instructions->yf-skill-authoring
yf-plan->yf-beads-extra               yf-plan->yf-beads-authoring
yf-research->yf-beads-extra           yf-research->yf-beads-authoring
```

`plan.md:184` ("the 10 `depends-on-skill` edges") and `plan.md:193` ("**0 of 10**
`depends-on-skill` edges drawn") both say ten. **inferred:** the undercount is the two
non-`beads`-target edges — `yf-okf-hygiene->yf-okf` and
`yf-optimal-instructions->yf-skill-authoring` — which is the same shape as the plan's own
scope-of-search defect recorded at `plan.md:128`. `SC19` and Issue 4.1 should be read as **12**.

**measured:** one further frontmatter irregularity — `skills/yf-herdr/SKILL.md` carries no
`depends-on-skill` key at all (the other 19 carry it, sometimes empty). It contributes no edge
either way, so the count is unaffected.

## 1. Legibility at this density

| Artifact | Path | Dimensions | Bytes |
| :-- | :-- | --: | --: |
| d2 render | `assets/archify-trial/architecture.png` | 6540 x 8248 px | 621,130 |
| archify viewer | `assets/archify-trial/architecture.html` | viewBox 3560 x 1680 | 753,916 |
| archify raster (light) | `architecture.visual-check.2048x1320.light.png` | 2048 x 1320 px | 239,619 |
| archify raster (light) | `architecture.visual-check.1440x900.light.png` | 1440 x 900 px | 171,371 |

Dark-theme rasters exist at both sizes. `d2 --version` = **v0.8.2**; the render used **exactly**
the repo's pinned invocation `d2 --theme 0 --layout elk <src> <out.png>`, exit 0. No pin was
changed and `web/content/images/` was not touched.

### The d2 render — read directly

**measured:** every node label is legible at 1:1. The three layers read as layers: the `yf CLI`
container sits at the top, `external tools (8)` in the middle band, `embedded skills (20)` as a
large container at the bottom. The four groups read unambiguously as groups — each is its own
labelled sub-container with a visible border.

**measured, and the real defect:** elk stacks the four group containers by rank rather than
side-by-side, so `beads` is pushed roughly 1,400 px below `workflows`/`utility`/`markdown`,
leaving a **large empty band** inside the skills container — about 25% of the canvas is white.
The tool-to-skill edges become long orthogonal snaking runs (some ~4,000 px) descending through
that band in a dense parallel bundle of ~18 lines. Edges do not overlap nodes and no label is
masked, but the bundle is hard to trace by eye: following `git -> yf-okf-hygiene` across the
canvas is a deliberate act, not a glance. Aspect ratio 0.79 makes it a scroll-down artifact.

**measured:** the alternative `direction: right` was rendered as a control and is **worse for a
page** — 11330 x 4232 px (47.9 Mpx vs 53.9 Mpx, but 11,330 px wide). Kept `down`.

### The archify raster — read directly

**measured, stated rather than cropped away:** `archify visual-check` yields a **full-page viewer
screenshot**, not a clean diagram render. The captured image contains the document title bar, the
`Light` / `Classic` / `Present` / `Export` controls at top right, a `PATH / MAP / LENS` zoom dock
at bottom right, and the four HTML conclusion cards below the diagram panel. Roughly 30% of the
2048 x 1320 raster is viewer chrome and cards rather than diagram. That is a real limitation of
using this raster as a committable figure.

**measured:** inside the diagram panel, the four groups read as groups **better than in d2** —
each is a dashed, coloured, labelled region (`beads (5)`, `workflows (3)`, `utility (8)`,
`markdown (4)`) and the five regions plus the CLI region sit in one clean horizontal row. The
tool layer reads as a layer (a single labelled band across the top). Edge routing is orthogonal
with no node overlaps and no masked labels.

**measured:** node text is **not readable** at any checked desktop size. `visual-check` measured
`minimumProjectedNodeTextPx` = **2.35 px** at 1440x900 / 1600x1000 / 1920x1080 and **4.51 px** at
2048x1320, against a floor of 6 px — the viewer projects a 3560-wide viewBox into a 930 px
diagram panel. On my own read of the 2048x1320 capture I can resolve the region titles and the
cards, but the 43 node labels are grey smears.

**measured:** `visual-check` **exit 1**, `status: fail`, 8 error diagnostics: 4 x
`viewer/viewport-overflow` (vertical overflow at 1440x900, 1600x1000, 1920x1080 light and
1440x900 dark; e.g. `scrollHeight` 1085 vs `innerHeight` 900) and 4 x
`viewer/projected-text-readability`. `deliver` itself exited **0**: 9/9 artifact checks,
composition profile `standard`, 0 errors, **37 warnings** (all `composition/proper-crossing` —
edge-over-edge crossings, which archify tolerates as warnings at `standard`).

### The cost of getting archify to render at all

**measured, and this is the load-bearing legibility fact.** archify's architecture renderer
enforces a `clean-flow` invariant set that a caller must satisfy by **hand-placing every node and
hand-routing every edge**. The convergence path, counting unique renderer diagnostics:

| Round | What was authored | Unique diagnostics |
| :-- | :-- | --: |
| 1 | naive grid, auto routes | render aborted; boundary-outside-viewBox, 3 too-short connections, plus `edge-through-node` / `endpoint-side-direction` en masse |
| 2 | generous spacing, explicit viewBox, short boundary labels | **39** (25 `edge-through-node`, 12 `endpoint-side-direction`, 2 `container-border-run`) |
| 3 | programmatic lane allocator: per-tool horizontal lanes, per-column vertical corridors, explicit `fromSide`/`toSide`/`via` on all 32 edges | **3** |
| 4 | corridor lanes moved off the 30 px boundary pad; one CLI edge re-routed under the canvas | **0** — `validate --quality standard` `ok: true` |

**inferred:** rounds 3 and 4 were only tractable because the spec is generated by a script that
computes lanes; hand-editing 32 `via` arrays to convergence is not a realistic authoring loop.
d2/elk does this routing automatically, for free, from 145 lines of source.

**measured:** `--quality showcase` was not attempted. `SKILL.md` caps a showcase candidate at
"at most 12 primary nodes"; the declared load is 43. `standard` is the profile the skill itself
names for a dense map.

## 2. Do the enumerated member ids survive? — the real checker, run against each

The decisive checkability question. Command, per artifact:

```bash
uv run scripts/checks/check_web_counts.py --corpus '<path>' --min-files 1 --json
```

`--min-files 1` was required: the default floor is 5 and a single-file corpus is INCONCLUSIVE
below it. Exit codes were captured directly from `$?`, never through a pipe.

| Artifact | Exit | Verdict | Claims | Mismatches | Unenumerated |
| :-- | --: | :-- | --: | --: | --: |
| `architecture.d2` | **0** | PASS | 9 | 0 | 0 |
| `architecture.json` | **1** | FAIL | 17 | 7 | 0 |
| `architecture.html` | **1** | FAIL | 141 | 63 | 12 |
| `architecture.png` | **2** | INCONCLUSIVE | 0 | — | — |

Verbatim summary lines:

```
architecture.d2    check_web_counts: scanned 1 file(s), 9 counted-set claim(s); 0 mismatch(es), 0 unenumerated group(s)
architecture.json  check_web_counts: scanned 1 file(s), 17 counted-set claim(s); 7 mismatch(es), 0 unenumerated group(s)
architecture.html  check_web_counts: scanned 1 file(s), 141 counted-set claim(s); 63 mismatch(es), 12 unenumerated group(s)
architecture.png   check_web_counts: INCONCLUSIVE — scanned 1 file(s) and found ZERO counted-set claims — the matcher, not the docs, is what to fix
```

**measured — what the checker does with a non-`.md`/`.d2` path.** It does **not** filter by
extension: `expand_corpus` globs whatever `--corpus` names and reads it as text, so `.json`,
`.html` and `.png` are all *scanned*. What it does not do is *understand* them. The region rule
is a single binary switch, `is_d2 = path.suffix == ".d2"`. On `.d2` a group's membership region
is exactly one physical line; on everything else it is the claim line **plus continuation lines**
— the Markdown-bullet rule. So:

- On `.json`, the `utility (8): ...` boundary label is followed by its `"wraps"` array, and the
  next group's ids bleed into the previous group's region. All **7** findings are of the form
  ``group `beads` lists non-member(s) ['yf-change-validation', ...]`` — **false positives, every
  one**. This is exp-001's measured defect (it saw 2) reproduced and made worse by richer
  content.
- On `.html`, the ids live in minified inline JSON inside a `<script>` block, so line boundaries
  are arbitrary: 141 claims are matched, 63 are reported as mismatches (mostly `OMITS member(s)`
  under the omission rule `REQ-CHECK-013`) and 12 groups as *unenumerated*. Also **false
  positives**. Note this differs from exp-001, which recorded the HTML as exit 0 with membership
  silently unchecked; two things changed since — the omission rule landed, and this HTML embeds
  conclusion cards that enumerate every id. The artifact now fails loudly instead of passing
  vacuously. Neither behaviour is *correct*; both are the checker reading a format it has no
  parser for.
- On `.png` the answer is the honest one: **exit 2, INCONCLUSIVE, zero claims.** A raster is not
  checkable by this instrument, in either toolchain.

**measured — the ids do physically survive in the archify artifacts.** The `.json` carries every
id twice (component labels and the conclusion cards) and the `.html` carries them in the embedded
spec. Survival of the *strings* is not the issue. What does not survive is the checker's ability
to **partition them into groups**, because that partition is expressed as JSON structure rather
than as one line of text.

**measured — the `.d2` pays for its pass.** To make membership visible under the one-line rule,
each group container's `label:` is a single physical source line carrying the count and all its
member ids (`\n`-escaped for rendering), while the group's children are the individual skill
nodes. The names are therefore written twice in the source. That redundancy is a cost imposed by
`member_region`'s one-line `.d2` rule, and it is the price of the exit 0.

## 3. The checkability cost of committing an archify artifact

**archify has no d2 input path.** It consumes its own typed JSON and emits HTML; there is no
importer, no exporter and no intermediate `.d2`. So committing an archify artifact does not add a
format — it *replaces* the one the repo's checks are written against.

The **checkability** cost, measured, is three-layered:

1. **The default corpus never sees it.** `DEFAULT_CORPUS` is
   `web/content/**/*.md`, `web/content/**/*.d2`, `README.md`, `AGENTS.md`. An `.html` or `.json`
   committed under `web/content/images/` is simply **not scanned**. Silence, not a failure.
2. **Pointed at it explicitly, the checker is wrong in both directions.** 7 false-positive
   mismatches on the `.json`, 63 + 12 on the `.html`. Adopting archify therefore means either
   living with a checker that cannot be pointed at the artifact, or **writing and maintaining a
   second, format-specific extractor** — a new instrument, with its own negative controls, whose
   only job is to re-derive what one `.d2` line already gives away.
3. **The raster is uncheckable either way** (exit 2), so nothing is lost *there* by switching —
   but nothing is gained either, and the archify raster is additionally polluted with viewer
   chrome (§1).

The narrower structural point, still standing from exp-001 and re-measured here: the archify HTML
references `https://fonts.googleapis.com/css2` and `https://fonts.gstatic.com`, so it is not
network-independent. That is a site-build consideration, not a checkability one.

## 4. Adoption does NOT proceed inside this plan

State plainly, regardless of which option the operator picks: **adopting archify does not proceed
inside plan-067.** Every downstream artifact this plan touches keys on `*.d2`:

| Keyed surface | Where | What it keys on |
| :-- | :-- | :-- |
| `web-diagram-src` manifest node | `DRIFT-CHECK.md:79` | `web/content/images/*.d2` |
| four drift edges | `DRIFT-CHECK.md:136-140` | `e-web-diagram-counts`, `e-web-diagram-cli`, `e-web-diagram-formulas`, `e-web-backend-diagram`, all sourced at `web-diagram-src` |
| DRIFT-CHECK §6 trigger scope | `DRIFT-CHECK.md:275` | `web/content/images/*.d2` |
| CHANGE-VALIDATION §3 trigger scope | `CHANGE-VALIDATION.md:334` | `web/content/images/*.d2` -> `web-counts`, `web-harness-paths`, `web-backend-claim` |
| the per-skill generator's emitter | `plan.md:210`, Issue 5.2 | `build_model()` -> **`to_d2()`** |
| the `.d2`/`.png` pairing rule | `DRIFT-CHECK.md:231` | every `*.d2` must have a sibling `*.png` |

**measured:** `to_d2()` does not exist yet — `grep -rn "to_d2" --include='*.py' .` returns nothing
outside `plan.md`. It is this plan's own Issue 5.2 deliverable, which is precisely why an
adoption decision taken now would invalidate work the plan has not yet done.

Re-keying those surfaces is a **toolchain migration**, and belongs upstream as its own plan.
Consequently **all three operator outcomes leave plan-067 continuing in d2**:

| Outcome | What plan-067 does next |
| :-- | :-- |
| **adopt** | plan-067 continues in d2 unchanged; a separate upstream plan is filed for the migration |
| **keep-for-exploration** | plan-067 continues in d2 unchanged; archify stays an ad-hoc, uncommitted, unchecked tool |
| **drop** | plan-067 continues in d2 unchanged |

## 5. Verdict: PENDING OPERATOR

**No recommendation is made here.** The operator commissioned the trial and the operator judges
it. The evidence for each option, neutrally:

### Option A — adopt archify (as a future upstream migration)

*Evidence for:* the four groups and the tool layer read as clean, labelled, colour-coded regions
in one horizontal row — visibly better group legibility than elk's rank-stacked containers. The
viewer is interactive (pan/zoom/search/focus/trace/Export), which no PNG offers. `deliver` gives
deterministic receipts (spec sha256 `5deb041c…`, artifact sha256 `4325bc31…`) and headless raster
export works — exp-001's raster disqualifier is refuted. Three of exp-001's four disqualifiers no
longer stand.

*Evidence against:* `visual-check` **failed** (exit 1) on this content load at every checked
desktop size, on both containment and text readability (2.35 px vs a 6 px floor) — the artifact
does not meet archify's *own* bar here. Reaching a clean `validate` required a programmatic lane
router and four rounds. The checker FAILs the `.json` (exit 1, 7 false positives) and the `.html`
(exit 1, 75 findings), and the default corpus would not scan either. Six declared surfaces are
keyed to `*.d2`, and **archify has no d2 input path**.

### Option B — keep archify for exploration only

*Evidence for:* costs nothing and forecloses nothing. The HTML is genuinely a better *explorer*
than a PNG at this density (search and focus solve exactly the "too busy" complaint), and nothing
uncheckable enters the repo. This is what exp-001 recommended (`Recommendations` #5).

*Evidence against:* the artifact is unversioned and unchecked, so it can drift from the `.d2`
silently; and every use pays the hand-routing cost above unless the lane-generator script is kept
too — a second, undeclared maintenance surface.

### Option C — drop archify

*Evidence for:* the `.d2` passes the real checker at this exact content load (exit 0, 9 claims,
0 mismatches, 0 unenumerated). One source, one instrument, no second extractor. The measured d2
weakness — the empty band and the long snaking bundle — is a **layout-engine and decomposition**
problem the plan already prescribes fixes for (per-skill decomposition, Issues 4.x/5.x), not a
format problem.

*Evidence against:* discards the one dimension where archify measurably won — group legibility —
and discards a working interactive explorer. Dropping is irreversible only in attention, not in
code.

**The gate is not resolved by this document.**

## Provenance / caveats

- **measured:** the branch moved under this work — commit `cd4c360` ("plan-067 Epic 2") was
  created by a concurrent process mid-trial and swept an in-progress `architecture.json` into
  history. The files described here are the final ones; the earlier committed `architecture.json`
  is superseded.
- **measured:** `archify` version `2.17.0-dev.1` at `~/.claude/skills/archify`, `doctor` all-ok,
  Node v24.20.0, Chrome from `/Applications/Google Chrome.app`.
- **measured:** exit codes throughout were read from `$?` on unpiped commands. `${PIPESTATUS[@]}`
  is empty under this repo's zsh, so no exit code in this document came through a pipe.
- Sidecars written by `visual-check` (`architecture.visual-check.json`,
  `architecture.visual-check.html`, four `.png` captures) are left in place as evidence.
