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


# --- #129 / REQ-BUP-050: push-command construction is a CONTRACT ---------------
#
# These assert the CONTRACT, never the emitted string. The defect that made #129
# survive a green 48-test suite was exactly the opposite style: fixtures comparing
# an emitted command against an expected string that contained the same comma.
# An expected-string test cannot fail when the bug is in the expectation too, so
# every assertion below is phrased over a PROPERTY of the emitted command.


def _push_ids_segment(cmd: str, backend: str = "github") -> str:
    """The argument text between `bd <backend> push` and the next flag (or end).

    Isolating the id segment is what lets the tests below assert over the ids
    themselves rather than over the whole command string.
    """
    marker = f"bd {backend} push "
    assert marker in cmd, f"not a push command: {cmd!r}"
    tail = cmd.split(marker, 1)[1]
    # stop at the first flag, a shell pipe, or the end of the command
    for stop in (" --", " |", " ||", " &&"):
        idx = tail.find(stop)
        if idx != -1:
            tail = tail[:idx]
    return tail.strip()


def _push_commands(cmds, backend="github"):
    return [c for c in cmds if f"bd {backend} push " in c]


def test_push_ids_are_space_separated_never_comma_joined():
    """REQ-BUP-050: ids are POSITIONAL args. A comma-joined list matches ZERO
    beads while bd exits 0 — the #129 silent-data-loss signature."""
    cmds = up.plan_hoist(["yf-aaa", "yf-bbb", "yf-ccc"], "plan-038",
                         backend="github", gran="coarse")
    pushes = _push_commands(cmds)
    assert pushes, "expected the dry-run + real push"
    for cmd in pushes:
        seg = _push_ids_segment(cmd)
        # THE assertion #129 needed and the old fixture style could not produce:
        assert "," not in seg, (
            f"comma found between push ids ({seg!r}) — bd would match ZERO beads "
            "and still exit 0 (#129)"
        )
        assert seg.split() == ["yf-aaa", "yf-bbb", "yf-ccc"]


def test_push_ids_space_separated_for_plan_push_too():
    """The same contract holds for the plain `push` verb (REQ-BUP-051), which
    must inherit the fix rather than re-derive it."""
    cmds = up.plan_push(["yf-aaa", "yf-bbb"], backend="github")
    for cmd in _push_commands(cmds):
        seg = _push_ids_segment(cmd)
        assert "," not in seg
        assert seg.split() == ["yf-aaa", "yf-bbb"]


def test_single_bead_push_has_no_separator_at_all():
    """Single-bead hoist was never broken (a one-element join has no comma),
    which is why #129 survived. Pin that it stays correct."""
    cmds = up.plan_hoist(["yf-solo"], "plan-038", backend="github", gran="coarse")
    for cmd in _push_commands(cmds):
        assert _push_ids_segment(cmd) == "yf-solo"


def test_parse_pushed_count_reads_bd_success_line():
    """REQ-BUP-050 verification parse (bd 1.1.2 shape)."""
    assert up.parse_pushed_count("✓ Pushed 2 issues") == 2
    assert up.parse_pushed_count("✓ Pushed 1 issue") == 1
    assert up.parse_pushed_count("noise\n✓ Pushed 11 issues\nmore") == 11


def test_parse_pushed_count_unrecognized_output_is_unverified_not_zero():
    """An unparseable output must read as UNVERIFIED (None), never as 'pushed
    nothing' — the distinction is what makes an unknown bd version fail CLOSED."""
    assert up.parse_pushed_count("") is None
    assert up.parse_pushed_count("some future bd wording") is None
    # the exact #129 signature: bd printed no success line and exited 0
    assert up.parse_pushed_count("Syncing...\n") is None


def test_hoist_close_stage_is_guarded_by_push_verification():
    """REQ-BUP-050 fail-closed: the destructive `bd close` stage must not be
    reachable unless the push verified. Contract: every close command is ordered
    AFTER a push command that carries a halting verification for the expected count."""
    cmds = up.plan_hoist(["a", "b"], "plan-038", backend="github", gran="coarse")
    closes = [i for i, c in enumerate(cmds) if c.startswith("bd close")]
    assert closes, "expected the local-close stage"
    verified = [
        i for i, c in enumerate(cmds)
        if "bd github push " in c and "grep -qE" in c and "exit 1" in c
    ]
    assert len(verified) == 2, "both the dry-run and the real push must be verified"
    assert max(verified) < min(closes), "close stage must follow the verified push"
    # the verification must key on the number of beads actually being pushed
    assert all("2 issues?" in cmds[i] for i in verified)


