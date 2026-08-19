#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["click>=8.1", "pyyaml>=6"]
# ///
"""Tier-1 tests for the REQ-PORT-006 count disambiguation (plan-047 Issues 0.9b / 2.7).

The defect: `update-status <dir> review` and the create-on-present step BOTH emitted a
`- review:` bullet, so a **correct** bundle could show 2 bullets against 1 `pass-1.md` and
hard-fail `_audit_plan`. Reproduced on a scratch copy of plan-047's own bundle.

The fix: a presentation writes `- review-pass:`; a status transition keeps `- review:` and is
inert to the count, like `intake:` and `validated:`.

Run:  uv run skills/yf-plan/scripts/test_review_count.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plan_manager as pm  # noqa: E402

failures: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(name)


def bundle(tmp: Path, log_body: str, n_pass: int) -> Path:
    d = tmp / "plan-999-t-abc123"
    (d / "reviews").mkdir(parents=True)
    (d / "plan.md").write_text("# Plan: t\n\n**Status:** review\n\n## Objective\nt\n")
    (d / "log.md").write_text("# Log\n\n## 2026-01-01\n\n" + log_body)
    for i in range(1, n_pass + 1):
        (d / "reviews" / f"pass-{i}.md").write_text(f"# Pass {i}\n")
    return d


with tempfile.TemporaryDirectory() as td:
    t = Path(td)

    # 1. THE DEFECT: a status transition on top of presentations must not inflate the count.
    d = bundle(t / "a", "- review: entering review\n- review-pass: pass 1\n", 1)
    check("a `review:` status transition is inert to the count",
          pm._plan_review_line_count(d) == 1, f"got {pm._plan_review_line_count(d)}")

    d = bundle(t / "b", "- review: t1\n- review: t2\n- review-pass: p1\n- review-pass: p2\n", 2)
    check("...however many status transitions there are",
          pm._plan_review_line_count(d) == 2, f"got {pm._plan_review_line_count(d)}")

    # 2. A genuinely missing pass file must STILL be caught.
    d = bundle(t / "c", "- review-pass: p1\n- review-pass: p2\n", 1)
    check("a genuinely missing pass file is still caught",
          pm._plan_review_line_count(d) == 2, "expected 2 presentations against 1 file")

    # 3. A plan in `review` with no presentation yet expects ZERO — this used to hard-fail.
    d = bundle(t / "d", "- review: entering review\n", 0)
    check("in `review` with no presentation yet expects 0",
          pm._plan_review_line_count(d) == 0, f"got {pm._plan_review_line_count(d)}")

    # 4. LEGACY bundles (no `review-pass:` marker at all) keep their current numbers.
    #    The fix is forward-looking by design: the two events are indistinguishable in a
    #    legacy history, and an inferred count is worse than the status quo.
    d = bundle(t / "e", "- review: p1\n- review: p2\n", 2)
    check("a legacy bundle falls back to the `review:` count",
          pm._plan_review_line_count(d) == 2, f"got {pm._plan_review_line_count(d)}")

    d = bundle(t / "f", "- review: p1\n", 0)
    check("...but a legacy bundle with NO pass files expects 0, not 1",
          pm._plan_review_line_count(d) == 0,
          "the fallback must not manufacture a failure on a bundle that has no pass files")

    # 5. The token is a recognized NON-STATUS token: it never advances `status`.
    check("`review-pass:` is not a plan status",
          "review-pass" not in pm.VALID_STATUSES if hasattr(pm, "VALID_STATUSES") else True)

print(f"\n{len(failures)} failure(s)" if failures else "\nall passed")
sys.exit(1 if failures else 0)
