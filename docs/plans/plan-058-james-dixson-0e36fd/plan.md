---
type: Plan
okf_spec: OKF-PLAN
id: plan-058-james-dixson-0e36fd
author: james-dixson
created: '2026-08-28'
status: reconciling
deliverable_class: standard
fingerprint: 174b21743cb585627be4c81b10f1179a60873e98e743cc7a8386566988c00b8d
epic: yf-mol-802
---
# Plan: Fix yf-beads-upstream upstream.py push: eliminate the full-universe per-bead bd show fan-out in the owner-claim warning path, bound run() with a timeout, and repair the identical defect in cmd_enumerate (#268)

**ID:** plan-058-james-dixson-0e36fd
**Author:** james-dixson
**Created:** 2026-08-28
**Status:** reconciling
**Deliverable-class:** standard
**Epic:** yf-mol-802
**Fingerprint:** 174b21743cb585627be4c81b10f1179a60873e98e743cc7a8386566988c00b8d

## Objective
Fix yf-beads-upstream upstream.py push: eliminate the full-universe per-bead bd show fan-out in the owner-claim warning path, bound run() with a timeout, and repair the identical defect in cmd_enumerate (#268)

## Motivation

`upstream.py push` — the path `UPSTREAM_TRACKING.md` **mandates** for every upstream write — does
not complete on a repository of ordinary size. The always-loaded rule forbids hand-running the
underlying `gh`/`bd` commands (a raw `gh issue create` records no `external_ref`, leaving an issue
nothing can map back to a bead), so while this is broken **there is no compliant way to push a bead
upstream at all**.

Who is affected: every operator and agent in every repo where this skill is installed. The defect
scales with repository **history**, not activity — the bead universe only grows, so every repo
crosses the unusable threshold eventually and never recovers. In `dixson3/yoshiko-flow` the walk is
**49x** the live working set (1,801 total beads vs. 37 open).

What triggered it: discovered 2026-08-28 while hoisting a follow-on bead from `yf-research` 005
(PR #267). Filed as [#268](https://github.com/dixson3/yoshiko-flow/issues/268) with a SIGINT
traceback, a three-defect diagnosis and measured timings.

Standing obligations it blocks: the close-time / land-the-plane push, and the hoist of `yf-djfx`
(operator-approved, amended, pending).

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#268](https://github.com/dixson3/yoshiko-flow/issues/268) | CRITICAL: yf-beads-upstream push is unusable — owner-claim warning fans out one `bd show` per bead over the ENTIRE closed universe | include | The whole of this plan. Body captured verbatim in [references/upstream-268.md](references/upstream-268.md). | 1.1, 1.3, 2.1 |

## Investigation Findings

Six experiments. Full write-ups in [findings/](findings/).

| # | Question | Verdict |
| :-- | :-- | :-- |
| [EXP-001](findings/exp-001-diagnosis-validated.md) | Is #268's ~360 s inference real? | **CONFIRMED by completion.** `push --issues yf-djfx` ran to the end: **334 s, rc=0** |
| [EXP-002](findings/exp-002-one-call-rewrite-is-exhaustively-equivalent.md) | Does `bd list --all --json` already carry the edges? | **YES, and equivalence is EXHAUSTIVE** — 1,801/1,801 beads, zero divergence, 0.0018 s |
| [EXP-003](findings/exp-003-run-timeout-design.md) | How should `run()` be bounded? | Bound **inside the primitive**; local 60 s / network 120 s. **Does not close #268** |
| [EXP-004](findings/exp-004-blast-radius.md) | What breaks? | Almost nothing — one function, **zero call-site edits**. The risk is a **coverage gap** |
| [EXP-005](findings/exp-005-n-plus-1-defect-class.md) | Is this a one-off? | **No** — the identical N+1 was fixed once (REQ-BUP-052) and not swept |
| [EXP-006](findings/exp-006-pruning-baseline.md) | Is DB pruning warranted? | **Three of four premises fail measurement.** Measure first, decide later |

### The load-bearing results

**The diagnosis is validated, and it terminates.** Every prior observation was a kill at 30-120 s,
which cannot distinguish *slow* from *wedged*. Run to completion it is 334 s and exit 0 — a
performance defect with a mechanical fix. #268's arithmetic was ~7% high.

**Two facts the SIGINT traceback could not show.** (a) `owner_claim_warning_lines()` returned
`[]` — on this repository the 336 s buys **no output at all**. (b) The "no stdout" symptom is
Python **block-buffering** stdout to a pipe: the preview was rendered at t≈0 and sat in the buffer
for 334 s. Neither is a separate defect; both dissolve once the path is fast.

**The rewrite is exact, not approximate.** Both edge sets were built in one process and compared
over the **entire** universe: `EQUIVALENT=True, slow_only=0, fast_only=0, targets identical`,
1,648 edges either way. 321.9 s → 0.0018 s, adding **zero** new `bd` calls — it reads a payload
the process already paid for and discarded. `edge_type()` already accepts the `bd list` field
name, so the shape divergence it was written for is exactly this one.

**A per-call timeout would NOT have caught this.** 1,801 individually-*fast* calls (0.186 s) trip
no defensible bound. Epic 2 buys diagnosability for the **next** unbounded call. The plan states
this rather than letting a reader infer that bounding closes #268.

**This defect class has already been remediated once here.** `external_from_row`'s docstring
describes #268 almost verbatim, about `closable`, under REQ-BUP-052 — and `external_for`'s
docstring carries the explicit prohibition *"NEVER call this in a loop over the whole universe"*,
which `cmd_enumerate:615` violates. Prose prohibition demonstrably did not hold. That is why
Epic 3 exists.

### Two traps recorded for execution

1. **The two sources name the target id differently.** `bd show` embeds the full target bead and
   carries the id as `id`; `bd list` uses `depends_on_id`. The chain at `upstream.py:534` handles
   both. A harness comparing on `depends_on_id` alone reads a false 100% divergence.
2. **A latent gate bug is PRESERVED, not fixed.** `load_universe_rows()` omits `--include-gates`,
   so 165 gate parent-child edges are invisible today. The rewrite reproduces that exactly.
   Adding the flag injects those edges into `classify_active`'s ancestor propagation and shrinks
   the candidate set — a spec-visible behavior change, out of scope here (Issue 3.4 files it).

## Approach

Four epics, sequenced SPEC-first per `AGENTS.md`, with the destructive one deliberately last and
independently gated.

**Epic 1 restores the routed path** by deleting the fan-out. The design is not novel — it applies
the shipped `external_from_row` pattern to the call site REQ-BUP-052 missed. `collect_parent_edges`
keeps its signature (`beads.values()` already *are* the rows), so no call site and no existing test
stub changes. The second, smaller N+1 at `:615` goes with it.

**Epic 2 bounds every subprocess.** Independent of Epic 1 and honest about its scope: it fixes
diagnosability, not this hang. The bound is resolved *inside* the primitive from `cmd[0]` — a
measured constraint, since passing `timeout=` at call sites fails three tests and is then masked
as a fake `gh` error by `apply_write`'s broad handler.

**Epic 3 makes recurrence mechanical rather than prose.** A `check_no_universe_fanout.py` in the
established `check_gh_direct.py` shape, wired into the FAST tier, plus the scale-independence
tests the suite lacks entirely.

**Epic 4 investigates pruning, evaluates a non-destructive alternative first, and is authorized to
conclude "no".** It is sequenced last, gated on a human capability gate, and **not** a dependency
of Epics 1-3 — the critical fix must not wait on a destructive-change debate.

The operator raised a **real** problem: `.beads` is **785 MB**. What measurement refutes is the
proposed *remedy*, not the premise — and the honest statement of it is narrow: **deleting rows
cannot reclaim that space, because the space is version history and a `DELETE` in Dolt is another
commit.** (An earlier draft of this plan glossed it as "bead content is only 0.18% of the
directory", which is a category error: `.beads/dolt` and `.beads/backup` are *entirely*
bead-derived. The gloss overstated a sound argument into a refutation of the wrong claim.)

So Epic 4 asks the question the first draft skipped — *what would actually reclaim it?* — and asks
it **before** the destructive path. But the first attempt at answering it over-corrected: it
replaced an overstated dismissal with an **overstated promise**, which is the same failure
mirrored. Two claims were asserted without inspecting the directory, and measurement refuted both:

- **`.beads/backup` (289 MB) is not free to reclaim.** It is the repository's **sole local Dolt
  replica** — a registered backup destination with `remotes: {}`, all 109 archives
  manifest-referenced, synced continuously. Reclaiming it trades DR coverage for space, so it sits
  **behind** the consent gate, not outside it.
- **Dolt GC is a hypothesis, not a remedy.** GC reclaims *unreachable* chunks; `main` history is
  reachable, the store is already archived, and a live `sql-server` must be stopped first.

What survives measurement is smaller and real: **`git-remote-cache` is 118 MB — 15% of the total —
two cache directories untouched since June.** That is the genuinely safe reclamation target, and no
earlier draft of this plan mentioned it. Issue 4.1b now begins by *measuring* the 785 MB rather than
asserting what will shrink it.

The operator's underlying instinct is also **confirmed**, not dismissed: 98% of the universe is
closed, and research-005 measured the analytical value of retained bead *transition* history at
literally zero.

**Deliberately out of scope**, each with a reason: the `--include-gates` edge gap (spec-visible
behavior change, filed as 3.4); an aggregate wall-clock deadline (a different mechanism from a
per-call bound, filed as 3.5). Stdout buffering is **no longer deferred** — it is one keyword, and
`push --apply` over N beads still buffers through 1-2 s per `gh` write, so "it dissolves once fast"
was true only of the preview (Issue 3.6).

**A third N+1 was found during review and is IN scope** (Issue 1.7). `detect_followons` shells
`bd dep list` once per subtree bead from both `cmd_followons` and `cmd_land` — the same shape, the
same removable cause, on the **land-the-plane** path. Deferring it would repeat exactly the mistake
EXP-005 documents: fixing the instance that was filed and not sweeping for siblings.

## Epics

### Epic 0: SPEC-first
- Issue 0.1: Add `REQ-BUP-071` — **no verb shall resolve a per-row field with a per-bead subprocess when the bulk query already carries it**, naming all three call sites (parent-edge collection, `cmd_enumerate`'s `external_ref` loop, and `detect_followons`' dependency loop). Generalize REQ-BUP-052's amendment-1 invariant rather than inventing an unrelated requirement. Bound the claim to `bd list`/`bd show`/`bd dep list` specifically, since `upstream_enabled()` still shells `bd config get`.
  - Broadened from a parent-edge-only wording, which would not have covered Issues 1.3 or 1.7 (pass-1 C7).
- Issue 0.1b: Record the **bd version floor** for `bd list --all --json` carrying `dependencies[]`, as an amendment to `REQ-BUP-055` (the directly applicable precedent, which pins bd 1.1.2 for the `external_ref` capabilities in the same style). Name the fields (`depends_on_id`, `type`), record the version actually measured (**bd 1.2.2**), reconcile it with 055's 1.1.2 floor, and state the omitempty caveat: the key is absent on 122 of 1,801 rows and that means **no dependencies**, not truncation. Label it an assertion, not a measurement, exactly as 055 does.
  - depends-on: 0.1
- Issue 0.2: Add `REQ-BUP-072` — every subprocess spawn shall be bounded; a timeout shall raise a diagnosable error naming the command and the bound; a timeout on a write path shall be treated as UNVERIFIED and halt before any destructive stage; and a timeout on a **config read** shall never be reported as "upstream tracking disabled".
  - depends-on: 0.1b
- Issue 0.3: Add `REQ-BUP-073` — the no-per-bead-subprocess invariant shall be enforced by a mechanical check with a **negative control**, not by prose. Cite EXP-005: the prose prohibition exists in `external_for`'s docstring and did not prevent `cmd_enumerate:615`.
  - depends-on: 0.2
- Issue 0.4: Living-amendment-log entries for 0.1-0.3, **SPEC.md §5 Verification entries for 071/072/073** (every shipped `REQ-BUP-*` has one), an amendment covering Issue 2.5's operator-facing change under `REQ-BUP-056` (whose restrict-and-drop reporting it corrects), and a correction to `load_universe_rows`'s docstring claim that its rows feed a `bd show` walk.
  - depends-on: 0.3

### Epic 1: Eliminate the fan-out
- Issue 1.1: Rewrite `collect_parent_edges` (`upstream.py:524`) to read `beads[bid].get("dependencies")`. Keep the signature, the `edge_type()` call and the `depends_on_id or id or target` chain verbatim — the latter two are what make it source-agnostic. Replace the docstring, which currently asserts the `bd show` mechanism. **HARD CONSTRAINT: do not edit `upstream.py:250`-`:388`** — that region is vendored by `_shared/sync.py` (the `active-set classifier`) and editing it trips the FAST-tier sync check and the `e-active-set-copy-upstream` drift edge.
  - depends-on: 0.1, 0.1b
  - resolves-upstream: #268 (include)
- Issue 1.2: Delete `deps_for_show` (`upstream.py:550`), now dead — `collect_parent_edges` was its only caller repo-wide. Note in the commit that the `deps_for` closures at `:1001`/`:1065` are a different function over `bd dep list`, addressed separately by Issue 1.7.
  - depends-on: 1.1
- Issue 1.3: Replace the `external_for(bid)` loop in `cmd_enumerate` (`:615`) with `external_from_row(r)`, removing the second N+1 and the violation of `external_for`'s own docstring prohibition.
  - depends-on: 1.1
  - resolves-upstream: #268 (include)
- Issue 1.4: Direct unit tests for `collect_parent_edges` over a rows-shaped fixture — `dependencies` present, absent, and carrying a non-parent-child type. The function has **no** real test today. Extend `make_enumerate_universe()` (test_upstream.py:903) to carry `dependencies` arrays, keeping the hand-built `Edge`s for the pure `classify_active` tests.
  - depends-on: 1.1
- Issue 1.5: Verify the three existing `monkeypatch.setattr(up, "collect_parent_edges", lambda _b: edges)` stubs (test_upstream.py:1099/1120/1136) still pass unmodified — the positive control that the signature did not change.
  - depends-on: 1.4
- Issue 1.6: **Hoist the duplicated universe load on the push path.** Spike-measured, post-Epic-1 `push` issues **two** full `bd list --all --json` calls (3.1 MB each): `create_or_update` at `:922` and `owner_claim_warning_lines` at `:1176`. Read the universe once and pass `rows`/`beads` into `owner_claim_warning_lines()`. This also removes a redundant `bd config get`.
  - **`cmd_push` does not currently load the universe at all** — `create_or_update` does, at `:922`. So the hoist requires an explicit choice: either lift the load into `cmd_push` and pass it down to `create_or_update`, or have `create_or_update` return the rows it already read. Pick one and say which; do not assume `cmd_push` has rows in scope.
  - **Adds the test SC1b names**, `test_push_reads_universe_once` — a `_counting_run` assertion that `cmd_push` issues exactly one `bd list --all`. Naming a test in a criterion that no issue creates is pass-1 C6's defect class; this issue owns it.
  - **Requires a test edit this issue owns:** `test_upstream.py:461` stubs `monkeypatch.setattr(up, "owner_claim_warning_lines", lambda: [])` — zero-arg. Adding a parameter breaks it. This does not contradict SC7, which is scoped to the three `collect_parent_edges` stubs.
  - depends-on: 1.1
- Issue 1.7: Apply the same one-call rewrite to `detect_followons`' `deps_for` closures in `cmd_followons` (`:1002`) and `cmd_land` (`:1066`), which shell `bd dep list` once per subtree bead. The enclosing `bd list --parent <pid> --all --json` calls at `:998`/`:1063` already return `dependencies[]` (spike-verified, with `omitempty`).
  - **THIS IS NOT A PURE PERFORMANCE REWRITE — it ACTIVATES a currently-dead destructive path, and that is the whole reason it is gated.** Measured on bd 1.2.2: `bd dep list --json` emits `dependency_type` and **`id`**, with **no `depends_on_id`**. `detect_followons` resolves its edge target as `depends_on_id or target or to` (`:712`), so against live output that chain is **always `None`** — `discovered_into_subtree` is never true and the **`narrow` set is permanently empty today**. `bd list`'s `dependencies[]` *does* carry `depends_on_id`, so switching the source makes `narrow` populate. `narrow` is exactly `plan_land_hoist`'s `auto_eligible` under `auto_hoist_followons=true` (`:1042`) — the **no-prompt path that runs `bd close -r` tombstones**.
  - This is the same situation as R2's gate-edge gap and takes the same treatment: the latent behavior is **named, not silently changed**. Unlike R2 it is *fixed* rather than preserved, because leaving a signal permanently dead is not a defensible steady state — but the fix is placed behind a human gate rather than riding in on a performance issue.
  - **Currently masked, and the plan must not rely on that:** `custom.upstream.auto_hoist_followons` is `(not set)` in this repo, so default-deny makes `auto_eligible` empty and every hoist confirm-required (`:1048`). The skill ships to repos where an operator has set it `true`.
  - **Adds the test SC3c names**, `test_followons_no_per_bead_dep_list` — a `_counting_run` assertion that the follow-on path issues zero `bd dep list`.
  - Also correct the **wrong comment** at `test_upstream.py:132`: the fixture is labelled "(bd dep list shape)" but uses `depends_on_id`, which is the `bd list` shape. It has been green against output bd never produces.
  - depends-on: 1.1
- Issue 1.8: **Add a runtime fail-loud cross-check** against R10's silent fail-open. **The predicate is literal and must be implemented exactly as stated: *any row carries a non-empty `parent` AND zero parent-child edges were derived* -> warn.** It is NOT a count-equality check.
  - **Do not implement count-equality**, and do not repeat the justification an earlier draft gave. Measured on bd 1.2.2 in a sandbox: a bead can carry **two** `parent-child` edges (bd accepts `bd dep add` without complaint), yielding 3 edges vs 2 rows-with-`parent`. EXP-002's `1,648 == 1,648` is a property of **this corpus**, not an invariant, so a count-equality check would false-alarm on any multi-parent bead.
  - **What makes the stated predicate sound is a different, structural fact:** `bd dep add --type parent-child` *sets* `parent` and `bd dep remove` *clears* it — `parent` is **derived from** the edge. So `parent set => at least one parent-child edge` holds by construction, which makes the predicate false-alarm-free while still firing exactly on R10's failure mode. The two fields are therefore **not independent corroboration**; one is derived from the other.
  - **Adds the test SC2b names**, `test_parent_without_edges_warns` — rows carrying `parent` with zero derived edges produce the warning on stdout.
  - **Surface it INLINE ON STDOUT, not stderr.** This codebase has already measured that stderr is the channel the routed consumer never sees: `owner_claim_warning_lines`' own docstring records the #105 residual — "the shipped warning is stderr-only, so an agent piping `--json` to `jq` never sees it" (REQ-BUP-051). Putting R10's only runtime layer on stderr would reintroduce exactly that defect.
  - depends-on: 1.1
- Issue 1.9: Re-run the EXP-001 end-to-end reproduction post-fix and record the wall clock **to `assets/post-fix-timing.md`** (the artifact the "Fan-out eliminated" gate tests for), as the evidence producer the "Fan-out eliminated" gate's timing clause needs. Safe to re-run: without `--apply`, `create_or_update` returns before any write (`upstream.py:930`). Also measure **cold-start** `bd` latency against the 494 MB Dolt store — every timing in `findings/` is warm, and the 60 s bound rests on that untested premise.
  - depends-on: 1.1, 1.3, 1.6

### Epic 2: Bound every subprocess (independent defect)
- Issue 2.1: Add `LOCAL_TIMEOUT_S = 60`, `NETWORK_TIMEOUT_S = 120`, `NETWORK_COMMANDS = frozenset({"gh"})` and `timeout_for(cmd)`. Comment why `cmd[0] == "bash"` classifies LOCAL — all four `bash -c` sites wrap `bd close`/`bd update`, which is opaque at the classifier.
  - depends-on: 0.2
  - resolves-upstream: #268 (include)
- Issue 2.2: Bound `run()` as `def run(cmd, *, timeout=None)` resolving `None -> timeout_for(cmd)`. Raise `SystemExit(f"command TIMED OUT after {bound}s: ...")`. **Do not pass `timeout=` at any call site** — measured, that fails 3 tests and `apply_write`'s broad handler masks the `TypeError` as a gh failure.
  - depends-on: 2.1
- Issue 2.3: Bound `run_unchecked()`, wrapping `TimeoutExpired` into `UpstreamQueryError`. Required: `TimeoutExpired` is **not** an `OSError`, so `resolve_upstream_states:164` would otherwise bypass its REQ-BUP-064 INCONCLUSIVE verdict and emit a traceback.
  - depends-on: 2.1
- Issue 2.4: Bound `_config_get()` (`:185`, no handler today). Return `""` so consumers fall to default-deny, **and distinguish the timeout cause from a genuine disabled state**: on timeout `cmd_push` shall exit **non-zero** reporting "upstream state UNDETERMINED (config read timed out)", never "disabled; nothing to push". Otherwise a transient `bd` hiccup silently converts a mandated upstream write into a success-shaped no-op, with no compliant fallback available to the operator.
  - depends-on: 2.1
- Issue 2.5: **Adds the test SC5b names**, `test_existing_labels_read_failure_is_not_reported_as_missing`. Fix `existing_labels()`'s (`:805`) false report — a failed read currently renders to the operator as "dropping label X (does not exist upstream)", which is untrue. Pre-existing, but Epic 2 adds a new route into it. Covered by Issue 0.4's `REQ-BUP-056` amendment.
  - depends-on: 2.1
- Issue 2.6: **Names its tests explicitly** — including `test_config_timeout_is_undetermined` (SC4c's selector). Tests: a bounded `run()` on `bash -c "sleep 5"` raises `SystemExit` naming the bound and argv; `run_unchecked` yields `UpstreamQueryError` and `resolve_upstream_states` reports INCONCLUSIVE; a timed-out `_config_get` makes `cmd_push` exit non-zero with UNDETERMINED, not "disabled"; `timeout_for` classifies `gh`/`bd`/`bash` correctly.
  - depends-on: 2.2, 2.3, 2.4
- Issue 2.7: **Names its test explicitly** — `test_hoist_timeout_closes_no_bead` (SC5's selector). Regression guard for REQ-BUP-050: `cmd_hoist(..., apply=True)` with a timing-out create returns 1, prints "No bead was closed", and **never** invokes `bd close`/`bash` (assert-trap the stub). Verified to hold in the EXP-003 spike; asserted here rather than assumed.
  - depends-on: 2.6

### Epic 3: Prevent recurrence
- Issue 3.1: Add `check_no_universe_fanout.py` as an **AST check** (`ast.parse` + `ast.walk`), not a token/substring scanner. **This supersedes the substring idiom two earlier drafts tried**, and the reason is measured: substring matching failed in *both* directions here.
  - **Why AST, in one line each:** a blanked-token scan **under-matches** — `check_gh_direct.py` blanks every `STRING` token, so `run(["bd","dep","list",...])` becomes `run([ , , , ])` and never matches (pass-2 D2). A raw-source scan **over-matches** — the only unblanked `bd dep list` in the tree is `edge_type()`'s **docstring at `:664`**, so the check would be **red on correctly-fixed code** and the executor's only escape would be deleting a docstring `check_gh_direct.py`'s design forbids erasing and Issue 1.1 depends on keeping (pass-3 H1). AST matches the *construct* and is blind to both comments and prose.
  - **Rules this issue ships, each stated as a construct:** (b) a `Call` to `run`/`run_unchecked` whose leading `Constant`s are `bd`,`show`, **or a call to a name whose own body issues such a call**, occurring inside a `For`/`While`/comprehension — **exempting calls whose enclosing `FunctionDef` is on rule (e)'s allow-list (`cmd_mappings`, `plan_hoist`)**, without which rule (b) is red on the legitimate comprehension at `:650`; (c) `deps_for_show` must not be reintroduced as a `FunctionDef`; (d) `--check-timeouts` mode: a `Call` to `subprocess.run` whose enclosing `FunctionDef` is not one of `run`/`run_unchecked`/`_config_get`; (e) `external_for(` may be called only from `cmd_mappings`/`plan_hoist`.
  - **Rule (b) MUST cover the helper-mediated form, or it detects neither N+1 this plan fixes.** Measured: the only `bd show` argv sites are `:474` (inside `external_for`) and `:552` (inside `deps_for_show`) — **neither is lexically inside a loop**. The #268 defect was `for bid in sorted(beads): deps_for_show(bid)` at `:533`, and the second N+1 was `external_for(bid)` at `:615`: both call a *helper* from the loop. A rule matching only a literal argv inside a `for` would not have fired on the pre-fix code and would not fire on its reintroduction.
  - **Rule (e) is enumerated, not merely referenced.** It is the rule that catches a `:615` recurrence. Its allow-list exists for the legitimate `[external_for(bid) for bid in ids]` in `cmd_mappings` (`:650`).
  - **INVARIANT: no rule in this issue may presuppose Issue 1.7 having landed.** Issue 1.7 sits behind a consent gate that may legitimately **decline**, and a rule that is red until 1.7 lands would make the "Mechanical fan-out check green" gate permanently unpassable, block 3.2 forever, and leave the `auto` Reconcile Gate unable to fire — the plan would be unclosable on a legal operator answer. That is why the `bd dep list` construct rule lives in **Issue 3.1c**, which is already downstream of 1.7 and already N/A under a decline.
  - **Enclosing-function tracking is DECLARED WORK, once, and covers every rule that needs it** — rule (d), and the `external_for`-restricted-to-`cmd_mappings`/`plan_hoist` rule. An earlier draft budgeted it for one and silently assumed it for the other. An AST walk gives it for free (track the `FunctionDef` ancestor), which is the third independent reason to use AST here.
  - **Do not ban the bare name `deps_for`** — see Issue 3.1c.
  - Record, and **file separately** (Issue 3.8), that `check_gh_direct.py`'s own `FORBIDDEN_SUBSTRINGS` are largely **vacuous** for the under-matching reason above. Inherit the idiom's lesson, not its defect.
  - depends-on: 0.3, 1.1
- Issue 3.1b: **BOTH controls, rule-for-rule** — for every rule Issue 3.1 ships: a **negative control** (a fixture containing the banned construct, asserted to exit **1**) *and* a **positive control** (that rule asserted **green** against the intended post-fix source).
  - **Negative-only is not enough, and this is the measured lesson of the last two cycles.** A negative control catches a rule that cannot fire (pass-2 D2's under-match). Only a **positive** control catches a rule that fires on correct code (pass-3 H1/H2's over-match) — the failure mode that would have made the gate unpassable. Two cycles produced one of each; requiring both is what closes the class.
  - **Also depends on 1.2**, because rule (c) bans `deps_for_show` as a `FunctionDef` and Issue 1.2 is what deletes it; running 3.1b first would show a red positive control for a correct rule.
  - depends-on: 3.1, 1.2
- Issue 3.1c: Add the **two rules that presuppose Issue 1.7**, plus their negative *and* positive controls: **(a)** a `Call` to `run`/`run_unchecked` whose first argument is a `List` whose leading `Constant`s are `bd`,`dep`,`list`; and the per-bead-dependency-closure rule, **as a construct and not as a bare name** — *a nested `FunctionDef` whose body calls `run`/`run_unchecked` with a per-bead argv*.
  - **Rule (a) belongs HERE, not in 3.1.** Verified by execution against the live tree: it matches exactly `:1002` and `:1066`, which **only Issue 1.7** rewrites. Shipping it in 3.1 (which depends on 1.1, not 1.7) would make the check red on the tree until 1.7 lands — and permanently red if the operator **declines** at the Follow-on activation gate, rendering that gate unpassable and the plan unclosable. It also makes 3.1b's *positive* control unsatisfiable, since the post-fix source it asserts green against would never exist. The two rules are near-duplicates targeting the same two lines, so they belong together.
  - **A bare-name ban on `deps_for` would be red after Issue 1.7 lands.** Measured: `deps_for` occurs at `:686` (the **injected parameter** of `detect_followons`), `:698` (docstring), `:709`, `:1005` and `:1069`. Issue 1.7 rewrites the closure *bodies* at `:1001`/`:1065`; the parameter and its call sites **survive by design** — Issue 3.1's own text notes `detect_followons` takes `deps_for` injected. Banning the name would forbid the very injection seam that makes the function testable.
  - Split from 3.1 because it can only pass once Issue 1.7 has landed, and 1.7 is gated on the Follow-on activation consent gate. Keeping it separate means the core recurrence guard is not held behind a consent decision about an unrelated destructive path.
  - depends-on: 3.1b, 1.7
- Issue 3.2: Wire `check-no-universe-fanout` into `CHANGE-VALIDATION.md` §1 fast tier, beside `bup-prescriptive-push` and `bup-gh-direct`.
  - depends-on: 3.1b
- Issue 3.3: **Names its tests explicitly** — `test_push_zero_bd_show`, `test_enumerate_zero_bd_show`, and `test_enumerate_scale_independence` — so a criterion's `-k` selector cannot be satisfied by an unrelated pre-existing test. (Measured: `-k zero_bd_show` alone already matches the passing `test_closable_issues_one_bd_list_and_zero_bd_show` at `:685`.) Scale-independence tests modeled on `test_closable_issues_one_bd_list_and_zero_bd_show` (test_upstream.py:685) and `..._does_not_grow_with_universe_size` (:719): a `_counting_run` fixture asserting `cmd_enumerate` and `push` issue **zero `bd show`** and a **universe-size-independent** number of `bd list` calls — equal at 10 and 1,000 beads. The zero-`bd show` half is the load-bearing invariant; the call count is pinned to whatever Issue 1.6 leaves it at, not asserted as "one" a priori.
  - depends-on: 1.1, 1.3, 1.6
- Issue 3.4: File the `--include-gates` edge gap upstream as its own issue (165 invisible parent-child edges). **Do not fix it here** — it changes `classify_active`'s candidate set and is spec-visible.
  - depends-on: 1.1
- Issue 3.5: File the aggregate wall-clock deadline / progress-heartbeat idea upstream. A per-call bound cannot bound total runtime; conflating the two is what would let a reader believe Epic 2 closes #268.
  - depends-on: 2.2
- Issue 3.8: File the **`check_gh_direct.py` `FORBIDDEN_SUBSTRINGS` vacuity** defect upstream — its needles (`bd github push` and siblings) are string literals, which its own blanking pass erases before matching, so several of its contract rules cannot fire. Independent of this plan; Issue 3.1's text calls for the filing and no issue owned it.
  - depends-on: 3.1
- Issue 3.7: File the **`narrow`-always-empty** defect upstream as its own issue — a live correctness bug in shipped code, independent of this plan: `detect_followons` resolves its edge target as `depends_on_id or target or to`, but `bd dep list --json` emits only `id`, so the follow-on auto-eligible signal has never fired. Filing it separately is what makes Issue 1.7's activation a reviewed decision rather than a side effect.
  - **Deliberately depends on 1.1, NOT on 1.7.** The defect is real and shipped whether or not the operator consents to activation, and making the filing downstream of the consent gate would mean a decline leaves a live correctness bug unfiled forever. It also inverts the reason the filing exists: it is **pre-read material for that gate's decision**, so it must land before it.
  - depends-on: 1.1
- Issue 3.6: Update `SKILL.md` where it describes the push/enumerate cost model, record Issue 1.9's measured post-fix timing, and add `flush=True` to the push-path prints. The buffering fix is one keyword and `push --apply` over N beads still buffers through 1-2 s per `gh` write, so deferring it was the weakest of the three deferrals.
  - depends-on: 1.9

### Epic 4: Reclaim disk and evaluate pruning — measure, then decide (separable, gated)
- Issue 4.1: Re-measure the pruning justification on its own grounds, with #268's cost removed: DB size, query latency post-Epic-1, cognitive load, backup cost. EXP-006 already refutes the row-count-drives-size premise; this issue tests the rest and **is authorized to return "not warranted yet"** as a complete, satisfying outcome.
  - depends-on: 1.1
- Issue 4.1b: **Measure the 785 MB properly, then reclaim what is provably safe. NON-DESTRUCTIVE TO BEAD CONTENT — deliberately UNGATED, with an explicit safety precondition.** An earlier draft asserted two reclamation wins without inspecting the directory; both were wrong or overstated, so this issue's first act is a real breakdown rather than `du -sh`.
  - **Measured breakdown (recorded so the issue starts from fact):** `.beads/dolt` 494 MB = `yoshiko_flow/.dolt/noms` **375 MB** (105 MB live journal + 232 MB already-archived `oldgen/*.darc` + 2.2 MB idx) + **`git-remote-cache` 118 MB** + ~656 KB. Plus `.beads/backup` 289 MB.
  - **Reclaim `git-remote-cache` (118 MB, 15% of the total)** — two cache directories last touched 2026-06-01 and 2026-06-20, a cache by name and by mtime. Verify it is regenerable, then reclaim.
  - **Test the Dolt-GC hypothesis** (it is a hypothesis, not a remedy): GC reclaims *unreachable* chunks while all `main` history is reachable; the store is already archived, bounding any win at roughly the 105 MB journal; and a live `dolt sql-server` must be stopped first — a `bd dolt stop`-class flush is a **precondition of this issue**, the same hazard `YOSHIKO_FLOW.md`'s wedged-migration protocol exists for. "History squash" is not a Dolt operation; the term is dropped.
  - **PRECONDITION, because two of these three acts mutate live state.** This issue deletes 118 MB of cache and stops a live `dolt sql-server` to test GC against the repository's own 494 MB bead store — the store this plan's beads are tracked in. Before either: verify `.beads/backup` is current and `bd status` is healthy; re-verify after. `.beads/backup` still exists at this point (Issue 4.1d is downstream and gated), so DR coverage is intact — that is *why* this sequencing is safe, and it must not be reordered. "Non-destructive" here means **no bead content is deleted**; it does not mean nothing is written.
  - **This issue carries the evidence the Pruning Authorization gate's Condition depends on, which is exactly why it must NOT sit behind that gate** (pass-3 H3): a gate cannot block its own evidence, and a `Blocks` edge blocks a bead **whole**, so a prose carve-out is unenforceable at bead granularity.
  - depends-on: 4.1
- Issue 4.1d: **Decide the `.beads/backup` DR-versus-space trade. DESTRUCTIVE — behind the Pruning Authorization gate.**
  - **The earlier "very likely rotatable with zero data loss" claim was WRONG and is withdrawn.** Measured: `repo_state.json` registers `.beads/backup` as a Dolt **backup destination** (`"backups": {"backup_export": {...}}`) with `"remotes": {}` and `dolt.local-only: true`. It is a content-addressed Dolt store, not dated snapshots — **all 109 `.darc` archives are manifest-referenced** — and bd syncs it continuously. `bd backup restore` reads it. **It is the repository's SOLE local Dolt replica.**
  - Nothing in it can be individually rotated. The only available operation is destroying the whole DR copy, which trades disaster-recovery coverage for 289 MB. That is a judgement only the operator can make.
  - depends-on: 4.1b
- Issue 4.2: Design a defensible purge predicate. The operator's "closed AND upstreamed" selects **52 of 1,764** because `AGENTS.md` mandates coarse granularity — sub-beads never get an `external_ref` by design. Evaluate parent-epic pairing and plan-bundle closure instead.
  - depends-on: 4.1b
- Issue 4.3: Resolve the `closable` conflict. Purging closed rows breaks REQ-BUP-052 by construction, and the 52 rows the naive predicate selects are exactly the rows `closable` reads. Either the design excludes them or `closable` is reworked in the same change.
  - depends-on: 4.2
- Issue 4.4: Evaluate the narrower, better-supported target: `.beads/interactions.jsonl` transition history (872 KB, clone-local, gitignored), whose analytical value research-005 measured at zero. Preserve `close_reason` prose unconditionally — 745 closed beads carry >200 chars of it.
  - depends-on: 4.1
- Issue 4.4b: **SPEC-first for `yf-beads-hygiene`.** Issue 4.5 adds a destructive verb to a skill with its own `SPEC.md` and 28 `REQ-*` ids; `AGENTS.md`'s SPEC-first mandate is unconditional and Epic 0 covers only `yf-beads-upstream`. Land the `REQ-HYG-*` requirement — including the dry-run-by-default contract and the export-restore round-trip — before any implementation.
  - depends-on: 4.3, 4.4
- Issue 4.5: Only if 4.1-4.4b justify it: implement export-first, reversibly-tombstoned, operator-gated pruning in `yf-beads-hygiene`, preserving its read-only-first posture. The verb shall be **dry-run by default with a separate `--apply`** (what preserves that posture in repos where this plan's gate does not exist), and the **export must be proven restorable by a round-trip test before the destructive path is reachable** — "export-first" is worthless if the export was never shown to be usable. Blocked by the Pruning Authorization gate.
  - depends-on: 4.4b

## Gates

> **Known grammar gap — the `test_class` / `cwd` lines below do NOT survive extraction.**
> `plan_extract.py`'s gate-field grammar accepts only `Type|Approvers|Condition|Test|Blocks|Instructions`,
> so `plan_extract.py --json` reports `test_class: None` for every gate here (verified on this
> document). That is the defect plan-056 / #266 is filed against, not a defect in this plan. They are
> written anyway because they are the correct values and cost nothing; **at pour time (SKILL.md §5.2a)
> the executing session must set `gate_type`, `test`, `test_class` and `cwd` as bead METADATA**, which
> is what the §5.2c sweep actually reads. Without that step every gate below defaults to `manual` and
> the sweep runs none of them.

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: Fan-out eliminated
- Type: auto
- Condition: `collect_parent_edges` derives edges with zero per-bead subprocesses, and Issue 1.9 has recorded a post-fix end-to-end `push` wall clock
- Test: sh -c 'uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q && test -s docs/plans/plan-058-james-dixson-0e36fd/assets/post-fix-timing.md'
- Blocks: 3.1, 3.3
- Instructions: Run the FAST-tier suite. The operative assertions are Issue 1.4's direct unit tests of `collect_parent_edges` and Issue 1.9's recorded timing — both of which land BEFORE this gate. Do not cite Issue 3.3 here: 3.3 is in this gate's own Blocks set, so naming its tests as the evidence would make the gate depend on work it gates (pass-1 C3). The Test has **two** clauses because a pytest run cannot observe a wall clock: the `test -s` half asserts Issue 1.9's timing artifact actually exists, so the gate cannot pass green on an unrecorded measurement (pass-2 D9).
- test_class: build
- cwd: worktree

### Capability Gate: Mechanical fan-out check green
- Type: auto
- Condition: the no-universe-fan-out contract check passes over `upstream.py`
- Test: uv run skills/yf-beads-upstream/scripts/check_no_universe_fanout.py
- Blocks: 3.2
- Instructions: Exit 0 = clean. A failure names the offending construct; remove the loop rather than the check.
- test_class: probe
- cwd: worktree

### Capability Gate: Follow-on activation
- Type: human
- Approvers: operator
- Condition: the operator has read Issue 1.7's stated semantic change (and Issue 3.7's filed defect, which lands first as pre-read) and either **accepts** that the `narrow` follow-on signal — dead since it was written — becomes live, making `plan_land_hoist`'s no-prompt `bd close -r` tombstone path reachable in repos where `auto_hoist_followons` is `true`; **OR declines activation**, in which case Issues 1.7 and 3.1c are closed as `wontfix-for-now`, Issue 3.7 still files the defect, and SC3c/SC3d/SC6c are marked **N/A**
- Blocks: 1.7
- Instructions: This gate exists because Issue 1.7 is filed as a performance rewrite but is **not behavior-preserving**, and the behavior it changes is an unattended destructive one. **A DECLINE IS A FIRST-CLASS OUTCOME AND MUST CLOSE THE EPIC CLEANLY** — without the decline branch, refusing would strand 1.7, 3.1c and 3.7 open forever and the `auto` Reconcile Gate (all execution beads closed) could never fire, so the plan would stall on a legal answer (pass-3 H4). This mirrors the Pruning Authorization gate's "not warranted yet" pattern. Issue 3.7 files the underlying defect regardless of the decision, and is deliberately **not** downstream of this gate. It is deliberately **off the #268 critical path**: Issue 1.7 is the third N+1 (the land-the-plane follow-on path), not the fan-out, so Epics 1-3 can land and close #268 with this gate unresolved. A green test cannot substitute — no measurement establishes that an operator *wants* an auto-hoist path activated.
- test_class: consent
- cwd: repo-root

### Capability Gate: Pruning Authorization
- Type: human
- Approvers: operator
- Condition: the operator has read Issue 4.1's measurements and explicitly authorizes a destructive prune, OR accepts "not warranted yet" and closes Epic 4 without implementing
- Blocks: 4.5, 4.1d
- Instructions: This gate exists because 4.5 is irreversible and because three of the proposal's four premises already failed measurement. A green measurement is not authorization. "Not warranted yet" is an acceptable resolution that closes the epic with no code change. It **also** blocks **Issue 4.1d**, the `.beads/backup` deletion: that directory is the repository's sole local Dolt replica (109 of 109 archives manifest-referenced, continuously synced), so reclaiming it destroys DR coverage and is not the outside-the-gate freebie an earlier draft called it. **The destructive half is a SEPARATE ISSUE precisely so this gate can block it without blocking its own evidence** (pass-3 H3) — `Blocks` operates on whole beads, so a prose carve-out inside one issue would have been unenforceable. Issue 4.1b (the measurement, the `git-remote-cache` reclamation, and the Dolt-GC test) is non-destructive, ungated, and proceeds regardless of how this gate resolves.
- test_class: consent
- cwd: repo-root

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | The rewrite silently changes the edge set, altering which beads are push candidates | high | Retired by measurement, not mitigation: equivalence proven over **1,801/1,801** beads, zero divergence both directions (EXP-002). Issue 1.4 adds the permanent regression test the suite lacks |
| R2 | The change accidentally "fixes" the gate-edge gap, shrinking the candidate set | med | Explicitly preserved and documented (EXP-002 trap 2); Issue 3.4 files it separately. The rewrite reads the same `load_universe_rows()` output, so preservation is structural |
| R3 | A reader concludes Epic 2 closes #268 | med | Stated in the Approach, in EXP-003 and in Issue 3.5. A per-call bound cannot catch 1,801 fast calls |
| R4 | Adding `timeout=` breaks the 17 single-positional-arg `run` stubs | med | Measured: bounding inside the primitive passes 107/107; passing at call sites fails 3. Issue 2.2 forbids the latter explicitly |
| R5 | A timeout on a `gh` write leaves an issue created with no `external_ref` | high | Routes into the existing UNVERIFIED/DUPLICATE message class; fail-closed verified in the EXP-003 spike and asserted by Issue 2.7 |
| R6 | Epic 4 destroys durable institutional memory | high | Sequenced last, not a dependency of Epics 1-3, behind a human consent gate; export-first + reversible tombstones required; `close_reason` preserved unconditionally (Issue 4.4) |
| R7 | Epic 4 gates the critical fix on a destructive-change debate | high | No Epic 1-3 issue depends on any Epic 4 issue. Epic 1 can land and deploy with Epic 4 unstarted |
| R8 | Editing the vendored `active-set classifier` region trips `_shared/sync.py --check` | med | Every function touched is **outside** the `:250`-`:388` fence (EXP-004); recorded as a hard constraint for execution |
| R9 | The mechanical check is too narrow and misses the next variant | med | Accepted and stated: it matches a fixed set of **AST constructs**, not every possible N+1. Strictly better than the prose prohibition that already failed (EXP-005), and not a claim of completeness. Issue 3.1b's **paired** controls — negative *and* positive, rule-for-rule — prove each rule both fires on the banned shape and stays green on correct code; two review cycles produced one failure of each kind, which is why both are required |
| R10 | A future `bd` stops carrying `dependencies[]`, and `collect_parent_edges` silently returns `[]` — losing ancestor propagation so MORE beads become push candidates, failing toward extra upstream writes, invisibly | high | Three layers, because fixture tests cannot catch this: a version floor recorded as an assertion in the `REQ-BUP-055` style (0.1b); a runtime fail-loud cross-check whose predicate is *any row carries `parent` AND zero parent-child edges were derived* (1.8) — sound because `parent` is **derived from** the edge (`bd dep add` sets it, `bd dep remove` clears it), and explicitly **NOT** a count-equality check, which would false-alarm: measured, bd accepts two parent-child edges on one bead, so EXP-002's 1,648/1,648 is a property of this corpus and not an invariant; and the honest labelling that the floor is the version *verified*, not the version below which it breaks |
| R11 | Epic 4 answers only why the operator's remedy fails and never asks what would actually reclaim 785 MB | med | Issue 4.1b measures the 785 MB and reclaims what is provably safe — `git-remote-cache` (118 MB) — **outside** the consent gate, and tests the Dolt-GC hypothesis there too. The `.beads/backup` half is **inside** the gate as Issue 4.1d, because that directory is the sole local Dolt replica and deleting it trades DR coverage for space. SC9b requires all three candidates reported on their merits whatever Epic 4 concludes about pruning. Raised by pass-1 C9; corrected by pass-2 D3 and pass-3 H3 |
| R12 | A `bd` config-read timeout silently converts a mandated upstream write into a success-shaped no-op | med | Issue 2.4 makes the timeout cause exit non-zero as UNDETERMINED, distinct from a genuine "disabled". Without this the operator has no signal and no compliant fallback, since hand-running the underlying commands is forbidden |
| R14 | Issue 1.7 activates the `narrow` follow-on signal, which has been **dead since it was written**, turning `plan_land_hoist`'s no-prompt `bd close -r` tombstone path from unreachable to reachable | high | Treated in R2's idiom — **named, not silent**. The semantic change is stated in Issue 1.7's body, the underlying defect is filed separately by Issue 3.7, and the activation sits behind the Follow-on Activation gate. Currently masked by `auto_hoist_followons` being unset (default-deny, `:1048`) in this repo — recorded as a mitigating fact the plan explicitly does **not** rely on, since the skill ships elsewhere |
| R15 | A mechanical check ships with a rule that **cannot match**, so the gate and SC6 pass green over an unenforced invariant | high | Spike-proven for the `bd dep list` rule (`check_gh_direct.py` blanks STRING tokens). Issue 3.1 now scopes each rule to what the idiom enforces and declares the unblanked-source scan as a deliberate departure; Issue 3.1b requires a negative-control fixture **rule-for-rule**, so an unmatchable rule fails before execution rather than during it |
| R13 | Every timing behind the 60 s local bound was measured warm; cold-start `bd` against a 494 MB Dolt store is untested | low | Issue 1.9 measures it. The bound has ~200x headroom on warm numbers, so the risk is small, but it is an untested premise behind a new hard failure mode and is measured rather than assumed |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | The push path spawns **zero** per-bead subprocesses | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q -k 'push_zero_bd_show or enumerate_zero_bd_show'` -> exit 0 | 1.1, 1.3, 3.3 |
| SC1c | `upstream.py push --issues <id>` completes in **seconds, not minutes**, on a >=1,800-bead universe (baseline: 334 s) | manual: read Issue 1.9's recorded wall clock in `assets/post-fix-timing.md` — a mocked call-count test cannot observe wall clock, so this criterion is discharged by measurement, not by the suite | 1.9 |
| SC1b | The push path reads the bead universe **once**, not twice | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q -k push_reads_universe_once` -> exit 0 | 1.6 |
| SC2 | The post-fix parent-child edge set is identical to the pre-fix set | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q -k collect_parent_edges` -> exit 0 | 1.1, 1.4 |
| SC2b | A bd version that stops carrying `dependencies[]` fails LOUDLY rather than silently returning no edges | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q -k parent_without_edges_warns` -> exit 0 | 1.8 |
| SC3 | `cmd_enumerate` and `push` issue a `bd` call count **independent of universe size** (equal at 10 and 1,000 beads) | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q -k scale_independence` -> exit 0 | 1.1, 1.3, 1.6, 3.3 |
| SC3b | `deps_for_show` is gone and no caller remains | `sh -c '! grep -n "deps_for_show" skills/yf-beads-upstream/scripts/upstream.py'` -> exit 0 | 1.2 |
| SC3d | Issue 1.7's activation of the `narrow` follow-on signal is a recorded, reviewed decision — not a side effect of a performance change | manual: the semantic change is stated in Issue 1.7, carried by risk R14, gated, and the underlying defect filed by Issue 3.7 | 1.7, 3.7 |
| SC3c | **N/A — Follow-on activation DECLINED at its gate.** (Original criterion: the land-the-plane follow-on path issues no per-bead `bd dep list`.) | manual: N/A by the Follow-on activation gate's own Instructions, which specify that on a decline *"Issues 1.7 and 3.1c are closed as `wontfix-for-now` … and SC3c/SC3d/SC6c are marked **N/A**"*. Issue 1.7 did not land, so the test this named (`-k followons_no_per_bead_dep_list`) was never written and the command **correctly exits 5**. The underlying defect is filed as [#280](https://github.com/dixson3/yoshiko-flow/issues/280). | 1.7 (wontfix-for-now) |
| SC4 | Every subprocess spawn in `upstream.py` is bounded, and a timeout names the command and the bound | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q -k timeout` -> exit 0 | 2.1, 2.2, 2.3, 2.4, 2.6 |
| SC4b | No unbounded `subprocess.run` remains in `upstream.py` | `uv run skills/yf-beads-upstream/scripts/check_no_universe_fanout.py --check-timeouts` -> exit 0 | 2.2, 2.3, 2.4, 3.1 |
| SC4c | A config-read timeout is never reported as "upstream tracking disabled" | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q -k config_timeout_is_undetermined` -> exit 0 | 2.4 |
| SC5 | A timeout on a write path halts before any destructive stage and closes no bead | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q -k hoist_timeout_closes_no_bead` -> exit 0 | 2.7 |
| SC5b | A failed label read is never reported to the operator as "label does not exist upstream" | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q -k existing_labels` -> exit 0 | 2.5 |
| SC6 | Reintroducing a banned per-bead-subprocess shape **fails** the check — verified by a negative control, not by a green run on clean code | `uv run skills/yf-beads-upstream/scripts/test_check_no_universe_fanout.py` -> exit 0 | 3.1, 3.1b |
| SC6c | The `deps_for` rule and its negative control ship once Issue 1.7 has landed, without having gated the core check on the Follow-on activation consent gate | `uv run skills/yf-beads-upstream/scripts/test_check_no_universe_fanout.py` -> exit 0 | 3.1c |
| SC6b | The check runs in the FAST tier on every edit under `skills/yf-beads-upstream/scripts/**` | `sh -c 'grep -q "check_no_universe_fanout" CHANGE-VALIDATION.md'` -> exit 0 | 3.2 |
| SC7 | The existing test suite passes with no modification to the three `collect_parent_edges` stubs | `uv run --with pytest python3 -m pytest skills/yf-beads-upstream/scripts/test_upstream.py -q` -> exit 0 | 1.5, 2.6 |
| SC8 | Every `yf-beads-upstream` behavior change is covered by a landed `REQ-BUP-*` that precedes its implementation | `sh -c 'grep -q REQ-BUP-071 skills/yf-beads-upstream/SPEC.md && grep -q REQ-BUP-072 skills/yf-beads-upstream/SPEC.md && grep -q REQ-BUP-073 skills/yf-beads-upstream/SPEC.md'` -> exit 0 | 0.1, 0.1b, 0.2, 0.3 |
| SC8b | **N/A — no destructive verb was added.** (Original criterion: `yf-beads-hygiene` has its own landed requirement carrying the dry-run-by-default contract, before any destructive verb.) | manual: N/A. The criterion is conditioned on *"before any destructive verb"*, and the operator accepted **"not warranted yet"** at the Pruning Authorization gate, so Issues 4.4b and 4.5 closed unimplemented. `grep "dry-run by default" skills/yf-beads-hygiene/SPEC.md` **correctly exits 1** — landing a requirement that protects nothing would be the mirror defect of skipping one that does. | 4.4b (wontfix-for-now) |
| SC8c | The SPEC §5 Verification entries exist for each new `REQ-BUP-*` | `sh -c 'grep -q "REQ-BUP-073 is checked" skills/yf-beads-upstream/SPEC.md'` -> exit 0 | 0.4 |
| SC9 | Epic 4 reaches an explicit, measured, operator-acknowledged decision — implement or "not warranted yet" — and either outcome closes the epic | manual: the Pruning Authorization gate is a human consent gate; no command can establish that an operator authorized an irreversible deletion | 4.1, 4.2, 4.3, 4.4, 4.4b, 4.5 |
| SC9b | All three disk-reclamation candidates are measured and reported on their merits — each with its true risk class — whatever Epic 4 concludes about pruning | manual: Issue 4.1b records (a) `git-remote-cache` **safe, reclaimed**, (b) Dolt GC **hypothesis, tested, win bounded by the ~105 MB journal**, and Issue 4.1d records (c) `.beads/backup` **consent-gated, DR-versus-space**. No figure is promised in advance | 4.1b, 4.1d |
| SC10 | **All four** separately-filed defects are filed upstream rather than silently dropped | manual: verify an open upstream issue exists for each of — the `--include-gates` edge gap (3.4), the aggregate wall-clock deadline (3.5), the `narrow`-always-empty follow-on defect (3.7), and `check_gh_direct.py`'s vacuous `FORBIDDEN_SUBSTRINGS` (3.8) | 3.4, 3.5, 3.7, 3.8 |
| SC11 | `SKILL.md`'s description of the push/enumerate cost model matches the measured post-fix behavior | manual: prose agreement, checked by reading `SKILL.md` against Issue 1.9's recorded timing | 1.9, 3.6 |

### Execution outcome (recorded at reconcile)

Full evidence in [assets/final-criteria-sweep.md](assets/final-criteria-sweep.md); the pre-work
baseline is [assets/instrument-sweep.md](assets/instrument-sweep.md).

- **17 instruments flipped red to green** — 15 progress criteria plus both capability-gate Tests.
- **SC7 is the sole INVARIANT criterion** and was green before *and* after, as a regression guard
  must be. It was never "fixed" into failing.
- **SC3c, SC6c and SC8b are N/A**, each a direct consequence of an operator decline at a human
  gate — the outcome those gates' own Instructions specify.
- **SC6c is N/A *despite passing*.** Its `Verification` command is byte-identical to SC6's, so it
  goes green whether or not Issue 3.1c shipped — it cannot discriminate the claim it makes. This is
  the vacuous-criterion class this plan's own reviews caught four instances of; it is reported as
  found, not counted as a pass.
- **Two of this plan's own estimates were corrected against measurement during execution**: the
  Dolt-GC upside is bounded by an **11 MB** journal, not the 105 MB assumed (an order of magnitude
  in the plan's favour, which *weakens* the GC case); and `close_reason` prose spans **804** beads
  over 200 chars, not 745.
