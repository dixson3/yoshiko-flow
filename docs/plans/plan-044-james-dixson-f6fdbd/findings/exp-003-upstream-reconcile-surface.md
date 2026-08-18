---
type: Finding
okf_spec: OKF-PLAN
id: exp-003-upstream-reconcile-surface
plan: plan-044-james-dixson-f6fdbd
created: '2026-08-17'
---

# exp-003 — The upstream reconcile/closable surface (#144, #142)

**Date:** 2026-08-17
**Question:** What does `upstream.py` actually do about upstream issue state, and what would it take to fix #144 (bead stays open when its issue closes) and #142 (`closable` proposes already-closed/deleted issues)?
**Method:** read-only source trace of `skills/yf-beads-upstream/scripts/upstream.py` (1331 lines) plus live read-only measurement against this repo's bead DB and GitHub.

## Headline

**No code anywhere in the repo reads an upstream issue's state for reconciliation.** Exactly
three files call `gh` at all, and none of them consult issue state on the reconcile path:

| File | `gh` usage | Direction |
| :-- | :-- | :-- |
| `upstream.py` | `gh label list` (L682), `gh issue create`/`edit` (L755, L765) | writes only |
| `beads_hygiene.py` | `gh_issue_list()` L486–511 — hardcoded `--state open` | bead → issue |
| `plan_manager.py` | `_gh_issue_view()` L1750 — the only per-issue state read | plan-table assertion |

So local↔upstream state is reconciled in **one direction (bead → issue), by two independent
paths, and in zero directions the other way.**

## #142 — confirmed, and much larger than filed

`closable_candidates()` (L1126–1162) groups beads by the **raw `external_ref` string** and sets
`closable` iff no mapped bead is non-closed (`_is_closed`, L220). `gh` is never consulted. The
limitation is already admitted in prose at `SKILL.md:540` — so the current behavior is
**spec-conformant**, making #142 a SPEC gap before it is a code gap.

Measured (`closable --json`, 0.96 s, exit 0) cross-referenced against
`gh issue list --state all --limit 400`:

| Bucket | Count |
| :-- | --: |
| Mapped issues | 50 |
| Marked `closable` | 36 |
| `gh issue close` commands emitted | 35 |
| — already CLOSED upstream | 28 |
| — ABSENT/DELETED (#139) — command would error | 1 |
| — unparseable ref (`gh-91`) — **silently emits nothing** | 1 |
| **Genuinely actionable** (#142, #143, #147, #150, #152, #153) | **6** |

**83% of emitted commands (29/35) are no-ops or errors.** This verb is wired into the
always-loaded land-the-plane sequence, so this is the precise erosion pattern that trains an
operator to stop reading proposals.

## #144 — real, n=1 today, bounded by mapping coverage

1136 beads total; **50** carry an `external_ref`; **14** of those are non-closed. Exactly one is
the #144 class:

| bead | local | upstream | upstream state |
| :-- | :-- | :-- | :-- |
| **yf-1656** | **open** | **#132** | **CLOSED 2026-08-16T18:07:16Z** |
| yf-m78m … yf-3d13, yf-7mbi, yf-hg4w (12 beads) | open | #118–#127, #149, #151 | OPEN |
| yf-uz5k | deferred | #92 | OPEN |

Why `plan_manager.py`'s `verify-reconcile` did not catch it: it keys off **plan.md Upstream
Issues table rows** (L1863), not off `external_ref`, and its output is a pass/fail *assertion*
about the issue (L1791–1838). For plan-040's `#132 / supersede` row it would return **`pass`** —
#132 *is* closed as intended. The mirror bead was never in its field of view.

The reconciler's reach is bounded by mapping coverage (50/1136), not by the bug.

## Two incidental defects found in the same code

1. **`external_ref` format drift is live.** `yf-4d7s` carries `external_ref = "gh-91"` (1 of 50).
   The two readers disagree: `external_for()` (L346–354, `EXTERNAL_RE` L70) demands `https?://`
   and reports it **unmapped**; `external_from_row()` (L357–370) takes any non-empty string and
   reports it **closable**. Nothing in SPEC constrains the value's shape.
2. **Silent unparseable-ref drop.** `issue_number_from_url("gh-91")` returns `None`, so
   `cmd_closable` L1204–1206 skips the row with **no diagnostic** — 36 closable, 35 commands.
   Compare GR-BUP-008, which exists precisely to forbid a silent *label* drop one function away.

Both argue a reconciler must normalize to an **issue number**, not string-match a URL.

## Deleted vs closed (measured)

```
gh issue view 132     → exit 0, {"state":"CLOSED"}
gh issue view 139     → exit 1, GraphQL: Could not resolve to an issue ... (139 was deleted)
gh issue view 999999  → exit 1, byte-identical error modulo the number
```

**A deleted issue is indistinguishable from a never-existed number.** A reconciler cannot tell
"deleted" from "typo/format drift" on the `gh` signal alone; both must classify as
`UNRESOLVABLE` and route to a human — never auto-close a bead on that basis.

The bulk form gives this free: `gh issue list --state all` simply **omits** deleted numbers, so a
mapped ref absent from the bulk result is `UNRESOLVABLE` at zero extra cost. That is how #139 was
detected without any per-issue probe. (*Inferred, unverified:* a transferred issue also 404s, and
UNRESOLVABLE is correct-by-accident there.)

## Design conclusion

**#144 and #142 are the same missing input, not the same verb.** Both need one capability:
resolve current upstream state for every distinct mapped issue. Measured cost: **one bulk
`gh issue list --state all --json number,state` round-trip, 154 issues, sub-second.**

Recommended shape — one new `reconcile` verb plus a narrow in-place fix to `closable`:

- **`closable` must not be left wrong on its own.** It is in the land-the-plane sequence today.
  Minimum fix: annotate each row with `upstream_state`, stop emitting a command for non-OPEN
  issues, and degrade gracefully when `gh` is unavailable.
- **`reconcile`** emits both directions off the shared query.

**The asymmetric authority split is the load-bearing constraint:**

| Half | Reversible? | Authority |
| :-- | :-- | :-- |
| Close a **local bead** | yes — `bd close -r` tombstone (REQ-BUP-045), `unhoist` (L1211) restores | `--apply`-able |
| Close an **upstream issue** | no | **propose-only, no `--apply`** — REQ-BUP-052 + always-loaded rule |

`--apply` convention inherited from `push`: absent `--apply` *is* the dry run. One tension to
state explicitly in the new REQ: `push`'s preview renders locally with no network round-trip,
but `reconcile`'s proposal **cannot** be computed without a `gh` read. A `gh` failure must yield
**INCONCLUSIVE**, never an empty (falsely clean) proposal — the `plan_manager.py:1750` model,
not the `beads_hygiene.py:493–502` return-`[]`-on-failure model.

## SPEC gaps (SPEC-first: these land before any code)

`skills/yf-beads-upstream/SPEC.md` runs REQ-BUP-001…059, GR-BUP-001…008. Missing:

1. No REQ mentions reading upstream issue state at all.
2. No `reconcile` REQ — the upstream→local direction is unspecified.
3. No REQ on `external_ref` format/normalization (REQ-BUP-058 covers only omitempty
   serialization); nothing forbids the two readers disagreeing.
4. No REQ forbidding the silent unparseable-ref drop.
5. No guardrail against auto-closing a bead on an UNRESOLVABLE ref.

## Caveat on scope

`bd`/`gh` failures inside nominally read-only verbs still exit 1: the `run()` helper (L85–90)
raises `SystemExit` on any non-zero subprocess. Worth noting for any gate that shells these verbs.
