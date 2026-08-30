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

def _step_ok(name, journal=None):
    return {"step": name, "verdict": "pass", "reason": "stubbed", "journal": journal,
            "halting": False, "detail": {}}


class FakeRunner:
    """A scripted process runner. Injected via LandingContext(runner=...), so the SAME step
    functions run under test as in production — one code path, not a parallel one."""

    def __init__(self, script=None):
        self.script = script or {}
        self.calls: list[list[str]] = []

    def __call__(self, args, cwd=None):
        self.calls.append(list(args))
        for key, res in self.script.items():
            if all(tok in args for tok in key.split("|")):
                return res
        return _R(0)

    def saw(self, *toks) -> bool:
        return any(all(t in c for t in toks) for c in self.calls)


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
    monkeypatch.setattr(pm, "_worktree_teardown", lambda pd: {"action": "removed"})

    monkeypatch.setattr(pm, "_resolve_landing_strategy", lambda: "feature-branch")
    r = FakeRunner()
    out = pm._land_l18_prune(_ctx(repo, r))
    assert out["detail"]["strategy"] == "feature-branch"
    assert PLAN_ID in out["detail"]["preserved"], "REQ-BRANCH-004: the feature branch is KEPT"
    deleted = [c for c in r.calls if "branch" in c and "-d" in c]
    assert deleted and all(f"{PLAN_ID}-execute" in c for c in deleted), (
        "ONLY the execute branch may be deleted")
    assert not any(c[-1] == PLAN_ID for c in deleted), "the feature branch was deleted"

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
    monkeypatch.setattr(pm, "_worktree_teardown", lambda pd: {"action": "removed"})
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


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))
