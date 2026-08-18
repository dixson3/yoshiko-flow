# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
# ]
# ///
"""Mechanical enforcement of the yf-herdr launch + observation contract (REQ-HERDR-015/026).

Run from anywhere:  uv run skills/yf-herdr/scripts/test_launch_contract.py

WHY THIS FILE EXISTS
--------------------
Before plan-045, `yf-herdr` shipped **no scripts and no test suite**, and the only
CHANGE-VALIDATION id its paths could reach was `frontmatter` — a check that passes whatever
the launch recipe says. So the skill's central artifact, the prompt it sends a subordinate,
had no mechanical check of any kind. This file is that skill's first one.

The defect it exists to catch was measured, not hypothesised: the launch recipe was a bare

    herdr agent prompt "<name>" "/yf-plan execute <plan-id>"

while the fix for the resulting behaviour lived as advisory prose under `## Observe` —
"If autonomy is wanted, say so explicitly" — read *after* the prompt was already composed.
A parent following the recipe literally produced the stop-after-every-epic behaviour the
skill's own trap warned about. REQ-HERDR-015 makes the three prompt elements mandatory;
this test is what makes "mandatory" mean something.

THE ENUMERATION IS FROM SOURCE
------------------------------
Assertions parse `SKILL.md` rather than hardcoding an expected prompt string. A hardcoded
expected prompt verifies today's wording and is silent on tomorrow's rewrite — which is the
edit that would actually reintroduce the defect. Each requirement is checked as "some line in
the Launch section satisfies this predicate", so the prose may be reworded freely and only a
*removal* fails.

SCOPE RULES
-----------
* **Block boundary** — the `## Launch` heading to the next `## ` heading. The autonomy
  directive must live in Launch, not in Observe: living in Observe is precisely the
  measured defect, so a test that accepted it anywhere in the file would pass on the
  broken arrangement.
* **Push contract** — the trigger classes are checked in the Observe section, where
  REQ-HERDR-026 places them. The `--wait` prohibition is checked **file-wide**, because a
  `--wait` in the push path is a defect wherever it appears.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_SKILL_DIR = _HERE.parent
_SKILL_MD = _SKILL_DIR / "SKILL.md"
_SPEC_MD = _SKILL_DIR / "SPEC.md"


def _section(heading_prefix: str, text: str) -> str:
    """Extract a `## ` section: from its heading to the next `## ` heading."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.startswith(heading_prefix):
            start = i
            break
    assert start is not None, f"no {heading_prefix!r} heading found in SKILL.md"
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end])


@pytest.fixture(scope="module")
def skill_md() -> str:
    assert _SKILL_MD.is_file(), f"missing {_SKILL_MD}"
    return _SKILL_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def launch(skill_md: str) -> str:
    return _section("## Launch", skill_md)


@pytest.fixture(scope="module")
def observe(skill_md: str) -> str:
    return _section("## Observe", skill_md)


# ---------------------------------------------------------------------------------------
# REQ-HERDR-015 (a) — the autonomy directive
# ---------------------------------------------------------------------------------------

_AUTONOMY_RE = re.compile(
    r"(run\s+to\s+completion|without\s+waiting|continue\s+without|autonom)",
    re.IGNORECASE,
)


def test_launch_carries_an_autonomy_directive(launch: str) -> None:
    """REQ-HERDR-015(a): the launch prompt instructs the subordinate to run to completion."""
    assert _AUTONOMY_RE.search(launch), (
        "the `## Launch` section carries no autonomy directive. REQ-HERDR-015 makes it "
        "mandatory prompt content: a subordinate launched without it stops after every "
        "epic. Advisory prose under `## Observe` does NOT satisfy this — that arrangement "
        "is the measured defect, because it is read after the prompt is composed."
    )


def test_autonomy_directive_names_the_stop_condition(launch: str) -> None:
    """An unbounded 'never stop' is not the contract — stopping at declared gates is."""
    assert re.search(r"gate", launch, re.IGNORECASE), (
        "the autonomy directive must bound itself by the plan's declared gates. "
        "'Run to completion' with no stop condition instructs the subordinate to run "
        "past the human gates the plan exists to preserve."
    )


# ---------------------------------------------------------------------------------------
# REQ-HERDR-015 (c) — the parent handle
# ---------------------------------------------------------------------------------------

def test_launch_seeds_the_parent_handle_via_env(launch: str) -> None:
    """REQ-HERDR-015(c): `YF_PARENT_PANE` is seeded with `--env` on `tab create`."""
    assert "YF_PARENT_PANE" in launch, (
        "the `## Launch` section never mentions YF_PARENT_PANE. Without the parent handle "
        "the subordinate cannot push at all — it does not know the parent exists."
    )
    assert re.search(r"--env\s+YF_PARENT_PANE", launch), (
        "YF_PARENT_PANE must be seeded via `--env` on `tab create` so it reaches the agent "
        "process and its grandchildren; naming it in prose alone does not export it."
    )


