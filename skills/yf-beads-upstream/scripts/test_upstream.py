# /// script
# requires-python = ">=3.11"
# ///
"""Tests for upstream.py — config knobs, follow-on detection, hoist/un-hoist planning.

Run:  uv run --with pytest python3 -m pytest test_upstream.py -q

The pure layers (config readers with an injected `config_get`, candidate_filter,
parse_json_array, external regex, detect_followons with injected query closures,
plan_hoist / plan_unhoist command builders) are exercised WITHOUT a live bd or
network — every bd interaction is faked.
"""
import importlib.util
import sys
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "upstream", Path(__file__).parent / "upstream.py"
)
up = importlib.util.module_from_spec(_spec)
sys.modules["upstream"] = up
_spec.loader.exec_module(up)


def fake_config(values):
    """Return a config_get(key)->text reader backed by an in-memory dict.

    A key absent from `values` simulates an unset key: bd prints `(not set)`.
    """
    def _get(key):
        return values.get(key, "(not set)\n")
    return _get


# --- A.1 granularity ----------------------------------------------------------

def test_granularity_coarse_explicit():
    g = fake_config({"custom.upstream.granularity": "coarse\n"})
    assert up.granularity(g) == "coarse"


def test_granularity_granular_explicit():
    g = fake_config({"custom.upstream.granularity": "granular\n"})
    assert up.granularity(g) == "granular"


def test_granularity_unset_defaults_coarse():
    g = fake_config({})  # key absent -> (not set)
    assert up.granularity(g) == "coarse"


def test_granularity_unrecognized_value_defaults_coarse():
    g = fake_config({"custom.upstream.granularity": "weekly\n"})
    assert up.granularity(g) == "coarse"


def test_granularity_never_trusts_exit_code():
    # (not set) substring wins even with surrounding whitespace/noise.
    g = fake_config({"custom.upstream.granularity": "  (not set)  \n"})
    assert up.granularity(g) == "coarse"


# --- A.2 auto_hoist_followons (default-DENY) ----------------------------------

def test_auto_hoist_true():
    g = fake_config({"custom.upstream.auto_hoist_followons": "true\n"})
    assert up.auto_hoist_followons(g) is True


def test_auto_hoist_false():
    g = fake_config({"custom.upstream.auto_hoist_followons": "false\n"})
    assert up.auto_hoist_followons(g) is False


def test_auto_hoist_unset_denies():
    assert up.auto_hoist_followons(fake_config({})) is False


def test_auto_hoist_other_value_denies():
    g = fake_config({"custom.upstream.auto_hoist_followons": "yes\n"})
    assert up.auto_hoist_followons(g) is False


def test_auto_hoist_empty_denies():
    g = fake_config({"custom.upstream.auto_hoist_followons": "\n"})
    assert up.auto_hoist_followons(g) is False


# --- pure helpers -------------------------------------------------------------

def test_candidate_filter_drops_containers():
    rows = [
        {"id": "a", "issue_type": "task"},
        {"id": "e", "issue_type": "epic"},
        {"id": "m", "issue_type": "molecule"},
        {"id": "g", "issue_type": "gate"},
        {"id": "b", "issue_type": "bug"},
    ]
    kept = [r["id"] for r in up.candidate_filter(rows)]
    assert kept == ["a", "b"]


def test_parse_json_array_tolerates_warning_prefix():
    text = 'WARN: db locked\n[{"id":"x"}]'
    assert up.parse_json_array(text) == [{"id": "x"}]


def test_external_regex_anchored():
    body = "Some description mentioning External: not a url\nExternal: https://github.com/o/r/issues/1\n"
    m = up.EXTERNAL_RE.search(body)
    assert m and m.group(1) == "https://github.com/o/r/issues/1"


# --- C.2 follow-on detection --------------------------------------------------

def make_followon_fixture():
    """A subtree: m (molecule), t1 (open, discovered-from m -> narrow),
    t2 (in_progress, created after intake -> broad but NOT narrow),
    t3 (open, no discovered-from edge, created before intake -> neither)."""
    intake = "2026-06-24T00:00:00Z"
    subtree = [
        {"id": "m", "issue_type": "molecule", "status": "open", "created_at": "2026-06-23T00:00:00Z"},
        {"id": "t1", "status": "open", "created_at": "2026-06-25T00:00:00Z"},
        {"id": "t2", "status": "in_progress", "created_at": "2026-06-26T00:00:00Z"},
        {"id": "t3", "status": "open", "created_at": "2026-06-20T00:00:00Z"},
    ]
    deps = {
        # discovered-from edge into the subtree (target m). `type` field (bd dep list shape).
        "t1": [{"type": "discovered-from", "depends_on_id": "m"}],
        # t2 also discovered-from m, but it is in_progress -> active -> NOT narrow.
        "t2": [{"dependency_type": "discovered-from", "depends_on_id": "m"}],
        "t3": [],
        "m": [],
    }
    return intake, subtree, deps


