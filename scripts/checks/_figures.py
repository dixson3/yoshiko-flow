#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""_figures.py <figure-id> — the AUTHORITATIVE re-measurement for one cited figure.

Companion to `check-cited-figures.py` (plan-060 Issue 0.10, `dixson3/yoshiko-flow#289`).

WHY THE MEASUREMENTS LIVE HERE AND NOT IN THE REGISTRY.
A registry row whose `command` is an ad-hoc shell pipeline is a registry that can answer a
DIFFERENT QUESTION from the one the figure was about, silently. Measured during Issue 0.10:

  * `test_close_contract.py --list-steps | grep -c .`  returned **16** — it counted JSON
    lines, not steps. The true figure is **12**.
  * a naive `grep -c '@cli\\.command('`                returned **40** — it does not
    distinguish the bare from the named registration form the way the spec's own check does.
    The true source figure is **39**.

Both pipelines were plausible, ran clean, and exited 0. Naming each measurement here — one
function, one figure, using the same parse the authoritative instrument uses — is what makes a
re-measurement comparable to the original rather than merely numeric.

EXIT CONTRACT (three-valued, per `scripts/checks/_common.sh` / REQ-CLI-029):
    0  the figure was measured; the value is on stdout, ALONE
    1  unused here — a *drift* is the caller's verdict, never this script's
    2  INCONCLUSIVE — this figure could not be measured at all (missing tool, missing file)

An INCONCLUSIVE prints its reason to STDERR and NOTHING to stdout, so a caller that reads
stdout can never mistake silence for a zero. That matters most for the ABSENCE figures
(`herdr-schema-*`): a `0` produced because `herdr` is not installed would be the worst
possible false green, since the requirement those figures underwrite is itself a claim of
absence.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, check=True).stdout.strip()
        return Path(out)
    except Exception:
        return Path.cwd()


ROOT = repo_root()
PLAN_MANAGER = ROOT / "skills" / "yf-plan" / "scripts" / "plan_manager.py"
CLI_SPEC = ROOT / "skills" / "yf-plan" / "spec" / "cli.md"
CLOSE_CONTRACT = ROOT / "skills" / "yf-plan" / "scripts" / "test_close_contract.py"

REQ_ROOTS = ["skills", "SPEC.md", "yf/src", "scripts", "_shared"]


def inconclusive(msg: str) -> "int":
    print(f"_figures: INCONCLUSIVE — {msg}", file=sys.stderr)
    return 2


#: The pre-plan-060 baseline commit. plan-060's Gate-G1 claim — "all 20 EXISTING call sites
#: of `_run_git` are read-only or worktree/branch operations" — is a statement about the
#: repository AS IT STOOD WHEN THE GATE WAS WRITTEN, so the figure must be pinned to that
#: tree. Measured live: unpinned, the same count reads 29 on the execute branch, because
#: plan-060's own Epic 1 added nine more (all reads: merge-tree, rev-parse, ls-tree, diff,
#: rev-list, ls-files). Reporting 29 against a quoted 20 is a TRUE drift of a FALSE figure —
#: the claim never was "the repository has exactly 20 forever".
RUN_GIT_BASELINE_REV = "777c5be5298564c0c027a7570b70b3e668ffe0b7"


def f_run_git_call_sites() -> int | str:
    """Call sites of `_run_git` AT THE PINNED PRE-PLAN BASELINE.

    The DEFINITION is excluded: `def _run_git(` is not a call site, and counting it would
    inflate the figure by exactly one — the drift red-team pass 1 found.

    PINNED, NOT LIVE, and the pin is the whole correction. A live count of a helper that any
    later plan may legitimately call more of is a figure that goes stale on every commit and
    therefore teaches its reader to ignore it. The claim this figure underwrites is
    historical, so the measurement is historical too.
    """
    proc = subprocess.run(
        ["git", "show", f"{RUN_GIT_BASELINE_REV}:skills/yf-plan/scripts/plan_manager.py"],
        capture_output=True, text=True, cwd=ROOT)
    if proc.returncode != 0 or not proc.stdout:
        return inconclusive(
            f"the baseline commit {RUN_GIT_BASELINE_REV[:10]} is not reachable in this "
            f"clone — a shallow clone cannot measure a historical figure, and an "
            f"unreachable baseline is INCONCLUSIVE, never a drift")
    return len(re.findall(r"(?<!def )\b_run_git\(", proc.stdout))


