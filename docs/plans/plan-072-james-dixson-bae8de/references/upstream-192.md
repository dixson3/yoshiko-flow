---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #192 - Evaluate a structure-first plan DSL with generated
  markdown — single source for plan.md, the bead pour, and cross-reference integrity'
---
# Upstream #192: Evaluate a structure-first plan DSL with generated markdown — single source for plan.md, the bead pour, and cross-reference integrity

- **Number:** 192
- **Title:** Evaluate a structure-first plan DSL with generated markdown — single source for plan.md, the bead pour, and cross-reference integrity
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Idea

Author plan **structure** in a machine-first artifact — YAML or a small DSL — holding epics, issues, dependency edges, gates, criteria, risks and the upstream table with its internal/external references. Generate `plan.md` from it. The DSL is what the model and tools modify; the markdown is what the operator reads. When an operator edits the markdown during a human-gated review, the workflow ingests those edits back into the DSL and regenerates. **The DSL is also the source of the bead pour.**

## What the current context actually supports

This is filed because the evidence is unusually specific, not because it sounds tidy.

**1. The precedent exists.** `SKILL.md:370` — the `plan.md` skeleton is already *generated*:

```
<!-- >>> BEGIN plan.md skeleton — GENERATED from _shared/plan_template.py by _shared/sync.py; do not edit by hand -->
```

The proposal extends a mechanism already in the repo from the skeleton to the payload.

**2. Both of the current CRITICALs are parser defects that would not exist.**

- **#186** — `mask_inline_code` blanks code spans for parsing, then the title is read from the masked line. This is a defect of *recovering structure from prose*.
- **#187** — the extractor carries no `detail` field, so §5.2a's `bd create --description=` has no source. This is a defect of *what the parser chose to keep*.

Authored structure has no masking step and no field to forget.

**3. There is a measurable recovery layer that exists solely to cope with hand-authoring.** `_shared/plan_extract.py` carries a `recovered[]` channel and four named recovery classes:

```
RECOVER class A: an `Issue N.M` prefix inside Blocks is the bare id
RECOVER class B: `Epic N` / `Epics N` normalize to epic:N
RECOVER class C: a column-0 sub-key attaches to the preceding issue
RECOVER class D: a title parenthetical does not break the issue id
```

Every one is "the human typed a legal-looking variant". None would be reachable from a schema-validated source.

**4. The dominant defect class in `plan-050`'s eleven review cycles is one fact stated in N places.** Measured across its review records: stale cross-references appeared in **eight** of eleven passes, in runs of 8, then 3, then 1, then 1 — under four different actors, including two independent agents. Pass 10 named the general mechanism precisely:

> *edited the leaf without walking back up to the artifacts that enumerate over it* — `controls.txt`, the REQ list in Issue 0.1, SC1, and the Objective's count.

That class is **structurally eliminated** by single-source-plus-generation. It is not eliminated by more review: eleven passes did not eliminate it.

**5. Much of `doc_lint` is checking shape that generation would guarantee.** 17 document-type schemas, whose check kinds are dominated by `frontmatter-keys` (7), `headings-any-level` (5), `table-columns` (3), `row-id-grammar` (2) and `cell-non-empty` (2) — all assertions that a generator satisfies by construction. The `regex-present` rules would largely remain, since they assert content.

## What the context does NOT support, stated plainly

- **The round-trip is the hard part and this repo has no evidence about it.** Ingesting operator markdown edits back into a DSL is a merge problem, and it is where systems of this shape usually fail. Nothing measured here says it will work. A one-way generation (DSL → markdown, operator edits the DSL) is far more tractable and should be evaluated first, even though it is worse for the operator.
- **Prose does not fit.** `## Motivation`, `## Approach`, the Scope Decisions rationales and the review records are the *load-bearing* parts of a mature plan and are irreducibly prose. `plan-050`'s issue titles reach **2571 characters** and carry the substantive instruction. A DSL that structures the DAG and leaves prose as opaque blocks is realistic; one that structures the prose is not.
- **Migration cost is real** — ~50 existing bundles, plus the OKF portability contract, which requires a cold reader to understand a bundle from its files alone. A DSL adds a second artifact that must itself be portable.
- **It does not fix the assertion problem.** #188 shows a 62-assertion suite that asserted nothing about payload fidelity. Generation guarantees *shape*; it says nothing about whether the content is right, and the largest defects found in `plan-050` were semantic (a gate that could not be satisfied, a criterion that could not fail).

## Suggested shape if pursued

Not a full replacement. **Structure-only, one-way first:**

1. A schema for the parts that are already machine-read — epics, issues, `depends-on`, `resolves-upstream`, gates, criteria, risks, upstream rows. These are exactly what `plan_extract.py` already returns, so the schema is *derivable from the existing extractor's output* rather than designed from scratch.
2. Generate the `## Epics`, `## Gates`, `## Risks`, `## Success Criteria` and `## Upstream Issues` sections; leave prose sections hand-written between generated markers, the way `sync.py` already brackets generated regions.
3. Pour from the schema, not from a re-parse of the generated markdown — which closes #187 by construction and makes #186 unreachable.
4. Only then evaluate ingesting operator edits, with the generated-region markers making "what did the human change" mechanically answerable.

Step 2's marker convention is the crux: it is what isolates manual changes, which is the operator's stated motivation for the idea.

## Provenance

Proposed by the operator during `plan-050-james-dixson-d0414b` review cycle 11, after eleven cycles in which the stale-cross-reference and enumerated-list-goes-stale classes survived every countermeasure tried. Deliberately **not** folded into plan-050 — that plan has already been split once (D-9) and widened once (D-10). Related: #186, #187 (the parser defects), #188 (structure-vs-fidelity), #191 (scaffold review records — the same idea at the smallest possible scope, and the sensible first probe).
