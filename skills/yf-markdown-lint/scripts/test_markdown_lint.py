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

FIXTURES = Path(__file__).parent.parent / "fixtures"


def lint(tmp_path, text, rules):
    p = tmp_path / "t.md"
    p.write_text(text, encoding="utf-8")
    return ml.Linter(set(rules)).lint_file(p)


def lint_fixture(name, rules):
    return ml.Linter(set(rules)).lint_file(FIXTURES / name)


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


# --- ML003 title-strip (REQ-MDLINT-002a, #81): resolve on path only ---

def test_ml003_split_dest_title_double_quote():
    assert ml.split_dest_title('images/x.png "caption"') == ("images/x.png", '"caption"')


def test_ml003_split_dest_title_single_quote():
    assert ml.split_dest_title("images/x.png 'cap'") == ("images/x.png", "'cap'")


def test_ml003_split_dest_title_paren():
    assert ml.split_dest_title("images/x.png (cap)") == ("images/x.png", "(cap)")


def test_ml003_split_dest_no_title():
    assert ml.split_dest_title("images/x.png") == ("images/x.png", None)


def test_ml003_split_dest_angle_wrapped_with_title():
    assert ml.split_dest_title('<a b.png> "t"') == ("a b.png", '"t"')


def test_ml003_titled_image_resolves_on_path_only(tmp_path):
    # REQ-MDLINT-002a: the title must not be folded into the resolved target.
    (tmp_path / "images").mkdir()
    (tmp_path / "images" / "x.png").write_bytes(b"x")
    text = '# t\n\n![alt](images/x.png "a caption")\n'
    assert lint(tmp_path, text, ["ML003"]) == []


def test_ml003_still_flags_genuinely_missing_titled_target(tmp_path):
    # Stripping the title must not mask a truly broken path.
    text = '# t\n\n![alt](images/missing.png "a caption")\n'
    out = lint(tmp_path, text, ["ML003"])
    assert any(r == "ML003" for _, r, _ in out)


def test_ml003_titled_image_fixture_clean():
    # Regression fixture: ![alt](images/x.png "caption") resolves on images/x.png.
    assert lint_fixture("ml003_titled_image.md", ["ML003", "ML004"]) == []


# --- ML010: bare CriticMarkup in prose (REQ-MDLINT-006, #48) ---

def test_ml010_registered_in_all_rules():
    assert "ML010" in ml.ALL_RULES


def test_ml010_in_authoring_subset():
    # REQ-MDLINT-011: ML010 IS part of the on-edit authoring subset.
    subset = {"ML001", "ML002", "ML005", "ML006", "ML007", "ML008", "ML010"}
    assert "ML010" in subset


def test_ml010_registry_has_five_constructs():
    assert set(ml.CRITICMARKUP) == {
        "addition", "deletion", "substitution", "highlight", "comment"
    }
    # Only substitution requires a separator.
    assert ml.CRITICMARKUP["substitution"]["sep"] == "~>"
    assert all(
        m["sep"] is None
        for n, m in ml.CRITICMARKUP.items() if n != "substitution"
    )


@pytest.mark.parametrize("construct,name", [
    ("{++added++}", "addition"),
    ("{--removed--}", "deletion"),
    ("{~~old~>new~~}", "substitution"),
    ("{==marked==}", "highlight"),
    ("{>>note<<}", "comment"),
])
def test_ml010_flags_each_construct(tmp_path, construct, name):
    out = lint(tmp_path, f"# t\n\nsome {construct} prose\n", ["ML010"])
    assert len(out) == 1
    assert out[0][1] == "ML010"
    assert name in out[0][2]


def test_ml010_substitution_requires_separator(tmp_path):
    # {~~ ~~} without a ~> is not a substitution -> not flagged.
    assert lint(tmp_path, "# t\n\na {~~no arrow~~} b\n", ["ML010"]) == []


def test_ml010_exempts_inline_code(tmp_path):
    assert lint(tmp_path, "# t\n\nsee `{++x++}` here\n", ["ML010"]) == []


def test_ml010_exempts_fenced_block(tmp_path):
    assert lint(tmp_path, "# t\n\n```\n{++x++}\n{~~a~>b~~}\n```\n", ["ML010"]) == []


def test_ml010_fixture_flags_five_constructs():
    # Five bare constructs; code-span, fenced block, and no-arrow sub are exempt.
    out = lint_fixture("ml010_criticmarkup.md", ["ML010"])
    assert len(out) == 5
    assert {r for _, r, _ in out} == {"ML010"}
    assert {m.split(":")[0].replace("bare CriticMarkup ", "") for _, _, m in out} == {
        "addition", "deletion", "substitution", "highlight", "comment"
    }


