---
type: Finding
okf_spec: OKF-PLAN
id: exp-006-spec-and-validation-surface
plan: plan-044-james-dixson-f6fdbd
created: '2026-08-17'
---

# exp-006 — SPEC-first and validation machinery (reference)

**Date:** 2026-08-17 · verified at `HEAD = 0d900b1`
**Purpose:** the sequencing constraints every epic in this plan must satisfy.

## SPEC family

Two tiers (`SPEC.md:512-527`): the **macro spec** `/SPEC.md` (1412 lines, `REQ-YF-*`) and 19
**per-skill** `skills/<skill>/SPEC.md` (`REQ-<KEY>-NNN`). Nine skills also carry `spec/*.md`
design docs which **do** carry REQ ids in practice (e.g. `REQ-CLI-*` in
`skills/yf-plan/spec/cli.md`, `REQ-COMPLETE-*` in `spec/phases.md`).

**One amendment log**, at `SPEC.md:8-497`, blockquoted, oldest-first. Per-skill SPECs have none
(sole exception `yf-herdr`). Entry shape to copy — `**plan-NNN (YYYY-MM-DD, #issue — title):**`,
every id bolded+backticked, verbs *Added / Revised / Amended / Superseded / Corrected / WAIVED*,
an `Engine:` clause naming touched source files.

## The coverage gate — three limits to design around

`yf/src/coverage.rs` (258 lines), a `#[cfg(test)]` module, so `cargo test` + CI enforce it.

1. **Macro-only.** `testable_reqs()` (`:80-102`) requires `**REQ-YF-`. **Per-skill `REQ-PLAN-*` /
   `REQ-BUP-*` / `REQ-CLI-*` are entirely ungated** — they rely on per-skill pytest suites and
   prose `Verification:` lines, a convention rather than a gate.
2. **Exact-string annotation.** `if !line.contains("*(testable)*")` (`:85`).

   | Annotation | Enforced? |
   | :-- | :-: |
   | `*(testable)*` | **YES** |
   | `*(testable, plan-042)*`, `*(testable, #67)*` | **no** |
   | none, `*(WAIVED …)*`, `*(superseded …)*` | no |

3. **Tags scanned in `yf/src/**` only** (`:177`, `:208`). **A REQ tagged only in `yf/tests/*.rs`
   does NOT satisfy the gate.** `install_sync_e2e.rs` passes only because its REQs are *also*
   tagged in `src`. Any integration-test-only REQ needs a `// REQ-…` comment in a `src` file.

Failure mode: `every_testable_req_is_tagged_or_allowlisted()` (`:164-197`) **panics**, failing
CI. Escape hatch is `ALLOWLIST` (`:36-69`, 7 entries), itself policed by a second test that fails
if an entry is stale or now-tagged. Self-stated honest scope (`:10-17`): *"proves a test **names**
a REQ id, not that its assertions verify intent — a tripwire, not a proof."*

**Precedent for a SPEC-first epic:** plan-032 used a temporary allowlist bridge while the SPEC
landed ahead of the implementing epics, then went net-clean (`coverage.rs:65-68`).

## Next free ids

`REQ-YF-TUNE-029` · `REQ-YF-SELF-009` · `REQ-YF-FLOW-008` · `REQ-YF-MARK-005` ·
`REQ-YF-DOCTOR-006` · `REQ-YF-INSTALL-010` · `REQ-YF-PRE-012` · `REQ-BINIT-026` ·
`REQ-BUP-060` · `REQ-CLI-020` · `REQ-PLAN-077`

Consent-gate anchor: `consent_required` is declared in **REQ-YF-TUNE-001** (`SPEC.md:1120`),
default `false`, *"profile-declared rather than key-path-matched"*. Profiles live at
`yf/profiles/{claude-code,codex,opencode}.json` — **only 3**.

## CHANGE-VALIDATION.md — §0 `approved: yes`, both triggers live

FAST = 27 ided rows; FULL = 28 rows with **empty id cells** (FAST + `cargo clippy --workspace
--all-targets -- -D warnings`), so FULL is not glob-selectable — it is the all-or-nothing
pre-push gate mirroring CI.

| Edited path | FAST ids that fire |
| :-- | :-- |
| `yf/src/**` (`.rs`) | `cargo-fmt`, `cargo` |
| `yf/src/cmd/{harness,self_cmd}/**` | + `sync-e2e` |
| `yf/profiles/**` | `cargo`, `sync-e2e` (**no `cargo-fmt`**) |
| `skills/yf-beads-upstream/scripts/*` | `uv-with`, `bup-prescriptive-push`, `bup-gh-direct` |
| `skills/yf-plan/scripts/*` | all 13 `uv-yf*` ids |
| `skills/*/SKILL.md` | targeted ids + `frontmatter` |
| **`SPEC.md`** | **NOTHING** |
| **`skills/*/SPEC.md`, `skills/*/spec/*`** | **NOTHING** |

