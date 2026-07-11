# Plan: Markdown tooling improvements: fix ML003 title parsing (#81), add un-escaped-markup lint rule (#48), bless alt/title image convention across lint+pdf (#46), document+advise CriticMarkup PDF hazard (#49), and add a new markdown-html skill (#50)

**ID:** plan-026-james-dixson-6e0e2f
**Author:** james-dixson
**Created:** 2026-07-11
**Status:** approved
**Fingerprint:** 611a1c963a535513f3d1af6152dafe7f3249bf773bdd3232898c27907c7e5769
**Phase log:**
- 2026-07-11 scoping: initial scope captured
- 2026-07-11 scoping: 4 scope decisions resolved (full CriticMarkup filter, ML010 in authoring subset, caption filter default-on, add ML011)
- 2026-07-11 investigating: 1 experiment: validate CriticMarkup pandoc Lua filter
- 2026-07-11 drafting: plan v1 synthesized: 4 epics
- 2026-07-11 review: pass-1 red-team REVISE (6 concerns, 2 missing) — see reviews/pass-1.md
- 2026-07-11 review: pass-2 red-team APPROVE (2 low, self-resolving) — see reviews/pass-2.md
- 2026-07-11 ready-for-approval: ready-check green — last red-team APPROVE + audit pass
- 2026-07-11 approved: operator approved

