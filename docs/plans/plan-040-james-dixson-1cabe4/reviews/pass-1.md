---
type: Review
okf_spec: OKF-PLAN
---
# Plan Red-Team: plan-040-james-dixson-1cabe4

**Pass:** 1 · **Date:** 2026-08-16

> **Independent pass** — fresh-eyes sub-agent, no access to the drafting conversation, instructed
> to apply the three `Evaluate` items plan-039 added (gate reachability, premise check,
> precondition cross-check) as the newest and least-exercised part of the contract.

## Verdict: REVISE

## Strengths

- **Every `[measured]` finding re-verified exactly** — 991 beads, the type/priority census, 20
  beads with `external_ref`, the label list, the absent mapping, and all EXP-002 code claims
  (`cmd_closable`:969, `external_for`:340, `load_universe_rows`:357, `BACKEND_AUTH`:586,
  `plan_push`:675). The docstring/call disagreement is real.
- **The `[measured]`/`[inferred]` discipline is genuine, not decorative** — the one load-bearing
  inference is flagged in the finding, the Approach, R1, and made the first execution issue behind
  its own gate, with an explicit "if it fails, Epic 2 simplifies" branch.
- **Gate reachability is clean on both capability gates**, and the plan *records* the v1 cycle it
  caught rather than silently fixing it.
- Folding the three sides of `external_ref` into one plan is justified — they genuinely are one
  field.

## Concerns

- **C1 — the plan rewords the wrong guardrail.** — severity: high

  `GR-BUP-001` is the never-bare-sync invariant (REQ-BUP-030); **`GR-BUP-002` is the
  token/inline-auth one** (REQ-BUP-031). The plan asserts the opposite in Motivation, decision 2,
  and Issue 2.3 — so an executor following 2.3 literally would rewrite the token-security
  guardrail. The error is inherited from #133, and `SPEC.md:165` carries the same slip.
  *Verified.*

- **C2 — Issue 4.3 stamps an epic that does not exist yet.** — severity: high

  `yf-plan` §4.5 runs at INTAKE; §4.6 states *"No pour happened at intake"* and §5.2 owns the
  pour. §4.5 itself says the issue links the plan folder and *"(once poured)"* its epic. So
  `bd update <epic> --external-ref` cannot run there — there is no epic id. #131's filed wording
  was taken at face value without checking the pour ordering. *Verified.*

