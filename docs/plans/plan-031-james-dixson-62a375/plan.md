---
type: Plan
okf_spec: OKF-PLAN
id: plan-031-james-dixson-62a375
author: james-dixson
created: '2026-07-22'
status: approved
deliverable_class: ci-release
fingerprint: a384289e2d4c776525d430c571c70419363916c8e62e46ec23388cfc81fb628e
---
# Plan: Build yoshiko-flow documentation + Pelican static site under web/ deployed to yoshikoflow.sh (supersedes #54, #28)

**ID:** plan-031-james-dixson-62a375
**Author:** james-dixson
**Created:** 2026-07-22
**Status:** approved
**Deliverable-class:** ci-release
**Fingerprint:** a384289e2d4c776525d430c571c70419363916c8e62e46ec23388cfc81fb628e
**Phase log:**
- 2026-07-22 scoping: initial scope captured; upstream #54/#28 triaged (both superseded)
- 2026-07-22 investigating: repo + AWS recon complete (cargo-dist workspace, yoshikoflow.sh zone exists, 18 skills, suppressed vendor installer, existing Docusaurus site)
- 2026-07-22 drafting: plan v1 presented
- 2026-07-22 review: red-team pass 1 — APPROVE (2 medium + 2 low concerns, resolved in place)

## Objective

