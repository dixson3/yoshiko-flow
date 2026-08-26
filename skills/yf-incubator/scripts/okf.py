#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""OKF engine — construct, manage, and conformance-check yf artifact bundles.

`yf-okf`'s canonical engine (SPEC `skills/yf-okf/SPEC.md`, REQ-OKF-*). Makes yf
artifact folders ("bundles") compatible with the Open Knowledge Format v0.1
(reserved `index.md` / `log.md`; a non-empty `type` on every non-reserved `.md`)
and layers the yoshiko-flow extensions on top (a dual **frontmatter + `**Field:**`**
field model, an `okf_spec:` member key, per-skill `OKF-EXTENSION.md` composition).

**Baked-in ruleset (REQ-OKF-FAM-002).** The machine-readable BASELINE + YF-EXTENSIONS
ruleset is encoded in the module-level constants below — the engine never reads
`spec/OKF-BASELINE.md` / `spec/OKF-YF-EXTENSIONS.md` at runtime. Those docs are the
authored spec, kept in agreement with these constants by a `yf-drift-check` edge.
Only the per-skill `OKF-EXTENSION.md` is resolved at runtime, and only
`__file__`-relative (REQ-OKF-FAM-003).

**Vendored (plan-016 `_shared/`).** This file is authored once as `_shared/okf.py`
(canonical) and copied **verbatim, whole-file** into each consuming skill's
`scripts/okf.py` by `_shared/sync.py` (the `manifest_update.py` precedent — no
cross-skill imports; independent-installability preserved). Do **not** hand-edit a
copy; edit the canonical and run `uv run _shared/sync.py` (`--check` reports
divergence).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Optional, Union

import yaml

# ---------------------------------------------------------------------------
# Baked-in ruleset (REQ-OKF-FAM-002) — BASELINE ∪ YF-EXTENSIONS, in code.
# Kept in agreement with spec/OKF-BASELINE.md + spec/OKF-YF-EXTENSIONS.md by a
# yf-drift-check edge. The engine never parses those .md files at runtime.
# ---------------------------------------------------------------------------

okf_version = "0.2"  # pinned OKF baseline version (SPEC REQ-OKF-FAM-005; root-only key REQ-OKF-032)

#: Reserved filenames at any level of a bundle (OKF-BASELINE §3/§4; REQ-OKF-001/002).
#: They carry NO ``type`` and NO ``okf_spec`` (REQ-OKF-031).
RESERVED_FILES: tuple[str, ...] = ("index.md", "log.md")

#: The yf member-selector frontmatter key (REQ-OKF-030).
OKF_SPEC_KEY = "okf_spec"

#: The single OKF MUST key (OKF-BASELINE §2 B2).
TYPE_KEY = "type"

#: OKF-BASELINE conformance MUSTs (OKF-BASELINE §2, B1–B3). Structured so the
#: drift-check edge can diff this against the authored doc's MUST table.
BASELINE_MUSTS = {
    "B1": "Every non-reserved .md carries a parseable YAML frontmatter block delimited by ---",
    "B2": "Every such frontmatter block carries a non-empty `type` field",
    "B3": "Each present reserved file (index.md / log.md) follows its §6/§7 structure",
}

#: OKF-YF-EXTENSIONS rules the engine bakes in (OKF-YF-EXTENSIONS §1–§7).
YF_EXTENSION_RULES = {
    "reserved-names": "index.md / log.md are the reserved index + log filenames (REQ-OKF-001/002)",
    "log-newest-first": "log.md entries are newest-first under ISO-8601 (YYYY-MM-DD) headings (REQ-OKF-002)",
    "okf_spec": "every non-reserved .md carries an okf_spec: member key (REQ-OKF-030)",
    "reserved-no-type": "index.md / log.md carry no type and no okf_spec (REQ-OKF-031)",
    "dual-field": "header metadata is dual-written as frontmatter AND **Field:** lines (REQ-OKF-020)",
    "frontmatter-first-read": "reads are frontmatter-first with **Field:** fallback (REQ-OKF-021)",
    "placement": "frontmatter + **Field:** blocks sit above the first `## ` heading (REQ-OKF-010)",
    "single-file-exemption": "a lone .md with no owning dir is exempt from index.md/log.md (REQ-OKF-050)",
    "non-md-exclusion": "non-.md files are excluded from the frontmatter-type rule (REQ-OKF-060)",
    "merge-and-preserve": "writes add only yf keys and never drop a pre-existing key (REQ-OKF-070)",
    "report-only": "check / migrate --dry-run record findings and never raise (REQ-OKF-071)",
}

#: Human-readable member names for the composed ruleset report.
BASELINE_MEMBER = "OKF-BASELINE"
YF_MEMBER = "OKF-YF-EXTENSIONS"

#: Reserved-but-deferred family member (REQ-OKF-FAM-004) — declared, not applied.
RESERVED_DEFERRED_MEMBERS = ("OKF-SPECIFICATION",)


class OKFParseError(ValueError):
    """Raised by the low-level frontmatter reader on malformed YAML.

    Report-only callers (``check_conformance``, ``migrate``) catch this and record
    a finding rather than propagating it (REQ-OKF-071).
    """


# ---------------------------------------------------------------------------
# Frontmatter + body primitives
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---[ \t]*\n(.*?\n)?---[ \t]*\n?", re.DOTALL)
_FIELD_RE = re.compile(r"^\*\*(?P<label>[^:*][^:]*):\*\*[ \t]*(?P<val>.*?)[ \t]*$")
_H2_RE = re.compile(r"^## ", re.MULTILINE)

#: Baseline yf dual-field metadata keys (OKF-YF-EXTENSIONS §1/§2). The REQ-OKF-010
#: placement check treats a below-`## ` `**Label:**` line as a MISPLACED metadata
#: field only when its normalized label is one of these known keys (unioned with the
#: composed member's §4 labels + required keys) — so bold PROSE lead-ins
#: (`**Recommendation:** …`, `**Objective:** …`) are never false-flagged.
_BASELINE_FIELD_KEYS = frozenset(
    {"id", "author", "created", "status", "epic", "fingerprint", "idx", "topic"}
)


def _load_text(source: Union[str, os.PathLike, Path]) -> str:
    """Coerce a path or a text blob to text. Multiline / `---`-leading strings are
    treated as text; a single-line existing path is read from disk."""
    if isinstance(source, Path):
        return source.read_text()
    if isinstance(source, (str, os.PathLike)):
        s = str(source)
        if "\n" in s or s.lstrip().startswith("---"):
            return s
        p = Path(s)
        if p.exists():
            return p.read_text()
        return s
    raise TypeError(f"read_frontmatter: unsupported source type {type(source)!r}")


def read_frontmatter(source: Union[str, os.PathLike, Path]) -> tuple[dict, str]:
    """Return ``(frontmatter_dict, body)`` for a path or text blob.

    Malformed YAML raises :class:`OKFParseError` (report-only callers catch it,
    REQ-OKF-071). A file with no frontmatter yields ``({}, full_text)``.
    """
    text = _load_text(source)
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1) or ""
    body = text[m.end():]
    try:
        data = yaml.safe_load(raw) if raw.strip() else {}
    except yaml.YAMLError as exc:
        raise OKFParseError(f"malformed YAML frontmatter: {exc}") from exc
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise OKFParseError(f"frontmatter is not a mapping (got {type(data).__name__})")
    return data, body


def _dump_frontmatter(data: dict) -> str:
    """Serialize a frontmatter dict, preserving key insertion order."""
    if not data:
        return "---\n---\n"
    body = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False)
    return f"---\n{body}---\n"


def _split_at_first_h2(text: str) -> tuple[str, str]:
    """Split ``text`` into ``(head, tail)`` where ``tail`` begins at the first
    ``## `` heading (REQ-OKF-010 placement boundary). If none, tail is empty."""
    m = _H2_RE.search(text)
    if not m:
        return text, ""
    return text[: m.start()], text[m.start():]


