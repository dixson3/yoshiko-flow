`yf-markdown-format` is the **write-in-place** counterpart of
[`yf-markdown-lint`](/skills/yf-markdown-lint/). Where the linter *flags*
non-conforming GFM, this skill *fixes* it. The two are the two sides of one set
of conventions: the linter validates and never rewrites; this skill owns the
content-altering axis the linter deliberately refuses. It runs two transforms
today, structured so future GFM-conforming transforms drop in beside them:

- **Table alignment** — normalizes every pipe table to uniform-width, explicit-marker GFM.
- **Wiki-link migration** — rewrites Obsidian `[[…]]` and `![[…]]` into GFM links and images.

## When it fires

Invoke `/yf-markdown-format` when you want Markdown rewritten to conform, not just
checked:

- aligning the pipe tables in a file or a tree;
- migrating an Obsidian vault's `[[wiki-links]]` to portable GFM links;
- gating a repo in CI so a mis-aligned table fails the build.

Skip it to *validate* Markdown (that is [`yf-markdown-lint`](/skills/yf-markdown-lint/))
or to *render* it to [PDF](/skills/yf-markdown-pdf/) or
[HTML](/skills/yf-markdown-html/). This skill only rewrites the source.

## Opt-in, never an always-on autofix

A skill that rewrites files in place is a larger footgun than a linter's flag, so
there is **no always-on on-edit autofix**. The read-only `--check` gate is the
default CI use, and every in-place write is explicit. A repo that wants on-edit
autofix opts in by placing a `.markdown-format-on-edit` marker at its root,
mirroring the lint skill's `.markdown-lint-on-edit`. Absent that marker, the skill
never fires on edit — it runs only when invoked.

## Table alignment

The table aligner reflows every GFM pipe table so each column is padded to a
uniform display width, pipe-delimited, and its delimiter row carries an explicit
alignment marker: `:---` left, `:--:` center, `---:` right. A column with no
marker in the source defaults to explicit **left**. Existing center and right
markers are preserved, and cell text is justified to match its column.

It has three mutually-exclusive modes:

| Mode | Effect |
| :--- | :--- |
| `--check` | Read-only gate. Exits **1** and lists offending files if any table would change; exits **0** with `all tables strictly aligned` otherwise. Mutates nothing. |
| `--write` | Rewrites changed files in place. Idempotent — a second run over an aligned file is a zero-diff no-op. |
| bare (no mode flag) | Prints the normalized document to stdout, touching no file. |

Two properties keep the aligner safe to run in CI:

- **It is East-Asian-width aware.** Characters classified Wide or Fullwidth by
  Unicode count as two display columns, so CJK and fullwidth cells align visually.
- **It leaves fenced code untouched.** A pipe line inside a ` ``` ` or `~~~` fence
  is never mistaken for a table. A table is recognized only as a pipe line
  immediately followed by a valid delimiter row of equal column count.

The `--check` finding output reports at **file granularity** — it names each file
whose tables are not strictly aligned but does not track a per-table line number.
The output is line-oriented so it greps cleanly in CI:

```text
md_table_align: tables not strictly aligned in:
  docs/report.md
  notes/table.md
```

A clean run prints `md_table_align: all tables strictly aligned` and exits 0.

## Wiki-link migration

The migrator is a one-time Obsidian-to-GFM pass. It rewrites `[[target]]`,
`[[target|alias]]`, `[[target#heading]]`, `[[#heading]]`, and embeds `![[embed]]`
into standard Markdown links and images with relative paths and GFM-slugified
anchors. Four properties define it:

- **Code-aware.** Wiki-link syntax inside YAML frontmatter, fenced code blocks,
  and inline-code spans is never rewritten, so docs that *describe* wiki-link
  syntax survive verbatim.
- **Best-effort resolution.** Bare basenames resolve vault-wide (same directory
  first, then a shortest-path tie-break); slash-bearing targets resolve as
  vault-relative paths. An unresolved or ambiguous link is still converted
  best-effort and surfaced in the report rather than aborting the run.
- **Idempotent.** Re-running over an already-migrated tree — one with no remaining
  `[[…]]` — makes no further change.
- **Report-driven, not gate-driven.** It always exits 0. `--report FILE` writes
  the full breakdown of unresolved, ambiguous, and bad-anchor cases, and a summary
  always prints to stdout.

Run it in `--dry-run` first to see the rewrites it would make against a
`--vault-root`, then run it in place once you are satisfied.

## Requirements

`uv` on PATH. Both scripts are stdlib-only and run through `uv run`. No other
tools, no `init` step, and no config.
