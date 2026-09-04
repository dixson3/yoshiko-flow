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
        "| :-- | :-- | :-- | :-- | :-- |\n"
        "| #1 | a | partial | n | 1.1 |\n"
        "| #301 | b | include | n | 1.1 |\n"
        "| #293 | c | partial | n | 1.2 |\n", encoding="utf-8")
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


def test_route_record_check_sees_a_CLOSED_gate(repo, monkeypatch):
    """REQ-LAND-015 regression. THE CHECK MUST BE ABLE TO FIRE AT ALL.

    THE DEFECT THIS PINS, measured on the live tree: `_land_route_record_findings` queried
    `bd list --type gate` WITHOUT `--all`, and **`bd list` excludes closed issues by
    default**. A route record is stamped AT CLOSE, so the two reachable states were:

        gate OPEN   -> no route_record yet   -> `if not rr: continue` -> nothing to flag
        gate CLOSED -> record exists         -> INVISIBLE TO THE QUERY

    There is no third state, so the check could never fire — for any gate, ever. A CHECK THAT
    CANNOT FAIL, shipped as the detection control for dixson3/yoshiko-flow#293, by the plan
    whose subject is checks that cannot fail.

    THE FAKE `bd` REPRODUCES THE REAL SEMANTICS rather than just returning the gate: it
    returns the closed gate ONLY when `--all` is present. So this test is RED against the
    unfixed query and GREEN against the fixed one, which is the property that makes it a
    regression test rather than a restatement.
    """
    pdir = repo / "docs" / "plans" / PLAN_ID
    # The **Epic:** field is a HEADER field and must sit ABOVE the first `## ` heading —
    # `_read_plan_field` reads the header block only. Appending it at end-of-file (an earlier
    # draft of this fixture) leaves it unread, and the check then returns early having never
    # queried bd, which looks exactly like the bug under test. A fixture that reproduces the
    # symptom for the wrong reason is worse than no fixture.
    t = (pdir / "plan.md").read_text(encoding="utf-8")
    t = t.replace("\n## ", "\n**Epic:** yf-mol-test\n\n## ", 1)
    (pdir / "plan.md").write_text(t, encoding="utf-8")

    gate = {
        "id": "yf-mol-test.8",
        "title": "Gate: a human consent gate",
        "status": "closed",
        "issue_type": "gate",
        "metadata": {
            "gate_type": "human",
            "route_record": {
                "has_tty": False,
                "agent_markers": ["CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT"],
                "closed_by": "execution-agent",
            },
        },
    }

    calls: list[list[str]] = []

    class _P:
        def __init__(self, out): self.returncode = 0; self.stdout = out; self.stderr = ""

    real_run = subprocess.run

    def fake_run(args, *a, **kw):
        if isinstance(args, list) and args and args[0] == "bd":
            calls.append(args)
            # REAL SEMANTICS: closed issues are returned ONLY with --all.
            return _P(json.dumps([gate] if "--all" in args else []))
        return real_run(args, *a, **kw)

    monkeypatch.setattr(pm.subprocess, "run", fake_run)
    monkeypatch.setattr(pm.shutil, "which", lambda n: "/usr/bin/bd")

    findings = pm._land_route_record_findings(Path("docs/plans") / PLAN_ID)

    assert calls, "the check never queried bd at all"
    assert any("--all" in c for c in calls), (
        "the bd gate query omits --all, so it can never see a CLOSED gate — and a route "
        "record only exists once the gate is closed. The check cannot fire.")
    assert len(findings) == 1, (
        f"expected the agent-closed human gate to be flagged, got {findings}")
    f = findings[0]
    assert f["status"] == "fail"
    assert "yf-mol-test.8" in f["item"]
    assert "CLAUDECODE" in f["detail"]
    assert "DETECTION, not prevention" in f["detail"]


def test_route_record_check_does_not_flag_a_clean_close(repo, monkeypatch):
    """The other direction. Flagging a CLEAN record would claim it proves a human, which it
    cannot — the markers are strippable, so absence is weak evidence (REQ-LAND-015)."""
    pdir = repo / "docs" / "plans" / PLAN_ID
    # The **Epic:** field is a HEADER field and must sit ABOVE the first `## ` heading —
    # `_read_plan_field` reads the header block only. Appending it at end-of-file (an earlier
    # draft of this fixture) leaves it unread, and the check then returns early having never
    # queried bd, which looks exactly like the bug under test. A fixture that reproduces the
    # symptom for the wrong reason is worse than no fixture.
    t = (pdir / "plan.md").read_text(encoding="utf-8")
    t = t.replace("\n## ", "\n**Epic:** yf-mol-test\n\n## ", 1)
    (pdir / "plan.md").write_text(t, encoding="utf-8")
    gate = {"id": "yf-mol-test.8", "title": "Gate: g", "status": "closed",
            "issue_type": "gate",
            "metadata": {"gate_type": "human",
                         "route_record": {"has_tty": True, "agent_markers": []}}}

    class _P:
        def __init__(self, out): self.returncode = 0; self.stdout = out; self.stderr = ""

    real_run = subprocess.run
    monkeypatch.setattr(pm.subprocess, "run",
                        lambda args, *a, **kw: _P(json.dumps([gate]))
                        if isinstance(args, list) and args and args[0] == "bd"
                        else real_run(args, *a, **kw))
    monkeypatch.setattr(pm.shutil, "which", lambda n: "/usr/bin/bd")
    assert pm._land_route_record_findings(Path("docs/plans") / PLAN_ID) == []


def test_route_record_check_agrees_across_address_spaces(repo, monkeypatch, tmp_path):
    """REQ-LAND-015. THE CHECK MUST ANSWER THE SAME FROM BOTH ADDRESS SPACES.

    THE DEFECT THIS PINS, measured on the live tree at 09c74f6: identical command, identical
    plan_dir, `fail` from the primary checkout and `pass` from the execute worktree — because
    `plan_dir/plan.md` is read RELATIVE TO CWD and the `**Epic:**` field is written
    PRIMARY-SIDE, so the worktree's copy predates it. The check had TWO TRUTHS, and the wrong
    one was a SILENT PASS.

    The fixture reproduces exactly that asymmetry: the epic field exists only in the primary's
    plan.md, and the linked worktree carries the pre-execution copy.
    """
    wt = repo / ".worktrees" / PLAN_ID
    (repo / ".gitignore").write_text(".worktrees/\n", encoding="utf-8")
    _git("add", "-A", cwd=repo); _git("commit", "-q", "-m", "ignore", cwd=repo)
    assert _git("worktree", "add", "-q", str(wt), f"{PLAN_ID}-execute", cwd=repo).returncode == 0

    # THE ASYMMETRY: the epic field lands PRIMARY-SIDE only, which is what the address-space
    # model prescribes and what actually happens during execution.
    pm_md = repo / "docs" / "plans" / PLAN_ID / "plan.md"
    t = pm_md.read_text(encoding="utf-8").replace("\n## ", "\n**Epic:** yf-mol-test\n\n## ", 1)
    pm_md.write_text(t, encoding="utf-8")
    assert "yf-mol-test" not in (wt / "docs" / "plans" / PLAN_ID / "plan.md").read_text(
        encoding="utf-8"), "the fixture must reproduce the asymmetry, not paper over it"

    gate = {"id": "yf-mol-test.8", "title": "Gate: g", "status": "closed",
            "issue_type": "gate",
            "metadata": {"gate_type": "human",
                         "route_record": {"has_tty": False,
                                          "agent_markers": ["CLAUDECODE"]}}}
    # The epic, stamped with metadata.plan_dir at pour time — the cwd-INDEPENDENT linkage.
    epic_bead = {"id": "yf-mol-test", "title": "plan-execute", "status": "open",
                 "issue_type": "epic",
                 "metadata": {"plan_dir": f"docs/plans/{PLAN_ID}"}}

    class _P:
        def __init__(self, out): self.returncode = 0; self.stdout = out; self.stderr = ""

    real_run = subprocess.run

    def fake_run(args, *a, **kw):
        if isinstance(args, list) and args and args[0] == "bd":
            if "--type" in args and "gate" in args:
                return _P(json.dumps([gate] if "--all" in args else []))
            return _P(json.dumps([epic_bead, gate]))
        return real_run(args, *a, **kw)

    monkeypatch.setattr(pm.subprocess, "run", fake_run)
    monkeypatch.setattr(pm.shutil, "which", lambda n: "/usr/bin/bd")

    rel = Path("docs/plans") / PLAN_ID
    cwd0 = os.getcwd()
    try:
        os.chdir(repo)
        from_primary = pm._land_route_record_findings(rel)
        os.chdir(wt)
        from_worktree = pm._land_route_record_findings(rel)
    finally:
        os.chdir(cwd0)

    def shape(fs):
        return sorted((f["status"], f.get("class", "finding"), f["item"]) for f in fs)

    assert shape(from_primary) == shape(from_worktree), (
        "THE CHECK HAS TWO TRUTHS depending on where the caller stands:\n"
        f"  primary : {shape(from_primary)}\n"
        f"  worktree: {shape(from_worktree)}\n"
        "A control that answers differently by address space is not a control.")
    assert from_primary, "both agreed — on NOTHING. Agreement on silence is not agreement."
    assert any(f["status"] == "fail" for f in from_primary)


def test_route_record_check_no_op_is_LOUD(repo, monkeypatch):
    """The check must never return an empty list meaning "did not run".

    `if not epic: return out` was silent, and every caller read the empty list as "checked and
    clean". A control whose failure mode is indistinguishable from a clean result is the
    defect this plan exists to remove. The no-op is now an INCONCLUSIVE-class finding —
    `warn`, never `fail`, per REQ-DATA-057: an instrument that could not run must not
    manufacture a verdict on the artifact.
    """
    class _P:
        def __init__(self, out): self.returncode = 0; self.stdout = out; self.stderr = ""

    real_run = subprocess.run
    monkeypatch.setattr(pm.shutil, "which", lambda n: "/usr/bin/bd")
    monkeypatch.setattr(pm.subprocess, "run",
                        lambda args, *a, **kw: _P("[]")
                        if isinstance(args, list) and args and args[0] == "bd"
                        else real_run(args, *a, **kw))

    out = pm._land_route_record_findings(Path("docs/plans") / PLAN_ID)
    assert out, "an unresolvable epic must NOT return an empty list — that reads as `clean`"
    assert out[0]["class"] == "inconclusive"
    assert out[0]["status"] == "warn", "INCONCLUSIVE maps to warn, never fail (REQ-DATA-057)"
    assert "DID NOT RUN" in out[0]["detail"]

    # And when `bd` is absent entirely — also loud, for the same reason.
    monkeypatch.setattr(pm.shutil, "which", lambda n: None)
    out2 = pm._land_route_record_findings(Path("docs/plans") / PLAN_ID)
    assert out2 and out2[0]["class"] == "inconclusive"
    assert "not on PATH" in out2[0]["detail"]


