#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""check-provably-necessary.py — the yf-plan mechanism freeze, EXECUTED (REQ-PLAN-086, plan-071 D-9).

The one declared exception to the freeze: the check that enforces it. Without it the freeze is
prose (#392). Three assertions, each an exit code:

  VERBS.   For every `@cli.command` registered in `plan_manager.py`:
           (a) >= 1 CALL SITE on a live surface — `SKILL.md`, `agents/*.md`, the
               `LAND_CLOSE_CHAIN` table, the L-step executor functions (`_land_*` source that
               launches `plan_manager.py <verb>`), or `CHANGE-VALIDATION.md`; and
           (b) >= 1 INVOCATION-FORM reference in a `test_*.py` — the verb literal inside a
               `CliRunner.invoke(...)` call, an argv list beside `str(PM)` / `"uv"` /
               `plan_manager.py`, or a `plan_manager.py <verb>` string. A bare mention in an
               enumeration list (`test_cli_enumeration.py`'s set) does NOT count (pass-1 C10).
  REQ-LAND. For every `REQ-LAND-*` id in `spec/landing.md`, every `test_*` token its
           `Verification:` line(s) name exists — as a `def test_*` in a test file, or as a
           `scripts/test_*.py` file.
  CEILINGS. The registered verb count <= `verb_ceiling` and the distinct REQ-LAND id count <=
           `req_land_ceiling`, BOTH READ FROM REQ-PLAN-086 in `skills/yf-plan/SPEC.md` — never
           from a constant beside this code (#392 "derived not transcribed").

EXIT  0 the freeze holds  ·  1 a verb, a REQ-LAND id or a ceiling fails  ·  2 could not run

`--self-test` drives the check against FIVE negative-control fixtures — a dead verb; a verb
whose only test hit is an enumeration list; a REQ-LAND id whose Verification names a missing
test; the verb ceiling exceeded; the REQ-LAND ceiling exceeded — each built by mutating a copy
of the real tree, and asserts every one FAILS while the real tree PASSES. A freeze check that
cannot fail is the vacuous green this plan exists to remove (R7).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SKILL = ROOT / "skills" / "yf-plan"

_VERB_NAMED = re.compile(r'^@cli\.command\("([a-z][a-z0-9-]*)"\)', re.M)
_VERB_BARE = re.compile(r'^@cli\.command\(\)\s*\n(?:@[^\n]*\n)*def ([a-z_][a-z0-9_]*)\(', re.M)
_REQ_LAND = re.compile(r"\bREQ-LAND-\d+[a-z]*\b")
_TEST_TOKEN = re.compile(r"\btest_[A-Za-z0-9_]+\b")
_CEIL_VERB = re.compile(r"`verb_ceiling = (\d+)`")
_CEIL_REQ = re.compile(r"`req_land_ceiling = (\d+)`")
#: Markers that make a nearby verb literal an INVOCATION rather than a mention. Looked for in
#: the 300 characters BEFORE the literal.
_INVOKE_MARKERS = ("invoke(", "str(PM)", "str(_PM)", "plan_manager.py", '"uv"', "'uv'",
                   "subprocess.run(", "_run(", "_pm(", "PM_ARGS", "pm_cmd(")


def inconclusive(msg: str) -> int:
    print(f"check-provably-necessary: INCONCLUSIVE — {msg}", file=sys.stderr)
    return 2


def registered_verbs(pm_text: str) -> set[str]:
    """Every flat `@cli.command` verb, read from the AST — both the named form
    (`@cli.command("x")`) and the bare form (`@cli.command()`, name derived from the def),
    exactly as `test_cli_enumeration.py` reads them. Group subcommands are out of scope."""
    import ast
    verbs: set[str] = set()
    for node in ast.parse(pm_text).body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for d in node.decorator_list:
            if not (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                    and d.func.attr == "command" and isinstance(d.func.value, ast.Name)
                    and d.func.value.id == "cli"):
                continue
            if d.args and isinstance(d.args[0], ast.Constant):
                verbs.add(str(d.args[0].value))
            else:
                verbs.add(node.name.replace("_", "-"))
    return verbs


def live_surfaces(skill: Path, root: Path, pm_text: str) -> dict[str, str]:
    """name -> text, for the leg-(a) surfaces."""
    out = {}
    for p in [skill / "SKILL.md", *sorted((skill / "agents").glob("*.md")), root / "CHANGE-VALIDATION.md"]:
        if p.is_file():
            out[str(p.relative_to(root))] = p.read_text(encoding="utf-8", errors="replace")
    # LAND_CLOSE_CHAIN rows + the L-step executor sources (verbs the executor launches itself).
    m = re.search(r"^LAND_CLOSE_CHAIN[^\n]*\n(.*?)^\)", pm_text, re.M | re.S)
    out["plan_manager.py:LAND_CLOSE_CHAIN"] = m.group(1) if m else ""
    lsteps = re.findall(r"^def (_land_l\d+[a-z0-9_]*)\(.*?(?=^def |\Z)", pm_text, re.M | re.S)
    out["plan_manager.py:_land_l*"] = "\n".join(
        re.search(r"^def %s\(.*?(?=^def |\Z)" % re.escape(n), pm_text, re.M | re.S).group(0)
        for n in lsteps)
    return out


def call_sites(verb: str, surfaces: dict[str, str]) -> list[str]:
    pat = re.compile(r"(?<![a-z0-9-])" + re.escape(verb) + r"(?![a-z0-9-])")
    return [name for name, text in surfaces.items() if pat.search(text)]


_CALL_HELPER = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\(\s*$")
_HELPER_NAME = re.compile(r"(pm|run|invoke|cli|verb|cmd)", re.I)


def _in_argv_list(text: str, pos: int) -> bool:
    """True when `pos` sits inside an unclosed `[` — an argv LIST — and not inside `{`, the
    set an enumeration test writes. Scanned back over at most 400 characters."""
    depth_sq = depth_br = 0
    for ch in reversed(text[max(0, pos - 400):pos]):
        if ch == "]": depth_sq -= 1
        elif ch == "[": depth_sq += 1
        elif ch == "}": depth_br -= 1
        elif ch == "{": depth_br += 1
        if depth_sq > 0:
            return depth_br <= 0
        if depth_br > 0:
            return False
    return False


def invocation_hits(verb: str, tests: dict[str, str]) -> list[str]:
    """Files whose reference to `verb` is an INVOCATION, not a mention (pass-1 C10).

    Three forms count: the literal within 300 chars after an invocation marker (`invoke(`,
    `str(PM)`, `"uv"`, `plan_manager.py`, …); the literal as the first argument of a helper
    whose name says it runs things (`pm_json("verb", …)`, `_run_pm("verb")`, …); or the
    literal inside an argv LIST in a file that invokes `plan_manager.py` at all. A literal in a
    SET — `{"a", "b"}`, the shape an enumeration test uses — never counts.
    """
    hits = []
    lit = re.compile(r"""["']""" + re.escape(verb) + r"""["']""")
    for name, text in tests.items():
        invokes_pm = any(k in text for k in ("invoke(", "str(PM)", "str(_PM)", "plan_manager.py"))
        found = False
        for m in lit.finditer(text):
            window = text[max(0, m.start() - 300):m.start()]
            if any(k in window for k in _INVOKE_MARKERS):
                found = True; break
            call = _CALL_HELPER.search(text[max(0, m.start() - 40):m.start()])
            if call and _HELPER_NAME.search(call.group(1)):
                found = True; break
            if invokes_pm and _in_argv_list(text, m.start()):
                found = True; break
        if not found and re.search(r"plan_manager\.py\s+" + re.escape(verb) + r"\b", text):
            found = True
        if found:
            hits.append(name)
    return hits


def req_land_ids_and_tests(landing_text: str) -> tuple[set[str], dict[str, set[str]]]:
    ids = set(_REQ_LAND.findall(landing_text))
    named: dict[str, set[str]] = {}
    cur = None
    for line in landing_text.splitlines():
        m = re.match(r"^(REQ-LAND-\d+[a-z]*):", line)
        if m:
            cur = m.group(1); named.setdefault(cur, set()); continue
        if cur and line.startswith("Verification:"):
            named[cur] |= set(_TEST_TOKEN.findall(line))
        elif cur and line.startswith("`") and "test_" in line and "check-pytest-ran" in line:
            named[cur] |= set(_TEST_TOKEN.findall(line))
    return ids, named


def run_check(root: Path, skill: Path, *, as_json: bool = False, quiet: bool = False) -> int:
    pm = skill / "scripts" / "plan_manager.py"
    landing = skill / "spec" / "landing.md"
    spec = skill / "SPEC.md"
    for p in (pm, landing, spec):
        if not p.is_file():
            return inconclusive(f"missing {p}")
    pm_text = pm.read_text(encoding="utf-8", errors="replace")
    spec_text = spec.read_text(encoding="utf-8", errors="replace")
    mv, mr = _CEIL_VERB.search(spec_text), _CEIL_REQ.search(spec_text)
    if not (mv and mr):
        return inconclusive("REQ-PLAN-086 in SPEC.md carries no `verb_ceiling = N` / `req_land_ceiling = N` line")
    verb_ceiling, req_ceiling = int(mv.group(1)), int(mr.group(1))

    verbs = registered_verbs(pm_text)
    if len(verbs) < 5:
        return inconclusive(f"parsed only {len(verbs)} verbs — the registration grammar changed")
    surfaces = live_surfaces(skill, root, pm_text)
    tests = {p.name: p.read_text(encoding="utf-8", errors="replace")
             for p in sorted((skill / "scripts").glob("test_*.py"))}
    if not tests:
        return inconclusive("no test_*.py under the skill's scripts/")

    findings: list[dict] = []
    rows = []
    for v in sorted(verbs):
        sites = call_sites(v, surfaces)
        hits = invocation_hits(v, tests)
        rows.append({"verb": v, "call_sites": sites, "test_invocations": hits})
        if not sites:
            findings.append({"kind": "verb-no-caller", "verb": v,
                             "detail": f"`{v}` is registered but no live surface invokes it (D-1 leg a)"})
        if not hits:
            findings.append({"kind": "verb-no-test", "verb": v,
                             "detail": f"`{v}` has no invocation-form test reference (D-1 leg b)"})
    if len(verbs) > verb_ceiling:
        findings.append({"kind": "verb-ceiling", "detail": f"{len(verbs)} verbs registered, ceiling {verb_ceiling} (REQ-PLAN-086)"})

    ids, named = req_land_ids_and_tests(landing.read_text(encoding="utf-8", errors="replace"))
    if not ids:
        return inconclusive("spec/landing.md carries no REQ-LAND id")
    all_defs = set()
    for text in tests.values():
        all_defs |= set(re.findall(r"^def (test_[A-Za-z0-9_]+)\(", text, re.M))
    files = {p.stem for p in (skill / "scripts").glob("test_*.py")}
    for rid, toks in sorted(named.items()):
        if not toks:
            findings.append({"kind": "req-no-test", "id": rid, "detail": f"{rid} names no test in its Verification"})
        for tk in sorted(toks):
            if tk not in all_defs and tk not in files:
                findings.append({"kind": "req-test-missing", "id": rid,
                                 "detail": f"{rid}'s Verification names `{tk}`, which exists as neither a `def` nor a test file"})
    if len(ids) > req_ceiling:
        findings.append({"kind": "req-land-ceiling", "detail": f"{len(ids)} REQ-LAND ids, ceiling {req_ceiling} (REQ-PLAN-086)"})

    out = {"check": "check-provably-necessary", "verbs": len(verbs), "verb_ceiling": verb_ceiling,
           "req_land_ids": len(ids), "req_land_ceiling": req_ceiling, "findings": findings,
           "verdict": "FAIL" if findings else "PASS", "rows": rows}
    if not quiet:
        if as_json:
            print(json.dumps(out, indent=1))
        else:
            print(f"check-provably-necessary: {out['verdict']} — {len(verbs)}/{verb_ceiling} verbs, "
                  f"{len(ids)}/{req_ceiling} REQ-LAND ids, {len(findings)} finding(s)")
            for f in findings:
                print(f"  - [{f['kind']}] {f['detail']}")
    return 1 if findings else 0


def _stage(tmp: Path) -> tuple[Path, Path]:
    """A copy of the parts of the tree the check reads, so a fixture mutates a COPY."""
    root = tmp / "repo"; skill = root / "skills" / "yf-plan"
    (skill / "scripts").mkdir(parents=True); (skill / "spec").mkdir(); (skill / "agents").mkdir()
    for rel in ("SKILL.md", "SPEC.md", "spec/landing.md"):
        shutil.copy(SKILL / rel, skill / rel)
    for p in (SKILL / "agents").glob("*.md"):
        shutil.copy(p, skill / "agents" / p.name)
    for p in (SKILL / "scripts").glob("test_*.py"):
        shutil.copy(p, skill / "scripts" / p.name)
    shutil.copy(SKILL / "scripts" / "plan_manager.py", skill / "scripts" / "plan_manager.py")
    shutil.copy(ROOT / "CHANGE-VALIDATION.md", root / "CHANGE-VALIDATION.md")
    return root, skill


def self_test() -> int:
    results = []
    with tempfile.TemporaryDirectory() as td:
        root, skill = _stage(Path(td))
        results.append(("control: the real tree PASSES", run_check(root, skill, quiet=True) == 0))
        pm = skill / "scripts" / "plan_manager.py"; base_pm = pm.read_text()
        spec = skill / "SPEC.md"; base_spec = spec.read_text()
        landing = skill / "spec" / "landing.md"; base_land = landing.read_text()
        # 1. a dead verb — registered, invoked nowhere, tested nowhere
        pm.write_text(base_pm + '\n\n@cli.command("zz-dead-verb")\ndef zz_dead_verb():\n    pass\n')
        results.append(("negative 1: a dead verb FAILS", run_check(root, skill, quiet=True) == 1))
        # 2. a verb whose ONLY test hit is an enumeration list (and which has a caller)
        pm.write_text(base_pm + '\n\n@cli.command("zz-listed-verb")\ndef zz_listed_verb():\n    pass\n')
        (skill / "SKILL.md").write_text((skill / "SKILL.md").read_text() + "\nuv run ${SKILL_DIR}/scripts/plan_manager.py zz-listed-verb\n")
        (skill / "scripts" / "test_zz_enum.py").write_text('KNOWN = {"audit", "zz-listed-verb", "init"}\n')
        rc = run_check(root, skill, quiet=True)
        results.append(("negative 2: a verb whose only test hit is an enumeration list FAILS", rc == 1))
        (skill / "scripts" / "test_zz_enum.py").unlink(); pm.write_text(base_pm)
        shutil.copy(SKILL / "SKILL.md", skill / "SKILL.md")
        # 3. a REQ-LAND id whose Verification names a missing test
        landing.write_text(base_land.replace("test_narrowing_only", "test_zz_missing_control", 1))
        results.append(("negative 3: a REQ-LAND Verification naming a missing test FAILS", run_check(root, skill, quiet=True) == 1))
        landing.write_text(base_land)
        # 4. verb ceiling exceeded
        spec.write_text(re.sub(r"`verb_ceiling = \d+`", "`verb_ceiling = 1`", base_spec))
        results.append(("negative 4: the verb ceiling exceeded FAILS", run_check(root, skill, quiet=True) == 1))
        spec.write_text(base_spec)
        # 5. REQ-LAND ceiling exceeded
        spec.write_text(re.sub(r"`req_land_ceiling = \d+`", "`req_land_ceiling = 1`", base_spec))
        results.append(("negative 5: the REQ-LAND ceiling exceeded FAILS", run_check(root, skill, quiet=True) == 1))
        spec.write_text(base_spec)
        results.append(("control: the restored tree PASSES again", run_check(root, skill, quiet=True) == 0))
    ok = all(r for _, r in results)
    for name, r in results:
        print(f"{'ok  ' if r else 'FAIL'} {name}")
    print(f"check-provably-necessary --self-test: {'all controls behaved' if ok else 'a control did NOT behave'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    return run_check(ROOT, SKILL, as_json=a.json)


if __name__ == "__main__":
    raise SystemExit(main())
