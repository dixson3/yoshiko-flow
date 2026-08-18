---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream Issue Triage: deploy-path and beads-integrity defect clusters

Instructions: For each issue, set disposition to: include, exclude, partial, supersede.
Add notes as needed. When done, say "triage ready".

_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._

## #159 — yf doctor --repair --remove-remote reports ok but does not remove the Dolt remote

> ## Symptom

`yf doctor --repair --local-only --remove-remote` reports success for the remote-clearing step while leaving the Dolt remote configured.

Measured 2026-08-17 on `dixson3/yoshiko-flow` (`do...

**Disposition:** include
**Notes:** Filed root cause is WRONG (exp-002): the real cause is derive_dolt_repo_root refusing on the server-mode two-.dolt layout, so --remove-remote has never worked in the canonical profile. Fix the shared helper + fail-loud + doctor postcondition (D-6). Epic 1.

## #160 — A Dolt remote was configured and bead data pushed to GitHub despite dolt.local-only = true

> ## What was found

On 2026-08-17, `dixson3/yoshiko-flow` — a repo with `bd config get dolt.local-only` = **`true`** — was discovered to be configured as a live Dolt remote, with bead data present on G...

**Disposition:** include
**Notes:** GitHub-side dolt refs are already deleted — the exposure is remediated; only the code-path defect remains. Authority = detect + propose, repair on request (D-2). Epic 1 also probes the repair() init-ordering hypothesis (exp-002 b) rather than closing on detection alone.

## #154 — yf harness tune regenerates YOSHIKO_FLOW.md wholesale — no managed block, no guard, and --revert deletes rather than restores

> ## Summary

`yf harness tune` regenerates `~/.claude/rules/YOSHIKO_FLOW.md` **wholesale**, with no managed-block delimiters and no checksum guard. Operator edits inside it are silently lost, and `--re...

**Disposition:** include
**Notes:** Fix = sha256 in RuleRecord + conservative-keep on revert mismatch (D-9), NOT block conversion — exp-001 shows block conversion alone does not deliver 'restore', which needs a real backup. Requires #156 to land first. Epic 2.

## #156 — skills upgrade writes YOSHIKO_FLOW.md to the wrong surface for non-claude-code harnesses, unmanaged by the tune manifest and backed by no REQ

> ## Summary

`yf harness skills upgrade` writes the `YOSHIKO_FLOW.md` rules aggregate to the **skills-sibling** `rules/` directory. For every harness except claude-code that is **not the surface the ha...

**Disposition:** include
**Notes:** Must land BEFORE #154 (exp-001 blocker 2): two writers, one path. Only upgrade's rules write is removed; `remove` keeps its own (D-10). The `agents` rules target is PROBED first (D-11), then either given a RULE_TARGETS row carrying that evidence or declared skills-only -- an unevidenced row would commit tune to writing a file exp-001 found nothing loads. Epic 2.

## #155 — A file dropped from a skill lingers in the deployed tree, so that skill reports 'modified' forever — give install an opt-in --prune

> ## Summary

A file **deleted or renamed inside a still-shipping skill** is never removed from the deployed tree, so that skill reports `modified` in `yf doctor` / `yf skills status` **permanently**.

...

**Disposition:** include
**Notes:** Scope is --prune PLUS a tree-hash ignore-list (D-5). exp-004 measured that --prune alone does not keep doctor green — the 7 leftovers are runtime residue that regenerates on the next `uv run`. Epic 2.

## #158 — yf self update could never refresh codex, opencode or pi (--surface blindness)
Labels: bug
> ## Summary

`yf self update`'s post-update refresh was structurally unable to reach **three of the five supported harnesses**. Fixed by plan-042 (#157), but recorded separately because the defect is w...

**Disposition:** supersede
**Notes:** Verified FULLY FIXED by plan-042 (exp-005 Part B): refresh_user_skills/present_user_surfaces no longer exist, SYNC_PRESENCE spans all 5 descriptors, --surface is not emitted on the vendor path, and both hazards are test-pinned. Verify-and-close only, gated on a green `cargo test -p yf sync`. Epic 4.

## #144 — yf-beads-upstream: a bead stays open when its upstream issue closes — the reverse of #117, with no reconciler

> ## Summary

When an upstream issue is closed, **nothing closes the local bead that mirrors it.** The bead stays `open`, keeps its `external_ref`, and keeps appearing in `bd ready` as available work th...

**Disposition:** include
**Notes:** Live instance: bead yf-1656 open while #132 closed. Served by the same bulk gh query as #142 (exp-003). Local close is --apply-able (reversible tombstone); the upstream half stays propose-only. Epic 3.

## #142 — closable proposes closing issues that are already closed (or deleted) upstream
Labels: priority::medium, type::bug
> Discovered during plan-040 Issue 4.4's backfill.

MEASURED: after stamping 18 coarse trackers, `upstream.py closable` proposed 25 closures:
  - 23 already CLOSED upstream
  - 2 no longer exist (#139 d...

**Disposition:** include
**Notes:** Measured blast radius far exceeds the filing: 29 of 35 emitted commands are no-ops or errors, 6 genuinely actionable (exp-003). Spec gap first — current behavior is spec-conformant. Epic 3.

## #143 — Five plan.md **Epic:** fields are dangling refs to pre-rename beads-skills-mol-* beads
Labels: priority::low
> Discovered during plan-040 Issue 4.4's backfill.

MEASURED: plan-007, plan-009, plan-010, plan-012 and plan-017 each record an epic id with the
`beads-skills-mol-*` prefix. `bd list --all --json` retu...

**Disposition:** include
**Notes:** Re-scoped 5 -> 14 dangling refs (plan-004..plan-017); the issue counted only the tracker-bearing subset. Defect is a SILENT FALSE SUCCESS in resume-scan (found:true, total:0), not found:false. Repair all 14 keeping bundles OKF-legacy + add a validator (D-3). Epic 3.

## #152 — feature: yf auto-updates claude-code settings.json to disable recommended skills/tools (UPSTREAM)
Labels: type::feature, priority::medium
> Have yf automatically update claude-code settings appropriately, with the recommended competing skills/tools disabled (so the yf skills take precedence). This should be filed as an upstream GitHub iss...

**Disposition:** exclude
**Notes:** Deferred by operator decision (D-1): a feature rather than a defect, and a new autonomy-lever config write that deserves its own consent-gate design pass alongside plan-042's gate. Not scheduled here.
