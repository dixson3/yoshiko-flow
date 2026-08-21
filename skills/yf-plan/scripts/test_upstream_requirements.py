# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""The shared per-disposition requirement table (REQ-CLI-025 / #178) — SC8 and SC10.

Run from anywhere:  uv run skills/yf-plan/scripts/test_upstream_requirements.py

WHAT IS BEING ASSERTED, AND WHY IT IS BEHAVIORAL
------------------------------------------------
SC8 says the grant generator and the reconcile verifier "consume one requirement table". The
tempting checks are structural — the table exists, `_verify_row` imports it — and pass-3 C12
MEASURED the import form as UNDETECTING: a table that exists and is ignored passes it.

So the assertion here is behavioral, and it is the shape SC8 specifies:

    mutate ONE entry in a throwaway copy of the table,
    re-run `grant` AND `_verify_row`,
    and assert BOTH verdicts change.

`_gh_issue_view` is STUBBED to a fixed payload throughout. That is not convenience — it is
required for the assertion to mean anything. `_verify_row` calls it unconditionally as its
first act and returns `inconclusive` before consulting any table, so without the stub both
verdicts would be identical for a reason unrelated to the property (pass-5 C47).

The mutated entry is `include`, which is the disposition the `ctl-178-grant` fixture
exercises.

SC10 — every literal in `UPSTREAM_DISPOSITIONS` has exactly one entry, including `exclude`,
`deferred` and `tracker`. A generator silently omitting a disposition is #181's defect class
in a new place.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

_PM = Path(__file__).resolve().parent / "plan_manager.py"
_spec = importlib.util.spec_from_file_location("plan_manager", _PM)
assert _spec and _spec.loader
pm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pm)


# --- SC10: the table's entry set ------------------------------------------------------

def test_every_disposition_has_exactly_one_entry():
    """SC10's structural half. A literal with no entry falls through to the
    unrecognised-literal branch and is omitted from every grant — silently."""
    assert set(pm.UPSTREAM_REQUIREMENTS) == set(pm.UPSTREAM_DISPOSITIONS), (
        f"missing={sorted(pm.UPSTREAM_DISPOSITIONS - set(pm.UPSTREAM_REQUIREMENTS))} "
        f"extra={sorted(set(pm.UPSTREAM_REQUIREMENTS) - pm.UPSTREAM_DISPOSITIONS)}"
    )


def test_the_set_is_not_vacuously_equal():
    """Guard the guard: two empty sets are equal."""
    assert len(pm.UPSTREAM_DISPOSITIONS) >= 6, pm.UPSTREAM_DISPOSITIONS
    for literal in ("include", "exclude", "partial", "supersede", "deferred", "tracker"):
        assert literal in pm.UPSTREAM_REQUIREMENTS, f"{literal} has no requirement entry"


def test_every_entry_carries_every_field():
    """A half-filled entry would raise a KeyError deep inside a fail-loud step."""
    for literal, req in pm.UPSTREAM_REQUIREMENTS.items():
        for field in ("end_state", "state_reason", "requires_mention", "report_only", "why"):
            assert field in req, f"{literal} is missing {field!r}"
        assert req["end_state"] in (None, "OPEN", "CLOSED"), (literal, req["end_state"])
        assert req["why"].strip(), f"{literal} carries no rationale"


def test_grant_actions_are_derived_from_the_fields_not_declared():
    """The divergence `ctl-178-grant`'s contrast arm caught, pinned.

    `supersede` DECLARED a `comment` action while its own `requires_mention` is False, so the
    generator demanded a clause the verifier would never check. Deriving the actions makes
    that divergence unrepresentable.
    """
    for literal, req in pm.UPSTREAM_REQUIREMENTS.items():
        acts = pm._grant_actions_for(req)
        assert ("comment" in acts) == bool(req["requires_mention"]), (
            f"{literal}: a comment is asked for iff a mention is required")
        closes = {"close", "close-not-planned"} & set(acts)
        assert bool(closes) == (req["end_state"] == "CLOSED"), (
            f"{literal}: a close is asked for iff the end state is CLOSED")
        if req["state_reason"] == "NOT_PLANNED":
            assert "close-not-planned" in acts, literal


# --- SC8: the read is BEHAVIORAL ------------------------------------------------------

_ISSUE = "172"
_PLAN = "plan-048-james-dixson-ed68a5"

#: A CLOSED issue whose comments mention the plan — i.e. an `include` row that PASSES today.
_PAYLOAD = {"state": "CLOSED", "stateReason": "COMPLETED",
            "comments": [{"body": f"landed by {_PLAN}"}]}


def _stub_gh(monkeypatch):
    """`_verify_row` calls `_gh_issue_view` unconditionally as its FIRST act and returns
    `inconclusive` before consulting any table. Without this stub both verdicts would be
    identical for a reason unrelated to the property (pass-5 C47)."""
    monkeypatch.setattr(pm, "_gh_issue_view", lambda _n: (dict(_PAYLOAD), None))


