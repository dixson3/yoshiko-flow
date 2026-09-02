"""Tests for `check_skill_readme_contract.py` (REQ-YF-DOC-010..018).

The three load-bearing tests, and why each exists:

- **A planted defect must FAIL the checker.** A checker only ever observed green proves
  nothing about its sensitivity — it may be green because it enumerated nothing, or because it
  never evaluates the rule at all. Every rule here gets a planted counter-example.

- **The `--min-skills` floor must trip at exit 2, never 1.** At exit 1 the floor is
  byte-identical to a real contract failure, so a sensitivity gate of the form "the checker
  exits non-zero" would be satisfied by a checker that read nothing — the risk realised
  through its own mitigation (REQ-YF-DOC-015).

- **An unparseable fence must actually emit `fence-unparseable`.** SC4 passes when that array
  is empty, so a checker that never emits the class satisfies SC4 **vacuously** (#263). This
  test is what makes the closed enum (REQ-YF-DOC-014) a claim rather than a wish.

Run (house convention):
    uv run --with pytest python3 -m pytest scripts/checks/test_check_skill_readme_contract.py -q
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

CHECKER = Path(__file__).resolve().parent / "check_skill_readme_contract.py"


# --------------------------------------------------------------------------- fixtures

SKILL_MD = """---
name: {name}
description: a test skill
user-invocable: true
skill-group: utility
depends-on-tool: [{tools}]
---
# {name}

Invoke with `/{name}`.
"""

README_OK = """# {name}

A one-line description.

## Prerequisites

- `{tool}` on `PATH`.

## Install

Run `yf skills install`.

## Usage

User-invocable (`/{name}`).

## File layout

