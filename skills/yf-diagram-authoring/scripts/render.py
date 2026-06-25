#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""d2 diagram render helper for the diagram-authoring skill.

Subcommands:
  preflight            OS-independent check that `d2` is on PATH (command -v d2 only;
                       NO Chromium/playwright cache probe — those paths are OS-specific and
                       probing them risks a false negative). The one-time PNG-browser warm-up
                       is owned outside this skill (dotfiles bootstrap); preflight only reports
                       whether d2 is installed.
  render <file.d2>     Render one .d2 to a sibling .png (theme 0, elk by default).
  render-dir <dir>     (Re)render every .d2 under <dir> to a sibling .png. The regeneration
                       discipline: run before commit so renders track their source.
  check-dir <dir>      Authoritative: every .d2 has a matching .png (orphan -> exit 1).
                       Advisory: WARN when a .d2 is newer than its .png in the same working
                       tree (mtime staleness). Advisory only — git checkout normalizes mtimes,
                       so a fresh clone cannot distinguish stale from current.

Inline-source <-> standalone-render round-trip (the d2 renderable fence):
  embed <src.d2> <tgt.md>   Insert the d2 source as an inline ```d2 fenced block in <tgt.md>.
  lift <tgt.md>             Extract the FIRST inline ```d2 block to a standalone <out>.d2,
                            render its sibling .png, and replace the fence with an image link.
  inline <tgt.md>           Inverse of lift: replace the FIRST ![](x.png) image link whose
                            sibling x.d2 exists with an inline ```d2 fence carrying that source.

embed (inline source) vs standalone .d2/.png — the trade-off:
  * embed:      the d2 source travels INLINE in the markdown and is rendered at preview/PDF
                time by yf-markdown-pdf. One file, no committed binary, source edits in place.
  * standalone: a committed .d2 + rendered .png pair, referenced by a markdown image link.
                The PNG is reviewable in any viewer with no render step, at the cost of a
                committed binary and a regeneration discipline (check-dir).
  `lift` converts inline -> standalone; `inline` converts standalone -> inline. The pair
  round-trips: the d2 source survives embed -> lift -> inline unchanged.

All subcommands accept --json for machine-readable output. render/render-dir accept
--theme (default 0, light) and --layout (default elk; dagre selectable).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_THEME = "0"
DEFAULT_LAYOUT = "elk"


def _emit(payload: dict, as_json: bool, human: str) -> None:
    if as_json:
        print(json.dumps(payload))
    else:
        print(human)


def d2_path() -> str | None:
    """OS-independent presence check. The ONLY preflight contract."""
    return shutil.which("d2")


def d2_version(exe: str) -> str | None:
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def cmd_preflight(args: argparse.Namespace) -> int:
    exe = d2_path()
    present = exe is not None
    version = d2_version(exe) if exe else None
    payload = {"status": "ok" if present else "missing", "d2_present": present,
               "d2_path": exe, "d2_version": version}
    if present:
        human = f"d2 present: {exe} ({version})"
    else:
        human = ("d2 is MISSING (not on PATH). Install it: `brew install d2`. The skill "
                 "accepts any d2/download flow once d2 is present.")
    _emit(payload, args.json, human)
    return 0 if present else 1


def _render_one(exe: str, src: Path, theme: str, layout: str) -> tuple[bool, str, Path]:
    out = src.with_suffix(".png")
    proc = subprocess.run(
        [exe, "--theme", theme, "--layout", layout, str(src), str(out)],
        capture_output=True, text=True,
    )
    ok = proc.returncode == 0 and out.exists()
    msg = (proc.stderr or proc.stdout).strip()
    return ok, msg, out


def cmd_render(args: argparse.Namespace) -> int:
    exe = d2_path()
    if not exe:
        _emit({"status": "missing", "d2_present": False}, args.json,
              "d2 is MISSING — cannot render. Run `render.py preflight` for guidance.")
        return 1
    src = Path(args.file)
    if src.suffix != ".d2" or not src.is_file():
        _emit({"status": "error", "error": "not a .d2 file", "file": str(src)}, args.json,
              f"Not a .d2 file: {src}")
        return 2
    ok, msg, out = _render_one(exe, src, args.theme, args.layout)
    payload = {"status": "ok" if ok else "error", "source": str(src), "png": str(out),
               "rendered": ok, "message": msg}
    _emit(payload, args.json, (f"rendered {src} -> {out}" if ok else f"FAILED {src}: {msg}"))
    return 0 if ok else 1


def _iter_d2(root: Path):
    return sorted(root.rglob("*.d2"))


def cmd_render_dir(args: argparse.Namespace) -> int:
    exe = d2_path()
    if not exe:
        _emit({"status": "missing", "d2_present": False}, args.json,
              "d2 is MISSING — cannot render. Run `render.py preflight` for guidance.")
        return 1
    root = Path(args.dir)
    if not root.is_dir():
        _emit({"status": "error", "error": "not a directory", "dir": str(root)}, args.json,
              f"Not a directory: {root}")
        return 2
    results, failed = [], 0
    for src in _iter_d2(root):
        ok, msg, out = _render_one(exe, src, args.theme, args.layout)
        results.append({"source": str(src), "png": str(out), "rendered": ok, "message": msg})
        if not ok:
            failed += 1
    payload = {"status": "ok" if failed == 0 else "error", "dir": str(root),
               "count": len(results), "failed": failed, "results": results}
    human = f"render-dir {root}: {len(results)} source(s), {failed} failed"
    _emit(payload, args.json, human)
    return 0 if failed == 0 else 1


def cmd_check_dir(args: argparse.Namespace) -> int:
    root = Path(args.dir)
    if not root.is_dir():
        _emit({"status": "error", "error": "not a directory", "dir": str(root)}, args.json,
              f"Not a directory: {root}")
        return 2
    orphans, stale = [], []
    for src in _iter_d2(root):
        png = src.with_suffix(".png")
        if not png.exists():
            orphans.append(str(src))          # authoritative failure
        elif src.stat().st_mtime > png.stat().st_mtime:
            stale.append(str(src))            # advisory only
    payload = {"status": "ok" if not orphans else "error", "dir": str(root),
               "orphans": orphans, "stale_advisory": stale}
    lines = [f"check-dir {root}: {len(orphans)} orphan(s), {len(stale)} stale (advisory)"]
    for o in orphans:
        lines.append(f"  ORPHAN: {o} has no matching .png")
    for s in stale:
        lines.append(f"  WARN (advisory): {s} is newer than its .png — run render-dir before commit")
    _emit(payload, args.json, "\n".join(lines))
    return 0 if not orphans else 1


# --- Inline d2 fence <-> standalone render round-trip -----------------------
#
# The `d2` renderable fence (canonical registry: _shared/renderable_fences.py).
# A renderable fence's interior is d2 *source* rendered at preview/PDF time, not
# shown verbatim. embed/lift/inline move a diagram between two representations:
#   inline      ```d2\n<source>\n```          (source travels in the markdown)
#   standalone  ![alt](<slug>.png) + <slug>.d2 (committed render + sibling source)

FENCE = "```"
D2_INFO = "d2"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_source(spec: str) -> str:
    """Read d2 source from a path, or from stdin when spec is '-'."""
    if spec == "-":
        return sys.stdin.read()
    return _read_text(Path(spec))


