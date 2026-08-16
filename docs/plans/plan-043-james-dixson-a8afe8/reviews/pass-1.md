---
type: Review
okf_spec: OKF-PLAN
id: pass-1
plan: plan-043-james-dixson-a8afe8
created: '2026-08-16'
verdict: REVISE
status: resolved
---

# Review pass 1 — adversarial (red-team)

## Verdict: REVISE

4 high, 7 medium, 3 low, plus 3 missing items. Conformance passed first (with three
advisories, all fixed before this pass).

## Premise verification — all independently re-measured, all CONFIRMED

| Premise | Evidence |
| :-- | :-- |
| `REQ-COMPLETE-001` is count-bearing | `spec/phases.md:89` *"runs a fixed three-step order"* + positional `Verification:`. Also restated at `SKILL.md:1066`. |
| complete-gate writes fail to stderr; SKILL.md captures stdout | `plan_manager.py:1653-1657` `err=True`; `SKILL.md:1112` `GATE=$(…)`. Second instance: `"plan.md not found"` also `err=True`. |
| `reconciler.md` already has a verify step | `agents/reconciler.md:49-53`, `### 4 — Verify updates`. |
| 24.4% blocking rate | Re-ran the corpus: 41 complete, **31 pass / 10 fail**, failing set **byte-identical** to E3's table. |
| `${RECONCILE_STEP}` set only at §5.2a | Two hits: set 815, consumed 1094. |
| cascade exits 0 on root-not-found | `close_cascade.py:188-192`. |
| `update-status` non-idempotent | `plan_manager.py:1138` unconditional `append_log`. |

> *"The evidence base is the strongest I have seen in this corpus. Every concern below is
> downstream of a correct premise."*

## Strengths (verbatim)

- **D2 is genuinely the leverage claim it says it is** — one sentence at `phases.md:89` blocks
  three issues.
- **D3 makes a false spec statement true.** `spec/cli.md` REQ-CLI-016 already asserts a
  mirroring that does not hold. A conformance fix, not a preference.
- **D6 is well-founded and non-obvious** — a real falsification test that was actually run.
- **Landing one payload of each authority class is the right proof obligation** for a
  convention-only contract.
- **Gate reachability is clean**, and confirmed not vacuously satisfied today.

## Concerns

| # | Concern | Severity |
| :-- | :-- | :-- |
| C1 | **The D3 envelope cannot express INCONCLUSIVE, which R1 requires.** `{passed, reason, remediation}` is boolean; R1 says the distinction "must be in the envelope (0.2)"; SC4 requires the behavior. All three cannot hold. The mitigation does not mitigate. | **high** |
| C2 | **The fail-loud/propose-only discriminator cannot classify #145** — the plan's own test case. #145's remediation is prose authoring (→ propose-only) but its requirement is to *enforce* (→ halting). The discriminator conflates **halting authority** with **remediation kind**; escape capture is an authoring-remediation halting step. #145 will re-derive its own answer — the exact outcome the plan exists to prevent. | **high** |
| C3 | **Epic 3 makes behavior changes with no SPEC issue.** 3.3 changes `close_cascade.py`'s documented exit-code contract; 3.2 changes observable `log.md` behavior that REQ-DATA-016 parsers key on. Epics 0/1/2 each carry a SPEC issue; Epic 3 has none, violating the project's SPEC-first rule. | **high** |
| C4 | **Issue 3.3 conflates "root not found" with "`bd` unavailable".** `close_cascade._bd()` returns `[]` on `CalledProcessError`, `FileNotFoundError` **and** `OSError`, so `_bd_show(root) is None` fires identically for a typo, a missing binary, and a wedged DB. Exiting non-zero converts a `bd` outage into a hard completion halt — the R1 failure mode, in an epic with no INCONCLUSIVE treatment. | **high** |
| C5 | **The delta's measured benefit is one case, against real cost.** The Phase-3 audit is a *precondition of approval*, so the stored baseline is an empty fail set by construction on every non-`--force` approval — the delta equals the absolute set in the normal path. Its entire measured benefit is suppressing plan-001 (class B). And since the step is propose-only, noise costs nothing. Complexity spent to quiet a report that cannot block. | medium |
| C6 | **Re-approval can silently re-baseline past the regressions the delta exists to catch.** If a verdict is re-recorded at any re-approval *after* execution artifacts exist, the baseline absorbs them and the close report says nothing — same shape as #136. R3 covers *absent* baseline, R4 *fingerprint perturbation*; neither covers a *present-but-wrongly-late* one. | medium |
| C7 | **Issue 2.1's storage decision is open, and both candidates conflict with the plan's own decisions.** `log.md` collides with D8, E3's grandfathering constraint, and REQ-DATA-016; `plan.md` body breaks the fingerprint. The safe answer exists and is unnamed: `_plan_content_sections` structurally drops preamble `**Field:**` lines, so a preamble field is fingerprint-neutral **by construction**. | medium |
| C8 | **Delta semantics underspecified in two ways** that will be decided ad hoc: (i) fails, warns, or both — live, since approval blocks on `fail` only, so warns are the only findings that can legitimately pre-exist; (ii) the finding-identity key — content-heuristic findings embed paths/text in `item`, so an unrelated edit re-reports a pre-existing finding as new. | medium |
| C9 | **`verify-reconcile` has no representation for partial failure.** 5 rows, row 2 definitively wrong, `gh` dies on row 4 — a single verdict collapses to halt-on-outage or mask-a-regression. The plan-039 scenario is itself a 3-of-5 partial. | medium |
| C10 | **R2's stated fallback defeats D6.** "Assert *some* comment postdating execution start" would have **passed plan-039** — #108 was closed by a human 15 h after the reconcile bead closed. That is exactly what SC3 requires to fail. | medium |
| C11 | **The Approach diagram omits the first two things §6.4 runs.** `classify-deliverable` and `set-deliverable-class` precede `bd close ${RECONCILE_STEP}`, and `set-deliverable-class` is a **dual-write plan.md write** — the exact class D7 exists to precede. An implementer following the diagram places the audit *after* it. | medium |
| C12 | **Epic 0 does not name `SKILL.md:1066`**, the other count-bearing sentence. It becomes false the moment either payload lands, and belongs to Epic 0, not to the wiring issues. No issue owns it. | medium |
| C13 | **The Capability Gate test is satisfiable by writing the words.** A presence grep cannot detect that `REQ-COMPLETE-001` still says "fixed three-step order" three lines above. | low |
| C14 | **SC1 reintroduces a count** ("five steps") — a criterion whose purpose is deleting a count should not assert one. | low |
| C15 | **Issue 0.4 is described as "first" but declares `depends-on: 0.1`** — reads as a contradiction. | low |

