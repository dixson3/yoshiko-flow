---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` is a repository of beads-backed **skills** for agentic coding harnesses, plus the
Rust `yf` binary that installs and manages them. It is **both the source and a consumer of its own
skills** — the plan bundles under `docs/plans/` are produced by the `yf-plan` skill this repo ships.

Two stacks:

- **Python** — the skill engines (`_shared/*.py`, `skills/*/scripts/*.py`), run via `uv run` with
  PEP 723 inline dependency blocks. There is no project-level virtualenv or `requirements.txt`; each
  script declares its own deps. **The system `python3` has no `pyyaml`** — anything parsing
  frontmatter must go through `uv run`, not bare `python3`.
- **Rust** — `yf/`, which embeds the `skills/` tree via `rust-embed` at release build time.

**The three-artifact rule is load-bearing for this plan.** Editing `skills/` changes neither the
binary-embedded tree nor the skill the running session resolved at invocation. `SKILL.md` prose is
loaded once at invocation; `plan_manager.py` is re-invoked per call. So a mid-execution
`yf skills install` would run new scripts against old prose — deploy only at land-the-plane.

**Vendoring.** `_shared/okf.py` is copied byte-identically into four `skills/*/scripts/` trees by
`_shared/sync.py`, which `CHANGE-VALIDATION.md` gates in the FAST tier. Editing one without syncing
fails the on-edit gate. This plan touches `okf.py`, so Issue 1.7 is not optional bookkeeping.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-28 -->

- `bd`: bd version 1.2.2 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.12.6 (7938ca5d5 2026-08-25 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.98.0 (2026-08-20)
- `glab`: glab 1.115.0 (c3612c8de)
- `claude`: 2.1.247 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-056-james-dixson-473dba`

## Operator identity

- Git user: `james-dixson`
- Contact: james@yoshikostudios.com
- Role: repository owner and sole maintainer of `dixson3/yoshiko-flow`.
- Authority scope: full — may approve plans, authorize pushes to `main`, file and close upstream
  issues, and authorize destructive local operations. No second approver exists or is required.
- **Delegated authority this plan does NOT carry:** nothing may be filed to
  `GoogleCloudPlatform/open-knowledge-format` (D-6, read-only tracking), and no write of any kind may
  be made to the 40 other repositories surveyed in EXP-005 (D-10).

## Runtime assumptions

- **OS/shell:** macOS (Darwin 25.5.0), `zsh`. Paths are case-insensitive; `sed` is BSD, **not GNU** —
  it does not support `\|` alternation, and a prior plan recorded it matching nothing while reporting
  success. Prefer Python for text surgery.
- **Network:** required only by the upstream reconcile (Issue 4.3). Everything else runs offline. The
  baseline-pin detector that used to need it was carried to plan-057 at the D-17 split.
- **Credentials:** `gh` is authenticated and owns its own credential store — **no token is ever
  written to config or passed inline**. `bd` is configured `dolt.local-only = true`, so
  `bd dolt push` must never be proposed.
- **Side-effect permissions.** **Every write this plan makes is additive, with one exception that is
  not destructive:** Issue 3.4 repairs the indexes of bundles that are drifting *now*, which is forward
  maintenance of live artifacts. **This plan modifies no completed bundle's content on any axis.**

  An earlier revision of this file described a `backfill --apply` rewriting 30 completed bundles under a
  human capability gate, with nine lines of fingerprint safety evidence. **That was pre-split text and it
  was false for this plan** — there is no such issue and no such gate here; the work is plan-057's, whose
  `context.md` carries it. It survived six red-team passes because every instrument reads `plan.md` and
  none cross-checks its siblings, which is this plan's own thesis reproducing inside its own bundle.


- **The other 40 repositories are strictly out of bounds.** EXP-005 surveyed them read-only. The
  hygiene skill must be *able* to run there; this plan never runs it there.
- **Bundle count assumptions will drift.** Every corpus figure in this plan was measured on
  2026-08-28. Per D-1 and D-10, re-measure before citing rather than inheriting.

## Adjacent-concept glossary

- **OKF** — Open Knowledge Format. An upstream, vendor-neutral markdown+frontmatter format for
  knowledge bundles, now at `GoogleCloudPlatform/open-knowledge-format`. yf is *compatible with* it,
  not governed by it.
- **Bundle** — an OKF "unit of distribution". Here, a plan or research folder. **OKF v0.2 provides no
  way to identify a bundle root**, which is EXP-006's central finding.
- **Reserved files** — `index.md` (a listing) and `log.md` (newest-first history). Reserved at every
  level by OKF; yf uses them only at the bundle root.
- **`doc_lint` mini-schemas** — 17 `document_types/*.toml` files declaring 48 checks over typed yf
  documents. Status-aware and repo-root-relative.
- **`okf.check_conformance`** — the second, independent structural validator. Status-blind and
  bundle-relative. The two have never referenced each other; Issue 4.1 fixes that.
- **`STATUS_SEVERITY`** — doc_lint's promotion/demotion table. At `complete` it demotes both `E` and
  `W` to `R`, which is why 46 of 48 checks cannot currently fail.
- **Drift (index)** — an index that no longer matches its directory: a `ghost` entry names a file that
  is gone; a `missing` entry is a file the index omits.
- **Collapsed signal** — this repo's recurring defect class: two distinct facts sharing one signal.
  `no-index` vs `no-such-path` (EXP-001) is a fresh instance; #263 is the meta-issue.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
