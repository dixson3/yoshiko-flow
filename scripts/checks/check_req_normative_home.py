#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_req_normative_home.py — every REQ id a plan's amendment-log entry CLAIMS to add has a
NORMATIVE definition in the spec that owns its namespace.

The gap this closes is narrow and was reachable: ``check_amendment_log.py`` asserts the reverse
direction — every id an Epic-0 issue *names* carries an amendment-log *bullet*. Both sides of
that check live in prose. So a plan could announce ``Added REQ-CHECK-013`` in the log, ship the
implementation, and never write the requirement anywhere a later reader could find it — and every
existing check would stay green. An amendment log is a CHANGE RECORD; it is not the requirement.

PREDICATE.  For each ``REQ-<KEY>-NNN`` id appearing in the named plan's root-``SPEC.md``
amendment-log entry under an ``Added`` claim, a line matching ``**REQ-<KEY>-NNN:`` shall exist in
the spec file registered for ``<KEY>`` below.  Ids the entry only *revises*, *cites* or *amends*
are out of scope: their normative home already exists and may legitimately live elsewhere.

VACUITY FLOOR.  ``--min-ids`` (default 1). An entry claiming no additions is INCONCLUSIVE here,
not a pass — this script has then inspected nothing.

EXIT  0 every added id has a normative home  ·  1 at least one does not  ·  2 INCONCLUSIVE
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CHECK = "check_req_normative_home"

# Namespace -> the spec file that owns its normative text. Hand-authored, and stated as this
# instrument's soundness limit rather than hidden: a namespace absent from this table is
# reported as unmapped (INCONCLUSIVE), never silently skipped.
NAMESPACE_HOME = {
    "CHECK": "skills/yf-drift-check/spec/checks.md",
    "DRIFT": "skills/yf-drift-check/spec/engine.md",
}

REQ_RE = re.compile(r"REQ-([A-Z]+(?:-[A-Z]+)*)-(\d{3})")
ADDED_RE = re.compile(r"\*\*Added ([^*]*?)\*\*", re.S)


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def repo_root() -> Path:
    try:
        return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True, check=True).stdout.strip())
    except Exception:
        return Path(__file__).resolve().parent.parent.parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True, help="plan id, e.g. plan-067-james-dixson-de852a")
    ap.add_argument("--spec", default=None)
    ap.add_argument("--min-ids", type=int, default=1)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = repo_root()
    spec = Path(args.spec) if args.spec else root / "SPEC.md"
    if not spec.is_file():
        inconclusive(f"no SPEC.md at {spec}")
    text = spec.read_text(encoding="utf-8")

    num = args.plan.split("-")[1]
    m = re.search(rf"^> - \*\*plan-{num} \(", text, re.M)
    if not m:
        inconclusive(f"SPEC.md has no amendment-log entry for plan-{num}")
    tail = text[m.start():]
    nxt = re.search(r"^> - \*\*", tail[1:], re.M)
    entry = tail[: nxt.start() + 1] if nxt else tail

    added: set[str] = set()
    for claim in ADDED_RE.findall(entry):
        added |= {f"REQ-{k}-{n}" for k, n in REQ_RE.findall(claim)}

    if len(added) < args.min_ids:
        inconclusive(f"the plan-{num} entry claims {len(added)} added id(s), below the "
                     f"--min-ids floor of {args.min_ids} — nothing was inspected")

    missing, unmapped = [], []
    homes: dict[str, str] = {}
    for rid in sorted(added):
        key = REQ_RE.match(rid).group(1)
        rel = NAMESPACE_HOME.get(key)
        if rel is None:
            unmapped.append(rid)
            continue
        homes[rid] = rel
        f = root / rel
        if not f.is_file():
            inconclusive(f"namespace home {rel} for {rid} does not exist")
        if f"**{rid}:" not in f.read_text(encoding="utf-8"):
            missing.append(f"{rid} (no `**{rid}:` line in {rel})")

    rc = 0
    if unmapped:
        inconclusive("no namespace home registered for: " + ", ".join(unmapped))
    if missing:
        rc = 1
        print(f"{CHECK}: FAIL — the plan-{num} entry claims to ADD id(s) that have no normative "
              "definition: " + "; ".join(missing), file=sys.stderr)

    result = {"check": CHECK, "verdict": "PASS" if rc == 0 else "FAIL",
              "plan": args.plan, "added_ids": sorted(added), "homes": homes,
              "missing": missing,
              "not_checked": [
                  "ids the entry REVISES/AMENDS/CITES rather than adds — their normative home "
                  "already exists and may legitimately live in another spec",
                  "whether the normative text is CORRECT or merely present (a prose judgement, "
                  "REQ-CHECK-009(a))",
              ]}
    if args.json:
        print(json.dumps(result, indent=2))
    elif rc == 0:
        print(f"{CHECK}: plan-{num} adds {len(added)} id(s); all have a normative definition "
              f"in their registered namespace home")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