## Missing

- **A — The self-referential risk is not in the risk table.** Epic 0's deliverable *is* prose,
  whose teeth are "the SPEC + tests, not a dispatcher". Nothing ensures a future step author
  reads `REQ-COMPLETE-00N`; SC2 verifies the four *known* steps and does not fail when a fifth
  non-conformant step is added. **Epic 1 gets this right** (a script verb replaces an ignorable
  instruction); **Epic 0 does not.** Recommendation: make Issue 0.3's test **enumerate §6.4's
  steps from the SKILL.md source** rather than hardcoding four, so a new non-conformant step
  fails CI — the plan's own thesis applied to itself.
- **B — `verify-reconcile` duplicates the reconciler's table parser.** Two parsers of one table
  can disagree (`[#N]` vs `#N`; `_TRACKER_ROW_RE` already handles both), producing a fail-loud
  false positive — the most expensive kind. Not risked.
- **C — §6.4 now makes network calls where it previously made none.** R1 covers outage but not
  latency; the INCONCLUSIVE path needs a bounded timeout so a hung `gh` cannot hang
  land-the-plane.

## Gate Assessment

Capability Gate is **reachable, no cycle**, condition produced by Epic 0 (outside its `Blocks`
set), verified not vacuously satisfied today, and its scoping rationale (block wiring, not verb
implementation) is *"correct and well-argued"*. **But the test is a word-presence tautology**
(C13). Two unmet preconditions found: Epic 3 assumes a SPEC amendment no issue produces (C3),
and Issue 2.2's delta assumes a baseline whose location and freshness rules 2.1 does not fix
(C6–C8).

## Upstream Assessment

Dispositions *"well-reasoned and unusually honest"*. #136 `include` and #140 `partial` both
justified, with #140's in/out split citing the OKF v0.2 §8/§9/§11 MAY/MUST-NOT basis.
**#145 `exclude` is right but Issue 4.4's content is the weak point** — it promises to name two
authority classes that C2 shows cannot classify #145's own payload. *"Posting a discriminator
that does not discriminate for the reader it is addressed to is worse than posting nothing."*
No supersedes claimed; no issue silently absorbed.

## Operator Resolutions