def write_frontmatter(
    path: Union[str, Path],
    updates: dict,
    *,
    delete: Iterable[str] | None = None,
    dry_run: bool = False,
) -> str:
    """Merge ``updates`` into ``path``'s frontmatter and write it back.

    **Merge-and-preserve (REQ-OKF-070):** existing keys keep their position and
    value unless named in ``updates``; new keys are appended. A pre-existing
    foreign key (Obsidian ``tags``/``aliases``/``cssclass``) is never dropped.
    The frontmatter block sits at the file top — trivially above the first
    ``## `` heading (REQ-OKF-010). Returns the new file text.

    **Deletion (plan-053 Issue 4.3, #207).** ``delete`` names keys to REMOVE. The writer was
    merge-only, so there was no supported way to un-set a key — an operator whose plan
    recorded a burned epic could only hand-edit ``plan.md``, which reliably updates one of the
    two dual-written surfaces and leaves the other.

    Deletion is deliberately a SEPARATE ARGUMENT rather than a sentinel value in ``updates``
    (``None``, say): ``None`` is a legitimate frontmatter value, so overloading it would make
    "set this key to null" and "remove this key" indistinguishable — the same
    two-facts-one-signal conflation this plan exists to close. A key named in ``delete`` that
    is not present is a no-op, not an error, which is what makes the caller idempotent.
    """
    p = Path(path)
    existing, body = read_frontmatter(p) if p.exists() else ({}, "")
    merged = dict(existing)  # ordered copy
    for k, v in updates.items():
        merged[k] = v  # in-place if present (order kept), else appended
    for k in (delete or ()):
        merged.pop(k, None)  # absent is a no-op, never an error
    text = _dump_frontmatter(merged) + body
    if not dry_run:
        p.write_text(text)
    return text


# ---------------------------------------------------------------------------
# Dual field model (REQ-OKF-020 / REQ-OKF-021)
# ---------------------------------------------------------------------------


def _label_to_key(label: str) -> str:
    """Normalize a ``**Field:**`` label to a frontmatter key (``ID`` -> ``id``)."""
    return label.strip().lower().replace(" ", "_")


def read_fields(source: Union[str, os.PathLike, Path]) -> dict:
    """Dual-mode read (REQ-OKF-021): frontmatter-first with ``**Field:**`` fallback.

    Frontmatter values win; keys absent from frontmatter are filled from legacy
    ``**Field:**`` header lines (normalized to lowercase keys). Never raises on a
    missing frontmatter block; malformed YAML propagates as :class:`OKFParseError`.
    """
    text = _load_text(source)
    try:
        fm, body = read_frontmatter(text)
    except OKFParseError:
        fm, body = {}, text
    model = dict(fm)
    head, _tail = _split_at_first_h2(body if fm else text)
    for line in head.splitlines():
        m = _FIELD_RE.match(line.strip())
        if not m:
            continue
        key = _label_to_key(m.group("label"))
        if key not in model:  # frontmatter wins
            val = m.group("val").strip()
            if val:
                model[key] = val
    return model


def write_fields(
    path: Union[str, Path],
    model: dict,
    *,
    field_labels: Optional[dict] = None,
    field_order: Optional[Iterable[str]] = None,
    dry_run: bool = False,
) -> str:
    """Dual-write (REQ-OKF-020): emit BOTH a frontmatter block and ``**Field:**``
    lines from one in-memory ``model``, both above the first ``## `` heading
    (REQ-OKF-010).

    ``field_labels`` maps a model key to its display label (default: title-cased
    key); ``field_order`` restricts/orders which keys get a ``**Field:**`` line
    (default: every key in ``model``). Merge-and-preserves existing frontmatter.
    """
    p = Path(path)
    _existing, body = read_frontmatter(p) if p.exists() else ({}, "")
    head, tail = _split_at_first_h2(body)

    # strip any pre-existing **Field:** lines from the head so we don't duplicate
    kept_head_lines = [ln for ln in head.splitlines() if not _FIELD_RE.match(ln.strip())]
    kept_head = "\n".join(kept_head_lines).strip("\n")

    labels = dict(field_labels or {})
    keys = list(field_order) if field_order is not None else list(model.keys())
    field_lines = []
    for k in keys:
        if k not in model:
            continue
        label = labels.get(k, k.replace("_", " ").title())
        field_lines.append(f"**{label}:** {model[k]}")
    field_block = "\n".join(field_lines)

    # frontmatter (merge-and-preserve) + field block + remaining head + tail
    fm_text = write_frontmatter(p, dict(model), dry_run=True)
    # fm_text already includes the old body; rebuild deterministically instead:
    merged, _ = read_frontmatter(fm_text)
    parts = [_dump_frontmatter(merged)]
    if field_block:
        parts.append("\n" + field_block + "\n")
    if kept_head:
        parts.append("\n" + kept_head + "\n")
    if tail:
        # ensure a blank line before the first ## heading
        if not parts[-1].endswith("\n\n"):
            parts.append("\n")
        parts.append(tail)
    text = "".join(parts)
    if not dry_run:
        p.write_text(text)
    return text


# ---------------------------------------------------------------------------
# Bundle scaffolding + reserved files
# ---------------------------------------------------------------------------


def scaffold_bundle(
    directory: Union[str, Path],
    *,
    spec_member: Optional[str] = None,
    subdirs: Iterable[str] = (),
    entry: Optional[str] = None,
    entry_type: Optional[str] = None,
    entry_meta: Optional[dict] = None,
    title: Optional[str] = None,
    reserved: bool = True,
    root: bool = True,
) -> Path:
    """Create an OKF-compatible dir-form bundle skeleton at ``directory``.

    Writes reserved ``index.md`` and ``log.md``
    (REQ-OKF-001/002) when ``reserved`` is set, mkdirs any ``subdirs``, and — if
    ``entry`` is given — a typed concept document carrying ``type``+``okf_spec``
    frontmatter (REQ-OKF-003/030). Returns the bundle directory Path.

    ``root`` declares whether ``directory`` is a bundle **root** (REQ-OKF-004).
    Root-ness is a property of the invocation, not of the filesystem, so it is
    passed rather than inferred. Only a root ``index.md`` may carry the
    ``okf_version`` key (REQ-OKF-032, OKF v0.2 §8).
    """
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    for sub in subdirs:
        (d / sub).mkdir(parents=True, exist_ok=True)

    if reserved:
        idx = d / "index.md"
        if not idx.exists():
            name = title or d.name
            head = _dump_frontmatter({"okf_version": okf_version}) if root else ""
            idx.write_text(head + f"\n# {name}\n\n")
        log = d / "log.md"
        if not log.exists():
            log.write_text("# Log\n\n")

    if entry:
        ep = d / entry
        meta = {TYPE_KEY: entry_type or "Concept"}
        if spec_member:
            meta[OKF_SPEC_KEY] = spec_member
        if entry_meta:
            meta.update(entry_meta)
        heading = title or Path(entry).stem
        ep.write_text(_dump_frontmatter(meta) + f"\n# {heading}\n\n")
    return d


# --- reserved index.md ------------------------------------------------------


def _read_index(bundle: Path, *, root: bool = True) -> tuple[dict, str]:
    idx = bundle / "index.md"
    if idx.exists():
        return read_frontmatter(idx)
    # REQ-OKF-032: only a bundle-ROOT index.md may carry okf_version (v0.2 §8).
    return ({"okf_version": okf_version} if root else {}), f"\n# {bundle.name}\n\n"


def render_index(bundle: Union[str, Path], *, root: bool = True) -> str:
    """Return the reserved ``index.md`` text for ``bundle`` (progressive-disclosure
    listing: ``#`` heading + ``- [child](path) - description`` bullets). If no
    ``index.md`` exists, a minimal generic one is generated from the bundle's
    direct ``.md`` children and subdirs (per-skill adapters refine this later).

    ``root`` declares whether ``bundle`` is a bundle **root** (REQ-OKF-004).
    A generated non-root listing carries NO frontmatter: OKF v0.2 §8 permits
    ``okf_version`` on a bundle-root ``index.md`` only (REQ-OKF-032)."""
    b = Path(bundle)
    idx = b / "index.md"
    if idx.exists():
        return idx.read_text()
    lines = ([_dump_frontmatter({"okf_version": okf_version})] if root else [])
    lines.append(f"\n# {b.name}\n\n")
    if b.is_dir():
        for child in sorted(b.iterdir()):
            if child.name in RESERVED_FILES or child.name.startswith("."):
                continue
            if child.is_dir():
                lines.append(f"- [{child.name}/]({child.name}/index.md)\n")
            elif child.is_file():
                lines.append(f"- [{child.name}]({child.name})\n")
    return "".join(lines)


def add_index_entry(
    bundle: Union[str, Path],
    path: str,
    desc: str = "",
    *,
    dry_run: bool = False,
    root: bool = True,
) -> str:
    """Append a listing bullet ``- [path](path) - desc`` to the bundle's reserved
    ``index.md``, preserving its ``okf_version`` frontmatter. Idempotent on the
    same ``path``. Returns the new ``index.md`` text."""
    b = Path(bundle)
    fm, body = _read_index(b, root=root)
    bullet = f"- [{path}]({path})" + (f" - {desc}" if desc else "")
    if bullet.split(" - ")[0] not in body:
        if not body.endswith("\n"):
            body += "\n"
        body += bullet + "\n"
    text = _dump_frontmatter(fm) + body
    if not dry_run:
        (b / "index.md").write_text(text)
    return text


