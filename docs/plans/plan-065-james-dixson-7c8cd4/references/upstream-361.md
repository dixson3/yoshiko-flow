---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #361 - plan_extract.py --strict validates neither self-edges
  nor cycles in the plan DAG'
---
# Upstream #361: plan_extract.py --strict validates neither self-edges nor cycles in the plan DAG

- **Number:** 361
- **Title:** plan_extract.py --strict validates neither self-edges nor cycles in the plan DAG
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug, follow-on

## Body

Red-team pass 4, C34, on plan-064. **Measured during that plan's own drafting**: a `depends-on`
self-edge (an issue declaring itself as its own predecessor) was introduced, passed
`plan_extract.py --strict` GREEN, and surfaced only later and indirectly as an unrelated
requirement-coverage failure.

**Why it matters:** `--strict` is the gate that stops a partially-read plan from driving the pour
(REQ-DATA-043), and SKILL.md §5.2a says plainly that "a DAG missing an edge silently reorders
execution". A self-edge or a cycle is a DAG that cannot be executed in any order — a strictly worse
condition than a missing edge — and the extractor reports neither.

**Scope:**

- reject a `depends-on` naming the issue itself;
- reject a dependency cycle;
- both under `--strict`, at exit **2 (INCONCLUSIVE)** consistent with REQ-DATA-043 — the extractor
  cannot produce a usable DAG, which is a statement about the reading, not a claim that the plan is
  substantively wrong.

**Note on the workaround in use:** plan-064's own bead-creation script hand-rolled a topological
walk that detects self-edges and cycles and exits non-zero. That is a per-plan script, not a gate;
the check belongs in the extractor where every plan gets it.

`_shared/plan_extract.py` is vendored — `_shared/sync.py` must regenerate the copies and the FAST
tier gates on byte-identity.
