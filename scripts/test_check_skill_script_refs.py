#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tests for `scripts/check_skill_script_refs.py` — REQ-YF-EMBED-005 / #210.

SEEDED FROM THE TWO SANDBOX FIXTURES (plan-053 Issue 3.6). EXP-003 noted the prototype had no
unit tests at all; these are them, and they are the two fixtures the investigation actually
measured against, not fresh inventions:

  FP-CLEAN       five prose `_shared/` mentions (including plan-050's own note verbatim — the
                 note EXPLAINING this defect, which a naive grep flags), a non-shell `python`
                 fence containing an invocation-shaped comment, and an allow-marked
                 deliberate external.  -> exit 0
  PLAN-050 MUTANT the same tree plus plan-050 Issue 7.3's original bug, verbatim.  -> exit 1

THE MUTANT IS THE WHOLE ARGUMENT FOR D-3. Volume is the wrong justification — the `_shared/`
class is EXACTLY ONE live break. The right one is that re-inserting the FIRST instance makes
this check go red, which is what "put a check in front of the failing component" means.

The fixture trees live in the plan bundle
(`docs/plans/plan-053-james-dixson-4015d3/assets/fixtures/corpus/`). When they are absent —
this test outlives the bundle's working life — the fixture-backed arms SKIP with a stated
reason and the SYNTHETIC arms below still run. A skip is never counted as a pass.

Run:  uv run scripts/test_check_skill_script_refs.py
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
CHECK = HERE / "check_skill_script_refs.py"
CORPUS = (REPO / "docs" / "plans" / "plan-053-james-dixson-4015d3"
          / "assets" / "fixtures" / "corpus")

_spec = importlib.util.spec_from_file_location("cssr", CHECK)
cssr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cssr)

failures: list[str] = []
skipped: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def skip(name: str, why: str) -> None:
    print(f"SKIP {name} — {why}")
    skipped.append(name)


def run(root: Path, *extra: str) -> tuple[int, dict]:
    r = subprocess.run([sys.executable, str(CHECK), "--root", str(root), "--json", *extra],
                       capture_output=True, text=True)
    try:
        return r.returncode, json.loads(r.stdout)
    except json.JSONDecodeError:
        return r.returncode, {}


# --- 1. THE TWO SANDBOX FIXTURES ----------------------------------------------------------
if not (CORPUS / "fp-clean").is_dir() or not (CORPUS / "plan050-mutant").is_dir():
    skip("the two sandbox fixture trees",
         f"absent from {CORPUS} — this test outlives the plan bundle's working life. "
         "The synthetic arms below still cover the contract.")
else:
    rc, d = run(CORPUS / "fp-clean")
    check("FP-CLEAN: the false-positive tree returns exit 0", rc == 0, f"got {rc}: {d}")
    check("FP-CLEAN: ...over at least one REAL invocation, so the green is earned",
          d.get("checked", 0) >= 1, str(d))
    check("FP-CLEAN: ...and the allow-marked external is not counted a violation",
          d.get("violations", 1) == 0, str(d.get("by_class")))

    rc, d = run(CORPUS / "plan050-mutant")
    check("MUTANT: plan-050's original bug, re-inserted verbatim, returns exit 1",
          rc == 1, f"got {rc}")
    recs = d.get("records", [])
    check("MUTANT: ...naming `_shared/plan_extract.py`",
          any("_shared/plan_extract.py" == r["path"] for r in recs), str(recs))
    check("MUTANT: ...classified `repo-only`, NOT `missing-in-repo`",
          any(r["class"] == "repo-only" for r in recs), str(recs))


# --- 2. SYNTHETIC ARMS — the contract, independent of the bundle ---------------------------
def tree(td: Path, skill_md: str, *, with_script: bool = True) -> Path:
    d = td / "skills" / "yf-demo"
    (d / "scripts").mkdir(parents=True, exist_ok=True)
    if with_script:
        (d / "scripts" / "demo.py").write_text("print('demo')\n")
    (d / "SKILL.md").write_text(
        "---\nname: yf-demo\ndescription: fixture\n---\n# yf-demo\n\n" + skill_md)
    return td


