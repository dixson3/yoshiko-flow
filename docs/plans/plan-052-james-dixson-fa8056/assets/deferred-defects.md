# plan-052 — deferred defects

**Ten** defects this plan **found and deliberately did not fix**. Each is declared out of scope
with its measurement, and each is filed upstream so it survives this plan rather than living
in a findings file nobody re-reads.

`ctl-deferred-count` (SC21a) asserts mechanically that there are **ten** rows and that every
row names a filed issue. **SC21b is `manual:` deliberately** — whether each filing carries a
*correct* measurement is a reader judgement over issue prose. The count is checkable and IS
checked; only the substance is waived, rather than waiving both and calling the pair verified.

The `Filed` column was populated by Issue 7.3, after the `upstream-write` consent gate was
resolved. Each defect is filed as a bead **out of tree** (no parent — a child of the plan epic
would make cascade-close fail-loud on it) and pushed through `/yf-beads-upstream`, so every one
carries an `external_ref` and is visible to `upstream.py closable`.

## The three bd defects (EXP-005 I-4)

Independent of #196/#197 — these are defects in `bd` itself, not in this repo.

| # | Defect | Measurement | Filed |
| :-- | :-- | :-- | :-- |
| D1 | `bd distill --var` **silently substitutes nothing and exits 0** | EXP-005 I-4(i): a `--var` pass produced output with the placeholders intact and returned success, so a caller cannot tell substitution from a no-op | [#211](https://github.com/dixson3/yoshiko-flow/issues/211) (`yf-slor`) |
| D2 | A step with `type = "gate"` and no `[steps.gate]` table **pours as a plain task with no diagnostic** | EXP-005 I-4(ii): the gate silently degrades to a task, so a formula author gets a DAG that looks poured and gates nothing | [#212](https://github.com/dixson3/yoshiko-flow/issues/212) (`yf-fnxb`) |
| D3 | `bd distill` **cannot reconstruct gate steps**, making it non-idempotent against bd's own pour | EXP-005 I-4(iii): pour → distill → pour does not round-trip; the gate is lost on the way back | [#213](https://github.com/dixson3/yoshiko-flow/issues/213) (`yf-nsm9`) |

## The `REQ-PLAN-073` id collision (D-18)

| # | Defect | Measurement | Filed |
| :-- | :-- | :-- | :-- |
| D4 | **Two different requirements share the id `REQ-PLAN-073`** | `skills/yf-plan/SPEC.md:345` defines it as *"the plan and incubator roots shall be configurable"* (plan-037 / #107), while `skills/yf-plan/spec/phases.md:150` defines it as the **`stamp-tracker`** requirement. Re-confirmed on this tree by `grep -n 'REQ-PLAN-073' skills/yf-plan/SPEC.md skills/yf-plan/spec/phases.md`. A cited id that resolves to two different requirements makes every citation of it ambiguous | [#214](https://github.com/dixson3/yoshiko-flow/issues/214) (`yf-xqj8`) |

## The two coordinator instrumentation defects (D-26)

Without both, **no concurrency question about this corpus is ever answerable** — which is why
they are filed rather than quietly worked around.

| # | Defect | Measurement | Filed |
| :-- | :-- | :-- | :-- |
| D5 | `started_at` is written for only **86 of 225** plan beads (plan-048: **0 of 39**), and is **not exposed by `bd list --json`** | EXP-006 §1: beads carrying both `started_at` and `closed_at` = 86/225. Two halves, both required: the coordinator must write it unconditionally, and bd must expose it | [#215](https://github.com/dixson3/yoshiko-flow/issues/215) (`yf-zrtx`) |
| D6 | The coordinator **closes beads in batches**, making **84%** of all observed interval overlap an artifact | EXP-006 §1/I-5: batching collapses distinct work intervals onto one timestamp, so measured "concurrency" is mostly an artifact of when the closes were flushed, not of when work ran | [#216](https://github.com/dixson3/yoshiko-flow/issues/216) (`yf-ek9a`) |

## The `change_validation` run-record (D-13)

| # | Defect | Measurement | Filed |
| :-- | :-- | :-- | :-- |
| D7 | `change_validation.py` **persists no run record** | EXP-004 §4. It is the shared prerequisite for BOTH the recipe-row predicate (P5) and the criterion-re-check predicate (P6): neither can ask "did this actually run, and when?" without one. Filed, not built — building it inside this plan would have pulled two more predicates into scope with it | [#217](https://github.com/dixson3/yoshiko-flow/issues/217) (`yf-ku0x`) |

## The gate Test/Condition fidelity gap (found at execution)

**This one was found AFTER the other seven**, at execution, by a human — not by the checker this
plan shipped for gates. It is added here rather than left out, because excluding a real defect to
keep a control's count green is the exact inversion of what this plan is for. `ctl-deferred-count`
was amended from seven to eight in the same change, and the reason is recorded in the control.

| # | Defect | Measurement | Filed |
| :-- | :-- | :-- | :-- |
| D8 | **`gate_consistency.py` does not check TEST/CONDITION FIDELITY** | 4.2 ships two arms — Blocks-set self-satisfaction and discharger closure — and neither compares a gate's `Test` to its own `Condition`. Worked instance: this plan's own Reconcile Gate, whose Condition read *"every non-gate execution bead UNDER THIS PLAN'S EPIC"* while the Test keyed only on `metadata.plan`, so it counted 7 out-of-tree beads that are open by design and the gate could never open. `gate_consistency.py` reports that gate **PASS, 0 findings**. A gap in #113's sub-case SCOPE, not a bug in 4.2 — SC13 asserts the two arms commissioned, and both work | [#219](https://github.com/dixson3/yoshiko-flow/issues/219) (`yf-q4rr`) |

## The harness's own record-keeping (found by the §6.4 halt)

**Discovered by trying to build a receipt and failing.** That failure IS the finding: a plan
that had accepted the receipt would have shipped a green clause matching nine records and
proving none of them.

| # | Defect | Measurement | Filed |
| :-- | :-- | :-- | :-- |
| D9 | **`red-observations.tsv` cannot distinguish a driven RED from a real failure**, and records no subject — plus **`grant --check` does not verify AMENDMENTS** | Schema is `(timestamp, ctl_id, exit)`. For `ctl-spec-first-order` alone: **18** records, **11** exit-0, **9** of those pre-merge, nothing distinguishing which run measured what; both exit-1 records are `CTL_RED` driven REDs, indistinguishable from failures. So `SC2` and both red-prework Conditions — *"a recorded RED observation with EXIT 1"* — are **weaker than their wording**. Second finding, same class one layer up: two grant amendments were written to a stale worktree copy and never reached the authoritative file, and `grant --check` returned **exit 0** anyway; only counting `AMENDMENT` markers caught it | [#220](https://github.com/dixson3/yoshiko-flow/issues/220) (`yf-sfle`) |

## SC24's formulation (found by the completion commit itself)

The plan was **NOT** reverted to `reconciling` and `SC24` was **NOT** amended. The operator
ruled that its falseness is recorded upstream rather than papered over — the same direction as
everything else here: fix the predicate, or file it, but never lower the claim to match what the
check happens to return.

| # | Defect | Measurement | Filed |
| :-- | :-- | :-- | :-- |
| D10 | **`SC24` asserts a MOVING fact (`stamp == HEAD`) where it should assert a DURABLE one** (`stamp ==` the commit it was built from, recorded at deploy) | Stamp `ed0803f`, HEAD `e94206a`. The deploy was real and `SC24` was genuinely green at `ed0803f`; then the commit **recording that the close chain passed** moved HEAD and re-staled it — and that commit touches `docs/plans/**` only, which `cargo:rerun-if-changed` does not watch, so no rebuild would have re-stamped it either. **Re-stamping does not terminate:** any further commit re-stales it, including the one recording the check passing. **Predicted and closed on a false premise** — red-team pass 4 raised it as `M7` and the resolution was *"rebuild-then-verify after the final commit"*. **There is no final commit.** FOURTH instance of one class, with `SC1c`, `SC20` and the Reconcile Gate | [#221](https://github.com/dixson3/yoshiko-flow/issues/221) (`yf-487t`) |
