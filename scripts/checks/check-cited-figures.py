#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check-cited-figures.py <registry.md> — re-measure every cited figure and report drift.

plan-060 Issue 0.10, `dixson3/yoshiko-flow#289`.

WHAT IT DOES. Reads a bundle's `cited-figures.md` registry — a GFM table of
`id | quoted | command` — runs each command under ``bash -c`` (the same shell
``recheck-criteria`` uses), and diffs the printed value against the quoted one.

WHY ``bash -c`` AND NOT THE AMBIENT SHELL. Measured in this repository, in the interactive
shell *and* under the agent harness: ``grep`` resolves to a **ugrep shell function** that
honours ``.gitignore``. A figure re-measured in a shell that is not the shell the figure's
consumer uses is a figure measured against a different file set. The shell is therefore
pinned, and it is pinned to the one ``recheck-criteria`` actually uses.

THE VERDICT IS THREE-VALUED, AND THE THIRD VALUE IS THE POINT (#263).

    0  every figure was measured and MATCHES its quoted value
    1  at least one figure DRIFTED — measured, and different
    2  INCONCLUSIVE — the registry could not be read, it is empty, or **every** figure that
       could be measured was inconclusive

A figure whose command exits 2 is reported ``inconclusive`` and does **not** become a drift.
"The instrument could not run" and "the number is wrong" are different facts, and collapsing
them is the defect class #263 catalogues — the same conflation as ``doc_lint``'s
``not-selected`` vs ``no-such-path`` (#181) and ``resume-scan``'s ``found`` (#207). An
INCONCLUSIVE matters most for **absence figures** (a quoted ``0``), where a missing
instrument and a genuine zero are indistinguishable from the exit code alone.

FAIL-LOUD ON AN EMPTY INSPECTION (REQ-CLI-029(b)). A registry that parses to zero rows
certifies nothing, so it is INCONCLUSIVE rather than a clean pass. ``--min-figures`` raises
the floor above the default 1.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROW = re.compile(r"^\|\s*`([a-z0-9-]+)`\s*\|\s*([^|]+?)\s*\|\s*`(.+?)`\s*\|\s*$")


def parse_registry(text: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in text.splitlines():
        m = ROW.match(line)
        if m:
            rows.append((m.group(1), m.group(2).strip(), m.group(3).strip()))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("registry", type=Path)
    ap.add_argument("--min-figures", type=int, default=1,
                    help="floor below which the run is INCONCLUSIVE (default 1)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not args.registry.is_file():
        print(f"check-cited-figures: INCONCLUSIVE — no registry at {args.registry}",
              file=sys.stderr)
        return 2

    rows = parse_registry(args.registry.read_text(encoding="utf-8"))
    if len(rows) < max(1, args.min_figures):
        print(f"check-cited-figures: INCONCLUSIVE — parsed {len(rows)} figure row(s) "
              f"(floor {max(1, args.min_figures)}); a run over an empty registry certifies "
              f"vacuously", file=sys.stderr)
        return 2

    results = []
    for fid, quoted, cmd in rows:
        proc = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
        measured = proc.stdout.strip()
        if proc.returncode == 2 or (proc.returncode != 0 and not measured):
            status = "inconclusive"
            detail = (proc.stderr.strip() or f"command exited {proc.returncode}")
        elif measured == quoted:
            status, detail = "match", measured
        else:
            status, detail = "drift", f"quoted {quoted!r}, measured {measured!r}"
        results.append({"id": fid, "quoted": quoted, "measured": measured,
                        "status": status, "detail": detail, "cmd": cmd})

    drifted = [r for r in results if r["status"] == "drift"]
    inconc = [r for r in results if r["status"] == "inconclusive"]
    matched = [r for r in results if r["status"] == "match"]

    if args.json:
        print(json.dumps({"registry": str(args.registry), "figures": results,
                          "matched": len(matched), "drifted": len(drifted),
                          "inconclusive": len(inconc)}, indent=2))
    else:
        for r in results:
            print(f"  {r['id']:<24} {r['status']:<13} {r['detail']}")

    if not matched and not drifted:
        print("check-cited-figures: INCONCLUSIVE — every figure was inconclusive; nothing "
              "was actually re-measured", file=sys.stderr)
        return 2
    if drifted:
        print("check-cited-figures: FAIL — " + ", ".join(
            f"{r['id']} ({r['detail']})" for r in drifted), file=sys.stderr)
        return 1
    print(f"check-cited-figures: {len(matched)} figure(s) match"
          + (f"; {len(inconc)} inconclusive (NOT counted as matching)" if inconc else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
