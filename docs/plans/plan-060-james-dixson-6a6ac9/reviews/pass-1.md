---
type: Review
okf_spec: OKF-PLAN
description: 'Red-team pass 1 — VERDICT REVISE. Fourteen concerns, three high: 20 of 31 criteria are vacuous via the pytest argv-discard defect, SC30 is unsatisfiable by construction, and the tty gate rests on a herdr predicate that does not exist.'
---
# Review pass 1 — adversarial (red-team)

## Verdict: REVISE

**All 14 concerns resolved** by the main session; re-dispatched as pass 2.
**Date:** 2026-08-29
**Dispatched as:** sub-agent (REQ-AGENT-049), read-only with respect to the repository under review.
**Subject:** plan.md v1 (6 epics, 39 issues, 61 edges, 5 gates, 31 criteria), after the conformance
pass returned PASS.

> Note on scope: `findings/exp-006-conflict-handling.md` was written by the main session *during*
> this review, in response to operator input on apply-path conflict handling. It is not part of the
> version this pass reviewed, and the concerns below do not account for it.

## Strengths

- **The investigation is unusually honest about its own subject.** EXP-005 refutes the issue that
  commissioned it (#301's "structural" claim), files the residue as #304, and enumerates three
  mechanisms *each labelled with what it does not guarantee*. D-11/D-12 are the strongest work in
  the bundle. A plan about self-authorization that concludes "we cannot prevent this, here is
  detection instead" is the right shape.
- **D-2 / EXP-004 F1 is a real measured defect with independent corroboration.** Verified
  `4f4bd94`, `61ddbaa`, `c04b071` and the ancestry relation; `test_close_contract.py --list-steps`
  returns exactly the 12 steps cited. F7's refutation of #301 (steps 1–3 are not sequential;
  `close-reconcile-step` is a bead close REQ-COMPLETE-001 c2 *requires* first) is correct —
  confirmed at `spec/phases.md:94`.
- **D-6 is a genuine narrowing of what the agent must be trusted for.** `UPSTREAM_REQUIREMENTS`
  (`plan_manager.py:2676`) really is one shared table read by both `verify-reconcile` and `grant`,
  and it really does mechanically refute "close the upstream issues" for a `partial`-heavy plan.
- **D-1's substantive claim holds.** Grepped the whole `skills/` Python surface: no `git merge`,
  `pull` or `push` anywhere. `land --apply` genuinely would be the first such code.
- **The gate-reachability fix from the conformance pass held.** The first-merge-and-push gate's
  evidence (Issue 0.2) sits outside its `Blocks` set (3.5).
- `git merge-tree --write-tree` (Issue 1.2) is supported on this machine (git 2.50.1) — the
  dry-run-without-mutation design is buildable as specified.

## Concerns

