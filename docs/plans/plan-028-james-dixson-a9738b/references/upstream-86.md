---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #86: yf-plan: approved-but-unexecuted plans masquerade as completed (intake commit subject + tracking-issue title); add parked-plan visibility

- **Number:** 86
- **Title:** yf-plan: approved-but-unexecuted plans masquerade as completed (intake commit subject + tracking-issue title); add parked-plan visibility
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement

## Body

## Problem

An **approved-but-unexecuted** yf-plan plan is easily mistaken for a **completed** one. This was hit live: plan-026 (markdown tooling, #81/#48/#46/#49/#50) was approved and intake'd on 2026-07-11 but never executed — yet a `git log` scan and its tracking issue both read as if the work shipped, leading to a wrong "these issues are stale, close them" triage. Nothing had been built.

### Evidence that fooled the reader

1. **The `commit-plan` (Phase 4.3) commit subject restates the objective in the imperative.** plan-026's intake commit `d0db769`:

   > `plan-026-…: approved — Markdown tooling improvements: fix ML003 title parsing (#81), add un-escaped-markup lint rule (#48), bless alt/title image convention (#46), document CriticMarkup PDF hazard (#49), and add a new markdown-html skill (#50)`

   Scanning history, that reads as a completed-work changelog ("fix #81, add #48, add skill #50"), not "a plan document was approved." The commit in fact touched **only** `docs/plans/plan-026/` — zero code.

2. **The intake tracking issue (Phase 4.5) is titled `Complete execution of plan-026 …`.** The imperative "Complete" glances as past-tense "Completed."

3. **No visibility for parked plans.** An approved-but-unexecuted plan is invisible unless you run `/yf-plan list`. plan-026 was the *only* plan not `complete` (all of 001–025, 027 are done) and nothing surfaced it.

### Root cause (not a reconcile bug)

Under the intake-at-execute model, INTAKE stops at approved + committed + landed + tracking-issue-filed and defers the pour/execution/reconciliation to `/yf-plan execute <id>` in a new session. plan-026's `/yf-plan execute` was simply never invoked. `resume-scan` confirms: `found: false`, `epic_id: null`, no beads, fingerprint still fresh. Reconciliation never ran because execution never ran — working as designed, but the artifacts above hide that state.

## Proposed fixes

1. **State-signalling intake commit subject.** The Phase 4.3 `commit-plan` subject should signal plan *state*, not restate the objective as if done. e.g.
   `plan-026: INTAKE approved (awaiting /yf-plan execute) — <objective>`
   (objective can stay in the body, not the imperative subject).

2. **Parked-plan nudge.** `/yf-plan status` (and/or a land-the-plane check) should flag plans stuck at `approved` with a fresh fingerprint: "N plan(s) approved but not executed — run /yf-plan execute <id>."

3. (Optional) Consider whether the tracking-issue title should read `plan-026 execution tracking` rather than `Complete execution of plan-026` to avoid the past-tense glance.

## Not affected

The reconciliation machinery itself is correct; plan-027 executed and reconciled cleanly through the same code path in the same session this was found.
