# Red-Team Review — Pass 1

**Plan:** plan-026-james-dixson-6e0e2f
**Date:** 2026-07-11

## Verdict: REVISE

## Strengths
- exp-001 is real evidence: caught the two under-specified pandoc incantations (`-f gfm-strikeout`,
  `+implicit_figures`) and validated the caption filter through a full xelatex PDF.
- #81 diagnosis verified against actual code (`MDLINK_RE` `[^)]*` dest capture).
- SPEC-first correctly wired in Epics 1–3 (SPEC issue precedes + blocks implementation).
- #46 correctly decomposed into lint half (1.4) and pdf half (2.2), both partial.
- Epic 4 defers exp-002 rather than assuming the mechanism.

## Concerns

| # | Severity | Concern | Recommendation |
|:--|:---------|:--------|:---------------|
| C1 | medium | Epic 4 premise factually wrong for md2pdf: it **already** has `check_deps()` (REQ-MDPDF-003) exiting with a named-tool message. 4.3's run-guard is redundant for md2pdf. | Rescope 4.3 run-guard to `md2html.py` only (align md2pdf message format optionally); reframe Epic 4's real gap as doctor/preflight **declaration enforcement** (whether `depends-on-tool` actually gates), which 4.1 investigates. |
| C2 | medium | Epic 4 has no SPEC-first issue, yet introduces new observable behavior (report vs crash). Repo mandate is unconditional. | Add an Epic 4 SPEC issue: md2html guard under `REQ-MDHTML-*`, plus a `yf`-kernel REQ for doctor/preflight enforcement, ahead of 4.2/4.3. |
| C3 | medium | Authoring subset is enumerated in **three** canonical places + the installed copy: SPEC `REQ-MDLINT-011` (§2.2), `SKILL.md`, `protocols/MARKDOWN_LINT.md`. Issue 1.3 names only two. | Amend REQ-MDLINT-011's enumerated subset in Issue 1.1; require an install refresh so the on-edit trigger actually runs ML010. |
| C4 | medium | ML010 in the always-on subset will false-positive on prose that **documents** CriticMarkup — most affected is the new markdown-html SKILL/SPEC itself. Exemption covers only code spans/fences. | Mandate code-span wrapping for all CriticMarkup examples in repo docs incl. the new skill's SKILL/SPEC; add a risk-table row. |
| C5 | low-med | `--criticmarkup` uses `-f gfm-strikeout`, silently disabling legitimate `~~strike~~` in HTML output — unstated behavior change. | Document the tradeoff in markdown-html SKILL/SPEC (criticmarkup mode ⇒ plain GFM strikethrough off). |
| C6 | low-med | "math via MathJax/KaTeX" conflicts with `--embed-resources` self-containment; under-specified. | Pin the math strategy in `REQ-MDHTML` (e.g. `--mathml` for a self-contained artifact, or accept a documented CDN exception). |

## Missing
- M1 (low): Root-level wiring for the new skill beyond the installer — root `README.md` skill-index
  row (DRIFT-CHECK `e-index-table`), root `SPEC.md` §4 MDHTML reference, DRIFT-CHECK trigger-scope
  coverage for the new files. Epic 3.4 lists installer + manifest/rule only.
- M2 (low): Fixture notes — ML011 must fire only on images (leading `!`), not empty-text links;
  `ALL_RULES` (line 49) + the script `Rules:` docstring must gain ML010/ML011 or the default full
  run omits them.

## Gate Assessment
Start gate (human/operator) appropriate. Reconcile Gate reasonable, but should confirm **both**
halves of the #46 split (Issues 1.4 + 2.2) closed, not treat #46 as a single unit.

## Upstream Assessment
Dispositions all specific and consistent; #46 partial boundary clear. Gap vs AGENTS.md **coarse**
convention: the plan should state reconcile files/updates ONE coarse plan-026 tracking issue
(precedent #13/#14/#16) referencing #81/#48/#46/#49/#50 — not push five granular targets.

## Operator Resolutions
| Concern | Resolution | Status |
|:--------|:-----------|:-------|
| C1 (Epic 4 premise wrong for md2pdf) | Rescoped Epic 4: reframed premise (md2pdf already guarded via REQ-MDPDF-003); 4.3 run-guard now md2html-only; Epic 4 gap reframed as doctor/preflight declaration enforcement. | resolved |
| C2 (Epic 4 no SPEC issue) | Added Issue 4.1 SPEC (md2html guard under REQ-MDHTML-*, yf-kernel REQ for enforcement); renumbered investigate/impl issues after it. | resolved |
| C3 (subset in 3 places) | Issue 1.1 now amends REQ-MDLINT-011 subset explicitly; Issue 1.3 adds install-refresh step. | resolved |
| C4 (ML010 prose false-positive) | Added code-span-wrapping mandate for CriticMarkup examples (incl. new skill SKILL/SPEC) to Approach + risk-table row. | resolved |
| C5 (criticmarkup disables strikethrough) | Added SPEC/SKILL documentation requirement to Issue 3.3. | resolved |
| C6 (math vs embed-resources) | Pinned `--mathml` (self-contained) as default in Issue 3.2 / REQ-MDHTML. | resolved |
| M1 (root wiring) | Added root README index row + root SPEC §4 reference to Issue 3.4. | resolved |
| M2 (fixtures/ALL_RULES) | Added ML011 images-only + ALL_RULES/docstring update to Issues 1.4/1.5. | resolved |
| Gate (#46 both halves) | Reconcile Gate updated to require both 1.4 + 2.2 closed. | resolved |
| Upstream (coarse) | Added coarse-tracking note to Upstream Issues section + reconcile. | resolved |
