# Upstream #50: New skill: markdown-html — render Markdown to standalone HTML via pandoc (CriticMarkup-aware option)

- **Number:** 50
- **Title:** New skill: markdown-html — render Markdown to standalone HTML via pandoc (CriticMarkup-aware option)
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement, type::feature

## Body

## Request

A new skill `markdown-html` that renders a Markdown file to **standalone HTML** via pandoc —
the HTML analogue of the existing `markdown-pdf` (pandoc + xelatex) skill.

## Motivation

`markdown-pdf` covers print output, but there is no first-class path to a shareable, self-contained
HTML rendering of a Markdown note/report. HTML is the natural target for: previewing in a browser,
embedding diagram PNGs, sharing a rendered doc without a PDF toolchain, and matching what an
in-editor live preview shows.

## Proposed shape (mirroring markdown-pdf)

- Invocation: `/markdown-html <file.md>` → `<file>.html`.
- pandoc `--standalone --to=html5`, `--embed-resources` (or `--self-contained`) so images/CSS inline
  into one portable file.
- Relative image paths (`![](diagrams/x.png)`) resolved against the source file's directory, same
  as markdown-pdf.
- A broad-coverage default stylesheet (readable margins, sane fonts, blue links) so output looks
  finished, not bare pandoc.
- Math via MathJax/KaTeX; fenced diagram handling consistent with the project's conventions.

## CriticMarkup-aware option (ties the trio together)

Because HTML is where CriticMarkup *should* render (track-changes view), `markdown-html` is the
natural home for an opt-in CriticMarkup-rendering mode:

- A reusable pandoc Lua filter that renders `` `{++…++}` `` / `` `{--…--}` `` / `` `{~~…~>…~~}` `` /
  `` `{==…==}` `` / `` `{>>…<<}` `` into styled `<ins>`/`<del>`/`<mark>`/`<span>` (classes
  `cm-add`/`cm-del`/`cm-hl`/`cm-comment`), with `~~strikeout~~` disabled at the reader so
  substitutions survive, and inline/fenced code protected.
- `dixson3/emacs.d` plan-004 is building exactly this filter for an emacs `markdown-xwidget`
  preview; the validated approach (an `Inlines`-level filter, `--from=gfm-strikeout`) could be
  lifted into this skill as a shared component so the editor preview and `markdown-html` agree.
- Default OFF (literal pass-through); `--criticmarkup` (or a frontmatter flag) turns rendering on.

## Companion issues

- `markdown-lint`: flag un-escaped markup-like constructs in prose (so docs that *describe* markup
  don't accidentally render).
- `markdown-pdf`: document/advise on the same un-escaped-markup rendering hazard.