def test_no_target_taking_rewind_in_landing_path():
    """REQ-LAND-017a. No landing step issues a history-rewind that takes a TARGET REVISION.

    THIS PINS AN IMMUNITY THAT WAS ACCIDENTAL. The landing path happens to contain no `reset`,
    `revert`, `cherry-pick` or forced push, and its one history-affecting operation
    (`git merge --abort`) takes NO revision argument — git computes the restore point from
    MERGE_HEAD/ORIG_HEAD, so there is no target to select wrongly.

    Why it needs pinning: during this plan's own execution the session proposed
    `git reset --hard <commit>` on the TRUE premise that the commit being dropped contained
    nothing it had authored, and that reset would have deleted a LATER commit sitting on top —
    the very fix the reset existed to preserve. A rewind target is defined by what it
    PRESERVES, not by what it drops. An executor computing one the same way would make that
    error with the operator's authorization already attached.

    Issue 4.10 still has to decide abort-vs-leave empirically, so a future implementation could
    reach for a target-taking form. This test is what makes that a failure rather than a
    regression nobody notices.
    """
    code = _code_only(_PM.read_text(encoding="utf-8"))
    landing = code[code.index("LAND_SCHEMA_MANIFEST"):]

    for verb in ("reset", "cherry-pick", "--hard", "--force", "-f'", "revert"):
        assert f"'{verb}'" not in landing and f'"{verb}"' not in landing, (
            f"the landing path issues a history-rewinding git verb: {verb}")

    # The one permitted operation, asserted to take NO revision argument.
    import inspect
    abort = _code_only(inspect.getsource(pm._land_abort_merge))
    assert '"merge", "--abort"' in abort or "'merge', '--abort'" in abort
    call = re.search(r"_run_git\(\[(.*?)\]", abort, re.S)
    assert call, "could not locate the abort invocation"
    args = [a.strip().strip("\"'") for a in call.group(1).split(",")]
    assert args == ["merge", "--abort"], (
        f"`merge --abort` must take NO revision argument; got {args}")


def test_capture_rejects_an_unenumerated_site(repo):
    with pytest.raises(ValueError, match="four enumerated conflict states"):
        pm._land_capture_conflict("L_SOMETHING_ELSE", repo)


# =========================================================================================
# EPIC 4 — the ordered steps L0-L19, and the CONFLICT MATRIX (Issue 4.10)
# =========================================================================================


def _teardown_ok(plan_dir, force=False):
    """A stub of `_worktree_teardown` that matches the REAL SIGNATURE AND THE REAL SHAPE.

    Both axes were wrong, and only one of them is mechanically detectable. `check_mock_fidelity`
    binds `inspect.signature`, so it catches the arity; it is STRUCTURALLY BLIND to the RETURN
    shape, and the return shape is what L18 branches on (REQ-LAND-031). The four shipped stubs
    returned `{"action": "removed"}` — a key `_worktree_teardown` NEVER produces.
    """
    return {"status": "ok", "path": f".worktrees/{PLAN_ID}", "branch": f"{PLAN_ID}-execute",
            "steps": {"remove": {"ok": True, "detail": ""},
                      "branch_delete": {"ok": True, "detail": ""},
                      "prune": {"ok": True, "detail": ""}}}


def _step_ok(name, journal=None):
    return {"step": name, "verdict": "pass", "reason": "stubbed", "journal": journal,
            "halting": False, "detail": {}}


class FakeRunner:
    """A scripted process runner. Injected via LandingContext(runner=...), so the SAME step
    functions run under test as in production — one code path, not a parallel one."""

    def __init__(self, script=None):
        self.script = script or {}
        self.calls: list[list[str]] = []

    def __call__(self, prog, args, cwd=None):
        # THE PROGRAM IS PART OF THE RECORDED CALL. An earlier version dropped it and
        # returned 0 for any argv, which is precisely why `git issue comment`,
        # `git push --issues` and `git self install` all passed their tests. A fake that
        # answers everything cannot witness the wrong executable being invoked.
        self.calls.append([prog, *args])
        for key, res in self.script.items():
            if all(tok in [prog, *args] for tok in key.split("|")):
                return res
        return _R(0)

    def saw(self, *toks) -> bool:
        return any(all(t in c for t in toks) for c in self.calls)

    def programs(self) -> set:
        return {c[0] for c in self.calls}


class _R:
    def __init__(self, rc=0, out="", err=""):
        self.returncode = rc; self.stdout = out; self.stderr = err


def _ctx(repo, runner, decision=None, steps=None):
    rel = Path("docs/plans") / PLAN_ID
    manifest = pm._land_manifest(rel)
    d = {"schema": pm.LAND_SCHEMA_DECISION,
         "manifest_digest": pm._land_digest(manifest["facts"]),
         "plan_id": PLAN_ID, "authored_by": "lander", "summary": "s",
         "upstream_writes": [],
         "steps": steps or {k: "enable" for k in pm.LAND_STEPS}}
    if decision:
        d.update(decision)
    return pm.LandingContext(rel, d, manifest, root=repo, runner=runner)


# -- SC22 ---------------------------------------------------------------------------------

def test_red_full_tier_halts_with_lock_held(repo, monkeypatch):
    """SC22 / Issue 4.1. A red FULL tier halts WITH THE LANDING LOCK STILL HELD, and the
    post-merge tree assertion catches an invalidated down-merge.

    Both halves matter. The lock staying held is what makes the operator repair under
    serialization; the tree assertion is what catches `pull --rebase` picking up commits that
    arrived after L1, which the single-machine lock cannot prevent.
    """
    monkeypatch.setattr(pm, "_validate_merged",
                        lambda pd: {"status": "fail", "engine": "change-validation",
                                    "first_failure": {"cmd": "cargo test"}})
    ctx = _ctx(repo, FakeRunner())
    out = pm._land_l3_validate_merged(ctx)
    assert out["verdict"] == "fail" and out["halting"] is True
    assert out["detail"]["lock_held"] is True
    assert "LOCK IS STILL HELD" in out["reason"]

    # The post-merge tree assertion — trees deliberately disagree.
    r = FakeRunner({"rev-parse|HEAD^{tree}": _R(0, "aaa\n"),
                    f"rev-parse|{PLAN_ID}-execute^{{tree}}": _R(0, "bbb\n")})
    out2 = pm._land_l4_commit_merge(_ctx(repo, r))
    assert out2["verdict"] == "fail"
    assert "does NOT match the down-merged branch tree" in out2["reason"]
    assert out2["detail"]["lock_released"] is True, (
        "the lock must be released even on this failure — it is a post-merge assertion, not "
        "the validation gate")


def test_inconclusive_validation_is_not_coerced_to_fail(repo, monkeypatch):
    """#262/#263. An INCONCLUSIVE tier is reported and does NOT halt the landing."""
    monkeypatch.setattr(pm, "_validate_merged",
                        lambda pd: {"status": "inconclusive", "engine": "none"})
    out = pm._land_l3_validate_merged(_ctx(repo, FakeRunner()))
    assert out["verdict"] == "inconclusive"
    assert out["halting"] is False


# -- SC23 / SC24 ---------------------------------------------------------------------------

def test_prepush_recheck_is_advisory(repo):
    """SC23 / Issue 4.2. L5 reports without halting — ADVISORY describes the VERDICT, not
    whether it runs."""
    out = pm._land_l5_advisory_recheck(_ctx(repo, FakeRunner()))
    assert out["halting"] is False
    assert out["verdict"] == "pass"
    assert out["detail"]["advisory"] is True
    assert out["journal"] == "L_PREPUSH_CHECKED"


def test_push_one_is_gated_and_declared_irreversible(repo):
    """SC24 / Issue 4.3. L6 is declared THE FIRST IRREVERSIBLE STEP, and a halt after it is
    reported as leaving the merge on the target."""
    ok = pm._land_l6_push_one(_ctx(repo, FakeRunner()))
    assert ok["verdict"] == "pass"
    assert ok["detail"]["irreversible"] is True
    assert "IRREVERSIBLE" in ok["reason"]
    assert ok["journal"] == "L_PUSHED_1"

    # L6 sits AFTER L3 in the executor — the ordering is the gate.
    order = [k for k, _ in pm.LAND_EXECUTOR]
    assert order.index("l3_validate_merged") < order.index("l6_push_one")
    assert order.index("l6_push_one") < order.index("l7_reconcile_writes"), (
        "the first irreversible step must precede the first OUTWARD-FACING one")


# -- SC25 ----------------------------------------------------------------------------------

def test_readback_catches_wrong_body(repo):
    """SC25 / Issue 4.4. A write whose read-back body DIFFERS halts.

    An exit 0 from `gh` does not establish that the body posted is the body intended —
    measured on issue #292 during this plan's own drafting.
    """
    body = repo / "b.md"
    body.write_text("the body I intended to post\n", encoding="utf-8")
    dec = {"upstream_writes": [{"issue": "301", "action": "comment",
                                "body_path": str(body)}]}
    # gh reports success, but the read-back shows a DIFFERENT comment.
    r = FakeRunner({"issue|view": _R(0, json.dumps(
        {"state": "OPEN", "comments": [{"body": "something else entirely"}]}))})
    out = pm._land_l7_reconcile_writes(_ctx(repo, r, decision=dec))
    assert out["verdict"] == "fail"
    assert "could NOT be verified by read-back" in out["reason"]
    assert "exit 0 is not proof" in out["reason"]

    # And the matching body passes.
    r2 = FakeRunner({"issue|view": _R(0, json.dumps(
        {"state": "OPEN", "comments": [{"body": "the body I intended to post"}]}))})
    assert pm._land_l7_reconcile_writes(_ctx(repo, r2, decision=dec))["verdict"] == "pass"


def test_a_close_the_disposition_forbids_is_refused(repo):
    """Issue 4.4. `partial` requires end state OPEN, so a close is REFUSED regardless of what
    the decision asks — the agent explains the contract, it does not override it."""
    dec = {"upstream_writes": [{"issue": "293", "action": "close"}]}
    out = pm._land_l7_reconcile_writes(_ctx(repo, FakeRunner(), decision=dec))
    refused = out["detail"]["refused"]
    assert refused and refused[0]["issue"] == "293"
    assert "contradict the dispositions" in refused[0]["refused_because"]


# -- SC26 ----------------------------------------------------------------------------------

def test_close_chain_exit_codes_read(repo):
    """SC26 / Issue 4.5. The close chain's exit codes are READ, not echoed (#180).

    A halting non-zero stops the landing; an `inconclusive` (exit 2) does not.
    """
    halting = {s for _, _, h in [] } # placeholder
    tbl = {verb: h for verb, _, h in pm.LAND_CLOSE_CHAIN}
    assert tbl["close-reconcile-step"] is True, "gate-before-close ordering is HALTING (#180)"
    assert tbl["verify-reconcile"] is True
    assert tbl["recheck-criteria"] is True
    assert tbl["audit-close"] is False, "the close-time audit is ADVISORY"
    assert tbl["retrospective-report"] is False

    # `CHANGED` is HEAD^1..HEAD, never <target>...HEAD (#303).
    import inspect
    src = _code_only(inspect.getsource(pm._land_l8_to_l15_close_chain))
    assert "_land_changed_set" in src
    assert "..." not in src, "the empty-by-construction three-dot form must not appear"


