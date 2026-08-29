---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #83: Investigate OKF (Open Knowledge Format) compliance + integration for yf-plan / yf-research folders

- **Number:** 83
- **Title:** Investigate OKF (Open Knowledge Format) compliance + integration for yf-plan / yf-research folders
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement

## Body

## Summary

Investigate the integration and compliance of our **portable plan/research folder** artifacts
(produced by `yf-plan` and `yf-research`) against the **Open Knowledge Format (OKF)** spec:
https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md

OKF is a minimal spec for representing knowledge as "a directory of markdown files with YAML
frontmatter," optimized for human readability, agent parsing, version control, and cross-system
portability. That is squarely the goal of our plan/research folder portability contract — so it is
worth determining how close we already are and whether adopting OKF (as a native layout or an
export target) buys us interop with the broader knowledge-catalog ecosystem.

## Why this matters

`yf-plan` plan folders (`docs/plans/<plan-id>/`) and `yf-research` research dirs
(`docs/research/<NNN>-<slug>/`) are already **portable, self-contained, markdown-first knowledge
bundles** with an explicit portability contract (README + context + references + reviews, a cold
reader must understand the folder alone). OKF codifies a very similar shape. Aligning could make
our artifacts consumable by OKF-aware tooling without giving up our conventions.

## OKF requirements to check against (from the spec)

- **Directory of markdown**, no fixed taxonomy; hierarchical `<concept>.md` + optional
  subdirectories. ✅ we already are.
- **YAML frontmatter with a non-empty `type` field** on every non-reserved `.md`. ⚠️ our `plan.md`
  uses `**Field:**` header lines (ID/Author/Status/Fingerprint/Phase log), **not** YAML
  frontmatter — this is the biggest compliance gap.
- **Reserved filenames** `index.md` and `log.md` with defined purposes; MUST NOT be used for
  concept docs. ⚠️ we use `README.md` (orientation) and an in-`plan.md` phase log — map these to
  OKF `index.md` / `log.md`?
- **Recommended frontmatter:** `title`, `description`, `resource` (canonical URI), `tags`,
  `timestamp` (ISO 8601).
- **`# Citations`** heading convention (numbered) — `yf-research` already produces cited reports;
  check the citation shape against OKF.
- **Bundle-relative links** beginning with `/` recommended; we use GFM relative links
  (`findings/exp-001.md`) — assess.
- **`okf_version`** declared in root `index.md` frontmatter only.
- **Permissive consumption** — OKF forbids rejecting bundles for missing optional fields; our
  portability *audit* (`plan_manager.py audit`) is stricter (hard-fails). Note the philosophical
  difference (our audit is a producer-side gate, OKF is a consumer-side tolerance rule) — not a
  conflict, but worth documenting.

## Investigation questions

1. **Compliance delta** — enumerate exactly where plan/research folders diverge from OKF §9
   conformance (frontmatter `type`, reserved-file semantics, citation heading). Which gaps are
   mechanical (add YAML frontmatter) vs conceptual (`**Field:**` headers vs frontmatter; README vs
   index.md)?
2. **Integration options** — (a) adopt OKF-compliant frontmatter natively in `plan.md`/research
   reports; (b) add an **export/emit** path (`yf-plan`/`yf-research` → OKF bundle) leaving our
   native format unchanged; (c) do nothing but document alignment. Recommend one.
3. **Round-trip** — does OKF's `type`/`resource`/`tags`/`timestamp` model losslessly carry our
   plan metadata (ID, status, fingerprint, upstream dispositions, phase log, review passes)? What
   maps cleanly, what needs an OKF `type`-specific extension?
4. **Reserved-file mapping** — should our `README.md` become OKF `index.md` and our phase log become
   `log.md`? Impact on the portability contract + the `plan_manager.py audit` checks.
5. **Ecosystem value** — what does OKF compliance actually unlock (knowledge-catalog ingestion,
   agent interop)? Is the interop worth the frontmatter migration?

## Suggested approach

Route through `/yf-research` (this is a cited, resumable investigation, not a build) — produce a
compliance-delta report + an integration recommendation, then file follow-on `/yf-plan` work if we
decide to adopt or export OKF.

## References

- OKF SPEC: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md
- Our portability contract: `skills/yf-plan/spec/portability.md`, the plan-folder layout in
  `skills/yf-plan/SKILL.md`, and `yf-research` research-dir layout.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
