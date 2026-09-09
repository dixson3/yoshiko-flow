---
type: Retrospective
okf_spec: OKF-PLAN
description: "plan-066's retrospective: 26 content defects and 9 process defects, counted separately, plus the finding that outlasted the plan — its diagram set was fully green and was declined, twice over, by a human read."
id: plan-retrospective
plan: plan-066-james-dixson-e7fadb
created: 2026-09-08
---
# Plan retrospective — plan-066-james-dixson-e7fadb

## Why the two classes are counted separately

A **content defect** is a false or absent claim in a shipped artifact. A **process defect** is a
defect in the thing that was supposed to *catch* it — a checker that reads past its subject, an
edge with no firing surface, a criterion that cannot fail.

They are counted apart because they have different remedies and opposite failure modes. A content
defect is found by looking; a process defect is found only by making the instrument fail on
purpose. `#317` asked for the separation explicitly, and the reason shows in the numbers below:
**the corpus was green while every content defect existed.**

## Counts

| Class | Count | What it means |
| :-- | --: | :-- |
| **Content defects** | 26 | false or absent claims in shipped artifacts |
| **Process defects** | 9 | defects in the instruments that should have caught them |
| **Instrument false-greens** | 1 | an instrument reporting PASS over input it could not see |

**The content count was corrected upward during execution, from ~4 to 26**, by a
checker-derived inventory rather than by re-reading the issue. `#317` named roughly four sites;
the inventory found 26, including four the issue never listed. That correction is the whole
argument for D1's rule-before-repair order, and plan-067 inherited it as its own D2.

## Content defects (26)

Enumerated by site in [findings/class-a-inventory.md](findings/class-a-inventory.md). The
concentrations:

| Surface | Count | Representative |
| :-- | --: | :-- |
| harness paths and `name_transform` | 9 | retired `.config/opencode/skills` roots taught as current; a `lowercase-hyphen,max64` transform that no longer exists |
| multi-backend upstream claims | 6 | pages teaching `bd gitlab push` for a mechanism that is `gh`-direct and GitHub-only |
| skill counts and group membership | 5 | `19 skills` where 20 ship; `beads group (8)` listing the *workflows* skills |
| formula set | 2 | `three shipped standard formulas` where five ship |
| the P0 build break | 1 | a twentieth skill added with no authored page; the site did not build |
| other prose | 3 | removed features taught as present; unqualified claims |

## Process defects (9)

| # | Defect | Why it is a PROCESS defect |
| :-- | :-- | :-- |
| P1 | `REQ-CHECK-004`'s two halves were stated as one requirement | put the reachability half in contradiction with `REQ-CHECK-005`, so a node-level check had **no firing surface at all** |
| P2 | `skill-page` was a `required` node nothing enforced | a skill shipped with no page, and the site broke. Coverage existed; detection did not |
| P3 | three well-specified edges were assigned to an LLM prose judge over a node set that excluded `.d2` | 7 live mismatches across 4 files, structurally out of reach |
| P4 | `web/content/**` fanned out to ONE narrow edge | seven documents had no content coverage whatsoever |
| P5 | no edge covered the upstream-backend claim | six false multi-backend claims, none reachable |
| P6 | `e-web-cli-surface` excluded `harness_desc.rs` | the install-root table could drift with nothing watching |
| P7 | a derived-side-only §6 trigger | measured on commit `75a5796`: it added a skill and broke the build while touching **zero** files on the derived side |
| P8 | `optional`/`required` reachability enforced nothing | the distinction was decorative |
| P9 | `render.py check-dir` was cited as a staleness check | it exits non-zero only on ORPHANS; staleness never affects its exit code |

## The instrument false-green

**EXP-001's checker B** returned `PASS (0 mismatches), EXIT=0` against a tree carrying **15 real
defects**. The shared root `.agents/skills` *contains* the harness id `agents`, so repaired rows
scanned as ambiguous and were silently skipped. The checker was wrong in exactly the direction
that looks like success.

