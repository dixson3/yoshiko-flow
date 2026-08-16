#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Acceptance check for plan-040 / SC3 + SC4: the `bd <backend>` write path is GONE
from the implementation.

Run:  uv run skills/yf-beads-upstream/scripts/check_gh_direct.py
Exit: 0 = clean, 1 = a deleted mechanism was reintroduced.

WHY THIS IS SCOPED TO CODE, NOT PROSE
-------------------------------------
Its sibling `check_prescriptive_push.py` guards SKILL.md, where `bd github push` is
allowed to appear in explanation and forbidden in procedure. This check guards
`upstream.py`, where the rule is different and simpler: the command must never be
CONSTRUCTED, while comments explaining why it was removed are fine and wanted.

So the mechanical boundary here is CODE vs COMMENT:

  CODE     = a line with the mechanism outside a comment or docstring. Flagged.
  COMMENT  = `#` lines and the module/function docstrings that record what was deleted
             and why. Never flagged — deleting them would erase the provenance of a
             decision that took a red-team cycle and a live measurement to reach.

WHY IT EXISTS
-------------
Migrating only some call sites would leave two write mechanisms with different failure
modes and separator conventions side by side — the exact condition that produced #129
(a comma-joined id list matching ZERO beads while exiting 0, after which the
destructive stage tombstoned every bead). One mechanism, enforced.
"""
from __future__ import annotations

import io
import sys
import tokenize
from pathlib import Path

TARGET = Path(__file__).parent / "upstream.py"

# Constructing any of these means the deleted write path came back.
FORBIDDEN_SUBSTRINGS = (
    "bd github push",
    "bd gitlab push",
    "bd jira push",
    "<backend> push",
    "--push-only",
    "BACKEND_AUTH",
)

# Names deleted by plan-040. Their reappearance means a half-finished migration.
FORBIDDEN_NAMES = (
    "def push_command_sequence",
    "def verified_push",
    "def parse_pushed_count",
    "def plan_push",
    "PUSHED_COUNT_RE",
    'add_argument("--backend"',
)


def code_lines(path: Path) -> list[tuple[int, str]]:
    """Source lines with comments and string literals blanked out.

    Tokenizing rather than regexing the source is what lets the explanatory comments
    survive: they are removed before matching, so they cannot trip the check.
    """
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    blanked = list(lines)
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except tokenize.TokenError:
        return list(enumerate(lines, 1))
    for tok in toks:
        if tok.type not in (tokenize.COMMENT, tokenize.STRING):
            continue
        (srow, scol), (erow, ecol) = tok.start, tok.end
        for row in range(srow, erow + 1):
            i = row - 1
            if i >= len(blanked):
                continue
            line = blanked[i]
            a = scol if row == srow else 0
            b = ecol if row == erow else len(line)
            blanked[i] = line[:a] + " " * (b - a) + line[b:]
    return list(enumerate(blanked, 1))


def main() -> int:
    if not TARGET.exists():
        print(f"check_gh_direct: {TARGET} not found", file=sys.stderr)
        return 1

    violations: list[str] = []
    for lineno, line in code_lines(TARGET):
        for needle in FORBIDDEN_SUBSTRINGS + FORBIDDEN_NAMES:
            if needle in line:
                violations.append(f"  {TARGET.name}:{lineno}: {needle!r} -> {line.strip()}")

    if violations:
        print("check_gh_direct: FAIL — the deleted `bd <backend>` write path was "
              "reintroduced in CODE (comments explaining the removal are fine):",
              file=sys.stderr)
        print("\n".join(violations), file=sys.stderr)
        print("\nUpstream writes are gh-direct (REQ-BUP-057): `gh` writes the issue and "
              "`bd update --external-ref` records the mapping. See SPEC.md REQ-BUP-030/040/057.",
              file=sys.stderr)
        return 1

    print("check_gh_direct: clean — no `bd <backend>` write path in upstream.py code.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
