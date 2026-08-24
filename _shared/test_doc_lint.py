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
import shutil
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
# plan-052 Issue 1.2: this asserted the WORD never appears anywhere in the JSON, which is a
# different claim from "the VERDICT is never INCONCLUSIVE". Findings quote document content
# back to the reader, so any plan whose own `Verification` cell contains the word trips a
# substring scan — and one does. The verdict vocabulary is what Issue 4.4 was about, so the
# assertion now reads the field it was always about.
check("...and never reports INCONCLUSIVE",
      json.loads(out).get("verdict") != "INCONCLUSIVE",
      f'verdict={json.loads(out).get("verdict")!r}')

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


# --- plan-048 Issue 3.5 / SC10: the seven COMMITTED relational fixtures -----------------
#
# These are committed artifacts, distinct from the mutants `gate-relations.sh` generates at
# run time. The gate generates its own precisely so it never executes this deliverable —
# 3.5 sits in the gate's BLOCKED set, so a gate that ran these fixtures would be circular.
#
# THE CONTROL IS NOT DECORATION. Without an unmutated plan-047 asserting zero findings, the
# bold-disposition mutant passes trivially: any fixture "fails" if the control already
# fails, and the mutation would be credited for a pre-existing defect.

RELFIX = REPO / "tests" / "fixtures" / "plan-relations"
_EXPECTED_FIXTURES = 7
_MUTANTS = {
    "m1-R1-dangling-discharged-by": "R1",
    "m2-R1b-issue-named-by-no-criterion": "R1b",
    "m3-R2a-dangling-resolved-by": "R2a",
    "m4-R2b-exclude-resolves-something": "R2b",
    "m5-R2c-unrecognised-disposition": "R2c",
    "m6-R2b-include-resolves-nothing": "R2b",
    "m7-R1-criterion-names-a-letter-issue": "R1",
}

_on_disk = sorted(p.stem for p in RELFIX.glob("m*.md"))
check(f"SC10: exactly {_EXPECTED_FIXTURES} relational fixtures are committed",
      len(_on_disk) == _EXPECTED_FIXTURES, f"found {len(_on_disk)}: {_on_disk}")
check("SC10: the fixtures on disk are the ones the test drives",
      set(_on_disk) == set(_MUTANTS), f"disk={_on_disk} expected={sorted(_MUTANTS)}")

_, _out = run("--type", "plan-relations", "--path", str(RELFIX / "control.md"), "--json")
_ctrl_findings = json.loads(_out).get("findings", [])
check("SC10: the UNMUTATED control reports zero relational findings",
      len(_ctrl_findings) == 0,
      f"control already fails: {[f[chr(39)+chr(39).join([]) or 'check'] for f in _ctrl_findings][:4]}")

for _name, _rule in sorted(_MUTANTS.items()):
    _, _o = run("--type", "plan-relations", "--path", str(RELFIX / f"{_name}.md"), "--json")
    _d = json.loads(_o)
    _fired = [f for f in _d.get("findings", []) if f["check"] == _rule]
    check(f"SC10 {_name}: makes {_rule} fire", len(_fired) > 0,
          f'findings={[f["check"] for f in _d.get("findings", [])]}')


# --- plan-049 Issue 0.2 / SC13: `promote = false` bypasses STATUS_SEVERITY both ways -----
#
# THE FIXTURE MUST BE A BUNDLE. A flat file has no sibling `plan.md`, so `bundle_status()`
# returns None, the promotion map never applies, and the assertion **exits 0 before any fix**
# — a vacuous green. `promotion-off-bundle/plan.md` carries `status: review`, the status at
# which the un-fixed engine promoted `W -> E`.
#
# BOTH ARMS COME FROM THE SAME INVOCATION SHAPE. The post-fix arm runs the shipped engine;
# the pre-fix arm re-runs the identical call against a types-dir whose `plan-relations.toml`
# has the `promote = false` line stripped — i.e. exactly the schema as it stood before this
# issue. Asserting only the green arm would pass against an engine that never promotes
# anything.

