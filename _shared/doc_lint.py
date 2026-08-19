#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Schema-driven linter for yf artifact documents (REQ-DATA-024).

**MINIMAL engine — plan-047 Epic 1.** Reads `_shared/document_types/<type>.toml`, walks each
type's path set, and emits `{"findings": [...]}` on `--json`. The severity/status-promotion
and full path machinery land in Epic 4; what is here is exactly enough to make the Epic-3 gate
*real*.

**The one thing that must be true from the first commit: `sys.exit(1)` on any error-severity
finding.** EXP-005 reproduced a linter printing `errors=4` while the delegating engine reported
`status: pass`, because it exited 0. A linter with no exit code is not a step.

Exit contract (REQ-DATA-024), binary at every binding point:

    0  no error-severity finding            (verdict PASS)
    1  at least one error-severity finding  (verdict FAIL)
    2  the linter could not run             (verdict INCONCLUSIVE)

`INCONCLUSIVE` means *only* "could not run". "Not finished yet" is a `W` finding **inside a
PASS** — it never changes the exit code. `INCOMPLETE` is the reviewer agent's vocabulary and
never appears here.

Usage:

    uv run _shared/doc_lint.py                       # lint every type over the repo
    uv run _shared/doc_lint.py --json                # machine-readable
    uv run _shared/doc_lint.py --path <p> [--path p] # only these files
    uv run _shared/doc_lint.py --type plan           # only this type
    uv run _shared/doc_lint.py --no-exclude          # POSITIVE CONTROL: ignore carve-outs
