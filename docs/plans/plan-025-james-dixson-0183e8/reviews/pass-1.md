---
type: Review
okf_spec: OKF-PLAN
plan: plan-025-james-dixson-0183e8
date: '2026-07-09'
conformance_pass: PASS (mechanical checklist, run inline before this pass)
---
# Red-Team Review — pass 1

**Plan:** plan-025-james-dixson-0183e8
**Date:** 2026-07-09
**Conformance pass:** PASS (mechanical checklist, run inline before this pass)

## Verdict: REVISE

## Strengths

- The Task*/Agent distinction is correct and well-guarded; nothing in the deny list is a bare
  `Task`/`Agent`, so agent dispatch survives. R1 makes it a verified acceptance criterion.
- Boolean correction is right and evidence-backed against the operator's own `settings.json`.
- `bypassPermissions` honesty guardrail (R2) preserves the doc's "recommendations, not hard
  requirements" framing.
- Single-source-of-truth placement (lean README + full tables in the doc, cross-linked) is a
  sound anti-drift structure.
- Docs-only scoping, SPEC-first exemption, and coarse single-tracking-issue upstream disposition
  match project conventions.

## Concerns

- **C1 (high) — "context savings" claim for the deny list is unverified and likely overstated.**
  `permissions.deny` is an *invocation* gate, not a documented *schema-removal* mechanism; denying a
  tool name blocks the call but does not reliably remove its schema from turn context. The boolean
  feature-kills (`disableWorkflows`, `todoFeatureEnabled`, `disableBundledSkills`) more plausibly
  reclaim budget. Publishing "saves context" as the headline benefit of the deny list may misinform.
  Recommendation: verify whether deny-listed schemas are actually withheld; otherwise reframe the
  deny-list benefit as "avoids interference / removes the temptation surface" and reserve the
  context/tool-schema-savings claim for the boolean feature-disables. Extend the honesty guardrail
  to cover the context-savings claim.

- **C2 (medium) — `askUserQuestionTimeout: "never"` filed under the wrong axis; semantics likely
  inverted.** "never" most plausibly means the question never auto-resolves — the run blocks
  indefinitely for a human, i.e. *more* blocking on an unattended run, opposite of "fewer
  interruptions." Recommendation: verify semantics; if "never" means "never auto-answer," present it
  as an interactive-correctness tradeoff, not a run-efficiency win.

- **C3 (medium) — `SendMessage` (and peers) treated as annotation-only, no dependency verification.**
  `SendMessage` continues a spawned agent with context intact; if any `yf-*` coordinator/resume loop
  relies on it rather than re-dispatching a fresh `Agent`, denying it silently breaks resume.
  Recommendation: fold `SendMessage`, `ReportFindings`, `ScheduleWakeup`, `RemoteTrigger`,
  `PushNotification`, `DesignSync` into R1's verification scope (no `yf-*` skill invokes them
  natively), not just `Agent`.

- **C4 (low) — `bypassPermissions` documented without companion `skipDangerousModePermissionPrompt:
  true`.** Without the latter the dangerous-mode prompt can still interrupt; Issue 1.5 omits it.
  Recommendation: include it in the baseline update (or note why excluded).

## Missing

- Verification that the deny-list mechanism produces the claimed context savings (see C1).
- A one-line statement that operator-specific baseline keys (`spinnerVerbs`, `tui`,
  `enabledPlugins`, `extraKnownMarketplaces`) are consciously out of scope, so the omission does
  not read as oversight.
- A note that the `rm -rf` safety-denial globs are illustrative/operator-tunable, not a fixed
  `yf-*` requirement.

## Gate Assessment

Appropriate. A single mandatory human Start Gate is the right and only gate for a docs-only change.
No over-gating; Epic 3's lint/JSON checks are correctly validation issues, not blocking gates.

## Upstream Assessment

Reasonable and convention-conformant. No existing issue matches; one coarse tracking issue at
INTAKE per AGENTS.md. No supersedes/partials to justify.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
|:--|:--------|:---------|:-----------|:-------|
| C1 | Deny-list "context savings" overstated | high | **Refuted by Claude Code docs**: a *bare tool name* in `permissions.deny` removes the tool's schema from context entirely (real savings); only *scoped* patterns are call-time blocks. Plan now cites the mechanism and splits bare-name Tool disables (savings) from the `rm -rf` scoped globs (safety-only). Claim is accurate and now mechanism-backed. | resolved |
| C2 | `askUserQuestionTimeout: "never"` axis/semantics | medium | **Confirmed**: "never" = question waits indefinitely for a human (never auto-times-out). Moved out of the fewer-interruptions axis; documented as an interactive-correctness tradeoff (blocks-for-a-human), not a run-efficiency win. R2 extended to cover it. | resolved |
| C3 | `SendMessage` & peers dependency unverified | medium | **Verified**: grep of `skills/` for every denied tool found zero references; dispatch is exclusively via `Agent`/`subagent_type`, resume re-dispatches fresh agents. Denying the whole list is safe; evidence recorded in Investigation Findings + Issue 1.3. R1 retired. | resolved |
| C4 | Missing `skipDangerousModePermissionPrompt` companion | low | **Accepted**: Issue 1.5 adds `skipDangerousModePermissionPrompt: true` to the reference baseline as the `bypassPermissions` companion; out-of-scope operator keys noted. | resolved |

**Missing-items disposition:** context-savings verification added (C1); out-of-scope operator keys
(`spinnerVerbs`/`tui`/`enabledPlugins`/`extraKnownMarketplaces`) noted as conscious exclusions
(Issue 1.5); `rm -rf` globs documented as illustrative/operator-tunable (Approach honesty guardrails).

**Verdict after resolution:** all four concerns resolved; C1 refuted with evidence, C2–C4
addressed. Plan ready for operator approval.
