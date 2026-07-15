# SPEC — Markdown Lint (`yf-markdown-lint`)

> **Status: Active (reference exemplar).** Worked example of the per-skill SPEC schema for the `yf-markdown-lint` skill (shipped). Requirements use RFC-2119 "shall".

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
- **REQ-MDLINT-002a** *(testable)* ML003 shall strip an optional GFM **title** from a link/image
  destination before path resolution — a destination of the form `path "title"` (also `path
  'title'` or `path (title)`) resolves on `path` only. Thus a titled image `![alt](path "caption")`
  is **not** flagged when `path` exists; the caption is not folded into the resolved target.
- **REQ-MDLINT-003** *(testable)* it shall flag malformed GFM tables — row column count ≠ delimiter
  row (ML005) — and malformed delimiter/alignment markers, e.g. `:-:-` (ML007).
- **REQ-MDLINT-003a** *(testable)* it shall flag a table delimiter-row column that lacks an explicit
  alignment marker — i.e. a bare `---` cell with no leading/trailing `:` (ML008) — so every column
  declares its alignment.
- **REQ-MDLINT-004** *(testable)* it shall flag empty link destinations `[text]()` (ML006).
- **REQ-MDLINT-006** *(testable)* it shall flag bare **CriticMarkup** constructs in prose (ML010).
  The rule consumes a documented, extensible registry of the **five** CriticMarkup delimiter pairs:
  addition `{++ ++}`, deletion `{-- --}`, substitution `{~~ ~> ~~}`, highlight `{== ==}`, and
  comment `{>> <<}`. The substitution construct fires **only** when the `~>` separator is present
  between the two `~~` markers. Inline-code spans and fenced code blocks are **exempt** (reusing the
  linter's existing inline-code strip and fence tracking), so docs that *describe* CriticMarkup
  syntax in code are not flagged. ML010 is part of the authoring-time subset (REQ-MDLINT-011).
- **REQ-MDLINT-007** *(testable)* it shall warn on images with **empty alt text** (ML011) —
  `![](x.png)`. It fires **only on images** (a leading `!`), never on an empty-text link `[](x)`,
  and a **present title never warns** (`![alt](src "title")` and `![](src "title")` are clean).
- **REQ-MDLINT-005** *(testable)* it shall provide an **opt-in** rule (ML009) that compile-checks the
  interior of a *renderable fence* whose class exposes a validate path — the renderable-fence set is
  the shared `_shared/renderable_fences.py` registry (currently ` ```d2 ` compile-checkable;
  ` ```csv ` renderable but not compile-checkable). ML009 shells out to the renderer and shall
  **degrade to a clean pass** (no finding) when the renderer binary (e.g. `d2`) is absent; it is
  **excluded from the authoring-time subset** (REQ-MDLINT-011). The vendored registry region is the
  single source of truth ML009 consumes.

### 2.2 Invocation & output

- **REQ-MDLINT-010** *(testable)* it shall accept one or more paths and a `--rules ML001,…` subset
  (default: all) and a `--format text|json`.
- **REQ-MDLINT-011** *(testable)* the **authoring-time subset** (ML001, ML002, ML005, ML006, ML007,
  ML008, ML010) shall skip link/anchor resolution (ML003/ML004) and the shell-out compile check
  (ML009) so it is fast enough for on-edit use. ML010 (CriticMarkup, no shell-out) and ML011 are
  cheap; ML010 is included in the on-edit subset, ML011 is a full-audit a11y rule.
- **REQ-MDLINT-012** *(testable)* a clean run shall report `markdown-lint: clean` and exit zero; any
  violation shall exit non-zero.

### 2.3 On-edit trigger

- **REQ-MDLINT-020** the on-edit trigger shall be a **silent no-op unless the repo opts in** via a
  `.markdown-lint-on-edit` marker at its root (an empty marker selects the authoring subset; a
  non-empty marker may override `--rules` or list exclude globs).

## 3. Interfaces

- **CLI / scripts:** `scripts/markdown_lint.py` (the linter, run via `uv`).
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

- A fixture corpus with one file per rule (ML001–ML008, ML010, ML011) asserting the expected
  violation; a clean fixture asserting `clean` + exit 0. The authoring-subset speed/skip behavior
  (REQ-MDLINT-011) asserted by running with `--rules` and confirming ML003/ML004 are not evaluated.
  ML003's title-strip (REQ-MDLINT-002a) is asserted by a regression fixture — `![alt](path
  "caption")` resolves on `path` only. ML010 (REQ-MDLINT-006) is asserted against all five
  CriticMarkup delimiter pairs, the `~>`-required substitution case, and the code-span/fence
  exemptions. ML011 (REQ-MDLINT-007) is asserted to fire on empty-alt images only, never on
  empty-text links, and never when a title is present. ML009 (opt-in, shell-out) is verified
  separately: a broken ` ```d2 ` fence is flagged when `d2` is present, a valid one passes, and the
  rule degrades to clean when `d2` is monkeypatched absent.

## 6. References

- `skills/yf-markdown-lint/SKILL.md` (rule table ML001–ML011, table conventions).
- `_shared/renderable_fences.py` (canonical renderable-fence registry consumed by ML009).
- `protocols/MARKDOWN_LINT.md` (on-edit trigger).
- Root `SPEC.md` §4 (MDLINT) and `GUARDRAILS.md` (GR-004).
