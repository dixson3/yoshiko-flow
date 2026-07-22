---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

yoshiko-flow (`dixson3/yoshiko-flow`) is a Rust/cargo-dist workspace whose single crate `yf`
(a compiled CLI, currently v0.4.0) embeds a set of Claude Code skills under `skills/` via
rust-embed at build time. The skills are beads-backed (`bd`) workflow tools (yf-plan,
yf-research, the beads/markdown/utility families — 18 in total). Releases are cut by bumping
`yf/Cargo.toml` and pushing a `v*` tag; `.github/workflows/release.yml` (cargo-dist v0.32.0)
builds the platform matrix, creates a GitHub Release (including `yf-installer.sh`), and
publishes the Homebrew formula to `dixson3/homebrew-tap`. CI (`ci.yml`) runs
`cargo fmt`/`clippy`/`cargo test --workspace`. A disabled Docusaurus site exists under
`website/` (being retired by this plan). This plan adds a **Pelican** static site under `web/`
deployed to AWS (S3 + CloudFront) at https://yoshikoflow.sh, modeled on the sibling project
`naba` (`/Users/james/workspace/dixson3/naba`, its `web/` directory).

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-07-22 -->

- `bd`: bd version 1.1.0 (Homebrew)
- `git`: git version 2.50.1 (Apple Git-155)
- `uv`: uv 0.11.26 (396ef7ce4 2026-06-30 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.96.0 (2026-07-02)
- `glab`: glab 1.106.0 (fc1869c7)
- `claude`: 2.1.201 (Claude Code)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-031-james-dixson-62a375`

## Operator identity

- Git user: `james-dixson` (James Dixson)
- Contact: james@yoshikostudios.com; GitHub `dixson3`.
- Authority scope: repo owner/maintainer. Holds AWS credentials for account `534185824505`
  (IAM user `dixson3`) with authority to provision S3, CloudFront, ACM, and Route53 for
  `yoshikoflow.sh`, and to set GitHub repo secrets via `gh secret set`. Authorizes the billable
  AWS go-live step gated in Epic 7.

## Runtime assumptions

- **OS/shell:** macOS (darwin), zsh. `direnv` available for `.envrc` loading; `uv` for Python.
- **Toolchain:** Rust/cargo toolchain, Pelican (installed into `web/`'s uv/venv from
  `requirements.txt`), `aws` CLI v2 + `jq` (for provisioning), `gh` (authenticated, for secrets
  and release inspection), `git`.
- **Network:** outbound HTTPS to GitHub (releases, `gh`), AWS APIs, and PyPI (Pelican install).
- **Credentials/side-effects:** Epics 1–6 are author-only and produce **no** cloud state — safe
  to run anywhere. Epic 7 makes **billable, externally-visible AWS changes** (creates an S3
  bucket, CloudFront distribution, ACM cert, and Route53 records for `yoshikoflow.sh`) and sets
  GitHub repo secrets; it requires AWS credentials for account `534185824505` and is gated
  behind the AWS capability gate. A cold reader on a different machine/account must NOT run
  Epic 7 without those credentials and explicit authorization.
- **DNS precondition:** the `yoshikoflow.sh` Route53 hosted zone (`Z0201468FY30AYTNQWIO`)
  already exists; provisioning validates the ACM cert via a CNAME UPSERT into it.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
