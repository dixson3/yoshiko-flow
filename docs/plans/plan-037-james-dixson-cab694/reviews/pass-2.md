---
type: Review
okf_spec: OKF-PLAN
---
## Plan Red-Team: plan-037-james-dixson-cab694 (pass 2)

Re-review after the pass-1 REVISE. Scope: verify the nine resolutions actually close their
concerns, and re-examine the plan as a whole for anything the restructuring introduced.

## Verdict: APPROVE

### Strengths

- **Both high concerns are structurally resolved, not papered over.** Epic 4 is a real epic
  with three issues and a dependency edge on Epics 2 and 3, and Criterion 1 now names Issue
  4.2 as its measurement — so the criterion is falsifiable rather than aspirational. The
  self-modification policy is stated as a policy with a named choice and a recorded
  consequence, which is the right shape for a decision that would otherwise be made ad hoc
  mid-execution.
- **The plan is honest about what it accepts.** The risk table now carries "executes on the
  stale `yf-plan` throughout" as an accepted trade rather than hiding it. A plan that names
  its own compromises is easier to execute correctly than one that reads as uniformly clean.
- **Verification is mechanical end-to-end.** Both capability gates now have runnable `Test:`
  commands, and the two verification issues (1.4, 4.2) specify exact exclusions. There is no
  step whose pass condition is a judgment call.
- **The evidence base remains the plan's strongest feature.** The refresh authorization rests
  on exact blob matching against history, and the newly-added Issue 4.3 closes the loop by
  requiring the backup be *proven* redundant before removal rather than assumed so.
- **Scope held under revision.** The revision added an epic and two issues without pulling in
  #102 or the wider `.yf/` migration; Issue 1.1's "drift" branch explicitly routes new work to
  a follow-up issue instead of absorbing it.

### Concerns

- **Epic 4 assumes the installer can target a subset, which is unverified** — severity: low
  Issue 1.3 excludes `yf-plan` from the refresh and Issue 4.1 installs all 19. Whether
  `install.sh` supports per-skill selection was not established by any experiment; if it only
  does whole-tree installs, Issue 1.3 needs a different mechanism (install then restore the
  preserved `plan_manager.py`, or accept the whole-tree refresh and adjust the policy).
  Recommendation: make this the first thing Issue 1.3 determines. It does not block approval —
  the fallback (install whole tree, restore the one file from the Issue 1.2 backup) is
  straightforward and the backup already exists for exactly this reason.

- **Issue 4.3's retirement step is irreversible and lightly gated** — severity: low
  It removes the only copy of the preserved work after 4.2 passes. The ordering is correct and
  4.2 is a strong precondition, but the plan does not say to keep the backup until the *push*
  is authorized and complete, and Phase 6 defers push to explicit operator authorization.
  Recommendation: retire the backup only after the upstream push completes, not merely after
  the merge validates. Cheap insurance; can be applied at execution time.

Both concerns are low and neither blocks approval — per the red-team rules, high blocks,
medium prompts discussion, low is nice-to-have. Recorded for the executor rather than sent
back for another revision cycle.

### Missing

Nothing blocking. The pass-1 gaps (post-merge re-install, self-modification policy, Tier-2
coverage) are all now present and wired into the dependency graph.

### Gate Assessment

Four gates: Start, two capability gates, and Reconcile. The duplicate Reconcile Gate that the
restructuring briefly introduced has been removed — verified single occurrence.

Both capability gates now have executable `Test:` commands. The preservation gate's test
checks all three preserved artifacts and diffs them against their sources, so it fails loudly
if the copy is partial — appropriate for the plan's only unrecoverable step. The config-tier
gate's test (`test -s .../decisions/config-tier.md`) is a presence check, which is the right
level for a human decision gate: it cannot validate the *content* of a judgment call, only
that the judgment was made and recorded.

Gate placement is correct: the preservation gate blocks 1.3 (the overwrite), and the
config-tier gate blocks 2.2/2.3 (the code whose shape depends on the decision). No gate
guards work that could not proceed without it.

### Upstream Assessment

Unchanged from pass 1 and still sound. The one pass-1 defect — an unspecific `partial` on
#110 with a placeholder owner — is fixed: the Notes cell now states the in/out split
concretely (skill surface in; `herdr agent *` fan-out primitive out), Issue 3.7 owns writing
it, and #110 is explicitly left open. That is what a well-formed partial looks like.

#107/#100/#101 as `include` with #100 sequenced first remains correctly justified by the
dependency (one reader, two consumers). #102 and #109 excluded with reasons. No supersedes
claimed.

### Operator Resolutions

| # | Concern | Severity | Status | Resolution |
|:--|:--|:--|:--|:--|
| 1 | Installer subset-targeting unverified | low | acknowledged | Carried into execution as the first determination in Issue 1.3. Fallback (whole-tree install + restore from the Issue 1.2 backup) is known and the backup exists for this purpose. Not blocking. |
| 2 | Backup retired after merge rather than after push | low | acknowledged | Executor to hold `~/yf-preserve-plan-037/` until the Phase 6 push is authorized and complete, then run Issue 4.3. Not blocking. |
