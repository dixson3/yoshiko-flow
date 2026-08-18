---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #158: yf self update could never refresh codex, opencode or pi (--surface blindness)

- **Number:** 158
- **Title:** yf self update could never refresh codex, opencode or pi (--surface blindness)
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

## Summary

`yf self update`'s post-update refresh was structurally unable to reach **three of the five supported harnesses**. Fixed by plan-042 (#157), but recorded separately because the defect is worth its own history.

## The defect (measured, plan-042 finding E5 defect D)

`refresh_user_skills` shelled out with `--surface`, a **deprecated alias spanning only two values** (`claude`, `agents`), and `present_user_surfaces` probed only `~/.claude` and `~/.agents`.

Consequences on the vendor path:

- **codex, opencode and pi were unreachable** — a `yf self update` on a machine using any of them refreshed nothing for that harness, silently.
- Every run emitted a **stderr deprecation warning** for the `--surface` alias.
- The `--surface` value space could not express the full descriptor table (`harness_desc::DESCRIPTORS`, 5 rows).

This was never the motivating defect for any plan — it was found on the way to something else, which is part of why it survived so long.

## Fix (landed)

plan-042 Issues 1.2/1.3 replaced `--surface` with an explicit per-harness `--harness`, backed by the sync's own presence predicate (`REQ-YF-SELF-008`):

- `claude-code` / `agents` keep the incumbent *yf-already-deployed-here* signal (a yf-written `skills`/`rules` dir), which both preserves the `~/.agents`-with-no-`~/.codex` case and avoids writing into a `~/.claude` that yf never installed into.
- `codex` / `opencode` / `pi` are selected by their own config home, making them reachable for the first time.

A binary on `PATH` deliberately does **not** select a harness — that is `REQ-YF-INSTALL-009`'s detection breadth, which is wrong for a write triggered by promoting a binary.

Tests pin both hazards and the newly-reachable harnesses (`yf/src/cmd/self_cmd/sync.rs`, `yf/tests/install_sync_e2e.rs`).

## Status

Fixed in `main` as of the plan-042 merge. Filed for the record per plan-042 Issue 4.3.

Refs #157
