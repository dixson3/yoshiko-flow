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
import json
import sys
from pathlib import Path

import pytest

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


def test_plan_hoist_returns_only_the_local_close_stage():
    """Under gh-direct the upstream write is no longer a shell command string.

    A hoist is now two phases — `create_or_update` (the write) then the local tombstone
    — so `plan_hoist` carries only the second. What must NOT change is the tombstone
    contract: reversible `bd close -r`, one per bead, recording the destination, never
    `bd delete`.
    """
    cmds = up.plan_hoist(["a", "b"], "plan-013", gran="coarse")
    assert len(cmds) == 2
    assert all(c.startswith("bd close") for c in cmds)
    assert all("plan-013" in c for c in cmds)
    assert all("bd delete" not in c for c in cmds)


def test_no_bd_backend_push_command_is_ever_constructed():
    """SC3, as a contract rather than a grep over prose.

    The #129 defect was born in the translation between a comma-separated `--issues`
    and bd's positional ids. gh-direct removes the translation entirely, so the
    invariant is now the stronger one: NO `bd <backend> push` string is emitted at all.
    """
    emitted = up.plan_hoist(["a", "b"], "plan-013", gran="coarse")
    emitted += up.hoist_close_commands(["a"], "plan-013")
    for c in emitted:
        assert "bd github push" not in c
        assert "bd gitlab push" not in c
        assert " sync" not in c


def test_the_deleted_bd_push_machinery_is_actually_gone():
    """Guard against a half-finished migration leaving both mechanisms in place.

    Two coexisting write paths with different failure modes is the exact condition
    that produced #129, so its absence is asserted rather than assumed.
    """
    for dead in ("BACKEND_AUTH", "push_command_sequence", "verified_push",
                 "parse_pushed_count", "plan_push", "DEFAULT_BACKEND"):
        assert not hasattr(up, dead), f"{dead} should have been deleted by plan-040"


# --- REQ-BUP-054: the field mapping ------------------------------------------

def test_field_mapping_derives_type_and_priority_labels():
    labels = up.issue_labels_for(
        {"id": "a", "issue_type": "bug", "priority": 1, "labels": []})
    assert labels == ["type::bug", "priority::high"]


def test_priority_table_covers_every_row_including_the_unmapped_ones():
    """P0 and P4 have NO label in this repo — the mapping still names them.

    Naming them is what makes a P0/P4 bead's dropped label a REPORTED drop rather than
    a silent absence.
    """
    assert up.PRIORITY_LABELS == {
        0: "priority::critical", 1: "priority::high", 2: "priority::medium",
        3: "priority::low", 4: "priority::backlog",
    }


def test_bead_labels_pass_through_alongside_derived_labels():
    labels = up.issue_labels_for(
        {"id": "a", "issue_type": "task", "priority": 2, "labels": ["web", "docs"]})
    assert labels == ["type::task", "priority::medium", "web", "docs"]


def test_mapping_never_duplicates_a_label():
    labels = up.issue_labels_for(
        {"id": "a", "issue_type": "task", "priority": 2, "labels": ["type::task"]})
    assert labels.count("type::task") == 1


def test_title_and_body_map_verbatim_and_notes_design_do_not_sync():
    """REQ-BUP-054: `description` is the ONLY body source; notes/design never sync."""
    plan = up.plan_write(
        {"id": "a", "title": "T", "description": "B", "issue_type": "task",
         "priority": 2, "notes": "SECRET-NOTES", "design": "SECRET-DESIGN"},
        {"type::task", "priority::medium"})
    assert plan["title"] == "T"
    assert plan["body"] == "B"
    assert "SECRET-NOTES" not in plan["body"]
    assert "SECRET-DESIGN" not in plan["body"]


# --- REQ-BUP-056: restrict-and-drop, and the drop is REPORTED -----------------

def test_restrict_and_drop_keeps_existing_drops_unknown():
    kept, dropped = up.restrict_labels(
        ["type::task", "type::chore", "priority::medium"],
        {"type::task", "priority::medium"})
    assert kept == ["type::task", "priority::medium"]
    assert dropped == ["type::chore"]


def test_restrict_and_drop_never_creates_a_label(monkeypatch):
    """The policy's whole cost argument is that it takes no label-write scope."""
    def boom(cmd):
        assert "label" not in cmd or "create" not in cmd, \
            f"restrict-and-drop must never create a label: {cmd!r}"
        return "[]"
    monkeypatch.setattr(up, "run", boom)
    up.restrict_labels(["nope"], set())


def test_dropped_label_is_reported_in_the_preview():
    """GR-BUP-008's revisit trigger is THIS LINE. Without it the mitigation for the
    growing-uncovered-set risk has no producer at all (pass-2 D4)."""
    plans = [up.plan_write(
        {"id": "yf-abcd", "title": "T", "description": "B",
         "issue_type": "decision", "priority": 2}, {"priority::medium"})]
    rendered = up.render_plan(plans)
    assert "yf-abcd" in rendered
    assert "type::decision" in rendered
    assert "dropping label" in rendered


def test_drop_report_names_both_the_bead_and_the_label():
    plans = [up.plan_write(
        {"id": "yf-zzzz", "title": "T", "description": "B",
         "issue_type": "chore", "priority": 4}, set())]
    assert plans[0]["dropped_labels"] == ["type::chore", "priority::backlog"]
    assert plans[0]["labels"] == []


# --- REQ-BUP-057: create-vs-update idempotency on external_ref ----------------

def test_a_bead_with_external_ref_produces_an_UPDATE():
    """The `yf-uz5k` -> #92 behavior: the mapping alone drives create-vs-update."""
    plan = up.plan_write(
        {"id": "a", "title": "T", "description": "B", "external_ref": ISSUE_A}, set())
    assert plan["action"] == "update"
    assert plan["external"] == ISSUE_A


def test_a_bead_without_external_ref_produces_a_CREATE():
    plan = up.plan_write({"id": "a", "title": "T", "description": "B"}, set())
    assert plan["action"] == "create"
    assert plan["external"] is None


