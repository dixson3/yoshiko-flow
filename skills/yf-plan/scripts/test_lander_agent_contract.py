# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
#     "click>=8",
#     "pyyaml",
# ]
# ///
"""Contract tests for the `lander` agent (plan-060 Epic 2, Issues 2.5 and 2.6).

TWO HALVES, AND NEITHER SUBSTITUTES FOR THE OTHER (REQ-AGENT-065).

  * The TEXTUAL half (`test_lander_contract`) asserts the file says what it must say. It can
    only ever establish that **the instruction was written**.
  * The BEHAVIOURAL half (`test_dispatch_leaves_tree_clean`) observes that a dispatch leaves
    the working tree unchanged. It is what establishes that **the instruction was obeyed**.

A `grep -qF` for "read-only" has repeatedly been read as evidence of the second when it only
ever showed the first. That conflation is why Issue 2.6 exists as a separate issue from 0.4.

THE `__main__` IS THE FORWARDING FORM (REQ-CLI-028): the house shim discards `sys.argv`, so a
`-k` selector never reaches pytest and the criterion stays green when its named test is
deleted.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_AGENT = _HERE.parent / "agents" / "lander.md"
_SKILL = _HERE.parent / "SKILL.md"
_PM = _HERE / "plan_manager.py"


def _load():
    spec = importlib.util.spec_from_file_location("pm_lander_under_test", _PM)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pm_lander_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


pm = _load()


def _text() -> str:
    assert _AGENT.is_file(), f"no lander agent at {_AGENT}"
    return _AGENT.read_text(encoding="utf-8")


# --------------------------------------------------------------------------------------
# SC12 — the textual contract
# --------------------------------------------------------------------------------------

def test_lander_contract():
    """SC12 / Issues 2.1, 2.2, 2.5 — front matter, verbatim sentences, five adjudications,
    the fenced Output template, and NO LIFTABLE SHELL COMMAND."""
    t = _text()

    # --- front matter: exactly the five house keys, with `model:` present and EMPTY ------
    assert t.startswith("---\n")
    fm = t.split("---\n", 2)[1]
    keys = [ln.split(":", 1)[0] for ln in fm.splitlines() if ln and not ln[0].isspace()]
    assert keys == ["name", "role", "stance", "model", "description"], keys
    assert re.search(r"^model:\s*$", fm, re.M), "`model:` must be present and empty"
    assert re.search(r"^description:\s*\S", fm, re.M), "`description:` must be non-empty"

    # --- the two read-only sentences, VERBATIM ------------------------------------------
    for sentence in ("Read-only with respect to the repository under review",
                     "A sandbox spike is authorized"):
        assert sentence in t, f"missing verbatim: {sentence!r}"

    # --- declared in BOTH places: the Rules section AND the body ------------------------
    rules = t[t.index("## Rules"):]
    assert "Read-only with respect to the repository under review" in rules
    body = t[:t.index("## Rules")]
    assert "without write authority" in body or "read-only" in body.lower()

    # --- house section order -------------------------------------------------------------
    heads = [ln for ln in t.splitlines() if ln.startswith("## ")]
    assert heads == ["## Inputs", "## Evaluate", "## Rules", "## Output"], heads

    # --- the FIVE adjudications, numbered -------------------------------------------------
    ev = t[t.index("## Evaluate"):t.index("## Rules")]
    nums = re.findall(r"^\*\*(\d)\.", ev, re.M)
    assert nums == ["1", "2", "3", "4", "5"], f"expected five numbered adjudications, got {nums}"

    # --- the narrowed trust is stated: EXPLAIN, not DISCOVER --------------------------------
    assert "EXPLAIN" in ev and "DISCOVER" in ev, (
        "the agent must be told it EXPLAINS the per-disposition contract rather than "
        "DISCOVERING it — `UPSTREAM_REQUIREMENTS` already encodes it")

    # --- it emits a decision and never a command ------------------------------------------
    assert "decision document and never a command" in t

    # --- the fenced Output template, parseable as JSON with the pinned schema tag ----------
    out = t[t.index("## Output"):]
    m = re.search(r"```json\n(.*?)\n```", out, re.S)
    assert m, "## Output must carry a fenced ```json template"
    tmpl = json.loads(m.group(1))
    assert tmpl["schema"] == pm.LAND_SCHEMA_DECISION
    for k in ("manifest_digest", "upstream_writes", "upstream_refusals",
              "residual_bead_groups", "gate_adjudications", "steps"):
        assert k in tmpl, f"Output template omits {k!r}"

    # --- NO LIFTABLE IMPERATIVE SHELL COMMAND ----------------------------------------------
    # The agent must not carry anything an executor could copy and run. Fenced blocks are
    # checked by LANGUAGE: the one fence it may have is the ```json output template.
    # Toggle open/closed rather than regexing every fence marker: a closing ``` carries no
    # language, so a naive findall reports a phantom "" fence. Only OPENERS have a language.
    openers, inside = [], False
    for ln in t.splitlines():
        if ln.startswith("```"):
            if not inside:
                openers.append(ln[3:].strip())
            inside = not inside
    assert not inside, "an unterminated fence"
    assert set(openers) <= {"json"}, f"only a ```json fence is permitted, found {openers}"
    for verb in ("git ", "gh ", "bd ", "uv run", "$(", "&&", "sudo"):
        for ln in t.splitlines():
            if ln.strip().startswith(("- ", "#", ">", "|")) or not ln.strip():
                continue
        assert f"\n{verb}" not in t, f"a liftable command line beginning {verb!r} is present"
    assert "```bash" not in t and "```sh" not in t and "```console" not in t


def test_lander_length_is_in_the_house_band():
    """Issue 2.1's 79-109 line band. A band, not a maximum: far under it means the contract
    is not actually stated, and far over means it will not be read."""
    n = len(_AGENT.read_text(encoding="utf-8").splitlines())
    assert 79 <= n <= 109, f"lander.md is {n} lines, outside the 79-109 band"


def test_lander_is_dispatched_from_skill_md():
    """SC13's sibling. An agent file nothing reads is not a capability."""
    s = _SKILL.read_text(encoding="utf-8")
    assert "Read ${SKILL_DIR}/agents/lander.md" in s
    assert "land --dry-run" in s
    assert "MAIN SESSION writes the decision file" in s.replace("**", "")