def test_pour_fidelity_inconclusive_is_not_a_divergence(repo, monkeypatch):
    """Issue 4.5. THREE-VALUED, not two. Branching on `!= 0` reports an INCONCLUSIVE as a
    DIVERGENCE — two different facts collapsed into one signal (#181/#207's class)."""
    import ast as _ast, inspect
    # ASSERT ON THE AST, not on substring positions in unparsed source: `!= 0` occurs in
    # unrelated earlier lines, so an index comparison compares the wrong things — the same
    # "measure the thing you mean" error this suite keeps catching.
    fn = _ast.parse(inspect.getsource(pm._land_l13_l15_finish)).body[0]
    # SCOPED TO THE POUR-FIDELITY VARIABLE. Walking the whole function collects
    # `g.returncode != 0` from the complete-gate branch above it, so a whole-function
    # ordering assertion compares two different subjects — the same "measure the thing you
    # mean" error, one layer down.
    tests = []
    for node in _ast.walk(fn):
        if isinstance(node, _ast.If) and isinstance(node.test, _ast.Compare):
            left = node.test.left
            if (isinstance(left, _ast.Attribute) and left.attr == "returncode"
                    and isinstance(left.value, _ast.Name) and left.value.id == "f"):
                op = type(node.test.ops[0]).__name__
                val = getattr(node.test.comparators[0], "value", None)
                tests.append((op, val))
    assert ("Eq", 2) in tests, (
        f"the INCONCLUSIVE code 2 must be branched on SEPARATELY; found {tests}")
    assert ("NotEq", 0) in tests, f"the divergence branch is missing; found {tests}"
    assert tests.index(("Eq", 2)) < tests.index(("NotEq", 0)), (
        "the three-valued branch must precede the catch-all non-zero branch, or an "
        "INCONCLUSIVE is reported as a DIVERGENCE")


# -- SC27 ----------------------------------------------------------------------------------

def test_no_unpushed_plan_writes(repo):
    """SC27 / Issue 4.6. L16 asserts a clean porcelain AND zero unpushed commits — the exact
    residue measured on plan-057."""
    clean = FakeRunner({"status|--porcelain": _R(0, ""),
                        "rev-list|--count": _R(0, "0\n"),
                        "diff|--cached": _R(1)})
    ok = pm._land_l16_commit_and_push_two(_ctx(repo, clean))
    assert ok["verdict"] == "pass" and ok["journal"] == "L_PUSHED_2"

    dirty = FakeRunner({"status|--porcelain": _R(0, " M docs/plans/x/plan.md"),
                        "rev-list|--count": _R(0, "2\n"),
                        "diff|--cached": _R(1)})
    bad = pm._land_l16_commit_and_push_two(_ctx(repo, dirty))
    assert bad["verdict"] == "fail"
    assert "residue the step exists to remove" in bad["reason"]


# -- SC28 ----------------------------------------------------------------------------------

def test_residual_mirroring_is_concrete_and_gated(repo):
    """SC28 / Issue 4.7. L17 calls `upstream.py push` CONCRETELY and is PROPOSE-ONLY unless
    the grant demonstrably covers the bead set; a close is believed only on read-back."""
    dec = {"residual_bead_groups": [{"proposed_title": "t", "beads": ["yf-aaa", "yf-bbb"]}]}
    out = pm._land_l17_residual_mirroring(_ctx(repo, FakeRunner(), decision=dec))
    assert out["verdict"] == "pass"
    assert "PROPOSE-ONLY" in out["reason"]
    assert out["detail"]["applied"] == []
    prop = out["detail"]["proposed"][0]
    assert "upstream.py" in prop and "push --issues yf-aaa,yf-bbb --apply" in prop, (
        "the proposal must name the CONCRETE subcommand — `/yf-beads-upstream` is a prose "
        "skill this Python cannot invoke")

    # A grant naming only ONE of the two beads does NOT cover the set.
    g = repo / "docs" / "plans" / PLAN_ID / "assets" / "upstream-grant.md"
    g.parent.mkdir(parents=True, exist_ok=True)
    g.write_text("authorized: yf-aaa\n", encoding="utf-8")
    cov = pm._land_grant_covers(Path("docs/plans") / PLAN_ID, ["yf-aaa", "yf-bbb"])
    assert cov["covered"] is False and cov["uncovered"] == ["yf-bbb"]
    g.write_text("authorized: yf-aaa, yf-bbb\n", encoding="utf-8")
    assert pm._land_grant_covers(Path("docs/plans") / PLAN_ID,
                                 ["yf-aaa", "yf-bbb"])["covered"] is True


# -- SC29 ----------------------------------------------------------------------------------

def test_prune_is_strategy_aware(repo, monkeypatch):
    """SC29 / Issue 4.8. A `feature-branch` fixture KEEPS `<plan-id>` and loses only
    `<plan-id>-execute`; the tab close defaults to a PROPOSAL."""
    seen = []

    def _capture(plan_dir, force=False, **kw):
        seen.append(((plan_dir,), {"force": force, **kw}))
        return _teardown_ok(plan_dir, force)

    monkeypatch.setattr(pm, "_worktree_teardown", _capture)

    monkeypatch.setattr(pm, "_resolve_landing_strategy", lambda: "feature-branch")
    r = FakeRunner()
    out = pm._land_l18_prune(_ctx(repo, r))
    assert out["detail"]["strategy"] == "feature-branch"
    assert PLAN_ID in out["detail"]["preserved"], "REQ-BRANCH-004: the feature branch is KEPT"
    # REPLACED, NOT DELETED (Issue 2.2). The duplicate `ctx.run` branch-delete this used to
    # assert on is gone — the real delete happens INSIDE `_worktree_teardown` via `_run_git`
    # and is invisible to `ctx.run`. Deleting the assertion would leave L18's HEADLINE ACTION
    # untested at the step level, so it is replaced with the two facts that survive the fix:
    # the delegation is made with the right arguments, and no branch delete reaches `ctx.run`.
    assert seen == [((pm.Path("docs/plans") / PLAN_ID,), {"force": False})], (
        f"L18 must delegate to _worktree_teardown(plan_dir, force=False) in KEYWORD form; "
        f"observed {seen}")
    assert not [c for c in r.calls if "branch" in c and "-d" in c], (
        "L18 must NOT issue its own `git branch -d` — the teardown already deletes the "
        "branch, so a second delete permanently reports ok:false 'branch not found'")
    dele = [a for a in out["detail"]["actions"] if a["action"] == "delete-execute-branch"][0]
    assert dele["via"] == "_worktree_teardown" and dele["ok"] is True, (
        "the delete is REPORTED from the teardown's own branch_delete step")

    tab = [a for a in out["detail"]["actions"] if a["action"] == "herdr-tab"][0]
    assert tab["decision"] == "PROPOSE", "provenance is unanswerable, so a close is never inferred"


# -- SC30 ----------------------------------------------------------------------------------

def test_redeploy_iff_skills_touched(repo, monkeypatch):
    """SC30 / Issue 4.9. IFF, not IF — both directions asserted."""
    monkeypatch.setattr(pm, "_land_changed_set", lambda root=None: ["docs/x.md"])
    r = FakeRunner()
    out = pm._land_l19_redeploy(_ctx(repo, r))
    assert out["detail"]["redeployed"] is False
    assert "correctly SKIPPED" in out["reason"]
    assert not r.saw("self", "install"), "redeploy ran on a change set that touches no skills/"

    monkeypatch.setattr(pm, "_land_changed_set",
                        lambda root=None: ["skills/yf-plan/SKILL.md"])
    r2 = FakeRunner()
    out2 = pm._land_l19_redeploy(_ctx(repo, r2))
    assert out2["detail"]["redeployed"] is True
    assert r2.saw("self", "install", "--from-build")
    assert out2["journal"] == "L_DONE"


# -- SC31 — THE CONFLICT MATRIX ------------------------------------------------------------

def test_conflict_matrix_covers_four_sites_and_staleness(repo, monkeypatch):
    """SC31 / Issue 4.10 — the operator-requested matrix. FIVE cases.

    L1 down-merge · L2 merge · L6 push rejection · **L16 push rejection (POST-outward-write)**
    · target-moved staleness. Each asserts the halt is LEGIBLE and, where restoration applies,
    that the tree is restored.

    THE MATRIX IS WHAT DECIDES abort-vs-leave EMPIRICALLY, which the plan deliberately did not
    decide up front. Measured here: `merge --abort` restores an empty porcelain at BOTH local
    sites, so `--apply` ABORTS rather than leaving the tree conflicted — a conflicted tree left
    behind would block the operator's next `git` operation for no gain, since the full capture
    is already in the verdict.
    """
    monkeypatch.setattr(pm, "_land_capture_conflict",
                        lambda site, root: {"site": site, "unmerged_paths": ["skills/x.py"],
                                            "porcelain_v2": ["u ..."], "merge_head": "abc",
                                            "auto_resolved": False,
                                            "recovery": pm.LAND_CONFLICT_RECOVERY[site]})
    monkeypatch.setattr(pm, "_land_abort_merge",
                        lambda root: {"aborted": True, "tree_clean": True, "detail": None})

    cases = {}

    # 1 — L1 down-merge conflict.
    r1 = FakeRunner({"merge|--no-ff": _R(1, "", "CONFLICT")})
    cases["L1"] = pm._land_l1_down_merge(_ctx(repo, r1))

    # 2 — L2 merge conflict.
    r2 = FakeRunner({"merge|--no-ff|--no-commit": _R(1, "", "CONFLICT")})
    cases["L2"] = pm._land_l2_merge(_ctx(repo, r2))

    # 3 — L6 push rejection (PRE-outward-write).
    r3 = FakeRunner({"push|origin": _R(1, "", "rejected")})
    cases["L6"] = pm._land_l6_push_one(_ctx(repo, r3))

    # 4 — L16 push rejection (POST-outward-write).
    r4 = FakeRunner({"push|origin": _R(1, "", "rejected"), "diff|--cached": _R(1)})
    cases["L16"] = pm._land_l16_commit_and_push_two(_ctx(repo, r4))

    # 5 — target-moved staleness, halting BEFORE the merge is attempted.
    rel = Path("docs/plans") / PLAN_ID
    stale = {"schema": pm.LAND_SCHEMA_DECISION, "manifest_digest": "sha256:" + "0" * 64,
             "plan_id": PLAN_ID, "authored_by": "lander", "summary": "s",
             "upstream_writes": [], "steps": {k: "enable" for k in pm.LAND_STEPS}}
    cases["stale"] = pm._land_repreview_or_halt(rel, stale)

    assert len(cases) == 5, "the matrix covers FIVE cases"

    for k in ("L1", "L2", "L6", "L16"):
        assert cases[k]["verdict"] == "fail", f"{k} must halt"
        assert cases[k]["halting"] is True
        assert cases[k]["journal"] in pm.LAND_CONFLICT_STATES, (
            f"{k} must record ITS OWN journal state, not a generic one")
    assert cases["stale"]["proceed"] is False and cases["stale"]["stale"] is True

    # FOUR DISTINCT journal states — one per site.
    states = {cases[k]["journal"] for k in ("L1", "L2", "L6", "L16")}
    assert len(states) == 4, f"one state per site, got {states}"

    # THE RECOVERIES ARE NOT UNIFORM, and L16's is the one that differs in kind.
    assert "merge --abort" in cases["L1"]["detail"]["conflict"]["recovery"]
    assert "merge --abort" in cases["L2"]["detail"]["conflict"]["recovery"]
    assert "RE-VALIDATE" in cases["L6"]["detail"]["recovery"]
    assert "NEVER REVERT" in cases["L16"]["detail"]["recovery"]
    assert cases["L16"]["detail"]["post_outward_write"] is True
    assert "merge --abort" not in cases["L16"]["detail"]["recovery"], (
        "abort is the WRONG recovery post-outward-write — comments posted, beads closed, "
        "`status: complete` written")

    # ABORT-VS-LEAVE, DECIDED EMPIRICALLY: the two local sites restore the tree.
    for k in ("L1", "L2"):
        assert cases[k]["detail"]["restore"]["tree_clean"] is True

    # And no site auto-resolved.
    for k in ("L1", "L2"):
        assert cases[k]["detail"]["conflict"]["auto_resolved"] is False


