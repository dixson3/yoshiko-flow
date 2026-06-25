# markdown-pdf

Render a `.md` file to PDF via pandoc + xelatex, tuned for Unicode glyphs and
relative image paths. See [SKILL.md](SKILL.md) for the full contract.

## Prerequisites

| Tool | Version | Purpose | Install |
|:-----|:--------|:--------|:--------|
| `uv` | any | Runs the wrapper script (PEP 723) | https://docs.astral.sh/uv/ |
| `pandoc` | any | Markdown → PDF converter | https://pandoc.org/installing.html |
| `xelatex` | any | PDF engine (from a LaTeX distribution) | TeX Live / MacTeX |

Mirrors SKILL.md frontmatter `depends-on-tool: [uv, pandoc, xelatex]`. The script
checks for `pandoc` and `xelatex` and exits with a clear message if either is
missing. No `init` step, no config, no companion rule.

## Install

Installed by the repo-level `install.sh` / `install.py`, which auto-discovers
every `skills/*/` directory (group `markdown`). See the project
[README](../../README.md) for flags. Or per-skill: copy `skills/markdown-pdf` to
`~/.claude/skills/markdown-pdf`.

## Usage

User-invocable. Render one or more Markdown files to PDF:

```bash
uv run .claude/skills/markdown-pdf/scripts/md2pdf.py <input.md> [-o OUT.pdf]
# batch; override font; rotate wide tables to landscape
uv run .claude/skills/markdown-pdf/scripts/md2pdf.py a.md b.md
uv run .claude/skills/markdown-pdf/scripts/md2pdf.py r.md --mainfont "STIX Two Text" --table-font normalsize --landscape-cols 8
# keep ```d2```/```csv``` fences verbatim instead of rendering them
uv run .claude/skills/markdown-pdf/scripts/md2pdf.py r.md --no-render-fences
```

Output defaults to `<input>.pdf` beside the source. Pipeline defaults, font
notes, and the PDF table levers (`--table-font`, dash-width tuning,
`--landscape-cols`, `--columns`) are documented in [SKILL.md](SKILL.md).

**Renderable fences.** By default md2pdf renders a ` ```d2 ` fence to an embedded
vector diagram and a ` ```csv ` fence to a native table (so the source travels
inline in the Markdown), degrading to a verbatim listing if `d2` is absent or a
block fails. **Glyph fallback:** on macOS a `glyph-fallback.tex` header remaps ✅
onto a monochrome ✔ (macOS best-effort; off macOS it degrades to a warning, never a
hard fail). The renderable-fence set is the shared `_shared/renderable_fences.py`
registry. See [SKILL.md](SKILL.md#renderable-fences-d2-csv).

## Phase model

None. This is a tool/reference skill with no phases or state transitions.

## File layout

```text
markdown-pdf/
  SKILL.md            entry point — trigger, invocation, pipeline defaults
  README.md           this file
  scripts/
    md2pdf.py                  pandoc/xelatex wrapper (PEP 723, argparse)
    landscape_wide_tables.lua  render-time filter: rotate wide tables to landscape
    blocks.lua                 render-time filter: d2 fences -> PDF, csv -> table
    glyph-fallback.tex         macOS -H header: remap ✅ color emoji -> monochrome ✔
    test_md2pdf.py             pytest: fence render, no-leak, glyph degrade
```

Requirements (`pandoc` + `xelatex`) and the platform-aware font defaults (macOS
forces Arial Unicode MS / Menlo; off macOS no font is forced, so xelatex falls
back to Latin Modern and warns on missing glyphs — pass `--mainfont` for full
coverage) are documented in [SKILL.md](SKILL.md#pipeline-defaults).

---
MIT © 2026 James Dixson <dixson3@gmail.com>, Yoshiko Studios LLC
