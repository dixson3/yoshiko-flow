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
| D6 | **Class B ships a MECHANICAL GATE plus the manifest fixes.** Runnable checkers for the decidable edges become `CHANGE-VALIDATION.md` recipe rows; genuinely-LLM edges stay on the prose trigger with an explicit `not_checked` declaration. | EXP-002 measured the engine at **4 firing opportunities, 0 catches** — a *dispatch* gap. Manifest edits cannot fix dispatch, so #317's remedy alone would produce more edges that also never run. Precedent: `check_skill_readme_contract.py` already does exactly this. |
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

**#317 is followed on intent and overridden on fact.** Six of its specifics are wrong (see
Corrections above); the implementation follows the measurements in `findings/`.

## Epics

### Epic 0: SPEC-first — repair the drift engine's own contradiction
- Issue 0.1: Amend `skills/yf-drift-check/spec/checks.md` to resolve REQ-CHECK-004(a) vs REQ-CHECK-005 — a node-level whole-corpus check has no firing surface when §6 maps globs to edges only. Add the new/revised `REQ-*` id and a living-amendment-log entry.
- Issue 0.2: Declare in the spec how a node-level existence check is dispatched — the mechanism the amendment authorizes, so Epic 3's §4 row has something to bind to.
  - depends-on: 0.1
- Issue 0.3: Record the `not_checked` declaration convention in the spec: which claim classes a mechanical gate covers, which remain prose-judged, and that the split must be stated rather than implied.
  - depends-on: 0.1

### Epic 1: P0 — unbreak the Pelican build
- Issue 1.1: Author `web/content/skills/yf-okf-hygiene.md` — prose only, no frontmatter, first heading `##`, sourced from the skill's `SKILL.md`, `README.md` and `SPEC.md` so the three `e-skill-page-*` edges pass by construction. Model on `web/content/skills/yf-okf.md`.
- Issue 1.2: Verify the build with the no-pipe, `--fatal warnings` form, plus content assertions on the emitted HTML (an `<hr>` with a non-trivial body, >= 1 `<h2>` beyond "At a glance") — because an EMPTY file satisfies the existence-only guard.
  - depends-on: 1.1
  - resolves-upstream: #317 (partial)

### Epic 2: Class-B — the mechanical gate
- Issue 2.1: Build `scripts/checks/check_web_counts.py` — counted-set claims over `web/content/**/*.{md,d2}` against `skills/*/SKILL.md` frontmatter and `skills/*/formulas/*.formula.toml` (excluding staged `.beads/formulas/`).
- Issue 2.2: Build `scripts/checks/check_web_harness_paths.py` — path/identifier claims against `yf/src/harness_desc.rs` `DESCRIPTORS`. Must strip path tokens before attributing a line to a harness id, or it false-greens on `.agents/skills`.
- Issue 2.3: Build `scripts/checks/check_skill_page_contract.py` — the set-difference existence check. Set A = dirnames of `skills/*/SKILL.md`; Set B = stems of `web/content/skills/*.md`; assert `A \ B == {}`, report `B \ A` as orphans, carry a `--min-skills` vacuity floor.
  - depends-on: 0.2
- Issue 2.4: Build `scripts/checks/check_web_backend_claim.py` — the upstream-backend denylist with a legitimate-mention allowlist, covering all five known sites including `images/architecture.d2:36`.
- Issue 2.5: Give every checker a CODE-SIDE negative control test: mutate the source of truth under passing docs, assert the checker exits non-zero. A checker without one is not merged.
  - depends-on: 2.1, 2.2, 2.3, 2.4
- Issue 2.6: Wire the checkers as `CHANGE-VALIDATION.md` §1 recipe rows with §3 trigger globs. The `check_skill_page_contract` trigger MUST include the source side (`skills/*/SKILL.md`, skill-dir creation) — an absent file is never edited and can never fire its own on-edit check.
  - depends-on: 2.5