## Objective
Markdown tooling improvements: fix ML003 title parsing (#81), add un-escaped-markup lint rule (#48), bless alt/title image convention across lint+pdf (#46), document+advise CriticMarkup PDF hazard (#49), and add a new markdown-html skill (#50)

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

Affected: anyone authoring markdown in this repo and downstream repos (`dixson3/writing`,
`dixson3/emacs.d`) that dogfood these skills. Triggered by the writing plan-010 and emacs.d
plan-004 dogfood surfacing all five.

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

**Rule numbering:** ML009 is already taken (renderable-fence compile-check). New rules are
**ML010** (un-escaped markup, #48) and **ML011** (empty-alt a11y, #46).

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

**Coarse upstream tracking (AGENTS.md).** Reconcile files/updates **one coarse plan-026 tracking
issue** (precedent #13/#14/#16) referencing #81/#48/#46/#49/#50 and closing them as resolved — it
does **not** push granular per-bead sub-issues upstream.

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

### Epic 2 — yf-markdown-pdf (#46-pdf, #49)
1. **#46 title→caption** — bundle `caption_from_title.lua`, wire into `md2pdf.py` `pre_args`
   **default-on**; ensure the reader enables `implicit_figures` (`-f gfm+implicit_figures` or
   equivalent). Images with no title keep pandoc's alt caption. Tagged test asserts caption source.
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
Operator-requested. pandoc + xelatex are hard runtime deps of markdown-pdf, and pandoc of the new
markdown-html; today a missing tool surfaces only as a raw failure at run time.
1. Add pandoc (and xelatex for markdown-pdf) to the affected skills' preflight/`yf doctor`
   dependency checks so a missing binary is reported as a clear **INCONCLUSIVE/skip** with an
   install hint, not a crash — matching the Skill Surface Convention's `system_deps_missing`
   pattern.
2. markdown-html declares pandoc; markdown-pdf declares pandoc + xelatex. Guard the run entrypoint
   to fail-closed with a readable message when a dep is absent.
- Investigate first: how existing skills declare system deps to `yf doctor`/preflight (exp-002,
  a short code-read) so Epic 4 matches the established mechanism rather than inventing one.

## Epics

### Epic 1: yf-markdown-lint — ML003 fix + ML010/ML011 (#81, #48, #46-lint)
- Issue 1.1: SPEC — add `REQ-MDLINT-*` for ML003 title-parse clarification, ML010 (un-escaped
  markup), ML011 (empty-alt); update the §2.1 rule table **and** amend the §2.2 **REQ-MDLINT-011**
  enumerated authoring subset to include ML010. **(SPEC-first — precedes 1.2–1.5.)**
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
- Issue 2.2: Bundle `caption_from_title.lua`; wire into `md2pdf.py` pre_args default-on; ensure the
  reader enables `implicit_figures`; tagged test asserts caption source (#46).
  - depends-on: 2.1
  - resolves-upstream: #46 (partial — pdf half)
- Issue 2.3: Document the `~~`-strikeout / un-escaped-markup hazard in SKILL.md; optional
  non-blocking pre-render advisory reusing ML010 (#49).
  - depends-on: 2.1, 1.3
  - resolves-upstream: #49 (include)

### Epic 3: new yf-markdown-html skill (#50)
- Issue 3.1: SPEC — author `SPEC.md` with `REQ-MDHTML-*` (standalone HTML, embed-resources,
  stylesheet, relative-path resolution, opt-in CriticMarkup). **(SPEC-first.)**
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
  **root `README.md` skill-index row** (DRIFT-CHECK `e-index-table`) and **root `SPEC.md` §4
  MDHTML reference** (the macro spec composes per-skill specs); add DRIFT-CHECK trigger-scope
  coverage for the new SKILL/SPEC/protocol.
  - depends-on: 3.2

### Epic 4: dependency guarding — yf doctor / preflight (operator-requested)
**Premise correction (pass-1 C1):** `md2pdf.py` **already** guards its run entrypoint via
`check_deps()` (REQ-MDPDF-003) — a missing pandoc/xelatex exits with a clear named-tool message,
not a raw crash. So the run-entrypoint work is **md2html-only**. Epic 4's real gap is upstream of
the entrypoint: whether the `depends-on-tool` **frontmatter declaration** actually gates via `yf`
doctor/preflight, or is inert.
- Issue 4.1: SPEC — md2html's entrypoint guard under `REQ-MDHTML-*` **and** a `yf`-kernel REQ for
  doctor/preflight enforcement of `depends-on-tool` (new observable behavior — report vs crash).
  **(SPEC-first — precedes 4.3/4.4.)**
- Issue 4.2: INVESTIGATE (exp-002) — read how `yf` preflight/doctor consumes `depends-on-tool`
  frontmatter today (markdown-pdf declares `[uv, pandoc, xelatex]`): does it check presence and
  surface `system_deps_missing`, or is the declaration inert? Record the mechanism.
- Issue 4.3: Per exp-002: ensure markdown-html declares `depends-on-tool: [uv, pandoc]`; if the
  declaration is inert, wire enforcement so a missing binary reports a clear
  `system_deps_missing` / doctor warning with an install hint (matching md2pdf's message format).
  - depends-on: 4.1, 4.2, 3.2
- Issue 4.4: Guard the `md2html.py` run entrypoint to fail-closed with a readable message (align
  with md2pdf's `check_deps()`) when pandoc is absent; tagged test. (md2pdf already covered.)
  - depends-on: 4.1, 3.2

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step (upstream issues #81, #48, #46, #49, #50 all incorporated). #46 is a
  **partial split** — the gate requires **both** Issue 1.4 (lint half) and Issue 2.2 (pdf half)
  closed before #46 counts as reconciled.

## Risks & Mitigations
| Risk | Mitigation |
|:-----|:-----------|
| CriticMarkup filter mis-handles nested inline markup (`{++**bold**++}`) | Documented out-of-scope edge (exp-001); CriticMarkup wraps plain text in practice. SPEC states the boundary explicitly. |
| `implicit_figures` not enabled → caption filter silently no-ops | exp-001 caught this; Epic 2 pins `-f gfm+implicit_figures` and the tagged test asserts the caption source, so a regression fails loudly. |
| ML010 false positives on prose that legitimately uses braces | Registry fires only on the explicit 5 CriticMarkup delimiter pairs; substitution requires `~>`; code spans/fences exempt (8/8 exp-001 cases). |
| ML011 empty-alt warns on intentional decorative images | Warning (not error); documented; present-title suppresses. Consider a decorative-image opt-out if noise surfaces. |
| ML010 (always-on subset) false-positives on prose that *documents* CriticMarkup — esp. the new markdown-html SKILL/SPEC | Exemption covers code spans/fences; mandate backtick-wrapping every CriticMarkup example in repo docs incl. the new skill's SKILL/SPEC (Issue 3.2). The registry only fires on the 5 explicit delimiter pairs. |
| Epic 4 depends-on-tool mechanism turns out inert / harder than assumed | exp-002 investigates before implementing; Epic 4 matches the existing mechanism rather than inventing one. |
| New markdown-html skill adds pandoc dep with no guard | Epic 4 explicitly closes this — the skill ships with dep declaration + entrypoint guard together. |

## Success Criteria
- ML003 no longer flags `![alt](path "title")` — regression fixture green; the full link audit is
  clean on titled images.
- ML010 flags bare CriticMarkup in prose, exempts code spans/fences, and runs in the on-edit
  authoring subset; ML011 warns on empty alt only.
- markdown-pdf routes a non-empty image title to the figure caption by default; no-title images
  unchanged; hazard documented in SKILL.md.
- `markdown-html` renders standalone HTML with embedded resources and a default stylesheet;
  `--criticmarkup` renders all five constructs to styled `<ins>/<del>/<mark>/<span>`; default OFF
  is literal pass-through.
- A missing pandoc/xelatex is reported by `yf doctor`/preflight and by each run entrypoint as a
  clear message, not a raw crash.
- Every new behavior has a SPEC `REQ-*` landed ahead of code and a tagged test; upstream issues
  #81, #48, #46, #49, #50 reconciled.
