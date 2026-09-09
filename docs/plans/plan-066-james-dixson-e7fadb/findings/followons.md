---
type: Finding
okf_spec: OKF-PLAN
description: "Issue 8.4 — every follow-on this plan and its successor produced, tagged by class, with what closed and what remains open. Local beads only; none pushed."
id: followons
plan: plan-066-james-dixson-e7fadb
created: 2026-09-08
---
# Follow-ons, tagged by class

## What D5 asked for

File the defects this plan **found but did not fix**, tagged by class, so none becomes a stale
tracker. `#317` named three candidates; the honest answer is that two of them are now **closed by
the successor plan**, and the open set is different from the one anticipated.

## CLOSED — no follow-on needed

| Item | Class | Closed by |
| :-- | :-- | :-- |
| the zero-byte-page guard hole | pipeline | **plan-067 Issue 5.7** (`#374`). The guard was `os.path.isfile` only, so `touch` satisfied a check whose purpose is that a *governed* page exists. It now measures renderable prose, with a control observed end to end: a zero-byte page makes the build exit **1** |
| `e-okf-version-pin`'s category defect | manifest | **this plan, Issue 3.6.** Its §2 Check Category read `value-equal`, a §3 CONTRACT term outside the §2 vocabulary, so the edge selected **no check engine and was vacuous**. Corrected to `contract` |

Both are recorded here rather than dropped, because "we fixed it" and "we never filed it" look
identical a year later.

## OPEN — filed as local beads, tagged by class

| Bead | Class | What |
| :-- | :-- | :-- |
| `yf-w57p` | pipeline | `check_web_counts`'s region logic is **shape-specific** — one `is_d2` switch stands in for "what a document looks like". Latent: `DEFAULT_CORPUS` expands only `.md` and `.d2`, so nothing in the shipped recipe reaches it. It bites the moment anyone points `--corpus` at a third shape, and the failure mode is a burst of confident false FAILs. **Twice observed** on two different third shapes |
| `yf-8g5x` | environment | **`d2` was upgraded v0.8.2 → v0.9.0 on this machine, outside any session.** Both plans' `render-bytes-match` is now INCONCLUSIVE — correctly, since byte equality is decidable only *within* a version. The 21 committed PNGs are unchanged and correct for their pin. Two options, both the operator's, and one of them requires a fresh human read |
| `yf-2eyf` | pipeline | `plan_extract.py --strict` validates neither self-edges nor cycles in the plan DAG |
| `yf-pvft` | pipeline | `yf-okf-hygiene`'s `_index.md` legacy-variant transform manufactures a hybrid state |

**None is pushed.** They are local beads; whether any goes upstream is the operator's call at the
Upstream write authorization gate.

## The one that is NOT a follow-on, and why

**Script-verb coverage is a declared limit, not an open defect.** Measured: `plan_manager.py`
carries 40 flat `@cli.command` registrations with **zero** visibility metadata, and `spec/cli.md`
`REQ-CLI-006` frames the whole set as internal delegation. There is no bit in the source to read.
`REQ-CHECK-010` excludes the class **by name** and every relevant checker says so in its own
`not_checked` output.

Filing it would imply a fix somebody has not done; calling it closed would be false. It is
neither — it is **declared**, and the distinction is the point of `REQ-CHECK-009`.
