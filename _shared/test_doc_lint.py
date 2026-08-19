#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tier-1 tests for `_shared/doc_lint.py` (plan-047 Issue 1.3, REQ-DATA-024).

**The headline assertion is the EXIT CODE, not the printed findings.** EXP-005 reproduced a
linter printing `errors=4` while the delegating engine reported `status: pass`, because the
linter exited 0. Without this test the CHANGE-VALIDATION row added in Epic 3 is decorative:
the command runs, prints, and passes.

Run:  uv run _shared/test_doc_lint.py
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

SHARED = Path(__file__).resolve().parent
REPO = SHARED.parent
LINT = SHARED / "doc_lint.py"
FIXTURES = REPO / "tests" / "fixtures" / "doclint"

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def run(*args: str) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(LINT), *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


import importlib.util as _ilu
_dl_spec = _ilu.spec_from_file_location("doc_lint_mod", LINT)
doc_lint_mod = _ilu.module_from_spec(_dl_spec)
_dl_spec.loader.exec_module(doc_lint_mod)


# --- 1. the exit contract: 1 on an error finding, 0 on a clean file ------------------

rc, out = run("--type", "plan", "--path", str(FIXTURES / "plan" / "bad.md"))
check("known-bad plan fixture exits 1", rc == 1, f"got {rc}")
check("known-bad plan fixture reports FAIL", "FAIL:" in out)

rc, out = run("--type", "finding", "--path", str(FIXTURES / "finding" / "bad.md"))
check("known-bad finding fixture exits 1", rc == 1, f"got {rc}")

# plan-048 Issue 2.9. `sections()` returns ONLY `##`/`###` headings and NEVER an `H1`.
# A schema that checks an H1 title via `headings-any-level` therefore reports it missing on
# EVERY file, forever — a check that can only ever fail, which is the mirror image of R4's
# "a check that cannot fail". `plan-retrospective.toml` shipped that defect and SC6 caught
# it; pinning it here means the next schema author meets it as a test, not a mystery.
_h1_only = "# Title Only\n\nbody text\n"
check("sections() does not see an H1 (use regex-present for a title check)",
      doc_lint_mod.sections(_h1_only, any_level=True) == [],
      str(doc_lint_mod.sections(_h1_only, any_level=True)))
check("...and it DOES see an H2",
      doc_lint_mod.sections("## Real Section\n\nbody\n", any_level=True) == ["Real Section"])

# plan-048 Issue 2.6. Schemas load EAGERLY, so ONE malformed schema makes EVERY type
# report INCONCLUSIVE, not just its own. Measured during 2.6: a `code-generated` type
# missing `derive_from` took all seven instantiated types to `files_checked: 0`. The
# failure is fail-SAFE (INCONCLUSIVE, never a false PASS) but its blast radius is the
# whole type set, so every shipped schema must be loadable.
rc, out = run("--json")
check("every shipped schema loads (one malformed schema poisons ALL types)",
      "must set `derive_from`" not in out and "no schema for type" not in out,
      out[:300])

# plan-048 Issue 2.1b / SC25. The third SHIPPED type had no known-bad fixture at all, so
# its one check (`vendored-marker`) had never been shown to fail. A check that has never
# been driven red is indistinguishable from a check that cannot go red.
rc, out = run("--type", "reference", "--path", str(FIXTURES / "reference" / "bad.md"))
check("known-bad reference fixture exits 1", rc == 1, f"got {rc}")
check("...and it names the vendored-marker check", "vendored-marker" in out, out[:200])

