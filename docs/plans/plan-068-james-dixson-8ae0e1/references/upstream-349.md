---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #349 - The land --apply executor frame is outside both
  REQ-LAND-030''s wrapper and the test suite'
---
# Upstream #349: The land --apply executor frame is outside both REQ-LAND-030's wrapper and the test suite

- **Number:** 349
- **Title:** The land --apply executor frame is outside both REQ-LAND-030's wrapper and the test suite
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Shared cause

`REQ-LAND-030` (plan-063) made landing step dispatch fail-closed: an exception raised by a `LAND_EXECUTOR` step is caught and returned as a halting `inconclusive` row rather than a traceback. The wrap covers `out = globals()[fname](ctx)` and **nothing else**. These two findings are the same residual seen from two sides: the frame *around* the wrapped region - the `--apply` CLI preamble ahead of it, and the executor's own bookkeeping around it - got neither the wrapper nor any tests. A fix for either is naturally a fix for both, and a reader needs to see the frame as one uncovered region rather than two coincidences. **Sharpened by plan-063's own landing:** the digest-recheck preamble is exactly the uncovered frame that produced the `halt_class 5` halt it hit on resume.

Grouped per the coarse-granularity convention in AGENTS.md. Recorded during plan-063 and deliberately not fixed there.

---

## The `land --apply` CLI preamble has zero test coverage (bead `yf-acrn`)

**Found by plan-063 (EXP-002; raised again at pass-3 as Missing 1) and deliberately not closed.**

`land --apply`'s CLI preamble — everything between the `--apply` branch and the `_land_execute`
call — has **zero test coverage**. Measured: it is untested by anything.

That preamble now contains, in order:

1. `_land_assert_primary_checkout` (REQ-LAND-010)
2. the containment refusal, `_land_assert_outside_tree` (REQ-LAND-035, added by plan-063)
3. the tty gate (REQ-LAND-014)
4. the decision read + JSON parse
5. the `body_path` half of the containment refusal
6. `journal.recover()` and the four-way branch on its action (REQ-LAND-009)

**Every one of those is a gate, and (6) is the one that can re-push.** `recover()` is total over
seventeen states and its `action` is branched on four ways; an unhandled action silently becomes a
*fresh landing*, which is the single wrong answer that can re-post reconcile comments and re-push.

Coverage exists on either side of the preamble — `_land_execute` is covered comprehensively, and
`_land_tty_gate` / `_land_assert_outside_tree` are covered as helpers — but **the sequencing is
not**, and sequencing is the whole point: REQ-LAND-035 requires the containment refusal to precede
the tty gate so a refusal is never preceded by a write. plan-063 added
`test_the_containment_refusal_precedes_the_tty_gate`, which asserts that ordering **on the source
text**, not by execution. That is a real check and an honest one, but it is a proxy.

This is the `#263` vacuous-check class at the harness level, the same shape as `#327`: an engine
covered comprehensively behind an entry point nothing drives.

**Proposed fix.** Drive `land --apply` through the real CLI in a sandbox for each preamble
outcome, asserting the exit code and that **no write occurred** — one case per gate, plus one per
`recover()` action.

---

## The executor's own bookkeeping can still raise a bare traceback (bead `yf-pyqn`)

**Recorded by plan-063 at its own pass-3 review (C34), and explicitly OUT OF SCOPE of
`REQ-LAND-030`.**

`REQ-LAND-030` makes step dispatch fail-closed: an exception raised by a `LAND_EXECUTOR` step is
caught and returned as a halting `inconclusive` row rather than a traceback. The wrap covers
**`out = globals()[fname](ctx)` and nothing else**.

Outside it, still able to raise a bare traceback:

- **the journal write** — `ctx.journal.write(r["journal"], step=r["step"])`. `LandingJournal.write`
  validates against a closed 17-state set and **raises** on an unenumerated phase, so a step
  returning a bad journal value crashes *after* the step succeeded.
- **the row-shape access** — `r["verdict"]`, `r.get("halting")`, `r["step"]`. A step returning a
  malformed row (or `None`) raises `KeyError`/`TypeError` at the loop, not at the step.
- **the post-loop block** — `ctx.journal.read()`, `journal.clear()`.

**Why the scope was drawn there.** Wrapping the bookkeeping too would mean catching exceptions
raised by the *executor's own* invariant checks, and a caught invariant violation is much harder to
report honestly than a caught step failure: the executor would be reporting that its own
record-keeping failed, in a record. That needs its own design, not a wider `except`.

**Why it is filed rather than left implicit.** plan-063's `REQ-LAND-030` and its code comment both
state this scope explicitly, so the residue is *documented* — but a documented gap with no issue is
a gap nobody is going to close. Both texts were amended mid-execution to stop asserting a filing
that did not yet exist; this is that filing.

**Proposed fix.** Either (a) validate the row shape and the journal value *inside* the wrapped
region — return a halting `inconclusive` for a malformed row, which keeps one reporting path — or
(b) add a second, narrower guard around the bookkeeping that reports an executor-internal fault as
a distinct halt class.

---

<sub>Filed from plan `plan-063-james-dixson-3f74c1` (bundle: `docs/plans/plan-063-james-dixson-3f74c1`). Beads: `yf-acrn`, `yf-pyqn`.</sub>

