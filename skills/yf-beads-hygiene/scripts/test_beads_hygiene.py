# /// script
# requires-python = ">=3.11"
# ///
"""Tests for beads_hygiene.py — the four-class edge classifier + the #29 regression.

Run:  uv run --with pytest python3 -m pytest test_beads_hygiene.py -q

The classifier core (Edge.classify / classify_edges / collect_edges) is pure: it takes
in-memory beads, so these fixtures reproduce the #29 incident WITHOUT a live DB.
"""
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "beads_hygiene", Path(__file__).parent / "beads_hygiene.py"
)
bh = importlib.util.module_from_spec(_spec)
sys.modules["beads_hygiene"] = bh  # so dataclass forward-ref resolution finds the module
_spec.loader.exec_module(bh)


def gate(id_, status="open"):
    return {"id": id_, "issue_type": "gate", "status": status}


def task(id_, status="open"):
    return {"id": id_, "issue_type": "task", "status": status}


# --- the four classifications -------------------------------------------------

def test_live_gate_open_gate_target_is_preserved_never_dangling():
    e = bh.Edge(blocked="b-1", blocker="g-1", dep_type="blocks", target=gate("g-1", "open"))
    assert e.classify() == bh.LIVE_GATE
    assert e.classify() != bh.TRULY_DANGLING


def test_satisfied_gate_closed_gate_target():
    for closed in ("closed", "resolved", "done"):
        e = bh.Edge(blocked="b-1", blocker="g-1", dep_type="blocks", target=gate("g-1", closed))
        assert e.classify() == bh.SATISFIED_GATE


def test_truly_dangling_blocks_edge_to_missing_target():
    e = bh.Edge(blocked="b-1", blocker="ghost", dep_type="blocks", target=None)
    assert e.classify() == bh.TRULY_DANGLING


def test_true_orphan_parent_child_edge_to_missing_root():
    e = bh.Edge(blocked="child-1", blocker="root-x", dep_type="parent-child", target=None)
    assert e.classify() == bh.TRUE_ORPHAN


def test_healthy_edge_to_existing_non_gate_is_not_a_finding():
    e = bh.Edge(blocked="b-1", blocker="t-2", dep_type="blocks", target=task("t-2"))
    assert e.classify() == "healthy"


# --- repair safety contract ---------------------------------------------------

def test_only_truly_dangling_is_removable():
    assert bh.REMOVABLE == {bh.TRULY_DANGLING}
    for cls in (bh.LIVE_GATE, bh.SATISFIED_GATE, bh.TRUE_ORPHAN):
        assert cls in bh.PRESERVE
        assert cls not in bh.REMOVABLE


def test_report_removable_excludes_gates_and_orphans():
    edges = [
        bh.Edge("b-1", "g-open", "blocks", gate("g-open", "open")),       # live-gate
        bh.Edge("b-2", "g-closed", "blocks", gate("g-closed", "closed")), # satisfied-gate
        bh.Edge("b-3", "ghost", "blocks", None),                          # truly-dangling
        bh.Edge("c-1", "root-x", "parent-child", None),                   # true-orphan
    ]
    report = bh.classify_edges(edges)
    assert len(report.removable) == 1
    assert report.removable[0]["blocker"] == "ghost"
    assert {f["blocker"] for f in report.findings[bh.LIVE_GATE]} == {"g-open"}


# --- the #29 regression: 11 live-gate edges must NOT be flagged dangling ------

def test_issue29_eleven_live_gate_edges_classify_as_live_gate_not_dangling():
    """Reproduces the real incident: 11 edges pointing at OPEN gates.

    The ad-hoc audit diffed edges against `bd list` (which HIDES gate beads), so all 11
    resolved to "missing" and were flagged dangling — blindly removing them would have
    un-gated 7 live beads. The correct audit resolves targets via `bd show` (sees gates)
    and classifies an open gate as live-gate. NONE may be truly-dangling.
    """
    gate_names = [
        "Gate: Substrate Foundation", "Gate: human", "Gate: Hoist",
        "Gate: Substrate Foundation", "Gate: human", "Gate: Hoist",
        "Gate: human", "Gate: human", "Gate: Hoist",
        "Gate: Substrate Foundation", "Gate: human",
    ]
    # 7 of the 11 blocked beads are distinct live beads that would have been un-gated.
    blocked = [f"work-{i}" for i in range(11)]
    edges = [
        bh.Edge(blocked=blocked[i], blocker=f"gate-{i}", dep_type="blocks",
                target={"id": f"gate-{i}", "issue_type": "gate", "status": "open",
                        "title": gate_names[i]})
        for i in range(11)
    ]
    report = bh.classify_edges(edges)

    assert len(report.findings.get(bh.LIVE_GATE, [])) == 11
    assert report.findings.get(bh.TRULY_DANGLING, []) == []
    assert report.removable == []          # nothing proposed for removal => no un-gating
    for e in edges:
        assert e.classify() == bh.LIVE_GATE


def test_issue29_mixed_universe_still_isolates_the_one_real_dangling():
    """Same incident plus one genuinely dangling edge — only that one is removable."""
    edges = [
        bh.Edge(f"w-{i}", f"g-{i}", "blocks",
                {"id": f"g-{i}", "issue_type": "gate", "status": "open"})
        for i in range(11)
    ]
    edges.append(bh.Edge("w-x", "deleted-bead", "blocks", None))  # the one true dangler
    report = bh.classify_edges(edges)
    assert len(report.findings[bh.LIVE_GATE]) == 11
    assert len(report.removable) == 1
    assert report.removable[0]["blocker"] == "deleted-bead"


# --- collect_edges resolves targets via the resolver (bd show), not bd list ---

def test_collect_edges_resolves_gate_target_hidden_from_universe():
    """A gate target absent from the (bd list) universe is still resolved via the resolver,
    so its edge is correctly live-gate — the structural fix for the #29 false positive."""
    universe = {"b-1": task("b-1")}  # gate intentionally absent (bd list hides it)
    shown = {
        "b-1": {"id": "b-1", "dependencies": [
            {"id": "g-1", "dependency_type": "blocks", "issue_type": "gate", "status": "open"}
        ]},
        "g-1": gate("g-1", "open"),
    }
    edges = bh.collect_edges(universe, resolver=lambda i: shown.get(i))
    assert len(edges) == 1
    assert edges[0].classify() == bh.LIVE_GATE


# --- defensive bd JSON parsing (delegated contract from yf-beads-extra) --------

def test_parse_bd_json_handles_warning_prefix_and_array():
    txt = "warning: auto-export pending\n[{\"id\": \"a-1\", \"status\": \"open\"}]"
    parsed = bh.parse_bd_json(txt)
    assert bh.rows_of(parsed)[0]["id"] == "a-1"


def test_parse_bd_json_empty_is_none():
    assert bh.parse_bd_json("") is None
    assert bh.parse_bd_json("   ") is None
