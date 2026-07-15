# SPEC — Markdown Format (`yf-markdown-format`)

> **Status: Active.** Per-skill SPEC for content-altering Markdown formatting — the **autofix
> side** of `yf-markdown-lint`. Requirements use RFC-2119 "shall"; composed by the root `SPEC.md`
> macro spec.

## 1. Purpose & scope

`yf-markdown-format` is the **write-in-place** counterpart of `yf-markdown-lint`: it rewrites
Markdown to conform to plain GFM along the axes the linter only *flags*. It owns **two** transforms:

1. **Table alignment** — normalizes every pipe table so columns are uniform-width, pipe-aligned,
   and carry an explicit alignment marker (`:---` / `:--:` / `---:`).
2. **Obsidian→GFM wiki-link migration** — rewrites `[[target]]` / `![[embed]]` (and aliased/
   anchored forms) into standard GFM links/images.

**In scope:** the `--check` gate, the `--write` idempotent in-place autofix, and bare normalized
stdout for table alignment; the code-aware wiki-link migration. Future GFM-conforming transforms
drop in beside these on the same content-altering axis.

**Out of scope:** *validating* GFM (that is `yf-markdown-lint`); rendering to PDF/HTML (those are
`yf-markdown-pdf` / `yf-markdown-html`); rewriting prose content beyond the two declared
transforms.

## 2. Requirements (`REQ-MDFMT-NNN`)

### 2.1 Table alignment

- **REQ-MDFMT-001** *(testable)* the table aligner shall normalize every GFM pipe table so each
  column is padded to a uniform display width, pipe-delimited (`| … | … |`), and its delimiter row
  carries an **explicit** alignment marker: left `:---`, center `:--:`, right `---:`. A column with
  no marker in the source defaults to explicit **left** (`:---`); existing center/right markers are
  preserved. Cell text shall be justified to match its column's alignment.
- **REQ-MDFMT-002** *(testable)* it shall expose three mutually-exclusive modes: `--check` (exit
  **1** if any input file would change — the CI / pre-commit gate — exit **0** otherwise, mutating
  nothing), `--write` (rewrite changed files **in place**), and bare (no mode flag: write the
  normalized document to **stdout**).
- **REQ-MDFMT-003** *(testable)* `--write` shall be **idempotent**: running it a second time over
  an already-aligned file produces **no further change** (zero diff, and — per REQ-MDFMT-002 —
  `--check` on that file then exits 0). Normalization is thus a fixed point.
- **REQ-MDFMT-004** *(testable)* cell display width shall be **East-Asian-width-aware**: characters
  classified Wide (`W`) or Fullwidth (`F`) by Unicode East-Asian-width count as **2** columns, all
  others as **1**, so CJK/fullwidth content aligns visually.