with tempfile.TemporaryDirectory() as _td:
    td = Path(_td)

    # THE TWO FAILURE SHAPES ARE DISTINCT AND BOTH ARE IN SCOPE.
    # Collapsing them would certify a rooted-but-unvendored path — exactly what #210's
    # one-edit fix would have produced for `pour_fidelity.py`.
    rc, d = run(tree(td / "a", "```bash\nuv run _shared/thing.py\n```\n"))
    check("repo-only: a `_shared/` path is flagged", rc == 1)
    check("repo-only: ...and classified `repo-only`",
          any(r["class"] == "repo-only" for r in d.get("records", [])), str(d.get("records")))

    rc, d = run(tree(td / "b", "```bash\nuv run ${SKILL_DIR}/scripts/gone.py\n```\n"))
    check("missing-in-repo: a CORRECTLY ROOTED path naming a never-vendored script is flagged",
          rc == 1, "this is the shape #210's one-edit fix would have produced")
    check("missing-in-repo: ...and is NOT conflated with `repo-only`",
          any(r["class"] == "missing-in-repo" for r in d.get("records", [])),
          str(d.get("records")))

    rc, _ = run(tree(td / "c", "```bash\nuv run ${SKILL_DIR}/scripts/demo.py\n```\n"))
    check("ok: a rooted path that resolves is clean", rc == 0)

    # THE CARVES. Each was required to get the measured false-positive surface to zero.
    rc, d = run(tree(td / "d", "The `_shared/sync.py` module keeps the copies identical.\n"))
    check("carve: PROSE mentioning a `_shared/` path is not an invocation", rc == 0,
          "43 `_shared/` mentions across skills/*.md, exactly ONE of them an invocation")

    rc, _ = run(tree(td / "e", "```python\n# uv run _shared/thing.py\n```\n"))
    check("carve: a NON-SHELL fence is a code listing, not a command listing", rc == 0)

    rc, d = run(tree(td / "f", "```bash\nuv run script.py\n```\n"))
    check("carve: a path with no directory component is `illustrative`", rc == 0,
          str(d.get("by_class")))

    rc, _ = run(tree(td / "g",
                     "<!-- skill-script-refs: allow deliberately external -->\n"
                     "`uv run .agents/skills/other/scripts/x.py`\n"))
    check("carve: the allow marker opts out a DELIBERATE external reference", rc == 0)

    # The marker must be NARROW — it opts out what it names, not the whole file.
    rc, _ = run(tree(td / "h",
                     "<!-- skill-script-refs: allow deliberately external -->\n"
                     "`uv run .agents/skills/other/scripts/x.py`\n\n"
                     "```bash\nuv run _shared/thing.py\n```\n"))
    check("the allow marker does NOT blanket the rest of the file", rc == 1,
          "an exemption that silently widens is indistinguishable from an oversight")

    # `<yf-NAME>/` is a RECOGNISED root per EXP-003's stated predicate.
    (td / "i" / "skills" / "yf-other" / "scripts").mkdir(parents=True)
    (td / "i" / "skills" / "yf-other" / "scripts" / "z.py").write_text("x\n")
    rc, _ = run(tree(td / "i", "```bash\nuv run <yf-other>/scripts/z.py\n```\n"))
    check("root: the `<yf-NAME>/` placeholder form resolves", rc == 0)

    # #210'S OWN LIVE SHAPE: `VAR=$(uv run ...)`. The first draft of the checker tokenised
    # the runner as `FIDELITY=$(uv` and never saw it — a checker that misses the defect it
    # was built for. Caught by RUNNING it against the tree, not by reading it.
    rc, d = run(tree(td / "j", "```bash\nFIDELITY=$(uv run _shared/pour_fidelity.py x --json)\n```\n"))
    check("command substitution: `VAR=$(uv run ...)` is seen", rc == 1,
          "#210's own live instance was written in exactly this form")

    # SCOPE: fixture corpora carry arbitrary invocations BY DESIGN.
    fx = td / "k" / "skills" / "yf-demo" / "scripts" / "fixtures"
    tree(td / "k", "# nothing\n")
    fx.mkdir(parents=True, exist_ok=True)
    (fx.parent.parent / "README.md").write_text("# yf-demo\n\n```bash\nuv run _shared/x.py\n```\n")
    rc, _ = run(td / "k")
    check("scope: `README.md` IS in scope — the same break lives there", rc == 1,
          "excluding it would repeat the prototype-convenience scoping error EXP-003 made")

    # The exit contract's third value.
    rc, d = run(td / "nonexistent-root")
    check("exit contract: a missing `skills/` tree is INCONCLUSIVE (2), never a FAIL", rc == 2,
          f"got {rc}")
    check("exit contract: ...and says so in the JSON",
          d.get("verdict") == "INCONCLUSIVE", str(d))


if skipped:
    print(f"\n{len(skipped)} skipped (stated, never counted as a pass): {skipped}")
print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
