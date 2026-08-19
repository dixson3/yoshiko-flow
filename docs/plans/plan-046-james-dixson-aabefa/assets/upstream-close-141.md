---
type: Reference
okf_spec: OKF-PLAN
id: upstream-close-141
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
title: 'Draft: #141 close comment (reconcile OKF-BASELINE to v0.2)'
---

> Verbatim text of an upstream write performed at plan-046 reconcile (§6.3).
> Kept in the bundle so the upstream record is reproducible from the plan folder alone.

Done in plan-046 Epic 2. `skills/yf-okf/spec/OKF-BASELINE.md` is reconciled to **OKF v0.2**, and the `okf_version` pin reads `0.2` in all five copies of the engine.

## What shipped

- **Both upstream revisions vendored verbatim** — v0.2 (`@ main`, retrieved 2026-08-18) and v0.1 (`@ ee67a5ca`, 2026-06-12) — so every claim in the baseline is checkable **offline**, and the v0.1→v0.2 delta is *diffable* rather than asserted.
- **`OKF-BASELINE.md` rewritten against the v0.2 text**, with a `§8` **section map** and every `(§N)` citation verified **row by row** against it. Not by grep: v0.2 reuses the identical `(§N)` syntax, so a stale v0.1 pointer is textually indistinguishable from a correct v0.2 one.
- **`okf_version = "0.2"`** in `_shared/okf.py` and all four vendored copies; `_shared/sync.py --check` exits 0.
- **The extension-layer concept mapping** (`OKF-YF-EXTENSIONS.md` §9): five entries, each labelled **AGREE / DIVERGE / ABSENT**, covering v0.2's four new frontmatter families.
- **A new `DRIFT-CHECK.md` edge, `e-okf-version-pin`.** The baseline *declared* a coupling to the baked-in ruleset and **no edge encoded it** — a v0.1→v0.2 edit fired nothing that inspected `okf_version`. It does now.
- **No corpus frontmatter migration**, as scoped. Exposure to both declared breaking changes is **exactly zero**: the corpus emits `timestamp` 0 times and `# Citations` 0 times. yf declined both v0.1 features independently, long before v0.2 retired them.

## Three things the reconciliation turned up

**1. §13 is accurate but incomplete — three omissions, not the one you would expect.** It declares two breaking changes and both check out. It then claims *"Everything else … is carried forward unchanged."* Not so:
- `SHOULD NOT` → **`MUST NOT`** on the extension clause (§4.1) — a normative force upgrade, undeclared. Confirmed first-hand: v0.1 `:161-162` vs v0.2 `:219-220`.
- **Seven sections were renumbered**, flagged nowhere.
- **v0.1 §10 "Relationship to other formats" was removed entirely** — a whole section, undeclared.

**2. A citation that was wrong against v0.1 too.** `OKF-BASELINE.md` cited `(§5)` for the `okf_version` key. v0.1 mentions it exactly once, inside **§11 Versioning** — §5 was *Cross-linking*. So it was never a renumbering casualty; the v0.2-correct target is **§12**, reached by fixing an error rather than applying the map. Recorded, because mapping `§5 → §6` would have produced a confidently wrong citation in a fixed-authority document.

**3. The biggest status change: v0.2 §9 specifies the `log.md` format, and yf had guessed right.** v0.1 was silent on ordering; v0.2 states *"newest first"* and makes ISO-8601 `YYYY-MM-DD` date headings a **MUST**. yf already emits exactly that, so **no artifact changed** — but the rule moved across the baseline/extensions boundary: it is now upstream conformance, not a yf decision. Three sites claiming "OKF is silent on log ordering" were corrected. Worth noting the direction: an upstream revision can **claim** a silence the extension layer had decided, which is the case that list must be re-read for on every future bump.

**Subsumes #128** (add a reference/link to the Google OKF spec) — now satisfied at v0.2 rather than v0.1.

Plan: `docs/plans/plan-046-james-dixson-aabefa/` — see `findings/exec-002-v01-verbatim-delta.md` for the measured delta. Tracker: #167.
