# Plan: Markdown tooling improvements: fix ML003 title parsing (#81), add un-escaped-markup lint rule (#48), bless alt/title image convention across lint+pdf (#46), document+advise CriticMarkup PDF hazard (#49), add a new markdown-html skill (#50), and add a new yf-markdown-format skill that absorbs the strict GFM table aligner (#85)

**ID:** plan-026-james-dixson-6e0e2f
**Author:** james-dixson
**Created:** 2026-07-11
**Status:** approved
**Fingerprint:** 03ba0a5078aacc42b150fdd2014a6167489a94f8ffe4f559ddc1d94810eb6359
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

## Objective
Markdown tooling improvements: fix ML003 title parsing (#81), add un-escaped-markup lint rule (#48), bless alt/title image convention across lint+pdf (#46), document+advise CriticMarkup PDF hazard (#49), add a new markdown-html skill (#50), and add a new `yf-markdown-format` skill that absorbs the strict GFM table aligner (`md_table_align.py`) — keeping `yf-markdown-lint` validate-only (#85)

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
  authors, reformats, or aligns content* (alignment is a separate concern). Reformatting is a
  distinct axis, so #85 ships as a **new `yf-markdown-format` skill** — a home for content-altering
  format autofixes (starting with table alignment, extensible to future format standards) that
  keeps `yf-markdown-lint` faithful to its validate-only intent. It rides in this plan because it
  completes the same markdown-toolchain sweep as #81/#48/#46/#49/#50 (pass-4 C1).

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

5. **#85 → new `yf-markdown-format` skill (pass-4 C1).** Rather than an ML012 rule inside
   `yf-markdown-lint` (which would reverse `GR-MDLINT-001` "never aligns content"), the table
   aligner ships as a **standalone skill** owning the content-altering axis end-to-end: a `--check`
   format-gate (exit 1 if any table would change — CI/pre-commit use) **and** a `--write` idempotent
   in-place autofix, plus bare-stdout. The skill is scoped to grow to **multiple format standards**
   later; table alignment is the first. `yf-markdown-lint` gets **no** ML012 and stays read-only.
   The script stays stdlib-only (East-Asian-width aware). Vendoring source (pass-3 C1): the
   locally-present `dixson3/d3-pxe/scripts/md_table_align.py` (~6 KB), with `dixson3/obsidian-primary`
   — the original home, not checked out locally — reachable via `gh api` as a fallback; confirm the
   copies are byte-identical before treating either as canonical.

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

### Epic 5 — new yf-markdown-format skill (#85)
A new skill for **content-altering** markdown format autofixes — the axis `yf-markdown-lint`
deliberately refuses (`GR-MDLINT-001`). Table alignment is the first standard; the skill is
structured so future format standards drop in beside it.
1. New skill mirroring the markdown-pdf/lint structure: `SKILL.md`, `SPEC.md` (`REQ-MDFMT-*`),
   `README.md`, `scripts/md_table_align.py` + tests, and a `protocols/` trigger rule if warranted
   (a format skill that can rewrite files on `--write` likely wants an opt-in marker like
   yf-markdown-lint's `.markdown-lint-on-edit`, NOT an always-on autofix).
2. Vendor `md_table_align.py` from the locally-present `dixson3/d3-pxe/scripts/md_table_align.py`
   (~6 KB, stdlib-only, East-Asian-width aware); `dixson3/obsidian-primary` (the original home) is
   reachable via `gh api` as a fallback — confirm byte-identical first. Re-shebang to the
   `#!/usr/bin/env -S uv run --script` + PEP-723 convention the fleet uses (pass-4 C4). Preserve the
   three modes: `--check` (exit 1 if any table would change — the CI/pre-commit gate), `--write`
   (idempotent in-place autofix — running twice is a no-op), bare (normalized to stdout).
3. `--check` finding output: since the aligner reports at file granularity (no per-line number,
   pass-4 C4), define the skill's check output convention (report the first offending table's line,
   or file-level) and test it.
4. Document alignment as a `yf-markdown-format` capability in SKILL.md; add a **consumer-migration
   note** so `dixson3/obsidian-primary` and `dixson3/d3-pxe` drop their vendored
   `scripts/md_table_align.py` and point their AGENTS.md at the skill.
5. Root + install wiring: installer copy, **root `README.md` skill-index row** (DRIFT-CHECK
   `e-index-table`), **root `SPEC.md` §4** `yf-markdown-format` reference, DRIFT-CHECK trigger-scope
   coverage for the new SKILL/SPEC/protocol.
- SPEC-first: author `SPEC.md` with `REQ-MDFMT-*` (the `--check`/`--write`/bare contract, the
  idempotent-autofix guarantee, East-Asian width) before the script.

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

### Epic 5: new yf-markdown-format skill (#85)
- Issue 5.1: SPEC — author `skills/yf-markdown-format/SPEC.md` with `REQ-MDFMT-*`: the
  `--check`/`--write`/bare-stdout contract, the idempotent-autofix guarantee (`--write` twice = no-op),
  East-Asian-width awareness, and the fenced-code-skip behavior. **Author a `§4 Guardrails`
  section with `GR-MDFMT-*`** (pass-5 C6) — this is the fleet's one write-in-place skill, so bound
  it: aligns tables only, **opt-in per repo** (never an always-on autofix), idempotent, and never
  rewrites non-table prose (mirrors `GR-MDPDF-002` "renders; never lints"). **(SPEC-first — precedes 5.2–5.5.)**
- Issue 5.2: Vendor `md_table_align.py` into `skills/yf-markdown-format/scripts/` from the
  locally-present `dixson3/d3-pxe/scripts/md_table_align.py` (`gh api` on obsidian-primary as
  fallback; confirm byte-identical first). Re-shebang to `#!/usr/bin/env -S uv run --script` + PEP-723
  (pass-4 C4). Preserve the three modes. Tagged tests incl. an **idempotent-`--write`** fixture
  (twice = no-op) and a mis-aligned-table `--check` fixture.
  - depends-on: 5.1
  - resolves-upstream: #85 (include)
- Issue 5.3: `SKILL.md` + `README.md` — document the skill, its `--check` (CI/pre-commit gate) vs
  `--write` (autofix) modes, and the `--check` finding-output convention (file-level or first
  offending table's line, pass-4 C4). Add an opt-in trigger marker if an on-edit autofix rule is
  warranted (NOT always-on — a format skill that rewrites files must be opt-in per repo).
  - depends-on: 5.2
- Issue 5.4: Root + install wiring — installer copy, **root `README.md` skill-index row**
  (DRIFT-CHECK `e-index-table`), **root `SPEC.md` §4** `yf-markdown-format` reference, a
  **`GUARDRAILS.md` compose-by-reference line** for `GR-MDFMT-*` (pass-5 C6), DRIFT-CHECK
  trigger-scope coverage for the new SKILL/SPEC/protocol.
  - depends-on: 5.2
- Issue 5.5: Consumer-migration note — document that `dixson3/obsidian-primary` and `dixson3/d3-pxe`
  can drop their vendored `scripts/md_table_align.py` and point AGENTS.md at the skill (a downstream
  consequence recorded here, not executed in those repos by this plan).
  - depends-on: 5.3

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
| `yf-markdown-format` `--write` mutates files — a format skill that rewrites content is a bigger footgun than a linter | The skill is opt-in per repo (no always-on autofix, Issue 5.3); `--check` (read-only gate) is the default CI use; `--write` is explicit. Idempotent-`--write` fixture (twice = no-op) guards behavior. Keeping it OUT of yf-markdown-lint preserves that skill's validate-only guardrail (pass-4 C1). |
| Absorbed `md_table_align.py` drifts from the still-vendored downstream copies | Issue 5.5 ships a consumer-migration note so obsidian-primary / d3-pxe drop their copies and point at the skill; the skill becomes the single source of truth. |

## Success Criteria
- ML003 no longer flags `![alt](path "title")` — regression fixture green; the full link audit is
  clean on titled images.
- ML010 flags bare CriticMarkup in prose, exempts code spans/fences, and runs in the on-edit
  authoring subset; ML011 warns on empty alt only. `yf-markdown-lint` remains validate-only
  (`GR-MDLINT-001` intact — no `--write`, no ML012).
- markdown-pdf routes a non-empty image title to the figure caption by default; no-title images
  unchanged; the pandoc reader is unchanged (guard test); hazard documented in SKILL.md.
- `markdown-html` renders standalone HTML with embedded resources and a default stylesheet;
  `--criticmarkup` renders all five constructs to styled `<ins>/<del>/<mark>/<span>`; default OFF
  is literal pass-through.
- markdown-html declares `depends-on-tool: [uv, pandoc]` (preflight reports a missing tool as
  `system_deps_missing`) and its run entrypoint fails closed with a clear message, not a raw crash;
  if adopted, `yf doctor` also reports the missing per-skill dep.
- The new `yf-markdown-format` skill ships the strict GFM table aligner: `--check` flags a
  mis-aligned table (exit 1), `--write` reflows idempotently (twice = no-op), and the skill
  documents alignment so downstream repos (obsidian-primary, d3-pxe) can drop their vendored copies.
  `yf-markdown-lint` is untouched by this.
- Every new behavior has a SPEC `REQ-*` landed ahead of code and a tagged test; upstream issues
  #81, #48, #46, #49, #50, #85 reconciled.