"""

from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TYPES_DIR = Path(__file__).resolve().parent / "document_types"

ERROR, WARN, REPORT = "E", "W", "R"

# Status-aware promotion (REQ-DATA-024). A plan's `status` selects the severity mapping.
#
# **Why this is not cosmetic, and why it lands with the recipe row rather than after it.**
# Measured on this corpus: all 46 historical bundles are `complete`, and the raw linter
# reports 320 error-severity findings across 169 files. Adding the `doclint` recipe row
# without this mapping would make the repo's own FAST tier permanently RED — and, decisively,
# it would make the row's own falsification VACUOUS: injecting a mutant and observing
# `status: fail` proves nothing when the tier was already failing. A control that cannot
# distinguish its signal from the background is the same defect class as one that cannot fire.
STATUS_SEVERITY = {
    # drafting statuses: completeness warnings are informational, structure still errors
    "scoping": {WARN: WARN},
    "investigating": {WARN: WARN},
    "drafting": {WARN: WARN},
    # under review: a warning becomes an error — the plan is claiming to be finished
    "review": {WARN: ERROR},
    "ready-for-approval": {WARN: ERROR},
    # a finished plan is REPORT-ONLY, never an error. History is not re-judged by a rule
    # written after it: the 46 completed bundles predate every schema in document_types/.
    # Past the enforcement point. The linter's binding is at INTAKE (`review` /
    # `ready-for-approval`); once a plan is approved its content is frozen by the
    # fingerprint (REQ-PORT-040), so re-judging it mid-execution would manufacture exactly
    # the stale-approved churn REQ-DATA-025 exists to avoid.
    "approved": {WARN: REPORT, ERROR: REPORT},
    "executing": {WARN: REPORT, ERROR: REPORT},
    "reconciling": {WARN: REPORT, ERROR: REPORT},
    "complete": {WARN: REPORT, ERROR: REPORT},
}


class Inconclusive(RuntimeError):
    """The linter could not run — exit 2, verdict INCONCLUSIVE. Never a FAIL."""


# --- schema loading ----------------------------------------------------------------


def load_schemas(only: str | None = None) -> list[dict]:
    if not TYPES_DIR.is_dir():
        raise Inconclusive(f"no document_types/ directory at {TYPES_DIR}")
    out = []
    for f in sorted(TYPES_DIR.glob("*.toml")):
        try:
            d = tomllib.load(f.open("rb"))
        except Exception as e:  # malformed schema is a harness failure, not a document FAIL
            raise Inconclusive(f"{f.name}: {e}") from e
        if d.get("type") != f.stem:
            raise Inconclusive(f"{f.name}: `type` is {d.get('type')!r}, expected {f.stem!r}")
        if d.get("producer_class") == "code-generated" and not d.get("derive_from"):
            raise Inconclusive(f"{f.name}: code-generated type must set `derive_from`")
        if only and d["type"] != only:
            continue
        out.append(d)
    if only and not out:
        raise Inconclusive(f"no schema for type {only!r}")
    return out


def resolve_derived(dotted: str) -> list[str]:
    """Import `<module>.<ATTR>` from `_shared/` and return it as a list of section names."""
    mod_name, _, attr = dotted.rpartition(".")
    path = Path(__file__).resolve().parent / f"{mod_name}.py"
    if not path.exists():
        raise Inconclusive(f"derive_from: no module {mod_name!r} in _shared/")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, attr):
        raise Inconclusive(f"derive_from: {mod_name} has no attribute {attr!r}")
    return list(getattr(mod, attr))


# --- document parsing --------------------------------------------------------------


def bundle_status(path: Path) -> str | None:
    """The `status` of the plan bundle owning `path`, or None if it is not in one.

    Walks up to the nearest directory containing a `plan.md` and reads its status
    frontmatter-first with a `**Status:**` fallback (REQ-DATA-015 read order).
    """
    for d in [path if path.is_dir() else path.parent, *path.parents]:
        pm = d / "plan.md"
        if not pm.is_file():
            continue
        text = pm.read_text(encoding="utf-8", errors="replace")
        if text.startswith("---\n"):
            end = text.find("\n---\n", 4)
            if end > 0:
                m = re.search(r"^status:\s*['\"]?([\w-]+)", text[4:end], re.M)
                if m:
                    return m.group(1)
        m = re.search(r"^\*\*Status:\*\*\s*(\S+)", text, re.M)
        return m.group(1) if m else None
    return None


def frontmatter_keys(text: str) -> set[str]:
    if not text.startswith("---\n"):
        return set()
    end = text.find("\n---\n", 4)
    if end < 0:
        return set()
    keys = set()
    for line in text[4:end].split("\n"):
        m = re.match(r"^([A-Za-z_][\w.-]*):", line)
        if m:
            keys.add(m.group(1))
    return keys


def sections(text: str, any_level: bool = False) -> list[str]:
    """Ordered headings, skipping fenced code blocks. Level 2 only unless `any_level`."""
    out, fenced = [], False
    for line in text.split("\n"):
        if line.startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = re.match(r"^#{2,6} +(.+?)\s*$" if any_level else r"^## +(.+?)\s*$", line)
        if m:
            out.append(m.group(1))
    return out


def section_body(text: str, name: str) -> str | None:
    lines, body, fenced, capturing = text.split("\n"), [], False, False
    for line in lines:
        if line.startswith("```"):
            fenced = not fenced
            if capturing:
                body.append(line)
            continue
        if not fenced and re.match(r"^## +", line):
            if capturing:
                break
            capturing = re.match(r"^## +(.+?)\s*$", line).group(1) == name
            continue
        if capturing:
            body.append(line)
    return "\n".join(body) if capturing or body else None


def first_table(body: str) -> tuple[list[str], list[list[str]]] | None:
    """Return (header cells, data rows) of the first GFM table in `body`."""
    rows, in_tbl = [], False
    for line in body.split("\n"):
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            rows.append([c.strip() for c in s[1:-1].split("|")])
            in_tbl = True
        elif in_tbl:
            break
    if len(rows) < 2:
        return None
    return rows[0], rows[2:]  # rows[1] is the alignment row


# --- checks ------------------------------------------------------------------------


def run_check(chk: dict, text: str, schema: dict) -> list[str]:
    """Return a list of failure detail strings ([] = the check passed)."""
    kind = chk.get("kind")
    if kind in ("headings-present", "headings-any-level"):
        want = chk.get("value") or resolve_derived(schema["derive_from"])
        have = sections(text, any_level=(kind == "headings-any-level"))
        missing = [s for s in want if s not in have]
        if missing:
            return ["missing section(s): " + ", ".join(missing)]
        idx = [have.index(s) for s in want]
        if idx != sorted(idx):
            return ["sections out of order: expected " + " -> ".join(want)]
        return []
    if kind == "frontmatter-keys":
        missing = [k for k in chk["value"] if k not in frontmatter_keys(text)]
        return ["missing frontmatter key(s): " + ", ".join(missing)] if missing else []
    if kind == "regex-absent":
        return ([f"forbidden pattern present: {chk['pattern']}"]
                if re.search(chk["pattern"], text, re.M) else [])
    if kind == "regex-present":
        return ([] if re.search(chk["pattern"], text, re.M)
                else [f"required pattern absent: {chk['pattern']}"])
    if kind in ("table-columns", "row-id-grammar"):
        body = section_body(text, chk["section"])
        if body is None:
            return [f"section not found: {chk['section']}"]
        tbl = first_table(body)
        if tbl is None:
            return [f"no table under ## {chk['section']}"]
        header, data = tbl
        if kind == "table-columns":
            return ([] if header == chk["value"]
                    else [f"## {chk['section']} columns are {header}, expected {chk['value']}"])
        pat, seen, bad = re.compile(chk["pattern"]), set(), []
        for r in data:
            cell = r[0].strip() if r else ""
            if not pat.match(cell):
                bad.append(f"row id {cell!r} does not match {chk['pattern']}")
            elif cell in seen:
                bad.append(f"duplicate row id {cell!r}")
            else:
                seen.add(cell)
        return bad
    raise Inconclusive(f"unknown check kind: {kind!r}")


def _rel(p: Path, root: Path) -> str:
    """Repo-relative when possible; an explicit --path outside the root stays absolute."""
    try:
        return str(p.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(p)


# --- walking ------------------------------------------------------------------------


def select(schema: dict, root: Path, use_exclude: bool = True) -> list[Path]:
    hits: set[Path] = set()
    for g in schema["paths"]:
        hits.update(p for p in root.glob(g) if p.is_file())
    if use_exclude:
        for g in schema.get("exclude", []):
            hits = {p for p in hits
                    if not fnmatch.fnmatch(str(p.relative_to(root)), g)
                    and not fnmatch.fnmatch(str(p.relative_to(root)), g.rstrip("/*") + "/*")}
    return sorted(hits)


def lint(root: Path, only_type: str | None, only_paths: list[Path] | None,
         use_exclude: bool = True) -> dict:
    """Lint the repo, or an explicit file set.

    `--path` is an **explicit override**, not a filter over the glob-selected set: a caller
    naming a file means "lint this file", and that must work for a path the type's globs do
    not select — a committed fixture under `tests/fixtures/doclint/<type>/` lives deliberately
    outside `docs/plans/**` so the engine does not lint its own test corpus. Without the
    override the fixture test would silently check nothing and pass, which is the exact
    vacuous-green class this plan exists to close.

    With `--path` and no `--type`, a file is linted against every schema whose globs select
    it (so an ordinary on-edit call still routes by path). With `--type`, it is linted against
    that schema regardless of the globs.
    """
    findings, checked = [], 0
    for schema in load_schemas(only_type):
        if only_paths is not None:
            if only_type:
                files = sorted({p for p in only_paths if p.is_file()})
            else:
                selected = {f.resolve() for f in select(schema, root, use_exclude)}
                files = sorted({p for p in only_paths if p.resolve() in selected})
        else:
            files = select(schema, root, use_exclude)
        for f in files:
            checked += 1
            text = f.read_text(encoding="utf-8", errors="replace")
            status = bundle_status(f)
            mapping = STATUS_SEVERITY.get(status or "", {})
            for chk in schema.get("checks", []):
                for detail in run_check(chk, text, schema):
                    declared = chk.get("severity", ERROR)
                    findings.append({
                        "path": _rel(f, root), "type": schema["type"],
                        "check": chk["id"],
                        "severity": mapping.get(declared, declared),
                        "declared_severity": declared,
                        "bundle_status": status,
                        "detail": detail,
                    })
    errors = sum(1 for x in findings if x["severity"] == ERROR)
    warnings = sum(1 for x in findings if x["severity"] == WARN)
    reported = sum(1 for x in findings if x["severity"] == REPORT)
    return {
        "verdict": "FAIL" if errors else "PASS",
        "files_checked": checked, "errors": errors,
        "warnings": warnings, "report_only": reported, "findings": findings,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--type")
    ap.add_argument("--path", action="append", type=Path)
    ap.add_argument("--root", type=Path, default=REPO_ROOT)
    ap.add_argument("--show-report-only", action="store_true",
                    help="Print R-severity findings from `complete` bundles too.")
    ap.add_argument("--no-exclude", action="store_true",
                    help="POSITIVE CONTROL: ignore every carve-out glob")
    a = ap.parse_args()
    try:
        res = lint(a.root, a.type, a.path, use_exclude=not a.no_exclude)
    except Inconclusive as e:
        out = {"verdict": "INCONCLUSIVE", "reason": str(e),
               "files_checked": 0, "errors": 0, "warnings": 0, "findings": []}
        print(json.dumps(out, indent=1) if a.json else f"INCONCLUSIVE: {e}", file=sys.stdout)
        return 2
    if a.json:
        print(json.dumps(res, indent=1))
    else:
        for x in res["findings"]:
            if x["severity"] == REPORT and not a.show_report_only:
                continue
            print(f"{x['severity']} {x['path']}: [{x['check']}] {x['detail']}")
        print(f"{res['verdict']}: {res['files_checked']} file(s), "
              f"{res['errors']} error(s), {res['warnings']} warning(s), "
              f"{res['report_only']} report-only")
    # The whole point of the file: a non-zero exit on an error-severity finding.
    return 1 if res["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
