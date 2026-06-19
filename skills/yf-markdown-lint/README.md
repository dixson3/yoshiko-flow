# markdown-lint

Lint markdown as conventional GitHub-Flavored Markdown — no Obsidian
wiki-links/embeds, resolvable relative links/anchors, well-formed tables. See
[SKILL.md](SKILL.md) for the rule list, table-authoring conventions, and the
optional `FileChanged` hook.

## Prerequisites

| Tool | Version | Purpose | Install |
|:-----|:--------|:--------|:--------|
| `uv` | any | Runs the linter scripts (PEP 723) | https://docs.astral.sh/uv/ |

Mirrors SKILL.md frontmatter `depends-on-tool: [uv]`. No `init` step, no config,
no companion rule.

## Install

Installed by the repo-level `install.sh` / `install.py`, which auto-discovers
every `skills/*/` directory (group `markdown`) and copies the skill's
`protocols/*.md` companion rule to the rules surface. See the project
[README](../../README.md) for flags. Or per-skill: copy `skills/markdown-lint` to
`~/.claude/skills/markdown-lint`.

The companion rule `protocols/MARKDOWN_LINT.md` is the portable lint-on-edit
trigger: a **silent no-op unless** the repo opts in with a `.markdown-lint-on-edit`
marker at its root (see SKILL.md "Lint on edit").

## Usage

User-invocable. Lint files or directories, optionally scoping the rule set:

```
/markdown-lint [<path> ...] [--rules ML001,...] [--format text|json]
```

```bash
uv run .claude/skills/markdown-lint/scripts/markdown_lint.py ${ARGS:-.}
# one-time Obsidian wiki-link -> GFM migration for a tree
uv run .claude/skills/markdown-lint/scripts/convert_wikilinks.py <dir> --vault-root . --report <out.md>
```

Exit 1 on any violation. Rules ML001–ML007 are documented in
[SKILL.md](SKILL.md#rules); the lint-on-edit trigger (portable rule + the
Claude-Code hook alternative) is in [SKILL.md](SKILL.md#lint-on-edit).

## Phase model

None. This is a tool/reference skill with no phases or state transitions.

## File layout

```text
markdown-lint/
  SKILL.md            entry point — rules, table conventions, lint-on-edit
  README.md           this file
  protocols/
    MARKDOWN_LINT.md  always-loaded lint-on-edit trigger (opt-in, portable)
  scripts/
    markdown_lint.py      the GFM linter (PEP 723, argparse)
    convert_wikilinks.py  one-time wiki-link → GFM migration tool
```

---
MIT © 2026 James Dixson <dixson3@gmail.com>, Yoshiko Studios LLC
