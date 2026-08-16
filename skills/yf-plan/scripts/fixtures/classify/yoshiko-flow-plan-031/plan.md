---
deliverable_class: ci-release
source_plan: plan-031-james-dixson-62a375
source_repo: yoshiko-flow
---
# Plan: Build yoshiko-flow documentation + Pelican static site under web/ deployed to yoshikoflow.sh (supersedes #54, #28)

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
|:------|:------|:------------|:------|:------------|
| #28 | Epic 7: User-facing documentation site (Docusaurus) | supersede | Docusaurus/`website/` + GitHub Pages approach abandoned in favor of Pelican + `web/` + yoshikoflow.sh (S3/CloudFront). `website/` and `docs-deploy.yml` removed. | Epic 1, Epic 6 |
| #54 | Level up getting-started documentation | supersede | Getting-started content (install → user-scope init → configure upstream + beads) authored as first-class pages on the new site. | Epic 3, Epic 4 |

Both are **supersede** (not merely include): the deliverable is a different site generator and
hosting target than either issue assumed. Reconcile step closes both with a pointer to
yoshikoflow.sh and this plan.

**Coarse plan tracker.** Per the project's coarse upstream convention (AGENTS.md — ONE tracking
issue per plan-scale effort, precedent #13/#14/#16), the single `plan-031 execution tracking`
GitHub issue is filed at INTAKE (yf-plan §4.5), linking this plan and its epics. It is not listed
as a row above because it tracks plan-031's own delivery rather than being an incorporated issue.

## Epics

### Epic 1: Retire Docusaurus, scaffold `web/` (Pelican)
- Issue 1.1: Salvage reusable content from `website/docs/*.md` into a staging note under the plan folder (install, commands, preflight, migration, skills, intro).
- Issue 1.2: Remove `website/` directory and `.github/workflows/docs-deploy.yml`; grep-remove dangling references (README, docs).
  - depends-on: 1.1
- Issue 1.3: Scaffold `web/` skeleton — `pelicanconf.py`, `publishconf.py` (fail-closed on unset `PUBLISH_URL`), `requirements.txt` (pinned), `Makefile`, `.gitignore`, `content/` tree, `plugins/`.
- Issue 1.4: Port + rebrand theme `themes/yoshikoflow/` (from naba-terminal) and the `home_content` hero/cards plugin; `make html` builds clean.
  - depends-on: 1.3

### Epic 2: Skill-page auto-generation
- Issue 2.1: Write `web/plugins/skill_pages.py` — read `skills/*/SKILL.md` frontmatter (`name`, `description`, `skill-group`) and parse the `TRIGGER when:` / `SKIP for:` prose out of `description` (there is no separate `triggers` field); emit one page per skill + a grouped index; resolve skill dir relative to repo root.
  - depends-on: 1.3
- Issue 2.2: Add optional per-skill intro override mechanism (`web/content/skills/<name>.md` front-matter merged over generated content).
  - depends-on: 2.1
- Issue 2.3: Verify generated set == 18 skills, grouped (beads/utility/markdown), links resolve; lint generated pages.
  - depends-on: 2.1

### Epic 3: Content pages (landing, architecture, lifecycle)
- Issue 3.1: Landing/hero — what/why of yoshiko-flow; feature cards.
  - depends-on: 1.4
- Issue 3.2: Architecture page — `yf` kernel + embedded skills + beads + upstream tracking; include a d2 diagram (yf-diagram-authoring).
  - depends-on: 1.4
- Issue 3.3: Skill lifecycle page — install → preflight → invoke → coordinate/execute; d2 diagram.
  - depends-on: 1.4

### Epic 4: Installation + usage pages, install-default switch
- Issue 4.1: `web/scripts/sync_installer.sh` — mirror cargo-dist `yf-installer.sh` (pinned tag) to `content/extra/install.sh`; fail-safe placeholder when no release exists.
  - depends-on: 1.3
- Issue 4.2: Installation page — vendor `curl | sh` default, Homebrew + from-source alternatives, prerequisites (`bd`, `uv`, `git`), `yf skills install` for skill vendoring.
  - depends-on: 1.4, 4.1
- Issue 4.3: Usage-examples page — `/yf-plan`, `/yf-research`, `yf skills install`, the beads ready→claim→close loop.
  - depends-on: 1.4
- Issue 4.4: Un-suppress + rewrite README install section — recommended CLI install becomes `curl … https://yoshikoflow.sh/install.sh | sh`; Homebrew/source demoted.
  - depends-on: 4.1
  - resolves-upstream: #54 (supersede)

### Epic 5: AWS provisioning scripts + CI OIDC (author only)
- Issue 5.1: `web/scripts/provision_aws.sh` (idempotent, state-file, fail-closed) — S3, OAC, ACM (us-east-1, DNS-validated via existing zone), CloudFront Function, distribution (+ `/install.sh` no-cache behavior), bucket policy, Route53 A/ALIAS.
  - depends-on: 1.3