- **REQ-MDFMT-005** *(testable)* fenced code blocks (both ` ``` ` and `~~~`) shall be left
  **untouched** — pipe lines inside a fence are never mistaken for a table. A table is recognized
  only as a pipe line immediately followed by a valid delimiter row of equal column count.
- **REQ-MDFMT-006** *(testable)* the `--check` finding output shall report at **file granularity** —
  it names each file whose tables are not strictly aligned (the aligner does not track a per-table
  line number). A clean `--check` reports all-aligned and exits 0.

### 2.2 Wiki-link migration

- **REQ-MDFMT-010** *(testable)* the migrator shall rewrite Obsidian wiki-links to GFM: `[[target]]`,
  `[[target|alias]]`, `[[target#heading]]`, `[[#heading]]`, and embeds `![[embed]]` become standard
  markdown links / images with relative paths and GFM-slugified anchors.
- **REQ-MDFMT-011** *(testable)* it shall be **code-aware**: wiki-link syntax inside YAML
  frontmatter, fenced code blocks, and inline-code spans shall **never** be rewritten (so docs that
  *describe* wiki-link syntax are preserved verbatim).
- **REQ-MDFMT-012** *(testable)* resolution shall follow Obsidian semantics on a **best-effort**
  basis — bare basenames resolve vault-wide (same-dir first, then shortest-path tie-break),
  slash-bearing targets resolve as vault-relative paths; **unresolved/ambiguous** links are still
  converted best-effort and surfaced in an optional report rather than aborting the run.
- **REQ-MDFMT-013** *(testable)* the migration shall be **idempotent**: re-running it over an
  already-migrated tree (no remaining `[[…]]`) makes no further change.
- **REQ-MDFMT-014** it shall support a **dry-run** mode that reports the rewrites it *would* make
  without touching files, distinct from the in-place write.

### 2.3 Invocation & opt-in

- **REQ-MDFMT-020** *(testable)* each script shall accept one or more paths; the aligner's default
  (no mode flag) is bare stdout, and its `--check` / `--write` select the gate / in-place modes.
- **REQ-MDFMT-021** any on-edit autofix trigger shall be a **silent no-op unless the repo opts in**
  via a repo-root marker — a write-in-place skill is **never** an always-on autofix.

## 3. Interfaces

- **CLI / scripts:** `scripts/md_table_align.py` (the table aligner — `--check` / `--write` / bare
  stdout, run via `uv`); `scripts/convert_wikilinks.py` (the Obsidian→GFM migrator — moved here from
  `yf-markdown-lint` by a later plan-026 issue). Both are stdlib-only, run via `uv run`.
- **Companion rule:** an opt-in on-edit trigger rule under `protocols/` if warranted (a marker-gated
  autofix, mirroring `yf-markdown-lint`'s `.markdown-lint-on-edit`), NOT an always-on rule.
- **Config / state:** repo-root opt-in marker for any on-edit autofix; no `.local.json` / `.yf/`
  state.

## 4. Guardrails (`GR-MDFMT-NNN`)

- **GR-MDFMT-001** *Drift:* becoming a general prose rewriter / formatter. *Rule:* this skill
  rewrites Markdown **only** along its declared transforms — GFM **table alignment** and
  **Obsidian→GFM wiki-link migration**. *Why:* it is the fleet's one **write-in-place** skill; a
  bounded transform set is what makes an autofix safe to run.
- **GR-MDFMT-002** *Drift:* an always-on autofix that mutates files on every edit. *Rule:* the
  write-in-place path is **opt-in per repo** (marker-gated, never default-on); `--check` (read-only)
  is the default CI use, `--write` is always explicit. *Why:* silently rewriting a repo's Markdown
  is a larger footgun than a linter's flag.
- **GR-MDFMT-003** *Drift:* a transform that is not a fixed point. *Rule:* every transform shall be
  **idempotent** — a second `--write` (or re-run) makes no further change. *Why:* an autofix that
  churns on re-run is unsafe in CI / pre-commit.
- **GR-MDFMT-004** *Drift:* rewriting content the linter is meant to *validate*, blurring the
  flag/fix split. *Rule:* `yf-markdown-lint` **validates only**; `yf-markdown-format` **fixes**. The
  two skills are the two sides of the same conventions and never merge. *Why:* keeping the transform
  axis out of the linter preserves `GR-MDLINT-001` (the linter never rewrites).

## 5. Verification

- Table alignment (REQ-MDFMT-001/004/005) is asserted by transform fixtures: a mis-aligned table
  normalizes to uniform-width, explicit-marker output; a CJK/fullwidth cell aligns on display width;
  a pipe line inside a fenced block is left untouched.
- The mode contract (REQ-MDFMT-002/003/006) is asserted by: a mis-aligned-table **`--check`** fixture
  exiting 1; an **idempotent `--write`** fixture run twice where the second run is a zero-diff no-op
  (and `--check` then exits 0); a clean `--check` exiting 0.
- Wiki-link migration (REQ-MDFMT-010–014) is asserted by fixtures added when
  `convert_wikilinks.py` moves in: dry-run vs in-place write, code / frontmatter-fence protection,
  and idempotence on an already-migrated tree.

## 6. References

- `skills/yf-markdown-format/SKILL.md` (both transforms, the `--check` / `--write` / bare modes).
- `skills/yf-markdown-format/scripts/md_table_align.py`, `scripts/convert_wikilinks.py`.
- `skills/yf-markdown-lint/SKILL.md` and its `SPEC.md` `GR-MDLINT-001` (the validate-only linter —
  the flag side of this skill's fix side).
- Root `SPEC.md` §4 (MDFMT) and `GUARDRAILS.md` (GR-MDFMT-*).
