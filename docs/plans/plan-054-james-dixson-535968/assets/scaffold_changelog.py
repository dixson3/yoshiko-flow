#!/usr/bin/env python3
"""THROWAWAY scaffolder for plan-054 Issue 4.1 — changelog reconstruction input.

Deliberately not shipped: it exists to produce ONE artifact (the v0.5.0 changelog body) and has
no second consumer. Keeping it in `assets/` rather than `scripts/` records that.

WHY THIS SPINE AND NOT THE SPEC AMENDMENT LOG (EXP-004, which REFUTED the assumed one). The
amendment log misses NINE of the 28 plans, is fragmented across five blockquote regions, and is
non-chronological — so reconstructing from it would silently omit a third of the range. Each
bundle's `index.md` carries a one-line `> ` summary and 28 of 28 have one, which makes it the
only spine with full coverage.

Only `include`-dispositioned upstream rows are emitted. Measured: 59 of 183 rows across the range
are `include`; the rest are exclude/deferred/partial and did not ship in this window, so listing
them would describe work the release does not contain.
"""
import json, pathlib, re, subprocess, sys, os

ROOT = pathlib.Path(__file__).resolve().parent
if not (ROOT / "docs").is_dir():
    ROOT = pathlib.Path.cwd()
LOW, HIGH = 26, 53

def summary(idx: pathlib.Path) -> str:
    for ln in idx.read_text(encoding="utf-8").splitlines():
        if ln.startswith("> "):
            return " ".join(ln[2:].split())
    return ""

rows = []
for d in sorted((ROOT / "docs" / "plans").glob("plan-*")):
    m = re.match(r"plan-(\d{3})", d.name)
    if not m or not (LOW <= int(m.group(1)) <= HIGH):
        continue
    # index.md OR the legacy README.md. The five OLDEST bundles in this range (026-030)
    # predate the OKF reserved-name convention and carry their summary in `README.md`; looking
    # only at `index.md` reported 23 of 28 and would have silently dropped five plans from the
    # release notes. EXP-004's 28/28 coverage claim was correct — the gap was in this reader.
    idx = d / "index.md"
    if not idx.is_file():
        idx = d / "README.md"
    rec = {"plan": d.name, "n": int(m.group(1)),
           "summary": summary(idx) if idx.is_file() else "", "include": []}
    p = subprocess.run(["uv", "run", str(ROOT / "_shared" / "plan_extract.py"), str(d), "--json"],
                       capture_output=True, text=True, env={**os.environ, "VIRTUAL_ENV": ""})
    if p.stdout.strip():
        try:
            e = json.loads(p.stdout)
            e = e[0] if isinstance(e, list) else e
            for u in e.get("upstream", []):
                if (u.get("disposition") or "").strip().lower() == "include":
                    rec["include"].append({"issue": u.get("issue"), "title": u.get("title", "")})
        except Exception:
            pass
    rows.append(rec)

print(json.dumps(rows, indent=1))
print(f"\n# plans: {len(rows)}  with-summary: {sum(1 for r in rows if r['summary'])}  "
      f"include-rows: {sum(len(r['include']) for r in rows)}", file=sys.stderr)