# -- the executor ---------------------------------------------------------------------------

def test_executor_halts_before_any_destructive_stage(repo, monkeypatch):
    """REQ-LAND-020 fail-closed. An unverified L7 write aborts BEFORE L12 cascade-close is
    reachable — the ordering is what makes the guarantee, not a check inside L12."""
    body = repo / "b.md"; body.write_text("intended\n", encoding="utf-8")
    dec = {"upstream_writes": [{"issue": "301", "action": "comment", "body_path": str(body)}]}
    monkeypatch.setattr(pm, "_validate_merged", lambda pd: {"status": "pass", "engine": "x"})
    monkeypatch.setattr(pm, "_landing_lock_acquire", lambda p: {"acquired": True})
    monkeypatch.setattr(pm, "_landing_lock_release", lambda p, f=False: {"released": True})
    r = FakeRunner({"issue|view": _R(0, json.dumps({"state": "OPEN", "comments": []})),
                    "rev-parse|HEAD^{tree}": _R(0, "t\n"),
                    f"rev-parse|{PLAN_ID}-execute^{{tree}}": _R(0, "t\n")})
    out = pm._land_execute(_ctx(repo, r, decision=dec))
    assert out["halted"] is True
    assert out["at"] == "l7_reconcile_writes"
    assert "l12_close_cascade" not in out["results"][-1]["step"]
    steps = [x["step"] for x in out["results"]]
    assert "l12_close_cascade" not in steps, (
        "the first unverified write must abort BEFORE any destructive follow-on stage")


def test_executor_table_is_the_declared_order(repo):
    """The executor's order IS REQ-LAND-004's order — asserted, not assumed."""
    keys = [k for k, _ in pm.LAND_EXECUTOR]
    idx = {k: i for i, k in enumerate(pm.LAND_STEPS)}
    assert keys == sorted(keys, key=lambda k: idx[k]), "the executor reorders the L-steps"
    for k, fname in pm.LAND_EXECUTOR:
        assert callable(globals_of_pm(fname)), f"{fname} is not callable"


def globals_of_pm(name):
    return getattr(pm, name, None)


def test_a_skipped_step_is_surfaced_never_silent(repo, monkeypatch):
    """REQ-LAND-002. Every skip is surfaced, so 'the landing did less than you think' is
    never silent."""
    monkeypatch.setattr(pm, "_validate_merged", lambda pd: {"status": "pass", "engine": "x"})
    monkeypatch.setattr(pm, "_landing_lock_acquire", lambda p: {"acquired": True})
    monkeypatch.setattr(pm, "_landing_lock_release", lambda p, f=False: {"released": True})
    monkeypatch.setattr(pm, "_worktree_teardown", _teardown_ok)
    # Stub the close chain: this test isolates SKIP SURFACING, and an unstubbed
    # pour-fidelity legitimately halts at L14 on a fixture with no real beads — which the
    # guard below caught, rather than letting the test pass vacuously.
    monkeypatch.setattr(pm, "_land_l8_to_l15_close_chain",
                        lambda ctx: [_step_ok("l8_close_chain_head")])
    monkeypatch.setattr(pm, "_land_l12_close_cascade",
                        lambda ctx: _step_ok("l12_close_cascade"))
    monkeypatch.setattr(pm, "_land_l13_l15_finish",
                        lambda ctx: [_step_ok("l15_update_status", journal="L_CLOSED")])
    steps = {k: "enable" for k in pm.LAND_STEPS}
    steps["l18_prune"] = "skip:provenance-unknown"
    r = FakeRunner({"rev-parse|HEAD^{tree}": _R(0, "t\n"),
                    f"rev-parse|{PLAN_ID}-execute^{{tree}}": _R(0, "t\n"),
                    "status|--porcelain": _R(0, ""), "rev-list|--count": _R(0, "0\n"),
                    "diff|--cached": _R(0)})
    out = pm._land_execute(_ctx(repo, r, steps=steps))
    steps_run = [x["step"] for x in out["results"]]
    assert not out["halted"] or "l18_prune" in steps_run, (
        f"the executor halted at {out.get('at')} before reaching the skipped step, so this "
        f"test would pass vacuously against an executor that never surfaces a skip at all. "
        f"Steps reached: {steps_run}")
    skipped = [x for x in out["results"] if x.get("detail", {}).get("skipped")]
    assert skipped, "the skip was silent"
    assert "provenance-unknown" in skipped[0]["reason"]


def test_change_validation_rows_registered():
    """SC35 / Issue 5.3. The three new test files are registered under ASSERTED ROW IDS.

    A BARE GLOB MATCH PROVES NOTHING: `skills/yf-plan/scripts/**` already selects all three,
    so a scoped run would look green while no row actually names them. The assertion is that
    each file has its OWN id, that the id appears in BOTH tiers, and that the trigger scope
    maps the file to that id BY NAME.
    """
    root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True).stdout.strip())
    manifest = (root / "CHANGE-VALIDATION.md").read_text(encoding="utf-8")

    expected = {
        "skills/yf-plan/scripts/test_land_manifest.py": "uv-yf-land-manifest",
        "skills/yf-plan/scripts/test_lander_agent_contract.py": "uv-yf-lander-contract",
        "skills/yf-plan/scripts/test_land_apply.py": "uv-yf-land-apply",
    }

    fast = manifest[manifest.index("### fast"):manifest.index("### full")]
    full = manifest[manifest.index("### full"):manifest.index("## 2.")]
    scope = manifest[manifest.index("## 3."):]

    for path, rid in expected.items():
        assert (root / path).is_file(), f"{path} does not exist"
        assert f"`{rid}`" in fast, f"{rid} is not a FAST-tier row"
        assert path in fast, f"the {rid} row does not target {path} explicitly"
        assert path in full, f"{path} has no FULL-tier row"
        # The trigger scope must map the FILE to the ID BY NAME — not merely be covered by
        # the pre-existing broad `skills/yf-plan/scripts/**` glob.
        line = next((ln for ln in scope.splitlines()
                     if ln.startswith("|") and f"`{path}`" in ln), None)
        assert line, f"no trigger-scope row names {path}"
        assert f"`{rid}`" in line, f"the trigger-scope row for {path} does not name {rid}"


def test_each_step_invokes_the_RIGHT_EXECUTABLE(repo, monkeypatch):
    """THE TEST THAT WOULD HAVE CAUGHT THE BUG THE REHEARSAL FOUND.

    `ctx.run` used to wrap `_run_git`, so every step's argv was handed to **git**: L7 ran
    `git issue comment`, L17 ran `git push --issues`, L19 ran `git self install`. All 38
    Tier-1 tests passed, because the injected fake returned 0 for any argv it did not
    recognise — a fake that answers everything cannot witness the wrong executable.

    This asserts the PROGRAM, not the arguments. It is the cheap check that closes the gap
    between "a mock answered" and "a process ran".
    """
    body = repo / "b.md"; body.write_text("x\n", encoding="utf-8")
    monkeypatch.setattr(pm, "_worktree_teardown", _teardown_ok)
    monkeypatch.setattr(pm, "_land_changed_set", lambda root=None: ["skills/a.py"])

    checks = [
        (pm._land_l1_down_merge,   {},                                          {"git"}),
        (pm._land_l2_merge,        {},                                          {"git"}),
        (pm._land_l6_push_one,     {},                                          {"git"}),
        (pm._land_l7_reconcile_writes,
         {"upstream_writes": [{"issue": "301", "action": "comment",
                               "body_path": str(body)}]},                       {"gh"}),
        (pm._land_l16_commit_and_push_two, {},                                  {"git"}),
        # L18 invokes NOTHING through `ctx.run` (Issue 2.2): its only process work is the
        # branch delete, and that is DELEGATED to `_worktree_teardown`, which uses `_run_git`
        # directly. The empty set is the assertion, not an omission — a `{"git"}` expectation
        # here would only be satisfiable by restoring the duplicate delete this plan removed.
        (pm._land_l18_prune,       {},                                          set()),
        (pm._land_l19_redeploy,    {},                                          {"yf"}),
    ]
    for fn, dec, want in checks:
        r = FakeRunner({"issue|view": _R(0, json.dumps(
            {"state": "OPEN", "comments": [{"body": "x"}]}))})
        fn(_ctx(repo, r, decision=dec or None))
        got = r.programs()
        assert got == want, (
            f"{fn.__name__} invoked {got or 'nothing'}, expected {want}. Running the wrong "
            f"executable is invisible to a fake that answers any argv.")

    # L17 shells out to `uv run <upstream.py>`, not to git and not to a prose skill.
    g = repo / "docs" / "plans" / PLAN_ID / "assets" / "upstream-grant.md"
    g.parent.mkdir(parents=True, exist_ok=True)
    g.write_text("authorized: yf-aaa\n", encoding="utf-8")
    r17 = FakeRunner()
    pm._land_l17_residual_mirroring(_ctx(
        repo, r17, decision={"residual_bead_groups": [{"beads": ["yf-aaa"]}]}))
    assert r17.programs() == {"uv"}, (
        f"L17 invoked {r17.programs()}; it must call `uv run upstream.py push` CONCRETELY")
    assert r17.saw("run", "push", "--issues", "--apply")


# =========================================================================================
# EPIC 6 — the rehearsal (Issue 6.1), read from its COMMISSIONED artifact
# =========================================================================================