def _bundle(tmp_path: Path) -> Path:
    d = tmp_path / _PLAN
    d.mkdir()
    (d / "plan.md").write_text(
        "# Plan: t\n\n"
        "## Upstream Issues\n"
        "| Issue | Title | Disposition | Notes | Resolved By |\n"
        "| :-- | :-- | :-- | :-- | :-- |\n"
        f"| [#{_ISSUE}](https://x/{_ISSUE}) | t | include | n | 1.1 |\n",
        encoding="utf-8")
    return d


def _grant_actions(bundle: Path) -> list[str]:
    res = CliRunner().invoke(pm.cli, ["grant", str(bundle), "--json"])
    payload = json.loads(res.output)
    return sorted(a["kind"]
                  for row in payload["proposal"]["rows"] for a in row["actions"])


def test_both_readers_change_when_one_entry_is_mutated(tmp_path, monkeypatch):
    """SC8, executed. Mutate ONE entry; BOTH verdicts must change.

    An existence check or an import check passes on a table that is present and ignored.
    This does not.
    """
    _stub_gh(monkeypatch)
    bundle = _bundle(tmp_path)
    row = {"issue": _ISSUE, "disposition": "include"}

    before_verify = pm._verify_row(row, _PLAN)["verdict"]
    before_grant = _grant_actions(bundle)

    # The arm must not be vacuous: the unmutated state has to be the one we think it is.
    assert before_verify == "pass", before_verify
    assert before_grant == ["close", "comment"], before_grant

    mutated = copy.deepcopy(pm.UPSTREAM_REQUIREMENTS)
    mutated["include"]["end_state"] = "OPEN"        # the payload is CLOSED, so this must fail
    mutated["include"]["requires_mention"] = False  # ...and drop the comment from the grant
    monkeypatch.setattr(pm, "UPSTREAM_REQUIREMENTS", mutated)

    after_verify = pm._verify_row(row, _PLAN)["verdict"]
    after_grant = _grant_actions(bundle)

    assert after_verify != before_verify, (
        "`_verify_row`'s verdict did not change when the table entry it claims to read was "
        "mutated — it is not reading the table")
    assert after_verify == "fail", after_verify
    assert after_grant != before_grant, (
        "`grant`'s proposal did not change when the table entry it claims to read was "
        "mutated — it is not reading the table")
    assert after_grant == [], after_grant


def test_the_stub_is_load_bearing(tmp_path, monkeypatch):
    """Without the stub, `_verify_row` returns `inconclusive` BEFORE any table read.

    Recorded as its own assertion so a future edit that drops the stub fails here, loudly,
    instead of turning the test above into a comparison of two identical `inconclusive`s.
    """
    monkeypatch.setattr(pm, "_gh_issue_view", lambda _n: (None, "network down"))
    assert pm._verify_row({"issue": _ISSUE, "disposition": "include"},
                          _PLAN)["verdict"] == "inconclusive"


# --- SC10's behavioral half: coverage of EVERY disposition ---------------------------

@pytest.mark.parametrize("disposition", sorted(
    {"include", "exclude", "partial", "supersede", "deferred", "tracker"}))
def test_grant_covers_every_disposition_without_crashing(tmp_path, disposition):
    """Every literal produces a well-formed proposal row — including the three that require
    NO action. `exclude` and `deferred` yield an empty action list, which is a RESULT, not a
    skip: a row silently absent from the proposal is indistinguishable from a row nobody
    checked."""
    d = tmp_path / _PLAN
    d.mkdir()
    (d / "plan.md").write_text(
        "# Plan: t\n\n## Upstream Issues\n"
        "| Issue | Title | Disposition | Notes | Resolved By |\n"
        "| :-- | :-- | :-- | :-- | :-- |\n"
        f"| [#900](https://x/900) | t | {disposition} | n | 1.1 |\n", encoding="utf-8")
    res = CliRunner().invoke(pm.cli, ["grant", str(d), "--json"])
    assert res.exit_code == 0, res.output
    payload = json.loads(res.output)
    rows = payload["proposal"]["rows"]
    assert len(rows) == 1, f"{disposition} produced {len(rows)} rows, expected 1"
    assert rows[0]["disposition"] == disposition
    assert rows[0]["why"].strip(), "the rationale must travel with the requirement"
    if disposition in ("exclude", "deferred"):
        assert rows[0]["actions"] == [], (
            f"{disposition} requires no upstream action, but the row must still be PRESENT")


def test_an_unrecognised_disposition_fails_loudly_rather_than_being_skipped(tmp_path):
    """The failure mode SC10 exists to prevent, from the generator's side."""
    d = tmp_path / _PLAN
    d.mkdir()
    (d / "plan.md").write_text(
        "# Plan: t\n\n## Upstream Issues\n"
        "| Issue | Title | Disposition | Notes | Resolved By |\n"
        "| :-- | :-- | :-- | :-- | :-- |\n"
        "| [#901](https://x/901) | t | inclde | n | 1.1 |\n", encoding="utf-8")
    res = CliRunner().invoke(pm.cli, ["grant", str(d), "--json"])
    assert res.exit_code != 0, "a typo'd disposition was silently skipped"
    assert json.loads(res.output)["verdict"] == "fail"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
