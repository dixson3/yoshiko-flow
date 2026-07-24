`yf-markdown-pdf` renders a Markdown file to PDF through a **pandoc + xelatex**
pipeline tuned for two things the LaTeX defaults get wrong: Unicode glyph coverage
(so `→`, `≤`, `≈` and similar characters render) and relative image paths resolved
against the source file's directory. It renders; it never lints or rewrites the
source. Its sibling [`yf-markdown-html`](/skills/yf-markdown-html/) is the same
idea for self-contained HTML.

## When it fires

Invoke `/yf-markdown-pdf` when you want a PDF from a `.md` file:

- "export this report to PDF";
- "make a PDF of this note";
- rendering one or many `.md` files to PDF in a batch.

Skip it for HTML output ([`yf-markdown-html`](/skills/yf-markdown-html/)), for
slide decks, and for linting the source
([`yf-markdown-lint`](/skills/yf-markdown-lint/)). By default the PDF lands at
`<input>.pdf` beside the source; `-o OUT.pdf` overrides the path for a single
input, and arguments after a literal `--` pass through to pandoc verbatim.

## Renderable fences

By default md2pdf **renders** the source inside certain fenced blocks instead of
showing it verbatim, so a diagram or table can live inline in the Markdown and
still produce a real figure or table in the PDF:

| Fence | Rendered as | Tool |
| :--- | :--- | :--- |
| ` ```d2 ` | a vector diagram embedded as a PDF figure | `d2` |
| ` ```csv ` | a native LaTeX table | pandoc (no extra tool) |

The renderable-fence set is the shared `_shared/renderable_fences.py` registry —
the same source of truth [`yf-markdown-lint`](/skills/yf-markdown-lint/) uses to
compile-check a d2 fence (ML009), so the render and the check cannot drift apart.
Three properties define the behavior:

- **d2 embeds as PDF, not SVG.** xelatex cannot use inline SVG, so md2pdf renders
  the diagram to a vector PDF and embeds that — sharper and smaller than a PNG.
- **It degrades gracefully.** If `d2` is absent or a block fails to compile, that
  fence is left as a verbatim code listing and the build still exits 0. The same
  holds for malformed CSV.
- **No temp leak.** Rendered d2 PDFs go in one run-scoped temp dir that md2pdf
  reaps after pandoc finishes, so nothing accumulates across renders.

Pass `--no-render-fences` to keep the fences verbatim — the right choice when you
are *documenting* d2 or CSV syntax itself.

## Figure captions

md2pdf honors the two-field image convention it shares with
[`yf-markdown-lint`](/skills/yf-markdown-lint/): in `![alt](path "title")` the
**alt** text is the accessibility description and the **title** is the print
caption. A default-on filter routes a non-empty title to the figure caption; an
image with no title keeps pandoc's default alt-derived caption. Only an image that
becomes a figure — alone in its paragraph — gets a caption; an inline image is
left untouched.

## Fonts and glyph coverage

Font handling is **platform-aware**, because naming a font that does not exist
makes xelatex hard-fail:

- **On macOS** the defaults are `Arial Unicode MS` for the main font and `Menlo`
  for mono, which cover common glyphs (`→ ≤ ≈`) the LaTeX defaults miss.
- **Off macOS** the script forces no font. xelatex falls back to Latin Modern and
  merely *warns* on a missing glyph while the build still succeeds. For full
  coverage on Linux, pass `--mainfont "DejaVu Sans"` or another Unicode-complete
  font.

The distinction is load-bearing: a missing **font** fails the build; a missing
**glyph** (font present, glyph absent) only warns.

Color emoji are a special case. xelatex cannot use color-bitmap fonts, so a
codepoint like `✅` renders as nothing. On macOS a `glyph-fallback.tex` header
remaps `✅` onto the monochrome `✔` for a legible, zero-warning check-mark. Off
macOS the header is skipped and the glyph degrades to a warning — never a hard
fail. This is a monochrome substitute, not color parity.

Referenced 16-bit or alpha-channel PNGs are auto-flattened as well: they embed but
render blank under xelatex, so the script writes an 8-bit RGB copy into a temp dir
and uses that, never modifying the source. Disable it with `--no-normalize-images`.

## Wide tables

Wide, many-column tables are the main PDF rendering pain point, so md2pdf adds
PDF-specific levers that are invisible in Obsidian and on GitHub:

- **`--table-font SIZE`** (default `footnotesize`) shrinks all table text so dense
  tables fit without cells bleeding into neighbors. `normalsize` means no shrink.
- **Dash-width tuning.** pandoc sets each column's PDF width from the length of its
  separator segment, so more dashes on a text-heavy column widens it. It engages
  once the separator row is wider than `--columns` (default 72); lower `--columns`
  to tune narrower tables.
- **`--landscape-cols N`** rotates any table with more than N columns onto a
  landscape page (`0` = off), via a render-time filter rather than
  `\begin{landscape}` in the source.

The portable pipe-table authoring conventions — alignment markers, `<br>` in-cell
breaks, pipe-only tables, splitting wide ones — live in
[`yf-markdown-lint`](/skills/yf-markdown-lint/); those render identically in
pandoc, Obsidian, and on GitHub.

## Markup hazards

Prose that *describes* inline markup can be *interpreted* as markup by pandoc. The
sharpest case is strikeout: `~~text~~` renders struck-through even when you meant
the literal tildes, so a sentence mentioning a `~~…~~` construct silently loses
its tildes. The same trap applies to CriticMarkup constructs, which pandoc does
not implement. To keep such text literal, code-span or backslash-escape the
delimiters in the source.

By default md2pdf runs the sibling `yf-markdown-lint` **ML010** rule over the
source before rendering and prints a warning for any hit — then still produces the
PDF. The advisory is best-effort: if the linter is unavailable it skips silently
and never blocks the render. Disable it with `--no-lint-advisory`.

## Requirements

`pandoc` and `xelatex` (from a LaTeX distribution) on PATH. The script checks both
and exits with a clear message if either is missing. No `init` step, no config, no
companion rule.
