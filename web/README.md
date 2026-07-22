# yoshiko-flow website (`web/`)

The source for **https://yoshikoflow.sh** — a bespoke [Pelican](https://getpelican.com)
static site with a dark terminal/technical theme, published to AWS (private S3 + CloudFront +
ACM + Route53).

```text
web/
├── pelicanconf.py          # dev config (pretty directory-style URLs, theme, menu)
├── publishconf.py          # prod overrides (SITEURL=https://yoshikoflow.sh)
├── requirements.txt        # pinned Pelican + sitemap + markdown + PyYAML
├── Makefile                # devserver / validate / publish / deploy / provision
├── content/
│   ├── pages/              # install, usage, architecture, lifecycle, 404 (home is the index template)
│   ├── home/hero.md        # homepage hero content (name, install cmd, CTAs, description)
│   ├── cards/              # homepage feature cards, one markdown file each
│   ├── skills/             # optional per-skill intro overrides (merged over generated pages)
│   └── extra/              # robots.txt, staged install.sh (site-root files)
├── plugins/
│   ├── home_content.py     # local plugin: hero.md + cards/*.md -> HOME_HERO / HOME_CARDS
│   └── skill_pages.py      # local plugin: skills/*/SKILL.md -> one page per skill + /skills/ index
├── themes/yoshikoflow/     # bespoke theme: templates + one hand-authored CSS file
├── scripts/
│   ├── sync_installer.sh   # stage the hosted install.sh from a cargo-dist release
│   ├── provision_aws.sh    # idempotent AWS provisioning (gated, billable)
│   └── aws/index-rewrite.js# CloudFront viewer-request Function (pretty-URL rewrite)
└── docs/provisioning-runbook.md
```

## Develop

```bash
cd web
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt

make devserver        # serve + live-reload at http://localhost:8000
```

Edit `content/` and `themes/yoshikoflow/`; the dev server regenerates on change.

### Homepage content

The homepage is the `index` direct template (`themes/yoshikoflow/templates/index.html`),
kept structural on purpose — its content lives in markdown, not the theme. The
`home_content` plugin (`plugins/home_content.py`) reads the files below and exposes them to
`index.html` as `HOME_HERO` / `HOME_CARDS`. Neither is published as a standalone page.

- **Hero** — `content/home/hero.md`. Metadata drives the name (`Name`, `Glyph`), the install
  command (`Install`), and the CTA buttons (`Cta: label | href | flags`, where `flags` may be
  `primary`/`external`); the markdown body is the description. The tokens `{install_url}`,
  `{github_url}`, `{site_url}` are substituted per-build from settings, so URLs stay
  config-driven across dev/prod. The hero **tagline** is `SITESUBTITLE` in `pelicanconf.py`.
- **Feature cards** — one markdown file each under `content/cards/*.md`. Metadata drives the
  card (`Title`, `Href`, `Glyph`, `Order`, `Command`); the markdown body is the blurb. Cards
  are sorted by `Order`. Add, remove, or reorder a card by editing files in `content/cards/`.

### Skill pages (auto-generated)

The `skill_pages` plugin (`plugins/skill_pages.py`) reads every `skills/*/SKILL.md` in the
repo root at build time and emits one page per skill plus a grouped `/skills/` index. The
single source of truth is the `SKILL.md` frontmatter (`name`, `description`, `skill-group`),
so the count and descriptions on the site never drift from the installed skills. To add a
hand-authored intro above a generated skill page, drop `content/skills/<name>.md` — its body
is layered over the generated content (see `plugins/skill_pages.py`).

## Validate

```bash
make validate         # production build into a throwaway dir; non-zero on any build error
```

This is the CI build gate. It does not touch the dev `output/` tree.

## Provision (gated, billable)

Creates the live AWS stack (private S3 bucket, CloudFront OAC + distribution, ACM cert in
us-east-1, CloudFront Function, Route53 alias). **Billable** — run only after the go-live
gate. Idempotent (check-before-create); safe to re-run.

```bash
make provision        # == ./scripts/provision_aws.sh
```