- Issue 2.7: Record the `not_checked` declaration alongside the rows: semantic mis-assignment, missing qualifiers and editorial omission are out of mechanical scope and discharged by human read.
  - depends-on: 2.6, 0.3

### Epic 3: Class-B — the manifest repair
- Issue 3.1: Add a `web-diagram-src` node (`web/content/images/*.d2`) to `DRIFT-CHECK.md` §1 with edges to the frontmatter contract, `harness_desc.rs` and the formula set, then a §6 trigger row. Node → edge → §6 row, in that order: a §6 row can only name edges that exist.
- Issue 3.2: Widen `e-web-cli-surface` — all THREE edits: add `yf/src/harness_desc.rs` to the source node; add a §6 trigger row for that path; rewrite the §3 contract from `path-resolves` to `value-equal`. Add `web/content/pages/architecture.md`'s harness table to the node set.
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
- Issue 4.3: Repair the counted-set sites: `pages/architecture.md:59,65` (19→20 skills, utility 7→8, and name `yf-okf-hygiene` in the utility list).
  - depends-on: 4.2
- Issue 4.4: Repair all 15 path/identifier sites across `pages/install.md`, `pages/architecture.md` and `images/install-matrix.d2` — both user AND project columns, plus the prose bullet at `install.md:204-207`.
  - depends-on: 4.2
- Issue 4.5: Repair the five upstream-backend sites: `pages/architecture.md:98`, `pages/glossary.md:151`, `pages/beads-concepts.md:131`, `images/architecture.d2:36`, `skills/yf-plan.md:90`.
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
  - depends-on: 5.1, 5.2, 4.4
- Issue 5.4: HUMAN READ of each regenerated PNG for the residue no extractor catches — semantic mis-assignment, group membership, label placement. Record the read per diagram.
  - depends-on: 5.3
- Issue 5.5: Confirm `render.py check-dir web/content/images` is clean. Do NOT assert byte-equality against the committed PNGs — measured, all six differ from a fresh render for reasons unrelated to correctness.
  - depends-on: 5.3

### Epic 6: Editorial coverage and the concepts glossary
- Issue 6.1: Document the real `land` mechanism accurately — a `plan_manager.py` verb and a lander agent, NOT a `/yf-plan` slash command. Verify against `SKILL.md:137-143` before writing.
  - depends-on: 1.2
- Issue 6.2: Document retrospectives, the escalation surface (a yf-plan mechanism, NOT a `yf-judgement` skill — no such skill ships) and the autonomy levels (`--checkpoint`, `--autonomous`, `--sweep-gates`).
  - depends-on: 1.2
- Issue 6.3: Document the `closable` verb on `web/content/skills/yf-beads-upstream.md`.
  - depends-on: 1.2
- Issue 6.4: Author the `web/concepts` idiomatic-terms glossary — pouring beads, landing, molecules, wisps, gates.
  - depends-on: 1.2
  - resolves-upstream: #127 (include)

### Epic 7: Adjacent surfaces
- Issue 7.1: Remediate `OKF-EXTENSION.md` — 3 stale DRAFT banners, 2 dangling symbols, 2 shipped-but-open decisions.
  - resolves-upstream: #363 (include)
- Issue 7.2: Fix the `yf-okf-hygiene` SKILL.md "31 legacy, 7 halt" figure so it does not read as repo-agnostic.
  - resolves-upstream: #322 (include)
- Issue 7.3: Fix #104 — `IGNORE_FILES` in `pelicanconf.py`, a `set -m` process-group `devserver` plus a `stopserver` target reading `.devserver.pgid`, and the gitignore line. Sequenced so it cannot block the P0: measured orthogonal to one-shot builds.
  - resolves-upstream: #104 (include)

### Epic 8: Verification, retrospective, and closure
- Issue 8.1: Full verification sweep — every checker exits 0, `pelican` builds clean under `--fatal warnings` with no pipe, `render.py check-dir` clean.
  - depends-on: 4.9, 5.5, 6.4, 7.1, 7.2, 7.3