# --------------------------------------------------------------------------------------
# SC15/SC16 support — the decision validator (Issue 2.3), report-only
# --------------------------------------------------------------------------------------

def _decision(digest: str, **over) -> dict:
    d = {
        "schema": pm.LAND_SCHEMA_DECISION,
        "manifest_digest": digest,
        "plan_id": "p",
        "authored_by": "lander",
        "summary": "s",
        "upstream_writes": [],
        "steps": {k: "enable" for k in pm.LAND_STEPS},
    }
    d.update(over)
    return d


def _manifest(halts=None) -> dict:
    return {"facts": {"a": 1, "b": [2, 3]}, "halts": halts or []}


def test_validate_decision_accepts_a_conformant_one():
    m = _manifest()
    env = pm._land_validate_decision(_decision(pm._land_digest(m["facts"])), m)
    assert env["verdict"] == "pass" and env["problems"] == []


def test_validate_decision_rejects_a_stale_digest():
    m = _manifest()
    env = pm._land_validate_decision(_decision("sha256:" + "0" * 64), m)
    assert env["verdict"] == "fail"
    assert env["digest_ok"] is False
    assert any("MISMATCH" in p for p in env["problems"])
    assert env["halt_class"] == pm.LAND_HALT_MECHANICAL


def test_validate_decision_rejects_skipping_a_non_skippable_step():
    m = _manifest()
    for step in sorted(pm.LAND_NON_SKIPPABLE):
        d = _decision(pm._land_digest(m["facts"]))
        d["steps"][step] = "skip:because"
        env = pm._land_validate_decision(d, m)
        assert env["verdict"] == "fail", f"{step} must be non-skippable"
        assert any("NON-SKIPPABLE" in p for p in env["problems"])


def test_validate_decision_requires_a_reason_for_every_skip():
    m = _manifest()
    d = _decision(pm._land_digest(m["facts"]))
    d["steps"]["l18_prune"] = "skip"
    env = pm._land_validate_decision(d, m)
    assert env["verdict"] == "fail"
    assert any("without a reason" in p for p in env["problems"])


def test_validate_decision_rejects_a_coarse_step_key_set():
    """A coarse key set cannot express a two-push order and would make `merge: skip` legal."""
    m = _manifest()
    d = _decision(pm._land_digest(m["facts"]), steps={"merge": "enable", "push": "enable"})
    env = pm._land_validate_decision(d, m)
    assert env["verdict"] == "fail"
    assert any("omits" in p for p in env["problems"])


def test_narrowing_only():
    """SC16. An `enable` on a step the manifest HALTED is IGNORED and REPORTED.

    The guarantee is not that the decision is rejected — it is that the enable does not take
    effect and does not do so SILENTLY. `ignored_enables` is the report.
    """
    m = _manifest(halts=[{"code": "merge-conflicts-predicted", "detail": "x"}])
    env = pm._land_validate_decision(_decision(pm._land_digest(m["facts"])), m)
    assert env["ignored_enables"], (
        "an enable against a halted manifest must be reported, never silently honoured")
    assert set(env["ignored_enables"]) <= set(pm.LAND_STEPS)

    clean = _manifest()
    env2 = pm._land_validate_decision(_decision(pm._land_digest(clean["facts"])), clean)
    assert env2["ignored_enables"] == [], (
        "with no halts nothing is ignored — otherwise the signal means nothing")


