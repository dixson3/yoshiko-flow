# markdown-format

The autofix side of `markdown-lint` — rewrites Markdown in place to conform to
plain GFM along the axes the linter flags. Two transforms: strict GFM **table
alignment** and Obsidian→GFM **wiki-link migration**. See [SKILL.md](SKILL.md)
for the full contract, the `--check` finding-output convention, and the opt-in
model.

## Prerequisites

| Tool | Version | Purpose | Install |
|:-----|:--------|:--------|:--------|
| `uv` | any | Runs both scripts (PEP 723, stdlib-only) | https://docs.astral.sh/uv/ |

Mirrors SKILL.md frontmatter `depends-on-tool: [uv]`. No `init` step, no config,
no companion rule.

## Install

Installed by the repo-level `install.sh` / `install.py`, which auto-discovers
every `skills/*/` directory (group `markdown`). See the project
[README](../../README.md) for flags. Or per-skill: copy `skills/markdown-format`
to `~/.claude/skills/markdown-format`.

This skill is **opt-in per repo** and has **no always-on on-edit autofix** — a
write-in-place skill is never default-on. See [SKILL.md](SKILL.md#opt-in--never-an-always-on-autofix).

## Usage

User-invocable. Two independent transforms.

**Table alignment** (`scripts/md_table_align.py`) — `--check` gate, `--write`
idempotent in-place autofix, or bare stdout:

```bash
# CI / pre-commit gate: exit 1 if any table would change, mutating nothing
uv run .claude/skills/yf-markdown-format/scripts/md_table_align.py --check PATH...
# idempotent in-place autofix (running twice is a no-op)
uv run .claude/skills/yf-markdown-format/scripts/md_table_align.py --write PATH...
# normalized document to stdout
uv run .claude/skills/yf-markdown-format/scripts/md_table_align.py PATH...
```

`--check` reports at **file granularity** (no per-table line number): it lists
the offending files and exits 1, or prints `all tables strictly aligned` and
exits 0.

**Wiki-link migration** (`scripts/convert_wikilinks.py`) — Obsidian `[[…]]` /
`![[…]]` to GFM links/images; dry-run or in-place; always exits 0:

```bash
# dry-run: report the rewrites it WOULD make, touching no files
uv run .claude/skills/yf-markdown-format/scripts/convert_wikilinks.py <dir>... --vault-root DIR --dry-run
# in-place migration + a full conversion report
uv run .claude/skills/yf-markdown-format/scripts/convert_wikilinks.py <dir>... --vault-root DIR --report report.md
```

Both scripts are documented in [SKILL.md](SKILL.md): the three alignment modes,
East-Asian-width awareness, fenced-code skip, and the code-aware,
best-effort-resolving, idempotent wiki-link migration.

## Migrating from a vendored copy

Some downstream repos (`dixson3/obsidian-primary`, `dixson3/d3-pxe`) currently
**vendor** their own `scripts/md_table_align.py` — a per-repo copy. Now that this
skill ships the canonical `md_table_align.py` (byte-identical origin), those repos
can:

- **delete** the vendored `scripts/md_table_align.py` copy (and any
  `convert_wikilinks.py` reference), and
- **point their `AGENTS.md` at this skill** instead of the local copy.

This is a **downstream consequence recorded here as guidance** — this repo does
**not** execute any change in those other repos. Migrate each consumer on its own
schedule.

## Phase model

None. This is a tool/reference skill with no phases or state transitions.

## File layout

```text
markdown-format/
  SKILL.md            entry point — both transforms, --check convention, opt-in
  README.md           this file
  SPEC.md             REQ-MDFMT-* contract + GR-MDFMT-* guardrails
  scripts/
    md_table_align.py         strict GFM table aligner (--check / --write / stdout)
    convert_wikilinks.py      Obsidian -> GFM wiki-link migrator (dry-run / in-place)
    test_md_table_align.py    pytest: align, check-gate, idempotent-write, CJK width, fence skip
    test_convert_wikilinks.py pytest: dry-run vs write, fence/frontmatter protection, idempotence
```

Requirement (`uv` only; both scripts are stdlib-only PEP 723) and the opt-in,
never-always-on model are documented in [SKILL.md](SKILL.md).

---
MIT © 2026 James Dixson <dixson3@gmail.com>, Yoshiko Studios LLC