def test_create_records_the_mapping_so_a_repush_updates_not_duplicates(monkeypatch):
    """Idempotency is what prevents duplicates — so the write-back is not optional."""
    calls = []
    def _run(cmd):
        calls.append(list(cmd))
        if cmd[:3] == ["gh", "issue", "create"]:
            return f"{ISSUE_A}\n"
        return ""
    monkeypatch.setattr(up, "run", _run)
    url = up.apply_write({"id": "a", "action": "create", "external": None,
                          "title": "T", "body": "B", "labels": [],
                          "dropped_labels": []})
    assert url == ISSUE_A
    assert ["bd", "update", "a", "--external-ref", ISSUE_A, "-q"] in calls


# --- REQ-BUP-057: verification is STRUCTURAL and fails closed ----------------

def test_create_with_no_returned_url_FAILS_CLOSED(monkeypatch):
    """A create whose output carries no parseable URL is UNVERIFIED, never 'probably ok'."""
    monkeypatch.setattr(up, "run", lambda cmd: "created something, trust me\n")
    with pytest.raises(up.WriteError) as exc:
        up.apply_write({"id": "a", "action": "create", "external": None,
                        "title": "T", "body": "B", "labels": [], "dropped_labels": []})
    assert "UNVERIFIED" in str(exc.value)


def test_no_test_parses_the_pushed_n_issues_string():
    """SC7, asserted against the implementation.

    plan-040 Issue 1.1 measured that `bd github push --dry-run` ALSO prints the success
    line — it is emitted when nothing was pushed. Any code reintroducing that parse
    would be pinning a string that cannot distinguish a real write from a no-op, so the
    check is that the IMPLEMENTATION contains no such parse.
    """
    impl = (Path(__file__).parent / "upstream.py").read_text()
    assert "PUSHED_COUNT_RE" not in impl
    assert "def parse_pushed_count" not in impl
    assert "def verified_push" not in impl


def test_parse_issue_url_extracts_only_a_real_issue_url():
    assert up.parse_issue_url(f"{ISSUE_A}\n") == ISSUE_A
    assert up.parse_issue_url("no url here") is None
    assert up.parse_issue_url("") is None
    assert up.parse_issue_url(None) is None


def test_a_failed_gh_call_raises_WriteError_not_SystemExit(monkeypatch):
    """`run()` raises SystemExit (a BaseException).

    A handler catching only `Exception` would let it escape and bypass the fail-closed
    path entirely — the destructive stage's guard would simply not run.
    """
    def _boom(cmd):
        raise SystemExit("command failed (1): gh issue create")
    monkeypatch.setattr(up, "run", _boom)
    with pytest.raises(up.WriteError):
        up.apply_write({"id": "a", "action": "create", "external": None,
                        "title": "T", "body": "B", "labels": [], "dropped_labels": []})


def test_external_ref_writeback_failure_is_loud_and_names_the_duplicate_risk(monkeypatch):
    """Issue created but mapping unrecorded is the ONE unrecoverable-by-retry state:
    re-running would create a second issue. It must say so, with the repair command."""
    def _run(cmd):
        if cmd[:3] == ["gh", "issue", "create"]:
            return f"{ISSUE_A}\n"
        raise SystemExit("bd exploded")
    monkeypatch.setattr(up, "run", _run)
    with pytest.raises(up.WriteError) as exc:
        up.apply_write({"id": "a", "action": "create", "external": None,
                        "title": "T", "body": "B", "labels": [], "dropped_labels": []})
    msg = str(exc.value)
    assert "DUPLICATE" in msg
    assert "bd update a --external-ref" in msg


# --- SC13: the live already-mapped population survives the swap ---------------

def test_stale_or_deleted_issue_ref_is_an_update_that_fails_closed(monkeypatch):
    """SC13, driven by a REAL fixture rather than a synthetic one.

    Bead `yf-nzdv` carries an external_ref pointing at issue #139, which plan-040 Issue
    1.1 created and then DELETED. A stale ref must fail closed with a named reason —
    never silently fall back to creating a duplicate.
    """
    monkeypatch.setattr(up, "run", lambda cmd: (_ for _ in ()).throw(
        SystemExit("command failed (1): gh issue edit")))
    with pytest.raises(up.WriteError) as exc:
        up.apply_write({"id": "yf-nzdv", "action": "update",
                        "external": "https://github.com/dixson3/yoshiko-flow/issues/139",
                        "title": "T", "body": "B", "labels": [], "dropped_labels": []})
    assert "yf-nzdv" in str(exc.value)
    assert "edit failed" in str(exc.value)


def test_a_non_url_external_ref_is_still_treated_as_mapped():
    """Bead `yf-4d7s` carries the bare form `gh-91` (38 of 39 refs are full URLs).

    It must NOT read as unmapped — that would create a duplicate issue for a bead that
    already has one. It reads as an update, which then fails closed upstream if the ref
    does not resolve. Wrong-but-loud beats silently-duplicating.
    """
    plan = up.plan_write({"id": "yf-4d7s", "title": "T", "description": "B",
                          "external_ref": "gh-91"}, set())
    assert plan["action"] == "update"
    assert plan["external"] == "gh-91"


# --- REQ-BUP-051: the `push` verb, preview-first and preview-local ------------

def test_push_without_apply_writes_nothing(monkeypatch, capsys):
    monkeypatch.setattr(up, "upstream_enabled", lambda: True)
    monkeypatch.setattr(up, "load_universe_rows", lambda: [
        {"id": "a", "title": "T", "description": "B", "issue_type": "task",
         "priority": 2}])
    monkeypatch.setattr(up, "existing_labels", lambda: {"type::task", "priority::medium"})
    def boom(cmd):
        raise AssertionError(f"push executed {cmd!r} without --apply")
    monkeypatch.setattr(up, "run", boom)
    monkeypatch.setattr(up, "owner_claim_warning_lines", lambda: [])
    assert up.cmd_push("a", apply=False) == 0
    out = capsys.readouterr().out
    assert "Preview only" in out
    assert "[create]" in out


