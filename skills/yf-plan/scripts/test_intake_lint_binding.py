#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pyyaml>=6",
# ]
# ///
"""The intake linter binding (plan-049 Issue 4.2, REQ-DATA-057).

Run from anywhere:  uv run skills/yf-plan/scripts/test_intake_lint_binding.py

WHAT THIS PINS, AND WHY IT IS NOT OBVIOUS FROM THE CODE
-------------------------------------------------------
plan-047's Epic 9 named two enforcement points; neither was ever wired. A non-conformant NEW
plan was caught only by the FAST tier — never at intake — so the fail-closed gate that would
have blocked plan-047 at its own intake **did not exist**. `_audit_plan` is that gate, and
these tests assert three things about it that a reading of the code will not tell you:

1. **It actually fails.** SC16's injected malformed heading drives `ready-check` to exit **3**.
   Before this binding the identical bundle exited **0** — the test drives BOTH arms so the
   claim is a measurement, not a recollection.
2. **`Inconclusive` maps to `warn`, never `fail`.** INCONCLUSIVE means the *linter* could not
   run. Mapping it to `fail` turns the linter's own breakage into an intake outage; mapping it
   to `pass` hides a linter that quietly stopped working.
3. **`files_checked: 0` is reported, not accepted.** Zero selected files is `verdict: PASS`,
   exit 0 — indistinguishable from clean. It has to be surfaced, or the whole binding can be
   satisfied by an engine that checks nothing.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PM = HERE / "plan_manager.py"
REPO = HERE.parent.parent.parent

_spec = importlib.util.spec_from_file_location("pm_mod", PM)
pm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pm)

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def _live_bundle() -> Path:
    hits = sorted((REPO / "docs" / "plans").glob("plan-049-*"))
    return hits[0] if hits else Path()


def _stage(td: Path, *, status: str = "review") -> Path:
    """A copy of the live plan-049 bundle, forced to `status`."""
    src = _live_bundle()
    dst = td / src.name
    shutil.copytree(src, dst)
    pmd = dst / "plan.md"
    text = pmd.read_text(encoding="utf-8")
    import re
    text = re.sub(r"(?m)^status: .*$", f"status: {status}", text, count=1)
    text = re.sub(r"(?m)^\*\*Status:\*\* .*$", f"**Status:** {status}", text, count=1)
    pmd.write_text(text, encoding="utf-8")
    return dst


def ready_check(bundle: Path) -> tuple[int, dict]:
    p = subprocess.run(["uv", "run", str(PM), "ready-check", str(bundle), "--json"],
                       capture_output=True, text=True, cwd=REPO)
    try:
        return p.returncode, json.loads(p.stdout)
    except json.JSONDecodeError:
        return p.returncode, {"raw": p.stdout + p.stderr}


check("the live plan-049 bundle is present to drive against", _live_bundle().is_dir(),
      str(_live_bundle()))

with tempfile.TemporaryDirectory() as _td:
    TD = Path(_td)

    # --- the CONTROL arm. Without it, "the mutant fails" proves nothing: a binding that
    # --- failed on everything would satisfy the mutant arm perfectly.
    clean = _stage(TD / "clean", status="review")
    (TD / "clean").mkdir(exist_ok=True)
    rc_clean, res_clean = ready_check(clean)
    check("CONTROL: an unmutated bundle at `review` still passes ready-check", rc_clean == 0,
          f"rc={rc_clean} reasons={res_clean.get('reasons')}")

    # --- SC16: the mutant.
    bad = _stage(TD / "bad", status="review")
    bad_md = bad / "plan.md"
    bad_md.write_text(bad_md.read_text(encoding="utf-8")
                      .replace("\n## Approach\n", "\n## Aproach\n", 1), encoding="utf-8")
    check("SC16: the injection really landed (a required section is now misspelt)",
          "\n## Approach\n" not in bad_md.read_text(encoding="utf-8"))
    rc_bad, res_bad = ready_check(bad)
    check("SC16: an in-flight bundle with an injected malformed heading drives ready-check "
          "to exit 3 — it exited 0 before this binding", rc_bad == 3,
          f"rc={rc_bad} reasons={res_bad.get('reasons')}")
    check("SC16: and the reason names the portability audit, so the operator is pointed "
          "somewhere real", any("audit" in r for r in res_bad.get("reasons", [])),
          str(res_bad.get("reasons")))

    audit = pm._audit_plan(bad)
    check("SC16: the audit attributes it to the linter, not to a generic failure",
          any(f["item"].startswith("doc-lint/") and f["status"] == "fail"
              for f in audit["findings"]),
          str([f["item"] for f in audit["findings"]]))
    check("SC16: the finding carries the linter's own `E` severity in its detail",
          any("[E]" in f["detail"] for f in audit["findings"]
              if f["item"].startswith("doc-lint/")),
          str([f["detail"][:60] for f in audit["findings"]
               if f["item"].startswith("doc-lint/")]))

    # --- the severity mapping, both directions.
    live_audit = pm._audit_plan(_live_bundle())
    check("the LIVE bundle passes the bound audit (the binding is not a blanket refusal)",
          live_audit["status"] == "pass",
          str([f for f in live_audit["findings"] if f["status"] == "fail"]))

    # --- The forced-`plan` call is what makes `plan.md` checkable ANYWHERE.
    #
    # Path routing selects by glob, so a bundle staged outside the plans root selects nothing
    # and reports `files_checked: 0` — which is `verdict: PASS`, exit 0, indistinguishable
    # from clean. The staged bundles above live in a tempdir, so every assertion in this file
    # depends on the forced call actually working. Asserted directly rather than relied upon.
    stray = TD / "stray-bundle"
    stray.mkdir()
    (stray / "plan.md").write_text("# not a plan\n", encoding="utf-8")
    got = pm._lint_findings_for_audit(stray)
    check("a plan.md OUTSIDE the plans root is still linted — the forced-type call, without "
          "which `files_checked: 0` would read as a clean pass",
          any(f["item"].startswith("doc-lint/") and f["status"] == "fail" for f in got),
          str([(f["item"], f["status"]) for f in got][:4]))
    check("...and the severity mapping holds on it: linter `E` -> `fail`, `W` -> `warn`",
          {f["status"] for f in got} <= {"fail", "warn"}
          and any(f["status"] == "fail" and "[E]" in f["detail"] for f in got)
          and any(f["status"] == "warn" and "[W]" in f["detail"] for f in got),
          str([(f["item"], f["status"], f["detail"][:24]) for f in got]))

    # --- INCONCLUSIVE -> `warn`, NEVER `fail`.
    #
    # Driven by making the engine unfindable, which is the real-world shape: a yf-plan
    # installed without the vendored linter, or a vault where the deploy half-completed.
    # Mapping this to `fail` would turn the linter's own breakage into an intake OUTAGE.
    _orig_file = pm.__file__
    import types as _types
    _saved = pm._lint_findings_for_audit.__globals__["__file__"]
    try:
        pm._lint_findings_for_audit.__globals__["__file__"] = str(TD / "nowhere" / "x.py")
        degraded = pm._lint_findings_for_audit(_live_bundle())
    finally:
        pm._lint_findings_for_audit.__globals__["__file__"] = _saved
    check("an ABSENT engine yields `warn`, never `fail` — the linter's own breakage must "
          "not become an intake outage",
          degraded and all(f["status"] == "warn" for f in degraded), str(degraded))
    check("...and it says UNCHECKED in words, so a silent degradation is not mistaken for a "
          "clean pass", any("UNCHECKED" in f["detail"] for f in degraded), str(degraded))
    check("an absent engine does NOT flip the audit verdict to fail",
          all(f["status"] != "fail" for f in degraded), str(degraded))

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