| # | Severity | Concern | Recommendation |
| :-- | :-- | :-- | :-- |
| C1 | high | **20 of 31 criteria are vacuous by the exact mechanism `REQ-CLI-028` exists to forbid.** SC5–SC9, SC12–SC24, SC31 use `uv run … test_land_*.py -k <name>`. The house `__main__` shim is `pytest.main([__file__, "-q"])`, which **discards `sys.argv`**. Measured: `uv run skills/yf-plan/scripts/test_gates.py -k this_selector_matches_nothing_at_all` -> `22 passed`, **exit 0**. Issue 4.3 reasons about `-k <no-match>` exiting 5 — that is the *module* form; the criteria use the *direct-file* form, where the selector never reaches pytest. `scripts/checks/check-pytest-ran.sh` was written for precisely this, after three consecutive red-team passes of plan-056 found it. This is #224/#165's class authored into the plan whose subject is checks that cannot fail. | Rewrite every `-k` criterion as `bash scripts/checks/check-pytest-ran.sh <file> <test_name> -> exit 0`, add an Epic-0 issue requiring every new test file's `__main__` to use the forwarding form `pytest.main([__file__, *sys.argv[1:]])` (the `test_recheck_criteria.py:204` precedent), and add a criterion asserting the forwarding form is present in all three new files. |
| C2 | high | **SC30 is unsatisfiable by construction.** Its own verification string contains `'tier full'`, and it greps `plan.md` for that string: `grep -n 'tier full' plan.md` -> line **620, SC30's own row**. Measured with a non-empty record file present, the compound exits **1**. A criterion that can never pass is the mirror of one that can never fail, and it will halt `recheck-criteria` at L10 of this plan's own landing. Separately, `test -s <file>` is satisfied by one byte. | Move the forbidden-pattern check off `plan.md` (grep the Verification column only, or use a pattern that cannot appear in its own row). Replace `test -s` with a check that the record carries a dated duration line. |
| C3 | high | **The tty gate's allow-list is defeated by a first-class herdr verb, and its stated predicate does not exist.** (a) On `herdr api schema --json`, `human` occurs **0** times and `attached` **0** times — "a pane herdr reports as human-attached" is not a capability herdr has; the schema exposes a per-pane `tty` and nothing about who is at it. The gate degrades to "matching *any* herdr pane". (b) `herdr pane run <PANE_ID> <COMMAND>` exists and runs a command in a pane with a genuine pty. EXP-005 prices evasion at "`pty.fork()` in ~15 lines" and calls the act "unmistakable"; it is **one sanctioned tool call**, producing a pane tty in herdr's own list. EXP-005 F3 itself measured that `herdr agent list` needs no auth and that injected input is "indistinguishable from typing" — **the finding contains the refutation of the mechanism it recommends**. | Either (i) drop the herdr half, specify the gate as pure POSIX (refuse when `os.ttyname(0)` raises or `/dev/tty` is not openable), and remove "human-attached" from Issue 3.3 and REQ-PLAN-083; or (ii) keep an allow-list but make it **operator-configured** (not herdr-derived) and state in the SPEC that `herdr pane run` is a known bypass. Do not ship a predicate whose herdr precondition was measured absent. |
| C4 | medium-high | **The two-push "proof" (D-3 / F9) rests on a prose convention presented as a measurement.** Constraint (3) is `SKILL.md:1578` plus `reconciler.md`'s "See commit `<sha>`" template. Mechanically `UPSTREAM_REQUIREMENTS[include].requires_mention` requires a **plan-id**, not a SHA. Plan-060 itself authors the reconcile bodies, so it *controls* the constraint it treats as given. EXP-004 F9 admits this; plan.md D-3 drops the admission and asserts all four are "each independently measured". Consequence: **push #1 at L5 puts the merge on `main` before L9 `verify-reconcile` and L10 `recheck-criteria`**, so the headline property "L3 precedes every irreversible step" is false for the plan's own criteria check. | Restate D-3's constraint (3) as a *convention this plan adopts*, and record the rejected single-push alternative. Independently, hoist `recheck-criteria` to run on the merged tree **before** L5's push. If two pushes are kept, say explicitly that L5 is irreversible and that L10 failing means `main` already carries the merge. |
| C5 | medium | **L1/L2 leave the address space, the conflict path, and F5's precondition unspecified.** L1 down-merges "in the worktree"; L2 does `git checkout <target>`, which `SKILL.md:1462-1464` says must be primary-side. `--apply` is typed by the operator in their own shell — the plan never says from which checkout. No step handles a **down-merge conflict** and no journal state covers it. F5's tree-equality guarantee is explicitly conditional ("only for the window in which nothing else lands"); L2's `pull --rebase` can pick up commits arriving after L1's fetch, and the lock is single-machine. plan.md drops the caveat and asserts L1 "is what makes L10 honest" unconditionally. | Declare the cwd contract for `--apply` in `spec/landing.md`, and have `--dry-run` emit the fully-qualified command including the checkout it must run from. Add to 3.5 a conflict path with its own journal state, and a post-L2 assertion that the merge result's tree matches the down-merged branch tree. |
| C6 | medium | **SC28 is vacuous.** Measured: `change_validation.py run --tier fast --changed zzz/nonexistent_totally.py --json` -> `status: pass`, **0 commands**, exit 0. And for `test_land_apply.py` it already selects 21 commands *today*, before any registration, because a pre-existing broad `skills/yf-plan/scripts/**` glob matches. The criterion cannot distinguish "registered" from "matched by a pre-existing glob" from "nothing selected". | Assert the specific row id is present in the selected set. |
| C7 | medium | **The outward-write gate's `Condition` and `Test` describe different things, and it gates the wrong nodes.** The Condition names the decision document's `upstream_writes` — an artifact produced at **landing time**, downstream of the issues (3.6, 3.9) it Blocks. The Test checks plan-060's *own* reconcile grant (exits 1 today, satisfiable now). So the Condition as literally written has the self-satisfaction shape the conformance pass fixed elsewhere; read as the Test intends, it authorizes a runtime act in order to permit *writing code*. The Redeploy gate has the same defect (Blocks 3.11, the issue that *implements* redeploy). | Restate both Conditions to match their Tests: the outward-write gate authorizes plan-060's own reconcile writes and should Block the reconcile step; the redeploy gate should Block the landing's L18, not Issue 3.11. A per-landing grant belongs in `spec/landing.md` as a runtime precondition of `--apply`, not as a plan gate. |
| C8 | medium | **Issue 3.9 as written is not executable.** "routing every write through `/yf-beads-upstream`" — that is a **prose skill for an LLM**; `land --apply` is Python and cannot invoke it. The callable surface is `upstream.py push --issues <csv> --apply` (which also already has a `land` subcommand — the collision R6 names). Compounding: per `UPSTREAM_TRACKING.md` the push is **confirm-required by default**, and #280 makes the narrow auto-eligible set permanently empty, so the non-interactive path this verb needs does not exist. | Rewrite 3.9 to name `upstream.py push --issues <csv> --apply` concretely, and specify in `spec/landing.md` how L16 obtains confirmation — either covered by the batched grant (cite `_grant_coverage`) or L16 is **propose-only**. |
| C9 | medium | **Issue 3.10 contradicts `REQ-BRANCH-004`.** It says "delete the branch local and remote" flatly. `spec/phases.md:63`: under `feature-branch`, teardown deletes only `<plan-id>-execute` and **preserves** feature `<plan-id>`. | Amend 3.10 to delete `<plan-id>-execute` only and consult `_resolve_landing_strategy`; add a criterion that a `feature-branch` fixture leaves `<plan-id>` intact. |
| C10 | medium | **Epic 3 is not one epic's worth of work, and its DAG is a 7-deep serial chain.** 12 issues covering the first merging and pushing code, an fsync'd journal, a tty gate, a route record plus an `audit-close` change, and eight landing-step groups — with `3.5 -> … -> 3.11` fully serial and 3.12 depending on all seven. Nothing parallelizes; a single mid-chain revision re-opens everything downstream. | Split into Epic 3a (mechanism: 3.1–3.4, mostly parallel) and Epic 3b (the ordered steps). Give per-mechanism test issues rather than one terminal 3.12. Consider deferring L18 (redeploy) — the only step mutating the machine outside the repo. |
| C11 | low-medium | **Cited figures drift from the repository.** (a) D-1 and the first capability gate say **17** `_run_git` call sites; measured **20**, plus further direct `subprocess.run(["git", …])` sites a reader would count as the git surface. (b) EXP-004 F6 cites `SKILL.md:1707`/`:1712`; they are at **1662** and **1672**. (c) context.md says the FULL tier is 58 rows; measured **57** (fast = 59 correct). The substantive claims all survived re-measurement — the numbers did not. | Re-measure and correct all three, and state D-1's scope precisely ("call sites of the `_run_git` helper"). Given #289, consider an Epic-0 issue that re-runs each cited command and diffs the figure. |
| C12 | low | **Four more criteria are weaker than their prose claims.** SC3 claims `landing.md` defines the family, the 18-step order and the journal state table, but is discharged by a single `REQ-LAND-001:` line. SC27 (`grep … -> exit 1`) is equally satisfied by **deleting** the §6.4 block, which Issue 4.1 may do. SC29 is discharged by strings in a file the session itself writes — self-attestation, in the plan built to eliminate self-attestation. SC21's prose says "after a complete rehearsal landing" but its verification is a unit test. | SC3: add positive greps for the 18 step labels and journal state names. SC27: pair with a positive grep. SC29: derive from the harness's own output, or mark it self-attested. SC21: reword to match what the test proves. |
| C13 | low | **Upstream table / annotation mismatch.** The table gives #304 `Resolved By: 0.6, 3.3, 3.4`, but 3.3 and 3.4 carry `resolves-upstream: #293 (partial)` and no #304 annotation. | Add `resolves-upstream: #304 (partial)` to 3.3/3.4, or trim the table. |
| C14 | low | **The landing halt is a class-1 stop reached by prose, and `REQ-AGENT-064` says no halt is.** The plan is nonetheless right that this is class 1 — `SKILL.md`'s write-site table states class 1 has no write site because every instance is a designed consent gate. But REQ-AGENT-064's closing clause ("every stop class is an exit code or a counter") is falsified by class 1 as documented, and the plan inherits the tension silently: a green `land --dry-run` exits 0, so the stop is prose. | Have REQ-COMPLETE-005 record the class-1 exception explicitly and cite the write-site table. Give `--dry-run` a distinct exit code or a `halt_class: 1` manifest field so the stop is mechanically signalled. |

