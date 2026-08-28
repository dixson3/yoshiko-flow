---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: Deploy skills once to shared .agents/skills root

Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #257 — Deploy skills ONCE to .agents/skills for every harness that reads it; keep only config/hooks/extensions harness-specific

> ## Proposal

**For any harness that reads `.agents/skills` with no configuration, deploy SKILLS there and
nowhere else.** Harness-specific directories keep only what is genuinely harness-specific —
co...

**Disposition:** include
**Notes:** The plan's primary deliverable

## #256 — check-harness-smoke: the state model is missing 'installed but consent-gated' — codex reaches INCONCLUSIVE for the wrong reason
Labels: bug
> ## The gap

`check-harness-smoke.sh` (plan-054 Issue 2.5, backing SC18) models a harness as **drivable or
absent**:

```
EXIT  0 both harnesses pass  ·  1 an assertion failed  ·  2 could not run (harn...

**Disposition:** partial
**Notes:** **IN:** the tier-registration defect (4.6) — the row fires on the cheap tier and never on the land gate. **OUT:** the state-vocabulary rework itself, deferred with 4.1-4.5. Calling this `include` would claim a state model that no longer ships.

## #255 — Cut the v0.5.0 release: push the tag (deferred from plan-054, everything else staged and green)

> **The tag push is the only remaining work.** plan-054 completed everything else and deliberately
descoped Issue 6.8 so the operator could verify the harnesses manually under a real `HOME`
before an ir...

**Disposition:** deferred
**Notes:** Sequencing only. This plan lands **before** the tag because it changes what "multi-harness support" means in the release notes — cheaper to decide before the tag than to caveat after

## #243 — Successor to #154: harness tune OVERWRITES a pre-existing rules aggregate with no backup

> ## Summary

**Successor to the closed #154**, covering the half that survived it.

#154 is closed, and correctly: its `--revert` half genuinely works — the `REQ-YF-TUNE-029`
sha256 guard fires, and as...

**Disposition:** exclude
**Notes:** Rules surface, not skills. Adjacent hazard class, no shared code path. Re-characterized rather than dismissed: plan-055 builds a marker-gated, quarantine-backed remover on the SKILLS surface precisely so it does not create a second instance of #243's no-backup hazard (D-2, D-2b, 5.2a).
**Resolved By:** —

## #240 — codex budget check models ONE AGENTS.md; codex concatenates several against the same cap

> ## Summary

The codex block-size budget check (`CodexBudgetCheck`, #120) models codex's
`project_doc_max_bytes` cap against **one file** — the user-scope `~/.codex/AGENTS.md`. Codex
concatenates **mul...

**Disposition:** exclude
**Notes:** Rules surface

## #239 — pi's project-trust gate is unexercised by any test or smoke

> ## Summary

**pi's project-trust gate is unexercised by anything in this repo.** pi prompts before
operating in an untrusted project directory, and no test, no smoke and no manual procedure
covers wha...

**Disposition:** partial
**Notes:** **IN:** a `yf doctor` axis and an install-time warning. **OUT:** the test/smoke coverage the issue actually asks for — neither 4.8 nor 4.9 exercises pi loading under an untrusted project. This ships VISIBILITY, not COVERAGE. #257 must prove pi loads from `.agents/skills`; the trust gate is the precondition under which pi loads anything

## #238 — yf ignores XDG_CONFIG_HOME / CODEX_HOME / OPENCODE_CONFIG_DIR when resolving harness directories

> ## Summary

`yf` resolves every harness directory from `$HOME` plus a hardcoded relative subpath, and
**ignores the environment variables the harnesses themselves honour**. Measured on the v0.5.0
tree...

**Disposition:** partial
**Notes:** **IN:** skills-root env-immunity for codex/pi/opencode, `CLAUDE_CONFIG_DIR` followed for claude-code skills (3.2), and an install-time warning. **OUT:** surface-dir resolution — yf still writes config/hooks/rules to the `$HOME`-derived path and merely *narrates* the mismatch (D-13). Calling this `include` would claim more than ships. Same descriptor table and same resolution function as #257; landing separately edits `harness_desc.rs` twice, and #257 also narrows it — once skills leave the harness-private roots, `OPENCODE_CONFIG_DIR` governs config only.

## #121 — Pi config tuning re-verification (plan-033 deferral REQ-YF-TUNE-017)
Labels: type::task, priority::medium, deferred, plan-033-followon
> plan-033 shipped Pi skills+rules but DEFERRED Pi config tuning: research-002 Q6 marks Pi's config surface (settings.json/permissions.json/mcp.json) [uncertain] (questionable-tier only), and rust-embed...

**Disposition:** exclude
**Notes:** Config surface, which this plan explicitly leaves harness-specific. No shared code path
