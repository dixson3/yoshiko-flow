#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate a skill README's ASCII-tree layout fence (REQ-YF-DOC-002..006).

The **producer** half of the contract `scripts/checks/check_skill_readme_contract.py` verifies.
One walk, one form, one parser — the reason REQ-YF-DOC-003 standardises on the ASCII tree at all.

**Existing `# description` comments are PRESERVED, never regenerated** (REQ-YF-DOC-005). This is
the single most important property here and it is R3 in plan-061's risk table: the descriptions
are hand-authored, they are the only thing that makes a fence more useful than `ls -R`, and a
generator that silently dropped them would pass the checker while destroying the artifact. Entries
that have no comment are **reported** (`--report-uncommented`) rather than silently emitted bare.

Comment provenance is by **entry path**, so a comment survives the entry moving position in the
tree, and survives a fence whose old root line was stale (`markdown-lint/` rather than
`skills/yf-markdown-lint/`) — which is 10 of the 19 pre-existing fences.

  --check    exit 1 if the on-disk fence differs from the generated one (no write)
  --write    rewrite the fence in place
  (neither)  print the generated fence to stdout

EXIT  0 clean / written  ·  1 drift (under --check)  ·  2 INCONCLUSIVE (could not run)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

EXCLUDE_PARTS = ("__pycache__", ".pytest_cache")
EXCLUDE_SUFFIX = (".pyc", ".pyo")
EXCLUDE_NAMES = (".DS_Store",)

FENCE_RE = re.compile(r"^\s*```")
HEADING_RE = re.compile(r"^(#{2,6})\s+(.*?)\s*$")
# Matches BOTH conformant tree lines and the legacy two-space-indent form, because the whole
# point of harvesting is to carry comments ACROSS the conversion.
TREE_LINE = re.compile(r"^(?:[│ ]*)(?:├── |└── )?(?P<name>[^\s#][^#]*?)(?:\s{2,}#?\s*(?P<c>\S.*?))?\s*$")


def inconclusive(msg: str) -> int:
    print(json.dumps({"tool": "gen-skill-readme-fence", "verdict": "INCONCLUSIVE",
                      "exit": 2, "reason": msg}, indent=1))
    print(f"gen-skill-readme-fence: INCONCLUSIVE — {msg}", file=sys.stderr)
    return 2


def repo_root() -> Path:
    try:
        return Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"],
                                            text=True, stderr=subprocess.DEVNULL).strip())
    except Exception:
        return Path.cwd()


def git_ignored(root: Path, paths: list[Path]) -> set[str]:
    if not paths:
        return set()
    try:
        proc = subprocess.run(["git", "-C", str(root), "check-ignore", "--stdin"],
                              input="\n".join(str(p) for p in paths),
                              capture_output=True, text=True)
        return {ln.strip() for ln in proc.stdout.splitlines() if ln.strip()}
    except Exception:
        return set()


# --------------------------------------------------------------------------- harvest

def locate_fence(text: str) -> tuple[int, int] | None:
    """`(start, end)` line indices of the layout fence's ``` lines, or None."""
    lines = text.splitlines()
    in_layout = False
    for i, line in enumerate(lines):
        m = HEADING_RE.match(line)
        if m:
            in_layout = len(m.group(1)) == 2 and "layout" in m.group(2).lower()
            continue
        if in_layout and FENCE_RE.match(line):
            for j in range(i + 1, len(lines)):
                if FENCE_RE.match(lines[j]):
                    return i, j
            return None
    return None


def harvest_comments(text: str) -> dict[str, str]:
    """Existing `# description` text, keyed by BASENAME (REQ-YF-DOC-005).

    Keyed by basename rather than by full path so a comment survives the entry moving, and
    survives a stale fence root. Collisions are rare and resolved first-wins; a wrong-but-
    plausible carried comment is a strictly better failure than a silently dropped one.
    """
    span = locate_fence(text)
    out: dict[str, str] = {}
    if span is None:
        # Fall back to a BULLET-list layout section (`- \`SKILL.md\` — the conventions…`),
        # which is the form 4 of the 19 pre-existing READMEs use. Their descriptions are the
        # richest in the corpus; dropping them because they were not in a fence would be the
        # exact R3 loss this function exists to prevent.
        lines, in_layout = text.splitlines(), False
        for line in lines:
            m = HEADING_RE.match(line)
            if m:
                in_layout = len(m.group(1)) == 2 and "layout" in m.group(2).lower()
                continue
            if not in_layout:
                continue
            b = re.match(r"^\s*-\s+`([^`]+)`\s*[—–-]\s*(.+?)\s*$", line)
            if b:
                out.setdefault(Path(b.group(1).rstrip("/")).name, b.group(2).strip())
        return out

    start, end = span
    for line in text.splitlines()[start + 1:end]:
        if not line.strip():
            continue
        m = TREE_LINE.match(line)
        if not m:
            continue
        name = (m.group("name") or "").strip()
        comment = (m.group("c") or "").strip()
        if not name or not comment:
            continue
        out.setdefault(Path(name.rstrip("/")).name, comment)
    return out


