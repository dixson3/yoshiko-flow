#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Machine-read a `plan.md` into JSON: the epic/issue DAG, gates, criteria, upstream rows.

**Why this exists.** `plan_manager.py` is ~4800 lines and contains ZERO parses of
`### Epic N:` or `- Issue N.M:`. The epic/issue DAG — the thing the document exists to
express — had exactly one consumer: an LLM freehanding `bd create` calls at SKILL.md §5.2a.
Pour fidelity was checked by nobody. Measured over 43 comparable plans, **17 carried a pour
divergence**: 885 declared dependency edges against 860 in `bd`, 45 dropped and 20 invented.
A dropped `blocks` edge means the coordinator marked a bead ready *before its declared
predecessor*.

**The governing rule: FAIL LOUDLY, NEVER DEGRADE (plan-047 Issue 5.1).** Every construct this
parser cannot read lands in `unparsed[]` with its line number and the reason. EXP-003's
prototype silently corrupted its own fidelity number **four times** before each widening was
found — a parser that quietly drops what it does not understand produces a number that looks
like a measurement and is not one.

## The grammar is ANCHORED, and that is load-bearing

The prototype matched dependencies with an unanchored search:

    DEPENDS = re.compile(r'depends[- ]on:\\s*(?P<val>.+?)\\s*$', re.I)

Run against plan-047 itself, that reports two dependency edges **that do not exist**. Issue
5.2's body contains the literal ``(`2.5 depends-on: 2.6, 2.7` — correct execution order,
inverted numbering)`` — inside an inline code span, quoting *another* issue's edge as a parser
hazard to test for. The unanchored search reads it and attributes 2.6 and 2.7 to Issue **5.2**.

So keys are matched only in their canonical bullet position, and inline code spans are masked
before any key match. Both hazards are in the test set.

Usage:

    uv run _shared/plan_extract.py <plan.md> [...] [--json] [--strict]

`--strict` exits 1 if any input produced an `unparsed[]` entry.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

# --- grammar (REQ-DATA-019 + the SKILL.md "Epics and Gates grammar" block) --------------

H2 = re.compile(r"^## +(.+?)\s*$")
H3 = re.compile(r"^### +(.+?)\s*$")

# An epic heading. Bold and an em-dash separator are tolerated because the historical corpus
# contains both; a LETTERED epic (`### Epic B:`) is also accepted and flagged, since plan-012
# used letters and the normalizer's letter->numeric rewrite is Issue 8.5's subject.
EPIC = re.compile(r"^### +(?:\*\*)?Epic +([0-9]+|[A-Z])(?:\*\*)?\s*[:—-]\s*(.+?)\s*$")

# An issue bullet at COLUMN 0 of the `## Epics` body. Canonical form only; anything else that
# looks like a list item in that section is reported as `unparsed`, never guessed at.
# The id may be LETTERED (`A.1`, `B.3`) as well as numeric. Plans 012-017 used lettered
# epics, and rejecting that form is not strictness — it is a silent loss of six plans from
# every downstream join. The letter form is extracted and FLAGGED (`lettered`); converting
# it is the normalizer's job (Issue 8.5), not the reader's.
# READING-grammar widening (plan-048 Issue 1.3, REQ-DATA-019). A title parenthetical
# before the colon — `- Issue 1.6 (firing surface): …` — is recovered: the parenthetical
# never carries an id, so dropping it from the id is unambiguous.
ISSUE = re.compile(r"^- +(?:\*\*)?(?:Issue +)?(?P<id>[0-9]+|[A-Z])\.(?P<sub>[0-9]+[a-z]?)"
                   r"(?:\*\*)?(?P<paren>\s*\([^)]*\))?\s*:\s*(?P<rest>.*)$")

# A sub-key written at COLUMN 0 instead of two-space-indented. Recovered by attaching it to
# the immediately preceding issue bullet — no other referent is possible.
COL0_SUBKEY = re.compile(r"^- +(depends-on|resolves-upstream|touches)\s*:\s*(?P<val>.*)$", re.I)

# Noise-word prefixes inside a `Blocks:` referent. `Issue 5.1` and `5.1` are the same
# referent; the prefix (singular or plural) carries no information.
_ISSUE_PREFIX = re.compile(r"^Issues?\s+(?P<rest>.+)$", re.I)
_EPIC_PREFIX = re.compile(r"^Epics?\s+(?P<rest>[0-9]+|[A-Z])$", re.I)

# Sub-keys are TWO-SPACE-INDENTED bullets under their issue. Anchored: `^ {2}- key:`.
SUBKEY = re.compile(r"^ {2}- +(depends-on|resolves-upstream|touches)\s*:\s*(?P<val>.*)$", re.I)

