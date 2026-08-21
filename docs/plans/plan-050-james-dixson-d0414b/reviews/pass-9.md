---
type: Review
okf_spec: OKF-PLAN
id: pass-9
status: complete
---

# Red-team pass 9

## Verdict: REVISE

Seventh independent pass. **Eight of pass-8's nine resolutions verified by execution and hold. One
does not** — and it is mine: C77's fix was wrong on its central claim, proven by building the change
and running the tests. **C86 is execution-blocking**; C87-C91 are non-blocking observations.

## Strengths

- **The portability audit held at zero findings**, `okf check` OK, `doc_lint` PASS over all root
  documents. `ready-check`'s only blocker is the outstanding REVISE verdict — no structural defect
  underneath it.
- **Discharged-by is complete in both directions with an empty set on each** — the first pass at
  which that could be confirmed.
- **C79's claim is exactly true and its fix well-specified**: `SKILL.md:1440-1441` captures `RSTEP`
  and only echoes it, while the adjacent `verify-reconcile` and `close_cascade.py` blocks both
  capture and halt. "The pattern Issue 1.3 must copy is twelve lines below the line it must edit."
- **SC7's figure reproduces for the seventh consecutive round** — `--exclude` → **757** while
  unfiltered has moved 817 → 820 → 823 → **824** across four measurements. The self-exclusion
  mechanism has not budged once.
- **All cited `file:line` anchors resolve**; all 14 upstream rows confirmed OPEN; every disposition
  re-checked against `_verify_row`'s branches at HEAD rather than against its docstring.

## Concerns

| Concern | Sev | Detail | Resolution |
| :-- | :-- | :-- | :-- |
| C86 | **high, execution-blocking** | **The `--path`-keyed scope was wrong, and my C77 fix asserted the opposite.** C77 said "the `--path` reading survives"; pass 9 built it and ran the suite: it breaks `_shared/test_doc_lint.py`'s **SC17** block (`:722-743`), which pins an unselected `--path` to `PASS`/rc 0 **and identical to a nonexistent path** — the exact opposite of this plan's SC6. **SC6 and plan-049's shipped SC17 are in direct contradiction.** The real FAST tier was run: `doclint-tests FAIL rc=1`. Worse, the chosen scope **does not fix #181's titled scenario** — a bundle *copied* outside `docs/plans/` is the `--root` form, still a silent green under `--path`-keying, while #181 is dispositioned `include`, which requires CLOSED. And `DOC-LINT.md`'s reserved `index.md`/`log.md` case would become INCONCLUSIVE on every `log.md` edit, including this plan's own | Adopted **#181's own option 2**, which the reviewer built and measured green: an **opt-in `--require-selection` flag**. Zero edits to `test_doc_lint.py` (SC17 *and* SC42 stay green, measured `all passed`), covers the `--root` form, leaves DOC-LINT.md's "ordinary" case true for unflagged callers, and confines the exit-2 widening to callers that asked for loudness — which also sits better with REQ-DATA-024. SC6 extended to a three-outcome assertion **including the `--root` arm**; Issue 2.3 now runs the suite and the FAST tier as the pinning regression |
| C87 | med | **C81's fix corrected `plan.md` and left the same superseded claim live in two satellites.** `findings/exp-005` still prescribes "ship a `grant` verb by asking `_verify_row` what it will demand" — the design pass-3 C12 refuted by measurement — and `index.md` repeats it as a one-line summary. An executor reading `findings/` first would build the refuted design. Seventh round of the plan.md-vs-satellite class, and self-injected: C81's own resolution swept one of three surfaces | A `> **SUPERSEDED at pass-3 C12**` banner added to exp-005 above its first section, naming Issues 3.2/3.2a; `index.md`'s summary corrected. Swept all six findings: **exp-003 was also stale** and now carries a `> **REFINED at pass-9 C86**` note, since its "add the verdicts" recommendation predates the measurement that forced the flag |
| C88 | low | **Issue 2.2 carried a duplicated instruction, and the duplicate was C84's placeholder** — C77's edit inserted a paragraph mid-issue without removing the original trailing sentence, so a defect closed the same round survived inside C77's remedy | Removed with the C86 rewrite; one `<fixture> <control>` remains, the legitimate verb signature in 0.2 |
| C89 | low | C83 removed "two different times" and left "two different **trees**" beside it — after C69, nothing in the records asserts tree identity either. The same unverifiable residue, one clause over | Both the gate Condition and Issue 0.2 now say "by two different verbs" / "at different points in the DAG" |
| C90 | low | **SC4's post-fix arm had no assigned runner.** SC4 requires `close_cascade.py` non-zero "both before and after 1.2", but only the *before* run was assigned; 1.4's text covers the epic's two *controls*, and neg-179 is deliberately not one | Issue 1.4 now re-runs `neg-179-open-wrapper` directly against the fixed tree. Permitted by 1.4's own constraint — a raw scenario is not a `redcheck.sh` verb, so no gate evidence is produced inside `Blocks` |
| C91 | low | SC20 was close to unfailable — its escape hatch is "a reason recorded in `log.md`", written by the same executor | Tightened: the reason **and** `git diff --name-only <base>...HEAD` touching nothing under `yf/` or `skills/`. One command, so the exemption is checkable rather than assertable |

## Missing

Nothing structural; the bundle is complete. One observation below the concern bar, recorded because
it outlives this plan: **Issue 3.2's shared requirement table is anchored in no `REQ-*`.** R6's whole
mitigation is "a divergence requires editing that table", and nothing in SPEC would stop a later
change re-forking the generator and the verifier. Not an SC1 defect — the refactor is
behaviour-preserving — but R6 has no durable enforcement past this plan. Folding the one-table
invariant into the #178 grant-generator REQ that 0.1 already lands costs one sentence.

## Gate Assessment

All four gates OK. The observed-RED gate is reachable, aggregate and falsifiable;
`producers ∩ Blocks = ∅` confirmed mechanically; no REQ-AGENT-046 cycle; no frontloading miss (it
needs 3.2a's record, so it cannot sit earlier). C66's dual disclosure re-verified honest. The
negative control is correctly outside `controls.txt`. The Reconcile Gate's `length > 0` guard
prevents a vacuous pass.

## Upstream Assessment

All 14 rows OPEN, each disposition re-checked against `_verify_row`'s source branches at HEAD
(`:2024` include, `:2033` supersede, `:2042` partial, `:2052` deferred, `:2073` tracker→inconclusive,
`:2087` unrecognised→fail), with the `exclude` pre-filter real at `:2119`/`:3991`. C71's fix holds —
6.2's two `resolves-upstream` lines merge into all four `partial` rows.

One note carried forward: `_mentions_plan_id` (`:1992`) scans **comments only, not the body**, so
`gh issue close --comment` satisfies it but a body-only mention would not. The grant verb enumerates
the action, so this is low — but the plan never says it explicitly.
