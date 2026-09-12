# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
#     "click>=8",
#     "pyyaml>=6",
# ]
# ///
"""INVOCATION-FORM tests for every `plan_manager.py` verb no other test file invokes (plan-071
Issue 4.6, REQ-PLAN-086 leg (b)).

Run from anywhere:  uv run skills/yf-plan/scripts/test_verb_invocations.py

`check-provably-necessary.py` requires every registered verb to carry at least one test that
INVOKES it — a `CliRunner.invoke(pm.cli, ["<verb>", ...])` — not merely a test of the engine
behind it, because a verb whose CLI wiring is broken passes every engine test (#327's class).
Each case below has a passing arm and, where the verb can refuse, a failing arm, so the test can
fail on a fixture (D-1 leg (b): a negative control, not an existence check).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

_HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _HERE / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pm = _load("plan_manager", "plan_manager.py")
PLAN_ID = "plan-995-tester-verbs1"

_PLAN = """---
type: Plan
okf_spec: OKF-PLAN
id: {pid}
status: executing
---
# Plan: verbs

**ID:** {pid}
**Status:** executing

## Objective
t

## Motivation
m

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |

## Investigation Findings
none

## Approach
a

## Epics
### Epic 1: e
- Issue 1.1: do a thing
- Issue 1.2: do another
  - depends-on: 1.1

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

{gate}
### Reconcile Gate
- Type: auto (all execution beads closed)
- Blocks: reconcile step

## Risks & Mitigations
| # | Risk | Severity | Mitigation |
| :-- | :-- | :-- | :-- |
| R1 | r | low | m |

## Success Criteria
| # | Criterion | Verification | Discharged-by |
| :-- | :-- | :-- | :-- |
| SC1 | c | `true` → exit 0 | 1.1 |
"""

_GOOD_GATE = """### Capability Gate: g
- Type: auto
- Condition: something holds
- Test: true
- Blocks: 1.2
- Instructions: none
"""
# ARM 1 of gate_consistency: the gate names the issue it blocks as producing its own evidence.
_BAD_GATE = """### Capability Gate: g
- Type: auto
- Condition: the artifact Issue 1.2 produces exists
- Test: true
- Blocks: 1.2
- Instructions: 1.2 produces it
"""


def _git(*args, cwd):
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A git repo (on `main`) holding one plan bundle; cwd moved into it."""
    root = tmp_path / "repo"
    pd = root / "docs" / "plans" / PLAN_ID
    (pd / "reviews").mkdir(parents=True)
    _git("init", "-q", "-b", "main", ".", cwd=root)
    for k, v in (("user.email", "t@example.invalid"), ("user.name", "T"), ("commit.gpgsign", "false")):
        _git("config", k, v, cwd=root)
    (pd / "plan.md").write_text(_PLAN.format(pid=PLAN_ID, gate=_GOOD_GATE), encoding="utf-8")
    (pd / "log.md").write_text("# Log\n\n## 2026-01-01\n- scoping: init\n", encoding="utf-8")
    (pd / "index.md").write_text("# Index\n\n- [plan.md](plan.md) - The plan.\n", encoding="utf-8")
    (root / ".gitignore").write_text("/.yf/\n", encoding="utf-8")
    _git("add", "-A", cwd=root); _git("commit", "-q", "-m", "seed", cwd=root)
    monkeypatch.chdir(root)
    return root, pd


def _run(*args, input=None):
    return CliRunner().invoke(pm.cli, list(args), input=input)


# --- json-get -------------------------------------------------------------------------------

def test_json_get_reads_a_key_and_refuses_a_missing_one():
    r = _run("json-get", "a", input='{"a": 7}')
    assert r.exit_code == 0 and r.output.strip() == "7", r.output
    r = _run("json-get", "zz", input='{"a": 7}')
    assert r.exit_code != 0


# --- classify-deliverable / set-deliverable-class ------------------------------------------

def test_classify_deliverable_suggests_and_refuses_a_missing_bundle(repo):
    root, pd = repo
    r = _run("classify-deliverable", str(pd), "--json")
    assert r.exit_code == 0, r.output
    assert json.loads(r.output)["suggested_class"] in ("standard", "ci-release")
    assert _run("classify-deliverable", str(root / "nope"), "--json").exit_code != 0


def test_set_deliverable_class_writes_the_field_and_refuses_a_bogus_class(repo):
    root, pd = repo
    r = _run("set-deliverable-class", str(pd), "standard")
    assert r.exit_code == 0, r.output
    assert "**Deliverable-class:** standard" in (pd / "plan.md").read_text(encoding="utf-8")
    assert _run("set-deliverable-class", str(pd), "bogus").exit_code != 0


# --- record-epic / clear-epic / resume-scan / resolve-start-gate ---------------------------

def test_record_epic_writes_the_field_and_clear_epic_removes_it(repo):
    root, pd = repo
    r = _run("record-epic", str(pd), "yf-zz1")
    assert r.exit_code == 0, r.output
    assert "**Epic:** yf-zz1" in (pd / "plan.md").read_text(encoding="utf-8")
    assert _run("record-epic", str(root / "nope"), "yf-zz1").exit_code != 0
    r = _run("clear-epic", str(pd), "--force", "--json", "-m", "test")
    assert r.exit_code == 0, r.output
    assert "**Epic:** yf-zz1" not in (pd / "plan.md").read_text(encoding="utf-8")


def test_resume_scan_reports_no_epic_and_resolve_start_gate_refuses_without_one(repo):
    root, pd = repo
    r = _run("resume-scan", str(pd), "--json")
    assert r.exit_code == 0, r.output
    assert json.loads(r.output)["epic_state"] == "none"
    r = _run("resolve-start-gate", str(pd), "--json")
    assert r.exit_code != 0, "no epic recorded — the verb must refuse, not report a resolved gate"
    assert json.loads(r.output)["verdict"] != "pass"


