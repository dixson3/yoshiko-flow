# Plan: Markdown tooling improvements: fix ML003 title parsing (#81), add un-escaped-markup lint rule (#48), bless alt/title image convention across lint+pdf (#46), document+advise CriticMarkup PDF hazard (#49), add a new markdown-html skill (#50), and add a new yf-markdown-format skill — the autofix side of the linter — absorbing the strict GFM table aligner (#85) and the existing Obsidian→GFM wiki-link migrator

**ID:** plan-026-james-dixson-6e0e2f
**Author:** james-dixson
**Created:** 2026-07-11
**Status:** reconciling
**Epic:** yf-mol-a1f
**Fingerprint:** 686a7f8f8c9380f2f44bd319360fa08f424fdea27c9ba9525fa217a55c938510
**Phase log:**
- 2026-07-11 scoping: initial scope captured
- 2026-07-11 scoping: 4 scope decisions resolved (full CriticMarkup filter, ML010 in authoring subset, caption filter default-on, add ML011)
- 2026-07-11 investigating: 1 experiment: validate CriticMarkup pandoc Lua filter
- 2026-07-11 drafting: plan v1 synthesized: 4 epics
- 2026-07-11 review: pass-1 red-team REVISE (6 concerns, 2 missing) — see reviews/pass-1.md
- 2026-07-11 review: pass-2 red-team APPROVE (2 low, self-resolving) — see reviews/pass-2.md
- 2026-07-11 ready-for-approval: ready-check green — last red-team APPROVE + audit pass
- 2026-07-11 approved: operator approved
- 2026-07-12 drafting: reopened: integrating #85 (absorb md_table_align.py → ML012) into scope
- 2026-07-12 review: pass-3 red-team APPROVE (3 concerns, all low/low-med, non-blocking) — see reviews/pass-3.md
- 2026-07-12 ready-for-approval: ready-check green — pass-3 red-team APPROVE + audit pass (#85 folded in)
- 2026-07-12 approved: operator approved (re-scope: #85 folded in)
- 2026-07-12 review: pass-4 red-team REVISE (full whole-plan review; 2 med, 2 low, 1 accept) — see reviews/pass-4.md
- 2026-07-12 drafting: pass-4 full red-team REVISE — returned to PLAN; approval superseded pending revisions
- 2026-07-12 drafting: revised — #85 → new Epic 5 (yf-markdown-format skill), keeps lint validate-only (C1); C2/C3/C4 fixed
- 2026-07-12 review: pass-5 red-team APPROVE (C1-C5 resolved+verified; 1 low-med C6 folded in) — see reviews/pass-5.md
- 2026-07-12 ready-for-approval: ready-check green — pass-5 red-team APPROVE + audit pass (#85→Epic 5 restructure)
- 2026-07-12 approved: operator approved (pass-5: #85→yf-markdown-format Epic 5)
- 2026-07-13 drafting: reopened: fold convert_wikilinks refactor (lint→yf-markdown-format) into Epic 5 — clean flag-side/fix-side split
- 2026-07-13 review: pass-6 red-team REVISE (1 med blocking: incomplete de-list list; 1 low accept) — see reviews/pass-6.md
- 2026-07-13 drafting: revised — de-list list now grep-complete (lint README/root README/skill-authoring) per pass-6 C1
- 2026-07-13 review: pass-7 red-team APPROVE (C1 resolved+verified grep-complete; 1 low folded in) — see reviews/pass-7.md
- 2026-07-13 ready-for-approval: ready-check green — pass-7 APPROVE + audit pass (convert_wikilinks→format refactor)
- 2026-07-13 approved: operator approved (pass-7: convert_wikilinks→yf-markdown-format; lint now truly validate-only)
- 2026-07-15 intake: epic yf-mol-a1f poured
- 2026-07-15 executing: start gate resolved
- 2026-07-15 reconciling: post-execution reconciliation; bead DAG drained (22/22 issues closed)

## Objective
Markdown tooling improvements: fix ML003 title parsing (#81), add un-escaped-markup lint rule (#48), bless alt/title image convention across lint+pdf (#46), document+advise CriticMarkup PDF hazard (#49), add a new markdown-html skill (#50), and add a new `yf-markdown-format` skill — **the autofix side of `yf-markdown-lint`** — that absorbs the strict GFM table aligner (`md_table_align.py`, #85) **and** the existing Obsidian→GFM wiki-link migrator (`convert_wikilinks.py`), keeping `yf-markdown-lint` genuinely validate-only

## Motivation
Five open GitHub issues cluster around one coherent gap in the repo's markdown toolchain and
reinforce each other:

- **#81** is a live bug: `yf-markdown-lint` ML003 folds a GFM image/link **title** into the link
  target, producing a repo-wide false positive on every titled image (`![alt](path "caption")`).
  The `dixson3/writing` house-essay convention *requires* the title form, so the full link audit
  is currently unusable there.
- **#48 / #49 / #50** form a trio around markup fidelity: prose that *describes* inline markup
  (CriticMarkup) silently renders as real markup when fed through pandoc — worse, bare `~~…~~`
  strikes text even without CriticMarkup support. #48 adds a lint guard, #49 documents the PDF
  hazard, and #50 adds `markdown-html` as the natural home for opt-in CriticMarkup *rendering*
  (track-changes view).
- **#46** blesses the two-field image convention (`alt` = a11y description, `title` = print
  caption) across both the linter and the PDF renderer so one image serves screen readers and
  print without the author picking a side.
- **#85** brings the strict GFM **table aligner** (`md_table_align.py`) into the yf skill fleet.
  Today alignment lives as a per-repo vendored script re-copied into every adopting repo
  (`dixson3/obsidian-primary`, `dixson3/d3-pxe`). It does **not** belong in `yf-markdown-lint`:
  that skill's `GR-MDLINT-001` guardrail is explicit that the linter *validates only — it never
  authors, reformats, or aligns content*. Reformatting is a distinct axis, so #85 ships as a **new
  `yf-markdown-format` skill** — the **autofix side of the linter**: everything that *rewrites*
  markdown to conform to what `yf-markdown-lint` *flags*. This gives a clean flag-side/fix-side
  split — ML001 flags `[[wikilinks]]` / the format skill rewrites them; ML005/ML008 flag table
  structure / the format skill reflows alignment — extensible to future standards.
- **Latent inconsistency this fixes (pass-6):** `yf-markdown-lint` **already** ships a
  content-rewriter — `scripts/convert_wikilinks.py`, a reusable Obsidian→GFM migrator that edits
  files in place — while `GR-MDLINT-001` claims the skill "never rewrites." That is a pre-existing
  guardrail violation. Rather than leave lint half-clean (pull tables out, leave the wiki-link
  rewriter in), `convert_wikilinks.py` **moves** into `yf-markdown-format` too, so the linter
  becomes genuinely validate-only and the format skill owns the transform axis end-to-end. Both
  ride in this plan because they complete the same markdown-toolchain sweep as
  #81/#48/#46/#49/#50 (pass-4 C1, pass-6).

Affected: anyone authoring markdown in this repo and downstream repos (`dixson3/writing`,
`dixson3/emacs.d`, `dixson3/obsidian-primary`, `dixson3/d3-pxe`) that dogfood these skills.
Triggered by the writing plan-010 and emacs.d plan-004 dogfood surfacing the first five; #85 was
folded in later as an in-scope yf-markdown-lint extension.

## Scope Decisions (operator-confirmed)
1. **markdown-html CriticMarkup** — ship the new skill *and* the opt-in CriticMarkup-rendering
   Lua filter now (`--criticmarkup`, default OFF / literal pass-through). Reusable filter
   co-located in the skill.
2. **ML010 tier** — the new un-escaped-markup rule runs in the **on-edit authoring subset**
   (`ML001,ML002,ML005,ML006,ML007,ML008,ML010`), not full-audit-only.
3. **Caption filter default** — the title→figure-caption Lua filter in `md2pdf` is **default-on**
   (always applied; images with no title keep pandoc's alt caption).
4. **ML011 empty-alt** — add the accessibility rule warning on images with empty alt; a present
   `title` never warns.

**Rule numbering:** ML009 is already taken (renderable-fence compile-check). New `yf-markdown-lint`
rules are **ML010** (un-escaped markup, #48) and **ML011** (empty-alt a11y, #46). #85's table
alignment is **not** an ML rule — it lives in the new `yf-markdown-format` skill (pass-4 C1), so
`yf-markdown-lint`'s validate-only guardrail (`GR-MDLINT-001`) is untouched.

5. **#85 → new `yf-markdown-format` skill = the autofix side of the linter (pass-4 C1, pass-6).**
   Rather than an ML012 rule inside `yf-markdown-lint` (which would reverse `GR-MDLINT-001` "never
   aligns content"), the table aligner ships in a **standalone skill** owning the content-altering
   axis end-to-end: a `--check` gate (exit 1 if content would change — CI/pre-commit) **and** a
   `--write` idempotent in-place autofix, plus bare-stdout. The skill is **not** table-only — it is
   the fix-side of everything the linter flags, so it also **absorbs `convert_wikilinks.py`** (the
   Obsidian→GFM migrator today misfiled in the lint skill). `yf-markdown-lint` gets **no** ML012,
   loses `convert_wikilinks.py`, and becomes genuinely read-only. Extensible to future format
   standards. Vendoring source for the aligner (pass-3 C1): the locally-present
   `dixson3/d3-pxe/scripts/md_table_align.py` (~6 KB), with `dixson3/obsidian-primary` — the
   original home, not checked out locally — reachable via `gh api` as a fallback; confirm the
   copies are byte-identical before treating either as canonical. `convert_wikilinks.py` moves from
   the local lint skill (already present, no external fetch).

**Environment:** pandoc 3.10 (`+lua`, Figure AST available), xelatex present. The emacs.d
plan-004 CriticMarkup filter is *not* locally accessible — it is built fresh here from the
approach described in the issues (Inlines-level filter, `--from=gfm-strikeout`).

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|
| #81 | ML003 folds image title into link target | include | Fix `MDLINK_RE` dest parsing — strip optional GFM title before resolution | Epic 1 |
| #48 | Flag un-escaped inline markup (CriticMarkup) in prose | include | New rule ML010, in authoring subset; extensible delimiter registry | Epic 1 |
| #46 | alt-text / title image convention (lint + pdf) | include | Lint: bless pattern + ML011 empty-alt (Epic 1); PDF: title→caption filter default-on (Epic 2) | Epics 1 & 2 |
| #49 | markdown-pdf un-escaped CriticMarkup/strikeout hazard | include | Document hazard in SKILL.md + optional pre-render advisory via ML010 | Epic 2 |
| #50 | New skill markdown-html (CriticMarkup-aware) | include | Full new skill + opt-in CriticMarkup Lua filter | Epic 3 |
| #85 | Absorb md_table_align.py (strict GFM table alignment) | include | New `yf-markdown-format` skill (NOT an ML rule — keeps lint validate-only, pass-4 C1); owns `--check` gate + `--write` autofix; extensible to future format standards; consumer-migration note | Epic 5 |

**Coarse upstream tracking (AGENTS.md).** Reconcile files/updates **one coarse plan-026 tracking
issue** (#82; precedent #13/#14/#16) referencing #81/#48/#46/#49/#50/#85 and closing them as
resolved — it does **not** push granular per-bead sub-issues upstream.

## Investigation Findings
See [exp-001](findings/exp-001-pandoc-lua-filters.md). All three filter/detection approaches
validated empirically against pandoc 3.10. Key corrections the issues under-specify:

1. **CriticMarkup→HTML filter** (works-with-mod): use `-f gfm-strikeout` (default `gfm` destroys
   `{~~old~>new~~}` before the filter runs); the filter must be an **`Inlines` filter buffering
   contiguous `Str`/`Space` tokens**, not a per-`Str` matcher (multi-word constructs split across
   tokens). Inline/fenced code protection is automatic (distinct AST nodes). Caveat: CriticMarkup
   wrapping *other* inline markup (`{++**bold**++}`) is out of scope — acceptable edge.
2. **title→caption filter** (works-with-mod): requires `-f gfm+implicit_figures` — `gfm` does NOT
   enable implicit-figures by default, so without it no `Figure` node exists and the filter never
   fires. Verified through a full xelatex PDF.
3. **ML010 detection** (works as described): five-pattern registry; the substitution pattern must
   require the `~>` separator; reuses the lint script's existing inline-code-strip + fence
   tracking.

## Approach

### Epic 1 — yf-markdown-lint (#81, #48, #46-lint)
1. **#81 ML003 title fix.** In `markdown_lint.py`, strip the optional GFM title from the link/image
   `dest` before path resolution (parse `dest` as `path ("title")?`, resolve only `path`). Tagged
   regression fixture: `![alt](images/x.png "caption")` resolves on `images/x.png`.
2. **#48 ML010** — new authoring-subset rule flagging bare CriticMarkup constructs in prose
   (registry of 5 delimiter pairs; substitution requires `~>`; exclude inline-code + fenced
   blocks). Add `ML010` to the on-edit subset in the SKILL and the always-loaded protocol rule.
   The delimiter registry is documented and extensible.
3. **#46 ML011** — new rule warning on images with **empty alt** (`![](x.png)`); a present title
   never warns. Bless `![alt](src "title")` as documented intent in SKILL.md.
- SPEC-first: add `REQ-MDLINT-*` for ML010 (un-escaped markup), ML011 (empty-alt), and the ML003
  title-parse clarification, ahead of code; extend the fixture corpus (one file per new rule).
  `yf-markdown-lint` stays validate-only — no `--write`/mutation REQ here (that axis is the new
  `yf-markdown-format` skill, Epic 5), so `GR-MDLINT-001` is untouched.

### Epic 2 — yf-markdown-pdf (#46-pdf, #49)
1. **#46 title→caption** — bundle `caption_from_title.lua`, wire into `md2pdf.py` `pre_args`
   **default-on**. The filter needs `implicit_figures`; `md2pdf.py` today passes **no `-f`** so it
   uses pandoc's default `markdown` reader, which **already enables `implicit_figures`** — so the
   filter fires with **no reader change** (pass-4 C2). Do **not** hardcode `-f gfm+implicit_figures`
   (that would swap md2pdf off full pandoc-markdown to `gfm`, silently dropping extensions — a
   regression). Images with no title keep pandoc's alt caption. Tagged test asserts caption source;
   a guard test asserts the reader is unchanged.
2. **#49 hazard** — document the un-escaped-markup / `~~`-strikeout rendering hazard in SKILL.md
   (call out the `~~…~~` strike case explicitly). Optional non-blocking pre-render advisory: run
   the ML010 rule over the source and surface hits as a warning (still produces the PDF).
- SPEC-first: add `REQ-MDPDF-*` for the caption filter and the documented hazard/advisory.

### Epic 3 — new yf-markdown-html skill (#50)
1. New skill mirroring markdown-pdf structure: `SKILL.md`, `SPEC.md`, `README.md`,
   `scripts/md2html.py` + tests, `protocols/` if a trigger rule is warranted.
2. pandoc `--standalone --to=html5 --embed-resources`; relative image paths resolved against the
   source dir; a broad-coverage default stylesheet; math via MathJax/KaTeX.
3. **Opt-in CriticMarkup** — `criticmarkup.lua` (`Inlines`-buffering filter, the exp-001 design)
   behind `--criticmarkup` (default OFF / literal pass-through, plain `gfm`; ON uses
   `-f gfm-strikeout`). Renders the 5 constructs to `<ins>/<del>/<mark>/<span>` with
   `cm-add/cm-del/cm-hl/cm-comment` classes + stylesheet entries.
- SPEC-first: author `SPEC.md` with `REQ-MDHTML-*` before the script.

### Epic 4 — dependency guarding (yf doctor / preflight)
Operator-requested. **Premise corrected (pass-4 C3):** `yf preflight` **already** reads a skill's
`depends-on-tool` frontmatter and emits `system_deps_missing` (`preflight.rs:452,583,326`, with a
passing parity test) — the declaration is **not** inert for preflight. Two genuine, narrower gaps
remain:
1. **`yf doctor` has no per-skill dep axis.** Its axes are fixed (`REQ-YF-DOCTOR-001`:
   version/bd/uv/git/homebrew-shadow/`skills:`/`rules:`) and do not enumerate a skill's
   `depends-on-tool`, so `yf doctor` will **not** report a missing pandoc/xelatex. Adding that is a
   scoped new doctor axis + a `REQ-YF-DOCTOR` line (only if the doctor-side report is wanted).
2. **markdown-html run entrypoint.** `md2pdf.py` already guards via `check_deps()` (REQ-MDPDF-003);
   the new `md2html.py` needs the same fail-closed guard, and markdown-html must **declare**
   `depends-on-tool: [uv, pandoc]` (which preflight then enforces for free).
- exp-002 (short code-read) confirms the preflight mechanism and the doctor-axis shape before
  implementing, so Epic 4 matches the kernel rather than re-deriving it.

### Epic 5 — new yf-markdown-format skill (#85 + convert_wikilinks migration)
A new skill for **content-altering** markdown transforms — **the autofix side of the linter**, the
axis `yf-markdown-lint` deliberately refuses (`GR-MDLINT-001`). It absorbs **two** transforms: the
strict GFM **table aligner** (#85, new) and the existing **Obsidian→GFM wiki-link migrator**
(`convert_wikilinks.py`, moved out of the lint skill where it violates `GR-MDLINT-001`). Structured
so future format standards drop in beside them.
1. New skill mirroring the markdown-pdf/lint structure: `SKILL.md`, `SPEC.md` (`REQ-MDFMT-*` +
   `GR-MDFMT-*`), `README.md`, `scripts/{md_table_align.py, convert_wikilinks.py}` + tests, and a
   `protocols/` trigger rule if warranted (a skill that rewrites files on `--write` wants an opt-in
   marker like yf-markdown-lint's `.markdown-lint-on-edit`, NOT an always-on autofix).
2. Vendor `md_table_align.py` from the locally-present `dixson3/d3-pxe/scripts/md_table_align.py`
   (~6 KB, stdlib-only, East-Asian-width aware); `dixson3/obsidian-primary` (the original home) is
   reachable via `gh api` as a fallback — confirm byte-identical first. Re-shebang to the
   `#!/usr/bin/env -S uv run --script` + PEP-723 convention the fleet uses (pass-4 C4). Preserve the
   three modes: `--check` (exit 1 if any table would change — the CI/pre-commit gate), `--write`
   (idempotent in-place autofix — running twice is a no-op), bare (normalized to stdout).
3. **Move `convert_wikilinks.py`** from `skills/yf-markdown-lint/scripts/` into the new skill
   (a `git mv`-style move — it is already local, no external fetch). Add the **tests it currently
   lacks** (dry-run vs write, code/frontmatter-fence protection, idempotence). **De-list it from
   `yf-markdown-lint`:** delete the SKILL.md "Migration helper" §, drop the `convert_wikilinks.py`
   line from `SPEC.md` §3 Interfaces + the migration-helper mention, and drop the
   `protocols/MARKDOWN_LINT.md` "migration helper" pointer — so the linter is genuinely
   validate-only and `GR-MDLINT-001` is finally true (this fixes a pre-existing violation).
4. `--check` finding output: the aligner reports at file granularity (no per-line number, pass-4
   C4); define the skill's check-output convention (first offending table's line, or file-level)
   and test it.
5. Document **both** transforms as `yf-markdown-format` capabilities in SKILL.md/README.md; add a
   **consumer-migration note** so `dixson3/obsidian-primary` and `dixson3/d3-pxe` drop their vendored
   `md_table_align.py` and any `convert_wikilinks.py` reference and point AGENTS.md at the skill.
6. Root + install wiring: installer copy, **root `README.md` skill-index row** (DRIFT-CHECK
   `e-index-table`), **root `SPEC.md` §4** `yf-markdown-format` reference, `GUARDRAILS.md`
   compose-by-reference for `GR-MDFMT-*`, DRIFT-CHECK trigger-scope + node coverage for the new
   SKILL/SPEC/protocol **and the moved `convert_wikilinks.py` `script` node** (its glob owner
   changes skills).
- SPEC-first: author `SPEC.md` with `REQ-MDFMT-*` (the `--check`/`--write`/bare contract, the
  idempotent-autofix guarantee, East-Asian width, **and** the wiki-link migration contract) +
  `GR-MDFMT-*` before moving/writing the scripts.

## Epics

### Epic 1: yf-markdown-lint — ML003 fix + ML010/ML011 (#81, #48, #46-lint)
- Issue 1.1: SPEC — add `REQ-MDLINT-*` for ML003 title-parse clarification, ML010 (un-escaped
  markup), and ML011 (empty-alt); update the §2.1 rule table **and** amend the §2.2
  **REQ-MDLINT-011** enumerated authoring subset to include ML010. **No `--write`/mutation REQ and
  no ML012** — table alignment is the new `yf-markdown-format` skill (Epic 5), so `GR-MDLINT-001`
  ("never aligns content") stays intact and unamended (pass-4 C1). **(SPEC-first — precedes 1.2–1.5.)**
- Issue 1.2: Fix ML003 — strip optional GFM title from link/image dest before resolution (#81).
  - depends-on: 1.1
  - resolves-upstream: #81 (include)
- Issue 1.3: Implement ML010 (registry + inline-code/fence exclusion) + add to the authoring subset
  in **all three** canonical surfaces (SKILL.md, `protocols/MARKDOWN_LINT.md`, and — via 1.1 —
  SPEC REQ-MDLINT-011) plus `ALL_RULES`/docstring; **refresh the installed rule copy**
  (`install.sh --force`) so the on-edit trigger actually runs ML010 (#48).
  - depends-on: 1.1
  - resolves-upstream: #48 (include)
- Issue 1.4: Implement ML011 empty-alt warning — **fires only on images (leading `!`)**, never on
  empty-text links; present title never warns. Bless `![alt](src "title")` in SKILL.md. Add
  ML010/ML011 to `ALL_RULES` (line 49) and the script `Rules:` docstring (#46).
  - depends-on: 1.1
  - resolves-upstream: #46 (partial — lint half)
- Issue 1.5: Fixture corpus — one file per new rule + regression fixture for the ML003 title case
  (`![alt](images/x.png "caption")`) + ML011 images-only vs empty-link discrimination; update
  tests.
  - depends-on: 1.2, 1.3, 1.4

### Epic 2: yf-markdown-pdf — caption filter + hazard docs (#46-pdf, #49)
- Issue 2.1: SPEC — add `REQ-MDPDF-*` for the title→caption filter and the un-escaped-markup
  hazard/advisory. **(SPEC-first.)**
- Issue 2.2: Bundle `caption_from_title.lua`; wire into `md2pdf.py` pre_args default-on. **Do NOT
  change the reader** — md2pdf's default `markdown` reader already enables `implicit_figures`, so
  the filter fires as-is; hardcoding `-f gfm+implicit_figures` would regress md2pdf off
  pandoc-markdown (pass-4 C2). Tagged test asserts caption source **and** a guard test asserts the
  pandoc reader/`-f` is unchanged (#46).
  - depends-on: 2.1
  - resolves-upstream: #46 (partial — pdf half)
- Issue 2.3: Document the `~~`-strikeout / un-escaped-markup hazard in SKILL.md; optional
  non-blocking pre-render advisory reusing ML010 (#49).
  - depends-on: 2.1, 1.3
  - resolves-upstream: #49 (include)

### Epic 3: new yf-markdown-html skill (#50)
- Issue 3.1: SPEC — author `SPEC.md` with `REQ-MDHTML-*` (standalone HTML, embed-resources,
  stylesheet, relative-path resolution, opt-in CriticMarkup) **and a `§4 Guardrails` section with
  `GR-MDHTML-*`** (pass-5 C6; every skill SPEC carries one — e.g. renders HTML only, never lints or
  reformats source). **(SPEC-first.)**
- Issue 3.2: `md2html.py` — pandoc `--standalone --to=html5 --embed-resources`, relative image
  resolution, default stylesheet; **math via `--mathml`** (self-contained; no CDN dependency —
  keeps `--embed-resources` honest, pinned in REQ-MDHTML). SKILL.md + README.md + tests. All
  CriticMarkup examples in SKILL.md/SPEC.md **backtick-wrapped** (avoids ML010 self-flagging, C4).
  - depends-on: 3.1
- Issue 3.3: `criticmarkup.lua` (Inlines-buffering, exp-001 design) behind `--criticmarkup`
  (default OFF → plain `gfm`; ON → `-f gfm-strikeout`) + cm-* stylesheet classes + test.
  **Document the tradeoff** in SKILL/SPEC: `--criticmarkup` disables real GFM `~~strikethrough~~`
  (rendered literally) so substitutions survive.
  - depends-on: 3.2
  - resolves-upstream: #50 (include)
- Issue 3.4: Root + install wiring — installer copy, manifest/rule if a trigger is warranted,
  **root `README.md` skill-index row** (DRIFT-CHECK `e-index-table`), **root `SPEC.md` §4
  MDHTML reference** (the macro spec composes per-skill specs), and a **`GUARDRAILS.md`
  compose-by-reference line** for `GR-MDHTML-*` (pass-5 C6); add DRIFT-CHECK trigger-scope
  coverage for the new SKILL/SPEC/protocol.
  - depends-on: 3.2

### Epic 4: dependency guarding — yf doctor / preflight (operator-requested)
**Premise corrected (pass-4 C3):** two prior assumptions were wrong against the code. (a) `md2pdf.py`
**already** guards its run entrypoint via `check_deps()` (REQ-MDPDF-003), so entrypoint work is
**md2html-only**. (b) `yf preflight` **already** reads `depends-on-tool` frontmatter and emits
`system_deps_missing` (`preflight.rs:452,583,326`, passing parity test) — the declaration is **not**
inert; there is no "wire preflight enforcement" work. The **actual** remaining gap is `yf doctor`,
whose axes are fixed (`REQ-YF-DOCTOR-001`) and do **not** enumerate a skill's `depends-on-tool`.
- Issue 4.1: SPEC — md2html's entrypoint guard under `REQ-MDHTML-*` **and** (only if the doctor-side
  report is wanted, per 4.2) a scoped `REQ-YF-DOCTOR` line for a new per-skill `depends-on-tool`
  doctor axis. **(SPEC-first — precedes 4.3/4.4.)**
- Issue 4.2: INVESTIGATE (exp-002) — confirm the preflight mechanism (already enforces) and scope
  the `yf doctor` per-skill-dep axis: shape, where it slots into the fixed axis list, and whether it
  is worth adding vs. relying on preflight + the entrypoint guard alone. Record the decision.
- Issue 4.3: Ensure markdown-html declares `depends-on-tool: [uv, pandoc]` (preflight then enforces
  it for free). If 4.2 decides the doctor axis is worth it, add the scoped new axis so `yf doctor`
  reports a missing pandoc with an install hint (matching md2pdf's message format).
  - depends-on: 4.1, 4.2, 3.2
- Issue 4.4: Guard the `md2html.py` run entrypoint to fail-closed with a readable message (align
  with md2pdf's `check_deps()`) when pandoc is absent; tagged test. (md2pdf already covered.)
  - depends-on: 4.1, 3.2

### Epic 5: new yf-markdown-format skill (#85 + convert_wikilinks migration)
- Issue 5.1: SPEC — author `skills/yf-markdown-format/SPEC.md` with `REQ-MDFMT-*` covering **both**
  transforms: (a) table alignment — the `--check`/`--write`/bare-stdout contract, idempotent-autofix
  guarantee (`--write` twice = no-op), East-Asian-width awareness, fenced-code skip; (b) the
  Obsidian→GFM **wiki-link migration** contract (code/frontmatter-fence protection, best-effort
  resolution, idempotence). **Author a `§4 Guardrails` section with `GR-MDFMT-*`** (pass-5 C6) — the
  fleet's one write-in-place skill, so bound it: transforms markdown to conform to GFM (table
  alignment, wiki-link migration) only, **opt-in per repo** (never an always-on autofix),
  idempotent, never rewrites content outside its declared transforms. **(SPEC-first — precedes 5.2–5.6.)**
- Issue 5.2: Vendor `md_table_align.py` into `skills/yf-markdown-format/scripts/` from the
  locally-present `dixson3/d3-pxe/scripts/md_table_align.py` (`gh api` on obsidian-primary as
  fallback; confirm byte-identical first). Re-shebang to `#!/usr/bin/env -S uv run --script` + PEP-723
  (pass-4 C4). Preserve the three modes. Tagged tests incl. an **idempotent-`--write`** fixture
  (twice = no-op) and a mis-aligned-table `--check` fixture.
  - depends-on: 5.1
  - resolves-upstream: #85 (include)
- Issue 5.3: **Move `convert_wikilinks.py`** from `skills/yf-markdown-lint/scripts/` into
  `skills/yf-markdown-format/scripts/` (already local — a move, no external fetch). Add the tests it
  currently lacks (dry-run vs in-place write, code/frontmatter-fence protection, idempotence).
  **De-list every in-repo reference (grep-complete, pass-6 C1):** `grep -rn convert_wikilinks` and
  clear all of them so no dangling pointer remains — specifically (a) `yf-markdown-lint/SKILL.md`
  (delete the "## Migration helper" §, lines ~90-98); (b) `yf-markdown-lint/SPEC.md` §3 Interfaces
  (drop the `scripts/convert_wikilinks.py` line + migration-helper mention); (c)
  **`yf-markdown-lint/README.md`** — both the usage command **and** the file-layout tree entry
  (else `e-readme-usage` + `e-readme-layout`, `required` edges, FAIL); (d) the
  `protocols/MARKDOWN_LINT.md` migration-helper pointer; (e) repoint the cross-skill mention in
  **`skills/yf-skill-authoring/SKILL.md`** (~:228) to the new skill. (The root README skills-index
  row is handled in Issue 5.5.) Result: the linter is genuinely validate-only and `GR-MDLINT-001`
  "never rewrites" is finally honored (fixes a pre-existing violation). Independent of Epic 1's rule
  work — touches different lint sections (the script + Migration-helper/Interfaces/README blocks,
  not the ML rule table).
  - depends-on: 5.1
- Issue 5.4: `SKILL.md` + `README.md` — document the skill and **both** transforms (`--check`
  gate vs `--write` autofix for alignment; the wiki-link migrator), and the `--check`
  finding-output convention (file-level or first offending table's line, pass-4 C4). The new
  `README.md` **file-layout fence and Usage section must list both** `scripts/md_table_align.py`
  **and** `scripts/convert_wikilinks.py` (pass-7 — the destination side of the `e-readme-layout`
  `field-set-equal` invariant). Add an opt-in trigger marker if an on-edit autofix rule is
  warranted (NOT always-on — a skill that rewrites files must be opt-in per repo).
  - depends-on: 5.2, 5.3
- Issue 5.5: Root + install wiring — installer copy, **new root `README.md` skills-index row** for
  `yf-markdown-format` (DRIFT-CHECK `e-index-table`/`e-index-desc`) **and edit the existing
  `yf-markdown-lint` root-README row to drop the "Ships `convert_wikilinks.py` …" clause** (pass-6
  C1 — else `e-index-desc` FAILs against the de-listed lint README), **root `SPEC.md` §4**
  `yf-markdown-format` reference, a **`GUARDRAILS.md` compose-by-reference line** for `GR-MDFMT-*`
  (pass-5 C6), DRIFT-CHECK trigger-scope + node coverage for the new SKILL/SPEC/protocol. The moved
  `convert_wikilinks.py` needs no per-file DRIFT-CHECK edit — it is covered by the generic
  `skills/*/scripts/*.{sh,py}` `script`-node glob, which matches the new path automatically.
  - depends-on: 5.2, 5.3
- Issue 5.6: Consumer-migration note — document that `dixson3/obsidian-primary` and `dixson3/d3-pxe`
  can drop their vendored `scripts/md_table_align.py` (and any `convert_wikilinks.py` reference) and
  point AGENTS.md at the skill (a downstream consequence recorded here, not executed in those repos
  by this plan).
  - depends-on: 5.4

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step (upstream issues #81, #48, #46, #49, #50, #85 all incorporated). #46 is a
  **partial split** — the gate requires **both** Issue 1.4 (lint half) and Issue 2.2 (pdf half)
  closed before #46 counts as reconciled. #85 reconciles when Issue 5.2 (yf-markdown-format aligner)
  closes.

## Risks & Mitigations
| Risk | Mitigation |
|:-----|:-----------|
| CriticMarkup filter mis-handles nested inline markup (`{++**bold**++}`) | Documented out-of-scope edge (exp-001); CriticMarkup wraps plain text in practice. SPEC states the boundary explicitly. |
| caption filter silently no-ops (no `Figure` node) | md2pdf's default `markdown` reader already enables `implicit_figures` (pass-4 C2), so the filter fires unchanged; the tagged test asserts the caption source and a guard test asserts the reader/`-f` is unchanged, so a regression fails loudly. Do NOT hardcode `-f gfm+implicit_figures` (would regress md2pdf off pandoc-markdown). |
| ML010 false positives on prose that legitimately uses braces | Registry fires only on the explicit 5 CriticMarkup delimiter pairs; substitution requires `~>`; code spans/fences exempt (8/8 exp-001 cases). |
| ML011 empty-alt warns on intentional decorative images | Warning (not error); documented; present-title suppresses. Consider a decorative-image opt-out if noise surfaces. |
| ML010 (always-on subset) false-positives on prose that *documents* CriticMarkup — esp. the new markdown-html SKILL/SPEC | Exemption covers code spans/fences; mandate backtick-wrapping every CriticMarkup example in repo docs incl. the new skill's SKILL/SPEC (Issue 3.2). The registry only fires on the 5 explicit delimiter pairs. |
| Epic 4 scope over-estimated (preflight assumed inert) | pass-4 C3: preflight already enforces `depends-on-tool`; Epic 4 is reframed to the real gaps (doctor axis + md2html declaration/guard). exp-002 confirms before implementing. |
| New markdown-html skill adds pandoc dep with no guard | Epic 4 closes this — markdown-html declares `depends-on-tool: [uv, pandoc]` (preflight enforces) + a md2html entrypoint guard. |
| `yf-markdown-format` `--write` mutates files — a format skill that rewrites content is a bigger footgun than a linter | The skill is opt-in per repo (no always-on autofix, Issue 5.4); `--check` (read-only gate) is the default CI use; `--write` is explicit. Idempotent-`--write` fixture (twice = no-op) guards behavior. Keeping BOTH transforms out of yf-markdown-lint preserves that skill's validate-only guardrail (pass-4 C1). |
| Absorbed `md_table_align.py` drifts from the still-vendored downstream copies | Issue 5.6 ships a consumer-migration note so obsidian-primary / d3-pxe drop their copies and point at the skill; the skill becomes the single source of truth. |
| Moving `convert_wikilinks.py` across skills breaks its DRIFT-CHECK `script` node / any in-repo caller | Issue 5.5 updates the DRIFT-CHECK `script`-node coverage for the new glob owner; the move is `git mv`-style (history preserved) and the script is a standalone CLI (no in-repo import); its consumers are external vaults referenced by path, updated via the 5.6 migration note. |
| `convert_wikilinks.py` is currently untested — moving it risks silent regressions | Issue 5.3 adds the tests it lacks (dry-run vs write, fence/frontmatter protection, idempotence) as part of the move, so the transform lands in the new skill better-covered than it left the old one. |

## Success Criteria
- ML003 no longer flags `![alt](path "title")` — regression fixture green; the full link audit is
  clean on titled images.
- ML010 flags bare CriticMarkup in prose, exempts code spans/fences, and runs in the on-edit
  authoring subset; ML011 warns on empty alt only. `yf-markdown-lint` is **genuinely validate-only**
  — no `--write`, no ML012, and **no `convert_wikilinks.py`** (moved to yf-markdown-format), so
  `GR-MDLINT-001` "never rewrites" is finally true (a pre-existing violation, resolved).
- markdown-pdf routes a non-empty image title to the figure caption by default; no-title images
  unchanged; the pandoc reader is unchanged (guard test); hazard documented in SKILL.md.
- `markdown-html` renders standalone HTML with embedded resources and a default stylesheet;
  `--criticmarkup` renders all five constructs to styled `<ins>/<del>/<mark>/<span>`; default OFF
  is literal pass-through.
- markdown-html declares `depends-on-tool: [uv, pandoc]` (preflight reports a missing tool as
  `system_deps_missing`) and its run entrypoint fails closed with a clear message, not a raw crash;
  if adopted, `yf doctor` also reports the missing per-skill dep.
- The new `yf-markdown-format` skill is the linter's autofix side, owning **both** transforms:
  the table aligner (`--check` flags a mis-aligned table exit 1, `--write` reflows idempotently)
  **and** the Obsidian→GFM `convert_wikilinks.py` migrator (moved from lint, now tested). The skill
  documents both so downstream repos (obsidian-primary, d3-pxe) drop their vendored copies.
- Every new behavior has a SPEC `REQ-*` landed ahead of code and a tagged test; upstream issues
  #81, #48, #46, #49, #50, #85 reconciled.
