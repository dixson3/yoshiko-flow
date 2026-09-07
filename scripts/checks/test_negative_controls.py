#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""test_negative_controls.py — every plan-066 checker, OBSERVED TO FAIL.

**A CHECKER NEVER OBSERVED TO FAIL IS NOT EVIDENCE.** This is not a maxim; it is a measurement.
plan-066 EXP-001's checker B returned `PASS (0 mismatches), EXIT=0` against a tree carrying 15
real defects, because the shared root `.agents/skills` CONTAINS the harness id `agents`, so
repaired rows scanned as ambiguous and were silently skipped. The checker was wrong in exactly
the direction that looks like success.

**THE CONTROL IS CODE-SIDE, AND THAT IS THE WHOLE POINT.** A doc-side control — break a doc,
watch the checker complain — cannot catch the failure above, because the docs were already
broken and the checker was already silent. The convention is therefore inverted: **mutate the
SOURCE OF TRUTH under docs that PASS, and require the checker to FAIL.**

    1. copy the repo tree to a sandbox      (the live repository is NEVER mutated)
    2. repair the DOCS in the sandbox until the checker is green   <- the precondition
    3. mutate the CODE-SIDE source of truth
    4. require the checker to exit non-zero                        <- the observation

Step 2 is what makes step 4 mean something. Mutating code under already-red docs proves nothing:
the checker would have been red either way.

**THE VACUITY FLOORS ARE IN THIS TEST, NOT ONLY IN THE CRITERION** (plan-066 pass-1 C9). A
harness that silently skips a checker exits 0 and opens the capability gate — EXP-001's
checker-B failure mode, one level up. So this file PRINTS AND ASSERTS a per-checker
observed-failure count and refuses to pass below `--min-checkers`.

EXIT  0 every checker was observed to fail  ·  1 one was not  ·  2 could not run
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CHECK = "test_negative_controls"


def repo_root() -> Path:
    return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True, check=True).stdout.strip())


def inconclusive(msg: str) -> int:
    print(f"{CHECK}: INCONCLUSIVE — {msg}", file=sys.stderr)
    return 2


def sandbox(root: Path, tmp: Path) -> Path:
    """A copy of everything the checkers read. The live repo is never touched."""
    dst = tmp / "tree"
    dst.mkdir()
    for rel in ("skills", "web/content", "web/plugins", "yf/src", "scripts/checks",
                "README.md", "AGENTS.md"):
        src = root / rel
        if not src.exists():
            continue
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, out, symlinks=True,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "output"))
        else:
            shutil.copy2(src, out)
    return dst


