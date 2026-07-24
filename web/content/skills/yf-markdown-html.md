`yf-markdown-html` renders a Markdown file to a **single, self-contained HTML
file** with pandoc. Every resource is inlined — images become `data:` URIs, the
stylesheet embeds in a `<style>` block, math renders as MathML — so the output has
no external host and opens offline. It renders; it never lints or rewrites the
source. Its sibling [`yf-markdown-pdf`](/skills/yf-markdown-pdf/) is the same idea
for PDF output.

## When it fires

Invoke `/yf-markdown-html` when you want an HTML artifact from a `.md` file — one
you can email, commit, or open offline with no server:

- "export this report to HTML";
- "make a self-contained web page from this note";
- rendering one or many `.md` files to standalone HTML in a batch.

Skip it for PDF output ([`yf-markdown-pdf`](/skills/yf-markdown-pdf/)), for slide
decks, and for linting or reformatting the source
([`yf-markdown-lint`](/skills/yf-markdown-lint/) and
[`yf-markdown-format`](/skills/yf-markdown-format/)).

## Self-contained output

The script runs `pandoc --standalone --to=html5 --embed-resources`, so the result
is one file with everything inlined and no network fetch at view time. That
guarantee is the whole point of the skill, and three pipeline choices protect it:

- **Relative images resolve from the source directory** via `--resource-path`,
  then get embedded. Keep referenced images present, or pandoc errors.
- **Math is self-contained** via `--mathml` — `$x^2$` becomes inline MathML.
  MathJax and KaTeX are deliberately not used: they load script from a CDN, which
  would break the offline guarantee. MathML has no external dependency.
- **A broad-coverage default stylesheet** is embedded, styling body text,
  headings, code, blockquotes, tables, images, and the CriticMarkup classes.
  `--no-default-css` omits it; `--css PATH` adds another stylesheet, repeatable,
  alongside or instead of the default.

By default the output lands at `<input>.html` beside the source. `-o OUT.html`
overrides the path for a single input, and arguments after a literal `--` pass
through to pandoc verbatim.

## CriticMarkup, opt-in

CriticMarkup is a plain-text convention for tracked changes. Pass `--criticmarkup`
and the five constructs render to styled HTML; the flag is **default off**, and
without it the constructs pass through literally.

| Construct | Syntax | Renders as |
| :--- | :--- | :--- |
| Addition | `{++text++}` | `<ins class="cm-add">` |
| Deletion | `{--text--}` | `<del class="cm-del">` |
| Substitution | `{~~old~>new~~}` | `<del class="cm-del">old</del><ins class="cm-add">new</ins>` |
| Highlight | `{==text==}` | `<mark class="cm-hl">` |
| Comment | `{>>text<<}` | `<span class="cm-comment">` |

The default stylesheet styles each `cm-*` class in light and dark: additions
green, deletions struck red, highlights yellow, comments grey italic.

**The flag carries one tradeoff.** With `--criticmarkup` on, the reader is
`gfm-strikeout` — the strikeout extension is disabled. That is required: under
default `gfm`, pandoc parses a substitution's inner `~~…~~` as strikeout and
destroys the construct before any filter runs. The cost is that real GFM
`~~strikethrough~~` renders literally while the flag is on. Off (the default) you
get normal strikethrough and CriticMarkup passes through as text. This is why
CriticMarkup is opt-in rather than default-on.

Two boundaries are worth noting. Inline `` `code` `` and fenced code are distinct
AST nodes, so a literal CriticMarkup construct inside a code span renders
untouched for free. And CriticMarkup wrapping other inline markup
(`{++**bold** text++}`) is not transformed — the inner markup node breaks the
filter's text buffer. CriticMarkup wraps plain prose in practice, so this edge is
documented and accepted.

## Relationship to the other markdown skills

- [`yf-markdown-pdf`](/skills/yf-markdown-pdf/) is the sibling renderer for **PDF**
  (pandoc plus xelatex). It shares the relative-image convention and produces a
  different output.
- [`yf-markdown-lint`](/skills/yf-markdown-lint/) validates GFM, and its ML010 rule
  flags bare CriticMarkup in prose. This skill *renders* that same CriticMarkup on
  an opt-in flag rather than flagging it.

## Requirements

`pandoc` on PATH. The script checks for it and exits with a clear message if it is
missing, rather than surfacing a raw traceback. No `xelatex` is needed — that
belongs to [`yf-markdown-pdf`](/skills/yf-markdown-pdf/). No `init` step, no
config, no companion rule.
