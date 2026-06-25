# Plan: Renderable fenced blocks: d2/csv embed convention across yf-diagram-authoring/yf-markdown-pdf/yf-markdown-lint (#33, #34) + bdresearch record-epic helper (#37)

**ID:** plan-017-james-dixson-9ac898
**Author:** james-dixson
**Created:** 2026-06-24
**Status:** reconciling
**Epic:** beads-skills-mol-806
**Phase log:**
- 2026-06-24 scoping: initial scope captured
- 2026-06-24 investigating: scope decisions locked; 2 experiments identified
- 2026-06-24 drafting: synthesizing plan
- 2026-06-24 review: plan v1 presented
- 2026-06-24 revised: red-team pass-1 concerns resolved (plan v2)
- 2026-06-24 approved: operator approved
- 2026-06-24 intake: epic beads-skills-mol-806 poured
- 2026-06-24 executing: start gate resolved
- 2026-06-24 reconciling: all execution beads closed; entering Phase 6

## Objective
Renderable fenced blocks: d2/csv embed convention across yf-diagram-authoring/yf-markdown-pdf/yf-markdown-lint (#33, #34) + bdresearch record-epic helper (#37)

## Motivation
Three upstream issues converge on one idea: let diagram (`d2`) and tabular (`csv`)
source live **inline** in markdown as fenced blocks, rendered at preview/PDF time,
as a first-class alternative to the current standalone-image model. The reference
pandoc Lua filter already works in the operator's emacs.d `markdown-xwidget` preview
(`pandoc/markdown-blocks.lua`); `yf-markdown-pdf` renders none of those fences and so
diverges from that live preview. Three skills must agree on which fence info-strings
are "renderable" or they will drift: `yf-diagram-authoring` (authors the blocks),
`yf-markdown-pdf` (renders them to PDF), and `yf-markdown-lint` (must treat them as
valid). A fourth, unrelated issue (#37) rides along: the `yf-research` durable
`epic:` pointer in `plan.yaml` is written by Phase-3 prose, not an idempotent helper
like `yf-plan`'s `plan_manager.py record-epic` — a robustness gap worth closing.

## Scope Decisions (operator-confirmed, 2026-06-24)
1. **Shared convention home:** a shared `_shared/renderable_fences.py` module is the
   single source of truth for the renderable fence-class registry (`d2`, `csv`, …).
   `markdown_lint.py` imports it. The pandoc **Lua** filter cannot import Python, so it
   mirrors the list — the mirror is a **declared drift edge** (DRIFT-CHECK / a test
   asserts the Lua filter's classes match the registry). Couples to the existing
   `_shared/` dir; the `_shared` vendoring engine (#41) is **not** a prerequisite —
   investigation E2 confirms the current consumption mechanism.
2. **yf-diagram-authoring scope:** deliver **embed + lift** (bidirectional). `embed`
   inserts a ```` ```d2 ```` fence into a target markdown file; `lift` extracts an inline
   ```` ```d2 ```` block to a standalone `.d2`/`.png` pair; the inverse re-inlines.
3. **Glyph coverage (#34):** add an optional **monochrome symbol fallback font**
   (Symbola / Noto Sans Symbols 2) via fontspec fallback + a documented install recipe.
   Symbols/checkmarks render as B&W glyphs; **color emoji remain unsupported** under
   xelatex (documented accepted limitation).

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|
| #33 | Embed d2 source as a markdown fenced block (cross-skill convention) | include | Anchors the shared registry + embed/lift + lint recognition | Epics A, C, D |
| #34 | yf-markdown-pdf near-parity with markdown-xwidget render (d2, csv, glyphs) | include | d2/csv fence rendering in PDF + monochrome glyph fallback | Epic B |
| #37 | bdresearch optional record-epic helper for idempotent plan.yaml epic: pointer | include | Independent; touches research spec REQ-CLI-006 (operator-approved) | Epic E |

## Investigation Findings

### E1 — d2/csv/glyph PDF path (`findings/exp-001-d2-csv-glyph-pdf.md`)
All four sub-questions validated end-to-end against pandoc 3.10 + xelatex + d2 0.7.1:
- **d2 → PDF embed works.** A Lua `CodeBlock` renderer shells `d2 <in> <out>.pdf` and
  returns `pandoc.Para({pandoc.Image({}, abspath)})` (NOT `RawBlock("html", svg)`, which
  only works for HTML). **d2→PDF beats d2→PNG** (vector, sharper, smaller). The Image src
  **must be an absolute temp path** (`$TMPDIR`) — pandoc resolves absolute paths
  independent of `--resource-path`.
- **csv → table works** via `pandoc.read(text, "csv").blocks` — native LaTeX table, no
  tool/package; identical to the emacs.d reference filter.
- **Graceful degradation works** — a failing `d2` under `pcall` returns `nil`, the fence
  stays a verbatim code listing, build exits 0.
- **Glyph fallback resolved cheaply.** ✔ U+2714 / ✖ U+2716 already render under the
  existing `-V mainfont="Arial Unicode MS"`. Only ✅ U+2705 fails (color emoji; xelatex
  can't use color-bitmap fonts). Fix needs **no font install**: a `-H` header
  `\usepackage{newunicodechar}\newunicodechar{✅}{\symbol{"2714}}` (newunicodechar.sty is
  in MacTeX). Portable fallback if Arial Unicode MS is absent: `brew install --cask font-symbola`.

### E2 — `_shared/` consumption (`findings/exp-002-shared-consumption.md`)
- `_shared/` is consumed at **authoring time via committed vendored copies**, NOT runtime
  import. `sync.py` regenerates marker-fenced **regions** (and whole-file copies) listed in
  `REGION_ASSETS`/`WHOLE_FILE_ASSETS`; `sync.py --check` is the byte-level guard.
- A new `_shared/renderable_fences.py` (region asset) is the registry SoT;
  `markdown_lint.py` carries a vendored marker-fenced region. **No install/`yf`/Rust
  changes** — `_shared/` sits outside `skills/`, the vendored copy ships inline.
- **Lua-mirror:** generate the filter's fence-class list from the Python registry via a new
  `sync.py` emitter (option c), backstopped by a DRIFT-CHECK `field-set-equal` edge
  (option b) for on-edit enforcement. Mirrors the `json-extract` precedent.

## Approach

One plan, **five epics** — four for the renderable-fence feature (#33/#34) plus one
independent helper (#37). The shared registry is built first so every other surface
references a single source of truth.

- **Registry-first.** `_shared/renderable_fences.py` is the canonical `{class → tool,
  output-kind, fallback}` registry. `markdown_lint.py` vendors it (region asset); the
  pandoc Lua filter's class list is **generated** from it (`sync.py` emitter); a
  DRIFT-CHECK `field-set-equal` edge enforces the Lua mirror on-edit.
- **PDF rendering** adds one registry-pattern `blocks.lua` (`--lua-filter`: d2→PDF Image,
  csv→native table, pcall-degrade) plus a `glyph-fallback.tex` (`-H`), wired into
  `md2pdf.py` on the default path. The d2→SVG→`RawBlock("html")` reference shape is
  **adapted** to d2→PDF→`Image` for xelatex.
- **Diagram authoring** gains bidirectional `embed` / `lift` / `inline` subcommands so a
  ```` ```d2 ```` fence and a standalone `.d2`/`.png` pair are interconvertible.
- **#37** ports `yf-plan`'s `plan_manager.py record-epic` into `research_manager.py`
  (adapting `plan.md` `**Epic:**` → `plan.yaml` `epic:`), updates the Phase-3 prose to call
  it, and realigns spec REQ-CLI-006 (which is already stale — names a removed `check`
  subcommand).

No capability gates required: d2 / pandoc / xelatex / newunicodechar are all present, and
the glyph fix needs no font install.

## Epics

### Epic A: Shared renderable-fence registry + lint recognition (#33)
- A.1: Create `_shared/renderable_fences.py` — canonical registry of renderable fence
  classes (`d2`, `csv`) with metadata (tool, output kind, degrade-to-code contract).
- A.2: Vendor the registry into `markdown_lint.py` as a marker-fenced region; register the
  `RegionAsset` in `_shared/sync.py` and extend `_shared/test_sync.py`.
  - depends-on: A.1
- A.3: Add a new **optional** ML rule to `markdown_lint.py` that validates embedded `d2`
  source compiles (`d2` validate/compile path), degrading cleanly when `d2` is absent. This
  is the only genuinely new lint behavior — `markdown_lint.py` already `continue`s over all
  fenced interiors, so d2/csv blocks are *already* valid/invisible to the linter; no change
  is needed to make them "valid." The new rule **consumes the vendored registry** (A.2) to
  know which fence classes are renderable-and-compile-checkable, so the vendored region is
  referenced by live code, not dead weight. Keep the rule out of the authoring-time subset
  (it shells `d2`). Update SKILL.md/SPEC.md rule list + authoring subset note.
  - depends-on: A.2

### Epic B: yf-markdown-pdf d2/csv rendering + glyph coverage (#34)
- B.1: Add `blocks.lua` (registry-pattern pandoc filter): `d2` → `d2 <in> <out>.pdf` →
  absolute-path `pandoc.Image`; `csv` → `pandoc.read(text,"csv").blocks`; both `pcall`-
  degrade to a code listing. **Temp-file discipline (red-team C3):** use
  `pandoc.system.with_temporary_directory` (pandoc 3.x) for per-run temp artifacts and an
  **argument-vector** exec (`pandoc.pipe` / `os.execute` only with shell-escaped args) — no
  raw string-concat of paths into a shell. The class list is hand-authored here from the
  registry; C.1 converts it to a generated region (see C.1 co-landing note).
  - depends-on: A.1 (filter class list sourced from the registry)
- B.2: Add `glyph-fallback.tex` and wire it (`-H`) + `blocks.lua` (`--lua-filter`) into
  `md2pdf.py`'s default pandoc invocation; reap temp artifacts deterministically via the
  script's existing `finally` path (mirroring the header-tempfile pattern already in
  `md2pdf.py`). Add a `--no-render-fences` opt-out (red-team M2) so a user documenting d2
  itself can keep ```` ```d2 ````/```` ```csv ```` verbatim; rendering is default-on.
  - depends-on: B.1
- B.3: Tests + docs. A fixture `.md` exercising d2 + csv + ✅ renders to a PDF with no raw
  source, plus a **no-temp-leak assertion** (temp dir empty after N renders, red-team C3).
  **Glyph scope is macOS+Arial-Unicode-MS best-effort** (red-team C4): on macOS the
  `\newunicodechar{✅}{\symbol{"2714}}` remap yields zero missing-character warnings;
  off-macOS (mainfont forced to `None`) the feature **degrades to xelatex warnings, never a
  hard fail** — B.3 asserts that graceful-degradation path. Update SKILL.md/SPEC.md/README.md
  (document the d2→PDF-not-SVG divergence, the glyph recipe + its macOS-specificity, the
  `--no-render-fences` flag, and `brew install --cask font-symbola` as the portable fallback).
  - depends-on: B.2

### Epic C: Lua-mirror sync + drift enforcement (#33 consistency)
- C.1: Extend `_shared/sync.py` with a Python→Lua emitter that generates the fence-class
  list into a marker-fenced region in `blocks.lua` from `renderable_fences.py`; extend
  `test_sync.py`; run `sync.py --check`. **Co-landing (red-team C5):** C.1 must land in the
  same change-set as B.1 — `blocks.lua` is never committed with an unguarded hand-maintained
  class list. The Reconcile auto-gate enforces `sync.py --check` green (see Gates).
  - depends-on: A.1, B.1
- C.2: Add DRIFT-CHECK.md nodes/edges/§6 globs — a `value-equal` canonical→`markdown_lint.py`
  copy edge and a `field-set-equal` registry↔Lua-mirror edge, mirroring the `json-extract`
  precedent.
  - depends-on: A.2, C.1

### Epic D: yf-diagram-authoring embed + lift (#33)
- D.1: Add `embed` subcommand to `render.py` — insert a ```` ```d2 ```` fence into a target
  markdown file; document the standalone-PNG-vs-embed trade-off.
  - depends-on: A.1
- D.2: Add `lift` (inline ```` ```d2 ```` block → standalone `.d2` + rendered `.png`) and
  `inline` (the inverse) subcommands; tests + SKILL.md/SPEC.md/README.md updates.
  - depends-on: D.1

### Epic E: yf-research record-epic helper (#37)
- E.1: Add a `record-epic` subcommand to `research_manager.py`, ported from
  `plan_manager.py` (idempotent; `plan.md` `**Epic:**` header + phase-log line adapted to
  `plan.yaml` `epic:` line + metadata fallback).
- E.2: Update the `yf-research` SKILL.md Phase-3 prose to call `record-epic`; add a test.
  **Full CLI-spec realignment (red-team C1):** audit **all** of REQ-CLI-006/007/008 against
  the live click CLI (which currently exposes only `json-get`). Realign REQ-CLI-006 to the
  actual set (`json-get`, `record-epic`) **and** repoint/descope REQ-CLI-007's stale
  `check --json-output` (that subcommand moved to the `yf preflight` kernel in plan-010) so
  the spec is internally consistent and the existing `e-skillspec-skillmd` drift edge stays
  green. Operator approval (the #37 "operator-approved" flag) is scoped to this **whole CLI
  spec section** edit, not REQ-CLI-006 alone.
  - depends-on: E.1

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

_No capability gates: all runtime tools (d2, pandoc, xelatex, newunicodechar.sty) are
present; the glyph fix requires no font install._

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed **and** integrity checks green)
- Condition (red-team C5/Gate): `uv run _shared/sync.py --check` exits 0 **and** the new
  DRIFT-CHECK edges (registry↔`markdown_lint.py` copy; registry↔Lua-mirror `field-set-equal`)
  pass — the generated-not-hand-maintained invariant must hold before reconcile.
- Test: `uv run _shared/sync.py --check`
- Blocks: reconcile step
- Note: per `AGENTS.md`, upstream tracking is **coarse** — at land-the-plane, update the
  three resolved issues (#33, #34, #37) and the single coarse plan-tracking issue; do NOT
  push granular sub-beads.

## Risks & Mitigations
- **Lua-mirror drift** (registry vs filter list diverge) → generated from the registry
  (C.1) + on-edit drift edge (C.2); not hand-maintained.
- **REQ-CLI-006 spec change (#37)** touches a deliberately narrow spec — operator already
  approved the include disposition; the change realigns an already-stale requirement
  (names a removed `check` subcommand), lowering risk. Surfaced explicitly at review.
- **Color-emoji parity gap** — ✅ and friends can't render as color under xelatex. Accepted
  and documented limitation; monochrome substitution (`\newunicodechar`) is the contract,
  not full emoji. **Glyph parity is also platform-bound** (red-team C4): the remap relies on
  `Arial Unicode MS` (macOS-only mainfont). Off-macOS it degrades to xelatex warnings, never
  a hard fail — documented as macOS-best-effort, asserted in B.3.
- **Temp-file lifecycle / exec surface in `blocks.lua`** (red-team C3) — d2 PDFs use absolute
  `$TMPDIR` paths (E1); B.1 uses `pandoc.system.with_temporary_directory` + arg-vector exec
  (no shell string-concat) and B.2 reaps via `finally`; B.3 asserts no temp leak.
- **Transient Lua-mirror drift inside execution** (red-team C5) — between B.1 (hand-authored
  list) and C.1 (generated region) the Lua list is an unguarded copy; mitigated by requiring
  C.1 to co-land with B.1 and gating Reconcile on `sync.py --check`.
- **Spec-section consistency for #37** (red-team C1) — realigning only REQ-CLI-006 would leave
  REQ-CLI-007's removed `check` stale; E.2 audits the whole CLI spec section under one
  operator-approved edit.
- **No `yf`/Rust/install changes needed** (E2); if that proves wrong during execution it
  becomes a discovered-work bead, not silent scope creep.

## Success Criteria
- A fixture `.md` with a ```` ```d2 ````, a ```` ```csv ````, and a ✅ renders via
  `md2pdf.py` to a PDF showing a real diagram, a real table, and (on macOS) a visible
  checkmark with zero missing-character warnings and no raw fenced source. Off-macOS the
  same build degrades to xelatex warnings without a hard fail. Temp dir is empty after the
  run (no leak). `--no-render-fences` keeps the fences verbatim.
- `markdown_lint.py` gains an optional rule that flags broken embedded d2 source (and is
  excluded from the authoring-time subset); the vendored registry region is referenced by
  that rule; `_shared/sync.py --check` is green.
- `render.py embed`/`lift`/`inline` round-trip a d2 fence ↔ standalone `.d2`/`.png` pair.
- `research_manager.py record-epic` is idempotent and writes the `epic:` pointer into
  `plan.yaml`; REQ-CLI-006/007/008 all match the implemented subcommand set (no stale
  `check`).
- DRIFT-CHECK edges for the registry↔copy and registry↔Lua-mirror pass, **and** the existing
  CLI↔SKILL drift edges stay green for the new `record-epic`/`embed`/`lift`/`inline`
  subcommands (red-team M1).
- Upstream #33, #34, #37 reconciled; one coarse plan-tracking issue updated.
