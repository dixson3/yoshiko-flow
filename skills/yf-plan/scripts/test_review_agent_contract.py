# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
# ]
# ///
"""The review-agent contract, EXECUTED: REQ-AGENT-049 / -043 / -045 (plan-051, #165/#182/#184).

Run from anywhere:  uv run skills/yf-plan/scripts/test_review_agent_contract.py

WHY THIS FILE EXISTS
--------------------
`skills/yf-plan/spec/agents.md` had **0 of 26** exit-code-decidable `Verification:` clauses.
Corpus-wide the figure was **1 of 251** — and that one closes the loop by *naming a
CV-registered test*, not by being a runnable line. So three requirements about how the review
agents behave were specified in prose that nothing ran.

That is the M5 defect `dixson3/yoshiko-flow#165` names, and plan-051 lands three requirements
that would otherwise reproduce it inside the very plan that cites it. This file is what makes
them executable.

**Naming a `test_*.py` in a Verification line is NOT execution.** Thirty clauses in this
corpus already do that and it buys nothing mechanically. What makes these three different is
that each `Verification:` line is a **whole-line backticked command whose first conjunct runs
this file** — so the line is *run*, not read.

THE THREE PARTS, ALL REQUIRED
-----------------------------
For each REQ, in one parameterized test:

1. **the prose property the REQ declares** actually holds in the agent template it constrains;
2. **the meta-assertion** — the REQ id exists in the spec, and its `Verification:` line
   **names this test**. This is what makes the check non-rottable: delete or rename this file
   and the assertion fails rather than silently passing;
3. a **vacuity guard** — the parameterized case set must EQUAL the declared REQ set, so a spec
   reshape fails loudly instead of quietly checking nothing.

SET ASSERTIONS, NEVER COUNTS
----------------------------
Per plan-051 Issue 3.3's rule, taken from measurement: `REQ-CLI-006` drifted **three times**
as a count and **zero** times as a set equality. Every assertion below names the specific
elements on each side.

Template: `test_cli_enumeration.py` / `uv-yf-cli-enum` — the one clause in 251 that closes the
loop, followed here verbatim in structure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_SKILL_DIR = _HERE.parent
_AGENTS_SPEC = _SKILL_DIR / "spec" / "agents.md"
_SKILL_MD = _SKILL_DIR / "SKILL.md"
_RED_TEAM = _SKILL_DIR / "agents" / "red-team.md"
_REVIEWER = _SKILL_DIR / "agents" / "reviewer.md"

# DERIVED from this file's own name, never hardcoded. A hardcoded literal would keep the
# meta-assertion GREEN after the file was RENAMED — the check would then be asserting that the
# spec names a test that no longer exists, which is the exact rot it exists to prevent, one
# level up. SC9's rename arm is only falsifiable because this line derives.
_THIS_TEST = Path(__file__).name

# The declared REQ set. The vacuity guard below asserts the parameterized case set EQUALS it.
_DECLARED: set[str] = {"REQ-AGENT-049", "REQ-AGENT-043", "REQ-AGENT-045"}

# Shared wording. Both amended REQs carve out the same two properties, which is D-8: rewording
# only the red-team would leave the two agents contradicting each other on one constraint.
_SCOPED_READ_ONLY = "Read-only with respect to the repository under review"
_SPIKE_AUTHORIZED = "A sandbox spike is authorized"


def _req_block(req: str) -> str:
    """The text of one REQ, from its id line to the next `REQ-` line."""
    text = _AGENTS_SPEC.read_text(encoding="utf-8")
    start = text.find(f"\n{req}:")
    assert start != -1, (
        f"{req} does not exist in {_AGENTS_SPEC.name}. A REQ this test parameterizes over "
        "must be present — its absence is drift, not a reason to skip."
    )
    # Search from AFTER this REQ's own id line — otherwise the very first match is the REQ
    # itself at offset 0 and every block parses EMPTY, which `test_the_spec_is_parseable_at_all`
    # exists to catch (and did, on the first run of this file).
    head = text.index("\n", start + 1) + 1
    nxt = re.search(r"^REQ-[A-Z]+-\d+:", text[head:], re.M)
    return text[start + 1: head + nxt.start()] if nxt else text[start + 1:]


def _verification_line(req: str) -> str:
    line = next(
        (ln for ln in _req_block(req).splitlines() if ln.startswith("Verification:")), ""
    )
    assert line, f"{req} has no `Verification:` line at all."
    return line


def _review_section() -> str:
    """SKILL.md's `### Review` section, HTML comments stripped.

    SECTION-SCOPED, NEVER WHOLE-FILE. Measured: `grep -q 'Agent' SKILL.md` exits 0 on the
    un-fixed tree, because `Agent` sits in the frontmatter `allowed-tools:` list — so a
    whole-file assertion ships unable to fail. Comments are stripped so a commented-out token
    cannot satisfy anything.
    """
    lines = _SKILL_MD.read_text(encoding="utf-8").split("\n")
    start = next((i for i, l in enumerate(lines) if l.strip() == "### Review"), None)
    assert start is not None, "SKILL.md has no `### Review` heading — the shape changed."
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("### ")), len(lines)
    )
    return re.sub(r"<!--.*?-->", "", "\n".join(lines[start:end]), flags=re.S)


# --- part 1: the prose property each REQ declares -----------------------------------------

def _check_049() -> None:
    """The adversarial pass is DISPATCHED as a sub-agent, not performed by the main session."""
    section = _review_section()
    assert "Agent" in section, (
        "REQ-AGENT-049: SKILL.md's `### Review` section does not name `Agent`. The section is "
        "where the adversarial pass is specified; naming the dispatch mechanism anywhere else "
        "(the frontmatter, Phase 2) does not specify THIS pass."
    )
    assert "Spawn a sub-agent" in section, (
        "REQ-AGENT-049: the `### Review` section names no imperative dispatch form. A bare "
        "`Agent` token is GREEN on `<!-- Agent -->` and on 'Do NOT use the Agent tool here', "
        "so the token alone cannot carry the requirement."
    )
    assert "agents/red-team.md" in section, (
        "REQ-AGENT-049: the `### Review` section dispatches without naming "
        "`agents/red-team.md` as the prompt — a dispatch to nothing in particular."
    )


def _check_agent_carve_out(path: Path, req: str) -> None:
    body = path.read_text(encoding="utf-8")
    assert _SCOPED_READ_ONLY in body, (
        f"{req}: {path.name} does not scope read-only to the repository under review. It "
        f"must carry the exact phrase {_SCOPED_READ_ONLY!r}, which is what REQ's own "
        "`Verification:` line greps for — an unscoped 'never writes files' is the "
        "over-broad reading #182 exists to correct."
    )
    assert _SPIKE_AUTHORIZED in body, (
        f"{req}: {path.name} does not authorize the sandbox spike. It must carry the exact "
        f"phrase {_SPIKE_AUTHORIZED!r}. The rule never forbade building something in a "
        "scratch directory and running it; leaving that unsaid is the under-specification "
        "#182 names."
    )


_PROSE_CHECKS = {
    "REQ-AGENT-049": _check_049,
    "REQ-AGENT-043": lambda: _check_agent_carve_out(_RED_TEAM, "REQ-AGENT-043"),
    "REQ-AGENT-045": lambda: _check_agent_carve_out(_REVIEWER, "REQ-AGENT-045"),
}


@pytest.mark.parametrize("req", sorted(_DECLARED))
def test_review_agent_requirement_holds(req: str) -> None:
    """One case per REQ: the declared prose property, plus the non-rottability meta-assertion.

    Both halves live in one case deliberately. A REQ whose property holds but whose
    `Verification:` line no longer names this test is a check that has quietly detached from
    the thing it checks — which is the same M5 defect one level up.
    """
    # part 1 — the prose property
    _PROSE_CHECKS[req]()

    # part 2 — the meta-assertion that makes it non-rottable
    verification = _verification_line(req)
    assert _THIS_TEST in verification, (
        f"{req}'s `Verification:` line no longer names {_THIS_TEST}. Delete or rename this "
        "test and the requirement would silently stop being checked — a spec Verification "
        "that names only a hand-run command is prose shaped like a command (#165)."
    )
    body = verification[len("Verification: "):]
    assert body.startswith("`") and body.endswith("`") and "`" not in body[1:-1], (
        f"{req}'s `Verification:` line is not a WHOLE-LINE backticked command: {verification!r}. "
        "A value containing inner backticks is prose with code spans — readable, but nothing "
        "runs it."
    )


# --- part 3: the vacuity guards ------------------------------------------------------------

def test_the_case_set_equals_the_declared_req_set() -> None:
    """Guard the guard, as a SET — never as a count (Issue 3.3's rule).

    A count would pass on a parameterization that dropped `REQ-AGENT-045` and added a
    duplicate. SC8 requires three REQs across two agent files; a singular or silently-shrunk
    case set would discharge the criterion while covering less than it claims.
    """
    parameterized = set(_PROSE_CHECKS)
    assert parameterized == _DECLARED, (
        f"the parameterized case set has drifted from the declared REQ set. "
        f"Only in cases: {sorted(parameterized - _DECLARED)}; "
        f"only in declared: {sorted(_DECLARED - parameterized)}."
    )


def test_the_checks_span_both_agent_files() -> None:
    """SC8's other half: three REQs, and genuinely across BOTH agent templates.

    Asserted as a set of paths rather than a count, so collapsing both cases onto one file
    fails loudly instead of still reporting 'two'.
    """
    covered = {_RED_TEAM.name, _REVIEWER.name}
    assert covered == {"red-team.md", "reviewer.md"}
    for p in (_RED_TEAM, _REVIEWER):
        assert p.is_file(), f"{p} does not exist — the agent templates moved."


def test_the_spec_is_parseable_at_all() -> None:
    """A spec reshape must fail loudly rather than make every case above vacuous."""
    for req in sorted(_DECLARED):
        block = _req_block(req)
        assert len(block.strip()) > 80, (
            f"{req}'s block parsed to {len(block.strip())} chars — the spec's shape changed "
            "and this check has gone vacuous. Fix the parser, do not relax the assertion."
        )
        assert _verification_line(req)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
