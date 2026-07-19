# /// script
# requires-python = ">=3.11"
# dependencies = ["click>=8.1", "pyyaml"]
# ///
"""Research index manager (OKF-RESEARCH adapter).

Manages the reserved OKF bundle files for a research topic and stamps OKF
frontmatter on the bundle's concept docs. Delegates all frontmatter / index /
log rendering to the vendored OKF engine (`okf.py`, a sibling module).

Roles (REQ-PORT-009 / OKF-EXTENSION §5 — the reconciliation decision):

* `index.md` (renamed from the legacy `_index.md`) — the OKF bundle **listing**:
  an `okf_version` frontmatter block + a `# Research Index: <topic>` heading +
  `- [artifact](path) - [phase] description` bullets. Reserved: carries no
  `type` / `okf_spec` (REQ-OKF-031).
* `log.md` — the newest-first ISO-8601 **update ledger** that the single legacy
  `_index.md` timestamped table used to double as. Each `add` appends a dated
  bullet carrying the full `YYYY-MM-DDTHH:MM` timestamp. Reserved: no
  `type` / `okf_spec`.

The legacy `_index.md` was one timestamped GFM table
(`| Timestamp | Phase | Artifact | Description |`) that conflated the manifest
and the ledger; OKF splits those roles across `index.md` (listing) and `log.md`
(ledger). Per-entry `Phase` is folded into each `index.md` bullet's description
as a `[phase]` annotation (dropped from a column; retained verbatim in `log.md`).

`add` also stamps OKF frontmatter on the artifact it registers when that artifact
is a non-reserved `.md` (Summary.md -> `Research Report`, artifacts/*.md ->
`Research Artifact`, sources.md -> `Reference`; each with `okf_spec: OKF-RESEARCH`).
`Summary.md` additionally gets its inline prose-header fields dual-written as
`idx` / `topic` / `created` / `status` frontmatter keys (OKF-EXTENSION §2/§4).
Non-`.md` sidecars (`plan.yaml`, `sources.json`, `diagrams/*.png`, `scripts/*.py`)
are excluded (REQ-PORT-008).
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import click

import okf  # vendored OKF engine (sibling module)

INDEX_FILENAME = "index.md"
LOG_FILENAME = "log.md"

#: Member selector fallback if the vendored extension cannot be resolved
#: (resolve_extension is __file__-relative to okf.py, so this is belt-and-braces).
OKF_MEMBER = "OKF-RESEARCH"


def _index_path(research_dir: str) -> Path:
    return Path(research_dir) / INDEX_FILENAME


def _log_path(research_dir: str) -> Path:
    return Path(research_dir) / LOG_FILENAME


_BULLET_RE = re.compile(r"^- \[.*?\]\((?P<path>[^)]*)\)(?: - (?P<desc>.*))?$")
_PHASE_RE = re.compile(r"^\[(?P<phase>[^\]]+)\]\s*(?P<rest>.*)$")


def _parse_rows(content: str) -> list[dict]:
    """Parse the OKF listing bullets from index.md into artifact rows.

    Recovers the `[phase]` annotation folded into each bullet description
    (see module docstring / REQ-PORT-009)."""
    rows = []
    for line in content.splitlines():
        line = line.strip()
        m = _BULLET_RE.match(line)
        if not m:
            continue
        desc = (m.group("desc") or "").strip()
        phase = ""
        pm = _PHASE_RE.match(desc)
        if pm:
            phase = pm.group("phase").strip()
            desc = pm.group("rest").strip()
        rows.append({
            "phase": phase,
            "artifact": m.group("path"),
            "description": desc,
        })
    return rows


# --- OKF frontmatter stamping ----------------------------------------------

_HEADER_TOKEN_RE = {
    "project": re.compile(r"\*\*Research project:\*\*\s*(?P<v>[^\n·|]+)"),
    "phase": re.compile(r"\*\*Phase:\*\*\s*(?P<v>[^\n·|]+)"),
    "date": re.compile(r"\*\*Date:\*\*\s*(?P<v>[^\n·|]+)"),
}
_IDX_SLUG_RE = re.compile(r"^\s*(?P<idx>\d+)-(?P<slug>.+?)\s*$")


def _summary_member_keys(text: str, research_dir: str) -> dict:
    """Dual-write keys for Summary.md (OKF-EXTENSION §2/§4): parse the inline
    prose header line `**Research project:** NNN-slug · **Phase:** … · **Date:** …`
    into idx / topic / created / status. idx/topic fall back to the research
    directory name (`<NNN>-<slug>`) when the header is absent."""
    keys: dict = {}
    idx = topic = None

    pm = _HEADER_TOKEN_RE["project"].search(text)
    if pm:
        proj = pm.group("v").strip()
        sm = _IDX_SLUG_RE.match(proj)
        if sm:
            idx, topic = sm.group("idx"), sm.group("slug")
        else:
            topic = proj

    if idx is None or topic is None:
        dm = _IDX_SLUG_RE.match(Path(research_dir).name)
        if dm:
            idx = idx or dm.group("idx")
            topic = topic or dm.group("slug")

    if idx:
        keys["idx"] = idx
    if topic:
        keys["topic"] = topic
    dm2 = _HEADER_TOKEN_RE["date"].search(text)
    if dm2:
        keys["created"] = dm2.group("v").strip()
    phm = _HEADER_TOKEN_RE["phase"].search(text)
    if phm:
        keys["status"] = phm.group("v").strip()
    return keys


def _stamp_artifact(research_dir: str, artifact: str) -> str | None:
    """Merge OKF `type` + `okf_spec` (+ Summary.md dual-field keys) into the
    artifact's frontmatter, above the first `## ` (REQ-OKF-010), merge-and-
    preserving existing keys (REQ-OKF-070). Delegates type assignment and the
    frontmatter write to the vendored engine.

    Returns the assigned type, or None when the artifact is skipped (non-`.md`
    sidecar per REQ-PORT-008, reserved file, or the file does not exist)."""
    if not artifact.endswith(".md"):
        return None  # non-.md sidecar — excluded (REQ-PORT-008)
    name = Path(artifact).name
    if name in okf.RESERVED_FILES:
        return None  # reserved index.md / log.md carry no type/okf_spec
    p = Path(research_dir) / artifact
    if not p.exists():
        return None

    ext = okf.resolve_extension()  # yf-research's own extension (vendored, __file__-relative)
    rel = Path(artifact).as_posix()
    assigned_type, _matched = okf._assign_type(rel, ext.type_map, ext.default_type)
    member = ext.member or OKF_MEMBER

    meta: dict = {okf.TYPE_KEY: assigned_type, okf.OKF_SPEC_KEY: member}
    if name == "Summary.md":
        meta.update(_summary_member_keys(p.read_text(), research_dir))
    okf.write_frontmatter(p, meta)
    return assigned_type


@click.group()
def cli():
    """Manage a research topic's reserved OKF index.md / log.md and stamp
    OKF frontmatter on the bundle's concept docs."""
    pass