PROMO_BUNDLE = FIXTURES / "plan-relations" / "promotion-off-bundle" / "plan.md"

check("SC13: the promotion-off fixture is a BUNDLE (sibling plan.md is the file itself)",
      PROMO_BUNDLE.is_file() and doc_lint_mod.bundle_status(PROMO_BUNDLE) == "review",
      f"bundle_status={doc_lint_mod.bundle_status(PROMO_BUNDLE) if PROMO_BUNDLE.is_file() else 'no fixture'!r}")

_rc_post, _out_post = run("--type", "plan-relations", "--path", str(PROMO_BUNDLE), "--json")
_d_post = json.loads(_out_post)
check("SC13 post-fix: exits 0 at `review` (W is not promoted to E)", _rc_post == 0,
      f"rc={_rc_post} errors={_d_post.get('errors')}")
check("SC13 post-fix: the R1b finding keeps its declared `W`",
      [f["severity"] for f in _d_post["findings"] if f["check"] == "R1b"] == ["W"],
      f'severities={[(f["check"], f["severity"]) for f in _d_post["findings"]]}')
check("SC13 post-fix: the finding is not silently absent (the arm would be vacuous)",
      any(f["check"] == "R1b" for f in _d_post["findings"]),
      f'findings={[f["check"] for f in _d_post["findings"]]}')

with tempfile.TemporaryDirectory() as _td:
    _pre_types = Path(_td) / "document_types"
    shutil.copytree(SHARED / "document_types", _pre_types)
    _rel = _pre_types / "plan-relations.toml"
    _rel.write_text("\n".join(l for l in _rel.read_text().splitlines()
                              if not l.strip().startswith("promote")) + "\n")
    _saved = doc_lint_mod.TYPES_DIR
    try:
        doc_lint_mod.TYPES_DIR = _pre_types
        _pre = doc_lint_mod.lint(REPO, "plan-relations", [PROMO_BUNDLE])
    finally:
        doc_lint_mod.TYPES_DIR = _saved
    check("SC13 pre-fix: the SAME fixture yielded an ERROR before the fix "
          "(so the green arm above is a real signal, not a no-op)",
          _pre["errors"] >= 1,
          f'pre-fix errors={_pre["errors"]} '
          f'severities={[(f["check"], f["severity"]) for f in _pre["findings"]]}')
    check("SC13 pre-fix: the promoted finding is the R1b whose declared severity is `W`",
          any(f["check"] == "R1b" and f["severity"] == "E" and f["declared_severity"] == "W"
              for f in _pre["findings"]),
          f'{[(f["check"], f["declared_severity"], f["severity"]) for f in _pre["findings"]]}')

# The other direction: `complete` must not DEMOTE a non-promoting schema's `W` to `R`.
_ctrl_status = doc_lint_mod.bundle_status(RELFIX / "control.md")
_, _o_m2 = run("--type", "plan-relations", "--path",
               str(RELFIX / "m2-R1b-issue-named-by-no-criterion.md"), "--json")
_d_m2 = json.loads(_o_m2)
check("SC13: a non-promoting schema is not demoted either — no R1b finding is reported as `R`",
      all(f["severity"] != "R" for f in _d_m2["findings"] if f["check"] == "R1b"),
      f'severities={[(f["check"], f["severity"], f["bundle_status"]) for f in _d_m2["findings"]]}')


# --- plan-049 Issue 0.3 / SC14: this plan's own Upstream Issues table at `review` ---------
#
# EXP-003 measured plan-049-as-drafted at 3 R2b errors from `_tbd_` cells in the
# `## Upstream Issues` table. They were filled at drafting; this asserts it, so the fix
# cannot silently regress.
#
# The copy is built at RUN TIME from the LIVE plan.md rather than committed as a fixture:
# a committed 47 KB duplicate would go stale the moment the plan is edited, and would then
# assert about a document nobody reads. Forcing `status: review` is the whole point —
# `review` is the status at which the intake binding grades a plan.
#
# STATED INTERACTION, because it makes the criterion weaker than it reads: since Issue 0.2
# (REQ-DATA-053) no `plan-relations` finding can be `E` at ANY status, so "zero R2b ERRORS"
# is now true of every plan by construction. The assertion below is therefore on **zero R2b
# findings at any severity**, which is the claim SC14 was actually written to make. The
# positive control that R2b *can* fire is the committed m4/m6 mutants above.

