---
type: Reference
okf_spec: OKF-PLAN
id: edge-audit-049
description: Hand audit of the recovered trailing-inline declarations (Issue 2.3 / SC7)
---

# Edge audit: the trailing-inline `depends-on:` recovery (plan-049 Issue 2.3)

**Criterion:** SC7 · **Measured at** `HEAD = 458092d` · **Population:** 74 recovered declarations across 5 plans

SC7 asks for **at least 20 rows across at least 4 plans**, each with a **reproducible**
before/after edge pair, plus an **explicit adverse-finding count** — and states that an
empty file with the right name does not discharge it. The table below carries 25 rows
across all 5 affected plans; the adverse count is stated in full, including its zero.

## What a row asserts

| Column | Meaning |
| :-- | :-- |
| `before` | the edges this source line produced **under the pre-widening extractor**, taken from the `dag_guard snapshot` recorded before Issue 2.1 landed. For a genuine dark-matter recovery this is **empty** — that is the whole finding |
| `after` | the edges the widened extractor materialises from the same line |
| verdict | a **hand** adjudication: the owning issue was read, and the attribution confirmed against it |

Reproduce any row with:

```bash
uv run _shared/dag_guard.py snapshot docs/plans --out /tmp/now.json
jq -r '.plans["<plan>"].L2[]' /tmp/now.json          # the AFTER edge set
uv run _shared/plan_extract.py docs/plans/<plan> --json \
  | jq '.[0].recovered[] | select(.class=="trailing-inline-subkey")'
```

## The adjudicated sample

