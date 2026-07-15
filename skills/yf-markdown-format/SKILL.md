---
name: yf-markdown-format
skill-group: markdown
depends-on-tool: [uv]
depends-on-skill: []
description: >
  The autofix side of `yf-markdown-lint` — rewrites Markdown in place to conform
  to plain GFM along the axes the linter flags. Owns two transforms: strict GFM
  table alignment (`--check` gate / `--write` idempotent autofix / bare stdout)
  and Obsidian to GFM wiki-link migration. TRIGGER when: /yf-markdown-format
  invoked; aligning GFM tables; converting `[[wiki-links]]` to GFM links; a
  write-in-place markdown fix. SKIP for: validating markdown (use
  `yf-markdown-lint`); rendering to PDF/HTML (use `yf-markdown-pdf` /
  `yf-markdown-html`). OPT-IN per repo — never an always-on autofix.
---

# yf-markdown-format

The **write-in-place** counterpart of [`yf-markdown-lint`](../yf-markdown-lint/SKILL.md).
Where the linter *flags* non-conforming GFM, this skill *fixes* it — the two are
the two sides of the same conventions. This skill owns the **content-altering**
axis the linter deliberately refuses (`GR-MDLINT-001` — the linter never
rewrites). Two transforms today, structured so future GFM-conforming transforms
drop in beside them:

- **Table alignment** (`scripts/md_table_align.py`) — normalizes every pipe
  table to uniform-width, explicit-marker (`:---` / `:--:` / `---:`) GFM.
- **Wiki-link migration** (`scripts/convert_wikilinks.py`) — rewrites Obsidian
  `[[…]]` / `![[…]]` into GFM links/images.

## Table alignment

`md_table_align.py` reflows every GFM pipe table so each column is padded to a
uniform display width, pipe-delimited, and its delimiter row carries an
**explicit** alignment marker (`:---` left, `:--:` center, `---:` right). A
column with no marker in the source defaults to explicit **left**; existing
center/right markers are preserved. Three mutually-exclusive modes:

```bash
# CI / pre-commit GATE — exit 1 if any file's tables would change, mutating nothing
uv run .claude/skills/yf-markdown-format/scripts/md_table_align.py --check PATH...
# idempotent in-place autofix — rewrite changed files (running twice is a no-op)
uv run .claude/skills/yf-markdown-format/scripts/md_table_align.py --write PATH...
# no mode flag — print the normalized document to stdout, touching nothing
uv run .claude/skills/yf-markdown-format/scripts/md_table_align.py PATH...
```

- **`--check` is the read-only gate.** It exits **1** and lists the offending
  files if any table would change, exits **0** with `all tables strictly aligned`
  otherwise. It mutates nothing — this is the safe default for CI and pre-commit.
- **`--write` is idempotent.** Running it a second time over an already-aligned
  file produces zero further change (a fixed point); `--check` on that file then
  exits 0.
- **East-Asian-width aware.** Wide (`W`) / Fullwidth (`F`) characters count as 2
  display columns, so CJK / fullwidth cells align visually.
- **Fenced code is untouched.** Pipe lines inside a ` ``` ` or `~~~` fence are
  never mistaken for a table; a table is recognized only as a pipe line
  immediately followed by a valid delimiter row of equal column count.

### `--check` finding output

The aligner reports at **file granularity** — it names each file whose tables
are not strictly aligned; it does **not** track a per-table line number. A clean
run reports all-aligned. The output is line-oriented so it greps cleanly in CI:

```text
md_table_align: tables not strictly aligned in:
  docs/report.md
  notes/table.md
```

(exit 1). A clean run prints `md_table_align: all tables strictly aligned`
(exit 0).

## Wiki-link migration

`convert_wikilinks.py` is a one-time Obsidian→GFM migrator: it rewrites
`[[target]]`, `[[target|alias]]`, `[[target#heading]]`, `[[#heading]]`, and
embeds `![[embed]]` into standard markdown links / images with relative paths and
GFM-slugified anchors.

```bash
# dry-run — report the rewrites it WOULD make, touching no files
uv run .claude/skills/yf-markdown-format/scripts/convert_wikilinks.py <dir>... --vault-root DIR --dry-run
# in-place — rewrite the .md files under <dir>, resolving against the vault root
uv run .claude/skills/yf-markdown-format/scripts/convert_wikilinks.py <dir>... --vault-root DIR
# write a full conversion report (unresolved / ambiguous / bad-anchor breakdown)
uv run .claude/skills/yf-markdown-format/scripts/convert_wikilinks.py <dir>... --vault-root DIR --report report.md
```

- **Code-aware.** Wiki-link syntax inside YAML frontmatter, fenced code blocks,
  and inline-code spans is **never** rewritten, so docs that *describe* wiki-link
  syntax survive verbatim.
- **Best-effort resolution.** Bare basenames resolve vault-wide (same-dir first,
  then shortest-path tie-break); slash-bearing targets resolve as vault-relative
  paths. Unresolved / ambiguous links are still converted best-effort and
  surfaced in the report rather than aborting the run.
- **Idempotent.** Re-running over an already-migrated tree (no remaining `[[…]]`)
  makes no further change.
- **Report-driven, not gate-driven.** It always exits 0; `--report FILE` writes
  the full breakdown (unresolved, ambiguous, bad/missing anchors, block refs,
  downgraded note embeds), and a summary always prints to stdout.

## Opt-in — never an always-on autofix

This skill is **invoke-only** and **opt-in per repo**. A skill that rewrites
files in place is a larger footgun than a linter's flag, so there is **no
always-on on-edit autofix** — `--check` (the read-only gate) is the default CI
use, and `--write` is always explicit.

If a repo wants on-edit autofix, it opts in **explicitly** with a
`.markdown-format-on-edit` marker file at its root (mirroring
[`yf-markdown-lint`](../yf-markdown-lint/SKILL.md)'s `.markdown-lint-on-edit`
opt-in). Absent that marker, this skill never fires on edit — it runs only when
invoked. This is the `GR-MDFMT-002` guardrail: the write-in-place path is
marker-gated, never default-on.

## Requirements

`uv` on PATH (both scripts are stdlib-only, PEP 723, run via `uv run`). No other
tools, no `init` step, no config.

See [SPEC.md](SPEC.md) for the full `REQ-MDFMT-*` contract (the `--check` /
`--write` / bare modes, the idempotent-autofix guarantee, East-Asian width, and
the wiki-link migration contract) and the `GR-MDFMT-*` guardrails.

---
MIT © 2026 James Dixson <dixson3@gmail.com>, Yoshiko Studios LLC
