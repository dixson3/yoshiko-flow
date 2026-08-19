---
type: Reference
okf_spec: OKF-PLAN
id: upstream-167
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
---

# Upstream #167: plan-046-james-dixson-aabefa execution tracking

- **URL:** https://github.com/dixson3/yoshiko-flow/issues/167
- **State:** OPEN
- **Disposition:** tracker (the coarse plan-scale tracking issue; not a work row)

## Body

Coarse tracking issue for **plan-046** — the OKF group.

**Plan:** [`docs/plans/plan-046-james-dixson-aabefa/`](https://github.com/dixson3/yoshiko-flow/tree/main/docs/plans/plan-046-james-dixson-aabefa)
**Status:** approved · fingerprint `8efe609b` · deliverable class `standard`
**Shape:** 5 epics / 39 issues, strictly ordered.

## Upstream dispositions

| Issue | Disposition | Notes |
| :-- | :-- | :-- |
| #141 | include | `OKF-BASELINE.md` v0.1 → v0.2 verbatim + extension-layer AGREE/DIVERGE/ABSENT mapping. **No corpus frontmatter migration** — measured exposure to both v0.2 breaking changes is zero (`timestamp` 0 emissions, `# Citations` 0). |
| #140 | **partial** | **IN:** root-scoped `reindex --check`/`--write`, the drift model, the root backfill, two extension decisions. **OUT:** nested `index.md` (deferred), nested `log.md` (dropped permanently), promotion to error-level enforcement (recorded, not executed). `partial` because the title's own nouns are all in the OUT column. |
| #92 | supersede | With **three named carve-outs** filed separately, not closed away. |
| #118 | include | Four sites, not the two the issue names. |

## Why #140 is `partial`, not `include`

Investigation measured the originally-scoped nested-index backfill and it did not survive:

- `description` — the field OKF §8 says an index entry SHOULD carry — occurs in **0 of 423** nested files, so every generated entry would read `*description pending*`
- **74 of 142 (52%)** of subdirectories would get a listing of no value
- root indexes already carry described subdirectory entries in **16 of 19** bundles

Meanwhile real drift exists at the root **today**: 25 ghost entries (24 dead directory links + 1 dead file) and 15 unlisted files, invisible because `okf.py check` does no link resolution. The work retargets there. Nested `log.md` is dropped permanently — 1–2 distinct commit dates per subdirectory, and every `okf.append_log` call site targets the bundle root, so nothing would populate it.

## Why #92 is superseded with carve-outs

Its emit half shipped on 2026-07-19 — **8h39m before the deferral was recorded**. Its stated rationale ("no confirmed non-Google adopter") is measurably false: four verified adopters, two at v0.2. But a clean supersede would silently drop the on-demand projection delivery mode, the conformance gate for yf-research and yf-incubator, and consumer round-trip fidelity. Those are filed as follow-ons.

## Review history

Five red-team cycles, high-severity findings **5 → 5 → 2 → 1 → 0**. Full adversarial record in `reviews/pass-1.md` … `pass-5.md`.

Two decisions were reversed by measurement mid-plan, and three findings carry inline corrections where a claim was asserted from *reading* code rather than running it — including one in `exp-003` that was load-bearing for the plan's headline retargeting.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
