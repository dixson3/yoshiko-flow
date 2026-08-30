---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #244 - README-contract drift: e-readme-layout fails 16/19
  skills, and the manifest contract is stronger than anything enforcing it'
---
# Upstream #244: README-contract drift: e-readme-layout fails 16/19 skills, and the manifest contract is stronger than anything enforcing it

- **Number:** 244
- **Title:** README-contract drift: e-readme-layout fails 16/19 skills, and the manifest contract is stronger than anything enforcing it
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

A full 52-edge `yf-drift-check` sweep at `dd9adc2` (plan-054 Issue 6.6) found **three
README-contract edges failing across 16 of 19 skills**, all pre-existing.

| Edge | Failing | Detail |
| :-- | --: | :-- |
| `e-readme-layout` | 16/19 | `SPEC.md` missing from 10 layout fences; `yf-plan` omits `scripts/doc_lint.py`, `plan_extract.py`, `pour_fidelity.py` and the 20-schema `scripts/document_types/`; `yf-research` omits `OKF-EXTENSION.md`, `scripts/okf.py` and 4 test files; **5 fences carry a stale unprefixed root** (`skills/beads-init/`, `skills/beads-upstream/`, `skills/diagram-authoring/`, `skills/drift-check/`, `skills/optimal-instructions/`) |
| `e-readme-prereqs` | 1 | `skills/yf-skill-authoring/README.md` has **no Prerequisites section at all**, while its `SKILL.md` declares `depends-on-tool: [uv]` |
| `e-readme-usage` | 2 (+1 missing) | `yf-incubator/README.md` teaches `/incubator …` and `yf-beads-upstream/README.md` teaches `/beads-upstream …` — the **pre-rename, unprefixed** invocations; neither appears in the corresponding `SKILL.md`. `yf-skill-authoring/README.md` has no Usage section |

## The contract is stronger than anything that enforces it

`e-readme-layout`'s contract is a file-by-file `field-set-equal` against
`find skills/<skill> -type f`. The repo's only mechanical enforcement
(`skills/yf-plan/scripts/test_cli_enumeration.py:223-249`) is deliberately **directory-level**.

So the manifest asserts something strictly stronger than the repo checks, and 16 of 19 skills
violate it. **Either the contract's wording or the READMEs need reconciling** — today they
simply disagree, and a manifest edge that 84% of its targets fail is not exerting force.

Recommendation: decide which is right *first*. If directory-level is the intended contract,
amend `DRIFT-CHECK.md` §3 to say so; if file-by-file is intended, the READMEs need a
generated layout fence rather than a hand-maintained one — the `_shared/sync.py` precedent
from plan-054 Issue 1.3 applies directly.

Discovered by plan-054's release-readiness drift sweep; pre-existing, out of scope for that plan.