| # | Plan | Line | Source line (verbatim) | before | after | Verdict |
| --: | :-- | --: | :-- | :-- | :-- | :-- |
| 1 | `006` | 160 | `Criterion 2/7). depends-on: 1.1` | *(none)* | `1.2<-1.1` | ✅ correct |
| 2 | `006` | 162 | `to bound the CONSISTENCY.md sub-agent runs). depends-on: 1.2` | *(none)* | `1.3<-1.2` | ✅ correct |
| 3 | `006` | 172 | `depends-on: 2.1` | *(none)* | `2.2<-2.1` | ✅ correct |
| 4 | `006` | 177 | `that all 8 edited SKILL.md still parse/load (Success Criterion 5). depends-on: 2.1` | *(none)* | `2.3<-2.1` | ✅ correct |
| 5 | `006` | 182 | `depends-on: 2.2` | *(none)* | `3.1<-2.2` | ✅ correct |
| 6 | `007` | 171 | `(depends-on: 1.1, 1.6)` | *(none)* | `1.2<-1.1`, `1.2<-1.6` | ✅ correct |
| 7 | `007` | 174 | `format). (depends-on: 1.1)` | *(none)* | `1.3<-1.1` | ✅ correct |
| 8 | `007` | 178 | `handling, the 4 manifest-driven check engines. (depends-on: 1.2, 1.3)` | *(none)* | `1.4<-1.2`, `1.4<-1.3` | ✅ correct |
| 9 | `007` | 179 | `- Issue 1.5: Add `templates/manifest.md` — the blank schema a repo fills in. (depends-on` | *(none)* | `1.5<-1.2` | ✅ correct |
| 10 | `007` | 184 | `(depends-on: 1.1)` | *(none)* | `1.6<-1.1` | ✅ correct |
| 11 | `009` | 224 | `refuse-on-dirty, non-git fallback, branch-name = plan id). depends-on: 1.1, 1.2, 1.3` | *(none)* | `1.4<-1.1`, `1.4<-1.2`, `1.4<-1.3` | ✅ correct |
| 12 | `009` | 228 | `start-gate resolve, before coordinator. depends-on: 1.4` | *(none)* | `2.1<-1.4` | ✅ correct |
| 13 | `009` | 230 | `orphan sweep: re-attach → sweep → loop). depends-on: 1.4` | *(none)* | `2.2<-1.4` | ✅ correct |
| 14 | `009` | 235 | `in-place fallback with a one-line reason. depends-on: 1.3, 2.1` | *(none)* | `2.4<-1.3`, `2.4<-2.1` | ✅ correct |
| 15 | `009` | 241 | `dogfood passes, then flip the default. depends-on: 2.3, 3.5` | *(none)* | `2.5<-2.3`, `2.5<-3.5` | ✅ correct |
| 16 | `010` | 168 | `(skill names, per-skill file list, read-file). depends-on: 1.1` | *(none)* | `1.2<-1.1` | ✅ correct |
| 17 | `010` | 171 | `closure with cross-group/external logging (install.py parity). depends-on: 1.2` | *(none)* | `1.3<-1.2` | ✅ correct |
| 18 | `010` | 182 | `names, `--strict`, `--dry-run`, `--force`. depends-on: 1.3, 1.4` | *(none)* | `1.5<-1.3`, `1.5<-1.4` | ✅ correct |
| 19 | `010` | 188 | `files**. depends-on: 1.5` | *(none)* | `1.6<-1.5` | ✅ correct |
| 20 | `010` | 192 | `exit on fail. depends-on: 1.6` | *(none)* | `1.7<-1.6` | ✅ correct |
| 21 | `012` | 218 | `detail, remediation }`; generalize `Axis`. depends-on: A.1` | *(none)* | `A.2<-A.1` | ✅ correct |
| 22 | `012` | 221 | `depends-on: A.2` | *(none)* | `A.3<-A.2` | ✅ correct |
| 23 | `012` | 224 | `depends-on: A.3` | *(none)* | `A.4<-A.3` | ✅ correct |
| 24 | `012` | 228 | `unlike a read-only check verdict). depends-on: A.4` | *(none)* | `A.5<-A.4` | ✅ correct |
| 25 | `012` | 230 | `update/extend doctor tests. depends-on: A.4` | *(none)* | `A.6<-A.4` | ✅ correct |

## Adverse findings

| Class | Count | Reading |
| :-- | --: | :-- |
| Recovered rows producing **no** edge (a claimed recovery that recovered nothing) | **0** | a non-zero count here would mean the audit trail is claiming recoveries that did not happen |
| Recovered rows whose edges **already existed** before the widening (double-counting) | **0** | a non-zero count would inflate the recovery total with edges another construct already supplied |
| Rows in the adjudicated sample whose attribution was **wrong** | **0** | each was checked against its owning issue bullet by reading the source |

**Zero adverse findings is a result, not an absence of checking.** All three classes were
computed over the **full 74-row population**, not over the 25-row sample — the sample is
what was hand-read, the counts are exhaustive. The two mechanical classes are derivable
from the two snapshots, so they can be re-run at any time; the attribution class cannot
be mechanised, which is why SC7 asks for a hand audit at all.

## Per-plan distribution

| Plan | Recovered | Edges before | Edges after | Note |
| :-- | --: | --: | --: | :-- |
| `plan-006-james-dixson-bf6e21` | 7 | 0 | 9 | reported `0 unparsed, 0 edges` before — the residue metric recording the loss as perfection |
| `plan-007-james-dixson-84da0d` | 12 | 0 | 17 | same: `0 edges` while carrying 11 declarations |
| `plan-009-james-dixson-996e44` | 13 | 0 | 19 | multi-referent lists (`depends-on: 1.1, 1.2, 1.3`) |
| `plan-010-james-dixson-73eebd` | 24 | 0 | 37 | largest population; also the only plan where two declarations are still refused (see below) |
| `plan-012-james-dixson-a99822` | 18 | 0 | 18 | **lettered** referents (`A.1`, `B.4`); a numeric-only widening would have recovered a biased sample, silently |

## The two declarations that are still refused, and why that is correct

`plan-010` carries two trailing-inline declarations the widened grammar **refuses**, and
both refusals are the intended behaviour rather than a shortfall:

| Line | Source | Why it is refused |
| --: | :-- | :-- |
| 280 | `… each test tagged with its REQ-…. depends-on: 1.3 **entry**` | the referent list is followed by a **prose tail**. Where the list stops is unknowable, so REQ-DATA-052 requires refusal over a guess — recovering `1.3` and discarding `entry` would be inventing a boundary |
| 311 | `depends-on: G1, 4.4` | `G1` is a **gate** id, not an issue id. The all-or-nothing rule (plan-048 Issue 1.4a) refuses the whole declaration rather than recovering the readable half, because a partially-recovered edge list looks complete while silently reordering execution |

Both were **invisible** before this widening and are now **reported** in `unparsed[]`.
That is a strict improvement in information and a **+2 rise in the residue count** — the
two are the same event seen from two sides. See `assets/widening-measurements.md` for
the consequence for SC31's `≤ 81` target.
