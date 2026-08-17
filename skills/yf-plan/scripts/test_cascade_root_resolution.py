# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
# ]
# ///
"""Tier-1 unit tests for cascade root resolution (REQ-PLAN-067, plan-043 Issue 3.3).

Run from anywhere:  uv run skills/yf-plan/scripts/test_cascade_root_resolution.py

`bd` is never shelled out to — `_bd_ex` and `_bd_healthy` are monkeypatched.

THE SPLIT UNDER TEST
--------------------
`_bd()` returned `[]` for `CalledProcessError`, `FileNotFoundError` AND `OSError` alike, so
`_bd_show(root) is None` fired identically for a typo, a missing binary and a wedged Dolt DB.
Two different fixes were therefore in tension:

  * making a not-found root fail loudly (SC8) — otherwise a typo'd `${EPIC}` walks an empty
    tree and reports a clean cascade over nothing, a silent pass that looks like success;
  * not halting completion on a `bd` outage (SC11) — healthy work must not be blocked
    because a dependency was down.

Doing only the first would have converted every outage into a hard halt. The split is what
lets both hold, and it is only real because `_bd_healthy()` asks a BEAD-INDEPENDENT question:
`bd show <missing-id>` exits non-zero, so a bead-specific failure cannot on its own tell a
missing bead from a broken `bd`.

Covers:
  (a) SC8 — bd healthy + bead absent  -> `fail`, exit 2;
  (b) SC11 second clause — bd unavailable -> `inconclusive`, exit 0;
  (c) the discrimination is genuine (same bead-level failure, opposite verdicts, decided
      only by the health probe);
  (d) a healthy tree with an open child still fails loudly (no regression);
  (e) envelope conformance on every root-resolution path.
"""
from __future__ import annotations

import importlib.util
import json
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


cc = _load("close_cascade", "close_cascade.py")

ROOT = "yf-mol-root"


def _run(root: str = ROOT, *extra: str) -> tuple[int, dict]:
    res = CliRunner().invoke(cc.main, [root, "--json", *extra])
    assert res.output.strip(), "a verdict must be emitted on every path"
    return res.exit_code, json.loads(res.output)


def _assert_envelope(out: dict):
    assert out["verdict"] in ("pass", "fail", "inconclusive")
    assert out["passed"] == (out["verdict"] == "pass")
    assert out["reason"]
    if out["verdict"] != "pass":
        assert out["remediation"]


# ---------------------------------------------------------------------------
# (a) SC8 — bd answered, bead absent
# ---------------------------------------------------------------------------

def test_root_not_found_fails_loudly(monkeypatch):
    """SC8 — a typo'd ${EPIC} must not pass with exit 0 over an empty tree."""
    monkeypatch.setattr(cc, "_bd_ex", lambda *a: ([], "`bd show` exited 1"))
    monkeypatch.setattr(cc, "_bd_healthy", lambda: True)
    rc, out = _run()
    _assert_envelope(out)
    assert out["verdict"] == "fail"
    assert rc == 2, "root-not-found must halt completion"
    assert "does not exist" in out["reason"]


def test_root_not_found_via_clean_empty_result(monkeypatch):
    """A functioning bd may also answer cleanly with an empty result."""
    monkeypatch.setattr(cc, "_bd_ex", lambda *a: ([], None))
    monkeypatch.setattr(cc, "_bd_healthy", lambda: True)
    rc, out = _run()
    assert out["verdict"] == "fail" and rc == 2


# ---------------------------------------------------------------------------
# (b) SC11 second clause — bd did not answer
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("reason", [
    "`bd` not found on PATH",
    "`bd` could not be run: [Errno 8] Exec format error",
    "unparseable `bd` output: Expecting value",
])
def test_bd_unavailable_is_inconclusive_and_does_not_halt(monkeypatch, reason):
    monkeypatch.setattr(cc, "_bd_ex", lambda *a: ([], reason))
    monkeypatch.setattr(cc, "_bd_healthy", lambda: False)
    rc, out = _run()
    _assert_envelope(out)
    assert out["verdict"] == "inconclusive", "a bd outage must never be `fail`"
    assert rc == 0, "SC11: a bd outage must not halt completion on healthy work"