_LIVE = sorted((REPO / "docs" / "plans").glob("plan-049-*/plan.md"))
check("SC14: the live plan-049 bundle is present to assert against", len(_LIVE) == 1,
      f"found {[str(x) for x in _LIVE]}")
if len(_LIVE) == 1:
    with tempfile.TemporaryDirectory() as _td:
        _b = Path(_td) / "plan-049-review-copy"
        _b.mkdir()
        _src = _LIVE[0].read_text(encoding="utf-8")
        _copy = re.sub(r"(?m)^status: .*$", "status: review", _src, count=1)
        _copy = re.sub(r"(?m)^\*\*Status:\*\* .*$", "**Status:** review", _copy, count=1)
        (_b / "plan.md").write_text(_copy, encoding="utf-8")
        check("SC14: the forced copy really reads `review` (else the arm is vacuous)",
              doc_lint_mod.bundle_status(_b / "plan.md") == "review",
              f"bundle_status={doc_lint_mod.bundle_status(_b / 'plan.md')!r}")
        _rc14, _out14 = run("--type", "plan-relations", "--path", str(_b / "plan.md"), "--json")
        _d14 = json.loads(_out14)
        check("SC14: plan-049's own Upstream Issues table yields zero R2b findings at `review`",
              not [f for f in _d14["findings"] if f["check"] == "R2b"],
              f'R2b={[f["detail"][:90] for f in _d14["findings"] if f["check"] == "R2b"]}')
        check("SC14: and the run is a real one — the file was linted, not skipped",
              _d14["files_checked"] == 1, f'files_checked={_d14["files_checked"]}')
        check("SC14: exit 0 at `review`", _rc14 == 0,
              f'rc={_rc14} findings={[(f["check"], f["severity"]) for f in _d14["findings"]]}')


# --- plan-049 Epic 3 / SC9, SC10, SC41: the two new document checks ----------------------
#
# EPIC 1 HAS MUTANT D AS ITS FALSE-POSITIVE CONTROL; EPIC 3 HAD NONE, and that omission is
# exactly what let the wrong gate predicate through. A check driven only by mutants is
# indistinguishable from a check that fires on everything — and the obvious `Type` + one-of
# gate predicate DOES fire on everything: measured, 79 of the 131 corpus gates, including
# every Start Gate and the canonical template itself.

DC = REPO / "tests" / "fixtures" / "doc-checks"
_DC_ARMS = {
    "m-empty-required-cell": 1,
    "m-zero-row-criteria": 1,
    "m-gate-all-three-absent": 1,
    "control-conformant": 0,
    "control-canonical-start-gate": 0,
}
for _stem, _want in sorted(_DC_ARMS.items()):
    _f = DC / _stem / "plan.md"
    check(f"SC41: fixture {_stem} is committed as a BUNDLE", _f.is_file(), str(_f))

for _stem, _want in sorted(_DC_ARMS.items()):
    _f = DC / _stem / "plan.md"
    if not _f.is_file():
        continue
    _rc, _o = run("--type", "plan", "--path", str(_f), "--json")
    _d = json.loads(_o)
    _kind = "positive" if _want else "false-positive control"
    check(f"SC9/SC10 {_kind}: {_stem} exits {_want}", _rc == _want,
          f'rc={_rc} findings={[(f["check"], f["severity"]) for f in _d.get("findings", [])]}')

# Direction-specific, so a check that fires on BOTH arms cannot pass by luck.
_rc, _o = run("--type", "plan", "--path", str(DC / "m-empty-required-cell" / "plan.md"), "--json")
check("SC9: an empty required cell is attributed to `criteria-cells-filled`",
      any(f["check"] == "criteria-cells-filled" for f in json.loads(_o)["findings"]), _o[:200])
