---
name: yf-markdown-html
skill-group: markdown
depends-on-tool: [uv, pandoc]
depends-on-skill: []
description: >
  Render a Markdown file to a single, self-contained HTML file via pandoc —
  standalone document, all resources embedded (images, CSS, fonts), a
  broad-coverage default stylesheet, relative image paths (`![](diagrams/x.png)`)
  resolved against the source file's directory, self-contained math (MathML, no
  CDN), and opt-in CriticMarkup rendering.
  TRIGGER when: /yf-markdown-html invoked; the user wants an HTML file
  created/generated from a `.md` file; "export this report to HTML", "make a
  self-contained web page from this note".
  SKIP for: PDF output (use `yf-markdown-pdf`); slide decks; linting markdown
  (use `yf-markdown-lint`); reformatting markdown (use `yf-markdown-format`).
---

# yf-markdown-html

Convert Markdown to a **single self-contained HTML file** with pandoc. Standalone
document, every resource embedded, a default stylesheet, self-contained math, and
opt-in CriticMarkup — the output renders offline with no external host.

## Invocation

```bash
uv run .claude/skills/yf-markdown-html/scripts/md2html.py <input.md>
```

Output defaults to `<input>.html` beside the source. Multiple inputs each render
to `<name>.html`. `-o OUT.html` overrides the path (single input only).

```bash
# explicit output
uv run .claude/skills/yf-markdown-html/scripts/md2html.py report.md -o /tmp/report.html
# batch
uv run .claude/skills/yf-markdown-html/scripts/md2html.py a.md b.md
# render CriticMarkup; add an extra stylesheet; pass extra pandoc flags after `--`
uv run .claude/skills/yf-markdown-html/scripts/md2html.py r.md --criticmarkup --css house.css -- --toc
# drop the built-in stylesheet (bring your own)
uv run .claude/skills/yf-markdown-html/scripts/md2html.py r.md --no-default-css --css house.css
```

## Self-contained output

The script runs `pandoc --standalone --to=html5 --embed-resources`, so the result
is one file with **everything inlined** — images become `data:` URIs, the
stylesheet is embedded in a `<style>` block, and there is no network fetch at view
time. This is the whole point of the skill: an HTML artifact you can email, commit,
or open offline.

- **Relative images resolve from the source dir** via `--resource-path`, then get
  embedded. Keep referenced images present, or pandoc errors.
- **Math is self-contained** via `--mathml` — `$x^2$` renders as inline MathML.
  MathJax / KaTeX are deliberately **not** used: they load script from a CDN, which
  would break the self-contained guarantee. MathML has no external dependency.
- **Default stylesheet.** A broad-coverage `default.css` (body text, headings,
  code, blockquotes, tables, images, and the CriticMarkup `cm-*` classes) is
  embedded via `--css`. `--no-default-css` omits it; `--css PATH` adds another
  stylesheet (repeatable) alongside or instead of the default.

## CriticMarkup (opt-in)

[CriticMarkup](http://criticmarkup.com/) is a plain-text convention for tracked
changes. `--criticmarkup` renders the five constructs to styled HTML; **default
off**, they pass through literally.

| Construct | Syntax | Renders as |
|:----------|:-------|:-----------|
| Addition | `{++text++}` | `<ins class="cm-add">` |
| Deletion | `{--text--}` | `<del class="cm-del">` |
| Substitution | `{~~old~>new~~}` | `<del class="cm-del">old</del><ins class="cm-add">new</ins>` |
| Highlight | `{==text==}` | `<mark class="cm-hl">` |
| Comment | `{>>text<<}` | `<span class="cm-comment">` |

The default stylesheet styles each `cm-*` class (add = green, del = struck red,
highlight = yellow, comment = grey italic), light and dark.

- **Reader:** `--criticmarkup` reads with `-f gfm-strikeout`. Disabling the
  `strikeout` reader extension is **required** — under default `gfm`, pandoc parses
  a substitution's inner `~~…~~` as strikeout and destroys the construct before any
  filter can see it.
- **Tradeoff — you give up GFM `~~strikethrough~~`.** Because `--criticmarkup`
  disables the strikeout extension, real GFM `~~struck~~` renders **literally**
  (as `~~struck~~`, not struck) while the flag is on. That is the deliberate cost
  of making CriticMarkup substitutions survive, and the reason CriticMarkup is
  opt-in rather than default-on. Off (the default) you get normal GFM strikethrough
  and CriticMarkup passes through as literal text.
- **Code is protected for free.** Inline `` `code` `` and fenced code blocks are
  distinct AST nodes, so a literal CriticMarkup construct inside code (e.g. a
  `{++x++}` in a snippet) renders untouched.
- **Accepted edge:** CriticMarkup *wrapping other inline markup*
  (`{++**bold** text++}`) is **not** transformed — the `Strong` node breaks
  the filter's text buffer. CriticMarkup wraps plain prose in practice; this
  boundary is documented and accepted (the fix would lose the free code protection).

The filter (`scripts/criticmarkup.lua`) is an `Inlines` filter that buffers
contiguous `Str`/`Space` tokens and runs an ordered 5-rule matcher (substitution
first) — never a per-`Str` matcher, so multi-word constructs
(`{++added several words++}`) transform correctly.

## Relationship to the other markdown skills

- **[`yf-markdown-pdf`](../yf-markdown-pdf/SKILL.md)** is the sibling renderer for
  **PDF** (pandoc + xelatex). Same relative-image convention; different output.
- **[`yf-markdown-lint`](../yf-markdown-lint/SKILL.md)** validates GFM (and its
  ML010 rule flags bare CriticMarkup in prose). This skill **renders**; it never
  lints or rewrites the source.

## Requirements

`pandoc` on PATH. The script checks for it and exits with a clear message if it is
missing. No `xelatex` needed (that is `yf-markdown-pdf`). No `init` step, no config,
no companion rule.
