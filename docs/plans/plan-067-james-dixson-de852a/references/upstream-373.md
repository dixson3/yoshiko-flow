---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #373 - Diagram set redesign + make DRIFT-CHECK omissions
  FAIL'
---
# Upstream #373: Diagram set redesign + make DRIFT-CHECK omissions FAIL

- **Number:** 373
- **Title:** Diagram set redesign + make DRIFT-CHECK omissions FAIL
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Split from plan-066 (#317) at its Diagram human-read gate. The operator read the six regenerated PNGs and did **not** accept them — not because any diagram makes a false claim, but because the set needs restructuring and because several real relationships are **absent**.

That distinction is the point of this issue, and it is why the two halves belong together.

## Why the two halves are one issue

plan-066 established, and leaned on, `DRIFT-CHECK.md:207`'s rule that a page which **"curates or omits repo-dev detail PASSes — only an affirmative contradiction FAILs"**. Under that rule an omission is invisible by construction.

The measured cost of that rule: `land`, retrospectives, the escalation surface, autonomy levels and `closable` went undocumented across multiple releases and **nothing ever complained**. plan-066 repaired them as editorial work precisely because no edge could have flagged them. The same rule is why `architecture.d2` could omit the `workflows` group entirely — a whole cluster missing, passing every check.

So a redesign alone re-drifts. The rule change is what keeps the new diagrams complete.

## Half 1 — the diagram set

**`architecture`** — restructure as a layered marketecture stack:

- **bottom:** CLI/tool dependencies — `bd`, `gh`, `pandoc`, `d2`, `uv`
- **middle:** beads skills and utility skills
- **top:** workflow skills

and show the **workflows → utility** dependency, which the current diagram omits. To keep it legible, break each skill out into its own small diagram showing its dependencies and what it wrappers — e.g. `yf-markdown-lint` over its specific linting script — rather than crowding one canvas.

**`formulas`** — remove the meta-diagram about formulas in general. Replace with:

- one diagram per shipped formula (`plan-execute`, `plan-investigate`, `plan-review`, `verify-artifact`, `yf-research`)
- a separate diagram mapping **which skills/agents drive which formulas**

**`phase-model` + `lifecycle`** — combine into one, and add what is currently missing: the **red-team review cycles**, **execution**, and **land-the-plane**.

**`install-matrix` + `tune-matrix`** — combine.

## Half 2 — make omissions FAIL

Amend `DRIFT-CHECK.md` so an omission is a failure, not a silent pass.

**A blanket `field-set-subset` → `field-set-equal` flip is the wrong shape** and should not be implemented as such: it would require every page to restate everything in its source, including repo-dev internals a user-facing page deliberately curates out, and would redden many currently-green edges at once.

The proposed form is a **declared required set**:

- omitting a **user-facing surface** — a slash verb, a shipped command, a documented behavior such as `land` or `closable`, a `skill-group` cluster — **FAILs**
- repo-dev internals may still be curated out

This preserves curation while closing the hole that let five real features go undocumented.

**Suggested sequencing, from plan-066's D1 precedent:** land the rule change *first*, let it fail the current diagrams and pages loudly, and use that failure list as the redesign's work inventory — a checker-derived inventory rather than a hand-written one. plan-066 measured that approach finding 4 defect sites its source issue did not list, and correcting an undercount from ~4 to 26.

## State of plan-066

- The six current diagrams are **factually correct and mechanically checked** — the `beads group` membership bug (count 8 while listing the *workflows* skills), the retired `lowercase-hyphen,max64` annotation, the absent `workflows` group and the three-vs-five formula count are all repaired, and `check_web_counts` now catches that class.
- All six PNGs are byte-identical to a fresh render under the pinned `d2 v0.8.2`.
- plan-066 **remains in `executing` with its Diagram human-read gate shut** and SC11 unmet. It has **not** been reported complete. Its P0 (the site had not built since plan-057) and its Class-A/Class-B work were landed to `main` so the site stops being broken while this work is planned.
- #317 stays **open**: its acceptance requires a retrospective that is gated behind that read.

## Related

- #317 — the parent; stays open
- #263 — omissions-pass-silently is another instance of "two facts, one signal"
- #247 — drift findings no declared edge covers