# --- ML011: empty-alt image warning (REQ-MDLINT-007, #46) ---

def test_ml011_registered_in_all_rules():
    assert "ML011" in ml.ALL_RULES


def test_ml011_not_in_authoring_subset():
    # ML011 is a full-audit a11y rule, not part of the on-edit subset.
    subset = {"ML001", "ML002", "ML005", "ML006", "ML007", "ML008", "ML010"}
    assert "ML011" not in subset


def test_ml011_flags_empty_alt_image(tmp_path):
    out = lint(tmp_path, "# t\n\n![](images/x.png)\n", ["ML011"])
    assert len(out) == 1
    assert out[0][1] == "ML011"


def test_ml011_present_alt_is_clean(tmp_path):
    assert lint(tmp_path, "# t\n\n![described](images/x.png)\n", ["ML011"]) == []


def test_ml011_present_title_never_warns(tmp_path):
    # A present title blesses the print-caption convention even with empty alt.
    assert lint(tmp_path, '# t\n\n![](images/x.png "caption")\n', ["ML011"]) == []


def test_ml011_ignores_empty_text_link(tmp_path):
    # Empty-text LINK (no leading !) must never be flagged by ML011.
    assert lint(tmp_path, "# t\n\n[](images/x.png)\n", ["ML011"]) == []


def test_ml011_image_vs_link_discrimination_fixture():
    # Fixture has an empty-alt image, an empty-text link, and a normal link.
    out = lint_fixture("ml011_image_vs_link.md", ["ML011"])
    assert len(out) == 1
    assert out[0][1] == "ML011"


def test_ml011_empty_alt_fixture():
    out = lint_fixture("ml011_empty_alt.md", ["ML011"])
    assert len(out) == 1
    assert out[0][1] == "ML011"


# --- ML009: optional compile-check of renderable embedded source (d2) ---

import shutil  # noqa: E402  (local to the ML009 d2-dependent tests)

_HAS_D2 = shutil.which("d2") is not None


def test_ml009_registered_in_all_rules():
    assert "ML009" in ml.ALL_RULES


def test_ml009_not_in_authoring_subset():
    # The on-edit authoring subset (SKILL.md / MARKDOWN_LINT.md) must not shell out.
    subset = {"ML001", "ML002", "ML005", "ML006", "ML007", "ML008"}
    assert "ML009" not in subset


def test_fence_info_class_parsing():
    assert ml.fence_info_class("```d2") == "d2"
    assert ml.fence_info_class("   ~~~CSV") == "csv"
    assert ml.fence_info_class("```python {.numberLines}") == "python"
    assert ml.fence_info_class("```") == ""


def test_vendored_registry_consumed_by_rule():
    # The vendored region is live: the rule's compile-checkable set comes from it.
    assert ml.compile_checkable_fence_classes() == ["d2"]
    assert "d2" in ml.renderable_fence_classes()
    assert "csv" in ml.renderable_fence_classes()


def test_fence_compile_error_degrades_for_non_checkable_class():
    # csv is renderable but not compile_checkable -> never flagged, no shell-out.
    assert ml.fence_compile_error("csv", "x,y\n1,2\n") is None
    assert ml.fence_compile_error("python", "import os\n") is None


def test_ml009_clean_when_no_renderable_fence(tmp_path):
    text = "# t\n\n```python\nprint(1)\n```\n\n```csv\nx,y\n1,2\n```\n"
    assert lint(tmp_path, text, ["ML009"]) == []


@pytest.mark.skipif(not _HAS_D2, reason="d2 binary not installed")
def test_ml009_flags_broken_d2(tmp_path):
    text = "# t\n\n```d2\na -> -> )(\n```\n"
    out = lint(tmp_path, text, ["ML009"])
    assert len(out) == 1
    lineno, rule, msg = out[0]
    assert rule == "ML009"
    assert lineno == 3            # reported at the fence-open line
    assert "does not compile" in msg


@pytest.mark.skipif(not _HAS_D2, reason="d2 binary not installed")
def test_ml009_passes_valid_d2(tmp_path):
    text = "# t\n\n```d2\na -> b\n```\n"
    assert lint(tmp_path, text, ["ML009"]) == []


def test_ml009_degrades_without_d2(tmp_path, monkeypatch):
    # With d2 unavailable the rule must produce no findings (graceful degrade).
    monkeypatch.setattr(ml.shutil, "which", lambda _name: None)
    text = "# t\n\n```d2\na -> -> )(\n```\n"
    assert lint(tmp_path, text, ["ML009"]) == []


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