## Missing

- **No conflict path anywhere** — down-merge (L1), merge (L2), push rejection (L5/L15). EXP-004
  mentions "the rejection path already mandates re-validation" but no issue implements it and no
  journal state covers it.
- **No statement of the `--apply` invocation contract** — which checkout, which cwd, what happens if
  the worktree was already torn down, whether `--apply` may be re-run after partial failure.
  `assets/decision-schema.md` lists the last as open question 3 and no issue closes it, yet
  `recover()` (3.1) presupposes an answer.
- **The journal state set is never enumerated in the plan**, only referred to. SC31 asserts the
  runbook names every state "defined in `spec/landing.md`" — but 0.2 does not commit to a state set,
  so the criterion is checkable only against whatever 0.2 happens to write.
- **Nothing verifies the read-only `lander` was actually read-only.** REQ-AGENT-065's Verification is
  a `grep -qF` for two sentences — that checks the *instruction*, not the behaviour.
- **No mention of `REQ-CLI-028` or `check-pytest-ran.sh` anywhere in the bundle** (zero hits). That
  absence is the direct cause of C1.

## Gate Assessment

Four gates plus the Start Gate. **First merge-and-push authorization** (Blocks 3.5, `Test: none`) is
**reachable and correctly placed** — its evidence (0.2) sits outside its Blocks set and its
Instructions honestly state that no command can establish the authorization. **This is the plan's
best gate.** **Outward-facing write authorization** — C7: Condition and Test describe different
objects, and the Condition as literally written depends on an artifact produced downstream of its own
Blocks set. Its Test does work (exit 1 today, satisfiable now), so this is a wording defect rather
than an unreachable gate — but it must be fixed, because the Condition is what the operator reads.
**Redeploy authorization** — same misplacement, and it is the one gate whose subject
(`yf self install`) AGENTS.md forbids during execution; the plan should say who runs it and when
relative to Epic 5's rehearsal. No frontloading misses: none of the three could be hoisted earlier.