# --------------------------------------------------------------------------- generate

def walk(root: Path, sd: Path) -> list[Path]:
    files: list[Path] = []
    for p in sorted(sd.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(sd)
        if any(part in EXCLUDE_PARTS for part in rel.parts):
            continue
        if p.suffix in EXCLUDE_SUFFIX or p.name in EXCLUDE_NAMES:
            continue
        files.append(p)
    ignored = git_ignored(root, files)
    return [p for p in files
            if str(p) not in ignored and str(p.relative_to(root)) not in ignored]


def build_tree(rels: list[Path]) -> dict:
    tree: dict = {}
    for rel in rels:
        node = tree
        for part in rel.parts[:-1]:
            node = node.setdefault(part + "/", {})
        node[rel.parts[-1]] = None
    return tree


def render(tree: dict, comments: dict[str, str], prefix: str = "",
           uncommented: list[str] | None = None, path: str = "") -> list[tuple[str, str]]:
    """Rows of `(drawn_name, comment)`; column alignment is applied by the caller."""
    rows: list[tuple[str, str]] = []
    # Directories first, then files — each alphabetically. Stable and diff-friendly.
    keys = sorted(tree, key=lambda k: (not k.endswith("/"), k.lower()))
    for i, key in enumerate(keys):
        last = i == len(keys) - 1
        rows.append((prefix + ("└── " if last else "├── ") + key,
                     comments.get(Path(key.rstrip("/")).name, "")))
        if not key.endswith("/") and not comments.get(Path(key).name) and uncommented is not None:
            uncommented.append(path + key)
        if tree[key] is not None:
            rows += render(tree[key], comments, prefix + ("    " if last else "│   "),
                           uncommented, path + key)
    return rows


def generate(root: Path, name: str, comments: dict[str, str]) -> tuple[str, list[str]]:
    sd = root / "skills" / name
    rels = [p.relative_to(sd) for p in walk(root, sd)]
    uncommented: list[str] = []
    rows = render(build_tree(rels), comments, uncommented=uncommented)
    width = max((len(d) for d, _ in rows), default=0)
    lines = [f"skills/{name}/"]
    for drawn, comment in rows:
        lines.append(f"{drawn.ljust(width)}  # {comment}" if comment else drawn)
    return "\n".join(lines), uncommented


# --------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("skills", nargs="*", help="Skill names. Default: every skills/*/ dir.")
    ap.add_argument("--check", action="store_true", help="Exit 1 on drift; never write.")
    ap.add_argument("--write", action="store_true", help="Rewrite the fence in place.")
    ap.add_argument("--report-uncommented", action="store_true",
                    help="List entries that have no `# description` (REQ-YF-DOC-005).")
    ap.add_argument("--json", action="store_true", dest="as_json")
    a = ap.parse_args()

    root = repo_root()
    sroot = root / "skills"
    if not sroot.is_dir():
        return inconclusive(f"{sroot} does not exist")

    names = a.skills or sorted(p.name for p in sroot.glob("*")
                               if p.is_dir() and (p / "SKILL.md").is_file())
    results, drift = [], []
    for name in names:
        readme = sroot / name / "README.md"
        if not readme.is_file():
            results.append({"skill": name, "status": "no-readme"})
            continue
        text = readme.read_text(encoding="utf-8")
        fence, uncommented = generate(root, name, harvest_comments(text))
        span = locate_fence(text)
        row = {"skill": name, "uncommented": uncommented}

        if a.write:
            lines = text.splitlines()
            if span is None:
                results.append({**row, "status": "no-fence",
                                "note": ("no layout fence found — author the `## File layout` "
                                         "section first; this tool rewrites, it does not create")})
                continue
            start, end = span
            new = lines[:start + 1] + fence.splitlines() + lines[end:]
            readme.write_text("\n".join(new) + "\n", encoding="utf-8")
            results.append({**row, "status": "written"})
            continue

        if a.check:
            current = "\n".join(text.splitlines()[span[0] + 1:span[1]]).rstrip() if span else None
            if current != fence:
                drift.append(name)
                results.append({**row, "status": "drift"})
            else:
                results.append({**row, "status": "clean"})
            continue

        if not a.as_json:
            print(f"# skills/{name}/README.md")
            print("```")
            print(fence)
            print("```")
        results.append({**row, "status": "generated", "fence": fence})

    if a.as_json or a.check or a.write or a.report_uncommented:
        payload = {"tool": "gen-skill-readme-fence",
                   "verdict": "DRIFT" if drift else "OK",
                   "skills": len(names), "drift": drift, "results": results}
        if a.report_uncommented:
            payload["uncommented_total"] = sum(len(r.get("uncommented", [])) for r in results)
        print(json.dumps(payload, indent=1))
    return 1 if (a.check and drift) else 0


if __name__ == "__main__":
    sys.exit(main())