def f_close_chain_steps() -> int | str:
    """Steps in SKILL.md's documented §6.4 close chain.

    Parsed from `--list-steps`' JSON, NOT counted as lines. The line count is 16 for a
    12-element array, which is the measured trap this function exists to avoid.
    """
    if not CLOSE_CONTRACT.is_file():
        return inconclusive(f"no test_close_contract.py at {CLOSE_CONTRACT}")
    proc = subprocess.run(["uv", "run", str(CLOSE_CONTRACT), "--list-steps"],
                          capture_output=True, text=True, cwd=ROOT)
    if proc.returncode != 0:
        return inconclusive(f"--list-steps exited {proc.returncode}")
    try:
        return len(json.loads(proc.stdout)["steps"])
    except Exception as exc:
        return inconclusive(f"--list-steps output is not the expected JSON: {exc}")


def f_cli_verbs() -> int | str:
    """Verbs enumerated in REQ-CLI-006's own paragraph — the SPEC side of the set equality.

    Scoped to the REQ block exactly as `test_cli_enumeration.py` scopes it, so backticked
    names elsewhere in cli.md cannot inflate the count.
    """
    if not CLI_SPEC.is_file():
        return inconclusive(f"no cli.md at {CLI_SPEC}")
    text = CLI_SPEC.read_text(encoding="utf-8")
    try:
        start = text.index("REQ-CLI-006:")
        end = text.index("Rationale:", start)
    except ValueError:
        return inconclusive("REQ-CLI-006 block not found in cli.md")
    line = next((ln for ln in text[start:end].splitlines()
                 if ln.startswith("The enumeration")), None)
    if line is None:
        return inconclusive("REQ-CLI-006 carries no `The enumeration` line")
    return len(set(re.findall(r"`([a-z0-9-]+)`", line.split(":", 1)[1])))


def f_req_families() -> int | str:
    """Distinct `REQ-<FAMILY>-` prefixes across the declared roots.

    Scanned in PYTHON, never `grep`: `grep` in this repository resolves to a ugrep shell
    function that honours `.gitignore`, in the interactive shell AND under the agent harness.
    """
    fams: set[str] = set()
    seen_any = False
    for root in REQ_ROOTS:
        p = ROOT / root
        if not p.exists():
            continue
        paths = [p] if p.is_file() else [q for q in p.rglob("*") if q.is_file()]
        for q in paths:
            seen_any = True
            try:
                data = q.read_bytes()
            except OSError:
                continue
            fams |= {m.group(1).decode() for m in re.finditer(rb"REQ-([A-Z]+)-\d+", data)}
    if not seen_any:
        return inconclusive("none of the declared roots exist")
    return len(fams)


def _herdr_schema() -> str | None:
    proc = subprocess.run(["herdr", "api", "schema", "--json"],
                          capture_output=True, text=True)
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    return proc.stdout


def f_herdr_schema_human() -> int | str:
    s = _herdr_schema()
    if s is None:
        return inconclusive("herdr is not available or returned nothing — an ABSENCE figure "
                            "must never be reported as a confirmed zero")
    return s.count("human")


def f_herdr_schema_attached() -> int | str:
    s = _herdr_schema()
    if s is None:
        return inconclusive("herdr is not available or returned nothing — an ABSENCE figure "
                            "must never be reported as a confirmed zero")
    return s.count("attached")


FIGURES = {
    "run-git-call-sites": f_run_git_call_sites,
    "close-chain-steps": f_close_chain_steps,
    "cli-verbs": f_cli_verbs,
    "req-families": f_req_families,
    "herdr-schema-human": f_herdr_schema_human,
    "herdr-schema-attached": f_herdr_schema_attached,
}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
        print(f"usage: _figures.py <{'|'.join(FIGURES)}>", file=sys.stderr)
        return 2
    fn = FIGURES.get(argv[1])
    if fn is None:
        print(f"_figures: INCONCLUSIVE — unknown figure id {argv[1]!r}", file=sys.stderr)
        return 2
    val = fn()
    if val == 2:
        return 2
    print(val)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
