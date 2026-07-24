`yf-markdown-lint` reads a Markdown file and reports where it stops being plain
GitHub-Flavored Markdown. The target dialect is **plain GFM** — no Obsidian
wiki-links, no embeds, resolvable relative links and anchors, well-formed tables.
It **validates only**. It never reformats, aligns, or rewrites the source; that
content-altering job belongs to [`yf-markdown-format`](/skills/yf-markdown-format/),
its autofix counterpart.

## When it fires

Reach for the linter whenever a `.md` file needs to be verified as clean GFM:

- you invoke `/yf-markdown-lint` on a path, a directory, or the whole tree;
- a generator skill (`/yf-plan`, `/yf-research`, `/yf-diagram-authoring`) has just
  written Markdown and you want it checked before it lands;
- a repo opts into linting on every edit (see [Linting on edit](#linting-on-edit)).

Skip it for non-Markdown files, and skip it if your convention is Obsidian
wiki-links rather than plain GFM — this linter treats those as violations, not
supported syntax.

## The rules

Each rule has a stable `ML0NN` id, so you can scope a run to a subset or read a
finding back to its rule. Eleven rules ship today:

| ID | Flags |
| :--- | :--- |
| ML001 | Obsidian wiki-link `[[...]]` — use a `[text](path)` link |
| ML002 | Obsidian embed `![[...]]` — use `![alt](path)` |
| ML003 | Broken relative link — the destination file does not exist |
| ML004 | Broken anchor — no matching heading in the target or this file |
| ML005 | Malformed table — a row's column count differs from the delimiter row |
| ML006 | Empty link destination `[text]()` |
| ML007 | Malformed delimiter or alignment marker, e.g. `:-:-` |
| ML008 | A table column with no explicit alignment marker (needs `:--`, `:-:`, or `--:`) |
| ML009 | A renderable fence whose interior does not compile, e.g. a broken ` ```d2 ` block |
| ML010 | A bare CriticMarkup construct in prose (`{++ ++}`, `{-- --}`, `{~~ ~> ~~}`, `{== ==}`, `{>> <<}`) |
| ML011 | An image with empty alt text `![](x.png)` — an accessibility check |

Frontmatter, fenced code blocks, and inline-code spans are exempt from the
link and wiki-link checks, so a document that *describes* wiki-link or
CriticMarkup syntax in a code span is never flagged for using it. Anchors are
validated with GitHub's heading-slug rules: lowercase, punctuation stripped,
spaces to hyphens, and a `-N` suffix on a duplicate.

## Two rules worth knowing

**ML010 catches CriticMarkup that would leak into your output.** The five
CriticMarkup constructs — addition, deletion, substitution, highlight, comment —
render as literal braces (or mangled text) in plain GFM and in the PDF pipeline.
ML010 is registry-driven and extensible. The substitution construct fires only
when its `~>` separator is present. Because inline-code and fenced code are
exempt, prose that documents CriticMarkup in a code span survives. If you *want*
CriticMarkup rendered rather than flagged, [`yf-markdown-html`](/skills/yf-markdown-html/)
turns it into styled HTML on an opt-in flag.

**ML009 compile-checks a renderable fence and shells out to do it.** It runs the
real renderer over the interior of a ` ```d2 ` block, so it is excluded from the
fast authoring subset and degrades to a clean pass when the `d2` binary is
absent. It reads the same `_shared/renderable_fences.py` registry that
[`yf-markdown-pdf`](/skills/yf-markdown-pdf/) uses to *render* those fences, so
the check and the render cannot drift apart.

## Table authoring

The linter enforces one table dialect: **pipe tables** only. Pandoc grid and
multiline tables render as literal text in Obsidian and on GitHub, so for a wide
table, split it into narrower ones rather than switching format.

- **Alignment markers are required.** ML008 flags any column whose delimiter
  cell is a bare `---` with no colon. Write `:--` for left, `:-:` for center,
  `--:` for right. Right-align numerics, center short flag columns, left for text.
- **Dash counts stay free.** The number of dashes per column is unconstrained,
  which is what lets `yf-markdown-pdf` tune PDF column widths from the separator
  row without the linter objecting.
- **Break a cell with `<br>`.** A literal newline cannot occur inside a pipe-table
  row, so `<br>` is the portable in-cell break across GFM, Obsidian, and pandoc.

When ML007 fires on a malformed delimiter, that table no longer parses, so ML005
cell-count checks are suppressed for its remaining rows. Fix the delimiter and
re-lint to surface any further table issues.

## Output and exit code

A clean run reports `markdown-lint: clean` and exits zero. Any violation exits
non-zero, and each finding names its file, its rule id, and an explanation.
`--format json` emits the same findings machine-readable for a CI gate, and
`--rules ML001,ML005` scopes a run to a chosen subset.

## Linting on edit

Two mechanisms lint every `.md` as it changes. Both run a fast authoring subset —
ML001, ML002, ML005, ML006, ML007, ML008, ML010 — and skip link and anchor
resolution (ML003/ML004) and the shell-out compile check (ML009) so they stay
quick. Run the full set (no `--rules`) for a deliberate link audit, which also
surfaces the ML011 empty-alt check.

- **Portable trigger rule (preferred).** The skill ships an always-loaded rule
  that is a **silent no-op unless the repo opts in** by placing a
  `.markdown-lint-on-edit` marker file at its root. With the marker present, each
  changed `.md` is linted on edit. This travels with the skill across harnesses.
- **Claude Code hook (alternative).** Hand-wire a `FileChanged` hook in
  `.claude/settings.json` that runs the same subset.

Use one mechanism, not both, so a file is not linted twice.
