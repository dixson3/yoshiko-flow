# Gate metadata read-back (Issue 0.0 / SC10)

Set-then-assert record for the three capability gates poured for this plan. `plan_extract.py`
silently drops the `test_class:` and `cwd:` lines while reporting `unparsed: []`, so these were
parsed out of `plan.md` directly and written as bead metadata at the pour, then read back with
`bd show --json`.

**Capability-gate count in `plan.md`:** `grep -c '^### Capability Gate:'` → **3**
**Gate beads created with metadata:** **3** (counts agree)

| Gate bead | Gate | `gate_type` | `test_class` | `cwd` | `test` present |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `yf-mol-3wtq.8` | execution is in-place, not in a worktree | `auto` | `probe` | `repo-root` | yes |
| `yf-mol-3wtq.9` | the mock-fidelity check is DISCRIMINATING before the stubs are fixed | `auto` | `probe` | `repo-root` | yes |
| `yf-mol-3wtq.10` | L16 no longer commits work it did not stage | `auto` | `probe` | `repo-root` | yes |

Read-back verbatim (`bd show <id> --json | jq .metadata`):

```json
{"cwd":"repo-root","gate_type":"auto","test":"uv run skills/yf-plan/scripts/plan_manager.py config-resolve --json | jq -e '.keys[\"execute.worktree\"].value == false' > /dev/null","test_class":"probe"}
{"cwd":"repo-root","gate_type":"auto","test":"test \"$(uv run scripts/checks/check_mock_fidelity.py --json | jq '[.incompatible[]] | length')\" -ge 1","test_class":"probe"}
{"cwd":"repo-root","gate_type":"auto","test":"uv run skills/yf-plan/scripts/test_land_apply.py -k l16_commits_only_plan_dir -q","test_class":"probe"}
```

No write was lost: every one of the four keys is present on all three gates, so none of the three
would be classified `manual` and skipped by the §5.2c sweep (R4).

**§5.2c sweep result at execute start**

| Gate | Verdict | Note |
| :-- | :-- | :-- |
| `yf-mol-3wtq.8` | **PASS** — resolved | `execute.worktree` resolves to `false` |
| `yf-mol-3wtq.9` | RED (expected) | the check does not exist until Issue 5.2 |
| `yf-mol-3wtq.10` | RED (expected) | the test does not exist until Issue 3.3 |
