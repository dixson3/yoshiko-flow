---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` publishes beads-backed Claude Code skills (`yf-*`) plus a compiled Rust CLI,
`yf`, that installs and verifies them. This plan touches exactly one skill,
`skills/yf-beads-upstream/`, which mirrors local `bd` beads to a GitHub/GitLab/Jira issue
tracker.

Structure a cold reader needs:

- `SKILL.md` — operator/agent-facing procedure (the thing being fixed).
- `SPEC.md` — `REQ-BUP-NNN` requirements and `GR-BUP-NNN` guardrails. Repo policy is
  SPEC-first: the requirement lands before the code.
- `scripts/upstream.py` (~840 lines) — helper verbs. Established pattern: a **pure planner**
  (`plan_hoist`) returning a command sequence, plus a **thin executor** (`cmd_hoist --apply`)
  running it via `run(["bash","-c",c])`. The new `push` verb mirrors this pair.
- `scripts/test_upstream.py` — 48 passing tests, all `bd` interaction faked (no live DB, no
  network).
- `protocols/UPSTREAM_TRACKING.md` — an **always-loaded companion rule**, hash-pinned in
  `protocols/manifest.json`. Editing it without restamping makes dependent preflights report
  `rule_drift`.

Three orthogonal things are all called "push", and conflating them is a known hazard:
`git push` (repo content), `bd dolt push` (Dolt DB replication — unused here; beads are
`dolt.local-only=true`), and this skill's `gh`-based issue mirror. This plan concerns only
the third.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-14 -->

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
- Plan directory: `docs/plans/plan-038-james-dixson-1ce25a`

## Operator identity

- Git user: `james-dixson` (james@yoshikostudios.com)
- Role: sole maintainer of `yoshiko-flow`; owns the repo and the `dixson3/yoshiko-flow` issue
  tracker.
- Authority scope: full — approves plans, merges to `main`, pushes, and closes issues without
  escalation.
- Relevant to this plan: the operator is also the person whose agent performed the
  non-compliant hand-run push that #106 describes. The defect was found by dogfooding, not
  reported by a third party, so there is no external reporter to confirm reproduction with.

## Runtime assumptions

- **OS / shell:** macOS (Darwin 25.5.0), `zsh`. Note zsh does not word-split unquoted
  parameter expansions — shell loops written for bash silently iterate once. Prefer Python for
  multi-file work.
- **Repo-only.** Every change lands in the working tree. No writes to `~/.claude/`.
- **The installed skills are stale.** User scope is a v0.4.0 snapshot (~2026-07-21); the
  operator has deliberately deferred the redeploy (see plan-037's `REDEPLOY-HANDOFF.md`). So
  the *installed* `yf-beads-upstream` will not carry this plan's changes until that redeploy.
  The repo is the source of truth; do not verify this work by invoking the installed skill.
- **Tests need no network or live `bd`.** `test_upstream.py` fakes every `bd` interaction, so
  the whole suite runs offline. This matters because `bd` is slow under contention.
- **`bd` is slow here.** Commands routinely take 30–200s against the local Dolt DB. Budget
  generous timeouts; do not read a slow `bd` call as a hang.
- **Credentials:** `gh` authenticated as the repo owner for issue read/write. Auth is always
  passed inline (`GITHUB_TOKEN=$(gh auth token) …`), never written to config — an invariant
  this plan preserves rather than changes.
- **Live upstream side effects:** Issue 3.5 files a GitHub issue; reconcile closes #106/#105
  and comments on #117. Those are outward-facing and operator-authorized.
- **Do not run a real push to validate.** `upstream.py push --apply` mutates the public
  tracker. Validate with fixtures and `--dry-run`; the plan requires no live push.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
