#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check_skill_script_refs — REQ-YF-EMBED-005 / #210.

THE PROTOTYPE, REBUILT (plan-053 Issue 1.0).

This file is the **prototype** rebuilt from EXP-003's stated predicate. No worktree from the
investigation survives, so nothing here was recovered — it is re-derived from the finding's
own specification (EXP-003 § "The predicate"). Issue 3.5 promotes it to its repo-level home
at `scripts/check_skill_script_refs.py`; until then it lives here so Issue 1.6 can drive a
RED against a *present* instrument rather than against an absent one. A fixture that fails
because its instrument is missing is an absent-instrument red, which is R3's named pattern.

THE PREDICATE
-------------
For every invocation `<runner> [flags] <PATH>` inside a **shell-info fence** or an **inline
code span** of an instruction document owned by `skills/<S>/`, `<PATH>` must

  (a) begin with a recognised skill-dir root — `${SKILL_DIR}/`, `<skill-dir>/`, `<yf-NAME>/`,
      or `[~/].{claude,agents}/skills/<name>/`; and
  (b) name an existing file at `skills/<name>/<rest>`.

This is a faithful REPO-SIDE re-expression of "resolves under an installed SKILL_DIR", because
install is a verbatim embed→deploy of `skills/<S>/` (REQ-YF-EMBED-001): `skills/<owner>/<rest>`
exists at repo time **iff** `<SKILL_DIR>/<rest>` exists at run time.

Absence of a recognised root fails by construction. `_shared/`, a bare `scripts/` and a bare
`skills/…/` are all **cwd-dependent**: they resolve in this repository's working tree and
nowhere else, which is exactly the defect #210 is.

THE TWO FAILURE SHAPES ARE DISTINCT AND BOTH ARE IN SCOPE
---------------------------------------------------------
  repo-only      the path is rooted somewhere that only exists here (`_shared/`, bare `scripts/`)
  missing-in-repo the path IS correctly rooted, but names a file that was never vendored

The second is not a lesser case of the first. `pour_fidelity.py` had **no vendored copy at
all**, so rewriting its `SKILL.md` line to `${SKILL_DIR}/scripts/pour_fidelity.py` alone would
have produced a correctly-rooted path that still did not resolve — a green-looking fix that
fixes nothing. A checker that collapsed the two would have certified it.

