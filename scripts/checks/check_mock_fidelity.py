#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["click>=8", "pyyaml"]
# ///
"""MOCK FIDELITY — bind every monkeypatched stub against the REAL signature of its target.

plan-063 Issue 5.2. The defect this closes is `dixson3/yoshiko-flow#340`: `_worktree_teardown`
takes `(plan_dir, force)`, four stubs faked it with ONE parameter, and the call site was
written to match THE STUBS. The first real `land --apply` in this repository's history died on
the resulting `TypeError` after two pushes, three public comments and `status: complete`.

**WHY THIS PASS AND NOT ANOTHER.** Four candidate passes were considered against the question
"which would have caught #340 before the first real `--apply`". This is the only one that
would have: a whole-module arity sweep found 1 defect in 252 functions (so dead code was not
the problem), and NO TYPE CHECKER VALIDATES A STUB AGAINST ITS TARGET — `monkeypatch.setattr`
takes `Any`. The common thread in the whole class is that **every instrument was calibrated
against the CALL SITE instead of the CALLEE**.

WHAT IT DOES *NOT* COVER — recorded rather than over-claimed, because "the class is closed" is
the exact overstatement that produced the vacuous checks this repository keeps finding:

- **RETURN SHAPES.** It binds the ARGUMENT axis only. `_worktree_teardown` returns
  `{"status", "path", "branch", "steps"}` and never an `"action"` key, while all four shipped
  stubs returned `{"action": "removed"}` — and plan-063's L18 BRANCHES ON `status`. That
  divergence is load-bearing in the very plan that adds this check, and this check is
  STRUCTURALLY BLIND to it. A return-shape check is a separate, unfiled piece of work.
- **KEYWORD-ONLY-NESS** beyond what `Signature.bind` itself rejects.
- **ASSIGNMENTS TO NON-CALLABLES** (a stubbed constant), which have no signature to bind.

EXIT CONTRACT — three-valued, and an EMPTY result is not a CLEAN result:

    0  every discovered stub binds against its target
    1  at least one stub is INCOMPATIBLE
    2  INCONCLUSIVE — the check could not run: a target file is absent, unparseable, or the
       discovered stub set is EMPTY. A check over an empty set certifies vacuously, which is a
       statement about the instrument rather than about the code.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import inspect
import json
import subprocess
import sys
from pathlib import Path

#: (stub file, module the stub patches) pairs.
#:
#: `land_rehearsal.py` IS IN THIS SET AND THAT IS THE POINT. A checker that swept only
#: `test_land_apply.py` — the file plan-063 already fixed — would be the vacuous-check class
#: over again: `land_rehearsal.py:140` is the stub that made plan-060's rehearsal record
#: `l18_prune: pass` on a code path that could not run, and it is the ONE stub still
#: uncorrected when this check's own capability gate is evaluated.
TARGETS: tuple[tuple[str, str], ...] = (
    ("skills/yf-plan/scripts/test_land_apply.py", "skills/yf-plan/scripts/plan_manager.py"),
    ("skills/yf-plan/scripts/land_rehearsal.py", "skills/yf-plan/scripts/plan_manager.py"),
)

#: A stub whose parameters are exactly this is a PASS-THROUGH and is not bound: `*a, **kw`
#: accepts any call by construction, so binding it proves nothing either way.
_VARIADIC = (ast.arguments,)


def inconclusive(msg: str, extra: dict | None = None, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps({"verdict": "INCONCLUSIVE", "reason": msg,
                          "incompatible": [], "checked": 0, **(extra or {})}, indent=2))
    else:
        print(f"check_mock_fidelity: INCONCLUSIVE — {msg}", file=sys.stderr)
    raise SystemExit(2)


def repo_root() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        return Path(out)
    except Exception:                                          # noqa: BLE001
        return Path.cwd()


def _load_module(path: Path):
    spec = importlib.util.spec_from_file_location(f"_mf_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _lambda_params(node: ast.Lambda) -> tuple[list[str], bool, bool]:
    a = node.args
    names = [p.arg for p in (*a.posonlyargs, *a.args)]
    return names, a.vararg is not None, a.kwarg is not None


def _funcdef_params(node) -> tuple[list[str], bool, bool]:
    a = node.args
    names = [p.arg for p in (*a.posonlyargs, *a.args)]
    return names, a.vararg is not None, a.kwarg is not None


def _defaults_count(node) -> int:
    return len(node.args.defaults)


def discover(src: str) -> list[dict]:
    """Every `monkeypatch.setattr(<mod>, "<name>", <lambda|func|name>)` and `<mod>.<name> = …`.

    Both forms, because #340's origin stub used the SECOND one — a bare attribute assignment
    in `land_rehearsal.py`, which a `monkeypatch`-only scan would have walked straight past.
    """
    tree = ast.parse(src)
    funcs = {n.name: n for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    found: list[dict] = []

    for node in ast.walk(tree):
        target_name = value = None

        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "setattr" and len(node.args) >= 3
                and isinstance(node.args[1], ast.Constant)
                and isinstance(node.args[1].value, str)):
            target_name, value = node.args[1].value, node.args[2]

        elif (isinstance(node, ast.Assign) and len(node.targets) == 1
              and isinstance(node.targets[0], ast.Attribute)):
            target_name, value = node.targets[0].attr, node.value

        if target_name is None or not target_name.startswith("_"):
            continue

        if isinstance(value, ast.Lambda):
            names, va, kw = _lambda_params(value)
            found.append({"target": target_name, "line": node.lineno, "kind": "lambda",
                          "params": names, "vararg": va, "kwarg": kw,
                          "defaults": _defaults_count(value)})
        elif isinstance(value, ast.Name) and value.id in funcs:
            fn = funcs[value.id]
            names, va, kw = _funcdef_params(fn)
            found.append({"target": target_name, "line": node.lineno, "kind": "function",
                          "via": value.id, "params": names, "vararg": va, "kwarg": kw,
                          "defaults": _defaults_count(fn)})
        # Anything else (a constant, a MagicMock, an attribute) has no bindable signature.
    return found


def check_one(stub: dict, real, kwargs_used: set[str] | None = None) -> str | None:
    """Return an incompatibility reason, or `None` when the stub binds."""
    if stub["vararg"] and stub["kwarg"]:
        return None                                   # `*a, **kw` accepts any call
    try:
        sig = inspect.signature(real)
    except (TypeError, ValueError):
        return None
    required = [p for p in sig.parameters.values()
                if p.default is inspect.Parameter.empty
                and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)]
    accepted = len(stub["params"]) + (99 if stub["vararg"] else 0)
    min_accepted = len(stub["params"]) - stub["defaults"]

    if accepted < len(required):
        return (f"the stub accepts {len(stub['params'])} parameter(s) "
                f"{stub['params']} but {stub['target']}{sig} REQUIRES {len(required)}: "
                f"{[p.name for p in required]}")
    if min_accepted > len(sig.parameters) and not stub["vararg"]:
        return (f"the stub requires {min_accepted} parameter(s) but "
                f"{stub['target']}{sig} accepts at most {len(sig.parameters)}")

    # NAMES ARE CHECKED ONLY AGAINST KEYWORDS A REAL CALL SITE ACTUALLY USES.
    #
    # A blanket positional-name equality check was tried first and REJECTED, measured: it
    # flagged 30 stubs whose abbreviated names (`pd`, `p`) are only ever bound POSITIONALLY.
    # A check that reports thirty findings nobody will act on is noise, and a gate keyed on
    # "found at least one" would then be satisfied by the noise rather than by the defect —
    # vacuous in the opposite direction.
    #
    # The narrow form catches the case that is genuinely load-bearing here: plan-063's L18
    # calls `_worktree_teardown(ctx.plan_dir, force=False)` in KEYWORD form, precisely so the
    # next signature change fails loudly. A one-parameter stub cannot absorb that call.
    if not stub["kwarg"]:
        for kw in sorted(kwargs_used or ()):
            if kw not in stub["params"]:
                return (f"a call site passes {kw}= to {stub['target']}{sig}, but the stub's "
                        f"parameters are {stub['params']} — the keyword-form call raises "
                        f"TypeError against this stub")
    return None


def keyword_call_sites(tree: ast.AST) -> dict[str, set[str]]:
    """`{target_name: {keyword names any call site passes}}`.

    Read from the PATCHED MODULE's own source, so the check asks "does a real caller use this
    keyword?" rather than "do the names happen to match". That is the difference between a
    finding and noise — see `check_one`.
    """
    used: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.keywords:
            continue
        fn = node.func
        name = fn.id if isinstance(fn, ast.Name) else (
            fn.attr if isinstance(fn, ast.Attribute) else None)
        if not name:
            continue
        used.setdefault(name, set()).update(
            k.arg for k in node.keywords if k.arg)
    return used


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=None)
    args = ap.parse_args()
    root = Path(args.root) if args.root else repo_root()

    checked, incompatible, skipped = 0, [], []
    for stub_rel, mod_rel in TARGETS:
        stub_path, mod_path = root / stub_rel, root / mod_rel
        # FAIL LOUDLY WHEN A TARGET IS ABSENT. Reporting zero incompatibilities for a file
        # that is not there is the same green as a file that is clean — an empty result and a
        # clean result MUST NOT share an exit code.
        if not stub_path.is_file():
            inconclusive(f"target stub file is absent: {stub_rel}", as_json=args.json)
        if not mod_path.is_file():
            inconclusive(f"patched module is absent: {mod_rel}", as_json=args.json)
        try:
            kw_sites = keyword_call_sites(ast.parse(mod_path.read_text(encoding="utf-8")))
        except SyntaxError as exc:
            inconclusive(f"could not parse {mod_rel}: {exc}", as_json=args.json)
        try:
            mod = _load_module(mod_path)
        except Exception as exc:                               # noqa: BLE001
            inconclusive(f"could not import {mod_rel}: {type(exc).__name__}: {exc}",
                         as_json=args.json)
        try:
            stubs = discover(stub_path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            inconclusive(f"could not parse {stub_rel}: {exc}", as_json=args.json)

        for st in stubs:
            real = getattr(mod, st["target"], None)
            if real is None or not callable(real):
                skipped.append({"file": stub_rel, "line": st["line"],
                                "target": st["target"],
                                "reason": "not a callable attribute of the module"})
                continue
            checked += 1
            why = check_one(st, real, kw_sites.get(st["target"]))
            if why:
                incompatible.append({"file": stub_rel, "line": st["line"],
                                     "target": st["target"], "kind": st["kind"],
                                     "reason": why})

    if checked == 0:
        inconclusive("the discovered stub set is EMPTY — a check over an empty set certifies "
                     "vacuously, which is a statement about the instrument, not the code",
                     as_json=args.json)

    # EXP-002 rec 6. Once the dispatch wrapper (REQ-LAND-030) exists, a future crash becomes
    # an `inconclusive` row carrying an `exception` key. Nothing looks for it unless something
    # does — so this check does, and reports it as an incompatibility of the same class: an
    # instrument that recorded a crash and let it read as green.
    for stub_rel, _ in TARGETS:
        text = (root / stub_rel).read_text(encoding="utf-8")
        for mark in ('"exception":', "'exception':"):
            if mark in text and "inconclusive" in text and "REQ-LAND-030" not in text:
                incompatible.append({
                    "file": stub_rel, "line": 0, "target": "<landing-step-record>",
                    "kind": "crash-record",
                    "reason": "a step record carries an `exception` key without naming "
                              "REQ-LAND-030 — a crash recorded as a non-halting green"})

    verdict = "FAIL" if incompatible else "PASS"
    if args.json:
        print(json.dumps({"verdict": verdict, "checked": checked,
                          "incompatible": incompatible, "skipped": skipped,
                          "targets": [t[0] for t in TARGETS],
                          "not_covered": ["return shapes", "keyword-only-ness",
                                          "assignments to non-callables",
                                          "parameter names with no keyword call site"]}, indent=2))
    elif incompatible:
        for i in incompatible:
            print(f"check_mock_fidelity: FAIL — {i['file']}:{i['line']} {i['reason']}",
                  file=sys.stderr)
    else:
        print(f"check_mock_fidelity: {checked} stub(s) bind against their targets "
              f"({len(skipped)} skipped as non-callable). "
              f"NOT COVERED: return shapes, keyword-only-ness, non-callable assignments.")
    return 1 if incompatible else 0


if __name__ == "__main__":
    raise SystemExit(main())
