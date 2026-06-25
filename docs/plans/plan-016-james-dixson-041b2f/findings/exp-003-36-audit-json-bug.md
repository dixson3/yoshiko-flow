# Exp 003 — #36 audit invalid-JSON-on-control-chars: bug repro + fix site

## Verdict: bug NOT present in current repo source

`skills/yf-plan/scripts/plan_manager.py` `audit --json-output` already serializes via
`click.echo(json.dumps(result, indent=2))` (`:2007`). `json.dumps` escapes all control characters
(`\t`, `\n`, …) by default, so a finding/report carrying raw control chars is emitted as **valid
JSON**.

## Evidence

- **Reproduction:** crafted a scratchpad temp plan whose files contain a literal tab, ran `audit
  … --json-output`, piped through `json.load` → **valid**. (No real plans mutated.)
- **Most newline-dense field:** the `report` is `"\n".join(report_lines)` (`:1984`) — many literal
  newlines — yet `json.dumps` escapes every one; round-trip confirmed.
- **No manual JSON assembly anywhere:** every `--json`/`--json-output` path in the file routes
  through `json.dumps` (~20 sites verified: audit `:2007`, list_plans `:738`, status `:799`,
  worktree `:1171/:1188/:1209`, landing-lock `:1464/:1481/:1495`, validate-merged `:1509`, …). No
  f-string/`.format()`/concat building of JSON braces.
- **Git history:** the `json.dumps` audit serializer dates to plan-004 (`3ac2bff`); never written
  with the manual-assembly defect; no prior "fix" commit.

This matches #36's own caveat — it was observed in the **installed** copy at
`~/.claude/skills/bdplan/scripts/plan_manager.py` ("not this repo's code"). The bead was a migrated
tracking placeholder, not a live defect against current source. `ensure_ascii` is irrelevant (the
issue class is control chars, which `json.dumps` escapes regardless).

## Action for the plan

- **No production fix required.**
- **Add a regression test** to pin the invariant (finding strings come from arbitrary file content
  — paths, section names — that could carry control chars). Home: `skills/yf-plan/scripts/test_worktree.py`
  (already `importlib`-loads the module as `pm` + uses `click.testing.CliRunner`, `:355-377`).
  Assert: an audit whose finding `detail`/`report` contains a raw tab/newline round-trips through
  `json.loads(result.output)` with control chars preserved.
- **Close #36** as already-fixed / not-present-in-current-source, noting the regression test landed.
- **No sibling anti-pattern instances** to clean up — fix scope is empty beyond the test.
