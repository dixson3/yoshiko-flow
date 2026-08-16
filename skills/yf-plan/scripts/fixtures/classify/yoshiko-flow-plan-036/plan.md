---
deliverable_class: standard
source_plan: plan-036-james-dixson-461061
source_repo: yoshiko-flow
---
# Plan: Authored per-skill web pages (hybrid), drift-check-enforced

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|

_No existing upstream issue drives this plan (a repo-search found none). A single coarse
`plan-036 execution tracking` issue is filed at intake per the AGENTS.md convention; no
`resolves-upstream` links, so **no reconcile gate/step** is needed._

## Epics

### Epic 1: Plugin hybrid-composition rework (keystone)
Invert `skill_pages.py` so authored prose wins while catalog facts stay generated.

- Issue 1.1: **Rework `web/plugins/skill_pages.py`.** Make `web/content/skills/<name>.md` the page
  prose body; keep the generated "At a glance" block, `/skills/` index, and `SKILL_NAV`; remove the
  README-body auto-transform from the page. **Also remove the generated "When it fires" / "When to
  skip" blocks (C5):** the RICH seed folds trigger/skip into the authored prose, so keeping the
  generated blocks would duplicate them — the generated block retains **only** the mechanical "At a
  glance" facts. Add a graceful **fallback to the README transform when no authored page exists**
  (rollout safety) and a `missing_authored_page` signal (list of skills with no page) for Epic 3 to
  tighten. Preserve link/anchor rewriting and frontmatter-stripping. **Note (M1):** authored-page
  `Title`/`Slug`/`Subtitle` stay plugin-set (`title=name`, `subtitle=summary[:120]`); the plugin
  strips any authored frontmatter — title/subtitle remain mechanical, unlike other content pages.
  Update the module docstring to describe the hybrid model.
- Issue 1.2: **Mechanism smoke + docstring/tests.** Add/adjust a lightweight build-time check or
  test that (a) an authored page renders as the prose body with the quick-ref block still present,
  and (b) a skill without an authored page still builds via fallback. If the plugin has existing
  tests, update them; otherwise a minimal `pelican` build assertion over a fixture page.
  - depends-on: 1.1

### Epic 2: Author the 18 skill pages (rich seed, VOICE-governed)
One `web/content/skills/<name>.md` per skill, seeded from its three sources, tuned to public voice.

- Issue 2.1: **Draft the beads-group pages (6):** `yf-beads-authoring`, `yf-beads-extra`,
  `yf-beads-hygiene`, `yf-beads-init`, `yf-beads-upstream`, plus `yf-change-validation`. Seed rich
  from each `{SKILL.md,README.md,SPEC.md}`; apply VOICE.md; lint clean.
  - depends-on: 1.1
- Issue 2.2: **Draft the workflows-group pages:** `yf-plan`, `yf-research`, `yf-incubator`,
  `yf-okf`. Same seed + VOICE + lint.
  - depends-on: 1.1
- Issue 2.3: **Draft the markdown-group pages:** `yf-markdown-lint`, `yf-markdown-format`,
  `yf-markdown-html`, `yf-markdown-pdf`. Same seed + VOICE + lint.
  - depends-on: 1.1
- Issue 2.4: **Draft the utility/authoring pages:** `yf-diagram-authoring`, `yf-drift-check`,
  `yf-optimal-instructions`, `yf-skill-authoring`. Same seed + VOICE + lint.
  - depends-on: 1.1

_(Grouping is for parallel drafting only; the site grouping remains the `skill-group` frontmatter.)_

### Epic 3: Drift-enforce + guard-tighten + exit gate
Wire the manifest edge, make the plugin fail-closed on a missing page, and prove the build.

- Issue 3.1: **Extend `DRIFT-CHECK.md`** (schema-conformant per C1/C3/C4/C6). Keep `approved: yes`.
  1. **§1 node:** add `skill-page` = `web/content/skills/*.md` (kind `doc`, authority `derived`).
  2. **§2 edges (three, node-sourced):** `e-skill-page-desc` (`skill-md` → `skill-page`),
     `e-skill-page-readme` (`skill-readme` → `skill-page`), `e-skill-page-spec` (`per-skill-spec` →
     `skill-page`) — each name-paired by the shared `*`. Every edge references existing §1 node IDs
     (schema rule), not a raw glob.
  3. **§3 per-edge contract:** `Contract = field-set-subset`, `Check Category = behavioral` (model
     on `e-spec-readme`). Subset semantics: the authored page's factual claims (invocation,
     triggers, dependencies, behavior) must not **contradict** the sources; a page that curates/omits
     repo-dev detail PASSes — only an affirmative contradiction FAILs (fixes the R7 false-positive
     risk). Mechanical quick-ref is generated and explicitly out of scope.
  4. **§6 Trigger Scope — all four touch-points:** the three source-side globs (`skills/*/SKILL.md`,
     `skills/*/README.md`, `skills/*/SPEC.md`) **and** the derived-side glob
     (`web/content/skills/*.md`) so editing the authored prose itself re-checks its own claims (C4).
  5. **§ fix stale sentence (C6):** the `e-web-skill-counts` verification prose says the per-skill
     pages "are auto-generated from the same frontmatter and never drift" — after hybridization the
     prose is authored + drift-checked; correct it to say only the **counts/index/nav** stay
     auto-derived, the prose is authored and guarded by `e-skill-page-*`.
  - depends-on: 2.1, 2.2, 2.3, 2.4
