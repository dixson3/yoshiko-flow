---
type: Reference
okf_spec: OKF-PLAN
id: exp-006-symlink-revert-spike
description: EXP-006 — does `yf harness tune --revert` behave correctly through symlinks into a git-tracked dotfiles repo?
---

# EXP-006: symlinked-surface revert spike

**Verdict: reverting TODAY is SAFE. A latent defect is confirmed, and the safety margin is
EXACTLY ONE LINE.**

Six sandbox spikes under `$(mktemp -d)` with a fake `HOME` and a scratch `git init` dotfiles
repo. The operator's real `~/.pi`, `~/.config/opencode` and `~/_dotfiles` were **only read**.

## Approach Tested

Built `./target/debug/yf` (reads `skills/` from disk; repo tree left clean). Ran **six sandbox spikes** under `$(mktemp -d)` with a fake `HOME` and a scratch `git init` dotfiles repo: a symlinked block file with operator prose; the same with an **empty** operator file; a symlinked **directory** (the opencode shape); the touched-since-tune guard via direct edits to the symlink *target*; the claude-code `aggregate` kind in four variants; and a **high-fidelity replica** using the real `AGENTS.md` files and manifests with all paths rewritten to the sandbox (verified: zero real paths remained). The operator's real surfaces were **only read**. All scratch dirs removed; `git status` identical before and after in both the repo and `~/_dotfiles/rc-files`.

## Result

## What is correct

**Every *write* path handles symlinks properly.** Tune and revert both go through
`std::fs::write`, which **follows** the symlink: the link is preserved, the target is modified.
Verified for both shapes — a symlinked **file** (the pi shape) and a symlinked **directory**
(the opencode shape, the riskier case). After tune+revert in both: link intact, content restored
byte-exact, scratch git repo **clean**.

**The touched-since-tune guard works through the symlink.** Editing the target directly after a
tune yields `"removed":["permission.*"],"kept":["share"]`, and operator prose appended
post-tune survives block removal.

## The defect: the DELETE path deletes the SYMLINK, not the content

Two independent reproductions:

- **pi shape, block-only file** (removing the block empties it): revert reported
  `"status":"reverted","removed":true,"wrote":true` — but `~/.pi/agent/` afterwards contained
  **no `AGENTS.md` at all** (the symlink was gone), while the dotfiles target still held
  **14552 bytes of yf-generated block**, leaving the repo ` M pi/AGENTS.md`.
- **`aggregate` kind at a symlinked path**: same shape — symlink deleted, **31613 bytes** of yf
  aggregate stranded in the tracked file, repo dirty, **and revert still reported success.**

Cause: `std::fs::remove_file(&path)` **unlinks the symlink itself**, whereas `std::fs::write`
follows it (`yf/src/cmd/harness/revert.rs:430` and `:477`). Every other branch uses `write`,
which is why only the two delete branches misbehave.

**This is #203's class again** — an operation reporting `"status":"reverted"` while the
postcondition is false.

## The risk to the operator's real setup — the answer to Q5

**Running `yf harness tune --revert` against `~/.pi` and `~/.config/opencode` right now is
safe.** It would strip the managed block from two *tracked* dotfiles files and remove
`permission.*` / `share` from `opencode.json`, leaving `~/_dotfiles/rc-files` dirty with ~502
deleted lines to commit or `git checkout`. **Housekeeping, not hazard.**

**But the margin is one line.** Measured: each real `AGENTS.md` has exactly **1** non-blank line
outside the managed block. Both files clear the delete branch *only because that single prose
line survives*. Remove it — or let yf's block become the whole file — and `--revert` silently
deletes the symlink and strands 14 KB in the tracked dotfiles file, **while reporting success**.
Latent, not hypothetical, on this machine.

Real-state facts that decide this: `rc-files/pi/AGENTS.md` and `rc-files/opencode/AGENTS.md` are
**tracked and currently clean** (the 251-line yf block is *committed*); `opencode.json` is
untracked; the `.yf` manifest is git-**ignored**. `~/.claude/rules/YOSHIKO_FLOW.md` is a
**regular file, not a symlink**, so the aggregate branch does not reach the real claude-code
surface.

## #154 is HALF-FIXED, and the surviving loss happens at TUNE, not revert

| Case | Behaviour | Verdict |
| :-- | :-- | :-- |
| Untouched yf-created aggregate | deleted (`removed:true`) | correct — fully regenerable |
| Hand-edited after tune | `"status":"kept_modified"` | **the REQ-YF-TUNE-029 sha guard works** |
| **Pre-existing operator content** | **destroyed by `tune`**, before revert is ever reached | **the real remaining defect** |

With `# MY OWN RULES / precious operator content` in place beforehand, the post-tune file no
longer contained it (`grep -c` → 0). Revert then *legitimately* deletes, because the sha matches
yf's own write. So "deleted rather than restored" is **still literally true** for that case —
there is no backup anywhere in the flow — but the defect's true location is the **tune-time
whole-file overwrite**, not revert.

**#154 should be re-scoped, not re-closed.** The `block` kind (codex/opencode/pi) is unaffected.

## Why no existing test catches this

The bug is **symlink-agnostic in the manifest** — nothing recorded distinguishes a symlinked
target — and `yf/tests/harness_cross_e2e.rs` exercises **regular files only**.

## Implications for Plan

- **Reverting today is safe** — a housekeeping consequence (a dirty dotfiles repo), not a hazard.
- **The safety margin is exactly one line.** Both real files clear the delete branch only because a single prose line survives outside the managed block. This is a latent, not hypothetical, hazard on this machine.
- The bug is **symlink-agnostic in the manifest**, so no existing test can catch it; `harness_cross_e2e.rs` uses regular files only.
- **#154 should be re-scoped, not re-closed:** the revert half is fixed; the unfixed half is that `tune` overwrites a pre-existing aggregate with no backup.

## Recommendations

Both a code fix and a release note; **the note alone is insufficient**.

- **Code fix (P1, ~5 lines)** — in `revert.rs`, before either `remove_file`, check
  `path.symlink_metadata()?.file_type().is_symlink()` and write through the link instead of
  unlinking it. Simplest correct behaviour for the block-empties case: **drop the
  "delete when empty" optimization when the path is a symlink.**
- **Test (P1)** — a symlink variant in `harness_cross_e2e.rs` covering both delete branches:
  assert the link still exists and the target no longer contains `BEGIN yf-managed-rules`.
- **Release note (P2)** — `--revert` edits the *targets* of symlinked surfaces, so a dotfiles
  repo is left dirty **by design**.
- **Separate bead for #154's remaining half** — `tune` should refuse to overwrite, or back up, a
  pre-existing aggregate yf did not author.
- **Cosmetic** — the `KeptModified` reason string carries ~30 literal spaces from a wrapped Rust
  string literal.

## Confidence

**measured:** all six spikes, both delete-branch reproductions, the guard behaviour, the high-fidelity replica (paths verified fully remapped), and every real-state fact — tracked and ignored status, the one-line margin, and `YOSHIKO_FLOW.md` not being a symlink.

**inferred:** the `remove_file`-versus-`write` cause, corroborated by two independent observations and the two source lines.
