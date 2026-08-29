#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""SC3 — deepening the root index LOWERS the share of byte-identical boilerplate entries.

THE EXTRACTION RULE IS STATED HERE AND IN THE CRITERION, because it was not written down once
and three independent readings then produced three different triples (257/127/142,
254/116/138, 210/72/138) of what was nominally one measurement:

  * an ENTRY is a line matching ``^- \\[`` in a bundle's ``index.md``;
  * its DESCRIPTION is the text after the FIRST ``) - `` on that line;
  * a line with no ``) - `` is an entry with no description and is excluded from the ratio's
    denominator, not counted as a distinct description.

THE DENOMINATOR IS FROZEN, AND THAT IS THE WHOLE POINT. Measured over ALL indexed bundles the
ratio is already BETTER than the baseline with zero index-deepening work, purely because newer
bundles carry richer indexes — so an open denominator makes this criterion green by arithmetic
rather than by the work it is supposed to measure. ``--frozen-set`` names bundles that all
PREDATE the baseline, so the ratio cannot be moved by adding bundles.

THE COMPARATOR IS STRICT ``<``. A ``<=`` implementation is satisfied by zero change, which is
this repository's own recurring defect class one abstraction layer down.

EXIT  0 the current ratio is STRICTLY LOWER than the baseline
      1 it is not lower (equal or higher) — the criterion does not hold
      2 could NOT RUN: an unreadable frozen set, an unparseable ``--baseline``, or an empty
        inspection. Reserved for the instrument, never for the corpus.

``--root`` accepts an ABSOLUTE path and must not crash on one (REQ-CLI-029(d)).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

CHECK = "check-index-boilerplate-ratio"


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def read_frozen_set(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        inconclusive(f"cannot read the frozen set at {path}: {exc}")
    names = [ln.strip() for ln in text.splitlines()
             if ln.strip() and not ln.lstrip().startswith("#")]
    if not names:
        inconclusive(f"the frozen set at {path} names no bundle — nothing to inspect")
    return names


def descriptions(index_md: Path) -> tuple[int, list[str]]:
    """(entry count, descriptions) under the stated extraction rule."""
    try:
        lines = index_md.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        inconclusive(f"cannot read {index_md}: {exc}")
    entries = 0
    descs: list[str] = []
    for ln in lines:
        if not ln.startswith("- ["):
            continue
        entries += 1
        marker = ln.find(") - ")
        if marker != -1:
            descs.append(ln[marker + 4:].strip())
    return entries, descs


def parse_baseline(spec: str) -> float:
    try:
        num, den = spec.split("/", 1)
        n, d = int(num), int(den)
    except ValueError:
        inconclusive(f"--baseline must be N/D (e.g. 126/184); got {spec!r}")
    if d <= 0:
        inconclusive(f"--baseline denominator must be positive; got {spec!r}")
    return n / d


def main() -> int:
    ap = argparse.ArgumentParser(description="SC3 boilerplate-ratio comparator")
    ap.add_argument("--baseline", required=True,
                    help="the baseline as REPEATED/DESCRIBED, e.g. 126/184")
    ap.add_argument("--frozen-set", required=True, type=Path,
                    help="file naming the frozen denominator bundles, one per line")
    ap.add_argument("--root", default="docs/plans", type=Path,
                    help="directory the frozen names are resolved under (absolute is fine)")
    ap.add_argument("--min-bundles", type=int, default=1,
                    help="fail-loud floor on how many bundles were actually inspected")
    args = ap.parse_args()

    baseline = parse_baseline(args.baseline)
    names = read_frozen_set(args.frozen_set)

    # An ABSOLUTE root is ordinary, not exceptional. Resolving with `/` handles both, and no
    # glob is expanded here at all — the frozen set NAMES its bundles, which is the reason a
    # pathlib pattern crash cannot happen on this path.
    root = args.root if args.root.is_absolute() else Path.cwd() / args.root

    inspected = 0
    missing: list[str] = []
    entries_total = 0
    descs: list[str] = []
    for name in names:
        index_md = root / name / "index.md"
        if not index_md.is_file():
            missing.append(name)
            continue
        n_entries, n_descs = descriptions(index_md)
        entries_total += n_entries
        descs.extend(n_descs)
        inspected += 1

    if missing:
        # A frozen bundle that is GONE makes the measurement incomparable to its baseline —
        # the denominator is no longer the one the baseline was struck over. That is an
        # instrument condition, not a corpus finding.
        inconclusive(f"{len(missing)} frozen bundle(s) have no index.md under {root}: "
                     f"{', '.join(missing[:5])}"
                     + (" …" if len(missing) > 5 else ""))

    # FAIL LOUDLY ON AN EMPTY INSPECTION (REQ-CLI-029(b)). Without this a run that resolved
    # zero bundles would divide by zero or, worse, report a ratio of 0.0 — a perfect score
    # earned by reading nothing.
    if inspected < args.min_bundles:
        inconclusive(f"inspected {inspected} bundle(s), --min-bundles {args.min_bundles}")
    if not descs:
        inconclusive(f"inspected {inspected} bundle(s) but found 0 described entries — "
                     "the extraction rule matched nothing, so there is no ratio to compare")

    described = len(descs)
    distinct = len(set(descs))
    repeated = described - distinct
    ratio = repeated / described

    print(f"{CHECK}: {inspected} frozen bundle(s) · entries {entries_total} · "
          f"described {described} · distinct {distinct} · repeated {repeated} · "
          f"ratio {ratio:.4f} (baseline {baseline:.4f})")

    if ratio < baseline:
        print(f"{CHECK}: ratio is strictly lower than the baseline")
        return 0
    print(f"{CHECK}: FAIL — ratio {ratio:.4f} is NOT strictly lower than the baseline "
          f"{baseline:.4f}; the comparator is `<`, so no change is not an improvement",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