def _runner(intake, subtree, deps):
    return up.detect_followons(
        "m", intake,
        list_subtree=lambda pid: subtree,
        deps_for=lambda bid: deps.get(bid, []),
    )


def test_narrow_signal_detects_discovered_from_nonactive():
    intake, subtree, deps = make_followon_fixture()
    result = _runner(intake, subtree, deps)
    assert result["narrow"] == ["t1"]


def test_false_positive_guard_inprogress_after_intake_not_narrow():
    # THE GUARD: t2 is in_progress, created after intake under the subtree.
    # It must NOT be in the narrow (auto) set even though it has a discovered-from edge.
    intake, subtree, deps = make_followon_fixture()
    result = _runner(intake, subtree, deps)
    assert "t2" not in result["narrow"]
    # but it IS a broad (gated-only) candidate, since created after intake.
    assert "t2" in result["broad"]


def test_broad_signal_is_created_after_intake():
    intake, subtree, deps = make_followon_fixture()
    result = _runner(intake, subtree, deps)
    # t1 and t2 created after intake; t3/m before -> not broad.
    assert set(result["broad"]) == {"t1", "t2"}
    assert "t3" not in result["broad"]


def test_edge_type_handles_both_field_names():
    assert up.edge_type({"dependency_type": "discovered-from"}) == "discovered-from"
    assert up.edge_type({"type": "blocks"}) == "blocks"
    assert up.edge_type({}) is None


# --- C.1 hoist planning -------------------------------------------------------

def test_hoist_issue_count_coarse_is_one_per_plan():
    assert up.hoist_issue_count(["a", "b", "c"], "coarse") == 1


def test_hoist_issue_count_granular_is_one_per_bead():
    assert up.hoist_issue_count(["a", "b", "c"], "granular") == 3


def test_hoist_issue_count_empty():
    assert up.hoist_issue_count([], "coarse") == 0


def test_close_reason_records_destination():
    reason = up.close_reason("plan-013")
    assert "plan-013" in reason
    assert "tombstone" in reason.lower()


def test_plan_hoist_dry_run_push_first_then_real_then_close():
    cmds = up.plan_hoist(["a", "b"], "plan-013", backend="github", gran="coarse")
    # dry-run push must precede the real push
    dry_idx = next(i for i, c in enumerate(cmds) if "push" in c and "--dry-run" in c)
    real_idx = next(i for i, c in enumerate(cmds) if "push" in c and "--dry-run" not in c)
    assert dry_idx < real_idx
    # never a bare sync
    assert all("sync" not in c for c in cmds)
    # inline auth only, never config
    assert all("$(gh auth token)" in c for c in cmds if "push" in c)
    # reversible close (never delete), one per bead, records destination
    closes = [c for c in cmds if c.startswith("bd close")]
    assert len(closes) == 2
    assert all("plan-013" in c for c in closes)
    assert all("bd delete" not in c for c in cmds)


def test_plan_hoist_backend_threads_into_push_and_auth():
    cmds = up.plan_hoist(["x"], "plan-013", backend="github", gran="granular")
    push_cmds = [c for c in cmds if "push" in c]
    assert push_cmds, "expected at least the dry-run + real push"
    assert all("bd github push" in c for c in push_cmds)
    assert all("$(gh auth token)" in c for c in push_cmds)


def test_plan_hoist_gitlab_backend_uses_glab_auth():
    cmds = up.plan_hoist(["x"], "plan-013", backend="gitlab", gran="coarse")
    push_cmds = [c for c in cmds if "push" in c]
    assert all("bd gitlab push" in c for c in push_cmds)
    assert all("GITLAB_TOKEN=$(glab auth token)" in c for c in push_cmds)


# --- C.4 un-hoist round-trip --------------------------------------------------

def test_plan_unhoist_reopens_each_id():
    cmds = up.plan_unhoist(["a", "b"])
    assert cmds == ["bd update a --status open", "bd update b --status open"]


