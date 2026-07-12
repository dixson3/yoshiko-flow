# Upstream #85 — yf-markdown-lint: absorb md_table_align.py (strict GFM table alignment)

- **URL:** https://github.com/dixson3/yoshiko-flow/issues/85
- **State:** OPEN
- **Labels:** (none)

---

## Summary

Fold the strict GFM **table aligner** into the `yf-markdown-lint` skill so table
alignment is enforced by the skill itself, instead of living as a per-repo vendored
script (`scripts/md_table_align.py`).

## Motivation

`yf-markdown-lint` validates GFM table *structure* (ML005/ML008) but does **not**
enforce column alignment. Alignment is currently handled by a separate
`md_table_align.py` that has to be copied into each repo that wants it:

- Obsidian vault (`dixson3/obsidian-primary`) — `scripts/md_table_align.py`, referenced by AGENTS.md
- `dixson3/d3-pxe` — just vendored a copy (`scripts/md_table_align.py`) to be self-sufficient

Every new repo that adopts the markdown conventions re-vendors the same script. It
should ship with the skill.

## What the tool does

Normalizes every pipe table so columns are uniform-width and pipe-aligned, with
**explicit** alignment markers always present:

- left -> `:---`, center -> `:--:`, right -> `---:`
- preserves existing center/right markers; unmarked columns default to explicit left
- justifies cell text to the column alignment
- skips fenced code blocks (``` and `~~~`)
- East-Asian-width aware (wide/fullwidth glyphs count as 2)

Modes: `--check PATH...` (exit 1 if any file would change — lint gate), `--write PATH...`
(rewrite in place, idempotent), or bare `PATH...` (print normalized to stdout).

Reference implementation: `dixson3/obsidian-primary:scripts/md_table_align.py` (~6 KB,
stdlib-only, no external deps).

## Proposed work

- [ ] Move `md_table_align.py` under the `yf-markdown-lint` skill's `scripts/` (PEP 723 header if any deps, though it is currently stdlib-only)
- [ ] Wire an alignment rule into the linter (e.g. a new `ML0xx` "table not aligned") so `--check` participates in the authoring-time subset and/or the full audit
- [ ] Expose a `--write`/autofix path consistent with the skill's existing invocation
- [ ] Update the always-loaded `yf-markdown-lint` trigger rule + SKILL.md to document alignment as part of the skill (so consumers stop vendoring the script)
- [ ] Note the migration for existing consumers (vault AGENTS.md, d3-pxe AGENTS.md) so they can drop the vendored copy once the skill ships it

## Consumers to update after landing

- `dixson3/obsidian-primary` — drop `scripts/md_table_align.py`, point AGENTS.md at the skill
- `dixson3/d3-pxe` — drop the vendored `scripts/md_table_align.py`, point AGENTS.md at the skill
