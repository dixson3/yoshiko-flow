# SPEC — Markdown PDF (`yf-markdown-pdf`)

> **Status: DRAFT (primed).** Per-skill SPEC for the PDF skill (currently `markdown-pdf`, renamed
> to `yf-markdown-pdf` by plan-010 Issue 3.7 / `REQ-YF-RENAME-001`). Operator to review/edit.
> Composed by the root macro `SPEC.md` §4 under spec key **MDPDF**.

## 1. Purpose & scope

`yf-markdown-pdf` renders a Markdown file to PDF via the **pandoc + xelatex** pipeline, tuned so a
broad-coverage Unicode font renders glyphs (arrows, `≤`, `≈`) the LaTeX default fonts miss, with
1in margins, blue links, and relative image paths (e.g. `![](diagrams/x.png)`) resolved against
the source file's directory.

**In scope:** the single/batch `.md → .pdf` render, the platform-aware font policy, relative-image
resolution, the table-fit levers (font shrink, dash-width tuning, landscape rotation), rendering
**renderable fences** (` ```d2 ` → PDF figure, ` ```csv ` → table) inline, and a macOS glyph
fallback for color emoji.

**Out of scope:** slide decks; HTML or any non-PDF output; **linting** markdown (that is
`yf-markdown-lint`). Portable pipe-table *authoring* conventions also live in `yf-markdown-lint`;
this skill only renders them.

## 2. Requirements (`REQ-MDPDF-NNN`)

### 2.1 Pipeline

- **REQ-MDPDF-001** *(testable)* the script shall invoke `pandoc --pdf-engine=xelatex` with
  `-V geometry:margin=<margin>` (default `1in`) and `-V linkcolor=blue`.
- **REQ-MDPDF-002** *(testable)* it shall set `--resource-path=<dir of the source .md>` so a
  relative image reference resolves against the source file's directory.
- **REQ-MDPDF-003** *(testable)* it shall verify `pandoc` and `xelatex` are on PATH and exit with
  a clear message naming the missing tool(s) if either is absent.
- **REQ-MDPDF-004** *(testable)* on pandoc non-zero exit the script shall surface stderr and exit
  non-zero; per-glyph `Missing character` lines are **warnings only** (build still succeeds) and
  shall be summarized.

### 2.2 Platform-aware fonts

- **REQ-MDPDF-010** *(testable)* on **macOS** the defaults shall be `mainfont=Arial Unicode MS` /
  `monofont=Menlo` (covering `→ ≤ ≈`); **off macOS** the defaults shall be unset so xelatex falls
  back to Latin Modern and only *warns* on missing glyphs — because naming a font that does not
  exist makes xelatex **hard-fail**.
- **REQ-MDPDF-011** *(testable)* a font shall be forced (`-V mainfont=` / `-V monofont=`) only
  when set — by the macOS default or an explicit `--mainfont`/`--monofont` (e.g. `--mainfont
  "DejaVu Sans"` for full coverage on Linux).
- **REQ-MDPDF-012** the distinction shall hold: a missing **font** fails the build; a missing
  **glyph** (font present, glyph absent) only warns.

### 2.3 Invocation & output

- **REQ-MDPDF-020** *(testable)* the script shall accept one or more `.md` inputs; each shall
  render to `<name>.pdf` beside the source. `-o OUT.pdf` shall override the path and shall be valid
  with a **single** input only (error otherwise).
- **REQ-MDPDF-021** *(testable)* arguments after a literal `--` shall pass through to pandoc
  verbatim; a non-file input shall error.

### 2.4 Table fit

- **REQ-MDPDF-030** *(testable)* `--table-font SIZE` (default `footnotesize`, `normalsize` = no
  shrink) shall apply a LaTeX size macro to every table env via an `\AtBeginEnvironment` header,
  from the valid size set.
- **REQ-MDPDF-031** *(testable)* `--landscape-cols N` (`0` = off) shall rotate any table with more
  than N columns to a landscape page via a render-time Lua filter (no `\begin{landscape}` in the
  Markdown source).
