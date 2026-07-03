# Plan: yf-plan lifecycle rework — intake-at-execute branch model, auto-commit, content-bound re-review gate

**ID:** plan-021-james-dixson-bb3558
**Author:** james-dixson
**Created:** 2026-07-02
**Status:** executing
**Epic:** yf-mol-al2
**Phase log:**
- 2026-07-02 scoping: initial scope captured; #62 deferred, #47 full-model chosen
- 2026-07-02 investigating: 4 experiments (EXP-1..4) dispatched; #47 full-model + #63 + #64
- 2026-07-02 drafting: approach + 6 epics synthesized from exp-001/002
- 2026-07-02 review: pass-1 conformance INCOMPLETE (stub dup) + red-team REVISE → 2 high/3 med/1 low + 2 conf resolved in-place
- 2026-07-02 resolved: pass-1 concerns closed; audit pass
- 2026-07-02 revised: operator correction — repo-source≠installed; Epic 0 → scratch-project test harness; self-hosting risk corrected (triggers pass-2)
- 2026-07-02 review: pass-2 red-team REVISE → 1 high (resolver-shadow) + 1 med (promotion) + 1 low resolved in-place
- 2026-07-02 approved: operator approved (pass-2)
- 2026-07-02 intake: epic yf-mol-al2 poured
- 2026-07-02 executing: start gate resolved

## Objective
Rework the yf-plan lifecycle for a **predictable, worktree-default** git model with **intake deferred
to execute**, an **auto-commit-at-plan** clean-handoff boundary, and a **content-bound re-review gate**
that invalidates a stale approval. Resolves #47 (full model), #63, #64. (#62 yf-spec is deferred to a
separate plan — see Out of scope.)

## Motivation
yf-plan's branch/worktree handling is inconsistent and its approval is a sticky status rather than a
statement about reviewed content. Three concrete pains, observed live:

