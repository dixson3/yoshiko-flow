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
fails the on-edit gate. This plan touches `okf.py`, so a vendor-sync step is not optional bookkeeping — plan-056's Issue 1.7 is the precedent.

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
- Plan directory: `docs/plans/plan-057-james-dixson-9ecf1c`

## Operator identity

- Git user: `james-dixson`
- Contact: james@yoshikostudios.com
- Role: repository owner and sole maintainer of `dixson3/yoshiko-flow`.
- Authority scope: full — may approve plans, authorize pushes to `main`, file and close upstream
  issues, and authorize destructive local operations. No second approver exists or is required.
- **Delegated authority this plan does NOT carry:** nothing may be filed to
  `GoogleCloudPlatform/open-knowledge-format` (D-9, read-only tracking), and no write of any kind may
  be made to the 40 other repositories surveyed in EXP-005 (D-7).

## Runtime assumptions

- **OS/shell:** macOS (Darwin 25.5.0), `zsh`. Paths are case-insensitive; `sed` is BSD, **not GNU** —
  it does not support `\|` alternation, and a prior plan recorded it matching nothing while reporting
  success. Prefer Python for text surgery.
- **Network:** required by exactly one issue (3.1a, the baseline-pin detector), by the
  "Upstream network reachable" capability gate, and by the upstream reconcile (3.5). Everything else runs offline. The detector's INCONCLUSIVE path exists precisely so
  an offline land is not blocked.
- **Credentials:** `gh` is authenticated and owns its own credential store — **no token is ever
  written to config or passed inline**. `bd` is configured `dolt.local-only = true`, so
  `bd dolt push` must never be proposed.
- **Side-effect permissions.** This plan performs one genuinely destructive local operation: Issue
  2.9's `backfill --apply` rewrites 31 completed bundles in place. It is gated (human capability
  gate), reversible (`--record` plus `git checkout` for tracked paths and an unlink for created ones),
  preconditioned on a clean tree scoped to the bundles being changed, and **crash-recoverable — but NOT
  atomic**. An earlier draft claimed "atomic per bundle by staging-and-swap", which this plan's own
  measurement refutes: `os.rename` onto a non-empty directory raises `OSError errno 66`, so the swap is
  **two renames with a window in which the bundle is absent**. Recovery therefore keys on a durable
  per-bundle journal fsynced before the first rename (Issue 2.4, R2), not on atomicity and not on
  directory presence. This matters here because an operator reads this file before authorizing the
  backfill gate. Every other write is additive.

  **Read the safety evidence precisely — the fingerprint is NOT the guarantee.**
  `_plan_content_fingerprint` covers `plan.md`'s content sections **only**. It excludes `README.md`,
  `index.md` and `log.md` entirely — that is, *every file the backfill mutates* — and it excludes the
  header preamble, which is exactly where `okf migrate` adds frontmatter. So the measured 30/30
  byte-identical result is very nearly a tautology, and it is structurally blind to the one measured
  data-loss mode: the phase log lives above the first `## ` and is dropped from the hash, and
  plan-030 was measured to strand 10 bullets across 2 dates. The real guarantees are the **separate**
  phase-log bullet-and-date equality check and the per-bundle audit-delta check, both fail-closed
  preconditions of `backfill`. An operator authorizing the gate is authorizing on those, not on the
  fingerprint.
- **The other 40 repositories are strictly out of bounds** (D-7). EXP-005 surveyed them read-only. The
  hygiene skill must be *able* to run there; this plan never runs it there.
- **This plan is gated on plan-056's completion.** Three of its outputs are load-bearing here: the
  `description:` producer contract, the member-declared path-exclusion mechanism, and the layer boundary
  document. That is a capability gate with a real `Test:`, not an assumption.
- **Bundle count assumptions will drift.** Every corpus figure in this plan was measured on
  2026-08-28. Re-measure before citing rather than inheriting. (An earlier draft attributed this to D-5, which is
  the backfill halt classes; no decision carries the re-measure instruction — the Investigation Findings
  preamble does.)

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
  bundle-relative. The two have never referenced each other; the layer boundary document
  plan-056 shipped (`docs/validation-layers.md`) is what records the split, and this plan's Issue 3.4
  writes the trigger boundary between the two OKF skills. (An earlier draft cited "Issue 6.4"; this
  plan has four epics and no Issue 6.4.)
- **`STATUS_SEVERITY`** — doc_lint's promotion/demotion table. At `complete` it demotes both `E` and
  `W` to `R`, which is why 46 of 48 checks cannot currently fail.
- **Drift (index)** — an index that no longer matches its directory: a `ghost` entry names a file that
  is gone; a `missing` entry is a file the index omits.
- **Collapsed signal** — this repo's recurring defect class: two distinct facts sharing one signal.
  `no-index` vs `no-such-path` (EXP-001) is a fresh instance; #263 is the meta-issue.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
