#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate plan-052's control set from plan.md — never hand-maintained.

`assets/controls.txt` is a two-column TSV (`id`, `set`). Both columns are DERIVED:

* the **id** set is the union of the ids ASSERTED in `plan.md`'s Success Criteria
  `Verification` cells and the ids BUILT under `assets/controls/`;
* the **set** column comes from the BUILDER'S EPIC (0-4 core, 5-6 ext, 7 land), read
  from the `- touches:` sub-key that names `assets/controls/<id>.sh`. It is never
  hand-assigned, so a control cannot be silently moved between gates.

Prose globs (`ctl-199b-*`) are IGNORED: a hand-count that read them as ids reached 28
for a true 27.

An id with no builder is emitted with set `orphan`, which makes `verify-partition`
fail — that is the intended detection, not an error here.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

CTL_TOKEN = re.compile(r"\bctl-[a-z0-9]+(?:-[a-z0-9]+)*\b")
ISSUE_RE = re.compile(r"^- Issue (\d+\.\d+[a-z]?): ")
TOUCH_CTL_RE = re.compile(r"assets/controls/(ctl-[a-z0-9-]+)\.sh")
EPIC_RE = re.compile(r"^### Epic (\d+):")


def _section(text: str, heading: str) -> str:
    """Return the body of a `## <heading>` section."""
    lines = text.splitlines()
    out, inside = [], False
    for ln in lines:
        if ln.startswith("## "):
            inside = ln.strip() == f"## {heading}"
            continue
        if inside:
            out.append(ln)
    return "\n".join(out)


def asserted_ids(plan_text: str) -> list[str]:
    """Control ids named in Success Criteria `Verification` cells."""
    body = _section(plan_text, "Success Criteria")
    found: list[str] = []
    for ln in body.splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        verification = cells[2]
        for tok in CTL_TOKEN.findall(verification):
            # Ignore prose globs: a `*` anywhere in the token's immediate context.
            idx = verification.find(tok)
            tail = verification[idx + len(tok): idx + len(tok) + 1]
            if tail == "*" or "*" in tok:
                continue
            if tok not in found:
                found.append(tok)
    return found


def builders(plan_text: str) -> dict[str, tuple[str, str]]:
    """Map control id -> (builder issue id, builder epic number)."""
    body = _section(plan_text, "Epics")
    out: dict[str, tuple[str, str]] = {}
    epic = None
    issue = None
    for ln in body.splitlines():
        m = EPIC_RE.match(ln)
        if m:
            epic = m.group(1)
            continue
        m = ISSUE_RE.match(ln)
        if m:
            issue = m.group(1)
            continue
        if ln.strip().startswith("- touches:") and issue and epic:
            for cid in TOUCH_CTL_RE.findall(ln):
                out.setdefault(cid, (issue, epic))
    return out


def set_for_epic(epic: str) -> str:
    n = int(epic)
    if 0 <= n <= 4:
        return "core"
    if n in (5, 6):
        return "ext"
    if n == 7:
        return "land"
    return "orphan"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    here = pathlib.Path(__file__).resolve().parent
    ap.add_argument("--plan", default=str(here.parent / "plan.md"))
    ap.add_argument("--controls-dir", default=str(here / "controls"))
    ap.add_argument("--out", default=str(here / "controls.txt"))
    ap.add_argument("--asserted-only", action="store_true",
                    help="print the ASSERTED control ids, one per line, and exit")
    ap.add_argument("--builders-only", action="store_true",
                    help="print `<ctl-id>\\t<issue>\\t<epic>` for every builder, and exit")
    args = ap.parse_args()

    plan = pathlib.Path(args.plan)
    if not plan.is_file():
        print(f"INCONCLUSIVE: plan.md unreadable: {plan}", file=sys.stderr)
        return 2
    text = plan.read_text(encoding="utf-8")

    asserted = asserted_ids(text)
    if args.asserted_only:
        print("\n".join(asserted))
        return 0

    bmap = builders(text)
    if args.builders_only:
        for cid, (issue, epic) in sorted(bmap.items()):
            print(f"{cid}\t{issue}\t{epic}")
        return 0

    cdir = pathlib.Path(args.controls_dir)
    built = sorted(p.stem for p in cdir.glob("ctl-*.sh")) if cdir.is_dir() else []

    ids = sorted(set(asserted) | set(built))
    rows = [(cid, set_for_epic(bmap[cid][1]) if cid in bmap else "orphan") for cid in ids]

    out = pathlib.Path(args.out)
    out.write_text("".join(f"{cid}\t{s}\n" for cid, s in rows), encoding="utf-8")
    print(f"wrote {out} — {len(rows)} control(s): "
          f"{sum(1 for _, s in rows if s == 'core')} core, "
          f"{sum(1 for _, s in rows if s == 'ext')} ext, "
          f"{sum(1 for _, s in rows if s == 'land')} land, "
          f"{sum(1 for _, s in rows if s == 'orphan')} orphan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
