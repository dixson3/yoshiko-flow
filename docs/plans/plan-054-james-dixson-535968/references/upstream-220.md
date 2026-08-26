---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #220: yf-plan: the RED-observation ledger cannot distinguish a driven RED from a real failure (and `grant --check` does not verify amendments)

- **Number:** 220
- **Title:** yf-plan: the RED-observation ledger cannot distinguish a driven RED from a real failure (and `grant --check` does not verify amendments)
- **URL:** 
- **State:** OPEN
- **Labels:** priority::medium, type::bug

## Body

**Measured:** plan-052, at execution — by the plan's own §6.4 halt, on the plan's own harness.

## Finding 1 — the RED-observation ledger cannot distinguish a driven RED from a real failure

`assets/red-observations.tsv` records three columns: `timestamp`, `ctl_id`, `exit`. That is all.

**Why it matters beyond bookkeeping.** `SC2` and **both** `red-prework` gate Conditions assert:

> every control ... has a recorded RED observation with **EXIT 1**

That is satisfied by **any** exit-1 record — including an accidental breakage, a missing
fixture, or a control that was simply broken at the time. Several of plan-052's controls are
green on the live tree by construction and are driven RED deliberately via a `CTL_RED=1` path
against a pinned negative fixture. **The ledger records those identically to a genuine
failure.** So the assertion is weaker than its wording implies: it proves *something exited 1*,
not *the control was demonstrated capable of a real negative*.

**How it surfaced.** plan-052's close chain halted on `SC1c`, whose clause measured
`main..HEAD` — empty post-merge. The proposed repair was to have the clause read the *recorded*
pre-merge verdict from the ledger instead. **It could not be written.** For `ctl-spec-first-order`
alone the ledger holds **18** records, **11** with exit 0 and **9** of those pre-merge, and
nothing distinguishes which run measured what. Both of its exit-**1** records are `CTL_RED`
driven REDs, indistinguishable from failures. A receipt clause would have matched nine records
and proved none of them.

**Proposed fix:** extend the schema with

- a **`subject`** column recording *what was measured* — the range, tree SHA, or fixture path;
- an explicit **`driven`** flag set by the `CTL_RED` path.

Then `SC2`'s assertion becomes what it already claims to be. **Do not weaken `SC2` to match the
record** — the criterion is right; the record is insufficient.

## Finding 2 — `grant --check` does not verify AMENDMENTS

Same class, one layer up, and found the same way.

`plan_manager.py grant --check` verifies that an authorization file covers the actions in the
**generated proposal**. An **amendment** is the mechanism for authorizing anything *beyond* that
proposal — a 24th, 25th, 26th outward-facing write. **Nothing verifies amendments.**

A grant can be amended into authorizing an extra write, or fail to be, and `--check` reports
**exit 0 either way**.

**Observed, not hypothesized.** During plan-052's close-out two amendments were written to a
*stale worktree copy* of the authorization file and never reached the authoritative one. The
executor was told both were authorized. `grant --check` returned **exit 0**. The only thing that
caught it was reading the artifact and counting the `AMENDMENT` markers — 1, where 3 were
claimed. Had the executor treated that exit 0 as confirmation, it would have made two
outward-facing writes with no authorization on record.

This is the repo's own headline defect — *an exit code that reads the wrong thing is worse than
none* — firing on **the consent gate itself**.

**Proposed fix:** have `--check` parse amendment blocks and report, per amendment, whether its
declared actions are covered; and report the file's stated total against the count it actually
verified, so a mismatch is loud.

---

*Filed as plan-052's ninth deferred defect under grant AMENDMENT 3. The others are #211-#217
and #219. Enumeration: `docs/plans/plan-052-james-dixson-fa8056/assets/deferred-defects.md`.*
