---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #238: yf ignores XDG_CONFIG_HOME / CODEX_HOME / OPENCODE_CONFIG_DIR when resolving harness directories

- **Number:** 238
- **Title:** yf ignores XDG_CONFIG_HOME / CODEX_HOME / OPENCODE_CONFIG_DIR when resolving harness directories
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Summary

`yf` resolves every harness directory from `$HOME` plus a hardcoded relative subpath, and
**ignores the environment variables the harnesses themselves honour**. Measured on the v0.5.0
tree: `XDG_CONFIG_HOME`, `CODEX_HOME` and `OPENCODE_CONFIG_DIR` occur **zero times** anywhere
under `yf/src/cmd/harness/` or `yf/src/dest.rs`.

## Why it matters

`yf` already documents that it resolves **its own** dirs via XDG and honours `XDG_*` overrides
(README, "Files and directories"). Harness destinations do not get the same treatment, so an
operator who has relocated their opencode or codex config has `yf` writing to a path that
harness does not read — and the install reports success.

This is the same shape as the resolver defect v0.5.0 just fixed (#-plan-054): a destination
computed one way and read another, with nothing reporting the mismatch.

## Scope

- `opencode` honours `OPENCODE_CONFIG_DIR`; `codex` honours `CODEX_HOME`; both fall back to
  XDG. The descriptor table (`yf/src/harness_desc.rs`) is the natural home — an env-var
  override column beside `user_subpath` / `project_subpath` keeps resolution in the one place
  that already owns it.
- `REQ-YF-TUNE-030`'s `settings_read_layers` is the precedent for widening what a profile
  declares without changing the write target.

## Not doing it blind

The exact variable names and their precedence should be verified **against each installed
harness**, not against its docs site — see the verify-against-the-binary rule recorded in
`yf-beads-extra` (#195). This issue records the gap; it does not prescribe the values.

Discovered by plan-054 (release-readiness pass), out of scope for that plan.