def test_push_preview_needs_no_network_or_credentials(monkeypatch):
    """The preview is rendered LOCALLY (REQ-BUP-057).

    The old mechanism asked bd to ask GitHub what it *would* do; this one does not, so
    a preview is readable without credentials and costs no round-trip.
    """
    rows = [{"id": "a", "title": "T", "description": "B", "issue_type": "task",
             "priority": 2}]
    monkeypatch.setattr(up, "load_universe_rows", lambda: rows)
    monkeypatch.setattr(up, "existing_labels", lambda: set())
    def boom(cmd):
        raise AssertionError(f"preview made a subprocess call: {cmd!r}")
    monkeypatch.setattr(up, "run", boom)
    result = up.create_or_update(["a"], apply=False)
    assert result["plans"][0]["action"] == "create"
    assert result["written"] == []


def test_push_leaves_beads_open_no_close_stage(monkeypatch, capsys):
    """`push` is plan_hoist stages 1-2 WITHOUT stage 3 — no tombstone."""
    monkeypatch.setattr(up, "upstream_enabled", lambda: True)
    monkeypatch.setattr(up, "load_universe_rows", lambda: [
        {"id": "a", "title": "T", "description": "B"}])
    monkeypatch.setattr(up, "existing_labels", lambda: set())
    monkeypatch.setattr(up, "owner_claim_warning_lines", lambda: [])
    monkeypatch.setattr(up, "run", lambda cmd: "")
    up.cmd_push("a", apply=False)
    assert "bd close" not in capsys.readouterr().out


def test_push_short_circuits_cleanly_when_tracking_disabled(monkeypatch, capsys):
    monkeypatch.setattr(up, "upstream_enabled", lambda: False)
    def boom(*a, **k):
        raise AssertionError("queried bd while upstream tracking is disabled")
    monkeypatch.setattr(up, "load_universe_rows", boom)
    assert up.cmd_push("a", apply=False) == 0
    assert "disabled" in capsys.readouterr().out


def test_push_surfaces_owner_claimed_warning_inline_on_stdout(monkeypatch, capsys):
    """#105 residual: the shipped warning is stderr-only, so `| jq` loses it."""
    monkeypatch.setattr(up, "upstream_enabled", lambda: True)
    monkeypatch.setattr(up, "load_universe_rows", lambda: [
        {"id": "a", "title": "T", "description": "B"}])
    monkeypatch.setattr(up, "existing_labels", lambda: set())
    monkeypatch.setattr(up, "owner_claim_warning_lines",
                        lambda: ["WARNING: 36 open bead(s) excluded as owner-claimed"])
    monkeypatch.setattr(up, "run", lambda cmd: "")
    up.cmd_push("a", apply=False)
    assert "owner-claimed" in capsys.readouterr().out


def test_push_on_unknown_bead_fails_closed(monkeypatch, capsys):
    monkeypatch.setattr(up, "upstream_enabled", lambda: True)
    monkeypatch.setattr(up, "load_universe_rows", lambda: [])
    monkeypatch.setattr(up, "existing_labels", lambda: set())
    assert up.cmd_push("nope", apply=False) == 1


# --- the destructive stage is guarded (REQ-BUP-050 contract, new evidence) ----

def test_hoist_closes_NO_bead_when_the_write_fails(monkeypatch, capsys):
    """The #129 lesson, re-asserted against the new mechanism.

    A hoist whose upstream write failed must not tombstone a single bead — a
    close_reason asserting an upstream hoist that never happened is silent data loss
    whose every visible step looks correct.
    """
    monkeypatch.setattr(up, "granularity", lambda: "coarse")
    monkeypatch.setattr(up, "load_universe_rows", lambda: [
        {"id": "a", "title": "T", "description": "B"},
        {"id": "b", "title": "T2", "description": "B2"}])
    monkeypatch.setattr(up, "existing_labels", lambda: set())
    def _run(cmd):
        if cmd[:3] == ["gh", "issue", "create"]:
            return "no url in this output"      # -> UNVERIFIED
        if cmd[:2] == ["bd", "close"] or cmd[:1] == ["bash"]:
            raise AssertionError(f"closed a bead after a failed write: {cmd!r}")
        return ""
    monkeypatch.setattr(up, "run", _run)
    rc = up.cmd_hoist("a,b", "plan-013", apply=True)
    assert rc == 1
    assert "No bead was closed" in capsys.readouterr().err


def test_hoist_dry_run_default_does_not_apply(monkeypatch, capsys):
    monkeypatch.setattr(up, "granularity", lambda: "coarse")
    monkeypatch.setattr(up, "load_universe_rows", lambda: [
        {"id": "a", "title": "T", "description": "B"}])
    monkeypatch.setattr(up, "existing_labels", lambda: set())
    def boom(cmd):
        raise AssertionError(f"hoist executed {cmd!r} without --apply")
    monkeypatch.setattr(up, "run", boom)
    assert up.cmd_hoist("a", "plan-013", apply=False) == 0
    out = capsys.readouterr().out
    assert "Preview only" in out
    assert "bd close a" in out          # shown as a plan, not executed


# --- REQ-BUP-059 / SC14: the removed --backend fails INFORMATIVELY ------------

def test_removed_backend_flag_is_explained_not_bare_argparse_error():
    """An existing `--backend gitlab` caller must learn WHY, and where it went."""
    import subprocess as sp
    proc = sp.run(
        [sys.executable, str(Path(__file__).parent / "upstream.py"),
         "push", "--issues", "x", "--backend", "gitlab"],
        capture_output=True, text=True)
    assert proc.returncode != 0
    combined = proc.stdout + proc.stderr
    assert "--backend was removed" in combined
    assert "#51" in combined and "#52" in combined and "#53" in combined
    assert "unrecognized arguments" not in combined


