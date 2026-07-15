# SPEC — Markdown HTML (`yf-markdown-html`)

> **Status: Active.** Per-skill SPEC for Markdown-to-HTML rendering. Requirements use RFC-2119
> "shall"; composed by the root `SPEC.md` macro spec.

## 1. Purpose & scope

`yf-markdown-html` renders a Markdown file to a **single, self-contained HTML file** via pandoc,
tuned so the output travels with no external dependency: standalone document, all resources
(images, CSS, fonts) embedded, a broad-coverage default stylesheet, relative image paths (e.g.
`![](diagrams/x.png)`) resolved against the source file's directory, self-contained math (MathML,
no CDN), and **opt-in** CriticMarkup rendering.

**In scope:** the single/batch `.md → .html` render, resource embedding, the default stylesheet,
relative-image resolution, self-contained math, and the opt-in CriticMarkup-to-HTML filter.

**Out of scope:** PDF or any non-HTML output (that is `yf-markdown-pdf`); slide decks; **linting**
or rewriting the Markdown (that is `yf-markdown-lint` / `yf-markdown-format`). This skill
**renders**; it never validates, reformats, or edits the source.

## 2. Requirements (`REQ-MDHTML-NNN`)

### 2.1 Pipeline

- **REQ-MDHTML-001** *(testable)* the script shall invoke `pandoc --standalone --to=html5
  --embed-resources` so the output is a single self-contained HTML file with every referenced
  resource inlined (no sidecar files, no network fetch at view time).
- **REQ-MDHTML-002** *(testable)* it shall set `--resource-path=<dir of the source .md>` so a
  relative image reference resolves against the source file's directory (and is then embedded by
  `--embed-resources`).
- **REQ-MDHTML-003** *(testable)* it shall verify `pandoc` is on PATH and exit with a clear message
  naming the missing tool if it is absent (fail-closed).
- **REQ-MDHTML-004** *(testable)* on pandoc non-zero exit the script shall surface stderr and exit
  non-zero.
- **REQ-MDHTML-005** *(testable)* the run entrypoint shall call a `check_deps()`-style guard
  **before** invoking pandoc: when `pandoc` is absent from PATH it shall fail **closed** with a
  single readable message naming the missing tool (with an install hint), exiting non-zero — never
  surfacing a raw `FileNotFoundError`/traceback. This is the entrypoint enforcement of the PATH
  guarantee REQ-MDHTML-003 states, mirroring `yf-markdown-pdf`'s `check_deps()` (REQ-MDPDF-003).

### 2.2 Stylesheet

- **REQ-MDHTML-010** *(testable)* the script shall inject a broad-coverage default stylesheet
  (`scripts/default.css`, via `--css` + `--embed-resources` so it is inlined) styling body text,
  headings, code, blockquotes, tables, and images. `--no-default-css` shall omit it; `--css PATH`
  shall supply an additional stylesheet.

### 2.3 Math

- **REQ-MDHTML-011** *(testable)* math shall render **self-contained** via `--mathml` — no CDN, no
  external script — so `--embed-resources` stays honest (the output has zero network dependencies).
  This choice is pinned: MathJax/KaTeX are rejected because they load script from a CDN, which
  would break the self-contained guarantee.

### 2.4 Opt-in CriticMarkup

- **REQ-MDHTML-020** *(testable)* CriticMarkup rendering shall be **opt-in** behind
  `--criticmarkup`, **default OFF**. Default off, the reader is plain `gfm` and CriticMarkup
  syntax passes through literally (untransformed).
- **REQ-MDHTML-021** *(testable)* with `--criticmarkup` the script shall read with `-f
  gfm-strikeout` (the `strikeout` reader extension disabled) and apply the `scripts/criticmarkup.lua`
  filter. Disabling `strikeout` is **required**: under default `gfm` pandoc parses the inner
  `~~…~~` of a substitution as `Strikeout` and destroys the construct before any filter runs.
- **REQ-MDHTML-022** *(testable)* the filter shall be an `Inlines` filter that **buffers contiguous
  `Str`/`Space` tokens** and runs an ordered 5-rule matcher (substitution first), never a per-`Str`
  matcher — a multi-word construct (`{++added several words++}`) splits across many tokens a
  per-`Str` filter would miss.
- **REQ-MDHTML-023** *(testable)* the five CriticMarkup constructs shall render to HTML as: addition
  → `<ins class="cm-add">`, deletion → `<del class="cm-del">`, substitution →
  `<del class="cm-del">old</del><ins class="cm-add">new</ins>`, highlight →
  `<mark class="cm-hl">`, comment → `<span class="cm-comment">`. The default stylesheet shall carry
  a matching entry for each of `cm-add` / `cm-del` / `cm-hl` / `cm-comment`.
- **REQ-MDHTML-024** *(testable)* HTML-special characters in construct bodies shall be escaped
  (e.g. `{++a<b & c++}` → `<ins class="cm-add">a&lt;b &amp; c</ins>`). Inline `Code` and
  `CodeBlock` nodes never enter the text buffer, so a literal CriticMarkup construct inside code
  renders untouched — no extra logic.
