# /// script
# requires-python = ">=3.11"
# ///
"""Tests for markdown_lint.py — focused on ML008 (table alignment markers).

Run:  uv run --with pytest python3 -m pytest test_markdown_lint.py -q
"""
import importlib.util
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "markdown_lint", Path(__file__).parent / "markdown_lint.py"
)
ml = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ml)


def lint(tmp_path, text, rules):
    p = tmp_path / "t.md"
    p.write_text(text, encoding="utf-8")
    return ml.Linter(set(rules)).lint_file(p)


# --- ML008: every table column needs an explicit alignment marker ---

def test_ml008_bare_delimiter_flags_all_columns(tmp_path):
    out = lint(tmp_path, "# t\n\n| A | B |\n|---|---|\n| 1 | 2 |\n", ["ML008"])
    assert len(out) == 1
    assert out[0][1] == "ML008"
    assert "1, 2" in out[0][2]


def test_ml008_markers_present_is_clean(tmp_path):
    # left / center / right markers, varied dash counts (variable widths allowed)
    text = "# t\n\n| A | B | C |\n| :-- | :-: | ---: |\n| 1 | 2 | 3 |\n"
    assert lint(tmp_path, text, ["ML008"]) == []


def test_ml008_variable_dash_counts_allowed(tmp_path):
    # per-column dash counts differ (PDF width tuning) — must NOT be flagged
    text = "# t\n\n| A | B |\n| :-------- | --: |\n| 1 | 2 |\n"
    assert lint(tmp_path, text, ["ML008"]) == []


def test_ml008_partial_marker_flags_only_bare_column(tmp_path):
    out = lint(tmp_path, "# t\n\n| A | B | C |\n| :-- | --- | --: |\n| 1 | 2 | 3 |\n", ["ML008"])
    assert len(out) == 1
    assert out[0][2].startswith("table column 2 ") or "column 2" in out[0][2]


def test_ml008_ignores_delimiter_like_row_in_code_fence(tmp_path):
    text = "# t\n\n```\n| A | B |\n|---|---|\n```\n"
    assert lint(tmp_path, text, ["ML008"]) == []


def test_ml008_ignores_non_table_dashes(tmp_path):
    # a thematic break / non-table line is not a table delimiter
    assert lint(tmp_path, "# t\n\nsome text\n\n---\n\nmore\n", ["ML008"]) == []


def test_ml008_left_align_single_colon_clean(tmp_path):
    assert lint(tmp_path, "# t\n\n| A | B |\n| :--- | :--- |\n| 1 | 2 |\n", ["ML008"]) == []


# --- regression: ML005/ML007 still behave alongside ML008 ---

def test_ml005_cell_count_mismatch_still_flags(tmp_path):
    out = lint(tmp_path, "# t\n\n| A | B |\n| :-- | :-- |\n| 1 | 2 | 3 |\n", ["ML005"])
    assert any(r == "ML005" for _, r, _ in out)


def test_ml008_registered_in_all_rules():
    assert "ML008" in ml.ALL_RULES


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
