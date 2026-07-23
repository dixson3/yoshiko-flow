---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #95 — plan-032 execution tracking: yf harness tune (settings alignment)

- **URL:** https://github.com/dixson3/yoshiko-flow/issues/95
- **State:** OPEN
- **Labels:** (none)
- **Disposition (this plan):** related (predecessor; plan-033 is the follow-on)

## Body

Coarse tracking issue for **plan-032** (one issue per plan-scale effort, per AGENTS.md).

**Plan:** `docs/plans/plan-032-james-dixson-6cb87b/plan.md`
**Objective:** Add `yf harness tune --harness <name>` — a harness-parameterized `yf` subcommand that idempotently aligns a Claude Code `settings.json` to the recommended yf baseline (deny competing native tools, disable competing features), plus a report-only `yf doctor` settings-drift check. Establishes a single machine-readable settings profile as the source of truth. Triggered by local bead `yf-nl8i`.

**Scope (this plan):** Claude Code only, fully implemented and `cargo test`-covered.

**Epics:**
1. SPEC — `REQ-YF-TUNE` (+ amendment log, coverage ALLOWLIST bridge)
2. Canonical machine-readable profile + separate rust-embed root + drift test
3. `yf harness tune` command — kind-aware merge (scalar add-missing/conflict; `permissions.deny` non-destructive union), user/project scope, Agent-never-denied, fail-safe on unparseable input
4. `yf doctor` report-only drift check over the effective merged settings view
5. `yf skills install --tune` flag-gated offer (no interactive prompt)

**Design highlights:** yf's first settings-key writer; never clobbers user `permissions.deny` entries or the `bd setup claude` hook block; multi-harness is a forward-compat lookup key only.

**Deferred follow-ons (out of this plan's scope):**
- Multi-harness profiles + engines (codex/opencode/pi) — gated on the per-harness rules research.
- Reversal/undo path (`--revert`).

**Related:** web-docs counterpart is the canonical settings.json block (local bead `yf-8ayq`).

Review trail: red-team pass-1 (REVISE → resolved) → pass-2 (APPROVE). Execution is per-bead in a `/yf-plan execute` session.