# TRAILING-INLINE sub-key (REQ-DATA-052, plan-049 Issue 2.1). The declaration is written at
# the END of an issue bullet, or of one of its two-space continuation lines, instead of as
# its own bullet:
#
#     - Issue 1.3: Frontmatter parser over embedded `SKILL.md`s; group computation and
#       transitive closure with cross-group logging. depends-on: 1.2
#     - Issue 1.5: Add `templates/manifest.md`. (depends-on: 1.2)
#
# THIS IS THE DARK MATTER. Measured across the corpus: 89 such declarations in 5 plans, read
# by NOTHING and counted by NOTHING — plan-006 and plan-007 reported `0 unparsed, 0 edges`
# while carrying 20 declarations between them, so the residue metric recorded the loss as
# perfection. That population is larger than the entire write-phase migration this plan was
# originally scoped around, and recovering it modifies ZERO documents.
#
# Anchored to END OF LINE deliberately. A declaration with prose after it cannot be attributed
# without guessing where the referent list stops, and REQ-DATA-052 requires the grammar to
# REFUSE rather than guess. An optional wrapping paren is tolerated because 12 of the 89 are
# written `(depends-on: 1.1, 1.6)`.
TRAILING_SUBKEY = re.compile(
    r"(?P<open>\()?\b(?P<key>depends-on|resolves-upstream)\s*:\s*(?P<val>[^()]*?)\s*"
    r"(?(open)\)|)\s*$", re.I)

# A gate field. Anchored to a bullet so gate prose cannot be read as a field.
GATE_FIELD = re.compile(
    r"^- +\*{0,2}(Type|Approvers|Condition|Test|Blocks|Instructions)\*{0,2}\s*:\s*(?P<val>.*)$",
    re.I)

ISSUE_ID = re.compile(r"^(?:[0-9]+|[A-Z])\.[0-9]+[a-z]?$")
EPIC_REF = re.compile(r"^epic:([0-9]+|[A-Z])$", re.I)
UPSTREAM_ROW = re.compile(r"#(\d+)")
REQ_ID = re.compile(r"\bREQ-[A-Z0-9]+-[0-9]+[a-z]?\b")
FILE_LINE = re.compile(r"([\w./\-]+\.(?:py|md|rs|toml|sh|json|yaml|yml)):(\d+)")
CRITERION_ID = re.compile(r"^SC[0-9]+[a-z]?$")

RECONCILE_SENTINEL = "reconcile step"


def natural_key(issue_id: str) -> tuple:
    """Sort key for an issue id. `6.10` sorts AFTER `6.2` — lexically it does not.

    Issue 5.2 names this as a required test case: the corpus contains ids that sort wrongly
    under a plain string comparison, and an extractor that emits them in lexical order hands
    the comparator a DAG whose edges look reordered.
    """
    m = re.match(r"^(\d+|[A-Z])\.(\d+)([a-z]?)$", issue_id)
    if not m:
        return (999, 999, "", issue_id)
    head = m.group(1)
    # Lettered epics sort after numeric ones; within each family, numerically.
    return ((0, int(head)) if head.isdigit() else (1, ord(head)),
            int(m.group(2)), m.group(3), issue_id)


def mask_inline_code(line: str) -> str:
    """Blank out `inline code spans`, preserving length so column offsets still line up.

    This is the fix for the prototype's headline defect: a `depends-on:` quoted inside an
    inline code span is DOCUMENTATION, not a declaration.
    """
    return re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), line)


def _subkey_value_verbatim(raw: str) -> str:
    """The sub-key's value, taken from the UNMASKED line by splitting on its first colon.

    NOT an offset slice of the match's `val` group, and the difference is load-bearing. The
    match ran against `mask_inline_code(raw)`, where a backticked term is blanked to a run of
    spaces — so the pattern's whitespace run after the colon GREEDILY SWALLOWS the first
    backticked value. Measured on plan-052: every `touches:` list lost its FIRST path, and a
    single-path list came back EMPTY (13 of 31 issues), while `--strict` still reported
    `unparsed: []` and exit 0. That is the same silent-corruption shape #186 found in titles,
    reached by a different route: there the masked text was captured, here the masked text
    moved the offsets.

    Splitting on the first colon is safe because the key (`depends-on`, `resolves-upstream`,
    `touches`) contains none.
    """
    _, sep, rest = raw.partition(":")
    return rest.strip() if sep else ""


def _verbatim(raw: str, m: "re.Match[str]", group) -> str:
    """The `group` span of `m`, read from the UNMASKED source line (REQ-DATA-062, #186).

    `m` was matched against `mask_inline_code(raw)`. That masking is CORRECT for parsing — a
    `depends-on:` inside an inline code span is documentation, not a declaration — and is
    preserved. But a title captured from the masked line has every backticked term blanked to
    spaces, so `plan_extract` emitted corrupt titles while `--strict` reported `unparsed: []`
    and exit 0, and §5.2a poured that corruption straight into the bead DAG.

    The capture is an OFFSET SLICE, never a re-match of `ISSUE`/`EPIC` against `raw`.
    `mask_inline_code` is length-preserving by construction (it substitutes a run of spaces of
    the same width), so the match offsets are valid in `raw` — that guarantee is what makes the
    slice correct, and it is the only reason this form is safe.

    The naive alternative — matching the pattern against `raw` — was MEASURED at plan-050's
    pass 10 producing a spurious edge to a nonexistent target and driving `--strict` non-zero,
    because a `depends-on:` written inside a code span becomes visible to `try_trailing` again.
    Every other consumer keeps matching against the masked line; only the title reads `raw`.
    """
    start, end = m.start(group), m.end(group)
    if start < 0:
        return ""
    return raw[start:end].strip()