def make_fence(source: str) -> str:
    """A ```d2 fenced block carrying `source` verbatim (no trailing newline)."""
    body = source.rstrip("\n")
    return f"{FENCE}{D2_INFO}\n{body}\n{FENCE}"


def find_d2_fence(text: str) -> tuple[int, int, str] | None:
    """Locate the FIRST ```d2 fenced block.

    Returns (start_line_idx, end_line_idx_inclusive, source) or None. The info
    string must be exactly `d2` (optionally surrounded by whitespace).
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(FENCE) and stripped[len(FENCE):].strip() == D2_INFO:
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == FENCE:
                    source = "\n".join(lines[i + 1:j])
                    return i, j, source
            return None  # unterminated fence
    return None


# An image link whose target ends in .png, e.g. ![alt](path/to/diagram.png)
IMG_LINK_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+\.png)\)")


def find_png_link(text: str, md_dir: Path) -> tuple[int, str, str, Path] | None:
    """Locate the FIRST ![](*.png) image link whose sibling .d2 exists.

    Returns (line_idx, alt, png_path_str, d2_path) or None.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = IMG_LINK_RE.search(line)
        if not m:
            continue
        png_str = m.group("path")
        d2_path = (md_dir / png_str).with_suffix(".d2")
        if d2_path.is_file():
            return i, m.group("alt"), png_str, d2_path
    return None


