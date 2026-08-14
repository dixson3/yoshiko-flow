---
type: Finding
okf_spec: OKF-PLAN
---
# Experiment 2: The `plan_manager.py` local patch and the canonical-config reality

**Question.** What exactly is the local patch (#107), what does the repo's current config
read actually do, and how must #107 and #100 be sequenced?

## The isolated local patch

Diffed against its closest ancestor `0b0cc78c`, the entire local delta is one hunk
replacing two module constants:

```python
# repo (both at line 34-35)
PLANS_DIR = Path("docs/plans")
INCUBATOR_PARENT = Path("Incubator")
```

```python
# user-scope
PROJECT_CONFIG_FILE = Path(".yf-plan.json")        # committed layout decisions
LOCAL_CONFIG_FILE = Path(".yf-plan.local.json")    # operator overrides (gitignored)

def _bootstrap_layout() -> dict:
    """Layout config: committed `.yf-plan.json`, then `.yf-plan.local.json` override.

    Read at import time because PLANS_DIR / INCUBATOR_PARENT are module constants.
    Deliberately dependency-free — it runs before `_read_json` is defined. Both
    paths are CWD-relative, matching the constants they configure.
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

28 added lines, 2 removed, no other change anywhere in the file. It is well-formed: it
degrades to the current defaults when no config exists, swallows malformed JSON rather than
crashing at import, and documents why it cannot use `_read_json` (defined later in the file).

The motivating use case, per #107: a repo that is also an Obsidian vault, where a visible
top-level `Incubator/` folder trips the vault's own structure linter.

## Two properties that constrain how it lands

1. **Import-time evaluation.** `PLANS_DIR` / `INCUBATOR_PARENT` are module constants read at
   import, so config resolution must happen before most of the module exists. Any
   re-implementation inherits this constraint or must convert the constants into functions —
   a much wider change touching every call site.
2. **CWD-relative.** Both the config paths and the constants they set are relative to the
   process working directory. This matches the existing behavior, but means a
   `plan_manager.py` invoked from a worktree resolves config from that worktree.

## The repo's current config read (what #100 is about)

```python
SKILL_NAME = "yf-plan"
CONFIG_FILE = Path(f".{SKILL_NAME}.local.json")   # → .yf-plan.local.json  (legacy root)
STATE_DIR   = Path(".yf") / SKILL_NAME            # → .yf/yf-plan/         (FULL name)

def _read_config() -> dict:
    return _read_json(CONFIG_FILE) if CONFIG_FILE.exists() else {}
```

`_read_config()` has exactly three call sites (lines 1646, 1660, 1674 — the
`landing-strategy`, `validate-cmd`, and `execute.worktree` resolvers). `STATE_DIR` backs
`LANDING_LOCK` (line 2058).

The Rust binary is the ground truth and disagrees on both axes (`yf/src/preflight.rs`):
config is `.yf/<short>/config.local.json` read **canonical-first with the legacy root
dotfile as fallback**, and state is `.yf/<short>/preflight.json` — where `<short>` is the
`yf-`-stripped name (`plan`, not `yf-plan`). So today an operator who has migrated to the
canonical layout has `landing-strategy` / `validate-cmd` / `execute.worktree` **silently
ignored**, and one skill's state is split across `.yf/plan/` and `.yf/yf-plan/`.

## Sequencing conclusion

The local patch is built on the legacy root-dotfile idiom the repo has already superseded.
Porting it verbatim would add a **third** config reader on the deprecated surface, directly
re-creating the drift #100 exists to remove. Therefore:

**#100 must land before #107.** The order is:

1. Fix `_read_config()` to canonical-first (`.yf/plan/config.local.json`, legacy fallback)
   and `STATE_DIR` to the short name, with migration of any existing `.yf/yf-plan/` state.
   This yields a single canonical config reader.
2. Re-express the #107 patch as a **consumer of that reader** — `plans-root` /
   `incubator-root` keys resolved canonical-first — rather than its own bespoke
   `.yf-plan.json` loader.

The import-time constraint (property 1) is the one real friction: the shared reader is
defined later in the module than the constants that need it. Resolving that is the first
implementation task, and the options are to hoist a minimal dependency-free reader to the
top (what the local patch already does, generalized) or to make the roots lazily resolved.
The plan does not pre-commit to one; it makes the choice an explicit issue.

Note the local patch also introduces a **committed** `.yf-plan.json` tier (shared layout
decisions) distinct from the gitignored local override. The canonical `.yf/` tree is
entirely gitignored, so a committed layout decision has no canonical home today. Whether
`plans-root` is a shared-and-committed or local-only decision is a genuine open question the
plan must settle — it is the same commit-semantics problem #102 raises for the
markdown-lint marker.

## Third consumer: #101

`skills/yf-change-validation/scripts/change_validation.py:44` reads yf-plan's `validate-cmd`
seed from the legacy root dotfile only. It is the same precedence bug in a second file. Once
#100 produces a canonical-first reader, leaving this call site legacy-only re-creates the
drift being fixed, so #101 is included as that reader's second consumer.