def test_unhoist_record_round_trip(tmp_path, capsys):
    # Write a record file of hoisted ids; unhoist (dry-run) reads and reopens them.
    rec = tmp_path / "hoisted.txt"
    rec.write_text("a\nb\n c \n")
    rc = up.cmd_unhoist(None, str(rec), apply=False)
    assert rc == 0
    out = capsys.readouterr().out
    assert "bd update a --status open" in out
    assert "bd update b --status open" in out
    assert "bd update c --status open" in out
    assert "Dry run" in out


def test_hoist_dry_run_default_does_not_apply(capsys):
    rc = up.cmd_hoist("a,b", "plan-013", "github", apply=False)
    assert rc == 0
    out = capsys.readouterr().out
    assert "--dry-run" in out
    assert "Dry run" in out


def test_is_nonactive_classification():
    assert up.is_nonactive({"status": "open"}) is True
    assert up.is_nonactive({"status": "open", "owner": "alice"}) is False  # claimed
    assert up.is_nonactive({"status": "in_progress"}) is False
    assert up.is_nonactive({"status": "blocked"}) is True
    assert up.is_nonactive({"status": "deferred"}) is True
    assert up.is_nonactive({"status": "closed"}) is False


# --- C.7 ported classifier (verbatim copy) ------------------------------------

def test_classify_active_matches_glossary():
    beads = {
        "ip": {"status": "in_progress"},
        "claimed": {"status": "open", "owner": "alice"},
        "open_unclaimed": {"status": "open"},
        "blocked": {"status": "blocked"},
        "closed": {"status": "closed"},
    }
    rep = up.classify_active(beads, [])
    assert set(rep.active) == {"ip", "claimed"}
    assert set(rep.non_active) == {"open_unclaimed", "blocked"}
    # closed is excluded from both buckets
    assert "closed" not in rep.active and "closed" not in rep.non_active


def test_classify_active_open_ancestor_of_active_is_active():
    # epic (open, unclaimed) is the parent of an in_progress task -> epic is ACTIVE.
    beads = {
        "epic": {"status": "open"},
        "task": {"status": "in_progress"},
    }
    edges = [up.Edge(blocked="task", blocker="epic", dep_type="parent-child", target=beads["epic"])]
    rep = up.classify_active(beads, edges)
    assert "epic" in rep.active
    assert rep.reasons["epic"] == up.ACTIVE_ANCESTOR


# --- C.7 ENUMERATE-PARITY regression -----------------------------------------
#
# The refactored enumerate computes candidates as the NON-ACTIVE set from the single
# active-set classifier instead of the old status-only CANDIDATE_STATUSES slice. The
# ONLY intended behavior change vs the old status-only filter is the owner/ancestor
# refinement: a claimed-open bead (owner set) and an open ANCESTOR of an active bead
# are now correctly EXCLUDED from the candidate set (they are active work, not parked
# push candidates). All other statuses partition exactly as before. Container types
# (epic/molecule/gate) are still dropped. This test pins that behavior with no live bd.

def make_enumerate_universe():
    """A fixture universe spanning every relevant case.

      t_open       open, unclaimed, task        -> NON-ACTIVE candidate (unchanged)
      t_blocked    blocked, task                 -> NON-ACTIVE candidate (unchanged)
      t_deferred   deferred, task                -> NON-ACTIVE candidate (unchanged)
      t_claimed    open + owner, task            -> EXCLUDED now (owner refinement)
      t_ip         in_progress, task             -> EXCLUDED (active, unchanged)
      t_closed     closed, task                  -> EXCLUDED (not a candidate, unchanged)
      epic_anc     open epic, parent of t_ip     -> EXCLUDED now (open ancestor of active)
      epic_parked  open epic, parent of t_open   -> dropped as a container type anyway
    """
    beads = {
        "t_open": {"id": "t_open", "status": "open", "issue_type": "task"},
        "t_blocked": {"id": "t_blocked", "status": "blocked", "issue_type": "task"},
        "t_deferred": {"id": "t_deferred", "status": "deferred", "issue_type": "task"},
        "t_claimed": {"id": "t_claimed", "status": "open", "owner": "alice", "issue_type": "task"},
        "t_ip": {"id": "t_ip", "status": "in_progress", "issue_type": "task"},
        "t_closed": {"id": "t_closed", "status": "closed", "issue_type": "task"},
        "epic_anc": {"id": "epic_anc", "status": "open", "issue_type": "epic"},
        "epic_parked": {"id": "epic_parked", "status": "open", "issue_type": "epic"},
    }
    edges = [
        up.Edge(blocked="t_ip", blocker="epic_anc", dep_type="parent-child", target=beads["epic_anc"]),
        up.Edge(blocked="t_open", blocker="epic_parked", dep_type="parent-child", target=beads["epic_parked"]),
    ]
    return beads, edges


