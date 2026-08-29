---
type: Reference
okf_spec: OKF-PLAN
description: The exact gh commands and bodies the ungranted upstream-writes capability gate authorizes, drafted for operator review before any outward-facing write. Nothing here has been executed.
---
# Upstream-writes runbook — DRAFTED, NOT EXECUTED

**Nothing in this directory has been run.** The capability gate *"upstream writes authorized"* is
a human gate with no `Test:` (deliberately — a green command can never establish authorization),
and it is **not granted**. It blocks Issues 0.2, 2.7, 6.3 and 6.4, and through Issue 0.3's
dependency edge it blocks the reconcile-time sweep as well.

`context.md` declares issue create/comment a **stop class**, authorized individually and never
batched, so these are presented together for review but must be authorized as four decisions.

**#269 is NOT in this set.** Its correction comment was already posted at `2026-08-28T23:24Z`,
before execution began. An earlier plan draft still scheduled it; it is excluded here.

## Bodies compose with a QUOTED heredoc or `--body-file`, never `--body '...'`

**The body files carry a `.body.txt` extension, not `.md`, and that is load-bearing.** A `.md`
file inside a plan bundle is a non-reserved OKF member, so `REQ-PORT-050` requires it to carry
`type:` + `okf_spec:` frontmatter — and `--body-file` would then post that frontmatter **into the
published issue body**. Measured here: three `.md` drafts turned the portability audit red, and
the only two ways out were to publish the frontmatter or to fail the audit. The extension change
is the third.


Per `AGENTS.md`: a single-quoted `--body` passes backslashes through literally and an unquoted one
lets the shell expand `` ` `` and `$`. Every command below feeds a **file**. Verify each posted
body by reading it back (`gh issue view N`), not by trusting exit 0.

## 1 — Issue 2.7: file the missing `yf-drift-check` edge

```bash
gh issue create \
  --title "yf-drift-check edge over the escape/stop taxonomy — #145's announced mitigation does not exist" \
  --body-file docs/plans/plan-059-james-dixson-55137e/assets/upstream-drafts/issue-2.7-drift-check-edge.body.txt
```

Then record the number returned:

```bash
sed -i '' 's/^DRIFT_EDGE_ISSUE=$/DRIFT_EDGE_ISSUE=<N>/' \
  docs/plans/plan-059-james-dixson-55137e/assets/filed-issues.env
```

**Discharges SC2d**, which greps the posted body for both `drift-check` and `taxonomy`. The draft
carries both.

## 2 — Issue 6.3: file the detector re-measurement

```bash
gh issue create \
  --title "Re-measure the severity-decay detector: blind labelling over nine held-out bundles, gated on the PR #267 parser repair" \
  --body-file docs/plans/plan-059-james-dixson-55137e/assets/upstream-drafts/issue-6.3-detector-remeasurement.body.txt
```

```bash
sed -i '' 's/^REMEASURE_ISSUE=$/REMEASURE_ISSUE=<N>/' \
  docs/plans/plan-059-james-dixson-55137e/assets/filed-issues.env
```

**Discharges SC9c**, which greps the posted body for `blind` and `held-out`. The draft carries both.

## 3 — Issue 6.4: correct #273 in place

This is an **edit of an existing issue**, not a new one. The replacement body is generated from
the live body with three surgical substitutions; it is checked in so the diff is reviewable
before it is posted.

```bash
gh issue edit 273 \
  --body-file docs/plans/plan-059-james-dixson-55137e/assets/upstream-drafts/issue-273-corrected-body.body.txt
