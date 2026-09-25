#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Negative controls for `scripts/check_frontmatter.py`'s REQ-YF-EMBED-007 field rules (plan-072 Issue 1.2).

Each case builds a throwaway `skills/` tree in a temp dir, runs the checker against it with
`--root`, and asserts the exit code. There is one FAIL case per rule, so a rule that silently
stops firing turns this test red. There is also the scope control: an `agents/*.md` carrying a
2000-char description must PASS, because the field rules bind `SKILL.md` only.

The astral case matters because the length unit is UTF-16 code units (what pi's JS
`String.length` measures). 1000 ASCII chars plus 13 U+1F600 is 1013 code points but 1026 UTF-16
units, so a code-point count would pass it and the check must not.

Run:  uv run scripts/test_check_frontmatter.py
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECK = HERE / "check_frontmatter.py"


def skill_md(name: str, desc: str) -> str:
    # Double-quoted YAML scalar; the descriptions used here carry no `"` or `\`.
    return f'---\nname: {name}\ndescription: "{desc}"\n---\n# {name}\n'


def run(tree: dict[str, str]) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        for rel, text in tree.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
        r = subprocess.run(["uv", "run", "--quiet", str(CHECK), "--root", str(root)],
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr


OK_DESC = "Does a thing. TRIGGER when: asked. SKIP for: other things."

CASES = [
    # (label, tree, expected_rc, substring expected in output or None)
    ("baseline clean", {"skills/good-skill/SKILL.md": skill_md("good-skill", OK_DESC)}, 0, None),
    ("description exactly 1024", {"skills/a/SKILL.md": skill_md("a", "x" * 1024)}, 0, None),
    ("description > 1024", {"skills/a/SKILL.md": skill_md("a", "x" * 1025)}, 1,
     "description 1025 > 1024 (over by 1)"),
    ("astral: 1013 code points, 1026 UTF-16 units",
     {"skills/a/SKILL.md": skill_md("a", "x" * 1000 + "\U0001F600" * 13)}, 1,
     "description 1026 > 1024"),
    ("empty description", {"skills/a/SKILL.md": '---\nname: a\ndescription: ""\n---\n'}, 1,
     "description is missing or empty"),
    ("missing description", {"skills/a/SKILL.md": "---\nname: a\n---\n"}, 1,
     "description is missing or empty"),
    ("name > 64", {f"skills/{'n' * 65}/SKILL.md": skill_md("n" * 65, OK_DESC)}, 1, "name 65 > 64"),
    ("bad charset", {"skills/Bad_Name/SKILL.md": skill_md("Bad_Name", OK_DESC)}, 1,
     "outside [a-z0-9-]"),
    ("leading hyphen", {"skills/-lead/SKILL.md": skill_md("-lead", OK_DESC)}, 1,
     "starts or ends with a hyphen"),
    ("trailing hyphen", {"skills/trail-/SKILL.md": skill_md("trail-", OK_DESC)}, 1,
     "starts or ends with a hyphen"),
    ("double hyphen", {"skills/a--b/SKILL.md": skill_md("a--b", OK_DESC)}, 1, "contains '--'"),
    ("name != dir", {"skills/dir-name/SKILL.md": skill_md("other-name", OK_DESC)}, 1,
     "does not equal its directory"),
    ("scope: agents/*.md with a 2000-char description passes",
     {"skills/good-skill/SKILL.md": skill_md("good-skill", OK_DESC),
      "skills/good-skill/agents/big.md": '---\nname: Big Agent\ndescription: "' + "y" * 2000 + '"\n---\n'},
     0, None),
]


def main() -> int:
    failed = 0
    for label, tree, want, needle in CASES:
        rc, out = run(tree)
        ok = rc == want and (needle is None or needle in out)
        print(f"{'PASS' if ok else 'FAIL'}  {label}  (rc={rc}, want={want})")
        if not ok:
            failed += 1
            print("      output:", out.strip().replace("\n", "\n      "))
    # The live tree must also be clean (REQ-YF-EMBED-007 holds on the shipped skills).
    r = subprocess.run(["uv", "run", "--quiet", str(CHECK)], capture_output=True, text=True)
    live_ok = r.returncode == 0
    print(f"{'PASS' if live_ok else 'FAIL'}  live skills/ tree is clean (rc={r.returncode})")
    failed += 0 if live_ok else 1
    total = len(CASES) + 1
    print(f"\ntest_check_frontmatter: {total - failed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
