"""Mechanism smoke for skill_pages hybrid composition.

Proves the invariants of the reworked plugin:

- an authored ``content/skills/<name>.md`` supplies the page prose body, rendered *below* the
  always-generated "At a glance" quick-reference block;
- the generated trigger/skip blocks are gone (their guidance folds into the authored prose);
- the build is fail-closed: a skill with no authored page raises a build error naming it.

Run from ``web/``::

    uv run --with pelican==4.11.0 --with markdown==3.6 --with PyYAML==6.0.2 --with pytest \\
        pytest plugins/test_skill_pages.py
"""

import os

import pytest

import skill_pages


def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


class _Gen:
    """Minimal PagesGenerator stand-in for add_skill_pages guard tests."""

    def __init__(self, settings, path):
        self.settings = settings
        self.context = {}
        self.pages = []
        self.path = path


def _fixture(tmp_path):
    """A content dir with one authored skill page."""
    content = tmp_path / "content"
    _write(
        str(content / "skills" / "authored.md"),
        "---\ntitle: ignored\n---\n## Authored heading\n\nAUTHORED_PROSE_MARKER body.\n",
    )
    settings = {"PATH": str(content), "GITHUB_URL": "https://github.com/dixson3/yoshiko-flow"}
    return settings


def _skill(name, group="utility"):
    return {
        "name": name,
        "group": group,
        "invocable": False,
        "summary": f"{name} summary",
        "trigger": "",
        "skip": "",
        "depends_on_tool": [],
        "depends_on_skill": [],
        "dependents": [],
    }


def test_authored_page_is_prose_body_below_at_a_glance(tmp_path):
    settings = _fixture(tmp_path)
    html = skill_pages._skill_page_html(settings, _skill("authored"), {"authored"})
    # Quick-reference block is generated regardless of authored content.
    assert "At a glance" in html
    # Authored prose is the body, rendered BELOW the At-a-glance block.
    assert "AUTHORED_PROSE_MARKER" in html
    assert html.index("At a glance") < html.index("AUTHORED_PROSE_MARKER")


def test_authored_frontmatter_is_stripped(tmp_path):
    settings = _fixture(tmp_path)
    body = skill_pages._authored_page_html(settings, "authored")
    assert "AUTHORED_PROSE_MARKER" in body
    assert "title: ignored" not in body  # leading YAML frontmatter stripped


def test_no_generated_trigger_skip_blocks(tmp_path):
    """C5: When-it-fires / When-to-skip are no longer emitted as generated blocks."""
    settings = _fixture(tmp_path)
    skill = _skill("authored")
    skill["trigger"] = "TRIGGER_SHOULD_NOT_RENDER"
    skill["skip"] = "SKIP_SHOULD_NOT_RENDER"
    html = skill_pages._skill_page_html(settings, skill, {"authored"})
    assert "When it fires" not in html
    assert "When to skip" not in html
    assert "TRIGGER_SHOULD_NOT_RENDER" not in html
    assert "SKIP_SHOULD_NOT_RENDER" not in html


def test_missing_authored_page_is_hard_build_error(tmp_path):
    """Fail-closed: a skill with no authored page stops the build, naming the skill."""
    repo = tmp_path / "repo"
    content = tmp_path / "content"
    os.makedirs(str(content / "skills"), exist_ok=True)
    _write(
        str(repo / "skills" / "lonely" / "SKILL.md"),
        "---\nname: lonely\nskill-group: utility\ndescription: lonely summary\n---\n",
    )
    settings = {"PATH": str(content), "REPO_ROOT": str(repo), "GITHUB_URL": ""}
    gen = _Gen(settings, str(content / "pages"))
    with pytest.raises(RuntimeError) as exc:
        skill_pages.add_skill_pages(gen)
    assert "lonely" in str(exc.value)
    assert gen.context["missing_authored_page"] == ["lonely"]