_rc, _o = run("--type", "plan", "--path", str(DC / "m-zero-row-criteria" / "plan.md"), "--json")
check("SC9: a ZERO-ROW table is attributed to `criteria-cells-filled` "
      "(the hole EXP-006 measured as wider than recorded)",
      any(f["check"] == "criteria-cells-filled" and "ZERO rows" in f["detail"]
          for f in json.loads(_o)["findings"]), _o[:200])
_rc, _o = run("--type", "plan", "--path", str(DC / "m-gate-all-three-absent" / "plan.md"), "--json")
check("SC10: a gate with ALL THREE of Type/Condition/Test absent is attributed to "
      "`gate-completeness`",
      any(f["check"] == "gate-completeness" for f in json.loads(_o)["findings"]), _o[:200])
_rc, _o = run("--type", "plan", "--path",
              str(DC / "control-canonical-start-gate" / "plan.md"), "--json")
check("SC10 (the other direction): the CANONICAL `Type: human` + `Approvers: operator` Start "
      "Gate does NOT fire — the measured 79-of-131 false positive",
      not [f for f in json.loads(_o)["findings"] if f["check"] == "gate-completeness"], _o[:200])

# The canonical fixture must contain the LITERAL template text. Without this, the fixture can
# silently drift away from the template it claims to protect and keep passing forever.
_canon = "## Gates\n### Start Gate (mandatory)\n- Type: human\n- Approvers: operator\n"
check("SC10: the canonical control embeds the LITERAL `plan_template.py` Start Gate block",
      _canon in (DC / "control-canonical-start-gate" / "plan.md").read_text()
      and _canon in (SHARED / "plan_template.py").read_text().encode()
          .decode("unicode_escape"),
      "fixture and template have diverged — re-derive the fixture")

# SC41: both blast radii MEASURED here, not cited, and asserted to be small. A check with a
# huge blast radius is one that has to be bound at `W` forever, i.e. one that never enforces.
_SELF = "plan-049-james-dixson-725bc0"
_corpus = [p for p in sorted((REPO / "docs" / "plans").glob("*/plan.md"))
           if p.parent.name != _SELF]
_radius = {"criteria-cells-filled": 0, "upstream-cells-filled": 0, "gate-completeness": 0}
for _p in _corpus:
    _txt = _p.read_text(encoding="utf-8", errors="replace")
    for _schema in doc_lint_mod.load_schemas("plan"):
        for _chk in _schema["checks"]:
            if _chk["id"] in _radius:
                _radius[_chk["id"]] += len(doc_lint_mod.run_check(_chk, _txt, _schema, path=_p))
print(f"     [measured] blast radius over {len(_corpus)} plans (plan-049 self-excluded): {_radius}")
check("SC41: `criteria-cells-filled` has a measured blast radius of 0 over the corpus",
      _radius["criteria-cells-filled"] == 0, str(_radius))
# MEASURED 2 BEFORE Issue 3.3, AND 1 AFTER — the drop is the relocation working.
# plan-008's `Capability Gate: d2 present (see above)` stub was one of the two; the authorized
# corpus write removed it, so the check that flagged it as vacuous now finds one fewer. The
# survivor is plan-006's `### Reconcile Gate` / `- Not needed — no upstream issues
# incorporated`, whose "declare it not needed" idiom Issue 3.2 decided EXPLICITLY should fire
# (free prose is machine-indistinguishable from an unfinished gate) and which is left in place
# because it sits in a `complete` bundle and needs no corpus write to resolve.
check("SC41: `gate-completeness` fires on exactly 1 gate — plan-006's, the survivor after "
      "Issue 3.3 removed plan-008's vacuous stub",
      _radius["gate-completeness"] == 1, str(_radius))
check("SC41: ...and the survivor is the one Issue 3.2 decided should fire",
      any("Reconcile Gate" in d for _p in _corpus
          for _schema in doc_lint_mod.load_schemas("plan")
          for _chk in _schema["checks"] if _chk["id"] == "gate-completeness"
          for d in doc_lint_mod.run_check(
              _chk, _p.read_text(encoding="utf-8", errors="replace"), _schema, path=_p)),
      "the surviving finding is not plan-006's Reconcile Gate")
