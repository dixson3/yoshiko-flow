---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #138 — plan-040 execution tracking

**URL:** https://github.com/dixson3/yoshiko-flow/issues/138
**State:** CLOSED
**Disposition:** tracker (the coarse plan-level tracking issue for this plan; not a work item)

---

Coarse tracking issue for **plan-040** (one per plan-scale effort, per `AGENTS.md`).

- **Plan:** [`docs/plans/plan-040-james-dixson-1cabe4/`](https://github.com/dixson3/yoshiko-flow/tree/main/docs/plans/plan-040-james-dixson-1cabe4)
- **Status:** approved, awaiting `/yf-plan execute` — 5 epics, 19 issues, 3 gates, 16 success criteria
- **Epic:** poured at execute start (intake-at-execute model)

## Scope

`bd` reads bead content, **`gh` writes issues**, `bd update --external-ref` records the mapping — across all three write paths (`push`, `hoist`, `land`). Plus the read and coverage sides of the same field.

| Side | Role of `external_ref` | Issue |
| :-- | :-- | :-- |
| write | gh-direct creates/updates, then records the mapping | #133 |
| read | `closable` groups beads by mapping to propose closures | #117 |
| coverage | `yf-plan` stamps the coarse tracker so it is mapped at all | #131 |

Dispositions: **#133 / #117 / #131** include · **#132** supersede (mooted, not fixed — the whole `--backend` surface is removed) · **#51 / #52 / #53 / #60 / #111** exclude, left open.

## Investigation changed the plan twice

**1. "~20 lines" understates it.** The bead→issue label mapping exists **nowhere in this repo** — no `type::`/`priority::` match in `upstream.py`, `SKILL.md` or `SPEC.md`. It lives entirely inside `bd`, known only from observed output. So it must be reverse-engineered and **specified for the first time** (SPEC-first), not copied.

**2. `closable` does not complete on this repo.** Zero output in 4 minutes, killed. `cmd_closable` spawns **one `bd show` subprocess per bead across 991 beads** to read a field `bd list --all --json` already returns — only 20 beads carry one. So #131 as filed would ship a stamp feeding a verb nobody can run; the N+1 fix is a prerequisite, not an optimization.

## The #117/#131 sequencing, resolved

`closable` already exists (REQ-BUP-052, recorded as *"#117 partial"*). The gap was never "build it":

- **#131's stamp is impossible where it is filed.** It says to stamp at `yf-plan` §4.5 — but §4.5 runs at INTAKE, §4.6 states *"No pour happened at intake"*, and §4.5's own text says the issue links the epic *"(once poured)"*. **There is no epic id there.** Relocated to §5.2a immediately after `record-epic`, made idempotent, and added to the §5.2b resume branch so a late or failed stamp is repaired on the next execute.
- **#117 closes fully** — the stamp discharges its coarse signal via the *existing* per-bead mechanism, so the per-plan `plan.md`-status reader #117 proposed is unnecessary. No `plans-root` coupling in either direction.

Five coarse trackers have gone stale and been closed by hand so far: #103, #95, #96, #98, #134.

## Decisions taken at scoping

| # | Decision |
| :-- | :-- |
| 1 | **GitHub only.** gitlab/jira are removed rather than left as broken stubs implying support — the coexistence condition #133 identifies as having produced #129 |
| 2 | **Reword `GR-BUP-001`, not delete.** A raw `bd sync` is *destructive*; a raw `gh issue create` is not. Rationale changes, invariant survives |
| 3 | **Locally-rendered preview + structural verification** replaces the network dry-run — "did each create return a URL", not parsing `Pushed N issues` |
| 4 | REQ-BUP-050's fail-closed *contract* is preserved; only its *evidence* changes |
| 5 | **Restrict-and-drop** for missing labels (revised at review — see below) |
| 6 | Fix `closable`'s N+1 **in this plan**, as a prerequisite to #131's stamp |

## Two defects found in the filed issues themselves

- **#133 misnames the guardrail.** `GR-BUP-002` is the *inline-auth* rule (REQ-BUP-031); the never-bare-sync invariant is **`GR-BUP-001`** (REQ-BUP-030). Issue 2.3 also repairs the same misreference sitting in `SPEC.md:165`.
- **#131's stamp location cannot work** — see above.

## A correction to this plan's own evidence

EXP-001 first reported `type::molecule` (42 beads), `type::chore` and `type::decision` as uncovered, and the missing-label policy was decided as *ensure-label-before-use* on that basis. Review found `CONTAINER_TYPES = {epic, molecule, gate}` and `candidate_filter` drop those from the push path entirely — the **real** gap is `chore` (2), `decision` (1) and one P4 bead, **3 of 991**. Decision 5 was reversed to restrict-and-drop, which needs no label-write token scope.

Every figure in the original finding was accurate; together they were misleading. Recorded in `findings/exp-001` under a correction banner rather than silently adjusted.

## Review

Three independent red-team cycles; passes 1–2 REVISE, pass 3 APPROVE. Cycle 1 found a **gate-reachability cycle in this plan's own first draft** — a gate blocking the issues that produce its own evidence — caught by the check plan-039 shipped two days earlier (#112). Also found: an unscoped third skill (`yf-beads-hygiene` delegates its hoist to `upstream.py`), six SPEC targets the implementation invalidates but Epic 2 did not cover, and two mutually-unsatisfiable success criteria.

## Not in scope

- Adding GitLab/Jira/Linear **support** (#51/#52/#53) — reframed as "add a backend to a gh-direct architecture", left open
- Label *semantics* in `enumerate`/`hoist` (#60)
- Beads alternatives (#111) — noted only that gh-direct narrows the `bd` surface a replacement must match

🤖 Generated with [Claude Code](https://claude.com/claude-code)