| # | Concern | Severity | Resolution | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 | Envelope cannot express INCONCLUSIVE | high | Accepted. Issue 0.2 now specifies a **tri-state** `verdict: pass|fail|inconclusive` with `passed` retained as a derived compatibility key, and states the halting rule per state (`fail` halts; `inconclusive` never halts, always reports). SC2 reworded to the tri-state. | resolved |
| C2 | Discriminator cannot classify #145 | high | Accepted — **operator decision: split the axes** (D9). Classes are defined on the **halting axis alone** (`halting`/`advisory`); remediation-kind (`command|prose|adjudication`) is a separate documented attribute, with legal combinations stated and **halting + prose-remediation explicitly permitted** — #145's shape. Issue 4.4 and SC10 now require posting *that* answer, not merely "a contract exists". | resolved |
| C3 | Epic 3 has no SPEC issue | high | Accepted. New **Issue 3.0** lands the SPEC amendments + amendment-log entry for Epic 3 before any of its code; 3.1/3.2/3.3 all `depends-on: 3.0`, which itself `depends-on: 0.4`. | resolved |
| C4 | 3.3 conflates root-not-found with bd-unavailable | high | Accepted, and the mechanism verified in the finding: `_bd()` returns `[]` on `CalledProcessError`, `FileNotFoundError` **and** `OSError`. Issue 3.3 now requires distinguishing *bd answered, bead absent* (exit non-zero) from *bd did not answer* (`inconclusive`). | resolved |
| C5 | Delta benefit is 1/10 against real cost | medium | Accepted — **operator decision: drop the delta** (D5). Ships absolute propose-only findings. Issue 2.1 (persisted baseline) removed and Epic 2 renumbered to 2.1–2.3. The measured benefit was 1 of 10 against an approval-gated baseline that is empty by construction, on a step that cannot block. Deferred to #140's remaining half; Issue 4.2 records it upstream. | resolved |
| C6 | Re-approval can silently re-baseline | medium | **Dissolved** by dropping the delta — no baseline is stored, so there is no late re-baseline. | resolved |
| C7 | Baseline storage location unresolved | medium | **Dissolved** by dropping the delta. (The finding that `_plan_content_sections` structurally drops preamble `**Field:**` lines is recorded here for whoever builds the delta later — it is the fingerprint-neutral storage answer.) | resolved |
| C8 | Delta semantics underspecified | medium | **Dissolved** by dropping the delta. | resolved |
| C9 | No partial-failure representation | medium | Accepted. Issue 1.1's envelope now carries `rows: [{issue, disposition, verdict, detail}]` with a stated aggregate rule — **any row `fail` → `fail` (halt), even alongside `inconclusive` rows**; inconclusive-only → `inconclusive`. Issue 1.2 gains the mixed-case test. | resolved |
| C10 | R2 fallback defeats D6 | medium | Accepted — **the fallback is deleted.** R2 now permits only a *normalized* plan-id match, never a time window. The reviewer is right that the fallback would have passed plan-039, which SC3 requires to fail. | resolved |
| C11 | Diagram omits the dual-write step | medium | Accepted. The Approach diagram now enumerates `classify-deliverable` and `set-deliverable-class`, and states the audit's position is **above the dual-write**, not merely above the `log.md` write. Issue 2.2 and SC6 updated to match. | resolved |
| C12 | SKILL.md:1066 unowned | medium | Accepted. Issue 0.1 now explicitly owns `SKILL.md:1066`, and the Capability Gate test asserts its removal. | resolved |
| C13 | Gate test is a tautology | low | Accepted. The gate test is now **negative-assertion first** — it asserts the blocking wording is *gone* from both `spec/phases.md` and `SKILL.md`, which is what the gate actually cares about. | resolved |
| C14 | SC1 reintroduces a count | low | Accepted. SC1 no longer asserts a step count. | resolved |
| C15 | 0.4 "first" vs depends-on | low | Accepted. Issue 0.4 now states that "first" means first in the SPEC amendment log, not in execution order. | resolved |
| M-A | Contract has no mechanical teeth | high | Accepted — **operator decision: mechanical teeth** (D10). Issue 0.3's regression test now **enumerates §6.4's steps by parsing `SKILL.md`'s documented `X=$(… --json)` invocations** rather than hardcoding them, so a non-conformant future step fails CI. Added as **risk R8**, which states plainly that if 0.3 ships without source-enumeration the risk is unmitigated. This is the plan's own thesis applied to itself. | resolved |
| M-B | Duplicate table parser | medium | Accepted. Issue 1.1 must **reuse** the existing `plan_manager.py` table parser rather than writing a second one; Issue 1.2 pins the `[#N]` vs `#N` row-shape variants. Added as **risk R9**. | resolved |
| M-C | No bounded timeout on gh | low | Accepted. Issue 0.2's envelope contract now requires a **bounded timeout** for any network-calling step, with expiry as `inconclusive`. Added as **risk R10**. | resolved |