> **The single most important sequencing finding.** A **SPEC-first Epic 0 that edits only
> `SPEC.md` fires ZERO change-validation.** A bare-`*(testable)*` REQ added with no test will
> therefore break the **next** epic's FAST run, not its own. Add an explicit `cargo test
> --workspace` step to the SPEC epic itself.

A new test script costs **three** edits: the §1 row, the §3 glob, and a §2 fingerprint
re-approval (`**/test_*.py` is fingerprinted).

## DRIFT-CHECK.md — §0 `approved: yes`, 43 nodes / 47 edges

This repo is the engine's reference instance. §7: on a conflict across a spec-rooted edge **the
spec wins** — never edit a spec to fit. Exception: if the *authority itself* is stale, emit
CONFLICT and **halt**.

| Changed path | Scopes to |
| :-- | :-- |
| `SPEC.md` | `e-spec-guardrails`, `e-spec-readme` |
| `skills/*/SPEC.md` | `e-skillspec-skillmd`, `e-skill-page-spec` |
| `skills/*/scripts/*.{sh,py}` | `e-skill-script-cli`, `e-json-contract` |
| `skills/*/SKILL.md` | **19 edges — the widest fan-out** |
| `yf/src/**` | **no glob** |

> **Complement to the gap above.** Where change-validation is silent on `SPEC.md`, drift-check is
> **not** — a SPEC edit fires `e-spec-guardrails` + `e-spec-readme`, so **`GUARDRAILS.md` and
> `README.md` must move in the same pass** or the on-edit check FAILs. Conversely `yf/src/**` has
> no drift glob. Neither manifest alone covers a SPEC→code→doc change end to end.

## TESTING.md — Tier-1/Tier-2, and a correction

Scoped by its own title to the **manager-script skills** only. Tier-1 = `uv run
skills/*/scripts/test_*.py`. Tier-2 = **mechanical drive** of the manager verbs (deterministic,
offline, no LLM) under a **sandboxed `HOME`**, because the `SKILL_DIR` resolver searches
`~/.claude/skills` first (`head -1`) and would otherwise shadow the scratch copy:

```bash
HOME=<sandbox> cargo build          # debug reads ../skills at RUNTIME — no rebuild for skill edits
HOME=<sandbox> yf skills install
HOME=<sandbox> <drive + verify>
```

Binary is the **workspace-root** `target/debug/yf`. Do not promote into the real `~/.claude` until
Tier-2 passes.

**Correction: TESTING.md is silent on cross-harness testing.** The 5-harness recipe lives in the
Rust integration tests instead. `yf/tests/harness_cross_e2e.rs:69-93 surfaces()` is the
per-harness oracle — but it **panics on `"agents"`** (`:91`), so it covers 4 of 5, iterating
`["claude-code","codex","opencode"]` (`:111`) with `pi` in its own test (`:185`). The table that
*does* cover all five is `sync.rs:358`; `:375` flags `harness_detect::PROBES` as the regression
hazard. Only 3 harnesses have config profiles; `pi` is rule-only, `agents` is a bare surface.

## Rust test organization

Unit tests inline `#[cfg(test)] mod tests` in **30 source files** — *this is where coverage tags
must live*. Integration tests `yf/tests/<concern>_e2e.rs`, selected by target
(`cargo test -p yf --test install_sync_e2e`).

Shape to copy (`install_sync_e2e.rs`): `const YF: &str = env!("CARGO_BIN_EXE_yf")`; a `yf_at()`
helper setting `.env("HOME", home).env_remove("CI")`; `seeded_home()` pre-creating
`.claude/skills` so the presence predicate selects it; `snapshot()` for byte-level no-op asserts.

**Assert the JSON status, never just the exit code** (`:112-118`):

```rust
assert_eq!(tune["status"], "ok", "…: {out}");  // "an exit code of 0 alone would not prove it"
```

**Sandbox discipline (quote into the plan)** — `install_sync_e2e.rs:9-16`: every invocation sets
`HOME` to a tempdir and clears `CI`; nothing may touch the real `~/.claude`, `~/.config`,
`~/.codex`, `~/.local/bin`, because the claude-code profile applies
`permissions.defaultMode: "bypassPermissions"` — a leak would **silently escalate the developer's
security posture**, the exact harm the consent gate exists to prevent.
