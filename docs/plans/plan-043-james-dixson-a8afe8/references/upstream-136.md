---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #136: yf-plan: reconcile silently skipped three mapped 'include' upstream issues while the plan reported complete

- **Number:** 136
- **Title:** yf-plan: reconcile silently skipped three mapped 'include' upstream issues while the plan reported complete
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## What happened

plan-039 ([tracker #134](https://github.com/dixson3/yoshiko-flow/issues/134)) completed cleanly by every signal `yf-plan` reports:

```
status: complete
resume-scan: {found: true, total: 33, counts: {closed: 33}, stuck: [], open_work_remaining: 0}
cascade-close: clean (exit 0)
```

Merged to `main`, pushed, plan folder in order.

**Three of its four `include` upstream issues had not been touched.** #108, #112 and #114 were all `include`, all genuinely resolved by the executed work — and all still `OPEN`, with **zero comments mentioning plan-039**:

```
#108: 1 comments, 0 mention plan-039
#112: 2 comments, 0 mention plan-039
#114: 1 comments, 0 mention plan-039
```

Their most recent comments were corroboration notes from an unrelated earlier session, which made the issues *look* recently active on a glance.

`#109` (`supersede`) was closed correctly and `#113` (`partial`) got its re-scope comment and correctly stayed open — so reconciliation ran and handled two dispositions properly, then silently did nothing for the third.

## Why this is not #117 or #131

Those cover the **coarse plan-level tracker** being invisible to `closable` because it carries no bead mapping. Real, and it applies to #134.

This is different: **#108/#112/#114 were mapped.** They appear in the plan's Upstream Issues table with dispositions and a populated `Resolved By` column, and their resolving issues carry `resolves-upstream` annotations. The information reconciliation needed was present and structured. It just was not acted on.

## Why it matters

Per REQ-AGENT-031, `include` → close with a comment. Skipping it fails in the direction that hides itself:

- The plan reports `complete` with `open_work_remaining: 0`, so nothing prompts a human to look.
- The upstream issues stay open, so a later session may re-plan work that already shipped.
- The execution evidence — which for plan-039 included four independently-validated replay fixtures proving the review additions actually fire — was recorded **nowhere upstream**. That is the most valuable artifact the plan produced, and it existed only inside the plan folder until swept by hand.

A completion signal that is green while a documented step silently did not run is worse than a loud failure. The close-step cascade already **fail-louds** on an unclosed child (REQ-COMPLETE-001); the reconcile step has no equivalent.

## Suggested directions

Not prescriptive.

- **Make reconcile fail-loud like cascade-close.** After the reconciler runs, verify each `include`/`partial` row reached its expected end state — `include` → upstream closed + commented; `partial` → commented, still open — and exit non-zero listing any row that did not. This mirrors the existing close-step contract rather than inventing a mechanism.
- **A `reconcile --verify` / dry-run verdict** reporting the intended action per row before it runs, so a no-op is visible up front.
- At minimum, **report** the per-row outcome in the completion summary instead of only the bead counts, so a human can see that three rows were skipped.

Worth determining whether the reconciler errored silently, filtered these rows out, or was never dispatched for them — the fix differs. The plan folder's reconcile artifacts and the execution transcript should settle it.

## Provenance

Found by mechanical verification during delegated execution — checking `gh issue view` state against the plan's disposition table rather than trusting the subordinate's completion report. It would not have been visible from the plan's own status output.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

