# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pytest>=8",
# ]
# ///
"""REQ-CLI-006 self-consistency: the spec enumeration IS the source (plan-045, drift #3).

Run from anywhere:  uv run skills/yf-plan/scripts/test_cli_enumeration.py

WHY THIS FILE EXISTS
--------------------
REQ-CLI-006 enumerates `plan_manager.py`'s flat subcommands. It has drifted **three times**:

1. it read ``10`` while the script carried ``21``;
2. plan-045 corrected it to ``23``, then to ``24`` when ``review-loop-check`` landed;
3. it was **still wrong at 25**, because ``retrospective-report`` was added in the *same
   epic* that fixed drift #2.

Each repair bumped a hardcoded literal — a fix that re-breaks on the very next verb. But the
third drift is the instructive one, and it is the reason this file exists rather than a
fourth literal:

    **It survived a full green sweep.** The FULL validation tier passed 33/33 while
    REQ-CLI-006's own ``Verification:`` line asserted something false — because that line was
    *prose shaped like a command*. Nothing ran it. A `grep` written in a spec is not a check;
    it is a description of a check that someone might run.

That is precisely the defect class `dixson3/yoshiko-flow#149` names — a process rule that
nothing executes — reproduced **inside the spec of the plan that cites #149**. A plan whose
thesis is "every stop must be mechanical, and an actor must report what it verified rather
than what it intended" shipped a spec assertion that was neither mechanical nor verified.

So the fix has two halves, and this file is the half that matters:

* REQ-CLI-006 is restated as a **set equality** (enumeration == source), which cannot go
  stale by arithmetic the way a count does; and
* that equality is **executed here**, registered as CHANGE-VALIDATION id ``uv-yf-cli-enum``
  and fired by edits to *both* ``skills/yf-plan/scripts/**`` and ``skills/yf-plan/spec/cli.md``
  — so adding a verb without amending the REQ fails at the point of the change, not three
  epics later at a review someone happened to do carefully.

THE ASSERTION IS SET EQUALITY, NOT A COUNT
------------------------------------------
Comparing counts would pass on a spec that lists 25 verbs of which one is misspelled and one
real verb is missing. The failure message names the specific verbs on each side, because
"expected 25, got 24" is the message that made the first three drifts tedious to diagnose.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
_SKILL_DIR = _HERE.parent
_PLAN_MANAGER = _HERE / "plan_manager.py"
_CLI_SPEC = _SKILL_DIR / "spec" / "cli.md"


def _source_verbs() -> set[str]:
    """Every `@cli.command`-decorated verb name in plan_manager.py.

    Handles both registration forms: `@cli.command("explicit-name")` and a bare
    `@cli.command()` whose name derives from the function. Group-registered subcommands
    (`@fingerprint.command`, `@worktree.command`, `@landing_lock.command`) are deliberately
    EXCLUDED — they are outside REQ-CLI-006's scope by construction, which is exactly why
    REQ-CLI-021 mandates the flat form for new verbs.
    """
    text = _PLAN_MANAGER.read_text(encoding="utf-8")
    verbs: set[str] = set()
    for m in re.finditer(r"^@cli\.command\((.*?)\)\s*$", text, re.M | re.S):
        arg = m.group(1).strip()
        literal = re.match(r'"([a-z0-9-]+)"', arg)
        if literal:
            verbs.add(literal.group(1))
            continue
        tail = text[m.end():m.end() + 800]
        fn = re.search(r"^def ([a-z0-9_]+)\(", tail, re.M)
        assert fn, f"could not resolve a name for a bare @cli.command() near offset {m.start()}"
        verbs.add(fn.group(1).replace("_", "-"))
    return verbs


def _spec_verbs() -> set[str]:
    """Every verb enumerated in REQ-CLI-006's own paragraph.

    Scoped to the REQ block (from `REQ-CLI-006:` to the following `Rationale:`) so that
    backticked verb names appearing elsewhere in cli.md — in other REQs, or in this REQ's
    Rationale narrating past drifts — cannot inflate the set.
    """
    text = _CLI_SPEC.read_text(encoding="utf-8")
    start = text.index("REQ-CLI-006:")
    end = text.index("Rationale:", start)
    block = text[start:end]

    enum_line = next(
        (ln for ln in block.splitlines() if ln.startswith("The enumeration")), None
    )
    assert enum_line, (
        "REQ-CLI-006 has no line starting 'The enumeration' — the parser and the spec have "
        "diverged in SHAPE, which this test cannot silently tolerate: a shape change that "
        "made the enumeration unparseable would turn this check vacuous."
    )
    verbs = set(re.findall(r"`([a-z][a-z0-9-]+)`", enum_line))
    # `REQ-CLI-021`-style cross-references are not verbs.
    return {v for v in verbs if not v.startswith("req-")}


def test_the_enumeration_is_parseable_at_all():
    """Guard the guard: a vacuous check is worse than none."""
    spec = _spec_verbs()
    assert len(spec) > 15, (
        f"only {len(spec)} verbs parsed out of REQ-CLI-006 — the enumeration format changed "
        "and this check has gone vacuous. Fix the parser, do not relax the assertion."
    )


def test_spec_enumeration_equals_source_commands():
    """REQ-CLI-006's normative invariant, executed.

    This is the whole point of the file. It has failed for real three times in this repo's
    history; the failure message is written for the person reading it at 2am.
    """
    source = _source_verbs()
    spec = _spec_verbs()

    missing_from_spec = sorted(source - spec)
    missing_from_source = sorted(spec - source)

    assert not missing_from_spec, (
        f"{len(missing_from_spec)} verb(s) exist in plan_manager.py but are ABSENT from "
        f"REQ-CLI-006's enumeration: {missing_from_spec}. "
        "Add them to the enumeration in skills/yf-plan/spec/cli.md. This is drift #4 of a "
        "REQ that has already drifted three times — each previous time because a verb was "
        "added without amending the spec."
    )
    assert not missing_from_source, (
        f"{len(missing_from_source)} verb(s) are enumerated in REQ-CLI-006 but do NOT exist "
        f"in plan_manager.py: {missing_from_source}. "
        "Either the verb was removed or renamed and the spec was not updated, or the "
        "enumeration has a typo."
    )
    assert source == spec


def test_the_stated_count_matches_the_enumeration():
    """The `currently N` convenience must not itself go stale.

    The count is derived, not normative — but a derived number that disagrees with the thing
    it derives from is exactly the artifact that made the first three drifts believable.
    """
    text = _CLI_SPEC.read_text(encoding="utf-8")
    start = text.index("REQ-CLI-006:")
    block = text[start:text.index("Rationale:", start)]
    m = re.search(r"currently \*\*(\d+)\*\*", block)
    assert m, "REQ-CLI-006 no longer states a 'currently **N**' count"
    stated = int(m.group(1))
    actual = len(_spec_verbs())
    assert stated == actual, (
        f"REQ-CLI-006 says 'currently {stated}' but its own enumeration lists {actual} verbs."
    )


def test_group_registered_subcommands_are_excluded():
    """Groups are outside the invariant — assert that exclusion is real, not assumed.

    If `@fingerprint.command`-style registrations ever leaked into `_source_verbs()`, the
    invariant would demand they be enumerated in a REQ that explicitly places them outside
    its scope, and the fix would be to add them to the spec — the wrong repair.
    """
    text = _PLAN_MANAGER.read_text(encoding="utf-8")
    group_cmds = re.findall(r"^@(\w+)\.command\(\"([a-z0-9-]+)\"\)", text, re.M)
    non_cli = {name for grp, name in group_cmds if grp != "cli"}
    assert non_cli, (
        "no group-registered subcommands found at all — either they were removed or the "
        "pattern changed, and this exclusion test has gone vacuous."
    )
    assert not (non_cli & _source_verbs()), (
        f"group-registered subcommands leaked into the flat set: "
        f"{sorted(non_cli & _source_verbs())}"
    )


def test_verification_line_names_an_executing_check():
    """The lesson, encoded: a spec Verification must not be prose shaped like a command.

    REQ-CLI-006's third drift survived a 33/33 green sweep because its `Verification:` line
    was a `grep` nobody ran. A Verification that names only a hand-run command is
    indistinguishable from one that names nothing.
    """
    text = _CLI_SPEC.read_text(encoding="utf-8")
    start = text.index("REQ-CLI-006:")
    block = text[start:text.index("REQ-CLI-012:", start)]
    verification = next(
        (ln for ln in block.splitlines() if ln.startswith("Verification:")), ""
    )
    assert "test_cli_enumeration.py" in verification, (
        "REQ-CLI-006's Verification line no longer names this executing test. A spec "
        "Verification that names only a hand-run grep is prose shaped like a command — "
        "which is how this REQ passed a full green sweep while asserting something false."
    )


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
