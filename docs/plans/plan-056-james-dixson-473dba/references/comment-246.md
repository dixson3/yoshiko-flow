---
type: Reference
okf_spec: OKF-PLAN
description: "Draft closing comment for #246 — resolved TOWARD the schema; the two E close-out checks are the only ones that can fail a completed bundle."
disposition: include
target: "#246"
---
**Fixed and closing. Resolved toward the SCHEMA, not toward the prose.**

You were right that `REQ-DATA-044`'s *"the `R*` rule family ships at severity `W`, **uniformly**"*
contradicted the shipped schema. It had been false since plan-052, when `R1-closeout` and
`R2a-closeout` landed at `E`.

**The resolution keeps the two `E` checks and amends the requirement, and the reason is the
measurement.** Re-measured 2026-08-28 with the terminal-status demotion disabled, the corpus yields
**197 `E` findings** over 1116 files; with it enabled, **`errors: 0`**. Those two checks are the
**only 2 of 55** in the whole `document_types/` set capable of producing an `E` at
`bundle_status: complete`. Deleting them to satisfy the old wording would have made `doc_lint`
**structurally incapable of failing a completed bundle** — which is the defect, not the fix.

**What landed:**

- **`REQ-DATA-044` amended** — the severity bullet now states the authoring-time binding is `W` and
  that the kind *additionally* carries an `E` close-out binding.
- **`REQ-DATA-074` added** — declaring the close-out binding, which plan-052 **implemented and
  documented nowhere**. Four elements, all load-bearing: a separate check (one check cannot carry two
  severities), the elevated severity, a `statuses` scope, and `promote = false`. The last is what
  makes it work at all — without it `STATUS_SEVERITY` demotes the `E → R` at exactly the statuses the
  check is scoped to, disarming the binding at the only moment it can fire. A close-out `E` without
  the opt-out is not a weaker check; it is **no check**.
- **All four copies of the false banner corrected** — `_shared/doc_lint.py`, its vendored twin, and
  both `plan-relations.toml` copies. The banner was **replaced rather than patched**, because
  `promote = false` is doing two *opposite* jobs on this one schema (suppressing an unwanted
  promotion at `review`, preserving a wanted severity at `complete`) and the one-line form could not
  state both. This also closes the `e-doclint-spec` drift edge, which named the engine banner
  explicitly.
- **`scripts/checks/check-closeout-can-fail.sh`** — a RED fixture carrying a close-out violation at
  `status: complete` produces an error, and the same fixture *without* the violation does not. Two
  branches, so a broken or absent linter cannot satisfy it.

Plan: `docs/plans/plan-056-james-dixson-473dba/`
