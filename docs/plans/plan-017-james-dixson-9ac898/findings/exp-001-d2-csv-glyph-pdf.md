# EXP-001 — Rendering ```d2 / ```csv fences and monochrome glyph fallback in pandoc+xelatex PDF

De-risking experiment for plan-017. Throwaway validation in a worktree; no skill modified.

**Environment (confirmed):** d2 0.7.1 (`/opt/homebrew/bin/d2`), pandoc 3.10
(`/opt/homebrew/bin/pandoc`), xelatex (`/Library/TeX/texbin/xelatex`), MacTeX with
`newunicodechar.sty` and `amssymb.sty` present. macOS (`byid`-class machine).

**Baseline reference filter** (`/Users/james/_dotfiles/emacs.d/pandoc/markdown-blocks.lua`)
renders `d2` via `pandoc.pipe("d2", {"-","-"}, text)` → `pandoc.RawBlock("html", svg)`.
That is HTML-only: xelatex cannot `\includegraphics` raw SVG, so the diagram is lost in PDF.
This experiment finds the PDF-correct path.

---

## 1. d2 → PDF embed

### Commands run

Probe both d2 output formats:

```sh
printf 'direction: right\na -> b -> c\n' > probe.d2
d2 probe.d2 probe.pdf   # -> PDF document, version 1.4, 1 pages (17 KB)
d2 probe.d2 probe.png   # -> PNG 1122x536 RGBA (17 KB)
```

Lua filter (`blocks.lua`) writes the fence text to a temp `.d2`, shells `d2` to a temp
`.pdf` under `$TMPDIR` (absolute), and returns a pandoc `Image` (not a RawBlock):

```lua
renderers["d2"] = function(text)
  local ok, result = pcall(function()
    local tmpdir = os.getenv("TMPDIR") or "/tmp"
    local base = tmpdir .. "/d2blk_" .. tostring(os.time()) .. "_" .. tostring(math.random(100000))
    local infile, outfile = base .. ".d2", base .. ".pdf"
    local fh = io.open(infile, "w"); fh:write(text); fh:close()
    local rc = os.execute("d2 " .. infile .. " " .. outfile .. " >/dev/null 2>&1")
    if rc ~= true and rc ~= 0 then error("d2 failed") end
    local of = io.open(outfile, "r"); if not of then error("no output") end; of:close()
    return outfile
  end)
  if not ok then return nil end                       -- degrade to code block
  return { pandoc.Para({ pandoc.Image({}, result) }) }  -- Image, NOT RawBlock("html")
end
```

Build:

```sh
pandoc test.md -o test.pdf --pdf-engine=xelatex \
  --lua-filter=blocks.lua \
  -V geometry:margin=1in -V mainfont="Arial Unicode MS" -V monofont=Menlo \
  --resource-path=.
```

### Result

- Build exit 0. `test.pdf` is 34 KB (vs ~a few KB empty).
- `strings test.pdf | grep XObject` shows a vector **Form XObject**
  (`/Type/XObject/Subtype/Form/FormType 1/BBox[0 0 576 576]...`) — the embedded d2 PDF.
- `pdftotext test.pdf | grep -c "direction: right"` → **0**: no raw d2 source in the PDF.
- Visual render (`pdftoppm -png`): the `plan → exec → done` boxes-and-arrows diagram
  renders as a crisp vector figure.
- **Path resolution:** `pandoc … -t native` shows the Image target is an **absolute**
  path: `/var/folders/.../d2blk_1782352651_89093.pdf`. Because it is absolute, pandoc
  resolves it regardless of `--resource-path`. A *relative* temp path would be resolved
  against the source dir and fail — so the filter MUST emit an absolute path (use
  `$TMPDIR`, which is absolute on macOS, or `os.tmpname()`).

### Recommendation

**Use d2 → PDF** (not PNG) for xelatex embedding. The PDF is a true vector Form XObject:
sharp at any zoom, smaller, no rasterization. PNG also embeds fine (DeviceRGB Image
XObject) but is raster — only prefer it if a future d2 feature emits PDF poorly. Emit an
**absolute** temp path. Return `pandoc.Image`, never `RawBlock("html")`.

---

## 2. csv → table

### Commands run

`blocks.lua` reuses the reference filter's CSV renderer verbatim:

```lua
renderers["csv"] = function(text)
  local ok, doc = pcall(pandoc.read, text, "csv")
  if not ok then return nil end
  return doc.blocks
end
```

