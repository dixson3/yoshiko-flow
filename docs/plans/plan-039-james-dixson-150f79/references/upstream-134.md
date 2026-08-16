---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #134 — plan-039 execution tracking

**URL:** https://github.com/dixson3/yoshiko-flow/issues/134
**State:** CLOSED
**Disposition:** tracker (the coarse plan-level tracking issue for this plan; not a work item)

---

Coarse tracking issue for **plan-039** (one issue per plan-scale effort, per `AGENTS.md`).

- **Plan:** [`docs/plans/plan-039-james-dixson-150f79/`](https://github.com/dixson3/yoshiko-flow/tree/main/docs/plans/plan-039-james-dixson-150f79)
- **Status:** approved, awaiting `/yf-plan execute` — 5 epics, 23 issues, 4 gates, 14 success criteria
- **Epic:** poured at execute start (intake-at-execute model)

## Scope

Raise `yf-plan` review quality along three measured axes, plus one in-flight repair.

| Issue | Disposition | In this plan |
| :-- | :-- | :-- |
| #112 | include | Gate-reachability check in the red-team `Evaluate` section (REQ-AGENT-046) |
| #114 | include | Measurement-vs-inference split in `investigator.md`; premise check + falsification prompt in `red-team.md` (REQ-AGENT-048) |
| #113 | **partial** | **In:** the prose precondition cross-check (REQ-AGENT-047). **Out:** the DAG-walk engine and the `requires:` schema — declined on evidence, see below. Issue stays **open**, re-scoped |
| #108 | include | Five classifier fixes (F3 require-a-high-signal, F1 section-scoped scan, F2 negative guards, F5 strip code spans, F4 honest confidence) + a fixture-backed regression suite |
| #109 | supersede | Closed with non-reproduction evidence |
| #133 | exclude | Materially different surface (`yf-beads-upstream` mechanism swap) with four unresolved design decisions — gets its own plan |

## What investigation changed

Three experiments against primary artifacts, not restatements of the issues.

- **#108 is materially worse than reported.** It cites two false positives on Proxmox plans. Measured across a **53-plan corpus** (39 `yoshiko-flow` + 14 `d3-pxe`), the classifier suggests `ci-release` on **40**, and on **all 17** plans carrying an operator-confirmed class — **16 of them wrongly, with zero correct negatives ever recorded**. A bias control (plans 031–038, eight consecutive, all labeled) confirms the labeled set is not selected on the classifier's output. All five fixes preserve `FN=0` at every step.

  Demonstrated live at this plan's own intake: `classify-deliverable` returned `ci-release`, `confidence: high`, six signals, on a plan that ships only Python, markdown, and SPEC edits.

- **#113's expensive branch is not justified by its own evidence.** Reading the as-landed `d3-pxe` plan-013, every one of the five defects had a remedy expressible in today's schema — three `depends-on` edges, one capability gate, one issue split. No `requires:` key was needed for any of them; the missing artifact was the *edge*, not the *declaration*. Further, **2 of the 5 are not reachability failures at all** (one capability gap, one semantic conflict), which weakens the "mechanical, pass/fail, therefore conformance" framing. The `n=1` caveat stands. Hence `partial`: ship the prose cross-check, defer the engine, gather a second plan's evidence.

- **#109 does not reproduce.** 0/38 completed plans display the tag. The mechanism claim is **code-true** — `stale_approved` is computed and rendered with no status filter — but the path is unreachable because completion cannot perturb the fingerprint (status is a `**Field:**` line, the phase log lives in `log.md`, both outside the hashed region). Latent, not absent; residual exposure is a post-completion `--force`d content edit.

## Review history

Five red-team cycles. Pass 1 was a self-review (recorded as such); passes 2–5 were independent fresh-eyes agents. Passes 2, 3 and 4 returned REVISE; pass 5 APPROVE under a strict bar.

Each cycle found real, verified defects — **including defects introduced by the previous cycle's fixes**: a gate-reachability cycle in the plan's own gate (caught by the check this plan adds), a success criterion falsified twice by measurement, a harness expectation wrong by 4×, a `REQ` id matching no convention in its target file, and a verification command naming a script that does not exist in this repo.

Two structural lessons are encoded in the plan's risk table rather than left to be re-learned: **assert properties, not counts**, against a document that is its own measurement subject; and **verify an id or command against the real target file**, not its assumed shape.

## Not in scope

- #113's topological DAG-walk engine and `requires:` schema (deferred on evidence; issue stays open)
- Install parity — skills are `rust-embed`-baked into `yf` at `cargo build` time, so re-baking depends on a binary release cycle this plan does not touch. Filed as a follow-on bead.
- A pre-existing false-positive audit — declined explicitly: the population is currently empty (the one `ci-release`-labelled plan is a true positive), and re-labelling completed plans mutates approved, fingerprinted artifacts.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