- Issue 8.2: Assert each Class-B defect is CLOSED or FILED WITH AN OWNER, enumerated explicitly — never implied by a green build.
  - depends-on: 3.6, 2.7
- Issue 8.3: Write `plan-retrospective.md` distinguishing content defects from process defects, with counts, per #317's acceptance.
  - depends-on: 8.1, 8.2
- Issue 8.4: File follow-on issues tagged by class — the zero-byte-page guard hole, the `e-okf-version-pin` category defect if not fixed here, and any pipeline defect found outside the four in-scope Class-B items (D5).
  - depends-on: 8.3
- Issue 8.5: Reconcile upstream — update #317, #104, #127, #363, #322 per disposition; leave #247 and #263 open as partials.
  - depends-on: 8.4

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: Build green
- Type: auto
- Condition: Pelican builds with zero errors AND zero warnings, and the new page has real content
- Test: cd web && .venv/bin/pelican content -s pelicanconf.py -o "$(mktemp -d)" --fatal warnings
- Blocks: epic:4, epic:5, epic:6
- Instructions: Author the missing skill page (Issue 1.1). Never pipe this command — `| tail` masks pelican's exit 1, and `${PIPESTATUS[@]}` is a bash-ism that expands to nothing under this repo's zsh.

### Capability Gate: Checkers are fail-capable
- Type: auto
- Condition: every Epic-2 checker has been OBSERVED to fail against a code-side mutation
- Test: uv run scripts/checks/test_negative_controls.py --all
- Blocks: epic:4, epic:5
- Instructions: Each checker needs a control that mutates the SOURCE OF TRUTH under passing docs. Doc-side controls are insufficient — measured, checker B false-greened on 15 real defects and only a code-side control exposed it.

### Capability Gate: Diagram human read
- Type: human
- Condition: each of the six regenerated PNGs has been read by a human for semantic residue
- Test: manual
- Blocks: 5.5, 8.1
- Instructions: No text extractor catches semantic mis-assignment. Measured: the corrected `beads group (5)` box still listed the workflows skills — count right, membership wrong. Read each PNG and record the read.

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
| R3 | A verification snippet pipes pelican through `tail` and reports green on a broken build; the reflexive `${PIPESTATUS[@]}` fix is **silently empty under zsh**. | high | No-pipe form mandated in the gate Test and in every criterion. `${pipestatus[@]}` is the zsh spelling; `set -o pipefail` the portable one. |
| R4 | The plan repairs #317's stale table and misses the ~4 sites and 11 extra path cells it does not list. | high | D1: the inventory is checker-derived (4.1); #317's table is the negative control (4.2), never the work list. |
| R5 | Manifest edits land but the engine still never dispatches, so new edges inherit the measured 0-catch rate. | high | D6: the mechanical gate (Epic 2) is the primary deliverable and is wired into CHANGE-VALIDATION, which does run. |
| R6 | A §6 row is added naming an edge that does not exist, and silently covers nothing. | med | Issue 3.1 enforces node → edge → §6 row ordering explicitly. |
| R7 | The three widened-`e-web-cli-surface` edits are done partially, leaving the node unable to fire on its own source edit. | med | Issue 3.2 enumerates all three as one issue rather than three separable ones. |
| R8 | Re-rendering diagrams produces a byte diff on all six and is misread as failure or as staleness. | med | D7 re-renders all six under one pinned version; Issue 5.5 forbids a byte-equality assertion and states why. |
| R9 | A diagram is mechanically correct and semantically wrong (right count, wrong membership). | med | Capability Gate: Diagram human read; Issue 5.4 records a per-diagram read. |
| R10 | Documenting `land` as a slash command manufactures a **new** false claim while fixing old ones. | med | D8 and Issue 6.1 both state the constraint; the page must be verified against `SKILL.md:137-143`. Same for the non-existent `yf-judgement` skill. |
| R11 | Epic 7's #104 fix couples an unrelated Makefile/process-group change to the P0 and blocks it. | low | Measured orthogonal to one-shot builds (EXP-003); Issue 7.3 carries no dependency into Epics 1-5. |
| R12 | The spec amendment lands after the manifest change that depends on it, violating SPEC-first. | low | D9: Epic 0 is first, and Issues 2.3 / 3.4 depend on 0.2. |
| R13 | Scope creep — the new checkers surface pipeline defects beyond the four Class-B items. | med | D5: file, do not fix. Issue 8.4 is the filing route. |

