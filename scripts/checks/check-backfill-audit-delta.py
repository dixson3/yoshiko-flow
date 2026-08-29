#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""SC12 — NO BACKFILLED BUNDLE'S AUDIT VERDICT IS WORSE AFTER THE RUN THAN BEFORE IT.

--- WHY THIS IS ONE OF THREE GUARANTEES AND NOT AN EXTRA ---------------------------------
The content fingerprint covers `plan.md`'s content sections ONLY. It excludes `README.md`,
`index.md` and `log.md` entirely — that is, EVERY FILE THE BACKFILL MUTATES — and it excludes
the header preamble, which is exactly where migration adds frontmatter. A "byte-identical"
result over it is therefore very nearly a TAUTOLOGY. The real guarantees are three separate
fail-closed preconditions: fingerprint invariance, phase-log bullet-and-date equality, and THIS
per-bundle audit delta.

The delta matters because the failure mode is not "the transform corrupted a file" — it is
"the transform left a bundle failing an audit it previously passed". `okf_missing_level` flips
from `warn` to `fail` the moment `plan.md` gains frontmatter, so a half-done backfill is
STRICTLY WORSE THAN NONE, and only a before/after comparison can see that.

--- THE RECORD FORMAT (produced by `okf_hygiene.py backfill --record <path>`) --------------
    {
      "bundles": [
        {"bundle": "docs/plans/plan-010-…",
         "before": {"verdict": "warn"},
         "after":  {"verdict": "pass"}},
        …
      ]
    }

`verdict` is ordered `pass < warn < fail`. AFTER strictly worse than BEFORE is the failure.
An `inconclusive` on either side is an INSTRUMENT condition, not a corpus finding, and exits 2
— never 1, which would report a harness fault as data loss.

`--record` accepts an ABSOLUTE path and must not crash on one (REQ-CLI-029(d)).

EXIT  0 no bundle regressed  ·  1 at least one did  ·  2 could not run / empty inspection
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CHECK = "check-backfill-audit-delta"

# `pass < warn < fail`. A HIGHER rank is WORSE.
RANK = {"pass": 0, "clean": 0, "ok": 0, "warn": 1, "warning": 1, "fail": 2, "error": 2}


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def verdict_of(side: object, bundle: str, which: str) -> tuple[str, int]:
    if isinstance(side, str):
        raw = side
    elif isinstance(side, dict):
        raw = str(side.get("verdict", ""))
    else:
        inconclusive(f"{bundle}: `{which}` is neither a string nor an object")
    key = raw.strip().lower()
    if key not in RANK:
        # `inconclusive` lands here deliberately, with every other unknown token.
        inconclusive(f"{bundle}: `{which}` verdict {raw!r} is not one of "
                     f"pass/warn/fail — an unrankable verdict is an instrument condition, "
                     f"not a regression")
    return key, RANK[key]


def main() -> int:
    ap = argparse.ArgumentParser(description="SC12 backfill audit-delta comparator")
    ap.add_argument("--record", required=True, type=Path,
                    help="the per-bundle audit record `backfill --record` wrote")
    ap.add_argument("--min-bundles", type=int, default=1,
                    help="fail-loud floor on how many bundles the record carries")
    args = ap.parse_args()

    record = args.record if args.record.is_absolute() else Path.cwd() / args.record
    try:
        data = json.loads(record.read_text(encoding="utf-8"))
    except OSError as exc:
        # A MISSING RECORD IS AN INSTRUMENT CONDITION, not a green. Reporting 0 here would
        # certify a backfill that never ran.
        inconclusive(f"cannot read the record at {record}: {exc}")
    except json.JSONDecodeError as exc:
        inconclusive(f"the record at {record} is not JSON: {exc}")

    if isinstance(data, list):
        bundles = data
    elif isinstance(data, dict):
        bundles = data.get("bundles", [])
    else:
        inconclusive(f"the record at {record} is neither a list nor an object")

    if not isinstance(bundles, list):
        inconclusive("the record's `bundles` key is not a list")

    # FAIL LOUDLY ON AN EMPTY INSPECTION (REQ-CLI-029(b)). An empty record satisfies
    # "no bundle regressed" for every bundle it does not mention.
    if len(bundles) < args.min_bundles:
        inconclusive(f"the record carries {len(bundles)} bundle(s), "
                     f"--min-bundles {args.min_bundles} — a record naming nothing "
                     f"certifies nothing")

    regressions: list[str] = []
    for entry in bundles:
        if not isinstance(entry, dict):
            inconclusive("a record entry is not an object")
        name = str(entry.get("bundle", "<unnamed>"))
        if "before" not in entry or "after" not in entry:
            inconclusive(f"{name}: the entry lacks a `before` and/or `after` verdict — "
                         "a delta needs both sides")
        b_name, b_rank = verdict_of(entry["before"], name, "before")
        a_name, a_rank = verdict_of(entry["after"], name, "after")
        arrow = "=" if a_rank == b_rank else ("->" if a_rank < b_rank else "!!")
        print(f"  {name}: {b_name} {arrow} {a_name}")
        if a_rank > b_rank:
            regressions.append(f"{name} ({b_name} -> {a_name})")

    print(f"{CHECK}: {len(bundles)} bundle(s) compared")
    if regressions:
        print(f"{CHECK}: FAIL — {len(regressions)} bundle(s) are WORSE after the backfill "
              f"than before it: {', '.join(regressions)}", file=sys.stderr)
        return 1
    print(f"{CHECK}: no bundle's audit verdict regressed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
