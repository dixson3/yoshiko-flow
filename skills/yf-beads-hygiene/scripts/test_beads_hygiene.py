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


# --- REQ-HYG-011: classify_active (the canonical active-set core, plan-013 B.1) ---

def _bead(id_, status="open", owner="", issue_type="task"):
    return {"id": id_, "status": status, "owner": owner, "issue_type": issue_type}


def _pc_edge(child, parent):
    """A parent-child edge as collect_edges produces it: blocked=child depends-on blocker=parent."""
    return bh.Edge(blocked=child, blocker=parent, dep_type="parent-child", target=None)


def test_classify_active_in_progress_is_active():
    beads = {"a": _bead("a", status="in_progress")}
    rep = bh.classify_active(beads, [])
    assert rep.active == ["a"]
    assert rep.non_active == []
    assert rep.reasons["a"] == bh.ACTIVE_IN_PROGRESS


def test_classify_active_open_and_claimed_is_active():
    beads = {"a": _bead("a", status="open", owner="user@example.com")}
    rep = bh.classify_active(beads, [])
    assert rep.active == ["a"]
    assert rep.reasons["a"] == bh.ACTIVE_CLAIMED


def test_classify_active_open_ancestor_of_active_child_is_active():
    """An OPEN parent-chain ancestor (walk parent-child edges) of an active bead is active."""
    beads = {
        "epic": _bead("epic", status="open", issue_type="epic"),
        "mol": _bead("mol", status="open", issue_type="molecule"),
        "task": _bead("task", status="in_progress"),  # the active leaf
    }
    edges = [_pc_edge("task", "mol"), _pc_edge("mol", "epic")]  # task -> mol -> epic
    rep = bh.classify_active(beads, edges)
    assert set(rep.active) == {"task", "mol", "epic"}
    assert rep.reasons["mol"] == bh.ACTIVE_ANCESTOR
    assert rep.reasons["epic"] == bh.ACTIVE_ANCESTOR
    assert rep.non_active == []


def test_classify_active_open_unclaimed_is_non_active():
    beads = {"a": _bead("a", status="open", owner="")}
    rep = bh.classify_active(beads, [])
    assert rep.non_active == ["a"]
    assert rep.active == []


def test_classify_active_blocked_is_non_active():
    beads = {"a": _bead("a", status="blocked", owner="user@example.com")}
    rep = bh.classify_active(beads, [])
    # blocked is never active even when claimed (only in_progress / open+owner / open-ancestor).
    assert rep.non_active == ["a"]
    assert rep.active == []


def test_classify_active_deferred_is_non_active():
    beads = {"a": _bead("a", status="deferred")}
    rep = bh.classify_active(beads, [])
    assert rep.non_active == ["a"]


def test_classify_active_closed_excluded_from_both_buckets():
    beads = {
        "live": _bead("live", status="in_progress"),
        "done": _bead("done", status="closed"),
    }
    rep = bh.classify_active(beads, [])
    assert rep.active == ["live"]
    assert rep.non_active == []
    assert "done" not in rep.reasons


def test_classify_active_closed_ancestor_not_promoted():
    """A closed ancestor of an active bead is NOT promoted (closed beads are excluded)."""
    beads = {
        "epic": _bead("epic", status="closed", issue_type="epic"),
        "task": _bead("task", status="in_progress"),
    }
    edges = [_pc_edge("task", "epic")]
    rep = bh.classify_active(beads, edges)
    assert rep.active == ["task"]
    assert "epic" not in rep.reasons


# --- REQ-HYG-011: find_obsolete_upstream (delivered-signal classifier, plan-013 B.1) ---

def test_find_obsolete_complete_plan_is_obsolete():
    issues = [{"number": 35, "title": "track", "plan": "plan-012"}]
    out = bh.find_obsolete_upstream(issues, plan_status_lookup=lambda r: "complete")
    assert len(out[bh.OBSOLETE]) == 1
    assert out[bh.OBSOLETE][0]["signal"] == bh.OBSOLETE_PLAN_COMPLETE
    assert out[bh.FLAG_FOR_REVIEW] == []


