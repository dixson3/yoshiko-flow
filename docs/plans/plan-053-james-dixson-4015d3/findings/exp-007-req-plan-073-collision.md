---
type: Finding
okf_spec: OKF-PLAN
id: exp-007-req-plan-073-collision
description: Which side of the REQ-PLAN-073 collision to renumber, measured by live citation count
---

# EXP-007: the `REQ-PLAN-073` collision — which side moves?

> ## ⚠ THIS FINDING'S SITE COUNTS ARE WRONG. The recommendation survives; the arithmetic does not.
>
> **Refuted at pass 1 (C5) and again at pass 3 (C33/C37).** The error: the tables below were
> built from a `git grep` whose hits in **`SPEC.md`** are the **repo-root** `SPEC.md`, which
> this finding then attributed to `skills/yf-plan/SPEC.md`. The latter carries exactly **one**
> `REQ-PLAN-073` line, not three.
>
> | Claim below | Measured |
> | :-- | :-- |
> | roots: "three lines in one file" | cited across **six** files, repo-wide |
> | stamp: "four files plus a SKILL.md narrative" | **four** files — fewer live sites than roots |
> | live cost favours moving roots | **it favours moving the STAMP** — the opposite |
>
> The count itself moved three times across three review passes (3 → 12 → 14 → 15), which is
> why `plan.md` now records **no count literal** for it at all and `ctl-214-id-collision`
> enumerates the site set instead.
>
> **D-8 still stands, on ONE argument rather than two**: plan bundles are records that must
> never be rewritten, so the retired meaning strands its citations permanently — 8 for the
> stamp against 1 for roots. The live-site argument below is **withdrawn**.

**Measured directly in the drafting session** (not dispatched), because the question is a
two-command count rather than an investigation.

## The collision is real and current

```bash
git grep -n 'REQ-PLAN-073' skills/yf-plan/
```

| Site | Meaning |
| :-- | :-- |
| `skills/yf-plan/SPEC.md:345` | *the plan and incubator roots shall be configurable* (plan-037 / #107) |
| `skills/yf-plan/spec/phases.md:150` | **`stamp-tracker`** — stamp the coarse tracker URL onto the plan epic as `external_ref` |

#214's line numbers are confirmed exactly.

## It has been observed twice before and filed once

`plan-045`'s `findings/exp-006-spec-amendment-surface.md:86` recorded it on 2026-08-18 as
*"corroborating evidence"* for a different argument and did not file it. plan-052 re-confirmed
it as deferred defect **D4** and filed **#214**. So this is a **third** sighting — the first
two produced a note, not an id.

## `REQ-PLAN-079` is free

```bash
git grep -c 'REQ-PLAN-079'      # → no output: unused
git grep -ho 'REQ-PLAN-[0-9][0-9][0-9]' | sort -u | tail -3   # → 077, 078, 080
```

The vocabulary runs to `REQ-PLAN-080` with **079 unallocated** — an available id that needs no
renumbering of anything else.

## Recommendation: renumber the ROOTS requirement, not the stamp

The instinct is to move the newer requirement. **The citation count says the opposite.**

| Meaning | Live (non-record) citations | Historical bundle citations |
| :-- | --: | --: |
| **stamp-tracker** | `spec/phases.md:150`, `SPEC.md:349` (amendment log), `spec/cli.md:33`, `SKILL.md` §5.2a (twice, incl. a whole explanatory subsection) | plan-044, 045, 048, 049, 050, 052 — **8 references** |
| **roots** | `SPEC.md:345` (the definition), `SPEC.md:239`, `SPEC.md:919` | plan-037 `REDEPLOY-HANDOFF.md` — **1 reference** |

Renumbering **roots → `REQ-PLAN-079`** touches **three lines in one file**. Renumbering the
stamp would touch four files plus `SKILL.md`'s §5.2a narrative.

**Historical plan bundles are RECORDS and must not be rewritten** — which is the argument's
sharp end rather than a caveat. Whichever id is retired, the bundles that cite it keep citing
the old number forever. Retiring the meaning with **8** such references strands eight; retiring
the meaning with **1** strands one.

## Open question for the red-team

An id that is retired-but-still-cited-in-records is not free of cost either. Is a
**disambiguation note** at the retired id's location required, so a reader arriving from
`plan-037`'s handoff is not silently misrouted to the stamp requirement? This finding
recommends yes, and that the note is part of the fix rather than a follow-on.
