# Exp 002 — yf-plan §6.1.5 delegation surface

**Question:** How does `validate-merged` read `validate-cmd` today (layer b), and what is the
cleanest delegation contract so `yf-change-validation` supersedes it while `validate-cmd` stays a
thin fallback?

## Key finding: the seam is PRE-SANCTIONED

`plan_manager.py:879-884` already records the extraction trigger — **`yf-change-validation` IS the
foreseen "acceptance" skill**, and the contract is explicitly a **prose soft-dependency**
(detect-and-delegate; present → delegate, absent → fallback). Verbatim:

> `* acceptance skill — extract the validate-merged / validate-cmd seam (below) ONLY when a
> second skill needs merged-state/regression validation. When extracted, the consumer keeps a
> PROSE soft-dep (present → worktree flow; absent → in-place) … NEVER add worktree/acceptance to
> a SKILL.md frontmatter depends-on-skill edge — that is force-install, the wrong coupling.`

## The code today

- `_validate_merged(plan_dir)` at `plan_manager.py:1316-1343`; Click wrapper `validate_merged_cmd`
  at `1396-1412` (emits `json.dumps(result, indent=2)`, **exits 3 when `status != "pass"`**).
- `_resolve_validate_cmd()` (`918-925`) reads the single flat key `"validate-cmd"` from
  `.yf-plan.local.json` via `_read_config()` (`597-599`). Non-string/blank → `None`.
- **Asymmetric layer split:** `_validate_merged` owns **layer (b) only** (the project suite). When
  `validate-cmd` is `None` it runs **no suite** and returns `status:"pass"` + the verbatim
  "CROSS-PLAN REGRESSIONS NOT CHECKED" notice. **Layer (a)** (the plan's own Gate `Test:` cmds) is
  driven by SKILL §6.1.5 prose / the coordinator, *not by this function*.
- Output schema (must stay stable): `{plan_dir, validate_cmd_configured, layer_b, notice, status}`.
- `.yf-plan.local.json` keys in use: `ignore-skill` (bool), `validate-cmd` (str),
  `execute.worktree` (bool, flat or nested).

## The delegation contract (where + how)

**Insertion point:** a new precedence tier *ahead of* the `validate-cmd` logic, at
`_validate_merged` line ~1327 (right after `validate_cmd = _resolve_validate_cmd()`). Three tiers:

1. **`yf-change-validation` engine present** (detected by an **approved** `CHANGE-VALIDATION.md`
   manifest at repo root — mirroring the `DRIFT-CHECK.md` precedent) → invoke its engine over the
   merged tree; map its PASS/FAIL onto `status`/`layer_b`.
2. **else `validate-cmd` configured** → `_run_shell(validate_cmd)` (today's behavior).
3. **else** → layer-(a)-only `pass` + the verbatim not-checked notice (today's behavior).

- Keep the `{plan_dir, validate_cmd_configured, layer_b, notice, status}` schema + exit-3 contract
  unchanged; add a discriminator key (e.g. `engine: "change-validation"|"validate-cmd"|"none"`) so
  SKILL prose can surface which tier ran.
- All inputs are already in-scope at the seam (`plan_dir`, `_read_config`, `_resolve_validate_cmd`,
  `_run_shell`, `_read_json`, repo-root). **No `yf` Rust change.**

## Route as a SKILL, not a `yf` subcommand

The `yf` crate scopes itself to skill install/upgrade/verify/preflight (`yf/src/preflight.rs:11-17`,
GR-005 kernel/skill boundary): "per-skill audit/pour stays in each skill's Python." `yf` never
shells out to `plan_manager.py` for runtime ops. Running a project's suite over a merged tree is
**per-skill runtime behavior** → a skill with a Python engine + per-repo manifest (mirroring
`yf-drift-check`'s `DRIFT-CHECK.md` model). `yf doctor`/`yf preflight` could at most *detect/report*
a `CHANGE-VALIDATION.md`, not run it.

## Flag for plan authors

SKILL §6.1.5 prose says "when unset, validate-merged runs **layer (a) only**" but the code runs
**no** suite when unset (layer (a) is the coordinator's separate responsibility). Preserve the
*actual* contract when wiring delegation; optionally correct the prose as a docs sub-task.