def test_find_obsolete_incomplete_plan_is_not_obsolete():
    issues = [{"number": 38, "title": "track", "plan": "plan-013"}]
    out = bh.find_obsolete_upstream(issues, plan_status_lookup=lambda r: "approved")
    assert out[bh.OBSOLETE] == []
    assert len(out[bh.FLAG_FOR_REVIEW]) == 1
    assert out[bh.FLAG_FOR_REVIEW][0]["signal"] == "unresolvable"


def test_find_obsolete_unresolvable_is_flag_for_review_never_obsolete():
    issues = [{"number": 99, "title": "no linked plan"}]
    out = bh.find_obsolete_upstream(issues, plan_status_lookup=lambda r: None)
    assert out[bh.OBSOLETE] == []
    assert len(out[bh.FLAG_FOR_REVIEW]) == 1


def test_find_obsolete_merged_pr_signal_is_obsolete():
    issues = [{"number": 40, "title": "track", "plan": "plan-013"}]
    out = bh.find_obsolete_upstream(
        issues,
        plan_status_lookup=lambda r: "approved",     # plan not complete
        pr_merged_lookup=lambda i: True,              # but linked PR merged
    )
    assert len(out[bh.OBSOLETE]) == 1
    assert out[bh.OBSOLETE][0]["signal"] == bh.OBSOLETE_PR_MERGED


# --- B.3: gated reconcile --apply delegates hoist to yf-beads-upstream --------

import json as _json
import types


class _Args:
    """Minimal argparse.Namespace stand-in for cmd_reconcile."""
    def __init__(self, **kw):
        self.json = kw.get("json", False)
        self.apply = kw.get("apply", False)
        self.yes = kw.get("yes", False)
        self.record = kw.get("record", None)


def _stub_reconcile_env(monkeypatch, beads, *, gh_issues=None, plan_status=None):
    """Stub every live-DB / shell touchpoint so cmd_reconcile runs purely on fixtures.

    `beads` is {id: bead-dict}. No `bd`, no `gh`, no plan-disk read, no real shell-out.
    """
    monkeypatch.setattr(bh, "db_is_wedged", lambda: (False, ""))
    monkeypatch.setattr(bh, "load_universe", lambda: beads)
    # collect_edges drives off bd show; with no parent-child edges the active set is
    # decided directly. Return [] so classify_active uses status/owner only.
    monkeypatch.setattr(bh, "collect_edges", lambda universe, resolver=bh.show: [])
    monkeypatch.setattr(bh, "gh_issue_list", lambda: list(gh_issues or []))
    monkeypatch.setattr(bh, "_plan_status_from_disk", lambda ref: plan_status)


def test_reconcile_default_is_read_only_no_delegation(monkeypatch, capsys):
    """Default reconcile (no --apply) never delegates a hoist."""
    beads = {"a": _bead("a", status="open", owner="")}  # non-active => candidate
    _stub_reconcile_env(monkeypatch, beads)
    calls = []
    rc = bh.cmd_reconcile(_Args(apply=False), runner=lambda cmd: calls.append(cmd))
    assert rc == 0
    assert calls == []  # nothing delegated without --apply
    assert "Dry run" in capsys.readouterr().out


def test_reconcile_apply_yes_delegates_each_non_active_bead(monkeypatch, capsys):
    """--apply --yes delegates ONE upstream hoist per non-active bead, unattended."""
    beads = {
        "a": _bead("a", status="open", owner=""),                 # non-active
        "b": _bead("b", status="in_progress"),                    # active -> NOT hoisted
        "c": _bead("c", status="deferred"),                       # non-active
    }
    _stub_reconcile_env(monkeypatch, beads)
    calls = []
    rc = bh.cmd_reconcile(
        _Args(apply=True, yes=True), runner=lambda cmd: calls.append(cmd), script="/x/upstream.py"
    )
    assert rc == 0
    hoisted_ids = {cmd[cmd.index("--issues") + 1] for cmd in calls}
    assert hoisted_ids == {"a", "c"}          # active "b" not hoisted
    for cmd in calls:
        assert cmd[:4] == ["uv", "run", "/x/upstream.py", "hoist"]
        assert cmd[-1] == "--apply"
        assert "--dest" in cmd