- Issue 3.2: **Tighten the plugin guard + drop dead code.** Now that all 18 pages exist, flip the
  Epic-1 fallback to a **hard build failure** when a skill has no authored page (a new skill must
  get a page), with a clear error naming the missing skill(s). Since the README-transform fallback
  is now unreachable, **remove the dead `_readme_html` / `_readme_body_md` / `_rewrite_readme_links`
  functions and their now-orphaned module constants (`_DROP_SECTIONS`, `_MD_LINK`)** (C7) rather
  than leave confusing dead code. Update the docstring/test accordingly.
  - depends-on: 2.1, 2.2, 2.3, 2.4, 1.2
- Issue 3.3: **Exit gate.** (1) Full `yf-markdown-lint` audit over the 18 new pages (no `--rules`
  subset; known ML003 Pelican site-absolute `/slug/` false positives are acceptable **only** if the
  target slug/anchor exists and the build is clean — any other class fails). (2) **0-warning Pelican
  build** with all 18 `/skills/<name>/` pages present, the `/skills/` index intact, and `SKILL_NAV`
  rendering. (3) A `yf-drift-check` run scoped to the three `e-skill-page-*` edges returns **PASS**
  (or only INCONCLUSIVE with a surfaced reason — never FAIL) across all 18 pairings.
  - depends-on: 3.1, 3.2

## Risks & Mitigations

| # | Risk | Mitigation |
|:--|:-----|:-----------|
| R1 | Inverting the plugin breaks the existing `/skills/` pages or the sidebar mid-migration. | Epic 1 keeps the index + `SKILL_NAV` generation untouched and adds a **README-transform fallback** so any not-yet-authored skill still renders; the mechanism smoke (1.2) proves both authored and fallback paths build before any page is cut over. |
| R2 | Authored pages drift from skill behavior over time — the exact failure authored prose invites. | Epic 3 adds the three `e-skill-page-*` drift edges to the already-`approved` manifest; editing a skill's `SKILL/README/SPEC` **or** its authored page fires the check (§6 source + derived triggers). Hybrid composition keeps mechanical facts generated, shrinking the drift surface to prose. |
| R3 | Rich seeding just copies README prose, reproducing the current dev-facing register on an "authored" page. | VOICE.md (plan-035) governs every page: public register, one-idea sentences, exposition over density. Seeding is a **starting draft to trim**, and the drafter rewrites rather than pastes; the exit-gate lint + a spot review catch raw dumps. |
| R4 | A new skill added later silently gets no page (or a stale fallback), reintroducing an ungoverned page. | Issue 3.2 makes a missing authored page a **hard build failure** naming the skill, so CI/build cannot pass until the page exists. |
| R5 | Removing the README auto-transform loses useful content that lived only on the generated page (e.g. rewritten diagram links). | Rich seeding pulls the README exposition into the authored page as the starting draft, so nothing is lost — it becomes editable. Skill-relative links are re-pointed to GitHub the same way the plugin did (carried into the seed). |
| R6 | ML003 Pelican site-absolute-URL false positives mask a real broken link on the new pages. | The exit gate judges ML003 against a **real Pelican build** (0 warnings) with every referenced slug/anchor confirmed to exist (the plan-035 precedent); any non-ML003 class, or any build warning, fails the gate. |
| R7 | The drift edge is too strict and flags every stylistic difference between prose and source. | The §3 per-edge contract is `field-set-subset` / `behavioral`: agreement is scoped to **factual claims** (invocation, triggers, dependencies, behavior), explicitly excluding wording/structure; a curated page that omits repo-dev detail PASSes — only an affirmative contradiction FAILs. The verifier is report-only and INCONCLUSIVE-tolerant. |
| R8 | Edge cases in the skill↔page mapping: an orphan `content/skills/<name>.md` with no skill dir (M2), or a future 19th skill added with no page (M3). | Orphan pages are silently ignored by the plugin (no skill → no page) — a one-line note in Issue 1.1's docstring flags them; a stray page still lints/builds harmlessly. New-skill onboarding is enforced by Issue 3.2's fail-closed guard: the build fails, naming the skill, until its page exists. |
| R9 | Editing `skill_pages.py` (Epic 1) self-fires the existing `e-web-skill-groups` drift edge. | Expected and non-blocking (C7): the group registry is untouched so it passes; `e-web-skill-groups` / the plugin node are out of this plan's scope. |

## Success Criteria
- **Authored pages exist:** `web/content/skills/<name>.md` present for all **18** skills, each a
  rich, VOICE-governed page (not a stub, not a raw README dump), hand-editable. (Epic 2)
- **Hybrid composition works:** the `skill_pages.py` plugin renders each authored page as the prose
  body with the generated **"At a glance"** block above it; the `/skills/` index and `SKILL_NAV`
  remain frontmatter-derived and correct. (Epic 1)
- **Fail-closed on gaps:** a skill with no authored page is a **hard build failure** naming the
  skill; no silent fallback in the shipped state. (Epic 3)
- **Drift-enforced (schema-clean):** `DRIFT-CHECK.md` carries the `skill-page` node, the three
  node-sourced edges `e-skill-page-desc`/`-readme`/`-spec` (`field-set-subset`/`behavioral`,
  per-skill-paired), and §6 trigger-scope globs on **both** the source side and the derived
  (`web/content/skills/*.md`) side; a `yf-drift-check` run over the three edges returns PASS across
  all 18 pairings. (Epic 3)
- **Catalog still can't drift:** skill count, groups, invocation, and dependencies on the `/skills/`
  index and sidebar remain derived from `SKILL.md` frontmatter. (Epic 1)
- **Exit gate green:** full `yf-markdown-lint` audit clean over the new pages (net of known ML003
  Pelican-URL false positives with targets verified) + a **0-warning Pelican build** with all 18
  skill pages, index, and nav. (Epic 3)
