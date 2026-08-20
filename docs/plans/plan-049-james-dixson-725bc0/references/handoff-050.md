---
type: Reference
okf_spec: OKF-PLAN
id: handoff-050
description: Everything plan-049 leaves for its successor — GENERATED from the plan's own tables (Issue 6.6 / SC29)
---

# Handoff to plan-050

**Generated** from `plan.md`'s own tables at `HEAD = ae5a75a` on 2026-08-20 — not typed. SC29 is explicit that *"a typed list does NOT discharge it"*, because a hand list is exactly what silently omits the row nobody remembered. Regenerate with the command in [Provenance](#provenance).

## 1. Unmet `Discharged-by` criteria

Derived by joining the **42 criteria** in `## Success Criteria` against the live status of the **44 execution beads**, keyed on each bead's `plan_issue` metadata.

| Criterion | Discharged-by | Why it is unmet |
| :-- | :-- | :-- |
| `SC25` | 6.7 | discharged by **6.7 (deploy)**, which is blocked on a separate operator authorization — the `--allow-permissions-write` config half is explicitly **not** granted |
| `SC29` | 6.6 | discharged by **6.6**, this document; it is unmet at the moment of generation by construction and is satisfied the moment this file lands |

**Two, and both are structural rather than dropped work.** Every other criterion is
discharged by a closed bead. Note that two criteria — **SC31** and **SC23** — are
discharged by *closed* beads and were nonetheless **MISSED on their numbers**; they are
not in this table because the work happened. See §3.

## 2. Upstream rows that stay open

| Issue | Disposition | What plan-050 inherits |
| :-- | :-- | :-- |
| [#140](https://github.com/dixson3/yoshiko-flow/issues/140) | `partial` | the readability half shipped; nested `index.md`/`log.md` generation, the `reindex`/`--fix` verb and the drift model remain — all of them #171's |
| [#149](https://github.com/dixson3/yoshiko-flow/issues/149) | `partial` | **M5 closed** (the linter has an executing home at three bindings). **M9 out of scope**, with its measurement: 26 deduplicated `discovered-from` edges, **0** connecting two plan epics |
| [#113](https://github.com/dixson3/yoshiko-flow/issues/113) | `partial` | residue dropped 81 -> 75 and `dag_guard` gives a ready-made instrument, but the topological walk itself is untouched |
| [#174](https://github.com/dixson3/yoshiko-flow/issues/174) | `partial` | the binding closes more of the class; the **review-phase falsification pass** is untouched and is this issue's remaining substance |
| [#171](https://github.com/dixson3/yoshiko-flow/issues/171) | `deferred` | blocked behind a `description:` producer change (plan-046 D-9); a separate skill's axis |

`#102` and `#145` are `exclude` (unrelated axes) and `#135` is **closed**. The coarse
tracker [#183](https://github.com/dixson3/yoshiko-flow/issues/183) is closed by the
land-the-plane sweep, not by reconciliation.

## 3. The two missed criteria, and why the number was wrong

| Criterion | Target | Measured | Status |
| :-- | :-- | --: | :-- |
| SC31 (post-widening) | corpus `unparsed[]` ≤ 81 | **83** | ❌ +2 |
| SC23 / SC31 (post-write) | corpus `unparsed[]` ≤ 73 | **75** | ❌ +2 |

**One cause, counted twice.** The write phase performed exactly as derived (−5 on
`plan-008`, −3 on `plan-015`, both predicted in `assets/proposed-write-diff.md` *before*
the authorization gate was evaluated). The whole shortfall is Epic 2's +2: two `plan-010`
declarations that were **invisible** before the widening and are now visible-and-refused.
Hitting the target required silently dropping them, which `REQ-DATA-052` forbids in its
own text.

**For plan-050: do not re-target this number without re-deriving it.** The literal was
fixed at approval before the refusal behaviour existed, which is precisely what plan-049's
own Principle 3 warns about — *a number is not a target unless it is derivable from what
the plan permits*. The satisfiable form is a **derived** criterion: *residue rises by at
most the number of newly-visible unattributable declarations, and every such row is
named*. Both clauses held.

## 4. Work explicitly scheduled forward

| Item | Provenance | Disposition |
| :-- | :-- | :-- |
| The two `finding.toml` repairs — the stale `## Output` cross-reference, and the `sections()` fenced-template trap | EXP-003, recorded at Issue 4.8 | **SCHEDULED.** Out of scope for plan-049, which touched the `plan` and `plan-relations` schemas, not the `finding` type |
| The one-shot `R1b` sweep before enforcement | EXP-003, recorded at Issue 4.8 | **DECLINED with a falsifiable condition.** Its premise was that R1b would be promoted to `E` at `review`; `REQ-DATA-053`'s `promote = false` makes that permanently false. **Reopens if** any future plan proposes removing `promote = false` or promoting R1b to `E` — the sweep then becomes that plan's prerequisite |
| The **eight** out-of-scope non-gate-block constructs | Issue 3.4, `assets/out-of-scope-constructs.md` | **NOT work.** Each is recorded with the measured reason it is not a relocation; relocating `plan-010`'s three would *reduce* information by manufacturing gates with no `Type` and no `Test` |
| `plan-006`'s surviving `gate-completeness` finding | Issue 3.2's recorded decision | **INTENTIONAL.** The `- Not needed — no upstream issues incorporated` idiom fires by design; it sits in a `complete` bundle and is report-only, so no corpus write is needed |
| The `Incubator/*` §3 rows | Issue 4.5, `CHANGE-VALIDATION.md` preamble | **PERMANENT no-op here, keep anyway** — load-bearing in an incubator-using vault |

## 5. The instrument plan-050 inherits

- **`_shared/dag_guard.py`** — `snapshot`/`verify`, four layers, 0/1/2 exit contract, and
  a `--upper-bound` mode. Use it to bracket any corpus write. Its mutant suite
  (`_shared/test_dag_guard.py`) is the template for *a control must be shown to FAIL
  before it is trusted to pass*.
- **The intake binding** — `ready-check` now exits 3 on a non-conformant in-flight plan.
  **plan-050 will be graded by it at its own intake.** It inherits the audit's
  grandfather level, so a legacy bundle is not re-judged.
- **`--exclude`** on both engines. A plan measuring the corpus must self-exclude, or it
  writes literals that its own next edit stales.
- **The `stale-measured-literal` rule** will fire on plan-050 while it is in flight. Its
  blind spot is **denominator-only**: it finds a stale *count*, never a stale *claim about*
  a count.

## 6. Deferred, not done: the 6.7 deploy config half

`yf self install --from-build --build` was run **without** `--allow-permissions-write`.
The config half is a **separate operator decision** and was explicitly not granted. See
the plan's `log.md` for the per-key delta reported at the halt.

## Provenance

```bash
# The two tables in §1 and §2 are joins over plan.md and the live bead DB:
uv run _shared/plan_extract.py docs/plans/plan-049-james-dixson-725bc0 --json \
  | jq '.[0].criteria'                      # criteria + Discharged-by
bd list --all --limit 900 --json \
  | jq '[.[]|select(.metadata.plan=="plan-049-james-dixson-725bc0")|{id,status,i:.metadata.plan_issue}]'
```
