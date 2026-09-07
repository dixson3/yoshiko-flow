"""Shared corpus + census helpers for the plan-066 web checkers.

**THE CORPUS IS A PARAMETER, NOT `web/content/**`** (plan-066 pass-1 C4). Measured: `README.md`
and `AGENTS.md` carry the IDENTICAL drifted harness matrix, and a `web/content/**`-scoped
checker cannot reach either — so a criterion certifying "all sites repaired" would have left the
most-read document in the repository wrong. Every checker that consumes this module takes
`--corpus` and defaults to the widened set.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

DEFAULT_CORPUS = ["web/content/**/*.md", "web/content/**/*.d2", "README.md", "AGENTS.md"]


def repo_root() -> Path:
    try:
        return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True, check=True).stdout.strip())
    except Exception:
        return Path.cwd()


def expand_corpus(root: Path, patterns: list[str]) -> list[Path]:
    """Glob each pattern relative to `root`, de-duplicated and sorted."""
    seen: dict[Path, None] = {}
    for pat in patterns:
        if any(ch in pat for ch in "*?["):
            for p in sorted(root.glob(pat)):
                if p.is_file():
                    seen[p] = None
        else:
            p = root / pat
            if p.is_file():
                seen[p] = None
    return list(seen)


def skill_census(root: Path) -> dict:
    """The SOURCE OF TRUTH for every counted-set claim.

    Groups come from `skills/*/SKILL.md` frontmatter `skill-group`. Formulas come from
    `skills/*/formulas/*.formula.toml` — **excluding `.beads/formulas/`**, which is the staged
    copy `yf preflight` writes and is not a shipped formula.
    """
    groups: dict[str, list[str]] = {}
    for skill_md in sorted((root / "skills").glob("*/SKILL.md")):
        m = re.search(r"^skill-group:\s*(\S+)\s*$", skill_md.read_text(encoding="utf-8"), re.M)
        if m:
            groups.setdefault(m.group(1), []).append(skill_md.parent.name)
    formulas = sorted(p.name.replace(".formula.toml", "")
                      for p in (root / "skills").glob("*/formulas/*.formula.toml"))
    return {
        "skills": sum(len(v) for v in groups.values()),
        "groups": {k: sorted(v) for k, v in sorted(groups.items())},
        "formulas": formulas,
    }


NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
             "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


def as_int(tok: str) -> int | None:
    tok = tok.strip().lower()
    if tok.isdigit():
        return int(tok)
    return NUM_WORDS.get(tok)
