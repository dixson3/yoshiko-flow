# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
#     "pyyaml",
#     "click",
# ]
# ///
"""SC28 / plan-056 Issue 2.4 — adding a member to a GROUPED index must not reparent the
previous group's children.

Run from anywhere:  uv run skills/yf-plan/scripts/test_index_members.py

THE BUG. `_ensure_index_lists_member` and `_ensure_index_lists_retrospective` located the
insertion point with `ln.startswith("- [")`, which matches **column-0 bullets only**. A yf
bundle index is GROUPED — a top-level member followed by its indented children:

    - [assets/](assets/) - the plan's own harness
      - [assets/redcheck.sh](assets/redcheck.sh) - the driven-red harness

so "the last bullet" resolved to the last GROUP HEADING rather than to the last bullet, and
the new entry was inserted BETWEEN that heading and its own children. Every child of the
final group was thereby reparented under the newly added member — silently, and in the one
file whose whole purpose is to orient a cold reader.

Red on plan-048, plan-049 and plan-050 at the time of writing: all three end in a group.

WHY THIS FILE AND NOT AN EXISTING ONE. The functions live in `plan_manager.py:784`, not in
`doc_lint.py`, so `_shared/test_doc_lint.py` is not their home — and that file is a
hand-rolled script with **zero** test functions, so it is not a valid pytest host for
anything (REQ-CLI-028).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("plan_manager", _HERE / "plan_manager.py")
pm = importlib.util.module_from_spec(_spec)
sys.modules["plan_manager"] = pm
_spec.loader.exec_module(pm)


GROUPED_INDEX = """---
okf_version: 0.2
---

# plan-999-fixture

> a fixture objective

- [plan.md](plan.md) - The plan of record.
- [log.md](log.md) - Newest-first update history.
- [findings/](findings/) - Investigation findings.
  - [findings/exp-001.md](findings/exp-001.md) - The first experiment.
  - [findings/exp-002.md](findings/exp-002.md) - The second experiment.
"""


def _bundle(tmp_path: Path, index: str = GROUPED_INDEX) -> Path:
    d = tmp_path / "plan-999-fixture"
    (d / "findings").mkdir(parents=True)
    (d / "index.md").write_text(index)
    (d / "plan.md").write_text("# p\n")
    (d / "log.md").write_text("# Log\n")
    (d / "findings" / "exp-001.md").write_text("# e\n")
    (d / "findings" / "exp-002.md").write_text("# e\n")
    return d


def _bullets(d: Path) -> list[str]:
    return [ln for ln in (d / "index.md").read_text().splitlines() if ln.lstrip().startswith("- [")]


def test_ensure_index_lists_member_indentation(tmp_path):
    """The new member lands AFTER the last bullet of ANY indentation.

    The pre-fix behaviour inserted it after `- [findings/](findings/)` — i.e. ABOVE that
    group's two children, which then read as children of the new entry.
    """
    d = _bundle(tmp_path)
    (d / "upstream-triage.md").write_text("# t\n")

    assert pm._ensure_index_lists_member(d, "upstream-triage.md") is True

    bullets = _bullets(d)
    assert any("upstream-triage.md" in b for b in bullets), "the member was not added at all"

    # THE INVARIANT: the new bullet is LAST, so nothing indented follows it.
    assert "upstream-triage.md" in bullets[-1], (
        "the new member is not the last bullet — the group's children now follow it and "
        "read as ITS children:\n" + "\n".join(bullets))

    # And it is at column 0: a member of the bundle, not a child of the previous group.
    assert bullets[-1].startswith("- ["), "the new member was indented into the previous group"

    # THE NON-VACUITY ARM: the group's children are still present, still indented, and still
    # in order. Without this, a fix that simply DELETED them would pass every check above.
    idx = [b for b in bullets if "exp-00" in b]
    assert len(idx) == 2 and all(b.startswith("  ") for b in idx), (
        "the group's children were lost or de-indented:\n" + "\n".join(bullets))
    assert bullets.index(idx[0]) < bullets.index(idx[1])


def test_ensure_index_lists_retrospective_indentation(tmp_path):
    """The retrospective helper carries the SAME defect and the same fix.

    Two call sites shared one wrong predicate. Fixing one and testing one is how a defect
    like this survives its own repair.
    """
    d = _bundle(tmp_path)
    (d / pm.RETROSPECTIVE_FILE).write_text("# r\n")

    assert pm._ensure_index_lists_retrospective(d) is True

    bullets = _bullets(d)
    assert pm.RETROSPECTIVE_FILE in bullets[-1], (
        "the retrospective is not the last bullet:\n" + "\n".join(bullets))
    assert bullets[-1].startswith("- [")
    assert len([b for b in bullets if "exp-00" in b]) == 2


def test_flat_index_is_unaffected(tmp_path):
    """A FLAT index (no groups) behaves exactly as before — the fix is not a rewrite.

    The old predicate was correct for this shape, which is why the bug went unnoticed: every
    fixture in the test suite was flat.
    """
    flat = """---
okf_version: 0.2
---

# plan-999-fixture

- [plan.md](plan.md) - The plan of record.
- [log.md](log.md) - Newest-first update history.
"""
    d = _bundle(tmp_path, index=flat)
    (d / "upstream-triage.md").write_text("# t\n")
    assert pm._ensure_index_lists_member(d, "upstream-triage.md") is True
    bullets = _bullets(d)
    assert len(bullets) == 3 and "upstream-triage.md" in bullets[-1]


def test_is_idempotent(tmp_path):
    """A second call adds nothing. The index is written on three lifecycle events
    (REQ-PLAN-081), so a non-idempotent insert would duplicate the entry each time."""
    d = _bundle(tmp_path)
    (d / "upstream-triage.md").write_text("# t\n")
    assert pm._ensure_index_lists_member(d, "upstream-triage.md") is True
    before = (d / "index.md").read_text()
    assert pm._ensure_index_lists_member(d, "upstream-triage.md") is False
    assert (d / "index.md").read_text() == before


def test_absent_member_is_not_listed(tmp_path):
    """A member that does not exist on disk is NOT added.

    git does not track empty directories, so listing a member absent from every clone
    asserts something false everywhere but the machine that made it — and generates the
    `empty-dir` drift `reindex` reports.
    """
    d = _bundle(tmp_path)
    assert pm._ensure_index_lists_member(d, "upstream-triage.md") is False
    assert not any("upstream-triage" in b for b in _bullets(d))


if __name__ == "__main__":
    # ARGUMENTS ARE FORWARDED (REQ-CLI-028).
    sys.exit(pytest.main([__file__, *sys.argv[1:]]))
