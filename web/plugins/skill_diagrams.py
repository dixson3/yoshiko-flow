#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""skill_diagrams.py — GENERATE the per-skill diagrams. Never hand-author them.

WHY GENERATED (EXP-004, and this is the whole design):

    event                          hand-authored              generated
    a skill adds a depends-on-*    edit 1-3 .d2 -> CAN DRIFT  re-run -> CANNOT DRIFT
    a skill adds/removes a script  invisible -> DRIFTS SILENTLY  re-run -> CANNOT DRIFT
    a new skill is added           someone must remember      appears automatically
    a skill is removed             orphan .d2+.png linger     disappears

Twenty hand-authored diagrams would be twenty NEW drift surfaces, which is the opposite of what
this plan is for. The measured cost of SIX is already on record: plan-066 found 7 live mismatches
across 4 files that three well-specified manifest edges all missed. Going 6 -> 26 multiplies it.

**Second-order, and the reason this file exists at all:** you cannot omit a cluster or an edge
from a diagram you did not write — so generation makes this surface immune to the very omission
problem the rest of plan-067 is about.

TWO STAGES, DELIBERATELY SPLIT:
  build_model()  — toolchain-NEUTRAL. Reads the shared `skill_model`, adds the publication
                   decision, and returns plain dicts.
  to_d2()        — the EMITTER. The only place d2 syntax appears.
An archify adoption would replace `to_d2()` and leave the model untouched; that split is what
makes the toolchain question separable from the content question.

PUBLICATION IS A COMPUTED THRESHOLD, NOT A LIST (`nodes >= PUBLISH_MIN_NODES`). A hand-maintained
list of "which skills earn a diagram" goes stale silently; a threshold re-decides on every run, so
a skill that grows past it gains a diagram and one that shrinks below loses it, with nobody
remembering. The node/edge definition and the re-derived value are in
`docs/plans/plan-067-james-dixson-de852a/findings/per-skill-census.md`.

`--check` BYTE-COMPARES the emitted source against the committed source. **Without it this is a
convenience, not a guarantee** — the precedent is `_shared/sync.py --check`.

EXIT  0 clean / in sync  ·  1 --check found a difference  ·  2 could not run
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import skill_model  # noqa: E402

CHECK = "skill_diagrams"
OUT_SUBDIR = os.path.join("web", "content", "images", "skills")

# The RE-DERIVED threshold (Issue 5.0). It sits on a three-way tie, which is a property of the
# corpus shape rather than of the choice — recorded in the census finding rather than engineered
# away by nudging the number until the tie disappears.
PUBLISH_MIN_NODES = 5

GROUP_FILL = {
    "workflows": "#eef2ff",
    "beads": "#f0fdf4",
    "utility": "#f8fafc",
    "markdown": "#fff7ed",
}


def inconclusive(msg: str) -> None:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def repo_root() -> Path:
    try:
        return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                   capture_output=True, text=True, check=True).stdout.strip())
    except Exception:
        return Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# STAGE 1 — build_model(): toolchain-neutral
# ---------------------------------------------------------------------------

def _containers(s: dict) -> list[tuple[str, str, list[str]]]:
    """(key, label, members) for each NON-EMPTY listing. Empty ones are omitted rather than
    drawn as an empty box — an empty box asserts a thing exists and is unpopulated, which is a
    different claim from the thing not existing."""
    out = []
    if s["scripts"]:
        out.append(("scripts", "scripts/", s["scripts"]))
    if s["agents"]:
        out.append(("agents", "agents/", s["agents"]))
    if s["formulas"]:
        out.append(("formulas", "formulas/", s["formulas"]))
    if s["protocols"]:
        out.append(("protocols", "protocols/", s["protocols"]))
    return out


