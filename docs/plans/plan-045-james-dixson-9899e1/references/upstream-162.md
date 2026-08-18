---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #162 — plan-045-james-dixson-9899e1 execution tracking

- **URL:** https://github.com/dixson3/yoshiko-flow/issues/162
- **State:** OPEN
- **Labels:** (none)

---

Coarse tracking issue for **plan-045** (one per plan-scale effort, per AGENTS.md).

**Bundle:** [`docs/plans/plan-045-james-dixson-9899e1/`](docs/plans/plan-045-james-dixson-9899e1/) — landed on `main` at intake.
**Epic:** poured at `/yf-plan execute`; stamped here as `external_ref`.
**Status:** approved / awaiting execution. 7 epics, 46 issues, 7 findings, 4 review cycles.

## Objective

Make plan execution and review **autonomous by default**, with human gates **frontloaded**. Partially resolves #110, #145, #149; excludes #113.

## The thesis is two-sided

1. **Autonomy is the default; stopping is the exception that must be justified.**
2. **Autonomy is only safe where every claim of success is mechanically verified** — because every stop was also an *incidental checkpoint* at which a human saw real state. Removing stops removes the only verification the system had.

Without (2) the change makes the system *faster at being confidently wrong*. The evidence is a four-instance pattern: a `--repair` step that printed `ok` without checking its postcondition (what plan-044 fixed); a coordinator that closes every bead `--reason "Completed"` with **no failure branch at all**; a herdr push whose success return is acknowledgement of **injection, not submission**; and an agent that **narrated** its side-effects instead of verifying them. Three are machine-layer; the fourth is the agent-reporting layer, which no existing check covers.

## Diagnosed causes (all measured, all skill-text defects)

| Symptom | Cause |
| :-- | :-- |
| Review cycles need manual ack | Phase 3 grants autonomy to the conformance step, then ends the red-team step *"Present the verdict… to the operator."* "Address concerns" has **no subject** and is disambiguated toward the operator 4× more, plus normatively in REQ-AGENT-043 |
| Execution stops between epics | `"Wait for operator"` is the **only** explicit wait and is the loop's documented exit. "Report blocked gates" appears **5×**; "continue to the next bead" **0×** |
| Gates not frontloaded | Grep for `frontload\|up front\|as early\|gate placement` → **zero hits**. The only topological rule prescribes the opposite |
| herdr delegation stops turn-by-turn | The launch recipe carries no autonomy clause; the fix exists only as advisory prose read *after* the prompt is composed; `autonom` in yf-herdr SPEC.md → **no match** |

## Notable findings

- **exp-003 refuted the gate-sweep design as originally scoped.** Only 33% of live gates yield a runnable command; **59% are `Type: human`** where a green test is explicitly not consent — auto-resolving would have granted publish authorization on at least three historical gates. Most `auto` gates are *designed* to fail at t=0. Revised to structure-then-probe-only.
- **A standalone bug:** `bd ready` never returns gate beads, so the coordinator's gate step has **never fired**. Also `bd gate list --all --json` silently truncates at **50 of 113**, exit 0.
- **exp-005 verified the herdr push channel live** — env handoff, queued-not-lost delivery (proven mid-tool-call), `--append-system-prompt` at ~0ms cost. Two hazards found: `--wait --until idle` times out on success, and `agent_prompted` is not proof of delivery.
- **exp-007** is a live incident, not an experiment.

## Review

Four cycles: REVISE (15) → REVISE (9) → APPROVE (6) → APPROVE (4). **Three of four passes caught the author over-claiming in a resolutions table**, each found by an independent reviewer or the operator — never by the author. That is the plan's own thesis with its author as the recurring subject, and it is the direct evidence for the `detected_by` / `evidence` fields the retrospective schema now carries.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
