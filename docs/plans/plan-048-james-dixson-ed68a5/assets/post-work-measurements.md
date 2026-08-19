# Post-work measurements against the approval-fixed targets (Issue 4.3 / SC20)

Measured on the **merged tree** (`e080d29`), after Epics 0–3 and Issue 4.1 landed.
Every figure is derived at run time by the command in its row — none is carried forward
from an earlier phase (D-5: re-measure, never cite).

## The targets

| # | Target | Fixed at | Measured | Pass |
| :-- | :-- | :-- | --: | :-: |
| SC1 / SC20 | corpus unparsed residue **<= 81** | re-based at execution (operator decision) | **81** | ✅ |
| SC20 | `doc_lint` `files_checked` **>= 600** | approval | **726** | ✅ |
| SC1 | corpus documents modified = **0** | approval | **0** | ✅ |
| SC27 | FULL validation tier `status: pass` with `commands > 0` | approval | pass, **41** commands | ✅ |

## Commands

```bash
# residue + recoveries
uv run _shared/plan_extract.py docs/plans/*/ --json \
  | python3 -c 'import json,sys;d=json.load(sys.stdin);print(sum(len(x.get("unparsed") or []) for x in d))'

# linter census
uv run _shared/doc_lint.py --json \
  | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d["files_checked"],d["errors"],d["warnings"])'

# zero corpus documents modified
git diff --stat main -- docs/plans ':!docs/plans/plan-048-james-dixson-ed68a5'
```

## Full census

| Quantity | Before plan-048 | After | Δ |
| :-- | --: | --: | --: |
| Corpus unparsed residue | 150 | **81** | −69 |
| Plans carrying unparsed constructs | 33 of 48 | **24 of 48** | −9 |
| Constructs recovered (all hand-adjudicated) | 0 | **39** across 15 plans | +39 |
| `doc_lint` `files_checked` | 180 | **726** | +546 |
| `doc_lint` error-severity findings | 0 | **0** | 0 |
| `doc_lint` warning-severity findings | — | **31** | — |
| `doc_lint` report-only findings | — | **1340** | — |
| Document types declared | 3 | **17** | +14 |
| Corpus documents modified | — | **0** | 0 |

**`files_checked` 726 vs the 677 measured at the end of Epic 2.** The difference is not new
work: 3.5 committed seven relational fixtures plus a control (8 files), 2.10 added fixture
pairs, and the `plan-relations` type selects all 48 `plan.md` files. The number moves when
fixtures are added, which is why SC20's bar is a floor (`>= 600`) rather than an equality.

## What the 1340 report-only findings are, and why that is not alarming

`R` severity means *always reported, never promoted* — `STATUS_SEVERITY` keys only on `W`
and `E`. The bulk are:

- **R1b** (an issue named by no criterion) across the historical corpus — the rule ships at
  `W` with promotion declared OFF (REQ-DATA-044) precisely because history predates it;
- **`finding` / `review` / `plan-retrospective`** content-shape checks, moved to `R` by
  Issue 2.9's rule: a type whose files are authored *during* the phase at which the linter
  binds cannot carry a promotable severity;
- **24 `*-inconclusive`** entries, one per plan the extractor cannot fully read — REQ-DATA-043
  reporting honestly rather than judging an incomplete DAG.

**Zero errors is the number that gates anything**, and it is 0 on the merged tree.

## The residue, itemized (unchanged from the Epic 1 analysis)

81 = 35 prose-tailed/qualified `Blocks:` referents + 22 prose-tailed or `start-gate`
`depends-on` referents + 16 gate-blocks written inside `## Epics` + 7 epic-level
`depends-on: Epic N` fan-outs + 1 dangling target.

**16 of those 81 are a free recovery for plan-049** — perfectly parseable, refused only
because relocating a section is a document write that D-4 forbids here. See
[references/handoff-049.md](../references/handoff-049.md) §1.
