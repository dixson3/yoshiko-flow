#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pyyaml>=6.0",
# ]
# ///
"""OKF (Open Knowledge Format) conformance checker.

Walks a "bundle" directory (a yf-plan plan folder, a yf-research research dir, or
a yf-incubator artifact set) and reports, per markdown file, how it diverges from
a *provisional* OKF SPEC ruleset. Emits a structured JSON report and/or a
human-readable summary.

────────────────────────────────────────────────────────────────────────────────
PROVISIONAL SPEC — READ THIS
────────────────────────────────────────────────────────────────────────────────
The exact OKF SPEC is NOT yet known at the time this tool was built. It will be
retrieved in a later phase of research project 001-okf-compliance-delta. The
ruleset encoded in `DEFAULT_SPEC` below is a best-effort guess derived solely
from the research plan's questions (frontmatter `type`, reserved index.md/log.md,
citation heading convention, bundle-relative links, okf_version). Treat every
delta this tool reports as PROVISIONAL. Once the real OKF SPEC is retrieved,
update `DEFAULT_SPEC` (or pass `--spec spec.json`) and re-run.

The checks this tool performs against each markdown file:
  1. frontmatter-present   — does the file open with a YAML `---` frontmatter block?
  2. frontmatter-keys      — are the expected keys (e.g. `type`, `okf_version`)
                             present in that frontmatter?
  3. reserved-files        — does the bundle contain the expected reserved
                             filenames (index.md, log.md)? (bundle-level check)
  4. citation-heading      — for files that carry citations, is there a heading
                             matching the expected citation-heading regex?
  5. bundle-relative-links — are markdown links bundle-relative (no absolute
                             filesystem paths, no bare http(s) where a relative
                             link is expected)? (advisory)

Exit codes: 0 = ran successfully (deltas may still be reported in the payload);
2 = usage / bad-bundle-path error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - dependency declared in PEP 723 block
    print("error: PyYAML is required (declared in the PEP 723 block; run via `uv run`)",
          file=sys.stderr)
    sys.exit(2)


# ─── Provisional SPEC ruleset (see module docstring) ─────────────────────────
DEFAULT_SPEC: dict = {
    "provisional": True,
    "okf_version": "unknown",
    # Reserved filenames the SPEC is *guessed* to expect at bundle root.
    "reserved_files": ["index.md", "log.md"],
    # Frontmatter keys every OKF document is guessed to require.
    "required_frontmatter_keys": ["type", "okf_version"],
    # Regex a citation section heading is guessed to match (case-insensitive).
    "citation_heading_regex": r"^#{1,6}\s+(sources|citations|references|bibliography)\b",
    # Filenames that are conventionally citation-bearing (heuristic).
    "citation_bearing_globs": ["*summary*.md", "*report*.md", "*findings*.md"],
}


@dataclass
class FileReport:
    path: str
    has_frontmatter: bool
    frontmatter_keys: list[str]
    missing_frontmatter_keys: list[str]
    has_type_field: bool
    is_citation_bearing: bool
    has_citation_heading: bool | None  # None when not citation-bearing
    absolute_links: list[str] = field(default_factory=list)
    deltas: list[str] = field(default_factory=list)


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)
# Markdown inline links: [text](target)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def parse_frontmatter(text: str) -> dict | None:
    """Return the parsed YAML frontmatter dict, or None if absent/unparseable."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def is_absolute_link(target: str) -> bool:
    """True when a link target is an absolute filesystem path (not bundle-relative).

    http(s)/mailto and fragment/anchor links are treated as legitimately non-relative.
    """
    target = target.strip().split(" ")[0]  # drop optional "title"
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return False
    return target.startswith("/") or bool(re.match(r"^[A-Za-z]:[\\/]", target))


