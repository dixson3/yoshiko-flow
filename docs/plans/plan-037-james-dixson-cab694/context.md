---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` publishes a suite of beads-backed Claude Code skills (`yf-*`) plus a
compiled Rust CLI, `yf`, that installs, upgrades, verifies, and repairs them. Two
halves that must stay in agreement:

- `skills/<name>/` — the skill sources (`SKILL.md`, `README.md`, `SPEC.md`, optional
  `scripts/`, `spec/`, `protocols/`). Python helpers run via `uv run` with PEP 723
  inline deps; there is no project-level virtualenv.
- `yf/` — the Rust binary. It embeds the entire `skills/` tree at build time via
  `rust-embed` (`folder = "../skills"`), so a new skill needs no registration to be
  shipped — but `yf/src/testdata/install-parity.json` is a frozen golden fixture that
  `yf/src/parity.rs` asserts against, and it **does** enumerate every skill.

Non-obvious setup a cold reader needs:

- **Two locations for the same skill.** `skills/` in the repo is the source; the
  *installed* copy lives at `~/.claude/skills/<name>/` (user scope). They drift. The
  installer injects a provenance line, `<!-- yf-skills: v=<ver> tree=<sha> -->`, into
  every installed `SKILL.md`; any diff that does not filter that line is 19 false
  positives. **This plan is entirely about the gap between those two locations.**
- **`v=` in the stamp is the Cargo package version, not a git tag.** The `v0.4.0` tag
  is a different commit than the `0.4.0`-stamped install.
- Task tracking is `bd` (beads), never markdown checklists. Repo policy is SPEC-first:
  the `SPEC.md` REQ change lands ahead of the code implementing it.
- Two self-enforcing manifests gate edits: `DRIFT-CHECK.md` (cross-artifact content
  agreement, glob-scoped edges) and `CHANGE-VALIDATION.md` (executable build/test/lint
  recipe).
- The repo is its own dogfood: the `yf-plan` skill used to author this plan is the same
  skill the plan modifies.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-13 -->

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
- Plan directory: `docs/plans/plan-037-james-dixson-cab694`

## Operator identity

- Git user: `james-dixson` (james@yoshikostudios.com)
- Role: sole maintainer and author of `yoshiko-flow`, and the operator whose user-scope
  install is the subject of this plan.
- Authority scope: full — owns the repo, the `dixson3/yoshiko-flow` GitHub issue tracker,
  and the machine holding the divergent install. Can approve plans, merge to `main`, push
  upstream, and close issues without escalation.
- Consequence for a cold reader: the "operator" and the "user whose install is stale" are
  the same person, so there is no coordination boundary to negotiate — but also no second
  party to catch a mistake. The un-upstreamed `yf-herdr` skill exists on **this machine
  only** and has no other copy anywhere.

## Runtime assumptions

**This plan is not machine-portable.** Epic 1 acts on the state of one specific
machine's `~/.claude/` tree. Epics 2 and 3 are ordinary repo work and port fine; Epic 1
does not, and a cold reader on a different machine should not run it.

- **OS / shell:** macOS (Darwin 25.5.0), `zsh`. Note zsh does **not** word-split unquoted
  parameter expansions — shell loops written for bash silently iterate once. The
  investigation hit this; prefer Python for multi-file comparison work.
- **Writes outside the repo.** Epic 1 modifies `~/.claude/skills/` and `~/.claude/rules/`.
  This is the only part of the plan that touches state outside the working tree, and it is
  the only irreversible step.
- **Non-reproducible inputs.** The divergent user-scope tree is the input to Epic 1 and
  exists nowhere else. `yf-herdr` in particular is unstamped, uncommitted, and unbacked —
  if it is lost before Issue 1.2 captures it, it is gone. The capability gate ahead of
  Issue 1.3 exists for exactly this.
- **Credentials / network:** `gh` authenticated as the repo owner (issue close/comment on
  `dixson3/yoshiko-flow`); push rights to `origin`. Network needed for `gh`, `git push`,
  and the Pelican build's asset fetches.
- **Side-effect permissions assumed:** local commits and merges to `main`, worktree
  create/teardown, installer runs that overwrite user scope, and issue mutation. The
  upstream `git push` remains operator-authorized per repo guardrails, not automatic.
- **Tooling:** `bd` >= 1.1.0 (have 1.1.2), `uv`, `python` 3.14, `gh`, plus a Rust toolchain
  for `cargo test` (`parity.rs`) and Pelican for the web build.
- **`herdr` binary:** required by the imported skill, gated on `HERDR_ENV=1`. Assumed
  absent in CI; the skill should be inert there rather than failing. Unverified — carried
  as a risk, not an assumption.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