def _rehearsal_record():
    """The record the rehearsal WROTE. Read, never invented.

    Resolved from either checkout for the address-space reason recorded on
    `test_cited_figures_match_repository`: the artifact is a plan-folder file and the tests
    are code, so before the landing merges them they live in different checkouts.
    """
    root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True).stdout.strip())
    rel = Path("docs/plans/plan-060-james-dixson-6a6ac9/assets/rehearsal-record.json")
    cands = [root / rel]
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute",
                             "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    if common and Path(common).name == ".git":
        cands.append(Path(common).parent / rel)
    for c in cands:
        if c.is_file():
            return json.loads(c.read_text(encoding="utf-8"))
    return None


def test_rehearsal_origin_is_not_this_repo():
    """SC36 / Issue 6.1. The rehearsal ran against a SANDBOX CLONE with a FAKE ORIGIN.

    A verb whose first real execution is the landing of the plan that built it has no rollback
    if it is wrong. This asserts the origin was a throwaway local bare repo — and, crucially,
    that it was NOT this repository or any remote of it.
    """
    rec = _rehearsal_record()
    assert rec is not None, "no rehearsal record — the rehearsal was never run"
    assert rec["schema"] == "yf-plan/landing-rehearsal@1"
    assert rec["origin_is_local_sandbox"] is True
    origin = rec["origin_url"]
    assert origin.endswith("fake-origin.git"), origin
    assert "yoshiko-flow" not in origin, "the rehearsal targeted the LIVE repository"
    assert "github.com" not in origin and "://" not in origin, (
        "the rehearsal origin must be a local path, not a network remote")
    assert rec["plan_id"] != "plan-060-james-dixson-6a6ac9", (
        "the rehearsal must not be this plan's OWN landing")


def test_rehearsal_reached_terminal_state():
    """SC36b / Issue 6.1. The rehearsal drove the landing to a GREEN TERMINAL journal state,
    executing every enabled step.

    A REHEARSAL THAT HALTED AT L2 MUST NOT SATISFY R1's MITIGATION. That is the whole point of
    this criterion, and it is why the record carries the terminal state by name rather than a
    bare success flag.
    """
    rec = _rehearsal_record()
    assert rec is not None, "no rehearsal record — the rehearsal was never run"
    assert rec["halted"] is False, f"the rehearsal HALTED at {rec.get('halted_at')}"
    assert rec["terminal_journal_state"] == "L_DONE"
    assert rec["reached_terminal_state"] is True
    assert all(v == "pass" for v in rec["verdicts"].values()), (
        f"non-passing steps: {[k for k, v in rec['verdicts'].items() if v != 'pass']}")

    # EVERY ENABLED STEP RAN. The stubbed and skipped sets are declared in the record, so a
    # rehearsal that quietly executed less than it claims is visible rather than plausible.
    executed = set(rec["steps_executed"])
    for key in ("l1_down_merge", "l2_merge", "l6_push_one", "l16_commit_and_push_two",
                "l18_prune"):
        assert key in executed, f"{key} never ran — the rehearsal did not exercise the landing"
    assert "l19_redeploy" in executed, "the skipped step must still be REPORTED, not omitted"

    # The push actually reached the fake origin — the rehearsal moved real refs.
    assert any("landed" in p for p in rec["pushed_paths_on_fake_origin"]), (
        "nothing reached the fake origin; the pushes were not real")


