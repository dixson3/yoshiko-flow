# Landing specification (`REQ-LAND-*`)

The `land` verb and the `lander` agent: the capability that takes a plan from "the work is done
on `<plan-id>-execute`" to "merged, pushed, reconciled, closed, pruned and redeployed" **on one
informed consent grant** instead of the eleven separate operator instructions plan-057's landing
measured.

This file owns the `REQ-LAND-*` family. It is a **new** spec key, precedented by plan-057's
`REQ-OKFH-001`..`010`; `docs/plans/plan-060-james-dixson-6a6ac9/assets/free-req-ids.md` records
that `REQ-LAND` appears nowhere else in the repository, so the family starts at `001`.

**Not to be confused with `upstream.py land`**, which is the follow-on hoist. The two are
different operations on different objects. Wherever both appear in prose, the distinction is
stated at the point of co-occurrence rather than assumed (plan-060 R11).

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

REQ-LAND-002: `--apply` shall trust the decision document for **judgements only** — grouping,
prose bodies, which rows may close, per-step enable/skip — and for **no fact whatsoever**. Every
fact shall be **re-derived at apply time** and checked against the `manifest_digest` the decision
carries. A decision that disagrees with re-derived reality is a **halt**, never an override.

Three consequences follow structurally rather than procedurally:

1. The agent cannot fabricate an authorization, because there is no field in which to assert one.
2. The agent cannot close a gate. The verb closes gates, and only when the verb's own re-derived
   condition holds.
3. A decision can only ever **narrow** the landing. An `enable` on a step the manifest halted is
   ignored and reported; a `skip` requires a reason and is surfaced in the consent prompt.

Rationale: this is #293's structural answer rather than a procedural one. It is also materially
narrower trust than #301 assumes: `UPSTREAM_REQUIREMENTS` already encodes the per-disposition end
states mechanically, so the agent is trusted to *explain* that a `partial` row stays open, never
to *discover* it.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_narrowing_only`

REQ-LAND-003: **An omission from enumeration is not a `skip`.** The "every skip is surfaced in
the consent prompt" guarantee of REQ-LAND-002 covers only writes the manifest *enumerated and
then declined*. A write the manifest never saw is silent, and no narrowing rule can catch it.
Rationale: recorded verbatim because the enumeration prescription in plan-060 Issue 1.9 was wrong
in five consecutive prose-reasoned rounds; the failure mode of a wrong enumeration is silence, not
an error.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_enumeration_uses_git_plumbing`

## 2. The order — twenty steps, L0 through L19

REQ-LAND-004: A landing shall execute the twenty steps below **in this order**. The order is
normative: each row carries the edge that forces its position, and no step may be reordered
without retiring the edge that pins it.

