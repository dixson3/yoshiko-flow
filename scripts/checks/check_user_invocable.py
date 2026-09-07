#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_user_invocable.py — REQ-CHECK-012(b): the tri-state key is POPULATED, and its
declared value does not contradict the skill's own description.

Two assertions over the same corpus, kept separate because they are different facts:

A1 — POPULATION.  Every ``skills/*/SKILL.md`` frontmatter carries an explicit
     ``user-invocable:``.  ``yf/src/frontmatter.rs`` types the key ``Option<bool>`` (absent =
     UNKNOWN), so an absent key is not a declared ``false`` — it is a fact nobody stated.  Four
     files omitted it and the published site rendered them "auto (fires from its description
     conditions)" while their own descriptions read ``TRIGGER when: /yf-markdown-lint invoked``.

A2 — NON-CONTRADICTION.  No skill declares ``user-invocable: false`` while its own
     ``description:`` names a ``/<skill-name>`` slash trigger.  This is the predicate that would
     have caught the original defect had the key been populated wrongly instead of omitted, so
     fixing A1 alone would leave the same falsehood reachable by a different route.

VACUITY FLOOR.  ``--min-skills`` (default 15).  A check that inspects nothing certifies nothing —
the same floor ``check-req-coverage`` and ``check_required_set`` carry, and the reason this
script cannot pass by finding no ``SKILL.md`` files at all.

EXIT  0 both assertions hold  ·  1 an assertion FAILED  ·  2 INCONCLUSIVE (could not run)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHECK = "check_user_invocable"
FM_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
KEY_RE = re.compile(r"^user-invocable:\s*(\S+)\s*$", re.M)
NAME_RE = re.compile(r"^name:\s*(\S+)\s*$", re.M)


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def repo_root() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        return Path(out)
    except Exception:
        return Path(__file__).resolve().parent.parent.parent


def description_of(fm_text: str) -> str:
    """The `description:` block, flattened. A YAML scalar that may be `>`-folded across lines."""
    m = re.search(r"^description:\s*(.*)$", fm_text, re.M)
    if not m:
        return ""
    lines = [m.group(1)]
    tail = fm_text[m.end():].splitlines()
    for ln in tail:
        if ln and not ln[0].isspace():
            break
        lines.append(ln.strip())
    return " ".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skills-root", default=None)
    ap.add_argument("--min-skills", type=int, default=15,
                    help="vacuity floor — fewer inspected SKILL.md files is INCONCLUSIVE")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = Path(args.skills_root) if args.skills_root else repo_root() / "skills"
    if not root.is_dir():
        inconclusive(f"no skills root at {root}")

    files = sorted(root.glob("*/SKILL.md"))
    if len(files) < args.min_skills:
        inconclusive(f"inspected {len(files)} SKILL.md file(s), below the --min-skills floor "
                     f"of {args.min_skills} — a check over such a set certifies vacuously")

    absent: list[str] = []
    contradictions: list[dict] = []
    inspected = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        m = FM_RE.match(text)
        if not m:
            inconclusive(f"{f} has no leading frontmatter fence — cannot read the key")
        fm = m.group(1)
        inspected += 1
        km = KEY_RE.search(fm)
        # `--skills-root` may legitimately point OUTSIDE the repo (that is how the
        # negative controls run), so a bare `relative_to` raises and the traceback's
        # exit 1 masquerades as an assertion failure — a false green for the control
        # itself. Measured while writing this file.
        try:
            rel = str(f.relative_to(repo_root()))
        except ValueError:
            rel = str(f)
        if not km:
            absent.append(rel)
            continue
        value = km.group(1).strip().lower()
        nm = NAME_RE.search(fm)
        name = nm.group(1).strip() if nm else f.parent.name
        if value in ("false", "no", "off"):
            desc = description_of(fm)
            if re.search(rf"/{re.escape(name)}\b", desc):
                contradictions.append({"file": rel, "skill": name,
                                       "declared": value,
                                       "evidence": f"description names /{name}"})

    rc = 0
    if absent:
        rc = 1
        print(f"{CHECK}: FAIL — A1: `user-invocable:` absent (tri-state UNKNOWN, not false) in: "
              + ", ".join(absent), file=sys.stderr)
    if contradictions:
        rc = 1
        for c in contradictions:
            print(f"{CHECK}: FAIL — A2: {c['file']} declares user-invocable: {c['declared']} "
                  f"while its {c['evidence']}", file=sys.stderr)

    result = {
        "check": CHECK,
        "verdict": "PASS" if rc == 0 else "FAIL",
        "skills_inspected": inspected,
        "absent": absent,
        "contradictions": contradictions,
        # REQ-CHECK-009(a): declare what this instrument does NOT cover.
        "not_checked": [
            "whether a `user-invocable: true` declaration is CORRECT — a skill may be a genuine "
            "slash entry point without naming itself in its own description (A2 is one-directional "
            "by construction, and the reverse predicate has no mechanical source of truth)",
        ],
    }
    if args.json:
        print(json.dumps(result, indent=2))
    elif rc == 0:
        print(f"{CHECK}: {inspected} SKILL.md inspected; all populate `user-invocable:`; "
              f"0 declaration/description contradictions")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