# --- reserved log.md --------------------------------------------------------

_LOG_DATE_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})[ \t]*$", re.MULTILINE)


def append_log(
    bundle: Union[str, Path],
    text: str,
    *,
    date: Optional[str] = None,
    dry_run: bool = False,
) -> str:
    """Append a newest-first ISO-8601 entry to the bundle's reserved ``log.md``
    (REQ-OKF-002). New entries are prepended; if ``date`` already heads the log,
    the bullet is added under that heading. Existing entries and the earliest
    date are preserved (grandfather, REQ-OKF-MIG-002). ``date`` defaults to today.
    Returns the new ``log.md`` text."""
    from datetime import date as _date

    b = Path(bundle)
    log = b / "log.md"
    date = date or _date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError(f"append_log: date {date!r} is not ISO-8601 YYYY-MM-DD")

    raw = log.read_text() if log.exists() else "# Log\n\n"
    # Split a leading `# ...` title from the entries region.
    lines = raw.splitlines(keepends=True)
    title_end = 0
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            title_end = i + 1
            # skip a trailing blank line after the title
            if title_end < len(lines) and lines[title_end].strip() == "":
                title_end += 1
            break
    title_part = "".join(lines[:title_end]) or "# Log\n\n"
    entries_part = "".join(lines[title_end:])

    bullet = f"- {text}\n"
    first_heading = _LOG_DATE_RE.search(entries_part)
    if first_heading and first_heading.group(1) == date and first_heading.start() == 0:
        # same date already heads the entries — insert bullet under it
        insert_at = first_heading.end()
        # move past the heading's own newline
        nl = entries_part.find("\n", insert_at)
        nl = nl + 1 if nl != -1 else len(entries_part)
        new_entries = entries_part[:nl] + bullet + entries_part[nl:]
    else:
        block = f"## {date}\n\n{bullet}\n"
        new_entries = block + entries_part
    if not title_part.endswith("\n\n"):
        title_part = title_part.rstrip("\n") + "\n\n"
    out = title_part + new_entries
    if not dry_run:
        log.write_text(out)
    return out


# ---------------------------------------------------------------------------
# Per-skill OKF-EXTENSION.md discovery + composition (REQ-OKF-FAM-001..003)
# ---------------------------------------------------------------------------


@dataclass
class ExtensionRuleset:
    """A parsed per-skill ``OKF-EXTENSION.md`` (REQ-OKF-FAM-003)."""

    skill: Optional[str]
    member: Optional[str] = None          # okf_spec member name, e.g. OKF-PLAN
    type_vocab: list[str] = field(default_factory=list)
    required_keys: list[str] = field(default_factory=list)
    reserved_subdirs: list[str] = field(default_factory=list)
    bundle_form: str = "dir-form"          # dir-form | single-file | both
    source: Optional[str] = None           # path to the OKF-EXTENSION.md
    found: bool = False
    #: Ordered (path-glob -> ``type``) rules driving migrate's per-file type
    #: assignment (REQ-OKF-MIG-004). First match wins; the ``*`` catch-all row (if
    #: present) also seeds ``default_type``.
    type_map: list[tuple[str, str]] = field(default_factory=list)
    #: Fallback ``type`` for a file matching no ``type_map`` rule (REQ-OKF-MIG-004).
    default_type: str = "Concept"
    #: Member-driven reserved-file sources (REQ-OKF-MIG-005): the legacy filename
    #: that becomes ``index.md`` (e.g. ``README.md`` / ``_index.md``, or ``scaffold``
    #: to synthesize a skeleton) and the ``log.md`` source (``<file>:phase-log`` to
    #: extract an in-body ``**Phase log:**`` block, or ``scaffold``).
    index_source: Optional[str] = None
    log_source: Optional[str] = None
    #: The member's primary artifact type (e.g. ``Plan`` for OKF-PLAN). Extension
    #: extra-required-keys (§2) are scoped to docs of this type (REQ-OKF-FAM-001).
    main_type: Optional[str] = None
    #: Normalized dual-field metadata labels declared in the member's §4 table
    #: (e.g. ``**ID:**`` -> ``id``). The REQ-OKF-010 placement check flags only these
    #: known metadata labels below the first ``## `` — never arbitrary bold prose.
    field_labels: list[str] = field(default_factory=list)


def _self_location() -> dict:
    """Locate the running ``okf.py`` and classify its address space.

    * vendored copy  -> ``skills/<skill>/scripts/okf.py``
    * canonical copy -> ``_shared/okf.py``
    """
    p = Path(__file__).resolve()
    parent = p.parent
    if parent.name == "scripts" and parent.parent.parent.name == "skills":
        skill_dir = parent.parent
        return {
            "mode": "vendored",
            "skill": skill_dir.name,
            "skill_dir": skill_dir,
            "skills_root": skill_dir.parent,
        }
    if parent.name == "_shared":
        repo_root = parent.parent
        return {"mode": "canonical", "skill": None, "skills_root": repo_root / "skills"}
    return {"mode": "unknown", "skill": None, "skills_root": None}


def _section(text: str, *substrings: str) -> str:
    """Return the body of the first heading containing all ``substrings``."""
    lines = text.splitlines()
    start = None
    heading = ""
    for i, ln in enumerate(lines):
        if ln.startswith("#") and all(s.lower() in ln.lower() for s in substrings):
            start, heading = i, ln
            break
    if start is None:
        return ""
    level = len(heading) - len(heading.lstrip("#"))
    out = []
    for ln in lines[start + 1:]:
        if ln.startswith("#"):
            lv = len(ln) - len(ln.lstrip("#"))
            if lv <= level:
                break
        out.append(ln)
    return "\n".join(out)


def _table_rows(section_text: str) -> list[list[str]]:
    rows = []
    for ln in section_text.splitlines():
        s = ln.strip()
        if s.startswith("|") and s.endswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(set(c) <= set("-: ") and c for c in cells):
                continue  # separator row
            rows.append(cells)
    return rows


_BACKTICK_RE = re.compile(r"`([^`]+)`")


def parse_extension(text: str, skill: Optional[str], source: Optional[str]) -> ExtensionRuleset:
    """Parse an ``OKF-EXTENSION.md`` document into an :class:`ExtensionRuleset`."""
    rs = ExtensionRuleset(skill=skill, source=source, found=True)

    m = re.search(r"\*\*(OKF-[A-Z][A-Z-]*)\*\*", text)
    if m:
        rs.member = m.group(1)

    # bundle form (from §0 identity table row / free text)
    id_sec = _section(text, "Member identity") or text
    has_single = "single-file" in id_sec.lower()
    has_dir = "dir-form" in id_sec.lower()
    rs.bundle_form = "both" if (has_single and has_dir) else "single-file" if has_single else "dir-form"

    # §1 type vocabulary — backticked values in the first column
    type_sec = _section(text, "type", "vocabulary")
    for row in _table_rows(type_sec)[1:]:  # skip header
        m2 = _BACKTICK_RE.search(row[0])
        if m2:
            rs.type_vocab.append(m2.group(1))

    # §2 required extension frontmatter keys — first-col key where force cell has MUST
    key_sec = _section(text, "frontmatter", "keys") or _section(text, "Required")
    for row in _table_rows(key_sec)[1:]:
        if len(row) < 2:
            continue
        m3 = _BACKTICK_RE.search(row[0])
        if m3 and "MUST" in row[1].upper():
            rs.required_keys.append(m3.group(1))

    # §3 reserved subdirs — backticked paths ending in /
    sub_sec = _section(text, "Reserved subdirs") or _section(text, "Reserved", "files")
    for row in _table_rows(sub_sec)[1:]:
        m4 = _BACKTICK_RE.search(row[0])
        if m4 and m4.group(1).endswith("/"):
            rs.reserved_subdirs.append(m4.group(1))

    # role -> type map (REQ-OKF-MIG-004) — the "Migration: role -> type map" table.
    # First column: a bundle-relative path glob; second column: the assigned type.
    # A ``*`` catch-all row seeds default_type (and never records a fallback finding).
    map_sec = _section(text, "role", "map")
    for row in _table_rows(map_sec)[1:]:
        if len(row) < 2:
            continue
        gm = _BACKTICK_RE.search(row[0])
        tm = _BACKTICK_RE.search(row[1])
        if gm and tm:
            glob, typ = gm.group(1), tm.group(1)
            if glob == "*":
                # the ``*`` row documents the fallback type only; it is NOT a
                # matchable rule, so a genuinely unmapped file still records a
                # default-fallback finding (REQ-OKF-MIG-004 — no silent mislabel).
                rs.default_type = typ
            else:
                rs.type_map.append((glob, typ))

    # member-driven reserved-file sources (REQ-OKF-MIG-005) — the
    # "Migration: reserved-file sources" table (target <- source).
    src_sec = _section(text, "reserved-file source")
    for row in _table_rows(src_sec)[1:]:
        if len(row) < 2:
            continue
        tgt = _BACKTICK_RE.search(row[0])
        src = _BACKTICK_RE.search(row[1])
        if not (tgt and src):
            continue
        if tgt.group(1) == "index.md":
            rs.index_source = src.group(1)
        elif tgt.group(1) == "log.md":
            rs.log_source = src.group(1)

    # §4 dual-field labels — the backticked `**Label:**` entries in the first column
    # of the "dual field set" table, normalized to keys (`**ID:**` -> `id`).
    dual_sec = _section(text, "dual field")
    for row in _table_rows(dual_sec)[1:]:
        mfl = _BACKTICK_RE.search(row[0])
        if mfl:
            lbl = mfl.group(1).strip().strip("*").rstrip(":").strip()
            if lbl:
                rs.field_labels.append(_label_to_key(lbl))

    # main artifact type: the backticked file named in the §2 required-keys header
    # ("Force on `plan.md`"), resolved through type_map; else the first vocab entry.
    key_rows = _table_rows(key_sec)
    if key_rows:
        for cell in key_rows[0]:
            fm2 = _BACKTICK_RE.search(cell)
            if fm2 and fm2.group(1).endswith(".md"):
                for glob, typ in rs.type_map:
                    if _glob_match(fm2.group(1), glob):
                        rs.main_type = typ
                        break
                if rs.main_type:
                    break
    if rs.main_type is None and rs.type_vocab:
        rs.main_type = rs.type_vocab[0]

    return rs