def cmd_embed(args: argparse.Namespace) -> int:
    source = _read_source(args.source)
    tgt = Path(args.target)
    if not tgt.is_file():
        _emit({"status": "error", "error": "target not a file", "target": str(tgt)}, args.json,
              f"Target markdown not found: {tgt}")
        return 2
    text = _read_text(tgt)
    fence = make_fence(source)
    lines = text.splitlines()
    if args.anchor is not None:
        idx = next((i for i, ln in enumerate(lines) if args.anchor in ln), None)
        if idx is None:
            _emit({"status": "error", "error": "anchor not found", "anchor": args.anchor},
                  args.json, f"Anchor not found in {tgt}: {args.anchor!r}")
            return 2
        block = ["", fence, ""]
        lines[idx + 1:idx + 1] = block
        where = f"after line {idx + 1} (anchor {args.anchor!r})"
        new_text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    else:
        sep = "" if text == "" else ("\n" if text.endswith("\n") else "\n\n")
        new_text = text + sep + fence + "\n"
        where = "appended"
    tgt.write_text(new_text, encoding="utf-8")
    _emit({"status": "ok", "target": str(tgt), "inserted": where,
           "lines": len(source.rstrip(chr(10)).splitlines())}, args.json,
          f"embedded ```d2 block in {tgt} ({where})")
    return 0


def cmd_lift(args: argparse.Namespace) -> int:
    tgt = Path(args.target)
    if not tgt.is_file():
        _emit({"status": "error", "error": "target not a file", "target": str(tgt)}, args.json,
              f"Target markdown not found: {tgt}")
        return 2
    text = _read_text(tgt)
    found = find_d2_fence(text)
    if found is None:
        _emit({"status": "error", "error": "no d2 fence", "target": str(tgt)}, args.json,
              f"No inline ```d2 block found in {tgt}")
        return 1
    start, end, source = found
    md_dir = tgt.parent
    if args.out is not None:
        d2_file = Path(args.out)
        if not d2_file.is_absolute():
            d2_file = md_dir / d2_file
    else:
        d2_file = md_dir / f"{tgt.stem}.d2"
    d2_file.write_text(source.rstrip("\n") + "\n", encoding="utf-8")
    # Render the sibling .png (best-effort; degrade if d2 missing/fails) in _lift_finish.
    return _lift_finish(args, tgt, text, start, end, d2_file, md_dir)


def _lift_finish(args, tgt: Path, text: str, start: int, end: int,
                 d2_file: Path, md_dir: Path) -> int:
    exe = d2_path()
    rendered, msg = False, ""
    png_file = d2_file.with_suffix(".png")
    if exe:
        rendered, msg, png_file = _render_one(exe, d2_file, args.theme, args.layout)
    rel_png = png_file.name if png_file.parent == md_dir else str(png_file)
    alt = args.alt if args.alt is not None else tgt.stem
    img_link = f"![{alt}]({rel_png})"
    lines = text.splitlines()
    lines[start:end + 1] = [img_link]
    new_text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    tgt.write_text(new_text, encoding="utf-8")
    status = "ok" if (rendered or not exe) else "error"
    payload = {"status": status, "target": str(tgt), "d2": str(d2_file),
               "png": str(png_file), "rendered": rendered, "image_link": img_link,
               "d2_present": exe is not None, "message": msg}
    human = (f"lifted ```d2 block from {tgt} -> {d2_file}"
             + (f" + {png_file}" if rendered else
                " (.png NOT rendered: d2 missing)" if not exe else f" (render FAILED: {msg})")
             + f"; replaced fence with {img_link}")
    _emit(payload, args.json, human)
    return 0 if status == "ok" else 1