```

**What changes, and why.** The original compared a **per-plan** rate (`5 / 6`) against a
**per-event** rate (`2 / 12`) over two *different* populations and then divided them. Two
incommensurable denominators do not form a ratio, so the reported "factor of five" was an artifact
of the unit change rather than a measured effect. The correction restates both rows at **one unit
(per plan) over ONE stated population** — the five post-plan-045 plans that exceeded the bound —
giving `4 / 5` vs `2 / 5`, and **withdraws the multiplier outright** rather than recomputing it.
The `15 / 15` script row is moved out of the comparison table into *Limits*, because a script that
cannot forget measures the absence of a failure mode rather than compliance.

**Discharges SC9b**, which asserts the posted body matches `4 ?/ ?5` and `2 ?/ ?5` and does **not**
match `factor of five`. Verified against the draft: all three hold.

## 4 — Issue 0.2: link the epic on the adopted tracker #269

**#269 is ADOPTED as this plan's coarse tracker, not created** — `AGENTS.md` mandates one tracker
per plan-scale effort and #269 already existed as this effort's proposal issue.
`assets/filed-issues.env` records `TRACKER_ISSUE=269`, and **SC0b is already green**, so no
upstream write is strictly required to discharge the criterion.

What is still missing is the **epic linkage**, which could not exist before execution: the epic
`yf-mol-vltm` was only poured at execute start.

Local half (no upstream write — safe to run before the gate):

```bash
# add a `tracker` disposition row for #269 to plan.md's `## Upstream Issues` table.
# That section is FINGERPRINT-EXCLUDED (REQ-PORT-040), so editing it cannot make the plan
# stale-approved.
uv run skills/yf-plan/scripts/plan_manager.py stamp-tracker \
  docs/plans/plan-059-james-dixson-55137e --json
```

Upstream half (gated):

```bash
gh issue comment 269 --body-file - <<'BODY'
plan-059 execution tracking: epic `yf-mol-vltm` (7 epics, 36 issues, 4 gates).
Bundle: `docs/plans/plan-059-james-dixson-55137e/`.
BODY
```

## What stays blocked until all four land

`Issue 0.3` — the reconcile-time re-run of the instrument sweep — depends on `2.7` and `6.4`, so it
cannot run until this gate is granted. Its rewritten `RC` block is what `SC0` reads, and `SC0`
requires every recorded non-zero row to be zero. The four rows currently non-zero
(`SC2d`, `SC9b`, `SC9c`, and `recheck-criteria`/`SC0` aggregating them) all trace to this gate
and to nothing else.

---

## 5 — RECONCILE comments (§6.3): NOT COVERED BY THE FIRST GRANT

**Added after the first grant was executed.** The operator's grant scoped four issue writes —
`0.2`, `2.7`, `6.3`, `6.4`. `verify-reconcile` then required **three more**, and they are a
different set: `#264`, `#273` and `#145`, none of which is in that grant's `Blocks` set. So this
section is a **second ask**, presented the same way and not executed.

`verify-reconcile` is a **HALTING** step in §6.4. Its verdict:

```
3 of 6 upstream row(s) did not reach the end state their disposition requires
  #264 (partial) · #273 (partial) · #145 (partial)
```

Each is `partial`, which means the issue **stays OPEN** — the remaining half is real work — but
what *this* plan did must be recorded upstream, or the deferred half becomes invisible. The other
three rows already pass: `#269 partial` (the tracker comment), `#270 deferred` (which requires no
mention by design), and `#269 tracker` (report-only — the tracker is closed by the land-the-plane
sweep, not by reconciliation).

**Note on `#273`:** Issue 6.4 **edited its body**; `verify-reconcile` checks **comments**. A body
edit and a comment are different artifacts and it is right not to accept one for the other.

```bash
gh issue comment 264 --body-file - < docs/plans/plan-059-james-dixson-55137e/assets/upstream-drafts/reconcile-264.body.txt
gh issue comment 273 --body-file - < docs/plans/plan-059-james-dixson-55137e/assets/upstream-drafts/reconcile-273.body.txt
gh issue comment 145 --body-file - < docs/plans/plan-059-james-dixson-55137e/assets/upstream-drafts/reconcile-145.body.txt
```

Then verify by read-back and re-run the gate:

```bash
for n in 264 273 145; do gh issue view $n --comments --json comments | jq -r '.comments[-1].body' | head -3; done
uv run skills/yf-plan/scripts/plan_manager.py verify-reconcile docs/plans/plan-059-james-dixson-55137e --json
```

**Until these three land, `set complete` is blocked** — and correctly so. `verify-reconcile` is
halting by design, and everything else in §6.4 is already green.
