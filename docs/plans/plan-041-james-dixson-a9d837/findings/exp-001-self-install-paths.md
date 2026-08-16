---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-self-install-paths
plan: plan-041-james-dixson-a9d837
created: '2026-08-16'
---

# E1 — What `yf self install` actually does today

**Question.** Map what `yf self install` does on both of its paths; locate
`REQ-YF-SELF-005`'s auto-refresh; determine whether `yf harness tune` runs on either
path.

**Verdict.** The question's premise is wrong, and that is the finding.

## Correction: `yf self install` has only ONE path

`yf self install` is **from-build only**. There is no vendor path inside it. A bare
`yf self install` does not install anything — it refuses, exit 1, before touching the
filesystem (`yf/src/cmd/self_cmd/install.rs:94`):

```rust
// `--from-build` is currently the only supported mode (vendor installs come
// from the curl|sh installer / `self update`, not this command).
if !args.from_build {
    return fail(
        args.json,
        "`yf self install` requires `--from-build` (the only supported mode); \
         vendor installs use the curl|sh installer or `yf self update`",
    );
}
```

Measured:

```
$ yf self install ; echo exit=$?
error: `yf self install` requires `--from-build` (the only supported mode); ...
exit=1
```

**The end-user command is `yf self update`** (`yf/src/cmd/self_cmd/update.rs:298`) —
source gate → fetch `dist-manifest.json` → version compare → download + sha256 verify →
extract → `self_replace` swap → post-update refresh. Initial vendor install is the
cargo-dist `curl|sh` installer, outside the binary entirely (`SPEC.md:743-748`). The two
commands share no code path.

## REQ-YF-SELF-005

Verbatim (`SPEC.md:798-803`):

> - **REQ-YF-SELF-005** *(testable)* after a successful vendor update — unless
>   `--binary-only` — `yf` shall re-deploy user-scope skills/rules by exec'ing the
>   **swap-destination** binary (the path captured before the swap, NOT a post-swap
>   `current_exe()`) once per **present** surface (`--surface claude` / `--surface
>   agents`). A refresh failure shall be **fail-soft**: reported with the manual re-run
>   command, exiting non-zero on the refresh alone, **never** rolling back the
>   (successful) swap. A from-build install shall NOT auto-refresh.

Implemented at `update.rs:262-277` (`refresh_user_skills`), gated solely on
`args.binary_only` (`update.rs:410-423`). "A from-build install shall NOT auto-refresh"
is implemented **by omission** — `install.rs` contains no refresh call at all.

**Load-bearing detail:** the refresh execs `skills **upgrade**`, not `skills install`
(`update.rs:248-250`). `upgrade` prunes *and* calls `install_rules_aggregate`
(`status.rs:103`), so it writes the `YOSHIKO_FLOW.md` rules aggregate. `skills install`
deliberately does not (`cmd/install.rs:7-11`).

## Does `harness tune` run automatically? NO — on either path

Measured by exhaustive grep: `harness` and `tune` return **zero matches** across all 10
files (2628 lines) of `yf/src/cmd/self_cmd/`. The only callers of
`tune_for_install_harnesses` are both inside `cmd/install.rs::compute_tune_bridge`,
gated on the explicit user-typed `yf skills install --tune`.

The codebase's own remediation strings presume tune is manual (`cmd/install.rs:21-25`):
`"warning: skills-only — run \`yf harness tune\` to deploy always-loaded rules"`.

**But the answer is nuanced, not binary.** "Tune does not run" ≠ "no rules are
deployed". The vendor path already deploys the rules aggregate through `skills upgrade`.
What is missing there is tune's **config-alignment** half (settings.json / codex-TOML
merge) and its **multi-harness fan-out**.

## The gap is ASYMMETRIC

| Path | Skills | Rules aggregate | Harness config |
| :-- | :-: | :-: | :-: |
| `yf self update` (end user) | yes | yes | **no** |
| `yf self install --from-build` (dev) | **no** | **no** | **no** |

A single undifferentiated "make both do the full sync" requirement would be untestable —
the two sides need different implementations.

## No staleness detection exists to reuse

`rg "marker::|tree_hash" yf/src/cmd/self_cmd/` → no matches. `self install` never
consults the `REQ-YF-MARK` machinery.

The machinery compares **embedded ↔ deployed** (`marker::embedded_tree_hash` vs
`deployed_tree_hash`, `marker.rs:82` / `:96`). There is **no embedded ↔ repo-source**
comparator anywhere in the crate. Detecting #137's stale embed would need a *third*
file-list builder (walk `skills/<name>/` on disk); the hash algorithm itself
(`marker.rs:59`) is reusable, the builder is not.

The only "verification" `self install` does is exec the promoted binary for
`version --json` to stamp a marker — and it **silently falls back to the current
binary's version on failure** (`install.rs:148`). It compares nothing.

## Two constraints on any fix

1. **Exec, never call in-process.** Calling `cmd::install::run` in-process from
   `self_cmd::install` would deploy the tree embedded in the **currently running (old)**
   binary — reintroducing #137 in a new place. `update.rs:252-258` already warns about
   exactly this for `current_exe()`; the from-build path must likewise exec the
   just-promoted `dst`.
2. **`--tune` can block on stdin.** `--tune` with no `--harness` on a multi-harness
   machine prompts `"Proceed and tune all detected harnesses? [y/N] "`
   (`install.rs:323`, REQ-YF-TUNE-023). An automated sync must pass explicit
   `--harness` or `--yes` or it will hang.

## Implications for the plan

- **D4 must be restated.** The plan asked whether the "end-user vendor path" of
  `self install` refreshes skills and tuning. That path does not exist. The requirement
  must name `yf self update` and `yf self install --from-build` as two separate commands.
- `skills upgrade` vs `skills install` is a real fork: upgrade prunes + writes rules but
  has **no `--tune` bridge** (bridge is install-only, `cli.rs:299-303`). Reaching config
  alignment from upgrade needs a third exec of `harness tune`.
- **A full sync does not by itself fix #137.** A stale binary syncing its stale skills is
  still stale, silently. The forced re-embed (E2) is required, not optional.
- Recommended shape: refactor `refresh_user_skills` out of `update.rs` into a shared
  module, have both commands use it, and add `harness tune` to both — making from-build a
  superset of today's vendor path. Keep the fail-soft contract (already specified and
  tested at `update.rs:886-922`). Add a `--binary-only` analog to `self install`.

## Uncertainties

- Not verified at runtime that `skills upgrade --surface claude` and `harness tune` write
  **identical** `~/.claude/rules/YOSHIKO_FLOW.md` content. Both route to
  `install_rules_aggregate` and both resolvers compute `<anchor>/.claude/rules`, but the
  `acted` skill-set arguments differ (`sel.install` vs `tune_acted_skills()`). Worth a
  sandboxed-`HOME` check before relying on "the vendor path already deploys the right
  rules".
- No install/update was executed; vendor-path claims are read from source and its unit
  tests, not observed end to end.
