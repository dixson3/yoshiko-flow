# Upstream #49: markdown-pdf: un-escaped CriticMarkup / strikeout-colliding constructs render unexpectedly in PDF

- **Number:** 49
- **Title:** markdown-pdf: un-escaped CriticMarkup / strikeout-colliding constructs render unexpectedly in PDF
- **URL:** 
- **State:** OPEN
- **Labels:** documentation, enhancement

## Body

## Problem

The `markdown-pdf` skill renders Markdown → PDF via pandoc + xelatex. When the source document
*describes* inline markup syntax without escaping it, the example renders as **actual markup** in
the PDF instead of as literal text:

- `` `{~~old~>new~~}` `` written un-escaped → pandoc/GFM `~~strikeout~~` strikes `old~>new` (this
  fires even though pandoc has no CriticMarkup support — `~~` alone is strikeout).
- Other CriticMarkup constructs (`` `{++…++}` ``, `` `{--…--}` ``, `` `{==…==}` ``, `` `{>>…<<}` ``)
  pass through literally under plain pandoc *today*, but a CriticMarkup-aware variant (or a future
  `markdown-html` skill sharing a filter) would render them — so relying on "pandoc ignores it" is
  fragile.

A document that enumerates markup syntax is precisely the document most prone to this.

## Proposed handling

This is primarily an **authoring-discipline** problem whose mechanical guard belongs in
`markdown-lint` (companion issue: a rule that flags un-escaped markup-like constructs outside code
spans). For `markdown-pdf` specifically:

1. **Document the gotcha** in the skill's `SKILL.md`: when rendering docs that describe markup,
   literals must be backtick-escaped, and unescaped `~~…~~` will strike text even without
   CriticMarkup support.
2. **Optional pre-render advisory:** before rendering, run the `markdown-lint` markup-escape rule
   (companion issue) over the source and surface any hit as a non-blocking warning ("line N: bare
   `{~~…~~}` will render as strikethrough — escape with backticks?"). Keep it advisory, not
   fail-closed — the rendering itself is still valid.

## Acceptance

- `SKILL.md` documents the un-escaped-markup rendering hazard (with the `~~` strikeout case called
  out explicitly).
- (If the advisory is adopted) rendering a source with a bare `{~~old~>new~~}` emits a warning
  pointing at the line, but still produces the PDF.

## Context

Surfaced while authoring `dixson3/emacs.d` plan-004 (a CriticMarkup-rendering pandoc preview
filter). Companion issues: a `markdown-lint` escape rule and a new `markdown-html` skill request.

