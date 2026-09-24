---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #346 - yf-research index_manager add: stamps a foreign
  idx into a bundle member and silently overwrites existing frontmatter type'
---
# Upstream #346: yf-research index_manager add: stamps a foreign idx into a bundle member and silently overwrites existing frontmatter type

- **Number:** 346
- **Title:** yf-research index_manager add: stamps a foreign idx into a bundle member and silently overwrites existing frontmatter type
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

Two related defects in `index_manager.py add`, both found in research 061's package phase.

## Defect 1 — a wrong `idx` is stamped from outside the bundle

`index_manager.py add` stamped `scripts/README.md` **inside bundle 061** with:

```yaml
idx: 49
```

`49` corresponds to nothing in this bundle. `idx` must be **inherited from the owning bundle** (061 here), not derived independently — a bundle member carrying a foreign index is worse than one carrying none, because it looks authoritative and cross-references will follow it.

## Defect 2 — pre-existing frontmatter is silently overwritten

The same run replaced an existing `type: Research Artifact` with `type: Concept`. It did not preserve the value, and it did not report the conflict.

Silent overwrite of hand-authored frontmatter is the more damaging half: a member file that was **correctly typed by its author** ends up mistyped by a tool that never says it changed anything. Every OKF conformance check downstream then reads the wrong type and agrees with itself.

## Fix direction

- Inherit `idx` from the owning bundle; never derive it independently inside a bundle.
- On encountering pre-existing `type` / `idx`, either preserve them or report a conflict — never silently overwrite. If overwrite is ever right, it should be explicit (`--force`) and it should say so on stdout.

## Repro

Write a `.md` with correct frontmatter under a research dir, then run `index_manager.py add` on it. Observe both the foreign `idx` and the replaced `type`.

