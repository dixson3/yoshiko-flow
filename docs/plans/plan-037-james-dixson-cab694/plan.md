---
type: Plan
okf_spec: OKF-PLAN
id: plan-037-james-dixson-cab694
author: james-dixson
created: '2026-08-13'
status: executing
deliverable_class: standard
fingerprint: c13a0f572818ae81b23436837dcc64974de01a8ceaa348142f815a52a820990c
epic: yf-mol-dh9
---
# Plan: Land the user-scope divergence into the repo (redeploy deferred)

**ID:** plan-037-james-dixson-cab694
**Author:** james-dixson
**Created:** 2026-08-13
**Status:** executing
**Deliverable-class:** standard
**Epic:** yf-mol-dh9
**Fingerprint:** c13a0f572818ae81b23436837dcc64974de01a8ceaa348142f815a52a820990c

## Objective

Bring **the repository** to the state where it already contains everything currently living
only in the operator's user-scope install: upstream the one genuine local patch as a proper
repo change on the current idiom, import the one user-scope-only skill (`yf-herdr`) as
first-class repo content, and fix the review-verdict parsing defect (#116) found while
authoring this plan.

The end state is that `main`, committed and pushed, is a **superset** of the operator's
working setup — so that a later redeploy would reproduce it with nothing lost.

### Scope boundary: this plan does not touch user scope

Every change lands in the repo. `~/.claude/skills/` and `~/.claude/rules/` are **not
modified by this plan at any point**. Refreshing the stale install is a separate,
operator-invoked redeploy that happens *after* this plan completes and is explicitly
requested; this plan's final epic prepares and documents that handoff but does not perform it.

This boundary is the plan's most important structural property. It removes the only
irreversible step, eliminates the self-modification hazard entirely (the plan can no longer
overwrite the skill executing it), and means nothing outside the working tree is at risk.

## Motivation

Local patches were made directly to user-scope skill files while working in other projects,
and a skill (`yf-herdr`) was authored entirely outside the repo. That work is real and in
daily use, but it lives only on one machine: it is absent from `main`, invisible to any other
clone, and silently destroyed by the next `install.sh --force`. Meanwhile the repo has moved
ahead of the install, so the operator is running skills whose behavior no longer matches
their own SPECs.

Concretely, this session drafted its plan using the **stale v0.4.0 `yf-plan` skill**, whose
Pre-flight section still documents `/.state/` gitignore anchors and `.yf-plan.local.json`
config — a layout `main` replaced with the canonical `.yf/<short>/` tree. The skill
describing the process and the repo defining it disagree, and the operator is following the
older one.

Left alone this gets worse in both directions: every repo advance widens the staleness gap,
and every further local patch adds unversioned work that a routine reinstall will silently
revert.

The urgency is one-sided, which is why the repo goes first. The staleness is harmless and
self-correcting — a redeploy fixes it whenever the operator chooses. The *un-upstreamed* work
is neither: `yf-herdr` exists on exactly one machine, uncommitted and unbacked, and any
routine `install.sh --force` destroys it. Getting it into version control is the part that
cannot wait; refreshing the install is the part that can.

## Investigation Findings

Three experiments; full detail in `findings/`.

**The install stamp is noise.** All 19 user-scope `SKILL.md` files differ by exactly one
injected line, `<!-- yf-skills: v=0.4.0 tree=<sha> -->`. Unfiltered comparison reports 19
false positives. After filtering, 22 files genuinely differ.

**21 of those 22 are stale-only, provably.** For each file, every historical version of that
path was searched for a blob matching the user-scope content. All 21 match an exact commit
(dates spanning 2026-06-30 to 2026-07-21, each file's newest version as of ~2026-07-21), so
the install is one coherent snapshot and **no stale-side file hides a local edit**. This is
what authorizes the deferred redeploy to overwrite them without loss — the finding is still
load-bearing even though this plan no longer performs the refresh. (`v=0.4.0` is the Cargo
version, not the `v0.4.0` tag — comparing against the tag yields false "local edit" verdicts.)

**Exactly one genuine local patch exists.** `yf-plan/scripts/plan_manager.py` matches none of
its 11 historical versions; the delta against its closest ancestor is a single 28-line hunk
adding `_bootstrap_layout()` and making `PLANS_DIR` / `INCUBATOR_PARENT` configurable. It is
well-formed but built on the **legacy root-dotfile idiom** the repo already superseded, so
porting it verbatim would add a third config reader on the deprecated surface — re-creating
the exact drift #100 exists to remove. **#100 must therefore land before #107.**

**The `yf-herdr` import is smaller than expected in some places and blocking in others.**
rust-embed takes the whole `skills/` tree and every DRIFT-CHECK edge is glob-scoped, so both
cover a new skill with zero manifest edits. But `yf/src/testdata/install-parity.json` is a
frozen golden enumerating all 18 skills and `parity.rs` asserts against it — a 19th skill
without a fixture update is a test failure. And the skill's `depends-on-skill: [herdr]` points
at a **third-party** skill, while that field means "bare in-repo skill names"; it must become a
prose soft-dep, matching the pattern yf-plan already uses for `yf-change-validation`.

**One question the investigation deliberately did not settle.** The 8 companion rules are
installed as a single concatenated `~/.claude/rules/YOSHIKO_FLOW.md` rather than 8 separate
files, and all 8 sections are stale. Whether the bundling is a deliberate harness choice or
install drift is unresolved. Under the repo-only scope this is now purely a **redeploy-time**
question — it concerns how rules are *installed*, not what the repo's `protocols/*.md` should
contain — so it is out of scope here and belongs to the deferred redeploy. Issue 5.3 records
it in the handoff as a thing to resolve at that point.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|:--|:--|:--|:--|:--|
| #107 | yf-plan: make PLANS_DIR and INCUBATOR_PARENT configurable | include | The local patch. Re-implemented on canonical `.yf/` config, not ported verbatim. | Issue 2.3 |
| #100 | plan_manager.py: align .yf/ layout to canonical short-name + canonical-first config read | include | Hard prerequisite of #107 — supplies the single config reader #107 consumes. | Issue 2.2 |
| #101 | yf-change-validation: read canonical .yf/plan/config.local.json for validate-cmd seed | include | Second consumer of the same reader; leaving it legacy-only re-creates the drift #100 removes. | Issue 2.4 |
| #110 | herdr: leverage `herdr agent *` to launch and monitor agent sessions | partial | **In scope:** the `yf-herdr` skill surface — source, SPEC, parity entry, web page — i.e. delegating an approved plan to a new herdr tab and observing it. **Out of scope:** the `herdr agent *` fan-out primitive itself (coordinator loops dispatching to secondary sessions instead of in-process subagents), which is what #110 actually proposes and which stays open. | Issue 3.7 |
| #116 | yf-plan: red-team template emits `### Verdict:` but ready-check parses `## Verdict:` | include | Found while authoring this plan — reviews written per the template are silently unparseable and `ready-check` reports no verdict at all. Filed and fixed here. | Issue 4.1–4.3 |
| #102 | .markdown-lint-on-edit -> .yf/markdown-lint-on-edit | exclude | Different marker; needs `migrate.rs` code + a gitignore commit-semantics decision. Not user-scope divergence. Its commit-semantics question is *related* to Issue 2.1 and is cross-referenced, not solved. |  |
| #109 | stale_approved computed status-independently | exclude | Unrelated to install reconciliation. |  |

All other open issues were reviewed and are out of scope.

## Approach

Five epics, all repo-only.

**Epic 1 rescues the at-risk work into version control, first.** `yf-herdr` and the local
patch are copied into the repo as reference material before anything else happens, so the
one-machine-only work stops being one-machine-only in the first commit. This is deliberately
the cheapest possible step — a copy, not an integration — because its whole purpose is to
close the window in which the work can be lost. Epic 3 does the real import later.

**Epic 2 upstreams the patch**, SPEC-first, in the order #100 → #107 → #101: establish one
canonical-first config reader, then add configurable roots as its consumer, then fix the
second consumer. The import-time constraint (`PLANS_DIR` is a module constant resolved before
most of the module exists) is the real friction and gets its own issue rather than being
assumed away.

**Epic 3 imports `yf-herdr`**, SPEC-first, ending with the parity fixture and the web page so
the drift-check and parity gates are satisfied in the same change-set that introduces the
skill.

**Epic 4 fixes the review-verdict defect (#116)**, found while authoring this plan: the
red-team template emits `### Verdict:` while the parser matches `## Verdict:`, so a review
written exactly as prescribed is silently unparseable and `ready-check` reports no verdict at
all. It is independent of the other epics and touches only `yf-plan`.

**Epic 5 verifies the repo's final state and prepares the redeploy handoff.** Full validation
over the merged tree, plus a written handoff describing the redeploy the operator will invoke
separately. It **documents** that redeploy; it does not run it.

### Deferred: the user-scope redeploy

Refreshing `~/.claude/skills/` is explicitly **out of this plan**, deferred to an
operator-invoked step after completion. Two consequences worth stating, because they are what
this deferral buys:

- **The self-modification hazard is gone, not mitigated.** An earlier draft had to exclude
  `yf-plan` from a mid-plan refresh so the coordinator would not have `plan_manager.py`
  swapped underneath it while holding `landing.lock`. With no refresh in scope, that whole
  class of problem disappears and no policy is needed.
- **The plan executes on the stale installed `yf-plan` throughout**, including its
  `.yf/yf-plan/` state path. Epic 2 changes the *repo's* manager; the *installed* one is
  untouched until the operator redeploys. This is expected, not a defect.

Ordering: Epic 1 first (it is the risk-closing step). Epics 2, 3, and 4 are mutually
independent and may run in any order or in parallel. Epic 5 depends on all of them.

## Epics

### Epic 1: Rescue the at-risk work into version control

Read-only with respect to user scope: it copies *out of* `~/.claude/`, never into it.

- **Issue 1.1: Copy the divergent artifacts into the plan folder and commit.** Into
  `docs/plans/plan-037-james-dixson-cab694/references/user-scope/`:
  - `plan_manager.py` (the locally patched copy) and `plan_manager.py.pre-incubator-root.bak`
  - the entire `yf-herdr/` directory (`SKILL.md`, `README.md`, `SPEC.md`)

  Verify each copy byte-for-byte against its source, then commit. After this commit the
  one-machine-only work is in git history permanently, and every later step is recoverable.
  This is reference material, not the import — Epic 3 does the real integration.
  - depends-on: —
- **Issue 1.2: Record the isolated `#107` patch as a reviewable diff.** Write the 28-line hunk
  (`plan_manager.py` against its closest ancestor `0b0cc78c`) to
  `references/user-scope/107-local-patch.diff`, so Epic 2 has an exact specification of the
  behavior to re-implement rather than working from the whole stale file.
  - depends-on: 1.1

### Epic 2: Upstream the configurable-roots patch on the canonical idiom

- **Issue 2.1: Decide and record the config-tier semantics.** Settle whether `plans-root` /
  `incubator-root` are a **shared, committed** decision or a **local-only** one. The local
  patch invented a committed `.yf-plan.json` tier, but the canonical `.yf/` tree is entirely
  gitignored, so a committed layout decision has no canonical home today. This is the same
  commit-semantics problem #102 raises for the markdown-lint marker; cross-reference, do not
  solve #102 here. Output: a recorded decision. Blocks 2.2 and 2.3 — the reader's shape depends
  on the answer.
- **Issue 2.2 (#100): SPEC then implement canonical-first config + short-name state.** Land the
  `SPEC.md` / `spec/data.md` / `spec/prerequisites.md` REQ changes first, then change
  `_read_config()` to read `.yf/plan/config.local.json` first with the legacy root dotfile as
  fallback (mirroring `preflight.rs` `read_config`), and `STATE_DIR` to the short name
  `.yf/plan/`. Include migration of existing `.yf/yf-plan/` state. Three `_read_config()` call
  sites (`landing-strategy`, `validate-cmd`, `execute.worktree`) and `LANDING_LOCK`.
  - depends-on: 2.1
  - resolves-upstream: #100 (include)
- **Issue 2.3 (#107): SPEC then implement configurable plan roots as a consumer of that reader.**
  Resolve the import-time constraint explicitly — either hoist a minimal dependency-free reader
  above the constants (what the local patch does, generalized) or make the roots lazily
  resolved; the tradeoff is a wider call-site change for the lazy option. Then express
  `plans-root` / `incubator-root` through the canonical reader. Must preserve the local patch's
  good properties: defaults when unconfigured, malformed JSON tolerated at import.
  - depends-on: 2.2
  - resolves-upstream: #107 (include)
- **Issue 2.4 (#101): Point the change-validation seed at the canonical reader.**
  `change_validation.py:44` (`VALIDATE_CMD_CONFIG`) reads legacy-only; make it canonical-first
  with legacy fallback.
  - depends-on: 2.2
  - resolves-upstream: #101 (include)
- **Issue 2.5: Tier-1 unit tests for config precedence and root configurability.** Cases:
  canonical-only, legacy-only, both-present (canonical wins), neither (defaults), malformed
  JSON at import time, and non-default roots end-to-end through `init`. Tag each against the
  REQ ids from 2.2/2.3.
  - depends-on: 2.3, 2.4
- **Issue 2.6: Tier-2 mechanical drive under a sandboxed `HOME`.** `TESTING.md` requires this
  for manager-script changes and warns explicitly *"never trust the installed copy — it is the
  old, `rust-embed`-baked skill."* That warning is doubly pointed here, since a stale installed
  copy is this plan's whole subject — and under the self-modification policy the installed
  `yf-plan` stays stale for the entire execution. Drive the modified `plan_manager.py` verbs
  directly under a sandboxed `HOME`; do not hand-roll an interactive-agent smoke.
  - depends-on: 2.5

### Epic 3: Import yf-herdr as a first-class repo skill

- **Issue 3.1: SPEC-first — review and land `skills/yf-herdr/SPEC.md`.** Bring the
  hand-authored SPEC to repo discipline before any other import step, per AGENTS.md: renumber
  requirements to the **`REQ-HERDR-*`** prefix (consistent with the other per-skill SPECs) and
  add the living-amendment log.
- **Issue 3.2: Land the skill source with corrected frontmatter.** Copy `SKILL.md` / `README.md`
  into `skills/yf-herdr/`, and **drop `depends-on-skill: [herdr]`** — that field is in-repo
  names only and `herdr` is third-party. Keep `depends-on-tool: [herdr, uv]`. Express the
  relationship as a prose soft-dep, following yf-plan's `yf-change-validation` precedent.
  - depends-on: 3.1
- **Issue 3.3: Update the frozen parity golden.** Hand-edit
  `yf/src/testdata/install-parity.json`: add `yf-herdr` to `skill_group` (→ `utility`), to
  `group_members` / the `group:utility` closure, and give it its own closure entry. Do not run
  the deleted `install.py`. Verify `parity.rs` passes.
  - depends-on: 3.2
- **Issue 3.4: Update the architecture skill counts.** `web/content/pages/architecture.md`:
  18 → 19 skills, utility 6 → 7. Enforced by the `e-web-skill-counts` drift edge.
  - depends-on: 3.2
- **Issue 3.5: Author `web/content/skills/yf-herdr.md`.** Per the plan-036 hybrid convention
  (authored prose body; "At a glance", index, and `SKILL_NAV` stay generated) and VOICE.md.
  - depends-on: 3.2
- **Issue 3.6: Prove the import.** Full lint, 0-warning Pelican build, drift-check PASS over
  the new `skills/yf-herdr/*` and `web/content/skills/yf-herdr.md` glob matches, and `parity.rs`
  green.
  - depends-on: 3.3, 3.4, 3.5
- **Issue 3.7: Write the #110 partial split.** Update #110 to record precisely what this plan
  delivered and what remains: **delivered** — the `yf-herdr` skill surface (delegate an approved
  plan to a new herdr tab, observe it, mine deviations); **still open** — the `herdr agent *`
  fan-out primitive, i.e. coordinator loops dispatching to secondary full sessions instead of
  in-process subagents, which is what #110 actually proposes. Leave #110 **open**.
  - depends-on: 3.6
  - resolves-upstream: #110 (partial)

### Epic 4: Fix the red-team verdict parsing defect (#116)

Independent of Epics 1–3; touches only `yf-plan`.

- **Issue 4.1: SPEC-first — state the verdict-line contract.** Record in `yf-plan`'s spec
  which heading form is canonical and that the parser and the agent template must agree.
  - depends-on: —
- **Issue 4.2: Align template and parser.** Fix `agents/red-team.md` to emit `## Verdict:`
  (matching the parser, its own docstring, and 47 of 49 existing reviews), and relax the regex
  at `plan_manager.py:2766` to `^#{2,3}\s+Verdict:` so the 2 existing `###` reviews become
  parseable and the trap cannot recur.
  - depends-on: 4.1
  - resolves-upstream: #116 (include)
- **Issue 4.3: Make a malformed verdict fail loud.** `ready-check` currently cannot distinguish
  "no review exists" from "a review exists but its verdict did not parse" — it reported
  `review_pass: 2` alongside `verdict: null`, a contradiction it presented as an absent
  verdict. Report that state as a malformed-review error naming the offending file.
  - depends-on: 4.2
- **Issue 4.4: Tests.** Tier-1 cases for `##` and `###` verdict lines, a malformed/absent
  verdict, and the `review_pass > 0 && verdict == null` contradiction. Tag against 4.1's REQ.
  - depends-on: 4.3

### Epic 5: Verify the repo's final state and prepare the redeploy handoff

- **Issue 5.1: Full-tier validation over the merged tree.** Lint, 0-warning Pelican build,
  drift-check PASS, `parity.rs` green, and both TESTING.md tiers.
  - depends-on: Epic 1, Epic 2, Epic 3, Epic 4
- **Issue 5.2: Prove the repo is a superset of user scope.** Re-run the `exp-01` comparison
  (excluding `__pycache__/`, `*.pyc`, `.DS_Store`) in **one direction only**: every artifact
  present in user scope must now have a repo counterpart that is equal-or-newer. The repo
  legitimately contains *more* than user scope at this point — that is the intended end state,
  not drift. **No files are written to user scope.**
  - depends-on: 5.1
- **Issue 5.3: Write the redeploy handoff.** Document, in the plan folder, the exact command
  the operator runs afterward to refresh user scope, what it will change (all 19 skills plus
  the rules surface), and how to verify it — including the two traps this plan discovered: the
  install stamp must be filtered from any comparison, and `__pycache__`/`.DS_Store` excluded.
  Must also record:
  - that the redeploy is the point at which the installed `yf-plan` picks up the `.yf/plan/`
    state path from Epic 2, so it should not run while a plan holds `landing.lock`;
  - the unresolved **rules-bundling question** (concatenated `YOSHIKO_FLOW.md` vs 8 files) as
    something to settle at redeploy time, since it is an install-shape question this plan
    deliberately did not answer.

  **This issue writes a document; it does not run the redeploy.**
  - depends-on: 5.2

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: at-risk work committed to git
- Type: auto
- Condition: the divergent artifacts are committed to the repo, byte-identical to their
  user-scope sources, before any other epic proceeds.
- Test:
  ```bash
  R=docs/plans/plan-037-james-dixson-cab694/references/user-scope
  diff -r "$R/yf-herdr" ~/.claude/skills/yf-herdr \
    && diff "$R/plan_manager.py" ~/.claude/skills/yf-plan/scripts/plan_manager.py \
    && test -f "$R/plan_manager.py.pre-incubator-root.bak" \
    && git ls-files --error-unmatch "$R/yf-herdr/SKILL.md" >/dev/null
  ```
- Blocks: Epics 2, 3, 4
- Instructions: run Issue 1.1 and commit. The `git ls-files` check is the point of the gate —
  copying is not enough; the files must be **tracked**, since untracked copies are no safer
  than the originals.

### Capability Gate: config-tier semantics decided
- Type: human
- Condition: Issue 2.1's committed-vs-local decision is recorded at
  `docs/plans/plan-037-james-dixson-cab694/decisions/config-tier.md`.
- Test: `test -s docs/plans/plan-037-james-dixson-cab694/decisions/config-tier.md`
- Blocks: Issues 2.2, 2.3
- Instructions: settle whether `plans-root` / `incubator-root` are a shared-and-committed or
  local-only decision, and record the choice with its rationale at the path above.

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| Risk | Mitigation |
|:--|:--|
| `yf-herdr` or the local patch is destroyed by an *ambient* `install.sh --force` — not by this plan, which never writes to user scope, but by ordinary use of the machine before Epic 1 lands. | Epic 1 runs **first** and is deliberately trivial (copy + commit), minimizing the exposure window. Its capability gate requires the files be **git-tracked**, not merely copied. |
| The un-upstreamed work is captured but subtly altered in transit (line endings, permissions, partial directory copy). | The gate diffs each artifact byte-for-byte against its live source and recursively for `yf-herdr/`, so a partial or mangled copy fails loudly rather than silently passing. |
| #100's canonical-first change silently breaks operators still on the legacy dotfile. | Legacy stays a read fallback, never removed. Issue 2.5 tests the legacy-only and both-present cases explicitly. |
| The import-time constraint forces a wider refactor than expected, expanding Issue 2.3. | It is called out as the explicit subject of 2.3 with two named options rather than assumed away; the lazy-resolution option's cost (every call site) is known up front. |
| `yf-herdr` depends on a third-party `herdr` binary that CI does not have. | Its `SKILL.md` is gated on `HERDR_ENV=1` and should be inert; `depends-on-tool` declares the requirement. Issue 3.6's FULL-tier run over the merged tree is where this surfaces. Carried as an open risk, not a solved problem. |
| Scope creep from the adjacent `.yf/` issues (#102 and the rest of the canonical migration). | #102 is explicitly excluded; only its commit-semantics *question* is cross-referenced from Issue 2.1. |
| The plan executes on the stale installed `yf-plan`, so nothing Epic 2 or Epic 4 fixes is available during execution (including the stale `.yf/yf-plan/` state path). | Expected and harmless under the repo-only scope: Epic 2 changes the repo's manager, the installed one is untouched until the operator redeploys. Recorded here so it is not mistaken for a defect mid-execution. |
| Epic 4 edits `plan_manager.py` and `agents/red-team.md` — the verdict machinery — while this plan's own reviews depend on it. | The edit lands in the **repo**; the executing session keeps using the installed copy, so no review can be invalidated mid-flight. Issue 4.4's tests are the check, not this plan's own reviews. |
| Deferring the redeploy means the operator keeps running stale skills indefinitely if the follow-up never happens. | Issue 5.3 leaves a written, ready-to-run handoff in the plan folder rather than relying on recall. The deferral is a sequencing choice, not an abandonment. |

## Success Criteria

1. **`main` is a superset of the operator's working setup**, committed and pushed. Measured by
   Issue 5.2: every artifact present in user scope has a repo counterpart that is
   equal-or-newer (comparison excludes `__pycache__/`, `*.pyc`, `.DS_Store`). The repo
   containing *more* than user scope is the intended end state.
2. Configurable `plans-root` / `incubator-root` is a **repo feature** reachable through
   canonical `.yf/` config — so the hand-edit in user scope is now redundant rather than load-
   bearing, and a later redeploy would overwrite it losing nothing.
3. `yf-herdr` installs from the repo like any other skill: present in `skills/`, in the parity
   golden, counted in `architecture.md`, with an authored web page.
4. #107, #100, #101, and #116 are closed. #110 stays **open**, updated per Issue 3.7 with an
   explicit in/out split: skill surface delivered, `herdr agent *` fan-out primitive still open.
5. Full lint, 0-warning Pelican build, drift-check PASS, `parity.rs` green, and both TESTING.md
   tiers (Tier-1 unit + Tier-2 sandboxed-`HOME` drive) green over the merged tree.
6. One coarse upstream tracking issue for this plan (#115), per the AGENTS.md convention.
7. A review written per the corrected red-team template parses correctly — `ready-check`
   returns the verdict rather than `verdict: null`, and a malformed verdict now fails loud.
8. The redeploy handoff (Issue 5.3) is written and ready to run, and **no user-scope file was
   modified by this plan**.
