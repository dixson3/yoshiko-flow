# /// script
# requires-python = ">=3.11"
# ///
"""Repair dangling `**Epic:**` refs in legacy plan bundles (plan-044 #143).

A **purpose-built one-shot**, not a general verb. The `yf-*` rename regenerated
molecule ids into an 8-hex form (`yf-<8hex>`), but 14 plan bundles (plan-004 …
plan-017) kept their pre-rename ids in `plan.md`. The result is worse than a missing
ref: `_resume_scan` resolves `plan.md` FIRST and only falls back to
`metadata.plan_dir` when the field is ABSENT — so a dangling-but-PRESENT field yields
`found: true` with zero descendants. A resumed execute session reads "no open work"
and skips the plan entirely. A silent false success.

**The mapping is derived, not hardcoded.** The channel is `metadata.plan_dir` on the
molecule bead, which is exactly 1:1. Deriving it live means the tool re-verifies its
own inputs on every run rather than trusting a table transcribed months ago.

**Two lines per plan**, not one — `plan.md` carries both:

    **Epic:** <id>
    - <date> intake: epic <id> poured

**`--dry-run` is the DEFAULT** (mirroring the `push --apply` convention). Nothing is
written without an explicit `--apply`.

Bundles stay OKF-legacy (plan-044 D-3): this rewrites the two lines in place and does
NOT route through `record-epic`, which would restructure the bundle.
"""
import argparse
import json
import re
import sys
from pathlib import Path

EPIC_FIELD_RE = re.compile(r"^(\*\*Epic:\*\*\s+)(\S+)\s*$", re.MULTILINE)
INTAKE_LOG_RE = re.compile(r"^(- .*intake: epic )(\S+)( poured\s*)$", re.MULTILINE)


def load_plan_dir_map(jsonl: Path) -> dict[str, list[str]]:
    """plan_dir -> [molecule bead ids], from the beads JSONL export."""
    out: dict[str, list[str]] = {}
    with jsonl.open() as f:
        for line in f:
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            if r.get("issue_type") != "molecule":
                continue
            md = r.get("metadata")
            if isinstance(md, str):
                try:
                    md = json.loads(md)
                except json.JSONDecodeError:
                    md = None
            if isinstance(md, dict) and md.get("plan_dir"):
                out.setdefault(md["plan_dir"], []).append(r["id"])
    return out


def current_refs(text: str) -> tuple[str | None, str | None]:
    """The ids currently named by the two lines (field, log)."""
    f = EPIC_FIELD_RE.search(text)
    l = INTAKE_LOG_RE.search(text)
    return (f.group(2) if f else None, l.group(2) if l else None)


def plan_files(plan_dir: Path) -> list[Path]:
    """`plan.md` plus `log.md` when present (the phase log may live in either)."""
    return [p for p in (plan_dir / "plan.md", plan_dir / "log.md") if p.is_file()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--plans-root", default="docs/plans")
    ap.add_argument("--beads-jsonl", default=".beads/issues.jsonl")
    ap.add_argument(
        "--apply",
        action="store_true",
        help="write the repairs. ABSENT --apply IS THE DRY RUN (the default).",
    )
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()

    jsonl = Path(args.beads_jsonl)
    if not jsonl.is_file():
        print(f"ERROR: no beads export at {jsonl}", file=sys.stderr)
        return 2
    plan_dir_map = load_plan_dir_map(jsonl)
    known_ids = {i for ids in plan_dir_map.values() for i in ids}

    rows = []
    for pd in sorted(Path(args.plans_root).glob("plan-*")):
        if not pd.is_dir():
            continue
        files = plan_files(pd)
        if not files:
            continue
        key = str(pd)
        candidates = plan_dir_map.get(key, [])
        text = (pd / "plan.md").read_text() if (pd / "plan.md").is_file() else ""
        cur_field, cur_log = current_refs(text)
        cur = cur_field or cur_log
        if cur is None:
            continue  # no Epic ref recorded at all — not this tool's business

        # No candidate at all: we cannot DERIVE a new id — but neither have we
        # shown the current ref is dangling. Most often this is simply a stale
        # export (a molecule poured after the last `bd export`). Classify it
        # honestly as SKIPPED, not as a refusal: calling it a refusal implies a
        # problem was found, and the loudest signal should mean the loudest thing.
        if not candidates:
            rows.append({
                "plan_dir": key, "current": cur, "new": None, "status": "skipped",
                "detail": "no molecule bead carries this plan_dir in the export "
                          "(commonly a stale export) — cannot derive; left untouched",
            })
            continue
        # AMBIGUITY IS A REFUSAL, never a guess.
        if len(candidates) != 1:
            rows.append({
                "plan_dir": key, "current": cur, "new": None,
                "status": "refused",
                "detail": f"{len(candidates)} molecule beads carry this plan_dir "
                          "— refusing to guess",
            })
            continue
        new = candidates[0]
        if cur == new:
            rows.append({"plan_dir": key, "current": cur, "new": new,
                         "status": "ok", "detail": "ref already resolves"})
            continue
        # Only repair a ref that is genuinely DANGLING. A ref pointing at a real
        # bead that simply is not this plan's molecule is a different problem and
        # must not be silently rewritten.
        if cur in known_ids:
            rows.append({
                "plan_dir": key, "current": cur, "new": new, "status": "refused",
                "detail": "current ref resolves to a DIFFERENT known bead — not a "
                          "dangling ref; refusing to rewrite",
            })
            continue
        rows.append({"plan_dir": key, "current": cur, "new": new,
                     "status": "repair", "detail": "dangling ref -> derived molecule"})

    repairs = [r for r in rows if r["status"] == "repair"]
    refusals = [r for r in rows if r["status"] == "refused"]
    skipped = [r for r in rows if r["status"] == "skipped"]

    written = []
    if args.apply:
        for r in repairs:
            pd = Path(r["plan_dir"])
            for f in plan_files(pd):
                t = f.read_text()
                t2 = EPIC_FIELD_RE.sub(lambda m: m.group(1) + r["new"], t)
                t2 = INTAKE_LOG_RE.sub(
                    lambda m: m.group(1) + r["new"] + m.group(3), t2)
                if t2 != t:
                    f.write_text(t2)
                    written.append(str(f))

    if args.as_json:
        print(json.dumps({
            "applied": bool(args.apply),
            "repairs": repairs, "refusals": refusals, "skipped": skipped,
            "rows": rows,
            "files_written": written,
        }, indent=2))
    else:
        mode = "APPLY" if args.apply else "DRY RUN (default — pass --apply to write)"
        print(
            f"[{mode}] {len(repairs)} bundle(s) to repair, "
            f"{len(refusals)} refused, {len(skipped)} skipped\n"
        )
        print(f"{'plan_dir':<46} {'current (dangling)':<26} -> new")
        for r in repairs:
            print(f"{r['plan_dir']:<46} {r['current']:<26} -> {r['new']}")
        for r in refusals:
            print(f"REFUSED {r['plan_dir']}: {r['detail']}")
        for r in skipped:
            print(f"skipped {r['plan_dir']}: {r['detail']}")
        if written:
            print(f"\nWrote {len(written)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
