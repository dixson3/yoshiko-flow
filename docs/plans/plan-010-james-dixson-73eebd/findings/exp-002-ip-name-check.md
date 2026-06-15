# Finding exp-002: IP / naming-conflict check for `yflow`

Date: 2026-06-14. Method: web search across Homebrew, OS binaries, package registries
(PyPI/npm/crates.io/RubyGems/Go), GitHub, and trademark/domain. Full sources at bottom.

## Verdict: moderate-low risk, with ONE real same-space collision

| Axis | Result | Detail |
|:-----|:-------|:-------|
| Homebrew formula `yflow` | **clear** | `formulae.brew.sh/formula/yflow` → 404; not in core or known taps |
| OS / coreutils binary | **clear** | not a builtin/coreutils/known binary on macOS or Linux |
| PyPI `yflow` | **COLLISION** | "The Makefile for AI workflows", v0.6.3.1, released **2026-06-03**, MIT, **installs a `yflow` binary on PATH** (`yflow init`, `yflow run`). Same domain (dev/AI tooling). alanpaul1969/yflow |
| npm `yflow` | low | "async flow control", v0.1.1 (2022), dormant, no CLI |
| crates.io `yflow` | **free** | 404; only unrelated `yewflow` exists |
| RubyGems `yflow` | **free** | 404 |
| Go `…/yflow` | low | `leeyaf/yflow` YAML workflow *library* (not a CLI), 0 importers |
| GitHub | low | only low-star repos; no prominent CLI owns the name |
| Trademark / product | negligible | no payments/fintech "Yflow" exists; only **Yflow SD**, a **defunct nanotech** firm (unrelated field). `yflow.com` parked by that entity. No active software mark. |

## The one genuine conflict

An **actively-maintained PyPI `yflow`** (released ~11 days before this check) **also installs a
`yflow` executable** and sits in the **same space** (dev tooling / AI workflows). A user who
`pip install yflow` (or `uv tool install yflow`) **and** `brew install …/yflow` gets two different
tools fighting for `…/bin/yflow` (last-install-wins). It is alpha / low-adoption — not a hard
blocker — but it is real same-binary, same-domain overlap, and `yflow` depends on `uv`, so our
users are likely to have Python tooling in reach.

## Trademark exposure: negligible

The only "Yflow" mark is a defunct nanotechnology company in an unrelated class; trademark
protection is field-specific. For an OSS developer CLI this is essentially no practical risk.

## Options if avoiding the collision

`yfl`, `yflo`, `yf`, or an org-tied form (`yk-flow`, `yoshiko`). The repo is already
`yoshiko-flow`, and skills use the `yf-` prefix — `yf` or `yfl` keep brand alignment. Note: a
binary-name change cascades through the formula name, the `<!-- yflow-skills: … -->` marker string,
`yflow preflight`/`yflow doctor` invocations, all docs, and SPEC/GUARDRAILS — cheapest to decide
**now**, before Epic 0 authors the SPEC.

## Sources

formulae.brew.sh/formula/yflow (404) · pypi.org/project/yflow · github.com/alanpaul1969/yflow ·
npmjs.com/package/yflow · pkg.go.dev/github.com/leeyaf/yflow · crates.io (404) · rubygems (404) ·
crunchbase.com/organization/yflow · yflow.com.
