---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #175: plan-047: mechanically parseable yf artifact documents — templates, linters, normalizer, extractor

- **Number:** 175
- **Title:** plan-047: mechanically parseable yf artifact documents — templates, linters, normalizer, extractor
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Coarse tracking issue for **plan-047** (precedent: #167 for plan-046, #134 for plan-039).

**Bundle:** `docs/plans/plan-047-james-dixson-dec9ff/`

## Objective

Make yf artifact documents mechanically parseable: formal templates per document type, per-type
linters, a corpus normalizer, and a common extractor that machine-reads the epic/issue DAG.

## Why

Every yf artifact document — `plan.md`, findings, review passes, research reports, `SPEC.md` — is
authored as prose against a template that **nothing executes**. The templates are real and mostly
correct; what is missing is a verdict. This is #149's M5 (*a step with no exit code is not a step*)
applied to the plan document itself.

## The measurement that justifies it

`plan_manager.py` is 4779 lines and contains **zero** parses of `### Epic N:` or `- Issue N.M:`.
The epic/issue DAG is transcribed into beads by an LLM at `SKILL.md` §5.2a, and nothing checks the
result. Prototyping the extractor and joining it to the live bead graph across 43 comparable plans:

| Axis | `plan.md` declares | `bd` has | Divergence |
| :-- | --: | --: | :-- |
| epics | 189 | 188 | 1 never poured |
| issues | 781 | 752 | 31 unmatched |
| **dependency edges** | **885** | **860** | **45 dropped · 20 invented** |
| gates | 116 | 114 | 4 plans disagree |

**17 of 43 plans carry a divergence — a 40% per-plan pour-defect rate.** A dropped `blocks` edge
means the coordinator marked a bead ready *before its declared predecessor*. Three plans (006, 007,
036) have no recoverable plan↔bead mapping at all. Verified with a positive control: deleting an
issue line, a `depends-on`, and a gate block each make the comparator fail, and it is silent on an
unmutated copy. The last six plans measure 0 dropped / 0 invented, so this is legacy drift — but
nothing detects it either way.

The control that validates the whole thesis: **every enforced document type measures 0% drift;
every unenforced agent-written type measures 14–95%.**

## Scope

11 epics / 78 issues. Formal templates + linters for all ~15 document types across `yf-plan`
bundles, `yf-research` bundles, and the `SPEC.md` family; a hash-neutral corpus normalizer; the
common extractor and a pour-fidelity comparator; enforcement bound at INTAKE, as a
`CHANGE-VALIDATION.md` recipe row, and always-on on-edit.

## Upstream dispositions

- **include:** #165 (spec `Verification:` lines — measured 4 of 12 executed clauses are FALSE),
  #125 (status-enum hardening — measured far more load-bearing than filed: `update-status` accepts
  `approved` with exit 0 on a plan whose `ready-check` just exited 3)
- **partial, staying open:** #113, #174, #149, #135, #62
- **exclude:** #173, #150, #145, #172

Six investigation findings, three red-team passes (all REVISE, all resolved) — see
`findings/` and `reviews/` in the bundle.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

