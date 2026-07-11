# Upstream #48: markdown-lint: flag un-escaped inline markup constructs (CriticMarkup et al.) in prose

- **Number:** 48
- **Title:** markdown-lint: flag un-escaped inline markup constructs (CriticMarkup et al.) in prose
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement, type::feature, priority::medium

## Body

## Problem

When a markdown document *describes* inline markup syntax — CriticMarkup (`` `{++added++}` ``,
`` `{--removed--}` ``, `` `{~~old~>new~~}` ``, `` `{==highlight==}` ``, `` `{>>comment<<}` ``) or
similar constructs that a downstream pipeline renders — the author must wrap each literal in a
backtick code span. If they don't, the example renders as *actual* markup when the doc is later
fed through a rendering pipeline:

- the `markdown-pdf` skill (pandoc → xelatex),
- a future `markdown-html` skill (see companion request),
- editor live-preview pipelines (e.g. an emacs `markdown-xwidget` pandoc filter).

Worse, `` `{~~…~~}` `` written un-escaped additionally collides with pandoc/GFM `~~strikeout~~`,
so even pandoc invocations with no CriticMarkup support silently strike the text.

This is a real authoring hazard: prose that enumerates markup is exactly the prose most likely
to contain un-escaped markup.

## Proposed enhancement

Add a `markdown-lint` rule (new `MLxxx`) that flags **un-escaped, markup-like inline constructs
in running prose** and recommends wrapping them in a backtick code span.

### Detection heuristic (authoring-time subset candidate)

- Match a small registry of "render-significant" delimiter pairs on a single line, outside any
  code span / fenced block:
  - CriticMarkup: `{++…++}`, `{--…--}`, `{~~…~>…~~}`, `{==…==}`, `{>>…<<}`
  - (extensible registry — the rule should make the delimiter set configurable so other markup
    families can be added)
- Report only occurrences **not** already inside an inline code span (`` `…` ``) or fenced/indented
  code block — those are the safe, intended form.
- Fix suggestion: wrap the matched run in backticks.

### Notes

- This is distinct from the existing GFM-validity rules; it is about *un-rendered example fidelity*,
  not link/table validity. It is a strong candidate for the on-edit authoring subset.
- False-positive control: only fire on the explicit delimiter registry (don't try to detect
  arbitrary "markup-looking" text), and always exempt code spans/blocks.

## Acceptance

- A doc line containing a bare `{++added++}` (outside code) is flagged with a fix suggestion.
- The same construct inside `` `{++added++}` `` or a fenced block is **not** flagged.
- The delimiter registry is documented and extensible.

## Context

Surfaced while authoring an emacs-config plan (`dixson3/emacs.d`, plan-004) that builds a
CriticMarkup-rendering pandoc preview filter; the plan doc itself had to backtick every example
so it wouldn't render when previewed through the very pipeline it describes. Companion issues:
a `markdown-pdf` rendering-hazard note and a new `markdown-html` skill request.

