---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (a.k.a. `beads-skills`) is a monorepo of beads-backed Claude Code skills
(`skills/yf-*`) **plus a Rust `yf` kernel binary** that provides `yf preflight <skill>` and
`yf doctor`. This plan changes the **kernel** (Rust), not just skills:

- `yf/src/preflight.rs` — the per-skill preflight pipeline (`run_with_env`, ~:259); `ensure_scaffold`
  (~:965) is the precedent for a sanctioned idempotent write to the repo.
- `yf/src/cmd/doctor/{mod.rs, check.rs, checks.rs}` — the `Check`-trait registry; `checks()`
  (~:215-252) is the per-skill check-assembly loop. `mod.rs:34-37` short-circuits `--repair` to
  `beads_init::repair`; `mod.rs:41` hardcodes a single `Scope::User/Surface::Claude`.
- `yf/src/embed.rs` — the `skills/` tree (incl. `formulas/*.formula.toml`) is `rust-embed`-compiled
  into the binary; `common.rs:100` deploys a verified byte-identical copy on install.
- Root `SPEC.md` is the kernel spec: §3.5 `REQ-YF-PRE`, §3.6 `REQ-YF-DOCTOR`, with a living
  amendment log at the top. `docs/yf/preflight-contract.md` §2 is the preflight status enum.

Beads staging: `bd` resolves molecule protos from a project's `.beads/formulas/`. Today skills
copy a formula in per-invocation; this plan moves that ownership into the kernel.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-11 -->

- `bd`: bd version 1.1.0 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.26 (396ef7ce4 2026-06-30 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.96.0 (2026-07-02)
- `glab`: glab 1.106.0 (fc1869c7)
- `claude`: 2.1.201 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-027-james-dixson-a59656`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson (GitHub `dixson3`), repo owner/maintainer, full authority over the
  `dixson3/yoshiko-flow` codebase and its published skills + `yf` kernel.

## Runtime assumptions

- **OS/shell:** macOS (darwin), zsh. Downstream Linux/Windows consumers exist; keep shell snippets
  portable.
- **Rust toolchain required.** This plan compiles the `yf` kernel (`cargo build`/`cargo test` in
  `yf/`). The Capability Gate blocks the Rust epics until the toolchain is confirmed. bd 1.1.0.
- **Binary-distribution / cutover assumption (load-bearing, pass-1 M5).** Skills run from the
  installed/embedded copy, and the staging ownership lives in the **compiled `yf` binary**. The
  SKILL.md migration (Epic 4, dropping the cp/rm dance) is only safe once operators run the
  **rebuilt** binary. Cutover (`install.sh --force`) must rebuild+install the binary and skills
  together and verify `yf --version`; a migrated SKILL.md against a stale binary is a broken window.
- **Side effects:** edits the `yf` Rust kernel, skill SKILL.md files, and root `SPEC.md`; preflight
  gains a new idempotent write into the project `.beads/formulas/` + root `.gitignore` anchor. No
  network/credentials to execute. GC (`doctor --repair`) deletes files — bounded to yf-staged
  entries via the staged-manifest marker (never foreign formulas).

## Adjacent-concept glossary

- **Molecule / formula / proto** — a `bd` workflow template (`*.formula.toml`); `bd mol pour|wisp
  <name>` instantiates it. `bd` resolves the proto from `.beads/formulas/<name>.formula.toml`.
- **wisp** — an ephemeral (`phase="vapor"`) molecule; created, injected, executed, then burned
  (`bd mol burn <id> --force`).
- **Staging** — placing a skill's formula into `.beads/formulas/` so `bd` can resolve the proto.
- **rust-embed / embedded tree** — the `skills/` tree compiled into the `yf` binary; the source of
  truth for what `yf doctor`/preflight see, independent of on-disk install scope.
- **FormulaCheck** — the new static `yf doctor` check validating pour/wisp ↔ shipped-formula.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