# --- REQ-BUP-052: the `closable` verb (#117, partial) --------------------------

ISSUE_A = "https://github.com/o/r/issues/1"
ISSUE_B = "https://github.com/o/r/issues/2"


def test_closable_when_every_mapped_bead_is_closed():
    report = up.closable_candidates([
        {"id": "a", "status": "closed", "external": ISSUE_A},
        {"id": "b", "status": "closed", "external": ISSUE_A},
    ])
    assert len(report) == 1
    assert report[0]["closable"] is True
    assert report[0]["blocking"] == []
    assert report[0]["beads"] == ["a", "b"]


def test_not_closable_when_any_mapped_bead_is_open_and_names_it():
    report = up.closable_candidates([
        {"id": "a", "status": "closed", "external": ISSUE_A},
        {"id": "b", "status": "open", "external": ISSUE_A},
    ])
    assert report[0]["closable"] is False
    assert report[0]["blocking"] == ["b"]
    assert "b" in report[0]["reason"]


def test_unmapped_beads_are_absent_from_the_report():
    """A bead with no External: maps to no issue — and, per the recorded gap, a
    hand-filed coarse tracker has no bead pointing at it and can never appear."""
    report = up.closable_candidates([
        {"id": "a", "status": "closed", "external": None},
        {"id": "b", "status": "closed", "external": ""},
    ])
    assert report == []


def test_closable_groups_independent_issues_separately():
    report = up.closable_candidates([
        {"id": "a", "status": "closed", "external": ISSUE_A},
        {"id": "b", "status": "open", "external": ISSUE_B},
    ])
    by = {r["external"]: r for r in report}
    assert by[ISSUE_A]["closable"] is True
    assert by[ISSUE_B]["closable"] is False


def test_closable_short_circuits_cleanly_when_disabled(capsys, monkeypatch):
    monkeypatch.setattr(up, "upstream_enabled", lambda: False)
    def boom(*a, **k):
        raise AssertionError("queried bd while upstream tracking is disabled")
    monkeypatch.setattr(up, "load_universe_rows", boom)
    rc = up.cmd_closable(as_json=False)
    assert rc == 0
    assert "disabled" in capsys.readouterr().out


def test_closable_never_closes_anything(capsys, monkeypatch):
    """Propose-only: it emits `gh issue close` commands and executes NOTHING.

    The mapping now arrives ON THE ROW (`external_ref`) rather than via a patched
    `external_for` — that is the REQ-BUP-052 bulk-read change, not a change to what
    this test asserts. `run` is still booby-trapped: propose-only is the contract.
    """
    monkeypatch.setattr(up, "upstream_enabled", lambda: True)
    monkeypatch.setattr(up, "load_universe_rows", lambda: [
        {"id": "a", "status": "closed", "external_ref": ISSUE_A},
        {"id": "b", "status": "closed", "external_ref": ISSUE_A}])
    def boom(cmd):
        raise AssertionError(f"closable executed {cmd!r} — it must never close")
    monkeypatch.setattr(up, "run", boom)
    # plan-044 Issue 3.3: `closable` now READS upstream state before proposing.
    # Booby-trap the new call path too — `run_unchecked` would otherwise escape the
    # trap above AND make this hermetic unit test hit the real network.
    monkeypatch.setattr(up, "run_unchecked", boom)
    monkeypatch.setattr(
        up, "resolve_upstream_states",
        lambda nums, runner=None: up.UpstreamStates(states={1: "OPEN"}),
    )
    rc = up.cmd_closable(as_json=False)
    assert rc == 0
    out = capsys.readouterr().out
    assert "gh issue close 1" in out
    assert "NOT executed" in out


# --- REQ-BUP-052: the bulk read is a SCALE-INDEPENDENT invariant ---------------

def _counting_run(calls):
    """A `run` stand-in that records every bd argv and serves `bd list --all --json`."""
    def _run(cmd):
        calls.append(list(cmd))
        if cmd[:2] == ["bd", "list"]:
            return json.dumps([
                {"id": f"b{i}", "status": "closed",
                 **({"external_ref": ISSUE_A} if i == 0 else {})}
                for i in range(500)
            ])
        raise AssertionError(f"unexpected bd call in closable: {cmd!r}")
    return _run


def test_closable_issues_one_bd_list_and_zero_bd_show(capsys, monkeypatch):
    """EXP-002's defect, pinned as an invariant rather than a wall-clock threshold.

    The shipped implementation called `external_for` — a fresh `bd show` subprocess —
    once per bead, across 991 beads, to read a field `bd list --all --json` already
    returns. It produced zero output in four minutes and had to be killed.

    Asserting a DURATION would rot: it passes on a small DB and silently regresses as
    the DB grows, which is the exact shape of the original defect. So assert the
    invariant instead — exactly one `bd list`, and zero per-bead `bd show` — which is
    independent of universe size.

    NOTE the bound is on `bd list`/`bd show`, NOT on total `bd` invocations:
    `upstream_enabled()` shells `bd config get`, a second subprocess this change does
    not remove. "Exactly one bd invocation" would fail on correct code.
    """
    calls = []
    monkeypatch.setattr(up, "upstream_enabled", lambda: True)
    monkeypatch.setattr(up, "run", _counting_run(calls))
    # plan-044 Issue 3.3: stub the upstream state read. `closable` now consults it
    # before proposing, and without a stub this hermetic test would hit the network
    # (its `run` counter does not cover the new `run_unchecked` path).
    monkeypatch.setattr(
        up, "resolve_upstream_states",
        lambda nums, runner=None: up.UpstreamStates(states={}),
    )
    rc = up.cmd_closable(as_json=False)
    assert rc == 0

    lists = [c for c in calls if c[:2] == ["bd", "list"]]
    shows = [c for c in calls if c[:2] == ["bd", "show"]]
    assert len(lists) == 1, f"expected exactly one `bd list`, got {len(lists)}: {lists}"
    assert shows == [], f"expected ZERO per-bead `bd show`, got {len(shows)}"


