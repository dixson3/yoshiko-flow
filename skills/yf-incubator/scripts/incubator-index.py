#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6"]
# ///
"""Index the Incubator/ tree: managed incubators by state + staleness, unmanaged by mtime.

Managed = state file frontmatter carries both `status` and `last_reviewed`.
Unmanaged = anything else (existing dirs/single files); listed, never mutated.

OKF (OKF-INCUBATOR, `skills/yf-incubator/OKF-EXTENSION.md`). Frontmatter reads and
writes route through the vendored `okf` engine (sibling module), never hand-rolled
YAML:

  * `parse_frontmatter` delegates to `okf.read_frontmatter` (report-only: malformed
    YAML lands the entry in *unmanaged*, never raises — REQ-OKF-071).
  * `scaffold` types a state file in place via `okf.write_frontmatter`
    (merge-and-preserve: the seven pre-OKF keys survive byte-for-byte, adding only
    `type: Incubator` + `okf_spec: OKF-INCUBATOR` — REQ-INCUB-002/040, REQ-OKF-070).
  * A single-file incubator (`Incubator/<kebab>.md`) is EXEMPT from the reserved
    `index.md`/`log.md` files (REQ-INCUB-042 / REQ-OKF-050); only a dir-form bundle
    gets them. `promote` moves `## Files`→`index.md` and `## Decision log`→`log.md`
    when a single-file incubator becomes dir-form (REQ-INCUB-041), never dropping a
    section.
  * `Incubator/INDEX.md`, the cross-incubator catalog this indexer regenerates, is a
    reserved listing surface OUTSIDE the OKF bundle model: it is never a bundle-root
    `index.md` and never gains `type`/`okf_spec` (REQ-INCUB-043).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

# Vendored yf-okf engine, imported as a sibling scripts/ module (the skill's
# sibling-import pattern). Do NOT re-implement frontmatter YAML here.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import okf  # noqa: E402

INCUBATOR_TYPE = "Incubator"
OKF_SPEC = "OKF-INCUBATOR"
CATALOG_NAME = "INDEX.md"  # cross-incubator catalog; never a bundle-root index.md

PRIORITY_RANK = {"high": 0, "normal": 1, "low": 2}
STATUS_VALUES = {"incubating", "scoping", "exploring", "converging",
                 "concluded", "parked", "abandoned"}


def parse_frontmatter(path: Path) -> dict | None:
    """State-file frontmatter dict, or None. Routes through the vendored engine's
    `read_frontmatter` (merge-and-preserve reader). Report-only: malformed YAML,
    an unreadable/binary file, or an absent frontmatter block all return None so
    the caller lists the entry as unmanaged instead of crashing (REQ-OKF-071)."""
    try:
        fm, _body = okf.read_frontmatter(Path(path))
    except (okf.OKFParseError, OSError, UnicodeDecodeError, ValueError):
        return None
    return fm or None


def is_single_file(entry: Path) -> bool:
    """A single-file incubator: a lone `.md` with no owning directory
    (`Incubator/<kebab>.md`). Reserved-file-exempt (REQ-INCUB-042 / REQ-OKF-050)."""
    return okf._is_single_file_bundle(Path(entry))


def state_file(entry: Path) -> Path | None:
    """The file whose frontmatter represents the incubator's state.

    Dir-form: `<entry>/README.md` — kept as the typed state file, NEVER renamed to
    index.md (REQ-INCUB-040). Single-file: the `.md` itself.
    """
    if entry.is_dir():
        readme = entry / "README.md"
        return readme if readme.is_file() else None
    if entry.is_file() and entry.suffix == ".md":
        return entry
    return None


# ---------------------------------------------------------------------------
# OKF typing / scaffolding (write path — routed through the vendored engine)
# ---------------------------------------------------------------------------


def type_state_file(sf: Path, *, dry_run: bool = False) -> str:
    """Add `type: Incubator` + `okf_spec: OKF-INCUBATOR` to a state file's
    frontmatter IN PLACE (REQ-INCUB-002/040). Merge-and-preserve via the engine:
    the seven pre-OKF keys keep their position and byte value; only the two OKF
    keys are appended (REQ-OKF-070). Returns the new file text."""
    return okf.write_frontmatter(
        Path(sf),
        {okf.TYPE_KEY: INCUBATOR_TYPE, okf.OKF_SPEC_KEY: OKF_SPEC},
        dry_run=dry_run,
    )


def scaffold(target: Path, *, dry_run: bool = False) -> dict:
    """Bring an existing incubator to OKF conformance in place.

    Both forms: type the state file (`README.md` for dir-form, the `.md` itself for
    single-file). Dir-form ONLY: scaffold the reserved `index.md`/`log.md` skeletons
    (REQ-INCUB-041). Single-file bundles are EXEMPT (REQ-INCUB-042 / REQ-OKF-050) and
    get no reserved files. Never renames `README.md` (REQ-INCUB-040).
    """
    target = Path(target)
    if target.name == CATALOG_NAME:
        raise ValueError(f"{CATALOG_NAME} is the cross-incubator catalog, not a bundle (REQ-INCUB-043)")
    sf = state_file(target)
    if sf is None:
        raise ValueError(f"no incubator state file at {target}")

    type_state_file(sf, dry_run=dry_run)
    result = {"state_file": str(sf), "single_file": is_single_file(target)}

    if target.is_dir():  # dir-form → reserved files; single-file is exempt
        if not dry_run:
            okf.scaffold_bundle(target, reserved=True, title=target.name)
        result["reserved"] = ["index.md", "log.md"]
    else:
        result["reserved"] = []  # exempt
    return result


def _split_sections(body: str) -> list[tuple[str, str]]:
    """Split a state-file body into ordered `(heading_line, section_text)` pairs at
    each `## ` boundary. Text before the first `## ` is keyed by the empty heading."""
    sections: list[tuple[str, str]] = []
    cur_head = ""
    cur: list[str] = []
    for line in body.splitlines(keepends=True):
        if line.startswith("## "):
            sections.append((cur_head, "".join(cur)))
            cur_head, cur = line.rstrip("\n"), []
        else:
            cur.append(line)
    sections.append((cur_head, "".join(cur)))
    return sections


def promote(single_md: Path, *, dry_run: bool = False) -> dict:
    """Promote a single-file incubator (`Incubator/<kebab>.md`) to dir-form
    (`Incubator/<kebab>/README.md`), moving `## Files`→`index.md` and
    `## Decision log`→`log.md` (REQ-INCUB-041). The moved sections are NEVER
    dropped (REQ-INCUB-003); the reserved files carry no `type`/`okf_spec`
    (REQ-OKF-031); `README.md` keeps `type: Incubator`.

    The exemption boundary: while single-file, those sections stay in-body
    (REQ-INCUB-042); on promotion they extract to the reserved files.
    """
    src = Path(single_md)
    if not is_single_file(src):
        raise ValueError(f"{src} is not a single-file incubator")
    bundle = src.with_suffix("")
    dst = bundle / "README.md"

    fm, body = okf.read_frontmatter(src)
    sections = _split_sections(body)
    files_text = next((t for h, t in sections if h.lower().startswith(("## files", "## layout"))), None)
    log_text = next((t for h, t in sections if h.lower().startswith("## decision log")), None)
    # README keeps every section EXCEPT the two promoted to reserved files.
    kept = [(h, t) for h, t in sections
            if not (h.lower().startswith(("## files", "## layout", "## decision log")))]

    plan = {
        "bundle": str(bundle),
        "state_file": str(dst),
        "moved": [s for s, present in
                  (("index.md", files_text is not None), ("log.md", log_text is not None)) if present],
    }
    if dry_run:
        return plan

    bundle.mkdir(parents=True, exist_ok=True)
    # Rebuild README body without the promoted sections, re-emit typed frontmatter.
    new_body = "".join(
        (h + "\n" if h else "") + t for h, t in kept
    )
    dst.write_text(okf._dump_frontmatter(dict(fm)) + new_body)
    type_state_file(dst)  # ensure type: Incubator + okf_spec present
    # Reserved index.md/log.md skeletons (okf_version frontmatter, no type).
    okf.scaffold_bundle(bundle, reserved=True, title=bundle.name)
    # Move `## Files` listing into index.md, `## Decision log` into log.md — verbatim,
    # never dropped. index.md keeps its okf_version frontmatter (untyped).
    if files_text is not None and files_text.strip():
        idx = bundle / "index.md"
        ifm, ibody = okf.read_frontmatter(idx)
        idx.write_text(okf._dump_frontmatter(ifm) + ibody.rstrip("\n") + "\n\n" + files_text.strip("\n") + "\n")
    if log_text is not None and log_text.strip():
        (bundle / "log.md").write_text("# Log\n\n" + log_text.strip("\n") + "\n")
    src.unlink()  # the single file is now README.md
    return plan


# ---------------------------------------------------------------------------
# Indexing / triage
# ---------------------------------------------------------------------------


def collect(root: Path):
    managed, unmanaged = [], []
    for entry in sorted(root.iterdir()):
        # The cross-incubator catalog is a reserved listing surface, NOT a bundle
        # (REQ-INCUB-043) — never index it, never type it.
        if entry.name.startswith(".") or entry.name == CATALOG_NAME:
            continue
        sf = state_file(entry)
        name = entry.name[:-3] if entry.is_file() else entry.name
        if sf is None:
            unmanaged.append({"name": name, "path": str(entry),
                              "mtime": entry.stat().st_mtime, "reason": "no state file"})
            continue
        fm = parse_frontmatter(sf)
        if not fm or "status" not in fm or "last_reviewed" not in fm:
            unmanaged.append({"name": name, "path": str(entry),
                              "mtime": sf.stat().st_mtime,
                              "reason": "frontmatter missing status/last_reviewed"})
            continue
        managed.append({
            "name": fm.get("title", name),
            "path": str(entry),
            "status": str(fm.get("status", "")),
            "priority": str(fm.get("priority", "normal")),
            "last_reviewed": str(fm.get("last_reviewed", "")),
        })
    return managed, unmanaged


def days_since(iso: str, today: dt.date) -> int | None:
    try:
        return (today - dt.date.fromisoformat(iso)).days
    except ValueError:
        return None


def sort_managed(managed: list[dict], today: dt.date) -> list[dict]:
    def key(m):
        pr = PRIORITY_RANK.get(m["priority"], 1)
        stale = days_since(m["last_reviewed"], today)
        # stalest first within a priority band; unparseable dates sort last
        return (pr, -(stale if stale is not None else -1))
    return sorted(managed, key=key)


def render_text(managed, unmanaged, today) -> str:
    out = [f"# Incubator index — {today.isoformat()}", ""]
    out.append(f"Managed: {len(managed)}   Unmanaged: {len(unmanaged)}")
    out.append("")
    out.append("## Managed (priority, then stalest first)")
    if not managed:
        out.append("_none_")
    for m in managed:
        d = days_since(m["last_reviewed"], today)
        age = f"{d}d ago" if d is not None else "unknown"
        out.append(f"- [{m['priority']}/{m['status']}] {m['name']} "
                   f"— reviewed {m['last_reviewed']} ({age}) — {m['path']}")
    out.append("")
    out.append("## Unmanaged (by file mtime, stalest first)")
    if not unmanaged:
        out.append("_none_")
    for u in sorted(unmanaged, key=lambda x: x["mtime"]):
        mt = dt.date.fromtimestamp(u["mtime"]).isoformat()
        out.append(f"- {u['name']} — touched {mt} — {u['path']} ({u['reason']})")
    return "\n".join(out) + "\n"


def cmd_list(args) -> int:
    root = Path(args.root)
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 1

    today = dt.date.today()
    managed, unmanaged = collect(root)
    managed = sort_managed(managed, today)

    if args.json:
        print(json.dumps({"generated": today.isoformat(),
                          "managed": managed, "unmanaged": unmanaged}, indent=2))
    else:
        print(render_text(managed, unmanaged, today), end="")

    if args.write:
        # Plain-GFM cross-incubator catalog. NOT an OKF bundle-root index.md: no
        # frontmatter, no `type`, no `okf_spec` (REQ-INCUB-043).
        banner = "<!-- generated by /incubator list --write — do not edit by hand -->\n\n"
        (root / CATALOG_NAME).write_text(
            banner + render_text(managed, unmanaged, today), encoding="utf-8")
        print(f"\nwrote {root / CATALOG_NAME}", file=sys.stderr)
    return 0


def cmd_scaffold(args) -> int:
    res = scaffold(Path(args.target), dry_run=args.dry_run)
    print(json.dumps(res, indent=2))
    return 0


def cmd_promote(args) -> int:
    res = promote(Path(args.target), dry_run=args.dry_run)
    print(json.dumps(res, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Index / OKF-manage the Incubator/ tree.")
    sub = ap.add_subparsers(dest="cmd")

    lst = sub.add_parser("list", help="triage the Incubator/ tree (default)")
    lst.add_argument("--root", default="Incubator", help="Incubator dir (default: ./Incubator)")
    lst.add_argument("--json", action="store_true", help="machine-readable output")
    lst.add_argument("--write", action="store_true", help="also (re)generate <root>/INDEX.md")
    lst.set_defaults(func=cmd_list)

    sc = sub.add_parser("scaffold", help="type a state file (+ dir-form reserved files) in place")
    sc.add_argument("target", help="incubator path (Incubator/<kebab> or Incubator/<kebab>.md)")
    sc.add_argument("--dry-run", action="store_true")
    sc.set_defaults(func=cmd_scaffold)

    pr = sub.add_parser("promote", help="promote a single-file incubator to dir-form (move Files/Decision log)")
    pr.add_argument("target", help="single-file incubator (Incubator/<kebab>.md)")
    pr.add_argument("--dry-run", action="store_true")
    pr.set_defaults(func=cmd_promote)

    # Backward compat: bare flags (`--root/--json/--write`) mean `list`.
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or (argv[0].startswith("-") and argv[0] not in ("-h", "--help")):
        argv = ["list", *argv]
    args = ap.parse_args(argv)
    if not getattr(args, "func", None):
        args = ap.parse_args(["list", *argv])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