# --- review-loop-check ------------------------------------------------------------------------

def test_review_loop_check_escalates_at_the_bound_and_accepts_a_raise(repo):
    root, pd = repo
    for n in range(1, 6):
        (pd / "reviews" / f"pass-{n}.md").write_text(f"# r\n\n## Verdict: REVISE\n", encoding="utf-8")
    r = _run("review-loop-check", str(pd), "--json")
    assert r.exit_code == 3 and json.loads(r.output)["escalates"] is True, r.output
    r = _run("review-loop-check", str(pd), "--max-review-cycles", "9", "--json")
    assert r.exit_code == 0 and json.loads(r.output)["escalates"] is False, r.output


# --- scope / triage ----------------------------------------------------------------------------

def test_scope_writes_the_questionnaire(repo):
    root, pd = repo
    before = {p.name for p in pd.iterdir()}
    r = _run("scope", str(pd), "an objective")
    assert r.exit_code == 0, r.output
    assert {p.name for p in pd.iterdir()} - before, "scope wrote no new file"
    assert _run("scope", str(root / "nope"), "x").exit_code != 0


def test_triage_writes_upstream_triage_from_an_issues_file(repo, tmp_path):
    root, pd = repo
    issues = tmp_path / "issues.json"
    issues.write_text(json.dumps([{"number": 5, "title": "t", "body": "b", "labels": [],
                                   "state": "OPEN", "url": "https://x/5"}]), encoding="utf-8")
    r = _run("triage", str(pd), "an objective", "--issues-json", str(issues))
    assert r.exit_code == 0, r.output
    assert (pd / "upstream-triage.md").is_file()
    assert _run("triage", str(pd), "x", "--issues-json", str(tmp_path / "none.json")).exit_code != 0


# --- commit-plan ------------------------------------------------------------------------------

def test_commit_plan_refuses_on_main_and_commits_on_a_branch(repo):
    root, pd = repo
    (pd / "log.md").write_text("# Log\n\n## 2026-01-02\n- executing: x\n", encoding="utf-8")
    r = _run("commit-plan", str(pd), "--json")
    assert json.loads(r.output)["status"] != "committed", "REQ-PLAN-065: refused on the default branch"
    _git("checkout", "-q", "-b", f"{PLAN_ID}-execute", cwd=root)
    r = _run("commit-plan", str(pd), "--json")
    assert r.exit_code == 0 and json.loads(r.output)["status"] == "committed", r.output


# --- config-resolve ---------------------------------------------------------------------------

def test_config_resolve_reports_value_and_source_and_rejects_an_unknown_token(repo):
    r = _run("config-resolve", "--autonomy", "autonomous", "--json")
    assert r.exit_code == 0, r.output
    out = json.loads(r.output)
    assert out["keys"]["autonomy"]["value"] == "autonomous" and out["keys"]["autonomy"]["source"] == "flag"
    r = _run("config-resolve", "--autonomy", "bogus", "--json")
    assert "error" in json.loads(r.output), "an unrecognised token must be REJECTED, not ignored"


# --- escalation-push --------------------------------------------------------------------------

def test_escalation_push_skips_without_a_file_and_dry_runs_with_one(repo):
    root, pd = repo
    r = _run("escalation-push", str(pd), "--json")
    assert r.exit_code == 0 and json.loads(r.output)["verdict"] == "skipped", r.output
    r = _run("escalation-raise", str(pd), "--question", "q?", "--alternative", "a", "--alternative", "b",
             "--recommended", "a", "--on-no-answer", "take a", "--json")
    assert r.exit_code == 0, r.output
    r = _run("escalation-push", str(pd), "--dry-run", "--json")
    assert r.exit_code == 0, r.output
    assert json.loads(r.output)["dry_run"] is True


# --- gate-consistency -------------------------------------------------------------------------

def test_gate_consistency_wrapper_passes_a_clean_plan_and_fails_a_self_satisfying_gate(repo):
    root, pd = repo
    r = _run("gate-consistency", str(pd), "--json")
    assert r.exit_code == 0 and json.loads(r.output)["verdict"] == "PASS", r.output
    (pd / "plan.md").write_text(_PLAN.format(pid=PLAN_ID, gate=_BAD_GATE), encoding="utf-8")
    r = _run("gate-consistency", str(pd), "--json")
    assert r.exit_code == 1 and json.loads(r.output)["verdict"] == "FAIL", r.output


# --- list ---------------------------------------------------------------------------------------

def test_list_enumerates_the_bundle_and_the_parked_filter_counts(repo):
    root, pd = repo
    r = _run("list", "--json")
    assert r.exit_code == 0, r.output
    assert PLAN_ID in {p["id"] for p in json.loads(r.output)["plans"]}
    r = _run("list", "--parked", "--json")
    assert r.exit_code == 0 and json.loads(r.output)["count"] == 0, r.output


# --- retrospective-append --------------------------------------------------------------------

def test_retrospective_append_refuses_a_fidelity_entry_without_numbers_and_accepts_one_with(repo):
    root, pd = repo
    r = _run("retrospective-append", str(pd), "--kind", "fidelity", "--json")
    assert r.exit_code != 0
    r = _run("retrospective-append", str(pd), "--kind", "fidelity", "--sc-flipped-post-approval", "1",
             "--halts-post-irreversible", "no-record", "--json")
    assert r.exit_code == 0 and json.loads(r.output)["appended"] is True, r.output


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