with tempfile.TemporaryDirectory() as td:
    clean = Path(td) / "plan.md"
    sys.path.insert(0, str(SHARED))
    import plan_template  # noqa: E402

    clean.write_text(
        "---\ntype: Plan\nokf_spec: OKF-PLAN\nid: plan-999-t-000000\nauthor: t\n"
        "created: 2026-01-01\nstatus: scoping\n---\n"
        + plan_template.seed_body("Clean fixture", "plan-999-t-000000", "t", "2026-01-01")
        + "\n## Investigation Findings\n_none_\n"
    )
    rc, out = run("--type", "plan", "--path", str(clean))
    check("a freshly seeded plan.md exits 0", rc == 0, f"got {rc}: {out.strip()[:300]}")
    check("...and reports PASS", "PASS:" in out, out.strip()[:200])

# --- 2. an error-severity finding, and ONLY it, sets the exit code -------------------

rc, out = run("--type", "plan", "--path", str(FIXTURES / "plan" / "bad.md"))
check("warnings are reported alongside errors", " warning(s)" in out)

# --- 3. INCONCLUSIVE is exit 2, and only means "could not run" -----------------------

rc, out = run("--type", "no-such-type")
check("an unknown type is INCONCLUSIVE (exit 2), not FAIL", rc == 2, f"got {rc}")
check("...and says INCONCLUSIVE", "INCONCLUSIVE" in out)

# --- 4. --path is an explicit override, not a filter ---------------------------------
# The fixture lives OUTSIDE docs/plans/**, so a filter-over-glob implementation would
# select nothing and exit 0 — a vacuous pass. This is the regression guard for that.

rc, out = run("--type", "plan", "--path", str(FIXTURES / "plan" / "bad.md"), "--json")
check("--path reaches a file outside the type's globs", '"files_checked": 1' in out, out[:200])

# --- 5. the engine is path-keyed and inert where nothing matches ---------------------

with tempfile.TemporaryDirectory() as td:
    rc, out = run("--root", td, "--json")
    check("a repo with no yf documents exits 0", rc == 0, f"got {rc}")
    check("...and checks zero files", '"files_checked": 0' in out, out[:200])

# --- 6. --no-exclude is a real positive control --------------------------------------

rc_with, out_with = run("--type", "plan", "--json")
rc_without, out_without = run("--type", "plan", "--no-exclude", "--json")
n_with = json.loads(out_with)["files_checked"]
n_without = json.loads(out_without)["files_checked"]
check("--no-exclude widens the file set", n_without >= n_with, f"{n_without} vs {n_with}")


# --- 7. CARVE-OUTS: the positive control must actually fire (plan-047 Issue 2.2-2.4) ------
# `control_fired: false` was originally the RIGHT answer for the WRONG reason: finding.toml's
# `paths` glob was single-level, so the 45 nested okf-migration-samples files were never
# selected and the carve-out under test was never exercised. A control that cannot fire is
# the same defect class as a gate that cannot fail.

# plan-048 Issue 2.3 NARROWED this deliberately. `/references/` was wholly carved when
# `reference.toml` was the only type reaching it and declared no content checks. Issue 2.3
# instantiates `upstream-reference` over the CODE-GENERATED subset
# (`references/upstream-<N>.md`, 194 files), which is no longer carved — it has a real
# producer to derive from, so linting it against that producer is exactly right.
#
# What stays carved is what the carve-out was always ABOUT: VENDORED content
# (`references/user-scope/**`) and hand-authored notes, neither of which has an authored
# template to check. Measured after 2.3: 16 of 194 generated references predate the current
# producer and lack its `- **Number:**` bullet — real drift, correctly reported at `W`.
CARVED = re.compile(
    r"(findings/okf-migration-samples/|/fixtures/|/references/user-scope/)")

rc, out = run("--json")
on = json.loads(out)
rc, out = run("--no-exclude", "--json")
off = json.loads(out)

carved_on = [f for f in on["findings"] if CARVED.search(f["path"])]
carved_off = [f for f in off["findings"] if CARVED.search(f["path"])]

check("zero findings inside the carved regions with excludes ON",
      len(carved_on) == 0, f"{len(carved_on)}: {[f['path'] for f in carved_on][:3]}")
check("the positive control FIRES with excludes off",
      len(carved_off) > 0, "control cannot fire — the carve-out is untested")