## Upstream Assessment

Dispositions are careful and the exclude rationales specific (#287's "four live readings, two of them
'do nothing'" is a good refusal). Two notes. **#301 is dispositioned `include` -> will be CLOSED**,
but EXP-005's own recommendation 5 is *"file the residue so #301 cannot close claiming a fix it does
not deliver"*, and D-11 concludes the issue's central claim is false. Closing it while filing #304 is
defensible, but the reconcile body should say #301 is closed **as amended**, not as written.
**#204's partial is honest** — the harvest-before-prune subset is buildable without provenance and
propose-by-default is the right answer to an unanswerable predicate. **#280's deferral is not neutral
for L16** (C8): "delegate rather than reimplement" is only complete if the delegated path can run
non-interactively, and #280 says the one auto-eligible path is permanently empty. That deferral does
make an in-scope item under-specified.

## Resolutions

| Concern | Severity | Resolution | Actor | Status |
| :-- | :-- | :-- | :-- | :-- |
| C1 — 20 of 31 criteria vacuous (pytest argv discard) | high | **Accepted and adopted.** Verified independently: `uv run test_gates.py -k this_selector_matches_nothing_at_all` -> `22 passed`, exit 0. New **Issue 0.9** mandates the forwarding `__main__` (`pytest.main([__file__, *sys.argv[1:]])`) for all three new test files and routes every test-backed criterion through `scripts/checks/check-pytest-ran.sh <file> <test>`. All 27 affected criteria rewritten. New **SC2b** asserts the forwarding form is present. **R4** records the failure rather than hiding it. | `main-session` | `resolved` |
| C2 — SC30 unsatisfiable by construction | high | **Accepted.** Reproduced: with a non-empty record file present the compound still exits 1. SC30 is retired; the durable half is now **SC37**, `grep -qE '^- \*\*duration_s:\*\* [0-9]+'` against the record file — a positive assertion with no self-reference, replacing both the self-defeating grep and the one-byte `test -s`. | `main-session` | `resolved` |
| C3 — tty gate predicate absent; `herdr pane run` bypass | high | **Accepted in full — option (i).** The herdr half is withdrawn. Approach §2 and **Issue 3.3** now specify the gate as pure POSIX (`os.ttyname(0)` raises, or `/dev/tty` unopenable), state that `herdr api schema --json` contains zero `human`/`attached`, make any allow-list operator-configured rather than herdr-derived, and name `herdr pane run` as a KNOWN BYPASS in code and SPEC. **SC17** asserts the POSIX-only property. The concern that EXP-005 contained the refutation of its own recommendation is correct and is recorded in the finding's own terms. | `main-session` | `resolved` |
| C4 — two-push constraint (3) is convention, not measurement | medium-high | **Accepted, both halves.** D-3's constraint (3) is restated as a **convention this plan adopts**, on the honest ground that a reconcile comment asserting work shipped is *false* while the merge is unpushed — not on the SHA-citation reading, which pass 1 correctly demolished; the rejected single-push alternative is recorded. The overclaim is removed: the Approach and **Issue 4.3** now state plainly that **L5's push is the first irreversible step** and that every later halt leaves `main` carrying the merge. New **L4.5 / Issue 4.2** adds an advisory criteria run on the merged tree before the push. **R7** carries the residual risk. | `main-session` | `resolved` |
| C5 — L1/L2 address space, conflict path, F5 caveat | medium | **Accepted.** **Issue 0.2** must now enumerate the `--apply` invocation contract (checkout, cwd, resumability) and the conflict contract, not refer to them; **Issue 1.7** makes `--dry-run` emit the fully-qualified command including the required checkout (**SC11**); **Issue 3.5** adds the conflict path with its own journal states; **Issue 4.1** adds the post-merge tree assertion for a down-merge invalidated by `pull --rebase`. The F5 caveat is restated in the Approach's conflict section rather than dropped. | `main-session` | `resolved` |
| C6 — SC28 vacuous | medium | **Accepted.** Old SC28 retired. **SC35** now asserts the specific row ids are present in a scoped `run`, via a test, rather than relying on a `pass` that a pre-existing broad glob already produces. | `main-session` | `resolved` |
| C7 — outward-write and redeploy gates mis-worded and mis-placed | medium | **Accepted.** Both gates restated so Condition matches Test. The outward-write gate now authorizes **this plan's own** reconcile writes and Blocks `reconcile step`; the redeploy gate likewise. The per-landing grant and the runtime redeploy authorization move into `spec/landing.md` (Issue 0.2) as runtime preconditions of `--apply`, which is where a landing-time artifact belongs. | `main-session` | `resolved` |
| C8 — Issue 3.9 not executable | medium | **Accepted.** **Issue 4.7** now names `upstream.py push --issues <csv> --apply` concretely, states that `/yf-beads-upstream` is a prose skill Python cannot invoke, and makes L16 **propose-only unless the batched grant demonstrably covers it** — with that decision required in `spec/landing.md` rather than left implicit. **R10** carries the risk. #280's deferral is no longer treated as neutral. | `main-session` | `resolved` |
| C9 — Issue 3.10 contradicts REQ-BRANCH-004 | medium | **Accepted.** **Issue 4.8** deletes `<plan-id>-execute` only and consults `_resolve_landing_strategy`; **SC29** asserts a `feature-branch` fixture retains `<plan-id>`. | `main-session` | `resolved` |
| C10 — Epic 3 oversized, 7-deep serial chain | medium | **Accepted.** Epic 3 split into **Epic 3 (mechanism**: journal, digest binding, tty gate, route record, conflict contract, re-preview — largely parallel) and **Epic 4 (the ordered steps** L0-L18). Per-epic test issues (3.7, 4.10) replace the single terminal test issue. Epics 4/5 renumbered to 5/6 and every `depends-on`, `Resolved By` and `Discharged-by` reference updated; `plan_extract.py --strict` re-verified at 0 unparsed and 0 dangling edges. | `main-session` | `resolved` |
| C11 — cited figures drift | low-medium | **Accepted; all three corrected.** `_run_git` call sites 17 -> **20**, with the scope stated precisely as "call sites of the `_run_git` helper" and the direct `subprocess.run(["git", …])` sites noted separately. `SKILL.md:1707`/`:1712` -> **:1662**/**:1672** (also corrected upstream on #303). FULL tier 58 -> **57** rows in both `context.md` and EXP-003. Each correction is marked in place rather than silently overwritten. New **Issue 0.10** builds the #289 re-measurement instrument, discharged by **SC5**. | `main-session` | `resolved` |
| C12 — four criteria weaker than their prose | low | **Accepted.** SC3 now asserts `spec/landing.md` enumerates the family, all nineteen step labels and the journal state set by name. SC27's negative grep is replaced by a **positive** `grep -qF 'HEAD^1..HEAD'` (**SC34**) — and the main session's own verification found the old pattern could never match the real text, so it was already passing before any fix; recorded upstream on #303. SC29's self-attestation is replaced by a test over the rehearsal harness's own output (**SC36**). SC21's prose reworded to match what its test proves. | `main-session` | `resolved` |
| C13 — upstream table / annotation mismatch for #304 | low | **Accepted.** `resolves-upstream: #304 (partial)` added to Issues 3.3 and 3.4; the table's Resolved By for #304 now reads `0.6, 3.3, 3.4` consistently with the annotations. | `main-session` | `resolved` |
| C14 — class-1 halt reached by prose | low | **Accepted.** **Issue 0.5** now requires REQ-COMPLETE-005 to record the stop-class-1 exception explicitly, citing SKILL.md's write-site table (which already states class 1 has no write site). **Issue 1.6** adds a `halt_class` field to the manifest envelope, so the session's stop is mechanically signalled rather than judged from prose. | `main-session` | `resolved` |
