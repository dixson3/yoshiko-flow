# markdown-html

Render a `.md` file to a single, self-contained HTML file via pandoc — standalone
document, all resources embedded, a default stylesheet, self-contained math, and
opt-in CriticMarkup. See [SKILL.md](SKILL.md) for the full contract.

## Prerequisites

| Tool | Version | Purpose | Install |
|:-----|:--------|:--------|:--------|
| `uv` | any | Runs the wrapper script (PEP 723) | https://docs.astral.sh/uv/ |
| `pandoc` | any | Markdown → HTML converter | https://pandoc.org/installing.html |

Mirrors SKILL.md frontmatter `depends-on-tool: [uv, pandoc]`. The script checks for
`pandoc` and exits with a clear message if it is missing. No `xelatex` needed (that
is [`yf-markdown-pdf`](../yf-markdown-pdf/SKILL.md)). No `init` step, no config, no
companion rule.

## Install

Installed by the repo-level `install.sh` / `install.py`, which auto-discovers every
`skills/*/` directory (group `markdown`). See the project
[README](../../README.md) for flags. Or per-skill: copy `skills/yf-markdown-html`
to `~/.claude/skills/yf-markdown-html`.

## Usage

User-invocable. Render one or more Markdown files to self-contained HTML:

```bash
uv run .claude/skills/yf-markdown-html/scripts/md2html.py <input.md> [-o OUT.html]
# batch
uv run .claude/skills/yf-markdown-html/scripts/md2html.py a.md b.md
# render CriticMarkup; add a stylesheet; pass extra pandoc flags after `--`
uv run .claude/skills/yf-markdown-html/scripts/md2html.py r.md --criticmarkup --css house.css -- --toc
```

Output defaults to `<input>.html` beside the source. Pipeline defaults, the
default stylesheet, self-contained math, and the opt-in CriticMarkup contract are
documented in [SKILL.md](SKILL.md).

**Self-contained.** `pandoc --standalone --to=html5 --embed-resources` inlines
every resource — images become `data:` URIs, the stylesheet embeds in a `<style>`
block, and math renders as MathML (no CDN) — so the output opens offline with no
external host. **CriticMarkup** (opt-in via `--criticmarkup`) renders the five
constructs to styled `<ins>`/`<del>`/`<mark>`/`<span>`; note the tradeoff that it
disables real GFM `~~strikethrough~~` while on. See
[SKILL.md](SKILL.md#criticmarkup-opt-in).

## Phase model

None. This is a tool/reference skill with no phases or state transitions.

## File layout

```text
markdown-html/
  SKILL.md            entry point — trigger, invocation, pipeline defaults
  SPEC.md             per-skill requirements (REQ-MDHTML-*) + guardrails
  README.md           this file
  scripts/
    md2html.py        pandoc wrapper (PEP 723, argparse)
    criticmarkup.lua  opt-in Inlines filter: CriticMarkup -> styled HTML
    default.css       broad-coverage default stylesheet (incl. cm-* classes)
    test_md2html.py   pytest: render, embed, math, CriticMarkup, arg constraints
```

Requirements (`pandoc`) and the pipeline defaults (standalone, embed-resources,
default stylesheet, MathML math, opt-in CriticMarkup) are documented in
[SKILL.md](SKILL.md#self-contained-output).

---
MIT © 2026 James Dixson <dixson3@gmail.com>, Yoshiko Studios LLC
