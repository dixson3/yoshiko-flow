# exp-001: Validate CriticMarkup + caption pandoc Lua filters (pandoc 3.10)

**Question:** Do the three filter/detection approaches plan-026 depends on actually work against
the installed pandoc 3.10, so the plan can commit to concrete designs?

**Verdict:** All three viable. Two need a specific reader-extension incantation the issues
under-specify; one (ML010 regex) works as described.

## Finding 1 — CriticMarkup → HTML Lua filter (#50): works-with-modification

- **`-f gfm-strikeout` is required and correct.** Under default `gfm`, `{~~old~>new~~}` is
  destroyed before any filter runs (pandoc parses the inner `~~…~~` as `Strikeout`). Disabling
  the `strikeout` reader extension lets the whole construct survive as a `Str` token.
- **Must be an `Inlines` filter that BUFFERS contiguous `Str`/`Space` tokens — not a per-`Str`
  matcher.** Multi-word constructs (`{++added several words++}`) split across many tokens; a
  per-`Str` filter would only catch single-token cases. Buffer contiguous text, flush on any
  other node, run an ordered 5-rule matcher (substitution first).
- **Code protection is FREE.** `Code` (inline) and `CodeBlock` are distinct AST nodes that never
  enter the text buffer, so `` `{++literal++}` `` and fenced literals render untouched — no
  extra logic.
- Verified: single + multi-word constructs, adjacent constructs `{++one++}{--two--}`, HTML-special
  escaping (`{++a<b & c++}` → `<ins class="cm-add">a&lt;b &amp; c</ins>`).
- **Honest caveat:** CriticMarkup *wrapping other inline markup* (`{++**bold** ins++}`) does not
  transform — the `Strong` node breaks the buffer. Acceptable edge (CriticMarkup wraps plain text
  in practice); the only fix is a raw-source regex preprocessing pass, which loses free code
  protection — not recommended.

Command: `pandoc -f gfm-strikeout -t html --lua-filter=criticmarkup.lua input.md`

Construct → HTML map (confirmed): add→`<ins class="cm-add">`, del→`<del class="cm-del">`,
sub→`<del class="cm-del">old</del><ins class="cm-add">new</ins>`, highlight→`<mark class="cm-hl">`,
comment→`<span class="cm-comment">`.

## Finding 2 — title → figure-caption Lua filter (#46 ask 1): works-with-modification

- The issue's `Figure(fig)` filter (pandoc 3.0+ Figure AST) validates cleanly, **but `Figure`
  nodes only exist when `implicit_figures` is active**, and **`gfm` does NOT enable it by
  default**. The reader must be `-f gfm+implicit_figures` (or `-f markdown`). This is the
  load-bearing detail for the markdown-pdf invocation.
- Default caption derives from **alt**; the title lives on the inner `Image` target tuple. Filter
  walks the figure for the first `Image` and, if `img.title ~= ""`, sets
  `fig.caption.long = {pandoc.Plain{pandoc.Str(img.title)}}`.
- Verified three ways: native AST (`[Plain [Str "short caption"]]`), HTML (`<figcaption>short
  caption</figcaption>`), and a full xelatex PDF via `pdftotext` (`Figure 1: short caption` /
  `Figure 2: alt only no title` for the no-title control).
- Note: a 1×1 placeholder PNG crashes xelatex's graphics driver — use a real-sized PNG for
  pipeline tests (unrelated to the filter).

Command: `pandoc -f gfm+implicit_figures -t pdf --pdf-engine=xelatex --lua-filter=figtitle.lua input.md -o out.pdf`

## Finding 3 — ML010 un-escaped-markup detection (#48, Python/regex): works

- Registry of five compiled patterns, non-greedy bodies; the substitution pattern **must require
  the `~>` separator** (`\{~~.+?~>.+?~~\}`) to distinguish it from deletion. No cross-matches.
- Two-part exclusion: (a) blank out inline code spans before matching
  (`(\`+)(?:.+?)\1`, multi-backtick-safe, column-stable), (b) line-oriented fence state machine
  (`^\s*(\`\`\`+|~~~+)`) suppressing matches inside fences.
- 8/8 cases pass: all five bare constructs flagged; same inside inline code / fenced block NOT
  flagged; non-CriticMarkup braces (`{single}`) NOT flagged; line numbers correct across fences.
- Slots directly onto `markdown_lint.py`'s existing inline-code stripping + fence tracking.

## Implications for the plan

- **markdown-html** invokes pandoc with `-f gfm-strikeout` when `--criticmarkup` is on; the Lua
  filter is `Inlines`-buffering. Default (no flag) is literal pass-through (plain `gfm`).
- **markdown-pdf** caption filter requires `+implicit_figures` on the reader — confirm md2pdf's
  current `-f`/`--from` and add the extension when wiring the always-on caption filter.
- **ML010** is a self-contained regex rule reusing existing code-span/fence infrastructure; safe
  for the authoring subset.