## Success Criteria

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | The plan authored `web/content/skills/yf-okf-hygiene.md`, and Pelican builds with zero errors and zero warnings | `cd web && .venv/bin/pelican content -s pelicanconf.py -o "$(mktemp -d)" --fatal warnings` exits 0, no pipe | 1.1, 1.2 |
| SC2 | The authored page has real content, not merely a file that satisfies an existence-only guard | emitted `index.html` contains `<hr>` and >= 2 `<h2>` | 1.2 |
| SC3 | The plan amended `skills/yf-drift-check/spec/checks.md` with a new/revised `REQ-*` id and a living-amendment-log entry, BEFORE any manifest edit that depends on it | git log order: Epic 0 commits precede Issues 2.3 and 3.4 | 0.1, 0.2 |
| SC4 | Every checker the plan shipped has been OBSERVED to fail against a code-side mutation | `uv run scripts/checks/test_negative_controls.py --all` exits 0 and reports one observed failure per checker | 2.5 |
| SC5 | Every checker the plan shipped exits 0 over the repaired tree | each `scripts/checks/check_web_*.py` and `check_skill_page_contract.py` exits 0 | 4.9, 8.1 |
| SC6 | The checker-derived inventory contains every row #317 names — no #317 row is absent from it | Issue 4.2's assertion passes; any absence is recorded as an instrument defect, not an absent defect | 4.2 |
| SC7 | The plan repaired all 15 path/identifier sites, not the ~4 #317 lists | `check_web_harness_paths.py` exits 0; the inventory records 15 sites repaired | 4.4 |
| SC8 | The plan repaired all five upstream-backend sites including the `.d2` | `check_web_backend_claim.py` exits 0 | 4.5 |
| SC9 | The plan added the `workflows` group to `architecture.d2`, which previously omitted it entirely | `check_web_counts.py` exits 0 over `images/architecture.d2` | 5.1 |
| SC10 | All six diagrams were re-rendered from one pinned d2 version in one commit, with the version recorded | the commit message names the d2 version; all six PNGs are in that commit | 5.3 |
| SC11 | Each regenerated PNG was read by a human and the read recorded | six per-diagram read records exist | 5.4 |
| SC12 | The plan asserted NO byte-equality between regenerated and committed PNGs | no criterion or check compares PNG bytes | 5.5 |
| SC13 | The plan documented `land` as a `plan_manager.py` verb and NOT as a `/yf-plan` slash command | `grep '/yf-plan land' web/content/` returns nothing | 6.1 |
| SC14 | The plan documented the escalation surface as a yf-plan mechanism, not as a `yf-judgement` skill | `grep -r 'yf-judgement' web/content/` returns nothing | 6.2 |
| SC15 | Every Class-B defect is explicitly CLOSED or FILED WITH AN OWNER, enumerated by name — never implied by a green build | Issue 8.2's enumeration lists all six with a disposition each | 8.2 |
| SC16 | The retrospective distinguishes content defects from process defects, with counts | `plan-retrospective.md` carries both counts | 8.3 |
| SC17 | The plan declared which claim classes the mechanical gate does NOT cover | the `not_checked` declaration exists alongside the CHANGE-VALIDATION rows | 2.7 |

