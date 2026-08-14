---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #90: yf-change-validation: default recipe of actionlint + shellcheck for repos with .github/workflows

- **Number:** 90
- **Title:** yf-change-validation: default recipe of actionlint + shellcheck for repos with .github/workflows
- **URL:** 
- **State:** OPEN
- **Labels:** enhancement, type::task, priority::low

## Body

**Lesson from pybridge plan-010 / the v0.1.33 release work.**

Every workflow / embedded-shell edit was validated pre-push with `actionlint` (which also runs `shellcheck` on `run:` blocks) + `yq` for YAML sanity, and it caught real bugs before they cost a CI round-trip (shell syntax, unbound vars, bad step wiring). On self-hosted runners a bad workflow is expensive to discover (10–30 min per iteration), so cheap static checks have outsized value.

## Proposal

When `yf-change-validation` bootstraps a manifest for a repo that contains `.github/workflows/`, suggest a default recipe entry:
- **FAST/FULL:** `actionlint` over `.github/workflows/*.yml` (and, where composite actions exist, over `.github/actions/**/action.yml`).

Notes for the recipe:
- `actionlint` bundles shellcheck for embedded `run:` scripts — one tool covers both YAML and shell.
- Self-hosted runners use **custom `runs-on` labels** (e.g. `[self-hosted, macOS, ARM64, matlab, pybridge]`) that actionlint flags as unknown; the recipe/manifest should note these are expected (or provide an `actionlint.yaml` with the label list) so they aren't treated as failures.

This is an executable, exit-code-driven check — a natural fit for `yf-change-validation`'s run-and-report model.