check("...and the control widens the file set",
      off["files_checked"] > on["files_checked"],
      f'{off["files_checked"]} vs {on["files_checked"]}')

# The specific region that the single-level glob could not reach.
nested_off = [f for f in off["findings"] if "okf-migration-samples/" in f["path"]]
check("the control reaches the NESTED okf-migration-samples corpus",
      len(nested_off) > 0,
      "a single-level `findings/*.md` glob reaches 0 of these — the vacuity regression")

# --- 8. glob DEPTH regression, by fixture -------------------------------------------------
# tests/fixtures/doclint/nested-reach/deeper/bad.md is one level deeper than a `*/findings/*.md`
# glob can reach. Reverting finding.toml to the single-level form must fail this.

sys.path.insert(0, str(SHARED))
import tomllib  # noqa: E402

ft = tomllib.load((SHARED / "document_types" / "finding.toml").open("rb"))
check("finding.toml globs are RECURSIVE",
      all("**" in g for g in ft["paths"]),
      f'non-recursive glob present: {ft["paths"]}')

nested = REPO / "tests" / "fixtures" / "doclint" / "nested-reach" / "deeper" / "bad.md"
rc, out = run("--type", "finding", "--path", str(nested))
check("a nested malformed finding is caught (exit 1)", rc == 1, f"got {rc}")

with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    deep = root / "docs" / "plans" / "plan-000-x" / "findings" / "sub" / "bad.md"
    deep.parent.mkdir(parents=True)
    deep.write_text(nested.read_text())
    rc, out = run("--type", "finding", "--root", str(root), "--json")
    n = json.loads(out)["files_checked"]
    check("a recursive glob SELECTS a nested findings/ file a single-level glob misses",
          n == 1, f"selected {n} — reverting finding.toml to `findings/*.md` makes this 0")


# --- 9. SEVERITY TIERS + STATUS-AWARE PROMOTION (Epic 4: Issues 4.1, 4.2) -----------------
# The mapping is what makes an always-on trigger non-hostile to a plan still being written,
# and what keeps a rule written today from retro-judging 46 bundles that predate it.

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("dl", SHARED / "doc_lint.py")
dl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dl)
sys.path.insert(0, str(SHARED))
import plan_template as _pt  # noqa: E402

_FM = ("---\ntype: Plan\nokf_spec: OKF-PLAN\nid: plan-001-t-aaaaaa\nauthor: t\n"
       "created: 2026-01-01\nstatus: %s\n---\n")


def _plan_repo(tmp: Path, status: str, body: str | None = None) -> Path:
    d = tmp / "docs" / "plans" / "plan-001-t-aaaaaa"
    d.mkdir(parents=True)
    (d / "plan.md").write_text(
        (_FM % status)
        + (body if body is not None
           else _pt.seed_body("x", "plan-001-t-aaaaaa", "t", "2026-01-01", status))
    )
    return tmp


with tempfile.TemporaryDirectory() as td:
    # A freshly seeded plan must lint with ZERO ERRORS at every pre-`review` status.
    # The seeded template is structurally valid by construction; only its placeholder
    # bodies are incomplete, and incomplete is `W`.
    for st in ("scoping", "investigating", "drafting"):
        root = _plan_repo(Path(td) / st, st)
        res = dl.lint(root, "plan", None)
        check(f"a fresh plan at `{st}` has 0 errors", res["errors"] == 0,
              f'{res["errors"]}: {[f["check"] for f in res["findings"] if f["severity"] == "E"]}')

    # At the enforcement point a completeness warning is PROMOTED to an error: the plan is
    # claiming to be finished.
    for st in ("review", "ready-for-approval"):
        root = _plan_repo(Path(td) / st, st)
        res = dl.lint(root, "plan", None)
        check(f"`W` is promoted to `E` at `{st}`", res["errors"] > 0,
              "an unfilled placeholder must block a plan claiming to be ready")

    # A finished plan is REPORT-ONLY and can never error, however non-conformant.
    root = _plan_repo(Path(td) / "complete", "complete",
                      body="# Plan: x\n\n## Objective\nnothing else at all\n")
    res = dl.lint(root, "plan", None)
    check("a `complete` plan NEVER errors", res["errors"] == 0, f'{res["errors"]}')
    check("...but its findings are still reported", res["report_only"] > 0,
          "report-only must still report — silence would be a different defect")