def test_closable_bd_show_count_does_not_grow_with_universe_size(monkeypatch):
    """Scale-independence, stated as a comparison rather than a constant.

    A regression that reintroduced the N+1 would still pass a fixed-size fixture if the
    fixture were small. Running two universes an order of magnitude apart and asserting
    the bd-call count is IDENTICAL catches it whatever the constant happens to be.
    """
    def count_for(n):
        calls = []
        def _run(cmd):
            calls.append(list(cmd))
            if cmd[:2] == ["bd", "list"]:
                return json.dumps([
                    {"id": f"b{i}", "status": "closed",
                     **({"external_ref": ISSUE_A} if i == 0 else {})}
                    for i in range(n)
                ])
            raise AssertionError(f"unexpected bd call: {cmd!r}")
        monkeypatch.setattr(up, "upstream_enabled", lambda: True)
        monkeypatch.setattr(up, "run", _run)
        # plan-044 Issue 3.3: stub the upstream state read so the scale invariant
        # stays hermetic (and O(1) in wall clock) rather than hitting the network
        # once per universe size.
        monkeypatch.setattr(
            up, "resolve_upstream_states",
            lambda nums, runner=None: up.UpstreamStates(states={}),
        )
        up.cmd_closable(as_json=True)
        return len(calls)

    assert count_for(10) == count_for(1000)


def test_external_from_row_is_omitempty_safe():
    """`external_ref` is serialized omitempty — the KEY IS ABSENT, not null.

    Measured on bd 1.1.2: missing from 998 of 1019 rows, including the first. A
    key-presence test or `row["external_ref"]` would see zero mappings on a real DB
    while passing any fixture that always sets the key.
    """
    assert up.external_from_row({"id": "a"}) is None          # key absent entirely
    assert up.external_from_row({"id": "a", "external_ref": None}) is None
    assert up.external_from_row({"id": "a", "external_ref": ""}) is None
    assert up.external_from_row({"id": "a", "external_ref": "   "}) is None
    assert up.external_from_row({"id": "a", "external_ref": ISSUE_A}) == ISSUE_A
    assert up.external_from_row({"id": "a", "external_ref": f"  {ISSUE_A} "}) == ISSUE_A


def test_external_for_helper_is_retained_for_its_other_callers():
    """`external_for` must NOT be deleted along with closable's use of it.

    It has two other live call sites (`mappings`, and the enumerate mapping flag) and is
    monkeypatched by three existing tests. Removing it while fixing the N+1 would break
    callers the fix never touched — pass-2 D7.
    """
    assert callable(getattr(up, "external_for", None))


def test_issue_number_parsed_for_the_close_proposal():
    assert up.issue_number_from_url("https://github.com/o/r/issues/117") == "117"
    assert up.issue_number_from_url("https://github.com/o/r/issues/117/") == "117"
    assert up.issue_number_from_url("not-a-url") is None


def test_closable_caveat_survives_in_skill_md():
    """Cheap insurance on this plan's most misreadable output (Issue 4.4).

    If a future edit softens or drops the limitation, a clean `closable` run starts
    reading as 'nothing needs closing' — which is exactly wrong, and silently so.
    """
    raw = (Path(__file__).parent.parent / "SKILL.md").read_text()
    # Normalize wrapping and markdown emphasis: the contract is that the caveat
    # SURVIVES, not that it keeps any particular line breaks or bolding.
    skill = " ".join(raw.replace("*", "").replace(">", " ").split())
    assert "Known limitation" in skill
    assert "does NOT mean" in skill and "nothing needs closing" in skill
    assert "coarse" in skill.lower()
    # the four stale trackers that motivated #117 are named as NOT caught
    for n in ("#103", "#95", "#96", "#98"):
        assert n in skill, f"the motivating tracker {n} must stay named in the caveat"


def test_closable_json_carries_the_caveat():
    """An agent reading --json must get the caveat too, not just a human reader."""
    assert "coarse" in up.CLOSABLE_CAVEAT.lower()
    assert "does NOT mean" in up.CLOSABLE_CAVEAT


# --- REQ-BUP-053: the procedure/explanation boundary is real -------------------


def test_skill_md_procedure_blocks_route_through_the_verb():
    """Issue 5.1's contract, asserted here too: no fenced bash PROCEDURE block in
    SKILL.md instructs a raw `bd <backend>` push/sync."""
    import re
    skill = (Path(__file__).parent.parent / "SKILL.md").read_text()
    offenders = []
    for m in re.finditer(r"```bash\n(.*?)```", skill, re.S):
        if re.search(r"\bbd (github|gitlab|jira) (push|sync)\b", m.group(1)):
            offenders.append(m.group(1).strip()[:80])
    assert not offenders, f"raw push/sync in fenced procedure block(s): {offenders}"


def test_skill_md_keeps_the_explanatory_mentions():
    """The counter-assertion: a global 'zero occurrences' check would be WRONG.
    The invariant statements quote the command in order to forbid it, and the
    dated verification blockquotes are provenance — both must survive."""
    skill = (Path(__file__).parent.parent / "SKILL.md").read_text()
    assert "Verified (bd 1.0.5" in skill, "dated verification blockquotes must survive"
    assert skill.count("Verified (bd 1.0.5") == 2
    assert "bd <backend> sync" in skill, "the never-bare-sync invariant must still name the command"
    assert "Would update in GitHub" in skill, "the mapping-lost tripwire must survive"
    assert "Would create" in skill


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


# --- REQ-BUP-048: owner-on-create enumerate knob (#61) ------------------------

def test_owner_on_create_true():
    g = fake_config({"custom.upstream.owner_on_create": "true\n"})
    assert up.owner_on_create(g) is True


def test_owner_on_create_false_and_unset_and_other_deny():
    assert up.owner_on_create(fake_config({"custom.upstream.owner_on_create": "false\n"})) is False
    assert up.owner_on_create(fake_config({})) is False  # unset → (not set) sentinel
    assert up.owner_on_create(fake_config({"custom.upstream.owner_on_create": "yes\n"})) is False


