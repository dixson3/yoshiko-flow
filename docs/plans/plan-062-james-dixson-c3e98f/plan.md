---
type: Plan
okf_spec: OKF-PLAN
id: plan-062-james-dixson-c3e98f
author: James Dixson
created: '2026-09-03'
status: executing
deliverable_class: standard
fingerprint: 755a996cd7d9f240c8d27b6c600a94b8b37787f3a52f9e4f0341a649f3ac3a1e
epic: yf-mol-tm2d
---
# Plan: Wire `land --apply` to `_land_execute`, and make the seam testable

**ID:** plan-062-james-dixson-c3e98f
**Author:** James Dixson
**Created:** 2026-09-03
**Status:** executing
**Deliverable-class:** standard
**Epic:** yf-mol-tm2d
**Fingerprint:** 755a996cd7d9f240c8d27b6c600a94b8b37787f3a52f9e4f0341a649f3ac3a1e

## Objective

Make `land --apply` actually land: replace the unconditional stub at `plan_manager.py:8306-8311`
with real wiring into the fully-implemented `_land_execute`, fix the resume no-op that wiring
would otherwise make reachable, and add a **seam-level** test so a disconnected CLI entry point
fails loudly. **Narrowed at pass 4** — the L7 frontmatter fix (#326) was cut and is deferred.

## Motivation

`land --apply` is the **sole writing mode** of the landing capability, so **no plan can land
through the intended path.** plan-061 landed only because its L1-L19 sequence was walked by
hand; plans #316 and #317 are blocked behind the same wall.

The defect is dead code, not missing code. `_land_execute` drives all fifteen `LAND_EXECUTOR`
steps, advances the journal, and is fail-closed — and it has **exactly one occurrence in the
file, its own `def`**. plan-060's Epic 6 rehearsal drove it *directly*, which is why it caught a
real journal bug (an L19 skip stalling at `L_PRUNED`) while being structurally unable to notice
that nothing calls it. The decomposition never contained the seam: reading plan-060's Epic 3 and
Epic 4 issue lists, **no issue owns it**.

That is the `#263` vacuous-check class at the harness level — a suite passing comprehensively
over an engine no entry point invokes. This plan closes the instance and adds the check that
would have caught it.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #327 | `land --apply` is an unconditional stub | include | The plan's reason for existing, and the only `include` after the pass-4 narrowing. Closed when the seam is wired, the resume is fixed, and both are covered by a test PROVEN to discriminate. | 1.1, 2.1, 4.1 |
| #326 | `draft_body_path` posts bundle files verbatim vs OKF frontmatter | deferred | **Cut at pass-4 by operator decision.** Epic 3's five issues and their four criteria are removed. The fix design survives in full in `findings/exp-003` — strip + temp file + compare-the-stripped-text, reusing `okf.read_frontmatter`, with a 7/7 spike — so a later plan starts from a solved design, not a blank page. Nothing here depends on it. | — |
| #266 | The `## Gates` grammar cannot express `test_class` or `cwd` | partial | This plan structurally depends on the gap and does not close it. Issue 0.0 SETS the metadata directly at pour; the grammar is untouched. | — |
| #304 | The self-authorization residue does not close | partial | Design input, not a deliverable — it is why the seam test adds no production-reachable bypass. The record is `findings/exp-001`. Stays OPEN. | — |

## Investigation Findings

Three experiments, all with sandbox spikes. Full text in `findings/`.

**EXP-001 — the expensive seam test is unnecessary, measured.** A discrimination test (same
assertion, two builds) proves an in-process `CliRunner` test with the gate monkeypatched
separates broken from fixed: `exit 2 / FAIL` on the shipped build, `exit 1 / PASS` on a wired
build. A real pty is not required, because **the defect sits below the tty gate**. Of the four
mechanisms measured, a test env flag and the dormant `allow_list` both create
**production-reachable** bypasses; the in-process route creates none.

**EXP-002 — wiring the seam makes a latent data-loss bug reachable.** `_land_execute`'s
`resume_from` block contains `for key, _ in LAND_EXECUTOR: pass`; AST measurement shows `done`
is stored at 9550 and 9558 and **loaded nowhere**, and holds journal states where the step loop
needs step keys. Measured in a sandbox, a resume after a halt at L17 **re-executed all fifteen
steps from L0**, including `l6_push_one` and `l7_reconcile_writes`. The glue itself is ~38 lines
and ~80% of its helpers already exist.

**EXP-003 — retained though its issue is deferred.** The #326 fix design and its 7/7 spike are
recorded in full. It is no longer in scope; the finding is kept because a solved design is worth
more than the effort to re-derive it.

## Approach

**SPEC-first, then the RESUME FIX, then the seam, then land. Nothing else.**

**Scope is deliberately NARROW** (operator decision at pass 4). Only two defects are fixed: the
dead `--apply` executor (#327) and the resume no-op it would make reachable. Everything else this
plan's four red-team passes surfaced is **filed, not fixed** — see Issue 5.1. The reasoning is
that #327 alone is what blocks plans #316 and #317, and four passes established that `land` has
more defects than one plan should try to absorb.

**The resume fix lands BEFORE the seam wiring, and the order is the point** (pass-1 C8).
`depends-on` ordering is not atomicity, and seam-first would put the *dangerous* state first: a
window in which `--apply` works and a resume still re-posts every reconcile comment. Reversed,
**the resume fix is inert until something calls the engine.**

The seam test follows EXP-001's measured recommendation and adds **no production-reachable
mechanism**: an in-process test with the gate monkeypatched, a source-level `ast` assertion that
`land_cmd` calls `_land_tty_gate` before any write, and retention of the existing real-process
gate-closed test.

**This plan MUST execute with `execute.worktree: false` (in-place mode), and the config MUST be
written BEFORE `/yf-plan execute` is invoked** — `printf '{"execute.worktree": false}\n' >
.yf/plan/config.local.json`. The ordering is forced (pass-3 C30): §5.2a runs pour → `worktree
ensure` → the §5.2c sweep, so by gate-evaluation time the mode is already decided.

**And in-place mode alone makes `land` unable to run** (pass-4 C37): no execute branch is ever
created, so `land --dry-run` halts `execute-branch-missing`. Issue 0.7 creates that branch
explicitly in the primary checkout, satisfying both constraints at once.

**Every test command is `uv run skills/yf-plan/scripts/test_land_apply.py -k <name> -q`.** The
`uv run --with pytest python3 -m pytest …` form exits **2** on collection
(`ModuleNotFoundError: click`) because `--with pytest` never reads the file's PEP 723 block —
measured in pass-1 C1.

**Criteria re-evaluated at L11 are halting**, so **SC14 and SC15 are both `manual:`**. A
criterion that cannot be true after all gates are closed halts the landing past the irreversible
boundary (pass-3 C32) — and a criterion phrased to avoid that can end up permanently true
instead, which is what pass-4's `bd list --all` fix produced and pass-5 C47 measured. Neither
failure is expressible as a repo-wide clause, so the read-back is recorded by Issue 0.0 instead.

## Epics

### Epic 0: SPEC-first, verify the pour, and make landing reachable
- Issue 0.0: **Immediately after the §5.2a pour, SET THEN ASSERT** the gate metadata — do not merely detect it. Run `bd update <gate-id> --metadata '{"gate_type":"auto","test":"...","test_class":"probe","cwd":"repo-root"}'` for **ALL THREE** capability gates (`grep -c '^### Capability Gate:' plan.md` = 3 — the count is load-bearing and was wrong once already, pass-3 C28), then read them back and halt only if a write did not take. A detector whose remediation is "halt" is weaker than a setter, and relying on the executing agent to follow a blockquote is the command-vs-obligation hazard (#273).
- Issue 0.1: Retarget `REQ-LAND-011`'s `Verification:` line. **Runs after 0.7 so the execute branch already exists** — in-place mode has one address space, so anything committed before the branch is cut lands on `main` and is NOT in the execute→main merge L3 validates (pass-5 C51). It currently names `test_stale_decision_halts_before_merge`, which tests **staleness, not resume** — a vacuous verification for the requirement that says a partial failure is resumable. Point it at the resume test from Issue 4.1.
  - depends-on: 0.7
- Issue 0.4: **`REQ-LAND-027` is deliberately skipped** — reserved by `findings/exp-003` for the deferred #326 fix, so this plan takes 028/029 and leaves a documented hole rather than an unexplained one (pass-5 C54). Add `REQ-LAND-028` — `land --apply` shall reach the executor; a build whose CLI does not invoke `_land_execute` is non-conformant.
  - depends-on: 0.1
- Issue 0.5: Add `REQ-LAND-029` — a resume shall **not re-execute** a step whose journal state has been reached, and shall mark skipped steps explicitly in `results`.
  - depends-on: 0.4
- Issue 0.6: Add the living-amendment-log entry in the repo-root `SPEC.md` naming plan-062 and the ids above. **The log is in `SPEC.md`, not `spec/landing.md`** — the latter contains zero occurrences of "amendment" (pass-2 C18).
  - depends-on: 0.5
- Issue 0.7: **Create and check out `plan-062-james-dixson-c3e98f-execute` in the PRIMARY checkout**, cut from the pinned base (`git checkout -b <plan-id>-execute main`), immediately after §5.2a's in-place fallback. Measured (pass-4 C37): under `execute.worktree: false`, `_worktree_ensure` returns `viable: false, reason: opted-out` **before any branch creation**, so no execute branch ever exists and `land --dry-run` halts `execute-branch-missing` with `resolvable_by_agent: false`. Creating it by hand satisfies both constraints: the primary is on the branch carrying the fix, and `_land_manifest:8003` finds the branch it requires. **Placed SECOND, before every SPEC edit** (pass-5 C51): in-place mode has a single address space, so a commit made before this branch exists lands on `main` and escapes the merge L3 validates.
  - depends-on: 0.0

### Epic 1: Fix the resume no-op FIRST — inert until Epic 2 gives it a caller
- Issue 1.1: Replace the dead `for key, _ in LAND_EXECUTOR: pass` loop (`:9555-9557`) with a real step-to-journal translation: a step is done when `LAND_STEP_JOURNAL[key]` is in `reached`. For the three keys absent from that map (`l3_validate_merged`, `l8_close_chain_head`, `l12_close_cascade`) resolve **FORWARD** — done only when the journal state of the *next journaled* step is in `reached`. A backward scan is unsafe: after a halt at `l3_validate_merged`, `L_MERGED_UNCOMMITTED` is already reached, so backward resolution would mark l3 done and **skip validation of the merged tree** (pass-1 C7). **`l0_lock_acquire` is EXEMPT from skipping and always re-executes** (pass-2 C19): the landing lock is released at L4, not at the end, so a uniform skip rule would run L1-L4 holding no lock and then `unlink` a lock it never acquired — `_landing_lock_release` is keyed on plan+host, not PID. Re-executing L0 is safe because `_landing_lock_acquire` reclaims a same-host dead-PID lock. **Known asymmetry, recorded rather than papered over** (pass-3 C36): on a resume from L5 onward, L0 re-acquires while L4 is skipped, so that run ends holding a lock nothing released; it self-heals via dead-PID reclaim.
  - depends-on: 0.5, 0.7
  - resolves-upstream: #327 (include)
- Issue 1.2: **Actually consult `done`** in the step loop at `:9561`, skipping completed steps and recording an explicit `resumed` marker in `results`. Today `done` is stored at `:9550` and `:9558` and loaded nowhere.
  - depends-on: 1.1

### Epic 2: Wire the seam
- Issue 2.0: **Author the seam test FIRST, before any wiring**, and record that it FAILS against the unwired build. An in-process `CliRunner` test with `_land_tty_gate` monkeypatched open and `LandingContext(runner=...)` injected, asserting `--apply` against a conformant decision reaches at least `l0_lock_acquire`. A test authored after the fix proves only that the fix is self-consistent.
  - depends-on: 0.4, 0.7
- Issue 2.1: Replace `plan_manager.py:8306-8311` with the glue: parse the decision (mirror `:8265-8278`), `LandingJournal(...).recover()` and branch on its four actions, `_land_repreview_or_halt` on a stale bind, construct `LandingContext(...)` — **`manifest` is already in scope in `land_cmd`**, so reuse it rather than re-deriving; that fact is *why* ~40 lines is true — then call `_land_execute(ctx, resume_from=...)`. Verified end-to-end in EXP-002's sandbox.
  - depends-on: 1.2, 2.0
  - resolves-upstream: #327 (include)
- Issue 2.2: Derive the verdict **three-valued** from `_land_execute`'s bare progress dict. `halted -> fail / reached_terminal_state -> pass` is WRONG: L8's and L12's `inconclusive` results are explicitly non-halting, so a landing can reach `L_DONE` carrying them, and laundering that into `pass` is the coercion `REQ-LAND-012` forbids.
  - depends-on: 2.1
- Issue 2.3: Delete the stale remediation text (`:8309-8310`, identified unambiguously by the string `'Epics 3 and 4 implement'`). It says Epics 3 and 4 implement the steps; commit `26bb490` did. A reader who trusts it goes looking for unwritten code.
  - depends-on: 2.1

### Epic 4: The tests that would have caught this
- Issue 4.1: Add the resume test: after a forced halt at L17, a resume executes **neither** `l6_push_one` **nor** `l7_reconcile_writes`, **and DOES execute `l0_lock_acquire`** (the C19 lock exemption — a resume that silently skipped L0 would run unlocked). `REQ-LAND-011`'s retargeted Verification line points here.
  - depends-on: 1.2
  - resolves-upstream: #327 (include)
- Issue 4.2: Add halt-at-`l3` and halt-at-`l8` resume cases, proving FORWARD resolution: a halt at `l3_validate_merged` must **re-run** validation on resume, not skip it. These are the cases a backward scan would silently break.
  - depends-on: 4.1
- Issue 4.3: Add the source-level `ast` assertion that `land_cmd` calls `_land_tty_gate` before any write — closing the one gap a gate-stubbed test cannot see. The file already uses `ast` this way at `:350-351`. **This is a FUTURE regression guard, not evidence about the present defect**: `land_cmd` already calls the gate at `:8298`, so it passes the moment it is written (pass-2 C26).
  - depends-on: 2.0
- Issue 4.4: Add a test that a landing reaching `L_DONE` while carrying a non-halting `inconclusive` from L8 or L12 yields verdict `inconclusive` and exit 2 — **not** `pass`. Without it Issue 2.2 is unobservable and R5 is untested.
  - depends-on: 2.2
- Issue 4.7: Confirm `test_tty_refusal_exits_three_not_one_or_two` (`:388`) still passes **unmodified**. It is the gate-closed half's real-process coverage and must not be weakened to accommodate the gate-open test.
  - depends-on: 4.3

### Epic 5: File the rest, validate, and hand off the landing
- Issue 5.1: File upstream, as separate issues, every defect this plan found and deliberately did NOT fix: (a) **#326 is already filed** — re-label it `deferred` with a pointer to `findings/exp-003`, which contains the complete verified design; (b) `land` is incompatible with `execute.worktree: false` — no execute branch is created, so `--dry-run` halts `execute-branch-missing` (pass-4 C37); (c) `assets/upstream-drafts/` is undocumented in every yf-plan `.md` (zero `grep` hits outside `plan_manager.py:7936`, pass-4 C41); (d) a decision file written inside the tree halts the landing at L16, past the irreversible boundary; (e) `allow_list=[None]` opens the tty gate unconditionally, and its test at `:384` is vacuous.
  - depends-on: 4.7
- Issue 5.1c: **Author three draft bodies — `327.md`, `266.md`, `304.md`.** `_land_upstream_rows` (`:7941-7947`) filters on `disp == "exclude"` **only**, so #326 also gets a `draft_body_path` and will report `draft_present: false` — expected and correct, because `UPSTREAM_REQUIREMENTS["deferred"]` sets `requires_mention: False` (pass-5 C50). Three is the count of rows requiring a mention, not of non-exclude rows.
  - depends-on: 5.1
- Issue 5.2: Verify — do not assume — that `CHANGE-VALIDATION.md`'s `uv-yf-land-apply` row actually runs the NEW tests. The row exists at `:137` and already uses the working invocation, so that half is expected to be a **no-op**; say so explicitly rather than leaving a check nobody performs. **Then register `gate-plan062-amendment`** (`uv run scripts/check_amendment_log.py --plan plan-062-james-dixson-c3e98f`) with its §Trigger Scope entry: plan-060 mapped `SPEC.md` (`:253`) and `skills/yf-plan/spec/**` (`:254`) to its own row, and this plan edits both paths, so without a row of its own those triggers fire and report on **plan-060** (pass-5 C53).
  - depends-on: 5.1
- Issue 5.3: Run the FULL tier on the merged tree and record the run.
  - depends-on: 5.2, 4.7
- Issue 5.4: Confirm the **primary checkout's working tree carries the fix** before any `--apply` is attempted (pass-1 C4). Resolve the primary via `--git-common-dir`, not `--show-toplevel`, which resolves to a worktree root (pass-4 C42).
  - depends-on: 5.3, 5.1c
- Issue 5.5: **Record the Phase-6 landing route and its halt-recovery contract in the retrospective, for the OPERATOR to execute.** This is a Phase-5 bead and must close before the Reconcile Gate opens and Phase 6 begins — so it produces the handoff artifact, it does not perform the landing (pass-4 C40). **The executing session must NOT run `land --apply`**: SKILL.md §6.0 says *print the command and stop*, and names `#293`, an agent closing a consent gate by asserting its own authorization. The recorded contract: on a halt the OPERATOR reads the journal phase, fixes the cause, and re-invokes `land --apply`, which now genuinely resumes because Epic 1 landed first.
  - depends-on: 5.4
- Issue 5.1b: Bring `index.md` current with every bundle member and confirm `okf.py reindex --check` exits 0. **Author real descriptions, not bare bullets** — `reindex --write` satisfies the gate while degrading the artifact, which the check's own remediation text calls out. Placed LAST so it runs after every Phase-5 bundle write (`assets/upstream-grant.md` and `records/*.md` are not auto-indexed, pass-4 C39).
  - depends-on: 5.5

## Gates

> **Known grammar gap — the `test_class` / `cwd` lines below do NOT survive extraction.**
> `plan_extract.py` recognizes only `Type|Approvers|Condition|Test|Blocks|Instructions`, and
> `unparsed` stays `[]`, so `--strict` does not flag the loss. **Issue 0.0 is the control**: it
> SETS the metadata and asserts the write took. This blockquote is documentation; 0.0 is the
> check.

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: execution is in-place, not in a worktree
- Type: auto
- test_class: probe
- cwd: repo-root
- Condition: `execute.worktree` resolves to `false`, so the primary checkout carries the fix at land time
- Test: uv run skills/yf-plan/scripts/plan_manager.py config-resolve --json | jq -e '.keys["execute.worktree"].value == false' > /dev/null
- Blocks: 1.1
- Instructions: REMEDIATION IS A RESTART, NOT A TOGGLE. If this gate is red the session is ALREADY in worktree mode (`worktree ensure` runs before the sweep): set `{"execute.worktree": false}` in `.yf/plan/config.local.json`, REMOVE `.worktrees/<plan-id>`, and RESTART execution from §5.2. Setting the config and continuing does not re-decide the mode. Note that satisfying this gate is what makes Issue 0.7 necessary — in-place mode alone leaves `land` with no execute branch.

### Capability Gate: the seam test is DISCRIMINATING before the seam is wired
- Type: auto
- test_class: probe
- cwd: repo-root
- Condition: the seam test authored by Issue 2.0 FAILS against the unwired build, proving it measures the defect rather than passing vacuously
- Test: uv run skills/yf-plan/scripts/test_land_apply.py -k seam_reaches_executor -q; test $? -eq 1
- Blocks: 2.1
- Instructions: EXPECTED TO REPORT FAIL AT THE §5.2c EXECUTE-START SWEEP — the test does not exist until Issue 2.0, so pytest exits 5 and this gate reads red for a benign reason. ONCE-ONLY thereafter. Run it after the seam test is authored and before the wiring lands, record the observed exit code and `git rev-parse HEAD` in the resolution note, and DO NOT re-run it afterwards — once the wiring lands, the correct answer inverts.

### Capability Gate: a resume does not re-execute irreversible steps
- Type: auto
- test_class: probe
- cwd: repo-root
- Condition: after a forced halt at L17, a resumed landing executes NEITHER `l6_push_one` NOR `l7_reconcile_writes`
- Test: uv run skills/yf-plan/scripts/test_land_apply.py -k resume_skips_completed -q
- Blocks: 4.2
- Instructions: EXPECTED RED AT THE §5.2c EXECUTE-START SWEEP — the resume test does not exist until Epic 4's first issue, so pytest exits 5. This gate stands between the seam and duplicate public comments, and must be green before the landing is handed to the operator. Its evidence comes from the resume test, which this gate does NOT block.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | A window exists where the seam is live and the resume is still a no-op, re-posting reconcile comments | high | **Epic order reversed** — the resume fix lands first and is inert without a caller (pass-1 C8) |
| R2 | The seam test is authored after the fix and passes vacuously | high | Issue 2.0 authors it first; the gate requires `test $? -eq 1` against the unwired build — failure only (pass-1 C2) |
| R5 | The verdict wrapper launders a non-halting `inconclusive` into `pass` | medium | Issue 2.2 derives three-valued; Issue 4.4 tests it directly |
| R6 | The landing halts past the irreversible boundary | medium | Issue 5.5 records the recovery contract (journal → fix → re-invoke, which now genuinely resumes) and hands it to the operator |
| R7 | A forward-resolution error silently skips l3 validation or the close chain on resume | high | Issue 1.1 specifies FORWARD resolution; Issue 4.2 tests halt-at-l3 and halt-at-l8 (pass-1 C7) |
| R8 | Execution runs in a worktree, so `--apply` loads `main`'s stubbed module | high | A capability gate blocks 1.1 on `execute.worktree == false`, checked at execute start rather than discovered at land time (pass-2 C16) |
| R9 | Any of the THREE capability gates pours without `test_class`, is classified `manual`, and the sweep never runs it | high | Issue 0.0 SETS the metadata rather than detecting it, and asserts the read-back took — that is the mitigation. SC14 records the three gate ids and their `bd show` output (pass-2 C17, pass-4 C38, pass-5 C47) |
| R10 | A resume skips `l0_lock_acquire`, running L1-L4 unlocked | medium | Issue 1.1 exempts L0; Issue 4.1 asserts it re-executes (pass-2 C19) |
| R11 | In-place mode leaves no execute branch, so `land` cannot run at all | high | Issue 0.7 creates it explicitly in the primary checkout; SC0b asserts it exists (pass-4 C37) |
| R12 | A criterion re-evaluated at L11 cannot be true after the gates close, halting past the irreversible boundary | high | **SC14 and SC15 are both `manual:`**; the Approach enumerates the constraint (pass-3 C32, pass-4 C38, pass-5 C47) |

## Success Criteria

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC0b | The execute branch `land` requires exists | `git rev-parse --verify --quiet plan-062-james-dixson-c3e98f-execute` → exit 0 | 0.7 |
| SC1 | `land --apply` reaches the executor | `uv run skills/yf-plan/scripts/test_land_apply.py -k seam_reaches_executor -q` → exit 0 | 2.0, 2.1 |
| SC2 | `_land_execute` has a caller, not just a definition | `test "$(grep -c '_land_execute(' skills/yf-plan/scripts/plan_manager.py)" -ge 2` → exit 0 | 2.1 |
| SC3 | The stub verdict is gone | `grep -q 'executor is not implemented' skills/yf-plan/scripts/plan_manager.py` → exit 1 | 2.1 |
| SC3b | The stale remediation sentence is gone | `grep -q 'Epics 3 and 4 implement' skills/yf-plan/scripts/plan_manager.py` → exit 1 | 2.3 |
| SC4 | A resume skips already-completed steps | `uv run skills/yf-plan/scripts/test_land_apply.py -k resume_skips_completed -q` → exit 0 | 1.1, 1.2, 4.1 |
| SC4b | Forward resolution re-runs l3 and l8 rather than skipping them | `uv run skills/yf-plan/scripts/test_land_apply.py -k resume_forward_resolution -q` → exit 0 | 1.1, 4.2 |
| SC5 | `done` is READ, not merely written | `grep -q 'in done' skills/yf-plan/scripts/plan_manager.py` → exit 0 | 1.2 |
| SC9 | The tty-gate call cannot be deleted unnoticed | `uv run skills/yf-plan/scripts/test_land_apply.py -k ast_gate_called -q` → exit 0 | 4.3 |
| SC10 | The gate-closed process test still passes | `uv run skills/yf-plan/scripts/test_land_apply.py -k tty_refusal -q` → exit 0 | 4.7 |
| SC10b | ...and is UNMODIFIED in the contract it asserts | `test "$(grep -c 'p.returncode == 3' skills/yf-plan/scripts/test_land_apply.py)" -ge 1` → exit 0 | 4.7 |
| SC11 | No `YF_LAND`-prefixed test bypass was introduced | `grep -rq 'YF_LAND' skills/yf-plan/scripts/plan_manager.py` → exit 1 | 2.0, 4.3 |
| SC12 | A non-halting `inconclusive` is not laundered into `pass` | `uv run skills/yf-plan/scripts/test_land_apply.py -k inconclusive_not_laundered -q` → exit 0 | 2.2, 4.4 |
| SC13 | The two new REQ-LAND ids exist as DISTINCT ids | `test "$(grep -oE 'REQ-LAND-02[89]' skills/yf-plan/spec/landing.md \| sort -u \| wc -l \| tr -d ' ')" -eq 2` → exit 0 | 0.4, 0.5 |
| SC13b | `REQ-LAND-011` no longer names the staleness test as its verification | `grep -q 'test_stale_decision_halts_before_merge' skills/yf-plan/spec/landing.md` → exit 1 | 0.1 |
| SC13c | The amendment log records plan-062 | `uv run scripts/check_amendment_log.py --plan plan-062-james-dixson-c3e98f` → exit 0 | 0.6 |
| SC14 | All three capability gates carry `test_class` and `cwd` as bead metadata | manual: Issue 0.0 records the three gate ids and their `bd show <id>` read-back in the retrospective. **A repo-wide clause cannot express this** — pass-4 C38 removed a false-fail by adding `--all`, and pass-5 C47 measured the result as permanently TRUE (59 `test_class` lines across 194 historical gate beads), so the clause passed before anything was poured. Pass-2 C20 argued for a clause over manual; that argument is answered by C47's measurement, and the reversal is recorded here rather than made silently | 0.0 |
| SC15 | The FULL tier is green on the merged tree | manual: recorded by Issue 5.3, whose run is the authoritative one. Deliberately NOT a clause — `recheck-criteria` would re-run the multi-minute tier at L5 and again at L11, and its 300s cap would record a timeout as FAIL past the irreversible boundary (pass-3 C32) | 5.2, 5.3 |
| SC16 | The primary checkout carried the fix before `--apply` was attempted | `git -C "$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")" grep -q 'executor is not implemented' -- skills/yf-plan/scripts/plan_manager.py` → exit 1 | 5.4 |
| SC17 | The landing route and halt-recovery contract are handed to the operator | manual: the artifact is the retrospective entry; the OPERATOR runs `land --apply`, which no check inside the plan may perform or self-certify (SKILL.md §6.0, #293) | 5.5 |
| SC17b | THIS bundle's index is current | `uv run skills/yf-okf/scripts/okf.py reindex --check docs/plans/plan-062-james-dixson-c3e98f` → exit 0 | 5.1b |
| SC17c | Upstream draft bodies exist for every row REQUIRING A MENTION | `test "$(ls docs/plans/plan-062-james-dixson-c3e98f/assets/upstream-drafts 2>/dev/null \| wc -l \| tr -d ' ')" -eq 3` → exit 0 | 5.1c |
| SC18 | Every deliberately-unfixed defect is filed, not silently dropped | manual: five issue URLs recorded in the retrospective — filing is an outward-facing write and cannot be self-certified from inside the plan | 5.1 |
