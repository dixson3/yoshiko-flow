#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# ///
"""Acceptance check for REQ-BUP-053 / GR-BUP-005: no PRESCRIPTIVE raw `bd <backend>`
push survives in SKILL.md.

Run:  uv run skills/yf-beads-upstream/scripts/check_prescriptive_push.py
Exit: 0 = clean, 1 = a prescriptive raw push was reintroduced.

WHY THIS IS SCOPED AND NOT A GLOBAL GREP
----------------------------------------
`bd github push` appears ~20 times in SKILL.md and only a handful are procedure. The
rest are load-bearing EXPLANATION:

  * the Safety invariants quote the command **in order to forbid it**;
  * two dated blockquotes record empirical verification against a specific bd build;
  * the backend translation table documents what the verb emits on your behalf;
  * the three-mechanism section disambiguates this push from `bd dolt push`.

A check asserting "zero occurrences of `bd github push`" would fail on the invariant
statements themselves — pressuring a future editor into deleting the very rule this
check exists to protect. So the boundary is MECHANICAL (REQ-BUP-053):

  PROCEDURE   = fenced ```bash blocks inside the Push step and Backend generalization
                sections. These are what a reader copies and runs.
  EXPLANATION = everything else — prose, tables, blockquotes. Never flagged.

KNOWN SCOPE LIMIT (stated, not hidden)
--------------------------------------
This check covers fenced procedure blocks only. A prescriptive instruction written in
PROSE ("prefer running `bd jira push <ids>`") is out of its reach by construction —
that is the price of a boundary a machine can enforce without false positives. Prose
prescription is caught by human review; plan-038 Issue 3.3 fixed one such site that a
grep would also have missed, because the audit read the sections end to end.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# The two sections whose fenced blocks are operator-facing procedure (REQ-BUP-053).
GUARDED_SECTIONS = ("Push step", "Backend generalization")

# A raw push/sync against any backend, as it would appear in a runnable command.
RAW_PUSH_RE = re.compile(r"\bbd\s+(github|gitlab|jira)\s+(push|sync)\b")

FENCE_RE = re.compile(r"```bash\n(.*?)```", re.S)
H2_RE = re.compile(r"^## (.+)$", re.M)


def guarded_spans(text: str) -> list[tuple[int, int, str]]:
    """(start, end, title) byte spans of the `##` sections this check guards."""
    heads = [(m.start(), m.group(1).strip()) for m in H2_RE.finditer(text)]
    spans = []
    for i, (start, title) in enumerate(heads):
        if not any(title.startswith(g) for g in GUARDED_SECTIONS):
            continue
        end = heads[i + 1][0] if i + 1 < len(heads) else len(text)
        spans.append((start, end, title))
    return spans


def violations(text: str) -> list[dict]:
    """Prescriptive raw pushes: a RAW_PUSH_RE match inside a fenced bash block that
    is itself inside a guarded section."""
    found = []
    for start, end, title in guarded_spans(text):
        for block in FENCE_RE.finditer(text, start, end):
            body = block.group(1)
            m = RAW_PUSH_RE.search(body)
            if not m:
                continue
            offending = next(
                (ln.strip() for ln in body.splitlines() if RAW_PUSH_RE.search(ln)), ""
            )
            found.append(
                {
                    "section": title,
                    "line": text[: block.start() + block.group(0).index(offending)].count("\n") + 1
                    if offending in block.group(0)
                    else text[: block.start()].count("\n") + 1,
                    "command": offending,
                }
            )
    return found


def main() -> int:
    skill = Path(__file__).resolve().parent.parent / "SKILL.md"
    if not skill.exists():
        print(f"ERROR: {skill} not found", file=sys.stderr)
        return 1
    text = skill.read_text(encoding="utf-8")

    bad = violations(text)
    if bad:
        print("FAIL: prescriptive raw `bd <backend>` push in a fenced procedure block")
        print("      (REQ-BUP-053 / GR-BUP-005). Route it through `upstream.py push`.\n")
        for v in bad:
            print(f"  SKILL.md:{v['line']}  [{v['section']}]  {v['command']}")
        return 1

    # Positive half: the explanatory mentions MUST still be there. A "clean" result
    # produced by deleting the invariants is a regression, not a pass.
    missing = [
        label
        for label, needle in (
            ("never-bare-sync invariant", "bd <backend> sync"),
            ("dated verification blockquote", "Verified (bd 1.0.5"),
            ("mapping-lost tripwire", "Would update in GitHub"),
        )
        if needle not in text
    ]
    if missing:
        print("FAIL: an explanatory mention this check is meant to PROTECT is gone:")
        for m in missing:
            print(f"  - {m}")
        print("\nThe check is scoped to procedure blocks precisely so these survive.")
        return 1

    guarded = len(guarded_spans(text))
    print(f"PASS: {guarded} guarded section(s); no prescriptive raw push in a fenced block.")
    print("      Explanatory mentions (invariants, dated blockquotes, tripwire) intact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
