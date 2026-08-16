# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pytest>=8",
#     "pyyaml>=6",
# ]
# ///
"""Tier-1 regression suite for the deliverable-class classifier (REQ-CLI-015, plan-039).

Run from anywhere:  uv run skills/yf-plan/scripts/test_classify_deliverable.py

The suite scores `_classify_deliverable` against the **vendored** fixture corpus in
`fixtures/classify/` — one directory per operator-labeled plan, each holding a reduced
`plan.md` whose frontmatter carries the operator's ground-truth `deliverable_class`.
See `fixtures/classify/README.md` for how the corpus was derived and why it is vendored.

**Nothing here is a transcribed number.** Every count is re-derived from the corpus on
the fly. The corpus is self-including — a plan joins the ground-truth set the moment its
`deliverable_class` is written at intake — so any literal expectation goes stale as plans
are added. What the suite asserts instead are the two properties that must hold whatever
the corpus size:

  - **`FN == 0` — the hard invariant.** A false negative (a genuine `ci-release` plan
    suggested `standard`) silently disarms `complete-gate`. A false positive costs an
    operator seconds at intake. Recall is the safety-critical direction, so `FN` is
    asserted at zero and never traded away for precision.
  - **`FP` is non-increasing across the fix sequence.** The fixes landed in measured
    order (F3 -> F1 -> F2 -> F5 -> F4); each step must not make precision worse than the
    step before it. The suite reproduces that ordering by construction.

Plus two structural pins that do not depend on corpus composition at all:

  - **F1** — a trigger word in the H1/title (out of the scan region) yields no signal.
  - **F5** — a trigger word inside a fenced block or an inline code span yields no
    signal (SC5b): two documents identical except for backticks must not score alike.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent
FIXTURES = SCRIPTS / "fixtures" / "classify"

#: Ratchet markers. Each fix-specific pin below lands with the harness at Issue 3.1 —
#: BEFORE the fix it describes — as a *strict* xfail: red-by-design, so the suite is
#: green at every step, and the moment the fix lands pytest fails with an UNEXPECTED
#: PASS until the marker is removed. That makes "the harness measured this fix" a
#: mechanical fact rather than a claim. Remove a marker in the issue that lands its fix.
PENDING_F3 = pytest.mark.xfail(strict=True, reason="F3 not yet landed (Issue 3.2)")
PENDING_F1 = pytest.mark.xfail(strict=True, reason="F1 not yet landed (Issue 3.3)")
PENDING_F2 = pytest.mark.xfail(strict=True, reason="F2 not yet landed (Issue 3.4)")
PENDING_F5 = pytest.mark.xfail(strict=True, reason="F5 not yet landed (Issue 3.4b)")
PENDING_F4 = pytest.mark.xfail(strict=True, reason="F4 not yet landed (Issue 3.5)")


def _load_plan_manager():
    spec = importlib.util.spec_from_file_location("pm", SCRIPTS / "plan_manager.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pm = _load_plan_manager()


# --------------------------------------------------------------------------- corpus


def _corpus() -> list[tuple[str, str, Path]]:
    """Return [(name, ground_truth_class, plan_dir)] for every vendored fixture."""
    out = []
    for d in sorted(FIXTURES.iterdir()):
        plan_md = d / "plan.md"
        if not d.is_dir() or not plan_md.exists():
            continue
        m = re.search(r"^deliverable_class:\s*(\S+)", plan_md.read_text(), re.M)
        assert m, f"fixture {d.name} carries no ground-truth deliverable_class"
        out.append((d.name, m.group(1).strip(), d))
    return out


def _score(corpus) -> dict:
    """Re-derive the confusion matrix over `corpus`. Never transcribe these numbers."""
    tp = fp = tn = fn = 0
    misses = []
    for name, truth, plan_dir in corpus:
        got = pm._classify_deliverable(plan_dir)["suggested_class"]
        if truth == "ci-release" and got == "ci-release":
            tp += 1
        elif truth == "standard" and got == "ci-release":
            fp += 1
            misses.append(f"FP {name}")
        elif truth == "standard" and got == "standard":
            tn += 1
        else:
            fn += 1
            misses.append(f"FN {name}")
    return {"TP": tp, "FP": fp, "TN": tn, "FN": fn, "n": len(corpus),
            "detail": misses}


def test_corpus_is_present_and_labeled():
    corpus = _corpus()
    assert corpus, (
        "no vendored fixtures found — the corpus must be self-contained in this repo "
        "(REQ-CLI-015 verification); no test may reach outside it"
    )
    classes = {truth for _, truth, _ in corpus}
    assert classes <= {"ci-release", "standard"}, f"unexpected ground truth: {classes}"
    assert "ci-release" in classes, (
        "the corpus contains no positive example, so FN could not be observed even if "
        "the classifier regressed"
    )


def test_no_false_negatives():
    """The hard invariant (REQ-CLI-015). A false negative disarms `complete-gate`."""
    result = _score(_corpus())
    assert result["FN"] == 0, (
        f"FALSE NEGATIVE — a genuine ci-release plan was suggested `standard`, which "
        f"silently disarms complete-gate. {result['detail']}"
    )


def test_positive_example_still_classifies_ci_release():
    """SC5: no labeled `ci-release` plan regresses to `standard`."""
    for name, truth, plan_dir in _corpus():
        if truth != "ci-release":
            continue
        got = pm._classify_deliverable(plan_dir)
        assert got["suggested_class"] == "ci-release", (
            f"{name} is operator-labeled ci-release but classified "
            f"{got['suggested_class']} (signals={got['signals']})"
        )


def _baseline() -> dict:
    """The pre-fix matrix, re-derived at Issue 3.1 and written to `BASELINE.json`.

    Generated, never typed. It is a *snapshot of the same corpus under the pre-fix
    classifier*, which is what makes "FP non-increasing" checkable without a literal.
    """
    import json
    return json.loads((FIXTURES / "BASELINE.json").read_text())


def test_precision_does_not_regress():
    """`FP` non-increasing / `TN` non-decreasing against the generated baseline."""
    result = _score(_corpus())
    base = _baseline()
    print(f"\nclassifier corpus (re-derived): TP={result['TP']} FP={result['FP']} "
          f"TN={result['TN']} FN={result['FN']} n={result['n']}")
    print(f"pre-fix baseline (generated):   TP={base['TP']} FP={base['FP']} "
          f"TN={base['TN']} FN={base['FN']} n={base['n']}")
    for line in result["detail"]:
        print(f"  {line}")
    assert result["n"] == base["n"], (
        "the corpus changed size since the baseline was generated — regenerate it "
        "(`--write-baseline`) and re-measure rather than comparing across corpora"
    )
    assert result["FP"] <= base["FP"], (
        f"PRECISION REGRESSION: FP rose from {base['FP']} to {result['FP']}. "
        f"{result['detail']}"
    )
    assert result["TN"] >= base["TN"], (
        f"TN fell from {base['TN']} to {result['TN']}"
    )


# ------------------------------------------------------------------ structural pins


def _write_plan(tmp_path: Path, body: str) -> Path:
    d = tmp_path / "plan-xxx"
    d.mkdir(parents=True, exist_ok=True)
    (d / "plan.md").write_text(body)
    return d


SCANNED_BODY = """
## Epics

