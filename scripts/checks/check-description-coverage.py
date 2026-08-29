#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""SC5 / REQ-DATA-075 — the `description:` producer contract holds over a bundle's NESTED
artifacts: the producers stamped what the linter check requires.

SCOPE IS THE NON-EXEMPT NESTED TYPES ONLY, and every part of that is declared rather than
inferred (REQ-DATA-075):

  * NESTED — files BELOW the bundle root. The root's own `plan.md` / `context.md` /
    `upstream-triage.md` are a different population with different producers.
  * NON-EXEMPT — `context.md` and `plan-retrospective.md` are EXEMPT: a derived description
    there is the same string in every bundle (measured: 67 identical copies), and a key whose
    value is constant across the corpus carries zero information while diluting the ones that
    do not.
  * RESERVED `index.md` / `log.md` carry no frontmatter at all (REQ-OKF-031), so they are
    outside the population by construction, not by exemption.

AN EMPTY STRING DOES NOT SATISFY IT. The pattern is `^description:\\s*\\S`, matching the
linter check REQ-DATA-075 pairs with this — otherwise the producer could satisfy the criterion
by stamping the key and no value, which is the "asserting something nothing checks" failure
one level down.

FAIL-LOUD ON AN EMPTY INSPECTION (REQ-CLI-029(b)): `--min-files`.

EXIT  0 every non-exempt nested artifact carries a non-empty description
      1 at least one does not
      2 could not run
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CHECK = "check-description-coverage"
DESC_RE = re.compile(r"^description:\s*\S", re.MULTILINE)

# DECLARED exemptions (REQ-DATA-075). An inferred exemption is indistinguishable from an
# unstamped producer, which is the whole defect this check exists to detect.
EXEMPT_NAMES = {"index.md", "log.md", "context.md", "plan-retrospective.md"}


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def frontmatter(p: Path) -> str | None:
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if not t.startswith("---"):
        return ""
    end = t.find("\n---", 3)
    return t[3:end] if end >= 0 else ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("plan_dir", type=Path)
    ap.add_argument("--min-files", type=int, default=1,
                    help="fail-loud floor on the number of nested artifacts inspected")
    a = ap.parse_args()

    if not a.plan_dir.is_dir():
        inconclusive(f"no such plan dir: {a.plan_dir}")

    # The member's own §3b exclusions apply here too (REQ-OKF-CHK-003) — a deliberate
    # non-conformant fixture is not an artifact this contract judges.
    excludes: list[str] = []
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "_shared"))
        import okf  # noqa: PLC0415
        excludes = list(okf.resolve_extension("yf-plan").exclude_globs)
    except Exception:
        excludes = []

    def excluded(rel: str) -> bool:
        try:
            return okf.is_excluded(rel, excludes)  # type: ignore[name-defined]
        except Exception:
            return False

    missing, inspected = [], 0
    for f in sorted(a.plan_dir.rglob("*.md")):
        if f.parent == a.plan_dir:
            continue                       # ROOT level — a different population
        rel = f.relative_to(a.plan_dir).as_posix()
        if f.name in EXEMPT_NAMES or excluded(rel):
            continue
        inspected += 1
        fm = frontmatter(f)
        if fm is None:
            inconclusive(f"could not read {rel}")
        if not DESC_RE.search(fm):
            missing.append(rel)

    if inspected < a.min_files:
        inconclusive(f"inspected only {inspected} nested artifact(s) (floor {a.min_files}) — "
                     "this run would certify vacuously")

    print(f"{CHECK}: {inspected} non-exempt nested artifact(s) inspected, "
          f"{inspected - len(missing)} carry a non-empty `description:`")
    if missing:
        for m in missing[:40]:
            print(f"  MISSING description: {m}", file=sys.stderr)
        print(f"{CHECK}: FAIL — {len(missing)} nested artifact(s) carry no non-empty "
              "`description:` (REQ-DATA-075)", file=sys.stderr)
        return 1
    print(f"{CHECK}: the `description:` producer contract holds over {a.plan_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