def _split_h2(lines: list[str]) -> dict[str, tuple[int, int]]:
    """`{h2 title: (start, end)}` over body lines, fence-aware."""
    out: dict[str, tuple[int, int]] = {}
    cur, start, fenced = None, 0, False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = H2.match(ln)
        if m:
            if cur is not None:
                out[cur] = (start, i)
            cur, start = m.group(1), i + 1
    if cur is not None:
        out[cur] = (start, len(lines))
    return out


def _fence_indents(lines: list[str]) -> dict[int, int]:
    """Map each line inside an **indented** fenced block to that fence's opening indent.

    REQ-DATA-063 as amended by plan-053 (#206), drop shape 2. Returns only the lines belonging
    to a fence whose OPENING delimiter is indented — the CommonMark rule: an indented opening
    fence is list-item continuation, a **column-0** fence is document content.

    THE COLUMN-0 EXCLUSION IS LOAD-BEARING, NOT AN OPTIMISATION. What terminates an issue's
    continuation is an epic `###`, any other `###`, a column-0 `- ` bullet, or the end of
    `## Epics` — **a column-0 fence terminates nothing**. So a "collect every fenced line"
    variant attributes a plan-body fence written after the last issue to that issue, and it
    lands in the issue's BEAD DESCRIPTION. Measured: fixing #206 naively introduces a new
    silent-corruption shape while closing an old one. `ctl-206-dropped-continuation`'s fifth
    assertion is the guard.

    The recorded value is the opening fence's indent so the caller can strip exactly that much
    and no more, leaving INTERNAL indentation intact — a code block whose leading whitespace is
    normalised away is no longer the block the author wrote.
    """
    out: dict[int, int] = {}
    indent: int | None = None
    for i, ln in enumerate(lines):
        stripped = ln.lstrip()
        if stripped.startswith("```"):
            if indent is None:
                lead = len(ln) - len(stripped)
                # A column-0 fence is plan body. Enter a "skip" state (indent < 0) so its
                # CLOSING delimiter is still consumed and does not open a spurious block.
                indent = lead if lead > 0 else -1
                if indent > 0:
                    out[i] = indent
            else:
                if indent > 0:
                    out[i] = indent
                indent = None
            continue
        if indent is not None and indent > 0:
            out[i] = indent
    return out


def _fenced_spans(lines: list[str]) -> set[int]:
    inside, fenced = set(), False
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("```"):
            fenced = not fenced
            inside.add(i)
            continue
        if fenced:
            inside.add(i)
    return inside


# A GFM cell separator is an UNESCAPED pipe. `\|` inside a cell is a literal pipe and
# must not split it — a naive `.split("|")` shifts every later cell in the row left by
# one, which silently misreads the columns rather than failing (plan-048 Issue 1.1).
_CELL_SPLIT = re.compile(r"(?<!\\)\|")


def _split_row(inner: str) -> list[str]:
    """Split one table row's interior into cells, honouring GFM-escaped pipes."""
    return [c.strip().replace("\\|", "|") for c in _CELL_SPLIT.split(inner)]


def _table_rows(lines: list[str]) -> list[list[str]]:
    rows = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("|") and s.endswith("|"):
            rows.append(_split_row(s[1:-1]))
    return rows


def classify_test(value: str, fenced: bool) -> str:
    """`executable` | `fenced` | `sentinel` — what kind of `Test:` this is."""
    v = value.strip().strip("`").strip()
    if fenced:
        return "fenced"
    if not v or v.lower() in {"none", "n/a", "na", "-", "_(none)_", "*(none)*"}:
        return "sentinel"
    return "executable"


