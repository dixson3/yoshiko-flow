---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (`dixson3/yoshiko-flow`) ships **beads-backed skills for Claude Code and four other
harnesses**, plus `yf`, a Rust CLI that embeds the skill tree (`rust-embed`) and deploys it. The
skills are markdown instruction files with Python scripts (`uv`-run, PEP-723 inline deps) and a
`spec/*.md` requirements corpus.

**The repo is both the SOURCE and a CONSUMER of its own skills**, and this plan edits the very skill
it is executing under. Three artifacts move independently — repo source (`skills/`), the
binary-embedded tree, and the session-installed copy under `~/.claude/skills/` — and the `SKILL_DIR`
resolver reaches **none** of the repo's `skills/` paths. So `SKILL.md` prose and
`${SKILL_DIR}/scripts/*.py` resolve to the INSTALLED copy: there is no self-modification hazard
mid-run, and the one real constraint is **no `yf skills install` / `yf self install` mid-execution**
(`plan_manager.py` is re-invoked per call, so a mid-execution deploy would run new scripts against
old prose).

Task tracking is `bd` (beads) on Dolt, `dolt.local-only = true` — **never `bd dolt push`**.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-21 -->

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
- Plan directory: `docs/plans/plan-051-james-dixson-2f499f`

## Operator identity

- Git user: `james-dixson`
- Role: **sole maintainer and operator** of `dixson3/yoshiko-flow`; authors and approves plans.
- Authority scope: authorizes upstream writes (`gh issue` comment / create / close) against a
  generated grant, and authorizes deploys. Capability gates typed `human` are resolved by this
  operator alone and are **never** auto-resolved on a green test.
- Contact: `james@yoshikostudios.com`; upstream issues are filed against the same repo.

## Runtime assumptions

- **OS / shell:** macOS (darwin 25.5.0), `zsh`. Non-interactive flags are mandatory (`rm -f`,
  `cp -f`, `mv -f`) — an `-i` alias would otherwise hang on a confirmation prompt.
- **Toolchain:** `uv` for every Python script; `cargo` for the `yf` build; `bd` **1.1.2**;
  `gh` authenticated against `dixson3/yoshiko-flow`.
- **Network:** required for `gh` (upstream reads and the authorized writes) and for `cargo` on a cold
  build. `bd` is entirely local.
- **Credentials:** `gh` owns its own token store — this plan handles no token and writes none to
  config.
- **Side effects, and where consent is required:** upstream writes are gated (`Upstream write`, human)
  and never happen without an explicit authorization file. Deploying with `--allow-permissions-write`
  is a **separate** operator decision from deploying at all. No `bd dolt push` under any circumstance.
- **Safe to run as-is on a different machine? NO.** This plan measures *this* repo's SPEC corpus and
  skill tree and fixes expectations against those measurements (251 `Verification:` clauses, 1
  executed; 0 `Agent` occurrences across 7 `agents/*.md`; 3 sites pinning one literal; 2 deployed
  harness roots). A cold reader on another checkout must **re-measure before acting** — which is D-5.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
