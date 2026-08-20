---
type: Reference
okf_spec: OKF-PLAN
id: out-of-scope-constructs
description: The eight non-gate-block constructs left out of scope, each with plan, line, and the MEASURED reason it is not a relocation (Issue 3.4 / SC12)
---

# The eight out-of-scope constructs, each with the measured reason

**Issue:** plan-049 3.4 · **Criterion:** SC12 · **Measured:** 2026-08-20, post-write

## Why the count is EIGHT and not nine or sixteen

The arithmetic is worth stating because every prior figure in this chain was wrong:

| Step | Count | Source |
| :-- | --: | :-- |
| the inherited "16 free recoveries" | 16 | plan-048's handoff |
| ...re-measured (D-7) as genuinely free | **7** | EXP-006 — all seven are `plan-008`'s single gate block |
| the remainder, i.e. **not** gate blocks | **9** | 010 (3) + 015 (1) + 018 (2) + 045 (3) |
| ...of which `plan-015`'s moved **IN** scope | −1 | Issue 3.3 performs its de-bold |
| **left out of scope** | **8** | this record |

**Nine would be wrong**, and SC12 says so explicitly: `plan-015`'s construct is the ninth of
D-2a's split and Issue 3.3 *performed* it, so listing it here would double-count a construct the
plan actually fixed.

## The eight

| # | Plan | Line | The construct | Measured reason it is not a relocation |
| --: | :-- | --: | :-- | :-- |
| 1 | `plan-010` | 193 | `- **Capability Gate G1**: `yf skills install` round-trips before Epic 5 deletes `install.py`.` | A gate written as a **column-0 bullet inside `## Epics`**, not a `###` gate block. It states a *condition* and nothing else — no `Type`, no `Test`, no `Blocks`. Relocating it would mean **authoring** those three fields, which is inventing content the document never carried, not moving content it does. |
| 2 | `plan-010` | 221 | `- **Capability Gate G2** (backed by Epic 6): …` | As #1. Two prose lines; the "backed by Epic 6" relation has no `Blocks` form in the document. |
| 3 | `plan-010` | 270 | `- **Capability Gate G3 (human)**: `HOMEBREW_TAP_TOKEN` secret present…` | As #1, and the human/consent semantics live only in the bolded title. |
| 4 | `plan-018` | 231 | `### Epic 6 (follow-on, NOT built in this plan): on-disk materialization seam + Windows` | **Not a gate at all.** A deliberately-not-poured epic heading. The extractor already reports it as `H3 inside ## Epics is not an epic heading`, which is the correct and *intended* reading — REQ-DATA-019 wants a declared marker here, not a silent drop. Nothing to relocate. |
| 5 | `plan-018` | 232 | `- Captured as deferred scope (decision 7 + Windows)…` | The prose bullet belonging to #4. It is deferral rationale, not an issue and not a gate. |
| 6 | `plan-045` | 459 | `### Skill-artifact isolation (pass-1 C10, corrected pass-3)` | **Not a gate at all** — a prose subsection heading inside `## Epics`, carrying a red-team resolution narrative. |
| 7 | `plan-045` | 465 | `- The `SKILL_DIR` resolver searches …` | Explanatory prose under #6. |
| 8 | `plan-045` | 470 | `- Testing is sandboxed-`HOME` per `TESTING.md` Tier-2 …` | Explanatory prose under #6. |

## The finding that matters most: `plan-045` clears NOTHING

D-2a records it and the measurement confirms it:

> **plan-045 — the only plan the original scope fully unblocked — is entirely in that category.**

All three of `plan-045`'s constructs (#6–#8) are **prose**. Relocating them is not a
content-preserving move; there is no gate content to move. The plan that the original
16-recovery scope promised to fully unblock would have been "unblocked" by deleting or
restructuring three paragraphs of red-team narrative — trading a legible document for a lower
residue number.

## Why relocating #1–#3 would REDUCE information

This is plan-047's visible→invisible conversion, reproduced inside the migration written to
avoid it. Turning `- **Capability Gate G1**: <condition>` into

```markdown
### Capability Gate G1
- Condition: yf skills install round-trips before Epic 5 deletes install.py
```

produces a gate with **no `Type` and no `Test`** — which is exactly the shape
`gate-completeness` (REQ-DATA-055) reports as vacuous, and exactly the shape the DAG guard's L4
layer treats as content-free. The residue count would fall while the document gained a gate
that asserts nothing and that every downstream consumer must now special-case.

**The right treatment is to leave them legible and refused.** A refusal is a finding; it names
the line and says why. That is strictly more information than a well-formed gate with three
empty fields.

## Reproduce

```bash
uv run _shared/plan_extract.py docs/plans/plan-010-* docs/plans/plan-018-* docs/plans/plan-045-*
```
