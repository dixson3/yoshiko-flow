---
name: yf-markdown-lint
skill-group: markdown
depends-on-tool: [uv]
depends-on-skill: []
description: >
  Conventional GitHub-Flavored-Markdown linter. Checks that documents are valid
  GFM with well-formed, resolvable links — no Obsidian wiki-links (`[[...]]`) or
  embeds (`![[...]]`), valid relative links/anchors, and consistent tables.
  TRIGGER when: /yf-markdown-lint invoked; checking markdown validity; verifying a
  generated/edited `.md` file is clean GFM; after a generator skill writes
  markdown. SKIP for: non-markdown files; Obsidian-specific wiki-link tooling
  (plain GFM is the convention this linter enforces).
---

# yf-markdown-lint

Lint markdown against conventional GFM rules encoded in
`scripts/markdown_lint.py`. The target dialect is **plain GFM** — Obsidian
wiki-links and embeds are not used.

## Invocation

```
/yf-markdown-lint [<path> ...] [--rules ML001,...] [--format text|json]
```

- No args: lint the current directory tree
- `<path>`: one or more files or directories
- `--rules`: comma-separated subset (default: all)
- `--format json`: machine-readable output

```bash
uv run .claude/skills/yf-markdown-lint/scripts/markdown_lint.py ${ARGS:-.}
```

Exit 1 if any violation is found; report each and explain the rule.

## Rules

| ID | Description |
|:---|:------------|
| ML001 | Obsidian wiki-link `[[...]]` (use a `[text](path)` link) |
| ML002 | Obsidian embed `![[...]]` (use `![alt](path)`) |
| ML003 | Broken relative link (destination file does not exist) |
| ML004 | Broken link anchor (no matching heading in target / this file) |
| ML005 | Malformed GFM table (row column count ≠ delimiter row) |
| ML006 | Empty link destination `[text]()` |
| ML007 | Malformed table delimiter / alignment marker (e.g. `:-:-`) |
| ML008 | Table column lacks an explicit alignment marker (use `:---` / `:--:` / `---:`) |
| ML009 | Embedded renderable-fence source does not compile (e.g. a broken ` ```d2 ` block) |
| ML010 | Bare CriticMarkup construct in prose (`{++ ++}`, `{-- --}`, `{~~ ~> ~~}`, `{== ==}`, `{>> <<}`) |
| ML011 | Image with empty alt text `![](x.png)` (accessibility; a present title never warns) |

**ML009 is opt-in (full-audit only).** It compile-checks the *interior* of a
renderable fence whose class has a validate path — currently ` ```d2 ` (the set is
the shared `_shared/renderable_fences.py` registry). It **shells out** to the
renderer, so it is **excluded from the authoring-time subset** and degrades to a
clean pass when the `d2` binary is absent. ` ```csv ` is renderable but not
compile-checkable, so it is never flagged. See the
[`yf-markdown-pdf`](../yf-markdown-pdf/SKILL.md) skill, which *renders* these same
fences.

**ML010 flags bare CriticMarkup in prose.** The five CriticMarkup constructs —
addition `{++ ++}`, deletion `{-- --}`, substitution `{~~ old ~> new ~~}`,
highlight `{== ==}`, and comment `{>> <<}` — render as literal braces (or, worse,
mangled output) in plain GFM and in the PDF pipeline. ML010 is registry-driven and
**extensible** (the `CRITICMARKUP` table in `scripts/markdown_lint.py`); the
substitution construct fires only when its `~>` separator is present. Inline-code
spans and fenced code blocks are exempt, so documentation that *describes*
CriticMarkup in code (as this paragraph does) is not flagged. ML010 is part of the
authoring-time subset (it does not shell out).

**ML011 warns on images with empty alt text** (`![](x.png)`) as an accessibility
check. It fires **only on images** (a leading `!`), never on an empty-text link
`[](x)`. The blessed two-field image convention is `![alt](src "title")` — `alt`
is the accessibility description, `title` the print/figure caption — so a **present
title never warns** (`![alt](src "title")` and `![](src "title")` are both clean).
ML011 is a full-audit rule, not part of the on-edit authoring subset.

Frontmatter, fenced code blocks, and inline code spans are exempt from the
link/wiki-link checks (so docs that *describe* wiki-link syntax aren't flagged).
Anchors are validated with GitHub heading-slug rules (lowercase, punctuation
stripped, spaces→hyphens, duplicate `-N` suffixes).

## Table authoring (GFM)

Use **pipe tables** only — pandoc grid/multiline tables render as literal text in
Obsidian and GitHub. For a wide table, split it into narrower ones rather than
switching format.

- **Alignment:** `:--` left, `:-:` center, `--:` right — supported by GFM,
  Obsidian, and pandoc. Right-align numerics, center short categorical/flag
  columns, left for text. **ML008 requires an explicit marker on every column** —
  a bare `---` (no colon) is flagged. Per-column dash *counts* stay free (variable
  widths), so the PDF width-tuning below survives.
- **In-cell line breaks:** use `<br>` for intentional wrapping inside a cell
  (renders in GFM, Obsidian, and pandoc). A literal newline can't occur inside a
  pipe-table row, so `<br>` is the only portable break.
- **PDF column width** is tuned by the separator's dash counts when rendering
  via the [`yf-markdown-pdf`](../yf-markdown-pdf/SKILL.md) skill (invisible to Obsidian
  and GitHub). When adding `:` markers, keep each segment's length fixed so those
  tuned widths survive.

When ML007 fires on a malformed delimiter, that table fails to parse, so ML005
(cell-count) checks are suppressed for its remaining rows — fix the delimiter and
re-lint to surface any further table issues.

## Lint on edit

Two ways to lint every `.md` as it changes. Both run only the authoring-time
rules (wiki-links, embeds, tables, empty links, CriticMarkup) and skip link/anchor
resolution (ML003/ML004) to stay fast; run the full set (no `--rules`) for a
deliberate link audit (which also surfaces ML011 empty-alt).

**Portable (preferred) — the always-loaded trigger rule.** `protocols/MARKDOWN_LINT.md`
ships with the skill and is installed to the rules surface by `install.sh`. It is
a **silent no-op unless the repo opts in** by placing a `.markdown-lint-on-edit`
marker file at its root; with the marker present, the agent lints each changed
`.md` on edit. This works across harnesses and travels with the skill install.

**Claude-Code-native (alternative) — a `FileChanged` hook.** Hand-wire it in
`.claude/settings.json`:

```bash
uv run .claude/skills/yf-markdown-lint/scripts/markdown_lint.py "$CLAUDE_FILE_PATHS" --rules ML001,ML002,ML005,ML006,ML007,ML008,ML010
```

This hook is not managed by the installer — edit `settings.json` to add, change,
or remove it. Use **one** of the two mechanisms, not both, to avoid double-linting.

---
MIT © 2026 James Dixson <dixson3@gmail.com>, Yoshiko Studios LLC
