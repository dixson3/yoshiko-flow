---
type: Plan
okf_spec: OKF-PLAN
description: 'Regenerate user-facing website/docs (#317): unbreak the pelican build,
  repair Class-A content defects at every site, and close the Class-B harvest/generation-pipeline
  defects'
id: plan-066-james-dixson-e7fadb
author: james-dixson
created: '2026-09-05'
status: drafting
---
# Plan: Regenerate user-facing website/docs (#317): unbreak the pelican build, repair Class-A content defects at every site, and close the Class-B harvest/generation-pipeline defects

**ID:** plan-066-james-dixson-e7fadb
**Author:** james-dixson
**Created:** 2026-09-05
**Status:** drafting

## Objective
Regenerate user-facing website/docs (#317): unbreak the pelican build, repair Class-A content defects at every site, and close the Class-B harvest/generation-pipeline defects

## Motivation

**The site does not build, and has not since plan-057.** Reproduced on this branch,
2026-09-05, against `main` at `77eb7fe`:

```
CRITICAL RuntimeError: skill_pages: no authored web/content/skills/<name>.md
for: yf-okf-hygiene. Every skill needs an authored page (add one under web/content/skills/).
```

`web/plugins/skill_pages.py` is fail-closed: it enumerates skills from frontmatter and raises
if any lacks an authored page. So this is not a gap in a published site — **it halts the
build**, and every claim about "what the site renders" is unfounded because it renders nothing.
`.github/workflows/web-deploy.yml` chains off a successful Release, so a release cut today
would carry the failure to the deploy step.

Two failure classes have been conflated, and separating them is the point of this plan:

- **Class A — content defects.** Docs contradict the code. Repaired by editing.
- **Class B — process defects.** The harvest/generation pipeline cannot see, or cannot carry,
  the facts it publishes. Repaired *only* by changing the pipeline.

Every Class-A fix is a one-time patch that silently re-drifts until the matching Class-B defect
is closed — which is why this plan closes Class B **first** and lets the new coverage find and
then verify the Class-A repairs.

`web/content/` was last touched 2026-08-26 (plan-054, *"make the website true"*). **Eight**
plans have landed since, so #317's Class-A table is a stale snapshot in one direction only: it
cannot know about drift introduced after it was written.

This is **Plan 3 of 3**. Siblings #315 (README layout contract, closed 2026-09-02) and #316
(OKF corpus backfill, closed 2026-09-06 by plan-065) are both complete, so the sequencing
precondition #317 declares is satisfied.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| #317 | Plan 3/3: regenerate user-facing docs (the site does not currently BUILD) | include | The plan of record. Both its declared predecessors (#315, #316) are closed. | _TBD_ |
| #104 | web: prevent runaway Pelican devservers + add clean teardown | include | Folded per D3 — this plan runs `pelican` repeatedly and #317 flags it as likely to bite. | _TBD_ |
| #127 | web/concepts: define idiomatic workflow terms | include | Folded per D3. #317 records it as excluded originally but "may fold here". | _TBD_ |
| #363 | OKF-EXTENSION.md documentation remediation | include | Folded per D3 — same content-defect class, `docs/` surface. | _TBD_ |
| #322 | docs yf-okf-hygiene SKILL.md: the "31 legacy, 7 halt" figure | include | Folded per D3 — a skill-doc content defect the web skill page can inherit. | _TBD_ |
| #247 | Drift findings no declared edge covers | partial | This plan closes the four Class-B coverage gaps #317 enumerates, not all of #247's manifest gap. | _TBD_ |
| #263 | META: "two facts, one signal" | partial | The `optional`/`required` token defect (Class-B item 6) is an instance of this class. The META issue stays open. | _TBD_ |
| #273 | The command-vs-obligation law | exclude | Informs how checks are written; not itself in scope. | — |
| #312 | Process-audit stage: amend the poured DAG | exclude | Orthogonal — the enforcement half, on the yf-plan axis. | — |
| #365 | plan-065 execution tracking | exclude | A prior plan's tracker; unrelated to this work. | — |

## Scoping Decisions

| # | Decision | Rationale |
| :-- | :-- | :-- |
| D1 | **Re-derive the defect inventory mechanically.** Build runnable checkers, run them over the current tree to produce the inventory. #317's Class-A table is used as a **negative-control set**: every row it names must be found by a checker, or that checker is blind. | The table is eight plans stale and can only under-report. A hand-verified repair of a stale list would assert coverage the plan never had. The negative control is what distinguishes "the checkers found nothing" from "the checkers cannot see". |
| D2 | **Class B before Class A** (after the P0 build unbreak). Close the coverage gaps first, then let the new coverage find and verify the Class-A repairs. | #317's own argument. The inverse order lands coverage green by construction, which proves nothing about whether it would have caught the defects it was written for. |
| D3 | **Fold in #104, #127, #363, #322** alongside #317. | #104 (devserver teardown) will bite: this plan runs pelican repeatedly. #127 (concepts glossary) is content this regeneration would otherwise leave undone. #363 and #322 are the same content-defect class on the `docs/` and `skills/` surfaces. |
| D4 | **Acceptance is a local clean build plus green checkers.** No deploy. | Matches #317's stated acceptance and keeps this a `standard` plan with no outward-facing write. Exercising `web-deploy.yml` publishes to yoshikoflow.sh and would need its own consent gate. |
| D5 | **The plan authors no engine fix for defects it merely finds.** A pipeline defect outside the four Class-B items in scope is filed, not fixed. | Bounds a plan whose subject is drift detection and would otherwise absorb every defect the new checkers surface. |
| D6 | **Class B ships a MECHANICAL GATE plus the manifest fixes.** Runnable checkers for the decidable edges become `CHANGE-VALIDATION.md` recipe rows; genuinely-LLM edges stay on the prose trigger with an explicit `not_checked` declaration. | EXP-002 measured the engine at **4 firing opportunities, 0 catches** — a *dispatch* gap. Manifest edits cannot fix dispatch, so #317's remedy alone would produce more edges that also never run. Precedent: `check_skill_readme_contract.py` already does exactly this (plan-061 shipped the mechanical subset of the README edges as a checker gated in BOTH tiers, while `e-readme-desc` kept its LLM route and is DECLARED unchecked). **AMENDED after pass-1 C12 — the bet's boundary, stated:** CV's FULL tier IS mechanically enforced (`_validate_merged` returns fail/exit 3), a real difference from the prose-only trigger. But **CI runs no tier** (`grep change_validation .github/workflows/*` → nothing) and the FAST on-edit trigger is itself an always-loaded prose rule — the same class that produced 4-opportunities/0-catches. So the new coverage binds on the yf-plan land path only; a direct non-plan commit to `web/content/` still gets nothing. Issue 2.8 closes that residual with a CI job. |
| D7 | **Re-render ALL SIX diagrams under one pinned d2, in one commit**, with the version recorded in the message. | EXP-004: all six differ from a fresh render because of d2 **version drift**, not staleness. Repairing three would leave a visible layout/encoding split (RGBA/old-engine vs RGB/v0.8.2) across the set. |
| D8 | **Author the "missing coverage" items as EDITORIAL content**, verified against code rather than #317's phrasing. | EXP-002: these are pure omissions, which `DRIFT-CHECK.md:53-54` says **PASS by design** — they were never enforcement misses. They are still worth writing for a reader. **`land` is not a `/yf-plan` slash verb** (`SKILL.md:137-143`); documenting it as a command would manufacture a false claim — the trap #317 itself flags for `yf-judgement`. |
| D9 | **The engine-spec contradiction is repaired FIRST, in Epic 0.** | SPEC-first (AGENTS.md). `spec/checks.md` REQ-CHECK-004(a) mandates a node-level whole-corpus check while REQ-CHECK-005 confines the verifier to §6-scoped **edges**, and §6 maps globs→edges only — so a node-level check has **no firing surface**. Epic 3's §4 half depends on this being resolved. |

## Investigation Findings

### Planned experiments (pre-investigation checkpoint)

| # | Question | Why it can change the plan |
| :-- | :-- | :-- |
| EXP-001 | Of the claim classes #317's Class-A table names, which are **mechanically checkable** and which are irreducibly prose? Produce a census with a worked checker for at least one class. | **This experiment can refute D1.** If most claim classes are prose-only, "re-derive mechanically" buys a thin checker plus a manual sweep wearing a checker's clothes, and the scope must change to say so. |
| EXP-002 | For each of the six Class-B defects #317 asserts, does it reproduce against the **live** drift-check engine — and does the proposed remedy actually close it? Item 6 in particular claims `*`-glob pairing structurally cannot detect "zero instances on one side", and that flipping `optional`→`required` does **not** fix it. | If a defect does not reproduce it leaves scope; if a remedy does not close its defect, the epic is wrong. Item 6's claim is the one that decides whether a new existence check is needed at all. |
| EXP-003 | The build is **fail-closed on the first error**, so exactly one failure is currently observable. With a stub `yf-okf-hygiene` page in place, what else fails? Separately: what is #104's devserver failure mode, and does it bite a batch regeneration? | The P0 is scoped as "author one page". If the build fails again behind it, the P0 is an unknown-size epic, not a one-issue fix. |
| EXP-004 | How are the six `.png` files derived from their `.d2` sources — is there a committed target, is regeneration deterministic/reproducible, and does anything check `.d2` ↔ `.md` agreement? | #317 requires repairs "at all sites together, re-rendering affected PNGs". If regeneration is not reproducible, a diagram repair is unverifiable and needs a different discharge. |

### Findings summary

All four experiments completed. Full reports in `findings/`.

| Exp | Verdict | The result that changed the plan |
| :-- | :-- | :-- |
| [EXP-001](findings/exp-001-checkability-census.md) | **D1 corroborated** | 7 of 14 rows CHECKABLE, 5 PARTIAL, 2 PROSE-ONLY. Two ~70-line checkers covered 7 rows plus the P0 — and found **4 defect sites #317 does not list**, correcting its undercount on rows 4-6 from ~4 to **15**. Checker B initially returned a **false green**; only a *code-side* negative control exposed it. |
| [EXP-002](findings/exp-002-classb-reproduction.md) | **All six reproduce; 3 diagnoses WRONG, 2 remedies are NO-OPS** | Item 5 is a **dispatch gap**, not a manifest gap: the edge works when dispatched (3 FAILs, one new), but `CHANGE-VALIDATION.md:6-7` excludes the engine as "not a runnable command" — **4 opportunities, 0 catches**. Item 1's remedy is inert (§6 rows can only name edges that exist). Item 6's token flip is **byte-identical** either side. |
| [EXP-003](findings/exp-003-build-reality.md) | **P0 is ONE file** | Nothing is behind the first error — stub the page and the build is clean on both configs under `--fatal warnings`. But the guard is **existence-only**: an *empty* file passes it, so "the build passes" is an inadequate criterion. `\| tail` masks pelican's exit 1, and the reflexive fix `${PIPESTATUS[@]}` is a **bash-ism that is silently empty under zsh**. |
| [EXP-004](findings/exp-004-diagram-pipeline.md) | **Repair achievable; byte-verification is NOT** | All six PNGs differ from a fresh render, but **none is content-stale** — the cause is d2 version drift. A `.d2`↔code checker is buildable (~110 lines, 11 findings, two-sided control), but cannot catch **semantic mis-assignment**: the corrected `beads group (5)` box still lists the *workflows* skills. `architecture.d2` **omits the workflows group entirely**. |

**Two experiments converged independently** on `architecture.md`'s count drift and `install.md`'s
harness drift — both sitting on **required** drift edges, both still wrong. That convergence is the
strongest evidence for the Class-B thesis: **coverage is not detection.**

### Corrections to #317 this plan carries

The issue is the plan of record, and it is wrong in six places. Each is recorded so the
implementation follows the measurement rather than the prose:

1. **"images/cards/home have NO §6 trigger row"** — false; `web/content/**` matches all three. The
   defect is the narrow fan-out. Merge with item 3.
2. **"flipping `optional`→`required` does not fix it"** — correct, and now *proven* by A/B rather
   than argued. Drop the flip from the remedy entirely.
3. **"`yf-okf-hygiene` has neither a page nor a README"** — stale. It has a README (`4cf61c7`,
   plan-061); only the page is missing.
4. **"`harness-tune.md:156` contradicts `install.md:100-104`"** — no longer true, and was already
   untrue at filing. The narrower defect (an unconditional bullet vs a sha256 guard) remains.
5. **Rows 4-6 name ~4 sites** — the real count is **15**, including the project-scope column and a
   whole prose bullet at `install.md:204-207`.
6. **"no mention of `land` … is a coverage gap"** — omissions PASS by design; these were never
   enforcement misses. Retained as editorial work (D8), not as drift repair.

## Approach

**Order: unbreak → instrument → detect → repair → verify.** The build is unbroken first because
nothing downstream is observable until it runs. The spec repair and the checkers land next,
because D2 requires the new coverage to be what *finds* the Class-A inventory and then *verifies*
its repair. Content repair comes third, driven by checker output rather than by #317's stale table.

**Every checker ships with a CODE-SIDE negative control.** EXP-001's checker B returned a false
green against a tree with 15 real defects — the shared root `.agents/skills` contains the harness
id `agents`, so repaired rows scanned as ambiguous and were silently skipped. A doc-side control
cannot catch that. The convention is therefore: mutate the **source of truth** under passing docs
and require the checker to FAIL. A checker never observed to fail is not evidence.

**The mechanical/prose boundary is declared, not blurred.** Checkers cover counts, path strings,
artifact existence and formula-set membership. They explicitly do **not** cover semantic
mis-assignment (EXP-004's `beads group` membership bug), missing qualifiers, or editorial omission
— those are declared `not_checked` and discharged by a human read, following the precedent
`check_skill_readme_contract.py` already sets.

**The checker corpus is a PARAMETER, not `web/content/**`.** Pass-1 C4 measured the plan repeating #317's own undercount one level up: `README.md:105-106` and `AGENTS.md:78` carry the identical drifted harness matrix, and a `web/content/**`-scoped checker cannot reach either. The corpus is therefore `web/content/** + README.md + AGENTS.md`.

**#317 is followed on intent and overridden on fact.** Six of its specifics are wrong (see
Corrections above); the implementation follows the measurements in `findings/`.

## Epics

### Epic 0: SPEC-first — repair the drift engine's own contradiction
- Issue 0.1: Amend `skills/yf-drift-check/spec/checks.md` to resolve REQ-CHECK-004(a) vs REQ-CHECK-005 — a node-level whole-corpus check has no firing surface when §6 maps globs to edges only. Add the new/revised `REQ-*` id. **The amendment-log entry goes in the ROOT `SPEC.md`** — pass-1 C8 measured that neither `spec/checks.md` nor `yf-drift-check/SPEC.md` has a living amendment log, and that root `SPEC.md` currently contains zero `REQ-CHECK-*` ids. Reconcile the id namespace with `check_amendment_log.py`'s root-`SPEC.md` assumption in the same issue. **Write the tagged test for the new `REQ-CHECK-*` id in this same change-set, ahead of any code** — AGENTS.md SPEC-first, and it is what `check-req-coverage.py` looks for (pass-2 C8).
- Issue 0.2: Declare in the spec how a node-level existence check is dispatched — the mechanism the amendment authorizes, so Epic 3's §4 row has something to bind to.
  - depends-on: 0.1
- Issue 0.3: Record the `not_checked` declaration convention in the spec: which claim classes a mechanical gate covers, which remain prose-judged, and that the split must be stated rather than implied.
  - depends-on: 0.1
- Issue 0.4: Author `scripts/checks/plan066_checks.py` — one named subcommand per Success Criterion, each exiting 0/1, following the `plan065_checks.py` precedent. This is what makes the criteria EXECUTABLE rather than prose (pass-1 C1: `doc_lint` scored 17/17 non-conformant). Three implementation mandates, each from a measured failure: (a) `argparse(..., choices=sorted(SUBCOMMANDS))` so an unknown verb exits **2** (verified precedent) — a permissive dispatcher exits 0 and produces #364's silent false PASS; (b) **never pipe pelican** — `| tail` masks exit 1 and `${PIPESTATUS[@]}` is empty under zsh; use no pipe, or `set -o pipefail`; (c) the build verb must not hardcode `web/.venv`, which is absent from an execute worktree.
- Issue 0.4b: Author a `verbs-match` subcommand asserting `set(plan.md Verification verbs) == set(SUBCOMMANDS) - {'verbs-match'}`. **The carve-out is required, not cosmetic** (pass-3 C3): `verbs-match` is itself a subcommand, so a bare equality can never hold. Discharged by SC26 — the guard must be RUN, not merely written.
  - depends-on: 0.4
- Issue 0.5: Add the `gate-plan066-amendment` and req-coverage rows to `CHANGE-VALIDATION.md` (§1 recipe + §3 globs for `docs/plans/plan-066-*/**` and `skills/yf-drift-check/spec/**`), restoring the four-plan precedent (060, 062, 063, 064) that pass-1 C7 found broken. **Issue 0.5 DRAFTS these rows; Issue 8.4b LANDS them at land time, post-merge on `main`.** Pass-2 C8: `CHANGE-VALIDATION.md`'s own §1 banner declares a row reading `docs/plans/<in-flight-plan>/` **structurally unsatisfiable** from an execute worktree, and the existing `gate-plan049-*` rows are satisfiable only because those plans have LANDED. Adding them earlier would be the unsatisfiable-row class this repo already removed once.
  - depends-on: 0.1

### Epic 1: P0 — unbreak the Pelican build
- Issue 1.1: Author `web/content/skills/yf-okf-hygiene.md` — prose only, no frontmatter, first heading `##`, sourced from the skill's `SKILL.md`, `README.md` and `SPEC.md` so the three `e-skill-page-*` edges pass by construction. Model on `web/content/skills/yf-okf.md`.
- Issue 1.2: Bootstrap a reproducible build environment FIRST — `web/.venv` is untracked and exists only in the primary checkout, so the gate Test would exit 127 in an execute worktree (pass-1 C10). Use `uv run --with-requirements web/requirements.txt pelican …`, or create the venv as an explicit step. Then verify with the no-pipe, `--fatal warnings` form, plus content assertions on `output/skills/yf-okf-hygiene/index.html` (an `<hr>` with a non-trivial body, >= 2 `<h2>`) — because an EMPTY file satisfies the existence-only guard.
  - depends-on: 1.1, 0.4
  - resolves-upstream: #317 (partial)

### Epic 2: Class-B — the mechanical gate
- Issue 2.1: Build `scripts/checks/check_web_counts.py` — counted-set claims against `skills/*/SKILL.md` frontmatter and `skills/*/formulas/*.formula.toml` (excluding staged `.beads/formulas/`). **The corpus is a PARAMETER** defaulting to `web/content/**/*.{md,d2}` + `README.md` + `AGENTS.md` (pass-1 C4). It must also parse the enumerated GROUP-MEMBER IDS in the `architecture.md` group bullets, not only the integer (pass-1 C13). **This is NOT a `depends-on` edge and none may be added** (pass-3 C9): `4.3 → 4.2 → 4.1 → 2.5 → 2.1` already exists, so that edge would close a cycle and wedge the DAG. 2.1 must TOLERATE the pre-4.3 shape — parse the `workflows`/`beads` bullets, which already carry ids, and declare `utility`/`markdown` `not_checked` under 2.7 until 4.3 rewrites them.
- Issue 2.2: Build `scripts/checks/check_web_harness_paths.py` — path/identifier claims against `yf/src/harness_desc.rs` `DESCRIPTORS`, over the same parameterised corpus. Must strip path tokens before attributing a line to a harness id, or it false-greens on `.agents/skills` (measured, EXP-001). **Compare against the `(scope, field)` TUPLE — `user_skills_subpath` / `project_skills_subpath` vs `surface_dir` — never a flat string denylist** (pass-2 C12): `.config/opencode` and `.pi/agent` are the CORRECT `surface_dir` values; only their `/skills` subpaths are retired, so a bare-string denylist matches the real defects for the wrong reason and false-positives on any correct surface-dir mention.
- Issue 2.3: Build `scripts/checks/check_skill_page_contract.py` — the set-difference existence check. Set A = dirnames of `skills/*/SKILL.md`; Set B = stems of `web/content/skills/*.md`; assert `A \ B == {}`, report `B \ A` as orphans, carry a `--min-skills` vacuity floor.
  - depends-on: 0.2
- Issue 2.4: Build `scripts/checks/check_web_backend_claim.py` over **the same parameterised corpus as 2.1/2.2** (pass-2 C11 — it was the only checker whose corpus was unstated). Denylist plus a legitimate-mention allowlist: `README.md:25`'s `` `gh` / `glab` — GitHub / GitLab CLI `` is a correct mention of a CLI tool, not a backend claim, and must not false-positive.
- Issue 2.5: Build `scripts/checks/test_negative_controls.py` — one CODE-SIDE control per checker: mutate the SOURCE OF TRUTH under passing docs, assert the checker exits non-zero. It must PRINT AND ASSERT a per-checker observed-failure count and carry a `--min-checkers N` vacuity floor, so a harness that silently skips a checker cannot exit 0 (pass-1 C9 — EXP-001's checker-B failure mode, one level up).
  - depends-on: 2.1, 2.2, 2.3, 2.4
- Issue 2.6: Wire the checkers as `CHANGE-VALIDATION.md` §1 recipe rows with §3 trigger globs. **`grep 'web/' CHANGE-VALIDATION.md` currently returns NOTHING** — there is no web trigger scope at all, so the §3 globs are as load-bearing as the §1 rows. **Every checker's §3 globs MUST name its SOURCE OF TRUTH, not only the doc side** (pass-3 C2). Measured: commit `75a5796` ("yf-okf-hygiene ships") added skill #20, broke the build and drifted the 19→20 count while touching **zero** `web/` files — a doc-side-only trigger would not have fired on the very commit that caused the outage. So: `skills/*/SKILL.md` + `skills/*/formulas/**` for `check_web_counts`, `yf/src/harness_desc.rs` for `check_web_harness_paths`, and `skills/*/SKILL.md` + skill-dir creation for `check_skill_page_contract` — an absent file is never edited and can never fire its own on-edit check. The cited precedent `check_skill_readme_contract` already carries `skills/*/SKILL.md` in §3. **Sequenced after the repairs** (pass-1 C11): landing red rows earlier would make `_validate_merged` return fail/exit 3 and block every intermediate land.
  - depends-on: 2.5, 4.9, 5.3
- Issue 2.7: Record the `not_checked` declaration alongside the rows: semantic mis-assignment, missing qualifiers and editorial omission are out of mechanical scope and discharged by human read. Follow `check_skill_readme_contract.py`'s precedent of declaring an edge unchecked rather than implying it passed.
  - depends-on: 2.6, 0.3
- Issue 2.8: Add a CI job invoking all four checker scripts BY NAME (`check_web_counts.py`, `check_web_harness_paths.py`, `check_skill_page_contract.py`, `check_web_backend_claim.py` — the third does not match a `check_web_*` glob). Put it in `ci.yml`, which runs on every PR and every push to `main` with NO `paths:` filter; do not add one. Measured (pass-1 C12): CI runs NO CHANGE-VALIDATION tier, so without this the new coverage binds on the yf-plan land path only and a direct non-plan commit to `web/content/` is still unguarded.
  - depends-on: 2.6

### Epic 3: Class-B — the manifest repair
- Issue 3.1: Add a `web-diagram-src` node (`web/content/images/*.d2`) to `DRIFT-CHECK.md` §1 with edges to the frontmatter contract, `harness_desc.rs` and the formula set, then a §6 trigger row. Node → edge → §6 row, in that order: a §6 row can only name edges that exist.
- Issue 3.2: Widen `e-web-cli-surface` — all THREE edits: add `yf/src/harness_desc.rs` to the source node; add a §6 trigger row for that path; rewrite the §3 contract from `path-resolves` to `value-equal`. Add `web/content/pages/architecture.md`'s harness table AND `README.md`'s to the node set — `README.md`'s existing §6 row covers seven edges, none touching the harness matrix (pass-1 C4).
- Issue 3.3: Add a node/edge for the upstream-backend claim naming the four wrong sites including the `.d2`.
- Issue 3.4: Add a §4 Referencers row for `skill-page`, and at least one `required-section`-category inbound edge, so the existence check has a manifest binding.
  - depends-on: 0.2, 2.3
- Issue 3.5: Merge Class-B items 1 and 3 in the manifest — replace the narrow `web/content/**` → `e-status-values` fan-out with real content coverage for `lifecycle.md`, `workflows.md`, `usage.md`, `glossary.md`, `managed-files.md`, `beads-concepts.md`, `why.md`.
- Issue 3.6: Fix `DRIFT-CHECK.md:125` — `e-okf-version-pin`'s §2 Check Category is `value-equal`, a §3 Contract term outside the declared vocabulary, so the edge selects no check engine.
  - resolves-upstream: #247 (partial), #263 (partial)

### Epic 4: Class-A — prose site repair, driven by checker output
- Issue 4.1: Run every Epic-2 checker over the tree and record the produced inventory as `findings/class-a-inventory.md`. This inventory, not #317's table, is what Epic 4 repairs.
  - depends-on: 2.5
- Issue 4.2: NEGATIVE CONTROL on the inventory — assert every row #317 names appears in it. A row #317 lists that the checkers miss means a checker is blind, and is a defect in the instrument, not an absent defect.
  - depends-on: 4.1
- Issue 4.3: Repair the counted-set sites: `pages/architecture.md:59,65` (19→20 skills, utility 7→8, and name `yf-okf-hygiene` in the utility list). **Rewrite the `utility` and `markdown` bullets to enumerate BACKTICKED SKILL IDS** — pass-2 C7 measured that both currently carry English descriptions ("skill authoring, drift checking, OKF folders"), not ids, so there is nothing on line 65 a checker can compare to `skill-group` frontmatter without a hand-maintained translation table. The `workflows` and `beads` bullets already use ids; this makes all four uniform and checkable.
  - depends-on: 4.2
- Issue 4.4: Repair every path/identifier site the checker reports — across `pages/install.md`, `pages/architecture.md`, `images/install-matrix.d2`, **and `README.md:105-106` + `AGENTS.md:78`** (pass-1 C4) — both user AND project columns, plus the prose bullet at `install.md:204-207`. Ground truth: `yf/src/cmd/harness/prune_private.rs:487-488` (User/Project arms) classifies the two retired roots as legacy private roots to PRUNE, and `harness_desc.rs:381` asserts no shipped row may carry a `name_transform`.
  - depends-on: 4.2
- Issue 4.5: Repair the SIX upstream-backend sites: `pages/architecture.md:98`, `pages/glossary.md:151`, `pages/beads-concepts.md:131`, `images/architecture.d2:36`, `skills/yf-plan.md:90`, and **`README.md:417`** — which the corpus widening exposed (pass-2 C11): it states backend `github | gitlab | jira | none`, calls GitLab/Jira config-only stubs, and teaches the pre-gh-direct verb `bd github push <ids>`, contradicting `UPSTREAM_TRACKING.md`'s "no `bd <backend>` write command is issued at all".
  - depends-on: 4.2
- Issue 4.6: Repair the removed-feature claims: `skills/yf-okf.md:11,54` (`assess <corpus>`), and `skills/yf-okf.md:56` / `skills/yf-okf/SKILL.md:213` ("migration is the only write path" — an `e-skillspec-skillmd` finding too, so fixing the page alone leaves that edge unexamined).
  - depends-on: 4.2
- Issue 4.7: Repair the two PROSE-ONLY rows by hand: `harness-tune.md:156`'s missing sha256-guard qualifier, and the `yf-skill-authoring.md:109` lint-subset count (6→7, including `ML010`).
  - depends-on: 4.2
- Issue 4.8: Flag, do not "fix", the UNVERIFIABLE claims — `why.md`'s competitor table (no in-repo source of truth) and `yf-beads-extra.md`'s bd-version currency (checkable against the machine, `bd` measured at 1.2.2 vs a stated 1.0.5/1.1.0, so INCONCLUSIVE-tier not a hard gate).
  - depends-on: 4.2
- Issue 4.9: Re-run every checker; all must exit 0 over the repaired prose sites.
  - depends-on: 4.3, 4.4, 4.5, 4.6, 4.7

### Epic 5: Class-A — diagrams and the pinned re-render
- Issue 5.1: Repair `images/architecture.d2` — counts 18→20, beads (8)→(5), utility (6)→(8), ADD the entirely-absent workflows group, and correct the beads box membership (it currently lists the workflows skills).
  - depends-on: 4.2
- Issue 5.2: Repair `images/formulas.d2` — "three shipped" → five, and depict the undepicted `plan-review` and `verify-artifact`.
  - depends-on: 4.2
- Issue 5.3: Re-render ALL SIX diagrams with one pinned d2 version, in one commit, recording the version in the commit message. Per D7 — the version is the only reproducibility anchor.
  - depends-on: 5.1, 5.2, 4.4, 4.5
- Issue 5.4: HUMAN READ of each regenerated PNG for the residue no extractor catches — semantic mis-assignment, group membership, label placement. Record one dated entry per diagram in **`findings/diagram-reads.md`**.
  - depends-on: 5.3
- Issue 5.5: Run `render.py check-dir web/content/images` for ORPHAN DETECTION ONLY — a `.d2` with no sibling `.png`. Pass-1 C6 measured that it returns `{"status":"ok"}` exit 0 over the very diagrams this plan calls wrong: `render.py:154-169` exits non-zero only on orphans, and staleness never affects the exit code. Do NOT cite it as a staleness check and do NOT assert byte-equality against the committed PNGs.
  - depends-on: 5.3

### Epic 6: Editorial coverage and the concepts glossary
- Issue 6.1: Document the real `land` mechanism accurately — a `plan_manager.py` verb and a lander agent, NOT a `/yf-plan` slash command. Verify against `SKILL.md:137-143` before writing. **You MAY name the wrong form in order to correct it** — SC13's checker ignores negated mentions (pass-3 C6). What must not appear is an AFFIRMATIVE claim that the slash form exists.
  - depends-on: 1.2
- Issue 6.2: Document retrospectives, the escalation surface (a yf-plan mechanism, NOT a `yf-judgement` skill — no such skill ships) and the autonomy levels (`--checkpoint`, `--autonomous`, `--sweep-gates`).
  - depends-on: 1.2
- Issue 6.3: Document the `closable` verb on `web/content/skills/yf-beads-upstream.md`.
  - depends-on: 1.2
- Issue 6.4: Author the idiomatic-terms glossary — pouring beads, landing, molecules, wisps, gates. **It MUST render.** Pass-1 C5 measured that a page under `web/content/concepts/` produces exit 0, 32 pages (unchanged), zero warnings and NO OUTPUT — `pelicanconf.py` sets no `PAGE_PATHS`, so Pelican's default `["pages"]` silently excludes any new directory. Author under `web/content/pages/`, or add the directory to `PAGE_PATHS` in this same issue.
  - depends-on: 1.2
  - resolves-upstream: #127 (include)
- Issue 6.5: Assert every page Epic 6 authored actually RENDERED — the emitted `index.html` exists and is non-trivial, reusing SC2's shape. A page that silently never renders is this plan's own thesis firing inside the plan.
  - depends-on: 6.1, 6.2, 6.3, 6.4

### Epic 7: Adjacent surfaces
- Issue 7.1: Remediate `OKF-EXTENSION.md` — 3 stale DRAFT banners, 2 dangling symbols, 2 shipped-but-open decisions.
  - resolves-upstream: #363 (include)
- Issue 7.2: Fix the `yf-okf-hygiene` SKILL.md "31 legacy, 7 halt" figure so it does not read as repo-agnostic.
  - resolves-upstream: #322 (include)
- Issue 7.3: Fix #104 — `IGNORE_FILES` in `pelicanconf.py`, a `set -m` process-group `devserver` plus a `stopserver` target reading `.devserver.pgid`, and the gitignore line. Sequenced so it cannot block the P0: measured orthogonal to one-shot builds.
  - resolves-upstream: #104 (include)

### Epic 8: Verification, retrospective, and closure
- Issue 8.1: Full verification sweep — every checker exits 0, `pelican` builds clean under `--fatal warnings` with no pipe, `render.py check-dir` clean.
  - depends-on: 4.9, 5.5, 6.5, 7.1, 7.2, 7.3, 2.8, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6
- Issue 8.2: Assert each Class-B defect is CLOSED or FILED WITH AN OWNER, enumerated explicitly — never implied by a green build.
  - depends-on: 3.6, 2.7
- Issue 8.3: Write `plan-retrospective.md` distinguishing content defects from process defects, with counts, per #317's acceptance.
  - depends-on: 8.1, 8.2
- Issue 8.4: File follow-on issues tagged by class — the zero-byte-page guard hole, the `e-okf-version-pin` category defect if not fixed here, and any pipeline defect found outside the four in-scope Class-B items (D5).
  - depends-on: 8.3
- Issue 8.4b: **AT LAND, post-merge on `main`**, add the `gate-plan066-amendment` and req-coverage rows Issue 0.5 drafted. Pass-3 C5: 0.5 is an Epic-0 bead a coordinator dispatches immediately, but its rows are structurally unsatisfiable from an execute worktree — so 0.5 DRAFTS them and this issue LANDS them. Closing 0.5 alone would be a no-op.
  - depends-on: 0.5, 8.3
- Issue 8.5: Reconcile upstream — update #317, #104, #127, #363, #322 per disposition; leave #247 and #263 open as partials. Fill the `Resolved By` column for all five `include` rows before close (pass-1 C14: R2a promotes an empty cell to `E` severity at `reconciling`).
  - depends-on: 8.4
  - resolves-upstream: #317 (include)

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: Build green
- Type: auto
- Condition: Pelican builds with zero errors AND zero warnings, and the new page has real content
- Test: uv run scripts/checks/plan066_checks.py build-clean
- Blocks: epic:4, epic:5, epic:6
- Instructions: Author the missing skill page (Issue 1.1). The verb wraps `pelican … --fatal warnings` with NO PIPE and asserts the emitted page has real content — an empty file satisfies the existence-only guard. It must not hardcode `web/.venv`, which is untracked and absent from an execute worktree (exit 127). Never pipe pelican: `| tail` masks its exit 1, and `${PIPESTATUS[@]}` is a bash-ism that expands to nothing under this repo's zsh.

### Capability Gate: Checkers are fail-capable
- Type: auto
- Condition: every Epic-2 checker has been OBSERVED to fail against a code-side mutation
- Test: uv run scripts/checks/test_negative_controls.py --all --min-checkers 4
- Blocks: epic:4, epic:5
- Instructions: Each checker needs a control that mutates the SOURCE OF TRUTH under passing docs. Doc-side controls are insufficient — measured, checker B false-greened on 15 real defects and only a code-side control exposed it. The `--min-checkers` floor and the per-checker observed-failure count are IN THE TEST, not only in SC4: a harness that silently skips a checker would otherwise exit 0 and open this gate — the same failure mode, one level up.

### Capability Gate: Diagram human read
- Type: human
- Condition: each of the six regenerated PNGs has been read by a human for semantic residue
- Test: manual
- Blocks: 8.1
- Instructions: No text extractor catches semantic mis-assignment. Measured: the corrected `beads group (5)` box still listed the workflows skills — count right, membership wrong. Read each PNG and record the read to `findings/diagram-reads.md`. Pass-1 C6 removed `5.5` from this Blocks set: `render.py check-dir` passes today with no work done, so gating it behind a human gate spent operator attention to unblock a vacuous check.

### Capability Gate: Upstream write authorization
- Type: human
- Condition: the operator has authorized the follow-on issue filings and the reconcile writes
- Test: manual
- Blocks: 8.4, 8.5
- Instructions: `gh issue create` / `gh issue comment` / `gh issue close` are outward-facing writes. Present the drafted bodies; never self-authorize. Compose with `--body-file -` fed by a quoted heredoc, and verify by reading back.

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | A checker returns a **false green** and the plan reports coverage it never had. **Measured, not hypothetical** — EXP-001's checker B did exactly this against 15 real defects. | high | Code-side negative control per checker, gated (Capability Gate: Checkers are fail-capable). Issue 4.2 additionally asserts every #317 row appears in the produced inventory. |
| R2 | "The build passes" is satisfied by an **empty file** — the guard is existence-only. | high | Issue 1.2's criterion is conjunctive: exit 0 under `--fatal warnings` PLUS content assertions on the emitted HTML. |
| R3 | A verification snippet pipes pelican through `tail` and reports green on a broken build; the reflexive `${PIPESTATUS[@]}` fix is **silently empty under zsh**. | high | **AMENDED after pass-3 C7 — the old cell claimed enforcement "in every criterion", which was FALSE: 0 of 26 criteria mention pelican or a pipe, since every Verification cell delegates to `plan066_checks.py`.** What actually enforces it: Issue 0.4 mandate (b) (no pipe in the script; `set -o pipefail` if unavoidable) and the Build-green gate's Instructions. `${pipestatus[@]}` is the zsh spelling. |
| R4 | The plan repairs #317's stale table and misses the ~4 sites and 11 extra path cells it does not list. | high | D1: the inventory is checker-derived (4.1); #317's table is the negative control (4.2), never the work list. |
| R5 | Manifest edits land but the engine still never dispatches, so new edges inherit the measured 0-catch rate. | high | D6: the mechanical gate (Epic 2) is the primary deliverable, wired into CHANGE-VALIDATION's FULL tier, which IS mechanically enforced by `_validate_merged` (fail/exit 3). **AMENDED after pass-1 C12:** that binds the yf-plan LAND PATH ONLY — CI runs no tier and the FAST trigger is itself prose. Issue 2.8 adds the CI job that covers direct non-plan commits. |
| R6 | A §6 row is added naming an edge that does not exist, and silently covers nothing. | med | Issue 3.1 enforces node → edge → §6 row ordering explicitly. |
| R7 | The three widened-`e-web-cli-surface` edits are done partially, leaving the node unable to fire on its own source edit. | med | Issue 3.2 enumerates all three as one issue rather than three separable ones. |
| R8 | Re-rendering diagrams produces a byte diff on all six and is misread as failure or as staleness. | med | D7 re-renders all six under one pinned version. **AMENDED after pass-2 C4:** byte equality is NOT forbidden — it is the strongest available check, and is decidable *within* a pinned version (measured: identical sha256 across two renders). EXP-004's "byte-verification is not achievable" is true only ACROSS d2 versions. SC10 asserts sha256 equality against a fresh render plus `d2 --version` equal to the recorded pin. |
| R9 | A diagram is mechanically correct and semantically wrong (right count, wrong membership). | med | Capability Gate: Diagram human read; Issue 5.4 records a per-diagram read. |
| R10 | Documenting `land` as a slash command manufactures a **new** false claim while fixing old ones. | med | D8 and Issue 6.1 both state the constraint; the page must be verified against `SKILL.md:137-143`. Same for the non-existent `yf-judgement` skill. |
| R11 | Epic 7's #104 fix couples an unrelated Makefile/process-group change to the P0 and blocks it. | low | Measured orthogonal to one-shot builds (EXP-003); Issue 7.3 carries no dependency into Epics 1-5. |
| R12 | The spec amendment lands after the manifest change that depends on it, violating SPEC-first. | low | D9: Epic 0 is first, and Issues 2.3 / 3.4 depend on 0.2. |
| R13 | Scope creep — the new checkers surface pipeline defects beyond the four Class-B items. | med | D5: file, do not fix. Issue 8.4 is the filing route. |
| R14 | The plan repeats #317's undercount one level up — a `web/content/**`-scoped checker cannot reach `README.md` or `AGENTS.md`, which carry the identical drifted matrix, so SC7 certifies "all sites repaired" while the most-read document stays wrong. **Measured, pass-1 C4.** | high | The checker corpus is a parameter covering `web/content/** + README.md + AGENTS.md` (Issues 2.1, 2.2, 4.4), and `README.md`'s harness table joins the `harness_desc.rs`-sourced node (3.2). |
| R15 | An authored page silently never renders — measured, a file under a directory absent from `PAGE_PATHS` yields exit 0, unchanged page count, zero warnings and no output. **The plan's own thesis firing inside the plan.** | high | Issue 6.4 authors under a rendered path or amends `PAGE_PATHS`; Issue 6.5 asserts every Epic-6 page actually emitted a non-trivial `index.html`. |

## Success Criteria

Every Verification cell is an **executable clause** discharged by `scripts/checks/plan066_checks.py`
(authored in Issue 0.4, `plan065_checks.py` precedent). Pass-1 C1 measured the previous prose table
at 17/17 non-conformant under `doc_lint`. The one irreducibly manual row says so explicitly.

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | The plan authored `web/content/skills/yf-okf-hygiene.md` and Pelican builds with zero errors and zero warnings | `uv run scripts/checks/plan066_checks.py build-clean` → exit 0 | 1.1, 1.2 |
| SC2 | The authored page has real content, not merely a file satisfying an existence-only guard — Asserts `output/skills/yf-okf-hygiene/index.html` has >= 1 `<hr>` and >= 2 `<h2>` | `uv run scripts/checks/plan066_checks.py page-content` → exit 0 | 1.2 |
| SC3 | The plan amended the drift-engine spec with a new/revised `REQ-*` id and a root-`SPEC.md` amendment-log entry | `uv run scripts/check_amendment_log.py --plan plan-066-james-dixson-e7fadb` → exit 0 | 0.1, 0.5 |
| SC4 | Every checker the plan shipped was OBSERVED to fail against a code-side mutation | `uv run scripts/checks/test_negative_controls.py --all --min-checkers 4` → exit 0 | 2.5 |
| SC5 | Every checker the plan shipped exits 0 over the repaired tree | `uv run scripts/checks/plan066_checks.py checkers-green` → exit 0 | 4.9, 8.1 |
| SC6 | The checker-derived inventory contains every row #317 names — no #317 row is absent from it | `uv run scripts/checks/plan066_checks.py inventory-control` → exit 0 | 4.2 |
| SC7 | The plan repaired every path/identifier site the checker reports, across `web/content/**`, `README.md` AND `AGENTS.md` — not the ~4 #317 lists | `uv run scripts/checks/plan066_checks.py harness-sites` → exit 0 | 4.4 |
| SC8 | The plan repaired all SIX upstream-backend sites including the `.d2` and `README.md:417` | `uv run scripts/checks/plan066_checks.py backend-sites` → exit 0 | 4.5 |
| SC9 | The plan added the `workflows` group to `architecture.d2`, which previously omitted it entirely, and the group-member NAME lists agree with frontmatter | `uv run scripts/checks/plan066_checks.py group-membership` → exit 0 | 5.1, 4.3 |
| SC10 | Every committed PNG is byte-identical (sha256) to a fresh render of its `.d2` under the recorded pin `d2 v0.8.2` with the pinned flags `--theme 0 --layout elk`, and `d2 --version` equals that pin — MEASURED twice: two renders of one source under one version give equal sha256, so byte equality IS decidable within a pin (correcting EXP-004, whose "not achievable" holds only ACROSS versions). It replaces an encoding-signature form measured NON-discriminating: all six fresh renders share one signature and committed `lifecycle.png` already matched it while differing in sha256 — 1/6 satisfied with zero work, and satisfiable by a stale PNG. sha256 equality is flag-sensitive, hence the pinned flags | `uv run scripts/checks/plan066_checks.py render-bytes-match` → exit 0 | 5.3 |
| SC11 | Each regenerated PNG was read by a human for the semantic residue no extractor catches | manual: a human must look at a rendered image; no command can decide it | 5.4 |
| SC11b | The human reads were RECORDED — `findings/diagram-reads.md` carries one dated entry per diagram | `uv run scripts/checks/plan066_checks.py diagram-reads` → exit 0 | 5.4 |
| SC12 | The plan added the DRIFT-CHECK nodes, edges and §6 rows Class-B requires, and every §6 row names an edge that exists | `uv run scripts/checks/plan066_checks.py manifest-rows` → exit 0 | 3.1, 3.2, 3.3, 3.4, 3.5, 3.6 |
| SC13 | The plan documented `land` as a `plan_manager.py` verb — the authored file exists AND states the verb form AND no page ASSERTS the slash form. The negative leg must IGNORE a negated or quoted mention (pass-3 C6: the idiomatic sentence "`land` is not a `/yf-plan land` slash command" writes the forbidden string, so a naive grep would flip to FALSE and punish the correct way to do the work) | `uv run scripts/checks/plan066_checks.py land-documented` → exit 0 | 6.1 |
| SC14 | The plan documented the escalation surface as a yf-plan mechanism — positively stated, and no page ASSERTS a `yf-judgement` skill exists. Same negated-mention carve-out as SC13, with `-r` (its absence makes system grep exit 2 on a directory having searched zero bytes) | `uv run scripts/checks/plan066_checks.py escalation-documented` → exit 0 | 6.2 |
| SC15 | Every page Epic 6 authored actually RENDERED — a non-trivial emitted `index.html` per page | `uv run scripts/checks/plan066_checks.py epic6-renders` → exit 0 | 6.1, 6.2, 6.3, 6.4, 6.5 |
| SC16 | Every Class-B defect is explicitly CLOSED or FILED WITH AN OWNER, enumerated by name — never implied by a green build — Asserts six named dispositions | `uv run scripts/checks/plan066_checks.py classb-disposition` → exit 0 | 8.2 |
| SC17 | The retrospective distinguishes content defects from process defects, with counts | `uv run scripts/checks/plan066_checks.py retro-classes` → exit 0 | 8.3 |
| SC18 | The plan declared which claim classes the mechanical gate does NOT cover | `uv run scripts/checks/plan066_checks.py notchecked-declared` → exit 0 | 2.7 |
| SC19 | The plan repaired the three adjacent surfaces it took on (#363, #322, #104) | `uv run scripts/checks/plan066_checks.py adjacent-surfaces` → exit 0 | 7.1, 7.2, 7.3 |
| SC20 | The new coverage fires OUTSIDE the yf-plan land path — a CI job invokes all four checker scripts BY NAME and is REACHED on every PR and every push to `main`. **Do NOT add a `paths:` filter** (pass-3 C2): `ci.yml` runs unfiltered today, so a filtered job would give strictly LESS coverage. The criterion asserts the job is not gated behind `if: false` or a filter excluding the source side | `uv run scripts/checks/plan066_checks.py ci-wired` → exit 0 | 2.8 |
| SC26 | The criteria table's verb set agrees with the script's subcommands — the guard over the 22 criteria routing through one script is itself EXECUTED, not merely authored (pass-3 C3: 0.4b landed the subcommand but no criterion ran it) | `uv run scripts/checks/plan066_checks.py verbs-match` → exit 0 | 0.4, 0.4b |
| SC25 | `CHANGE-VALIDATION.md` gained §1 recipe rows for all FOUR checkers NAMED EXPLICITLY — `check_web_counts.py`, `check_web_harness_paths.py`, `check_skill_page_contract.py`, `check_web_backend_claim.py` (not a `check_web_*` glob: the third lacks that prefix, so a glob silently drops it — pass-3 C4) — AND §3 globs covering BOTH the doc side (`web/content/**`, `README.md`, `AGENTS.md`) and the SOURCE side (`skills/*/SKILL.md`, `skills/*/formulas/**`, `yf/src/harness_desc.rs`). Measured at ZERO `web/` rows before this plan | `uv run scripts/checks/plan066_checks.py cv-rows` → exit 0 | 2.6, 2.7 |
| SC21 | The plan repaired the removed-feature claims at every site, INCLUDING the `SKILL.md` copy — fixing the page alone would leave `e-skillspec-skillmd` unexamined — Asserts `assess <corpus>` absent from `skills/yf-okf.md`, and the "migration is the only write path" claim corrected at BOTH `yf-okf.md:56` and `skills/yf-okf/SKILL.md:213` | `uv run scripts/checks/plan066_checks.py removed-features` → exit 0 | 4.6 |
| SC22 | The plan repaired the two PROSE-ONLY rows by hand and FLAGGED rather than "fixed" the unverifiable ones — Asserts the `harness-tune.md` sha256 qualifier present, the lint-subset count reads 7 incl. `ML010`, and `why.md`'s competitor table carries an explicit unverifiable marker | `uv run scripts/checks/plan066_checks.py prose-rows` → exit 0 | 4.7, 4.8 |
| SC23 | `formulas.d2` states five shipped formulas and depicts all five | `uv run scripts/checks/plan066_checks.py formulas-diagram` → exit 0 | 5.2 |
| SC24 | No `.d2` lacks a sibling `.png` after the re-render — Orphan detection ONLY — `render.py check-dir` cannot detect staleness, measured | `uv run scripts/checks/plan066_checks.py diagram-orphans` → exit 0 | 5.5 |

**Deliberately uncovered issues — the list is MECHANICALLY DERIVED and must match the extractor.**
Currently exactly ten: `0.2, 0.3, 2.1, 2.2, 2.3, 2.4, 4.1, 8.4, 8.4b, 8.5`. Pass-3 C8 caught the
previous list disagreeing with `plan_extract` by two entries while asserting coverage that did not
exist — the same bookkeeping drift as pass-2's C6, one level down. The instrument-building steps
(0.2, 0.3, 2.1-2.4, 4.1) carry no criterion of their own **by design** — every criterion above executes the instruments they
build, so a broken instrument fails the criteria that run it rather than passing a criterion written
about itself. Naming them would be a criterion asserting that a checker exists, which is weaker than
one asserting the checker WORKS. 8.4 and 8.5 are discharged by the reconcile gate and the §6.4
`verify-reconcile` chain, not by a plan criterion — as is 8.4b, whose deliverable lands post-merge
where no plan criterion can observe it.

**Issues 0.4 and 0.4b were on this list and have been REMOVED (pass-3 C3/C8).** The old note claimed
0.4 was "covered by SC-verb agreement via 0.4b" — false: 0.4b landed the `verbs-match` subcommand but
**no criterion ever ran it**, so the guard over the 22 criteria routing through one script was itself
unexecuted. **SC26** now discharges both.

**Issue 2.6 was on this list and has been REMOVED (pass-2 C6).** It is the plan's *primary*
deliverable — the CHANGE-VALIDATION wiring D6 names — not an instrument-building step. The pass-1
C3 and C11 resolutions interacted to hide it: C11 resequenced it to the end, C3's uncovered-list
swept it up, and no criterion asserted the rows landed. SC25 now does. Issue 0.4 is likewise
covered, by SC-verb agreement via 0.4b.