- **REQ-MDPDF-032** `--columns N` (default 72) shall control when pandoc's separator-dash-count
  column-width tuning engages (it engages once a table's separator row is wider than `--columns`).

### 2.5 Renderable fences & glyph fallback

- **REQ-MDPDF-040** *(testable)* by default the script shall render **renderable fences** via the
  `scripts/blocks.lua` pandoc filter: ` ```d2 ` → `d2 <in> <out>.pdf` embedded as a `pandoc.Image`
  at an absolute path (vector PDF, **not** SVG — a deliberate divergence from the HTML preview);
  ` ```csv ` → a native LaTeX table via `pandoc.read(text,"csv")`. The renderable-fence class set
  shall be the shared `_shared/renderable_fences.py` registry, mirrored into `blocks.lua` by
  `_shared/sync.py` (generated, drift-guarded).
- **REQ-MDPDF-041** *(testable)* rendering shall **degrade gracefully**: if `d2` is absent or a
  fence fails to compile/parse, that fence shall be left as a verbatim code listing and the build
  shall still exit 0 (`pcall` in the filter). Exec shall be arg-vector only (`pandoc.pipe`), never
  a shell string with concatenated paths.
- **REQ-MDPDF-042** *(testable)* rendered d2 artifacts shall be written into a single **run-scoped**
  temp dir (`MD2PDF_FENCE_TMPDIR`) that the script reaps in `finally` after pandoc completes — no
  temp artifact shall survive a render, and repeated renders shall not accumulate temp dirs.
- **REQ-MDPDF-043** *(testable)* `--no-render-fences` shall keep ` ```d2 `/` ```csv ` fences
  verbatim (rendering is default-on).
- **REQ-MDPDF-044** *(testable)* **on macOS** the script shall include `scripts/glyph-fallback.tex`
  (`-H`), remapping ✅ (U+2705) onto a monochrome ✔ (U+2714) via `newunicodechar` so the
  fixture renders with **zero** missing-character warnings; **off macOS** the header shall be
  skipped and the glyph shall degrade to an xelatex warning — **never a hard fail**. Color emoji
  remain unsupported (accepted limitation); the portable fallback font is `font-symbola` / Noto
  Sans Symbols 2 via `--mainfont`.

## 3. Interfaces

- **CLI / scripts:** `scripts/md2pdf.py` (run via `uv run`) — positional `.md` input(s); flags
  `-o/--output`, `--mainfont`, `--monofont`, `--margin`, `--table-font`, `--landscape-cols`,
  `--columns`, `--no-render-fences`, and `--` passthrough. Helpers:
  `scripts/landscape_wide_tables.lua` (landscape-rotation filter), `scripts/blocks.lua`
  (renderable-fence renderer; reads the `MD2PDF_FENCE_TMPDIR` env var), `scripts/glyph-fallback.tex`
  (macOS color-emoji remap header). **External tools:** the script shells to **pandoc** and **xelatex**
  (`depends-on-tool: [uv, pandoc, xelatex]`). This is a skill that shells to external tools,
  consistent with macro GUARDRAILS GR-004 (PDF rendering lives in the skill, not in `yf`) and
  GR-011 (`yf` shells to `pandoc`, never vendors it).
- **Companion rule:** none — `user-invocable`, no always-loaded trigger rule.
- **Config / state:** none — no `.<skill>.local.json`, no `.yf/<skill>/` state; a transient LaTeX
  header is written to a temp file and removed after each run.

## 4. Guardrails (`GR-MDPDF-NNN`)

- **GR-MDPDF-001** *Drift:* growing into a slide-deck / HTML / multi-format exporter. *Rule:* the
  output is **PDF only**, via pandoc + xelatex. *Why:* one tuned pipeline; other formats are
  out of domain.
- **GR-MDPDF-002** *Drift:* linting or rewriting the Markdown. *Rule:* this skill **renders**;
  GFM validity and pipe-table authoring conventions are `yf-markdown-lint`. *Why:* render and
  lint are separate axes.
- **GR-MDPDF-003** *Drift:* forcing a hardcoded font on every platform. *Rule:* force a font only
  when set; off macOS leave it unset so xelatex falls back rather than hard-failing on a missing
  font. *Why:* the macOS fonts do not exist elsewhere and would break the build.

## 5. Verification

- Dependency check (REQ-MDPDF-003) and single-vs-batch / `-o` constraints (REQ-MDPDF-020) are
  checkable by argument fixtures. The pandoc command construction (REQ-MDPDF-001/002,
  REQ-MDPDF-010/011) is asserted by inspecting the built `pandoc` argv for `--pdf-engine=xelatex`,
  the geometry/linkcolor `-V` flags, `--resource-path`, and the presence/absence of
  `mainfont=`/`monofont=` per platform.
- A `.md` referencing a relative image renders without a resource error (REQ-MDPDF-002); a
  `--landscape-cols`/`--table-font` run injects the expected header / Lua filter (REQ-MDPDF-030/031).
  Forward coverage per plan-010 Epic 6 (tests naming the REQ id).

## 6. References

- `skills/yf-markdown-pdf/SKILL.md` (pipeline defaults, font policy, table levers, renderable
  fences, glyph fallback).
- `skills/yf-markdown-pdf/scripts/md2pdf.py`, `scripts/landscape_wide_tables.lua`,
  `scripts/blocks.lua`, `scripts/glyph-fallback.tex`.
- `_shared/renderable_fences.py` (canonical renderable-fence registry mirrored into `blocks.lua`).
- `skills/yf-markdown-lint/SKILL.md` (portable pipe-table authoring + ML009 d2 compile-check — the
  lint axis on the same registry).
- Root `SPEC.md` §4 (MDPDF) and `GUARDRAILS.md` (GR-004, GR-011).