| Step | Action | The edge that forces this position |
| :-- | :-- | :-- |
| **L0** | `landing-lock acquire` | Merge-back is serialized per machine; the lock must precede the first tree mutation or two landings interleave. |
| **L1** | `git fetch`, then **down-merge** the target into `<plan-id>-execute`, in the worktree | Makes the branch tree byte-identical to the merged tree, which is what makes L11's completion-time criteria measurement and "the tree that will be on the target" reconcilable rather than in tension. |
| **L2** | checkout target; `pull --rebase`; `merge --no-ff` — **left uncommitted** | The merge must exist as a tree before L3 can validate it, and must remain uncommitted so a red L3 has something to fail closed onto. `--no-ff` keeps the landing one revertable commit. |
| **L3** | `validate-merged` — **FULL tier** — **HALT WITH THE LOCK HELD** on fail | plan-009 INV-4. This is the single most important correction to #301, which puts the FULL tier at its step 4, *after* the document close and bead close-out, so a red tier has nothing to fail closed onto. The lock stays held so the operator repairs under serialization. |
| **L4** | commit the merge; `landing-lock release` | The base is green; holding the global lock across the remaining steps would serialize them needlessly. |
| **L5** | **ADVISORY** `recheck-criteria` on the merged tree — never halting | The last fully reversible point. Tree-sensitive criteria are exercised while the landing can still be abandoned with no outward trace. Advisory because the authoritative run is L11, after the reconcile writes that some criteria depend on. |
| **L6** | **PUSH #1** | **The first IRREVERSIBLE step.** It is placed after L3 so what reaches the target is validated, and after L5 so the reversible checks have run. |
| **L7** | reconcile writes — `gh` comment/close, each verified by **read-back** | **The first OUTWARD-FACING write.** It follows the push so the commits its comments reference are already visible upstream. |
| **L8** | close chain steps 1–5, with `CHANGED` computed as `HEAD^1..HEAD` | `<target>...HEAD` is empty by construction once `HEAD == <target>` — dixson3/yoshiko-flow#303. |
| **L9** | `close-reconcile-step` | REQ-COMPLETE-001 constraint 2: the reconcile gate must be resolved before the reconcile bead closes. |
| **L10** | `verify-reconcile` — **halting** | Runs after the reconcile bead closes and before the first destructive step: the only window where §6.3 is done and nothing has been torn down. |
| **L11** | `recheck-criteria` on the merged tree — **halting** | Same window, same reason. This is the authoritative run; L5 was advisory. |
| **L12** | `close_cascade.py` | **The first destructive step.** It refuses any container with a non-terminal child and never force-closes an unmet gate. |
| **L13** | `complete-gate` | After cascade-close, before `complete` (REQ-PLAN-069). |
| **L14** | `pour_fidelity.py` | The executed DAG must be the declared DAG before the plan may claim completion. |
| **L15** | `update-status complete` | REQ-COMPLETE-001: last, and the sole status writer. |
| **L16** | **commit the L8/L15 plan-folder writes; PUSH #2** | **The step neither `SKILL.md` nor #301 has.** Without it every landing ends with an uncommitted, unpushed `plan.md` — measured on plan-057. |
| **L17** | mirror residual open beads upstream, grouped per the decision | Requires the plan-folder state pushed at L16 to be visible, so a mirrored bead's references resolve. |
| **L18** | prune — worktree, branch (local + remote), herdr tab | Nothing may be pruned before L16 has pushed everything that lived on the branch. |
| **L19** | redeploy **iff** the landing touched `skills/` | The only step that mutates the machine outside the repository. Last, because a half-deployed session runs new scripts against old prose (AGENTS.md, "Three artifacts, not one"). |

Rationale: plan-060's EXP-004 proved no single-push order satisfies all four landing
constraints, so the order is two-push by necessity rather than by preference. Neither
`SKILL.md`'s Phase 6 nor #301's six-step order is correct, and the deviations from #301 are
deliberate.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_landing_spec_enumerates_steps_and_journal_states`

REQ-LAND-005: **Every halt after L6 leaves the target already carrying the merge**, and the verb
shall say so in its halt report rather than implying otherwise. What makes that acceptable is
that L3's FULL tier ran first, so the code on the target is validated; the later halts (L10, L11,
L12) concern plan bookkeeping and upstream state, not code correctness, and each is repairable
without a revert.
Rationale: an honestly-labelled irreversibility boundary is worth more than a recoverability
claim that does not hold.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_push_one_is_gated_and_declared_irreversible`

## 3. The journal state set

REQ-LAND-006: `land --apply` shall maintain an **fsync'd journal** with the state set enumerated
below. The set is **closed and normative**: Issues 3.1 and 6.3, and criteria SC3, SC19 and SC38,
bind to *this* list rather than to whatever an implementation happens to write.

The model is `okf_hygiene.py backfill`'s (`REQ-OKFH-008`) — a five-state journal enumerated once
and normatively, `_fsync_write`, staged inside the repo tree, recovery keyed on the **recorded
phase** and never on observed state. Landing extends it in one specific way that requirement
names: **one state per conflict site**, of which there are **four**.

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
| `L_REJECTED_PUSH_2` | **L16** push #2 rejected | `pull --rebase` and retry — **NEVER revert** |