def test_enumerate_owner_on_create_reincludes_claimed_open():
    """#61/REQ-BUP-048: with the knob ON, an owner-only 'claim' is a candidate again,
    while in_progress and ancestor-of-active exclusions are preserved."""
    beads, edges = make_enumerate_universe()
    candidates = {r["id"] for r in up.enumerate_candidates(beads, edges, ignore_owner_claim=True)}
    # The owner-only bead re-enters candidacy (the #61 bug fix)...
    assert "t_claimed" in candidates
    assert candidates == {"t_open", "t_blocked", "t_deferred", "t_claimed"}
    # ...but genuine active work stays excluded (owner is not the only signal):
    assert "t_ip" not in candidates        # in_progress is status-based, unaffected by owner blanking
    assert "epic_anc" not in candidates    # still an open ancestor of the in_progress bead
    assert "t_closed" not in candidates


def test_enumerate_owner_on_create_off_is_byte_for_byte_prior():
    """Knob OFF (default) must reproduce the parity set exactly — no behavior change."""
    beads, edges = make_enumerate_universe()
    off = {r["id"] for r in up.enumerate_candidates(beads, edges, ignore_owner_claim=False)}
    assert off == {"t_open", "t_blocked", "t_deferred"}  # identical to test_enumerate_parity_nonactive_set


def test_enumerate_owner_on_create_does_not_mutate_input():
    """The knob blanks owner on a COPY — the caller's bead universe is untouched
    (guards the shared-classifier byte-identity invariant at the call boundary)."""
    beads, edges = make_enumerate_universe()
    up.enumerate_candidates(beads, edges, ignore_owner_claim=True)
    assert beads["t_claimed"]["owner"] == "alice"  # original dict unchanged


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
    monkeypatch.setattr(up, "load_universe_rows", lambda: [
        {"id": "t1", "title": "T1", "description": "B1"},
        {"id": "t2", "title": "T2", "description": "B2"}])
    monkeypatch.setattr(up, "existing_labels", lambda: set())
    rc = up.cmd_land("m", "2026-06-24T00:00:00Z", "plan-013", apply=False)
    assert rc == 0
    out = capsys.readouterr().out
    assert "single confirm required" in out
    assert "Preview only" in out
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
    monkeypatch.setattr(up, "load_universe_rows", lambda: [
        {"id": "t1", "title": "T1", "description": "B1"},
        {"id": "t2", "title": "T2", "description": "B2"}])
    monkeypatch.setattr(up, "existing_labels", lambda: set())
    rc = up.cmd_land("m", "2026-06-24T00:00:00Z", "plan-013", apply=False)
    assert rc == 0
    out = capsys.readouterr().out
    assert "NO-PROMPT auto-hoist (narrow only): ['t1']" in out
    assert "Still gated (broad" in out and "t2" in out


# --- REQ-BUP-049: never silently exclude owner-claimed beads (#105) -----------

def test_owner_claim_exclusions_reports_the_dropped_set():
    """#105/REQ-BUP-049: with the knob OFF, the owner-only bead is excluded and must be
    reported. This is the set enumerate has to warn about."""
    beads, edges = make_enumerate_universe()
    excluded = up.owner_claim_exclusions(beads, edges, ignore_owner_claim=False)
    assert excluded == ["t_claimed"]


def test_owner_claim_exclusions_empty_when_knob_on():
    """Knob ON → nothing is excluded on owner grounds, so there is nothing to warn about."""
    beads, edges = make_enumerate_universe()
    assert up.owner_claim_exclusions(beads, edges, ignore_owner_claim=True) == []


def test_owner_claim_exclusions_excludes_only_owner_grounds():
    """Genuinely-active work (in_progress, ancestor-of-active) and closed beads are NOT
    reported as owner-claim exclusions — they would be excluded either way, so warning
    about them would be noise."""
    beads, edges = make_enumerate_universe()
    excluded = set(up.owner_claim_exclusions(beads, edges, ignore_owner_claim=False))
    assert "t_ip" not in excluded        # excluded by status, not by owner
    assert "epic_anc" not in excluded    # excluded as ancestor-of-active
    assert "t_closed" not in excluded    # closed beads are in neither bucket


def test_owner_claim_exclusions_does_not_mutate_input():
    """Guards the shared-classifier byte-identity invariant at the call boundary
    (same contract as REQ-BUP-048's copy semantics)."""
    beads, edges = make_enumerate_universe()
    before = {bid: dict(b) for bid, b in beads.items()}
    up.owner_claim_exclusions(beads, edges, ignore_owner_claim=False)
    assert beads == before


def test_enumerate_warns_on_nonzero_candidates_with_exclusions(monkeypatch, capsys):
    """The #105 regression proper: a PLAUSIBLE NON-ZERO candidate list that still hides
    owner-claimed beads must warn. A guard keyed on `len(candidates) == 0` would not fire
    here — that is exactly why the real repo's `1 candidate(s)` went unnoticed."""
    beads, edges = make_enumerate_universe()
    monkeypatch.setattr(up, "load_universe_rows", lambda: list(beads.values()))
    monkeypatch.setattr(up, "collect_parent_edges", lambda _b: edges)
    monkeypatch.setattr(up, "owner_on_create", lambda: False)
    monkeypatch.setattr(up, "external_for", lambda _bid: None)

    rc = up.cmd_enumerate(as_json=False)
    cap = capsys.readouterr()
    assert rc == 0
    # Non-zero candidate list — the case a zero-keyed guard misses.
    assert "3 candidate(s)" in cap.out
    assert "WARNING: 1 open bead(s) excluded as owner-claimed" in cap.err
    assert "custom.upstream.owner_on_create true" in cap.err
    assert "t_claimed" in cap.err