def test_enumerate_parity_nonactive_set():
    beads, edges = make_enumerate_universe()
    candidates = {r["id"] for r in up.enumerate_candidates(beads, edges)}
    # The three plain non-active work items survive (parity with the old filter).
    assert candidates == {"t_open", "t_blocked", "t_deferred"}
    # Owner/ancestor refinement: claimed-open and the active bead's open ancestor are gone.
    assert "t_claimed" not in candidates   # claimed-open -> active now
    assert "epic_anc" not in candidates    # open ancestor of active in_progress -> active now
    # Unchanged exclusions: in_progress, closed, and container types.
    assert "t_ip" not in candidates
    assert "t_closed" not in candidates
    assert "epic_parked" not in candidates  # dropped as container (and is itself non-active)


# --- C.3 land-the-plane hoist -------------------------------------------------

def test_land_default_proposes_whole_batch_requires_confirm():
    followons = {"narrow": ["t1"], "broad": ["t1", "t2"]}
    d = up.plan_land_hoist(followons, auto=False)
    # default: nothing auto-eligible; whole de-duped batch needs a single confirm.
    assert d["auto_eligible"] == []
    assert set(d["requires_confirm"]) == {"t1", "t2"}
    assert d["mode"] == "propose"


def test_land_auto_hoists_narrow_only_broad_excluded():
    followons = {"narrow": ["t1"], "broad": ["t1", "t2"]}
    d = up.plan_land_hoist(followons, auto=True)
    # no-prompt: ONLY narrow is auto-eligible; broad-only stays gated.
    assert d["auto_eligible"] == ["t1"]
    assert d["requires_confirm"] == ["t2"]   # t2 is broad-only -> never auto
    assert "t2" not in d["auto_eligible"]
    assert d["mode"] == "auto"


def test_land_non_followon_never_auto_hoisted():
    # A bead that is not a detected follow-on (absent from narrow AND broad) can never
    # appear in auto_eligible — even under auto. plan_land_hoist only ever surfaces
    # ids that detect_followons classified.
    followons = {"narrow": ["t1"], "broad": []}
    d = up.plan_land_hoist(followons, auto=True)
    assert "x_unrelated" not in d["auto_eligible"]
    assert "x_unrelated" not in d["proposed"]
    assert d["auto_eligible"] == ["t1"]


def test_cmd_land_default_dry_run_no_apply(monkeypatch, capsys):
    # Default path (auto_hoist disabled): emits a proposal + Dry run, never executes.
    monkeypatch.setattr(up, "auto_hoist_followons", lambda *a, **k: False)
    monkeypatch.setattr(up, "granularity", lambda *a, **k: "coarse")
    monkeypatch.setattr(
        up, "detect_followons",
        lambda *a, **k: {"narrow": ["t1"], "broad": ["t1", "t2"]},
    )
    executed = []
    monkeypatch.setattr(up, "run", lambda cmd: executed.append(cmd) or "[]")
    rc = up.cmd_land("m", "2026-06-24T00:00:00Z", "plan-013", "github", apply=False)
    assert rc == 0
    out = capsys.readouterr().out
    assert "single confirm required" in out
    assert "Dry run" in out
    # NOTHING was hoisted (no bash -c executed) without --apply.
    assert not any(c[:2] == ["bash", "-c"] for c in executed)


def test_cmd_land_auto_path_narrow_only(monkeypatch, capsys):
    # auto_hoist enabled: the narrow set is auto-eligible (no prompt) while broad-only
    # stays gated. Still dry-run here (apply=False) so nothing executes.
    monkeypatch.setattr(up, "auto_hoist_followons", lambda *a, **k: True)
    monkeypatch.setattr(up, "granularity", lambda *a, **k: "coarse")
    monkeypatch.setattr(
        up, "detect_followons",
        lambda *a, **k: {"narrow": ["t1"], "broad": ["t1", "t2"]},
    )
    monkeypatch.setattr(up, "run", lambda cmd: "[]")
    rc = up.cmd_land("m", "2026-06-24T00:00:00Z", "plan-013", "github", apply=False)
    assert rc == 0
    out = capsys.readouterr().out
    assert "NO-PROMPT auto-hoist (narrow only): ['t1']" in out
    assert "Still gated (broad" in out and "t2" in out