- **C3 — SPEC-first is claimed but Epic 2 does not cover everything the implementation changes.** — severity: high

  Uncovered: **REQ-BUP-051** (mandates the inline-auth/dry-run-first behavior 3.2 deletes;
  SC4 requires `BACKEND_AUTH`→0), **REQ-BUP-031/GR-BUP-002** (the auth-model change is made by
  Issue **5.1**, a *documentation* issue in Epic 5 — behavior changing after implementation,
  the exact inversion AGENTS.md forbids), **`spec/safety.md`** and **`spec/backends.md`** (never
  named as edit targets, both written in `bd <backend>` terms), **REQ-BUP-041** (becomes dead),
  and **REQ-BUP-052** (Epic 4 changes `closable`'s contract with no amendment scheduled).

- **C4 — a third skill consumes the `hoist` path and is nowhere in scope.** — severity: high

  `yf-beads-hygiene` shells out to `upstream.py hoist --issues … --apply`
  (`beads_hygiene.py:551/579`), pins that contract in its own SPEC (14 mentions), and asserts the
  argv in its tests. The plan says it modifies "two skills". Its tests mock the runner, so a
  semantic divergence would not be caught. *Verified.*

- **C5 — the premise check is applied to one inference but not its twin.** — severity: medium

  Decision 5's rationale is "matching bd's apparent behavior… preserves current semantics". That
  rests on a **second** `[inferred]` claim — that bd creates labels on demand — corroborated only
  circumstantially. Issue 1.1 falsifies only the `gh` half. **What would falsify the bd half was
  never asked:** does `bd github push` of a `chore`/`decision` bead succeed today? If bd also
  fails, ensure-label-before-use is a **new feature**, not parity, and decision 5 loses its stated
  justification.

- **C6 — EXP-001's label-coverage gap is inflated ~5×.** — severity: medium

  `CONTAINER_TYPES = {epic, molecule, gate}` and `candidate_filter` drops them from the push
  candidate set. So the 42 `molecule` and 182 `epic` beads counted as needing labels are
  structurally excluded. The **real** uncovered population is `chore` (2), `decision` (1) and the
  single P4 bead — **3 beads out of 991**. That materially changes decision 5's cost/benefit
  versus restrict-and-drop. Exception worth stating: an explicit `hoist --issues <epic-id>`
  bypasses `candidate_filter`, so epics *can* reach the write path. *Verified.*

- **C7 — Issue 4.2's invariant is false and its test would fail on correct code.** — severity: medium

  `cmd_closable` first calls `upstream_enabled()` → `_config_get` → `bd config get`, a second
  `bd` subprocess the plan does not intend to remove. *Verified.*

- **C8 — the "Upstream write" gate `Test:` assumes a cwd the harness does not provide.** — severity: medium

  §6.1.5 states gate `Test:` commands run against the merged checkout at repo/worktree root, not
  the plan dir. The "run from `${plan_dir}`" annotation is a note to a human, not an instruction
  to the runner, so the gate fails closed for the wrong reason.

- **C9 — SC5's verification command does not exist.** — severity: medium

  `manifest_update.py` has no `--check` flag. The plan hedges "(or equivalent)", pushing the
  decision to execution on the criterion guarding R3 — the risk it rates high.

- **C10 — Issue 4.4's backfill has an unmet precondition.** — severity: medium

  "for each completed plan **whose tracker is known**" — known from where? Nothing produces or
  cites a plan→tracker map, and trackers are precisely the population carrying no bead mapping.

- **C11 — two success criteria do not discriminate.** — severity: medium

  SC10's first clause (`grep -q check_prescriptive_push CHANGE-VALIDATION.md`) **already passes
  today** — verified. SC2 says a REQ count "increases" with no recorded baseline (currently 35).

- **C12 — `upstream-triage.md` carries no dispositions.** — severity: low
- **C13 — `resolves-upstream` annotations missing for the three `include` issues.** — severity: low
- **C14 — R8 undercounts the plan's size** (says 15 issues; actual 16). — severity: low
- **C15 — R7 admits a dependency that exists only for review coherence, then keeps it.** — severity: low

  `4.1 depends-on 3.3` makes all of Epic 4 — the independently-valuable perf fix and the #131
  stamp — hostage to the largest, riskiest epic in an already near-linear 16-node chain.

## Missing

- **A migration story for the 20 already-mapped beads** — nothing verifies their `external_ref`
  values are in a form `gh issue edit` accepts, or what happens to a stale/deleted-issue ref.
  SC6 tests the fixture, not the live population.
- **What happens to an existing `--backend gitlab` caller** — deleting the flag is a hard argparse
  error. No deprecation window or error-message deliverable.
- **A `bd` version pin** — the plan still depends on `bd update --external-ref` and on
  `bd list --all --json` returning `external_ref`. Neither is spec'd as a version-pinned
  assumption; context.md records 1.1.2 without saying it is a floor.
- **Nothing checks the installed-vs-repo skill divergence** that context.md itself flags, though
  Epic 4 *runs* `closable` on the live repo as SC8/SC9 evidence.

## Gate Assessment

**Start Gate** — well-formed. **Scratch write** — reachable; `Blocks: 1.1`, condition is pure
operator authorization, test depends on nothing 1.1 produces. Gap: the test verifies *read*
access, not that write was authorized — acceptable for a human gate, but should be labeled so an
automated resolver does not treat a green test as consent. **Upstream write** — reachable and
correctly repositioned from the v1 cycle; `Blocks: {5.2b}` with evidence from 5.2a and 4.2, both
outside the Blocks set. Two mechanical defects: the cwd assumption (C8), and the Instructions
credit `closable-after.md` to 4.4 when 4.2 writes it. **Reconcile Gate** — correct type, but with
C13's missing annotations it has little to act on.

## Upstream Assessment

#133/#117/#131 are genuinely one mechanism and the Resolved By mapping is specific; #117's
partial-discharge reasoning correctly matches REQ-BUP-052's recorded "Known gap". #132 supersede
is justified and correctly the only close, with draft-then-publish enforced. #60 and #111
excludes are sound. **But the plan overstates the reduction it makes:** REQ-BUP-040, GR-BUP-004
and `spec/backends.md` REQ-BE-001 *already* say GitLab/Jira are unverified config-only stubs — so
R5's "reduction in stated capability" is softer than framed. What is removed is a flag and a
table row, not support. Weakness: the empty `upstream-triage.md` (C12) and missing
`resolves-upstream` lines (C13).

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | Wrong guardrail (GR-BUP-002 vs 001) | high | Verified at source: `SPEC.md:269` GR-BUP-001 = never-bare-sync (REQ-BUP-030); `:273` GR-BUP-002 = inline-auth (REQ-BUP-031). Corrected in Motivation, decision 2, and Issue 2.3, with a note that #133 and `SPEC.md:165` carry the same slip and 2.3 fixes the in-repo one | resolved |
| C2 | 4.3 stamps an epic that does not exist at §4.5 | high | Verified: §4.5 says "(once poured)", §4.6 says "No pour happened at intake". **Stamp relocated to §5.2a immediately after `record-epic`**, made idempotent, and added to the §5.2b resume branch so a late/failed stamp is repaired on the next execute. Skips with a note where no tracker exists rather than failing the pour | resolved |
| C3 | Epic 2 misses REQ-BUP-051/031/041/052, spec/safety.md, spec/backends.md | high | **New Issues 2.6 and 2.7.** 2.6 amends REQ-BUP-051, REQ-BUP-031/GR-BUP-002 (the auth-model change **moved out of Issue 5.1**, where the v1 draft had a behavior change landing in a docs pass), REQ-BUP-041, REQ-BUP-052. 2.7 covers `spec/safety.md` and `spec/backends.md`. 3.1 re-pointed from 2.5 to 2.7 | resolved |
| C4 | yf-beads-hygiene consumes hoist, unscoped | high | Verified: `beads_hygiene.py:551/579` delegates to `upstream.py hoist`, 14 SPEC references, tests mock the runner. **New Issue 3.3** re-validates the contract end to end against the real `hoist` and updates that skill's SPEC/SKILL wording. Added to R8's blast radius (now three skills) | resolved |
| C5 | bd-creates-labels premise never falsified | medium | Issue 1.1 extended to falsify **both halves** on the same authorized scratch write, with a 4-outcome table stating the consequence of each — including "yes/yes → restrict-and-drop is a deliberate divergence, say so" and "untestable → record as untested rather than assuming" | resolved |
| C6 | Label gap inflated ~5× by CONTAINER_TYPES | medium | Verified: `candidate_filter` drops `{epic, molecule, gate}`. Real gap is **3 of 991**, not ~45. Correction banner added to `findings/exp-001`; **the operator re-decided decision 5 from ensure-label-before-use to restrict-and-drop** on the corrected figure. R6 rewritten accordingly, and the `hoist --issues <epic-id>` bypass stated explicitly rather than left implicit | resolved |
| C7 | 4.2's one-invocation invariant is false | medium | Verified: `upstream_enabled()` → `_config_get` → `bd config get`. Restated as "one `bd list` invocation and **zero** per-bead `bd show`", in Issue 4.2 and SC8 | resolved |
| C8 | Gate Test assumes plan-dir cwd | medium | Test rewritten repo-root-relative with the §6.1.5 rationale inline. Also corrected the Instructions' provenance: `closable-after.md` is written by **4.2**, not 4.4 | resolved |
| C9 | SC5 names a nonexistent `--check` flag | medium | Pinned to `manifest_update.py --dry-run` reporting no pending change, plus the preflight `rule.outcome: ok` check. The "(or equivalent)" hedge removed | resolved |
| C10 | 4.4's plan→tracker map has no producer | medium | 4.4 gains an explicit derivation step (`gh issue list --search 'execution tracking in:title'` cross-referenced against `**Epic:**` fields) written to `references/tracker-backfill-map.md`, an expected population (~40 completed plans, ≥5 already closed), and a rule that an unidentifiable tracker is **recorded as such**, not skipped | resolved |
| C11 | SC10 already passes; SC2 has no baseline | medium | SC10's already-true clause dropped; now asserts the new test id in **both** tiers. SC2 pinned to "≥ 36 (baseline 35, measured at plan time)" | resolved |
| C12 | upstream-triage.md dispositions blank | low | All nine dispositions and notes back-filled to match plan.md's table | resolved |
| C13 | Missing resolves-upstream annotations | low | Added: #133 on 3.3/3.4, #131 on 4.3, #117 on 4.4 (#132 was already on 5.2b) | resolved |
| C14 | R8 undercounts issue count | low | R8 now reads 19 issues across three skills, and records that the plan grew at review (C3, C4, C15) | resolved |
| C15 | 4.1→3.3 edge blocks Epic 4 unnecessarily | low | **Edge cut** per operator decision. 4.1 now depends on 2.7, so Epics 3 and 4 fork from the SPEC work and rejoin at 5.1. Verified acyclic: 19 issues, no dangling deps, no cycles. R7 rewritten as resolved | resolved |
| — | Missing: 20 mapped beads, `--backend` caller, bd version floor, installed-vs-repo copy | — | Four new criteria: **SC13** (live-population `external_ref` check incl. stale-ref fail-closed), **SC14** (removed flag fails informatively), **SC15** (bd version floor recorded in SPEC + context.md), **SC16** (Epic 4's evidence names which copy of the skill produced it) | resolved |
| — | Upstream: R5 overstates the capability reduction | — | Verified — REQ-BUP-040, GR-BUP-004 and REQ-BE-001 already call GitLab/Jira unverified stubs. R5 downgraded to **low** and reworded as "deleting a stub surface, not withdrawing support"; 2.7 carries the same wording | resolved |
| — | Gate: scratch-write Test proves read, not consent | — | Test relabeled **smoke check only**, with "never treat a green test here as consent" inline | resolved |

**Final status:** all 15 concerns plus the Missing and Upstream items resolved. Pass 1 frozen.

**Note on process.** C6 changed an operator decision: the original ensure-label-before-use choice
was made on my EXP-001 figure, which overstated the affected population ~5× by counting bead types
`candidate_filter` never pushes. The corrected figure was taken back to the operator rather than
quietly adjusted. That is the #114 premise class — a finding that was individually accurate and
collectively misleading.
