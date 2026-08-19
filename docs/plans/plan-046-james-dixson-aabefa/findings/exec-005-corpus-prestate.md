---
type: Finding
okf_spec: OKF-PLAN
id: exec-005-corpus-prestate
plan: plan-046-james-dixson-aabefa
created: '2026-08-18'
---

# exec-005 — The corpus pre-state, measured (plan-046 Issue 4.1)

Verbatim pre-state before any `--write`. Raw per-bundle JSON:
[`assets/reindex-prestate.json`](../assets/reindex-prestate.json).

## The corpus, as pinned by Issue 4.1

**Single-level glob only** — `docs/plans/*/index.md docs/research/*/index.md`. Never `docs/**/index.md`:
that would sweep four **frozen migration fixtures** under
`plan-029-james-dixson-75fd34/findings/okf-migration-samples/*/after/index.md` and let `--write`
regenerate them, destroying the recorded evidence of a completed plan. Verified by execution — a
`docs/**` walk returns exactly those four extra paths and no others.

| measure | value |
| :-- | --: |
| bundles under `docs/plans/` + `docs/research/` | **50** |
| bundles carrying a root `index.md` | **19** |
| bundles with **no** root index → `no-index`, exit **2** | **31** |
| of the 19: `clean` | **0** |
| of the 19: `drift` | **19** |

**D-11 holds exactly as specified:** all 31 index-less bundles return `no-index` / exit `2` — never
`0`. Their absence can never be counted as green.

## Findings

| kind | count |
| :-- | --: |
| `ghost` | **37** |
| `missing` | **18** |
| `empty-dir` | 0 |
| **total** | **55** |

| ghost target | n | | missing target | n |
| :-- | --: | :-- | :-- | --: |
| `assets/` | 15 | | `upstream-triage.md` | 8 |
| `diagrams/` | 14 | | `artifacts/` | 3 |
| `findings/` | 4 | | `diagrams/` | 3 |
| `references/` | 3 | | `scripts/` | 2 |
| `plan-retrospective.md` | 1 | | `REDEPLOY-HANDOFF.md` | 1 |
| | | | `decisions/` | 1 |

## The count differs from the plan's expectation — and the plan's number is the stale one

Issue 4.1 states **"Expected: 40 items — 25 ghost + 15 unlisted files."** Measured: **55 — 37 ghost +
18 missing.**

**Two independently-implemented checks agree, exactly.** `reindex --check` (this plan's new engine,
SPEC `REQ-OKF-011`) and `markdown_lint.py --rules ML003` (a pre-existing, separately-written link
resolver) both report **37**, with an **identical per-target breakdown** and **identical
bundle-by-bundle sets** (set equality asserted programmatically, not eyeballed). Two checks written
at different times by different means converging on the same 37 is much stronger evidence than one
check agreeing with a prior estimate.

**The direction is explained.** exp-003's `25` was measured before the corpus grew: `plan-045`'s and
`plan-046`'s own bundles were added afterwards (`git log --diff-filter=A` places their `index.md`
files at `634385f` and `1c473a7`), and plan-046's bundle alone contributes 3 of the ghosts — the case
risk **R9** already anticipated. The corpus is a moving target and the plan's figure was a snapshot,
not an invariant.

**What survives from the plan's decomposition:** the `1` dead **file** is confirmed exactly
(`plan-retrospective.md`, the presence-optional ghost, Issue 4.2a(b)). The remainder are dead
**directory** links — **36**, where the plan said 24 — which is the class Issue 3.3 deliberately
broadened `ghost` to cover and the reason the two units now agree at all.

**No criterion is threatened.** SC6 requires `reindex --check` green over the 19 and ML003 at **0**
after the backfill — both are *post-state* conditions, indifferent to the pre-state magnitude. The
larger number strengthens the plan's premise rather than undermining it: there was more silent drift
than the investigation found, and it was invisible because `okf.py check` did no link resolution at
all until Issue 3.6.

> **Recorded, not reconciled into the plan.** `plan.md` is fingerprint-included and is not edited
> mid-execution (operator ruling, 2026-08-18, on the SC3 conflict). The pre-state of record is this
> file.
