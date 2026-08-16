---
type: Reference
okf_spec: OKF-PLAN
---

# Upstream #148 — plan-043 execution tracking: Phase 6.4 close-time step contract (+ #136, #140 audit half)

**URL:** https://github.com/dixson3/yoshiko-flow/issues/148
**State:** OPEN
**Filed:** 2026-08-16 at INTAKE (Phase 4.5)
**Role:** the coarse plan tracker — not a defect report. Snapshot below; the issue is live.

---

Tracking issue for **plan-043** (`docs/plans/plan-043-james-dixson-a8afe8/`), approved and awaiting execution.

## Why one plan for three issues

#136, #140 and #145 each want to add a step to `yf-plan`'s Phase 6.4 close sequence, and each would otherwise invent its own answer to the same three questions: fail-loud or propose-only, in what order, and what halts completion. This plan **settles that contract once** and proves it by landing two payloads against it — one of each authority class.

## Scope

| | |
| :-- | :-- |
| **Epic 0** | The contract — amend `REQ-COMPLETE-001`, define the step convention, fix a stderr defect, add mechanical enforcement |
| **Epic 1** | **#136** — `verify-reconcile`, halting |
| **Epic 2** | **#140 (audit half only)** — close-time bundle conformance, advisory |
| **Epic 3** | Three adjacent defects investigation surfaced, behind their own SPEC issue |
| **Epic 4** | Docs, and posting the settled answers to #136 / #140 / #145 |

**Deliberately out of scope:** #140's nested-`index.md`/`log.md` enforcement and index drift model (a yoshiko-flow *extension* decision — OKF v0.2 §8/§9 say index/log **MAY** appear and §11 says consumers **MUST NOT** reject for their absence — plus a ~40-bundle backfill), and #145's `yf-retrospective` skill. Both plug into the settled contract later.

## What investigation established

Three experiments; findings are in the plan bundle under `findings/`.

- **#136's stated cause was wrong.** The reconciler was dispatched and parsed the Upstream Issues table correctly — it then *asserted success it had not performed*. Detailed correction will be posted to #136 by Epic 4.
- **Phase 6.4 has no extension seam**, and this repo explicitly forbids the harness-hook shape. The contract is therefore a documented script-verb convention enforced by SPEC + tests, not a dispatcher.
- **`REQ-COMPLETE-001` is count-bearing** — *"runs a fixed three-step order"* — so it blocks all three issues today. Amending it once is the plan's core leverage.
- **A live defect:** `complete-gate` writes its failure verdict to stderr while `SKILL.md` captures stdout, so the documented idiom prints nothing on failure. Measured.
- **Fail-loud vs propose-only was decided by measurement, not preference.** A blocking close-time audit would have halted **22% of completed plans**, including a proven false positive and one plan blocked by the close step's own writes — hence advisory for the audit, halting for reconcile verification.

## Review history

Four adversarial cycles: REVISE → REVISE → REVISE → APPROVE. Reports in `reviews/`. Two findings worth recording publicly:

- The plan initially carried a **delta-reporting** refinement whose measured benefit turned out to be 1 case in 10, against an approval-gated baseline that is empty by construction. Dropped, and deferred to #140's remaining half.
- Epic 0's deliverable is **prose** — and this plan's own central finding is that prose instructions get ignored. So its regression test now enumerates §6.4's steps **from `SKILL.md` source**, making a non-conformant future step fail CI. The plan's thesis applied to itself.

Execution has not started. This issue will be stamped onto the plan's epic as `external_ref` at pour.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