def test_parent_handle_prefers_pane_id_over_agent_name(launch: str) -> None:
    """REQ-HERDR-015: the pane id is stable; an agent name goes stale on rename."""
    assert "HERDR_PANE_ID" in launch, (
        "the parent handle must be the parent's PANE ID ($HERDR_PANE_ID), which is injected "
        "automatically and is stable. An agent name exists only for `agent start`-ed agents "
        "and goes stale on rename."
    )


def test_mandatory_prompt_content_survives_compaction(launch: str) -> None:
    """REQ-HERDR-015: the three elements also go via `--append-system-prompt`."""
    assert "--append-system-prompt" in launch, (
        "the three mandatory elements must also be passed via `-- --append-system-prompt` "
        "so they survive the subordinate's context compaction. A long plan compacts away "
        "an ordinary prompt; the autonomy contract must outlive that."
    )


# ---------------------------------------------------------------------------------------
# REQ-HERDR-015 (b) / REQ-HERDR-026 — the push contract
# ---------------------------------------------------------------------------------------

def test_launch_carries_the_push_contract(launch: str) -> None:
    """REQ-HERDR-015(b): the launch prompt states when the subordinate pushes."""
    assert re.search(r"herdr\s+agent\s+prompt", launch), (
        "the `## Launch` section must show the subordinate the push command it is expected "
        "to use. A push contract the child cannot execute is not a contract."
    )
    assert re.search(r"epic", launch, re.IGNORECASE), (
        "the push contract must name its trigger classes; epic completion is the "
        "highest-volume one (REQ-HERDR-026)."
    )


def test_push_triggers_are_enumerated_and_exclude_per_bead(observe: str) -> None:
    """REQ-HERDR-026: three trigger classes, and explicitly never per bead."""
    for token in ("epic", "block", "complet"):
        assert re.search(token, observe, re.IGNORECASE), (
            f"the Observe section does not name the {token!r} push trigger class "
            "(REQ-HERDR-026 fixes exactly three: epic completion, blocker/failed gate/halt, "
            "and plan completion or abort)."
        )
    assert re.search(r"never\s+per\s+bead|not\s+per\s+bead", observe, re.IGNORECASE), (
        "the push contract must state that the subordinate never pushes per bead. A "
        "plan-sized DAG would emit tens of messages and flood the parent's context."
    )


def test_wait_is_forbidden_in_the_push_path(skill_md: str) -> None:
    """REQ-HERDR-026: `--wait` reintroduces lockstep and is measurably wrong for claude.

    Checked file-wide, not per-section: a `--wait` in the push path is a defect wherever
    it appears. A mention that *forbids* it is fine — what fails is a live invocation.
    """
    offenders = [
        line.strip()
        for line in skill_md.splitlines()
        if "--wait" in line
        and "herdr agent prompt" in line
        and not re.search(r"never|not\s|forbidden|do not|don't", line, re.IGNORECASE)
    ]
    assert not offenders, (
        "`--wait` appears in a live `herdr agent prompt` invocation: "
        f"{offenders!r}. It reintroduces the lockstep the push channel exists to remove, "
        "and `--wait --until idle` is measurably wrong for a claude subordinate, which "
        "settles at `done` and never at `idle` — so the wait times out on a turn that "
        "in fact completed."
    )


def test_push_is_paired_with_a_token_stamp(observe: str) -> None:
    """REQ-HERDR-026: `agent_prompted` is injection, not submission — pair with a token."""
    assert "report-metadata" in observe, (
        "every push must be paired with an idempotent `herdr pane report-metadata --token` "
        "stamp. `agent_prompted` acknowledges INJECTION, NOT SUBMISSION — one measured push "
        "returned success and was never submitted — so the token is the mechanical "
        "postcondition that makes the polling fallback a genuine backstop."
    )


# ---------------------------------------------------------------------------------------
# REQ-HERDR-026 — observation is push-primary, and the SPEC says so
# ---------------------------------------------------------------------------------------

def test_observation_is_push_primary_not_a_law_of_nature(observe: str) -> None:
    """REQ-HERDR-020/026: the not-continuous limit is a property of PULL, not observation."""
    assert re.search(r"push", observe, re.IGNORECASE), (
        "the Observe section never mentions pushing. It treats 'cannot watch continuously' "
        "as a law of nature — true for PULL, but the subordinate can speak."
    )


def test_spec_carries_the_reqs_this_test_enforces() -> None:
    """SPEC-first: the REQ ids must exist before the SKILL.md text implementing them."""
    assert _SPEC_MD.is_file(), f"missing {_SPEC_MD}"
    spec = _SPEC_MD.read_text(encoding="utf-8")
    for req in ("REQ-HERDR-015", "REQ-HERDR-026"):
        assert req in spec, (
            f"{req} is absent from yf-herdr/SPEC.md. This test enforces it, and the SPEC "
            "is fixed authority — a test asserting an unwritten requirement is the drift "
            "it exists to prevent."
        )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