def cmd_inline(args: argparse.Namespace) -> int:
    tgt = Path(args.target)
    if not tgt.is_file():
        _emit({"status": "error", "error": "target not a file", "target": str(tgt)}, args.json,
              f"Target markdown not found: {tgt}")
        return 2
    text = _read_text(tgt)
    md_dir = tgt.parent
    if args.d2 is not None:
        # Explicit .d2 source + replace the first matching/any png image link.
        d2_file = Path(args.d2)
        source = _read_text(d2_file)
        found = find_png_link(text, md_dir)
        if found is None:
            # No resolvable link: append the fence instead.
            return cmd_embed(_ns(source=str(d2_file), target=str(tgt),
                                 anchor=None, json=args.json))
        line_idx = found[0]
    else:
        found = find_png_link(text, md_dir)
        if found is None:
            _emit({"status": "error", "error": "no resolvable png link", "target": str(tgt)},
                  args.json, f"No ![](*.png) link with a sibling .d2 found in {tgt}")
            return 1
        line_idx, _alt, _png, d2_file = found
        source = _read_text(d2_file)
    fence = make_fence(source)
    lines = text.splitlines()
    lines[line_idx:line_idx + 1] = fence.splitlines()
    new_text = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    tgt.write_text(new_text, encoding="utf-8")
    _emit({"status": "ok", "target": str(tgt), "d2": str(d2_file),
           "inlined_at_line": line_idx}, args.json,
          f"inlined {d2_file} as ```d2 block in {tgt} (replaced image link)")
    return 0


def _ns(**kw) -> argparse.Namespace:
    return argparse.Namespace(**kw)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="render.py", description="d2 diagram render helper.")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("preflight", help="OS-independent `command -v d2` check (no cache probe).")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_preflight)

    sr = sub.add_parser("render", help="Render one .d2 to a sibling .png.")
    sr.add_argument("file")
    sr.add_argument("--theme", default=DEFAULT_THEME)
    sr.add_argument("--layout", default=DEFAULT_LAYOUT)
    sr.add_argument("--json", action="store_true")
    sr.set_defaults(func=cmd_render)

    sd = sub.add_parser("render-dir", help="(Re)render every .d2 under a directory.")
    sd.add_argument("dir")
    sd.add_argument("--theme", default=DEFAULT_THEME)
    sd.add_argument("--layout", default=DEFAULT_LAYOUT)
    sd.add_argument("--json", action="store_true")
    sd.set_defaults(func=cmd_render_dir)

    sc = sub.add_parser("check-dir", help="Verify every .d2 has a .png (+ advisory staleness).")
    sc.add_argument("dir")
    sc.add_argument("--json", action="store_true")
    sc.set_defaults(func=cmd_check_dir)

    se = sub.add_parser(
        "embed",
        help="Insert d2 source as an inline ```d2 fence in a target .md (source travels inline; "
             "rendered at preview/PDF time by yf-markdown-pdf — vs a committed standalone .png).")
    se.add_argument("source", help="path to a .d2 file, or '-' for stdin")
    se.add_argument("target", help="target markdown file to insert the fence into")
    se.add_argument("--anchor", default=None,
                    help="insert the fence after the first line containing this text "
                         "(default: append to end of file)")
    se.add_argument("--json", action="store_true")
    se.set_defaults(func=cmd_embed)

    sl = sub.add_parser(
        "lift",
        help="Extract the first inline ```d2 block to a standalone .d2, render its sibling .png, "
             "and replace the fence with an image link (inline source -> committed render).")
    sl.add_argument("target", help="markdown file containing the ```d2 block")
    sl.add_argument("--out", default=None,
                    help="output .d2 path (default: <target-stem>.d2 beside the .md)")
    sl.add_argument("--alt", default=None, help="alt text for the image link (default: stem)")
    sl.add_argument("--theme", default=DEFAULT_THEME)
    sl.add_argument("--layout", default=DEFAULT_LAYOUT)
    sl.add_argument("--json", action="store_true")
    sl.set_defaults(func=cmd_lift)

    si = sub.add_parser(
        "inline",
        help="Inverse of lift: replace the first ![](*.png) link whose sibling .d2 exists with "
             "an inline ```d2 fence carrying that source (committed render -> inline source).")
    si.add_argument("target", help="markdown file containing the image link")
    si.add_argument("--d2", default=None,
                    help="explicit .d2 source path (default: infer from the .png link's sibling)")
    si.add_argument("--json", action="store_true")
    si.set_defaults(func=cmd_inline)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