def test_runbook_covers_every_journal_state():
    """SC38 / Issue 6.3. The runbook names EVERY enumerated journal state.

    Derived from `LAND_JOURNAL_STATES`, never from a hand-written list — a hand-written list
    is a second enumeration that can drift from the first, which is the exact defect
    `okf_hygiene`'s five-state model suffered and that `spec/landing.md` exists to prevent.
    """
    root = Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True).stdout.strip())
    rel = Path("docs/plans/plan-060-james-dixson-6a6ac9/assets/landing-runbook.md")
    cands = [root / rel]
    common = subprocess.run(["git", "rev-parse", "--path-format=absolute",
                             "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    if common and Path(common).name == ".git":
        cands.append(Path(common).parent / rel)
    rb = next((c for c in cands if c.is_file()), None)
    assert rb is not None, "no landing runbook"
    text = rb.read_text(encoding="utf-8")

    missing = [st for st in pm.LAND_JOURNAL_STATES if st not in text]
    assert not missing, f"the runbook does not name journal state(s): {missing}"

    # And each CONFLICT state must carry its recovery, since those are the four that differ.
    for st in pm.LAND_CONFLICT_STATES:
        i = text.index(st)
        row = text[i:text.index("\n", i)]
        assert row.count("|") >= 2, f"{st} has no recovery column in the runbook"
    assert "NEVER REVERT" in text, "the L16 recovery's defining constraint is missing"
    assert "exit 3" in text and "detection" in text.lower()


# =========================================================================================
# plan-062 — THE SEAM. `land --apply` must REACH `_land_execute` (REQ-LAND-028, #327)
# =========================================================================================
#
# WHY THESE TESTS EXIST AT ALL. `_land_execute` drives all fifteen `LAND_EXECUTOR` steps,
# advances the journal, is fail-closed, and was covered by 43 passing tests above — while
# having exactly ONE occurrence in `plan_manager.py`: its own `def`. `--apply` returned an
# unconditional "the --apply executor is not implemented" stub. Every test in this file drove
# `_land_execute` DIRECTLY, so no test could observe that nothing called it. That is the #263
# vacuous-check class at the HARNESS level: a suite passing comprehensively over an engine no
# entry point invokes.
#
# THE MECHANISM IS DELIBERATE AND ADDS NO PRODUCTION-REACHABLE BYPASS (EXP-001, #304). The
# defect sits BELOW the tty gate, so a real pty is not required to observe it. Of the four
# mechanisms measured, a `YF_LAND*` test env flag and wiring the dormant `allow_list` both
# create a bypass reachable in production; monkeypatching the gate in-process creates none —
# the patch exists only inside the test process. `test_tty_refusal_exits_three_not_one_or_two`
# above is retained UNMODIFIED as the gate-closed half's real-process coverage, and
# `test_ast_gate_called_before_any_write` below closes the one gap a gate-stubbed test cannot
# see: that the gate is still CALLED.


def _seam_decision(rel):
    """A decision conformant against RE-DERIVED reality, so nothing halts on binding."""
    manifest = pm._land_manifest(rel)
    return _decision(pm._land_digest(manifest["facts"]))


def _open_the_gate(monkeypatch):
    """Stub the two pre-executor refusals, and ONLY those two.

    Neither is the subject: REQ-LAND-010's checkout assertion and REQ-LAND-014's tty gate both
    sit ABOVE the seam, and both are covered elsewhere in this file. Stubbing anything BELOW
    the seam would be stubbing the thing under test.
    """
    monkeypatch.setattr(pm, "_land_assert_primary_checkout",
                        lambda: {"ok": True, "cwd": ".", "primary": "."})
    monkeypatch.setattr(pm, "_land_tty_gate",
                        lambda allow_list=None: {"allowed": True, "reason": "stubbed in-test",
                                                 "route_record": {"tty": "/dev/ttys999"}})


def _run_land_apply(repo, tmp_path, monkeypatch, decision=None, execute_spy=None):
    """Drive the REAL click command in-process and return (exit_code, envelope)."""
    from click.testing import CliRunner

    rel = Path("docs/plans") / PLAN_ID
    _open_the_gate(monkeypatch)
    if execute_spy is not None:
        monkeypatch.setattr(pm, "_land_execute", execute_spy)

    # OUTSIDE THE TREE ON PURPOSE. A decision file written inside the repo is an untracked
    # path that halts the landing at L16, past the irreversible boundary.
    dpath = tmp_path / "decision.json"
    dpath.write_text(json.dumps(decision or _seam_decision(rel)), encoding="utf-8")

    res = CliRunner().invoke(
        pm.cli, ["land", "--apply", str(dpath), str(rel)], catch_exceptions=False)
    try:
        env = json.loads(res.output)
    except json.JSONDecodeError:
        env = {"_raw": res.output}
    return res.exit_code, env


def test_seam_reaches_executor(repo, tmp_path, monkeypatch):
    """SC1 / Issue 2.0 / REQ-LAND-028. `--apply` REACHES `_land_execute`.

    THE ASSERTION IS ABOUT THE CALL, NOT ABOUT THE LANDING. What must be true is that the CLI
    entry point invokes the executor and that the executor genuinely started — `l0_lock_acquire`
    is the first row of `LAND_EXECUTOR`, so its presence in the executed steps is the earliest
    observable proof that control crossed the seam. Whether the landing then succeeds is a
    different question, tested by the fifteen step tests above.

    AUTHORED BEFORE THE WIRING, AND RECORDED AS FAILING AGAINST THE UNWIRED BUILD. A test
    written after its fix proves only that the fix is self-consistent. Against the shipped
    stub this asserted `exit 2` / verdict `inconclusive` / "executor is not implemented" and
    reached no step at all.
    """
    seen: dict = {}

    def spy(ctx, resume_from=None):
        seen["called"] = True
        seen["ctx"] = ctx
        seen["resume_from"] = resume_from
        return {"halted": False, "results": [_step_ok("l0_lock_acquire", journal="L_LOCKED")],
                "journal_phase": "L_LOCKED", "terminal": False,
                "reached_terminal_state": False,
                "steps_executed": ["l0_lock_acquire"]}

    code, env = _run_land_apply(repo, tmp_path, monkeypatch, execute_spy=spy)

    assert seen.get("called"), (
        "`land --apply` did not reach `_land_execute` — the CLI entry point is disconnected "
        "from the engine (REQ-LAND-028). This is the #327 defect: a fully implemented, fully "
        "tested executor that no entry point invokes.")
    assert isinstance(seen["ctx"], pm.LandingContext), (
        "the seam must hand the executor a real LandingContext, assembled from re-derived "
        "facts (REQ-LAND-002)")
    assert seen["ctx"].plan_id == PLAN_ID
    assert "l0_lock_acquire" in (env.get("steps_executed") or
                                [r["step"] for r in env.get("results", [])]), (
        f"the executor was called but its first step is not reported: {env}")
    assert "not implemented" not in json.dumps(env), (
        "the unconditional stub verdict is still being emitted")
    assert code in (0, 1, 2), f"unexpected exit {code}: {env}"


def test_seam_passes_the_resume_phase_through(repo, tmp_path, monkeypatch):
    """The seam is not merely A call — it must carry the journal's resume point.

    A seam that always calls `_land_execute(ctx)` with no `resume_from` would satisfy
    `test_seam_reaches_executor` while making Epic 1's whole resume fix unreachable: every
    re-invocation would restart at L0 and re-execute `l6_push_one` and `l7_reconcile_writes`.
    The two defects compose, so the test for the second is separate from the test for the
    first.
    """
    rel = Path("docs/plans") / PLAN_ID
    j = pm.LandingJournal(repo, PLAN_ID)
    j.write("L_RECONCILED", note="a prior --apply halted here")

    seen: dict = {}

    def spy(ctx, resume_from=None):
        seen["resume_from"] = resume_from
        return {"halted": False, "results": [], "journal_phase": "L_RECONCILED",
                "terminal": False, "reached_terminal_state": False, "steps_executed": []}

    _run_land_apply(repo, tmp_path, monkeypatch, execute_spy=spy)
    assert seen.get("resume_from") == "L_RECONCILED", (
        f"the seam discarded the journal's recorded phase: resume_from={seen.get('resume_from')!r}. "
        "A resume that restarts at L0 re-posts every reconcile comment.")


def test_inconclusive_not_laundered(repo, tmp_path, monkeypatch):
    """SC12 / Issues 2.2 + 4.4 / REQ-LAND-012. `inconclusive` is NEVER coerced.

    L8's and L12's `inconclusive` results are explicitly NON-HALTING, so a landing can reach
    `L_DONE` while carrying one. A two-valued wrapper (`halted -> fail`, else `pass`) launders
    that into a green landing — which is exactly the coercion REQ-LAND-012 forbids, and
    without this test Issue 2.2's three-valued derivation is unobservable.
    """
    def spy(ctx, resume_from=None):
        return {"halted": False,
                "results": [_step_ok("l0_lock_acquire", journal="L_LOCKED"),
                            {"step": "l12_close_cascade", "verdict": "inconclusive",
                             "reason": "pour fidelity could not be measured",
                             "journal": None, "halting": False, "detail": {}}],
                "journal_phase": "L_DONE", "terminal": True,
                "reached_terminal_state": True,
                "steps_executed": ["l0_lock_acquire", "l12_close_cascade"]}

    called: dict = {}
    _spy = spy

    def spy(ctx, resume_from=None):          # noqa: F811 — wraps to record the call
        called["yes"] = True
        return _spy(ctx, resume_from)

    code, env = _run_land_apply(repo, tmp_path, monkeypatch, execute_spy=spy)

    # THE VACUITY GUARD, AND IT IS NOT DECORATION. Measured against the unwired build this
    # test PASSED — because the stub `land_cmd` emitted verdict `inconclusive` / exit 2 all
    # on its own, without ever calling the executor. A test that cannot tell "derived
    # three-valued from the executor's results" from "never reached the executor" is the
    # #263 vacuous check, in the very file written to close it.
    assert called.get("yes"), (
        "`_land_execute` was never called, so this test measured the stub's own "
        "`inconclusive`, not a verdict DERIVED from the executor's results")
    assert env.get("verdict") == "inconclusive", (
        f"a non-halting `inconclusive` reaching L_DONE was laundered into "
        f"{env.get('verdict')!r} — REQ-LAND-012 forbids the coercion")
    assert code == 2, f"an inconclusive verdict must exit 2, got {code}"


def test_ast_gate_called_before_any_write(repo):
    """SC9 / Issue 4.3. `land_cmd` CALLS `_land_tty_gate`, asserted at the SOURCE level.

    THIS IS A FUTURE REGRESSION GUARD, NOT EVIDENCE ABOUT THE PRESENT DEFECT. `land_cmd`
    already calls the gate, so this passes the moment it is written. It exists because the
    seam tests above monkeypatch the gate open: a gate-stubbed test cannot see the gate being
    DELETED, and the source is the only place that fact is observable.

    The file already uses `ast` this way for the two shell-out absence checks near the top.
    """
    import ast as _ast

    # THE MODULE SOURCE, not `inspect.getsource(pm.land_cmd)`. `land_cmd` is a click
    # `Command` object, not a function — `inspect` raises `TypeError` on it, which is how
    # this test first failed. Parsing the file is also the stronger form: it reads what a
    # reviewer reads, with no decorator indirection in between.
    # RAW source, not `_code_only`. This check looks for CALL nodes, and a docstring is a
    # `Constant` — it can never be mistaken for a call, so the prose-vs-code distinction
    # `_code_only` exists to draw does not arise here. (It is also unusable module-wide: it
    # unparses a docstring-only function into a `def` with an empty body.)
    tree_all = _ast.parse(_PM.read_text(encoding="utf-8"))
    fn = next((n for n in _ast.walk(tree_all)
               if isinstance(n, _ast.FunctionDef) and n.name == "land_cmd"), None)
    assert fn is not None, "no `land_cmd` function in plan_manager.py"
    calls = [n for n in _ast.walk(fn)
             if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Name)]
    names = [n.func.id for n in calls]
    assert "_land_tty_gate" in names, (
        "`land_cmd` does not call `_land_tty_gate` — the outward-write consent gate can be "
        "deleted and every gate-stubbed test above would still pass (REQ-LAND-014)")
    assert "_land_assert_primary_checkout" in names, (
        "`land_cmd` does not assert the primary checkout (REQ-LAND-010)")

    # ORDER, not merely presence: the gate must precede the executor call, or a refusal could
    # be preceded by a write.
    order = {}
    for n in calls:
        order.setdefault(n.func.id, n.lineno)
    assert order["_land_assert_primary_checkout"] < order["_land_tty_gate"], (
        "REQ-LAND-010's checkout assertion must run BEFORE the tty gate")
    if "_land_execute" in order:
        assert order["_land_tty_gate"] < order["_land_execute"], (
            "the tty gate must be called BEFORE `_land_execute` — otherwise a refusal can be "
            "preceded by a write")


def test_no_test_only_bypass_was_introduced():
    """SC11. No `YF_LAND`-prefixed environment escape exists in the production module.

    EXP-001 measured this alternative and rejected it: an env-var gate bypass is
    PRODUCTION-REACHABLE — anything that can set an environment variable can open the consent
    gate, and #293 is already an instance of an executing agent closing that gate by asserting
    its own authorization. The in-process monkeypatch above cannot escape the test process.
    """
    src = _PM.read_text(encoding="utf-8")
    assert "YF_LAND" not in src, (
        "a `YF_LAND*` environment escape appears in plan_manager.py — that is a "
        "production-reachable tty-gate bypass, which EXP-001 rejected on exactly this ground")


# =========================================================================================
# plan-062 — THE RESUME. A resume must not re-execute completed steps (REQ-LAND-029, #327)
# =========================================================================================

def _resume_ctx(repo, monkeypatch, phase):
    """A context whose journal is at `phase`, with every step stubbed to a recording no-op.

    THE STEPS ARE STUBBED BECAUSE THE SUBJECT IS THE SKIP DECISION, NOT THE STEPS. Each stub
    records that it ran, so "did not re-execute" is measured by an ABSENCE FROM A RECORD
    rather than inferred from a green result — an unstubbed step that halts early would make
    every "did not run" assertion pass vacuously.
    """
    ran: list[str] = []

    def _mk(key, journal):
        def _f(ctx):
            ran.append(key)
            return _step_ok(key, journal=journal)
        return _f

    for key, fname in pm.LAND_EXECUTOR:
        j = pm.LAND_STEP_JOURNAL.get(key)
        if fname == "_land_l8_to_l15_close_chain":
            def _chain(ctx, _k=key):
                ran.append(_k)
                return [_step_ok(_k)]
            monkeypatch.setattr(pm, fname, _chain)
        elif fname == "_land_l13_l15_finish":
            def _fin(ctx, _k=key, _j=j):
                ran.append(_k)
                return [_step_ok(_k, journal=_j)]
            monkeypatch.setattr(pm, fname, _fin)
        else:
            monkeypatch.setattr(pm, fname, _mk(key, j))

    j = pm.LandingJournal(repo, PLAN_ID)
    j.write(phase, note="a prior --apply halted here")
    return _ctx(repo, FakeRunner()), ran


def test_resume_skips_completed(repo, monkeypatch):
    """SC4 / Issue 4.1 / REQ-LAND-029. REQ-LAND-011's `Verification:` names THIS test.

    After a halt at L17, a resume must execute NEITHER `l6_push_one` NOR
    `l7_reconcile_writes` — the two irreversible outward writes. Measured before the fix, a
    resume from that point re-executed all fifteen steps from L0, re-pushing and re-posting
    every reconcile comment.

    AND IT MUST STILL EXECUTE `l0_lock_acquire`. The lock is released at L4, not at the end,
    so a uniform skip rule would run the remaining steps holding no lock and then `unlink` a
    lock it never acquired — `_landing_lock_release` is keyed on plan+host, not PID, so that
    unlink would steal a concurrent landing's lock. A resume that silently skipped L0 would
    look correct here and be unsafe.
    """
    ctx, ran = _resume_ctx(repo, monkeypatch, "L_MIRRORED")
    out = pm._land_execute(ctx, resume_from="L_MIRRORED")

    assert "l6_push_one" not in ran, "a resume RE-PUSHED — the irreversible L6 write repeated"
    assert "l7_reconcile_writes" not in ran, (
        "a resume RE-POSTED the reconcile comments — the irreversible L7 write repeated")
    assert "l0_lock_acquire" in ran, (
        "the resume skipped `l0_lock_acquire`, so the rest of the landing ran holding no "
        "lock and would `unlink` a lock it never acquired (the L4-release asymmetry)")
    assert "l18_prune" in ran, (
        "the resume skipped work that had NOT completed — L18 follows L17 (L_MIRRORED), so "
        "it must still run. Without this the test would pass against an executor that skips "
        "everything.")

    resumed = [r["step"] for r in out["results"] if r.get("detail", {}).get("resumed")]
    assert "l6_push_one" in resumed and "l7_reconcile_writes" in resumed, (
        f"a skipped step must be SURFACED with an explicit `resumed` marker, never a silent "
        f"absence (REQ-LAND-029). Marked: {resumed}")


def test_resume_forward_resolution(repo, monkeypatch):
    """SC4b / Issue 4.2 / REQ-LAND-029. The three unjournaled steps resolve FORWARD.

    `l3_validate_merged`, `l8_close_chain_head` and `l12_close_cascade` have no entry in
    `LAND_STEP_JOURNAL`, so whether they are "done" must be borrowed from a neighbour. Taking
    the PRECEDING neighbour is unsafe, and the failure is concrete rather than theoretical:
    after a halt at `l3_validate_merged` the preceding state `L_MERGED_UNCOMMITTED` is ALREADY
    reached, so a backward scan marks l3 done and SKIPS VALIDATION OF THE MERGED TREE — the
    one check standing between a merge and a push.

    These are the two cases a backward scan would silently break, which is why they are tested
    separately from the L17 case above.
    """
    # -- halt at l3: L_MERGED_UNCOMMITTED is reached, but l3 itself did NOT complete.
    ctx, ran = _resume_ctx(repo, monkeypatch, "L_MERGED_UNCOMMITTED")
    pm._land_execute(ctx, resume_from="L_MERGED_UNCOMMITTED")
    assert "l3_validate_merged" in ran, (
        "BACKWARD RESOLUTION: `l3_validate_merged` was skipped because its PREDECESSOR's "
        "journal state was reached. The merged tree would be pushed unvalidated.")
    assert "l2_merge" not in ran, "L2 genuinely completed (it wrote L_MERGED_UNCOMMITTED)"

    # -- halt at l8: the close chain is unjournaled and its successor L13 wrote nothing yet.
    ctx2, ran2 = _resume_ctx(repo, monkeypatch, "L_RECONCILED")
    pm._land_execute(ctx2, resume_from="L_RECONCILED")
    assert "l8_close_chain_head" in ran2, (
        "BACKWARD RESOLUTION: the close chain was skipped because L7's `L_RECONCILED` was "
        "reached — but the chain itself never ran.")
    assert "l12_close_cascade" in ran2, "l12 is unjournaled too and had not run"
    assert "l7_reconcile_writes" not in ran2, "L7 genuinely completed (it wrote L_RECONCILED)"


def test_resume_done_set_is_step_keys_not_journal_states(repo):
    """The unit under the two tests above, asserted directly.

    The original defect was a TYPE CONFUSION with no type error: `done` was built from journal
    PHASES (`L_PUSHED_1`, ...), named as though it held executor STEP KEYS (`l6_push_one`,
    ...), and then never read — so the mistake was invisible in both directions. Asserting the
    set's MEMBERSHIP VOCABULARY is what makes a regression to phases fail loudly.
    """
    done = pm._land_resume_done("L_MIRRORED")
    keys = {k for k, _ in pm.LAND_EXECUTOR}
    assert done, "a resume from L_MIRRORED must mark earlier steps done"
    assert done <= keys, (
        f"`done` contains members that are not executor step keys: {sorted(done - keys)}. "
        "The journal's phase vocabulary and the executor's key vocabulary are different sets.")
    assert not (done & set(pm.LAND_PROGRESS_ORDER)), "`done` must not hold journal phases"
    assert "l0_lock_acquire" not in done, "L0 is exempt from skipping"

    assert pm._land_resume_done(None) == set(), "no resume point means nothing is done"
    assert pm._land_resume_done("L_NOT_A_STATE") == set(), "an unknown phase claims nothing"

    # A trailing unjournaled step is never marked done — there is no successor to borrow from.
    keys_list = [k for k, _ in pm.LAND_EXECUTOR]
    trailing = [k for k in keys_list if k not in pm.LAND_STEP_JOURNAL
                and not any(x in pm.LAND_STEP_JOURNAL for x in keys_list[keys_list.index(k) + 1:])]
    for k in trailing:
        assert k not in pm._land_resume_done(pm.LAND_PROGRESS_ORDER[-1]), (
            f"{k} has no journaled successor, so nothing can establish that it ran")


# =========================================================================================
# SC1 / REQ-LAND-030 — a step that RAISES becomes a halting envelope, not a traceback
# =========================================================================================

def test_step_exception_becomes_halting(repo, monkeypatch):
    """REQ-LAND-030 (#340). An exception raised by a `LAND_EXECUTOR` step is caught at the
    dispatch site and becomes a HALTING `inconclusive` row with NO journal advance.

    Four assertions, each pinning something that was wrong once:

    1. The envelope exists at all. plan-062's landing died at L18 on a bare `TypeError`
       with no envelope, no halt class and no remediation.
    2. `halted` and the halt point. An `inconclusive` row FALLS THROUGH the loop's own
       `verdict == "fail" and halting` predicate, so the handler must return the halted
       envelope DIRECTLY. Asserting only `verdict == "inconclusive"` would pass against a
       fall-through, which for an early step walks past a crash into destructive work.
    3. NO STEP AFTER THE RAISER RAN. This is the fall-through detector.
    4. The journal did NOT advance past the raising step, and the reason SAYS SO — a resume
       re-enters this same step and raises again (Issue 1.2). That is correct: advancing the
       journal would manufacture the evidence `_land_resume_done` exists to refuse.
    """
    monkeypatch.setattr(pm, "_landing_lock_acquire", lambda p: {"acquired": True})

    boom_key = "l3_validate_merged"

    def _boom(ctx):
        raise TypeError("_worktree_teardown() takes 1 positional argument but 2 were given")

    monkeypatch.setattr(pm, "_land_l3_validate_merged", _boom)
    r = FakeRunner({"rev-parse|HEAD^{tree}": _R(0, "t\n"),
                    f"rev-parse|{PLAN_ID}-execute^{{tree}}": _R(0, "t\n")})
    ctx = _ctx(repo, r)
    out = pm._land_execute(ctx)

    assert out["halted"] is True, "a raising step must halt the landing"
    assert out["at"] == boom_key, f"halted at {out['at']!r}, expected {boom_key!r}"

    row = out["results"][-1]
    assert row["step"] == boom_key
    assert row["verdict"] == "inconclusive", (
        "a step that raised established NOTHING; `fail` would assert a measurement that "
        "never happened and `pass` would assert its opposite")
    assert row["halting"] is True
    assert row["journal"] is None, "the journal must NOT advance past a step that raised"
    assert row["detail"]["exception"] == "TypeError"
    assert "TypeError" in row["detail"]["traceback"]
    assert "RESUME WILL RE-ENTER THIS SAME STEP" in row["reason"].upper(), (
        "Issue 1.2: the reason must RECORD that a resume re-enters the same step and raises "
        "again, so the behaviour is read as correct rather than engineered around")

    steps_run = [x["step"] for x in out["results"]]
    assert steps_run[-1] == boom_key, (
        f"a step ran AFTER the raiser: {steps_run}. The handler must return the halted "
        f"envelope directly — the loop predicate is `fail and halting`, so an "
        f"`inconclusive` row falls through and the next step runs.")
    assert boom_key in steps_run and len(steps_run) >= 2, (
        "the executor never reached the raising step, so this test would pass vacuously")

    phase = (ctx.journal.read() or {}).get("phase")
    assert phase != pm.LAND_STEP_JOURNAL.get(boom_key), (
        "the journal recorded the raising step's own phase")


def test_step_exception_exit_code_is_one_not_two(repo, monkeypatch, tmp_path, capsys):
    """REQ-LAND-030's exit code, asserted EXPLICITLY because it is the one number the
    investigation measured wrong.

    EXP-002's measured exit 2 came from calling `_land_execute` DIRECTLY, where the
    `inconclusive` row *fell through* to the loop's own end — an artifact of the very defect
    the wrapper removes. Through the CLI, `halted` sets `verdict = "fail"` and halted wins
    over the inconclusive list, so the process exit is **1**.
    """
    assert pm._land_exit_code("fail") == 1
    assert pm._land_exit_code("inconclusive") == 2

    # The verdict derivation the CLI performs: halted DOMINATES a non-empty inconclusive list.
    out = {"halted": True, "at": "l3_validate_merged",
           "results": [{"step": "l3_validate_merged", "verdict": "inconclusive",
                        "reason": "raised", "journal": None, "halting": True, "detail": {}}]}
    results = out["results"]
    inconclusive = [x for x in results if x.get("verdict") == "inconclusive"]
    assert inconclusive, "the fixture must exercise the halted-vs-inconclusive precedence"
    verdict = "fail" if out.get("halted") else ("inconclusive" if inconclusive else "pass")
    assert verdict == "fail"
    assert pm._land_exit_code(verdict) == 1, (
        "a halted landing exits 1; the measured 2 was an artifact of the fall-through")


def test_dispatch_wrapper_reraises_control_flow(repo, monkeypatch):
    """`KeyboardInterrupt` and `SystemExit` are RE-RAISED, never captured as a step row.

    They do not inherit from `Exception`, so the clause is redundant against the hierarchy —
    which is exactly why it is asserted: the invariant must survive someone widening the
    handler to `BaseException`.
    """
    monkeypatch.setattr(pm, "_landing_lock_acquire", lambda p: {"acquired": True})
    r = FakeRunner({"rev-parse|HEAD^{tree}": _R(0, "t\n"),
                    f"rev-parse|{PLAN_ID}-execute^{{tree}}": _R(0, "t\n")})

    for exc in (KeyboardInterrupt, SystemExit):
        def _raise(ctx, _e=exc):
            raise _e()
        monkeypatch.setattr(pm, "_land_l3_validate_merged", _raise)
        with pytest.raises(exc):
            pm._land_execute(_ctx(repo, r))


# =========================================================================================
# SC2c / SC2d / REQ-LAND-031 — L18 branches on the teardown's STATUS, and delegates the delete
# =========================================================================================

def test_l18_delegates_branch_delete(repo, monkeypatch):
    """SC2d. L18 still deletes the execute branch — VIA THE TEARDOWN, not by itself.

    The pair with `test_prune_is_strategy_aware`: that one asserts no `git branch -d` reaches
    `ctx.run`; this one asserts the delete is nonetheless reported, sourced from the
    teardown's own `branch_delete` step. Without both, "the duplicate is gone" and "the
    branch is still deleted" cannot be distinguished from "nothing deletes it any more".
    """
    seen = []

    def _capture(plan_dir, force=False):
        seen.append((plan_dir, force))
        return _teardown_ok(plan_dir, force)

    monkeypatch.setattr(pm, "_worktree_teardown", _capture)
    r = FakeRunner()
    out = pm._land_l18_prune(_ctx(repo, r))

    assert len(seen) == 1 and seen[0][1] is False, (
        f"L18 must call the teardown exactly once with force=False; saw {seen}")
    dele = [a for a in out["detail"]["actions"] if a["action"] == "delete-execute-branch"][0]
    assert dele["via"] == "_worktree_teardown"
    assert dele["ok"] is True, "the branch delete is reported from the teardown's own step"
    assert dele["branch"] == f"{PLAN_ID}-execute", "ONLY the execute branch"
    assert not [c for c in r.calls if "branch" in c and "-d" in c], (
        "the duplicate delete is gone: nothing reaches ctx.run")
    assert out["verdict"] == "pass" and out["journal"] == "L_PRUNED"


def test_l18_blocked_teardown(repo, monkeypatch):
    """SC2c / REQ-LAND-031. A `blocked` teardown is a HALTING fail, never a `pass`.

    Measured before the fix: a dirty worktree meant nothing was removed and the branch was
    left behind, and L18 reported `verdict: pass`. A landing must not report a prune it did
    not perform.

    The ABSENT-`status` case is asserted in the same test because it is the shape the shipped
    stubs produced — `{"action": "removed"}`, a key `_worktree_teardown` never returns. It is
    `inconclusive`, never `pass`: nothing was established in either direction.
    """
    blocked = {"status": "blocked", "path": f".worktrees/{PLAN_ID}",
               "branch": f"{PLAN_ID}-execute",
               "steps": {"remove": {"ok": False, "detail": "contains modified files"}},
               "detail": "worktree remove refused (dirty?)"}
    monkeypatch.setattr(pm, "_worktree_teardown", lambda pd, force=False: blocked)
    out = pm._land_l18_prune(_ctx(repo, FakeRunner()))
    assert out["verdict"] == "fail", "a blocked teardown pruned NOTHING"
    assert out["halting"] is True
    assert out["journal"] is None, "the journal must not record L_PRUNED when nothing pruned"
    assert out["detail"]["teardown_status"] == "blocked"
    assert "BLOCKED" in out["reason"]

    # PARTIAL — some step failed. Non-halting, but never `pass`.
    partial = dict(blocked, status="partial",
                   steps={"remove": {"ok": True, "detail": ""},
                          "branch_delete": {"ok": False, "detail": "not fully merged"},
                          "prune": {"ok": True, "detail": ""}})
    monkeypatch.setattr(pm, "_worktree_teardown", lambda pd, force=False: partial)
    out = pm._land_l18_prune(_ctx(repo, FakeRunner()))
    assert out["verdict"] == "inconclusive" and out["halting"] is False

    # ABSENT `status` — the old stub shape. UNJUDGED, so `inconclusive`.
    monkeypatch.setattr(pm, "_worktree_teardown",
                        lambda pd, force=False: {"action": "removed"})
    out = pm._land_l18_prune(_ctx(repo, FakeRunner()))
    assert out["verdict"] == "inconclusive", (
        "a return shape carrying no `status` establishes nothing about the prune")
    assert out["detail"]["teardown_status"] is None
    assert "no `status` key" in out["reason"]


# =========================================================================================
# SC3 / SC3c / SC3d — L16 against a REAL git repo with a REAL bare origin
# =========================================================================================
#
# NOT `FakeRunner` (Issue 3.3). The only pre-existing L16 test drove a fake scripted with
# `{"diff|--cached": _R(1)}`, so NO REAL GIT RAN — an argv real git rejects (the `-o -- <dir>
# -m <msg>` ordering, measured: `error: pathspec '-m' did not match any file(s)`) would still
# have passed. A mock that answers is not a process that runs.

def _real_repo(tmp_path, anchor: bool = True):
    """A real git repo on `main`, with a real BARE origin, `main` already pushed.

    `anchor` controls the `/.yf/` gitignore entry `yf preflight` ensures in this repository.
    Without it the landing journal appears as an untracked path — the ONLY configuration in
    which the exemption filter is load-bearing at all, and the reason SC3c exists.
    """
    origin = tmp_path / "origin.git"
    _git("init", "-q", "--bare", "-b", "main", str(origin), cwd=tmp_path)
    root = tmp_path / "work"
    root.mkdir()
    _git("init", "-q", "-b", "main", ".", cwd=root)
    for k, v in (("user.email", "t@example.invalid"), ("user.name", "T"),
                 ("commit.gpgsign", "false")):
        _git("config", k, v, cwd=root)
    if anchor:
        (root / ".gitignore").write_text("/.yf/\n", encoding="utf-8")
    pdir = root / "docs" / "plans" / PLAN_ID
    pdir.mkdir(parents=True)
    (pdir / "plan.md").write_text(f"# Plan: t\n\n**ID:** {PLAN_ID}\n", encoding="utf-8")
    (root / "unrelated.py").write_text("v1\n", encoding="utf-8")
    _git("add", "-A", cwd=root)
    _git("commit", "-q", "-m", "base", cwd=root)
    _git("remote", "add", "origin", str(origin), cwd=root)
    _git("push", "-q", "-u", "origin", "main", cwd=root)
    return root


def _l16_ctx(root, monkeypatch):
    """A LandingContext over a real repo, with the REAL runner (no FakeRunner)."""
    monkeypatch.chdir(root)
    rel = Path("docs/plans") / PLAN_ID
    facts = {"git": {"merge_target": "main", "execute_branch": f"{PLAN_ID}-execute",
                     "worktree_path": f".worktrees/{PLAN_ID}"}}
    manifest = {"facts": facts}
    d = {"schema": pm.LAND_SCHEMA_DECISION, "plan_id": PLAN_ID, "authored_by": "lander",
         "summary": "s", "upstream_writes": [],
         "steps": {k: "enable" for k in pm.LAND_STEPS}}
    return pm.LandingContext(rel, d, manifest, root=root)


def _tracked_in_head(root, path: str) -> bool:
    r = subprocess.run(["git", "show", f"HEAD:{path}"], cwd=str(root),
                       capture_output=True, text=True)
    return r.returncode == 0


def test_l16_commits_only_plan_dir(tmp_path, monkeypatch):
    """SC3 / REQ-LAND-032 (#342). A PRE-STAGED UNRELATED FILE IS NOT IN THE COMMIT.

    The expected envelope is pinned, NOT merely the file's absence: `verdict: fail`,
    `halting: true`, and the file absent from `HEAD`. Writing this to expect `pass` would
    invite scoping the POST-CONDITION as well — which re-opens #342 on the very axis this
    gate guards. The commit is scoped; the halt is intended and stays.
    """
    root = _real_repo(tmp_path)
    (root / "unrelated.py").write_text("SECRET v2\n", encoding="utf-8")
    _git("add", "unrelated.py", cwd=root)                       # PRE-STAGED, unrelated
    (root / "docs" / "plans" / PLAN_ID / "log.md").write_text("- landed\n", encoding="utf-8")

    before = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(root),
                            capture_output=True, text=True).stdout.strip()
    out = pm._land_l16_commit_and_push_two(_l16_ctx(root, monkeypatch))
    after = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(root),
                           capture_output=True, text=True).stdout.strip()

    assert after != before, "L16 made no commit at all, so the scoping is untested"
    head = subprocess.run(["git", "show", "--name-only", "--format=", "HEAD"],
                          cwd=str(root), capture_output=True, text=True).stdout.split()
    assert "unrelated.py" not in head, (
        f"#342: the unrelated pre-staged file was committed under the plan's message. "
        f"HEAD touched {head}")
    assert f"docs/plans/{PLAN_ID}/log.md" in head, "the plan-folder write was not committed"
    assert subprocess.run(["git", "show", "HEAD:unrelated.py"], cwd=str(root),
                          capture_output=True, text=True).stdout.strip() != "SECRET v2", (
        "the unrelated content reached the commit")

    assert out["verdict"] == "fail", (
        "the halt is INTENDED — the post-condition still sees the unrelated staged file. "
        "Expecting `pass` here would invite scoping the post-condition and re-open #342.")
    assert out["halting"] is True
    assert "unrelated.py" in out["detail"]["porcelain"]


