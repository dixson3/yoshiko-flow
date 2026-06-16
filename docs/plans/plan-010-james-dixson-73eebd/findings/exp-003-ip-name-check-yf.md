# Finding exp-003: IP / naming check for `yf` + final name decision

Date: 2026-06-14. Follow-up to exp-002 (which checked `yflow` and found an active same-domain
PyPI `yflow` CLI collision). Operator switched the binary to **`yf`**; this is the `yf` check.

## Verdict: low risk — `yf` is clear on the axes that matter for a 2-letter command

| Axis | Result | Detail |
|:-----|:-------|:-------|
| Homebrew formula `yf` | **clear** | `formulae.brew.sh/api/formula/yf.json` → 404; scanned the full 8,437-formula index — zero `name`/`alias`/`oldname` match; no formula ships a `bin/yf` |
| Shell builtin / alias / binary | **clear** (strongest) | not a bash/zsh builtin; not coreutils/stock; `type yf`/`which yf` → not found; not a default oh-my-zsh alias |
| crates.io `yf` | **free** | API: crate does not exist — good for the cargo crate name |
| RubyGems `yf` | **free** | 404 |
| Go modules `yf` | **free** | no notable module/command |
| npm `yf` | taken, inert | `yf@0.0.1` (2014), no `bin` field, ~13 dl/mo — registry slug only, no CLI |
| PyPI `yf` | taken, inert | dict-inspection **library**, no console-script — no `yf` command |
| GitHub | low | `BillGatesCat/yf` — abandoned Yahoo-Finance CLI, 21★, last push 2021; no brew formula. Only namesake `yf` *command* and it's finance-adjacent + dormant |
| Trademark | clear | no notable software "yf" mark; 2-letter strings rarely protectable for software |

## Decision

Binary = **`yf`**. Rationale: clean on Homebrew + the shell-collision axis (the two that matter
most for a 2-letter command), free on crates.io (cargo crate name), and it matches the `yf-` skill
prefix so the surface reads naturally: `yf skills install`, `yf doctor`, `yf preflight <skill>`.

Consistency: binary `yf`, integrity marker `<!-- yf-skills: v=… tree=… -->`, runtime state root
**`.yf/`** (operator chose `.yf/` over `.yflow/`), formula `dixson3/tap/yf`. Product/brand name
remains **Yoshiko Flow**; the docs site target is still `yoshiko-flow.github.io`.

## Residual (non-blocking)

- Any 2-letter command can be shadowed by a user's personal shell alias — unavoidable, not a
  project-level conflict.
- npm/PyPI `yf` slugs are occupied (dormant, no CLI). Irrelevant for a Homebrew binary; only
  matters if we ever publish to npm/PyPI under the exact slug `yf`.
- Re-run a `brew install yf` namespace check at formula-submission time.

## Sources

formulae.brew.sh/api/formula/yf.json (404) · formula index (scanned) · crates.io/api/v1/crates/yf
(404) · rubygems gems/yf.json (404) · npmjs.com/package/yf · pypi.org/project/yf ·
github.com/BillGatesCat/yf (21★, 2021).
