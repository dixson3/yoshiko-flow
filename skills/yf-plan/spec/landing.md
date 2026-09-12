# Landing specification (`REQ-LAND-*`)

The `land` verb and the `lander` agent: the capability that takes a plan from "the work is done
on `<plan-id>-execute`" to "merged, pushed, reconciled, closed, pruned and redeployed" **on one
informed consent grant**. This file owns the `REQ-LAND-*` family — twenty-two ids since plan-071
rewrote it from thirty-nine (the merge map is that plan's root `SPEC.md` amendment entry). Each
id states a forward requirement and a `Verification:` naming an existing test; defect narrative
lives in the issues cited. **Not to be confused with `upstream.py land`**, the follow-on hoist.

## 1. The three-layer split

REQ-LAND-001: Landing shall be performed by **three separate layers**, and the middle layer
shall have no write authority.

| Layer | Produces | Authority |
| :-- | :-- | :-- |
| `plan_manager.py land --dry-run` | the **manifest** — facts, exit codes, merge preview, every enumerated write with its body | reads only |
| the `lander` agent (`agents/lander.md`) | a **decision document** — a data structure, never commands | read-only with respect to the repository under review (REQ-AGENT-065) |
| `plan_manager.py land --apply <decision.json>` | the **execution** | the only layer that writes |

Rationale: an agent that both decided and acted would hold write authority over `main`, the
upstream tracker, the worktree set and the installed toolchain — the highest-privilege role in
the system. dixson3/yoshiko-flow#293 is an executing agent closing a consent gate by writing its
own authorization into the close reason; a land agent with write authority is that defect at
larger scale.
Verification: `uv run skills/yf-plan/scripts/test_land_apply.py` — the decision schema carries no
field in which a condition, an exit code or a consent can be asserted.

REQ-LAND-002: **Facts are re-derived; the decision supplies judgements only.** `--apply` shall
trust the decision document for grouping, prose bodies, which rows may close and per-step
enable/skip — and for **no fact whatsoever**. Every fact is re-derived at apply time, and every
fact in the digest's **coverage set** is checked against the decision's `manifest_digest`; a
mismatch is a **staleness halt** reporting the digest, never an override and never a bare
conflict. Four clauses:

1. **Narrowing only.** An `enable` on a step the manifest halted is ignored and reported; a
   `skip` requires a reason and is surfaced in the consent prompt. There is no field in which
   the agent can assert an authorization, and only the verb closes gates.
2. **An omission from enumeration is not a `skip`.** Only writes the manifest enumerated and
   then declined are surfaced; a write it never saw is silent. Enumeration uses git plumbing.
3. **The coverage set excludes landing-mutated facts**, exhaustively `execute_worktree_present`
   and `execute_worktree_dirty` (L18 flips both); the exclusion is recorded in the manifest and
   the test asserts both directions (an excluded flip leaves the digest equal; a
   `primary_checkout_dirty_outside_plan_dir` flip changes it). The digest covers the merge
   preview (`predicted_tree`, target tip), which is what makes a moved target detectable.
4. **AMBIENT HEAD IS NOT A FACT.** **L1 shall check out `ctx.execute_branch` explicitly** and
   halt if that fails, rather than merging into whatever HEAD is (dixson3/yoshiko-flow#331:
   in-place, an ambient-HEAD L1 self-merged and reported `pass`).

Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_narrowing_only`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_enumeration_uses_git_plumbing`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_digest_survives_resume_after_teardown`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_digest_covers_merge_preview`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_inplace.py test_l1_operates_on_the_execute_branch_not_ambient_head`.

## 2. The order

REQ-LAND-004: A landing shall execute **20 logical steps, L0 through L19, carried by 15
`LAND_EXECUTOR` keys** (L8–L11 are one key, `l8_close_chain_head`; L13–L15 are one key,
`l13_complete_gate`), **in this order**. The order is normative: each row carries the edge that
forces its position, and no step may be reordered without retiring the edge that pins it.

| Step | Action | The edge that forces this position |
| :-- | :-- | :-- |
| **L0** | `landing-lock acquire` | Merge-back is serialized per machine; the lock precedes the first tree mutation or two landings interleave. Always re-executed on a resume (REQ-LAND-011). |
| **L1** | `git fetch`; check out `<plan-id>-execute` explicitly; **down-merge** the target into it | Makes the branch tree byte-identical to the merged tree, so L11's criteria measurement and "the tree that will be on the target" are one tree. |
| **L2** | checkout target; `pull --rebase`; `merge --no-ff` — **left uncommitted** | The merge must exist as a tree before L3 validates it, and stay uncommitted so a red L3 has something to fail closed onto. `--no-ff` keeps the landing one revertable commit. |
| **L3** | `validate-merged` — **FULL tier** — **HALT WITH THE LOCK HELD** on fail | plan-009 INV-4: the FULL tier runs before anything irreversible, and the lock stays held so the operator repairs under serialization. |
| **L4** | commit the merge; `landing-lock release` | The base is green; holding the global lock across the remaining steps would serialize them needlessly. |
| **L5** | **ADVISORY** `recheck-criteria` on the merged tree — never halting | The last fully reversible point; the authoritative run is L11. |
| **L6** | **PUSH #1** | **The first IRREVERSIBLE step.** After L3 so what reaches the target is validated. **Every halt after L6 leaves the target already carrying the merge**, and the halt report shall say so; that is acceptable because L3 validated the code, and the later halts concern bookkeeping and upstream state, each repairable without a revert. |
| **L7** | reconcile writes — `gh` comment/close, each verified by read-back (REQ-LAND-019) | **The first OUTWARD-FACING write.** After the push so the commits its comments reference are visible upstream. |
| **L8** | close chain steps 1–5, with `CHANGED` computed as **`HEAD^1..HEAD`** — never `<target>...HEAD`, which is empty by construction once `HEAD == <target>` and makes `classify-deliverable`'s `path-backed` evidence unreachable (dixson3/yoshiko-flow#303) | The merge's first-parent range is what actually landed. |
| **L9** | `close-reconcile-step` | REQ-COMPLETE-001 constraint 2: the reconcile gate is resolved before the reconcile bead closes. |
| **L10** | `verify-reconcile` — **halting** | After the reconcile bead closes and before the first destructive step: the only window where §6.3 is done and nothing has been torn down. |
| **L11** | `recheck-criteria` on the merged tree — **halting** | Same window, same reason. The authoritative run. |
| **L12** | `close_cascade.py` | **The first destructive step.** Refuses any container with a non-terminal child; never force-closes an unmet gate. |
| **L13** | `complete-gate` | After cascade-close, before `complete` (REQ-PLAN-069). |
| **L14** | `pour_fidelity.py` | The executed DAG must be the declared DAG before the plan may claim completion. |
| **L15** | `update-status complete` | REQ-COMPLETE-001: last, and the sole status writer. |
| **L16** | commit the plan-folder writes (REQ-LAND-032); **PUSH #2** | Without it every landing ends with an uncommitted, unpushed `plan.md`. |
| **L17** | mirror residual open beads upstream, grouped per the decision (REQ-LAND-021) | Needs the plan-folder state pushed at L16 visible, so a mirrored bead's references resolve. |
| **L18** | prune — worktree, branch (local + remote), herdr tab | Nothing is pruned before L16 has pushed everything that lived on the branch. **Strategy-aware:** L18 consults `_resolve_landing_strategy` and deletes `<plan-id>-execute` **only**; under `feature-branch` the feature `<plan-id>` branch is preserved (REQ-BRANCH-004). **Non-forcing:** L18 shall call `_worktree_teardown` with `force=False` in **keyword** form (the keyword is normative so a signature change fails loudly), shall issue no `git branch -d` of its own, and shall **branch on the returned `status`** — a `blocked` teardown is a non-`pass` step, and a mapping with no `status` key is `inconclusive`, never `pass`. The herdr tab is closed only under dixson3/yoshiko-flow#204's mechanical preconditions and only for an explicitly supplied tab id; the default is to **propose**, and any close is verified by reading back the agent list. |
| **L19** | redeploy **iff** the landing touched `skills/` (REQ-LAND-022) | The only step that mutates the machine outside the repository. Last, because a half-deployed session runs new scripts against old prose. |

**L2 IN-PLACE IS A DECLARED SCOPE BOUNDARY.** Under `execute.worktree: false` there is one
address space: L2 runs `git checkout <target>` **in `ctx.root`** — the execute checkout itself —
and the following `git pull --rebase`'s return code is **ignored**. Both are recorded as facts
about the current implementation; the work is routed to **plan-069**.
Rationale: plan-060 EXP-004 proved no single-push order satisfies all four landing constraints,
so the order is two-push by necessity.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_landing_spec_enumerates_steps_and_journal_states`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_push_one_is_gated_and_declared_irreversible`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_changed_set_nonempty`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_prune_is_strategy_aware`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_l18_blocked_teardown`.

## 3. The journal

REQ-LAND-006: `land --apply` shall maintain an **fsync'd journal** with the state set enumerated
below. The set is **closed and normative**: tests bind to *this* list, not to whatever an
implementation happens to write. The model is `okf_hygiene.py backfill`'s (`REQ-OKFH-008`),
extended in one way: **one state per conflict site**, of which there are **four**.

### 3.1 Progress states

| State | Meaning | Reached after |
| :-- | :-- | :-- |
| `L_INIT` | journal created; nothing acquired, nothing mutated | — |
| `L_LOCKED` | landing lock held; no tree mutated | L0 |
| `L_DOWNMERGED` | target down-merged into `<plan-id>-execute` | L1 |
| `L_MERGED_UNCOMMITTED` | merge present on the target, **uncommitted** | L2 |
| `L_VALIDATED` | FULL tier green; merge committed; lock released | L3, L4 |
| `L_PREPUSH_CHECKED` | advisory criteria run complete — **the last fully reversible state** | L5 |
| `L_PUSHED_1` | **push #1 done — the irreversible boundary has been crossed** | L6 |
| `L_RECONCILED` | every enumerated `gh` write posted and verified by read-back | L7 |
| `L_CLOSED` | close chain L8–L15 complete; `status: complete` written | L8–L15 |
| `L_PUSHED_2` | plan-folder writes committed and pushed | L16 |
| `L_MIRRORED` | residual open beads mirrored or proposed | L17 |
| `L_PRUNED` | worktree, branch and (if authorized) tab pruned | L18 |
| `L_DONE` | redeploy performed or correctly skipped — **the terminal GREEN state** | L19 |

### 3.2 Conflict states — one per site, and there are exactly four

| State | Site | Recovery |
| :-- | :-- | :-- |
| `L_CONFLICT_DOWNMERGE` | **L1** down-merge | capture, then `git merge --abort`; fully local, no outward trace |
| `L_CONFLICT_MERGE` | **L2** merge | capture, then `git merge --abort`; fully local, no outward trace |
| `L_REJECTED_PUSH_1` | **L6** push #1 rejected | `pull --rebase`, **re-validate**, retry; still pre-outward-write |
| `L_REJECTED_PUSH_2` | **L16** push #2 rejected | `pull --rebase` and retry — **NEVER revert**: by L16 the comments are posted, the bead tree is closed and `status: complete` is written, so a revert would contradict outward statements already made |

Three durability clauses: the journal is **written with `_fsync_write`** (`O_CREAT|O_TRUNC`,
`fsync(fd)`, `fsync(dirfd)`) and staged **inside the repository tree**, never in a `mktemp -d`
(another filesystem turns `os.rename` into a copy); **`recover()` is keyed on the recorded
phase**, never on observed state, and is **total** over the state set ("wrote nothing" and
"wrote everything then died" are indistinguishable from observed state); and
**`L_REJECTED_PUSH_2` is the only post-outward-write conflict state** — the four sites do not
all sit on the same side of the irreversible boundary.
Rationale: a five-state journal and a five-state test can be five *different* fives with every
instrument green.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_journal_recovery_every_state`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_conflict_matrix_covers_four_sites_and_staleness`.

## 4. The `--apply` invocation contract

REQ-LAND-010: `land --apply <decision.json>` shall be invoked **from the PRIMARY checkout**
(never `.worktrees/<plan-id>` — L2 checks out the merge target, which a linked worktree cannot
hold), **with cwd at the repository root** (`plan_dir` is cwd-relative throughout), and **by the
operator in their own shell** (REQ-LAND-013). `land --dry-run` shall emit the fully-qualified
command naming that checkout. The `--apply` branch of `land_cmd` shall invoke `_land_execute`; a
CLI that does not reach the executor is non-conformant however well the executor is tested
(dixson3/yoshiko-flow#327).
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_apply_command_is_fully_qualified`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_seam_reaches_executor`.

REQ-LAND-011: **A partial failure is resumable, and a resume never re-executes a completed
step.** Re-invoking `land --apply` with the same decision file shall read the journal, resume
from the recorded phase, re-derive every fact per REQ-LAND-002 (halting as a staleness report
when the coverage-set digest no longer matches), and **skip every step whose journal state has
already been reached**, marking each skipped step explicitly in `results` with a `resumed`
marker so a skip is observable rather than inferred from an absence. Two constraints: an
`LAND_EXECUTOR` key with no `LAND_STEP_JOURNAL` entry **resolves FORWARD** — done only when the
next journaled step's state is in `reached` (backward resolution would mark L3 done after a halt
at L3 and skip validation); and **L0 is exempt and always re-executes**, because the lock is
released at L4 and a uniform skip would run L1–L4 unlocked then `unlink` a lock never acquired
(same-host dead-PID locks are reclaimed, which also heals the resume-from-L5 asymmetry).

Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_resume_skips_completed`.

REQ-LAND-012: `land` shall register as a **flat** `@cli.command`, never a command group, and
shall use three-valued verdicts (`pass | fail | inconclusive`) throughout, with a `halt_class`
field in the REQ-COMPLETE-003 envelope so a session's stop is mechanically signalled. An
`inconclusive` of `land`'s own shall **never** be coerced to `fail`. (The `recheck-criteria`
clause grammar is binary: `-> exit 0` reads an instrument's `2` as criterion FALSE.)
Verification: `uv run skills/yf-plan/scripts/test_cli_enumeration.py`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_inconclusive_not_laundered`.

## 5. Consent — what is withheld, what is gated, what is merely recorded

REQ-LAND-013: **The session does not get the verb.** A yf-plan session shall run `land --dry-run`
and dispatch the `lander`, then **stop** — a declared stop-class-1 halt — printing the exact
`land --apply` command for the operator to run in their own shell. The session shall not invoke
`land --apply`.
Rationale: this is the only genuinely structural row of the consent model, and its guarantee is
the **absence of the capability**. It dies the moment a future rule adds the capability back,
which is precisely why it is paired with REQ-LAND-014.
Verification: `uv run skills/yf-plan/scripts/test_close_contract.py --assert-invocation land`

REQ-LAND-014: `land --apply` shall refuse without a controlling terminal. The predicate shall be
**pure POSIX**: refuse when `os.ttyname(0)` raises **or** `/dev/tty` is not openable. The refusal
shall exit **3** — the gate-signal code, not `1` (a criterion measured false) and not `2` (the
instrument could not run) — with a legible reason.

**This is not prevention, and the requirement says so in its own text.** `herdr pane run <pane>
<cmd>` runs a command in a pane with a genuine pty, in **one sanctioned tool call**; it is named
here as a **known bypass**. The gate converts self-authorization from a *rationalizable* act into
an *unmistakable* one, and nothing more.

Any allow-list shall be **operator-configured**, never herdr-derived: `herdr api schema --json`
contains **zero** occurrences of `human` and **zero** of `attached`, so "a pane herdr reports as
human-attached" is not a capability herdr has, and such a predicate would degrade to matching
*any* herdr pane.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_tty_gate_refuses_and_is_posix_only`

REQ-LAND-015: A **route record** — the controlling tty or its absence, `CLAUDECODE`/entrypoint
presence, pid and sid — shall be stamped at the two sites that exist: on every journal write
of `land --apply`, and on the envelope of a tty-gate refusal. **This is detection, not prevention.**
The markers are strippable, and useful because they are strippable *asymmetrically*: a clean
record is weak evidence of a human, a dirty one strong evidence of an agent. The record never
captures a value, only presence. *(Narrowed by plan-071 from a per-gate-close stamp no writer
ever produced — dixson3/yoshiko-flow#393, closed by subtraction.)*
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_route_record_detects_agent`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_journal_recovery_every_state`.

## 6. The conflict contract

REQ-LAND-017: On a conflict at **any** of the four sites of REQ-LAND-006 §3.2, `land --apply`
shall:

1. **Never auto-resolve.** No `-X ours`, no `-X theirs`, no strategy override, no heuristic. Each
   silently discards one side's work, and the discarding is invisible in the resulting commit.
   The verb has no basis for choosing; the agent, holding the plan and both diffs, at least has
   one.
2. **Capture from three independent sources** — `git diff --name-only --diff-filter=U` for the
   path list, `git status --porcelain=v2` for per-path stage detail, and `MERGE_HEAD` for the
   incoming commit.
3. **Write that site's own journal state** (REQ-LAND-006 §3.2), never a generic one.
4. **Halt with the whole picture handed back**, and apply that site's recovery — which is *not*
   uniform across the four.

Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_conflict_captured_and_restored`

REQ-LAND-017a: **No landing step shall issue a history-rewinding git command that takes a
TARGET REVISION** — no `reset`, no `revert`, no `cherry-pick`, no forced push. The only
history-affecting operation permitted on the recovery path is `git merge --abort`, which takes
no revision argument. Rationale: a rewind target is defined by what it **preserves**, never by
what it drops, and an executor computing one would err with the operator's authorization already
attached. The landing path contains zero occurrences of these verbs, and the test pins it.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_no_target_taking_rewind_in_landing_path`

## 7. Verification of writes, runtime preconditions

REQ-LAND-019: Every outward-facing write and every bead close performed by `land --apply` shall
be verified **structurally, by read-back** — `gh issue view` after a `gh` write, `bd show` after a
`bd close` — never by exit code and never by a returned URL alone.
Rationale: `bd close` **refuses and exits 0** when the bead is blocked by an open dependency
(dixson3/yoshiko-flow#230), and an exit 0 from `gh` does not establish that the body posted is the
body intended — measured on issue #292 during plan-060's own drafting.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_readback_catches_wrong_body`

REQ-LAND-020: `land --apply` shall be **fail-closed at every edge**: the first unverified write
aborts before any destructive stage is reachable, a post-condition runs on the way out, and **a
post-condition shall be able to see what the step did** (REQ-LAND-032 is the L16 instance).
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_close_chain_exit_codes_read`

REQ-LAND-021: **The per-landing upstream grant.** Step L17 mirrors residual open beads upstream by
calling `upstream.py push --issues <csv> --apply` **concretely** (Python cannot invoke the
`/yf-beads-upstream` prose skill). That push is confirm-required and dixson3/yoshiko-flow#280
leaves the auto-eligible set empty, so **L17 is propose-only unless the batched grant demonstrably
covers the specific bead set** — each bead id enumerated in the decision and named in the grant.
Otherwise L17 emits the proposed invocation and performs no upstream write.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_residual_mirroring_is_concrete_and_gated`

REQ-LAND-022: **The redeploy precondition.** Step L19 shall run `yf self install --from-build
--build` **if and only if** the landed change set touches `skills/`, and only when the decision
document enables the step; never mid-execution. Rollback is asymmetric — `yf harness tune
--revert` restores config but **deletes** the rules aggregate (dixson3/yoshiko-flow#154) — and
the operator authorizing the step is told so.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_redeploy_iff_skills_touched`

## 8. The dry-run contract

REQ-LAND-026: `land --dry-run` shall **mutate nothing** — `git status --porcelain` is empty after
it and no bead is mutated; the merge preview's `git merge-tree --write-tree` does create an
unreferenced object-database tree object, recorded here so no criterion claims the dry run
"writes nothing at all". It shall report each of the following as a **halting finding**:

- **A plan-number collision on the merge target** — two bundles sharing an `NNN` merge cleanly
  (dixson3/yoshiko-flow#302), so merge-back is the only place it is detectable.
- **A primary checkout dirty outside the plan folder**, via the single `_dirty_outside_plan_dir`
  helper of REQ-LAND-032; dirt inside the plan folder is what L16 stages and is not a finding.
  A halt here costs one `git stash`; the L16 failure it predicts costs a landing wedged at
  `L_CLOSED` (dixson3/yoshiko-flow#333).

Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_dry_run_does_not_mutate`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_number_collision_halts`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_dryrun_halts_on_dirty_primary`.

## 9. Step dispatch, L16, the seam, and the preview

REQ-LAND-030: **Step dispatch is fail-closed.** An exception raised by a `LAND_EXECUTOR` step
shall be caught at the dispatch site and reported as a **halting `inconclusive` step** — verdict
`inconclusive`, `halting: true`, `journal: null` — never as a traceback, and the halted envelope
shall be returned directly from the handler rather than falling through to the loop's own
verdict test. `KeyboardInterrupt` and `SystemExit` are re-raised; the journal does not advance
past a step that raised; the caught row is never `pass`; the process exits `1`. The wrap covers
dispatch only — the executor's bookkeeping after a step returns is outside it.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_step_exception_becomes_halting`

REQ-LAND-032: **L16 commits what it staged and its post-condition can see what it did.** Step L16
stages the plan folder (`git add -- <plan_dir>`); its commit shall be scoped to the same pathspec
— `git commit -m <msg> -o -- <plan_dir>` (argument order is normative: after `--` every token is
a pathspec) — and its staged-changes guard scoped identically. Its post-condition shall read
`git status --porcelain=v1 -uall -z`, split on NUL, and test the **path field** of each record
against a `.yf/plan/` **path-prefix allowlist** — never a substring match against the raw line
(`-uall`, the path field and the prefix are each load-bearing: git otherwise collapses untracked
directories to `?? .yf/`, a record carries a status prefix, and a substring exempts any path
containing the fragment). One definition site, `_dirty_outside_plan_dir`, serves L16 and
REQ-LAND-026's prediction.
Rationale: measured, a pre-staged unrelated file was committed and pushed with L16 reporting
`pass` because the commit removed the evidence (dixson3/yoshiko-flow#342, #343).
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_l16_commits_only_plan_dir`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_l16_without_anchor`.

REQ-LAND-035: **A decision document, and every `body_path` it names, shall live outside the work
tree.** `land` shall refuse a decision path inside the work tree and apply the same containment
check to every `body_path`; the refusal sits beside `_land_assert_primary_checkout` and **before**
the tty gate, so a refusal is never preceded by a write. `--dry-run`'s `apply_command` defaults
the decision path to `${TMPDIR:-/tmp}/<plan-id>-decision.json`.
Rationale: a file inside the tree is seen by L16's post-condition and halts the landing past the
irreversible boundary; a suggestion about where to put it is not a control (dixson3/yoshiko-flow#333).
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_decision_inside_tree_refused`

REQ-LAND-037: **Every landing process launch is on the `ctx.run` seam, or is a DECLARED
ctx-less helper.** Two obligations, the second making the first checkable: **(1) Direct** — no
`_land_l<N>_*` function shall contain a process-launch primitive (`subprocess.*`, `os.system` /
`os.popen` / `os.spawn*` / `os.exec*`, `pty.*`); every direct launch goes through
`LandingContext.run`. **(2) Indirect** — every launcher **transitively reachable from an L-step**
shall be a **declared ctx-less helper** resolving its cwd from an **explicit argument**; the
declaration is `LAND_CTXLESS_HELPERS`, and `LAND_CTXLESS_HELPERS_UNROOTED` is its subset that
does not yet take a root — a recorded defect, never an exemption.

**The set is DERIVED, never hand-written.** `skills/yf-plan/scripts/derive_land_launchers.py`
seeds on process-launch primitives, closes transitively over the call graph and BFS's from every
`_land_l<N>_*` function, excluding `ctx.run` / `LandingContext._dispatch` by name. A test parses
this exact line against a live derivation:

```
DERIVED: depth1_frontier=6 closure=14
```

**The declared set is NOT empty.** Three depth-1 helpers remain legitimately off-seam —
`_land_abort_merge`, `_land_capture_conflict` (conflict recovery) and `_land_changed_set` (the
close chain) — plus their transitive launchers, all rooted. The conflict path therefore reaches
a real `git merge --abort` an injected runner never sees, and a test asserting "every process
went through the runner" shall not be written.

**`runner=` closes half the escape and `root=` the other half**: **no runner intercepts a filesystem read**.
`_validate_merged`'s tier-1 decision is three probes keyed on `_repo_root()`
(`_approved_manifest_present`, `_change_validation_script`, `_resolve_validate_cmd`), and
`_worktree_teardown` resolves via `_git_root()`; unrooted, a test that does not `os.chdir()`
would run the real FULL tier at L3 and prune the real checkout at L18. Both take both
parameters; L18's `_worktree_teardown(ctx.plan_dir, force=False, root=ctx.root, runner=ctx.run)`
satisfies the REQ-LAND-004 L18 row verbatim while on the seam.
Verification: `uv run scripts/checks/check_land_seam.py`; `uv run skills/yf-plan/scripts/derive_land_launchers.py --check`; `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_seam.py test_declared_ctxless_helpers_match_the_derived_closure` (four negative controls, one per way the check could go vacuous).

REQ-LAND-038: **The merge preview states what the merge WILL LAND, not the symmetric
difference.** `_land_merge_preview`'s `changed_paths` shall be the set of paths the merge of
`<execute_branch>` into `<target>` **introduces** — the two-dot range `<target>..<execute_branch>`
— never the two-argument `git diff <target> <execute_branch>` form, which cannot distinguish
ahead from behind. `touches_skills` derives from `changed_paths` and is L19's redeploy
precondition, so directionality decides whether the machine's toolchain is rewritten.
`_land_changed_set` (`HEAD^1..HEAD`, after the merge) is total on a non-merge `HEAD`; the in-place
branch cut of `REQ-BRANCH-002` is what makes `HEAD` a real merge commit at L4.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_merge_preview_is_directional`
