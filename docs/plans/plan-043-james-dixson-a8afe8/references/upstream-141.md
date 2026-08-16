---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #141: yf-okf: reconcile OKF-BASELINE from v0.1 to OKF v0.2 (supersedes #128)

- **Number:** 141
- **Title:** yf-okf: reconcile OKF-BASELINE from v0.1 to OKF v0.2 (supersedes #128)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

`skills/yf-okf/spec/OKF-BASELINE.md` states it is *"Pinned to `okf_version: 0.1`"* and was distilled from research project `docs/research/001-okf-compliance-delta/`. Upstream `GoogleCloudPlatform/knowledge-catalog` now ships **v0.2** (`okf/SPEC.md`, "Version 0.2"; repo pushed 2026-08-15), which per its §13 *"supersedes OKF v0.1"*.

The interesting part is not the migration mechanics — it is that **several v0.2 additions land on problems yf already solved in its own private vocabulary.**

---

## What changed

**Breaking (two, deliberate):**

| Change | Impact here |
| :-- | :-- |
| `timestamp` superseded by `generated: { by, at }` | Every yf-emitted frontmatter block that carries a timestamp |
| Body `# Citations` list superseded by a `sources` frontmatter family | **`yf-research`** — its reports are citation-backed by design |

**Additive, and several land squarely on existing yf concepts:**

| v0.2 feature | Existing yf concept it maps to |
| :-- | :-- |
| `sources` with per-source credibility signals (`author`, `usage_count`, `last_modified`) + `usage_window` | `yf-research`'s **source credibility scoring** — already implemented, in a private vocabulary |
| `verified[]`, `status`, `stale_after` | `yf-plan`'s **review verdicts** and the **stale-approved fingerprint** gate |
| `generated: { by, at }` + the actor convention (`<producer>/<version>`, `human:<id>`) | Provenance of agent-authored findings and reviews — currently unrecorded |
| New `Attested Computation` type, `# Computation` heading | Possibly `yf-change-validation` attestations / the `- validated:` bullet |

That last column is the interesting part: **yf already solved several of these problems in its own vocabulary.** Reconciling is partly a rename toward an interoperable spelling, not net-new work — and where the shapes disagree, the disagreement is worth recording rather than papering over.

Note this also subsumes **#128** (add a reference/link to the Google OKF spec), which should point at v0.2.

---


## Suggested shape

Not prescriptive:

- Reconcile `OKF-BASELINE.md` to v0.2, keeping the existing discipline: BASELINE records **verbatim what OKF says**, `OKF-YF-EXTENSIONS.md` carries yoshiko-flow opinion. The v0.2 mappings above are extension-layer decisions, not baseline text.
- Sequence the two breaking changes deliberately. `# Citations` → `sources` touches `yf-research`'s output shape; `timestamp` → `generated.at` touches every emitted frontmatter block.
- **Treat the mappings as a design input, not a migration checklist.** Where `yf-research`'s credibility model and v0.2's `sources` family disagree, the disagreement is the finding — v0.2 was designed without knowledge of this repo, so agreement would be coincidence and divergence may be justified.
- Note that `docs/research/001-okf-compliance-delta/` is the v0.1 provenance this supersedes; it should be marked superseded rather than silently outdated.

## Related

- **#128** — add a reference/link to the Google OKF spec. **Subsumed by this issue**, which should link v0.2 specifically. Close #128 when this lands, or fold it in.
- #140 — nested OKF structure. Independent, but v0.2 changes the frontmatter that nested indexes surface (`description` feeds index entries per §8), so sequence deliberately.
- `docs/research/001-okf-compliance-delta/` — the v0.1 distillation
- plan-029 — introduced `yf-okf`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

