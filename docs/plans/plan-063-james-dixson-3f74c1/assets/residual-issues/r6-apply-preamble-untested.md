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
