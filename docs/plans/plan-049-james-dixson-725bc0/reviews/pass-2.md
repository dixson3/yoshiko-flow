---
type: Review
okf_spec: OKF-PLAN
pass: 2
---
# Red-team pass 2 — plan-049-james-dixson-725bc0

## Verdict: REVISE

## Part A — pass-1 resolutions verified against the artifact

**C3, C4, C12 verified as real edges**, not prose: `1.1 ← 0.8`, `3.1 ← 0.8`, `3.3 ← 3.2a` (outside
the gate's Blocks set — the self-reference is genuinely gone), `2.1 ← 1.4`.
**C1/C2 changed machine behaviour:** `verify-reconcile` now reads `partial` and demands a **comment**
where `include` demanded a **close**. **C8** filled. **C15 did NOT land** (D8).

## Part B — mechanical verification

7 epics, 39 issues, 55 edges, 6 gates, 37 criteria, `unparsed: []`; zero cycles, zero dangling, zero
forward references, no duplicate SC ids. `0.1` the only unnamed issue. `okf.py check` OK; `audit`
all-pass; `markdown_lint` clean on all 20 bundle files; `doc_lint` PASS.

**Premises reproduced:** all five widening-target plans at `edges 0` (006: 9/0, 007: 13/0, 009: 19/0,
010: 38/0, 012: 26/0); corpus `unparsed[]` **exactly 81**; `report_only` **exactly 1340**; plan-008's
`Capability Gate: d2 present (see above)` extracts as `type=None, condition=None, test=None` — a live
instance of the vacuous gate Issue 3.2 catches. **D-9 reproduced:** with the bookkeeping marker
stripped, `W → E` at `review`, verdict FAIL.

**A correction in the plan's favour:** the plan-015 de-bold is **safer** than EXP-001 claimed — one
de-bold clears all three refusals, `B.4 → B.3` is already materialised, and EXP-001's "shifts every
later ordinal" does not apply to a letter-keyed plan.

## Concerns

| # | Sev | Concern |
| :-- | :-- | :-- |
| D1 | **high** | **SC19 cannot pass.** "plan-048's 112 stays 112" — measured today **124** review files, 123 excluding plan-049. No `--exclude` glob yields 112. **A stale plan-048-era literal pinned as a run-time assertion, in the epic whose entire purpose is stale literals**, against a preamble asserting Verification counts are derived |
| D2 | **high** | **SC12 demands nine where the honest number is eight.** plan-015's construct is one of the "nine non-relocations" — but Issue 3.3 **performs** it, SC11 counts it as one of two modified documents, SC35 names it in the diff. SC12 forecloses the honest answer with "a count below nine does NOT discharge it" |
| D3 | **high** | **The C1/C2 fix landed in the table and the triage doc but not in Issue 6.5**, which still reads `resolves-upstream: #140 (include), #149 (include)`. Caught by `verify-reconcile` and the gate Instructions — a halt-and-reopen, not silent — but it is the one-file/not-its-siblings pattern this review hunts |
| D4 | med | **SC23 contains a clause already true.** `files_checked ≥ 731` — measured **750 today**, stale within its authoring day. `unparsed[] ≤ 81` — **exactly 81 today**, so a whitespace-only write satisfies SC23, SC31 and SC11 together. The derived floor is **73** (81 − 7 + 2 − 3) |
| D5 | med | **The Reconcile Gate's Test does not test its Condition.** Condition speaks about beads; Test runs `plan_extract --strict`, which reads markdown and never touches `bd`. **Exit 0 today, with zero beads created.** Same class as pass-1's C3, surviving the pass that closed C3 |
| D6 | med | **The guard is loss-only; nothing bounds edge GROWTH.** Epic 2 is a deliberately edge-adding operation across 105 issues. **EXP-001 Rec 1 asked for exactly this** — having measured **+141 invented edges from 11 lines** and noted "DAG-invariance passes all 141 cleanly". Neither scheduled nor declined |
| D7 | med | **Epic 0's coverage claim is prose-true and machine-false** — `doc_lint.py:353` exempts **every** issue in the marked epic. Stripping the marker emits exactly one finding (`0.1`) at `W`. Nothing schedules its removal |
| D8 | low | **C15's claimed resolution did not land** — no mention of the `index.md`/`log.md` `files_checked: 0` vacuity anywhere in plan.md |
| D9 | low | **Six of eight upstream titles are still truncated**, including two `partial` rows. The mechanism was fixed for the two rows caught, not for the class |
| D10 | low | Gate-script paths ambiguous — issues say `scripts/…`, gate Tests say `docs/plans/…/scripts/…` |
| D11 | low | SC37 retains the C10 shape — "or a written decline exists" is discharged by any sentence |
| D12 | low | Issue 6.6's "otherwise record that nothing is" is dead text given five `deferred`/`partial` rows |
| D13 | low | EXP-003 Rec 5 and Rec 6 neither scheduled nor declined — Missing-7's fix addressed the instance, not the class |
| D14 | low | Issue 6.7's deploy hits AGENTS.md's consent gate without `--allow-permissions-write`; not stated |

## Gate Assessment

**Reachability and frontloading are clean.** All three capability gates draw evidence strictly
outside their `Blocks` set from declared ancestors, and each sits at the floor. **No cycles, no
self-references, no frontloading misses.** SC30's "exit 1 — not 2, not 127" is the correct falsifier.
**The one remaining gate defect is the Reconcile Gate** (D5) — the harness is now present and correct
for the three that matter; the fourth acquired a test that only looks like one.

## Upstream Assessment

**Both `partial` dispositions are honest, verified at the machine level.** `upstream-triage.md`
carries all eight with reasoning, so the second independent record exists. The residual is **D3** —
the bullet still says `(include)`. **One thing is still silently deferred and it is not upstream:**
EXP-001's upper-bound postcondition (D6).

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| D1 | high | SC19 rewritten as a **derived** assertion: running with `--exclude` on a plan reduces that plan's own contribution to zero, and the excluded count equals `total − own`. No era literal | `main-session` | resolved |
| D2 | high | SC12 corrected to **eight**, with plan-015 named as **in scope** (Issue 3.3 performs it); D-2a's 7+9 split annotated with the move | `main-session` | resolved |
| D3 | high | Issue 6.5's `resolves-upstream` corrected to `#140 (partial), #149 (partial)` | `main-session` | resolved |
| D4 | med | SC23 and SC31 rewritten against the **derived floor of 73**, with the derivation shown; the already-true `files_checked` clause replaced by a delta assertion | `main-session` | resolved |
| D5 | med | The Reconcile Gate's Test replaced with a `bd`-reading command that actually observes bead closure | `main-session` | resolved |
| D6 | med | **EXP-001 Rec 1 scheduled** as Issue 1.6: a paired upper-bound postcondition — no plan's edge count may grow by more than its recovered-declaration count — with SC38 and a mutant driving the +141 fan-out | `main-session` | resolved |
| D7 | med | Issue 0.9 added: strip the `epic-kind: bookkeeping` marker once 0.2 lands, leaving `0.1` as a single `W` finding; SC39 asserts the marker is gone at completion | `main-session` | resolved |
| D8 | low | The `index.md`/`log.md` vacuity recorded in the plan as a known instance of SC17's class | `main-session` | resolved |
| D9 | low | All eight upstream titles restored in full | `main-session` | resolved |
| D10 | low | Issues 0.7/0.8 qualified to the plan-dir path the gate Tests use | `main-session` | resolved |
| D11 | low | SC37's escape branch removed — a decline must name the replacement signal | `main-session` | resolved |
| D12 | low | Issue 6.6's dead branch removed | `main-session` | resolved |
| D13 | low | EXP-003 Rec 5 and Rec 6 **scheduled** as Issue 4.8 | `main-session` | resolved |
| D14 | low | Issue 6.7 states the consent gate and `--allow-permissions-write` | `main-session` | resolved |
