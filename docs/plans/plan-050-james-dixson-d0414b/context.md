---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` is the source repo for a family of beads-backed skills for Claude Code and other
harnesses, plus the `yf` Rust binary that embeds and deploys them. Stack: Python skill scripts run
via `uv` with PEP-723 inline deps; a Rust workspace under `yf/` (`rust-embed` bakes the `skills/`
tree into release builds); `bd` (beads 1.1.2, Dolt storage, `dolt.local-only = true`) for all task
tracking; `gh` for upstream issues against `dixson3/yoshiko-flow`.

**The non-obvious setup a cold reader must know:** this repo is **both the source and a consumer**
of its own skills, and they are three artifacts that move independently — the repo `skills/` tree,
the binary-embedded tree, and the session-installed copy under `~/.claude/skills/`. The repo's
`skills/` directory matches none of the `SKILL_DIR` resolver's six roots, so it is unreachable at
runtime, not merely stale. See AGENTS.md "Three artifacts, not one".

**Specific to this plan:** the surfaces it changes are `skills/yf-plan/scripts/plan_manager.py`
(the grant generator, the close-chain ordering), `skills/yf-plan/formulas/plan-execute.formula.toml`
and the pour seam in `SKILL.md` §5.2a (the wrapper close), `_shared/doc_lint.py` (the verdicts),
`skills/yf-plan/agents/red-team.md` (one line), and — added by the post-pass-3 Epic-4 re-scope and
the #184 fold-in — `skills/yf-beads-hygiene/scripts/beads_hygiene.py` (a NEW `attribution-audit`
subcommand, strictly **outside** the vendored `# >>> BEGIN active-set classifier … do not edit >>>`
region at lines 269-407), repo-root `CHANGE-VALIDATION.md` (a §1 `fast` row plus a §3 trigger glob),
`skills/yf-plan/SKILL.md` §3 (sub-agent dispatch), and `skills/yf-plan/spec/agents.md`
(REQ-AGENT-043 amended plus one new REQ). `_shared/` is a real constraint: `derive_from`
resolves **only** modules under that directory.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-20 -->

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
- Plan directory: `docs/plans/plan-050-james-dixson-d0414b`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson <james@yoshikostudios.com>, sole maintainer and operator of this
  repository.
- Authority scope: full — may approve plans, authorize outward-facing writes (`gh` issue comments
  and closures against `dixson3/yoshiko-flow`), and authorize deploys (`yf self install`). Every
  gate in this plan routes to this operator.

## Runtime assumptions

- **OS / shell:** macOS (darwin 25.5.0), `zsh`. **BSD `sed`/`grep`, not GNU.** Also: **zsh arrays
  are 1-indexed** — this has produced real defects here three times, most recently while filing
  this plan's own upstream issues, where `T[0]` was empty and every issue title landed on the next
  issue's body.
- **Network:** required for `gh` in **Epic 3 and Epic 6**. Epic 3's grant path calls `_verify_row`,
  whose first act is `gh issue view` per row, so **Epic 3 is not local** — an earlier draft of this
  file claimed it was, and pass-3 C17 refuted it. Epics 0-2, 4 and 5 are entirely local.
- **Credentials:** `gh` auth is present and owns its own credential store — no token is ever passed
  inline or written to config.
- **Side-effect permissions this plan assumes:**
  - Writes under `_shared/`, `skills/`, `tests/fixtures/`, and this plan's own bundle.
  - **NO corpus rewrite.** This plan modifies **zero** documents under `docs/plans/` outside its own
    bundle. SC7 asserts that `doc_lint`'s verdict change perturbed no selection.
  - **Bead writes:** it pours and closes its own molecule, and Issue 4.2 changes how
    `discovered-from` beads are stamped **going forward only** (D-7) — no historical bead is edited.
  - **Outward-facing `gh` comments and a tracker**, gated by the Upstream-write gate (Epic 6).
  - A deploy (Issue **6.6**) at land-the-plane only — **never mid-execution**, per AGENTS.md.
- **Never `bd dolt push`** — this repo is `dolt.local-only = true`.
- **Safe to run as-is on a different machine?** **No.** This plan measures *this* repo's bead DB and
  corpus and fixes expectations against those measurements (1481 beads; 26 `discovered-from` edges,
  0 attributed; 49 of 49 start-gate wrappers hand-closed; `files_checked` parity in SC7). A cold
  reader on another checkout must re-measure before acting.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
