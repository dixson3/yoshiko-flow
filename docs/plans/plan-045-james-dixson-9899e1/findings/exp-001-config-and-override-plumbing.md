---
type: Finding
okf_spec: OKF-PLAN
id: exp-001-config-and-override-plumbing
plan: plan-045-james-dixson-9899e1
created: '2026-08-17'
---

# exp-001 — Config plumbing and the per-invocation override (D-1)

**Question:** How does yf-plan read per-repo config, and what would adding an `autonomy` key plus a per-invocation override actually cost?
**Method:** source trace of `plan_manager.py`, empirical probe of the three-tier reader in a temp repo, and a full audit of how existing invocation flags (`--force`, `--retro`) are honored. Read-only.

## Headline — two facts that shape the whole design

1. **Adding the config key is nearly free.** The reader already merges *unknown* keys across
   three tiers. The work is one `_resolve_autonomy()` helper (~10 lines, modeled verbatim on
   `_resolve_landing_strategy`), one levels tuple, one default constant. **There is no schema to
   update, because there is no schema.**
2. **`--force` is 100% prose-interpreted. There is no argv anywhere in the invocation path.**

## The three-tier reader (measured)

`_resolve_landing_strategy()` → `_read_config()` → `_bootstrap_config()`:

```python
cfg: dict = {}
for path in reversed(CONFIG_TIERS):
    try:
        if path.exists():
            loaded = json.loads(path.read_text())
            if isinstance(loaded, dict):
                cfg.update(loaded)
    except (json.JSONDecodeError, OSError, ValueError):
        continue
```

`CONFIG_TIERS` = `.yf/plan/config.local.json` → `.yf/plan/config.json` → `.yf-plan.local.json`.

Probe with tier 1 valid, **tier 2 deliberately malformed**, tier 3 valid:

```
_read_config: {"validate-cmd":"make test","landing-strategy":"feature-branch",
               "execute.worktree":false,"ignore-skill":false}
unknown key ignored: <absent>
```

Absent → skipped. Malformed → caught and skipped **silently**. Non-dict → dropped. Per-key merge
confirmed (tier-1's `landing-strategy` won; tier-3's `validate-cmd` survived). Design intent is
explicit in the docstring: *"deliberately total: a malformed or unreadable tier is skipped, never
raised, so a bad config file cannot make the module unimportable."*

**Validation is per-resolver, defensive-at-read** — each `_resolve_*` re-type-checks its own key
and falls back. Unknown keys pass through untouched with **no diagnostic**.

**Latent bug a new key inherits:** `CONFIG_TIERS` are **relative** `Path`s, so config resolves
against **CWD**, not repo root — while `yf/src/preflight.rs::read_config` uses
`env.repo_root.join(...)`. Running from a subdirectory silently sees no config.

## Every key honored today

| Key | Reader | Default | Consumer |
| :-- | :-- | :-- | :-- |
| `ignore-skill` | **Not read by `plan_manager.py` at all** — lives in Rust `preflight.rs` | falsy | SKILL.md Pre-flight |
| `plans-root` | `PLANS_DIR` — **import-time only**, from `_CONFIG` | `docs/plans` | §1.2 |
| `incubator-root` | `INCUBATOR_PARENT` — import-time only | `Incubator` | §1.2 |
| `execute.worktree` | `_worktree_opted_out()` (tolerates flat + nested) | `true` | `worktree ensure` → `opted-out` |
| `validate-cmd` | `_resolve_validate_cmd()` | `None` | §6.1.5 tier 2 — **and** `change_validation.py`, which reads the same tiers in the same order |
| `landing-strategy` | `_resolve_landing_strategy()` | `main` | `_resolve_execute_base` (mechanical) + §4.4/§6.1 merge target (**prose**) |

`landing-strategy` being **half-mechanical, half-prose** is the direct precedent for `autonomy`.

**Doc drift to budget for:** `spec/data.md` REQ-DATA-021 still asserts *"`ignore-skill` … is the
only config key"* — stale; six exist. This repo itself has **no** yf-plan config file, so it runs
entirely on defaults.

## Issue #100 is CLOSED and done in code — the docs are not

`gh issue view 100` → `CLOSED 2026-08-14`. Three-tier per-key merge is delivered in both readers;
`STATE_DIR = YF_DIR` (`.yf/plan/`) with `_migrate_state_dir()` at import; covered by
`test_config_tiers.py`.

**Four stale doc sites still describe the pre-#100 world**, and any config-touching plan will trip
`yf-drift-check` on them:

- `SPEC.md` §3 — *"`plan_manager.py` still reads config only from the legacy root…"*
- `spec/cli.md` REQ-CLI-005 — *"currently reads only the legacy root `.yf-plan.local.json`"*
- `spec/data.md` REQ-DATA-021 — the "only config key" claim
- `SKILL.md` Pre-flight — *"which `plan_manager.py` **will** read after #100"*

