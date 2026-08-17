---
type: Reference
okf_spec: OKF-PLAN
---

# Upstream #157 — plan-042 execution tracking: install-time sync

**URL:** https://github.com/dixson3/yoshiko-flow/issues/157
**State:** OPEN
**Filed:** 2026-08-17 at INTAKE (Phase 4.5)
**Role:** the coarse plan tracker — not a defect report. Snapshot below; the issue is live.

---

Tracking issue for **plan-042** (`docs/plans/plan-042-james-dixson-98631b/`), approved and awaiting execution.

## What it fixes

A promoted `yf` binary and the operator's deployed surface can disagree indefinitely, and nothing says so. The gap is **asymmetric** — neither path closes it, and they fail differently:

| Path | Skills | Rules aggregate | Harness config |
| :-- | :-: | :-: | :-: |
| `yf self update` (end user) | yes | yes | **no** |
| `yf self install --from-build` (dev) | **no** | **no** | **no** |

Today `AGENTS.md` documents a three-step ritual whose steps 2 and 3 are silently optional. This plan makes both commands perform the sync from **one shared routine**.

**Split from plan-041** (its pass-1 review, concern C10): the sync had zero technical dependency on the #137 embed fix while carrying an entire security-consent surface.

## Scope

| Epic | Content |
| :-- | :-- |
| 0 | SPEC-first — amend `REQ-YF-SELF-005`, `REQ-YF-TUNE-023`, `REQ-YF-TUNE-001`; add rules-only + sync-contract REQs |
| 1 | Factor the shared routine (pure refactor), `--harness` + presence predicate, switch the exec |
| 2 | The safe half — rules-only tune mode, wire into `self install`, `--no-sync` |
| 3 | The consent-bearing half — profile consent flags, the gate, CI suppression, delta report, and the single flip |
| 4 | Docs, CHANGE-VALIDATION, upstream |

25 issues. Findings are in the bundle under `findings/`.

## The safety finding this plan turns on

`yf harness tune` applies **autonomy levers** that materially change a machine's security posture, and it can **create** the config file where none exists. An earlier draft gated this on a `permissions.*` key-path test — which is **claude-code-specific**:

| Harness | Autonomy lever | Matches `permissions.*`? |
| :-- | :-- | :-: |
| claude-code | `permissions.defaultMode` = `bypassPermissions` | yes |
| codex | `approval_policy` = `"never"` | **no** |
| opencode | `permission.*` = `"allow"` (singular, blanket) | **no** |

On a machine with an existing codex or opencode config, that gate would have **auto-applied a blanket-allow with no consent**. The profiles' own rationale text already calls both *"the analog of claude-code's bypassPermissions"* — the codebase knew they were the same class; the predicate did not.

Consent is therefore **profile-declared**: a `consent_required: true` flag on the offending profile entries, tested against the computed change set. Self-maintaining — a new lever declares its own requirement rather than depending on a key prefix. `REQ-YF-TUNE-001` enumerates the entry schema exhaustively, so adding that field is itself a SPEC amendment and lands first.

## Incidental gap it closes

**`yf self update` has never been able to refresh codex, opencode or pi.** Its refresh emits `--surface`, a deprecated alias spanning only two values, and probes only `~/.claude` and `~/.agents`. Three of five supported harnesses were unreachable from the vendor path. Moving to `--harness` fixes that on the way.

## Review history

Three adversarial cycles: REVISE → REVISE → APPROVE. Reports in `reviews/`. Two structural corrections worth recording:

- An earlier draft claimed Epic 2 and Epic 3 were independently shippable. They were not — `tune_one_harness_at` runs both sub-operations unconditionally and no rules-only mode exists, so Epic 2 would have shipped the unconsented write Epic 3 exists to prevent. A rules-only mode now makes the seam real, and the dangerous flip is isolated to a single one-line issue.
- Scope did **not** shrink across revision: 22 → 25 issues. Splitting `--prune` out removed two; the safety work review surfaced added three. Recorded honestly rather than framed as a reduction.

## Related, deliberately not absorbed

- **#154** — `harness tune` regenerates `YOSHIKO_FLOW.md` wholesale, no managed block, `--revert` deletes rather than restores. This plan raises its **frequency**, not its severity.
- **#155** — a file dropped from a skill lingers, so that skill reports `modified` forever. Split out of this plan; orthogonal.
- **#156** — `skills upgrade` writes the aggregate to the wrong surface for non-claude-code harnesses. This plan **routes around** it by exec'ing `install --tune` instead; routing around is not fixing, so it is recorded.

Execution has not started. This issue will be stamped onto the plan's epic as `external_ref` at pour.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