def run(root: Path, script: str, extra: list[str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["uv", "run", f"scripts/checks/{script}", "--root", str(root),
                           *(extra or [])], cwd=root, capture_output=True, text=True)


def sub_file(path: Path, pairs: list[tuple[str, str]], *, required=True) -> int:
    """Literal replacements, ASSERTING EACH ANCHOR MATCHED.

    A bare replace that matches nothing changes nothing and reports success — the phantom-edit
    class this plan's own review history hit twice. Every substitution is counted and verified.
    """
    if not path.is_file():
        if required:
            raise RuntimeError(f"control target absent: {path}")
        return 0
    text = path.read_text(encoding="utf-8")
    n = 0
    for old, new in pairs:
        if old not in text:
            if required:
                raise RuntimeError(f"control ANCHOR NOT FOUND in {path.name}: {old[:60]!r}")
            continue
        text = text.replace(old, new)
        n += 1
    path.write_text(text, encoding="utf-8")
    return n


# ---------------------------------------------------------------------------
# Per-checker controls. Each returns (repair_docs, mutate_code).
# ---------------------------------------------------------------------------

def ctl_counts(tree: Path) -> tuple[str, str]:
    """Bring the docs to green, then ADD A SKILL and A FORMULA code-side.

    THE REPAIRS ARE BEST-EFFORT AND THE PRECONDITION IS `pre == 0`, not "these edits applied".
    Measured: this function originally hard-asserted the pre-repair strings (`**19 skills**`),
    and once Epic 4 repaired the live docs the control ERRORED — its "make the docs green" step
    could not find text that was already green. A control whose setup is pinned to one broken
    revision expires the moment the defect is fixed, which is precisely when you still need it.
    """
    sub_file(tree / "web/content/pages/architecture.md",
             [("**19 skills**", "**20 skills**"), ("**utility (7)**", "**utility (8)**")],
             required=False)
    sub_file(tree / "web/content/images/architecture.d2",
             [("embedded skills (18)", "embedded skills (20)"),
              ("beads group (8)\\nplan · research · incubator",
               "beads group (5)\\nbeads-init · beads-extra · beads-authoring"),
              ("utility group (6)", "utility group (8)")], required=False)
    sub_file(tree / "web/content/images/formulas.d2",
             [("three shipped standard formulas", "five shipped standard formulas")],
             required=False)
    return ("counted-set claims green (repaired where still needed)",
            "a 21st skill and a 6th formula added to the SOURCE OF TRUTH")


def mut_counts(tree: Path) -> None:
    new = tree / "skills/zz-control-skill"
    new.mkdir(parents=True, exist_ok=True)
    (new / "SKILL.md").write_text("---\nname: zz-control-skill\nskill-group: utility\n---\n")
    (new / "formulas").mkdir(exist_ok=True)
    (new / "formulas/zz-control.formula.toml").write_text("# control\n")


def ctl_harness(tree: Path) -> tuple[str, str]:
    """Repair every path/transform claim; then RETARGET a harness in `harness_desc.rs`."""
    for rel in ("web/content/pages/architecture.md", "web/content/pages/install.md",
                "web/content/images/install-matrix.d2", "README.md", "AGENTS.md"):
        p = tree / rel
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8")
        for tok in (".config/opencode/skills", ".opencode/skills",
                    ".pi/agent/skills", ".pi/skills"):
            t = t.replace(tok, ".agents/skills")
        t = re.sub(r"`?lowercase-hyphen,?\s*max64`?", "no name transform", t)
        t = t.replace("lowercase-hyphen", "no-transform").replace("max64", "no-limit")
        p.write_text(t, encoding="utf-8")
    return ("harness path/transform claims repaired",
            "`pi`'s user_skills_subpath retargeted in harness_desc.rs")


def mut_harness(tree: Path) -> None:
    rs = tree / "yf/src/harness_desc.rs"
    text = rs.read_text(encoding="utf-8")
    # Retarget ONLY pi's block, so the docs (now saying `.agents/skills`) become wrong.
    m = re.search(r'(id:\s*"pi"\s*,.*?user_skills_subpath:\s*)"[^"]*"', text, re.S)
    if not m:
        raise RuntimeError("control ANCHOR NOT FOUND: pi's user_skills_subpath")
    rs.write_text(text[:m.end(1)] + '".control/skills"' + text[m.end():], encoding="utf-8")


def ctl_pagecontract(tree: Path) -> tuple[str, str]:
    """Docs already pass (every skill has a page); then SHIP A NEW SKILL with no page."""
    return ("every shipped skill already has a page (checker is green)",
            "a new skill shipped with NO page — the exact 75a5796 shape")


def mut_pagecontract(tree: Path) -> None:
    new = tree / "skills/zz-control-nopage"
    new.mkdir(parents=True, exist_ok=True)
    (new / "SKILL.md").write_text("---\nname: zz-control-nopage\nskill-group: utility\n---\n")


def ctl_backend(tree: Path) -> tuple[str, str]:
    """Repair every multi-backend claim; then RE-INTRODUCE one on the source side."""
    for rel in ("web/content/pages/architecture.md", "web/content/pages/glossary.md",
                "web/content/pages/beads-concepts.md", "web/content/images/architecture.d2",
                "web/content/skills/yf-plan.md", "README.md"):
        p = tree / rel
        if not p.is_file():
            continue
        t = p.read_text(encoding="utf-8")
        t = re.sub(r"\(GitHub,\s*GitLab,\s*or\s*Jira\)", "(GitHub)", t, flags=re.I)
        t = re.sub(r"GitHub\s*/\s*GitLab\s*/\s*Jira", "GitHub", t, flags=re.I)
        t = re.sub(r"GitHub\s+or\s+GitLab", "GitHub", t, flags=re.I)
        t = re.sub(r"github\s*\|\s*gitlab[^`\n]*", "github", t, flags=re.I)
        t = re.sub(r"\bbd\s+(github|gitlab|jira)\s+push\b", "upstream.py push", t, flags=re.I)
        t = re.sub(r"GitLab\s*[,/]\s*Jira", "GitHub", t, flags=re.I)
        p.write_text(t, encoding="utf-8")
    return ("multi-backend claims repaired",
            "a `bd gitlab push` claim re-introduced into a skill page")


def mut_backend(tree: Path) -> None:
    p = tree / "web/content/skills/yf-beads-upstream.md"
    if not p.is_file():
        raise RuntimeError("control target absent: yf-beads-upstream.md")
    p.write_text(p.read_text(encoding="utf-8")
                 + "\n\nPush upstream with `bd gitlab push <ids>`.\n", encoding="utf-8")


CONTROLS = {
    "check_web_counts.py": (ctl_counts, mut_counts),
    "check_web_harness_paths.py": (ctl_harness, mut_harness),
    "check_skill_page_contract.py": (ctl_pagecontract, mut_pagecontract),
    "check_web_backend_claim.py": (ctl_backend, mut_backend),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--checker", action="append", default=None)
    ap.add_argument("--min-checkers", type=int, default=4,
                    help="VACUITY FLOOR: fewer checkers exercised than this fails, so a harness "
                         "that silently skips one cannot exit 0")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = repo_root()
    names = a.checker or sorted(CONTROLS)
    results, observed_failures = {}, 0

    for name in names:
        if name not in CONTROLS:
            return inconclusive(f"no control defined for {name}")
        repair, mutate = CONTROLS[name]
        with tempfile.TemporaryDirectory() as td:
            try:
                tree = sandbox(root, Path(td))
                repaired, mutation = repair(tree)
                pre = run(tree, name)
                mutate(tree)
                post = run(tree, name)
            except Exception as exc:
                results[name] = {"error": f"{type(exc).__name__}: {exc}"}
                print(f"  {name}: ERROR — {exc}")
                continue
        # TWO CONDITIONS, REPORTED SEPARATELY, because they fail for opposite reasons.
        # `pre != 0` means the SETUP is broken — the docs were never brought to green, so the
        # mutation proves nothing. `post != 1` means the CHECKER is blind. Collapsing them would
        # hide which half went wrong.
        setup_ok = pre.returncode == 0
        ok = setup_ok and post.returncode == 1
        results[name] = {"repaired": repaired, "mutation": mutation,
                         "pre_exit": pre.returncode, "post_exit": post.returncode,
                         "setup_ok": setup_ok, "observed_failure": ok}
        if ok:
            observed_failures += 1
        status = "OBSERVED-FAIL" if ok else "NOT OBSERVED"
        print(f"  {name}: pre={pre.returncode} (want 0, docs repaired) "
              f"post={post.returncode} (want 1, code mutated) -> {status}")
        if not ok:
            print("      SETUP FAILED — docs were not green before the mutation, so the "
                  "observation proves nothing" if not setup_ok
                  else "      CHECKER IS BLIND — docs green, source of truth mutated, still exit 0")
            print(f"      repaired: {repaired}")
            print(f"      mutation: {mutation}")
            for label, proc in (("pre", pre), ("post", post)):
                tail = (proc.stdout or proc.stderr).strip().splitlines()[-2:]
                print(f"      {label}: {' / '.join(tail)}")

    floor_ok = len(results) >= a.min_checkers
    all_ok = floor_ok and observed_failures == len(names) and observed_failures >= a.min_checkers

    print(f"{CHECK}: {observed_failures}/{len(names)} checker(s) OBSERVED TO FAIL against a "
          f"CODE-SIDE mutation under passing docs; floor --min-checkers={a.min_checkers} "
          f"{'met' if floor_ok else 'NOT MET'}")
    if a.json:
        print(json.dumps({"check": CHECK, "verdict": "PASS" if all_ok else "FAIL",
                          "observed_failures": observed_failures, "checkers": len(names),
                          "min_checkers": a.min_checkers, "results": results}, indent=1))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