> Budget a separate issue for the #100 doc reconciliation, independent of the autonomy feature.

**Where `autonomy` should live:** reads are free from any tier. Writes should target
`.yf/plan/config.local.json` — the `.gitignore` carve-out (`!/.yf/*/config.json`) makes
`config.json` committable/shared and `config.local.json` machine-local, and autonomy is an
operator preference like `execute.worktree`. A team could still commit a conservative default in
`config.json`; the tier model supports it. *(Inferred from the carve-out + the module's own
"a local file … must not mask a committed `plans-root`" rationale; no requirement states it.)*

## The hard part: there is no argv

**`/yf-plan execute --force` is honored entirely by the model reading the invocation string.**

- The Invocation list does not even document `--force`: *"`/yf-plan execute [<plan-id>]` — begin
  execution (new session)"*.
- `resume-scan`'s full option surface is `plan_dir` + `--json-output`. It **reports**
  `stale_approved`; it never decides.
- SKILL.md §5.2 instructs the model in prose: *"The only bypass is an explicit `/yf-plan execute
  --force`, which proceeds **and logs the override**"* — then runs the *generic* `update-status`
  verb with a `-m` message the model composes.
- The same pattern holds for `approve --force` and `capture --force`.

**The one partial exception is the seam to copy.** `capture --retro` is prose-detected but
*plumbed into the script* — REQ-CLI-011: *"`--retro` is plumbing only… it surfaces a `"retro"`
boolean in the output… but does not alter the mechanical verdict."*

### Recommended split

1. **Prose detects the token** (as `--force` does today) — unavoidable, no argv exists.
2. **A script validates and resolves it**, applying precedence `flag > config.local > config.json
   > legacy > default` and emitting the effective value as JSON.
3. **The coordinator consumes only resolved JSON**, never the raw invocation.

This is strictly better than the `--force` precedent because validation and defaulting become
**testable**; only token-detection stays LLM-judgment. Mitigate the residual (a misread
invocation) the way `--force` does — echo the resolved value into `log.md` so a misdetection is
auditable.

## Two structural facts for the coordinator

**`agents/coordinator.md`'s declared `## Inputs` are only `EPIC` and `plan_dir`.** An ambient
autonomy setting must become a **third declared input** (cleaner, matches how `plan_dir` flows) or
be re-resolved by the coordinator from `plan_dir`-adjacent config.

**The DAG drain today has ZERO operator checkpoints.** The only `AskUserQuestion` in all of
SKILL.md is the §5.2 resume/new prompt. So:

> The between-epic stops the operator observes are **not** explicit prompts — they are the model
> ending its turn because of the reporting language. That confirms the diagnosis (turn-ending
> prose, not gates), and it means **`--checkpoint` is genuinely new behavior**, not a toggle over
> something existing. It needs new prose in the Loop, most naturally between step 5 (spawn
> sub-agent) and step 6 (`bd close`) — the same seam exp-002 identifies for the attempt counter.

## No config-resolving verb exists

22 top-level commands + 3 groups; none is `config`. `yf` has no `config` subcommand either.
Every effective-config resolution is an internal `_resolve_*` helper **with no CLI surface** — the
prose layer cannot ask "what is the effective landing strategy?", only observe its effect.

A `config resolve --json` verb would be **the first of its kind**, and would retroactively benefit
`landing-strategy` (whose merge-target half is prose re-deriving what the script already knows).
Conventions it must follow: `--json-output`/`--json` dual alias; **JSON to stdout on every path
including failure** (REQ-CLI-016 — a verb captured with `GATE=$(…)` printed an empty string on
exactly the path an operator needed); exit 0 unconditionally for a pure read (precedent:
`audit-close`). A `source` discriminator per key has precedent in `change_validation.py`'s
validate-cmd seed. *(Shape below is synthesis — no such verb exists, no spec prescribes it.)*

## Next-free REQ ids (measured)

| Namespace | Next free | Note |
| :-- | :-- | :-- |
| `REQ-CLI-*` | **020** | contiguous 001–019 |
| `REQ-PLAN-*` | **077** | suffixed variants `069a/b` exist |
| `REQ-PHASE-*` | **006** | only 001–005 |
| `REQ-AGENT-*` | **064** (or **049** in the 040-band) | **deliberately banded, not contiguous** — gaps are per-agent padding, not free slots *(inferred; no explicit statement of the convention)* |
| `REQ-RESUME-*` | **005** | |
| `REQ-BRANCH-*` | **004** | where `landing-strategy` lives — arguably where an execute-scoped `autonomy` belongs |
| `REQ-SAFE-*` | **do not use** | belongs to **yf-beads-upstream**, not yf-plan; introducing it here collides by name across skills |
