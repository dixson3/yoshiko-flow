---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

`yoshiko-flow` (working dir name `beads-skills`) is the source repository for a family of
beads-backed Claude Code skills — `yf-plan`, `yf-research`, `yf-beads-*`, `yf-drift-check`,
`yf-change-validation`, and others. Each lives under `skills/<name>/` as a `SKILL.md` plus
`agents/*.md` prompts, a per-skill `SPEC.md` + `spec/*.md` requirement set, and `scripts/*.py`
helpers invoked via `uv run` with PEP 723 inline metadata (never installed as packages).

Non-obvious properties a cold reader needs:

- **This repo is both the source and a consumer.** The `yf-plan` skill that governs this plan is
  installed user-globally at `~/.claude/skills/yf-plan`, while the code this plan edits lives at
  `skills/yf-plan/` in the repo. They are different copies. Changes here do not take effect for
  the running session until reinstalled. Every verification command in the plan is pinned to the
  repo path for this reason; install parity is deliberately a follow-on (Issue 5.3), not a
  deliverable of this plan.
- **SPEC-first is mandatory** (`AGENTS.md`): a behavior change lands as a `REQ-*` amendment plus
  a living-amendment-log entry *before* the implementation, never after.
- **Two validation surfaces**: `CHANGE-VALIDATION.md` (executes build/test/lint; `fast` and
  `full` tiers) and `DRIFT-CHECK.md` (prose agreement across declared doc/spec/impl edges). They
  are orthogonal and neither invokes the other. A new test script must be added to
  `CHANGE-VALIDATION.md` to run in CI.
- **Task tracking is `bd` (beads) only** — never `TodoWrite` or markdown checklists.
- **Upstream tracking is coarse**: one GitHub tracking issue per plan-scale effort against
  `dixson3/yoshiko-flow`, not one per execution bead.

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
- Plan directory: `docs/plans/plan-039-james-dixson-150f79`

## Operator identity

- Git user: `james-dixson` (james@yoshikostudios.com)
- Role: sole maintainer and author of the `yoshiko-flow` skill family; owns the `dixson3`
  GitHub org.
- Authority scope: full — may amend `SPEC.md`, edit agent prompts, and close/comment on issues
  in `dixson3/yoshiko-flow` without further approval. The plan still gates outward-facing
  writes behind an explicit confirmation step by convention, not by permission limit.

## Runtime assumptions

- **OS / shell:** macOS (Darwin 25.5.0) on `d3-mbp-m5.local`, `zsh`. Paths assume a
  case-insensitive filesystem and a `$HOME` of `/Users/james`.
- **Network:** required for `gh` (issue read/close/comment) and for `uv`'s first-run dependency
  resolution. All experiments in `findings/` ran offline against local checkouts.
- **Credentials:** an authenticated `gh` CLI against `dixson3/yoshiko-flow` with issue-write
  scope. No other secrets are needed; nothing in this plan touches a vault or a remote host.
- **Sibling-repo dependency (authoring-time only):** Issues **3.1 and 2.5** read
  `~/workspace/dixson3/d3-pxe` — 3.1 for its fixture corpus, 2.5 for plan-013/014's pre-fix
  replay text. This is a **capability the repo cannot assert**, so it is declared as an explicit
  gate (`Gate: Evidence corpus`) rather than assumed. Documented degraded fallbacks exist for
  each: 3.1 falls back to the 8 `yoshiko-flow`-only labeled plans at reduced statistical power;
  2.5 reconstructs its fixtures from the #112/#113 descriptions and marks them as
  reconstructions. Once 3.1 vendors the fixtures and 2.5 writes its own into `references/`, the
  dependency is discharged and **no CI run** reaches outside this repo.
- **Side effects:** local git commits on a plan branch; no pushes without explicit
  authorization; two outward-facing GitHub writes (close #109, comment on #113), both gated.
- **`bd`:** a healthy local beads DB. Local-only mode — no Dolt remote, no `bd dolt push`.
  Note the preflight advisory recorded at plan creation: a Dolt remote was configured under
  local-only and should be cleared with `yf doctor --repair --local-only --remove-remote`.

## Adjacent-concept glossary

| Term | Meaning |
| :-- | :-- |
| **deliverable class** | Per-plan label `standard` \| `ci-release` (REQ-PLAN-069a). `ci-release` means the plan's primary deliverable is CI/infra/release configuration whose behavior is observable only on a runner. |
| **`complete-gate`** | The Phase 6.4 hard gate that refuses to mark a `ci-release` plan `complete` without a `- validated:` attestation or an open deferred-validation bead. The consumer of the deliverable class, and why a false positive matters. |
| **conformance pass** | The first, mechanical review pass (`agents/reviewer.md`), verdict `PASS` \| `INCOMPLETE`. Presence/well-formedness only, no judgment. |
| **red-team pass** | The second, adversarial review pass (`agents/red-team.md`), verdict `APPROVE` \| `REVISE` \| `INVESTIGATE-MORE`. Owns the Phase 3 transition and the `reviews/pass-N.md` lifecycle. |
| **gate reachability** | Whether a capability gate's `Condition` can be satisfied given what the gate `Blocks`. A condition depending on evidence produced inside its own `Blocks` set is a cycle. The #112 defect. |
| **measurement vs inference** | A measurement is a command's output; an inference is a conclusion drawn from it. Only inferences can be wrong while looking rigorous. The #114 distinction. |
| **`TP` / `FP` / `TN` / `FN`** | Classifier scoring in `findings/exp-001`. `FN` (a genuine `ci-release` plan called `standard`) is the safety-critical direction, because it silently disables `complete-gate`. |
| **F1 / F2 / F3 / F4** | The four #108 classifier fixes: section-scoped scan, negative context guards, require-a-high-signal, and path-marker-only high confidence. |
| **F5** | A fifth fix added during review: strip fenced code blocks and inline code spans before matching, since a quoted token is not a claim. See plan.md Issue 3.4b. |
| **self-reference class** | A plan whose *subject* is releases, signing, or the deliverable class itself, and which therefore matches classifier keywords in ordinary prose. A structural limit no keyword rule can close; this plan is the demonstration (SC6). |

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
