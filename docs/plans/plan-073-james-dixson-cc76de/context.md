---
type: Environment
okf_spec: OKF-PLAN
---
# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

**yoshiko-flow** (`dixson3/yoshiko-flow`) ships the `yf` CLI and a set of agent skills that `yf`
installs into coding-agent harnesses (claude-code, codex, opencode, pi, agents).

- **CLI:** Rust, a single crate in `yf/`. It embeds `skills/` with `rust-embed` in release
  builds; debug builds read `skills/` from disk.
- **Skills:** each is a `skills/<name>/SKILL.md` plus PEP 723 Python helpers run with `uv`.
- **Distribution:** cargo-dist via `.github/workflows/release.yml`, triggered by pushing a
  `v<semver>` tag. It publishes the GitHub release and the `dixson3/homebrew-tap` formula,
  then chains `web-deploy.yml` (Pelican → S3/CloudFront, yoshikoflow.sh).
- **Validation:** `CHANGE-VALIDATION.md` (FAST and FULL tiers) and `DRIFT-CHECK.md`.
- **Conventions:** `AGENTS.md` mandates SPEC-first (requirements in `SPEC.md` and per-skill
  `skills/<name>/SPEC.md` plus `spec/` before code). The shell is zsh. Task tracking is `bd`
  (beads).
- **Deploy discipline:** never `yf skills install` / `yf self install` mid-execution. Deploy
  at land-the-plane from clean, synced `main` only.

## Tool inventory

<!-- snapshot: host=d3-mbp-m5.local date=2026-10-15 -->

- `bd`: bd version 1.3.1 (Homebrew)
- `git`: git version 2.54.0 (Apple Git-157)
- `uv`: uv 0.12.22 (70fe1196a 2026-10-01 aarch64-apple-darwin)
- `python`: Python 3.14.2
- `gh`: gh version 2.102.0 (2026-09-30)
- `glab`: glab 1.120.0 (78790114c)
- `claude`: 2.1.288 (Claude Code)
- `cargo`: cargo 1.99.0 (Homebrew)
- `yf` (installed): yf 0.5.0 (5677780-dirty). This is a pre-0.5.0-tag dev build; the published
  v0.5.0 is `1eba35d`
- `herdr`: 0.9.3 (optional, used for operator-authorized landing tabs only)
- `pi`: 1.3.0
- `d2`: v0.9.0
- OS: macOS 27.0.1 (arm64)

## Paths

- Repo root: `/Users/james/workspace/dixson3/yoshiko-flow`
- Working directory at plan creation: `/Users/james/workspace/dixson3/yoshiko-flow`
- Plan directory: `docs/plans/plan-073-james-dixson-cc76de`

## Operator identity

- Git user: `james-dixson` (James Dixson, dixson3@gmail.com, GitHub `dixson3`)
- Role: repository owner and sole maintainer. Holds release authority: the `v0.6.0` tag push
  and the `release-authorized` gate are this operator's decision alone.

## Runtime assumptions

- **Platform:** macOS or Linux with zsh or bash. The plan's shell fragments are written to
  behave identically in both (AGENTS.md).
- **Toolchain:** Rust stable and `uv` with managed Python 3.14.
- **Tools:** `bd` ≥ 1.1.0, with the repo's beads DB healthy (`yf preflight yf-beads-init` →
  `ok`).
- **Network:** GitHub (git push, `gh` API, Actions) and crates.io for the build.
- **Model API access:** the FULL tier's trigger-eval row drives `claude` and `pi` against a
  shared model account. It is throttled to 150 runs/h, takes about 5 h and costs roughly
  $75–110 at CC list rate.
- **Credentials:** `gh` authenticated as `dixson3` with `repo` and `workflow` scopes. No
  credential is read or written by the plan itself. The release workflow uses the repo's
  `HOMEBREW_TAP_TOKEN` and AWS OIDC secrets, which already exist.
- **Side effects:** Epics 0–4 are local commits on `<plan-id>-execute`. Epic 5 pushes a tag,
  which is irreversible and publishes a release, a tap formula and the website. That push
  happens only behind the `release-authorized` human gate.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
