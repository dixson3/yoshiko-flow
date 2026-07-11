# Upstream Issue Triage: Markdown tooling improvements bundle

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #50 — New skill: markdown-html — render Markdown to standalone HTML via pandoc (CriticMarkup-aware option)
Labels: enhancement, type::feature
> ## Request

A new skill `markdown-html` that renders a Markdown file to **standalone HTML** via pandoc —
the HTML analogue of the existing `markdown-pdf` (pandoc + xelatex) skill.

## Motivation

`mar...

**Disposition:**
**Notes:**

## #81 — yf-markdown-lint ML003 folds image "title" into the link target — mis-flags GFM `![alt](path "title")`
Labels: bug
> ## Summary

`yf-markdown-lint` rule **ML003** (broken link/anchor target) does not parse the **optional GFM title** in link/image syntax. It treats the entire `images/x.png "caption"` string — includi...

**Disposition:**
**Notes:**

## #49 — markdown-pdf: un-escaped CriticMarkup / strikeout-colliding constructs render unexpectedly in PDF
Labels: documentation, enhancement
> ## Problem

The `markdown-pdf` skill renders Markdown → PDF via pandoc + xelatex. When the source document
*describes* inline markup syntax without escaping it, the example renders as **actual markup*...

**Disposition:**
**Notes:**

## #48 — markdown-lint: flag un-escaped inline markup constructs (CriticMarkup et al.) in prose
Labels: enhancement, type::feature, priority::medium
> ## Problem

When a markdown document *describes* inline markup syntax — CriticMarkup (`` `{++added++}` ``,
`` `{--removed--}` ``, `` `{~~old~>new~~}` ``, `` `{==highlight==}` ``, `` `{>>comment<<}` ``...

**Disposition:**
**Notes:**

## #46 — markdown-lint + markdown-pdf: support alt-text (a11y) / title (print caption) image convention

> ## Problem

A markdown image has two text fields, and they want to serve two different goals:

- **alt text** (`![...]`) should be a thorough, literal **accessibility description** for screen readers ...

**Disposition:**
**Notes:**
