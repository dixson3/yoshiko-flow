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

**Specific to this plan:** the document-conformance engine it extends lives in `_shared/`
(`doc_lint.py`, `plan_extract.py`, `pour_fidelity.py`, `document_types/*.toml`), shipped by
plan-047 Epics 0–5. `_shared/` is a real constraint: `derive_from` resolves **only** modules under
that directory, which is why hoisting producer constants out of `plan_manager.py` is a prerequisite
rather than a detail.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-08-19 -->

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
- Plan directory: `docs/plans/plan-048-james-dixson-ed68a5`

## Operator identity

- Git user: `james-dixson`
- Attribution: James Dixson <james@yoshikostudios.com>, sole maintainer and operator of this
  repository.
- Authority scope: full — may approve plans, authorize outward-facing writes (`gh` issue comments
  and closures against `dixson3/yoshiko-flow`), authorize deploys, and
  authorize deploys (`yf self install`). Every gate in this plan routes to this operator.

## Runtime assumptions

- **OS / shell:** macOS (darwin 25.5.0), `zsh`. **BSD `sed`/`grep`, not GNU** — this has caused real
  defects here. Also: **zsh arrays are 1-indexed**, which in plan-047 produced a loop iteration with
  an empty variable that wrote a file named `.txt` recording an empty command as `exit: 0`.
- **Network:** required for `gh` only, in **Epic 4** (the landing epic). Epics 0–3 are entirely local.
- **Credentials:** `gh` auth is present and owns its own credential store — no token is ever passed
  inline or written to config.
- **Side-effect permissions this plan assumes:**
  - Writes under `_shared/`, `skills/`, `tests/fixtures/`, and this plan's own bundle.
  - **NO corpus rewrite.** Per D-4 as amended, the `plan.md` worklist is addressed by widening the
    **extractor grammar**, so this plan modifies **zero** documents under `docs/plans/` outside its
    own bundle — SC1 asserts exactly that. The corpus migration was deferred to **plan-049** (D-13).
  - **Outward-facing `gh` comments and one issue closure (#175)**, gated by the Upstream-write gate,
    which blocks Issues **4.5 and 4.5a**. Drafts land in `references/comment-*.md` first.
  - A deploy (Issue **4.7**) at land-the-plane only — **never mid-execution**, per AGENTS.md, because
    `plan_manager.py` is re-invoked per call while `SKILL.md` prose loads once at invocation.
- **Never `bd dolt push`** — this repo is `dolt.local-only = true`.
- **Safe to run as-is on a different machine?** **No.** This plan measures *this* repo's corpus and
  fixes targets against those measurements (150 unparsed → target 54; 610 report-only; 180 files
  currently reachable of 744). A cold reader on another checkout must re-measure before acting — and
  note that **`Incubator/` does not exist here at all**, so every `Incubator/*` glob in the shipped
  schemas is inert in this repo though correct elsewhere.

## Scope boundary with plan-049

This plan is the **first half of a split taken at approval** (D-13). It ships the SPEC amendments,
the extractor grammar widening, the document-type instantiation, the relational checks, and its own
landing. **plan-049** inherits the corpus migration (`okf.py migrate` over 30 legacy `README.md`
bundles plus research-001) and the enforcement binding (`_audit_plan` consuming linter findings, the
always-on on-edit rule, the positive controls), together with decisions D-4a, D-8, D-9 and D-11 and
the deferred upstream rows #140 and #149. Issue 4.6 authors `references/handoff-049.md`.
