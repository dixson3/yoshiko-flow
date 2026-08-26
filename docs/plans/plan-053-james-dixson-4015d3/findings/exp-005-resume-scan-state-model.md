---
type: Finding
okf_spec: OKF-PLAN
id: exp-005-resume-scan-state-model
description: The resume-scan tri-state and clear-epic verb — the bd check already exists, SKILL.md just never reads it, and there are six states not three
---

# EXP-005: the `resume-scan` state model and `--clear-epic`

**Verdict: #207's DIAGNOSIS is partly refuted and its SUGGESTED FIX should be rejected — but
the wedge it reports is real and reproduces exactly. The `bd` reconciliation #207 asks for
ALREADY EXISTS. The defect is that `SKILL.md` §5.2 never reads it. And the state space is
SIX-valued, not three.**

## The wedge reproduces — and the signal was there all along

`found` is set at `plan_manager.py:4196` as `epic_id is not None` — purely "was an id
recorded", never consulting `bd`. #207 is right about that.

But **`epic_resolves` already exists** at line 4210 (plan-044 Issue 3.9 / #143), does consult
`bd`, is specified at `spec/cli.md:72` (REQ-CLI-013), and is tested at
`test_epic_ref_audit.py:146-180`.

Measured on a sandbox bundle with a nonexistent epic id:

```
"epic_id": "astrospike-mol-ppt", "epic_source": "plan_md",
"found": true, "epic_resolves": false, "total": 0, "open_work_remaining": 0     EXIT=0
```

The wedge is exactly as filed. **But `SKILL.md:844-850` extracts only `found` and
`stale_approved`, and the bullets at `:858-864` branch on `found` alone** — as do REQ-RESUME-001
(`spec/phases.md:69`) and REQ-RESUME-004 (`:83`).

> **So #207's real defect is narrower than filed, and cheaper: do not re-implement the
> existence check. Read the one that shipped a plan ago.**

The **human** (non-`--json`) output is worse than the JSON — it prints the epic, the descendant
count and "no stuck beads", and says *nothing* about `epic_resolves`. A dangling ref is
invisible on that path.

## Six states, not three — and two of the new ones are live hazards

| # | State | `epic_state` | §5.2 routing |
| --: | :-- | :-- | :-- |
| 1 | no epic recorded | `none` | **POUR** — normal first execution |
| 2 | present, open work | `present` | **RESUME** |
| 3 | present, all descendants terminal | `complete` | **NEITHER** — report finished, route to Phase 6 |
| 4 | recorded but **absent** from tracker | `stale` | **POUR** after reporting + clearing — the #207 case |
| 5 | present, but `metadata.plan_dir` names **another plan** | `foreign` | **HALT** — operator decision |
| 6 | `bd` unavailable / DB unreadable | `unknown` | **HALT — INCONCLUSIVE**, never pour |

**State 5 is a measured, live hazard.** Copying the plan-052 bundle to a sandbox path left its
epic `yf-mol-f2q` resolving with `counts:{closed:46}` — while the epic's own
`metadata.plan_dir` still named `docs/plans/plan-052-james-dixson-fa8056`, **a different
directory than the one scanned**. A copied bundle silently resumes another plan's epic. The
discriminator is already loaded in `_resume_scan`'s bead dict, so the check costs nothing.

**State 6 is the dangerous one.** An unreadable tracker looks exactly like a burned epic;
guessing "gone" produces the duplicate pour §5.2 exists to prevent. Note the current overload:
`epic_resolves is None` is returned *both* when `bd` is unreachable **and** when no epic is
recorded. The enum removes that.

## #207's suggested JSON shape should be REJECTED

#207 proposes `found: false, stale_pointer: "<id>"`. Three reasons against:

1. **It makes `found` assert something false.** An id *is* recorded. `found` has one clean
   meaning today; flipping it for the stale case silently changes behaviour for any caller not
   updated in lockstep — and it is the only field `SKILL.md` reads.
2. **It re-overloads one boolean with two facts.** `found: false` would mean both "no pointer"
   and "dead pointer", whose correct handling differs. **That is the #181 defect exactly** —
   `doc_lint` added a `class` field rather than keep overloading the exit code, and established
   the rule *branch on the class, never on the exit code alone*. `epic_state` is the same
   remedy in the same codebase.
3. **A boolean cannot express six states.** States 3, 5 and 6 have no representation at all,
   and state 6 has no room for INCONCLUSIVE.

Operationally: a caller branching on `epic_state` that meets an unrecognised value **fails
loudly**; a caller branching on a semantically-changed `found` **fails silently, taking the
pour path**.

Recommended: add `epic_state`, `epic_status`, `epic_plan_dir`; **keep `found` and
`epic_resolves` verbatim** for back-compat.

## `bd` probe mechanics — measured

| Command | Exit | Note |
| :-- | --: | :-- |
| `bd show <missing> --json` | **1** | `{"error":"no issues found…"}` — distinguishable |
| `bd show <present> <missing> --json` | **0** | **the missing id is dropped SILENTLY** |
| `bd list --all --json` | 0 | 1605, identical to `--limit 0` |
| `bd list --all --json` in a non-repo dir | **1** | no JSON at all |

Two corrections to my briefing: the **50-row truncation trap does not apply** here — `--all`
already lifts it, so budget nothing for it. The real trap is **batched `bd show`**: any
existence probe must be single-id and must inspect the returned array, never the exit code.

## `clear-epic`: three surfaces, a merge-only writer, and a fallback that undoes it

`record-epic` writes **three** surfaces, not two: the frontmatter `epic:` key, the `**Epic:**`
header line, and an inert `intake: epic <id> poured` bullet in `log.md`.

**`okf.write_frontmatter` is merge-only and has no delete path** (`_shared/okf.py:173-195`), so
this needs a new delete-capable helper. That touches an **OKF-owned helper shared by yf-research
and yf-incubator** — a wider blast radius than "add a verb".

**The load-bearing gotcha, measured:** clearing the plan.md fields does **not** reopen the pour
path if the epic bead survives — `_resume_scan` falls back to the `metadata.plan_dir` stamp and
returns `found: true, epic_source: "bd_metadata"` again. The reporter's hand-edit worked only
because their epic had been *burned*. `clear-epic` must report `metadata_fallback_remains: true`
and say plainly that the clear will not take effect.

Design: its own verb (not a flag on `record-epic`, whose `epic_id` is a required positional);
removes surfaces 1–2, keeps 3 as history, appends a `pointer cleared` bullet; idempotent;
**refuses on `present` and `unknown` without `--force`**. The fingerprint is unperturbed — both
blocks sit above the first `## ` (REQ-PORT-040), measured.

## Tests

`skills/yf-plan/scripts/test_epic_ref_audit.py` — already holds three `epic_resolves` tests, a
`_write_plan` fixture builder, and monkeypatches `_all_plan_beads` so it never shells to `bd`.
Six copy-pasteable RED assertions were returned (stale / unknown / foreign / complete / none /
`_clear_plan_fields`); they fail today with `KeyError: 'epic_state'`.

**Mechanically enforced SPEC-first:** REQ-CLI-006's set-equality test
(`test_cli_enumeration.py`) fails the moment the verb lands without the matching `spec/cli.md:33`
edit — the enumeration literal goes 31 → 32. That suits D-4 exactly.