# --- 10. PATH-KEYING, never filename-keying (Issue 4.3) ------------------------------------
# Measured counterfactual: filename-keying (`**/plan.md`) selects the 17 test-fixture
# plan.md files and produces 73 errors on the ground-truth corpus of
# test_classify_deliverable.py. Path-keying produces 0.

fixture_plans = sorted(REPO.glob("skills/**/fixtures/**/plan.md"))
check("the fixture plan.md corpus still exists", len(fixture_plans) > 0)
would = dl.lint(REPO, "plan", fixture_plans, use_exclude=False)
check("filename-keying WOULD error on the fixture corpus", would["errors"] > 0,
      "if this stops being true the counterfactual has gone vacuous")
actual = dl.lint(REPO, "plan", None)
check("path-keying produces 0 findings there",
      len([f for f in actual["findings"] if "/fixtures/" in f["path"]]) == 0)

# --- 11. IDEMPOTENCY SELF-CHECK (Issue 4.5) ------------------------------------------------
# The linter is a pure reader: two consecutive runs over an untouched tree must return
# byte-identical verdicts, and neither may mutate the tree.

import hashlib  # noqa: E402


def _tree_hash(root: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(root.rglob("*.md")):
        h.update(f.read_bytes())
    return h.hexdigest()


before = _tree_hash(REPO / "docs" / "plans")
r1 = dl.lint(REPO, None, None)
r2 = dl.lint(REPO, None, None)
after = _tree_hash(REPO / "docs" / "plans")
check("two consecutive runs return identical verdicts",
      json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True))
check("the linter does not mutate the tree", before == after,
      "doc_lint must be a pure reader — it never auto-fixes")

# --- 12. INCONCLUSIVE means ONLY "could not run" (Issue 4.4) -------------------------------

rc, out = run("--json")
check("a clean corpus exits 0", rc == 0, f"got {rc}")
check("...and never reports INCONCLUSIVE", "INCONCLUSIVE" not in out)

# --- plan-048 Issue 2.10: one fixture pair per newly instantiated type -------------------
#
# SC5 asks each new type's `bad.md` to drive exit 1 and its conforming control to drive 0.
# The control is not decoration: without it a FAIL cannot be attributed to the mutation
# rather than to a pre-existing failure.
#
# SC5 AND D-10 CONFLICT FOR FIVE TYPES, and the conflict is resolved in D-10's favour:
#
#   * `research-summary`, `research-artifact`, `research-sources` — D-10 / REQ-DATA-045
#     forbids an `E` on `docs/research/**`, where `bundle_status` is null and `E` can never
#     be softened. Every check is `W`, and a `W` does not change the exit code. These types
#     therefore CANNOT drive exit 1 without violating the plan's own severity rule.
#   * `reference-comment` — same shape: its one check is `W`.
#   * `reference-tracker`, `reference-authored` — declare NO checks by design (3 and 12
#     heterogeneous files, no producer and no template), so there is nothing to fail.
#
# For those, the strongest available assertion is that the FINDING fires on the bad fixture
# and not on the control. Faking an `E` to satisfy SC5's literal wording would break D-10
# and hard-fail the research corpus permanently — a worse outcome than a scoped, recorded
# deviation.

EXIT_TYPES = [
    "review", "upstream-reference", "skill", "context",
    "upstream-triage", "plan-retrospective", "agent",
]
FINDING_ONLY_TYPES = [
    "research-summary", "research-artifact", "research-sources", "reference-comment",
]
NO_CHECK_TYPES = ["reference-tracker", "reference-authored"]

