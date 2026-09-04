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
