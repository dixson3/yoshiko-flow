---
type: Finding
okf_spec: OKF-PLAN
description: "The MATERIAL for the Diagram human-read gate — the redesigned set inventoried, with what changed in each and what an extractor cannot see. This document is NOT a read and does not discharge the gate."
id: diagram-presentation
plan: plan-067-james-dixson-de852a
created: 2026-09-07
---
# The redesigned diagram set — presented for the human read

> **THIS DOCUMENT IS NOT A READ, AND IT DOES NOT DISCHARGE THE GATE.** It is the material the
> gate needs: what exists, what changed, and where the mechanical checks stop. The
> **Diagram human read** gate is `gate_type: human`, and an agent read is **evidence, never a
> discharge** — plan-066 measured a corrected diagram whose count was right and whose
> **membership was wrong**, which is precisely the residue no extractor catches.

## What changed, structurally

The set went from **6 diagrams to 20**, and the change is a restructure, not an addition:

| Change | Before | After |
| :-- | :-- | :-- |
| combined | `phase-model.d2` + `lifecycle.d2` | one `lifecycle.d2` |
| combined | `install-matrix.d2` + `tune-matrix.d2` | one `install-matrix.d2` |
| removed | `formulas.d2` (generic ER meta-diagram) | — (per `#373`) |
| replaced by | — | `formulas-map.d2` + 5 per-formula diagrams |
| rebuilt | `architecture.d2` | a layered marketecture |
| added | — | 11 GENERATED per-skill diagrams |

## The inventory

| Diagram | px | h/w | What to look for |
| :-- | :-- | --: | :-- |
| `architecture.png` | 7036 x 7554 | 1.07 | the three layers reading AS layers; whether 12 skill→skill edges are followable or a hairball |
| `lifecycle.png` | 4364 x 11602 | **2.66** | the tallest in the set. Does the nesting read, or does it become a column? |
| `install-matrix.png` | 8948 x 3672 | 0.41 | whether `surface_dir` and `skills_subpath` read as DIFFERENT things |
| `formulas-map.png` | 3986 x 3662 | 0.92 | whether "who owns what, who dispatches whom" is answerable at a glance |
| `formulas/plan-execute.png` | 2992 x 4722 | 1.58 | the declared-vs-injected split |
| `formulas/plan-investigate.png` | 7292 x 728 | 0.10 | very wide; does the burn warning survive the aspect ratio? |
| `formulas/plan-review.png` | 5798 x 1634 | 0.28 | whether the non-goals box competes with the chain |
| `formulas/verify-artifact.png` | 2710 x 2672 | 0.99 | whether the right/wrong attachment contrast lands |
| `formulas/yf-research.png` | 7558 x 1092 | 0.14 | the fan-out/fan-in around a linear chain |
| `skills/*.png` (11) | 2056-4380 wide | 0.30-1.21 | whether 11 near-identical generated diagrams are USEFUL or noise |

## What the mechanical checks DID establish

So the read can concentrate on what they cannot:

- Every committed `.png` is **sha256-identical** to a fresh render under the pinned
  `d2 v0.8.2 --theme 0 --layout elk` (`render-bytes-match`, 20 diagrams).
- Counts and **enumerated member ids** agree with `skills/*/SKILL.md` frontmatter, with
  `not_checked_groups == 0` — no group states a count while listing nothing (`check_web_counts`).
- All 12 declared `depends-on-skill` edges are drawn in `architecture.d2`, and the 8-tool layer
  and the `yf` subcommand paths are present (`architecture-complete`).
- The combined lifecycle carries the red-team cycle, gates, escalations, retrospectives,
  autonomy, `capture`, execution and land-the-plane, and uses the real literal
  `system_deps_missing` (`combined-diagrams`, `#375`).
- No `.d2` lacks a `.png`; no render is a single-column stack (`render.py check-dir`,
  `build-and-render`).
- The 11 per-skill diagrams byte-match a fresh generation (`skill_diagrams.py --check`).

## What NO check can see, and what the read is FOR

- **Label placement, overlap and truncation.** Nothing above measures whether two labels collide.
- **Whether the picture communicates.** `architecture.png` is 7036 x 7554 — mechanically complete
  and possibly still too busy, which was the ORIGINAL objection that started this plan.
- **Semantic mis-assignment beyond the id sets checked.** A box in the wrong cluster with the
  right count is invisible to every check above. That is the plan-066 defect, by name.
- **Whether 11 generated per-skill diagrams earn their place.** The threshold is computed and
  defensible; whether the *reader* wants eleven is not a question a threshold answers.

## The two open questions this read should settle

1. **`lifecycle.png` at 2.66:1 and 11602px tall.** Three layouts were measured; the all-`right`
   variant was 23042px wide at 10:1 and worse. This is the best of the three, and it may still be
   the wrong shape. **A judgement, not a measurement.**
2. **The per-skill set at 11.** Publication is `nodes >= 5`, re-derived and sitting on a
   three-way tie, so 11 is defensible but not inevitable — 8 or 16 are one definitional step
   away, and the census records both.

## Outcome

On acceptance, plan-066's `diagram-reads` record is updated for the new set, its gate opens, its
Issues 8.1/8.3 run, it reaches `complete`, and `#317` closes. **This plan does not resolve that
gate.** `plan066-still-green` currently reports exactly one FALSE criterion — `diagram-reads` —
and reports it as the **declared handoff**, not a regression.
