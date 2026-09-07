## plan-066 PARTIALLY landed — this tracker STAYS OPEN

`plan-066-james-dixson-e7fadb` merged to `main` as a **deliberate partial land**. The plan remains
in `executing`; it has **not** reached `complete`. This is the coarse tracker for that effort, and
it stays open until the plan does complete — the substantive write-ups are on the individual
issues.

### What landed

| Epic | Outcome |
| :-- | :-- |
| 0 | SPEC-first: the drift engine's own contradiction repaired — `REQ-CHECK-004` split, `-005` scoped, `-008`/`-009` added, `REQ-SCHEMA-002`/`REQ-DRIFT-011` widened |
| 1 | **P0: the site builds again.** One missing page; nothing behind it |
| 2 | Four checkers + code-side negative controls, wired into both `CHANGE-VALIDATION.md` tiers and a CI job |
| 3 | `DRIFT-CHECK.md`: 3 nodes, 7 edges, the `skill-page` §4 row, and the vacuous `e-okf-version-pin` category fixed |
| 4 | 40 checker-derived findings repaired across 10 files |
| 5 | All six diagrams re-rendered under a pinned `d2 v0.8.2`; 6/6 sha256-identical |
| 6 | `land`, escalations, autonomy, retrospectives, `closable` documented |
| 7 | Adjacent surfaces: #363, #322, #104 |

### Verification

- FULL `CHANGE-VALIDATION` tier: **79 rows, 0 failing**
- Success criteria: **27 total — 25 hold, 1 FALSE (the ungated retrospective), 1 not-evaluated
  (the manual diagram read)**
- All four checkers **observed to FAIL** against code-side mutations (4/4)

### What is NOT done

The **diagram human-read gate was not accepted** — a redesign is pending in a follow-on plan
(layered marketecture, per-skill and per-formula diagrams, combined phase/lifecycle and
install/tune matrices, plus a `DRIFT-CHECK.md` amendment making omissions FAIL). The diagrams as
they stand are factually correct and mechanically checked; the outstanding work is design, not
correction.

Gated behind it: the retrospective, the verification sweep, and the remaining reconcile
bookkeeping.

### Issues reconciled

Closed: **#104**, **#127**, **#363**, **#322** — their scope is complete and unaffected by the
diagram work.
Left **open**: **#317** (its acceptance requires the ungated retrospective), **#247** and **#263**
(partials — this plan closed the four Class-B coverage gaps #317 enumerates, not the whole of
#247's manifest gap, and the `optional`/`required` token defect is one instance of #263's META
class rather than the class itself), and **this tracker**.
Filed: three follow-ons under D5 (file, do not fix).

### One process note worth keeping

**This tracker was very nearly left stale, and the mechanism that should have prevented that did
not fire.** `plan_manager.py stamp-tracker` runs at pour to record the tracker URL as the epic's
`external_ref`, which is what makes it visible to `upstream.py closable`. It returned
`skipped — no coarse tracker found in plan.md Upstream Issues (no row with disposition tracker)`,
because this plan's Upstream Issues table carries no `tracker`-disposition row. So the tracker
existed upstream while being invisible to the local mechanism that enumerates closable issues.

That is the documented failure mode here — five trackers (#103, #95, #96, #98, #134) have gone
stale and been closed by hand. It was caught this time by an operator reading the write table and
noticing an absent row, which is not a mechanism.