def test_push_verification_halts_on_under_count():
    """Behavioral proof of the guard: run the emitted real-push command against a
    faked bd that reports FEWER issues than requested, and assert it exits
    non-zero — so `run()` raises and the close stage never executes."""
    import subprocess
    cmds = up.plan_push(["a", "b", "c"], backend="github")
    real = [c for c in _push_commands(cmds) if "--dry-run" not in c][0]
    # Replace the auth + bd invocation with a stub reporting only 2 of 3 pushed.
    stub = real.split("|", 1)[1]
    faked = "echo '✓ Pushed 2 issues' |" + stub
    proc = subprocess.run(["bash", "-c", faked], capture_output=True, text=True)
    assert proc.returncode != 0, "an under-count push must fail closed"
    assert "FAIL-CLOSED" in proc.stderr


def test_push_verification_passes_on_exact_count():
    """The guard must not be a blanket refusal — an exact-count push proceeds."""
    import subprocess
    cmds = up.plan_push(["a", "b", "c"], backend="github")
    real = [c for c in _push_commands(cmds) if "--dry-run" not in c][0]
    stub = real.split("|", 1)[1]
    faked = "echo '✓ Pushed 3 issues' |" + stub
    proc = subprocess.run(["bash", "-c", faked], capture_output=True, text=True)
    assert proc.returncode == 0
    assert "FAIL-CLOSED" not in proc.stderr


def test_push_verification_halts_when_bd_prints_nothing_but_exits_zero():
    """The literal #129 shape: bd matched zero beads, printed no success line,
    and exited 0. The sequence must still halt."""
    import subprocess
    cmds = up.plan_push(["a", "b"], backend="github")
    real = [c for c in _push_commands(cmds) if "--dry-run" not in c][0]
    stub = real.split("|", 1)[1]
    faked = "true |" + stub
    proc = subprocess.run(["bash", "-c", faked], capture_output=True, text=True)
    assert proc.returncode != 0
    assert "FAIL-CLOSED" in proc.stderr


def test_plan_unhoist_carries_no_separator_or_destructive_stage():
    """Issue 2.3 audit, pinned: the sibling builder emits ONE command per bead
    (no multi-id argument, so no separator hazard) and nothing destructive."""
    cmds = up.plan_unhoist(["a", "b", "c"])
    assert len(cmds) == 3, "one command per bead — no joined id list"
    for c in cmds:
        assert "," not in c
        assert "bd close" not in c and "bd delete" not in c


# --- REQ-BUP-051: the `push` verb ---------------------------------------------


def test_push_always_dry_runs_before_the_real_push():
    cmds = up.plan_push(["a", "b"], backend="github")
    dry = next(i for i, c in enumerate(cmds) if "--dry-run" in c)
    real = next(i for i, c in enumerate(cmds) if "bd github push " in c and "--dry-run" not in c)
    assert dry < real


def test_push_is_scoped_and_never_a_bare_sync():
    cmds = up.plan_push(["a", "b"], backend="github")
    assert all("sync" not in c for c in cmds)
    for c in cmds:
        assert "bd github push " in c


def test_push_leaves_beads_open_no_close_stage():
    """The contract that distinguishes `push` from `hoist`: no local removal."""
    cmds = up.plan_push(["a", "b"], backend="github")
    assert all("bd close" not in c for c in cmds)
    assert all("bd delete" not in c for c in cmds)
    # ...whereas hoist DOES close, so the two verbs are genuinely different.
    hoisted = up.plan_hoist(["a", "b"], "plan-038", backend="github", gran="coarse")
    assert any(c.startswith("bd close") for c in hoisted)


def test_push_inline_auth_per_backend():
    gh = up.plan_push(["a"], backend="github")
    assert all("GITHUB_TOKEN=$(gh auth token)" in c for c in gh)
    gl = up.plan_push(["a"], backend="gitlab")
    assert all("GITLAB_TOKEN=$(glab auth token)" in c for c in gl)
    # never persisted to config
    assert all("bd config set" not in c for c in gh + gl)