def test_enumerate_json_stdout_stays_a_pure_array(monkeypatch, capsys):
    """REQ-BUP-049: the warning goes to stderr so `--json` stdout survives a `| jq`."""
    beads, edges = make_enumerate_universe()
    monkeypatch.setattr(up, "load_universe_rows", lambda: list(beads.values()))
    monkeypatch.setattr(up, "collect_parent_edges", lambda _b: edges)
    monkeypatch.setattr(up, "owner_on_create", lambda: False)
    monkeypatch.setattr(up, "external_for", lambda _bid: None)

    up.cmd_enumerate(as_json=True)
    cap = capsys.readouterr()
    parsed = json.loads(cap.out)          # must parse — no warning text mixed in
    assert isinstance(parsed, list)
    assert {r["id"] for r in parsed} == {"t_open", "t_blocked", "t_deferred"}
    assert "WARNING:" in cap.err          # ...and the signal is still emitted


def test_enumerate_silent_when_nothing_owner_excluded(monkeypatch, capsys):
    """No spurious warning when the knob is ON — silence is correct here."""
    beads, edges = make_enumerate_universe()
    monkeypatch.setattr(up, "load_universe_rows", lambda: list(beads.values()))
    monkeypatch.setattr(up, "collect_parent_edges", lambda _b: edges)
    monkeypatch.setattr(up, "owner_on_create", lambda: True)
    monkeypatch.setattr(up, "external_for", lambda _bid: None)

    up.cmd_enumerate(as_json=False)
    assert "WARNING:" not in capsys.readouterr().err


# =============================================================================
# plan-044 Epic 0 SPEC-first bridge cases (REQ-BUP-060..064).
#
# These tag the five requirements added by plan-044 Issue 0.3. Their behavior is
# implemented in Epic 3, so each is marked `xfail(strict=True)` as a TEMPORARY
# BRIDGE, mirroring the D-7 allowlist discipline on the Rust side:
#
#   strict=True means an UNEXPECTED PASS is a FAILURE. So the moment the
#   implementing issue lands the behavior, the marker itself turns the suite red
#   and must be removed in that same commit. The bridge cannot outlive its tag.
#
# Removing the marker (not the test) is the implementing issue's job:
#   REQ-BUP-062 -> Issue 3.1   REQ-BUP-060 -> Issue 3.2   REQ-BUP-064 -> 3.3/3.5
#   REQ-BUP-063 -> Issue 3.4   REQ-BUP-061 -> Issue 3.5
# =============================================================================

# --- REQ-BUP-062: the two external_ref readers AGREE ---------------------------

@pytest.mark.parametrize(
    "raw",
    [
        "https://github.com/o/r/issues/91",
        "gh-91",
        "#91",
        "91",
    ],
)
def test_external_ref_normalizes_to_issue_number(raw):
    """Every accepted spelling of a ref resolves to the same issue number.

    The live drift this pins: a bead written `gh-91` is mapped by the any-string
    reader and INVISIBLE to the URL-only one, so it is silently omitted from the
    exact sweep meant to catch it.
    """
    assert up.normalize_external_ref(raw) == 91


def test_external_readers_agree_on_the_same_bead():
    """external_for() and external_from_row() shall not disagree (REQ-BUP-062)."""
    row = {"id": "yf-4d7s", "external_ref": "gh-91"}
    assert up.normalize_external_ref(up.external_from_row(row)) == 91


# --- REQ-BUP-060: upstream state resolved by ONE bulk query --------------------

def test_upstream_state_resolved_in_one_bulk_query():
    """One `gh issue list --state all` call, regardless of how many refs are asked for."""
    calls = []

    def fake_gh(cmd):
        calls.append(cmd)
        return json.dumps([
            {"number": 91, "state": "CLOSED"},
            {"number": 132, "state": "CLOSED"},
            {"number": 161, "state": "OPEN"},
        ])

    states = up.resolve_upstream_states([91, 132, 161, 9999], runner=fake_gh)
    assert len(calls) == 1
    assert states[91] == "CLOSED"
    assert states[161] == "OPEN"
    # A mapped ref absent from the bulk result is UNRESOLVABLE at zero extra cost.
    assert states[9999] == "UNRESOLVABLE"


# --- REQ-BUP-063: an unparseable ref is REPORTED, never silently dropped -------

def test_unparseable_external_ref_is_reported_not_dropped(capsys, monkeypatch):
    """REQ-BUP-063: an uninterpretable ref is a FINDING for a human, not an absence.

    The Epic-0 placeholder for this case guessed a `partition_refs` helper. The
    requirement landed as reporting inside `closable` instead, so this asserts the
    REQUIREMENT against the shipped shape rather than pinning an API that was never
    built — a permanently-xfailing test would have misreported REQ-BUP-063 as unmet.
    """
    monkeypatch.setattr(up, "upstream_enabled", lambda: True)
    monkeypatch.setattr(up, "load_universe_rows", lambda: [
        {"id": "yf-aaaa", "status": "closed", "external_ref": ISSUE_A},
        {"id": "yf-bbbb", "status": "closed", "external_ref": "not-a-ref-at-all"},
    ])
    monkeypatch.setattr(
        up, "resolve_upstream_states",
        lambda nums, runner=None: up.UpstreamStates(states={1: "OPEN"}),
    )
    up.cmd_closable(as_json=False)
    out = capsys.readouterr().out
    assert "UNPARSEABLE" in out, "the bad ref must be reported"
    assert "yf-bbbb" in out, "the owning bead must be named"
    assert "not-a-ref-at-all" in out, "the offending value must be shown"


# --- REQ-BUP-064: gh failure is INCONCLUSIVE, never a falsely-clean proposal ---

def test_gh_failure_yields_inconclusive_not_clean():
    """An empty proposal is indistinguishable from 'nothing to do' and reads as success.

    So when the network read fails, the verdict shall be INCONCLUSIVE.
    """
    def failing_gh(cmd):
        raise up.UpstreamQueryError("gh unavailable")

    verdict = up.resolve_upstream_states([91], runner=failing_gh)
    assert verdict.inconclusive is True


