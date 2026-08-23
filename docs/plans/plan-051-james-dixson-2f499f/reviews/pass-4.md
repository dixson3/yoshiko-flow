---
type: Review
okf_spec: OKF-PLAN
id: pass-4
status: complete
---

# Red-team pass 4

## Verdict: REVISE

Fourth independent pass, against `cd18bcc`. **The headline came back clean: `ctl-182-spike` finally
works, verified on four arms.** It did not fail a fourth way. But the streak held on a different
control — the blocking defect is again inside the previous pass's fix, this time in **SC4b**, the
criterion pass 3 added to close C32, and it was broken in **both** directions. 5 concerns: 1 high,
1 medium, 3 low. All resolved; none deferred.

## Strengths

- **`ctl-182-spike` is satisfiable — measured, four arms:**

  | arm | conjunct (a) | conjunct (b) | exit |
  | :-- | :-- | :-- | --: |
  | unfixed (pre-0.1) | FAIL | `pairs-found=0` | **1** |
  | post-0.1 (spec retargeted, agents not reworded) | FAIL | `pairs-found=2 failed=2` | **1** |
  | post-1.2a (both reworded) | PASS | `pairs-found=2 failed=0` | **0** |

  Non-zero then zero, as required. The DAG guarantees 1.1 runs against the post-0.1 tree
  (`1.1 ← 0.2 ← 0.1`), so the RED it records is the non-vacuous one. **Pass 3's fix — deleting the
  parser choice rather than patching a fourth reading — is what made this work.**
- **The self-check proved load-bearing, twice, by accident.** The reviewer's own first two fixture
  attempts (lowercase literals against capitalised prose; a `\S+` path capture swallowing a backtick)
  each produced a **false RED on an actually-fixed tree** — and the self-check caught both, returning
  **exit 2 = harness failure**, correctly routing to "repair the instrument" rather than "the fix is
  wrong". First pass where the machinery distinguishes its own breakage from the tree's.
- **SC10 verified by running it, and the requirement is real not stylistic** — the two single-path
  invocations select **disjoint** command sets (`cargo, uv-yf-close-contract, doclint, doclint-tests`
  vs `uv-yf-review-verdict, frontmatter, uv-yf-gates`).
- **SC11/4.1 verified at source**: `_validate_merged` returns `status`; `validate_merged_cmd` exits
  `0 if status == "pass" else 3`; `_run_change_validation` hard-codes FULL with no `--changed`
  reachable. C31's fix is correct.
- **SC7's instrument has real signal both ways** — `bd cook plan-investigate --dry-run` → `Steps (0)`
  (the vacuity case), `plan-execute` → `Steps (1)` with a titled gate step.
- **Zero stale citations, fourth pass running** — 21 re-checked and exact.
- All four mechanical checks green; `_verify_row`'s `UPSTREAM_REQUIREMENTS` confirmed mapping **both**
  `include` and `partial` to `requires_mention: True`, so 4.2's 5+2 comment count is right.

## Concerns

| Concern | Severity | Resolution |
| :-- | :-- | :-- |
| **C36 — SC4b was broken in BOTH directions: as written it cannot fail; corrected it cannot pass.** Run verbatim, the pattern returns **nothing, exit 1** — under `-E`, `\|` is an *escaped literal pipe*, so it matched the literal string rather than an alternation. An empty hit set is a subset of any row set, so **SC4b was unfalsifiable** — the M5 class this plan exists to close, inside its own criteria. Read charitably as a real alternation it returns **30 paths** against 8 enumerated rows, failing by 22 (fixtures, `plan_manager.py`, test files, nine `web/content/**` pages about other skills). The plan's claim that pass 3 "swept it and found the enumeration complete" was **measured false** | **high** | **Fixed, and the root cause addressed rather than the symptom.** The pattern moved **out of the table cell into a fenced snippet** — the table's `\|` escaping *was* the defect. New pattern measured end to end: `git grep -lniE 'never writes? (any )?files' …` → **exactly 7 paths**, five already rows; `agents/captor.md` and `spec/portability.md` added as explicit **NO-EDIT** rows (the *captor's* rule, a different agent). Added the **vacuity guard** SC4b alone lacked: the hit set must be **non-empty**. The narrower-phrase tradeoff is recorded rather than silently taken |
| **C37 — 1.2a still claimed an edit to `spec/agents.md:97`, the `Verification:` line 0.1 owns.** The identical double-ownership ambiguity pass 3 rated high as C30, on the **045** side: C30's carve-out was written into 1.2 and never propagated to 1.2a, which pass 3 rewrote in the same commit | med | **Fixed** — both mentions now read `:95` (REQ text + `Rationale:` only), mirroring 1.2's clause. Not fatal (`ctl-182-spike` keys off 043) but an executor following 1.2a literally would have wedged `ctl-165-executable`'s 045 case at 3.3, with gate `Instructions:` that could not diagnose it |
| **C38 — a literal containing a double quote is silently dropped by the positional parse**, and the self-check iterates the same parsed set so the dropped pair is invisible to it. `AGENTS.md:80` — where 1.2 sends the executor for wording — contains quoted fragments | low | **Fixed** — 1.1 now forbids double quotes in the chosen literals and requires `pairs-found` to equal the `grep -qF` count, failing **INCONCLUSIVE (exit 2)** otherwise |
| **C39 — 1.1 did not mandate the `pairs-found == 0 → fail` guard**, though 0.1 records the reason for it | low | **Fixed** — stated in conjunct (b): `pairs-found == 0` is a FAILURE, never a vacuous pass |
| **C40 — `change_validation.py` cited unqualified**, against 0.1's own rule that citations be path-qualified; it lives under `skills/yf-change-validation/`, not `skills/yf-plan/scripts/` | low | **Fixed** — both cites path-qualified |

## Missing

Nothing. C36 reopened C32's closure and is now genuinely closed by a measured pattern with a vacuity
guard.

**Self-injected during resolution, caught mechanically:** placing SC4b's fenced command before
`## Risks & Mitigations` put a `###` heading inside the `## Gates` section, and `plan_extract`
immediately reported **5 gates instead of 4**. Moved under `## Success Criteria`; back to 4. The
mechanical check caught in seconds what four prose passes are for.

## Gate Assessment

**Reachability sound for the fourth pass, and — for the first time — satisfiability HOLDS on
`ctl-182-spike`, verified by execution.** Graph properties clean per control; count derivation sound;
gate `Test:` shape byte-identical to plan-050's proven form.

The three prior failures were literal-vs-regex, whitespace, then ownership — each a different
*parser* choice on the same prose line. Pass 3 removed the parser choice instead of patching a fourth
reading, and that is why it worked: with the line reduced to a command, conjunct (b) has exactly one
legal shape. The only residual attack surface found is a double quote inside a literal (C38), which
degrades coverage but **cannot produce a false GREEN** — on the post-0.1 tree at least one pair is
always RED.

## Upstream Assessment

**Sound, no overclaiming.** All 11 issues re-verified OPEN with matching titles; #177 still OPEN.
Scope honesty holds on all four partials — #165 one-plan-scoped with 0.3 now recording the census
*with its pathspec* rather than shipping the unresolvable 251-vs-257 delta; #173/#174 each naming the
sub-case closed; #150 claiming two ranked classes, not the research. Both `include` rows wired to a
measured RED. Both out-of-scope defects route to 4.6 with C31's caveat recorded.