check("SC41: `upstream-cells-filled` stays in single digits "
      "(measured 5, all the zero-row shape)",
      _radius["upstream-cells-filled"] < 10, str(_radius))
check("SC41: and none of the three is VACUOUS — each fires on its own mutant above",
      all(v == 1 for k, v in _DC_ARMS.items() if k.startswith("m-")))


# --- plan-049 Issue 4.1 / SC15, SC42: the engine is VENDORED, and the vendor is REAL -------
#
# EXP-004 measured `find skills -name doc_lint.py` -> EMPTY, while `embed.rs` embeds only
# `../skills`. The always-on on-edit rule (Issue 4.3) would therefore have referenced an
# engine that exists in **no deployed vault** — a hard blocker neither plan-047 nor plan-048
# named.
#
# A BYTE-IDENTICAL VENDOR OF A ROOT-RELATIVE SCRIPT IS NOT A VENDOR, which is the whole
# reason SC42 asks for more than "the file is present". `doc_lint.py` computed its repo root
# positionally, so the copy at `skills/yf-plan/scripts/` resolved the root to the SKILL
# DIRECTORY, matched no `docs/plans/**` glob, and returned `files_checked: 0`. That is
# `verdict: PASS`, `exit 0` — indistinguishable from a clean run at every binding point.

VENDOR = REPO / "skills" / "yf-plan" / "scripts"
check("SC15: the engine is vendored into a deployed skill dir",
      (VENDOR / "doc_lint.py").is_file(), str(VENDOR / "doc_lint.py"))
check("SC15: and so is its TRANSITIVE closure — schemas plus the two modules "
      "`resolve_derived` imports from its own directory",
      (VENDOR / "document_types").is_dir()
      and (VENDOR / "plan_extract.py").is_file()
      and (VENDOR / "plan_template.py").is_file(),
      f"document_types={(VENDOR / 'document_types').is_dir()} "
      f"plan_extract={(VENDOR / 'plan_extract.py').is_file()} "
      f"plan_template={(VENDOR / 'plan_template.py').is_file()}")
_canon_types = sorted(p.name for p in (SHARED / "document_types").glob("*.toml"))
_vend_types = sorted(p.name for p in (VENDOR / "document_types").glob("*.toml"))
check("SC15: EVERY schema is vendored, not a hand-picked subset "
      "(an omitted schema is invisible — the copy just never runs that check)",
      _canon_types == _vend_types,
      f"canonical-only={set(_canon_types) - set(_vend_types)} "
      f"vendor-only={set(_vend_types) - set(_canon_types)}")
_sync = subprocess.run(["uv", "run", str(SHARED / "sync.py"), "--check"],
                       capture_output=True, text=True, cwd=REPO)
check("SC15: `sync.py --check` is green, so drift in any vendored copy fails loudly",
      _sync.returncode == 0, _sync.stdout[-400:] + _sync.stderr[-400:])

# SC42 proper: run BOTH copies over the same REAL, FINDING-PRODUCING document and diff the
# JSON. A document with zero findings would make the comparison pass trivially.
_target = REPO / "docs" / "plans" / "plan-006-james-dixson-bf6e21" / "plan.md"
_rc_c, _o_c = run("--type", "plan", "--path", str(_target), "--json")
_p = subprocess.run(["uv", "run", str(VENDOR / "doc_lint.py"),
                     "--type", "plan", "--path", str(_target), "--json"],
                    capture_output=True, text=True, cwd=REPO)
_dc, _dv = json.loads(_o_c), json.loads(_p.stdout)
check("SC42: the VENDORED engine reports `files_checked >= 1` on a real typed document "
      "(`files_checked: 0` does NOT discharge this)",
      _dv["files_checked"] >= 1, f'files_checked={_dv["files_checked"]}')
check("SC42: the comparison is not vacuous — the document actually produces findings",
      len(_dc["findings"]) > 0, f'canonical findings={len(_dc["findings"])}')
_strip = lambda d: {k: v for k, v in d.items() if k != "findings"} | {  # noqa: E731
    "findings": sorted((f["check"], f["severity"], f["detail"]) for f in d["findings"])}