- **REQ-MDHTML-025** the CriticMarkup / strikethrough **tradeoff shall be documented**: because
  `--criticmarkup` reads with `gfm-strikeout`, real GFM `~~strikethrough~~` is **disabled** and
  renders literally while the flag is on, so CriticMarkup substitutions survive. This is the
  deliberate cost of opt-in CriticMarkup and the reason it is not default-on.
- **REQ-MDHTML-026** CriticMarkup wrapping **other inline markup** (`{++**bold** ins++}`) is a
  documented out-of-scope edge: the `Strong` node breaks the text buffer, so the construct is not
  transformed. CriticMarkup wraps plain prose in practice; the buffering filter is the correct
  design and this boundary is accepted.

### 2.5 Invocation & output

- **REQ-MDHTML-030** *(testable)* the script shall accept one or more `.md` inputs; each shall
  render to `<name>.html` beside the source. `-o OUT.html` shall override the path and shall be
  valid with a **single** input only (error otherwise).
- **REQ-MDHTML-031** *(testable)* arguments after a literal `--` shall pass through to pandoc
  verbatim; a non-file input shall error.

## 3. Interfaces

- **CLI / scripts:** `scripts/md2html.py` (run via `uv run`) — positional `.md` input(s); flags
  `-o/--output`, `--criticmarkup`, `--css PATH`, `--no-default-css`, and `--` passthrough. Helpers:
  `scripts/criticmarkup.lua` (opt-in CriticMarkup-to-HTML `Inlines` filter), `scripts/default.css`
  (default stylesheet, including the `cm-*` construct classes). **External tools:** the script
  shells to **pandoc** (`depends-on-tool: [uv, pandoc]`). Consistent with macro GUARDRAILS GR-011
  (`yf` shells to `pandoc`, never vendors it).
- **Companion rule:** none — `user-invocable`, no always-loaded trigger rule.
- **Config / state:** none — no `.<skill>.local.json`, no `.yf/<skill>/` state.

## 4. Guardrails (`GR-MDHTML-NNN`)

- **GR-MDHTML-001** *Drift:* growing into a PDF / slide-deck / multi-format exporter. *Rule:* the
  output is **standalone HTML only**, via pandoc. *Why:* PDF is `yf-markdown-pdf`; one skill, one
  output format.
- **GR-MDHTML-002** *Drift:* linting, reformatting, or rewriting the Markdown source. *Rule:* this
  skill **renders HTML only** — it never validates GFM, aligns tables, migrates wiki-links, or
  edits the source. *Why:* validation is `yf-markdown-lint`; content-altering autofix is
  `yf-markdown-format`; render and lint/format are separate axes.
- **GR-MDHTML-003** *Drift:* pulling in a CDN for math or CriticMarkup styling to get richer
  output. *Rule:* the output stays **self-contained** — math is MathML, CriticMarkup styling ships
  in the embedded default stylesheet, no external host is ever referenced. *Why:*
  `--embed-resources` promises a file that renders offline; a CDN silently breaks that.

## 5. Verification

- Dependency check (REQ-MDHTML-003) and single-vs-batch / `-o` constraints (REQ-MDHTML-030) are
  checkable by argument fixtures. The entrypoint fail-closed guard (REQ-MDHTML-005) is asserted by
  running the entrypoint with `pandoc` masked from PATH and checking for the readable missing-tool
  message and a non-zero exit (no raw traceback). The pandoc command construction (REQ-MDHTML-001/002/010/011) is
  asserted by inspecting the built `pandoc` argv for `--standalone`, `--to=html5`,
  `--embed-resources`, `--resource-path`, `--css`, and `--mathml`.
- A `.md` render produces a single HTML file that contains an embedded `<style>` (default
  stylesheet), a `data:`-URI or inline image (embed-resources), and `<math` markup for math
  (REQ-MDHTML-010/011). A `--criticmarkup` render turns the five constructs into the
  `cm-*`-classed tags (REQ-MDHTML-023/024) while a default render leaves them literal
  (REQ-MDHTML-020). Tests name the REQ id.

## 6. References

- `skills/yf-markdown-html/SKILL.md` (pipeline defaults, stylesheet, math, opt-in CriticMarkup).
- `skills/yf-markdown-html/scripts/md2html.py`, `scripts/criticmarkup.lua`, `scripts/default.css`.
- `docs/plans/plan-026-james-dixson-6e0e2f/findings/exp-001-pandoc-lua-filters.md` (the validated
  CriticMarkup filter design against pandoc 3.10).
- `skills/yf-markdown-pdf/SKILL.md` (the sibling PDF renderer; shared relative-image convention).
- `skills/yf-markdown-lint/SKILL.md` (the lint axis, ML010 flags bare CriticMarkup in prose).
- Root `SPEC.md` §MDHTML and `GUARDRAILS.md` (GR-011).