### Epic 1: Do the thing
- Issue 1.1: Adjust a configuration value.

## Upstream Issues

| Issue | Title | Disposition |
| :-- | :-- | :-- |

## Success Criteria

| # | Criterion | Verification |
| :-- | :-- | :-- |
| SC1 | It works | `true` |
"""


def test_f1_title_is_out_of_scan_region(tmp_path):
    """F1 (Issue 3.3): a trigger verb in the H1 is not a claim about the plan's work."""
    plan = _write_plan(tmp_path, "---\n---\n# Plan: Deploy and release the widget\n"
                       + SCANNED_BODY)
    got = pm._classify_deliverable(plan)
    assert got["suggested_class"] == "standard", (
        f"H1 trigger words leaked into the scan region: signals={got['signals']}"
    )


def test_f1_scanned_sections_still_match(tmp_path):
    """The complement of the pin above: in-region text must still be scanned."""
    plan = _write_plan(tmp_path, "---\n---\n# Plan: Adjust a value\n\n## Epics\n\n"
                       "### Epic 1: Ship it\n- Issue 1.1: Cut a signed release "
                       "and publish it.\n" + SCANNED_BODY.split("## Upstream")[0])
    got = pm._classify_deliverable(plan)
    assert got["suggested_class"] == "ci-release", (
        "an in-region release/sign claim produced no suggestion — the scan region is "
        f"too narrow: signals={got['signals']}"
    )


