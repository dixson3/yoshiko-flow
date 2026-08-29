---
okf_version: 0.1
---

# plan-041-james-dixson-a9d837

> Close #137 — fix the embed **addition** blind spot and the version-stamp staleness in
> `yf/build.rs`, close the shipping-embed test-coverage hole, and retire the
> `touch yf/src/embed.rs` workaround. **Changes no command behavior.**
>
> Originally also covered an install-time skills/rules/config sync; that was split out to
> `plan-042-james-dixson-98631b` at review (see `reviews/pass-1.md`, concern C10).

This plan folder is **portable** — a cold reader understands its purpose, environment, reviewer history, and upstream context from the files below alone, without the drafting conversation.

- [plan.md](plan.md) - The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes.
- [context.md](context.md) - Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes.
- [log.md](log.md) - Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log).
- [upstream-triage.md](upstream-triage.md) - Per-issue disposition and rationale, including why the issue's own stated root cause was partially refuted and which of its three proposed fix directions was adopted.
- [references/](references/) - Inlined upstream issue bodies (`upstream-<N>.md`), one per non-excluded Upstream Issues row. Snapshots, not live — the issues this plan addresses.
- [reviews/](reviews/) - Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers flagged and how it was resolved.
- [findings/](findings/) - Investigation experiment results (if any).
- [findings/exp-001-self-install-paths.md](findings/exp-001-self-install-paths.md) - E1 — What `yf self install` actually does today
- [findings/exp-002-force-reembed.md](findings/exp-002-force-reembed.md) - E2 — Cheapest reliable way to force a `skills/` re-embed
- [findings/exp-003-debug-release-parity.md](findings/exp-003-debug-release-parity.md) - E3 — Debug/release embed parity, and the actual mechanism of #137
- [findings/exp-004-harness-tune-safety.md](findings/exp-004-harness-tune-safety.md) - E4 — Is `yf harness tune` safe to auto-invoke?
- [findings/exp-005-profiles-addition-probe.md](findings/exp-005-profiles-addition-probe.md) - E5 — Does `yf/profiles/` share the `skills/` addition blind spot?
- [findings/exp-006-spike-15-watch-form.md](findings/exp-006-spike-15-watch-form.md) - E6 — Issue 1.5 spike: per-file vs directory `rerun-if-changed`
- [findings/exp-007-spike-12a-test-mechanism.md](findings/exp-007-spike-12a-test-mechanism.md) - E7 — Issue 1.2a spike: the addition-propagation test mechanism
- [references/upstream-137-correction.md](references/upstream-137-correction.md)
- [references/upstream-137.md](references/upstream-137.md) - Upstream #137: yf self install --from-build can promote a binary with a STALE embedded skills tree (release profile, incremental rebuild)
- [reviews/pass-1.md](reviews/pass-1.md) - Review pass 1 — adversarial (red-team)
- [reviews/pass-2.md](reviews/pass-2.md) - Review pass 2 — adversarial (red-team), post-split
- [reviews/pass-3.md](reviews/pass-3.md) - Review pass 3 — adversarial (red-team)