def _glob_match(rel: str, glob: str) -> bool:
    """Match a bundle-relative POSIX path ``rel`` against a ``type_map`` glob.

    ``*`` matches any single file at the bundle root; ``findings/*`` matches a file
    directly under ``findings/``; a bare filename matches that path exactly."""
    g = glob.strip().rstrip("/")
    if not g:
        return False
    try:
        return PurePosixPath(rel).match(g)
    except ValueError:
        return False


def resolve_extension(skill: Optional[str] = None) -> ExtensionRuleset:
    """Discover + parse a consumer's ``skills/<skill>/OKF-EXTENSION.md``,
    ``__file__``-relative to the running (possibly vendored) ``okf.py``
    (REQ-OKF-FAM-003), working in BOTH address spaces:

    * **vendored** (``skills/<skill>/scripts/okf.py``): with no ``skill`` arg the
      script resolves its OWN skill's extension at ``<parent-of-scripts>/OKF-EXTENSION.md``
      — no sibling skill required on disk.
    * **canonical** (``_shared/okf.py``): ``skill`` names the target;
      ``<repo_root>/skills/<skill>/OKF-EXTENSION.md`` is resolved.

    Returns an :class:`ExtensionRuleset` with ``found=False`` when no extension
    doc exists (report-only; never raises for a missing file).
    """
    loc = _self_location()
    if skill is None:
        skill = loc.get("skill")
    if skill is None:
        return ExtensionRuleset(skill=None, found=False)

    ext_path: Optional[Path] = None
    if loc["mode"] == "vendored" and skill == loc["skill"]:
        ext_path = loc["skill_dir"] / "OKF-EXTENSION.md"
    else:
        root = loc.get("skills_root")
        if root is not None:
            ext_path = Path(root) / skill / "OKF-EXTENSION.md"

    if not ext_path or not ext_path.exists():
        return ExtensionRuleset(skill=skill, found=False, source=str(ext_path) if ext_path else None)
    try:
        return parse_extension(ext_path.read_text(), skill, str(ext_path))
    except Exception:  # report-only: a malformed extension doc yields "not found"
        return ExtensionRuleset(skill=skill, found=False, source=str(ext_path))


# ---------------------------------------------------------------------------
# Composed ruleset + conformance check (REQ-OKF-FAM-001, REQ-OKF-CHK-001)
# ---------------------------------------------------------------------------


@dataclass
class EffectiveRuleset:
    """The composed BASELINE ∪ YF-EXTENSIONS ∪ per-skill effective ruleset."""

    members: list[str]                     # e.g. ["OKF-BASELINE","OKF-YF-EXTENSIONS","OKF-PLAN"]
    reserved_files: tuple[str, ...]
    require_type: bool
    require_okf_spec: bool
    extension: ExtensionRuleset


def compose_ruleset(skill: Optional[str] = None) -> EffectiveRuleset:
    """Compose the effective ruleset (REQ-OKF-FAM-001): baked-in BASELINE ∪
    YF-EXTENSIONS ∪ the resolved per-skill ``OKF-EXTENSION.md``."""
    ext = resolve_extension(skill)
    members = [BASELINE_MEMBER, YF_MEMBER]
    if ext.found and ext.member:
        members.append(ext.member)
    elif ext.found and ext.skill:
        members.append(f"OKF-{ext.skill}")
    return EffectiveRuleset(
        members=members,
        reserved_files=RESERVED_FILES,
        require_type=True,
        require_okf_spec=True,
        extension=ext,
    )


@dataclass
class Finding:
    path: str
    req: str
    level: str  # "error" | "warning" | "info"
    message: str

    def as_dict(self) -> dict:
        return {"path": self.path, "req": self.req, "level": self.level, "message": self.message}


@dataclass
class Findings:
    findings: list[Finding] = field(default_factory=list)
    ruleset: Optional[EffectiveRuleset] = None

    def add(self, path: str, req: str, level: str, message: str) -> None:
        self.findings.append(Finding(path, req, level, message))

    @property
    def rulesets_composed(self) -> list[str]:
        return list(self.ruleset.members) if self.ruleset else []

    @property
    def ok(self) -> bool:
        return not any(f.level == "error" for f in self.findings)

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "rulesets_composed": self.rulesets_composed,
            "findings": [f.as_dict() for f in self.findings],
        }


def _is_single_file_bundle(target: Path) -> bool:
    return target.is_file() and target.suffix == ".md"


def check_conformance(
    bundle: Union[str, Path],
    skill: Optional[str] = None,
) -> Findings:
    """Verify the composed effective ruleset (REQ-OKF-FAM-001) over ``bundle``
    (REQ-OKF-CHK-001). Checks: reserved ``index.md``/``log.md`` structure
    (REQ-OKF-001/002), frontmatter + non-empty ``type`` on every non-reserved
    ``.md`` (REQ-OKF-003), the ``okf_spec`` member key (REQ-OKF-030), the
    single-file exemption (REQ-OKF-050), and the non-``.md`` exclusion
    (REQ-OKF-060). When a per-skill extension is composed, ``type`` membership in
    its vocabulary and its extra required keys are also verified.

    **Report-only and crash-safe (REQ-OKF-071):** malformed YAML / unreadable /
    binary input records a finding and continues — this never raises.
    """
    target = Path(bundle)
    eff = compose_ruleset(skill)
    findings = Findings(ruleset=eff)

    # Single-file-bundle exemption (REQ-OKF-050): a lone .md, no owning dir.
    if _is_single_file_bundle(target):
        _check_concept_doc(target, target.name, eff, findings)
        return findings

    if not target.is_dir():
        findings.add(str(target), "REQ-OKF-CHK-001", "error", "bundle path is neither a dir nor a .md file")
        return findings

    md_files = [p for p in sorted(target.rglob("*.md"))]
    non_reserved = [p for p in md_files if p.name not in eff.reserved_files]

    # dir-form bundle must carry reserved index.md / log.md at its root
    root_reserved = {p.name for p in target.iterdir() if p.is_file()}
    if "index.md" not in root_reserved:
        findings.add(str(target / "index.md"), "REQ-OKF-001", "error", "reserved index.md missing")
    else:
        _check_reserved_index(target / "index.md", findings)
    if "log.md" not in root_reserved:
        findings.add(str(target / "log.md"), "REQ-OKF-002", "error", "reserved log.md missing")
    else:
        _check_reserved_log(target / "log.md", findings)

    for md in non_reserved:
        rel = str(md.relative_to(target))
        _check_concept_doc(md, rel, eff, findings)

    # Index drift (REQ-OKF-CHK-002) — WARNING level, deliberately.
    #
    # `warning`, not `error`, and NOT because a new req could be promoted by the
    # downstream audit: that promotion filter is a four-element ALLOWLIST, so a
    # newly allocated req is outside it by construction and there is nothing to
    # opt out of. The reason is that relying on an allowlist's SILENCE is itself
    # an implicit guarantee no test asserts — a future edit widening it would
    # resurrect the risk invisibly. Promotion to error is a separate, later
    # change, gated on a green corpus.
    #
    # Root-scoped (REQ-OKF-004/011): `check` recurses, `reindex` does not.
    if "index.md" in root_reserved:
        try:
            drift = reindex_check(target)
        except Exception as exc:                 # report-only / crash-safe (REQ-OKF-071)
            findings.add(str(target / "index.md"), "REQ-OKF-CHK-002", "warning",
                         f"index drift check failed: {exc}")
        else:
            for f in drift.get("findings", []):
                if f["kind"] not in ("ghost", "missing"):
                    continue                     # `empty-dir` is a reindex-only signal
                findings.add(str(target / "index.md"), "REQ-OKF-CHK-002", "warning",
                             f"index {f['kind']}: {f['target']} — {f['detail']}")

    # Non-.md files are excluded (REQ-OKF-060) — no findings emitted for them.
    return findings


