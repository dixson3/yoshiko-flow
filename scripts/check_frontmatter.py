#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pyyaml>=6",
# ]
# ///
"""Repo-wide frontmatter guard (REQ-YF-EMBED-003, plan-039 Issue 4.2; REQ-YF-EMBED-007, plan-072).

Asserts that every `skills/*/SKILL.md` and `skills/*/agents/*.md` carries a well-formed,
**terminated** YAML frontmatter block: an opening `---` on line 1, a closing `---`
delimiter, and a body that parses as YAML.

REQ-YF-EMBED-007 adds, for `skills/*/SKILL.md` ONLY (never `agents/*.md`), the Agent Skills
field rules: `description` is a non-empty string of at most 1024 characters, and `name` is
1-64 chars of `[a-z0-9-]`, has no leading/trailing hyphen and no `--`, and equals the parent
directory name. Length is measured in UTF-16 code units of the PARSED YAML scalar, because pi
(the harness that enforces the cap) measures JavaScript `String.length`.

Run:  uv run scripts/check_frontmatter.py [--root DIR]
Exit: 0 = clean, 1 = at least one file has a malformed block or violates a field rule.

WHY A GUARD AND NOT JUST A REPAIR
---------------------------------
The failure this catches is **silent**. `skills/yf-plan/agents/reviewer.md` closed its
frontmatter with `:--` instead of `---`. The file still rendered as markdown and still
read correctly to a human, but the block was unterminated, so the agent's `name`, `role`,
`stance`, and `description` stopped parsing — the only machine-readable metadata the file
has. Nothing failed. Nothing warned. It was found by a person reading the file for an
unrelated reason.

`:--` is a **GFM table-alignment marker**, which is what makes this a class rather than a
one-off: it is exactly what a table-alignment autofix would write if it mistook a
frontmatter delimiter for a table delimiter. If that autofix is still live somewhere, the
repair alone would be undone on its next run and nobody would notice again. This check is
what turns a silent recurrence into a loud one.

Audited across all skills when it was written: `reviewer.md` was the only offender.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
PATTERNS = ("skills/*/SKILL.md", "skills/*/agents/*.md")

# REQ-YF-EMBED-007 — Agent Skills specification field limits.
MAX_DESCRIPTION = 1024
MAX_NAME = 64
NAME_RE = re.compile(r"^[a-z0-9-]+$")


def utf16_len(s: str) -> int:
    """Length in UTF-16 code units — what JS `String.length` (pi) reports."""
    return len(s.encode("utf-16-le")) // 2


def field_problems(path: Path, meta: dict) -> list[str]:
    """REQ-YF-EMBED-007 field rules for a skill's SKILL.md frontmatter."""
    out: list[str] = []
    desc = meta.get("description")
    if not isinstance(desc, str) or not desc.strip():
        out.append("REQ-YF-EMBED-007: description is missing or empty")
    else:
        n = utf16_len(desc)
        if n > MAX_DESCRIPTION:
            out.append(f"REQ-YF-EMBED-007: description {n} > {MAX_DESCRIPTION} "
                       f"(over by {n - MAX_DESCRIPTION})")
    name = meta.get("name")
    parent = path.parent.name
    if not isinstance(name, str) or not name:
        out.append("REQ-YF-EMBED-007: name is missing or empty")
        return out
    if utf16_len(name) > MAX_NAME:
        out.append(f"REQ-YF-EMBED-007: name {utf16_len(name)} > {MAX_NAME} chars")
    if not NAME_RE.match(name):
        out.append(f"REQ-YF-EMBED-007: name {name!r} has characters outside [a-z0-9-]")
    if name.startswith("-") or name.endswith("-"):
        out.append(f"REQ-YF-EMBED-007: name {name!r} starts or ends with a hyphen")
    if "--" in name:
        out.append(f"REQ-YF-EMBED-007: name {name!r} contains '--'")
    if name != parent:
        out.append(f"REQ-YF-EMBED-007: name {name!r} does not equal its directory {parent!r}")
    return out


def check(path: Path) -> str | None:
    """Return a human-readable problem, or None if the file is clean."""
    try:
        text = path.read_text()
    except OSError as exc:  # unreadable is a finding, not a crash
        return f"unreadable: {exc}"

    lines = text.splitlines()
    if not lines:
        return "empty file (no frontmatter block)"
    if lines[0].strip() != "---":
        return f"line 1 is {lines[0]!r}, expected an opening '---'"

    # Find the closing delimiter. Report the *look-alike* case specially: a line that is
    # plausibly a mangled delimiter is far more useful to name than "no closing ---".
    close = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            close = i
            break

    if close is None:
        for i, line in enumerate(lines[1:], start=1):
            s = line.strip()
            if s and set(s) <= set(":-.=~ ") and "-" in s:
                return (
                    f"unterminated block: line {i + 1} is {line!r}, which looks like a "
                    f"mangled '---' delimiter (a GFM table-alignment marker such as "
                    f"':--' is the known corruption)"
                )
        return "unterminated block: no closing '---' delimiter found"

    body = "\n".join(lines[1:close])
    try:
        parsed = yaml.safe_load(body)
    except yaml.YAMLError as exc:
        return f"frontmatter does not parse as YAML: {exc}"
    if parsed is not None and not isinstance(parsed, dict):
        return f"frontmatter parses as {type(parsed).__name__}, expected a mapping"
    if path.name == "SKILL.md":  # REQ-YF-EMBED-007 is scoped to SKILL.md only
        problems = field_problems(path, parsed or {})
        if problems:
            return "; ".join(problems)
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=REPO,
                    help="repo root holding skills/ (default: this repo)")
    args = ap.parse_args(argv)
    root = args.root.resolve()
    targets: list[Path] = []
    for pattern in PATTERNS:
        targets.extend(sorted(root.glob(pattern)))

    if not targets:
        print("check_frontmatter: no target files found — is the repo layout intact?",
              file=sys.stderr)
        return 1

    failures = []
    for path in targets:
        problem = check(path)
        if problem:
            failures.append((path, problem))

    for path, problem in failures:
        print(f"FAIL {path.relative_to(root)}: {problem}", file=sys.stderr)

    if failures:
        print(
            f"\ncheck_frontmatter: {len(failures)} of {len(targets)} file(s) have a "
            f"malformed frontmatter block (REQ-YF-EMBED-003) or violate a field rule "
            f"(REQ-YF-EMBED-007).\n"
            f"Fix the file; do not silence the check.",
            file=sys.stderr,
        )
        return 1

    print(f"check_frontmatter: {len(targets)} files clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
