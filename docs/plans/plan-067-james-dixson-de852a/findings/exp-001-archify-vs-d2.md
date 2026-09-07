---
type: Finding
okf_spec: OKF-PLAN
description: "Keep d2. archify has no headless raster export, a non-self-contained artifact, an unvendorable dev-channel dependency, and a quality gate that penalises the very member ids the repo checks."
id: exp-001-archify-vs-d2
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# EXP-001 — archify vs d2 for the diagram toolchain

## Approach Tested

**measured:** the same layered marketecture stack from #373 was built TWICE — once as `.d2`, once
as an archify `architecture` spec — each rendered/delivered twice for determinism, then run through
the **real, unmodified** `check_web_counts.py` plus a purpose-built extractor with four negative
controls. **inferred:** marked where stated.

## Result — KEEP d2

### The decisive result is ORTHOGONALITY, not tool quality

The omission mutation, run against the **current d2 pipeline** — two members deleted, count left
saying (8):

```
check_web_counts: scanned 1 file(s), 9 counted-set claim(s); 0 mismatch(es)   EXIT=0
```

It passes. The purpose-built extractor catches it only because of one added line
(`missing = [s for s in truth if s not in members]`).

**So #373's Half 2 is a CHECKER-LOGIC gap, not an artifact-format gap.** It is ~2 lines dropping
into `check_web_counts.py:179` today, with **zero** toolchain change. **Migrating to archify buys
none of it.**

### Checkability: archify survives only if the JSON spec is committed

| Artifact | Real checker's verdict |
| :-- | :-- |
| `.d2` source | clean — 9 claims, 0 mismatches, `EXIT=0` |
| archify `.json` spec | **2 FALSE-POSITIVE FAILs** — the `is_d2` branch (`:77-100`) has no third region shape, so `beads` bleeds into `utility` |
| archify `.html` | **membership LOST** — `4 declared unchecked`, `EXIT=0` |

Committing only the HTML degrades the check from "membership verified" to "count verified,
membership **silently** unchecked" — the exact failure class `check_web_counts.py:24-25` exists to
close. A purpose-built extractor over the `.json` does work, catching all four mutations.

### Four measured disqualifiers

| Fact | Consequence |
| :-- | :-- |
| **No CLI raster export.** `--help` lists render/compare/deliver/preview/validate/…; PNG/SVG/WebM are **browser export-menu** actions | **SC10 has no archify equivalent.** A hand-exported PNG is uncheckable by construction — a criterion that cannot fail |
| **HTML is not self-contained** — 695 KB referencing `fonts.googleapis.com` / `fonts.gstatic.com` | introduces a network font dependency into a published static site |
| **Unvendorable** — `"private": true`, `2.17.0-dev.1`, channel `development`, self-update manifest, lives outside the repo and outside `rust-embed` | a dev-channel third-party dependency on the critical path of the site build |
| **The showcase quality gate fights the checks** | at `--quality showcase` the candidate hits mutually exclusive constraints and the tool **pressures deleting the enumerated member ids** — precisely the strings `check_web_counts` verifies. Passing required demoting to `--quality standard` |

Determinism is **not** a differentiator: d2 gives `3e13fd21…` twice; archify gives `d831e651…`
twice and emits `specification.sha256` natively. Both qualify.

### The cheap win the spike found

`d2 --theme 0 --layout dagre`, same source, one flag: markedly cleaner — short curved edges, no
detours, whole stack legible in one screen. The pinned `elk` produces long orthogonal snaking runs.

**inferred:** the operator's "too busy" objection is a **layout-engine and decomposition** problem,
not a tool problem — and #373 already prescribes the decomposition.
**uncorroborated:** that `dagre` stays clean across all six; only one was tested.

## Implications for the plan

1. **No archify-migration epic.** It would re-key four manifests, **delete** the SC10-class byte
   criterion outright, add a network font dependency, and put an unvendorable dev-channel skill on
   the site build's critical path — for polish `--layout dagre` largely delivers free.
2. **Half 2 is free of the format question** and can land against the existing `.d2` corpus.
3. **Risk to record:** changing the pinned layout engine invalidates every committed PNG's sha256
   at once. That is an expected one-shot mass diff, not drift — but a reviewer must be told, or six
   red criteria get misread.
4. **Latent hazard:** `check_web_counts`'s region logic is shape-specific and has now been observed
   to break on a third shape. Any future format change inherits that cost.

## Recommendations

1. **Keep d2.**
2. **Add the omission check to `check_web_counts.py`** — ~2 lines beside the existing `wrong` at
   `:179`. This IS #373's Half 2.
3. **Evaluate `--layout dagre` as the new pin**, gated on a human read of all six.
4. **Decompose per #373's own prescription** rather than fighting one crowded canvas.
5. **If archify is wanted, scope it to EXPLORATION** — author `.d2` as the committed, checked
   source; use archify ad-hoc for a shareable interactive HTML that is neither committed nor
   checked. **Do not dual-commit both formats** — two sources of one fact is the defect
   `e-web-diagram-formulas` exists to catch.
