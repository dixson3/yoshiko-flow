---
type: Plan
okf_spec: OKF-PLAN
description: 'Release yf 0.6.0: yf doctor warns (not errors) on missing optional-skill
  tools such as herdr, beads gate-lock exclusion (yf-htws), yf-research fixes #410
  #411 #412'
id: plan-073-james-dixson-cc76de
author: james-dixson
created: '2026-10-15'
status: approved
deliverable_class: standard
fingerprint: c11fa7375e7e37ef713013ea3f4c7c31d579787c38e888920c5bf695500b6070
---
# Plan: Release yf 0.6.0: yf doctor warns (not errors) on missing optional-skill tools such as herdr, beads gate-lock exclusion (yf-htws), yf-research fixes #410 #411 #412

**ID:** plan-073-james-dixson-cc76de
**Author:** james-dixson
**Created:** 2026-10-15
**Status:** approved
**Deliverable-class:** standard
**Fingerprint:** c11fa7375e7e37ef713013ea3f4c7c31d579787c38e888920c5bf695500b6070

## Objective

Prepare **yf v0.6.0** for release from the tip of `main`. It carries everything since `v0.5.0`
(`1eba35d`, plans 055–072) plus five fixes, chosen because a new user hits each of them:

1. **`yf doctor` is green for anyone with `bd`, `uv` and `git`.** A new per-skill
   **`optional-tool:`** frontmatter key makes a missing optional tool a doctor *warning*, not a
   failure. `herdr` (yf-herdr), `pandoc` (yf-markdown-html, yf-markdown-pdf), `xelatex`
   (yf-markdown-pdf) and `d2` (yf-diagram-authoring) move to it.
2. **yf-htws:** the yf beads kernel tops up the project `.gitignore` with `/.beads.gate.lock`, and
   verify reports the file when it is untracked and unignored. bd ≥ 1.3 recreates it at the repo
   root on every call.
3. **#410:** `sources.json` becomes the single evidence store for quotes, via a per-source
   `quotes: []` array. A deterministic `check-quotes` verifies them, and the red-team uses its
   output.
4. **#411:** `sources.md` is built at the end of synthesize, so citation anchors resolve before
   critique.
5. **#412 (partial):** preprint servers score Tier 4 by default, and the `.dev` Tier-2 heuristic
   no longer promotes package registries or issue mirrors.

**The plan ends at a releasable `main`**: version 0.6.0, CHANGELOG written, and the landing's L3
FULL tier green on the merged tree. **Pushing the `v0.6.0` tag is a post-landing operator act,
not a bead** (see Approach → Release); `log.md` and `assets/` record it.

## Motivation

**v0.5.0 ships a `yf doctor` that fails for most users.** REQ-YF-DOCTOR-005 makes every declared
`depends-on-tool` that is missing from `PATH` a **required failure**, across every *embedded*
skill, not only installed ones.
- **Measured (red-team pass 1, sandbox):** with `herdr`, `d2`, `pandoc` and `xelatex` off
  `PATH`, `yf doctor --json` exits 1 on **four** axes: `skill-deps:yf-herdr`,
  `skill-deps:yf-diagram-authoring`, `skill-deps:yf-markdown-html` and
  `skill-deps:yf-markdown-pdf`.
- **These are optional tools.** Each one serves a single opt-in skill, and each of those skills
  already fails closed when its tool is absent. yf-markdown-html and yf-markdown-pdf have
  `check_deps()` (REQ-MDHTML-005, REQ-MDPDF-003); `render.py preflight` reports d2 missing; and
  yf-herdr is inert without `HERDR_ENV=1` (REQ-HERDR-041).
- **yf-plan and yf-research are not affected.** A read-only audit on 2026-10-15 found them not
  over-dependent on herdr: every herdr path is gated and has a working default.

**v0.5.0's yf-research gives wrong answers on every run.**
- **#411:** the red-team runs before the packager generates `sources.md`, so it reports every
  `[ID](sources.md#id)` citation as a broken link.
- **#410:** the red-team checks quotes against `sources.json`, which holds one `quote` per
  source, while the synthesizer quotes from cluster artifacts. In research 070 that produced 44
  of 71 false "untraceable quote" [high] findings, although 69 of the 71 quotes were verbatim in
  `artifacts/cluster-*.md`.
- **#412:** `credibility_scorer.py` scores `arxiv.org` at Tier 1, while the triangulator rubric
  puts preprints at Tier 4. Its `.dev` heuristic also scores third-party registries and mirrors
  (`pi.dev/packages/*`, `upd.dev`) at Tier 2.

**yf-htws:** bd 1.3.1 recreates `.beads.gate.lock` at the repo root on every call, and the
kernel's gitignore set (`PROJECT_GITIGNORE`, `yf/src/beads_init.rs:49`) does not cover it. The
untracked file blocked plan-072's landing (`primary-checkout-dirty-outside-plan-dir`) while
`yf preflight yf-beads-init` reported `ok`.

**Why now:** v0.5.0 was tagged at `1eba35d` on 2026-10-15, with 391 commits already past it.
0.6.0 publishes that work, and these fixes are the ones a first-run user meets.

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|
| #410 | yf-research red-team quote check reads only sources.json | include | Operator chose option 1: a `quotes[]` evidence store | 0.4, 3.1, 3.2, 3.3 |
| #411 | yf-research red-team runs before packager generates sources.md | include | Operator chose option 1: build `sources.md` at synthesize | 0.5, 3.4 |
| #412 | yf-research credibility_scorer over-scores arXiv and .dev | partial | Operator scoped two of three parts: preprints → Tier 4, and a restricted `.dev` bump. The **undated-source currency** part is out of scope, so #412 stays OPEN | 0.6, 3.5 |
| #442 | plan-073-james-dixson-cc76de execution tracking | tracker | Coarse tracker (https://github.com/dixson3/yoshiko-flow/issues/442), filed at intake | - |
| #255 | Cut the v0.5.0 release | exclude | Closed 2026-10-15; the release precedent this plan's post-landing tag follows | - |
| #302 | plan-number collisions across checkouts | exclude | Context only. plan-073's number was allocated past a placeholder (`log.md`) | - |