def build_model(root: Path) -> list[dict]:
    """The toolchain-NEUTRAL model. No d2 token appears in this function."""
    skills = skill_model.read_skills(str(root))
    if not skills:
        inconclusive(f"read zero skills under {root}/skills")
    model = []
    for s in skills:
        conts = _containers(s)
        externals = (sorted(set(s["depends_on_tool"]))
                     + sorted(set(s["depends_on_skill"]))
                     + sorted(set(s["dependents"])))
        nodes = 1 + len(externals) + len(conts)
        edges = len(externals) + len(conts)
        model.append({
            "name": s["name"],
            "group": s["group"],
            "invocable": s["invocable"],
            "verbs": s["verbs"],
            "engine": s["engine"],
            "tools": sorted(set(s["depends_on_tool"])),
            "deps": sorted(set(s["depends_on_skill"])),
            "dependents": sorted(set(s["dependents"])),
            "containers": conts,
            "nodes": nodes,
            "edges": edges,
            # THE THRESHOLD IS APPLIED HERE, ONCE, and recomputed on every run.
            "publish": nodes >= PUBLISH_MIN_NODES,
        })
    return model


# ---------------------------------------------------------------------------
# STAGE 2 — to_d2(): the ONLY place d2 syntax appears
# ---------------------------------------------------------------------------

def _id(text: str) -> str:
    return text.replace("-", "_").replace(".", "_").replace("/", "_")


def _grid(members: list[str]) -> str:
    """GRID-NEST a container's members (Issue 5.6).

    A single-column stack of 22 sub-boxes renders as a 4532px-tall bulleted list rather than a
    graph — measured on `yf-plan`. `grid-columns` is the one-line emitter fix; the column count
    grows with the member count so a 2-item box does not get 4 empty columns.
    """
    n = len(members)
    cols = 1 if n <= 2 else (2 if n <= 6 else (3 if n <= 12 else 4))
    return f"  grid-columns: {cols}\n" if cols > 1 else ""


