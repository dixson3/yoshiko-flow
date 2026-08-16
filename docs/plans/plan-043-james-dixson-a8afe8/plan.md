---
type: Plan
okf_spec: OKF-PLAN
id: plan-043-james-dixson-a8afe8
author: james-dixson
created: '2026-08-16'
status: approved
deliverable_class: standard
fingerprint: b5298aa068028c22cbbf5e40907ff05f2584778af2f2d52b65da1f7752320ff3
---
# Plan: Settle the Phase 6.4 close-time hook contract once, and land the payloads queued behind it (#136 reconcile verification, #140 bundle conformance at close, #145 escape capture)

**ID:** plan-043-james-dixson-a8afe8
**Author:** james-dixson
**Created:** 2026-08-16
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** b5298aa068028c22cbbf5e40907ff05f2584778af2f2d52b65da1f7752320ff3

## Objective

Settle the **Phase 6.4 close-time hook contract once** — ordering, fail-loud vs
propose-only, what halts completion — and prove it by landing the two cheapest payloads
against it.

Phase 6.4 today runs a fixed order (REQ-COMPLETE-001): **cascade-close → complete-gate →
set complete**. Both existing steps fail-loud. Three separate issues independently want to
add a step here, and each would otherwise invent its own answer to the same three
questions.

**In this plan:**

1. **The contract** — a single, documented extension point with settled semantics.
2. **#136** — verify each `include`/`partial` upstream row actually reached its end state.
3. **#140 (close-time audit half only)** — run the **existing** bundle conformance audit at
   close, where it can finally see execution-authored artifacts.

**Deliberately not in this plan** (they plug into the settled contract later): #140's
nested-`index.md`/`log.md` enforcement and index drift/regeneration model, and #145's
`yf-retrospective` skill.

## Motivation

**A completion signal that is green while a documented step silently did not run is worse
than a loud failure.** That sentence is from #136, and it is the whole plan.