## Investigation Findings

No `findings/` experiments were run. Every fact below was read or measured against the
2026-10-15 tree, during scoping or by red-team pass 1 (`reviews/pass-1.md`, which records the
measurements).

- **Doctor severity model exists.**
  - `CheckResult::warn` (`yf/src/cmd/doctor/check.rs:56`) returns `required: false`.
  - `is_failure()` counts only `required && !ok`.
  - `SkillDepsCheck` (`checks.rs:352-378`) only needs to emit `warn` for optional tools.
- **Preflight never enforced herdr, pandoc, xelatex or d2** (pass-1 C1, measured).
  - `check_system_deps` (`preflight.rs:597-634`) probes only `git`, `uv` and `bd`.
  - `yf preflight yf-herdr` with herdr off `PATH` returns `status: ok`.
  - yf-herdr's inertness comes from its own prose preflight, not from `yf preflight`.
    `HERDR_ENV=1` is the trigger precondition (REQ-HERDR-041), and `command -v herdr`
    (`skills/yf-herdr/SKILL.md:37`) is its fail-closed tool check (pass-2 C4).
  - So `optional-tool` needs **no preflight change**: preflight's behaviour is preserved by
    leaving it alone.
- **`depends-on-tool` consumers.** Found with `grep -rl depends-on-tool`, excluding history:
  - Rust: `frontmatter.rs` (`tools`); `cmd/common.rs:80` (the install missing-tools notice and
    the `--strict` abort); `preflight.rs:468-473` (reads `tools`, but probes only git/uv/bd).
  - Python checks: `scripts/checks/check_skill_readme_contract.py` (REQ-YF-DOC-007) and
    `scripts/checks/check_required_set.py` (the generated "At a glance" data).
  - Web: `web/plugins/skill_model.py`, `skill_pages.py` and `skill_diagrams.py`.
  - Generator: `yf/src/testdata/gen-install-parity.py`.
  - The `_shared/test_doc_lint.py` and `tests/fixtures/doclint/skill/*.md` fixtures only use the
    key as sample text.
- **Four SPEC and four README literals name the current `depends-on-tool` posture** (pass-2
  C1, C2).
  - **REQ-HERDR-040** (`skills/yf-herdr/SPEC.md:218`) says the frontmatter "**shall** declare
    [herdr] under `depends-on-tool`". It is normative, so it is amended in Epic 0.
  - **Descriptive literals:** the dependency-posture paragraphs at
    `skills/yf-diagram-authoring/SPEC.md:93`, `skills/yf-markdown-html/SPEC.md:100` and
    `skills/yf-markdown-pdf/SPEC.md:130` quote the literal.
  - **README lines:** each README has a "Mirrors SKILL.md frontmatter `depends-on-tool: […]`"
    line (`README.md:89` in the three, `yf-herdr/README.md:33`).
  - All of them change with Issue 1.4. The SPEC ones are amended first (Epic 0, SPEC-first),
    and the README ones in Issue 1.6.
- **`render.py` fail-closed coverage is partial** (pass-2 C4). Its tool-invoking subcommands
  (`render`, `render-dir`, `preflight`) return 1 without d2. `test_render.py` skips every d2
  test when `HAS_D2` is false, so nothing tests the missing-d2 path. Issue 1.4 adds that test.
- **Agent Skills frontmatter tolerance.** `depends-on-tool` and `skill-group` are already custom
  keys that pi and claude-code accept. REQ-YF-EMBED-007 constrains only `name` and
  `description`. So `optional-tool` is the same class of key; SC13 checks that `check_frontmatter`
  stays clean.
- **yf-htws reaches only repaired repos unless verify reports it** (pass-1 C7).
  `PROJECT_GITIGNORE` is used only by repair (`beads_init.rs:903`). Verify has an advisory
  hygiene block (`beads_init.rs:294`) that already reports `.beads` perms the same way.
- **#411 is a one-step fix.** `link_normalizer.py all` already exists and is idempotent
  (`agents/packager.md` step 4).
- **#410 schema impact.**
  - `render_sources_md` (`link_normalizer.py:86-135`) renders one `- **Quote:**` per source.
  - REQ-DATA-003 (`spec/data.md:15`) defines `sources.json`.
  - The legacy single `quote` stays readable.
- **#412 needs path-aware matching** (pass-1 C8).
  - `_domain_authority_score` matches tiers against **netloc only**, so an entry like
    `osf.io/preprints` never matches (measured: scored 30, the unknown fallback).
  - `arxiv.org` is in `TIER_1_DOMAINS` (`credibility_scorer.py:29`), and the `.dev` bump is at
    `:91`.
  - REQ-RESEARCH-024(b) currently mandates the `.dev` bump.
  - `test_credibility_scorer.py:102-103` asserts arXiv ≥ 85.
- **`cargo test <filter>` passes vacuously on zero matches** (pass-1 C3; the
  `CHANGE-VALIDATION.md:71-72` note). Every criterion that names a cargo test also asserts the
  test's presence with `cargo test -p yf -- --list | grep -q '<path>: test'`. The form was
  verified against the existing `beads_init::tests::ensure_gitignore_idempotent: test`.