def test_f5_code_spans_and_fences_are_not_claims(tmp_path):
    """SC5b / F5 (Issue 3.4b): two documents identical except for backticks.

    A plan that writes a trigger word inside a command, a regex, or a quoted example is
    not thereby announcing that it ships releases.
    """
    bare = _write_plan(tmp_path / "bare", "---\n---\n# Plan: T\n\n## Epics\n\n"
                       "### Epic 1: E\n- Issue 1.1: Grep the log for release lines.\n")
    wrapped = _write_plan(tmp_path / "wrapped", "---\n---\n# Plan: T\n\n## Epics\n\n"
                          "### Epic 1: E\n- Issue 1.1: Grep the log for `release` "
                          "lines.\n")
    bare_sig = pm._classify_deliverable(bare)["signals"]
    wrapped_sig = pm._classify_deliverable(wrapped)["signals"]
    assert "release" in bare_sig, (
        f"control failed — the unwrapped document should signal: {bare_sig}"
    )
    assert "release" not in wrapped_sig, (
        f"a backticked token was scored as a claim: {wrapped_sig}"
    )


def test_f5_fenced_block(tmp_path):
    """F5, fenced-block half of the pin."""
    plan = _write_plan(tmp_path, "---\n---\n# Plan: T\n\n## Epics\n\n### Epic 1: E\n"
                       "- Issue 1.1: Run the check below.\n\n"
                       "```bash\ngh release list --repo foo/bar\n```\n")
    got = pm._classify_deliverable(plan)
    assert "release" not in got["signals"], (
        f"a fenced code block was scored as prose: {got['signals']}"
    )


# --------------------------------------------------------------- contract shape


def test_result_reports_an_evidence_basis(tmp_path):
    """F4 (Issue 3.5): `evidence` distinguishes path-backed from prose-only."""
    plan = _write_plan(tmp_path, "---\n---\n# Plan: T\n\n## Epics\n\n### Epic 1: E\n"
                       "- Issue 1.1: Cut a signed release.\n")
    prose = pm._classify_deliverable(plan)
    assert prose["evidence"] == "prose-only", prose
    assert prose["confidence"] == "low", (
        f"a prose-only match reported confidence={prose['confidence']} — `high` is "
        "reserved for the path marker, which is the only non-prose signal"
    )

    backed = pm._classify_deliverable(plan, (".github/workflows/release.yml",))
    assert backed["evidence"] == "path-backed", backed
    assert backed["confidence"] == "high", backed


def test_low_only_match_does_not_suggest_ci_release(tmp_path):
    """F3 (Issue 3.2): a ci-release suggestion requires a high-tier signal."""
    plan = _write_plan(tmp_path, "---\n---\n# Plan: T\n\n## Epics\n\n### Epic 1: E\n"
                       "- Issue 1.1: Update the deploy runner workflow notes.\n")
    got = pm._classify_deliverable(plan)
    assert got["suggested_class"] == "standard", (
        f"low-tier keywords alone produced a ci-release suggestion: {got}"
    )
    assert got["signals"], (
        "low-tier matches must still be REPORTED as informational, not discarded"
    )


def test_negative_context_guards(tmp_path):
    """F2 (Issue 3.4): the demonstrated collisions are suppressed."""
    for phrase in ("Install a self-signed certificate.",
                   "Regenerate the signed certificate for the host.",
                   "Track the upstream release cadence.",
                   "Fix the metrics pipeline.",
                   "The service is deployed by ansible."):
        plan = _write_plan(tmp_path / re.sub(r"\W+", "-", phrase)[:24],
                           "---\n---\n# Plan: T\n\n## Epics\n\n### Epic 1: E\n"
                           f"- Issue 1.1: {phrase}\n")
        got = pm._classify_deliverable(plan)
        assert got["suggested_class"] == "standard", (
            f"negative context not guarded for {phrase!r}: {got}"
        )


if __name__ == "__main__":
    if "--write-baseline" in sys.argv:
        # Issue 3.1: re-derive the PRE-FIX matrix over the vendored corpus and record
        # it. Run once, against the unmodified classifier. Never hand-edit the output.
        import json
        snap = _score(_corpus())
        snap.pop("detail")
        (FIXTURES / "BASELINE.json").write_text(json.dumps(snap, indent=2) + "\n")
        print(f"wrote BASELINE.json: {snap}")
        sys.exit(0)
    sys.exit(pytest.main([__file__, "-v", "-s"]))
