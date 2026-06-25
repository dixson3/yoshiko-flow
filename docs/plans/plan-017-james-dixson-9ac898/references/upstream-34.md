# Upstream #34: yf-markdown-pdf: near-parity with the markdown-xwidget render (d2, csv, glyph coverage)

- **Number:** 34
- **Title:** yf-markdown-pdf: near-parity with the markdown-xwidget render (d2, csv, glyph coverage)
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement, type::feature, priority::medium

## Body

## Goal

Bring the `yf-markdown-pdf` (pandoc + xelatex) output to **near-parity with the
`markdown-xwidget` live-preview render** used in `dixson3/emacs.d`. The xwidget preview
runs `pandoc --from=gfm --to=html5 --mathjax --lua-filter=pandoc/markdown-blocks.lua`,
which renders fenced `d2`/`csv` blocks and YAML frontmatter; `yf-markdown-pdf` is plain
`pandoc --pdf-engine=xelatex` and renders none of those.

**Primary accepted exception:** YAML frontmatter rendering is **out of scope** — it is
fine for the PDF to consume the `---` block as document metadata and not print a
frontmatter card. Everything else below is a parity gap worth closing.

## Reproduction

Rendered `dixson3/emacs.d:docs/markdown-xwidget-demo/demo.md` (a feature-exercise doc:
frontmatter, tables, inline image, inline+display math, a `d2` diagram, a `csv` table,
Python syntax highlighting) with:

```bash
uv run ~/.claude/skills/yf-markdown-pdf/scripts/md2pdf.py demo.md
```

Build succeeded (79 KB PDF) but diverged from the xwidget render in the ways below.

## Deficiencies (vs. the xwidget render)

### 1. Fenced `d2` blocks render as plain code, not a diagram
The xwidget filter shells `d2 - -` and inlines the SVG. The PDF shows the raw d2 source
as a highlighted code block. **Want:** render `d2` fences to an image embedded in the PDF
(e.g. `d2` → SVG/PDF/PNG → `\includegraphics`), degrading to a code block when `d2` is
absent (same graceful-degradation contract as the lua filter).

### 2. Fenced `csv` blocks render as plain code, not a table
The xwidget filter uses pandoc's CSV reader to emit a native table. The PDF shows raw CSV
text. **Want:** convert `csv` fences to a real table in the PDF.

### 3. Glyph coverage: emoji/symbols silently dropped
6 × `Missing character: There is no ✅ (U+2705) in font Arial Unicode MS` — the status
table's checkmarks render blank. WebKit shows them fine. **Want:** either a fallback font
covering common symbol/emoji codepoints, or a documented `--mainfont`/fallback recipe so
symbol cells aren't silently empty.

## Out of scope (accepted divergence)

- **YAML frontmatter** — intentionally not rendered as a card in the PDF (metadata only).

## Notes

- Math (inline `$…$` + display `$$…$$`), tables, the relative-path inline image, and
  syntax highlighting already render in the PDF — those are at parity.
- The xwidget-side renderers live in `dixson3/emacs.d:pandoc/markdown-blocks.lua` and are
  a useful reference for the d2/csv behavior (incl. the pcall-degrade-to-code-block
  pattern for a missing external tool).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