THE CARVES, AND WHY EACH ONE EXISTS
-----------------------------------
Each carve was required to get the measured false-positive surface to zero. They are not
convenience:

  fences + code spans only  `_shared/` appears 43 times across skills/*.md and exactly ONE of
                            those is an invocation. The other 42 are prose — including
                            plan-050's own note EXPLAINING this defect, which a naive grep
                            flags. Prose about a path is not a use of it.
  a required runner token   without one, every bare path mentioned in a code span is a hit.
  `illustrative`            a path with no directory component (`script.py`) is a generic
                            example, not a reference to a real file.
  the allow marker          `<!-- skill-script-refs: allow <why> -->` opts out a DELIBERATE
                            external reference. Stated, never inferred — an inferred exemption
                            is indistinguishable from an oversight.
  fixtures/ excluded        `skills/*/scripts/fixtures/**` holds corpus fixture DOCUMENTS
                            carrying arbitrary invocations by design. EXP-003's "FP measured
                            to zero" never covered them.

`SPEC.md` and `spec/*.md` are out of scope: they cite repo test paths as Verification commands,
which are correct repo-time citations rather than runtime instructions. Widening to them adds
five rows, all false.

EXIT CONTRACT (three-valued, REQ-YF-EMBED-005)
  0  no violations
  1  at least one violation
  2  the check could not run (no skills/ tree, unreadable file) — a statement about the
     INSTRUMENT, never about the documents
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

#: Documents a *consumer* reads. `README.md` is in scope deliberately: the same break lives
#: there, and excluding it would repeat the prototype-convenience scoping error this check
#: exists to catch (EXP-003's own headline argument, turned on itself).
DOC_GLOBS = ("SKILL.md", "README.md", "agents/*.md", "protocols/*.md", "reference/*.md")

#: Fence info-strings that mean "these lines are commands".
SHELL_INFO = {"bash", "sh", "shell", "console", "zsh", "shell-session"}

#: A path with no directory component is a generic example, not a reference.
RUNNERS = ("uv run", "uvx", "bash", "sh", "python3", "python", "node")

_ALLOW = re.compile(r"<!--\s*skill-script-refs:\s*allow\b(?P<why>[^>]*?)-->")

#: `uv run [--flags] <path>` / `bash [--flags] <path>` / … — the runner, any flags, then the
#: first non-flag token. `--script`-style flags and `--with X` pairs are skipped.
_FLAG = re.compile(r"^-")
_SCRIPTISH = re.compile(r"\.(py|sh)$")

#: Recognised skill-dir roots. Each captures the SKILL NAME (or None when the root is generic).
_ROOTS: list[tuple[re.Pattern, str | None]] = [
    (re.compile(r"^\$\{SKILL_DIR\}/(?P<rest>.+)$"), None),
    (re.compile(r"^\$SKILL_DIR/(?P<rest>.+)$"), None),
    (re.compile(r"^<skill-dir>/(?P<rest>.+)$"), None),
    (re.compile(r"^\"?\$\{SKILL_DIR\}\"?/(?P<rest>.+)$"), None),
    (re.compile(r"^~?/?\.(?:claude|agents)/skills/(?P<name>[^/]+)/(?P<rest>.+)$"), "name"),
    # `<yf-NAME>/…` — the angle-bracket placeholder form. It is a RECOGNISED root per
    # EXP-003's predicate: it names the owning skill explicitly and tells the reader to
    # substitute the resolved skill dir, so it is not cwd-dependent the way a bare
    # `scripts/` is.
    (re.compile(r"^<(?P<name>yf-[a-z0-9-]+)>/(?P<rest>.+)$"), "name"),
    (re.compile(r"^(?P<name>yf-[a-z0-9-]+)/(?P<rest>.+)$"), "name"),
]


def _iter_code_regions(text: str) -> list[tuple[int, str, bool]]:
    """Yield (line-number, line-text, in_shell_fence) for every line in a code region.

    A line is in a code region if it is inside a shell-info fence, or if it carries at least
    one inline code span. Everything else is prose and is never inspected — which is the
    single carve that takes the `_shared/` false-positive count from 42 to 0.
    """
    out: list[tuple[int, str, bool]] = []
    in_fence = False
    fence_is_shell = False
    for n, raw in enumerate(text.splitlines(), 1):
        stripped = raw.lstrip()
        if stripped.startswith("```"):
            if in_fence:
                in_fence = False
                fence_is_shell = False
            else:
                info = stripped[3:].strip().split()
                in_fence = True
                fence_is_shell = bool(info) and info[0].lower() in SHELL_INFO
            out.append((n, raw, False))
            continue
        if in_fence:
            if fence_is_shell:
                out.append((n, raw, True))
            else:
                # A non-shell fence (```python, ```json, ```d2) is not a command listing.
                out.append((n, raw, False))
            continue
        # Prose line: only the inline code spans on it are a code region.
        spans = re.findall(r"`([^`]+)`", raw)
        if spans:
            out.append((n, " ".join(spans), True))
        else:
            out.append((n, raw, False))
    return out


def _invocations(line: str) -> list[str]:
    """Extract the script PATH from every `<runner> [flags] <path>` invocation on one line."""
    found: list[str] = []
    # Normalise command substitution and assignment BEFORE tokenising. Without this,
    # `FIDELITY=$(uv run _shared/pour_fidelity.py …)` — which is #210's own live instance,
    # verbatim, in `yf-plan/SKILL.md` — tokenises its runner as `FIDELITY=$(uv` and is never
    # seen. A checker that misses the defect it was built for is the silent green this plan
    # is about; caught by running the prototype against the tree rather than by reading it.
    line = re.sub(r"\$\(|\)|`|^\s*[A-Za-z_][A-Za-z0-9_]*=", " ", line)
    # Split on shell separators so `a && uv run x.py` is seen.
    for chunk in re.split(r"(?:&&|\|\||[;|])", line):
        toks = chunk.strip().split()
        if not toks:
            continue
        for i, tok in enumerate(toks):
            runner = None
            if tok in ("uv", "uvx") and i + 1 < len(toks) and toks[i + 1] == "run":
                runner, rest = "uv run", toks[i + 2:]
            elif tok in ("uv", "uvx"):
                continue
            elif tok in ("bash", "sh", "python", "python3", "node"):
                runner, rest = tok, toks[i + 1:]
            if runner is None:
                continue
            # Skip flags, and the value of a flag that takes one.
            j = 0
            while j < len(rest):
                t = rest[j]
                if t in ("--with", "-m", "--python", "--directory", "--project"):
                    j += 2
                    continue
                if _FLAG.match(t):
                    j += 1
                    continue
                break
            if j < len(rest):
                cand = rest[j].strip("\"'")
                if _SCRIPTISH.search(cand):
                    found.append(cand)
            break
    return found


def classify(path: str, repo: Path) -> tuple[str, str]:
    """Return (class, detail) for one invocation path.

    Classes: `ok` | `illustrative` | `repo-only` | `missing-in-repo` | `unresolvable`.
    """
    if "/" not in path:
        return "illustrative", "no directory component — a generic example, not a reference"
    for pat, namekey in _ROOTS:
        m = pat.match(path)
        if not m:
            continue
        rest = m.group("rest")
        if namekey is None:
            # `${SKILL_DIR}/…` — the owning skill is the document's own skill; the caller
            # resolves it. Reported as `ok-root` and completed by `check_file`.
            return "ok-root", rest
        name = m.group(namekey)
        target = repo / "skills" / name / rest
        if target.is_file():
            return "ok", str(target.relative_to(repo))
        return "missing-in-repo", f"rooted correctly but skills/{name}/{rest} does not exist"
    if path.startswith("_shared/"):
        return "repo-only", "`_shared/` is a directory in THIS repository and is not one of the six roots the SKILL_DIR resolver searches"
    if path.startswith("scripts/") or path.startswith("./scripts/"):
        return "repo-only", "a bare `scripts/` path is cwd-relative — it resolves from the skill dir and from nowhere else"
    return "unresolvable", "no recognised skill-dir root"


def check_file(doc: Path, repo: Path) -> list[dict]:
    """Return the violation records for one instruction document."""
    owner = doc.relative_to(repo / "skills").parts[0]
    try:
        text = doc.read_text(encoding="utf-8")
    except OSError as e:
        raise Inconclusive(f"cannot read {doc}: {e}") from e

    # Allow markers: a marker on line N suppresses line N, line N+1, and — when line N+1
    # opens a fence — that whole fence block. Deterministic and stated, never inferred.
    allowed: set[int] = set()
    lines = text.splitlines()
    for n, raw in enumerate(lines, 1):
        m = _ALLOW.search(raw)
        if not m:
            continue
        allowed.add(n)
        allowed.add(n + 1)
        if n < len(lines) and lines[n].lstrip().startswith("```"):
            k = n + 1
            while k < len(lines) and not lines[k].lstrip().startswith("```"):
                allowed.add(k + 1)
                k += 1
            allowed.add(k + 1)

    out: list[dict] = []
    for lineno, line, is_code in _iter_code_regions(text):
        if not is_code or lineno in allowed:
            continue
        for path in _invocations(line):
            klass, detail = classify(path, repo)
            if klass == "ok-root":
                target = repo / "skills" / owner / detail
                if target.is_file():
                    klass, detail = "ok", str(target.relative_to(repo))
                else:
                    klass = "missing-in-repo"
                    detail = f"rooted correctly but skills/{owner}/{detail} does not exist"
            out.append({
                "file": str(doc.relative_to(repo)),
                "line": lineno,
                "path": path,
                "class": klass,
                "detail": detail,
            })
    return out


class Inconclusive(RuntimeError):
    """The check could not run — exit 2. A statement about the instrument, never the docs."""


#: A record in one of these classes is a violation.
VIOLATION = {"repo-only", "missing-in-repo", "unresolvable"}


def collect(repo: Path) -> list[dict]:
    skills = repo / "skills"
    if not skills.is_dir():
        raise Inconclusive(f"no skills/ directory at {skills}")
    docs: list[Path] = []
    for sd in sorted(p for p in skills.iterdir() if p.is_dir()):
        for g in DOC_GLOBS:
            docs.extend(sorted(sd.glob(g)))
    recs: list[dict] = []
    for d in docs:
        if "/scripts/fixtures/" in str(d):
            continue
        recs.extend(check_file(d, repo))
    return recs


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="repository root (default: cwd)")
    ap.add_argument("--json", action="store_true", help="emit the structured report")
    ap.add_argument("--all", action="store_true",
                    help="measurement mode: report EVERY invocation, not only violations")
    ap.add_argument("paths", nargs="*", help="limit to these documents")
    a = ap.parse_args(argv)

    repo = Path(a.root).resolve()
    try:
        recs = collect(repo)
    except Inconclusive as e:
        if a.json:
            print(json.dumps({"verdict": "INCONCLUSIVE", "reason": str(e)}, indent=1))
        else:
            print(f"check_skill_script_refs: INCONCLUSIVE — {e}", file=sys.stderr)
        return 2

    if a.paths:
        want = {str(Path(p).resolve().relative_to(repo)) for p in a.paths}
        recs = [r for r in recs if r["file"] in want]

    violations = [r for r in recs if r["class"] in VIOLATION]
    shown = recs if a.all else violations

    if a.json:
        print(json.dumps({
            "verdict": "FAIL" if violations else "PASS",
            "checked": len(recs),
            "violations": len(violations),
            "by_class": {k: sum(1 for r in recs if r["class"] == k)
                         for k in sorted({r["class"] for r in recs})},
            "records": shown,
        }, indent=1))
    else:
        for r in shown:
            print(f"{r['class']:<16} {r['file']}:{r['line']}  {r['path']}  — {r['detail']}")
        if violations:
            print(f"\ncheck_skill_script_refs: {len(violations)} violation(s) "
                  f"of {len(recs)} invocation(s) checked", file=sys.stderr)
        else:
            print(f"check_skill_script_refs: {len(recs)} invocation(s) checked, 0 violations")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