# ---------------------------------------------------------------------------
# (c) the discrimination is genuine, not nominal
# ---------------------------------------------------------------------------

def test_identical_bead_failure_yields_opposite_verdicts(monkeypatch):
    """THE point of the split.

    The bead-level signal is byte-identical in both runs. Only the bead-INDEPENDENT
    health probe differs, and it flips the verdict between halt and report. If this
    ever collapses to one verdict, either SC8 or SC11 has been silently lost.
    """
    same_failure = ([], "`bd show yf-mol-root` exited 1")
    monkeypatch.setattr(cc, "_bd_ex", lambda *a: same_failure)

    monkeypatch.setattr(cc, "_bd_healthy", lambda: True)
    rc_healthy, out_healthy = _run()

    monkeypatch.setattr(cc, "_bd_healthy", lambda: False)
    rc_down, out_down = _run()

    assert (out_healthy["verdict"], rc_healthy) == ("fail", 2)
    assert (out_down["verdict"], rc_down) == ("inconclusive", 0)


def test_health_probe_is_bead_independent(monkeypatch):
    """`_bd_healthy` must not ask about the root bead — that is the whole point."""
    seen: list[tuple] = []

    def fake_check_output(argv, **kw):
        seen.append(tuple(argv))
        return "[]"

    monkeypatch.setattr(cc.subprocess, "check_output", fake_check_output)
    cc._bd_healthy()
    assert seen, "the health probe issued no command"
    for argv in seen:
        assert ROOT not in argv, f"health probe is bead-specific: {argv}"
        assert "show" not in argv, f"health probe uses a bead-specific verb: {argv}"


# ---------------------------------------------------------------------------
# (d) no regression on the normal paths
# ---------------------------------------------------------------------------

def _tree(open_child: bool):
    root = {"id": ROOT, "issue_type": "epic", "title": "plan", "status": "open"}
    child = {"id": f"{ROOT}.1", "issue_type": "task", "title": "t",
             "status": "open" if open_child else "closed"}

    def bd_ex(*args):
        if args[0] == "show":
            return ([root] if args[1] == ROOT else [child]), None
        return ([child] if args[1] == ROOT else []), None

    return bd_ex


def test_open_child_still_fails_loudly(monkeypatch):
    monkeypatch.setattr(cc, "_bd_ex", _tree(open_child=True))
    monkeypatch.setattr(cc, "_bd_healthy", lambda: True)
    rc, out = _run(ROOT, "--dry-run")
    assert out["verdict"] == "fail" and rc == 2
    assert out["blocked"], "an open child must appear in the blocked set"


def test_clean_tree_passes(monkeypatch):
    monkeypatch.setattr(cc, "_bd_ex", _tree(open_child=False))
    monkeypatch.setattr(cc, "_bd_healthy", lambda: True)
    rc, out = _run(ROOT, "--dry-run")
    _assert_envelope(out)
    assert out["verdict"] == "pass" and rc == 0
    assert not out["blocked"]


# ---------------------------------------------------------------------------
# (e) the human-readable path must not read as success
# ---------------------------------------------------------------------------

def test_human_output_does_not_report_no_containers_on_a_missing_root(monkeypatch):
    """"cascade: no containers to close" reads as success. A missing root must not
    produce it."""
    monkeypatch.setattr(cc, "_bd_ex", lambda *a: ([], None))
    monkeypatch.setattr(cc, "_bd_healthy", lambda: True)
    res = CliRunner().invoke(cc.main, [ROOT])
    assert "no containers to close" not in res.output
    assert "FAIL-LOUD" in res.output
    assert res.exit_code == 2


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
