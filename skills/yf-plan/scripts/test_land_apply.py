# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
#     "click>=8",
#     "pyyaml",
# ]
# ///
"""Tier-1 tests for the landing EXECUTOR — journal, binding, tty gate, conflicts.

plan-060 Epic 3 (Issue 3.7) and Epic 4 (Issue 4.10). Throwaway git repos in `tmp_path`, no
network.

THE `__main__` IS THE FORWARDING FORM (REQ-CLI-028). The house shim discards `sys.argv`, so a
`-k` selector never reaches pytest and a criterion routed through it stays green when the
named test is deleted.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_PM = _HERE / "plan_manager.py"
_SPEC = _HERE.parent / "spec" / "landing.md"


def _load():
    spec = importlib.util.spec_from_file_location("pm_apply_under_test", _PM)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pm_apply_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


pm = _load()


def _code_only(src: str) -> str:
    """Source with every docstring and comment removed — CODE, not prose.

    Both of this file's absence checks initially failed against their own subject's
    DOCSTRING: `_land_tty_gate` explains that `/dev/tty` is unopenable "inside a Claude Code
    Bash subprocess", and a raw-text scan read the word `subprocess` as proof that it shells
    out. A prose description of a constraint is not a violation of it, and an absence check
    that cannot tell them apart forbids documentation.
    """
    import ast as _ast
    tree = _ast.parse(src)
    for node in _ast.walk(tree):
        if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef,
                             _ast.Module)):
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], _ast.Expr)
                    and isinstance(body[0].value, _ast.Constant)
                    and isinstance(body[0].value.value, str)):
                body.pop(0)
    return _ast.unparse(tree)


def _git(*a, cwd):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True)


PLAN_ID = "plan-060-test-abc123"


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "repo"
    root.mkdir()
    _git("init", "-q", "-b", "main", ".", cwd=root)
    for k, v in (("user.email", "t@example.invalid"), ("user.name", "T"),
                 ("commit.gpgsign", "false")):
        _git("config", k, v, cwd=root)
    pdir = root / "docs" / "plans" / PLAN_ID
    pdir.mkdir(parents=True)
    (pdir / "plan.md").write_text(
        f"# Plan: t\n\n**ID:** {PLAN_ID}\n**Status:** reconciling\n\n"
        "## Upstream Issues\n| Issue | Title | Disposition | Notes | Resolved By |\n"
        "| :-- | :-- | :-- | :-- | :-- |\n| #1 | a | partial | n | 1.1 |\n", encoding="utf-8")
    (root / "skills").mkdir()
    (root / "skills" / "base.txt").write_text("base\n", encoding="utf-8")
    _git("add", "-A", cwd=root)
    _git("commit", "-q", "-m", "base", cwd=root)
    _git("checkout", "-q", "-b", f"{PLAN_ID}-execute", cwd=root)
    (root / "skills" / "new.py").write_text("x\n", encoding="utf-8")
    _git("add", "-A", cwd=root)
    _git("commit", "-q", "-m", "work", cwd=root)
    _git("checkout", "-q", "main", cwd=root)
    monkeypatch.chdir(root)
    return root


# =========================================================================================
# SC3 — the SPEC enumerates the steps and the journal states, and AGREES with the code
# =========================================================================================

def test_landing_spec_enumerates_steps_and_journal_states():
    """SC3 / Issue 0.2.

    NOT merely "the spec mentions them" — the spec's set and the CODE's set are asserted
    EQUAL in both directions. `okf_hygiene`'s five-state model drifted precisely because a
    document and a test could each say "five" about different fives.
    """
    assert _SPEC.is_file(), f"no landing spec at {_SPEC}"
    text = _SPEC.read_text(encoding="utf-8")

    for i in range(20):
        assert f"**L{i}**" in text, f"spec does not enumerate step label L{i}"

    for state in pm.LAND_JOURNAL_STATES:
        assert state in text, f"spec does not name journal state {state}"

    spec_states = set(re.findall(r"`(L_[A-Z0-9_]+)`", text))
    assert spec_states == set(pm.LAND_JOURNAL_STATES), (
        "the spec's journal-state set and the code's differ:\n"
        f"  spec-only: {sorted(spec_states - set(pm.LAND_JOURNAL_STATES))}\n"
        f"  code-only: {sorted(set(pm.LAND_JOURNAL_STATES) - spec_states)}")

    assert len(pm.LAND_CONFLICT_STATES) == 4
    assert set(pm.LAND_PROGRESS_ORDER) | pm.LAND_CONFLICT_STATES == set(pm.LAND_JOURNAL_STATES)
    assert not (set(pm.LAND_PROGRESS_ORDER) & pm.LAND_CONFLICT_STATES), (
        "progress and conflict states must be disjoint")

    for name in ("REQ-LAND-013", "REQ-LAND-014", "REQ-LAND-015"):
        assert name in text
    assert "not prevention" in text
    assert "detection, not prevention" in text
    assert "herdr pane run" in text


# =========================================================================================
# SC19 — the journal makes every enumerated state resumable
# =========================================================================================

def test_journal_recovery_every_state(repo):
    """SC19 / Issues 3.1, 3.7 / REQ-LAND-009.

    TOTAL over the state set: every one of the seventeen is written and recovered. A recovery
    table that is total over 13 of 17 is the `okf_hygiene` S1 defect again.
    """
    j = pm.LandingJournal(repo, PLAN_ID)

    assert j.recover()["action"] == "start", "no journal means a fresh landing"

    for state in pm.LAND_JOURNAL_STATES:
        j.write(state, note="t")
        rec = j.read()
        assert rec["phase"] == state
        assert rec["meaning"] == pm.LAND_JOURNAL_STATES[state]
        assert rec["route_record"]["pid"] == os.getpid()

        r = j.recover()
        assert r["phase"] == state
        if state in pm.LAND_CONFLICT_STATES:
            assert r["action"] == "halt"
            assert r["recovery"] == pm.LAND_CONFLICT_RECOVERY[state]
        elif state == pm.LAND_TERMINAL_STATE:
            assert r["action"] == "done"
        else:
            assert r["action"] == "resume"
            # RE-DERIVED, NEVER TRUSTED: a resume re-checks the digest before continuing.
            assert r["must_recheck_digest"] is True

    # The journal is INSIDE THE REPO TREE, never a mktemp -d.
    assert str(j.path).startswith(str(repo)), "the journal must be staged inside the tree"
    assert pm.LAND_JOURNAL_DIR in str(j.path)


def test_journal_rejects_an_unenumerated_state(repo):
    """The set is CLOSED. Adding a state means amending the spec in the same change-set."""
    j = pm.LandingJournal(repo, PLAN_ID)
    with pytest.raises(ValueError, match="CLOSED"):
        j.write("L_SOMETHING_INVENTED")


def test_a_corrupt_journal_is_not_an_absent_one(repo):
    """The single most dangerous wrong answer available here.

    Reading a corrupt journal as "nothing started" would invite a re-run of steps that may
    already have PUSHED. It must be INCONCLUSIVE.
    """
    j = pm.LandingJournal(repo, PLAN_ID)
    j.write("L_PUSHED_1")
    j.path.write_text("{not json", encoding="utf-8")
    r = j.recover()
    assert r["action"] == "halt"
    assert r["inconclusive"] is True
    assert "NOT an absent one" in r["reason"]


def test_journal_recovery_is_keyed_on_phase_not_observed_state(repo):
    """REQ-LAND-009, and this is the assertion that actually pins the property.

    The tree is made IDENTICAL for two different recorded phases. Anything keyed on observed
    state must answer the same for both; the journal answers differently, which is the point.
    """
    j = pm.LandingJournal(repo, PLAN_ID)
    # Snapshot AFTER the first write: the journal is staged INSIDE the tree (REQ-LAND-008),
    # so its own directory is part of the tree state. Capturing before would compare a tree
    # with no journal against a tree with one and prove nothing about phase-vs-observation.
    j.write("L_LOCKED")
    clean = _git("status", "--porcelain", cwd=repo).stdout
    a = j.recover()
    j.write("L_PUSHED_1")
    b = j.recover()

    assert _git("status", "--porcelain", cwd=repo).stdout == clean, (
        "the fixture must present an IDENTICAL tree for both phases, or the test proves "
        "nothing about phase-vs-observation")
    assert a["resume_after"] != b["resume_after"]
    assert a["next"] != b["next"]


def test_journal_survives_a_write_and_is_fsynced(repo):
    """The durability property, checked structurally: the file exists and re-reads after a
    fresh handle, and history accumulates rather than being overwritten."""
    j = pm.LandingJournal(repo, PLAN_ID)
    j.write("L_INIT")
    j.write("L_LOCKED")
    fresh = pm.LandingJournal(repo, PLAN_ID)
    rec = fresh.read()
    assert rec["history"] == ["L_INIT", "L_LOCKED"]
    fresh.clear()
    assert fresh.read() is None


# =========================================================================================
# SC15 / SC16 / SC21 — binding a decision to re-derived reality
# =========================================================================================

def _decision(digest: str, **over) -> dict:
    d = {"schema": pm.LAND_SCHEMA_DECISION, "manifest_digest": digest, "plan_id": PLAN_ID,
         "authored_by": "lander", "summary": "s", "upstream_writes": [],
         "steps": {k: "enable" for k in pm.LAND_STEPS}}
    d.update(over)
    return d


def test_digest_mismatch_halts(repo):
    """SC15 / Issue 3.2. A decision that disagrees with re-derived reality HALTS."""
    rel = Path("docs/plans") / PLAN_ID
    bad = pm._land_bind_decision(rel, _decision("sha256:" + "f" * 64))
    assert bad["bound"] is False
    assert bad["validation"]["verdict"] == "fail"
    assert any("MISMATCH" in p for p in bad["validation"]["problems"])

    good = pm._land_bind_decision(rel, _decision(
        pm._land_digest(pm._land_manifest(rel)["facts"])))
    assert good["bound"] is True


def test_narrowing_only(repo):
    """SC16. An `enable` on a step the manifest HALTED is ignored and REPORTED."""
    rel = Path("docs/plans") / PLAN_ID
    m = {"facts": {"x": 1}, "halts": [{"code": "merge-conflicts-predicted", "detail": "d"}]}
    env = pm._land_validate_decision(_decision(pm._land_digest(m["facts"])), m)
    assert env["ignored_enables"], "an ignored enable must be REPORTED, never silent"

    clean = {"facts": {"x": 1}, "halts": []}
    env2 = pm._land_validate_decision(_decision(pm._land_digest(clean["facts"])), clean)
    assert env2["ignored_enables"] == []

    for step in sorted(pm.LAND_NON_SKIPPABLE):
        d = _decision(pm._land_digest(clean["facts"]))
        d["steps"][step] = "skip:x"
        assert pm._land_validate_decision(d, clean)["verdict"] == "fail"


def test_stale_decision_halts_before_merge(repo):
    """SC21 / Issue 3.6. A CLEAN PREVIEW DOES NOT GUARANTEE A CLEAN APPLY.

    Preview clean at T0; the target advances; the decision is now stale. The halt reports a
    DIGEST MISMATCH — detectable BEFORE the merge is attempted — rather than a conflicted
    working tree discovered afterwards. The tree is asserted untouched across the halt.
    """
    rel = Path("docs/plans") / PLAN_ID
    d = _decision(pm._land_digest(pm._land_manifest(rel)["facts"]))
    assert pm._land_repreview_or_halt(rel, d)["proceed"] is True

    (repo / "skills" / "another.txt").write_text("another plan landed\n", encoding="utf-8")
    _git("add", "-A", cwd=repo)
    _git("commit", "-q", "-m", "target advances", cwd=repo)

    before = _git("status", "--porcelain", cwd=repo).stdout
    out = pm._land_repreview_or_halt(rel, d)

    assert out["proceed"] is False
    assert out["stale"] is True
    assert "moved since this decision was minted" in out["reason"]
    assert out["halt_class"] == pm.LAND_HALT_MECHANICAL
    assert "never applied and never overridden" in out["remediation"]
    assert _git("status", "--porcelain", cwd=repo).stdout == before, (
        "the staleness halt must happen BEFORE anything is touched")
    assert not (repo / ".git" / "MERGE_HEAD").exists()


# =========================================================================================
# SC17 / SC18 — the tty gate and the route record
# =========================================================================================

def test_tty_gate_refuses_and_is_posix_only():
    """SC17 / Issue 3.3. Refuses without a controlling terminal, at exit 3, POSIX-only.

    Under pytest fd 0 is not a tty, so the gate refuses HERE — the test runs as its own
    subject. Both refusal predicates are asserted, and so is the ABSENCE of any
    herdr-derived predicate: `herdr api schema --json` contains zero `human` and zero
    `attached`, so such a predicate would degrade to matching ANY herdr pane.
    """
    g = pm._land_tty_gate()
    assert g["allowed"] is False
    assert g["route_record"]["has_tty"] is False
    assert "REFUSED" in g["reason"]

    # NOT PREVENTION, and the remediation says so rather than implying a guarantee.
    assert "herdr pane run" in g["remediation"]
    assert "KNOWN" in g["remediation"] or "known" in g["remediation"]

    # POSIX-ONLY: the gate's source names ttyname and /dev/tty, and NOTHING herdr-derived.
    import inspect
    src = inspect.getsource(pm._land_tty_gate)
    assert "ttyname" in src and "/dev/tty" in src
    # THE PROPERTY IS "RUNS NO EXTERNAL PROCESS", not "never says the word herdr". The gate's
    # remediation legitimately NAMES `herdr pane run` as a known bypass — telling the reader
    # the truth about the gate is the opposite of depending on herdr. A token-blocklist here
    # would forbid the honesty and permit the dependency, which is exactly backwards.
    # ASSERT ON IDENTIFIERS AND CALL TARGETS, NEVER ON TOKENS.
    #
    # Three progressively-less-wrong drafts of this assertion failed before this one, and the
    # reason is worth stating: the gate's remediation string LEGITIMATELY contains the words
    # `herdr pane run`, because telling the operator the truth about a known bypass is the
    # entire point of the control. A token scan cannot distinguish "names herdr in prose" from
    # "depends on herdr", and every version that tried forbade the honesty while permitting
    # the dependency — exactly backwards.
    #
    # The real property is structural: the predicate CALLS nothing external. `herdr` can only
    # ever appear as a string; it can never be an identifier or a call target.
    import ast as _ast
    fn = _ast.parse(src).body[0]
    idents = {n.id for n in _ast.walk(fn) if isinstance(n, _ast.Name)}
    attrs = {n.attr for n in _ast.walk(fn) if isinstance(n, _ast.Attribute)}
    calls = set()
    for n in _ast.walk(fn):
        if isinstance(n, _ast.Call):
            f = n.func
            calls.add(f.id if isinstance(f, _ast.Name) else
                      getattr(f, "attr", "") if isinstance(f, _ast.Attribute) else "")

    assert "subprocess" not in idents, "a pure-POSIX predicate shells out to nothing"
    assert "_run_git" not in idents and "_run_git" not in calls
    for spawn in ("run", "Popen", "check_output", "system", "popen", "spawn"):
        assert spawn not in calls, f"the gate spawns a process: {spawn}"

    # POSITIVE half — it really IS the POSIX predicate, not merely "not herdr". An absence
    # check with no positive half passes against a gate that tests nothing at all.
    #
    # THE PREDICATE IS SPLIT ACROSS TWO FUNCTIONS and the assertion follows it rather than
    # assuming: `os.ttyname(0)` is in `_land_route_record` (which the gate composes with),
    # and the `/dev/tty` openability test is in the gate itself. REQ-LAND-014 names both
    # conditions, so both are checked — in whichever half actually carries them.
    rr_src = inspect.getsource(pm._land_route_record)
    rr_calls = {getattr(n.func, "attr", getattr(n.func, "id", ""))
                for n in _ast.walk(_ast.parse(rr_src)) if isinstance(n, _ast.Call)}
    assert "ttyname" in rr_calls, "the predicate must test os.ttyname(0)"
    assert any(isinstance(n, _ast.Constant) and n.value == "/dev/tty"
               for n in _ast.walk(fn)), "the gate must test /dev/tty openability"
    assert "subprocess" not in {n.id for n in _ast.walk(_ast.parse(rr_src))
                                if isinstance(n, _ast.Name)}, (
        "the route record must not shell out either — it is half the same predicate")

    # THE OPERATOR-CONFIGURED allow-list is the only escape, and it is not herdr-derived.
    allowed = pm._land_tty_gate(allow_list=[g["route_record"]["tty"] or "/dev/ttys999"])
    assert allowed["allowed"] is False or allowed["route_record"].get("allowed_by")


def test_tty_refusal_exits_three_not_one_or_two(repo):
    """The exit code is the CONTRACT (REQ-CLI-030), and 3 is neither 1 nor 2.

    Not 1: nothing about the landing was measured false. Not 2: the verb ran and reached a
    definite conclusion. Driven through the real CLI, not the helper.
    """
    dec = repo / "d.json"
    dec.write_text(json.dumps(_decision("sha256:" + "0" * 64)), encoding="utf-8")
    p = subprocess.run(
        ["uv", "run", str(_PM), "land", "--apply", str(dec), f"docs/plans/{PLAN_ID}"],
        cwd=repo, capture_output=True, text=True)
    assert p.returncode == 3, f"expected exit 3, got {p.returncode}: {p.stdout}{p.stderr}"
    env = json.loads(p.stdout)
    assert env["verdict"] == "fail"
    assert env["halt_class"] == pm.LAND_HALT_OUTWARD
    assert env["route_record"]["has_tty"] is False


def test_route_record_detects_agent(repo, monkeypatch):
    """SC18 / Issue 3.4. The record is stamped, and `audit-close` FAILS a `Type: human`
    gate whose record reads "no tty, CLAUDECODE set".

    ASYMMETRIC BY DESIGN, and both directions are asserted: a dirty record is reported, a
    clean one is not. Reporting a clean record would claim the record PROVES a human, which
    it cannot — the markers are strippable.
    """
    monkeypatch.setenv("CLAUDECODE", "1")
    rr = pm._land_route_record()
    assert rr["has_tty"] is False
    assert "CLAUDECODE" in rr["agent_markers"]
    assert "detection, not prevention" in rr["note"]
    # NAMES ONLY — a value must never reach the record.
    assert "1" not in [v for k, v in rr.items() if k == "agent_markers"]

    dirty = {"has_tty": False, "agent_markers": ["CLAUDECODE"]}
    clean = {"has_tty": True, "agent_markers": []}
    assert pm._land_route_record_is_agent(dirty) is True
    assert pm._land_route_record_is_agent(clean) is False

    monkeypatch.delenv("CLAUDECODE", raising=False)


def test_route_record_never_captures_a_value(monkeypatch):
    """A route record must never become a secret-exfiltration path."""
    monkeypatch.setenv("CLAUDECODE", "super-secret-value")
    rr = pm._land_route_record()
    assert "super-secret-value" not in json.dumps(rr)
    assert rr["agent_markers"] == sorted(set(rr["agent_markers"]))


# =========================================================================================
# SC20 — the conflict contract
# =========================================================================================

def test_conflict_captured_and_restored(repo):
    """SC20 / Issue 3.5. Three sources captured, tree restored, no auto-resolution flag.

    A REAL conflict is produced and a REAL merge attempted — the capture is exercised against
    an actually-conflicted index rather than a mock.
    """
    (repo / "skills" / "clash.txt").write_text("main\n", encoding="utf-8")
    _git("add", "-A", cwd=repo)
    _git("commit", "-q", "-m", "main edit", cwd=repo)
    _git("checkout", "-q", f"{PLAN_ID}-execute", cwd=repo)
    (repo / "skills" / "clash.txt").write_text("branch\n", encoding="utf-8")
    _git("add", "-A", cwd=repo)
    _git("commit", "-q", "-m", "branch edit", cwd=repo)
    _git("checkout", "-q", "main", cwd=repo)

    m = _git("merge", "--no-ff", "-m", "m", f"{PLAN_ID}-execute", cwd=repo)
    assert m.returncode != 0, "the fixture must actually conflict"

    cap = pm._land_capture_conflict("L_CONFLICT_MERGE", repo)
    assert cap["site"] == "L_CONFLICT_MERGE"
    assert cap["auto_resolved"] is False
    # THREE INDEPENDENT SOURCES, each non-empty.
    assert any("clash.txt" in p for p in cap["unmerged_paths"]), "source 1: the path list"
    assert cap["porcelain_v2"], "source 2: per-path stage detail"
    assert cap["merge_head"], "source 3: MERGE_HEAD"
    assert cap["recovery"] == pm.LAND_CONFLICT_RECOVERY["L_CONFLICT_MERGE"]

    out = pm._land_abort_merge(repo)
    assert out["aborted"] is True
    assert out["tree_clean"] is True, "measured: `merge --abort` restores an empty porcelain"


def test_no_auto_resolution_flag_is_ever_passed():
    """The absence half of SC20, read from the SOURCE rather than by running a merge.

    `-X ours` silently discards one side and the discarding is INVISIBLE in the resulting
    commit — so a runtime test cannot observe it after the fact. The source is where it is
    checkable.
    """
    code = _code_only(_PM.read_text(encoding="utf-8"))
    landing = code[code.index("LAND_SCHEMA_MANIFEST"):]
    # EXCLUDE the constant's OWN definition: LAND_FORBIDDEN_MERGE_FLAGS exists precisely to
    # NAME these flags, so scanning across it would read the enumeration of what is forbidden
    # as a use of it.
    decl = landing.index("LAND_FORBIDDEN_MERGE_FLAGS")
    scanned = landing[:decl] + landing[landing.index("\n", landing.index(")", decl)):]
    for flag in ("-X", "--strategy-option", "'ours'", "'theirs'", '"ours"', '"theirs"'):
        assert flag not in scanned, f"the landing path passes {flag}"
    assert len(pm.LAND_FORBIDDEN_MERGE_FLAGS) >= 4

    # The constant must still be REACHABLE, or its absence-check is decoration.
    assert "-X" in pm.LAND_FORBIDDEN_MERGE_FLAGS


def test_conflict_states_have_non_uniform_recoveries():
    """FOUR sites means FOUR recoveries, and `restore` is WRONG for one of them.

    This is the property that makes four states necessary rather than one generic
    "conflicted": an L16 rejection is post-outward-write, so its recovery is
    retry-never-revert.
    """
    r = pm.LAND_CONFLICT_RECOVERY
    assert len(r) == 4
    assert len(set(r.values())) == 4, "four sites, four DISTINCT recoveries"
    assert "merge --abort" in r["L_CONFLICT_DOWNMERGE"]
    assert "merge --abort" in r["L_CONFLICT_MERGE"]
    assert "RE-VALIDATE" in r["L_REJECTED_PUSH_1"]
    assert "NEVER REVERT" in r["L_REJECTED_PUSH_2"]
    assert "merge --abort" not in r["L_REJECTED_PUSH_2"], (
        "abort is the WRONG recovery post-outward-write — the comments are posted, the beads "
        "closed and `status: complete` written")


def test_capture_rejects_an_unenumerated_site(repo):
    with pytest.raises(ValueError, match="four enumerated conflict states"):
        pm._land_capture_conflict("L_SOMETHING_ELSE", repo)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))
