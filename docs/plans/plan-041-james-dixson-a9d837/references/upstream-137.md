---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #137: yf self install --from-build can promote a binary with a STALE embedded skills tree (release profile, incremental rebuild)

- **Number:** 137
- **Title:** yf self install --from-build can promote a binary with a STALE embedded skills tree (release profile, incremental rebuild)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

`yf self install --from-build --build` defaults to `--release`. A **release** incremental rebuild does not observe changes under `skills/`, because that tree lives outside the `yf/` package and `yf/build.rs` deliberately emits no `rerun-if-changed`. So the command can promote a binary whose embedded skills tree is **older than the working tree**, silently.

This is the same class of defect as plan-039's `yf-nkgh` (installed skill lagging the repo) — one level down, in the tool meant to fix it.

## Measured

Probe: add a new file `skills/yf-plan/RERUN-TEST.tmp.md`, rebuild without touching anything under `yf/`, extract the binary's embedded tree via `yf skills install --target`, check for the probe.

| Build | Result |
| :-- | :-- |
| `cargo build --release` (plain) | `Finished in 0.26s` — **probe ABSENT**, stale embed |
| `cargo build` (debug, plain) | `Finished in 0.14s` — **probe PRESENT** |
| `cargo build --release` after `touch yf/src/embed.rs` | recompiled 6.10s — **probe PRESENT** |

The debug row is not a contradiction. `rust-embed` v8 is declared without the `debug-embed` feature (`yf/Cargo.toml:18`), so **debug builds read `skills/` from disk at runtime** while **release builds bake it at compile time**. Only release is exposed.

## Root cause, already documented in-source

`yf/build.rs:51-59`:

```rust
// Deliberately emit NO `rerun-if-changed` narrowing (REQ-YF-PRE-009, red-team
// C7): the previous `.git/HEAD` / `.git/refs` pins did not move on a tracked
// source edit, so `build.rs` would not re-run and the dirty flag would go
// stale. With no rerun-if instructions, cargo re-runs this script whenever any
// file in the `yf/` package changes — the best dev-loop accuracy achievable.
// Known limit (documented, not over-promised): it still cannot observe
// repo-wide changes outside the `yf/` package on an incremental rebuild. The
// clean CI/release build (a fresh full build) is unaffected and authoritative.
```

The reasoning is sound and the limit is stated honestly. What has changed is that **`yf self install --from-build` turns that limit into a shipped artifact.** The comment's mitigation — "the clean CI/release build is unaffected and authoritative" — does not apply to the local promote path, which is an *incremental* release build by construction.

## Why it bites

The failure is silent and self-concealing:

- `cargo build --release` exits `0`.
- `yf self install` reports `{"status":"ok", ... "profile":"release"}`.
- `yf --version` prints a **stale git hash**, which is the only visible tell, and only if you know to compare it against `HEAD`.
- `yf skills install` then deploys the stale tree to `~/.claude/skills/`, so the *skills* go stale too — and that is the surface an operator actually uses.

Observed live: a `cargo build` returned in 0.31s leaving a binary stamped `3c25299-dirty` while `HEAD` was `5c747c0`. Caught only by comparing the version stamp to `HEAD` by hand.

## Suggested directions

Not prescriptive; the `build.rs` rationale should be preserved.

- **Emit a broad `rerun-if-changed` for the embedded tree only** — `println!("cargo:rerun-if-changed=../skills");` — *in addition to* the existing no-narrowing behavior for the `yf/` package. Cargo watches a directory recursively, so this covers the embed input without reintroducing the `.git/HEAD` staleness the comment warns about. The two concerns are separable: git-hash freshness wants no narrowing; embed freshness wants one explicit input.
- **Make `--build` force it** — have `yf self install --from-build --build` touch the embed module (or `cargo build` with an env var that busts the unit) before building, so the promote path cannot ship a stale tree even if `build.rs` is unchanged.
- **Fail-loud instead** — after promoting, compare the binary's embedded tree hash against a hash of `skills/` on disk and refuse (or warn hard) on mismatch. `yf` already computes per-skill tree hashes for the integrity marker (`REQ-YF-MARK`), so the machinery exists.

The first is the smallest and most direct; the third would catch the class regardless of cause.

## Related

- plan-039 / #134 — `yf-nkgh` was exactly this symptom one level up (installed skills lagging the repo).
- `REQ-YF-SELF-004` — defines the `--from-build` promote path.
- `REQ-YF-PRE-009` — the requirement `build.rs`'s comment cites.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

