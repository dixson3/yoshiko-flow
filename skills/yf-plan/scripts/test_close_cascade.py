# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Unit tests for close_cascade.py (Issue 2.4 / #73) — REQ-PLAN-067.

Run from anywhere:  uv run skills/yf-plan/scripts/test_close_cascade.py

The `bd`-calling seams (`_bd_show`, `_node_children`, `_bd_close`) are monkeypatched
against an in-memory bead tree, so these tests exercise the cascade *logic* — bottom-up
close of all-terminal containers incl. the top molecule (U1), fail-loud on any open child,
and the resolved-vs-unsatisfied gate distinction (C4) — without a live beads DB.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_CC_PATH = Path(__file__).resolve().parent / "close_cascade.py"
_spec = importlib.util.spec_from_file_location("close_cascade", _CC_PATH)
assert _spec and _spec.loader
cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cc)


class _FakeTree:
    """In-memory bead tree wiring cc's bd seams. `edges` maps parent id → child ids."""

    def __init__(self, nodes: dict[str, dict], edges: dict[str, list[str]]):
        self.nodes = nodes
        self.edges = edges
        self.closed: list[str] = []

    def install(self, monkeypatch):
        monkeypatch.setattr(cc, "_bd_show", lambda nid: self.nodes.get(nid))
        monkeypatch.setattr(
            cc, "_node_children",
            lambda nid: [self.nodes[c] for c in self.edges.get(nid, [])])

        def _close(nid, _reason):
            self.closed.append(nid)
            self.nodes[nid]["status"] = "closed"
            return (True, "")

        monkeypatch.setattr(cc, "_bd_close", _close)
        return self


def _n(nid, itype="task", status="open", **extra):
    return {"id": nid, "issue_type": itype, "status": status, "title": nid, **extra}


# --- _bead_is_terminal -------------------------------------------------------

def test_terminal_closed_bead():
    assert cc._bead_is_terminal(_n("t", status="closed")) is True


def test_terminal_open_task_is_not_terminal():
    assert cc._bead_is_terminal(_n("t", status="open")) is False


def test_terminal_resolved_gate_status_closed():
    # bd >= 1.1.0: a resolved gate is status:closed.
    assert cc._bead_is_terminal(_n("g", itype="gate", status="closed")) is True


def test_terminal_resolved_gate_forward_compat_flag():
    # C4 forward-compat: a gate marked resolved without status:closed is terminal.
    assert cc._bead_is_terminal(
        _n("g", itype="gate", status="open", gate_status="resolved")) is True


def test_terminal_unsatisfied_gate_is_open_child():
    # An unsatisfied gate (open, no resolved flag) is NOT terminal — a genuine open child.
    assert cc._bead_is_terminal(_n("g", itype="gate", status="open")) is False


# --- cascade: all-terminal closes bottom-up incl. the molecule (U1) ----------

def test_cascade_closes_all_terminal_bottom_up_incl_molecule(monkeypatch):
    nodes = {
        "root": _n("root", itype="epic", status="open"),      # top molecule
        "e1": _n("e1", itype="epic", status="open"),          # intermediate epic
        "t1": _n("t1", status="closed"),
        "g1": _n("g1", itype="gate", status="closed"),        # resolved gate
    }
    edges = {"root": ["e1", "g1"], "e1": ["t1"]}
    tree = _FakeTree(nodes, edges).install(monkeypatch)

    result = cc.cascade("root", "reason", dry_run=False)
    assert result["blocked"] == []
    # bottom-up: intermediate epic closes before the molecule.
    assert result["closed"] == ["e1", "root"]
    assert tree.closed == ["e1", "root"]


# --- cascade: open child → blocked (fail-loud), nothing closed ---------------

def test_cascade_blocks_on_open_child(monkeypatch):
    nodes = {
        "root": _n("root", itype="epic", status="open"),
        "e1": _n("e1", itype="epic", status="open"),
        "t2": _n("t2", status="open"),                        # still-open leaf
    }
    edges = {"root": ["e1"], "e1": ["t2"]}
    tree = _FakeTree(nodes, edges).install(monkeypatch)

    result = cc.cascade("root", "reason", dry_run=False)
    assert result["closed"] == []
    assert tree.closed == []                                  # nothing force-closed
    blocked_ids = {b["id"] for b in result["blocked"]}
    assert blocked_ids == {"e1", "root"}
    e1_blocked = next(b for b in result["blocked"] if b["id"] == "e1")
    assert e1_blocked["open_children"] == ["t2"]


# --- cascade: resolved gate does NOT block; unsatisfied gate DOES (C4) --------

def test_cascade_resolved_gate_not_blocked(monkeypatch):
    # Container whose only non-closed child is a resolved (forward-compat) gate → closes.
    nodes = {
        "e1": _n("e1", itype="epic", status="open"),
        "g1": _n("g1", itype="gate", status="open", gate_status="resolved"),
    }
    edges = {"e1": ["g1"]}
    _FakeTree(nodes, edges).install(monkeypatch)
    result = cc.cascade("e1", "reason", dry_run=False)
    assert result["blocked"] == []
    assert result["closed"] == ["e1"]


def test_cascade_unsatisfied_gate_blocks(monkeypatch):
    nodes = {
        "e1": _n("e1", itype="epic", status="open"),
        "g2": _n("g2", itype="gate", status="open"),          # unsatisfied gate
    }
    edges = {"e1": ["g2"]}
    _FakeTree(nodes, edges).install(monkeypatch)
    result = cc.cascade("e1", "reason", dry_run=False)
    assert result["closed"] == []
    assert result["blocked"][0]["open_children"] == ["g2"]


# --- CLI exit-code contract: §6.4 halts on a blocked set ---------------------

def test_cli_exit_0_on_clean(monkeypatch):
    from click.testing import CliRunner
    nodes = {"root": _n("root", itype="epic", status="open"),
             "t1": _n("t1", status="closed")}
    edges = {"root": ["t1"]}
    _FakeTree(nodes, edges).install(monkeypatch)
    result = CliRunner().invoke(cc.main, ["root", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.output)["blocked"] == []


def test_cli_exit_2_on_blocked(monkeypatch):
    from click.testing import CliRunner
    nodes = {"root": _n("root", itype="epic", status="open"),
             "t2": _n("t2", status="open")}
    edges = {"root": ["t2"]}
    _FakeTree(nodes, edges).install(monkeypatch)
    result = CliRunner().invoke(cc.main, ["root", "--json"])
    assert result.exit_code == 2          # fail-loud → §6.4 must halt completion
    assert json.loads(result.output)["blocked"]


def test_cli_dry_run_does_not_close(monkeypatch):
    from click.testing import CliRunner
    nodes = {"root": _n("root", itype="epic", status="open"),
             "t1": _n("t1", status="closed")}
    edges = {"root": ["t1"]}
    tree = _FakeTree(nodes, edges).install(monkeypatch)
    result = CliRunner().invoke(cc.main, ["root", "--dry-run", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.output)["closed"] == ["root"]
    assert tree.closed == []              # dry-run mutates nothing


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
