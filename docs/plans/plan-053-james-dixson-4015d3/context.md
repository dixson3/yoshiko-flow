---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**`dixson3/yoshiko-flow`** — the source repository for the `yf-*` family of agent skills
(`yf-plan`, `yf-research`, `yf-beads-*`, `yf-herdr`, `yf-drift-check`,
`yf-change-validation`, …) plus the `yf` Rust binary that embeds and deploys them.

**The property that matters for THIS plan: the repo is both the source AND a consumer of its
own skills, and those are three separate artifacts that move independently.**

| Artifact | What it is | When it changes |
| :-- | :-- | :-- |
| Repo source | `skills/<name>/` in this working tree | the moment you edit it |
| Binary-embedded tree | what `yf` carries (`rust-embed`) | on rebuild |
| Session-installed skill | what the running session resolved | on deploy, then next invocation |

The `SKILL_DIR` resolver searches `~/.claude/skills`, `~/.agents/skills`,
`$GIT_ROOT/.{claude,agents}/skills` and relative `.{claude,agents}/skills`. **The repo's
`skills/` directory matches none of those six roots** — it is *unreachable* by the resolver,
not merely stale. That fact is the entire subject of upstream issue #210, and it is why four
of this plan's six defects were discovered in a *different* repository.

**Stack.** Python 3.14 via `uv` (PEP-723 inline-dependency scripts, no project venv) for every
skill script; Rust for the `yf` kernel; `bd` (beads, Dolt-backed) for all task tracking;
`gh` for upstream issue tracking against this same repo.

**Non-obvious setup.**

- `_shared/` holds canonical copies of scripts that are **vendored** into individual skills by
  `_shared/sync.py`, which enforces byte-identity. Editing one copy alone fails the FAST tier.
  `_shared/` is a path *inside this repo* and is never installed.
- `bd` is configured `dolt.local-only = true`. **Never `bd dolt push`.**
- `CHANGE-VALIDATION.md` (approved) drives FAST/FULL validation; `DRIFT-CHECK.md` (approved)
  drives cross-edge agreement. Both fire on edit.
- Plans execute in a git worktree (`.worktrees/<plan-id>`) while the plan folder stays
  primary-side.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-25 -->

- `bd`: bd version 1.1.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.3 (507230998 2026-08-07 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.97.0 (2026-07-31)
- `glab`: glab 1.113.0 (d62881304)
- `claude`: 2.1.228 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-053-james-dixson-4015d3`

## Operator identity

- **Git user:** `james-dixson` — James Dixson `<james@yoshikostudios.com>`
- **Role / authority scope:** repository owner and sole maintainer of `dixson3/yoshiko-flow`.
  Holds authority to approve plans, resolve capability gates, authorize upstream writes
  (`gh issue create` / `close`), and authorize `git push` to `main`.
- **Machine:** `d3-mbp-m5.local` (Apple Silicon, darwin 25.5.0), zsh.
- **Credentials:** `gh` is authenticated against `dixson3/yoshiko-flow` and owns its own
  credential store — **no token is ever written to config**. `glab` is installed but unused.
- **Identity-dependent assumptions:** the plan id embeds the author hash
  (`plan-053-james-dixson-4015d3`). Machine-specific absolute paths appear only in this file
  and in `findings/`; every path inside `plan.md` is repo-root-relative, so the bundle stays
  portable to a cold reader on another machine.
- **What a delegate may NOT do:** resolve a capability gate on the operator's behalf, run
  `yf self install` mid-execution, or `bd dolt push` (this repo is `dolt.local-only`).

## Runtime assumptions

- **OS / shell:** macOS (darwin 25.5.0), `zsh`. The system bash is **3.2** — no `mapfile`,
  no `readarray`. Fixture scripts must stay 3.2-compatible; use a NUL-delimited `while read`
  loop instead.
- **Network:** required only for `gh` (upstream reconciliation, Epic 7) and `uv`'s first
  dependency resolve. **Every control and test in Epics 1-6 runs offline.**
- **Services:** none. `bd` is embedded-Dolt and local-only — no server to start, and **no
  replication target**, so `bd dolt push` must never be run.
- **Credentials:** `gh` auth is needed for Epic 7 only. Epics 0-6 need none.
- **Side-effect permissions.** Epics 0-6 write only inside this repo and the plan bundle.
  Epic 7 performs the plan's only **outward-facing** writes (upstream issue create/close) and
  its only **irreversible local** one (the deploy) — both behind gates.
- **`uv` inside a worktree:** prefix with `env -u VIRTUAL_ENV` so uv resolves the worktree's
  own environment. Do **not** follow uv's suggested `--active` — it targets the primary venv,
  the wrong address space.
- **Interactive flags are unavailable:** use `rm -f`, `cp -f`, `mv -f`. `git rebase -i` and
  `git add -i` are not supported here.
- **`bd` behaviours this plan depends on**, all measured: a **batched** `bd show` drops a
  missing id **silently at exit 0**, so existence probes must be single-id; `bd list --all`
  lifts the 50-row default truncation; `bd` can return **error-JSON with exit 0**, so never
  infer state from an exit code alone.

## Adjacent-concept glossary

| Term | Meaning here |
| :-- | :-- |
| **pour** | Materialising a plan's declared DAG into `bd` beads (`bd mol pour` + `bd create`). Happens at EXECUTE start, not intake. |
| **bead** | A `bd` issue. Task, epic, molecule or gate. |
| **molecule / wisp** | A `bd` container for a poured formula; a wisp is the throwaway kind, burned after use. |
| **burn** | `bd mol burn` — deletes a molecule and its issues. The documented remedy for a corrupt pour, and the operation that produces #207's wedge. |
| **driven RED** | Observing a control **fail** on a fixture before its fix exists, recorded with the exit code seen. Distinct from a real failure. |
| **detail** | The per-issue continuation prose `plan_extract.py` emits, poured verbatim as a bead's `--description`. The subject of #206 and #209. |
| **masking** | `mask_inline_code()` blanks inline code spans so a `depends-on:` inside backticks yields no edge. Correct for *parsing*, wrong as the gate for *capture* — that distinction is #206. |
| **vendoring** | `_shared/sync.py` copying a canonical script into a skill's `scripts/`, byte-identically. |
| **land the plane** | The session-close ritual: push, reconcile upstream, tear down, deploy. |
| **fingerprint** | A content hash over `plan.md`'s `##` bodies that carries execution eligibility across the session boundary. A later edit makes the plan stale-approved. |

## Additional context

**Why this plan exists at all is itself context a cold reader needs.** Five of its six
defects (#206-#210) were found on a **single recovery path in a different repository**
(`dixson3/astrospike`, `plan-001`) — a repo that consumes the *installed* skill. They are
structurally hard to see from inside `yoshiko-flow`, because this is the only repo where
`_shared/` paths resolve and the only one whose corpus the fixtures were built from.

A cold reader should treat "it works here" as **weak evidence** throughout this plan. The
strongest controls in Epic 1 are the ones that simulate *not being here*: the plan-050
mutation fixture, and the requirement that `test_pour_fidelity.py` stop depending on live
`bd` state.