def check_file(path: Path, bundle: Path, spec: dict) -> FileReport:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm = parse_frontmatter(text)
    has_fm = fm is not None
    keys = sorted(fm.keys()) if fm else []
    required = spec.get("required_frontmatter_keys", [])
    missing = [k for k in required if k not in keys] if has_fm else list(required)
    has_type = "type" in keys

    rel = path.relative_to(bundle).as_posix()
    citation_bearing = any(path.match(g) for g in spec.get("citation_bearing_globs", []))
    cite_re = re.compile(spec.get("citation_heading_regex", ""), re.IGNORECASE | re.MULTILINE)
    has_cite_heading: bool | None
    if citation_bearing and spec.get("citation_heading_regex"):
        has_cite_heading = bool(cite_re.search(text))
    else:
        has_cite_heading = None

    abs_links = sorted({t for t in LINK_RE.findall(text) if is_absolute_link(t)})

    deltas: list[str] = []
    if not has_fm:
        deltas.append("no-frontmatter")
    else:
        if not has_type:
            deltas.append("missing-frontmatter:type")
        for k in missing:
            if k != "type":
                deltas.append(f"missing-frontmatter:{k}")
    if citation_bearing and has_cite_heading is False:
        deltas.append("missing-citation-heading")
    if abs_links:
        deltas.append(f"absolute-links:{len(abs_links)}")

    return FileReport(
        path=rel,
        has_frontmatter=has_fm,
        frontmatter_keys=keys,
        missing_frontmatter_keys=missing,
        has_type_field=has_type,
        is_citation_bearing=citation_bearing,
        has_citation_heading=has_cite_heading,
        absolute_links=abs_links,
        deltas=deltas,
    )


def check_bundle(bundle: Path, spec: dict) -> dict:
    md_files = sorted(p for p in bundle.rglob("*.md") if p.is_file())
    file_reports = [check_file(p, bundle, spec) for p in md_files]

    # Bundle-level: reserved files. Match on basename anywhere in the bundle.
    present_names = {p.name for p in md_files}
    reserved = spec.get("reserved_files", [])
    reserved_status = {name: (name in present_names) for name in reserved}
    missing_reserved = [n for n, ok in reserved_status.items() if not ok]

    total_deltas = sum(len(fr.deltas) for fr in file_reports)
    return {
        "bundle": str(bundle),
        "spec_provisional": bool(spec.get("provisional", True)),
        "spec_okf_version": spec.get("okf_version", "unknown"),
        "summary": {
            "markdown_files": len(file_reports),
            "files_with_frontmatter": sum(1 for fr in file_reports if fr.has_frontmatter),
            "files_with_type_field": sum(1 for fr in file_reports if fr.has_type_field),
            "total_file_deltas": total_deltas,
            "reserved_files_present": reserved_status,
            "missing_reserved_files": missing_reserved,
        },
        "files": [asdict(fr) for fr in file_reports],
    }


def render_summary(report: dict) -> str:
    s = report["summary"]
    lines: list[str] = []
    lines.append(f"OKF conformance report — {report['bundle']}")
    if report["spec_provisional"]:
        lines.append("  (SPEC ruleset is PROVISIONAL — pending OKF SPEC retrieval)")
    lines.append("")
    lines.append(f"  markdown files          : {s['markdown_files']}")
    lines.append(f"  with YAML frontmatter   : {s['files_with_frontmatter']}")
    lines.append(f"  with `type:` field      : {s['files_with_type_field']}")
    lines.append(f"  total file-level deltas : {s['total_file_deltas']}")
    lines.append("")
    lines.append("  reserved files (bundle-level):")
    for name, present in s["reserved_files_present"].items():
        lines.append(f"    {'ok ' if present else 'MISSING'}  {name}")
    lines.append("")
    lines.append("  per-file deltas:")
    any_delta = False
    for fr in report["files"]:
        if fr["deltas"]:
            any_delta = True
            lines.append(f"    {fr['path']}")
            for d in fr["deltas"]:
                lines.append(f"        - {d}")
    if not any_delta:
        lines.append("    (none)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="OKF conformance checker (PROVISIONAL SPEC — see script header).",
    )
    ap.add_argument("bundle", type=Path,
                    help="Path to a bundle directory (yf-plan/yf-research/yf-incubator artifacts).")
    ap.add_argument("--json", action="store_true",
                    help="Emit the structured JSON report to stdout.")
    ap.add_argument("--spec", type=Path, default=None,
                    help="Optional JSON file overriding the provisional DEFAULT_SPEC.")
    ap.add_argument("--out", type=Path, default=None,
                    help="Write the JSON report to this file (in addition to stdout summary).")
    args = ap.parse_args(argv)

    bundle = args.bundle
    if not bundle.exists():
        print(f"error: bundle path does not exist: {bundle}", file=sys.stderr)
        return 2
    if not bundle.is_dir():
        print(f"error: bundle path is not a directory: {bundle}", file=sys.stderr)
        return 2

    spec = dict(DEFAULT_SPEC)
    if args.spec is not None:
        if not args.spec.is_file():
            print(f"error: --spec file not found: {args.spec}", file=sys.stderr)
            return 2
        try:
            spec.update(json.loads(args.spec.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError) as e:
            print(f"error: could not read --spec {args.spec}: {e}", file=sys.stderr)
            return 2

    report = check_bundle(bundle, spec)

    if args.out is not None:
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_summary(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
