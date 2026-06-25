# Upstream #33: Embed d2 source as a markdown fenced block (yf-diagram-authoring / yf-markdown-pdf / yf-markdown-lint)

- **Number:** 33
- **Title:** Embed d2 source as a markdown fenced block (yf-diagram-authoring / yf-markdown-pdf / yf-markdown-lint)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

Support **embedding d2 diagram source as a fenced ` ```d2 ` block directly in
markdown files**, as a first-class alternative to the current model of generating a
standalone diagram image and linking it. Three skills participate and should agree on
the convention: `yf-diagram-authoring` (d2), `yf-markdown-pdf`, and `yf-markdown-lint`.

## Motivation

Inline ` ```d2 ` fences let the diagram source live *with* the prose — single-source,
diffable, no separate `.png`/`.d2` files to keep in sync — and render in tools that
understand the fence. Concretely, a markdown preview can render the block inline via a
pandoc Lua filter that shells out to the `d2` CLI (`d2 - -`, stdin→stdout SVG); this is
already working in my Emacs config's `markdown-xwidget` preview. The same
filter-at-render-time approach generalizes to PDF export.

This is **additive** — standalone image generation stays the default for cases that
need a committed artifact (e.g. GitHub rendering, which does not execute d2). The ask
is to also support the embedded-source path and make the skills consistent about it.

## Requested changes

### `yf-diagram-authoring` (d2)
- Add an **embed mode**: emit the diagram as a ` ```d2 ` fenced block inserted into a
  target markdown file, instead of (or in addition to) writing `.d2` + rendering
  `.png`.
- Document the trade-off: embedded source renders only where a d2-aware renderer runs
  (preview, the PDF pipeline below); standalone PNG renders everywhere (GitHub, plain
  viewers). Keep standalone as the default; embed is opt-in.
- Consider a "lift" helper: extract an existing inline ` ```d2 ` block to a standalone
  `.d2`/`.png` pair, and the inverse.

### `yf-markdown-pdf`
- Teach the pandoc + xelatex pipeline to render ` ```d2 ` blocks: add a pandoc Lua
  filter (`CodeBlock` by class `d2`) that runs the `d2` CLI and inlines the result
  (SVG → or a rasterized image if xelatex needs PNG/PDF) so the PDF shows the diagram,
  not raw d2 code.
- Degrade gracefully when `d2` is not on PATH: leave the block as a code listing
  rather than aborting the render. (Reference implementation: the registry-style filter
  in my emacs.d at `pandoc/markdown-blocks.lua`.)
- Same hook point is the natural home for other renderable fences (csv→table, etc.).

### `yf-markdown-lint`
- Recognize ` ```d2 ` (and other known "renderable" fences) as **valid** — do not flag
  the block or its contents as malformed markdown.
- Optional: validate that the embedded d2 source parses (`d2` has a validate/compile
  path), surfacing a lint error on broken diagram source — analogous to how it already
  checks GFM validity.

## Cross-skill consistency

Define one shared convention for which fence info strings are "renderable" and how each
skill treats them, so authoring (`yf-diagram-authoring`), rendering (`yf-markdown-pdf`),
and validation (`yf-markdown-lint`) do not drift. A small shared list/spec of
renderable fence classes + their tools would be the natural anchor.

## Reference

Working pandoc Lua filter (d2 + csv, registry pattern, self-degrading on missing tool)
and wiring notes live in my Emacs config: `pandoc/markdown-blocks.lua` and
`pandoc/README.md` under `_dotfiles/emacs.d`. Happy to upstream the filter as a starting
point for the PDF pipeline.