- **Release mechanics (precedent: plan-054 Epic 6, #255, the v0.5.0 recovery).**
  - Version literals: `yf/Cargo.toml`, `Cargo.lock`, `CHANGELOG.md`, and `web/pelicanconf.py`
    (`YOSHIKOFLOW_RELEASE`).
  - Pushing a `v<semver>` tag runs cargo-dist `release.yml`: GitHub release, then the Homebrew
    tap, then `web-deploy.yml`.
  - **The tag must be on `main`'s tip.** A target commit whose `.github/workflows/` differs
    from `main` makes `gh release create` return 403 under `GITHUB_TOKEN` (measured on v0.5.0,
    run 38823048819).
  - **Landing L3 already runs the FULL tier on the merged tree** (`spec/landing.md`), and L4
    commits that tree as the merge commit. Later commits on `main` exist before any tag: L16's
    plan-folder commit, the post-landing authorization record, and possibly other plans' work
    (pass-2 C5). So the tag is valid only if everything after the L4 merge commit is
    plan-folder bookkeeping. The post-landing preconditions assert exactly that (Approach →
    Release). No separate 5-hour run is needed (pass-1 C10).
  - **Bead closure vs. landing** (pass-1 C2). Landing's close chain (L9 reconcile, L12 cascade,
    L13 complete-gate) requires every plan bead terminal. A tag bead that needs the plan landed
    first therefore deadlocks it, the shape plan-054 hit and descoped (#255).

## Approach

**SPEC first (Epic 0), then code against tagged tests (Epics 1–3), then docs (Epic 4), then the
version bump (Epic 5), then landing. The tag is a post-landing operator act.**

**Doctor: `optional-tool:`.** The operator chose an explicit per-skill key over "only bd/uv/git
fail" and over "the whole axis warns". Red-team pass 1 measured that herdr alone does not fix
doctor for new users, so the operator extended the key to `pandoc`, `xelatex` and `d2`.
- **Doctor:** a missing optional tool is reported as `warn` (`required: false`, exit
  unaffected), with the install hint in its detail.
- **Install:** the missing-tools notice lists optional tools separately, and `--strict` aborts
  only on required ones.
- **Preflight:** **unchanged.** It never probed these tools.

Resulting frontmatter:

| Skill | `depends-on-tool` | `optional-tool` |
| :-- | :-- | :-- |
| yf-herdr | `[uv]` | `[herdr]` |
| yf-markdown-html | `[uv]` | `[pandoc]` |
| yf-markdown-pdf | `[uv]` | `[pandoc, xelatex]` |
| yf-diagram-authoring | `[uv]` | `[d2]` |

yf-diagram-authoring currently declares `[d2]` only, but `render.py` runs via `uv run`
(`skills/yf-diagram-authoring/SPEC.md:89`), so it gains `uv` (pass-2 C10).

**yf-htws.**
- **Repair:** add `/.beads.gate.lock` to `PROJECT_GITIGNORE`. The `ensure_gitignore` top-up is
  already idempotent.
- **Verify:** gains an advisory diagnostic in its hygiene block when the file exists, is
  untracked, and is not ignored (`git check-ignore` fails). The remediation names `yf doctor
  --repair`, and status does not change.
- **This repo:** already carries the line (`31d83e5`).

**#410: one evidence store.**
- **Retriever:** records every passage it blockquotes into the source's `quotes: []`, keeping the
  legacy `quote` as entry 0.
- **Triangulator:** appends any new passage it quotes.
- **Synthesizer:** blockquotes only passages in `quotes[]`.
- **Checker:** `link_normalizer.py check-quotes <topic_dir>` is deterministic. It extracts each
  `> "…" [ID](…)` blockquote, normalizes it (Unicode quotes and dashes, emphasis markers,
  whitespace, split on `...`), and requires every fragment in that source's `quotes[]`.
- **Red-team:** check 4 is that command's output, verbatim.

**#411.**
- Synthesize ends with `link_normalizer.py all`. The packager re-runs it, which is idempotent.
- The red-team's context lists `sources.md` and states that anchors are expected to resolve.

**#412.**
- **Path-aware tier matching:** a tier entry containing `/` matches `netloc + path` by prefix;
  bare entries match netloc as today.
- **Preprints:** `arxiv.org`, `biorxiv.org`, `medrxiv.org`, `ssrn.com` and `osf.io/preprints`
  move to Tier 4. `--peer-reviewed` (`score`) or `peer_reviewed: true` (`batch`) restores Tier 1.
- **`.dev` bump:** keeps `docs.*` hosts. A `.dev` host qualifies only if its path matches none
  of `/packages/`, `/package/` or `/issues/`. `upd.dev` is listed in Tier 4.
- **Undated currency:** out of scope, and #412 stays open.

**Release (Epic 5, then post-landing).**
- **Epic 5 (in plan):**
  - Bump to `0.6.0` in `yf/Cargo.toml`, `Cargo.lock` and `web/pelicanconf.py`.
  - Write the CHANGELOG `## v0.6.0` section, grouped by theme. Every existing plan 055–073 is
    cited at least once; the v0.5.0 precedent cites cross-theme plans more than once (pass-1
    C11).
  - The section carries a **Known limitations** list, including #412's open currency part.
- **Validation:** the **landing's L3 FULL tier on the merged tree is the release validation.**
  `land --apply` halts on red or INCONCLUSIVE, so a landed plan-073 *is* a green-validated
  `main`.
- **Tracked across the boundary** (pass-2 C6). Issue 5.2 creates a standalone follow-on bead,
  "Cut v0.6.0: tag + verify", outside the plan subtree. It carries the procedure below and
  stays open after `complete`. Landing L17's residual mirroring pushes it upstream as the
  release tracker, the #255 role.
- **Post-landing (operator act, not a plan bead):**
  - The operator authorizes in conversation. The main session records the authorization in
    `assets/release-authorization.md`: who, when, the `origin/main` sha, and the **L4 merge
    sha**, read from the landing journal or `git log --merges`.
  - Preconditions:
    - `git rev-parse HEAD` equals `origin/main`.
    - `git diff --quiet origin/main HEAD -- .github/workflows`.
    - **Everything after the L3-validated merge is plan-folder bookkeeping** (pass-2 C5):
      `git diff --quiet <L4-merge-sha> HEAD -- . ':(exclude)docs/plans/'`. If this fails,
      another change has landed since validation. Re-run the FULL tier on `HEAD` before
      tagging.
  - Tag `v0.6.0` on `main`'s tip and push it.
  - Verify the GitHub release asset set, the tap formula `0.6.0`, the site and `install.sh` at
    `0.6.0`, and that a re-downloaded tarball's sha256 matches.
  - Record the results in `assets/release-verification.md` and in a `log.md` bullet.
  - The pattern is v0.5.0's (#255), with the tip-of-`main` rule that avoids the 403.

### Out of scope

- #412's undated-source currency.
- #275 (yf-herdr launch contract).
- The yf-plan P0 bugs.
- `yf doctor` scoping its skill-deps axis to *installed* skills. With `optional-tool` covering
  every non-core tool, embedded-skill checking no longer fails anyone, and narrowing the scan is
  a separate design change.
- Preflight enforcement of optional tools.

## Epics

### Epic 0: SPEC amendments (SPEC-first)

- Issue 0.1: Amend `REQ-YF-DOCTOR-005` and add `REQ-YF-DOCTOR-008` in `SPEC.md`.
  - **REQ-YF-DOCTOR-005 (amended):** a declared `depends-on-tool` missing from `PATH` stays a
    required failure. A tool declared in **`optional-tool`** and missing from `PATH` is reported
    on the same `skill-deps:<skill>` axis as a **warning** (`required: false`, exit unaffected)
    with the same install hint. If both kinds are missing, the verdict is the failure, and its
    detail names both.
  - **REQ-YF-DOCTOR-008 (new):** the `optional-tool` frontmatter contract.
    - It lists PATH tools that the skill needs only for its own opt-in operation, not for `yf`
      or the core workflow to be healthy.
    - `yf skills install` lists missing optional tools as optional, and `--strict` does not
      abort on them.
    - `yf preflight` is **unaffected**: it probes only git, uv and bd.
    - In a skill that declares an optional tool, **every operation that invokes the tool shall
      exit non-zero, with a message naming the tool, when it is absent**. Operations that never
      invoke it are unaffected.
    - A tool listed in both keys is a frontmatter error, rejected by
      `scripts/check_frontmatter.py`.
  - **Amendment log:** a `plan-073` entry in the living log, naming both ids.
- Issue 0.2: Amend `REQ-YF-DOC-007` in `SPEC.md`.
  - README **Prerequisites** shall be a superset of `depends-on-tool ∪ optional-tool`.
  - Each optional tool is marked by the literal token **`(optional)`** on the line that names
    it, in a table cell or in prose (pass-2 C11).
  - Add a bullet to the `plan-073` entry.
- Issue 0.7: Amend the per-skill SPEC dependency posture for the four skills (pass-2 C1, C2).
  - **REQ-HERDR-040** (`skills/yf-herdr/SPEC.md:218`): herdr is declared under `optional-tool`,
    never `depends-on-skill`, and `uv` under `depends-on-tool`. Add a `plan-073` bullet to
    `skills/yf-herdr/SPEC.md`'s amendment log.
  - **Descriptive dependency-posture literals:** update `skills/yf-diagram-authoring/SPEC.md:93`
    (`depends-on-tool: [uv]`, `optional-tool: [d2]`), `skills/yf-markdown-html/SPEC.md:100` and
    `skills/yf-markdown-pdf/SPEC.md:130`.
  - Name REQ-HERDR-040 in the root `plan-073` entry in `SPEC.md` too.
- Issue 0.3: Add `REQ-BINIT-028` to `skills/yf-beads-init/SPEC.md`.
  - Repair's project-`.gitignore` top-up set includes `/.beads.gate.lock`, the bd ≥ 1.3 runtime
    gate lock recreated at the repo root on every call.
  - Verify reports an advisory diagnostic when the file exists untracked and unignored. The
    diagnostic's remediation is `yf doctor --repair`; status does not change.
  - Add a bullet to the `plan-073` entry in `SPEC.md`.
- Issue 0.4: Add `REQ-RESEARCH-025` to `skills/yf-research/SPEC.md` (#410).
  - Every blockquoted passage in `Summary.md` and `artifacts/*.md` shall appear verbatim, under
    the documented normalization, in its cited source's `sources.json` `quotes[]`.
  - The retriever and triangulator write `quotes[]`, and the synthesizer quotes only from it.
  - `link_normalizer.py check-quotes` is the verifier and the red-team's basis.
  - A legacy single `quote` counts as a one-element `quotes[]`.
  - Amend REQ-DATA-003 in `spec/data.md` to define `quotes[]`.
  - Add a bullet to the `plan-073` entry in `SPEC.md`.
- Issue 0.5: Add `REQ-RESEARCH-026` to `skills/yf-research/SPEC.md` (#411).
  - The synthesize step ends by running `link_normalizer.py all`, so `sources.md` exists and
    every `[ID](sources.md#id)` anchor resolves before critique.
  - The packager's run stays and is idempotent.
  - Add a bullet to the `plan-073` entry.
- Issue 0.6: Amend `REQ-RESEARCH-024` and add `REQ-RESEARCH-027` in
  `skills/yf-research/SPEC.md` (#412).
  - **REQ-RESEARCH-024(b) (amended):** the `.dev` heuristic applies only when the URL path
    matches no registry or mirror pattern (`/packages/`, `/package/`, `/issues/`). A tier entry
    containing `/` matches `netloc + path` by prefix.
  - **REQ-RESEARCH-027 (new):** preprint servers (`arxiv.org`, `biorxiv.org`, `medrxiv.org`,
    `ssrn.com`, `osf.io/preprints`) score Tier 4 by default. `--peer-reviewed` (`score`) or
    `peer_reviewed: true` (`batch`) restores Tier 1.
  - Add a bullet to the `plan-073` entry.

### Epic 1: `optional-tool` (Rust, checks, frontmatter)

- Issue 1.1: Add `optional-tool:` support in the parser and the frontmatter guard.
  - **Parser:** parse it in `yf/src/frontmatter.rs` into `Frontmatter.optional_tools`, with the
    same list grammar as `depends-on-tool`. Unit tests are tagged `REQ-YF-DOCTOR-008` and named
    with the `optional_tool` prefix.
  - **Guard:** `scripts/check_frontmatter.py` rejects a tool listed in both keys. The negative
    control is a test named `test_optional_tool_overlap_rejected`, tagged `REQ-YF-DOCTOR-008`,
    in `scripts/test_check_frontmatter.py`.
  - depends-on: 0.1
- Issue 1.2: `SkillDepsCheck` (`yf/src/cmd/doctor/checks.rs`).
  - A missing required tool is still `fail`, and a missing optional tool is `warn`. If both
    kinds are missing, the verdict is `fail` and its detail names both.
  - Registration (`checks.rs:803`) fires when either list is non-empty.
  - Tests, tagged `REQ-YF-DOCTOR-005`, in `checks.rs`'s test module:
    - `skill_deps_optional_missing_is_warning`: optional-only missing gives `warn` and
      `is_failure() == false`.
    - `skill_deps_required_and_optional_missing_fails`.
    - `skill_deps_all_present_with_optional_ok`: all declared tools present, optional ones included, gives `ok`. The existing `skill_deps_all_present_is_ok` (`checks.rs:1700`) covers the empty declared set (pass-3 note).
  - depends-on: 1.1
- Issue 1.3: Install (`yf/src/cmd/common.rs` `missing_tools`, `install.rs:143-158`).
  - Return required and optional tools separately. The notice lists optional tools as optional,
    and `--strict` aborts only on required ones.
  - Test `strict_ignores_optional_tools`, tagged `REQ-YF-DOCTOR-008`, in the `#[cfg(test)]`
    module of `yf/src/cmd/common.rs`, so it lists as `cmd::common::tests::…` (pass-2 C8).
  - No preflight change (REQ-YF-DOCTOR-008).
  - depends-on: 1.1
- Issue 1.4: Move the four tools in frontmatter, per the Approach table.
  - Edit `skills/yf-herdr/SKILL.md`, `skills/yf-markdown-html/SKILL.md`,
    `skills/yf-markdown-pdf/SKILL.md` and `skills/yf-diagram-authoring/SKILL.md`.
  - Update each SKILL.md's prose where it names its hard tool requirement (e.g. yf-herdr's "the
    hard requirement is the tool" paragraph).
  - **Fail-closed checks (REQ-YF-DOCTOR-008):**
    - md2html and md2pdf already have tested `check_deps()`.
    - yf-herdr checks `command -v herdr` (`SKILL.md:37`).
    - yf-diagram-authoring gets a new test, `test_render_fails_closed_without_d2`, in
      `skills/yf-diagram-authoring/scripts/test_render.py`, tagged `REQ-YF-DOCTOR-008`. It runs
      `render.py render` with `PATH` emptied of d2, asserts a non-zero exit and a message
      naming `d2`, and does not skip on `HAS_D2`.
  - depends-on: 1.2, 1.3, 0.7
- Issue 1.5: End-to-end doctor test `doctor_green_without_optional_tools`, tagged
  `REQ-YF-DOCTOR-005`, in `yf/tests/`.
  - Run the built `yf doctor --json` with a `PATH` that holds only `bd`, `uv` and `git` shims,
    in a sandbox HOME with the embedded skill tree installed.
  - Assert that no `skill-deps:*` axis is a failure, that the four optional axes are warnings,
    and that doctor's exit is unaffected by them.
  - depends-on: 1.4
- Issue 1.6: Teach the non-Rust consumers the key.
  - **`check_skill_readme_contract.py`:** Prerequisites ⊇ `depends-on-tool ∪ optional-tool`,
    and optional tools must be marked optional. Negative-control test
    `test_optional_tool_must_be_marked_optional` in
    `scripts/checks/test_check_skill_readme_contract.py`.
  - **`check_required_set.py`:** the "At a glance" block carries optional tools.
  - **Web plugins** (`web/plugins/skill_model.py`, `skill_pages.py`, `skill_diagrams.py`):
    render optional tools labelled as optional.
  - **`yf/src/testdata/gen-install-parity.py`:** regenerate its output if it reads
    `depends-on-tool`.
  - **The four skills' README Prerequisites, in the same change-set as the checker** (pass-2
    C3):
    - Each optional tool gets the `(optional)` token.
    - The "Mirrors SKILL.md frontmatter `depends-on-tool: […]`" lines (`README.md:89` in
      yf-diagram-authoring, yf-markdown-html and yf-markdown-pdf, and `yf-herdr/README.md:33`)
      name both keys.
    - yf-diagram-authoring's Prerequisites table gains `uv`.
    - Doing this here keeps the FAST tier's `skill-readme-contract` row green at every
      commit.
  - Tests are tagged `REQ-YF-DOC-007`.
  - depends-on: 0.2, 1.4

### Epic 2: beads gate-lock (yf-htws)

- Issue 2.1: Repair and verify changes in `yf/src/beads_init.rs`.
  - Add `"/.beads.gate.lock"` to `PROJECT_GITIGNORE` (`:49`), and extend
    `ensure_gitignore_idempotent` to assert the line is added once.
  - Add the verify advisory in the hygiene block (`:294`), with test
    `verify_reports_unignored_gate_lock`. It covers both cases: diagnostic present when the file
    is untracked and unignored, absent when it is ignored. Tagged `REQ-BINIT-028`.
  - Close bead `yf-htws` with the commit.
  - depends-on: 0.3

### Epic 3: yf-research evidence and scoring (#410, #411, #412)

- Issue 3.1: `skills/yf-research/scripts/link_normalizer.py`.
  - `load_sources` normalizes a legacy `quote` into `quotes`, and `render_sources_md` renders
    every quote.
  - New `check-quotes <topic_dir>`. Exit codes: 0 all traced; 1 any untraced, each listed with
    its id; 2 inputs unreadable.
  - Tests in `test_link_normalizer.py`, tagged `REQ-RESEARCH-025`:
    - `test_check_quotes_traced`;
    - `test_check_quotes_untraced_reports_id`;
    - `test_legacy_quote_normalized`;
    - `test_check_quotes_ellipsis_split`.
  - depends-on: 0.4
- Issue 3.2: Agent briefs for #410.
  - `agents/retriever.md`, step 4: write every passage that step 5 blockquotes into
    `quotes[]`.
  - `agents/triangulator.md`: append any new passage it quotes.
  - `agents/synthesizer.md`, rule 3: only passages in `quotes[]`.
  - `agents/red-team.md`, check 4: run `link_normalizer.py check-quotes` and report its output
    verbatim.
  - depends-on: 3.1
  - resolves-upstream: #410 (include)
- Issue 3.3: Amend `skills/yf-research/spec/data.md` REQ-DATA-003 to define `quotes[]`, with
  legacy `quote` accepted. Update any `sources.json` example in the specs or README.
  - depends-on: 0.4
- Issue 3.4: #411 changes.
  - `formulas/yf-research.formula.toml`: the synthesize step's description adds
    `link_normalizer.py all` as its final action.
  - `agents/synthesizer.md`: add the same action as its final instruction.
  - `agents/red-team.md` `## Context`: add `sources.md`, and state that anchors are expected to
    resolve.
  - `agents/packager.md` step 4: note that it is a re-run.
  - Test `test_all_idempotent` (a second run is byte-identical), tagged `REQ-RESEARCH-026`, in
    `test_link_normalizer.py`.
  - depends-on: 0.5
  - resolves-upstream: #411 (include)
- Issue 3.5: #412 changes in `credibility_scorer.py`.
  - Path-aware tier matching. Preprint hosts and `upd.dev` move to Tier 4, the `.dev` path
    denylist is added, and `--peer-reviewed` / `peer_reviewed` restores Tier 1.
  - In `test_credibility_scorer.py`, tagged `REQ-RESEARCH-027` / `REQ-RESEARCH-024`:
    - invert the arXiv ≥ 85 test;
    - add `test_preprint_tier4`, `test_osf_preprints_path_match`,
      `test_peer_reviewed_restores_tier1`, `test_dev_registry_not_tier2` (`pi.dev/packages/x`,
      `upd.dev/...`) and `test_dev_docs_stays_tier2`.
  - Note preprints and `--peer-reviewed` in the `agents/triangulator.md` rubric.
  - depends-on: 0.6
  - resolves-upstream: #412 (partial)

### Epic 4: documentation

- Issue 4.1: Docs for `optional-tool`.
  - Root `README.md` (line 29 and the per-skill prerequisite mentions): herdr, pandoc, xelatex
    and d2 are **optional**. The four skill READMEs were already updated in 1.6.
  - `skills/yf-skill-authoring/SKILL.md` documents `optional-tool` and when to use it instead of
    `depends-on-tool`.
  - `web/content/pages/install.md`.
  - Run `yf-drift-check` over the touched edges; reported drift FAILs this issue.
  - depends-on: 1.6
- Issue 4.2: `skills/yf-research/README.md`: the evidence store, `sources.md` at synthesize, and
  the scorer tiers with `--peer-reviewed`.
  - depends-on: 3.2, 3.4, 3.5

### Epic 5: version bump (releasable `main`)

- Issue 5.1: One change-set covering the version bump and CHANGELOG.
  - **Version:** `yf/Cargo.toml`, `Cargo.lock` (refreshed by a build), and `web/pelicanconf.py`
    (`YOSHIKOFLOW_RELEASE = "v0.6.0"`).
  - **CHANGELOG:** a `## v0.6.0 — <date>` section in `CHANGELOG.md`, grouped by theme, citing
    at least once every plan 055–071 whose `plan.md` status is `complete`, plus plan-072 and
    plan-073. A plan not `complete` (today, plan-069 in `scoping`) is not cited, because it
    shipped nothing (pass-3 C1).
  - **Known limitations** in that section:
    - #412's undated-source currency is still open.
    - yf-htws reaches existing repos via `yf doctor --repair`; verify only reports it.
  - **Not changed:** the `0.5.0` literals in `yf/src/marker.rs` tests and the plan-054 SPEC log
    are fixtures and history, so they stay.
  - **No new REQ**: version literals and release notes change no behaviour.
  - depends-on: 1.5, 1.6, 2.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2
- Issue 5.2: Create the release follow-on bead (pass-2 C6).
  - **Title:** "Cut v0.6.0: tag + verify". Use `bd create -t task`, linked `discovered-from` the
    plan epic and **not** parented under it, so the plan's close chain does not wait on it.
  - **Body:**
    - Approach → Release's post-landing procedure verbatim: authorization record, the three
      preconditions including the L4-merge plan-folder-only diff, tag, publication checks,
      `assets/release-verification.md`.
    - A pointer to `assets/release-authorization.md`.
  - Landing L17's residual mirroring takes it upstream as the release tracker (the #255
    precedent).
  - **No new REQ**: it records an obligation and changes no behaviour.
  - depends-on: 5.1

> **Declared REQ exemptions:** `no-req-required` {5.1, 5.2}. A version bump, release notes, and a
> follow-on tracking bead change no behaviour, as each body states.

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: allocated REQ ids are free
- Type: auto
- Condition: `REQ-YF-DOCTOR-008`, `REQ-BINIT-028`, `REQ-RESEARCH-025`, `REQ-RESEARCH-026` and `REQ-RESEARCH-027` appear in no SPEC file
- Test: for id in REQ-YF-DOCTOR-008 REQ-BINIT-028 REQ-RESEARCH-025 REQ-RESEARCH-026 REQ-RESEARCH-027; do if grep -rq "$id" SPEC.md skills/*/SPEC.md skills/*/spec; then echo "TAKEN: $id"; exit 1; fi; done
- Blocks: 0.1, 0.3, 0.4, 0.5, 0.6
- Instructions: ONE-SHOT. Evaluate it before Epic 0 lands; it exits 1 by design afterwards. On TAKEN, renumber in plan.md before pouring.
- test_class: probe
- cwd: repo-root

### Capability Gate: baseline FAST tier is green
- Type: auto
- Condition: The FAST validation tier passes on the execute branch before any change, so a later red result is attributable to this plan
- Test: uv run skills/yf-change-validation/scripts/change_validation.py run --tier fast
- Blocks: 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7
- Instructions: `build` class. Run it with `--sweep-gates=all`, or as the first act of execution. **Precondition before this gate (R10):** plan-072 has landed with a green L3 FULL run; check that `docs/plans/plan-072-james-dixson-bae8de/plan.md` reads `status: complete` on `origin/main`. A red baseline must be named before any change in this plan, or this plan will be blamed for it. Epic 0 is blocked too because the SPEC edits feed the amendment-log and coverage rows (pass-1 gate assessment).
- test_class: build
- cwd: repo-root

### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations

| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | An optional tool's skill, now that doctor no longer fails, runs its tool-dependent path on a machine without the tool | med | Not a regression: preflight never probed these tools (pass-1 C1). Each skill already fails closed in its own entrypoint, and REQ-YF-DOCTOR-008 makes that a requirement, checked by Issue 1.4 |
| R2 | A `depends-on-tool` consumer is missed, so an optional tool disappears from a README contract, the "At a glance" block, or a web page | med | Issue 1.6 enumerates every non-history consumer from `grep -rl depends-on-tool`. SC6 runs the README checker's new negative control, and `check_required_set.py` runs in the FAST tier |
| R3 | `quotes[]` breaks rendering of existing research bundles that carry only `quote` | med | Legacy `quote` is normalized to a one-element `quotes[]` on load, with a tested legacy case (`test_legacy_quote_normalized`) |
| R4 | The red-team eyeballs quotes and ignores `check-quotes` | med | Check 4's basis is the deterministic command's verbatim output, so the false-positive class closes even if the brief is skimmed |
| R5 | Landing L3's FULL trigger-eval row goes INCONCLUSIVE on a shared-account rate limit (a FAIL is R10) | med | A landing halts on INCONCLUSIVE, and nothing outward has happened at L3. Recovery: re-run the `trigger-eval` row directly with `skill_trigger_eval.py … --resume <results.jsonl>` until it is green, then re-invoke `land --apply` (the journal resumes; L3 re-validates) |
| R6 | The post-landing `v0.6.0` tag lands on a commit behind `main`'s workflows and the release 403s (the v0.5.0 failure) | high | The post-landing preconditions assert tag == `origin/main` and no workflow diff before the push (Approach → Release) |
| R7 | Moving arXiv to Tier 4 under-scores peer-reviewed papers hosted there | low | `--peer-reviewed` / `peer_reviewed: true` restores Tier 1, and the triangulator rubric documents when to set it |
| R8 | The CHANGELOG omits a shipped plan, or cites an unshipped one | low | SC11 checks every `complete` plan 055–071 plus 072/073. Issue 5.1 excludes non-`complete` plans such as plan-069 |
| R9 | Landing plan-073 is blocked by bookkeeping (plan-072's own landing still holds the lock, or `main` is mid-merge) | low | Superseded by R10's stricter precondition: plan-073 execution starts only after plan-072 has **landed**, and the execute branch is cut from `main` at that point |
| R10 | plan-073's landing L3 inherits plan-072's open FULL `trigger-eval` FAIL. plan-072's code is already on `main`, and its landing attempt 4 failed L3 on a pi cell (`plan-072 assets/landing-handoff.md`) | med | **Execution-start precondition:** plan-073 does not start until plan-072 has landed with a green L3 FULL run. That run resolves the FAIL, whether by a description fix or by confirming noise. If plan-073's own L3 later fails the trigger-eval row, the recovery is the plan-072 handoff's Step 1–2: a pi/cc diagnostic run with `--results`, then a description fix or a confirmed-noise re-run, then re-invoke `land --apply` (pass-3 C2) |

## Success Criteria

| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | Every new or amended REQ id is in the SPEC set and the `plan-073` amendment-log entry | `uv run scripts/check_amendment_log.py --plan plan-073-james-dixson-cc76de` → exit 0 | 0.1, 0.2, 0.3, 0.4, 0.5, 0.6 |
| SC2 | `optional-tool` is parsed, and the frontmatter guard rejects a tool listed in both keys | `cargo test -p yf -- --list 2>/dev/null \| grep -q 'frontmatter::tests::optional_tool' && cargo test -p yf frontmatter::tests::optional_tool && grep -q 'def test_optional_tool_overlap_rejected' scripts/test_check_frontmatter.py && uv run scripts/test_check_frontmatter.py` → exit 0 | 1.1 |
| SC3 | A missing optional tool is a doctor warning, a missing required tool is still a failure, and `--strict` ignores optional tools | `L=$(cargo test -p yf -- --list 2>/dev/null) && for t in skill_deps_optional_missing_is_warning skill_deps_required_and_optional_missing_fails skill_deps_all_present_with_optional_ok strict_ignores_optional_tools; do echo "$L" \| grep -q "::$t: test" \|\| exit 1; done && echo "$L" \| grep -q "cmd::common::tests::strict_ignores_optional_tools: test" && cargo test -p yf skill_deps_ && cargo test -p yf strict_ignores_optional_tools` → exit 0 | 1.2, 1.3 |
| SC4 | The four tools are declared optional in their skills, yf-diagram-authoring declares uv, and `render.py render` fails closed without d2 | `grep -q '^optional-tool: \[herdr\]$' skills/yf-herdr/SKILL.md && grep -q '^optional-tool: \[pandoc\]$' skills/yf-markdown-html/SKILL.md && grep -q '^optional-tool: \[pandoc, xelatex\]$' skills/yf-markdown-pdf/SKILL.md && grep -q '^optional-tool: \[d2\]$' skills/yf-diagram-authoring/SKILL.md && grep -q '^depends-on-tool: \[uv\]$' skills/yf-diagram-authoring/SKILL.md && grep -q 'def test_render_fails_closed_without_d2' skills/yf-diagram-authoring/scripts/test_render.py && uv run skills/yf-diagram-authoring/scripts/test_render.py` → exit 0 | 0.7, 1.4 |
| SC5 | `yf doctor` with only bd/uv/git on `PATH` has no failing skill-deps axis | `cargo test -p yf -- --list 2>/dev/null \| grep -q 'doctor_green_without_optional_tools: test' && cargo test -p yf doctor_green_without_optional_tools` → exit 0 | 1.5 |
| SC6 | The README contract enforces the union and the optional marker, and the generated "At a glance" data still passes | `grep -q 'def test_optional_tool_must_be_marked_optional' scripts/checks/test_check_skill_readme_contract.py && uv run --with pytest python3 -m pytest scripts/checks/test_check_skill_readme_contract.py -q && uv run scripts/checks/check_skill_readme_contract.py && uv run scripts/checks/check_required_set.py` → exit 0 | 1.6, 4.1 |
| SC7 | The beads kernel tops up and verify-reports `/.beads.gate.lock` | `grep -q '"/.beads.gate.lock"' yf/src/beads_init.rs && cargo test -p yf -- --list 2>/dev/null \| grep -q 'verify_reports_unignored_gate_lock: test' && cargo test -p yf ensure_gitignore_idempotent && cargo test -p yf verify_reports_unignored_gate_lock` → exit 0 | 2.1 |
| SC8 | `check-quotes`, legacy-quote handling and idempotent `all` exist and are tested | `for t in test_check_quotes_traced test_check_quotes_untraced_reports_id test_legacy_quote_normalized test_check_quotes_ellipsis_split test_all_idempotent; do grep -q "def $t" skills/yf-research/scripts/test_link_normalizer.py \|\| exit 1; done && uv run skills/yf-research/scripts/link_normalizer.py check-quotes --help && uv run skills/yf-research/scripts/test_link_normalizer.py` → exit 0 | 3.1, 3.4 |
| SC9 | The agent briefs, data spec and README carry the evidence store and `sources.md`-at-synthesize | `R=skills/yf-research && grep -q 'check-quotes' $R/agents/red-team.md && grep -q 'sources.md' $R/agents/red-team.md && grep -q 'link_normalizer.py all' $R/agents/synthesizer.md && grep -q 'quotes\[\]' $R/agents/retriever.md && grep -q 'quotes\[\]' $R/agents/triangulator.md && grep -q 'quotes\[\]' $R/agents/synthesizer.md && grep -q 'quotes\[\]' $R/spec/data.md && grep -q 'quotes\[\]' $R/README.md && grep -q 'peer-reviewed' $R/README.md` → exit 0 | 3.2, 3.3, 3.4, 4.2 |
| SC10 | Preprints score Tier 4 by default, `--peer-reviewed` restores Tier 1, and registry/mirror `.dev` URLs do not get Tier 2 | `for t in test_preprint_tier4 test_osf_preprints_path_match test_peer_reviewed_restores_tier1 test_dev_registry_not_tier2 test_dev_docs_stays_tier2; do grep -q "def $t" skills/yf-research/scripts/test_credibility_scorer.py \|\| exit 1; done && uv run skills/yf-research/scripts/test_credibility_scorer.py` → exit 0 | 3.5 |
| SC11 | The CHANGELOG v0.6.0 section cites every `complete` plan 055–071 plus 072 and 073, and every version literal reads 0.6.0 | `grep -q '^version = "0.6.0"' yf/Cargo.toml && grep -q 'YOSHIKOFLOW_RELEASE = "v0.6.0"' web/pelicanconf.py && uv run python -c 'import re,pathlib,sys;t=pathlib.Path("CHANGELOG.md").read_text();s=t.split("## v0.6.0",1)[1].split("\n## v",1)[0];ids=sorted({int(p.name[5:8]) for p in pathlib.Path("docs/plans").glob("plan-0*") if 55<=int(p.name[5:8])<=71 and re.search(r"(?m)^status: complete$",(p/"plan.md").read_text())}\|{72,73});sys.exit(1 if [i for i in ids if not re.search(r"\bplan-0*%d\b"%i,s)] else 0)'` → exit 0 | 5.1 |
| SC12 | **Regression guard, not delivery evidence** (green before execution; pass-2 C9): the FAST tier is green on the execute branch at completion. The landing's L3 runs FULL on the merged tree | manual: `uv run skills/yf-change-validation/scripts/change_validation.py run --tier fast` exits 0 on the execute branch at completion (about 180 s, over ready-check's 30 s smoke bound, so recorded as manual) | 1.6, 2.1, 3.5, 5.1 |
| SC13 | **Regression guard, not delivery evidence** (green before execution; pass-2 C9): every SKILL.md frontmatter, including the new key, passes the repo guard | `uv run scripts/check_frontmatter.py` → exit 0 | 1.4 |
| SC14 | The release follow-on bead exists, stays open, and sits outside the plan subtree | `bd list --status open --json \| uv run python -c 'import json,sys;sys.exit(0 if any(i["title"].startswith("Cut v0.6.0") for i in json.load(sys.stdin)) else 1)'` → exit 0 | 5.2 |