def test_l16_commits_plan_dir_writes(tmp_path, monkeypatch):
    """SC3d — the POSITIVE case. A normal landing still commits its own plan-folder writes,
    INCLUDING A NEWLY CREATED UNTRACKED FILE, and still passes.

    Without this, "commits only the plan dir" is satisfiable by committing nothing.
    """
    root = _real_repo(tmp_path)
    pdir = root / "docs" / "plans" / PLAN_ID
    (pdir / "plan.md").write_text("# Plan: t\n\n**Status:** complete\n", encoding="utf-8")
    (pdir / "log.md").write_text("- complete\n", encoding="utf-8")       # UNTRACKED, new
    (pdir / "assets").mkdir()
    (pdir / "assets" / "a b.md").write_text("spaced\n", encoding="utf-8")  # SPACED PATH

    out = pm._land_l16_commit_and_push_two(_l16_ctx(root, monkeypatch))
    assert out["verdict"] == "pass", f"a clean landing must pass: {out['reason']}"
    assert out["journal"] == "L_PUSHED_2"
    for f in (f"docs/plans/{PLAN_ID}/log.md",
              f"docs/plans/{PLAN_ID}/assets/a b.md",
              f"docs/plans/{PLAN_ID}/plan.md"):
        assert _tracked_in_head(root, f), f"{f} was not committed"
    # ...and it really was PUSHED to the real bare origin.
    local = subprocess.run(["git", "rev-parse", "main"], cwd=str(root),
                           capture_output=True, text=True).stdout.strip()
    remote = subprocess.run(["git", "rev-parse", "origin/main"], cwd=str(root),
                            capture_output=True, text=True).stdout.strip()
    assert local == remote, "push #2 did not reach the origin"


