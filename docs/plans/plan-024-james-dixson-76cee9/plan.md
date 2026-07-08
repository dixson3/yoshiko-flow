# Plan: yf-plan lifecycle-integrity hardening: ready-for-approval gate (#69) + cascade-close containers on plan completion (#73)

**ID:** plan-024-james-dixson-76cee9
**Author:** james-dixson
**Created:** 2026-07-07
**Status:** complete
**Epic:** yf-mol-133
**Fingerprint:** f9952a051d11f51c8036056130913e50a98b0644262c2d269399050256f20507
**Phase log:**
- 2026-07-07 scoping: initial scope captured
- 2026-07-07 scoping: operator decisions locked (new status value; script-gated ready-check; reusable close-cascade helper)
- 2026-07-07 drafting: plan v1 presented
- 2026-07-07 review: plan v1 presented
- 2026-07-07 review: red-team pass 2 — APPROVE
- 2026-07-07 approved: operator approved
- 2026-07-07 intake: epic yf-mol-133 poured
- 2026-07-07 executing: start gate resolved
- 2026-07-07 reconciling: execution complete — post-execution reconciliation
- 2026-07-07 complete: plan complete — cascade-close clean (epics + molecule), upstream reconciled

## Objective

Harden two edges of the yf-plan lifecycle where the phase machine currently under-enforces its
own gates:

1. **#69 — ready-for-approval gate.** Do not solicit operator approval until a plan is genuinely
   *ready*: the adversarial red-team last returned APPROVE (re-run after any major-concern
   revision — a REVISE'd-but-unre-reviewed plan is not ready), **and** the portability audit
   passes. Introduce `ready-for-approval` as a first-class status distinct from `approved`, gated
   by a script-enforced `ready-check` verb.
2. **#73 — cascade-close containers on completion.** On plan completion, close every container in
   the plan's tree — intermediate epics **and the top-level plan molecule** — whose children are
   all terminal (today only leaves and sometimes the top molecule close, leaving stale open epics
   that pollute `bd ready`). A container with any still-open child while the plan is marked complete
   must **fail loudly**. Ship the walk as a self-contained helper in `skills/yf-plan/scripts/`;
   extraction to a shared surface is **deferred** until a genuine second in-repo runtime consumer
   exists (rule-of-three).

## Motivation

Both defects were observed live and cost manual cleanup / risked approving unverified plans:

- **#69** (plan-022 session): approval was solicited (a) after a red-team **REVISE** whose
  revisions were never re-reviewed, and (b) **before** the portability audit passed (the audit
  later failed on unedited `context.md` template prose). Approval should mean "I consent to this
  *verified* plan," not "I consent, now go verify it." Soliciting approval on an unverified plan
  defeats the gates.
- **#73** (thesoftwarefactory plan-002 + plan-003): plans shipped to production with `Status:
  complete`, but 8 intermediate epic containers remained `open` under closed molecules — surfacing
  as 8 false-positive "ready" epics in `bd ready` long after the work shipped. The operator asking
  "what's on deck" gets stale containers, not real work. All 8 had to be closed by hand.

Affected: every yf-plan user. #69 affects the PLAN→INTAKE boundary of every plan; #73 affects the
COMPLETE step of every plan with intermediate epics.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|:--|:--|:--|:--|:--|
| [#69](https://github.com/dixson3/yoshiko-flow/issues/69) | enforce a ready-for-approval gate | include | Epic 1 | Epic 1 |
| [#73](https://github.com/dixson3/yoshiko-flow/issues/73) | cascade-close epic/child beads on plan completion | include | Epic 2 | Epic 2 |

Coarse upstream tracking (AGENTS.md): ONE tracking issue filed per plan-scale effort at INTAKE.
These two are the plan's scope; the plan's own tracking issue links both.

## Investigation Findings

Probed `bd` capabilities in this repo (bd ≥ 1.1.0, already required) — no sub-agent experiments
needed; the primitives exist:

- **`bd mol stale [--json]`** — detects molecules (epics with children) that are complete but
  still open: `all children closed (Completed == Total)` AND `root open`. This is the exact
  "close if all children closed" **detector**, but it reports **globally** (all molecules), not
  scoped to one plan's subtree. The helper must scope detection to the plan's epic subtree.
- **`bd children <id> --json`** — lists all children of a parent **including closed** (alias for
  `bd list --parent <id> --status all`). This is the walk primitive: recurse from the plan epic to
  enumerate the container tree bottom-up.
- **`bd close <id> -r <reason>`** — closes; `-f/--force` is required to close a container with an
  **unsatisfied gate** child. In a genuinely-complete plan all gates are resolved, so the normal
  path needs no `--force`; an unsatisfied-gate container is part of the **fail-loud** signal.
- **`update_status`** (plan_manager.py L819) is **free-form** — it writes any status string with no
  enum validation. So adding `ready-for-approval` needs **no enum change in the writer**; the work
  is doctrine (SPEC/SKILL.md vocabulary) + the consumers that key on specific values
  (`list` filters, `resume-scan` execute-eligibility on `approved`).
- **`_shared/`** is the repo's canonical shared-helper surface, vendored into consumers by
  `_shared/sync.py` (whole-file copy, e.g. `manifest_update.py`; marker-region copy, e.g.
  `json_extract.py`). It was **considered and deferred** as the close-cascade helper's home:
  rule-of-three is unmet — the only in-repo runtime consumer today is yf-plan (yf-beads-authoring
  is a conventions skill with no `scripts/` dir; a future land-the-plane sweep would live in the
  same yf-plan `scripts/`). The helper therefore lands in `skills/yf-plan/scripts/`; extraction to
  `_shared/` is revisited when a genuine second runtime consumer appears.

## Approach

Two **independent** epics (no cross-dependency), each **SPEC-first** per AGENTS.md: the `REQ-*`
edit lands ahead of the code+test in the same epic.

**Epic 1 (#69)** introduces `ready-for-approval` into the status vocabulary (REQ-PLAN-001), adds a
script-gated `ready-check` verb that verifies both preconditions, and re-sequences Phase 3 so the
audit + a clean re-run red-team are **preconditions of the approval prompt** (REQ-PLAN-030/033),
with approval transitioning `ready-for-approval → approved`.

**Epic 2 (#73)** authors a self-contained close-cascade helper in `skills/yf-plan/scripts/`
(`close_cascade.py`) and wires it into yf-plan §6.4 completion. A new REQ codifies the
close-if-all-children-terminal + fail-loud-on-open-children contract, defines the close set to
include the **top-level plan molecule** (not just intermediate epics), and defines "terminal"
consistently with `resume-scan`'s gate accounting (a **resolved/verified gate is terminal**, even
if not `status: closed`, so a resolved gate never triggers a false fail-loud). `_shared/` extraction
is **not** done now — no second in-repo runtime consumer exists (yf-beads-authoring is a
conventions skill with no `scripts/` dir; a future land-the-plane sweep would live in the same
yf-plan `scripts/`). Issue 2.5 leaves only a **doctrine cross-reference** in yf-beads-authoring, not
a code consumer.

Both epics update SKILL.md doctrine and add tagged tests. The change-validation FULL tier
(`test_worktree.py` + the new `close_cascade` test) is the merged-state gate; there is no `_shared/`
vendoring row for this helper, so the Epic-1 `DRIFT-CHECK.md` `e-status-values` edge is the key
status-vocabulary backstop.

## Epics

### Epic 1: #69 — ready-for-approval gate

- Issue 1.1: **SPEC-first.** Amend `skills/yf-plan/SPEC.md`: add `ready-for-approval` to the
  REQ-PLAN-001 status vocabulary (between `review` and `approved`); revise REQ-PLAN-030 to require
  the red-team be **re-run after any major-concern revision** and that a REVISE verdict blocks
  ready-for-approval until a later cycle returns APPROVE; revise REQ-PLAN-033 so the portability
  audit is a **precondition of the approval prompt**, not a post-approval step; add a new
  `REQ-PLAN-066` defining the `ready-check` verb (both preconditions green → `ready`) and the
  `ready-for-approval → approved` transition as the operator's single act of consent, noting
  ready-check and the approval transition are **adjacent** (ready-check re-runs at approval so no
  content edit slips between a green check and the fingerprint write — M3). In `spec/phases.md`,
  amend **REQ-STATUS-001** — bump the hard count **8 → 9** and add `ready-for-approval` to its
  enumerated list (C2) — and update the phase machine. Update `spec/portability.md`
  (review-lifecycle): each red-team re-run still writes exactly one `pass-N.md` + one phase-log
  `review:` line, so the REQ-PLAN-031 `count(pass-*.md) == count(review: lines)` invariant holds
  across the re-run loop (M2).
  - resolves-upstream: #69 (include)
- Issue 1.2: Implement the `ready-check` verb in `plan_manager.py`: reads the latest
  `reviews/pass-N.md` verdict (must be APPROVE) and runs the portability audit (must be `pass`);
  returns `{ready, reasons:[...]}` JSON and exits 3 when not ready (mirrors the audit gate).
  - depends-on: 1.1
- Issue 1.3: Thread `ready-for-approval` through the status consumers. The real
  execute-eligibility surface is **SKILL.md §5.1** (the doctrinal `status: approved` + fresh
  fingerprint filter) — the script keys resume/execute on the **fingerprint** (`stale_approved`),
  not a `status == "approved"` literal (C3). Audit: SKILL.md §5.1 filter (must still require
  `approved`, so `ready-for-approval` is **not** execute-eligible), `list` output, and the SKILL.md
  status-vocabulary line (see 1.4). Document the new value for `update-status` (free-form writer).
  - depends-on: 1.1
- Issue 1.4: Update SKILL.md: Phase 3 (PLAN) / Phase 4 (INTAKE) — red-team re-run loop,
  `ready-check` before the approval prompt, `review → ready-for-approval → approved` sequence
  (approval is consent on an already-verified plan) — **and** the general **status-vocabulary line**
  (the `Status values: …` Phase Model line), which is the declared source of truth for the
  `DRIFT-CHECK.md` `e-status-values` edge (C2). Note `e-status-values` as the drift backstop.
  - depends-on: 1.2, 1.3
- Issue 1.5: Tests (`test_worktree.py`): `ready-check` returns not-ready on last-verdict-REVISE;
  not-ready on audit-fail; ready when both green; exit-code contract. Tag against REQ-PLAN-066.
  - depends-on: 1.2

### Epic 2: #73 — close-cascade on completion (yf-plan-local helper)

- Issue 2.1: **SPEC-first.** Add `REQ-PLAN-067` to `skills/yf-plan/SPEC.md`: on COMPLETE, yf-plan
  shall close every container in the plan's tree — intermediate epics **and the top-level plan
  molecule** (U1) — whose children are **all terminal**, bottom-up, with a close reason referencing
  the plan; a container with **any still-open child** while the plan is marked complete is a **hard
  failure** (surface loudly), never a silent close or silent leave. Define **"terminal"**
  consistently with `resume-scan`'s gate accounting: a **resolved/verified gate is terminal** even
  when not `status: closed`, so a resolved gate never triggers a false fail-loud (C4). Note the
  helper home is `skills/yf-plan/scripts/`, with `_shared/` extraction deferred until a real second
  runtime consumer exists. Cross-reference REQ-PLAN-063 (the existing reconcile/close step).
  - resolves-upstream: #73 (include)
- Issue 2.2: Author the helper `skills/yf-plan/scripts/close_cascade.py`: given the plan's root
  epic/molecule id, walk `bd children --json` bottom-up; close every container whose children are
  all **terminal** (closed, or a resolved/verified gate — C4), reason references the plan; return a
  structured report `{closed:[...], blocked:[{id, open_children:[...]}]}`; a non-empty `blocked` set
  is the fail-loud signal. Uses only `bd children`/`bd close` (+ `bd mol stale` as a cross-check).
  The close set includes the top-level plan molecule (U1).
  - depends-on: 2.1
- Issue 2.3: Wire the helper into yf-plan §6.4 completion (before/with the `bd close ${EPIC}` +
  `update-status complete`): run the cascade over the plan tree; on a non-empty `blocked` set,
  **halt** completion with a loud error (do **not** set `complete`); on clean, close containers +
  set `complete`. Update SKILL.md §6.4 doctrine.
  - depends-on: 2.2
- Issue 2.4: Tests (`test_worktree.py`, or a sibling `test_close_cascade.py`): helper closes
  all-terminal containers bottom-up including the plan molecule (U1); leaves an open-child container
  and reports it in `blocked`; a container whose only non-closed child is a **resolved gate** is
  **not** blocked (C4); yf-plan §6.4 halts on a blocked set. Tag against REQ-PLAN-067.
  - depends-on: 2.2, 2.3
- Issue 2.5: Add a **doctrine cross-reference** (prose only) in the yf-beads-authoring
  completion-handoff section (its SKILL.md / `spec/`), pointing at the yf-plan close-cascade helper
  as the pattern a coordinator's completion handoff should follow. **Not** a code consumer and
  **not** a vendored dependency — a documentation pointer (C1, M1).
  - depends-on: 2.2

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: bd ≥ 1.1.0 with `mol stale` / `children --json`
- Type: auto
- Condition: `bd mol stale --json` and `bd children <id> --json` are available (bd ≥ 1.1.0)
- Test: `bd version` and `bd mol stale --help` exit 0
- Blocks: 2.2
- Instructions: already required by the repo (yf-research/plan need bd ≥ 1.1.0); this gate just
  asserts it before authoring the helper.

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step
- Note: #69 and #73 are both `include` — reconcile updates them at land.

## Risks & Mitigations

- **New status value ripples** (`ready-for-approval` missed by a consumer that enumerates statuses)
  → Issue 1.1 amends the two hard source-of-truth points (`spec/phases.md` REQ-STATUS-001 count+list,
  `SPEC.md` REQ-PLAN-001) and Issue 1.4 the SKILL.md vocabulary line; the `DRIFT-CHECK.md`
  `e-status-values` edge is the automated backstop; tests assert `ready-for-approval` is not
  execute-eligible.
- **Cascade-close over-closes a real "incomplete plan" signal** → the fail-loud invariant
  (REQ-PLAN-067) is the guard: only all-terminal containers close; any open child halts and
  surfaces. A **resolved-but-not-closed gate is terminal** (C4), so a resolved gate does not cause a
  false fail-loud. Tested in 2.4.
- **`bd close` on an unsatisfied-gate container needs --force** → the helper does NOT force; an
  *unsatisfied* gate is part of the blocked/fail-loud signal, not an auto-force (distinct from a
  *resolved* gate, which is terminal).
- **Self-referential dogfooding**: this very plan (plan-024) completing will exercise the new
  cascade-close on its own epics + molecule — a live end-to-end check at RECONCILE.

## Success Criteria

- **#69:** yf-plan does not present the approval prompt until `ready-check` is green (last red-team
  APPROVE after any revision + audit pass). A plan whose last red-team verdict is REVISE, or whose
  audit fails, is blocked from approval. Approval transitions `ready-for-approval → approved`.
  SPEC/SKILL.md/`spec/portability.md` codify the state and preconditions (SPEC-first). `ready-check`
  has passing tests.
- **#73:** Completing a plan whose leaves are all done leaves **0 stale open epics/molecules** for
  that plan (including the top-level plan molecule); `bd ready` after completion shows no container
  beads from the completed plan. A plan marked complete with genuinely-open children produces a
  **visible failure**, not a silent close; a resolved-but-not-closed gate does not cause a false
  failure. The close-cascade helper lives in `skills/yf-plan/scripts/close_cascade.py` and is
  consumed by yf-plan §6.4; yf-beads-authoring carries a doctrine cross-reference only. Tagged tests
  pass.
- Change-validation FULL tier green over the merged tree.