def test_reconcile_apply_without_yes_requires_confirm(monkeypatch):
    """--apply without --yes calls _confirm(); a declined confirm makes NO delegation."""
    beads = {"a": _bead("a", status="open", owner="")}
    _stub_reconcile_env(monkeypatch, beads)
    monkeypatch.setattr(bh, "_confirm", lambda prompt: False)  # operator declines
    calls = []
    rc = bh.cmd_reconcile(_Args(apply=True, yes=False), runner=lambda cmd: calls.append(cmd))
    assert rc == 1
    assert calls == []


def test_reconcile_apply_confirm_accepted_delegates(monkeypatch):
    beads = {"a": _bead("a", status="open", owner="")}
    _stub_reconcile_env(monkeypatch, beads)
    monkeypatch.setattr(bh, "_confirm", lambda prompt: True)
    calls = []
    rc = bh.cmd_reconcile(_Args(apply=True, yes=False),
                          runner=lambda cmd: calls.append(cmd), script="/x/upstream.py")
    assert rc == 0
    assert len(calls) == 1
    assert calls[0][calls[0].index("--issues") + 1] == "a"


def test_reconcile_record_writes_round_trip_json(monkeypatch, tmp_path):
    """--record writes a JSON record reversible via upstream.py unhoist --record."""
    beads = {"a": _bead("a", status="open", owner="")}
    _stub_reconcile_env(monkeypatch, beads)
    rec = tmp_path / "hoist-record.json"
    rc = bh.cmd_reconcile(
        _Args(apply=True, yes=True, record=str(rec)),
        runner=lambda cmd: None, script="/x/upstream.py",
    )
    assert rc == 0
    data = _json.loads(rec.read_text())
    assert [h["id"] for h in data["hoisted"]] == ["a"]
    entry = data["hoisted"][0]
    assert "dest" in entry and "command" in entry
    assert entry["command"][:4] == ["uv", "run", "/x/upstream.py", "hoist"]


def test_reconcile_obsolete_upstream_never_auto_closed(monkeypatch):
    """Obsolete-upstream findings are proposal-only: --apply delegates hoists but the only
    runner calls are upstream HOISTS — no close of any upstream issue."""
    beads = {"a": _bead("a", status="open", owner="")}
    # An upstream issue whose linked plan is complete => classified OBSOLETE.
    gh_issues = [{"number": 35, "title": "track plan-012", "plan_ref": "plan-012"}]
    _stub_reconcile_env(monkeypatch, beads, gh_issues=gh_issues, plan_status="complete")
    calls = []
    rc = bh.cmd_reconcile(
        _Args(apply=True, yes=True), runner=lambda cmd: calls.append(cmd), script="/x/upstream.py"
    )
    assert rc == 0
    # Every delegated command is a hoist; none references the obsolete issue / a close.
    assert all(cmd[3] == "hoist" for cmd in calls)
    assert not any("close" in c or "35" in c for cmd in calls for c in cmd)
    # The hoist is for the local non-active bead only.
    assert {cmd[cmd.index("--issues") + 1] for cmd in calls} == {"a"}


def test_reconcile_apply_no_candidates_no_delegation(monkeypatch, capsys):
    """--apply with only active beads delegates nothing."""
    beads = {"b": _bead("b", status="in_progress")}
    _stub_reconcile_env(monkeypatch, beads)
    calls = []
    rc = bh.cmd_reconcile(_Args(apply=True, yes=True), runner=lambda cmd: calls.append(cmd))
    assert rc == 0
    assert calls == []
    assert "Nothing to hoist" in capsys.readouterr().out


def test_dest_for_uses_plan_ref_then_falls_back_to_id():
    assert bh._dest_for({"id": "x-1", "plan": "plan-013"}) == "plan-013"
    assert bh._dest_for({"id": "x-2", "title": "fix for plan-009 thing"}) == "plan-009"
    assert bh._dest_for({"id": "x-3", "title": "no ref"}) == "x-3"