- **Unpredictable topology (#47).** The same protocol produces at least three different branch shapes
  depending on the working-copy state at planning time — including a "branch-of-a-branch-of-`main`"
  that forces an error-prone double merge/push to land. `worktree ensure` cuts from whatever HEAD
  happens to be (possibly a prior plan's branch), and intake timing varies (sometimes during planning,
  sometimes at execute). Plan artifacts and plan code end up split across two branches and two address
  spaces.
- **Dirty handoff (#63).** Intake leaves the plan folder + sibling edits (e.g. an `AGENTS.md` rule)
  uncommitted; a fresh execute session inherits a dirty base, muddying the worktree start point and the
  §5.2 dirty-state detection. The operator must remember to commit. Intake artifacts that live only in
  an uncommitted tree are lost on a crash or fresh clone — defeating cold-resume portability.
- **Sticky approval (#64).** An already-approved, already-intaken plan (plan-019) took a post-approval
  scope addition with nothing forcing a re-review; a real medium-severity defect was caught only because
  the operator manually said "run red-team again." Approval must bind to *reviewed content*, not survive
  arbitrary later edits.

These reshape each other: #47's **intake-at-execute** means a planning-phase edit has **no poured beads
to reconcile**, which makes both the #63 commit boundary and the #64 re-review gate materially cleaner.
So the three are planned together, with #47's model as the foundation.

## Scope

**In scope**
- **#47 (full model):** relocate the `bd mol pour` from end-of-PLAN to start-of-EXECUTE; named
  per-phase branches (`<plan-id>-development`, feature `<plan-id>`, `<plan-id>-execute`); execute
  worktree pinned to a **known base** (`main` or feature `<plan-id>`), never "whatever HEAD was"; a
  project-config **landing-strategy** switch (`main` default vs `feature-branch`); restore the default
  checkout to a known branch between phases; the "Complete execution of `<plan-id>`" upstream tracking
  issue with dependency links.
- **#63:** always commit the plan after the portability check / at the intake→execute boundary
  (auto-commit **local only**, never auto-push; scoped staging; non-default-branch guard).
- **#64:** approval binds to a plan **content fingerprint**; a modified `review`/`approved` plan becomes
  **stale-approved** and cannot execute until a fresh conformance → red-team → portability cycle;
  `--force` override with logged reason.
- **SPEC-first:** land the yf-plan `spec/` requirement edits (new/revised `REQ-*` + amendment log)
  ahead of the `plan_manager.py` / `SKILL.md` / formula implementation.

**Out of scope**
- **#62 yf-spec skill — deferred to a separate plan** (operator decision). This plan does its own
  SPEC-first edits by hand against yf-plan's existing `spec/`, without the yf-spec tooling.
- Full-auto push (remains operator-authorized at land-the-plane, unchanged).
- The `--remove-remote` canonicalization-drift cleanup (#61, separate).

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|
| [#47](references/upstream-47.md) | Consistent, predictable branch/worktree model (no branch-of-a-branch, intake at execute) | include (full model) | Foundation — reshapes #63/#64 | Epic 1 (1.1/1.2), Epic 2, Epic 3 |
| [#63](references/upstream-63.md) | Always commit intake state before offering the plan for execution | include | Auto-commit local at plan→execute boundary | Epic 1 (1.3), Epic 4 |
| [#64](references/upstream-64.md) | Re-review gate — modifying a reviewed/approved plan must re-trigger review before re-approval | include | Content-fingerprint-bound approval | Epic 1 (1.4), Epic 5 |
| [#62](references/upstream-62.md) | Propose yf-spec skill; yf-plan SPEC-first integration | defer | Operator: separate plan. Stays open | — (future plan) |

## Investigation Findings

### Resolved — [exp-001 lifecycle](findings/exp-001-lifecycle-mechanics.md), [exp-002 fingerprint/spec/git-auth](findings/exp-002-fingerprint-spec-gitauth.md), [exp-003 two-copies/test-harness](findings/exp-003-two-copies-and-test-harness.md)

- **Repo source ≠ installed skill (test-fidelity finding).** This plan edits `skills/yf-plan/`; `/yf-plan`
  runs the installed `~/.claude/skills/yf-plan/` copy (skills are `rust-embed`-baked into the `yf`
  binary at build; deployed by `yf skills install`). Repo edits do **not** hot-swap the running skill,
  so plan-021 executes normally — but validating the change requires exercising the **modified repo
  copy** in a scratch project (Tier-1 `test_worktree.py` from the repo tree + Tier-2 rebuild/dev-link
  scratch smoke). Running the installed copy tests the *old* skill. This reshaped Epic 0 (from a
  self-hosting execution constraint into a real scratch-harness deliverable) and downgraded the
  self-hosting risk.

- **#47 root cause = one line + ambient topology.** `_worktree_ensure` (`plan_manager.py:1115`) cuts
  `git worktree add -b <branch>` from **ambient HEAD** (no start-point). The script contains **no
  git checkout/merge/pull** — all topology is SKILL.md main-session bash, and the §6.1 merge target is
  likewise **ambient** (not hardcoded `main`). So #47 must pin **two** things: the worktree base and
  the merge target. Named branches today collide on a single bare `plan_id` in 3 places.
- **Pour relocation needs no new verbs.** Moving the pour from SKILL §4.2–4.6 to Phase 5 execute-start
  reuses `record-epic`/`resume-scan`/`metadata.plan_dir` verbatim (only timing changes) and **collapses
  the two pour-once guards** (§4.2 duplicate-pour + §5.2 resume `found`) into one "epic absent → pour;
  present → resume" branch. Linkage must be written atomically right after the pour.
- **#64 fingerprint = hash content sections, exclude bookkeeping.** Review mutates the phase log,
  `**Status:**`, `**Epic:**`, `reviews/`, and Operator Resolutions — all excluded. Hash the normalized
  `##` bodies `Objective`→`Success Criteria`; store as a `**Fingerprint:**` header field (like
  `record-epic` inserts `**Epic:**`); detect at command time via `resume-scan` (hard gate) + `list`/
  `status` (advisory). No on-edit hook exists for yf-plan.
- **#63 local-commit is consistent but needs a SPEC carve-out.** Conservative authority is scoped to the
  **remote**; Phase 6 already auto-commits locally. But `GR-PLAN-003` lists auto-commit as drift → amend
  it. "Never commit to `main`" is **unwritten** and there is **no branch guard in code** → codify both.
  Auto-commit scope = `${plan_dir}` + `.beads/` only, explicit pathspec, never `git add -A`.
- **SPEC surface.** `SPEC.md` = `REQ-PLAN-*` numbered contract; topical `spec/phases.md`
  (REQ-PHASE/SESSION/RESUME), `spec/portability.md` (REQ-PORT). The **living-amendment log lives only in
  the repo-root macro `SPEC.md`**. No REQ→test coverage gate exists for `REQ-PLAN-*`/`REQ-PORT-*` (only
  `REQ-YF-*` in `yf/src/coverage.rs`) — add `Verification:` lines + tagged tests, gap documented.

## Approach

**Sequenced, SPEC-first, with #47's intake-at-execute as the foundation.** The new lifecycle:

```
PLAN (in <plan-id>-development worktree):
   scope → investigate → draft → review → portability
   → APPROVE: write **Fingerprint:** over content sections    [#64]
   → AUTO-COMMIT the plan (local, no push)                    [#63]
   → land: push feature <plan-id>  OR  merge to main          [#47 landing-strategy]
   → create "Complete execution of <plan-id>" tracking issue  [#47]
   (NO pour here — the Fingerprint IS the execution-eligibility token)
EXECUTE (in <plan-id>-execute worktree, pinned base):
   stale-approved gate (refuse if Fingerprint drifted)        [#64]
   → POUR the molecule (relocated) → implement → gates        [#47 intake-at-execute]
   → merge-back to pinned target → validate → authorized push
```

Design decisions from investigation:
- **Pin both ambient deps.** `_worktree_ensure` gains a base start-point; SKILL §6.1 pins the merge
  target. A new `_resolve_landing_strategy()` (`main` default | `feature-branch`) drives both.
- **Named branches.** `<plan-id>-development` (planning), feature `<plan-id>` (landed plan),
  `<plan-id>-execute` (execution) — replacing the single bare `plan_id`. Teardown re-pointed per branch.
- **Relocate the pour** (SKILL §4.2–4.6 → execute-start) and **unify** the duplicate-pour + resume
  guards into one gate; write `record-epic` linkage atomically post-pour.
- **Auto-commit** via a testable `plan_manager.py commit-plan` verb: branch guard (refuse on
  default branch), scoped `git add -- "${plan_dir}" .beads/`, local commit, never push.
- **Fingerprint** via `_plan_content_fingerprint()` + a `**Fingerprint:**` field; `resume-scan`
  surfaces `stale_approved`; `/yf-plan execute` refuses a stale plan (or `--force` with logged reason).
- **SPEC-first:** all `REQ-*` edits (+ macro-SPEC amendment-log line) land before the code.

**Validation (the modified skill is not the running one).** Because `/yf-plan` runs the installed,
`rust-embed`-baked copy — decoupled from the repo `skills/yf-plan/` this plan edits — the change is
validated in two tiers against a **scratch project** (Epic 0): Tier-1 `test_worktree.py` run from the
repo tree (mechanical `plan_manager.py` behavior), and Tier-2 a scratch bootstrap (rebuild +
`yf skills install --target` **or** a dev-link of the repo skill) driving a full plan→execute→land
smoke. The installed skill is **promoted only after** the scratch smoke passes.

## Epics

### Epic 0: Scratch-project test harness (validates the MODIFIED repo skill)
This plan edits the **repo source** `skills/yf-plan/`, which is **decoupled** from the installed skill
that `/yf-plan` runs (`~/.claude/skills/yf-plan/`; skills are `rust-embed`-baked into the `yf` binary
at build and deployed by `yf skills install`). So (a) repo edits do **not** hot-swap the running skill
mid-execution — the plan-019-style hazard evaporates — but (b) validating the change requires
exercising the **modified repo copy** in a scratch project; running the installed copy tests the *old*
skill (false green). See [exp-003](findings/exp-003-two-copies-and-test-harness.md).
- Issue 0.1: **Tier-2 scratch bootstrap with resolver isolation (RT2-1).** The `SKILL_DIR` resolver
  searches `~/.claude/skills` **first** with `head -1`, so a scratch `<scratch>/.claude/skills/yf-plan`
  is **shadowed** by the operator's existing installed copy and the smoke would silently run the *old*
  skill. The bootstrap MUST therefore isolate the resolver — the primary route is a **sandboxed
  `HOME`**: `HOME=<scratch-home> cargo build` (re-embeds `../skills`) then `HOME=<scratch-home> yf
  skills install` (lands the modified skill at `<scratch-home>/.claude/skills/yf-plan`), and drive the
  smoke with that `HOME` so the resolver's first hit **is** the modified copy. (Alternatives: shadow-
  aside the user install for the run, or drive 0.2 by explicit path to the scratch skill — weaker, it
  bypasses the resolver.) Correct the exp-003 route claims to reflect the shadowing.
- Issue 0.2: **End-to-end smoke driver.** A scripted (or checklist) run that drives a trivial throwaway
  plan through the new lifecycle in the scratch project — plan (in `<id>-development`) → auto-commit →
  fingerprint → execute (pour at `<id>-execute`, pinned base) → land — and **records the observed
  branch topology** as the acceptance artifact. This is what the capability gate consumes.
  - depends-on: 0.1
- Issue 0.3: **Promotion boundary + sequenced land step (RT2-2).** Document that plan-021's own
  execution runs normally (repo edits are inert w.r.t. the running installed skill) with **one rule: do
  not `yf skills install` (promote) until the scratch smoke passes.** Promotion is **in scope** and
  explicitly sequenced as the **final land action** (Epic 6.3 / reconcile): after the scratch smoke
  passes and the branch merges, `cargo build` (rust-embed re-embeds `../skills`) → `yf skills install`
  to promote the modified skill into the operator's `~/.claude/skills/`. Until that rebuild+promote, the
  rework has **zero effect** on the live environment — so the step is not orphaned. Tier-1
  (`test_worktree.py` from the repo tree, Epic 6.1) is the fast per-epic guard.

### Epic 1: SPEC-first amendments (lands before all code)
- Issue 1.1: `spec/phases.md` — intake-at-execute: revise REQ-PHASE-002 (start gate / pour now at
  execute, not intake) and REQ-RESUME-001 (`found=false` now means not-yet-poured); add REQ for the
  unified pour-once/resume gate. Mirror a `REQ-PLAN-05x` in `SPEC.md §2.6 Execute`.
  - resolves-upstream: #47 (include)
- Issue 1.2: `spec/phases.md` / `SPEC.md` — branch model: base-pinning, named per-phase branches, and
  the `landing-strategy` config switch as testable REQs.
  - resolves-upstream: #47 (include)
  - depends-on: 1.1
- Issue 1.3: `SPEC.md §2.7` — auto-commit-at-plan: new `REQ-PLAN-06x` + a **GR-PLAN-003 carve-out**
  (local commit permitted at plan boundary; push stays authorized-only) + the never-commit-to-default
  branch-guard requirement.
  - resolves-upstream: #63 (include)
- Issue 1.4: `spec/portability.md` + `SPEC.md §2.4` — content-fingerprint re-review gate: `REQ-PORT-04x`
  (fingerprint surface **with the explicit self-trigger exclusion set** — header fields, phase-log,
  `reviews/`, Operator Resolutions, **and `## Upstream Issues`** (RT-C2); stale-approved semantics) +
  mirror `REQ-PLAN-03x`. Add the repo-root macro-`SPEC.md` living-amendment-log entry for plan-021.
  - resolves-upstream: #64 (include)

### Epic 2: Branch/worktree model (#47 core) — `plan_manager.py` + SKILL
- Issue 2.1: `_resolve_landing_strategy()` config resolver (`landing-strategy`: main|feature-branch,
  default main), parallel to `_resolve_validate_cmd`.
  - depends-on: 1.2
- Issue 2.2: Pin the worktree base in `_worktree_ensure` (`git worktree add -b <branch> <base>`, base
  from strategy) — the core #47 fix.
  - depends-on: 2.1
- Issue 2.3: Named-branch scheme (`<plan-id>-development` / feature `<plan-id>` / `<plan-id>-execute`)
  across `_worktree_path` / `_plan_id_from_dir` / `_worktree_teardown`; re-point teardown's unmerged
  guard per branch. **Acceptance (RT-missing):** under `feature-branch` strategy teardown deletes only
  `<plan-id>-execute` and **preserves** feature `<plan-id>`; under `main` strategy it deletes
  `<plan-id>-execute` after merge — teardown must not delete the still-needed feature branch.
  - depends-on: 2.2
- Issue 2.4: SKILL Phase 1/5/6 prose — planning worktree, pinned execute base, **pinned merge target**
  per strategy, restore-default-checkout-between-phases, the two landing options, and the "Complete
  execution of `<plan-id>`" tracking-issue creation with dependency links.
  - depends-on: 2.3

### Epic 3: Intake-at-execute relocation (#47) — SKILL + guards
- Issue 3.1: Move SKILL §4.2–4.6 (pour + bead creation + linkage) to Phase 5 execute-start; keep §4.1
  status / §4.7 wisp-burn / §4.8 handoff on the plan side; rewrite the handoff to reflect no-pour-at-
  intake and the new landing options.
  - depends-on: 1.1, 2.4
- Issue 3.2: Unify the §4.2 duplicate-pour guard with the §5.2 `resume-scan` `found` check into one
  "epic absent → pour; present → resume" gate; ensure `record-epic` linkage is written atomically
  immediately after the relocated pour.
  - depends-on: 3.1

### Epic 4: Auto-commit at plan (#63)
- Issue 4.1: `plan_manager.py commit-plan` verb — current-branch detection + default-branch guard,
  scoped `git add -- "${plan_dir}" .beads/`, local commit (message `plan-NNN: <phase> — <objective>`),
  never push; JSON verdict. **Default-branch resolution (RT-C4):** `git symbolic-ref --short
  refs/remotes/origin/HEAD` → fallback `git config init.defaultBranch` → fallback `main`/`master`;
  a **detached HEAD or empty current-branch name is fail-closed = refuse** (never commit). Guard is
  specified as a testable REQ in Issue 1.3.
  - depends-on: 1.3, 2.1
- Issue 4.2: Wire `commit-plan` into the SKILL after the portability check / at the plan→execute
  landing boundary (per the Epic 2/3 model); decouple from the bd/Dolt side. The `**Fingerprint:**`
  write (5.1) happens **before** this commit so a landed/pushed plan always carries its fingerprint
  (RT-C3) — hence the 5.1 edge.
  - depends-on: 4.1, 3.1, 5.1

### Epic 5: Content-fingerprint re-review gate (#64)
- Issue 5.1: `_plan_content_fingerprint()` (normalized hash of the content sections, excluding
  header fields / phase-log / `reviews/` / Operator-Resolutions **and the `## Upstream Issues` table** —
  its "Resolved By" cells are filled at the relocated pour and would else flip the hash mid-execution,
  RT-C2) + write a `**Fingerprint:**` field at APPROVE (clone the `record-epic` insertion mechanism;
  the field is a `**Field:**` line, so it is self-excluded). The hashed span is the content sections
  minus `## Upstream Issues`: Objective, Motivation, Scope, Investigation Findings, Approach, Epics,
  Gates, Risks, Success Criteria.
  - depends-on: 1.4
- Issue 5.2: Surface `stale_approved` from `resume-scan` (execute hard-gate) + advisory in `list`/
  `status`; wire `/yf-plan execute` to refuse a stale plan and route back through conformance →
  red-team → portability; `--force` override logs a phase-log line.
  - depends-on: 5.1, 3.2

### Epic 6: Tests, diagram & docs
- Issue 6.1: `test_worktree.py` — assert worktree **base == configured base** (not HEAD); named-branch
  + landing-strategy-switch tests; tag REQ ids.
  - depends-on: 2.3, 2.4
- Issue 6.2: Fingerprint tests — self-trigger avoidance (a review/phase-log write **and** filling the
  `## Upstream Issues` "Resolved By" column at pour do **not** flip the fingerprint, RT-C2),
  stale-approved detection, default-branch fail-closed guard (RT-C4), `--force` path.
  - depends-on: 5.2
- Issue 6.3: Update `spec/worktree-execute-lifecycle.d2` + `.png` for the new topology; update
  **`README.md`** (the §Execute/§Reconcile paragraphs that hardcode the old bare-`<plan-id>` branch +
  intake-at-pour model, RT-C5); refresh `protocols/PLANS.md` if the trigger contract changed (+
  re-stamp `manifest.json`); CHANGELOG entry. **Final land action (RT2-2): after the capability-gate
  scratch smoke passes and the branch merges, `cargo build` → `yf skills install` to promote the
  modified skill.**
  - depends-on: 2.4, 3.2, 4.2, 5.2, 0.2

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: scratch-project dogfood (recommended)
- Type: human
- Condition: the reworked lifecycle — loaded from the **modified repo skill** (not the installed
  copy) via Epic 0's harness — can plan-and-execute a trivial throwaway plan end-to-end in a scratch
  project without the branch-of-a-branch topology or a manual commit step.
- Test: `uv run skills/yf-plan/scripts/test_worktree.py` green (Tier 1, from the repo tree) **and**
  Epic 0.2's end-to-end scratch smoke passing with the recorded topology showing pinned bases + named
  branches.
- Blocks: **Epic 3 close** (the topology-critical relocation) and Epic 6 close / reconcile.
- Instructions: run the full pytest suite (repo tree) and the Epic-0 scratch smoke (under the isolated
  `HOME`, Issue 0.1); record the branch topology observed. Interim guard while Epics 3–5 land: the
  per-epic `test_worktree.py` additions (Issue 6.1) — **Tier-1 cannot catch SKILL.md orchestration
  regressions** (pour relocation, handoff/merge-target prose), which are **Tier-2-only** (RT2-3), so a
  **working** Tier-2 harness (Epic 0.1/0.2) must exist before Epic 3 close, not just at land.

### Reconcile Gate (upstream #47/#63/#64 incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
- **Test fidelity, not hot-swap (medium — corrected from the initial high framing).** The repo source
  `skills/yf-plan/` and the installed skill `/yf-plan` runs are **decoupled** (rust-embed baked into
  the `yf` binary at build; deployed by `yf skills install`) — so repo edits do **not** change the
  running protocol under plan-021's own feet, and plan-021 executes normally (no pinned-snapshot /
  worktree-off gymnastics). The real risk is validating against the installed **old** skill and getting
  a false green. Mitigation: **Epic 0** provides the scratch-project harness that exercises the
  *modified* repo skill (Tier-1 `test_worktree.py` from the repo tree + a Tier-2 rebuild/dev-link
  scratch smoke); the capability gate consumes it; **do not `yf skills install` (promote) until the
  scratch smoke passes.** See [exp-003](findings/exp-003-two-copies-and-test-harness.md).
- **Pour-once guard collapse (high).** Merging the duplicate-pour + resume guards wrong reintroduces
  double-epic (failure #2) or a no-bead run. Mitigation: atomic `record-epic` post-pour; explicit test
  of "second `/yf-plan execute` does not pour twice"; the unified gate is a single audited code path.
- **Ambient→pinned regression (medium).** Pinning base but not merge target (or vice-versa) half-closes
  #47. Mitigation: Epic 2 pins both; Issue 6.1 asserts the base; SKILL §6.1 review covers the target.
- **GR-PLAN-003 literal conflict (medium).** Auto-commit reads as a guardrail violation until the
  carve-out lands. Mitigation: SPEC-first Issue 1.3 amends GR-PLAN-003 before Epic 4 code.
- **No REQ→test gate for REQ-PLAN/PORT (low).** New requirements won't be CI-enforced. Mitigation:
  `Verification:` lines + tagged tests in `test_worktree.py`; documented gap (a yf-crate-style gate for
  Python skills is out of scope / future).
- **Large plan (medium).** Six epics across two axes. Mitigation: strict SPEC-first DAG; epics are
  independently landable; execution can pace across sessions (the reworked model itself helps).

## Success Criteria
- **#47:** planning runs in a `<plan-id>-development` worktree; execute runs in a `<plan-id>-execute`
  worktree **pinned to a known base** (`main` or feature `<plan-id>`), never ambient HEAD; the merge
  target is pinned; no branch-of-a-branch topology is producible; a `landing-strategy` config selects
  `main` (default) vs `feature-branch`; a "Complete execution of `<plan-id>`" tracking issue is created.
- **Intake-at-execute:** no molecule is poured during PLAN; the pour happens at execute-start; a second
  `/yf-plan execute` never pours a second epic; the linkage is crash-safe.
- **#63:** the plan is auto-committed (local, no push) at the plan→execute boundary, scoped to
  `${plan_dir}` + `.beads/`, refusing the default branch; the push stays operator-authorized.
- **#64:** approval writes a `**Fingerprint:**`; editing a `review`/`approved` plan's content sections
  marks it stale-approved; `/yf-plan execute` refuses a stale plan until a fresh review cycle (or
  `--force` with a logged reason); a review/phase-log write alone does **not** flip the fingerprint.
- **SPEC-first:** all `REQ-*` edits + the macro-SPEC amendment-log entry land before the code; new
  testable REQs carry `Verification:` lines and tagged tests.
- `test_worktree.py` passes incl. the new base-pinning, named-branch, strategy, and fingerprint tests.
- **Validation against the modified repo skill:** the Epic-0 scratch harness drives a throwaway plan
  end-to-end (plan→auto-commit→execute→land) using the *modified* `skills/yf-plan/` (via rebuild +
  `yf skills install --target` or dev-link), recording a topology with pinned bases + named branches;
  the installed skill is promoted (`yf skills install`) only after that smoke passes.
- #47/#63/#64 reconciled; #62 remains open for its own plan.