def test_validate_decision_writes_nothing(tmp_path, monkeypatch):
    """Report-only. `--validate-decision` is not a writing mode."""
    root = tmp_path / "r"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    monkeypatch.chdir(root)
    (root / "f.txt").write_text("x\n", encoding="utf-8")
    before = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                            capture_output=True, text=True).stdout
    m = _manifest()
    pm._land_validate_decision(_decision(pm._land_digest(m["facts"])), m)
    after = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                           capture_output=True, text=True).stdout
    assert before == after


# --------------------------------------------------------------------------------------
# SC14 / Issue 2.6 — the BEHAVIOURAL half
# --------------------------------------------------------------------------------------

def test_dispatch_leaves_tree_clean(tmp_path, monkeypatch):
    """SC14 / Issue 2.6 — read-only-ness in BEHAVIOUR, not merely in instruction.

    A `grep -qF` proves the instruction was WRITTEN. This proves nothing wrote.

    THE DISPATCH IS SIMULATED, AND THE LIMIT IS STATED RATHER THAN HIDDEN: a Tier-1 test
    cannot spawn a real sub-agent (no network, no harness). What it CAN do — and what makes
    it more than decoration — is drive the whole dispatch path the main session executes
    around the agent (`land --dry-run`, then `--validate-decision` over the returned
    decision) and assert the tree is byte-identical across it. That covers every step the
    session performs; the agent's own conduct is covered by the harness-level check the
    SKILL.md dispatch describes. A test that silently claimed to cover the agent itself
    would be the same overstatement REQ-AGENT-065's honesty note warns about.
    """
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    for k, v in (("user.email", "t@example.invalid"), ("user.name", "T"),
                 ("commit.gpgsign", "false")):
        subprocess.run(["git", "config", k, v], cwd=root, check=True)

    pdir = root / "docs" / "plans" / "plan-060-test-abc123"
    pdir.mkdir(parents=True)
    (pdir / "plan.md").write_text(
        "# Plan: t\n\n**ID:** plan-060-test-abc123\n**Status:** reconciling\n\n"
        "## Upstream Issues\n| Issue | Title | Disposition | Notes | Resolved By |\n"
        "| :-- | :-- | :-- | :-- | :-- |\n| #1 | a | partial | n | 1.1 |\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=root, check=True)
    monkeypatch.chdir(root)

    def snapshot():
        return (
            subprocess.run(["git", "status", "--porcelain"], cwd=root,
                           capture_output=True, text=True).stdout,
            subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                           capture_output=True, text=True).stdout,
            subprocess.run(["git", "for-each-ref", "--format=%(refname) %(objectname)"],
                           cwd=root, capture_output=True, text=True).stdout,
            sorted(p.relative_to(root).as_posix()
                   for p in root.rglob("*") if p.is_file() and ".git/" not in p.as_posix()),
        )

    before = snapshot()

    rel = Path("docs/plans/plan-060-test-abc123")
    manifest = pm._land_manifest(rel)                       # what the session hands the agent
    decision = _decision(pm._land_digest(manifest["facts"]))  # what the agent hands back
    env = pm._land_validate_decision(decision, manifest)      # what the session checks

    assert env["verdict"] in ("pass", "fail")
    assert snapshot() == before, (
        "the lander dispatch path MUTATED the repository — read-only-ness is violated in "
        "BEHAVIOUR, whatever the agent file says")


def test_the_textual_check_cannot_substitute_for_the_behavioural_one():
    """The honesty clause, asserted rather than merely written down.

    A file can carry every required sentence and still be obeyed by nothing. This test pins
    that the two checks are DISTINCT FUNCTIONS — if someone ever collapses them into one,
    this fails and says why.
    """
    import inspect
    src_text = inspect.getsource(test_lander_contract)
    src_beh = inspect.getsource(test_dispatch_leaves_tree_clean)
    # The probe is spelled as an argv LIST (`["git", "status", ...]`), never as the string
    # "git status" — so match on the argv tokens. A literal-string match here would have
    # failed for a reason that has nothing to do with the property being pinned.
    assert '"status", "--porcelain"' not in src_text, (
        "the TEXTUAL check must not smuggle in a behavioural assertion — keeping them "
        "separate is what stops a green grep being read as proof of conduct")
    assert '"status", "--porcelain"' in src_beh, (
        "the BEHAVIOURAL check must actually observe the working tree")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, *sys.argv[1:]]))