- Issue 5.2: `web/scripts/aws/index-rewrite.js` (pretty-URL viewer function) + `web/scripts/aws/ci/{README,trust-policy.json.tmpl,deploy-policy.json.tmpl}` (least-privilege OIDC deploy role).
  - depends-on: 5.1
- Issue 5.3: `web/docs/provisioning-runbook.md` — provision, verify, teardown/rollback.
  - depends-on: 5.1

### Epic 6: CI deploy wiring + secrets/config
- Issue 6.1: `web/.envrc.example` (committed) — document all env vars + optional `op read "op://Y-Home/…"` sourcing; ensure real `.envrc` gitignored.
  - depends-on: 1.3
- Issue 6.2: `.github/workflows/web-deploy.yml` — `workflow_dispatch` + `workflow_run` off "Release"; OIDC auth; build → `s3 sync --delete` + invalidation + re-mirror install.sh. **Acceptance:** the `workflow_run` path is guarded by `event == 'push' && conclusion == 'success'` (so `release.yml`'s `pull_request` runs and failed releases never deploy), matching naba.
  - depends-on: 5.2, 6.1
  - resolves-upstream: #28 (supersede)

### Epic 7: Go-live (gated provisioning + first deploy)

Secret-setting is split so no secret is ever set before its value exists (the distribution id
does not exist until 7.2 provisions it; the deploy-role ARN until 7.3 creates the role).

- Issue 7.1: Set the **pre-known** GitHub repo secrets (`gh secret set`): `YOSHIKOFLOW_SITE_DOMAIN`, `YOSHIKOFLOW_HOSTED_ZONE_ID`, optional `YOSHIKOFLOW_GA_MEASUREMENT_ID`.
  - depends-on: 5.2, 6.2
- Issue 7.2: Run `provision_aws.sh` (behind the AWS capability gate); capture the distribution id into `.envrc` **and** set the `YOSHIKOFLOW_CF_DISTRIBUTION` repo secret; verify cert validated + distribution deployed.
  - depends-on: 7.1
- Issue 7.3: Create the CI OIDC provider + deploy role from the templates; set the `AWS_DEPLOY_ROLE_ARN` repo secret from the created role.
  - depends-on: 7.1
- Issue 7.4: First deploy — `make -C web deploy`; verify https://yoshikoflow.sh serves the site and `https://yoshikoflow.sh/install.sh | sh` installs `yf`.
  - depends-on: 7.2, 7.3

## Risks & Mitigations

| Risk | Mitigation |
|:-----|:-----------|
| Deleting `website/` loses usable content | Issue 1.1 salvages content into a staging note **before** 1.2 removes the dir; removal depends-on salvage. |
| ACM validation / DNS propagation stalls provisioning | `provision_aws.sh` uses `acm wait certificate-validated` with a timeout; runbook (5.3) documents manual re-check. Zone already exists, reducing risk. |
| Billable/irreversible AWS changes run prematurely | All live provisioning (Epic 7) sits behind the AWS capability gate with a verifiable `Test:`; Epics 1–6 are author-only and produce no cloud state. |
| `install.sh` mirror serves a stale/placeholder script | `sync_installer.sh` pins to the release `announcement_tag` (reproducible) and ships a fail-safe placeholder that exits 1 when no release exists; `/install.sh` served with short cache TTL + invalidation. |
| Skill count/description drift | Skill pages auto-generated from SKILL.md at build; no hand-maintained list. Issue 2.3 asserts count == 18. |
| Switching install default breaks the one-line install before the domain is live | README switch (4.4) lands with the code, but go-live (7.4) verifies `curl … | sh` works end-to-end before the plan completes; deliverable class re-confirmed at reconcile. |
| Secrets committed by accident | Real `.envrc` gitignored; only `.envrc.example` committed; CI uses OIDC role + `gh secret` (no long-lived keys in repo). |

## Success Criteria

1. `web/` contains a Pelican site that `make -C web html` builds with zero errors; `make validate` (prod build) passes.
2. The site has: a landing page (what/why), one auto-generated page per skill for **all 18** skills (grouped), an architecture page, a skill-lifecycle page, an installation page, and a usage-examples page.
3. `website/` and `.github/workflows/docs-deploy.yml` are removed; no dangling references remain.
4. `.github/workflows/web-deploy.yml` deploys on `workflow_dispatch` and on a completed "Release" run, via OIDC (no long-lived AWS keys), running `make -C web deploy`.
5. All operational values live in `.envrc` (gitignored) with a committed `web/.envrc.example`; CI reads them from GitHub repo secrets; optional 1Password/Y-Home sourcing documented.
6. https://yoshikoflow.sh serves the site over HTTPS (valid ACM cert), and `curl --proto '=https' --tlsv1.2 -LsSf https://yoshikoflow.sh/install.sh | sh` installs the `yf` CLI.
7. README's recommended CLI install is the vendor `curl | sh` at yoshikoflow.sh; Homebrew and from-source are documented as alternatives.
8. Cutting a `v*` release triggers (via `workflow_run`) a fresh web deploy that re-mirrors `install.sh`.
9. Upstream #28 and #54 are closed as superseded, pointing at yoshikoflow.sh and this plan.
