# SPEC — Markdown Lint (`yf-markdown-lint`)

> **Status: DRAFT (primed exemplar).** Worked example of the per-skill SPEC schema
> (`skills/SPEC-TEMPLATE.md`). Operator to review/edit. Composed by the root macro `SPEC.md` §4
> under spec key **MDLINT**.

## 1. Purpose & scope

`yf-markdown-lint` is a conventional GitHub-Flavored-Markdown validator: it checks that a document
is valid GFM with well-formed, resolvable links and tables. It **validates only** — it never
authors, reformats, or rewrites prose. Obsidian wiki-links/embeds are treated as violations (plain
GFM is the enforced convention).

## 2. Requirements (`REQ-MDLINT-NNN`)

### 2.1 Rules

- **REQ-MDLINT-001** *(testable)* the linter shall flag Obsidian wiki-links `[[...]]` (ML001) and
  embeds `![[...]]` (ML002).
- **REQ-MDLINT-002** *(testable)* it shall flag broken relative links (ML003) and broken link
  anchors with no matching heading (ML004).
- **REQ-MDLINT-003** *(testable)* it shall flag malformed GFM tables — row column count ≠ delimiter
  row (ML005) — and malformed delimiter/alignment markers, e.g. `:-:-` (ML007).
- **REQ-MDLINT-004** *(testable)* it shall flag empty link destinations `[text]()` (ML006).

### 2.2 Invocation & output

- **REQ-MDLINT-010** *(testable)* it shall accept one or more paths and a `--rules ML001,…` subset
  (default: all) and a `--format text|json`.
- **REQ-MDLINT-011** *(testable)* the **authoring-time subset** (ML001, ML002, ML005, ML006, ML007)
  shall skip link/anchor resolution (ML003/ML004) so it is fast enough for on-edit use.
- **REQ-MDLINT-012** *(testable)* a clean run shall report `markdown-lint: clean` and exit zero; any
  violation shall exit non-zero.

### 2.3 On-edit trigger

- **REQ-MDLINT-020** the on-edit trigger shall be a **silent no-op unless the repo opts in** via a
  `.markdown-lint-on-edit` marker at its root (an empty marker selects the authoring subset; a
  non-empty marker may override `--rules` or list exclude globs).

## 3. Interfaces

- **CLI / scripts:** `scripts/markdown_lint.py` (the linter, run via `uv`); `scripts/convert_wikilinks.py`
  (migration helper: `[[x]]` → `[x](x)`).
- **Companion rule:** `protocols/MARKDOWN_LINT.md` (the always-loaded on-edit trigger contract);
  no `manifest.json` today (candidate to add under the macro spec's rule-hash model).
- **Config / state:** repo-root `.markdown-lint-on-edit` marker; no `.local.json`/`.yf/` state.

## 4. Guardrails (`GR-MDLINT-NNN`)

- **GR-MDLINT-001** *Drift:* auto-formatting or rewriting prose/tables. *Rule:* the linter
  **validates GFM only**; it never authors, reformats, or aligns content. *Why:* table
  alignment/sizing is a separate concern (upstream #20/#21), not a lint side effect.
- **GR-MDLINT-002** *Drift:* enforcing Obsidian conventions. *Rule:* plain GFM is the target;
  wiki-links/embeds are violations, not supported syntax.

## 5. Verification

- A fixture corpus with one file per rule (ML001–ML007) asserting the expected violation; a clean
  fixture asserting `clean` + exit 0. The authoring-subset speed/skip behavior (REQ-MDLINT-011)
  asserted by running with `--rules` and confirming ML003/ML004 are not evaluated.

## 6. References

- `skills/yf-markdown-lint/SKILL.md` (rule table ML001–ML007, table conventions).
- `protocols/MARKDOWN_LINT.md` (on-edit trigger).
- Root `SPEC.md` §4 (MDLINT) and `GUARDRAILS.md` (GR-004).