Same xelatex build as §1, test.md contains a ```csv fence
(`Name,Role,Status / Alice,Lead,Active / Bob,Dev,Inactive`).

### Result

`pdftotext test.pdf` shows a real table — header row `Name / Role / Status` and data rows
`Alice/Lead/Active`, `Bob/Dev/Inactive` — rendered as a LaTeX table, not literal CSV text.
Works under the same single xelatex invocation; no extra package needed (`pandoc.read … csv`
is built in). CSV cells containing ✅ also render (see §4 combined test).

### Recommendation

Adopt as-is. No external tool, no LaTeX package, pcall-guarded. Identical to the reference
filter's `csv` entry — it is already PDF-correct because it produces native pandoc Blocks.

---

## 3. Graceful degradation (d2 absent / failing)

### Commands run

Simulate broken/absent d2 with a failing stub earliest on PATH (overriding the whole PATH
hides pandoc itself, so stub only `d2`):

```sh
mkdir -p stubbin
printf '#!/bin/sh\nexit 127\n' > stubbin/d2 && chmod +x stubbin/d2
PATH="$PWD/stubbin:$PATH" pandoc test.md -o test_nod2.pdf --pdf-engine=xelatex \
  --lua-filter=blocks.lua \
  -V geometry:margin=1in -V mainfont="Arial Unicode MS" -V monofont=Menlo
```

### Result

- Build exit **0** — the whole render does **not** abort.
- `pdftotext test_nod2.pdf | grep -c "direction: right"` → **1**: the d2 fence fell back to
  a plain code listing showing its source. CSV table still rendered normally.

The `pcall(...)` + `if not ok then return nil end` contract works: a failed/missing `d2`
returns `nil`, leaving the CodeBlock untouched (pandoc renders it as a verbatim listing).

### Recommendation

Keep the pcall-degrade pattern exactly. One missing binary degrades one block to a listing
rather than failing the document. The reference filter's documented "wrap in pcall, return
nil on failure" template holds for the PDF target too.

---

## 4. Monochrome glyph fallback (✔ U+2714 vs ✅ U+2705)

### Commands run

Font coverage survey:

```sh
fc-list ":charset=2714" family   # U+2714 heavy check
fc-list ":charset=2705" family   # U+2705 white-heavy-check (color emoji)
fc-list | grep -iE "symbola|noto sans symbols|stix|apple symbols"
```

Empirical render of all three glyphs with the *current* md2pdf recipe:

```sh
printf '# Glyph test\n\nHeavy U+2714: ✔\n\nEmoji U+2705: ✅\n\nCross U+2716: ✖\n' > glyph.md
pandoc glyph.md -o glyph_arial.pdf --pdf-engine=xelatex \
  -V geometry:margin=1in -V mainfont="Arial Unicode MS" -V monofont=Menlo
