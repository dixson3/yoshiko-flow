#!/usr/bin/env bash
# ctl-baseline-pathspec (SC1b) — every baseline figure is recorded WITH its verbatim pathspec.
#
# A figure without the command that produced it cannot be re-measured, so it is only ever as
# true as the last time a human read it. This plan's own prose carried three hand-counts that
# were wrong (7/24, 31-for-30, 47-for-49) and two stale corpus figures that reached the SPEC.
#
# The control checks the RECORD, not the figures: it never re-runs the commands. A baseline is
# by definition a PRE-FIX observation that a post-fix tree is expected to contradict —
# re-running is `recheck-criteria`'s job, on a different document.
#
# Exit: 0 every row carries a pathspec · 1 a real negative (missing file, or a bare figure)
#       · 2 the instrument could not run (unreadable/malformed record)
set -uo pipefail
ASSETS="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 - "$ASSETS" <<'PYEOF'
import pathlib, re, sys

assets = pathlib.Path(sys.argv[1])
doc = assets / "baseline-pre-fix.md"

# A MISSING declared artifact is exit 1 (a real negative); unreadable/malformed is exit 2.
if not doc.exists():
    print(f"FAIL: declared baseline record is absent: {doc}", file=sys.stderr)
    raise SystemExit(1)
try:
    text = doc.read_text(encoding="utf-8")
except OSError as e:
    print(f"INCONCLUSIVE: baseline record unreadable: {e}", file=sys.stderr)
    raise SystemExit(2)

def cells(line):
    """Split a GFM table row on UNESCAPED pipes, then unescape (REQ-DATA-070).

    A naive split on "|" truncates every cell containing an escaped pipe — which is exactly
    risk R9, and it fired on this control's own first draft. A cell inside a GFM table is
    necessarily escaped, so the unescape is not optional.
    """
    out, buf, i = [], [], 0
    body = line.strip()
    body = body[1:] if body.startswith("|") else body
    body = body[:-1] if body.endswith("|") and not body.endswith(r"\|") else body
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            buf.append(body[i + 1]); i += 2; continue
        if ch == "|":
            out.append("".join(buf).strip()); buf = []; i += 1; continue
        buf.append(ch); i += 1
    out.append("".join(buf).strip())
    return out

findings, rows, tables = [], 0, 0
header = None
for ln in text.splitlines():
    if not ln.startswith("|"):
        header = None
        continue
    c = cells(ln)
    if header is None:
        # first table line is the header; the next is the alignment row
        if any(h.lower().startswith("pathspec") for h in c):
            header = c
            tables += 1
        continue
    if all(set(x) <= set(":- ") for x in c if x):
        continue  # alignment row
    try:
        col = next(i for i, h in enumerate(header) if h.lower().startswith("pathspec"))
    except StopIteration:
        continue
    rows += 1
    ident = c[0] if c else "?"
    if col >= len(c) or not c[col]:
        findings.append(f"row {ident}: NO pathspec/command cell")
    elif not re.search(r"`[^`]+`|\*\*no\*\*", c[col]):
        findings.append(f"row {ident}: pathspec cell carries no command: {c[col]!r}")

if tables == 0 or rows == 0:
    print("INCONCLUSIVE: baseline record has no figure table with a "
          "'Pathspec / command' column", file=sys.stderr)
    raise SystemExit(2)

# Non-vacuous floor: a record with one row would pass trivially.
if rows < 10:
    findings.append(f"baseline record has only {rows} figure(s); expected >= 10")

if findings:
    print(f"FAIL: {len(findings)} baseline finding(s):", file=sys.stderr)
    for f in findings:
        print(f"  - {f}", file=sys.stderr)
    raise SystemExit(1)

print(f"PASS: {rows} baseline figure(s) across {tables} table(s), each recorded "
      f"with its verbatim pathspec")
PYEOF
