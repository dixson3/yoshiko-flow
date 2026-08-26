# /// script
# requires-python = ">=3.11"
# ///
"""Tests for `plan_manager.py stamp-tracker` — REQ-PLAN-073 (#131).

Run:  uv run --with pytest python3 -m pytest test_stamp_tracker.py -q

Every `bd`/`git` interaction is faked. The contract under test is that the stamp is
idempotent, non-clobbering, and — above all — **fail-soft**: it runs inside the §5.2a pour
sequence, so no failure mode may ever exit non-zero and break the pour.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

_spec = importlib.util.spec_from_file_location(
    "plan_manager", Path(__file__).parent / "plan_manager.py"
)
pm = importlib.util.module_from_spec(_spec)
sys.modules["plan_manager"] = pm
_spec.loader.exec_module(pm)

TRACKER = "https://github.com/dixson3/yoshiko-flow/issues/138"
OTHER = "https://github.com/dixson3/yoshiko-flow/issues/999"

PLAN_MD = """---
type: Plan
id: plan-040-james-dixson-1cabe4
status: executing
epic: yf-mol-win
---
# Plan: something

**Epic:** yf-mol-win

## Upstream Issues

| Issue | Title | Disposition | Notes | Resolved By |
| :-- | :-- | :-- | :-- | :-- |
| [#133](https://github.com/dixson3/yoshiko-flow/issues/133) | the swap | include | x | 2.1 |
| [#138](https://github.com/dixson3/yoshiko-flow/issues/138) | plan-040 execution tracking | tracker | the coarse tracker | — |
| [#51](https://github.com/dixson3/yoshiko-flow/issues/51) | gitlab | exclude | y | — |
"""


def _plan(tmp_path, text=PLAN_MD):
    d = tmp_path / "plan-040-james-dixson-1cabe4"
    d.mkdir()
    (d / "plan.md").write_text(text, encoding="utf-8")
    return d


def _run(plan_dir, *args):
    return CliRunner().invoke(pm.cli, ["stamp-tracker", str(plan_dir), "--json", *args])


def _verdict(res):
    assert res.exit_code == 0, f"stamp-tracker must never fail the pour: {res.output}"
    return json.loads(res.output.strip().splitlines()[-1])


@pytest.fixture(autouse=True)
def _no_real_subprocess(monkeypatch):
    """Fail loudly if a test forgets to fake a subprocess it triggers."""
    def boom(*a, **k):
        raise AssertionError(f"unfaked subprocess: {a!r}")
    monkeypatch.setattr(subprocess, "check_output", boom)
    monkeypatch.setattr(subprocess, "run", boom)


def _fake_bd(monkeypatch, existing_ref=None, update_ok=True, calls=None):
    """Fake `bd show --json` (existing ref) and `bd update --external-ref`."""
    def check_output(cmd, *a, **k):
        if cmd[:2] == ["bd", "show"]:
            row = {"id": cmd[2]}
            if existing_ref is not None:
                row["external_ref"] = existing_ref
            return json.dumps([row])
        if cmd[:2] == ["git", "config"]:
            return "git@github.com:dixson3/yoshiko-flow.git\n"
        raise AssertionError(f"unexpected check_output {cmd!r}")

    def run(cmd, *a, **k):
        if calls is not None:
            calls.append(list(cmd))
        if not update_ok:
            raise subprocess.CalledProcessError(1, cmd, stderr="boom")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(subprocess, "check_output", check_output)
    monkeypatch.setattr(subprocess, "run", run)


# --- the happy path -----------------------------------------------------------

def test_stamps_the_tracker_row_onto_the_epic(tmp_path, monkeypatch):
    """The tracker is the row whose Disposition is literally `tracker` — NOT #133."""
    calls = []
    _fake_bd(monkeypatch, existing_ref=None, calls=calls)
    v = _verdict(_run(_plan(tmp_path)))
    assert v["status"] == "stamped"
    assert v["epic"] == "yf-mol-win"
    assert v["tracker"] == TRACKER
    assert calls == [["bd", "update", "yf-mol-win", "--external-ref", TRACKER, "-q"]]


def test_include_and_exclude_rows_are_never_mistaken_for_the_tracker(tmp_path, monkeypatch):
    """#133 (include) and #51 (exclude) sit in the same table and must not match."""
    _fake_bd(monkeypatch, existing_ref=None)
    v = _verdict(_run(_plan(tmp_path)))
    assert "138" in v["tracker"]
    assert "133" not in v["tracker"] and "/51" not in v["tracker"]


# --- idempotency and non-clobbering -------------------------------------------

def test_restamping_the_same_url_is_a_noop(tmp_path, monkeypatch):
    """§5.2b re-runs this on every resume — it must not churn."""
    calls = []
    _fake_bd(monkeypatch, existing_ref=TRACKER, calls=calls)
    v = _verdict(_run(_plan(tmp_path)))
    assert v["status"] == "unchanged"
    assert calls == [], "an unchanged stamp must issue no bd update"


def test_a_different_existing_ref_is_reported_not_overwritten(tmp_path, monkeypatch):
    """Never clobber a mapping someone else established — report and stop."""
    calls = []
    _fake_bd(monkeypatch, existing_ref=OTHER, calls=calls)
    v = _verdict(_run(_plan(tmp_path)))
    assert v["status"] == "skipped"
    assert v["tracker"] == OTHER
    assert "different" in v["reason"].lower()
    assert calls == []


# --- fail-soft: the pour must never break -------------------------------------

def test_skips_cleanly_when_no_epic_recorded(tmp_path, monkeypatch):
    """Before the pour there is no epic. Normal state, not an error."""
    text = PLAN_MD.replace("epic: yf-mol-win\n", "").replace("**Epic:** yf-mol-win\n", "")
    v = _verdict(_run(_plan(tmp_path, text)))
    assert v["status"] == "skipped"
    assert v["epic"] is None
    assert "no epic" in v["reason"].lower()


def test_skips_cleanly_when_no_tracker_row_exists(tmp_path, monkeypatch):
    """A plan whose tracker has not been filed yet must not fail the pour."""
    text = "\n".join(ln for ln in PLAN_MD.splitlines() if "tracker" not in ln) + "\n"
    monkeypatch.setattr(
        subprocess, "check_output",
        lambda cmd, *a, **k: "git@github.com:dixson3/yoshiko-flow.git\n")
    v = _verdict(_run(_plan(tmp_path, text)))
    assert v["status"] == "skipped"
    assert "no coarse tracker" in v["reason"].lower()


def test_bd_update_failure_is_soft(tmp_path, monkeypatch):
    """A bd error is reported, never raised — the pour continues."""
    _fake_bd(monkeypatch, existing_ref=None, update_ok=False)
    v = _verdict(_run(_plan(tmp_path)))
    assert v["status"] == "skipped"
    assert "bd update failed" in v["reason"]


def test_missing_bd_binary_is_soft(tmp_path, monkeypatch):
    """`bd` absent entirely (FileNotFoundError) is still exit 0."""
    monkeypatch.setattr(
        subprocess, "check_output",
        lambda cmd, *a, **k: (_ for _ in ()).throw(FileNotFoundError("bd")))
    monkeypatch.setattr(
        subprocess, "run",
        lambda cmd, *a, **k: (_ for _ in ()).throw(FileNotFoundError("bd")))
    v = _verdict(_run(_plan(tmp_path)))
    assert v["status"] == "skipped"


def test_every_failure_path_exits_zero(tmp_path, monkeypatch):
    """The load-bearing contract, asserted directly rather than inferred.

    stamp-tracker runs INSIDE the §5.2a pour sequence. A non-zero exit on any of these
    ordinary states would abort a pour that is proceeding correctly.
    """
    _fake_bd(monkeypatch, existing_ref=None, update_ok=False)
    for text in (PLAN_MD,
                 PLAN_MD.replace("**Epic:** yf-mol-win\n", "").replace("epic: yf-mol-win\n", ""),
                 "\n".join(l for l in PLAN_MD.splitlines() if "tracker" not in l) + "\n"):
        d = tmp_path / f"p{abs(hash(text))}"
        d.mkdir()
        (d / "plan.md").write_text(text, encoding="utf-8")
        assert _run(d).exit_code == 0


# --- explicit override --------------------------------------------------------

def test_explicit_url_and_epic_override_the_derivation(tmp_path, monkeypatch):
    """4.4's backfill drives this verb with explicit values, bypassing plan.md."""
    calls = []
    _fake_bd(monkeypatch, existing_ref=None, calls=calls)
    v = _verdict(_run(_plan(tmp_path), "--epic", "yf-zzzz", "--url", OTHER))
    assert v["status"] == "stamped"
    assert calls == [["bd", "update", "yf-zzzz", "--external-ref", OTHER, "-q"]]
