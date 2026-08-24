---
type: Finding
okf_spec: OKF-PLAN
id: exp-003-verification-cells
description: How many Success Criteria Verification cells are machine-runnable as written? Zero — #199's naive design is refuted.
---

# EXP-003 — 0 of 155. #199's re-check is NOT buildable on today's corpus.

**Verdict: the naive design is REFUTED.** A completion-time re-runner keyed on the
`Verification` column would re-check **nothing**, ship green on every plan, and detect exactly
zero regressions — **including the `SC4b` regression that motivated #199 in the first place**.

All figures reproducible at `HEAD = 2d313fa`. **Every figure is recorded with its pathspec**, per
plan-051's unresolvable "251 vs 257" divergence.

## 1. The corpus is smaller than the question assumed

```bash
git ls-files -- 'docs/plans/plan-04[2-9]-*/plan.md' 'docs/plans/plan-05[01]-*/plan.md'   # → 10 files
git grep -n "^| # | Criterion | Verification | Discharged-by |" -- 'docs/plans/*/plan.md'  # → 5 files
```

**The canonical 4-column table exists in 5 plans (047–051), not 10.** Across the whole 53-plan
corpus, **46 plans use a numbered prose list** with no `Verification` column at all. Two more
(039, 040) use a 3-column variant.

Classifiable rows, 042–051: **155** (047: 44 · 048: 26 · 049: 42 · 050: 22 · 051: 21). The other
five bundles contribute 57 criteria that are not column-structured.

## 2. The headline number

| Class | Count | % |
| :-- | --: | --: |
| **(a) WHOLE-LINE EXECUTABLE** | **0** | **0.0%** |
| (b) runnable command wrapped in prose | 43 | 27.7% |
| (c) names a test/script/artifact, no command | 19 | 12.3% |
| (d) pure prose | 93 | 60.0% |

**Class (a) is empty and it is not a near-miss.** Sorted by prose length outside backticks, the
closest cell carries 3 characters of surrounding prose — and neither of its backticked spans is
a command (`` `status: pass` and `commands > 0` ``).

**The universal shape is `<command-ish span> + prose assertion`. The *predicate* is always
prose.**

## 3. The finding that reshapes the design: polarity lives in the prose

Two of the corpus's best-formed cells, both from plan-051, both re-run verbatim:

```
git grep -c 'Read-only — never writes files' -- ':!docs/plans' ':!docs/research'    → EXIT=1   (SC4  passes)
awk '/^### Review$/{f=1} f&&/^### Portability audit/{f=0} f' SKILL.md | grep -q 'Agent'  → EXIT=0   (SC6 passes)
```

Both discharge correctly — **but only because a human read the prose to learn that exit 1 means
pass in the first and exit 0 means pass in the second.** The pass-predicates are **opposite**,
and that fact exists nowhere but the prose.

So the missing artifact is **not the command — it is the predicate.** Any design must capture
`expect: exit 0 | exit non-zero | stdout matches …` as **structure**.

## 4. Class (c) resolves 100% as *files* and ~10% as *runnables*

All 21 named artifacts resolved against `git ls-files`. But "resolves to a file" ≠ "resolves to
something runnable with a known pass predicate": only **2 of 21** appear as `CHANGE-VALIDATION.md`
recipe rows (`gate-cellcheck`, `uv-yf-verify-reconcile`). The other 19 are **evidence files**
whose criterion is "this file records X" — a content claim requiring a reader.

Note `redcheck.sh` / `gate-run.sh` are **per-bundle assets**, not repo-root tools: a
completion-time checker must resolve them bundle-relative.

## 5. A premise in the plan's own brief was STALE — correct it

`Discharged-by` dangling references: **0 of 155.** Not luck — `doc_lint`'s `plan-relations` **R1**
already enforces it, and `criteria-table-columns` / `criterion-ids` ship at severity `E`.
**#199 should spend no scope there.** (The reverse direction R1b is not clean — plan-048 has 8
unnamed issues, plan-049 has 1 — mostly covered by the `epic-kind: bookkeeping` carve-out.)

## 6. What already exists — do NOT rebuild

- **`_shared/plan_extract.py`** already returns `criteria: [{id, criterion, verification,
  discharged_by[]}]`, raw. `--strict` already exits **2 = INCONCLUSIVE**.
- **`_shared/doc_lint.py`** already owns `criteria-table-columns` (**E**), `criterion-ids` (**E**),
  `criteria-cells-filled` (**W**, promoted to **E** at `review`), and R1/R1b.
- **Nothing anywhere executes a `Verification` cell.** The closest analogue is gate `Test:` lines,
  which `classify_test()` only **classifies** (`executable | fenced | sentinel`) and never runs.

**`criteria-cells-filled` measures 0 findings across the corpus.** The corpus is already clean
under every check that exists — which is the whole point: **the existing checks cannot see this
defect class.**

Independent corroboration from a different axis: `skills/yf-plan/SPEC.md:548` records *"1 of 251
corpus `Verification:` clauses executes today."*

## 7. Implications — #199 must SPLIT

| # | Implication |
| :-- | :-- |
| I-1 | **#199a (authoring) must precede #199b (re-runner).** A re-runner has nothing to consume until cells carry a machine-recoverable clause **and an expected predicate** |
| I-2 | **Adoption is 5 of 53 plans (~9%).** #199b covers newly-authored plans only; retrofitting 46 prose-list bundles is not on the table. Say so explicitly rather than implying corpus-wide coverage |
| I-3 | **60% of criteria are not mechanizable in principle** — they assert things about prose wording, posted GitHub comments, and reviewer judgement. #199a needs a first-class `manual` disposition, or authors will write **fake commands to satisfy a gate**, which is a worse failure mode than today's |
| I-4 | **Three grammars are already proven in-corpus** because authors reached for them unprompted: a `CHANGE-VALIDATION.md` recipe-row id; a bundle-local `ctl-*` id driven by `redcheck.sh verify-all` (which already exits 0/1/2 and already encodes red/green as distinct records); or a whole-line command **plus a declared expected exit**. The `ctl-*` form is strongest — plan-050 and plan-051 converged on it independently |
| I-5 | **This plan must state its own coverage as a number.** Today's is 0/155. Anything else reproduces the defect the plan exists to fix |
