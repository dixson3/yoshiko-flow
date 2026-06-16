#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Regenerate the FROZEN install-parity golden (REQ-YF-INSTALL-003/004).

This reproduces the authoritative output of the original `install.py`
(`load_skills` / `computed_groups` / `resolve_install_set`) over the live
`skills/` tree. install.py itself is deleted by plan-010 bead 5.1, so this
generator carries a faithful, standalone copy of that algorithm rather than
importing install.py.

The frozen output is the parity oracle that `yf/src/parity.rs` compares yf's
`frontmatter` computation against. It must be regenerated ONLY by a human when
the `skills/` tree legitimately changes group membership or `depends-on-skill`
edges — never at test time.

Regenerate (from the repo root):

    uv run yf/src/testdata/gen-install-parity.py > yf/src/testdata/install-parity.json

Keying matches yf: skills are keyed by their directory name under skills/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_DIR = Path(__file__).resolve().parents[3]
SKILLS_DIR = REPO_DIR / "skills"


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value]


def parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    parts = text.split("\n---", 1)
    if len(parts) < 2:
        return {}
    front = parts[0][len("---"):]
    data = yaml.safe_load(front)
    return data if isinstance(data, dict) else {}


def load_skills() -> dict[str, dict]:
    skills: dict[str, dict] = {}
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        fm = parse_frontmatter(skill_md)
        skills[skill_dir.name] = {
            "group": fm.get("skill-group"),
            "tools": _as_list(fm.get("depends-on-tool")),
            "skills": _as_list(fm.get("depends-on-skill")),
        }
    return skills


def computed_groups(skills: dict[str, dict]) -> list[str]:
    return sorted({m["group"] for m in skills.values() if m["group"]})


def resolve_install_set(skills: dict[str, dict], base: set[str]) -> set[str]:
    install: set[str] = set()
    queue = list(base)
    while queue:
        name = queue.pop()
        if name in install:
            continue
        install.add(name)
        for dep in skills[name]["skills"]:
            if dep not in skills:
                continue  # external / assumed-provided, skipped
            if dep not in install:
                queue.append(dep)
    return install


def main() -> int:
    skills = load_skills()
    groups = computed_groups(skills)
    skill_group = {name: meta["group"] for name, meta in skills.items()}
    group_members = {
        g: sorted(n for n, m in skills.items() if m["group"] == g) for g in groups
    }

    def closure(base) -> list[str]:
        return sorted(resolve_install_set(skills, set(base)))

    closures: dict[str, list[str]] = {}
    for g in groups:
        base = {n for n, m in skills.items() if m["group"] == g}
        closures[f"group:{g}"] = closure(base)
    for s in [
        "yf-beads-upstream",
        "yf-plan",
        "yf-research",
        "yf-beads-extra",
        "yf-markdown-lint",
    ]:
        if s in skills:
            closures[f"skill:{s}"] = closure([s])

    out = {
        "_comment": (
            "FROZEN GOLDEN — install.py authoritative output over skills/ "
            "(REQ-YF-INSTALL-003/004). install.py is deleted by plan-010 bead 5.1; "
            "do NOT run it at test time. Compared against by yf/src/parity.rs. "
            "Regenerate with: uv run yf/src/testdata/gen-install-parity.py "
            "> yf/src/testdata/install-parity.json"
        ),
        "skill_group": dict(sorted(skill_group.items())),
        "groups": sorted(groups),
        "group_members": dict(sorted(group_members.items())),
        "closures": dict(sorted(closures.items())),
    }
    json.dump(out, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