def test_push_without_apply_executes_nothing(capsys, monkeypatch):
    """Absent --apply IS the dry run — matching the hoist/land/unhoist idiom.
    Any execution attempt fails the test outright."""
    monkeypatch.setattr(up, "upstream_enabled", lambda: True)
    monkeypatch.setattr(up, "owner_claim_warning_lines", lambda: [])
    def boom(cmd):
        raise AssertionError(f"push executed {cmd!r} without --apply")
    monkeypatch.setattr(up, "run", boom)
    rc = up.cmd_push("a,b", "github", apply=False)
    assert rc == 0
    out = capsys.readouterr().out
    assert "--dry-run" in out
    assert "Dry run" in out


def test_push_has_no_dry_run_flag_of_its_own():
    """The idiom is --apply-only; a --dry-run flag would be a second, conflicting
    way to say the same thing."""
    import argparse
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf), contextlib.redirect_stdout(buf):
        with pytest.raises(SystemExit):
            up_main_with(["push", "--issues", "a", "--dry-run"])
    assert "--dry-run" in buf.getvalue() or "unrecognized" in buf.getvalue()


def up_main_with(argv):
    import sys as _s
    old = _s.argv
    _s.argv = ["upstream.py"] + argv
    try:
        return up.main()
    finally:
        _s.argv = old


def test_push_short_circuits_cleanly_when_tracking_disabled(capsys, monkeypatch):
    """REQ-BUP-010 default-deny: clean exit 0, no upstream call."""
    monkeypatch.setattr(up, "upstream_enabled", lambda: False)
    def boom(cmd):
        raise AssertionError("made an upstream call while disabled")
    monkeypatch.setattr(up, "run", boom)
    rc = up.cmd_push("a,b", "github", apply=True)
    assert rc == 0
    assert "disabled" in capsys.readouterr().out


def test_push_surfaces_owner_claimed_warning_inline_on_stdout(capsys, monkeypatch):
    """#105 residual (REQ-BUP-051): the enumerate warning is stderr-only, so an
    agent piping --json to jq misses it. On the routed path it must be INLINE
    on stdout."""
    monkeypatch.setattr(up, "upstream_enabled", lambda: True)
    monkeypatch.setattr(
        up, "owner_claim_warning_lines",
        lambda: ["WARNING: 36 open bead(s) are excluded as owner-claimed", "         excluded: a, b"],
    )
    monkeypatch.setattr(up, "run", lambda cmd: "")
    up.cmd_push("a", "github", apply=False)
    captured = capsys.readouterr()
    assert "excluded as owner-claimed" in captured.out, "warning must reach STDOUT, not just stderr"


def test_upstream_enabled_default_deny():
    """Both keys must agree, and the read is on config TEXT not exit code."""
    assert up.upstream_enabled(fake_config({
        "custom.upstream.enabled": "true\n", "custom.upstream.backend": "github\n"})) is True
    # unset
    assert up.upstream_enabled(fake_config({})) is False
    # enabled but backend none
    assert up.upstream_enabled(fake_config({
        "custom.upstream.enabled": "true\n", "custom.upstream.backend": "none\n"})) is False
    # backend set but not enabled
    assert up.upstream_enabled(fake_config({
        "custom.upstream.enabled": "false\n", "custom.upstream.backend": "github\n"})) is False
    # any other value denies
    assert up.upstream_enabled(fake_config({
        "custom.upstream.enabled": "yes\n", "custom.upstream.backend": "github\n"})) is False


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
    """Propose-only: it emits `gh issue close` commands and executes NOTHING."""
    monkeypatch.setattr(up, "upstream_enabled", lambda: True)
    monkeypatch.setattr(up, "load_universe_rows", lambda: [
        {"id": "a", "status": "closed"}, {"id": "b", "status": "closed"}])
    monkeypatch.setattr(up, "external_for", lambda bid: ISSUE_A)
    def boom(cmd):
        raise AssertionError(f"closable executed {cmd!r} — it must never close")
    monkeypatch.setattr(up, "run", boom)
    rc = up.cmd_closable(as_json=False)
    assert rc == 0
    out = capsys.readouterr().out
    assert "gh issue close 1" in out
    assert "NOT executed" in out


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