pdftotext glyph_arial.pdf -   # inspect surviving codepoints
```

### Result — coverage

| Codepoint | Glyph | Monochrome coverage on this machine | xelatex result with Arial Unicode MS |
|-----------|-------|-------------------------------------|--------------------------------------|
| U+2714 | ✔ heavy check | **Arial Unicode MS**, Menlo, Zapf Dingbats, Nerd Fonts | **renders** (already the mainfont) |
| U+2716 | ✖ heavy cross | Arial Unicode MS, others | **renders** |
| U+2705 | ✅ white-heavy-check | **none** — only Apple Color Emoji (color bitmap) + LastResort (.notdef placeholder) | **blank** + `Missing character` warning |

- **No** Symbola, Noto Sans Symbols 2, or STIX-with-2705 is installed. STIX/Apple Symbols
  do **not** cover U+2705.
- Empirical: `pdftotext glyph_arial.pdf` returns `0x2714 ✔`, `0xfffd �` (the dropped
  U+2705), `0x2716 ✖`. xelatex emits
  `[WARNING] Missing character: There is no ✅ (U+2705) in font Arial Unicode MS`.

So **U+2714 ✔ already works with the existing `-V mainfont="Arial Unicode MS"`** — no
change needed for the monochrome heavy check. **U+2705 ✅ is the only problem**, and it is
unfixable by font selection alone (no installed monochrome font has the glyph, and Apple
Color Emoji is a color-bitmap font xelatex/fontspec won't use).

### Result — fix for U+2705 via `newunicodechar` remap

Map the unsupported color emoji onto the supported heavy check at the LaTeX level.

**Recipe B (adopted — cleanest):** map U+2705 to the literal U+2714 symbol in the text font:

```tex
% header.tex
\usepackage{newunicodechar}
\newunicodechar{✅}{\symbol{"2714}}
```

```sh
pandoc glyph.md -o glyph_mapB.pdf --pdf-engine=xelatex \
  -V geometry:margin=1in -V mainfont="Arial Unicode MS" -V monofont=Menlo \
  -H header.tex
```

Result: `pdftotext` → `0x2714 ✔`, `0x2714 ✔`, `0x2716 ✖`. The ✅ now renders as ✔ (same
glyph as a literal ✔, visually consistent), **no missing-character warning**.

**Recipe A (alternative):** amssymb math checkmark, if you prefer a thin ✓:

```tex
\usepackage{amssymb}
\usepackage{newunicodechar}
\newunicodechar{✅}{\checkmark}
```

Result: ✅ → ✓ (U+2713). Works, but pulls in amssymb and uses a math-mode glyph; B keeps
everything in the text font.

### Recommendation

1. **Keep `-V mainfont="Arial Unicode MS"`** — it already covers ✔ U+2714, ✖ U+2716, →,
   ≤, ≈. No new font install is required for the monochrome checks.
2. **Add a header-includes remap for the color emoji** ✅ U+2705 so existing status tables
   don't go blank:

   ```tex
   \usepackage{newunicodechar}
   \newunicodechar{✅}{\symbol{"2714}}
   ```

   (Optionally also map ❌ U+274C → `\symbol{"2716}` ✖ and ⚠️ U+26A0 if those appear.)
3. **No font install needed on this machine.** If a future target lacks Arial Unicode MS,
   the portable fallback is `brew install --cask font-symbola` (Symbola covers both U+2714
   and a monochrome U+2705) and switch mainfont/remap accordingly — but that is not the
   case here, so don't add a dependency.

---

## Net recommendation for md2pdf.py

### Filter design — one Lua file, registry pattern

Ship a single `blocks.lua` beside `md2pdf.py` and add `--lua-filter=<dir>/blocks.lua` to
the pandoc invocation. Structure (matches the emacs.d reference filter's extension pattern,
PDF-targeted):

- A `renderers` table keyed by fence class. Each fn takes the block text, returns a list of
  pandoc Blocks or `nil` (leave untouched).
- `renderers["csv"]` = `pcall(pandoc.read, text, "csv")` → `doc.blocks` (native table; no
  tool, no package).
- `renderers["d2"]` = pcall: write fence to `$TMPDIR/d2blk_<unique>.d2`, run
  `d2 <in> <out>.pdf`, return `pandoc.Para({pandoc.Image({}, <absolute out.pdf path>)})`.
  **d2 → PDF** (vector Form XObject), **absolute** temp path, **Image not RawBlock**.
- `function CodeBlock(block)` iterates classes, calls the matching renderer; returns nothing
  for unmatched blocks.
- **pcall-degrade everywhere:** any failure (missing/broken d2, bad CSV) returns `nil`, so
  the block degrades to a verbatim code listing and the document still builds (verified:
  exit 0, source shown as listing).

### Exact working build command

```sh
pandoc <src>.md -o <out>.pdf --pdf-engine=xelatex \
  --lua-filter=<skill-dir>/scripts/blocks.lua \
  -V geometry:margin=1in -V linkcolor=blue \
  -V mainfont="Arial Unicode MS" -V monofont=Menlo \
  -H <skill-dir>/scripts/glyph-fallback.tex \
  --resource-path=<src-dir>
```

`--resource-path` still matters for user `![](diagrams/x.png)` images; the d2 temp PDFs use
absolute paths and are independent of it.

### Glyph-fallback recipe to adopt

Add a tiny `glyph-fallback.tex` and pass it via `-H` (header-includes):

```tex
\usepackage{newunicodechar}
\newunicodechar{✅}{\symbol{"2714}}   % U+2705 color emoji -> U+2714 heavy check (text font)
% optional: \newunicodechar{❌}{\symbol{"2716}}  % U+274C -> U+2716 heavy cross
```

Rationale: Arial Unicode MS already renders the monochrome ✔/✖; only the color-emoji
codepoints (✅ U+2705, ❌ U+274C) lack any monochrome glyph on this machine, so remap those
onto the covered heavy-check/cross. `newunicodechar.sty` is present in MacTeX; no font
install required. If portability to a host without Arial Unicode MS is later needed, document
`brew install --cask font-symbola` as the fallback font.

### Net

All four items validated end-to-end in one xelatex build (`combined.pdf`: d2 vector diagram
embedded, CSV-with-✅ table, status table with ✅/✔, zero missing-character warnings, exit 0).
The design is: one registry-pattern Lua filter (d2→PDF/Image, csv→native table, pcall-degrade)
+ a two-line `newunicodechar` header for the color-emoji checkmarks.
