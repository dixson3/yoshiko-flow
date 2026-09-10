#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""SC9b — plan-068's recorded REQ allocation and its landed SPEC diff must agree BOTH ways.

The one-directional form (`every recorded id is in the diff`) could never catch the over-claim
pass-4 C6 found, where the plan named `REQ-LAND-018` / `REQ-LAND-036` as its own while both
belong to plan-069. So this reports **both** set differences and exits 0 only when both are
empty.

Exit contract, three-valued:
  0  both directions agree
  1  a divergence in either direction (the SC9b failure)
  2  INCONCLUSIVE — the comparison could not be made (missing base file, unresolvable base,
     unreadable record). A statement about the instrument, never a verdict on the plan.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent
BUNDLE = ASSETS.parent
SPEC_PATHS = ["skills/yf-plan/spec/", "SPEC.md"]
REQ_RE = re.compile(r"REQ-[A-Z]+-\d+")


def inconclusive(msg: str) -> int:
    print(f"INCONCLUSIVE: {msg}", file=sys.stderr)
    return 2


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=ASSETS, capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise RuntimeError("not a git repository")
    return Path(out.stdout.strip())


def recorded_ids() -> set[str]:
    """The id set of the allocation TABLE — not of the surrounding prose.

    Prose deliberately names ids this plan does NOT own (REQ-LAND-018, REQ-LAND-036, the
    reserved REQ-LAND-027) in order to record that it does not own them. Reading the whole
    file would pull those back in and make the check assert the opposite of what it means.
    Only rows whose FIRST cell is a backticked id count.
    """
    record = BUNDLE / "assets" / "req-allocation.md"
    if not record.is_file():
        raise RuntimeError(f"missing allocation record: {record}")
    ids: set[str] = set()
    for line in record.read_text().splitlines():
        m = re.match(r"^\|\s*`(REQ-[A-Z]+-\d+)`\s*\|", line)
        if m:
            ids.add(m.group(1))
    if not ids:
        raise RuntimeError("allocation table parsed to zero ids")
    return ids


def diff_ids(root: Path, base: str) -> set[str]:
    """Ids appearing on ADDED or REMOVED diff lines, over the SPEC paths only."""
    out = subprocess.run(
        ["git", "diff", "-U0", f"{base}..HEAD", "--", *SPEC_PATHS],
        cwd=root, capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise RuntimeError(f"git diff failed: {out.stderr.strip()}")
    ids: set[str] = set()
    for line in out.stdout.splitlines():
        if line.startswith(("+++", "---")):
            continue
        if line.startswith(("+", "-")):
            ids.update(REQ_RE.findall(line))
    return ids


def main() -> int:
    try:
        root = repo_root()
        base_file = BUNDLE / "assets" / "execute-base.txt"
        if not base_file.is_file():
            return inconclusive(f"missing recorded execute base: {base_file}")
        base = base_file.read_text().strip()
        if not base:
            return inconclusive("recorded execute base is empty")
        probe = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}"],
            cwd=root, capture_output=True, text=True,
        )
        if probe.returncode != 0:
            return inconclusive(f"recorded base {base!r} does not resolve to a commit")
        recorded = recorded_ids()
        landed = diff_ids(root, base)
    except RuntimeError as exc:
        return inconclusive(str(exc))

    if not landed:
        return inconclusive(
            f"the SPEC diff against {base[:8]} is EMPTY — no SPEC change has landed yet, so "
            "there is nothing to compare the record against"
        )

    missing_from_record = sorted(landed - recorded)
    missing_from_diff = sorted(recorded - landed)

    print(f"base:     {base}")
    print(f"recorded: {len(recorded)} — {', '.join(sorted(recorded))}")
    print(f"landed:   {len(landed)} — {', '.join(sorted(landed))}")

    if not missing_from_record and not missing_from_diff:
        print("PASS: the recorded allocation and the landed SPEC diff agree in both directions.")
        return 0

    if missing_from_record:
        print(
            "FAIL (diff -> record): these ids are in the landed SPEC diff but NOT recorded in "
            f"assets/req-allocation.md: {', '.join(missing_from_record)}"
        )
    if missing_from_diff:
        print(
            "FAIL (record -> diff): these ids are recorded as this plan's but do NOT appear in "
            f"the landed SPEC diff — an OVER-CLAIM: {', '.join(missing_from_diff)}"
        )
    return 1


if __name__ == "__main__":
    sys.exit(main())
