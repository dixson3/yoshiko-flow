# Upstream #46: markdown-lint + markdown-pdf: support alt-text (a11y) / title (print caption) image convention

- **Number:** 46
- **Title:** markdown-lint + markdown-pdf: support alt-text (a11y) / title (print caption) image convention
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Problem

A markdown image has two text fields, and they want to serve two different goals:

- **alt text** (`![...]`) should be a thorough, literal **accessibility description** for screen readers — exhaustive by design.
- a good **print caption** (PDF/figure) should be short and interpretive.

Today these collide: pandoc's implicit-figure rendering uses the *alt* as the figure caption, so a screen-reader-quality alt becomes an overlong, clunky print caption. Authors are forced to pick one audience.

## Proposed convention

Use the two standard GFM image fields — no non-GFM syntax, lints clean, renders correctly on GitHub (the title becomes a hover tooltip):

```markdown
![<thorough accessibility description>](path/img.png "<short print caption>")
```

- `alt` (bracket) → accessibility description (screen readers / web).
- `title` (quoted) → short print caption (PDF figure caption).

## Ask 1 — `yf-markdown-pdf`: route title → figure caption natively

Bundle a Lua filter that, when an image has a non-empty `title`, uses it as the figure caption instead of the alt. Safe to always-apply: images with no title keep pandoc's default (alt) caption. Suggest wiring it into `md2pdf.py`'s `pre_args` alongside the existing landscape filter (or behind a `--caption-from-title` flag defaulting on). Filter (pandoc ≥ 3.0, Figure AST):

```lua
local utils = pandoc.utils
function Figure(fig)
  local title
  pandoc.walk_block(fig, { Image = function(img)
    if img.title and img.title ~= '' then title = img.title end
  end })
  if title and title ~= '' then
    local inlines = utils.blocks_to_inlines(pandoc.read(title, 'markdown').blocks)
    fig.caption.long = pandoc.Blocks(pandoc.Plain(inlines))
  end
  return fig
end
```

Currently consumers must pass `--lua-filter=...` by hand (and the literal `--` passthrough is mis-parsed by argparse's `nargs="+"` positional — the working form is a bare unknown flag `--lua-filter=path`, no `--` separator; worth documenting either way).

## Ask 2 — `yf-markdown-lint`: recognize / encourage the convention

- Treat `![alt](src "title")` as a first-class, blessed pattern in SKILL guidance (it already lints clean — make it documented intent, not incidental).
- Consider an accessibility rule: warn on an image with **empty alt** (bad for screen readers). A present `title` is optional (print caption) and should never warn.

## Why both skills

The split only works if both ends cooperate: the linter blesses/checks the pattern, the PDF renderer routes the fields correctly. A sibling request goes to `dixson3/emacs.d` so the xwidget HTML preview renders via the same pandoc + filter path (preview ↔ PDF parity).

