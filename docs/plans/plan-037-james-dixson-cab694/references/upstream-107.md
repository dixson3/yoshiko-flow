---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #107: yf-plan: make PLANS_DIR and INCUBATOR_PARENT configurable (currently hardcoded)

- **Number:** 107
- **Title:** yf-plan: make PLANS_DIR and INCUBATOR_PARENT configurable (currently hardcoded)
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## Problem

`plan_manager.py` hardcodes both plan roots as module-level constants:

```python
PLANS_DIR = Path("docs/plans")
INCUBATOR_PARENT = Path("Incubator")
```

There is no config key, no env var, and no CLI flag to change them. `--incubator <slug>`
selects *which* incubator, not *where* the incubator parent lives.

This is inconsistent with `yf-incubator`, whose `incubator-index.py` already exposes
`--root` (default `Incubator`) for exactly this purpose. The two halves of the same
workflow disagree on whether the root is configurable.

## Why it matters

The constants are CWD-relative, so today the only workaround is to run every
`plan_manager.py` invocation from a different working directory — which changes the
meaning of every `plan_dir` argument, and only works if the desired parent is literally
named `Incubator`.

Concrete case: a repo that is *also* an Obsidian vault, where a visible top-level
`Incubator/` folder is not acceptable. It would appear in the writer's file explorer and
trip the vault's own OKF structure linter (a non-dot top-level folder containing `.md`
files must be registered in the root `index.md` and in `AGENTS.md`). The engineering
artifacts need to live under a dot-prefixed root such as `.yoshiko-flow/Incubators/`,
which no amount of CWD juggling can produce.

More generally: any project that wants plans somewhere other than `docs/plans/` has no
supported option.

## Suggested fix

Resolve both constants from config, honouring the Skill Surface Convention §3 split —
committed `.yf-plan.json` for repo layout, `.yf-plan.local.json` for operator overrides:

```python
PROJECT_CONFIG_FILE = Path(".yf-plan.json")        # committed layout decisions
LOCAL_CONFIG_FILE = Path(".yf-plan.local.json")    # operator overrides (gitignored)


def _bootstrap_layout() -> dict:
    """Layout config: committed `.yf-plan.json`, then `.yf-plan.local.json` override.

    Read at import time because PLANS_DIR / INCUBATOR_PARENT are module constants.
    Deliberately dependency-free — it runs before `_read_json` is defined.
    """
    cfg: dict = {}
    for path in (PROJECT_CONFIG_FILE, LOCAL_CONFIG_FILE):
        try:
            if path.exists():
                cfg.update(json.loads(path.read_text()))
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


_LAYOUT = _bootstrap_layout()

PLANS_DIR = Path(_LAYOUT.get("plans-root", "docs/plans"))
INCUBATOR_PARENT = Path(_LAYOUT.get("incubator-root", "Incubator"))
```

Project config:

```json
{
  "incubator-root": ".yoshiko-flow/Incubators",
  "plans-root": ".yoshiko-flow/plans"
}
```

Note this puts *layout* in the committed `.yf-plan.json` rather than the gitignored
`.yf-plan.local.json` — the root is a repo fact every clone needs, not an operator
preference. `_read_config()` currently reads only the local file.

## Verified

Applied locally against `plan_manager.py`. `init --incubator bookpipe-skills` from the
repo root now yields:

```
plan_dir: .yoshiko-flow/Incubators/bookpipe-skills/plans/plan-001-james-dixson-2e7215
```

Defaults are unchanged when no config file is present (confirmed by running `list` from a
directory with no `.yf-plan.json` — still `docs/plans` / `Incubator`).

## Also worth considering

- `PLANS.md` / `SKILL.md` document the roots as fixed (`docs/plans/<plan-id>/` and
  `Incubator/<slug>/plans/<plan-id>/`); both would need a line noting they are the
  defaults.
- Aligning `incubator-index.py --root` to read the same config key would make the two
  skills agree without the caller passing `--root` on every call.