check("SC42: and it REPRODUCES the `_shared/` copy's verdict, finding for finding",
      _strip(_dc) == _strip(_dv),
      f'canonical={_strip(_dc)}\n     vendored={_strip(_dv)}')

# The defect, demonstrated rather than described: force the old positional root and watch a
# silent green appear.
_p2 = subprocess.run(["uv", "run", str(VENDOR / "doc_lint.py"), "--type", "plan",
                      "--root", str(REPO / "skills" / "yf-plan"), "--json"],
                     capture_output=True, text=True, cwd=REPO)
_d2 = json.loads(_p2.stdout)
check("SC42: with the OLD positional root the same engine returns `files_checked: 0`, "
      "`verdict: PASS`, exit 0 — the silent green this issue closes",
      _d2["files_checked"] == 0 and _d2["verdict"] == "PASS" and _p2.returncode == 0,
      f'files_checked={_d2["files_checked"]} verdict={_d2["verdict"]} rc={_p2.returncode}')


# --- SC17: the on-edit rule's DECISION PROCEDURE ------------------------------------------
#
# AMENDED by plan-050 Issue 2.2a (#181). The rule used to MANDATE PARSING `files_checked` and
# reporting `not-a-typed-document` — prose instructing an agent to read a field and
# reinterpret it. It now runs `doc_lint.py --classify` FIRST and branches on the returned
# `class`, which is an executed step carrying an exit code.
#
# THE ASSERTION MOVED WITH THE CONTRACT, DELIBERATELY. The two old literals still appear in
# the rewritten rule for real reasons — `files_checked` in the table explaining what the field
# still means, `not-a-typed-document` as the thing to report on the `not-selected` class — so
# the ORIGINAL assertion would still pass. Leaving it would have been the M5 vacuity class
# inside the test suite: a check that goes green against a contract that no longer exists.
# What is pinned here is the NEW decision procedure.

RULE = REPO / "skills" / "yf-plan" / "protocols" / "DOC-LINT.md"
check("SC17: the on-edit rule ships", RULE.is_file(), str(RULE))
_rule = RULE.read_text(encoding="utf-8") if RULE.is_file() else ""
check("SC17: the rule's on-edit step RUNS the classifier — not prose telling an agent to "
      "parse a field",
      "--classify" in _rule, "no `--classify` invocation in the on-edit rule")
check("SC17: it branches on the returned `class`, and says so explicitly — the two "
      "not-lintable classes share exit 1 and are different facts",
      all(c in _rule for c in
          ("`selected`", "`empty`", "`not-selected`", "`no-such-path`"))
      and "never on the classify exit code alone" in _rule)
check("SC17: `empty` is routed to the LINTABLE side — skipping it would manufacture a new "
      "silent green inside the fix for a silent green",
      "| `empty` | `0` | **lint it**" in _rule)
check("SC17: `no-such-path` is an ERROR, not an ordinary skip — a caller naming a file that "
      "does not exist is a caller bug",
      "caller bug" in _rule)
check("SC17: the `--root` form is documented — a bundle COPIED outside docs/plans/ is "
      "#181's titled scenario, and documenting only `--path` would leave the headline "
      "undocumented",
      "--classify --root" in _rule or ("--root" in _rule and "copied outside" in _rule.lower()))
check("SC17: the rule still explains what `files_checked` means — the field did not change, "
      "it simply stopped being the caller's decision procedure",
      "files_checked" in _rule and "not-a-typed-document" in _rule)
check("SC17: BOTH exit vocabularies are stated, keyed by mode — the same executable now "
      "carries two, and a caller reading the wrong one reads a number that means something "
      "else",
      "LINT mode" in _rule and "CLASSIFY mode" in _rule)
check("SC17: the rule declares NO marker file — inertness is structural via path-keying",
      "no opt-in marker" in _rule or "No marker file" in _rule)
