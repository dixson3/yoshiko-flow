---
type: Review
okf_spec: OKF-PLAN
id: pass-3
status: complete
---

# Red-team pass 3

## Verdict: REVISE

Third independent pass, against `68b76fc`. **One high concern, found by execution, and for the third
consecutive cycle living inside the previous pass's fix.** 6 concerns: 1 high, 2 medium, 3 low. All
resolved below; none deferred.

Pass 1 found `ctl-182-spike` unsatisfiable on a **literal-vs-regex** reading. Pass 2 found the fix
still unsatisfiable on a **whitespace** reading. Pass 3 found it unsatisfiable on an **ownership**
reading. The resolution retires the entire apparatus the three passes were fighting over.

## Strengths

- **C21's ellipsis rule is now correct and the printed pattern verifies** — `writes.*?at presentation`
  → 1, the naive spaced form → 0, all three fragments resolving on the unfixed tree
  (`fragments-checked=3 failed=0`).
- **C22's root fix is sound on its own axis.** A concrete post-fix `REQ-AGENT-043` line in 0.1's
  shape was written and **both** controls run against it: `ctl-165-executable` → exit 0;
  `ctl-182-spike` conjunct (b) → `fragments-checked=3`, not 0. The two are no longer incompatible.
- **C24's cwd clause is load-bearing and measured both ways** — from the root, exactly the 3 source
  files; from inside the bundle, the plan's own prose, confirming the pathspec is cwd-relative.
- **DAG re-verified clean after the new `3.2 ← 1.2a` edge** — acyclic by DFS, all six producers
  ancestors of the `.4` they feed, none inside `Blocks {1.4, 2.4, 3.4}`.
- **Zero stale citations, third pass running** — 17 re-checked and exact.
- **All 20 criteria falsifiable.** The reviewer looked and found none that cannot fail; SC3's arm 2
  *would* fail today under two of three readings, which is correct behaviour.
- **SC7's instrument verified by spike**: `bd cook --dry-run` on `plan-investigate.formula.toml`
  prints `Steps (0)` and **exits 0** — exactly the vacuity C6/C28 guard against, confirming the
  positive set assertion is necessary and workable.
- **SC13b's required quotation is verbatim in #182's body** — *"never write, edit, or create any
  file"* — and `red-team.md:63` demonstrably does not say it, so D-1's narrowing is a correction of
  the issue rather than an acceptance of it.
- **SC5's premise confirmed**: `DRIFT-CHECK.md` §2 has no `spec` → `agent` edge.

## Concerns