def _check_reserved_index(path: Path, findings: Findings) -> None:
    """Reserved index.md carries no type/okf_spec (REQ-OKF-031) and is a listing."""
    try:
        fm, body = read_frontmatter(path)
    except OKFParseError as exc:
        findings.add(str(path), "REQ-OKF-071", "error", f"index.md unparseable: {exc}")
        return
    except Exception as exc:  # pragma: no cover - defensive (binary etc.)
        findings.add(str(path), "REQ-OKF-071", "error", f"index.md unreadable: {exc}")
        return
    if TYPE_KEY in fm:
        findings.add(str(path), "REQ-OKF-031", "error", "reserved index.md must not carry `type`")
    if OKF_SPEC_KEY in fm:
        findings.add(str(path), "REQ-OKF-031", "error", "reserved index.md must not carry `okf_spec`")


def _check_reserved_log(path: Path, findings: Findings) -> None:
    """Reserved log.md: no type/okf_spec (REQ-OKF-031); entries newest-first
    ISO-8601 headings (REQ-OKF-002)."""
    try:
        fm, body = read_frontmatter(path)
    except OKFParseError as exc:
        findings.add(str(path), "REQ-OKF-071", "error", f"log.md unparseable: {exc}")
        return
    except Exception as exc:  # pragma: no cover
        findings.add(str(path), "REQ-OKF-071", "error", f"log.md unreadable: {exc}")
        return
    if TYPE_KEY in fm or OKF_SPEC_KEY in fm:
        findings.add(str(path), "REQ-OKF-031", "error", "reserved log.md must not carry type/okf_spec")
    dates = _LOG_DATE_RE.findall(body)
    if dates and dates != sorted(dates, reverse=True):
        findings.add(str(path), "REQ-OKF-002", "warning", "log.md date headings are not newest-first")


def _check_concept_doc(path: Path, rel: str, eff: EffectiveRuleset, findings: Findings) -> None:
    """Verify a non-reserved concept .md: frontmatter+type (REQ-OKF-003),
    okf_spec (REQ-OKF-030), placement (REQ-OKF-010), per-skill required keys +
    type vocab. Crash-safe (REQ-OKF-071)."""
    try:
        text = path.read_text()
    except Exception as exc:  # binary / unreadable
        findings.add(rel, "REQ-OKF-071", "error", f"unreadable: {exc}")
        return
    try:
        fm, body = read_frontmatter(text)
    except OKFParseError as exc:
        findings.add(rel, "REQ-OKF-071", "error", f"malformed frontmatter: {exc}")
        return

    if not fm:
        findings.add(rel, "REQ-OKF-003", "error", "no YAML frontmatter block")
        return
    t = fm.get(TYPE_KEY)
    if not (isinstance(t, str) and t.strip()):
        findings.add(rel, "REQ-OKF-003", "error", "missing or empty `type`")
    if OKF_SPEC_KEY not in fm or not str(fm.get(OKF_SPEC_KEY) or "").strip():
        findings.add(rel, "REQ-OKF-030", "error", "missing `okf_spec` member key")

    # Placement (REQ-OKF-010): frontmatter is at file top (above first ##) by
    # construction of read_frontmatter; verify any misplaced dual-field METADATA line
    # is caught. A below-`## ` `**Label:**` line counts as a misplaced metadata field
    # only when (a) it has a NON-EMPTY inline value and (b) its normalized label is a
    # KNOWN metadata key (the yf baseline set ∪ the member's §4 labels ∪ its required
    # keys). This never false-flags a bold PROSE lead-in (`**Recommendation:** …`,
    # `**Objective:** …`) that real document bodies use heavily.
    known_field_keys = set(_BASELINE_FIELD_KEYS)
    if eff.extension.found:
        known_field_keys.update(eff.extension.field_labels)
        known_field_keys.update(_label_to_key(k) for k in eff.extension.required_keys)
    head, tail = _split_at_first_h2(body)
    if tail:
        for ln in tail.splitlines():
            m = _FIELD_RE.match(ln.strip())
            if m and m.group("val").strip() and _label_to_key(m.group("label")) in known_field_keys:
                findings.add(rel, "REQ-OKF-010", "error", "a **Field:** metadata line sits below the first `## `")
                break

    ext = eff.extension
    if ext.found:
        if ext.type_vocab and isinstance(t, str) and t.strip() and t not in ext.type_vocab:
            findings.add(
                rel, "REQ-OKF-FAM-001", "warning",
                f"type {t!r} not in {ext.member or ext.skill} vocab {ext.type_vocab}",
            )
        # Extension extra-required-keys (§2) are WARNING-level and scoped to docs of
        # the member's MAIN type (REQ-OKF-FAM-001). Rationale: the OKF baseline MUSTs
        # (type + parseable frontmatter) plus okf_spec are the hard errors the base
        # engine guarantees; backfilling member-specific keys (id/idx/verdict/…) from
        # legacy prose/**Field:** surfaces is the per-skill ADAPTER's job (Epics 3/4/5).
        # Scoping to main_type avoids mislabeling a Finding/Review with a Plan's keys.
        is_main = ext.main_type is None or (isinstance(t, str) and t == ext.main_type)
        if is_main:
            for k in ext.required_keys:
                if k in (TYPE_KEY, OKF_SPEC_KEY):
                    continue
                if k not in fm or not str(fm.get(k) or "").strip():
                    findings.add(
                        rel, "REQ-OKF-FAM-001", "warning",
                        f"missing required key {k!r} (composed from {ext.member or ext.skill}; "
                        f"per-skill adapter backfills it)",
                    )


# ---------------------------------------------------------------------------
# Migration (REQ-OKF-MIG-001..003)
#
# `emit_conformant_copy` — a non-destructive "conformant projection" — was
# DELETED here by plan-046 Issue 5.2. Measured before removal: zero callers,
# zero tests, not a CLI verb; spec'd but unreachable since plan-029.
#
# Not revived, because exposing it as a verb would mean building the on-demand
# export projection that #92's revisit triggers do NOT justify: the adopter half
# of trigger (b) HAS fired (four verified non-Google OKF adopters, two at v0.2)
# but the DEMAND half has not — no consumer wants a projection. Deleting rather
# than leaving it in place is the point of risk R7: a spec'd, unreachable
# function lets a future investigator conclude the projection "exists". The
# capability is remembered as an upstream follow-on ("projection delivery
# mode"), so the record survives the removal.
# ---------------------------------------------------------------------------




@dataclass
class Change:
    op: str          # add-frontmatter | rename | extract-log | scaffold-index | scaffold-log
    path: str
    detail: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {"op": self.op, "path": self.path, **self.detail}


@dataclass
class ChangePlan:
    directory: str
    dry_run: bool
    changes: list[Change] = field(default_factory=list)
    skill: Optional[str] = None
    member: Optional[str] = None

    def add(self, op: str, path: str, **detail) -> None:
        self.changes.append(Change(op, path, detail))

    def as_dict(self) -> dict:
        return {
            "command": "migrate",
            "dir": self.directory,
            "dry_run": self.dry_run,
            "skill": self.skill,
            "member": self.member,
            "changes": [c.as_dict() for c in self.changes],
        }


