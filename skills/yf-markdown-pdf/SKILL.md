---
name: yf-markdown-pdf
skill-group: markdown
depends-on-tool: [uv, pandoc, xelatex]
depends-on-skill: []
description: >
  Render a Markdown file to PDF via the pandoc + xelatex pipeline — xelatex
  engine, a broad-coverage Unicode font (so →, ≤, ≈ and similar glyphs render),
  1in margins, blue links, and relative image paths (`![](diagrams/x.png)`)
  resolved against the source file's directory.
  TRIGGER when: /yf-markdown-pdf invoked; the user wants a PDF created/generated
  from a `.md` file; "export this report to PDF", "make a PDF of this note".
  SKIP for: slide decks; HTML or non-PDF output; linting markdown
  (use `yf-markdown-lint`).
---

# yf-markdown-pdf

Convert Markdown to PDF with pandoc + xelatex. A pandoc + xelatex pipeline tuned
for Unicode-glyph coverage and relative image paths.

## Invocation

```bash
uv run .claude/skills/yf-markdown-pdf/scripts/md2pdf.py <input.md>
```

Output defaults to `<input>.pdf` beside the source. Multiple inputs each render
to `<name>.pdf`. `-o OUT.pdf` overrides the path (single input only).

```bash
# explicit output
uv run .claude/skills/yf-markdown-pdf/scripts/md2pdf.py report.md -o /tmp/report.pdf
# batch
uv run .claude/skills/yf-markdown-pdf/scripts/md2pdf.py a.md b.md
# override the main font / margin; pass extra pandoc flags after `--`
uv run .claude/skills/yf-markdown-pdf/scripts/md2pdf.py r.md --mainfont "STIX Two Text" -- --toc
# no table shrink; rotate any table with >8 columns to landscape
uv run .claude/skills/yf-markdown-pdf/scripts/md2pdf.py r.md --table-font normalsize --landscape-cols 8
# keep ```d2```/```csv``` fences verbatim instead of rendering them
uv run .claude/skills/yf-markdown-pdf/scripts/md2pdf.py r.md --no-render-fences
```

## Renderable fences (d2, csv)

By default md2pdf **renders** the source inside certain fenced blocks instead of
showing it verbatim, so a diagram or table can live **inline** in the Markdown and
still produce a real figure/table in the PDF (near-parity with the
`markdown-xwidget` preview). The renderable set is the shared
`_shared/renderable_fences.py` registry — the same source of truth
[`yf-markdown-lint`](../yf-markdown-lint/SKILL.md) (ML009) and
[`yf-diagram-authoring`](../yf-diagram-authoring/SKILL.md) (`embed`/`lift`) use, so
the three skills cannot drift.

| Fence | Rendered as | Tool |
|:------|:------------|:-----|
| ` ```d2 ` | a vector diagram embedded as a PDF figure | `d2` |
| ` ```csv ` | a native LaTeX table | pandoc (no extra tool) |

- **d2 → PDF, not SVG.** The `markdown-xwidget` HTML preview embeds d2 as inline
  SVG; under xelatex that does not work, so md2pdf renders `d2 <in> <out>.pdf` and
  embeds the **PDF** (vector — sharper and smaller than a PNG) at an absolute temp
  path. This is a deliberate divergence from the HTML filter, not a bug.
- **Graceful degrade.** If `d2` is absent or a block fails to compile, that fence
  is left as a **verbatim code listing** and the build still exits 0. The same
  holds for malformed csv.
- **No temp leak.** Rendered d2 PDFs go in one run-scoped temp dir that md2pdf
  reaps after pandoc finishes — nothing accumulates across renders.
- **`--no-render-fences`** keeps ` ```d2 ` / ` ```csv ` fences verbatim — use it
  when you are *documenting* d2/csv syntax itself.

## Glyph coverage (color emoji)

xelatex cannot use color-bitmap (emoji) fonts, so a codepoint like ✅ (U+2705)
renders as nothing with a "Missing character" warning. **On macOS** md2pdf includes
a `glyph-fallback.tex` header that remaps ✅ onto the monochrome ✔ (U+2714, which
Arial Unicode MS supplies) via `newunicodechar` — zero missing-character warnings,
a legible check-mark. This is **macOS best-effort**: it relies on `newunicodechar.sty`
(MacTeX) and Arial Unicode MS. **Off macOS** the header is skipped and ✅ degrades to
an xelatex warning — never a hard fail. Color emoji remain unsupported under xelatex
(an accepted, documented limitation); the remap is a monochrome substitute, not
color parity. A portable monochrome-symbol font fallback if Arial Unicode MS is
absent: `brew install --cask font-symbola` (or install Noto Sans Symbols 2) and pass
it via `--mainfont`.

## Pipeline defaults

The script runs `pandoc --pdf-engine=xelatex` with: `geometry:margin=1in`,
`linkcolor=blue`, a platform-aware main/mono font (below), and
`--resource-path=<dir of the source .md>`.

- **Font defaults are platform-aware.** On **macOS** the defaults are
  `mainfont=Arial Unicode MS` / `monofont=Menlo`, which cover common glyphs
  (→ ≤ ≈) the LaTeX default fonts miss. Those fonts do **not** exist on
  Linux/Windows, and naming a missing font makes xelatex **hard-fail**
  (`fontspec: font cannot be found`) — so **off macOS the script forces no font**:
  xelatex falls back to Latin Modern and merely *warns* on missing glyphs (the
  script surfaces those warnings; the build still succeeds). For full glyph
  coverage on Linux, pass `--mainfont` a Unicode-complete font, e.g.
  `--mainfont "DejaVu Sans"`. Distinction: a missing *font* fails the build; a
  missing *glyph* (font present, glyph absent) only warns.
- **Relative images resolve from the source dir** via `--resource-path`. Keep
  referenced images present, or pandoc errors.

## Tables

Wide / many-column tables are the main PDF rendering pain point. PDF-specific
levers:

- `--table-font SIZE` (default `footnotesize`) shrinks all table text so dense
  tables fit without cells bleeding into neighbors. `normalsize` = no shrink.
- **Dash-width tuning.** pandoc sets each column's PDF width from the length of
  its separator segment (`---`, dashes *and* colons), so more dashes on a
  text-heavy column widens it. Only engages once the separator row is wider than
  `--columns` (default 72); lower `--columns` to tune narrower tables. Obsidian
  and GitHub ignore dash counts, so this is invisible there.
- `--landscape-cols N` rotates any table with more than N columns onto a
  landscape page (`0` = off). A render-time Lua filter — no `\begin{landscape}`
  in the source (which would show as literal text in Obsidian/GitHub).

Portable pipe-table authoring — `:` alignment, `<br>` in-cell breaks, pipe-only
(don't switch to grid/multiline), split wide tables — lives in the
[`yf-markdown-lint`](../yf-markdown-lint/SKILL.md) skill; those render identically in
pandoc, Obsidian, and GitHub.

## Requirements

`pandoc` and `xelatex` (a LaTeX distribution) on PATH. The script checks both
and exits with a clear message if either is missing.