| Concern | Severity | Resolution |
| :-- | :-- | :-- |
| **C30 — `ctl-182-spike` measures 1 / 1 / 1 again, because 0.1 and 1.2 BOTH claimed ownership of `spec/agents.md:73` and the plan never said which wins.** Three readings of conjunct (b) were built and run: nearest-preceding-filename → **1/1/1**; nearest-following-path → 1/1/0 but with `failed=3` on the *clean* tree, a **false RED** that can no longer distinguish the dangling state; a hard-coded table → **1/1/1**, failing on the literal SC4 requires at zero sites. Under the 0.1-owns branch, the fragment 1.1 normatively printed has **0 occurrences** — 1.1's whole C21 apparatus was authored against a state the DAG destroys first. Under the 1.2-owns branch, 0.1 violates its own SPEC-first clause. **Every branch broken or dead** | **high** | **Fixed at the root, all six steps.** 0.1 now **owns** the `Verification:` retarget and says so, including that the commands are legitimately RED from 0.1 until 1.2a — the intended SPEC-first order. 1.2 loses that step, keeping REQ text + `Rationale:`. Conjunct (b) is rewritten for the command shape as a **positional `grep -qF "<literal>" <path>` pairing** — no prose parsing, no inference, no ellipsis. **The ellipsis rule, the printed pattern and the fragment→file table are DELETED.** The self-check is re-aimed at the literals, and SC3's arms are restated against the command shape. The stated redundancy with `ctl-165-executable` is now written in 1.1 rather than discovered at execution |
| **C31 — 4.1's `--changed` mandate is inert.** Verified at source: `change_validation.py:820` reads `if args.changed and tier == "fast"`, and `plan_manager.py:3529` hard-codes the FULL invocation with no `--changed`. So the flag cannot reach the run 4.1 makes, and SC10 pointed the one-flag rule at the one tier where it provably does nothing | med | **Fixed.** 4.1 names `validate-merged <plan_dir> --json` and **forbids** `--changed`; SC10's clause is re-aimed at 4.6's report; SC11 now asserts the **status string** (`status: "pass"`, exit 3 on non-pass) rather than a failure count, and records that `CHANGE-VALIDATION.md:39` is `approved: yes` so a vacuous tier-3 pass is unreachable |
| **C32 — no criterion asserts `assets/edit-set-182.md` is complete** (raised at passes 2 and 3). SC4's grep covers **4 of 9** sites; `SKILL.md:486/516`, `skills/yf-plan/SPEC.md:65/389-390` and the three `web/content/*` restatements are covered by no grep, no CV row and no drift edge | med | **Fixed — SC4b added**, a **subset** assertion (not a count): every surviving read-only restatement under `skills/yf-plan/**` and `web/content/**` must be an enumerated row with a stated disposition. Pass 3 swept it and found the enumeration already complete — `workflows.md:251` is the **yf-research** table and correctly out of scope — so it should pass; it simply was not asserted |
| **C33 — 3.1's honesty note was factually wrong, in the plan's favour.** It claimed the RED comes *solely* from the missing test because the command conjunct is "already green". Measured: the retargeted commands grep for phrases the agent files do not yet carry, so they exit **1** — two independent causes, not one | low | **Fixed.** The note now records both causes and marks the earlier claim as measured-false. The real limitation stands: the control never observes the *"prose shaped like a command"* defect, since 0.1 fixes the shape |
| **C34 — the `251` census figure is likely stale and 4.2 hard-coded it into an outward-facing comment.** A pass-3 reconstruction returned **257**; EXP-003 never recorded its pathspec, so the difference is unresolvable — which is what D-5 forbids shipping | low | **Fixed.** 0.3 records the census **with its verbatim pathspec** so it is reproducible, and 4.2 quotes 0.3's record rather than the drafting literal |
| **C35 — 1.2a's edit set is stated as 2 files while its subject is restated in files 1.2 owns**, and `workflows.md:179` (the reviewer's `Read-only?` cell) was named nowhere | low | **Fixed.** 1.2a states the ownership boundary explicitly, and `:179` joins the no-edit list beside `:180` |

## Missing

Nothing. C32 was the last structural gap and is now asserted by SC4b. Pass-2's end-state re-run gap
is genuinely closed (4.1 re-runs all three fixtures; SC11 asserts it), and pass-1's Missing items
remain closed.

## Gate Assessment

**Reachability sound for the third pass; satisfiability failed for the third pass, on the same
control, one abstraction layer up each time.** Graph properties re-verified clean per control after
the new edge; count derivation sound (3 declared vs a 3-line manifest under both patterns, no
self-contamination); the gate `Test:` shape is byte-identical to plan-050's proven form, and
`redcheck.sh:211` resolves `plan.md` from the script's own location so 0.2's pattern substitution is
safe.

The three failures were **literal-vs-regex**, then **whitespace**, then **ownership** — each fix
individually correct and mutually destructive with the next, because C22 changed the shape of the
line C21's rule parsed and nothing reconciled them. The resolution does not patch a fourth reading:
it **collapses conjunct (b) to a positional `grep -qF "<literal>" <path>` pairing and deletes the
ellipsis machinery entirely**, which removes the parser choice that generated all three failures.

## Upstream Assessment

**Sound, no overclaiming found.** All 11 issues verified OPEN with matching titles; #177 still OPEN.
Both `include` rows correctly wired with a measured RED. C23's fix is real and well-targeted — SC13b's
required quotation is verbatim in #182's body. Scope honesty holds on all four partials: #165 is
genuinely one-plan-scoped against a census re-verified as large with all three measured-false clauses
still live; #173 and #174 each name the sub-case closed and state the general pass stays open; #150
claims two ranked classes, not the research. C4's five-comment count remains right. Both out-of-scope
defects are correctly routed to 4.6 — with C31's caveat now recorded: the `--changed` defect, though
real and verified at source, affects no invocation this plan makes.