Concretely (#136): plan-039 reported `status: complete`, `open_work_remaining: 0`, a clean
cascade, merged and pushed — while **three of its four `include` upstream issues were never
touched**. #108, #112 and #114 were all mapped, all carried dispositions and a populated
`Resolved By` column, all genuinely resolved by the executed work, and all still `OPEN` with
zero comments mentioning plan-039. Reconciliation ran, handled `supersede` and `partial`
correctly, then silently did nothing for the third disposition. Nothing prompted anyone to
look.

Concretely (#140): `plan_manager.py audit` is a **PLAN-phase gate**. It runs at Phase 3 and
in `/yf-plan capture` — both *before* INTAKE. But `references/` and `reviews/` are largely
authored during **EXECUTE**: replay fixtures, drafted comments, backfill maps, residuals
records. Those files are created *after* the only gate that would check them, and no later
gate re-runs it. Re-auditing the corpus today, **9 of 40 bundles fail** — and the
execution-authored class are all `status: complete` with closed trackers.

Both defects share one shape: **the close step is where the evidence is complete, and it is
the one place nothing looks.** The cascade already fail-louds on an unclosed child; the
reconcile step and the conformance audit have no equivalent.

**This plan's own provenance is an instance of the pattern.** plan-041 completed an hour
before this plan was scoped, and its execution surfaced three process deviations — a
tracking issue auto-closed at intake by a `close #137` merge-commit keyword before any work
ran, a `--no-ff` merge flattened by an automatic `pull --rebase`, and an unrelated
directory swept into a commit by a `bd`-side hook. None was captured by any mechanism; all
three exist only because a human read the subordinate's report. That is #145's payload, and
it is why the hook is worth building even before #145 is planned.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#136](https://github.com/dixson3/yoshiko-flow/issues/136) | reconcile silently skipped three mapped `include` upstream issues while the plan reported complete | include | Fully resolved by Epic 1's `verify-reconcile`. **E1 refuted the issue's own three hypotheses** — the cause was a false success assertion, not a silent error, filtering, or non-dispatch; and `reconciler.md` step 4 already prescribed the verification that was skipped. Issue 4.3 posts the correction. | Issue 1.1 |
| [#140](https://github.com/dixson3/yoshiko-flow/issues/140) | enforce OKF structure below the bundle root, and adopt an index drift/regeneration model | partial | **Only the close-time-audit half.** The nested-`index.md`/`log.md` enforcement and drift model are a yoshiko-flow *extension decision* (OKF v0.2 §8/§9 say index/log **MAY** appear; §11 says consumers **MUST NOT** reject for their absence), carry a ~40-bundle backfill, and are deferred. E3 also corrects the issue's framing: 9 of 10 failures are execution-authored, **not** legacy debt. Issue 4.2 posts both points; the issue stays **OPEN**. | Issue 2.1 |
| [#145](https://github.com/dixson3/yoshiko-flow/issues/145) | New skill: yf-retrospective — measure escape rate and enforce a fix+prevention contract | exclude | Not built here. But #145's own comment identifies it as the third payload queued behind this contract, so Issue 4.4 records that the contract exists and names its two authority classes — `yf-retrospective` inherits rather than re-derives it. | — |
| [#141](https://github.com/dixson3/yoshiko-flow/issues/141) | yf-okf: reconcile OKF-BASELINE from v0.1 to OKF v0.2 | exclude | Surfaced by the triage keyword scan. Independent OKF spec-version work with its own breaking changes; this plan touches no OKF baseline. | — |
| [#128](https://github.com/dixson3/yoshiko-flow/issues/128) | yf-okf skill: add reference/link to the Google OKF spec | exclude | Surfaced by triage. **Explicitly superseded by #141** and should simply be closed — unrelated to this plan, noted only so the triage scan's hit is accounted for. | — |

## Scope

**In scope**

- The Phase 6.4 hook contract: where steps attach, in what order, and the fail-loud /
  propose-only decision per step. Documented in `SPEC.md` (SPEC-first) and `yf-plan`
  `SKILL.md` §6.4.
- **#136**: post-reconcile verification of every non-`exclude` Upstream Issues row.
- **#140, close-time audit half only**: run the existing `plan_manager.py audit` at close.
- Whatever `SPEC.md` requirements the above create or amend (`REQ-COMPLETE-001` governs the
  6.4 order today).

**Out of scope**

- **#140's nested `index.md`/`log.md` enforcement and drift/regeneration model.** #140 is
  explicit that this is a **yoshiko-flow extension decision, not a conformance fix** — OKF
  v0.2 §8/§9 say index and log files **MAY** appear, and §11 says consumers **MUST NOT**
  reject a bundle for missing `index.md`. It also carries a ~40-bundle backfill and an
  index-generation-timing question. Separate plan.
- **#145's `yf-retrospective` skill.** A whole new skill whose hardest part — defining
  "escape", and separating **review-escapes** (the check existed and missed) from
  **process-escapes** (no check existed) — is a design problem, not a hook problem.
- **Backfilling the 9 currently-failing bundles.** This plan stops the bleeding forward; the
  existing corpus is a migration task.
- Re-litigating the existing cascade-close and complete-gate steps.

## Investigation Findings

### E1 — Why reconcile skipped three rows ([finding](findings/exp-001-reconcile-skip-cause.md))

**Verdict: none of #136's three hypotheses.** A fourth mechanism — the reconciler **was**
dispatched, **did** parse the table perfectly (correct dispositions and `Resolved By` bead ids
for all five rows), then **reported success without performing the `gh` writes**. There was no
error to swallow; there was a **false success assertion**.

The tell is linguistic: for the two rows it acted on the close reason describes an *upstream
action* ("commented and left OPEN", "closed with evidence"); for the three it skipped it
describes *code that shipped* ("2.2/REQ-AGENT-046 shipped"). Both read as done.

Timestamps confirm it: at the moment the reconcile bead closed asserting all six handled,
**zero `gh` writes had touched those three issues**. They were closed in a 5-second batch
**15 hours later** — the operator's manual repair, 5 minutes before #136 was filed.

**Why #109/#113 succeeded:** they were never left to the reconciler. Both had dedicated
Epic-5 beads with drafted artifacts on disk, *and* plan-039's SC9 asserted their end state
with `gh issue view -q .state`. The three `include` rows had none of that.

**The finding that shapes the payload:** `agents/reconciler.md:49-53` **already contains** a
*"### 4 — Verify updates"* step with `gh issue view <number> --json state,comments`. **The
verification prose already exists and was skipped in the same breath as step 3.** Adding a
sixth instruction to a five-instruction list that was partially ignored is a null change.

Also: reconcile has **no code path** (`grep reconcil plan_manager.py` → one docstring hit);
`complete-gate` is a strict no-op for `standard` plans so cannot absorb the check; and a
state-only assertion is insufficient — it would pass #108 *today*, closed late by a human.

### E2 — The Phase 6.4 surface ([finding](findings/exp-002-phase64-surface.md))

- **There is no seam.** 6.4 is prose in `SKILL.md` executed by an LLM calling four flat CLI
  verbs. No orchestrator, registry, or step table. **"Hook" is the wrong word and the repo
  says so** — the only two non-fixture `hook` matches in the skill are *prohibitions*
  (*"a portable, documented script-verb step — never a harness hook or scheduler"*).
- **LIVE DEFECT, measured.** `close_cascade.py` writes JSON to stdout on both paths;
  `complete-gate` writes its **fail** verdict to **stderr**. `SKILL.md` uses the same
  `GATE=$(…)` capture idiom for both, so on the failing path `echo "$GATE"` prints **nothing**
  (`GATE_RC=1`, capture length 0).
- **`REQ-COMPLETE-001` is count-bearing** — *"fixed three-step order"* plus a positional
  Verification clause. A fourth step cannot be added while leaving it true. **Amending it once
  is the highest-leverage edit in this plan.**
- Only 2 of 6 things §6.4 runs are gates; `classify-deliverable`, `set-deliverable-class` and
  `bd close ${RECONCILE_STEP}` are unguarded. Cascade exits **0** on a not-found root, so a
  typo'd `${EPIC}` passes silently.
- **`${RECONCILE_STEP}` is unset on the resume path** (set only at `SKILL.md:815`; §5.2b never
  pours), so `bd close ${RECONCILE_STEP}` degrades to `bd close --reason …` and fails
  silently. *Inferred from grep + absent re-derivation; not run live.*
- **`update-status complete` is not idempotent** — appends a duplicate `- complete:` bullet
  per run, and those bullets are what the parsers read.
- **Cost of adding one gated step, measured from plan-030: 10 files, 760 insertions.** The
  expense is the SPEC surface, not the code — which is the duplication this plan amortizes.

### E3 — Close-time audit authority ([finding](findings/exp-003-close-time-audit.md))

- **41 completed bundles: 31 pass, 10 fail (24.4%).** Under the checks in force at each plan's
  own close date: **9 of 41 (22.0%) would have been blocked.**
- **9 of 10 failures are class A** (execution/close-authored, structurally invisible to the
  Phase-3 gate) — **not legacy debt.** The OKF-legacy downgrade already absorbs that: 29 of 43
  bundles emit only `warn` across the OKF surface. This validates #140's claim while
  correcting its framing.
- **plan-029's failure is a proven false positive** — the Windows-drive-letter regex
  `[A-Za-z]:\` matched `s:` + `\` inside `tags:
` in a quoted fixture body.
  **plan-030's failure is caused by the close step's own `log.md` write.**
- **The audit is safe at close:** zero mutations (whole-corpus checksum over 43 runs),
  idempotent, no status-conditional logic, **≤ 0.2 s**. Cost is not the variable — verdict
  authority is.
- **Two ordering constraints**: the audit must run **before** the close step's `log.md`/status
  writes (plan-030's mechanism, plus the `dual-write:status` window); and grandfathering keys
  on `log.md`'s `scoping:` entries, so a close-time `log.md` write that drops them silently
  promotes warns to fails.
- **The delta refinement:** recording the Phase-3 verdict and reporting only findings *new
  since approval* catches **all 9 class-A cases** while plan-001's class-B case correctly stays
  silent.
- Recorded for #140's other half (out of scope): **nested `index.md`/`log.md` are silently
  exempted at any depth** — the reserved-file filter matches by bare name, not root position.
  Confirmed by synthetic fixture.

## Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D1 | **The deliverable is a documented script-verb step convention, not a "hook".** | E2: no seam exists, and `SKILL.md:1220` / `SPEC.md:197` explicitly forbid the harness-hook shape. Naming it a hook would invite exactly the mechanism the repo bans. |
| D2 | **Amend `REQ-COMPLETE-001` from a fixed three-step order to an extensible ordered gate chain.** | It is count-bearing and positional, so it blocks #136, #140 and #145 *today*. One amendment unblocks all three — the plan's core leverage. |
| D3 | **One verdict envelope: JSON to STDOUT on every path; non-zero exit halts; `{passed, reason, remediation}`.** Fix `complete-gate` to match. | E2 measured the stderr-on-fail split as a live defect that silently empties the documented capture idiom. `spec/cli.md:73` already *claims* the two mirror each other, so this makes a false statement true. |
| D4 | **#136's `verify-reconcile` is FAIL-LOUD.** | An unreconciled upstream issue is an **actionable state failure** — fixed by running a `gh` command, the same kind as closing a blocking bead. Distinct from an audit failure, which needs prose authoring. E1 showed the silent-success path is exactly what let plan-039 report complete. |
| D5 | **#140's audit step is PROPOSE-ONLY, reporting the ABSOLUTE finding set.** ~~delta since approval~~ — **the delta is dropped (pass-1 C5).** | E3: fail-loud would have blocked 22% of completed plans, including a proven false positive and one self-inflicted by the close step — so propose-only stands. But the delta does **not**: the Phase-3 audit is a *precondition of approval*, so the stored baseline is an **empty fail set by construction** on every non-`--force` approval, making the delta equal the absolute set in the normal path. Its entire measured benefit was suppressing plan-001 — 1 of 10, a legacy case. And a propose-only step cannot block, so noise costs nothing. Recorded as a follow-up on the deferred #140 half. |
| D9 *(added at pass-1; rows D9/D10 follow D5 because they supersede it and D1–D3, not because D6–D8 are newer)* | **The two step classes are defined on the HALTING axis alone** — `halting` / `advisory` — with **remediation-kind** (command / prose / adjudication) recorded as a *separate* documented attribute. | pass-1 C2: the original discriminator ("actionable state failure" vs "requires prose authoring") **conflated two independent axes** and could not classify #145 — escape capture has *authoring* remediation but is meant to *enforce*. Splitting the axes lets a step be halting-with-authoring-remediation, which is exactly #145's shape. Issue 4.4 posts **this answer**, not merely "a contract exists". |
| D10 | **The contract gets MECHANICAL TEETH**: Issue 0.3's regression test **enumerates every script invocation in §6.4 by parsing `SKILL.md`**, requiring each to be envelope-capturing or explicitly exempt, rather than hardcoding the known steps. *(The original capture-only key was superseded at pass-2 review, C18 — it was circular: it could see only steps already shaped like conformant ones.)* | pass-1 Missing-A, the review's sharpest structural point. Epic 0's deliverable is **prose** — and this plan's own central finding (E1) is that prose instructions get ignored: `reconciler.md` step 4 already prescribed the verification that was skipped. A contract whose only enforcement is "a future author will read it" reproduces the defect it exists to fix. Source-enumeration makes a non-conformant new step fail CI. **This is the plan's own thesis applied to itself.** |
| D6 | **`verify-reconcile` must assert a `<plan-id>` mention, not just issue state.** | E1: state alone would pass #108 today — closed by a human 15 h late — and would pass any issue closed for an unrelated reason. |
| D7 | **The audit step runs BEFORE the close step's own `log.md`/status writes.** | E3's two ordering constraints. Otherwise it judges artifacts the close step created microseconds earlier (plan-030's exact failure) and can hit the `dual-write:status` window. |
| D8 | **No new step may append to `log.md` unguarded.** | E2: `update-status complete` already double-appends on the documented "re-run §6.4" recovery, and those bullets drive the parsers. A new step should be a pure read or dedupe its own write. |

## Experiments

| ID | Question | Why it blocks the plan |
| :-- | :-- | :-- |
| E1 | **Why did reconcile skip three `include` rows?** #136 says explicitly: *"Worth determining whether the reconciler errored silently, filtered these rows out, or was never dispatched for them — the fix differs."* Read `agents/reconciler.md` and the plan-039 artifacts and determine which. | The #136 payload's shape depends entirely on this. A verification step catches a silent skip; it does **not** fix a reconciler that was never dispatched. |
| E2 | **What is the actual Phase 6.4 implementation surface?** Where do `close_cascade.py` and `complete-gate` attach, how does SKILL.md sequence them, what does each return, and how would a third and fourth step compose? Is there an existing extension seam or is 6.4 a hardcoded sequence in prose? | The contract is the deliverable. Designing it without knowing whether 6.4 is a script, a prose sequence, or both would produce a contract that cannot be implemented. |
| E3 | **What breaks if the existing audit runs at close?** Re-audit all bundles: how many fail, in which classes (execution-authored vs pre-OKF legacy), and would a close-time audit have blocked plans that legitimately completed? Does the audit mutate anything, and is it safe to run twice? | Determines whether the #140 payload is fail-loud or propose-only — the single most consequential decision in the contract, and the one three issues are waiting on. |

## Approach

**SPEC-first, contract-before-payloads.** Epic 0 amends `REQ-COMPLETE-001` and defines the
step convention. Epic 1 lands the fail-loud payload (#136), Epic 2 the propose-only payload
(#140-audit-half). Landing **one of each authority class** is deliberate: it proves the
convention describes both, rather than being a fail-loud contract with a propose-only
exception bolted on.

**Why the contract is convention, not code (D1).** E2 established there is no seam and that
the repo forbids the harness-hook shape. So "the contract" is: an amended `REQ-COMPLETE-001`
describing an ordered gate chain, one `REQ-COMPLETE-00N` per step, and a shared verdict
envelope every step honours. The convention's teeth are the SPEC + tests, not a dispatcher.

**Ordering within §6.4** (D7, and E3's constraints):

```
6.4  audit (ADVISORY, absolute)       <- FIRST: above the dual-write, not merely
                                         above the log.md write
     classify-deliverable             <- existing, unguarded
     set-deliverable-class            <- existing; a plan.md DUAL-WRITE
     bd close ${RECONCILE_STEP}
     verify-reconcile (HALTING)       <- after 6.3, before destructive steps
     cascade-close    (HALTING)
     complete-gate    (HALTING)
     set complete                     <- the only status writer
```

**The audit's position is above `set-deliverable-class`, not merely above the `log.md`
write** (pass-1 C11). `set-deliverable-class` is a plan.md dual-write — the exact class of
write D7 exists to precede, and the source of the `dual-write:status` window E3 flags. An
implementer who places the audit at the top of the existing bash block would land *below* it.

`verify-reconcile` sits after the reconcile bead closes and before the cascade, per E2's
insertion-point analysis — the only point where 6.3 is done and nothing destructive has run.

## Epics

### Epic 0: The contract (SPEC-first)

- Issue 0.1: Amend `REQ-COMPLETE-001` from a *"fixed three-step order"* to an **extensible
  ordered gate chain**, naming the ordering constraints rather than a step count. Update its
  positional `Verification:` clause, which currently names the exact slot. **Also fix
  `SKILL.md:1066`** — *"The close step runs a fixed order (REQ-COMPLETE-001): cascade-close →
  complete-gate → set complete"* — a second count-bearing sentence that becomes false the
  moment either payload lands, and which belongs to the contract, not to the wiring issues
  (pass-1 C12).
- Issue 0.2: Add `REQ-COMPLETE-00N` defining the **step convention**:
  - **Verdict JSON to stdout on EVERY path**, including failure.
  - **Tri-state verdict** `verdict: pass | fail | inconclusive`, with `passed` retained as a
    derived compatibility key (pass-1 C1 — a boolean cannot express the INCONCLUSIVE state R1
    requires and SC4 tests). Halting rule stated per state: **`fail` halts; `inconclusive`
    NEVER halts and always reports.**
  - **Two classes on the HALTING axis only** — `halting` / `advisory` (D9).
  - **Remediation-kind as a separate attribute** — `command | prose | adjudication` — with the
    legal combinations stated, explicitly including **halting + prose-remediation** (#145's
    shape).
  - A **bounded timeout** requirement for any step making network calls, so a hung `gh`
    cannot hang land-the-plane (pass-1 Missing-C).
  - depends-on: 0.1
- Issue 0.3: Fix `complete-gate` to emit its fail verdict on **stdout** (D3) — note the
  `"plan.md not found"` path is `err=True` too — and correct `spec/cli.md` REQ-CLI-016 /
  `SPEC.md:205`, which already claim it mirrors `close_cascade.py`.

  **The regression test must ENUMERATE §6.4's steps by parsing `SKILL.md`** (D10), not
  hardcode the known steps, and assert each captures a **non-empty, envelope-conformant verdict
  on its failing path**.

  **Enumerate EVERY script invocation in the §6.4 block, not only the `X=$(… --json)`
  captures** (pass-2). Capture-only enumeration is circular: it can see only steps already
  shaped like conformant ones, while the likeliest non-conformance — an author who adds a step
  *without* the capture idiom, which takes less effort, not more — is invisible and passes CI.
  Today's block contains only two captures alongside four non-capturing invocations. Each
  invocation must therefore be **either envelope-capturing or on an explicit named exempt
  list** in the test (`classify-deliverable`, `set-deliverable-class`, `update-status`). This
  converts the teeth from *"checks conformant steps"* to *"detects added steps"*.

  **Scope the enumerator explicitly** (pass-3 C24/C25): the block runs from the `### 6.4`
  heading to the next `###`. `worktree teardown` is **not** in it — that call lives in §6.2, so
  it is not on the exempt list. And `set-deliverable-class` currently appears only inside a
  `#` **comment**, not as an executed line, so the test must state its comment-handling rule or
  it will either miss it or see a phantom step. It is the contract's only mechanical enforcement; without it Epic 0 is documentation.
  - depends-on: 0.2
- Issue 0.4: Root `SPEC.md` amendment-log entry (mandatory per `AGENTS.md`). *"First" means
  first in the SPEC document's amendment log, not first in execution order* — it records 0.1's
  amendment and therefore follows it (pass-1 C15).
  - depends-on: 0.1

### Epic 1: #136 — `verify-reconcile` (fail-loud)

- Issue 1.1: Add `plan_manager.py verify-reconcile <plan_dir>` — parse the Upstream Issues
  table independently, query `gh issue view --json state,comments,stateReason` per
  **non-`exclude`** row, assert per disposition: `include` → `CLOSED` **and** a comment
  mentioning `<plan-id>`; `supersede` → `CLOSED` + `stateReason == NOT_PLANNED`; `partial` →
  `OPEN` **and** a `<plan-id>` mention (D6). Honour the D3 envelope.

  **Per-row verdicts (pass-1 C9).** The envelope must carry
  `rows: [{issue, disposition, verdict, detail}]`, with the top-level verdict an aggregate
  whose rule is stated: **any row `fail` → `fail` (halt), even if other rows are
  `inconclusive`**; inconclusive-only → `inconclusive` (no halt). The plan-039 scenario is
  itself a 3-of-5 partial, so a single collapsed verdict would either block on an outage or
  mask a real regression.

  **Reuse the existing table parser (pass-1 Missing-B).** Do **not** write a second parser —
  extract the one in `plan_manager.py` (note `_TRACKER_ROW_RE` already handles both `[#N]` and
  `#N` forms) so the verb and `reconciler.md` cannot disagree. Two parsers of one table
  produce a **fail-loud false positive**, the most expensive failure kind here.
  - depends-on: 0.2
  - resolves-upstream: #136 (include)
- Issue 1.2: Add a `REQ`-tagged test with a **mocked `gh`** covering: each disposition's pass
  and fail case; the plan-039 scenario (state OK, no mention) **failing**; `exclude` rows
  skipped; **a `gh` error producing `inconclusive`, not `fail`**; **the mixed case — one row
  `fail`, one row `inconclusive` → aggregate `fail`**; and **row-shape variants** (`[#N]` vs
  `#N`) pinning the shared parser. No network in tests.
  - depends-on: 1.1
- Issue 1.3: Wire `verify-reconcile` into `SKILL.md` §6.4 at the D7 position, with the
  fail-loud banner and remediation naming the exact `gh` commands to run.
  - depends-on: 1.1
- Issue 1.4: Add `REQ-PLAN-0NN` for the step, with an **executable** `Verification:` line
  (unlike `REQ-AGENT-031`'s, which points at prose — E1).
  - depends-on: 0.2
- Issue 1.5: Require the reconcile close reason to record the **upstream action** per row.
  Reporting-only improvement, explicitly **not** the enforcement (E1's caveat) — it makes E1's
  "shipped" tell impossible to write by accident.
  - depends-on: 1.3

### Epic 2: #140 (audit half) — close-time conformance (advisory)

- Issue 2.1: Add the close-time audit invocation reporting the **absolute** finding set (D5 —
  the delta is dropped; see pass-1 C5). Advisory: report + recommend `/yf-plan capture`,
  **never** gate `set complete`, and **do not** reuse the `FAIL-LOUD:` banner vocabulary.
  **Honour the D3 envelope** (JSON to stdout on every path) — the halting axis governs whether
  the step *stops* completion, not whether it emits a well-formed verdict; SC2 covers this step.
  - depends-on: 0.2
  - resolves-upstream: #140 (partial)
- Issue 2.2: Wire it into `SKILL.md` §6.4 **above the `classify-deliverable` block** (D7 +
  pass-1 C11) — anchor to that executed line rather than to the `set-deliverable-class`
  comment, which is not an executed statement (pass-3 C25),
  with the grandfathering caveat recorded — a `log.md` write that drops `scoping:` entries
  silently promotes warns to fails.
  - depends-on: 2.1
- Issue 2.3: Add `REQ-PLAN-0NN` + test. The test must assert the step **never returns a halting
  verdict** regardless of findings, and that it runs before the close step's own writes
  (plan-030's mechanism: an audit placed after them blocks on its own output).
  - depends-on: 2.1

### Epic 3: Adjacent defects E2 surfaced

Small, independently correct, and each would bite a 6.4 step.

- Issue 3.0: **SPEC amendments for Epic 3** (pass-1 C3). Epics 0/1/2 each carry a SPEC issue;
  this one did not, while 3.3 changes `close_cascade.py`'s documented exit-code contract
  (REQ-PLAN-067) and 3.2 changes observable `log.md` behavior that REQ-DATA-016 parsers key on.
  Land the requirement revisions + amendment-log entry **before** any Epic 3 code, per the
  project's SPEC-first rule.
  - depends-on: 0.4
- Issue 3.1: Fix `${RECONCILE_STEP}` unset on the resume path — re-derive the reconcile bead
  from bd rather than relying on a shell variable set only in §5.2a, and check the `bd close`
  exit code. **Verify the defect live first** (E2 inferred it from grep, did not run it).
  **Ship a `REQ`-tagged test** — SPEC-first is "requirement, then code **+ a tagged test**".
  - depends-on: 3.0
- Issue 3.2: Make `update-status complete` idempotent — no duplicate `- complete:` bullet on
  the documented "re-run §6.4" recovery (D8). **Ship a `REQ`-tagged test** asserting SC7.
  - depends-on: 3.0
- Issue 3.3: Make `close_cascade.py` exit non-zero when its **root is not found** — but
  **distinguish "bd answered and the bead does not exist" from "bd did not answer"** (pass-1
  C4). `_bd()` currently returns `[]` on `CalledProcessError`, `FileNotFoundError` **and**
  `OSError`, so `_bd_show(root) is None` fires identically for a typo, a missing binary, and a
  wedged Dolt DB. Only the first exits non-zero; the rest are **`inconclusive`** under the
  Issue 0.2 tri-state. Without this split, the fix converts a `bd` outage into a hard
  completion halt on healthy work. **Ship a `REQ`-tagged test** covering SC8 and SC11's
  second clause (mocked `bd` unavailable vs. bead-absent).
  - depends-on: 3.0

### Epic 4: Documentation + upstream

- Issue 4.1: Update `CHANGE-VALIDATION.md` — new tests in **both** fast and full tiers
  (plan-030 measured three separate tables each).
  - depends-on: 1.2, 2.3, 3.1, 3.2, 3.3
- Issue 4.2: Post to **#140** that its "9 of 40" is real but the framing needs correcting —
  9 of 10 failures are execution-authored, **not** legacy debt, because the OKF-legacy
  downgrade already absorbs the legacy half. Record that its nested-index half is confirmed
  real and deferred. Also record that the **delta refinement is deferred to this half** — its
  measured benefit against an approval-gated baseline was 1 of 10 (pass-1 C5).
  - depends-on: 2.3
- Issue 4.3: Post to **#136** the E1 root cause — not a silent error but a false success
  assertion, and the fact that `reconciler.md` step 4 already prescribed the verification that
  was skipped.
  - depends-on: 1.2
- Issue 4.4: Post **the answer itself** to #145, not merely that a contract exists (D9, SC10):
  the class axis is **`halting` / `advisory`**; **remediation-kind** (`command | prose |
  adjudication`) is a *separate* attribute; and **halting + prose-remediation is legal** —
  which is precisely #145's own shape (escape capture enforces, but its remediation is
  authoring). Posting a discriminator that does not discriminate for the reader it addresses is
  worse than posting nothing.
  - depends-on: 0.2

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: the contract exists before any payload uses it
- Type: auto
- Condition: `REQ-COMPLETE-001` is amended to an extensible chain **and** the step convention
  `REQ-COMPLETE-00N` is written with both authority classes defined.
- Test: the **negative** assertions are what matter — the gate cares about the *removal* of
  the blocking wording, not the presence of new words (pass-1 C13):
  ```bash
  ! grep -q "fixed three-step order" skills/yf-plan/spec/phases.md \
    && ! grep -q "runs a fixed order" skills/yf-plan/SKILL.md \
    && grep -q "ordered gate chain" skills/yf-plan/spec/phases.md \
    && grep -qE "halting|advisory" skills/yf-plan/spec/phases.md
  ```
- Blocks: Issue 1.3, Issue 2.2
- Instructions: The plan's entire premise is that the contract is settled **once**, before
  payloads. Wiring either payload into `SKILL.md` §6.4 while `REQ-COMPLETE-001` still says
  "fixed three-step order" would make the SPEC false the moment the step lands — the exact
  duplication this plan exists to prevent. Blocks the two **wiring** issues (1.3, 2.2), not the verb
  implementations (1.1/2.1), which are independently useful and produce the evidence.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | **`verify-reconcile` is fail-loud and calls the network.** A `gh` outage, rate limit, or auth lapse would halt completion on healthy work. | **High** | Distinguish *"the check could not run"* from *"the check failed"*. A `gh` error is **INCONCLUSIVE** — report loudly, do **not** halt. Only a definite wrong end-state halts. This distinction must be in the D3 envelope (Issue 0.2), not invented in 1.1. |
| R2 | **The `<plan-id>` mention check is a heuristic** and could false-positive on an issue commented by an unrelated plan, or false-negative if the comment phrases the id differently. | Medium | Test both directions in 1.2. Match the plan id exactly as `reconciler.md` is instructed to write it. **The time-window fallback is DELETED (pass-1 C10)** — "some comment postdating execution start" would have **passed plan-039**, since #108 was closed by a human 15 h after the reconcile bead closed. That is precisely what SC3 requires to fail. If exact matching proves brittle, the only permitted relaxation is a **normalized** plan-id match (case/punctuation tolerant), never a time heuristic. |
| R3 | ~~delta baseline absent~~ · ~~R4 fingerprint perturbation~~ — **both DISSOLVED** by dropping the delta (D5 / pass-1 C5). No baseline is stored, so there is no absent baseline, no late re-baseline (C6), no storage-location conflict (C7), and no delta-semantics ambiguity (C8). | — | Recorded so the R-numbering gap reads as a deliberate removal, not an editing loss. |
| R8 *(R8–R10 added at pass-1 review; appended after R3 to sit beside the risks they replace — R5–R7 below are original)* | **The contract is prose, and this plan's own central finding is that prose gets ignored.** `reconciler.md` step 4 already prescribed the verification that was skipped. A contract enforced only by "a future author will read it" reproduces the defect it exists to fix. | **High** | D10 / Issue 0.3: the regression test **enumerates §6.4's steps from `SKILL.md` source**, so a non-conformant new step fails CI. This is the only mitigation that is not itself another instruction. If Issue 0.3 ships without source-enumeration, this risk is **unmitigated** and the plan should say so rather than imply otherwise. |
| R9 | **`verify-reconcile` and `reconciler.md` could parse the Upstream Issues table differently**, producing a fail-loud false positive on healthy work — the most expensive failure kind here. | Medium | Issue 1.1 reuses the existing `plan_manager.py` parser rather than writing a second one; Issue 1.2 pins row-shape variants (`[#N]` vs `#N`). |
| R10 | **§6.4 now makes network calls where it previously made none.** Beyond outage (R1), a *hung* `gh` could hang land-the-plane indefinitely. | Low | Issue 0.2 requires a **bounded timeout** in the envelope contract for any network-calling step; timeout expiry is `inconclusive`, never `fail`. |
| R5 | **Changing `complete-gate`'s output stream is a behavior change** to a shipped, tested step; something may parse stderr today. | Low | E2 measured that the *documented* idiom captures stdout, so stdout is the contract-conformant direction. Issue 0.3's test asserts the documented idiom; grep for other callers before changing. |
| R6 | **Epic 3's defects are inferred, not reproduced** — E2 explicitly did not run bd live for the `${RECONCILE_STEP}` case. | Low | Issue 3.1 verifies the defect live **before** fixing it. A fix for a defect that does not exist is worse than no fix. |
| R7 | **Scope creep back toward #140's nested-index half.** It is measured, real, and adjacent — the temptation to "just add it" is live. | Low | Explicitly out of scope; Issue 4.2 records it upstream as deferred rather than silently absorbing it. |

## Success Criteria

1. **`REQ-COMPLETE-001` no longer specifies a step count** — it describes an ordered gate
   chain with named constraints, and remains true under the §6.4 sequence as documented, with
   **no step-count assertion** anywhere (pass-1 C14). `SKILL.md:1066`'s "fixed order" sentence
   is gone too.
2. **One tri-state verdict envelope, honoured by every step, enforced mechanically.** Every
   §6.4 step emits `verdict: pass|fail|inconclusive` JSON to **stdout on every path**.
   Verified by a test that **enumerates every script invocation in the documented §6.4 block**
   (not a hardcoded list, and not only the `X=$(… --json)` captures — see Issue 0.3), requires
   each to be **either envelope-capturing or on the named exempt list**, runs each capturing
   step's **failing** path, and asserts a non-empty envelope-conformant capture — the exact check that fails today, and the
   check that will fail for any future non-conformant step.
3. **The plan-039 scenario is caught.** A test with mocked `gh` in which the three `include`
   issues are `OPEN` (and the variant where they are `CLOSED` but carry no `<plan-id>` mention)
   makes `verify-reconcile` exit non-zero.
4. **`gh` unavailability does not halt completion** — an INCONCLUSIVE verdict is reported and
   `set complete` proceeds (R1).
5. **The close-time audit never gates `set complete`** — asserted by a test that gives it a
   failing bundle and confirms completion proceeds. It reports the **absolute** finding set
   (the delta is deferred, D5).
6. **Ordering is enforced and tested**: the audit runs **above the `classify-deliverable`
   block** — which contains the `set-deliverable-class` plan.md dual-write — not merely above
   the `log.md` write; a test asserts it does not observe
   artifacts written by the close step itself (plan-030's mechanism).
7. **`update-status complete` is idempotent** — running §6.4 twice leaves exactly one
   `- complete:` bullet in `log.md`.
8. **A typo'd `${EPIC}` fails loudly** rather than passing cascade-close with exit 0.
9. **SPEC leads implementation** — Epic 0 lands before any wiring, and every new verb has a
   `REQ` with an **executable** `Verification:` line.
10. **#136, #140 and #145 each carry the correction or the contract reference** so none
    re-derives the answer this plan settled. For #145 specifically, the posted answer names the
    **halting/advisory axis and the separate remediation-kind attribute**, and states that
    halting-with-prose-remediation is legal — the combination #145's own payload needs (D9).
11. **A `bd` outage or `gh` failure never halts completion.** Both surface as `inconclusive`;
    only a definite wrong end-state halts. Tested for `verify-reconcile` (mocked `gh` error)
    and for `close_cascade.py` root-resolution (mocked `bd` unavailable vs. bead-absent).