_PHASE_LOG_RE = re.compile(r"^\*\*Phase log:\*\*(?P<block>.*?)(?=^\s*##\s|\Z)", re.DOTALL | re.MULTILINE)
_SCOPING_DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2}).{0,40}?scoping|scoping.{0,40}?(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
_ANY_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def _assign_type(rel: str, type_map: list[tuple[str, str]], default: str) -> tuple[str, bool]:
    """Resolve a bundle-relative path to a ``type`` via an ordered ``type_map``
    (REQ-OKF-MIG-004). Returns ``(type, matched)``; ``matched`` is ``False`` when the
    ``default`` fallback was used (migrate records that as a finding — no silent
    mislabel). First matching glob wins."""
    for glob, typ in type_map:
        if _glob_match(rel, glob):
            return typ, True
    return default, False


def _first_scoping_date(block: str) -> Optional[str]:
    """Extract the earliest scoping date from a legacy phase-log block
    (REQ-OKF-MIG-002)."""
    dates = []
    for line in block.splitlines():
        if "scoping" in line.lower():
            m = _ANY_DATE_RE.search(line)
            if m:
                dates.append(m.group(0))
    if not dates:
        # fall back to any date in the block
        m = _ANY_DATE_RE.search(block)
        if m:
            dates.append(m.group(0))
    return min(dates) if dates else None


_PHASE_LOG_BULLET_RE = re.compile(r"^-\s+(\d{4}-\d{2}-\d{2})\s+(.*\S)\s*$")


def _phase_log_bullets(block: str) -> list[tuple[str, str]]:
    """Parse a legacy multi-bullet ``**Phase log:**`` block into ``(date, rest)``
    pairs, preserving each bullet's ``<status>:`` token (e.g.
    ``("2026-04-05", "review: plan v1 presented — REVISE")``).

    Only dated ``- YYYY-MM-DD <rest>`` bullets are returned, in document (oldest-
    first) order. An inline/semicolon-form phase log (``**Phase log:** 2026-03-01
    scoping; ...`` — no ``- `` bullets) yields ``[]``, so callers fall back to the
    single first-``scoping:`` line. These pairs feed ``append_log`` verbatim so
    every entry — crucially each ``review:`` line — survives migration, keeping the
    REQ-PORT-006 count-equality invariant intact across the extract-log step."""
    out: list[tuple[str, str]] = []
    for line in block.splitlines():
        m = _PHASE_LOG_BULLET_RE.match(line.strip())
        if m:
            out.append((m.group(1), m.group(2).strip()))
    return out


def migrate(
    directory: Union[str, Path],
    *,
    dry_run: bool = False,
    skill: Optional[str] = None,
    type_map: Optional[list] = None,
) -> ChangePlan:
    """Convert a legacy bundle in place to the OKF-compatible model (REQ-OKF-MIG-001),
    **member-driven** by the resolved per-skill ``OKF-EXTENSION.md``:

    * **Reserved files (REQ-OKF-MIG-005).** ``index.md`` and ``log.md`` are
      reconciled from the member's declared sources — e.g. OKF-PLAN renames
      ``README.md`` -> ``index.md`` and extracts ``plan.md``'s ``**Phase log:**``
      block -> ``log.md``; OKF-RESEARCH renames ``_index.md`` -> ``index.md`` and
      scaffolds ``log.md``; OKF-INCUBATOR keeps ``README.md`` (its typed state file)
      and scaffolds both. Where a member declares no source, a conformant skeleton is
      synthesized so ``check`` passes for that member.
    * **Per-file type (REQ-OKF-MIG-004).** Each non-reserved ``.md`` is stamped with
      the ``type`` its member ``type_map`` assigns for that path (Plan / Finding /
      Review / …), not a blanket ``Concept``. A path matching no rule falls back to
      the member default and is recorded (``type_source: default-fallback``).
    * **Dual-field mirror (REQ-OKF-020).** Existing human ``**Field:**`` header lines
      (``**ID:**``, ``**Status:**``, …) are mirrored into frontmatter so both
      representations stay in sync, never frontmatter-alone.
    * ``type``/``okf_spec`` frontmatter is added above the first ``## `` (REQ-OKF-010,
      hash-neutral -> REQ-OKF-MIG-003).

    ``--dry-run`` returns the :class:`ChangePlan` WITHOUT mutating the folder (the
    mode Epic 2's impact assessment relies on). Merge-and-preserves foreign keys
    (REQ-OKF-070); report-only/crash-safe on messy input (REQ-OKF-071).
    """
    d = Path(directory)
    ext = resolve_extension(skill)
    member = ext.member if ext.found else None
    plan = ChangePlan(directory=str(d), dry_run=dry_run, skill=skill, member=member)

    # Member-driven config, with the legacy plan-shaped defaults when no extension
    # resolves (keeps behaviour sane for a bare bundle with no OKF-EXTENSION.md).
    rules = type_map if type_map is not None else (ext.type_map if ext.found else [])
    default_type = ext.default_type if ext.found else "Concept"
    index_source = ext.index_source if (ext.found and ext.index_source) else ("README.md" if not ext.found else None)
    log_source = ext.log_source if (ext.found and ext.log_source) else ("plan.md:phase-log" if not ext.found else None)

    if not d.is_dir():
        return plan

    # 1. index.md reconciliation (member-driven, REQ-OKF-MIG-005)
    if not (d / "index.md").exists():
        src = index_source
        if src and src != "scaffold" and (d / src).exists():
            plan.add("rename", src, to="index.md")
            if not dry_run:
                try:
                    (d / "index.md").write_text((d / src).read_text())
                    (d / src).unlink()
                except Exception as exc:  # report-only
                    plan.add("error", src, message=str(exc))
        else:
            # no member index source present -> synthesize a conformant skeleton
            plan.add("scaffold-index", "index.md", reason=(f"no {src} present" if src and src != "scaffold" else "member scaffolds index.md"))
            if not dry_run:
                try:
                    (d / "index.md").write_text(render_index(d))
                except Exception as exc:
                    plan.add("error", "index.md", message=str(exc))

    # The file renamed to index.md is skipped by the frontmatter pass below.
    index_renamed = index_source if (index_source and index_source != "scaffold") else None

    # 2. log.md reconciliation (member-driven, REQ-OKF-MIG-005)
    if not (d / "log.md").exists():
        produced_log = False
        if log_source and ":phase-log" in log_source:
            srcfile = log_source.split(":", 1)[0]
            sp = d / srcfile
            if sp.exists():
                try:
                    ptext = sp.read_text()
                except Exception as exc:
                    ptext = ""
                    plan.add("error", srcfile, message=str(exc))
                m = _PHASE_LOG_RE.search(ptext)
                if m:
                    block = m.group("block")
                    first = _first_scoping_date(block)
                    # Transcribe every dated bullet (review: lines included) so the
                    # REQ-PORT-006 count-equality invariant survives migration — not
                    # just the first scoping: date (REQ-OKF-MIG-002 floor).
                    bullets = _phase_log_bullets(block)
                    # extract-log (I-3): plan.md is NOT renamed — source_kept: True.
                    plan.add("extract-log", srcfile, to="log.md", source_kept=True,
                             first_scoping_date=first, entries=len(bullets))
                    produced_log = True
                    if not dry_run:
                        try:
                            if bullets:
                                # Oldest-first append; append_log prepends each entry
                                # (newest-first) and folds same-date bullets under one
                                # heading, preserving every <status>: token.
                                for bdate, rest in bullets:
                                    append_log(d, rest, date=bdate)
                            elif first:
                                append_log(d, f"scoping: {first} (migrated from **Phase log:**)", date=first)
                            else:
                                append_log(d, "migrated from **Phase log:**")
                            # remove the block (above first ## -> hash-neutral, REQ-OKF-MIG-003)
                            sp.write_text(ptext[: m.start()] + ptext[m.end():])
                        except Exception as exc:
                            plan.add("error", srcfile, message=str(exc))
        if not produced_log:
            # member has no in-body log source (research/incubator) -> skeleton
            plan.add("scaffold-log", "log.md", reason="member scaffolds log.md")
            if not dry_run and not (d / "log.md").exists():
                try:
                    (d / "log.md").write_text("# Log\n\n")
                except Exception as exc:
                    plan.add("error", "log.md", message=str(exc))

    # 3. Add type/okf_spec (+ dual-field mirror) to non-reserved .md lacking it.
    for md in sorted(d.rglob("*.md")):
        if md.name in RESERVED_FILES:
            continue
        rel = str(md.relative_to(d))
        if index_renamed and rel == index_renamed:
            continue  # becomes reserved index.md
        try:
            fm, _ = read_frontmatter(md)
        except OKFParseError as exc:
            plan.add("skip", rel, reason=f"malformed frontmatter: {exc}")
            continue
        except Exception as exc:
            plan.add("skip", rel, reason=str(exc))
            continue

        # Dual-field mirror (REQ-OKF-020): lift legacy **Field:** header lines into
        # frontmatter (keys present only in the **Field:** surface, not frontmatter).
        try:
            model = read_fields(md)
        except OKFParseError:
            model = dict(fm)
        mirror = {k: v for k, v in model.items()
                  if k not in fm and k not in (TYPE_KEY, OKF_SPEC_KEY)}

        existing_type = fm.get(TYPE_KEY)
        has_type = isinstance(existing_type, str) and existing_type.strip()
        needs_type = not has_type
        needs_spec = OKF_SPEC_KEY not in fm and member is not None
        if not (needs_type or needs_spec or mirror):
            continue

        matched = True
        if has_type:
            assigned_type = existing_type
        else:
            assigned_type, matched = _assign_type(rel, rules, default_type)

        keys: dict = {}
        if needs_type:
            keys[TYPE_KEY] = assigned_type
        if needs_spec:
            keys[OKF_SPEC_KEY] = member
        keys.update(mirror)

        detail: dict = {"keys": keys}
        if needs_type and not matched:
            detail["type_source"] = "default-fallback"
        if mirror:
            detail["mirrored_fields"] = sorted(mirror.keys())
        plan.add("add-frontmatter", rel, **detail)
        if not dry_run:
            try:
                write_frontmatter(md, keys)
            except Exception as exc:
                plan.add("error", rel, message=str(exc))

    return plan


# ---------------------------------------------------------------------------
# reindex — root-scoped index generation and drift detection (REQ-OKF-011)
# ---------------------------------------------------------------------------

#: Generated-region markers. Text OUTSIDE these regions is author prose and is
#: carried through verbatim by ``reindex --write`` (REQ-OKF-072).
INDEX_MARKERS: tuple[tuple[str, str], ...] = (
    ("<!-- intro:start -->", "<!-- intro:end -->"),
    ("<!-- notes:start -->", "<!-- notes:end -->"),
)

#: `- [title](target)` or `- [title](target) - description`
# NOTE: every horizontal-space class here is `[ \t]`, never `\s`. `\s` matches a
# NEWLINE, so `(?:\s+-\s+(?P<desc>.*))?` let the optional description separator
# span a line break and swallow the FOLLOWING bullet as the current entry's
# description — parsing `- [a](a)\n- [b](b)` as ONE entry and silently dropping
# every alternate entry. Caught by test_reindex_ghost_covers_dead_files_and_dead_dirs.
_INDEX_ENTRY_RE = re.compile(r"^[ \t]*[-*][ \t]+\[(?P<title>[^\]]*)\]\((?P<target>[^)]+)\)"
                             r"(?:[ \t]+-[ \t]+(?P<desc>.*?))?[ \t]*$", re.MULTILINE)

# reindex verdicts, mapped to the process exit code (REQ-OKF-011).
REINDEX_EXIT = {"clean": 0, "drift": 1, "no-index": 2}


class MarkerImbalanceError(Exception):
    """An ``<!-- x:start -->`` with no matching ``<!-- x:end -->`` (REQ-OKF-072).

    HARD ERROR, deliberately. An unbalanced marker leaves the generated region
    unbounded, so regenerating would discard author prose *unrecoverably* — the
    one failure in this engine that cannot be reconstructed from the artifact.
    """


def _index_entries(text: str) -> list[tuple[str, str, str]]:
    """``[(title, target, description)]`` parsed from an index body."""
    return [(m.group("title"), m.group("target").strip(), (m.group("desc") or "").strip())
            for m in _INDEX_ENTRY_RE.finditer(text)]


def check_markers(text: str) -> None:
    """Raise :class:`MarkerImbalanceError` on an unbalanced generated-region marker."""
    for start, end in INDEX_MARKERS:
        if text.count(start) != text.count(end):
            raise MarkerImbalanceError(
                f"unbalanced index marker: {text.count(start)}x {start!r} vs "
                f"{text.count(end)}x {end!r} — refusing to regenerate, prose would be lost")


def _listing_members(bundle: Path) -> list[str]:
    """Direct children that belong in a root listing: files and non-empty subdirs.

    Reserved files and dot-prefixed entries are excluded (REQ-OKF-001/031).
    """
    out: list[str] = []
    for child in sorted(bundle.iterdir()):
        if child.name in RESERVED_FILES or child.name.startswith("."):
            continue
        if child.is_dir():
            # An EMPTY directory is not a listing member. git does not track empty
            # directories, so it is absent from every clone — listing it asserts
            # something that is false everywhere but the machine that made it.
            # Producer and checker must agree on this predicate or the producer's
            # correct output reads as `missing` here.
            try:
                if not any(child.iterdir()):
                    continue
            except OSError:
                continue
            out.append(child.name + "/")
        elif child.is_file():
            # ALL direct file children, not only `.md`. OKF v0.2 §8: an index
            # "enumerates the directory's contents". Research bundles carry
            # `plan.yaml` / `sources*.json` pipeline sidecars a cold reader needs
            # listed. Note this is a different axis from REQ-OKF-060, which
            # excludes non-`.md` from FRONTMATTER conformance — a sidecar is a
            # listing member without being a concept document.
            out.append(child.name)
    return out


def _covered_by_listed_children(member: str, listed: set[str]) -> bool:
    """Is directory ``member`` already represented by listed entries INSIDE it?

    A bare `- [artifacts/](artifacts/)` beside
    `- [artifacts/critique.md](artifacts/critique.md) - [critique] Red-team: …`
    adds no information and **dilutes** the property that makes a root index
    worth having: research root indexes beat nested ones precisely because they
    enumerate individual files with rich, phase-tagged descriptions (exp-003).

    So a directory is suppressed when its children are listed, and emitted when
    they are not. Both `reindex_check` (which must not call it `missing`) and
    `reindex_write` (which must not add it) use this one predicate — if they
    disagreed, the producer's correct output would read as drift.
    """
    if not member.endswith("/"):
        return False
    prefix = member                      # e.g. "artifacts/"
    return any(t.startswith(prefix) and t != prefix for t in listed)


def reindex_check(bundle: Union[str, Path]) -> dict:
    """Report root-index drift for ``bundle`` without mutating anything.

    Verdict is three-way (REQ-OKF-011): ``clean`` / ``drift`` / ``no-index``.
    ``no-index`` never collapses into either neighbour — a bundle with no
    ``index.md`` is neither in nor out of agreement with one, and counting it
    clean would let an index-less bundle pass as green.

    Finding kinds:
      ``ghost``      an entry whose relative target does not resolve (dead file
                     OR dead directory — both, since a listing may point at either)
      ``missing``    a listing member present on disk but absent from the index
      ``empty-dir``  a listed subdirectory that contains nothing
    """
    b = Path(bundle)
    idx = b / "index.md"
    result: dict = {"command": "reindex", "mode": "check", "bundle": str(b),
                    "verdict": "clean", "findings": [], "counts": {}}
    if not idx.exists():
        result["verdict"] = "no-index"
        result["exit"] = REINDEX_EXIT["no-index"]
        return result

    text = idx.read_text()
    entries = _index_entries(text)
    findings: list[dict] = []

    # --- ghost + empty-dir: every entry target must resolve --------------------
    listed: set[str] = set()
    for title, target, _desc in entries:
        if "://" in target or target.startswith("#"):
            continue  # external / in-page anchor: not a bundle path claim
        clean = target.split("#", 1)[0].split("?", 1)[0]
        if not clean:
            continue
        listed.add(clean.rstrip("/") + ("/" if clean.endswith("/") else ""))
        resolved = (b / clean).resolve()
        if not resolved.exists():
            findings.append({"kind": "ghost", "entry": title, "target": target,
                             "detail": "entry target does not resolve"})
        elif resolved.is_dir() and not any(resolved.iterdir()):
            findings.append({"kind": "empty-dir", "entry": title, "target": target,
                             "detail": "listed subdirectory is empty"})

    # --- missing: on disk but not listed --------------------------------------
    def _norm(x: str) -> str:
        return x.rstrip("/")

    listed_norm = {_norm(x) for x in listed}
    # A subdir may legitimately be listed as `sub/`, `sub`, or `sub/index.md`.
    listed_norm |= {_norm(x[: -len("/index.md")]) for x in listed if x.endswith("/index.md")}
    raw_listed = {t for _, t, _ in entries}
    for member in _listing_members(b):
        if _norm(member) in listed_norm:
            continue
        if _covered_by_listed_children(member, raw_listed):
            continue                     # children already listed with descriptions
        findings.append({"kind": "missing", "entry": member, "target": member,
                         "detail": "present in the bundle but absent from index.md"})

    result["findings"] = findings
    result["counts"] = {k: sum(1 for f in findings if f["kind"] == k)
                        for k in ("ghost", "missing", "empty-dir")}
    result["verdict"] = "drift" if findings else "clean"
    result["exit"] = REINDEX_EXIT[result["verdict"]]
    return result


def discarded_prose(before: str, after: str) -> list[str]:
    """Non-generated lines present in ``before`` but absent from ``after``.

    WARNING-level by design (REQ-OKF-072): unlike a marker imbalance, a dropped
    line is recoverable from git, so a warning is proportionate. Listing bullets
    are excluded — those are the generated content, and their churn is the point.
    """
    def _prose(t: str) -> list[str]:
        return [ln.rstrip() for ln in t.splitlines()
                if ln.strip() and not _INDEX_ENTRY_RE.match(ln)]
    kept = set(_prose(after))
    return [ln for ln in _prose(before) if ln not in kept]


def _split_listing(body: str) -> tuple[str, list[str], str]:
    """Split an index body into ``(head_prose, bullet_lines, tail_prose)``.

    The listing is the contiguous run from the first bullet to the last. Prose
    before and after it is authored content and is carried through verbatim —
    which is what makes regeneration safe on a corpus whose indexes were all
    hand-written and carry no markers.
    """
    lines = body.splitlines(keepends=True)
    idxs = [i for i, ln in enumerate(lines) if _INDEX_ENTRY_RE.match(ln)]
    if not idxs:
        return body, [], ""
    first, last = idxs[0], idxs[-1]
    return "".join(lines[:first]), lines[first:last + 1], "".join(lines[last + 1:])


def reindex_write(bundle: Union[str, Path], *, root: bool = True,
                  dry_run: bool = False) -> dict:
    """Regenerate ``bundle``'s root listing, PRESERVING author prose (REQ-OKF-072).

    Rules, in force order:

    * an unbalanced generated-region marker is a HARD ERROR
      (:class:`MarkerImbalanceError`) — the region is unbounded and prose would
      be lost unrecoverably;
    * prose outside the listing run (and outside any marker region) is carried
      through **verbatim**;
    * an existing entry that still resolves keeps its title AND its description —
      descriptions are never regenerated, because nothing can re-derive one;
    * a ghost entry is DROPPED;
    * a member on disk but not listed is APPENDED as a bare ``- [name](name)``.
      **A description is never invented** — emitting a placeholder would write an
      assertion that a description exists when none does.
    """
    b = Path(bundle)
    idx = b / "index.md"
    out: dict = {"command": "reindex", "mode": "write", "bundle": str(b),
                 "verdict": "clean", "changes": [], "warnings": [], "dry_run": dry_run}
    if not idx.exists():
        out["verdict"] = "no-index"
        out["exit"] = REINDEX_EXIT["no-index"]
        return out

    original = idx.read_text()
    check_markers(original)                      # hard error before any rewrite
    fm, body = read_frontmatter(idx)             # preserves okf_version as-is (D-2: no migration)
    head, bullets, tail = _split_listing(body)

    kept: list[str] = []
    listed_norm: set[str] = set()
    for ln in bullets:
        m = _INDEX_ENTRY_RE.match(ln)
        target = m.group("target").strip()
        clean = target.split("#", 1)[0].split("?", 1)[0]
        if "://" in target or target.startswith("#") or not clean:
            kept.append(ln)                      # external link: not a bundle claim
            continue
        if (b / clean).exists():
            kept.append(ln)
            listed_norm.add(clean.rstrip("/"))
            if clean.endswith("/index.md"):
                listed_norm.add(clean[: -len("/index.md")].rstrip("/"))
        else:
            out["changes"].append({"op": "drop-ghost", "target": target})

    raw_listed = set()
    for ln in kept:
        mm = _INDEX_ENTRY_RE.match(ln)
        if mm:
            raw_listed.add(mm.group("target").strip())
    for member in _listing_members(b):
        if member.rstrip("/") in listed_norm:
            continue
        if _covered_by_listed_children(member, raw_listed):
            continue                     # children already listed with descriptions
        kept.append(f"- [{member}]({member})\n")
        out["changes"].append({"op": "add-missing", "target": member})

    new_body = head + "".join(kept) + tail
    new_text = (_dump_frontmatter(fm) if fm else "") + new_body
    out["warnings"] = [{"kind": "discarded-prose", "line": ln}
                       for ln in discarded_prose(original, new_text)]
    out["text"] = new_text
    out["changed"] = new_text != original
    if out["changed"] and not dry_run:
        idx.write_text(new_text)
    out["verdict"] = "clean"
    out["exit"] = 0
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _cmd_check(args) -> int:
    findings = check_conformance(args.dir, skill=args.skill)
    if args.json:
        out = {"command": "check", "dir": str(args.dir), **findings.as_dict()}
        print(json.dumps(out, indent=2))
    else:
        print(f"check {args.dir}: {'OK' if findings.ok else 'FAIL'} "
              f"(composed: {', '.join(findings.rulesets_composed)})")
        for f in findings.findings:
            print(f"  [{f.level}] {f.path}: {f.req} — {f.message}")
    return 0 if findings.ok else 1


def _cmd_migrate(args) -> int:
    plan = migrate(args.dir, dry_run=args.dry_run, skill=args.skill)
    if args.json:
        print(json.dumps(plan.as_dict(), indent=2))
    else:
        verb = "would apply" if args.dry_run else "applied"
        print(f"migrate {args.dir}: {verb} {len(plan.changes)} change(s)")
        for c in plan.changes:
            print(f"  - {c.op} {c.path} {c.detail or ''}")
    return 0


def _cmd_reindex(args) -> int:
    """`reindex` exits 0 clean / 1 drift / 2 no-index (REQ-OKF-011)."""
    try:
        res = reindex_write(args.dir, dry_run=args.dry_run) if args.write \
            else reindex_check(args.dir)
    except MarkerImbalanceError as exc:
        res = {"command": "reindex", "bundle": str(args.dir), "verdict": "error",
               "error": str(exc), "exit": 1}
        print(json.dumps(res, indent=2) if args.json else f"reindex {args.dir}: ERROR — {exc}")
        return 1
    if args.json:
        print(json.dumps({k: v for k, v in res.items() if k != "text"}, indent=2))
    else:
        print(f"reindex {args.dir}: {res['verdict']}")
        for f in res.get("findings", []):
            print(f"  [{f['kind']}] {f['target']} — {f['detail']}")
        for c in res.get("changes", []):
            print(f"  {c['op']}: {c['target']}")
        for w in res.get("warnings", []):
            print(f"  [warning] discarded prose: {w['line']}")
    return res["exit"]


def _cmd_scaffold(args) -> int:
    d = scaffold_bundle(args.dir, spec_member=args.member, subdirs=args.subdir or ())
    if args.json:
        print(json.dumps({"command": "scaffold", "dir": str(d)}, indent=2))
    else:
        print(f"scaffold: created bundle skeleton at {d}")
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    # Shared options accepted both before and after the subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="emit JSON output")
    common.add_argument("--skill", default=None, help="per-skill OKF-EXTENSION.md to compose")

    parser = argparse.ArgumentParser(description="OKF bundle engine (yf-okf).", parents=[common])
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", parents=[common], help="conformance self-check (report-only)")
    p_check.add_argument("dir", type=Path)
    p_check.set_defaults(func=_cmd_check)

    p_mig = sub.add_parser("migrate", parents=[common], help="opt-in in-place migration")
    p_mig.add_argument("dir", type=Path)
    p_mig.add_argument("--dry-run", action="store_true", help="emit change plan without writing")
    p_mig.set_defaults(func=_cmd_migrate)

    p_ri = sub.add_parser("reindex", parents=[common],
                          help="root-scoped index generation + drift report")
    p_ri.add_argument("dir", type=Path)
    p_ri.add_argument("--check", action="store_true", help="report drift (default)")
    p_ri.add_argument("--write", action="store_true", help="regenerate, preserving prose")
    p_ri.add_argument("--dry-run", action="store_true", help="with --write: do not write")
    p_ri.set_defaults(func=_cmd_reindex)

    p_sc = sub.add_parser("scaffold", parents=[common], help="create an OKF bundle skeleton")
    p_sc.add_argument("dir", type=Path)
    p_sc.add_argument("--member", default=None, help="okf_spec member name")
    p_sc.add_argument("--subdir", action="append", help="reserved subdir (repeatable)")
    p_sc.set_defaults(func=_cmd_scaffold)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
