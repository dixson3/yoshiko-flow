#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_smoke_tier.py — SC14. The `harness-smoke` tier registration is FIXED and STAYS fixed.

## The defect this guards against

`harness-smoke` sat in `CHANGE-VALIDATION.md`'s ``### fast`` table while a blockquote directly
beneath it asserted the row was "FULL-tier ONLY, deliberately". Both halves were wrong in the
same direction:

* Measured against the engine, ``fast`` and ``full`` parse to **independent lists** — ``full`` is
  not a superset of ``fast``. So the row **never ran at FULL**, the land gate it was written for.
* And it **did** run on any unscoped ``--tier fast``, spending real ``pi``/``opencode`` model
  calls on the cheap on-edit tier.

The check is green-by-accident in both directions at once, which is why the fix is a registration
change rather than a script change.

## Three assertions, and the third is the one a naive checker misses

1. ``harness-smoke`` appears in **no** ``###`` tier table.
2. ``check_smoke_tier`` appears in ``### full`` — the static check takes the row's place, so the
   land gate still asserts something about the smoke without acquiring a live-harness dependency.
3. **No residual ``harness-smoke`` prose claim survives in §1.** This one matters because a
   manifest parser reads only ``|``-delimited rows: the orphaned blockquote asserting the row was
   "FULL-tier ONLY" is INVISIBLE to it, so a correct row-level checker would pass green over
   seven lines of false prose.

## Why the smoke is NOT simply moved into `### full`

SC19 runs ``--tier full``. The smoke exits **2 (INCONCLUSIVE)** when a harness is absent or
unauthenticated, and ``change_validation.py`` maps any nonzero row exit to ``fail`` — so moving it
would give the repo's land gate a hard dependency on three live, authenticated harnesses and real
model calls. That is the same dependency SC17 was made ``manual:`` to avoid; re-adding it as a
runnable criterion would be an internal contradiction rather than a trade-off. The re-add is
recorded as a follow-up, **blocked on** the upstream exit-2 mapping fix.

EXIT  0 registration is correct · 1 it is not · 2 CHANGE-VALIDATION.md is unparseable
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

MANIFEST = "CHANGE-VALIDATION.md"
SMOKE_ID = "harness-smoke"
REPLACEMENT = "check_smoke_tier"


def inconclusive(msg: str) -> None:
    print(f"check_smoke_tier: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def repo_root() -> Path:
    try:
        return Path(
            subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, check=True,
            ).stdout.strip()
        )
    except Exception:
        return Path.cwd()


def parse_tiers(text: str) -> dict[str, list[str]]:
    """`### <tier>` heading -> the raw `|`-delimited rows beneath it.

    Mirrors the engine: only pipe-delimited rows are recipe rows. Everything else — including a
    blockquote sitting inside a table — is prose the engine never sees.
    """
    tiers: dict[str, list[str]] = {}
    cur: str | None = None
    in_section_1 = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_section_1 = line.strip().startswith("## 1.")
            cur = None
            continue
        m = re.match(r"^### (\S+)", line)
        if m and in_section_1:
            cur = m.group(1)
            tiers.setdefault(cur, [])
            continue
        if cur is not None and line.lstrip().startswith("|"):
            tiers[cur].append(line)
    return tiers


def main() -> int:
    root = repo_root()
    path = root / MANIFEST
    if not path.is_file():
        inconclusive(f"no {MANIFEST} at {path}")
    text = path.read_text(encoding="utf-8")

    tiers = parse_tiers(text)
    if not tiers:
        inconclusive(f"{MANIFEST} parsed to ZERO tier tables — the manifest is unreadable")

    rc = 0

    # (1) the smoke appears in NO tier table.
    offenders = [t for t, rows in tiers.items() if any(f"`{SMOKE_ID}`" in r for r in rows)]
    if offenders:
        rc = 1
        print(
            f"check_smoke_tier: FAIL — `{SMOKE_ID}` is registered in tier table(s): "
            + ", ".join(sorted(offenders)),
            file=sys.stderr,
        )

    # (2) the static replacement is registered in `### full`.
    full = tiers.get("full")
    if full is None:
        inconclusive("no `### full` tier table — cannot judge the replacement's registration")
    if not any(REPLACEMENT in r for r in full):
        rc = 1
        print(
            f"check_smoke_tier: FAIL — `{REPLACEMENT}` is not registered in `### full`; the "
            "land gate would assert nothing about the smoke's tiering",
            file=sys.stderr,
        )

    # (3) NO residual prose claim about the smoke survives in §1. Invisible to a row-level
    #     parser, which is exactly why it is checked separately.
    try:
        s1 = text.index("## 1.")
    except ValueError:
        inconclusive("no `## 1.` section — the manifest layout changed")
    nxt = text.find("\n## ", s1 + 1)
    section_1 = text[s1 : nxt if nxt != -1 else len(text)]
    prose = [
        ln
        for ln in section_1.splitlines()
        if SMOKE_ID in ln and not ln.lstrip().startswith("|")
    ]
    if prose:
        rc = 1
        print(
            f"check_smoke_tier: FAIL — residual `{SMOKE_ID}` PROSE survives in §1. A row-level "
            "parser cannot see it, so it would outlive the row it describes:",
            file=sys.stderr,
        )
        for ln in prose:
            print(f"    {ln.strip()}", file=sys.stderr)

    if rc == 0:
        print(
            f"check_smoke_tier: `{SMOKE_ID}` is in no tier table, no §1 prose claims it, and "
            f"`{REPLACEMENT}` is registered in `### full`"
        )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