Rationale: R2, SC11 and the test suite of `okf_hygiene` all keyed on "a set of five" that no
document listed, so a five-state test and a five-state journal could have been five *different*
fives with every instrument green. This section exists so that cannot recur for landing.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_journal_recovery_every_state`

REQ-LAND-007: `L_REJECTED_PUSH_2` is the **only post-outward-write conflict state**, and its
recovery is **retry-after-rebase, never revert**. By L16 the reconcile comments are posted (L7),
the bead tree is closed (L12) and `status: complete` is written (L15); reverting would contradict
outward statements already made.
Rationale: the four conflict sites do **not** all sit on the same side of the outward-facing
boundary. An earlier draft of plan-060 claimed they did, and that claim was false.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_conflict_matrix_covers_four_sites_and_staleness`

REQ-LAND-008: The journal shall be written with `_fsync_write` — `O_CREAT|O_TRUNC`, `fsync(fd)`,
`fsync(dirfd)` — and staged **inside the repository tree**, never in a `mktemp -d`.
Rationale: a staging directory on a different filesystem turns `os.rename` into a copy and voids
every durability claim the journal makes.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_journal_recovery_every_state`

REQ-LAND-009: `recover()` shall be keyed on the **journal's recorded phase**, never on observed
state, and shall be **total** over the state set of REQ-LAND-006.
Rationale: "wrote nothing" and "wrote everything then died" are indistinguishable from observed
state at several of the boundaries above; only the recorded phase separates them.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_journal_recovery_every_state`

## 4. The `--apply` invocation contract

REQ-LAND-010: `land --apply <decision.json>` shall be invoked:

- **from the PRIMARY checkout**, never from `.worktrees/<plan-id>`. L2 checks out the merge
  target, and a linked worktree cannot check out a branch another worktree holds.
- **with cwd at the repository root**, because `plan_dir` is resolved relative to cwd throughout
  `plan_manager.py`.
- **by the operator, in their own shell** — see REQ-LAND-013.

`land --dry-run` shall emit the **fully-qualified** command, naming the checkout it must be run
from. An ambiguous cwd is the difference between merging in the primary checkout and attempting
it in a worktree that cannot check out the target branch.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_apply_command_is_fully_qualified`

REQ-LAND-011: A partial failure **is resumable**. Re-invoking `land --apply` with the same
decision file shall read the journal, resume from the recorded phase per REQ-LAND-009, and
**re-derive every fact** per REQ-LAND-002 before continuing. A resume whose re-derived manifest
digest no longer matches shall halt as a staleness report and route back to `--dry-run`.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_stale_decision_halts_before_merge`