def test_l16_without_anchor(tmp_path, monkeypatch):
    """SC3c / REQ-LAND-033 (#343). The exemption filter works in a repo WITHOUT `/.yf/` in
    `.gitignore` — the only configuration where it is load-bearing at all.

    Three things are asserted together because each alone is satisfiable by a wrong filter:

    1. The journal and `land-beads.json` are exempt (a PREFIX match on `.yf/plan/`).
    2. `-uall` is what makes (1) reachable: without it git collapses the whole tree to a
       single `?? .yf/` entry, which contains NEITHER path.
    3. A path with a SPACE outside the plan folder is still caught — the `-z` split and the
       path-field test, not a `startswith` over a quoted raw line.
    """
    root = _real_repo(tmp_path, anchor=False)
    jdir = root / ".yf" / "plan" / "landing-journal"
    jdir.mkdir(parents=True)
    (jdir / f"{PLAN_ID}.json").write_text('{"phase":"L_PUSHED_2"}\n', encoding="utf-8")
    (root / ".yf" / "plan" / "land-beads.json").write_text("[]\n", encoding="utf-8")
    (root / "docs" / "plans" / PLAN_ID / "log.md").write_text("- x\n", encoding="utf-8")

    # (2) the collapse this filter would otherwise be blind to, measured rather than assumed.
    collapsed = subprocess.run(["git", "status", "--porcelain"], cwd=str(root),
                               capture_output=True, text=True).stdout
    assert "?? .yf/\n" in collapsed, (
        "the fixture no longer reproduces git's untracked-directory collapse, so clause (2) "
        "of this test is vacuous")

    out = pm._land_l16_commit_and_push_two(_l16_ctx(root, monkeypatch))
    assert out["verdict"] == "pass", (
        f"#343: the landing journal was not exempted in a repo without the /.yf/ anchor: "
        f"{out['reason']}")

    # (3) a SPACED path outside the plan folder is still dirt.
    (root / "some file.txt").write_text("x\n", encoding="utf-8")
    dirt = pm._dirty_outside_plan_dir(Path("docs/plans") / PLAN_ID, root=root)
    assert dirt["dirty"] is True
    assert any("some file.txt" in p for p in dirt["paths"]), (
        f"a quoted, spaced path was missed by the porcelain split: {dirt['paths']}")
    assert not any(".yf/plan" in p for p in dirt["paths"]), "the allowlist leaked"


def test_dirty_outside_plan_dir_is_a_prefix_not_a_substring(tmp_path, monkeypatch):
    """REQ-LAND-033's third clause, isolated. A path merely CONTAINING the allowlist
    fragment is NOT exempt — that is the substring bug (#343) restated as a test."""
    root = _real_repo(tmp_path, anchor=False)
    trap = root / "docs" / "a.yf" / "plan"
    trap.mkdir(parents=True)
    (trap / "decoy.txt").write_text("x\n", encoding="utf-8")
    dirt = pm._dirty_outside_plan_dir(Path("docs/plans") / PLAN_ID, root=root)
    assert any("decoy.txt" in p for p in dirt["paths"]), (
        f"`docs/a.yf/plan/decoy.txt` CONTAINS `.yf/plan/` but is not PREFIXED by it — a "
        f"substring filter exempts it. paths={dirt['paths']}")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))