for _t in EXIT_TYPES:
    rc_bad, _ = run("--type", _t, "--path", str(FIXTURES / _t / "bad.md"))
    rc_good, _ = run("--type", _t, "--path", str(FIXTURES / _t / "good.md"))
    check(f"SC5 {_t}: bad.md drives exit 1", rc_bad == 1, f"got {rc_bad}")
    check(f"SC5 {_t}: conforming control drives exit 0", rc_good == 0, f"got {rc_good}")

for _t in FINDING_ONLY_TYPES:
    _, out_bad = run("--type", _t, "--path", str(FIXTURES / _t / "bad.md"), "--json")
    _, out_good = run("--type", _t, "--path", str(FIXTURES / _t / "good.md"), "--json")
    nb = len(json.loads(out_bad)["findings"])
    ng = len(json.loads(out_good)["findings"])
    check(f"SC5 {_t}: bad.md FIRES a finding (W-only per D-10, so exit stays 0)", nb > 0)
    check(f"SC5 {_t}: conforming control fires none", ng == 0, f"got {ng}")

# SC5b — the direct antidote to the D-11 silent green. `--path` on an UNSELECTED file
# returns the identical object to a NONEXISTENT path, so `errors == 0` proves nothing on
# its own. Every instantiated type must SELECT files from the real corpus.
for _t in EXIT_TYPES + FINDING_ONLY_TYPES + NO_CHECK_TYPES:
    _, out = run("--type", _t, "--json")
    d = json.loads(out)
    check(f"SC5b {_t}: selects > 0 real files", d["files_checked"] > 0,
          f'files_checked={d["files_checked"]} verdict={d.get("verdict")} '
          f'reason={d.get("reason", "")}')


# --- plan-048 Issue 3.4: R3 two-parser agreement must never be VACUOUS -------------------
#
# R3 shipped broken TWICE, in two different ways, and each time reported a clean corpus:
#   1. the source slice omitted a helper, so every call raised, was swallowed, and returned
#      None — "not checked" rendered as "agreed";
#   2. once running, it joined `#113` against `113` — ZERO shared keys, so it compared
#      nothing and reported no disagreements forever.
# Both are R4's defect class (a check that cannot fail) inside the rule meant to catch a
# two-parser split. These pins make a silent return to either state a test failure.

_pm_view = doc_lint_mod._parse_upstream_rows_view
_ctrl = REPO / "docs" / "plans" / "plan-047-james-dixson-dec9ff" / "plan.md"
if _ctrl.exists():
    _theirs = _pm_view(_ctrl)
    check("R3: the plan_manager parser view actually loads (not None)",
          _theirs is not None,
          "a None view makes R3 report agreement while checking nothing")
    if _theirs is not None:
        _d = doc_lint_mod._plan_extract().extract(_ctrl)
        _mine = {str(u["issue"]).lstrip("#"): u["disposition"] for u in _d["upstream"]}
        _th = {k.lstrip("#"): v for k, v in _theirs.items()}
        _common = set(_mine) & set(_th)
        check("R3: the two parsers share issue-number keys (the join is real)",
              len(_common) > 0 and len(_common) == len(_mine),
              f"common={len(_common)} mine={len(_mine)} theirs={len(_th)}")

# The escaped-pipe row R3 found on its first live run. plan-013 #17's title contains
# `(coarse\|granular)`; a naive split shifts every later cell left by one, so the
# DISPOSITION column reads `granular)` and the row escapes verification entirely.
_p013 = sorted((REPO / "docs" / "plans").glob("plan-013-*/plan.md"))
if _p013:
    _v = _pm_view(_p013[0])
    check("R3 regression: an escaped pipe in a title does not shift the disposition cell",
          _v is not None and _v.get("17") == "include",
          f'got {None if _v is None else _v.get("17")!r}, expected \'include\'')


print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
