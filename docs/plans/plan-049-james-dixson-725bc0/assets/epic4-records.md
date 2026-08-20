---
type: Reference
okf_spec: OKF-PLAN
id: epic4-records
description: The four recorded decisions of Epic 4 — M9 out-of-scope, the Incubator no-op, the alphabet rule re-scope, and EXP-003's two remaining recommendations (Issues 4.5-4.8)
---

# Epic 4 records: four decisions, each with its measurement

Four Epic-4 issues produce a **record** rather than code. Each names something that would
otherwise be implied by silence — and in every case the plan is explicit that *"declining is an
acceptable outcome; silence is not."* Every figure below was **re-measured here** (D-7), never
carried forward.

## Issue 4.6 — M9 of #149 is OUT OF SCOPE

[#149](https://github.com/dixson3/yoshiko-flow/issues/149) is titled *"M5/M9: process rules that
nothing executes, and remediation edges that exist only in prose"*. plan-049 carries **M5** — the
enforcement binding gives the linter an executing home (Issues 4.1–4.4) — and does **not** carry
M9.

**The measurement, re-taken at execution:**

| Figure | Value |
| :-- | --: |
| `discovered-from` bead edges in the live DB (deduplicated) | **26** |
| ...of which connect **two plan epics** | **0** |

*(plan-049 recorded 53 at drafting; the live deduplicated count is 26. The number that matters
is the second row, and it is **zero** either way.)*

So the "remediation edges" M9 describes **do not exist in the bead graph at all** — not sparsely,
not partially. Every `discovered-from` edge in the corpus connects a bead to a bead within a
plan; none connects one plan's epic to another's. Building the M9 half would mean *creating* that
edge class first, which is a different piece of work from binding a linter, and nothing in
plan-049 touches it.

**Recorded because a truncated title lies by omission.** #149's title names both halves, so
closing it against a plan that carried one half would read as if both had shipped. The
disposition in `## Upstream Issues` is `partial` for exactly this reason, and this record is what
makes "partial" mean something specific.

## Issue 4.5 — the `Incubator/*` §3 rows are a PERMANENT no-op here

`CHANGE-VALIDATION.md` §3 carries two rows that select **nothing in this repository** and always
will:

| Row | Why it is inert here |
| :-- | :-- |
| `Incubator/*/plans/**` | this repo has no `Incubator/` directory |
| `Incubator/*/research/**` | likewise |

**They are correct and must not be deleted.** The manifest schema is shared across vaults, and in
an incubator-using vault these rows are load-bearing. Deleting them here would break those vaults
to remove two lines that cost nothing. The right treatment is documentation, which is what D-5
concluded after EXP-004 measured it.

### D-5's research vacuity is CLOSED — do not re-schedule it

EXP-004 measured the original concern and found it already fixed: plan-048's Issue 2.7
instantiated the research document types, so `doc_lint --path` now returns `files_checked: 1`
for a real research file and `0` for a nonexistent one. The two are distinguishable, which is
what the concern was about.

The residual "these checks cannot fail" is **REQ-DATA-045 policy, not a defect**: off the
plan-bundle axis `bundle_status` is null, so `STATUS_SEVERITY` offers no softening and every
research check ships at `W` deliberately. Promoting one to `E` is permitted **only** with a
measured corpus pass recorded alongside it. That is a future option, not an outstanding bug.

## Issue 4.7 — `disposition-alphabet-offered`: RE-SCOPED, not retired

**Re-measured (D-7):** the rule fired on **30 of the 31** selected files. The single non-firing
file was `plan-049`'s own `upstream-triage.md` — the triage of the plan doing the measuring.

A rule that fires on essentially everything is a **constant**, and a constant carries zero
information regardless of the severity it wears. Shipping it at `R` did not fix that; it made
the noise quieter.

**The diagnosis is what determined the fix.** The 30 files are not wrong. The rule asserts
something the **current** `triage` producer emits, against 30 documents an **older** producer
wrote. It is a producer-version check, and re-judging finished documents by one teaches nobody
anything.

**Re-scoped** via a new generic schema key, `statuses` (REQ-DATA-058), which declares the bundle
statuses a check applies to — orthogonal to `STATUS_SEVERITY`, which changes a finding's
*severity* rather than deciding whether the check *runs*:

```toml
statuses = ["scoping", "investigating", "drafting", "review", "ready-for-approval"]
```

| | Before | After |
| :-- | --: | --: |
| violation rate over the 31 selected files | **30 / 31** | **0 / 31** |
| still fires on an in-flight bundle whose triage omits the alphabet | — | **yes** (verified) |

Strictly decreasing, as SC37 requires, **without** losing the signal: an in-flight bundle whose
triage lacks the alphabet still produces the finding, at the point an author can act on it.
Retiring the rule outright would have discarded a real check for new triage documents.

## Issue 4.8 — EXP-003's two remaining recommendations

Both are dispositioned. **Neither is left to silence.**

### (a) A one-shot `R1b` sweep before enforcement — **DECLINED, with reason**

The recommendation assumed R1b would be **promoted to `E` at `review`**, which would have made
every plan carrying an issue named by no criterion hard-fail at intake. **That premise no longer
holds.** Issue 0.2 (REQ-DATA-053) implements `promote = false` for the `plan-relations` kind, so
every `R*` rule now keeps its declared `W` at **every** status — never promoted at `review`,
never demoted at `complete`.

A sweep exists to clear a backlog *ahead of a gate closing*. With the gate declared permanently
open, the sweep would be a corpus-wide edit with no enforcement event to precede — and this plan
spent an entire epic establishing that unnecessary corpus writes are the expensive option.

**The condition under which it should be reconsidered, stated so the decline is falsifiable:**
if a future plan proposes removing `promote = false` or promoting R1b to `E`, the sweep becomes
a prerequisite of that plan and must be scheduled with it.

### (b) The two `finding.toml` repairs — **SCHEDULED, out of scope here**

1. the stale `## Output` cross-reference;
2. the `sections()` fenced-template trap.

Both are real and neither is in this plan's scope: plan-049 touches the `plan` and
`plan-relations` schemas and the enforcement binding, not the `finding` type. They carry
forward to `references/handoff-050.md` with this record as their provenance, rather than being
mentioned in an execution log nobody reads.