Captured resource ids are persisted to gitignored `.aws-provision-state.json`. The script
prints the CloudFront distribution id to set as `YOSHIKOFLOW_CF_DISTRIBUTION` (local `.envrc` +
GitHub repo secret) — the Makefile and CI read it from there. Full steps, verification, and
the **teardown/rollback** inverse are in [`docs/provisioning-runbook.md`](docs/provisioning-runbook.md).

## Deploy

```bash
make deploy           # s3_upload (site) + sync_installer (install.sh, short TTL) + invalidate
```

- `make s3_upload` — `aws s3 sync --delete` the built site, then invalidate `/*`.
- `make sync_installer` — stage `install.sh` (via `sync_installer.sh`) and re-upload **that
  one key** with `Cache-Control: max-age=300`, then invalidate `/install.sh`.
- `make invalidate` — invalidate the mutable paths on demand.

## Infrastructure identifiers (env vars / secrets)

Every account-specific / infrastructure value is read from the **environment** — nothing is
hardcoded in committed files. Locally they come from the repo's gitignored `.envrc` (direnv);
canonically they live as **GitHub repo Secrets** (masked in this public repo's Actions logs).
All fail closed when a required value is unset. See `.envrc.example` for the full list and an
optional 1Password (`op read`) sourcing pattern.

| Env var                        | Used by                                          | Purpose |
|:-------------------------------|:-------------------------------------------------|:--------|
| `YOSHIKOFLOW_SITE_DOMAIN`      | `Makefile` (`S3_BUCKET`), `provision_aws.sh`, CI | Bare site host — S3 bucket, ACM cert, Route53 record |
| `PUBLISH_URL`                  | `pelicanconf.py` / `publishconf.py`              | Canonical public URL; becomes Pelican's production `SITEURL`. Keep `SITEURL` empty in `pelicanconf.py` so dev stays relative |
| `YOSHIKOFLOW_CF_DISTRIBUTION`  | `Makefile` (CloudFront invalidation)             | CloudFront distribution id (printed by `make provision`) |
| `YOSHIKOFLOW_HOSTED_ZONE_ID`   | `provision_aws.sh`                               | Route53 hosted-zone id for the parent domain |
| `YOSHIKOFLOW_GA_MEASUREMENT_ID`| `publishconf.py`                                 | GA4 measurement id (production build only; unset → no gtag) |
| `AWS_DEPLOY_ROLE_ARN`          | CI (`web-deploy.yml` OIDC)                        | OIDC deploy role ARN — CI secret only (local deploys use your AWS CLI creds) |

The S3 bucket defaults to `YOSHIKOFLOW_SITE_DOMAIN`; override with `YOSHIKOFLOW_S3_BUCKET` if
they ever differ. In CI, `PUBLISH_URL` is derived from the `YOSHIKOFLOW_SITE_DOMAIN` secret.
Set a secret with `gh secret set <NAME> --body <value>`.

## The GH-canonical vs site-bootstrap boundary

**GitHub Releases is canonical for every `yf` binary and for self-update.** This site hosts
exactly **one** convenience artifact: `install.sh`, a byte-for-byte mirror of cargo-dist's
`yf-installer.sh` from a pinned release tag. It exists so users get a short bootstrap:

```bash
curl --proto '=https' --tlsv1.2 -LsSf https://yoshikoflow.sh/install.sh | sh
```

The installer itself pulls sha256-checksummed tarballs from GitHub Releases, and thereafter
`yf self update` runs off GitHub. The site never mirrors binaries — it is an additive,
human-facing surface only.

### Before the first release

Until the first cargo-dist release is cut, `sync_installer.sh` stages a **fail-safe
placeholder** `install.sh` that prints a "no release yet" message and exits non-zero, so a
premature `curl | sh` fails safely. Once the first `v<semver>` tag lands, re-run `make deploy`
to activate the real installer.

## How pretty URLs resolve on a private bucket

The site uses directory-style URLs (`/install/`). A private bucket read via CloudFront OAC is
not an S3 *website* endpoint, so it does not append `index.html` to directory requests. The
CloudFront viewer-request Function (`scripts/aws/index-rewrite.js`) rewrites slash-terminated
and extension-less paths to `/index.html`; `/install.sh` passes through. See the runbook.
