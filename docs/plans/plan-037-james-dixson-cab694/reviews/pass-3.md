---
type: Review
okf_spec: OKF-PLAN
---
## Plan Red-Team: plan-037-james-dixson-cab694 (pass 3)

Re-review after an operator rescope: the plan became **repo-only**, deferring the user-scope
redeploy to an explicit post-completion step, and absorbed the newly-filed #116. This is a
structural change to an already-approved plan, so the review is a fresh pass over the whole
document, not a delta check.

## Verdict: APPROVE

### Strengths

- **The rescope dissolves two concerns rather than mitigating them.** Pass-1's
  self-modification hazard and pass-2's "can `install.sh` target a subset?" unknown both
  existed only because the plan wrote to user scope. With no such write, neither is a risk to
  manage — the plan correctly deletes the self-modification *policy* instead of keeping it as
  reassurance, which is the honest move.
- **The remaining irreversible step is gone.** Every action now lands in a git working tree.
  The plan's worst failure mode is a bad commit, which is recoverable; previously it was
  destroying the only copy of `yf-herdr`.
- **Epic 1 is correctly sized for its purpose.** Making it a bare copy-and-commit — explicitly
  *not* the integration — means the risk-closing step has almost no failure surface and
  completes in one bead. Deferring real integration to Epic 3 is the right split.
- **The gate now checks the property that matters.** It requires the files be **git-tracked**
  (`git ls-files --error-unmatch`), not merely copied. An untracked copy inside the repo is no
  safer than the original, and the gate says so explicitly.
- **The deferral is documented rather than merely deferred.** Issue 5.3 leaves a runnable
  handoff in the plan folder, including the rules-bundling question the investigation left
  open. Deferred work that exists only in someone's memory is how staleness recurs; this does
  not do that.
- **Stale cross-references were caught and fixed.** The Investigation Findings' pointer to the
  retired Issue 1.1 was re-homed to Issue 5.3, and the "refresh is safe" finding was re-framed
  as what authorizes the *deferred* redeploy — preserving a load-bearing finding whose
  consumer moved.
- **#116 is well-placed.** It is genuinely independent, touches only `yf-plan`, and its Issue
  4.3 (make a malformed verdict fail loud) fixes the *class* of defect rather than just the
  instance — the tool reporting `review_pass: 2` alongside `verdict: null` was the real bug.

### Concerns

- **Success Criterion 1 is weaker than the criterion it replaced** — severity: low
  "Every artifact in user scope has a repo counterpart that is equal-or-newer" is the right
  claim for a repo-only plan, but "equal-or-newer" is a judgment call where the previous
  criterion was a mechanical diff. Issue 5.2 does not say how "newer" is established.
  Recommendation: at execution, treat the check as *set membership plus a content check on the
  two known-divergent artifacts* — every user-scope skill name exists in `skills/`, `yf-herdr`
  is present, and `plan_manager.py`'s configurable-roots behavior exists in the repo version.
  That is mechanical. Not blocking; the criterion is directionally correct as written.

- **Epic 4 modifies the verdict machinery this plan's own reviews depend on** — severity: low
  Noted in the risk table and correctly reasoned (the executing session uses the *installed*
  copy, so no in-flight review can be invalidated). Worth flagging that this becomes false at
  redeploy time: after the operator redeploys, `##` and `###` both parse, so nothing breaks
  retroactively — but only because Issue 4.2 relaxes the regex rather than only fixing the
  template. If the executor drops the regex relaxation as redundant, the 2 existing `###`
  reviews stay unparseable.
  Recommendation: keep both halves of 4.2. The regex relaxation is not redundant with the
  template fix; it is what makes existing history parseable.

Both concerns are low. Neither blocks approval.

### Missing

Nothing blocking. The scope boundary is stated in the Objective, restated in Approach, and
enforced by the epic structure — a reader cannot miss that user scope is untouched.

One observation rather than a gap: the plan no longer has any epic that *fails* if the operator
never runs the redeploy. That is the intended consequence of the rescope, and Issue 5.3 is the
mitigation, but it does mean the original motivating symptom (the operator running stale
skills) persists at plan completion by design. The plan is honest about this in its risk table.

### Gate Assessment

Four gates: Start, "at-risk work committed to git" (auto), "config-tier semantics decided"
(human), and Reconcile.

The preservation gate improved materially in the rescope. It changed from `human` to `auto`,
which is correct — every condition it checks is mechanically verifiable, and a human gate on a
mechanical property invites rubber-stamping. Its test now covers all three artifacts, diffs
`yf-herdr/` recursively, and adds the tracked-in-git check that is the actual point.

Blocking scope widened from a single issue to Epics 2, 3, and 4, which is right: the rescue
should precede all substantive work, not just one step.

The config-tier gate is unchanged and still correctly placed ahead of 2.2/2.3.

No gate guards work that could proceed without it, and there is no gate on Epic 4 — correct,
since it is independent and low-risk.

### Upstream Assessment

Six issues, dispositions sound.

#116 as `include` is properly justified: it was discovered by this plan's own execution, is a
genuine defect with evidence (the live `ready-check` failure), and is scoped to one skill. A
plan that finds a bug in its own tooling and fixes it in-flight is the right outcome, provided
the fix is small — it is.

#107/#100/#101 sequencing unchanged and still correct. #110's `partial` remains well-specified
with Issue 3.7 owning the split. #102 and #109 excluded with reasons.

One note: Success Criterion 4 now lists four issues to close (#107, #100, #101, #116) and one
to update (#110). That matches the table. Criterion 6 correctly names #115 as the coarse
tracker.

### Operator Resolutions

| # | Concern | Severity | Status | Resolution |
|:--|:--|:--|:--|:--|
| 1 | Criterion 1's "equal-or-newer" is a judgment call | low | acknowledged | Executor to implement Issue 5.2 as set-membership plus a content check on the two known-divergent artifacts. Not blocking. |
| 2 | Epic 4's regex relaxation must not be dropped as redundant | low | acknowledged | Both halves of Issue 4.2 are required: the template fix prevents recurrence, the regex relaxation makes the 2 existing `###` reviews parseable. Recorded for the executor. |