_man = json.loads((REPO / "skills" / "yf-plan" / "protocols" / "manifest.json").read_text())
check("SC17: and it is registered in the protocols manifest, so drift is detected",
      "DOC-LINT.md" in _man.get("files", {}), str(sorted(_man.get("files", {}))))

# Driven with a REAL unselected file, as SC17 requires — the reserved OKF `index.md` that
# sits inside every plan bundle and that no type claims.
_B = REPO / "docs" / "plans" / "plan-049-james-dixson-725bc0"
_rc_u, _o_u = run("--path", str(_B / "index.md"), "--json")
_d_u = json.loads(_o_u)
_rc_m, _o_m = run("--path", str(_B / "does-not-exist.md"), "--json")
_d_m = json.loads(_o_m)
_rc_s, _o_s = run("--path", str(_B / "plan.md"), "--json")
_d_s = json.loads(_o_s)
check("SC17: a REAL unselected path reports `files_checked: 0`",
      _d_u["files_checked"] == 0, str(_d_u)[:160])
check("SC17: and it is INDISTINGUISHABLE from a clean pass at the exit-code level — "
      "which is exactly why the rule now runs `--classify` FIRST rather than reading the "
      "lint's output and guessing",
      _rc_u == 0 and _d_u["verdict"] == "PASS" and _rc_s == 0 and _d_s["verdict"] == "PASS",
      f'unselected rc={_rc_u}/{_d_u["verdict"]} selected rc={_rc_s}/{_d_s["verdict"]}')
check("SC17: an unselected path and a NONEXISTENT path return the same object — the failure "
      "is silent in both directions",
      (_d_u["files_checked"], _d_u["verdict"], _rc_u)
      == (_d_m["files_checked"], _d_m["verdict"], _rc_m),
      f"unselected={_d_u} nonexistent={_d_m}")
check("SC17: the contrast arm is real — a SELECTED path reports `files_checked >= 1`",
      _d_s["files_checked"] >= 1, str(_d_s)[:160])


# --- plan-049 Issue 5.1 / SC19: `--exclude`, DERIVED not an era literal -------------------
#
# SC19 forbids a fixed number in the assertion, and the reason is the bug itself: #135 is
# about measured literals going stale, so a test pinned to "48" would be the same defect in
# the test suite. The identity below is checked over the LIVE tree, for TWO different plans.

for _plan in ("plan-010-james-dixson-73eebd", "plan-047-james-dixson-dec9ff"):
    _all = json.loads(run("--type", "plan", "--json")[1])["files_checked"]
    _exc = json.loads(run("--type", "plan", "--exclude", f"docs/plans/{_plan}/**",
                          "--json")[1])["files_checked"]
    _own = json.loads(run("--type", "plan", "--path",
                          str(REPO / "docs" / "plans" / _plan / "plan.md"),
                          "--json")[1])["files_checked"]
    check(f"SC19 [{_plan.split('-')[1]}]: excluded == unexcluded - that plan's own "
          f"contribution (derived; no literal appears in this assertion)",
          _exc == _all - _own, f"all={_all} excluded={_exc} own={_own}")
    check(f"SC19 [{_plan.split('-')[1]}]: the arm is not vacuous — the plan really does "
          f"contribute", _own > 0 and _all > _exc, f"all={_all} excluded={_exc} own={_own}")

# `--exclude` must survive `--no-exclude`. A positive control that silently re-admits the
# measuring plan reintroduces exactly the self-reference the flag removes.
_p = "plan-047-james-dixson-dec9ff"
_ne = json.loads(run("--type", "plan", "--no-exclude", "--json")[1])["files_checked"]
_ne_x = json.loads(run("--type", "plan", "--no-exclude",
                       "--exclude", f"docs/plans/{_p}/**", "--json")[1])["files_checked"]
check("SC19: `--exclude` is honoured even under `--no-exclude` — the schema's carve-outs and "
      "a caller's self-exclusion are different kinds of thing",
      _ne_x < _ne, f"no-exclude={_ne} no-exclude+exclude={_ne_x}")