```
skills/{name}/
├── SKILL.md        # entry point
└── README.md       # this file
```
"""


def make_skill(root: Path, name: str, *, readme: str | None = README_OK,
               tools: str = "uv", extra: dict[str, str] | None = None) -> Path:
    d = root / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(SKILL_MD.format(name=name, tools=tools))
    if readme is not None:
        (d / "README.md").write_text(readme.format(name=name, tool=tools.split(",")[0].strip()))
    for rel, body in (extra or {}).items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)
    return d


def run(skills_root: Path, *args: str) -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--skills-root", str(skills_root), "--json", *args],
        capture_output=True, text=True)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:  # pragma: no cover - a crash is itself a failure
        pytest.fail(f"checker emitted no parseable JSON (rc={proc.returncode}): "
                    f"{proc.stdout!r} / {proc.stderr!r}")
    return proc.returncode, payload


@pytest.fixture()
def skills(tmp_path: Path) -> Path:
    return tmp_path / "skills"


# --------------------------------------------------------------------------- the clean base

def test_a_conformant_skill_passes(skills: Path):
    make_skill(skills, "yf-clean")
    rc, out = run(skills)
    assert out["verdict"] == "PASS", out
    assert rc == 0
    assert out["skills_enumerated"] == 1
    assert out["failures"] == []


def test_enumeration_is_depth_one_never_rglob(skills: Path):
    """A nested fixture tree inside a skill is not a second skill (REQ-YF-DOC-011)."""
    d = make_skill(skills, "yf-clean")
    nested = d / "tests" / "fixtures" / "yf-fake"
    nested.mkdir(parents=True)
    (nested / "SKILL.md").write_text(SKILL_MD.format(name="yf-fake", tools="uv"))
    rc, out = run(skills)
    assert out["skills_enumerated"] == 1, out["skills"]
    assert "yf-fake" not in out["skills"]


# --------------------------------------------------------------------------- planted defects

def test_planted_layout_defect_fails(skills: Path):
    """A file on disk that the fence does not list is a `layout` failure (REQ-YF-DOC-006)."""
    make_skill(skills, "yf-drifty", extra={"scripts/tool.py": "# undeclared\n"})
    rc, out = run(skills)
    assert rc == 1
    assert out["verdict"] == "FAIL"
    classes = [f["class"] for f in out["failures"]]
    assert classes == ["layout"], out["failures"]
    assert "scripts/tool.py" in out["failures"][0]["detail"]


def test_planted_stale_fence_root_fails(skills: Path):
    """A fence root naming a path that does not exist is drift (REQ-YF-DOC-004)."""
    readme = README_OK.replace("skills/{name}/\n", "{name}/\n")
    make_skill(skills, "yf-stale", readme=readme)
    rc, out = run(skills)
    assert rc == 1
    assert any(f["class"] == "layout" and "real directory" in f["detail"]
               for f in out["failures"]), out["failures"]


def test_planted_phantom_fence_entry_fails(skills: Path):
    """A fence entry with no file behind it is drift in the other direction."""
    readme = README_OK.replace("└── README.md       # this file",
                               "├── README.md       # this file\n└── LICENSE         # absent")
    make_skill(skills, "yf-overclaim", readme=readme)
    rc, out = run(skills)
    assert rc == 1
    assert any("do not exist on disk" in f["detail"] for f in out["failures"]), out["failures"]


def test_planted_prereqs_defect_fails(skills: Path):
    """A declared tool absent from Prerequisites is a `prereqs` failure (REQ-YF-DOC-007)."""
    make_skill(skills, "yf-prereq", tools="uv, pandoc")
    rc, out = run(skills)
    assert rc == 1
    prereq = [f for f in out["failures"] if f["class"] == "prereqs"]
    assert prereq, out["failures"]
    assert "pandoc" in prereq[0]["detail"]


def test_planted_unprefixed_invocation_fails(skills: Path):
    """Teaching `/incubator` where the skill answers to `/yf-incubator` (REQ-YF-DOC-008)."""
    readme = README_OK.replace("User-invocable (`/{name}`).",
                               "User-invocable (`/unprefixed`).\n\n```\n/unprefixed new\n```")
    make_skill(skills, "yf-unprefixed", readme=readme)
    rc, out = run(skills)
    assert rc == 1
    assert any(f["class"] == "usage" and "unprefixed" in f["detail"]
               for f in out["failures"]), out["failures"]


def test_planted_missing_usage_section_fails(skills: Path):
    readme = README_OK.replace("## Usage\n\nUser-invocable (`/{name}`).\n\n", "")
    make_skill(skills, "yf-nousage", readme=readme)
    rc, out = run(skills)
    assert rc == 1
    assert any(f["class"] == "usage" for f in out["failures"]), out["failures"]


# ------------------------------------------------- absence is its OWN class (REQ-YF-DOC-018)

def test_missing_readme_is_its_own_class_not_a_mismatch(skills: Path):
    make_skill(skills, "yf-noreadme", readme=None)
    rc, out = run(skills)
    assert rc == 1
    classes = [f["class"] for f in out["failures"]]
    assert classes == ["missing-readme"], out["failures"]
    # The whole point: absence must NOT be reported as a layout/prereqs/usage mismatch.
    assert "layout" not in classes and "prereqs" not in classes and "usage" not in classes


# ------------------------------------------- the fence-unparseable class is really emitted

def test_planted_unparseable_fence_emits_fence_unparseable(skills: Path):
    """SC4 is vacuous unless this class is genuinely reachable (#263, REQ-YF-DOC-014)."""
    readme = README_OK.replace(
        "```\nskills/{name}/\n├── SKILL.md        # entry point\n"
        "└── README.md       # this file\n```",
        "```\nskills/{name}/\n  SKILL.md        entry point\n  README.md       this file\n```")
    make_skill(skills, "yf-flat", readme=readme)
    rc, out = run(skills)
    assert rc == 1
    classes = {f["class"] for f in out["failures"]}
    assert "fence-unparseable" in classes, out["failures"]
    # An unparseable fence FAILS the layout edge too — the two findings are different facts.
    assert "layout" in classes, out["failures"]


def test_bullet_list_layout_is_unparseable_not_clean(skills: Path):
    readme = README_OK.split("## File layout")[0] + (
        "## File layout\n\n- `SKILL.md` — entry point.\n- `README.md` — this file.\n")
    make_skill(skills, "yf-bullets", readme=readme)
    rc, out = run(skills)
    assert rc == 1
    assert any(f["class"] == "fence-unparseable" for f in out["failures"]), out["failures"]


def test_closed_enum_is_never_exceeded(skills: Path):
    """Every emitted class is drawn from the declared closed set (REQ-YF-DOC-014)."""
    make_skill(skills, "yf-a", tools="uv, pandoc", extra={"x.py": "#\n"})
    make_skill(skills, "yf-b", readme=None)
    rc, out = run(skills)
    assert set(out["classes"]) == {"layout", "prereqs", "usage",
                                   "missing-readme", "fence-unparseable"}
    assert {f["class"] for f in out["failures"]} <= set(out["classes"])


# ----------------------------------------------------- the floor trips at 2, NEVER at 1

def test_min_skills_floor_trips_at_exit_two_on_empty_enumeration(skills: Path):
    """REQ-YF-DOC-015 — the exit code IS the requirement, not the floor."""
    skills.mkdir(parents=True)
    rc, out = run(skills, "--min-skills", "20")
    assert rc == 2, f"a floor tripping at 1 is indistinguishable from a real FAIL: {out}"
    assert out["verdict"] == "INCONCLUSIVE"
    assert out["skills_enumerated"] == 0


def test_min_skills_floor_trips_at_two_even_with_a_clean_corpus(skills: Path):
    make_skill(skills, "yf-clean")
    rc, out = run(skills, "--min-skills", "20")
    assert rc == 2 and out["verdict"] == "INCONCLUSIVE", out
    assert out["skills_enumerated"] == 1


def test_min_skills_floor_outranks_a_real_failure(skills: Path):
    """An under-read corpus is INCONCLUSIVE even when what WAS read is dirty.

    Reporting `1` here would let a gate read "the checker failed" from a run that never
    established the corpus was fully enumerated.
    """
    make_skill(skills, "yf-dirty", extra={"undeclared.py": "#\n"})
    rc, out = run(skills, "--min-skills", "20")
    assert rc == 2 and out["verdict"] == "INCONCLUSIVE", out


def test_absent_skills_root_is_inconclusive_not_clean(skills: Path):
    rc, out = run(skills / "does-not-exist")
    assert rc == 2 and out["verdict"] == "INCONCLUSIVE", out


# ------------------------------------------------------------------- e-readme-desc is NOT claimed

def test_readme_desc_is_declared_unchecked(skills: Path):
    """REQ-YF-DOC-013 — the checker must say what it does not check, not imply it did."""
    make_skill(skills, "yf-clean")
    _, out = run(skills)
    assert "e-readme-desc" in out["not_checked"]


# --------------------------------------------------------------------------- scoping

def test_changed_scoping_narrows_enumeration(skills: Path):
    make_skill(skills, "yf-a")
    make_skill(skills, "yf-b", extra={"undeclared.py": "#\n"})
    rc, out = run(skills, "--changed", "skills/yf-a/README.md")
    assert out["skills"] == ["yf-a"], out
    assert rc == 0, out
