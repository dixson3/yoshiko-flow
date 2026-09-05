#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check-dual-home-amendment.py — the DUAL-HOME staleness `check_amendment_log.py` cannot see.

THE GAP THIS CLOSES, stated precisely. `check_amendment_log.py` reads the **root** `SPEC.md`
only. Several `REQ-*` ids are **dual-homed**: their normative body lives in a per-skill
`skills/<skill>/SPEC.md` while the root `SPEC.md` carries only the living-amendment-log entry.
So for a dual-homed id, *root alone satisfies that gate* — a plan can record an amendment in the
root log, never touch the per-skill body, and the SPEC-first gate goes green over a per-skill
copy that still states the superseded rule.

That is not a hypothetical: it is exactly what `plan-064` Issue 0.1's own text warns about
("root alone satisfies the gate but leaves the per-skill copy stale"), and it is the reason this
check exists rather than a prose reminder. A reminder has no exit code.

THE ASSERTION, over a DERIVED set — never a hand-enumerated one.

  1. Parse the plan's amendment-log entry out of the root ``SPEC.md`` and collect the ``REQ-*``
     ids it names. This is the set the plan CLAIMS to have amended.
  2. Intersect that set with the ids **normatively defined** in the per-skill SPEC files (a
     ``- **REQ-…**`` definition line). The intersection is the DUAL-HOMED set — the only ids for
     which this staleness is even possible.
  3. For each dual-homed id, require the per-skill definition body to carry a marker naming this
     plan (``plan-NNN``). A body with no such marker was not amended alongside the root log.

Deriving step 2 from the files is what keeps the check honest: a later plan that amends a
different dual-homed id is covered with no edit here, and an id that is NOT dual-homed is never
demanded to carry a marker it has no home for.

EXIT CONTRACT — three-valued, per `scripts/checks/_common.sh` (REQ-CLI-029).
    0  every dual-homed id the plan amended carries a per-skill amendment marker
    1  at least one does not — the per-skill copy is STALE
    2  INCONCLUSIVE — the check could not run, **including when the dual-homed set is EMPTY**.
       An empty set certifies vacuously (#263's class): it is indistinguishable from "this plan
       amended no dual-homed id" and "this check looked in the wrong place", and only one of
       those is fine. Refusing to score it is the point.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REQ_RE = re.compile(r"REQ-[A-Z]+(?:-[A-Z]+)*-\d{3}")
# A normative definition line, e.g. `- **REQ-OKF-012** *(testable)* …`
DEF_RE = re.compile(r"^- \*\*(REQ-[A-Z]+(?:-[A-Z]+)*-\d{3})\*\*")


def inconclusive(msg: str) -> None:
    print(f"check-dual-home-amendment: INCONCLUSIVE — {msg}", file=sys.stderr)
    sys.exit(2)


def repo_root() -> Path:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        inconclusive("not inside a git work tree; cannot resolve the repo root")
    return Path(out)


def plan_log_entry(spec_text: str, plan_num: str) -> str:
    m = re.search(rf"^> - \*\*plan-{plan_num} \(", spec_text, re.M)
    if not m:
        inconclusive(f"root SPEC.md has no amendment-log entry for plan-{plan_num}")
    tail = spec_text[m.start():]
    nxt = re.search(r"^> - \*\*", tail[1:], re.M)
    return tail[: nxt.start() + 1] if nxt else tail


def definitions(text: str) -> dict[str, str]:
    """-> {req_id: body}, where body runs to the next definition line or section heading."""
    out: dict[str, str] = {}
    cur: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        m = DEF_RE.match(line)
        if m:
            if cur:
                out[cur] = "\n".join(buf)
            cur, buf = m.group(1), [line]
            continue
        if cur is None:
            continue
        if line.startswith("## ") or line.startswith("### "):
            out[cur] = "\n".join(buf)
            cur, buf = None, []
            continue
        buf.append(line)
    if cur:
        out[cur] = "\n".join(buf)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plan", required=True, help="plan id, e.g. plan-064-james-dixson-a0b7fa")
    ap.add_argument(
        "--per-skill-spec", action="append", default=None,
        help="a per-skill SPEC.md to treat as a dual home (repeatable). "
             "Default: every skills/*/SPEC.md.",
    )
    args = ap.parse_args()

    root = repo_root()
    spec_md = root / "SPEC.md"
    if not spec_md.is_file():
        inconclusive(f"no root SPEC.md at {spec_md}")

    if args.per_skill_spec:
        homes = [Path(p) if Path(p).is_absolute() else root / p for p in args.per_skill_spec]
    else:
        homes = sorted(root.glob("skills/*/SPEC.md"))
    homes = [h for h in homes if h.is_file()]
    if not homes:
        inconclusive("no per-skill SPEC.md files found; there is no dual home to check")

    plan_num = args.plan.split("-")[1]
    entry = plan_log_entry(spec_md.read_text(encoding="utf-8"), plan_num)
    claimed = set(REQ_RE.findall(entry))
    if not claimed:
        inconclusive(
            f"the plan-{plan_num} amendment-log entry names no REQ-* id — "
            "nothing to cross-check against a per-skill home"
        )

    marker = re.compile(rf"plan-{plan_num}\b")
    dual: list[tuple[str, Path]] = []
    stale: list[tuple[str, Path]] = []
    for home in homes:
        defs = definitions(home.read_text(encoding="utf-8"))
        for rid in sorted(claimed & set(defs)):
            dual.append((rid, home))
            if not marker.search(defs[rid]):
                stale.append((rid, home))

    if not dual:
        inconclusive(
            f"the dual-homed set is EMPTY — plan-{plan_num} names {len(claimed)} id(s) "
            f"({', '.join(sorted(claimed))}) and none is normatively defined in any of the "
            f"{len(homes)} per-skill SPEC file(s). A check over an empty set certifies "
            "vacuously; it cannot distinguish 'no dual-homed id was amended' from "
            "'this check looked in the wrong place'."
        )

    if stale:
        for rid, home in stale:
            print(
                f"check-dual-home-amendment: FAIL — {rid} is amended in root SPEC.md's "
                f"plan-{plan_num} entry, but its normative body in "
                f"{home.relative_to(root)} carries no `plan-{plan_num}` amendment marker. "
                "The per-skill copy is STALE.",
                file=sys.stderr,
            )
        return 1

    print(
        f"check-dual-home-amendment: {len(dual)} dual-homed id(s) amended by plan-{plan_num} "
        f"all carry a per-skill amendment marker: "
        + ", ".join(f"{rid} ({home.relative_to(root)})" for rid, home in dual)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