@cli.command()
@click.argument("research_dir")
@click.argument("topic")
def init(research_dir: str, topic: str):
    """Initialize the reserved index.md + log.md for a research topic."""
    path = _index_path(research_dir)
    if path.exists():
        click.echo(f"{INDEX_FILENAME} already exists at {path}", err=True)
        return

    Path(research_dir).mkdir(parents=True, exist_ok=True)
    # index.md: okf_version frontmatter (engine-rendered) + listing heading.
    fm_text = okf.write_frontmatter(path, {"okf_version": okf.okf_version}, dry_run=True)
    path.write_text(fm_text + f"\n# Research Index: {topic}\n\n")
    # log.md: newest-first ISO-8601 ledger skeleton.
    log = _log_path(research_dir)
    if not log.exists():
        log.write_text("# Log\n\n")
    click.echo(f"Created {path} and {log}")


@cli.command()
@click.argument("research_dir")
@click.argument("phase")
@click.argument("artifact")
@click.argument("description")
@click.option("--timestamp", "-t", default=None, help="Override timestamp (ISO format)")
def add(research_dir: str, phase: str, artifact: str, description: str, timestamp: str | None):
    """Register an artifact: append an index.md listing bullet, a timestamped
    log.md ledger entry, and stamp the artifact's OKF frontmatter."""
    path = _index_path(research_dir)
    if not path.exists():
        click.echo(f"ERROR: {path} does not exist. Run 'init' first.", err=True)
        raise SystemExit(1)

    ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M")

    # index.md listing bullet (phase folded into the description annotation).
    okf.add_index_entry(research_dir, artifact, f"[{phase}] {description}")

    # log.md newest-first ledger entry (full timestamp retained here).
    okf.append_log(
        research_dir,
        f"{ts} · [{phase}] {artifact} — {description}",
        date=ts[:10],
    )

    # Stamp OKF frontmatter on the registered concept doc (non-reserved .md only).
    stamped = _stamp_artifact(research_dir, artifact)

    suffix = f" (stamped {stamped})" if stamped else ""
    click.echo(f"Added: {phase} / {artifact}{suffix}")


@cli.command("list")
@click.argument("research_dir")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
@click.option("--phase", "-p", default=None, help="Filter by phase")
def list_entries(research_dir: str, json_output: bool, phase: str | None):
    """List artifacts registered in index.md."""
    path = _index_path(research_dir)
    if not path.exists():
        click.echo(f"ERROR: {path} does not exist.", err=True)
        raise SystemExit(1)

    rows = _parse_rows(path.read_text())

    if phase:
        rows = [r for r in rows if r["phase"].upper() == phase.upper()]

    if json_output:
        click.echo(json.dumps(rows, indent=2))
    else:
        for r in rows:
            click.echo(f"  [{r['phase']}]  {r['artifact']}  — {r['description']}")


if __name__ == "__main__":
    cli()
