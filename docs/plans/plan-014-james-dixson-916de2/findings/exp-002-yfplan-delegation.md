# exp-002: yf-plan §6.1.5 delegation + validate-cmd migration

## `validate-merged` verb (`skills/yf-plan/scripts/plan_manager.py`)

- `_validate_merged(plan_dir)` (`:1316-1343`): resolves `validate-cmd` via
  `_resolve_validate_cmd()` (`:1326`); builds result `{plan_dir, validate_cmd_configured,
  layer_b, notice, status}`.
  - **Unset** (`:1333-1339`): `status="pass"`, emits the verbatim cross-plan-not-checked
    notice, returns early.
  - **Set** (`:1340-1342`): `_run_shell(validate_cmd)` (`subprocess.run(shell=True)`, captures
    `ok`/`returncode`/`output_tail[-2000:]`); `status = pass if ok else fail`.
  - **Layer (a)** is NOT here — coordinator runs the plan's Gate `Test:` cmds against the
    merged tree via SKILL §6.1.5 prose; this verb owns layer (b) + the honesty notice only.
- CLI `validate_merged_cmd` (`:1396-1412`): positional `plan_dir`, `--json`; **exit 3 on
  fail** (`sys.exit(0 if pass else 3)`).
- **JSON contract** downstream depends on: `{plan_dir, validate_cmd_configured(bool),
  layer_b(null|{cmd,ok,returncode,output_tail}), notice(null|str), status(pass|fail)}`.

## `.yf-plan.local.json` schema

- `CONFIG_FILE = .yf-plan.local.json` (`:34`), read via `_read_config`/`_read_json`
  (`:590-599`, `{}` if missing).
- Keys actually read (only two): `execute.worktree` (`:899`, `_worktree_opted_out`) and
  `validate-cmd` (`:900`, `_resolve_validate_cmd` `:918-925`). `ignore-skill` is docstring-only.

## Delegation hook point

- **Single seam: `_validate_merged()`.** Make it: *manifest present → delegate to
  yf-change-validation; else fall back to `_resolve_validate_cmd()` + `_run_shell()`*. Must
  **preserve the JSON contract** (status/validate_cmd_configured/layer_b/notice) so
  `validate_merged_cmd` exit code, SKILL §6.1.5, and tests keep working.
- In-code extraction trigger already present (`:879-884`): *"extract the validate-merged /
  validate-cmd seam ONLY when a second skill needs merged-state/regression validation"* +
  soft-dep coupling (present→delegate, absent→in-place). plan-014 IS that second consumer.
- SKILL §6.1.5 invokes `validate-merged` at `SKILL.md:775`; honesty prose `:789-792`.

## Phase-6 ordering (must not break)

§6.1 lock acquire → pull --rebase → merge --no-ff (uncommitted); §6.1.5 validate-merged:
**fail → halt, lock held**; **pass → commit merge, release lock**; §6.2 push (no lock). The
delegation must keep the same `status` pass/fail branch so lock-held-on-fail / commit-release-
on-pass is unchanged. In-place fallback skips merge; §6.1.5 still runs.

## Full migration surface (validate-cmd / validate-merged)

- Code: `plan_manager.py:879,898,900,918-925,1218,1316-1343,1396-1412`.
- Docs: `SKILL.md:775,776,789,791`; `SPEC.md:94,95,113,119` (REQ-PLAN-060/061); `README.md:31,132`.
- Tests: `test_worktree.py:238-256` (`test_validate_merged_unset_emits_notice`,
  `test_validate_merged_runs_configured_cmd`).
- Dogfood: `docs/plans/plan-009-*/findings/dogfood_worktree.sh:53-60`.