REQ-LAND-012: `land` shall register as a **flat** `@cli.command`, not a command group, and shall
use three-valued verdicts (`pass | fail | inconclusive`) throughout, with a `halt_class` field in
the REQ-COMPLETE-003 envelope so a session's stop is mechanically signalled rather than judged
from prose. An `inconclusive` shall **never** be coerced to `fail`.
Rationale: REQ-CLI-021 mandates the flat form, and a group escapes `test_cli_enumeration.py`'s
set-equality check entirely. The `inconclusive`-to-`fail` coercion is a live defect in
`_validate_merged`, the helper this verb calls (dixson3/yoshiko-flow#262); a verb carrying #263
must not reproduce it.
Verification: `uv run skills/yf-plan/scripts/test_cli_enumeration.py`

> **Where an `inconclusive` IS collapsed, stated so the two rules are not confused.** This
> requirement governs `land`'s **own** verdicts. It does **not** govern the `recheck-criteria`
> binding, whose clause grammar is **binary** — `_recheck_holds` is `rc == int(want)`
> (`plan_manager.py:3229`), so a criterion written `-> exit 0` reads an instrument's INCONCLUSIVE
> `2` as **criterion FALSE**. That is the fail-closed direction and is a property of the grammar,
> not of this specification; it is recorded here because a plan asserting that `inconclusive` is
> never coerced must not leave its own criteria layer quietly doing the opposite. The remedy when
> it bites is to read the instrument's printed INCONCLUSIVE reason, never to relax the clause.

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
presence, pid and sid — shall be stamped on every `land --apply` and on every gate close, and
`audit-close` shall **FAIL** a `Type: human` gate whose record reads "no tty, `CLAUDECODE` set".

**This is detection, not prevention.** The markers are strippable. They are useful because they
are strippable *asymmetrically*: a clean record is weak evidence of a human, a dirty one is strong
evidence of an agent. This would have surfaced dixson3/yoshiko-flow#293 within seconds.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_route_record_detects_agent`

REQ-LAND-016: Deliberately **not built**, and recorded here so their absence is a decision rather
than an oversight: a signed or otherwise unmintable consent token (plan-060 D-12 measured that no
purely local artifact is unmintable), GitHub branch protection on the default branch (the only
genuinely off-machine lever, but absent, admin-removable, and guarding one branch), and a
`PreToolUse` hook (Claude-only, and self-disabling because hook config is reloaded mid-session).
Tracked on dixson3/yoshiko-flow#304.

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
   uniform across the four (REQ-LAND-007).

Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_conflict_captured_and_restored`

REQ-LAND-017a: **No landing step shall issue a history-rewinding git command that takes a
TARGET REVISION** — no `reset`, no `revert`, no `cherry-pick`, no forced push. The only
history-affecting operation permitted on the recovery path is `git merge --abort`, which takes
**no revision argument**: git computes the restore point itself from `MERGE_HEAD`/`ORIG_HEAD`.

Rationale, and it is a defect the plan committed against itself rather than a hypothetical. A
rewind target is defined by **what it PRESERVES**, never by what it drops. During this plan's own
execution the session proposed `git reset --hard <epic-3-commit>` on the true premise that the
commit being removed "contains nothing I authored" — and that reset would have dropped a **later**
commit sitting on top of it, deleting the very fix the reset existed to preserve. The premise was
verified; the conclusion did not follow, because the reasoning was about which commit to remove
rather than about what the target keeps. `git merge-base --is-ancestor <fix> <target>` answers it
in one command.

An executor that computed such a target the same way would make that error **with the operator's
authorization already attached**, which is the worst available moment for it. The prohibition is
therefore structural rather than advisory: the shipped landing path contains zero occurrences of
any of these verbs, and this requirement plus its test PIN that property, which until now held
only by accident.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_no_target_taking_rewind_in_landing_path`

REQ-LAND-018: **A clean preview does not guarantee a clean apply.** `land --apply` shall
**re-preview immediately before the merge** and halt on any change since the decision was minted,
reporting the **digest mismatch** rather than the bare conflict.
Rationale: measured — preview clean at T0, the target advances, the same merge conflicts at T1.
The predicted merge-tree oid changes when the target moves, which is what makes the staleness
detectable at all; a digest omitting `predicted_tree` and the target tip could not detect the
staleness it exists to detect.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_digest_covers_merge_preview`

## 7. Verification of writes

REQ-LAND-019: Every outward-facing write and every bead close performed by `land --apply` shall
be verified **structurally, by read-back** — `gh issue view` after a `gh` write, `bd show` after a
`bd close` — never by exit code and never by a returned URL alone.
Rationale: `bd close` **refuses and exits 0** when the bead is blocked by an open dependency
(dixson3/yoshiko-flow#230), and an exit 0 from `gh` does not establish that the body posted is the
body intended — measured on issue #292 during plan-060's own drafting.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_readback_catches_wrong_body`

REQ-LAND-020: `land --apply` shall be **fail-closed at every edge**: the first unverified write
aborts before any destructive follow-on stage is reachable, and a post-condition assertion runs on
the way out, not merely a precondition on the way in.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_close_chain_exit_codes_read`

## 8. Runtime preconditions

These are preconditions `land --apply` checks **at runtime, for the plan it is landing**. They are
distinct from plan-060's own capability gates, which authorize plan-060's own landing.

REQ-LAND-021: **The per-landing upstream grant.** Step L17 mirrors residual open beads upstream by
calling `upstream.py push --issues <csv> --apply` **concretely** — `/yf-beads-upstream` is a prose
skill for an LLM, and `land --apply` is Python that cannot invoke it.

That push is **confirm-required by default**, and dixson3/yoshiko-flow#280 leaves
`detect_followons`' narrow auto-eligible set permanently empty. **L17 is therefore
propose-only unless the batched grant demonstrably covers the specific bead set** — "demonstrably"
meaning the decision document enumerates each bead id and the grant names each of them. Absent
that coverage, L17 emits the proposed `upstream.py push` invocation and performs no upstream write.

This decision is recorded **here**, normatively, rather than left implicit in the implementation.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_residual_mirroring_is_concrete_and_gated`

REQ-LAND-022: **The redeploy precondition.** Step L19 shall run `yf self install --from-build
--build` **if and only if** the landed change set touches `skills/`, and only when the decision
document enables the step. Redeploy shall never run mid-execution — it is the last step of the
last step, and the only one that mutates the machine outside the repository.

The operator authorizing it must have read the per-key config delta and must understand that
**rollback is asymmetric**: `yf harness tune --revert` restores config precisely, but the rules
aggregate is **deleted** rather than restored (dixson3/yoshiko-flow#154).
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_redeploy_iff_skills_touched`

REQ-LAND-023: **Prune is strategy-aware.** Step L18 shall consult `_resolve_landing_strategy` and
delete `<plan-id>-execute` **only**. Under the `feature-branch` strategy, REQ-BRANCH-004 requires
the feature `<plan-id>` branch to be **preserved**.

The herdr tab shall be closed **only** under dixson3/yoshiko-flow#204's mechanical harvest
preconditions **and** only for an explicitly supplied tab id; tab provenance — "a tab this session
created" — is currently unanswerable, so the **default is to PROPOSE**. Any close shall be
verified by reading back the agent list.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_apply.py test_prune_is_strategy_aware`

## 9. Halting findings from `--dry-run`

REQ-LAND-024: `land --dry-run` shall report a **plan-number collision on the merge target** as a
halting finding. Two bundles sharing an `NNN` and differing only by hash suffix **merge cleanly**
(measured, commented on dixson3/yoshiko-flow#302), so merge-back is the only place the collision
is detectable at all.
Rationale: scoped deliberately to the detection half. The `get_next_index()` `max+1` and
cross-worktree fixes (#302 B1/B2) are Phase-1 concerns and stay open.
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_number_collision_halts`

REQ-LAND-025: `land --dry-run` shall compute the changed set as **`HEAD^1..HEAD`**, never
`<target>...HEAD`, and feed it to `classify-deliverable`.
Rationale: `<target>...HEAD` runs when `HEAD == <target>` and is empty by construction, which makes
`classify-deliverable`'s `path-backed` evidence structurally unreachable
(dixson3/yoshiko-flow#303).
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_changed_set_nonempty`

REQ-LAND-026: `land --dry-run` shall **mutate nothing**: `git status --porcelain` is empty after it
and no bead is mutated. The merge preview uses `git merge-tree --write-tree`, which **does** create
an unreferenced object-database tree object — recorded honestly here so that no requirement and no
criterion claims the dry run "writes nothing at all".
Verification: `bash scripts/checks/check-pytest-ran.sh skills/yf-plan/scripts/test_land_manifest.py test_dry_run_does_not_mutate`