def to_d2(m: dict) -> str:
    """Emit one skill's `.d2`. GENERATED — the banner says so, in the file itself."""
    L = []
    L.append(f"# GENERATED by web/plugins/skill_diagrams.py — DO NOT EDIT BY HAND.")
    L.append(f"# Regenerate: uv run web/plugins/skill_diagrams.py")
    L.append(f"# Verify:     uv run web/plugins/skill_diagrams.py --check")
    L.append(f"# Source of truth: skills/{m['name']}/SKILL.md frontmatter + directory listings,")
    L.append(f"# read through web/plugins/skill_model.py — the SAME reader the site page uses.")
    L.append(f"# nodes={m['nodes']} edges={m['edges']} (threshold: nodes >= {PUBLISH_MIN_NODES})")
    L.append("direction: right")
    L.append("")
    fill = GROUP_FILL.get(m["group"], "#f8fafc")
    inv = (f"/{m['name']}" if m["invocable"] else "auto (fires from its description conditions)")
    verbs = ("\\nsub-verbs: " + " · ".join(m["verbs"])) if m["verbs"] else ""
    L.append(f"{_id(m['name'])}: {{")
    L.append(f'  label: "{m["name"]}\\nskill-group: {m["group"]}\\ninvocation: {inv}{verbs}"')
    L.append("  shape: rectangle")
    L.append(f'  style.fill: "{fill}"')
    L.append("  style.bold: true")
    L.append("}")
    L.append("")
    if m["tools"]:
        L.append("tools: {")
        L.append('  label: "depends-on-tool"')
        L.append(_grid(m["tools"]).rstrip("\n") or "  # single column")
        for t in m["tools"]:
            L.append(f'  {_id(t)}: "{t}"')
        L.append("}")
        L.append("")
    if m["deps"]:
        L.append("deps: {")
        L.append('  label: "depends-on-skill"')
        L.append(_grid(m["deps"]).rstrip("\n") or "  # single column")
        for d in m["deps"]:
            L.append(f'  {_id(d)}: "{d}"')
        L.append("}")
        L.append("")
    if m["dependents"]:
        L.append("dependents: {")
        L.append('  label: "skills that depend on this one (reverse edge)"')
        L.append(_grid(m["dependents"]).rstrip("\n") or "  # single column")
        for d in m["dependents"]:
            L.append(f'  {_id(d)}: "{d}"')
        L.append("}")
        L.append("")
    for key, label, members in m["containers"]:
        L.append(f"{key}: {{")
        star = f" · engine: {m['engine']}" if (key == "scripts" and m["engine"]) else ""
        L.append(f'  label: "{label}{star}"')
        g = _grid(members).rstrip("\n")
        if g:
            L.append(g)
        for name in members:
            L.append(f'  {_id(name)}: "{name}"')
        L.append("}")
        L.append("")
    sid = _id(m["name"])
    if m["tools"]:
        L.append(f"{sid} -> tools: \"requires on PATH\"")
    if m["deps"]:
        L.append(f"{sid} -> deps: \"declares\"")
    if m["dependents"]:
        L.append(f"dependents -> {sid}: \"declare it\"")
    for key, _label, _members in m["containers"]:
        L.append(f"{sid} -> {key}: \"ships\"")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=None)
    ap.add_argument("--check", action="store_true",
                    help="byte-compare the emitted source against the committed source and "
                         "write NOTHING. Without this the generator is a convenience, not a "
                         "guarantee (the `_shared/sync.py --check` precedent).")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve() if a.root else repo_root()
    model = build_model(root)
    out_dir = root / OUT_SUBDIR
    published = [m for m in model if m["publish"]]
    if not published:
        inconclusive(f"the threshold nodes >= {PUBLISH_MIN_NODES} selected NOTHING — a "
                     f"generator that emits an empty set certifies nothing")

    wanted = {f"{m['name']}.d2": to_d2(m) for m in published}
    existing = {p.name for p in out_dir.glob("*.d2")} if out_dir.is_dir() else set()

    drifted, missing, orphan = [], [], sorted(existing - set(wanted))
    for name, src in wanted.items():
        p = out_dir / name
        if not p.is_file():
            missing.append(name)
        elif p.read_text(encoding="utf-8") != src:
            drifted.append(name)

    if a.check:
        rc = 1 if (drifted or missing or orphan) else 0
        if rc:
            print(f"{CHECK}: FAIL — committed sources do not match a fresh generation. "
                  f"missing={missing} drifted={drifted} orphan={orphan}", file=sys.stderr)
        out = {"check": CHECK, "verdict": "FAIL" if rc else "PASS", "mode": "check",
               "threshold": PUBLISH_MIN_NODES, "published": len(published),
               "skills": len(model), "missing": missing, "drifted": drifted, "orphan": orphan}
        print(json.dumps(out, indent=1) if a.json else
              f"{CHECK}: {len(published)} of {len(model)} skill(s) published at "
              f"nodes >= {PUBLISH_MIN_NODES}; "
              + ("in sync" if not rc else f"OUT OF SYNC (missing {len(missing)}, "
                                          f"drifted {len(drifted)}, orphan {len(orphan)})"))
        return rc

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, src in wanted.items():
        (out_dir / name).write_text(src, encoding="utf-8")
    for name in orphan:
        (out_dir / name).unlink()
        png = out_dir / (name[:-3] + ".png")
        if png.is_file():
            png.unlink()
    out = {"check": CHECK, "verdict": "PASS", "mode": "write",
           "threshold": PUBLISH_MIN_NODES, "published": len(published),
           "skills": len(model), "written": sorted(wanted), "removed_orphans": orphan}
    print(json.dumps(out, indent=1) if a.json else
          f"{CHECK}: wrote {len(wanted)} diagram source(s) "
          f"({len(published)} of {len(model)} skills at nodes >= {PUBLISH_MIN_NODES}); "
          f"removed {len(orphan)} orphan(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