def extract(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    fenced_lines = _fenced_spans(lines)
    fence_indents = _fence_indents(lines)
    h2 = _split_h2(lines)
    unparsed: list[dict] = []

    def bad(i: int, reason: str, raw: str) -> None:
        unparsed.append({"line": i + 1, "reason": reason, "raw": raw[:200]})

    # Every construct the READING grammar recovered from a non-canonical form, with the
    # before/after pair. This is what makes a recovery AUDITABLE (plan-048 Issue 1.4b /
    # SC1b): a recovered edge that nobody can inspect is indistinguishable from an
    # invented one.
    recovered: list[dict] = []

    def rec(i: int, cls: str, before: str, after: str) -> None:
        recovered.append({"line": i + 1, "class": cls,
                          "before": before[:200], "after": after[:200]})

    # --- header fields -----------------------------------------------------------------
    def field(name: str) -> str | None:
        m = re.search(rf"^\*\*{name}:\*\*\s*(.+?)\s*$", text, re.M)
        return m.group(1).strip() if m else None

    # --- ## Epics ----------------------------------------------------------------------
    epics: list[dict] = []
    issues: list[dict] = []
    edges: list[dict] = []
    cur_epic: dict | None = None
    cur_issue: dict | None = None

    def handle_subkey(key: str, val: str, col0: bool, val_verbatim: str | None = None) -> None:
        """One implementation for both the canonical two-space form and the
        recovered column-0 form, so the two can never diverge."""
        if key == "touches":
            # plan-052 Issue 1.4 (REQ-DATA-071). `- touches:` becomes a FIRST-CLASS field so
            # single-writer ownership is measurable at authoring time. Consumed here — and so
            # excluded from `detail` on the same grounds as the other two sub-keys: the same
            # bytes must not be reachable both as a structured field and as prose.
            #
            # Deliberately NOT all-or-nothing, unlike `depends-on`. That rule exists because a
            # half-recovered EDGE LIST silently reorders execution; a path list materializes no
            # edge and drives no ordering, so refusing the whole declaration over one odd entry
            # would discard good data to protect an invariant this field does not have.
            if col0:
                rec(i, "col0-subkey", raw.strip(), f"  - touches: {val}")
            # READ THE VALUE VERBATIM (REQ-DATA-062's rule, applied to this field). The match
            # ran against `mask_inline_code(raw)`, where every backticked term is blanked to a
            # run of spaces — and a `touches:` value is ENTIRELY backticked paths, so the
            # masked value is whitespace and the field silently came back empty on every
            # issue. Masking is still correct for PARSING; it is only the captured text that
            # must come from the unmasked source.
            src = val_verbatim if val_verbatim is not None else val
            for q in src.split(","):
                q = q.strip().strip("`").strip("*").strip()
                if q and q not in cur_issue["touches"]:
                    cur_issue["touches"].append(q)
            return
        if key == "depends-on":
            parts = [q.strip().strip("`").strip("*") for q in val.split(",")
                     if q.strip()]
            # ALL-OR-NOTHING (plan-048 Issue 1.4a). If ANY referent is
            # unrecoverable, materialize NO edge from this declaration. Recovering
            # the readable half of an ambiguous list produces a half-complete edge
            # list, which is strictly worse than recovering none: a missing edge is
            # visible in `unparsed[]`, whereas a partial one looks complete and
            # silently reorders execution.
            bad_refs = [q for q in parts if not ISSUE_ID.match(q)]
            if bad_refs:
                for q in bad_refs:
                    bad(i, f"depends-on referent {q!r} is not an issue id "
                           "(a prose tail is forbidden — REQ-DATA-019); the whole "
                           "declaration is refused, not partially recovered", raw)
                return
            if col0:
                rec(i, "col0-subkey", raw.strip(), f"  - depends-on: {val}")
            for q in parts:
                cur_issue["depends_on"].append(q)
                edges.append({"from": cur_issue["id"], "to": q,
                              "kind": "depends-on", "line": i + 1})
        else:
            if col0:
                rec(i, "col0-subkey", raw.strip(), f"  - resolves-upstream: {val}")
            for num in UPSTREAM_ROW.findall(val):
                d = re.search(r"\((\w+)\)", val)
                cur_issue["resolves_upstream"].append(
                    {"issue": f"#{num}", "disposition": d.group(1) if d else None})

    def try_trailing(i: int, raw: str, ln: str) -> bool:
        """RECOVERED (plan-049 Issue 2.1, REQ-DATA-052): the TRAILING-INLINE form.

        Called from exactly two places — the issue bullet itself, and a two-space
        continuation of it — so attribution is never a guess: those are the only lines
        physically part of the issue. A column-0 bullet ends the issue's body and an epic
        heading clears `cur_issue`, so nothing else is ever in scope.

        Returns True when the line WAS a trailing declaration — recovered OR refused — so the
        caller stops processing it.
        """
        if cur_issue is None:
            return False
        m = TRAILING_SUBKEY.search(ln)
        if not m:
            return False
        key = m.group("key").lower()
        val = m.group("val").strip()
        before = raw.strip()
        n_before = (len(cur_issue["depends_on"]), len(cur_issue["resolves_upstream"]))
        handle_subkey(key, val, col0=False)
        n_after = (len(cur_issue["depends_on"]), len(cur_issue["resolves_upstream"]))
        # `handle_subkey` reports its own refusal into `unparsed[]`. Only a SUCCESSFUL
        # recovery is auditable, so `rec()` is keyed on an edge actually materialising — a
        # before/after pair for a refused construct would claim a recovery that never
        # happened, which is the one thing an audit trail must not do.
        if n_after != n_before:
            rec(i, "trailing-inline-subkey", before, f"  - {key}: {val}")
        return True

    def _collect_detail(raw: str, consumed: bool) -> None:
        """Append one continuation line to the current issue's `detail` (REQ-DATA-063).

        `consumed` is True when `try_trailing` already read a TRAILING-INLINE declaration off
        the end of this line. The declaration text is then stripped, because the same bytes
        must not be reachable BOTH as a structured edge and as prose — that exclusion is what
        makes `detail` a schema field rather than a raw-text dump, and it is the same reason
        the `- depends-on:` / `- resolves-upstream:` BULLET forms never reach here at all
        (they are matched and consumed by `SUBKEY` / `COL0_SUBKEY` above).
        """
        if cur_issue is None:
            return
        text = raw.strip()
        if consumed:
            text = TRAILING_SUBKEY.sub("", text).strip()
        if text:
            cur_issue["detail_lines"].append(text)

    def _collect_fence_line(raw: str, indent: int) -> None:
        """Append one INDENTED-fence continuation line VERBATIM (REQ-DATA-063, #206).

        Exempt from `_collect_detail`'s `strip()` by design: this is the one capture path
        where whitespace is content. Only the OPENING fence's indent is removed, so a line
        indented more deeply than its fence keeps the difference.

        A blank line inside a fence is preserved as a blank line — `_collect_detail` drops
        falsy text, which would silently close up the blank lines in a code block.
        """
        if cur_issue is None:
            return
        cur_issue["detail_lines"].append(raw[indent:].rstrip("\n") if len(raw) > indent
                                         else raw.strip())


    if "Epics" in h2:
        s, e = h2["Epics"]
        for i in range(s, e):
            raw = lines[i]
            if i in fenced_lines:
                # REQ-DATA-063 (#206), drop shape 2. An INDENTED fence under an open issue is
                # that issue's continuation and is collected VERBATIM, minus the opening
                # fence's own indent. Previously EVERY fenced line was skipped, so the whole
                # block vanished while `--strict` reported `unparsed: []` and exit 0.
                #
                # `_fence_indents` yields only indented-fence lines, so a COLUMN-0 fence still
                # falls through to the `continue` below and is never collected — the guard
                # against the new corruption shape a naive fix introduces.
                indent = fence_indents.get(i)
                if indent is not None and cur_issue is not None:
                    _collect_fence_line(raw, indent)
                continue
            ln = mask_inline_code(raw)

            m = EPIC.match(ln)
            if m:
                cur_epic = {"num": m.group(1), "name": _verbatim(raw, m, 2),
                            "lettered": not m.group(1).isdigit(), "line": i + 1,
                            "issue_ids": []}
                epics.append(cur_epic)
                cur_issue = None
                continue
            if H3.match(ln) and not m:
                # An H3 inside ## Epics that is not an epic heading. Deliberately-not-poured
                # epics (plan-041's "MOVED to plan-042") land here — D-12 requires an explicit
                # marker rather than a silent drop.
                bad(i, "H3 inside ## Epics is not an epic heading", raw)
                cur_epic, cur_issue = None, None
                continue

            m = ISSUE.match(ln)
            if m:
                if cur_epic is None:
                    bad(i, "issue bullet outside any epic", raw)
                    continue
                iid = f'{m.group("id")}.{m.group("sub")}'
                if m.group("paren"):
                    rec(i, "title-parenthetical",
                        f'Issue {iid}{m.group("paren").strip()}', f"Issue {iid}")
                cur_issue = {"id": iid, "lettered": not m.group("id").isdigit(),
                             "title": _verbatim(raw, m, "rest"),
                             "epic": cur_epic["num"], "line": i + 1,
                             "detail_lines": [],
                             "depends_on": [], "resolves_upstream": [], "touches": []}
                issues.append(cur_issue)
                cur_epic["issue_ids"].append(cur_issue["id"])
                # ...and a declaration written at the END OF THE BULLET ITSELF.
                try_trailing(i, raw, ln)
                continue

            m = SUBKEY.match(ln)
            if m:
                if cur_issue is None:
                    bad(i, "sub-key bullet with no owning issue", raw)
                    continue
                handle_subkey(m.group(1).lower(), m.group("val").strip(), col0=False,
                              val_verbatim=_subkey_value_verbatim(raw))
                continue

            # RECOVERED (plan-048 Issue 1.3): a sub-key written at column 0 instead of
            # two-space-indented. It attaches to the immediately preceding issue bullet —
            # no other referent is possible — so the form is unambiguous.
            m = COL0_SUBKEY.match(ln)
            if m:
                if cur_issue is None:
                    bad(i, "sub-key bullet with no owning issue", raw)
                    continue
                handle_subkey(m.group(1).lower(), m.group("val").strip(), col0=True,
                              val_verbatim=_subkey_value_verbatim(raw))
                continue

            # A two-space continuation of the current issue — and ONLY that, FOR THE
            # PURPOSE OF READING A DECLARATION. A more deeply nested list item belongs to
            # its own sub-list, and attributing its DECLARATION to the issue is precisely
            # the mis-attribution REQ-DATA-052 forbids.
            if re.match(r"^ {2}(?![ \t*-])\S", ln):
                consumed = try_trailing(i, raw, ln)
                _collect_detail(raw, consumed)
                continue

            # REQ-DATA-063 (#187). Any OTHER indented line under an open issue is that
            # issue's continuation PROSE: a nested bullet, a table row, a deeper-indented
            # paragraph. It is collected into `detail` and nothing else — no declaration is
            # ever read from it, so REQ-DATA-052's attribution rule is untouched. Before
            # this, such a line was dropped silently and `--description` had nothing to
            # carry: 35 of 35 beads poured from one plan came out with empty descriptions
            # on a DAG that was otherwise perfect.
            # THE OPERAND IS `raw`, NOT THE MASKED `ln` — REQ-DATA-063 (#206), drop shape 1.
            #
            # A continuation line whose entire visible content is ONE INLINE CODE SPAN masks
            # to whitespace, so `^\s+\S` finds no non-space character on `ln` and the line is
            # dropped SILENTLY while `--strict` still reports `unparsed: []` and exit 0.
            #
            # This widens CAPTURE and CANNOT widen PARSING. The branch is capture-only: it
            # calls `_collect_detail(raw, False)` and returns. It never calls `try_trailing`
            # and matches no `ISSUE` / `EPIC` / `SUBKEY` / `COL0_SUBKEY` pattern — every one
            # of those branches sits ABOVE this line and still tests `ln`. So a `depends-on:`
            # written inside a code span still produces no edge (REQ-DATA-062's companion
            # assertion), and `ctl-206-dropped-continuation` asserts exactly that.
            if cur_issue is not None and re.match(r"^\s+\S", raw):
                _collect_detail(raw, False)
                continue

            # Anything else at column 0 that looks like a list item in ## Epics.
            # Reported REGARDLESS of whether an issue is open: a column-0 bullet is never a
            # continuation (continuations are two-space indented), so one appearing after an
            # issue bullet is a non-conformant construct, not that issue's body. An earlier
            # version guarded on `cur_issue is None` and therefore silently dropped every
            # such bullet that followed an issue — which is the degrade-quietly behaviour
            # this parser exists to not have.
            if re.match(r"^- +\S", ln):
                bad(i, "column-0 bullet in ## Epics is not a conformant issue bullet", raw)
                cur_issue = None

    # --- ## Gates ----------------------------------------------------------------------
    gates: list[dict] = []
    if "Gates" in h2:
        s, e = h2["Gates"]
        cur_gate: dict | None = None
        pending_test: bool = False
        for i in range(s, e):
            raw = lines[i]
            m = H3.match(raw) if i not in fenced_lines else None
            if m:
                cur_gate = {"name": m.group(1).strip(), "line": i + 1, "type": None,
                            "condition": None, "test": None, "test_kind": None,
                            "blocks": [], "blocks_raw": None, "instructions": None}
                gates.append(cur_gate)
                pending_test = False
                continue
            if cur_gate is None:
                continue

            # A `Test:` whose value is empty and whose next content is a fenced block —
            # 4 plans (037, 038, 042, 046) do this. A one-physical-line parser mis-reads them.
            if pending_test and raw.lstrip().startswith("```"):
                body, j = [], i + 1
                while j < e and not lines[j].lstrip().startswith("```"):
                    body.append(lines[j])
                    j += 1
                cur_gate["test"] = "\n".join(body).strip()
                cur_gate["test_kind"] = classify_test(cur_gate["test"], fenced=True)
                pending_test = False
                continue

            if i in fenced_lines:
                continue
            gm = GATE_FIELD.match(raw)
            if gm:
                key, val = gm.group(1).lower(), gm.group("val").rstrip()
                pending_test = False
                # MULTI-LINE VALUES (Issue 5.2): plan-040 L360's parenthetical wraps across
                # two physical lines, putting the colon on a continuation line. A value
                # continues while following lines are indented and are not a new field.
                j = i + 1
                while (j < e and lines[j].strip()
                       and not GATE_FIELD.match(lines[j])
                       and not H3.match(lines[j])
                       and lines[j].startswith(("  ", "\t"))):
                    val += " " + lines[j].strip()
                    j += 1
                if key == "type":
                    cur_gate["type"] = val.strip().split()[0].lower() if val.strip() else None
                elif key == "condition":
                    cur_gate["condition"] = val.strip()
                elif key == "instructions":
                    cur_gate["instructions"] = val.strip()
                elif key == "test":
                    if not val.strip():
                        pending_test = True
                    else:
                        cur_gate["test"] = val.strip().strip("`")
                        cur_gate["test_kind"] = classify_test(val, fenced=False)
                elif key == "blocks":
                    cur_gate["blocks_raw"] = val.strip()
                    # Resolve every referent FIRST, then commit — all-or-nothing
                    # (plan-048 Issue 1.4a). A `Blocks:` list with one unreadable referent
                    # is refused whole: `Blocks: Epics 2, 3, 4` recovers `epic:2` from the
                    # prefixed token but `3` and `4` are bare numbers whose epic-ness is an
                    # INFERENCE from the neighbouring token, not a property of the token.
                    # Committing the first and dropping the rest would leave a gate blocking
                    # one epic instead of three — a half-complete edge list that reads as
                    # complete.
                    resolved: list[dict] = []
                    refused: list[str] = []
                    # Recoveries are STAGED, not logged as they are found. A `Blocks:` value
                    # is refused WHOLE, so logging a per-token recovery before the whole
                    # value is known would claim a recovery that never materialized — the
                    # half-complete hazard, relocated into the audit log. Measured: 6 of 43
                    # staged recoveries sat inside values that were ultimately refused.
                    staged: list[tuple[str, str, str]] = []
                    for tok in [p.strip() for p in val.split(",") if p.strip()]:
                        t = tok.strip("`").strip().strip("*").strip()
                        if ISSUE_ID.match(t):
                            resolved.append({"kind": "issue", "ref": t})
                            continue
                        if EPIC_REF.match(t):
                            resolved.append({"kind": "epic",
                                             "ref": EPIC_REF.match(t).group(1)})
                            continue
                        if t.lower() == RECONCILE_SENTINEL:
                            resolved.append({"kind": "sentinel", "ref": t.lower()})
                            continue
                        # RECOVERED class A: an `Issue`/`Issues` noise-word prefix.
                        pm = _ISSUE_PREFIX.match(t)
                        if pm and ISSUE_ID.match(pm.group("rest").strip()):
                            ref = pm.group("rest").strip()
                            staged.append(("blocks-issue-prefix", t, ref))
                            resolved.append({"kind": "issue", "ref": ref})
                            continue
                        # RECOVERED class B: `Epic N` / `Epics N` -> `epic:N`.
                        em = _EPIC_PREFIX.match(t)
                        if em:
                            ref = em.group("rest").strip()
                            staged.append(("blocks-epic-ref", t, f"epic:{ref}"))
                            resolved.append({"kind": "epic", "ref": ref})
                            continue
                        refused.append(t)
                    if refused:
                        for t in refused:
                            bad(i, f"Blocks referent {t!r} is outside the REQ-DATA-019 "
                                   "alphabet (issue-id | epic:<N> | 'reconcile step'); the "
                                   "whole Blocks value is refused, not partially recovered",
                                raw)
                    else:
                        cur_gate["blocks"].extend(resolved)
                        for cls_, b_, a_ in staged:
                            rec(i, cls_, b_, a_)

    # --- ## Success Criteria / ## Risks & Mitigations -----------------------------------
    def table_of(section: str) -> list[list[str]]:
        if section not in h2:
            return []
        s, e = h2[section]
        return _table_rows(lines[s:e])

    criteria: list[dict] = []
    rows = table_of("Success Criteria")
    for r in rows[2:] if len(rows) > 2 else []:
        cid = r[0].strip().strip("*")
        if not CRITERION_ID.match(cid):
            criteria.append({"id": None, "raw_id": r[0].strip(), "malformed": True})
            continue
        criteria.append({
            "id": cid,
            "criterion": r[1] if len(r) > 1 else "",
            "verification": r[2] if len(r) > 2 else "",
            "discharged_by": [x.strip() for x in (r[3] if len(r) > 3 else "").split(",")
                              if x.strip()],
        })

    risks: list[dict] = []
    rows = table_of("Risks & Mitigations")
    for r in rows[2:] if len(rows) > 2 else []:
        risks.append({"id": r[0].strip().strip("*"),
                      "risk": r[1] if len(r) > 1 else "",
                      "severity": r[2] if len(r) > 2 else "",
                      "mitigation": r[3] if len(r) > 3 else ""})

    upstream: list[dict] = []
    rows = table_of("Upstream Issues")
    for r in rows[2:] if len(rows) > 2 else []:
        m = UPSTREAM_ROW.search(r[0])
        upstream.append({"issue": f"#{m.group(1)}" if m else r[0].strip(),
                         "title": r[1] if len(r) > 1 else "",
                         "disposition": (r[2] if len(r) > 2 else "").strip().strip("*"),
                         "resolved_by": [x.strip() for x in (r[4] if len(r) > 4 else "")
                                         .split(",") if x.strip()]})

    # --- dangling-edge check ------------------------------------------------------------
    known = {i["id"] for i in issues}
    for ed in edges:
        if ed["to"] not in known:
            unparsed.append({"line": ed["line"],
                             "reason": f"depends-on target {ed['to']!r} is not a declared "
                                       "issue in this plan",
                             "raw": f"{ed['from']} -> {ed['to']}"})
    for g in gates:
        for b in g["blocks"]:
            if b["kind"] == "issue" and b["ref"] not in known:
                unparsed.append({"line": g["line"],
                                 "reason": f"gate {g['name']!r} Blocks undeclared issue "
                                           f"{b['ref']!r}",
                                 "raw": g["blocks_raw"] or ""})

    # REQ-DATA-063 (#187): materialise `detail` from the collected continuation lines. The
    # working list is dropped so the emitted object carries ONE representation, not two.
    # An issue whose only continuation was its sub-key bullets carries an EMPTY `detail`,
    # which is a valid value and not an error — 0 of 35 continuation bullets on plan-050
    # itself carry prose, and that is a negative observation rather than a failure.
    for _i in issues:
        _i["detail"] = "\n".join(_i.pop("detail_lines", []))

    return {
        "path": str(path),
        "plan_id": field("ID"),
        "status": field("Status"),
        "epic_bead": field("Epic"),
        "fingerprint": field("Fingerprint"),
        "epics": epics,
        "issues": sorted(issues, key=lambda x: natural_key(x["id"])),
        "issue_order_declared": [i["id"] for i in issues],
        "edges": edges,
        "gates": gates,
        "criteria": criteria,
        "risks": risks,
        "upstream": upstream,
        "reqs": sorted(set(REQ_ID.findall(text))),
        "file_refs": sorted({f"{a}:{b}" for a, b in FILE_LINE.findall(text)}),
        "counts": {"epics": len(epics), "issues": len(issues), "edges": len(edges),
                   "gates": len(gates), "criteria": len(criteria), "risks": len(risks),
                   "upstream": len(upstream), "unparsed": len(unparsed),
                   "recovered": len(recovered)},
        "unparsed": unparsed,
        # Every non-canonical construct the READING grammar normalized, before/after.
        # Emitted so a recovery can be AUDITED rather than trusted (SC1b).
        "recovered": recovered,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Extract a plan.md into JSON.")
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                    help="Skip inputs whose path matches GLOB. Repeatable. THE "
                         "SELF-EXCLUSION LEVER (#135): a plan measuring the corpus must not "
                         "count itself, or the literals it writes go stale the moment it "
                         "edits them. The excluded set is REPORTED, never silently dropped.")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="Exit 2 (INCONCLUSIVE) if any input produced an `unparsed` entry. "
                         "NOT 1 \u2014 see REQ-DATA-043: an unparsed construct means this "
                         "instrument could not read the plan, which is not the same claim as "
                         "the plan being wrong.")
    a = ap.parse_args()
    out, excluded = [], []
    for p in a.paths:
        pm = p / "plan.md" if p.is_dir() else p
        if any(fnmatch.fnmatch(str(pm), g) or fnmatch.fnmatch(str(pm.parent), g)
               or fnmatch.fnmatch(pm.parent.name, g) for g in a.exclude):
            excluded.append(str(pm))
            continue
        if not pm.is_file():
            out.append({"path": str(pm), "error": "no plan.md"})
            continue
        out.append(extract(pm))
    if excluded and not a.json:
        # REPORTED, never silent. An exclusion nobody can see is indistinguishable from an
        # input that was never supplied, which is how a denominator quietly shrinks.
        print(f"excluded {len(excluded)} input(s) by --exclude: "
              + ", ".join(Path(x).parent.name for x in excluded))
    if a.json:
        print(json.dumps(out, indent=1))
    else:
        for d in out:
            if "error" in d:
                print(f"{d['path']}: {d['error']}")
                continue
            c = d["counts"]
            print(f"{Path(d['path']).parent.name}: {c['epics']} epics, {c['issues']} issues, "
                  f"{c['edges']} edges, {c['gates']} gates, {c['criteria']} criteria, "
                  f"{c['unparsed']} unparsed")
            for u in d["unparsed"]:
                print(f"    L{u['line']}: {u['reason']}")
    if a.strict:
        # REQ-DATA-043: an unparsed construct means the extractor DID NOT SEE part of the
        # plan, so every downstream conclusion is drawn from a knowably incomplete DAG.
        # Exit 2 = INCONCLUSIVE ("this instrument could not read the plan"), which is a
        # different claim from exit 1 = FAIL ("the plan is wrong"). A caller that collapses
        # the two has not implemented this requirement.
        blocked = [d for d in out if d.get("counts", {}).get("unparsed")]
        if blocked:
            for d in blocked:
                name = Path(d["path"]).parent.name
                print(f"INCONCLUSIVE: {name} has {d['counts']['unparsed']} unparsed "
                      f"construct(s); the extracted DAG is incomplete.", file=sys.stderr)
                for u in d["unparsed"]:
                    print(f"    L{u['line']}: {u['reason']}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