# --- plan-049 Issues 5.2 / 5.3 (SC20, SC21): the #135 in-flight rule --------------------
#
# THE SCOPING IS THE DELIVERABLE. EXP-005 measured the naive form — "a number near a corpus
# noun" — firing **41 of 41 times, 39 of them on correct historical behaviour**. A completed
# plan's measurement is a HISTORICAL RECORD and is *supposed* to be a frozen literal; the
# measured-marker failure mode is re-judging it. So both arms are asserted: it must fire
# in-flight AND stay silent on the finished corpus.

_sml = [f for f in json.loads(run("--type", "plan", "--json")[1])["findings"]
        if f["check"] == "stale-measured-literal"]
check("SC20: the rule fires on ZERO of the finished corpus plans",
      not _sml, f"fired on {[f['path'] for f in _sml]}")

with tempfile.TemporaryDirectory() as _td:
    _b = Path(_td) / "inflight"
    shutil.copytree(REPO / "docs" / "plans" / "plan-049-james-dixson-725bc0", _b)
    _pm = _b / "plan.md"
    _tx = _pm.read_text(encoding="utf-8")
    _tx = re.sub(r"(?m)^status: .*$", "status: review", _tx, count=1)
    _tx = re.sub(r"(?m)^\*\*Status:\*\* .*$", "**Status:** review", _tx, count=1)
    _pm.write_text(_tx, encoding="utf-8")
    _rc_i, _o_i = run("--type", "plan", "--path", str(_pm), "--json")
    _d_i = json.loads(_o_i)
    _fi = [f for f in _d_i["findings"] if f["check"] == "stale-measured-literal"]
    check("SC20: ...and DOES fire on the same bundle in-flight — so the silence above is "
          "scoping, not a dead rule", len(_fi) >= 2, f"fired {len(_fi)} times")
    check("SC20: it stays at its declared `W` even at `review` — a HINT must never hard-fail "
          "intake (check-level `promote = false`)",
          {f["severity"] for f in _fi} == {"W"}, str({f["severity"] for f in _fi}))
    check("SC20: and the bundle's error count is unaffected by it",
          _d_i["errors"] == 0, f'errors={_d_i["errors"]}')
    check("SC20: findings/ and reviews/ are skipped — a writeup and a review verdict are "
          "point-in-time records BY CONSTRUCTION",
          not [f for f in _fi if "/findings/" in f["path"] or "/reviews/" in f["path"]],
          str([f["path"] for f in _fi]))
    check("SC21: the DENOMINATOR-ONLY blind spot is stated where a reader meets it — "
          "in the finding text itself",
          all("DENOMINATOR-ONLY" in f["detail"] for f in _fi),
          str([f["detail"][:60] for f in _fi]))

check("SC21: ...and in the check's own declaration, so an author reading the schema meets it",
      "denominator-only" in (SHARED / "document_types" / "plan.toml")
      .read_text(encoding="utf-8").lower())
check("SC21: ...and in the engine's own docstring for the kind",
      "DENOMINATOR-ONLY" in (SHARED / "doc_lint.py").read_text(encoding="utf-8")
      or "denominator-only" in (SHARED / "doc_lint.py").read_text(encoding="utf-8").lower())

# The promotion carve-out must be SURGICAL: other `plan` checks still promote at `review`.
#
# plan-052 Issue 1.2 added the SECOND opt-out, `verification-clause`. The invariant this
# guards is "carve-outs are rare and each is justified", not "there can only ever be one" —
# so the list is expected to grow slowly and each entry must carry its measurement in the
# schema. Measured before shipping that one: 0 of 186 criteria across 52 bundles are in the
# clause grammar, so promoting it would hard-fail intake on 51 of 52 plans for a convention
# that did not exist when they were written. That is an outage, not a check.
_sch = [s for s in doc_lint_mod.load_schemas("plan")][0]
_promoting = [c["id"] for c in _sch["checks"] if c.get("promote", True)]
_not = [c["id"] for c in _sch["checks"] if not c.get("promote", True)]
check("check-level `promote = false` is SURGICAL — only the hint opts out",
      _not == ["stale-measured-literal", "verification-clause"] and len(_promoting) > 5,
      f"opted-out={_not} promoting={len(_promoting)}")


print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
