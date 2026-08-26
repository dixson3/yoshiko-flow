---
type: Finding
okf_spec: OKF-PLAN
id: exp-002-pour-fidelity-correctness
description: Is pour_fidelity.py correct before we ship it? The join is sound; --strict has three silent-pass holes
---

# EXP-002: is `pour_fidelity.py` correct before #210 ships it?

**Verdict: the comparator's bead↔issue join is CORRECT — #210's warning describes a trap it
warns the fixer about, not a defect in the script. But `--strict` carries a separate,
previously unrecorded exit-code defect that #210's fix would generalise from a local curiosity
to a fleet-wide silent pass.**

## The premise #210 warns about is REFUTED

#210 warns the fixer that *"bead ids are positional… a fidelity comparator must map beads to
issues by the `Issue N.M:` title prefix, not by the numeric id suffix. Mapping by suffix
produces a confident, entirely wrong '12 edges missing' result."*

The script does not map by suffix. `_shared/pour_fidelity.py:81-87` joins **metadata first,
title second, never guessed** — and `TITLE_ID` (line 54) carries `[a-z]?`, so lettered ids are
first-class. The bead `id` is used only as a graph key for parent/child and dependency
resolution; nothing splits or regexes it.

Measured on a purpose-built fixture reproducing #210's exact skew (plan declares 1.1, 1.2,
1.2a, 1.3; beads are positionally 1.1–1.4, so bead `…1.4` is titled "Issue 1.3"):

| Arm | Result |
| :-- | :-- |
| **A** — with `metadata.plan_issue` | `comparable=1 skipped=0 divergent=0`, `plan_edges=3 bd_edges=3`, RC **0** |
| **B** — no metadata, title fallback only | `comparable=1 skipped=0 divergent=0`, `plan_edges=3 bd_edges=3`, RC **0** |

Two negative controls confirm the instrument can still fail: a simulated suffix mapper on the
same fixture reported `MISSING: ['1.2a']` / `EXTRA: ['1.4']` — 100% skew after the letter — and
deleting a real `depends-on: 1.2a` produced `invented: 1 edges`, RC **1**.

**End-to-end agreement with plan-052**, re-derived rather than corroborated from a record:
`plan_issues=31 bd_issues=31`, `plan_edges=49 bd_edges=49`, `id_source={"metadata":31}`,
gates 5/5, epics 8/8, `clean=true`, RC 0. Exactly the recorded figures.

> **Absence is itself a finding:** `grep -ril fidelity` over the plan-052 bundle returns **no
> pour-fidelity run record** in `log.md` or `plan-retrospective.md`. The gate ran, and left
> nothing behind that a later reader could check. That is [#217](https://github.com/dixson3/yoshiko-flow/issues/217)
> (no run record) observed from a second direction.

## The defect that IS present: `--strict` exits 0 on an EMPTY scope

`pour_fidelity.py:264-265`:

```python
scope = [r for r in res["results"]
         if (a.plan in r["plan"] if a.plan else True) and r["joinable"]]
return 1 if any(not r["clean"] for r in scope) else 0
```

An empty `scope` makes `any(...)` false → **exit 0**. Three ways to empty it, all measured:

| Case | stdout says | `$?` |
| :-- | :-- | --: |
| **D — no-mapping**: beads carry neither metadata nor an `Issue N.M:` title | `no-mapping: 1 plans`, `plan_edges=3 bd_edges=0` | **0** |
| **E — `--plan` matches nothing** | `divergent=1`, `invented: 1 edges in 1 plans` | **0** |
| **G — plan dir has no `plan.md` / no `**Epic:**`** | `comparable=0 skipped=1` | **0** |

**Case D is the one that matters, and it is self-defeating.** #210 justifies this gate on the
grounds that it is *"the specific control that would have caught #186 and #187"* — a pour that
produced **35 beads with empty descriptions and masked titles**. Masked titles are precisely
what destroys the title fallback. So on the exact population the gate was justified by, it
joins nothing and returns **exit 0 = PASS**.

The script's own comment (lines 266-278) argues INCONCLUSIVE(2) is the honest verdict for a
plan whose DAG cannot be judged — and applies that reasoning to the `unparsed` case but not to
the `no-mapping` case, though it already carries a `population: "no-mapping"` label.

Case E is latent, not live: §6.4 passes the full folder name, so today's substring match hits.
It breaks the moment anyone passes a short id.

## A caller-side conflation in `SKILL.md`

`SKILL.md:1578-1587` branches on `if [ "$FIDELITY_RC" -ne 0 ]` and prints *"the poured bead DAG
does not match the plan's declared DAG"* — so **exit 2 (INCONCLUSIVE) is reported to the
operator as a divergence.** Separately, §6.4 passes `--json`, sending the summary to stdout
while the INCONCLUSIVE *reason* goes to stderr and is not captured by `FIDELITY=$(…)`.

This is the same "two vocabularies, one branch" defect as `doc_lint`'s #181 and #207's
`found` boolean — a third instance in the same codebase.

## `pour_fidelity.py` is NOT one of #189's six untested scripts

`_shared/test_pour_fidelity.py` exists (149 lines) and is wired into `CHANGE-VALIDATION.md`
as the `pour-fidelity` recipe. All 15 checks pass. **But no arm covers exit 2, no-mapping under
`--strict`, a `--plan` mismatch, or the skipped case** — which is exactly why D/E/G survived.
The suite also depends on live `bd` state and on plan-047's `plan.md` staying byte-stable, so
it *cannot run in any repo but this one* — the same portability defect #210 is about.

## The relocation itself is mechanically safe

`pour_fidelity.py:49-52` loads `plan_extract.py` as a **sibling** via `Path(__file__).parent`.
`_shared/plan_extract.py` and `skills/yf-plan/scripts/plan_extract.py` are byte-identical, and
copying `pour_fidelity.py` beside the vendored copy reproduced the plan-052 run byte-for-byte.
`_shared/sync.py:214-216` already vendors the extractor; a parallel entry is needed.

## Implication for the plan

**Scope does not expand for the reason #210 warns about — it expands for a different one.**

Shipping the gate to every repo generalises case D from a local curiosity to a fleet-wide
silent pass: adopting repos have older, pre-metadata plans, and those are exactly the ones the
gate will wave through at exit 0. Fixing #210 without fixing that ships a halting gate that
no-ops on the population that justified it — the same shape as #210's own Impact argument
(*"an executor that treats the missing instrument as 'nothing to report' records a completion
as fidelity-checked when nothing checked it"*), except the instrument is now present and still
reports nothing.

**Recommended plan content:**

1. Ship `pour_fidelity.py` to `skills/yf-plan/scripts/`, add the `sync.py` vendoring entry,
   correct `SKILL.md:1578`.
2. **Fix the empty-scope hole BEFORE shipping** (~5 lines): return **2** when the scoped result
   set is empty, and **2** for a scoped plan in the `no-mapping` population — matching the
   treatment `extractor_unparsed` already gets. File as a sixth instance of #203.
3. Correct the §6.4 caller to distinguish exit 1 from exit 2, and stop losing the stderr reason
   under `--json`.
4. Ship `test_pour_fidelity.py` too, add the four missing arms, and decouple it from live `bd`.