That single measurement is why this plan's negative-control convention is **inverted**: repair the
DOCS until the checker is green, *then* mutate the SOURCE OF TRUTH and require a FAIL. A doc-side
control could never have caught it — the docs were already broken and the checker was already
silent.

## The finding that outlasted the plan

**This plan's diagram set was fully green and was declined by a human read** — every checker at 0,
all six PNGs byte-identical to a fresh render under the pinned `d2 v0.8.2`. The decline was not a
correction; it was a redesign request, and it produced `#373` and plan-067.

plan-067 then presented a first 20-diagram set, **also fully green, also declined**, which produced
its Epic 7 restyle. The restyled 21-diagram set was **accepted on 2026-09-08**, on a single reading
covering both plans.

| Set | Mechanically | Verdict |
| :-- | :-- | :-- |
| plan-066's six | fully green | **DECLINED** → `#373` |
| plan-067's first twenty | fully green | **DECLINED** → Epic 7 |
| plan-067's restyled twenty-one | fully green | **ACCEPTED** |

**The checks were not wrong on any of the three occasions.** They were answering a different
question from the one that decides acceptance, and **no mechanical signal distinguished the
accepted set from the two declined ones**. That is the strongest evidence this repository has for
`gate_type: human`, and it is worth more than either plan's diagram work: it is three
measurements, not an opinion.

## What this plan changed about how defects are caught

- **`REQ-CHECK-008`**: a decidable predicate must be realized as a **runnable checker**, and the
  **source-side trigger is mandatory** — an absent file is never edited and can never fire its own
  on-edit check.
- **`REQ-CHECK-009`**: a mechanical gate must **declare what it does not cover**, in its own
  machine-readable output. A green with an undeclared boundary is indistinguishable from a green
  with none.
- **Code-side negative controls**, inverted as described above, with a vacuity floor in the
  harness rather than only in the criterion.

## The rate to carry forward

Twenty-six content defects, nine process defects, one false green — and the corpus was green
throughout. The number to remember is not 26. It is **three**: the number of fully-green diagram
sets it took before a human read accepted one.

## RE-001

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-09 |
| `stop_class` | 5 |
| `asked` | Can plan-066's §6.4 close chain run to complete? |
| `answered` | NO — verify-reconcile fails 5 of 7 upstream rows and the chain HALTS. Reported, not worked around. Four of the five need upstream comments nobody had authorized; the fifth is an ordering conflict between the authorized step order and the chain's own gate. |
| `frontloadable` | partial |
| `detected_by` | mechanical-check |
| `evidence` | verify-reconcile verdict fail: #317 OPEN (an include row must be CLOSED); #104/#127/#363/#322 CLOSED but no comment carries the full plan id plan-066-james-dixson-e7fadb — each says only 'Fixed in plan-066'. |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

## RE-002

| field | value |
| :-- | :-- |
| `kind` | stop |
| `when` | 2026-09-09 |
| `stop_class` | 5 |
| `asked` | Can plan-066's §6.4 chain now reach complete, with verify-reconcile cleared? |
| `answered` | NO. It clears verify-reconcile (7/7) and stops one step later at close-reconcile-step: the reconcile gate cannot resolve while Issue 8.4b is open, and 8.4b's HARD GUARD requires HEAD on main. plan-066 completes at LAND, by its own design. Not forced. |
| `frontloadable` | yes |
| `detected_by` | mechanical-check |
| `evidence` | close-reconcile-step exit 1: 'the reconcile gate [yf-mol-a927.14] is not resolved'. 8.4b guard: branch-merged TRUE (plan-066's execute branch is in git branch --merged main), HEAD==main FALSE (HEAD is plan-067-james-dixson-de852a-execute, 24 ahead / 0 behind). |
| `escape_class` |  |
| `adjudication` |  |
| `origin` |  |
| `culpability` |  |
| `prevention` |  |
| `cost` |  |