Stand up **https://yoshikoflow.sh** as the public home of yoshiko-flow: a Pelican-based
static site under `web/` (modeled on `naba`'s `web/`), deployed to S3 + CloudFront, with a
landing page (what/why), an auto-generated page per skill (18 skills), and dedicated pages for
architecture, the skill lifecycle, installation, and top-level usage. Wire version publishing
to trigger a static web deploy, switch the recommended CLI install to the cargo-dist
`curl | sh` vendor installer hosted at the new domain, and hold all operational values/secrets
in `.envrc` (local) + GitHub repo secrets (CI). Supersede #54 (getting-started docs) and #28
(Docusaurus site) — the Docusaurus scaffold in `website/` is retired.

## Motivation

yoshiko-flow has no public web presence. Two things are blocked on that gap:

1. **The vendor `curl | sh` installer is suppressed.** The README already ships a cargo-dist
   shell installer but comments it out with an explicit note: "temporarily suppressed until the
   dedicated yoshiko-flow domain is stood up to host the install script." New users are steered
   to the Homebrew tap instead of the one-line install the project wants as its default.
2. **Docs are thin and drifting.** Getting-started docs (#54) are incomplete, and the earlier
   Docusaurus attempt (#28) was left disabled behind an unresolved GitHub Pages hosting
   decision (plan-010 Gate G4). Skill counts are already stale across surfaces (README says 17,
   the Docusaurus intro says 13; there are 18 on disk).

`naba` already proved the pattern this project wants — Pelican + private S3 + CloudFront (OAC) +
ACM + Route53, secrets via `.envrc`/GitHub secrets, and a web deploy chained off the cargo-dist
"Release" workflow. yoshiko-flow is the same kind of cargo-dist Rust workspace, and the
`yoshikoflow.sh` Route53 zone already exists. Adopting naba's pattern stands up the domain,
unblocks the install-default switch, and gives docs a maintainable home. Audience: prospective
and current yoshiko-flow users, plus maintainers who need install/usage docs to stop drifting.

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

## Investigation Findings

Recon (no separate experiments needed — findings gathered directly):

- **Repo is a cargo-dist Rust workspace.** `yf/Cargo.toml` v0.4.0; `release.yml` (cargo-dist
  v0.32.0) fires on `v*` tags, builds the matrix, creates a GitHub Release with `yf-installer.sh`,
  and publishes the Homebrew formula. **This means naba's `workflow_run`-chained web deploy
  transfers directly** — no new release machinery needed.
- **`yoshikoflow.sh` Route53 hosted zone exists** (`Z0201468FY30AYTNQWIO`). AWS access confirmed
  (account `534185824505`, user `dixson3`). **No** S3 bucket or ACM cert for the domain yet →
  provisioning required. `.sh` domain already registered (zone present).
- **Vendor installer already built, suppressed in README** pending the domain. Standing up the
  domain is the precondition the README itself names for flipping the default.
- **Existing Docusaurus site in `website/`** (disabled `docs-deploy.yml`, `if: false`, blocked
  on plan-010 Gate G4). This is issue #28. Superseding #28 = retiring `website/`. Salvageable
  content: `website/docs/{intro,install,commands,preflight,migration,skills}.md`.
- **18 skills** on disk under `skills/` (README lists 17, omits `yf-beads-hygiene` + `yf-okf`;
  Docusaurus intro says 13 — both stale). Groups: beads (8), utility (6), markdown (4).
- **naba `web/` reference** fully characterized: `pelicanconf.py` (empty `SITEURL`,
  `PUBLISH_URL` from env, pretty URLs, `home_content` plugin, sitemap), `publishconf.py`
  (env-driven `SITEURL`, fail-closed, prod-only GA), `Makefile` (html/publish/deploy/provision),
  `plugins/home_content.py`, `themes/naba-terminal/`, `scripts/provision_aws.sh` +
  `scripts/aws/index-rewrite.js` + `scripts/aws/ci/*`, `scripts/sync_installer.sh`, and
  `.github/workflows/web-deploy.yml` (OIDC + `workflow_run` off "Release"). **No 1Password/`op`
  usage exists in naba** — secrets are `.envrc` (direnv, gitignored) + `gh secret set`.

**Decision on the `.envrc` / 1Password ask.** The request named "1password / Y-Home vault as
needed." naba does *not* use `op`; it uses a gitignored `.envrc` + GitHub repo secrets. This plan
follows naba (env + `gh secret`) as the operational default, and adds an **optional** 1Password
sourcing convention (`op read "op://Y-Home/..."`) in the `.envrc.example` for operators who want
secrets backed by the vault rather than typed in-file. The non-secret operational values
(domain, distribution id, hosted-zone id) are not secrets and stay plain env.

## Approach

Port naba's `web/` pattern into yoshiko-flow's `web/` directory, rebranded, with a
metadata-driven skill-page generator, then provision live infra behind a capability gate and
flip the install default. Concretely:

**Site generator (`web/`).** Pelican, mirroring naba's structure: `pelicanconf.py` /
`publishconf.py` (empty `SITEURL` dev, `PUBLISH_URL` env for prod, fail-closed if unset, pretty
URLs `{slug}/index.html`, prod-only GA hook), `requirements.txt` (pinned Pelican + sitemap),
`Makefile` (`html`/`devserver`/`validate`/`publish`/`deploy`/`provision`), a rebranded theme
(`themes/yoshikoflow/`, adapted from `naba-terminal`), and the `home_content` hero/cards plugin.

**Skill pages (auto-generated).** A local Pelican plugin (`plugins/skill_pages.py`) reads each
`skills/*/SKILL.md` frontmatter (name, description, triggers, group) at build time and emits one
page per skill plus a grouped index. Single source of truth = the SKILL.md files, so counts and
descriptions never drift. Hand-authored intro prose is layered via optional per-skill overrides
in `web/content/skills/`.

**Static content pages.** Landing (what/why), architecture (the `yf` kernel + embedded skills +
beads + upstream tracking), skill lifecycle (install → preflight → invoke → coordinate/execute),
installation (vendor `curl | sh` default, Homebrew + from-source alternatives, prerequisites),
usage examples (top-level `/yf-plan`, `/yf-research`, `yf skills install`, beads loop). Salvage
usable prose from the retiring `website/docs/`.

**AWS provisioning (naba-cloned, gated).** `web/scripts/provision_aws.sh` (idempotent: private
S3 bucket `yoshikoflow.sh`, CloudFront OAC, ACM cert in us-east-1 DNS-validated via the existing
zone, CloudFront Function for pretty-URL rewrite, distribution with `/install.sh` no-cache
behavior, bucket policy, Route53 A/ALIAS) + `web/scripts/aws/{index-rewrite.js,ci/*}`. Run
behind a **capability gate** (billable go-live step). The CI deploy uses a GitHub OIDC role
(`web/scripts/aws/ci/`), no long-lived keys.

**Version-publishing → web deploy.** `.github/workflows/web-deploy.yml`: `workflow_dispatch` +
`workflow_run` on "Release" completed → OIDC auth → build Pelican → `aws s3 sync --delete` +
CloudFront invalidation + re-mirror `install.sh`. A `v*` tag → cargo-dist Release → web deploy,
exactly as naba chains it.

**Install-default switch.** `web/scripts/sync_installer.sh` mirrors cargo-dist's `yf-installer.sh`
(pinned to the release tag) to `web/content/extra/install.sh` → served at
`https://yoshikoflow.sh/install.sh`. Un-suppress and rewrite the README install section so the
recommended CLI install is `curl --proto '=https' --tlsv1.2 -LsSf https://yoshikoflow.sh/install.sh | sh`,
Homebrew + from-source demoted to alternatives.

**Secrets/config.** `web/.envrc.example` (committed) documenting `YOSHIKOFLOW_SITE_DOMAIN`,
`PUBLISH_URL`, `YOSHIKOFLOW_CF_DISTRIBUTION`, `YOSHIKOFLOW_HOSTED_ZONE_ID`, optional
`YOSHIKOFLOW_GA_MEASUREMENT_ID`, with an optional `op read "op://Y-Home/..."` sourcing pattern.
Real `.envrc` gitignored. CI secrets set via `gh secret set` (incl. `AWS_DEPLOY_ROLE_ARN`).

**Supersede cleanup.** Remove `website/` and `.github/workflows/docs-deploy.yml`; update any
references. Reconcile closes #28 and #54.

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

## Gates

### Start Gate (mandatory)
- Type: human
- Approvers: operator

### Capability Gate: AWS go-live provisioning
- Type: human
- Approvers: operator
- Condition: Operator authorizes running billable AWS provisioning for yoshikoflow.sh (S3, CloudFront, ACM, Route53) against account 534185824505.
- Test: `aws sts get-caller-identity` returns account `534185824505` AND `aws route53 list-hosted-zones --query "HostedZones[?Name=='yoshikoflow.sh.']" --output text` is non-empty.
- Blocks: 7.2, 7.3, 7.4
- Instructions: Confirm AWS credentials target the intended account and that provisioning cost/DNS changes are approved, then resolve the gate.

### Reconcile Gate (upstream issues incorporated)
- Type: auto (all execution beads closed)
- Blocks: reconcile step (close #28, #54 with supersede pointers to yoshikoflow.sh)

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