def test_never_auto_closes_a_bead_on_an_unresolvable_ref():
    plan = up.plan_reconcile(
        [{"id": "yf-zzzz", "status": "open", "external_ref": "#9999"}],
        states={9999: "UNRESOLVABLE"},
    )
    assert plan.commands == [], "UNRESOLVABLE must never produce a close command"
    assert any("yf-zzzz" in r for r in plan.reported)


# --- REQ-BUP-061: the `reconcile` verb and its ASYMMETRIC authority ------------

def test_reconcile_proposes_local_close_for_closed_upstream():
    plan = up.plan_reconcile(
        [{"id": "yf-1656", "status": "open", "external_ref": "#132"}],
        states={132: "CLOSED"},
    )
    assert any("bd close" in c and "yf-1656" in c for c in plan.commands)


def test_reconcile_upstream_half_is_propose_only():
    """The local half is --apply-able; the upstream half is NOT (REQ-BUP-052)."""
    assert up.reconcile_supports_apply(half="local") is True
    assert up.reconcile_supports_apply(half="upstream") is False


# --- plan-052 Issue 3.3 / 3.2 (REQ-BUP-070, 070a, 070b) ------------------------------------
#
# Fixture-driven throughout: no live `bd`, no network. The point of `--fixture` is that these
# assertions are about the CODE, not about the machine they run on.

import importlib.util as _ilu
import pathlib as _pl

_RENDER_PATH = _pl.Path(__file__).resolve().parent / "upstream_render.py"


def _render_mod():
    spec = _ilu.spec_from_file_location("upstream_render_under_test", _RENDER_PATH)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tombstone_bead(bid, ext, dest=None):
    return {"id": bid, "status": "closed", "external": ext,
            "close_reason": up.close_reason(dest or ext), "title": bid,
            "metadata": {}}


def _done_bead(bid, ext, reason="finished"):
    return {"id": bid, "status": "closed", "external": ext,
            "close_reason": reason, "title": bid, "metadata": {}}


def test_hoist_tombstone_is_recognised_from_its_generated_reason():
    """The predicate keys on the reason `close_reason()` actually writes, not a guess."""
    assert up.is_hoist_tombstone(_tombstone_bead("b1", "#900"))
    assert not up.is_hoist_tombstone(_done_bead("b2", "#900"))
    assert not up.is_hoist_tombstone({"id": "b3", "status": "closed"})


def test_tombstone_only_issue_is_not_closable_but_is_still_reported():
    """REQ-BUP-070: suppressed AND annotated. A dropped row would be a silent absence."""
    rows = up.closable_candidates([
        _tombstone_bead("t1", "#901"), _tombstone_bead("t2", "#901"),
    ])
    assert len(rows) == 1, "the row must be PRESENT, never dropped"
    row = rows[0]
    assert row["closable"] is False
    assert row["tombstone_only"] is True
    assert sorted(row["hoist_tombstones"]) == ["t1", "t2"]
    assert "TOMBSTONE" in row["reason"].upper(), "the row must say WHY it was suppressed"


def test_suppression_is_scoped_to_only_and_does_not_over_reach():
    """A MIX still carries real completion evidence; only an all-tombstone set is suppressed."""
    mixed = up.closable_candidates([
        _tombstone_bead("t1", "#903"), _done_bead("d1", "#903"),
    ])
    assert mixed[0]["closable"] is True, "a mix must remain closable"
    clean = up.closable_candidates([_done_bead("d1", "#900"), _done_bead("d2", "#900")])
    assert clean[0]["closable"] is True
    still_open = up.closable_candidates([
        _done_bead("d1", "#902"), {"id": "o1", "status": "open", "external": "#902"},
    ])
    assert still_open[0]["closable"] is False
    assert still_open[0]["blocking"] == ["o1"]


def test_missing_fixture_is_exit_1_and_malformed_is_exit_2(tmp_path):
    """REQ-BUP-070a's load-bearing distinction: a real negative vs an instrument failure."""
    import pytest
    with pytest.raises(SystemExit) as e:
        up.load_fixture_rows(str(tmp_path / "nope.json"))
    assert e.value.code == 1, "an ABSENT fixture is a real negative"

    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        up.load_fixture_rows(str(bad))
    assert e.value.code == 2, "a MALFORMED fixture is an instrument failure"

    notlist = tmp_path / "obj.json"
    notlist.write_text('{"a": 1}', encoding="utf-8")
    with pytest.raises(SystemExit) as e:
        up.load_fixture_rows(str(notlist))
    assert e.value.code == 2


def test_enrich_reports_evidence_and_flags_a_thin_row():
    """REQ-BUP-070b: a present-but-EMPTY key must not read as evidence supplied."""
    m = _render_mod()
    beads = {
        "b1": {"id": "b1", "close_reason": "done", "title": "t",
               "metadata": {"plan": "no-such-plan-999", "plan_issue": "1.1"}},
    }
    rows = [{"external": "#900", "beads": ["b1"], "closable": True}]
    m.enrich(rows, beads, _pl.Path(__file__).resolve().parents[3])
    assert rows[0]["close_reasons"], "reasons must be rendered"
    assert rows[0]["discharges"] == [], "an unresolvable plan yields no criteria"
    assert rows[0]["evidence_complete"] is False, (
        "evidence_complete must be FALSE when discharges is empty — otherwise an empty "
        "array renders as 'evidence supplied' while supplying none"
    )


def test_render_text_marks_tombstones_and_thin_evidence():
    m = _render_mod()
    rows = [{"issue": 901, "closable": False, "reason": "suppressed",
             "beads": ["t1"], "hoist_tombstones": ["t1"],
             "close_reasons": [{"bead": "t1", "title": "t", "close_reason": "hoisted",
                                "is_hoist_tombstone": True}],
             "discharges": []}]
    out = m.render_text(rows)
    assert "[HOIST TOMBSTONE]" in out
    assert "THIN" in out.upper(), "a row with no resolvable criteria must say so"
