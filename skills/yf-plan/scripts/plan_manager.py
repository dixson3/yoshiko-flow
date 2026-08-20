# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "click>=8.1",
#     "pyyaml>=6",
# ]
# ///
"""Plan manager utility for the /yf-plan skill.

Handles plan directory creation, index management, status queries,
and plan.md generation/updates.
"""

import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import click

# Vendored OKF engine (byte-identical to _shared/okf.py; synced by _shared/sync.py).
# Imported as a scripts/ sibling — same address-space convention as the defensive
# json extractor / manifest_update precedent (no cross-skill imports). Providing the
# dual-mode frontmatter+**Field:** field model (REQ-DATA-015 / REQ-OKF-020/021).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import okf  # noqa: E402
import plan_template  # noqa: E402

# --- Config tiers (REQ-YF-PRE-004 / REQ-YF-PRE-004a) --------------------------
# The short name (`plan`, not `yf-plan`) is what the `yf` binary emits, so the
# canonical dirs below match `preflight.rs` exactly. Three tiers, merged KEY BY KEY
# with the highest present tier winning each key:
#
#   1. .yf/plan/config.local.json   gitignored — machine-specific operator overrides
#   2. .yf/plan/config.json         COMMITTED  — shared, repo-carried decisions
#   3. .yf-plan.local.json          gitignored — legacy root dotfile, read-only fallback
#
# Merge (not whole-file first-match) is required for tier 2 to be useful: a local
# file setting only `landing-strategy` must not mask a committed `plans-root`.
# With a single tier present the two semantics coincide, so this is backward
# compatible. `yf/src/preflight.rs::read_config` implements the same three tiers —
# two readers disagreeing about precedence is the drift #100 exists to remove.
SKILL_SHORT = "plan"
YF_DIR = Path(".yf") / SKILL_SHORT
CONFIG_LOCAL_FILE = YF_DIR / "config.local.json"
CONFIG_SHARED_FILE = YF_DIR / "config.json"
LEGACY_CONFIG_FILE = Path(".yf-plan.local.json")
CONFIG_TIERS = (CONFIG_LOCAL_FILE, CONFIG_SHARED_FILE, LEGACY_CONFIG_FILE)


def _bootstrap_config() -> dict:
    """Read + merge the config tiers with no module-level dependencies.

    Called at import time because `PLANS_DIR` / `INCUBATOR_PARENT` are module
    constants bound before most of this module exists (REQ-PLAN-073, import-safe
    resolution). Deliberately dependency-free — it runs before `_read_json` is
    defined — and deliberately total: a malformed or unreadable tier is skipped,
    never raised, so a bad config file cannot make the module unimportable.

    Tiers are applied lowest-first so the highest tier wins each key.
    """
    cfg: dict = {}
    for path in reversed(CONFIG_TIERS):
        try:
            if path.exists():
                loaded = json.loads(path.read_text())
                if isinstance(loaded, dict):
                    cfg.update(loaded)
        except (json.JSONDecodeError, OSError, ValueError):
            continue
    return cfg


_CONFIG = _bootstrap_config()

# Repo layout is configurable (REQ-PLAN-073 / #107): a project whose plan or
# incubator roots are not the defaults — e.g. a repo that is also an Obsidian
# vault, where a visible top-level `Incubator/` trips the vault's structure
# linter — sets `plans-root` / `incubator-root`. These belong in the COMMITTED
# tier: plan-id numbering is global across roots, so two clones disagreeing about
# the root would silently fragment it.
PLANS_DIR = Path(str(_CONFIG.get("plans-root") or "docs/plans"))
INCUBATOR_PARENT = Path(str(_CONFIG.get("incubator-root") or "Incubator"))

# Dual-field model (REQ-DATA-015 / OKF-EXTENSION.md §4): a single in-memory model
# maps each frontmatter key to its human `**Field:**` label. Reads are
# frontmatter-first with `**Field:**` fallback; writes emit BOTH surfaces.
PLAN_FIELD_LABELS = {
    "id": "ID",
    "author": "Author",
    "created": "Created",
    "status": "Status",
    "deliverable_class": "Deliverable-class",
    "epic": "Epic",
    "fingerprint": "Fingerprint",
}
#: Canonical header-field ordering for the `**Field:**` block.
#: `deliverable_class` sits immediately after `status` (REQ-DATA-015 / REQ-PLAN-069a);
#: being a registered field it survives every `_rebuild_field_block` rewrite.
PLAN_FIELD_ORDER = ("id", "author", "created", "status", "deliverable_class",
                    "epic", "fingerprint")

#: Deliverable-class values (REQ-PLAN-069a). `ci-release` is the gated class;
#: `standard` (the default when the field is absent) makes the completion gate a no-op.
DELIVERABLE_CLASSES = ("standard", "ci-release")


def _read_plan_field(plan_md_text: str, key: str) -> str | None:
    """Single dual-mode header-field accessor (REQ-DATA-015 / REQ-OKF-021).

    Reads **frontmatter-first** via the vendored OKF engine and falls back to the
    legacy `**Field:**` header line when the key is absent from frontmatter — so a
    migrated (frontmatter-bearing) plan and an un-migrated (frontmatter-free) plan
    resolve identically. `key` is a frontmatter key (`status`, `epic`,
    `fingerprint`, `id`, …). Returns None when neither surface carries the field.
    """
    try:
        model = okf.read_fields(plan_md_text)
    except okf.OKFParseError:
        model = {}
    val = model.get(key)
    if val is None:
        return None
    val = str(val).strip()
    return val or None


def _rebuild_field_block(text: str, model: dict[str, str]) -> str:
    """Rewrite the contiguous `**Field:**` header block from `model`.

    Emits one `**Label:** <value>` line per PLAN_FIELD_ORDER key present in `model`,
    replacing the existing contiguous span of identity-field lines (never the
    `**Phase log:**` block, which is not a PLAN_FIELD_LABELS label and is preserved
    verbatim for Issue 3.4 to relocate). If no field block exists yet, the block is
    inserted just after the `# ` title. Everything else — title, blank lines, phase
    log, and all `## ` content — is preserved, so the content fingerprint is
    unaffected (REQ-OKF-010).
    """
    lines = text.splitlines()
    prefixes = {f"**{lbl}:**": key for key, lbl in PLAN_FIELD_LABELS.items()}
    idxs: list[int] = []
    for i, line in enumerate(lines):
        if any(line.startswith(p) for p in prefixes):
            idxs.append(i)
    block = [f"**{PLAN_FIELD_LABELS[k]}:** {model[k]}"
             for k in PLAN_FIELD_ORDER if k in model]
    if idxs:
        start, end = idxs[0], idxs[-1]
        new_lines = lines[:start] + block + lines[end + 1:]
    else:
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("# "):
                insert_at = i + 1
                if insert_at < len(lines) and lines[insert_at].strip() == "":
                    insert_at += 1
                break
        new_lines = lines[:insert_at] + block + lines[insert_at:]
    return "\n".join(new_lines) + "\n"


def _write_plan_fields(plan_dir: Path, updates: dict[str, str]) -> None:
    """Single dual-writer (REQ-DATA-015 dual-write consistency / REQ-OKF-020).

    One in-memory model drives BOTH representations: the human `**Field:**` header
    block AND a merge-and-preserve YAML frontmatter block (delegated to the OKF
    engine). There is no path that writes one surface without the other. The model
    is the current header fields (read frontmatter-first) merged with `updates`, so
    every write re-lands both surfaces in sync. Both blocks sit above the first
    `## ` heading, hence neither perturbs the content fingerprint (REQ-OKF-010).
    """
    plan_md = plan_dir / "plan.md"
    text = plan_md.read_text()
    model: dict[str, str] = {}
    for k in PLAN_FIELD_ORDER:
        v = _read_plan_field(text, k)
        if v is not None:
            model[k] = v
    model.update({k: str(v) for k, v in updates.items()})
    # Surface 1: the human **Field:** block (preserves **Phase log:** + body).
    plan_md.write_text(_rebuild_field_block(text, model))
    # Surface 2: the YAML frontmatter block (merge-and-preserve foreign keys).
    okf.write_frontmatter(plan_md, dict(model))

# Skill Surface Convention (see skill-authoring/reference/SURFACE_CONVENTION.md):
# operator config vs runtime state. Preflight (deps + installed-rule hash + the
# idempotent gitignore scaffold) moved to the `yf preflight` kernel (plan-010);
# the constants below are what the surviving domain commands still need.
SKILL_NAME = "yf-plan"
# Config tiers are defined at the top of the module (they must resolve before
# PLANS_DIR / INCUBATOR_PARENT bind). `CONFIG_FILE` is retained as an alias for
# the legacy root dotfile so existing references keep working.
CONFIG_FILE = LEGACY_CONFIG_FILE
# Runtime cache, SHORT-name (`.yf/plan/`) as of #100 — the same dir the `yf`
# preflight kernel writes `preflight.json` into. State written by an earlier
# version under the full-name `.yf/yf-plan/` is migrated by `_migrate_state_dir`.
STATE_DIR = YF_DIR
LEGACY_STATE_DIR = Path(".yf") / SKILL_NAME               # pre-#100 full-name dir
GITIGNORE_FILE = Path(".gitignore")


def _migrate_state_dir() -> list[str]:
    """Move pre-#100 full-name `.yf/yf-plan/` state into short-name `.yf/plan/`.

    Idempotent and non-destructive: an entry already present at the destination is
    left alone (the canonical copy wins) and the legacy one is removed. The legacy
    dir is removed only once empty. Returns the names moved, for reporting.

    State is a gitignored cache, so a failure here is never fatal — a migration
    error leaves the legacy file in place and the caller simply starts cold.
    """
    moved: list[str] = []
    if not LEGACY_STATE_DIR.is_dir() or LEGACY_STATE_DIR == STATE_DIR:
        return moved
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        for src in LEGACY_STATE_DIR.iterdir():
            dst = STATE_DIR / src.name
            if dst.exists():
                if src.is_file():
                    src.unlink()
                continue
            src.replace(dst)
            moved.append(src.name)
        if not any(LEGACY_STATE_DIR.iterdir()):
            LEGACY_STATE_DIR.rmdir()
    except OSError:
        return moved
    return moved


_migrate_state_dir()


# >>> BEGIN defensive json extractor (generated by _shared/sync.py — edit _shared/json_extract.py) >>>
def _extract_first_json(text: str):
    """Defensively extract the first balanced JSON value from text.

    bd's --json output may carry a warning prefix and/or be a concatenated array
    (notably `bd show`/`bd list`). Strip to the first balanced {...} or [...] block
    and parse that. Raises ValueError if none parses.
    """
    open_to_close = {"{": "}", "[": "]"}
    for i, ch in enumerate(text):
        if ch in open_to_close:
            depth = 0
            in_str = False
            esc = False
            for j in range(i, len(text)):
                c = text[j]
                if in_str:
                    if esc:
                        esc = False
                    elif c == "\\":
                        esc = True
                    elif c == '"':
                        in_str = False
                    continue
                if c == '"':
                    in_str = True
                elif c in open_to_close:
                    depth += 1
                elif c in open_to_close.values():
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(text[i:j + 1])
                        except json.JSONDecodeError:
                            break
            # this opener didn't yield a parse; try the next one
    raise ValueError("no balanced JSON value found in input")
# <<< END defensive json extractor (generated by _shared/sync.py — edit _shared/json_extract.py) <<<


def _git_root() -> Path:
    # Project anchor for project-scope rule installs. Falls back to cwd outside a
    # git repo (matches the SKILL_DIR resolver's `|| echo .`).
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=2)
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return Path(".")


# Tools probed by _detect_tools (Epic 1.4). Each is best-effort; missing tools
# are recorded as "not present" and never fail init.
DETECT_TOOLS = ("bd", "git", "uv", "python", "gh", "glab", "claude")
DETECT_TIMEOUT_SEC = 2

# Portability contract activation date (spec/portability.md REQ-PORT-ACT).
# Plans whose first scoping phase-log entry is on/after this date get hard
# audit failures for missing scaffolding. Older plans get warns (grandfather).
PORTABILITY_ACTIVATION_DATE = "2026-04-05"


def get_git_user() -> str:
    """Get normalized git username for plan IDs."""
    try:
        name = subprocess.check_output(
            ["git", "config", "user.name"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        name = os.environ.get("USER", "unknown")
    # Normalize: lowercase, spaces to hyphens, filename-safe
    return "".join(
        c if c.isalnum() or c == "-" else "-" for c in name.lower().replace(" ", "-")
    ).strip("-")


RESEARCH_DIR = Path("docs/research")


def list_plan_roots() -> list[Path]:
    """Return every directory that may hold `plan-*` dirs.

    Globally numbered plans live across `docs/plans/` and per-incubator
    `Incubator/<slug>/plans/` roots; this function returns all that exist on
    disk so callers can enumerate or count across the whole vault.
    """
    return _list_kind_roots("plans", PLANS_DIR)


def list_research_roots() -> list[Path]:
    """Return every directory that may hold research item dirs.

    Research lives across `docs/research/` (deep-research vault-default) and
    per-incubator `Incubator/<slug>/research/` roots. Items are either
    deep-research topics (`NNN-topic-slug/` with `plan.yaml`) or rehoused
    yf-plan plans (`plan-NNN-…/` with `plan.md`).
    """
    return _list_kind_roots("research", RESEARCH_DIR)


def _list_kind_roots(kind_dir: str, default_root: Path) -> list[Path]:
    roots: list[Path] = []
    if default_root.exists():
        roots.append(default_root)
    if INCUBATOR_PARENT.exists():
        for inc in INCUBATOR_PARENT.iterdir():
            if not inc.is_dir():
                continue
            p = inc / kind_dir
            if p.exists():
                roots.append(p)
    return roots


def _scope_for_root(root: Path, default_root: Path) -> str | None:
    """Return the incubator slug for a root, or None for the vault-default."""
    if root == default_root:
        return None
    try:
        return root.relative_to(INCUBATOR_PARENT).parts[0]
    except (ValueError, IndexError):
        return None


def _research_item_info(d: Path) -> dict | None:
    """Inspect a research-root child and classify it.

    Returns a dict for tracked items (deep-research topics or rehoused
    yf-plan plans); returns None for flat `.md` notes or other unstructured
    siblings that just happen to live alongside research items.
    """
    if not d.is_dir():
        return None
    plan_yaml = d / "plan.yaml"
    plan_md = d / "plan.md"

    if plan_yaml.exists():
        topic = d.name
        try:
            for line in plan_yaml.read_text().splitlines():
                stripped = line.strip()
                if stripped.startswith("topic:"):
                    topic = stripped.split(":", 1)[1].strip().strip('"').strip("'")
                    break
        except OSError:
            pass
        return {"id": d.name, "topic": topic, "kind": "research", "path": str(d)}

    if plan_md.exists() and d.name.startswith("plan-"):
        topic = d.name
        try:
            for line in plan_md.read_text().splitlines():
                if line.startswith("# Plan: "):
                    topic = line[8:].strip()
                    break
        except OSError:
            pass
        return {"id": d.name, "topic": topic, "kind": "rehoused-plan", "path": str(d)}

    return None


def detect_incubator_from_cwd() -> str | None:
    """Return the incubator slug if CWD is inside `Incubator/<slug>/...`."""
    try:
        cwd = Path.cwd().resolve()
    except OSError:
        return None
    try:
        parent_abs = INCUBATOR_PARENT.resolve()
    except (OSError, FileNotFoundError):
        return None
    try:
        rel = cwd.relative_to(parent_abs)
    except ValueError:
        return None
    parts = rel.parts
    return parts[0] if parts else None


def resolve_plans_dir(incubator: str | None = None) -> Path:
    """Choose the plans root for a new plan.

    - explicit `incubator` → `Incubator/<slug>/plans`
    - else falls back to `docs/plans`
    """
    if incubator:
        return INCUBATOR_PARENT / incubator / "plans"
    return PLANS_DIR


def get_next_index() -> int:
    """Get next plan index by counting every plan-* dir vault-wide.

    Counts plan-* directories under both plan roots and research roots so
    rehoused plans (e.g. an old yf-plan moved into `Incubator/<slug>/research/`)
    still consume a number and IDs stay globally unique.
    """
    total = 0
    for root in (*list_plan_roots(), *list_research_roots()):
        total += sum(
            1 for d in root.iterdir()
            if d.is_dir() and d.name.startswith("plan-")
        )
    return total + 1


def make_plan_id(objective: str) -> str:
    """Generate plan ID: plan-NNN-user-hash."""
    idx = f"{get_next_index():03d}"
    user = get_git_user()
    raw = f"{objective}{datetime.now().isoformat()}"
    h = hashlib.sha256(raw.encode()).hexdigest()[:6]
    return f"plan-{idx}-{user}-{h}"


def make_plan_dir(plan_id: str, plans_dir: Path | None = None) -> Path:
    """Create plan directory structure under the given root.

    `plans_dir` defaults to the configured `PLANS_DIR` (`plans-root`, default
    `docs/plans` — REQ-PLAN-073); callers that target an incubator should pass
    `resolve_plans_dir(incubator)`.
    """
    root = plans_dir if plans_dir is not None else PLANS_DIR
    plan_dir = root / plan_id
    (plan_dir / "findings").mkdir(parents=True, exist_ok=True)
    (plan_dir / "assets").mkdir(parents=True, exist_ok=True)
    (plan_dir / "diagrams").mkdir(parents=True, exist_ok=True)
    return plan_dir


# OKF-PLAN bundle construction (plan-029 Issue 3.3). Every non-reserved bundle `.md`
# is stamped `type` (role-mapped via the vendored engine's `_assign_type` over the
# OKF-EXTENSION.md §1a map) + `okf_spec: OKF-PLAN`, merge-and-preserved above the first
# `## ` (REQ-PORT-050 / REQ-OKF-003/010/030/070). Reserved `index.md`/`log.md` are
# exempt — they carry no `type`/`okf_spec` (REQ-OKF-031).
_OKF_MEMBER = "OKF-PLAN"
_okf_plan_ext_cache = None


def _okf_plan_extension():
    """Resolve + cache the vendored yf-plan `OKF-EXTENSION.md` ruleset (role→type map,
    member name). `__file__`-relative via the engine — independent of cwd."""
    global _okf_plan_ext_cache
    if _okf_plan_ext_cache is None:
        _okf_plan_ext_cache = okf.resolve_extension("yf-plan")
    return _okf_plan_ext_cache


def _stamp_okf_type(plan_dir: Path, md_path: Path) -> None:
    """Stamp `type` (role-mapped) + `okf_spec: OKF-PLAN` frontmatter onto a
    non-reserved bundle `.md` (REQ-PORT-050). The `type` is assigned from the bundle-
    relative path via the OKF-EXTENSION §1a map (`plan.md`→Plan, `context.md`→
    Environment, `references/*`→Reference, …), falling back to the member default.
    Merge-and-preserves existing keys and sits above the first `## ` (REQ-OKF-010/070).
    """
    ext = _okf_plan_extension()
    rel = str(md_path.relative_to(plan_dir))
    if ext.found and ext.type_map:
        typ, _matched = okf._assign_type(rel, ext.type_map, ext.default_type)
        member = ext.member or _OKF_MEMBER
    else:
        typ, member = "Concept", _OKF_MEMBER
    okf.write_frontmatter(md_path, {"type": typ, "okf_spec": member})


def seed_plan_md(plan_dir: Path, plan_id: str, objective: str, author: str) -> Path:
    """Create initial plan.md with scoping status.

    Issue 3.4 / REQ-DATA-012: the phase log no longer lives in plan.md — the initial
    `scoping:` entry is seeded into the reserved bundle-root `log.md` (newest-first)
    instead of a `**Phase log:**` block, so the first-`scoping:` grandfather date and
    the review-count invariant resolve from `log.md` from the plan's first moment.

    Issue 3.3 / REQ-PORT-050: plan.md is born OKF-conformant — a `type: Plan` +
    `okf_spec: OKF-PLAN` frontmatter block, dual-written with the `**Field:**` header
    lines via `_write_plan_fields` (REQ-OKF-020), both above the first `## `.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    # Canonical skeleton (plan-047 Issue 0.2): the literal lives in `plan_template.py`, a
    # sibling vendored from `_shared/` and read by BOTH this seeder and `_shared/sync.py`'s
    # SKILL.md emitter, so the written template and the documented one cannot diverge.
    content = plan_template.seed_body(
        objective=objective, plan_id=plan_id, author=author, created=today, status="scoping"
    )
    plan_md = plan_dir / "plan.md"
    plan_md.write_text(content)
    # Seed the initial scoping entry into the reserved `log.md` (Issue 3.4).
    okf.append_log(plan_dir, "scoping: initial scope captured", date=today)
    # Stamp OKF frontmatter (Issue 3.3): type: Plan + okf_spec, then dual-write the
    # identity `**Field:**` lines into their frontmatter mirror (REQ-OKF-020/050).
    _stamp_okf_type(plan_dir, plan_md)
    _write_plan_fields(plan_dir, {})
    return plan_md


def _detect_tools() -> dict[str, str]:
    """Probe portability-relevant tools for their version strings.

    Epic 1.4: best-effort, 2s timeout per tool, missing/failing tools recorded
    as 'not present'. Never raises — init must proceed even if every probe
    fails.
    """
    # Each tuple: (binary, version-arg). --version works for all currently
    # probed tools; keeping the per-tool arg explicit in case that changes.
    probes = {
        "bd": ["bd", "--version"],
        "git": ["git", "--version"],
        "uv": ["uv", "--version"],
        "python": ["python", "--version"],
        "gh": ["gh", "--version"],
        "glab": ["glab", "--version"],
        "claude": ["claude", "--version"],
    }
    results: dict[str, str] = {}
    for name in DETECT_TOOLS:
        cmd = probes.get(name)
        if not cmd or not shutil.which(cmd[0]):
            results[name] = "not present"
            continue
        try:
            out = subprocess.check_output(
                cmd,
                text=True,
                stderr=subprocess.STDOUT,
                timeout=DETECT_TIMEOUT_SEC,
            )
            # Collapse multi-line output (gh prints multiple lines) to first
            # non-empty line — the version stamp.
            first = next((ln.strip() for ln in out.splitlines() if ln.strip()),
                         "unknown")
            results[name] = first
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
                FileNotFoundError, OSError):
            results[name] = "not present"
    return results


def _portability_snapshot_header() -> str:
    """Tool-inventory snapshot header: hostname + detection date."""
    host = socket.gethostname() or "unknown-host"
    date = datetime.now().strftime("%Y-%m-%d")
    return f"<!-- snapshot: host={host} date={date} -->"


#: Bundle members listed in the reserved `index.md` — `(path, description)`. Folds the
#: legacy README `File map` + `Reading order` prose into OKF listing bullets
#: (REQ-PORT-001 / OKF-EXTENSION.md §5).
_INDEX_MEMBERS: tuple[tuple[str, str], ...] = (
    ("plan.md", "The plan of record — status, objective, motivation, approach, epics, gates, risks, success criteria. Read first for why this plan exists and how it executes."),
    ("context.md", "Project environment snapshot — tool versions, paths, operator, runtime assumptions at authoring time. What environment the plan assumes."),
    ("log.md", "Newest-first update history — scoping, review, and intake entries (the OKF-reserved phase log)."),
    ("upstream-triage.md", "Disposition of each candidate upstream issue (include / exclude / partial / supersede / deferred) with the reasoning. The triage record behind plan.md's Upstream Issues table."),
    ("references/", "Inlined upstream issue bodies (`upstream-<N>.md`), one per non-excluded Upstream Issues row. Snapshots, not live — the issues this plan addresses."),
    ("reviews/", "Reviewer verdicts (`pass-<N>.md`), one per review cycle. What reviewers flagged and how it was resolved."),
    ("findings/", "Investigation experiment results (if any)."),
    ("diagrams/", "d2 diagram sources beside their `.png` renders, per the `diagram-authoring` skill."),
    ("assets/", "Attachments and other generated artifacts (not diagrams — those live in `diagrams/`)."),
    ("plan-retrospective.md", "Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE)."),
)


RETROSPECTIVE_FILE = "plan-retrospective.md"

# REQ-PORT-052's field set, in emission order. A two-column key/value TABLE is used
# rather than `**Label:** value` lines because a bold label is invisible to
# `plan_manager.py audit` yet COLLIDES with the reserved-label rule `/yf-okf check`
# enforces (REQ-OKF-010) — the shape would pass the mechanical audit and fail the
# conformance check, which is the worse of the two orders to discover it in.
RETROSPECTIVE_FIELDS: tuple[str, ...] = (
    "kind", "when", "stop_class", "asked", "answered", "frontloadable",
    "detected_by", "evidence", "escape_class", "adjudication", "origin",
    "culpability", "prevention", "cost",
)
RETROSPECTIVE_KINDS = ("stop", "deviation")
RETROSPECTIVE_DETECTED_BY = ("self-report", "operator", "mechanical-check")

_RETRO_HEADER = """---
type: Retrospective
okf_spec: OKF-PLAN
---
# Plan retrospective

Stops and deviations recorded during execution, newest last. Each `## RE-NNN` section is
one entry; `RE-NNN` ids are append-only and are never reused or renumbered.

`detected_by` records WHO found the entry and `evidence` records the command and output
substantiating any state claim in it, or the literal `unverified`. Both exist because an
entry's trust level is a property of who found it, and the recorder is usually the subject:
a retrospective built from an actor's own account would faithfully transcribe a false claim
rather than detect one. A state assertion with no evidence is a narration, not a finding.

"""


def _retrospective_next_id(text: str) -> int:
    """The next `RE-NNN` number: max existing + 1. Append-only, never reused."""
    nums = [int(m) for m in re.findall(r"^## RE-(\d+)", text, re.M)]
    return (max(nums) + 1) if nums else 1


def append_retrospective(plan_dir: Path, entry: dict, *, dry_run: bool = False) -> dict:
    """Append one `## RE-NNN` entry to the bundle's `plan-retrospective.md` (REQ-CLI-022).

    Mirrors `okf.append_log`'s create-if-absent + idempotence contract. Implemented
    **locally rather than by generalizing `append_log`**, which is vendored in four
    byte-identical copies behind `e-okf-copy-*` drift edges — generalizing it would
    require changing all four in lockstep for one caller's benefit.

    Idempotent on entry identity: an entry whose non-`when` fields exactly match an
    existing one is not appended twice, and the existing id is returned.

    Returns ``{"file", "id", "appended", "created", "index_updated"}``.
    """
    path = plan_dir / RETROSPECTIVE_FILE
    created = not path.exists()
    text = _RETRO_HEADER if created else path.read_text(encoding="utf-8")

    row = {k: entry.get(k, "") for k in RETROSPECTIVE_FIELDS}
    row.setdefault("kind", "stop")
    if not row.get("kind"):
        row["kind"] = "stop"
    if row["kind"] not in RETROSPECTIVE_KINDS:
        raise ValueError(
            f"unknown retrospective kind {row['kind']!r}; expected one of "
            f"{', '.join(RETROSPECTIVE_KINDS)}"
        )
    if not row.get("when"):
        row["when"] = datetime.now().strftime("%Y-%m-%d")
    # An unsubstantiated state claim is a narration, not a finding (REQ-PORT-052).
    if not row.get("evidence"):
        row["evidence"] = "unverified"
    if not row.get("detected_by"):
        row["detected_by"] = "self-report"

    # Idempotence: compare every field EXCEPT `when`, so re-running a step on a later
    # date does not duplicate the same finding.
    identity = {k: str(row[k]) for k in RETROSPECTIVE_FIELDS if k != "when"}
    for block in re.split(r"(?=^## RE-\d+)", text, flags=re.M):
        m = re.match(r"^## RE-(\d+)", block)
        if not m:
            continue
        existing = {}
        for line in block.splitlines():
            cell = re.match(r"^\|\s*`([a-z_]+)`\s*\|\s*(.*?)\s*\|\s*$", line)
            if cell:
                existing[cell.group(1)] = cell.group(2)
        if all(existing.get(k, "") == v for k, v in identity.items() if v):
            return {"file": str(path), "id": f"RE-{int(m.group(1)):03d}",
                    "appended": False, "created": False, "index_updated": False}

    n = _retrospective_next_id(text)
    rid = f"RE-{n:03d}"
    lines = [f"## {rid}", "", "| field | value |", "| :-- | :-- |"]
    for k in RETROSPECTIVE_FIELDS:
        lines.append(f"| `{k}` | {row[k]} |")
    lines.append("")
    new_text = text.rstrip("\n") + "\n\n" + "\n".join(lines) + "\n"

    index_updated = False
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
        index_updated = _ensure_index_lists_retrospective(plan_dir)
    return {"file": str(path), "id": rid, "appended": True,
            "created": created, "index_updated": index_updated}


def _index_member_present(plan_dir: Path, member: str) -> bool:
    """Should ``member`` be emitted into the reserved ``index.md`` (REQ-PORT-001)?

    An index entry is an ASSERTION that the target exists; emitting one for an
    absent path makes the listing state something false. plan-046 measured this
    as **37 broken links across 19 root indexes**, 36 of them dead directory
    links from unconditional emission.

    Two cases, both keyed on what survives a fresh clone:

    * **file** — must exist. `plan-retrospective.md` is presence-optional
      (REQ-PORT-ACT-RETROSPECTIVE) and `upstream-triage.md` only exists once
      triage has run; each is listed when it appears, by
      :func:`_ensure_index_lists_member`.
    * **directory** — must exist AND be non-empty. **git does not track empty
      directories**, so a scaffolded-but-empty `diagrams/`/`assets/` is absent
      from every clone and the dead link returns. This is exactly why the fix is
      "emit only what exists" rather than "scaffold the missing directories" —
      the latter also generates the `empty-dir` drift `reindex` reports
      (SPEC REQ-OKF-011).
    """
    target = plan_dir / member.rstrip("/")
    if member.endswith("/"):
        try:
            return target.is_dir() and any(target.iterdir())
        except OSError:
            return False
    return target.is_file()


def _ensure_index_lists_member(plan_dir: Path, member: str) -> bool:
    """Add ``member``'s listing bullet to ``index.md`` if absent. Idempotent.

    The companion to :func:`_index_member_present`: the scaffold emits only what
    exists at scaffold time, so a member created later must be listed when it is
    created. Returns True if the index was modified.
    """
    index = plan_dir / "index.md"
    if not index.exists() or not _index_member_present(plan_dir, member):
        return False
    text = index.read_text(encoding="utf-8")
    if f"]({member})" in text:
        return False
    desc = next((d for m, d in _INDEX_MEMBERS if m == member), "")
    bullet = f"- [{member}]({member})" + (f" - {desc}" if desc else "") + "\n"
    lines = text.splitlines(keepends=True)
    last = max((i for i, ln in enumerate(lines) if ln.startswith("- [")), default=None)
    if last is None:
        text = text.rstrip("\n") + "\n\n" + bullet
    else:
        lines.insert(last + 1, bullet)
        text = "".join(lines)
    index.write_text(text, encoding="utf-8")
    return True


def _ensure_index_lists_retrospective(plan_dir: Path) -> bool:
    """Add the retrospective to `index.md`'s listing if absent (pass-1 C6).

    Without this the bundle's own cold-reader contract is violated by the very file
    added to support it: a member absent from the reserved listing is exactly the
    portability gap the retrospective exists to help close.
    """
    index = plan_dir / "index.md"
    if not index.exists():
        return False
    text = index.read_text(encoding="utf-8")
    if RETROSPECTIVE_FILE in text:
        return False
    desc = next((d for m, d in _INDEX_MEMBERS if m == RETROSPECTIVE_FILE), "Execution retrospective.")
    bullet = f"- [{RETROSPECTIVE_FILE}]({RETROSPECTIVE_FILE}) - {desc}\n"
    lines = text.splitlines(keepends=True)
    last = max((i for i, ln in enumerate(lines) if ln.startswith("- [")), default=None)
    if last is None:
        text = text.rstrip("\n") + "\n\n" + bullet
    else:
        lines.insert(last + 1, bullet)
        text = "".join(lines)
    index.write_text(text, encoding="utf-8")
    return True


def seed_index(plan_dir: Path, plan_id: str, objective: str) -> Path:
    """Write the OKF-reserved bundle listing `index.md` (Issue 3.3, REQ-PORT-001).

    A progressive-disclosure listing — an `okf_version` frontmatter block, a `#`
    heading, the objective, and `- [child](path) - description` bullets enumerating
    the bundle members (via the engine's `add_index_entry`). It replaces the legacy
    `README.md` file-map/reading-order surface. Being an OKF **reserved** file it
    carries no `type` and no `okf_spec` (REQ-OKF-031).
    """
    path = plan_dir / "index.md"
    path.write_text(
        f"---\nokf_version: {okf.okf_version}\n---\n\n# {plan_id}\n\n> {objective}\n\n"
        "This plan folder is **portable** — a cold reader understands its purpose, "
        "environment, reviewer history, and upstream context from the files below "
        "alone, without the drafting conversation.\n\n"
    )
    for member, desc in _INDEX_MEMBERS:
        if not _index_member_present(plan_dir, member):
            continue
        okf.add_index_entry(plan_dir, member, desc)
    return path


def seed_context_md(plan_dir: Path, author: str,
                    tools: dict[str, str] | None = None) -> Path:
    """Write context.md with required/optional sections (Epic 1.3 + 1.4).

    Required sections audit-enforces non-empty: Project environment, Tool
    inventory, Paths, Operator identity, Runtime assumptions. Optional sections
    may be empty: Adjacent-concept glossary, Additional context.
    """
    if tools is None:
        tools = _detect_tools()
    header = _portability_snapshot_header()
    tool_lines = "\n".join(f"- `{name}`: {tools[name]}" for name in DETECT_TOOLS)
    try:
        cwd = str(Path.cwd().resolve())
    except OSError:
        cwd = "unknown"
    try:
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True, stderr=subprocess.DEVNULL, timeout=DETECT_TIMEOUT_SEC,
        ).strip()
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
            FileNotFoundError, OSError):
        repo_root = cwd

    content = f"""# Project Environment Context

_Snapshot taken at plan-authoring time. Cold readers: verify these values
against the current environment before acting. The snapshot header below
records the machine and date of capture._

## Project environment

Describe the project this plan belongs to: what it does, what stack it uses,
any non-obvious setup. A cold reader should not need to infer this from code.

## Tool inventory

{header}

{tool_lines}

## Paths

- Repo root: `{repo_root}`
- Working directory at plan creation: `{cwd}`
- Plan directory: `{plan_dir}`

## Operator identity

- Git user: `{author}`
- Attribution: fill in role, contact, and authority scope before intake.

## Runtime assumptions

List the assumptions this plan makes about the environment it will execute in
(OS, shell, network access, credentials, side-effect permissions). A cold
reader on a different machine should be able to decide whether the plan is
safe to run as-is.

## Adjacent-concept glossary

_Optional._ Terms, acronyms, or project-specific jargon the plan uses.

## Additional context

_Optional._ Anything else a cold reader needs that does not fit above.
"""
    path = plan_dir / "context.md"
    path.write_text(content)
    # OKF frontmatter (Issue 3.3): context.md is the Environment concept doc.
    _stamp_okf_type(plan_dir, path)
    return path


def seed_portability_scaffolding(plan_dir: Path, plan_id: str, objective: str,
                                 author: str) -> dict[str, str]:
    """Epic 1.1/1.5: seed the reserved `index.md`, context.md, references/, reviews/.

    Returns a dict of created paths suitable for merging into init JSON
    output. Best-effort tool detection runs inline — any probe failure is
    non-fatal (see _detect_tools). Issue 3.3: the orientation surface is now the
    OKF-reserved `index.md` (not `README.md`).
    """
    # ORDER MATTERS (plan-046 Issue 4.2a): the index lists only members that
    # EXIST when it is written (REQ-PORT-001), so every member the scaffold
    # itself creates must be created FIRST. `context.md` was previously written
    # after `seed_index`, so the fix that stopped emitting ghost entries would
    # otherwise have dropped `context.md` from every new bundle.
    context = seed_context_md(plan_dir, author)
    references = plan_dir / "references"
    reviews = plan_dir / "reviews"
    references.mkdir(parents=True, exist_ok=True)
    reviews.mkdir(parents=True, exist_ok=True)
    index = seed_index(plan_dir, plan_id, objective)
    return {
        "index_md": str(index),
        "context_md": str(context),
        "references_dir": str(references),
        "reviews_dir": str(reviews),
    }


def _write_upstream_reference(plan_dir: Path, issue: dict) -> Path:
    """Epic 2.1/2.2: write one references/upstream-<N>.md file per issue.

    Full (untruncated) body. Clobbers existing file on re-triage — operator
    hand-edits will be lost (see SKILL.md Phase 1.3 and Epic 2.3).
    """
    number = issue.get("number", "unknown")
    refs_dir = plan_dir / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)
    path = refs_dir / f"upstream-{number}.md"
    labels_raw = issue.get("labels") or []
    if labels_raw and isinstance(labels_raw[0], dict):
        labels = ", ".join(lbl.get("name", "") for lbl in labels_raw)
    else:
        labels = ", ".join(str(lbl) for lbl in labels_raw)
    content = f"""# Upstream #{number}: {issue.get("title", "")}

- **Number:** {number}
- **Title:** {issue.get("title", "")}
- **URL:** {issue.get("url", "")}
- **State:** {issue.get("state", "")}
- **Labels:** {labels}

## Body

{issue.get("body", "") or "_(empty)_"}
"""
    path.write_text(content)
    # OKF frontmatter (Issue 3.3): each upstream reference is a Reference concept doc.
    _stamp_okf_type(plan_dir, path)
    return path


def seed_scope_answers(plan_dir: Path, objective: str) -> Path:
    """Create scope-answers.md questionnaire."""
    content = f"""# Scope Questionnaire: {objective}

Instructions: Fill in your answers below each question.
Delete or leave blank any that aren't applicable.
When done, tell the agent: "answers ready" (or similar).

## Objective
> {objective}
Is this correct? Adjustments?

**Answer:**

## Constraints
Platform requirements? Dependencies? Timeline? Budget?

**Answer:**

## Investigation Needs
What unknowns require experimentation before committing?
(API behavior, library evaluation, performance, etc.)

**Answer:**

## Scope Boundaries
What is explicitly out of scope?

**Answer:**

## Success Criteria
How do we know the plan is done?

**Answer:**

## Additional Context
Anything else relevant?

**Answer:**
"""
    path = plan_dir / "scope-answers.md"
    path.write_text(content)
    # OKF frontmatter (Issue 3.3): a non-reserved bundle .md — REQ-PORT-050.
    _stamp_okf_type(plan_dir, path)
    return path


def seed_upstream_triage(plan_dir: Path, objective: str,
                         issues: list[dict]) -> tuple[Path, list[Path]]:
    """Create upstream-triage.md for operator editing.

    Also writes one `references/upstream-<N>.md` file per issue containing the
    full (untruncated) body — portability contract (Epic 2.1/2.2). The 200-char
    truncation is kept at the triage-display line for readability.

    Returns (triage_path, [reference_paths]).
    """
    lines = [
        f"# Upstream Issue Triage: {objective}",
        "",
        "Instructions: For each issue, set disposition to: include, exclude, partial, supersede, deferred.",
        "Add notes as needed. When done, say \"triage ready\".",
        "",
        "_Full issue bodies are inlined under `references/upstream-<N>.md` (regenerated on re-triage)._",
        "",
    ]
    reference_paths: list[Path] = []
    for issue in issues:
        number = issue.get("number", "?")
        title = issue.get("title", "Untitled")
        labels_raw = issue.get("labels", []) or []
        if labels_raw and isinstance(labels_raw[0], dict):
            labels = ", ".join(lbl.get("name", "") for lbl in labels_raw)
        else:
            labels = ", ".join(str(lbl) for lbl in labels_raw)
        body = (issue.get("body", "") or "")[:200]
        lines.extend([
            f"## #{number} — {title}",
            f"Labels: {labels}" if labels else "",
            f"> {body}..." if body else "",
            "",
            "**Disposition:**",
            "**Notes:**",
            "",
        ])
        if number != "?":
            reference_paths.append(_write_upstream_reference(plan_dir, issue))
    path = plan_dir / "upstream-triage.md"
    path.write_text("\n".join(lines))
    # OKF frontmatter (Issue 3.3): upstream-triage.md is typed Reference (§1a).
    _stamp_okf_type(plan_dir, path)
    # List it the moment it exists (REQ-PORT-001, plan-046 Issue 4.2a). The scaffold
    # emits only members present AT SCAFFOLD TIME, and triage runs later — measured
    # as `upstream-triage.md` unlisted in 8 of 19 root indexes, one systematic
    # producer bug rather than 8 independent oversights.
    _ensure_index_lists_member(plan_dir, "upstream-triage.md")
    return path, reference_paths


def _read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _read_config() -> dict:
    """Operator config, merged across the three tiers (REQ-YF-PRE-004).

    Precedence, highest first: `.yf/plan/config.local.json` (gitignored override) →
    `.yf/plan/config.json` (committed, shared) → `.yf-plan.local.json` (legacy root
    dotfile, never removed). Merged **key by key**, matching
    `yf/src/preflight.rs::read_config`.

    Re-read on every call rather than reusing the import-time `_CONFIG`, so a config
    written during a run (or a test that rewrites it) is observed. `_CONFIG` exists
    only because `PLANS_DIR` / `INCUBATOR_PARENT` bind at import.
    """
    return _bootstrap_config()


@click.group()
def cli():
    """Plan manager for the /yf-plan skill."""
    pass


@cli.command("json-get")
@click.argument("keys", nargs=-1, required=True)
def json_get(keys: tuple[str, ...]):
    """Extract a value from JSON on stdin by key path (defensive).

    Tolerates warning prefixes and concatenated/array bd output by parsing the
    first balanced JSON value. Each argument is one nesting level; a numeric key
    indexes into a list (e.g. `bd show <id> --json | plan_manager.py json-get 0 metadata`):
      echo '{"a":{"b.c":1}}' | plan_manager.py json-get a "b.c"
    """
    raw = sys.stdin.read()
    try:
        data = _extract_first_json(raw)
    except ValueError as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        except (KeyError, TypeError, IndexError, ValueError):
            click.echo(
                f"ERROR: key {key!r} not found in path {' -> '.join(keys)}",
                err=True,
            )
            sys.exit(1)
    if isinstance(data, (dict, list)):
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(data)


@cli.command()
@click.argument("objective")
@click.option(
    "--incubator", default=None,
    help="Incubator slug to scope plan to (e.g. 'bookpipe'). "
         "If omitted, CWD is checked for an Incubator/<slug>/ prefix; "
         "otherwise plan lands in docs/plans/.",
)
def init(objective: str, incubator: str | None):
    """Initialize a new plan directory with seed documents."""
    if incubator is None:
        incubator = detect_incubator_from_cwd()
    plans_dir = resolve_plans_dir(incubator)
    plans_dir.mkdir(parents=True, exist_ok=True)
    user = get_git_user()
    plan_id = make_plan_id(objective)
    plan_dir = make_plan_dir(plan_id, plans_dir)
    plan_md = seed_plan_md(plan_dir, plan_id, objective, user)
    scaffolding = seed_portability_scaffolding(plan_dir, plan_id, objective, user)

    result = {
        "plan_id": plan_id,
        "plan_dir": str(plan_dir),
        "plans_root": str(plans_dir),
        "incubator": incubator,
        "plan_md": str(plan_md),
        **scaffolding,
    }
    click.echo(json.dumps(result, indent=2))


@cli.command()
@click.argument("plan_dir", type=click.Path(exists=True))
@click.argument("objective")
def scope(plan_dir: str, objective: str):
    """Generate scope-answers.md questionnaire for a plan."""
    path = seed_scope_answers(Path(plan_dir), objective)
    click.echo(json.dumps({"scope_answers": str(path)}, indent=2))


@cli.command()
@click.argument("plan_dir", type=click.Path(exists=True))
@click.argument("objective")
@click.option("--issues-json", type=click.Path(exists=True),
              help="JSON file with upstream issues to triage")
def triage(plan_dir: str, objective: str, issues_json: str):
    """Generate upstream triage document from issues JSON."""
    with open(issues_json) as f:
        issues = json.load(f)
    path, refs = seed_upstream_triage(Path(plan_dir), objective, issues)
    click.echo(json.dumps({
        "upstream_triage": str(path),
        "references": [str(p) for p in refs],
    }, indent=2))


def _enumerate_plans() -> list[dict]:
    """Collect plan records across vault-default + Incubator roots.

    Each record carries the advisory `stale_approved` (REQ-PORT-041) and `parked`
    (#86, REQ-PLAN-068) flags. Shared by `list` and `parked`.
    """
    plans = []
    for root in list_plan_roots():
        incubator = _scope_for_root(root, PLANS_DIR)
        for d in sorted(root.iterdir()):
            if not d.is_dir() or not d.name.startswith("plan-"):
                continue
            plan_md = d / "plan.md"
            if not plan_md.exists():
                continue

            text = plan_md.read_text()
            # Status via the single dual-mode accessor (frontmatter-first) so a
            # migrated (frontmatter-only) plan resolves; objective stays inline.
            status = _read_plan_status(text) or "unknown"
            objective = _read_plan_objective(text) or d.name

            # Advisory stale-approved flag (REQ-PORT-041): only meaningful once a
            # fingerprint is stored (review/approved onward). Non-fatal in list/status.
            fp_status = _fingerprint_status(d)
            stale = fp_status.get("stale_approved", False)
            # Parked = approved but never executed (#86, REQ-PLAN-068). Mutually
            # exclusive with stale_approved (freshness gate) by construction.
            parked = _is_parked(status, fp_status)
            plans.append({
                "id": d.name,
                "objective": objective,
                "status": status,
                "incubator": incubator,
                "path": str(d),
                "stale_approved": stale,
                "parked": parked,
            })
    plans.sort(key=lambda p: p["id"])
    return plans


@cli.command("list")
@click.option("--json-output", "as_json", is_flag=True)
def list_plans(as_json: bool):
    """List all plans and research items, across vault-default + Incubator roots."""
    plans = _enumerate_plans()

    research = []
    for root in list_research_roots():
        incubator = _scope_for_root(root, RESEARCH_DIR)
        for d in sorted(root.iterdir()):
            info = _research_item_info(d)
            if info is None:
                continue
            research.append({
                **info,
                "incubator": incubator,
            })
    research.sort(key=lambda r: (r["incubator"] or "", r["id"]))

    if as_json:
        click.echo(json.dumps({"plans": plans, "research": research}, indent=2))
        return

    if not plans:
        click.echo("No plans found.")
    else:
        click.echo("Plans:")
        for p in plans:
            scope = p["incubator"] or "docs"
            stale_tag = "  ⚠ STALE-APPROVED (re-review before execute)" if p.get("stale_approved") else ""
            parked_tag = "  ⏸ PARKED (approved, not executed — run /yf-plan execute)" if p.get("parked") else ""
            click.echo(
                f"  {p['id']:<35} [{scope:<18}] "
                f"{p['objective']:<40} status: {p['status']}{stale_tag}{parked_tag}"
            )

    if research:
        click.echo("")
        click.echo("Research:")
        for r in research:
            scope = r["incubator"] or "docs"
            kind_tag = "rehoused-plan" if r["kind"] == "rehoused-plan" else "research"
            click.echo(
                f"  {r['id']:<35} [{scope:<18}] "
                f"{r['topic']:<40} kind: {kind_tag}"
            )


@cli.command("parked")
@click.option("--json-output", "--json", "as_json", is_flag=True)
def parked_cmd(as_json: bool):
    """Enumerate parked plans — approved but never executed (#86, REQ-PLAN-068).

    Consumed by the `/yf-plan status` nudge and the land-the-plane check.
    """
    parked = [p for p in _enumerate_plans() if p.get("parked")]
    if as_json:
        click.echo(json.dumps({"count": len(parked), "parked": parked}, indent=2))
        return
    if not parked:
        click.echo("No parked plans.")
        return
    click.echo(f"{len(parked)} plan(s) approved but not executed — run /yf-plan execute <id>:")
    for p in parked:
        click.echo(f"  {p['id']:<35} {p['objective']}")


@cli.command()
@click.argument("plan_dir", type=click.Path(exists=True))
@click.argument("status")
@click.option("--message", "-m", default=None, help="Phase log message")
@click.option("--override-ready-check", is_flag=True,
              help="Authorize the `approved` transition on a RED ready-check "
                   "(REQ-DATA-028 / REQ-CLI-024). Logs a deviation. Deliberately NOT "
                   "named `--force`: that flag already means four different things on "
                   "four other verbs, and this one must never read as forcing a status "
                   "the plan has not earned.")
def update_status(plan_dir: str, status: str, message: str, override_ready_check: bool):
    """Update plan.md status and append to phase log.

    **The `approved` transition is GATED** (REQ-DATA-028, plan-047 Issue 2.5). Every other
    status is still free-form; `approved` is refused unless `ready-check` (REQ-PLAN-066) is
    green, or `--override-ready-check` is passed.

    Before this gate, `ready-check` exiting **3** and `update-status <dir> approved` exiting
    **0** on the *same plan* was reproducible in two commands — measured, and re-verified by
    the red-team. The intake gate was prose obedience, not code: nothing downstream of a
    failing audit could stop a plan reaching `approved`, no matter what the linter returned.

    The writer is otherwise **free-form** — it accepts any status string and does not validate
    against an enum. The status vocabulary is the source of truth in SPEC.md
    (REQ-PLAN-001) and the SKILL.md Phase Model "Status values:" line: `scoping`,
    `investigating`, `drafting`, `review`, `ready-for-approval`, `approved`,
    `executing`, `reconciling`, `complete`. `ready-for-approval` is the pre-approval
    gate state (set at the end of PLAN once `ready-check` is green) and is **not**
    execute-eligible — only `approved` (with a fresh fingerprint) is; execute
    eligibility keys on the fingerprint, never on a `status == "approved"` literal.
    """
    plan_md = Path(plan_dir) / "plan.md"
    if not plan_md.exists():
        click.echo("ERROR: plan.md not found", err=True)
        sys.exit(1)

    # --- REQ-DATA-028: the `approved` transition is fail-closed -----------------------
    # Scoped deliberately to `approved` alone. Gating every status would break the normal
    # drafting flow (a plan in `scoping` has no red-team verdict by construction), and
    # `approved` is the one transition that grants execute eligibility.
    if status == "approved":
        readiness = _ready_check_result(Path(plan_dir))
        if not readiness["ready"] and not override_ready_check:
            click.echo(json.dumps({
                "status": "refused",
                "requested": "approved",
                "reason": "ready-check is not green (REQ-DATA-028)",
                "reasons": readiness["reasons"],
                "remediation": (
                    "Resolve the reasons above (a REVISE needs a fresh red-team cycle; an "
                    "audit fail needs remediation or `/yf-plan capture`), then re-run. To "
                    "override deliberately, pass --override-ready-check — it writes the "
                    "status AND records a deviation."
                ),
            }, indent=2), err=True)
            sys.exit(3)
        if not readiness["ready"] and override_ready_check:
            # The override is authorized but never silent: it lands in log.md AND in the
            # retrospective, under the flag's own name.
            append_retrospective(Path(plan_dir), {
                "kind": "deviation",
                "when": datetime.now().strftime("%Y-%m-%d"),
                "asked": "update-status approved was refused: ready-check is not green",
                "answered": ("operator passed --override-ready-check; approving anyway. "
                             "Reasons bypassed: " + "; ".join(readiness["reasons"])),
                "frontloadable": "no",
                "detected_by": "mechanical-check",
                "evidence": f"ready-check reasons: {readiness['reasons']}",
            })
            message = (message or "operator approved") + \
                " — ready-check OVERRIDDEN via --override-ready-check"

    today = datetime.now().strftime("%Y-%m-%d")

    # Dual-write the status field (frontmatter + `**Field:**`) from one model.
    _write_plan_fields(Path(plan_dir), {"status": status})

    # Append the phase-transition entry to the reserved bundle-root `log.md`
    # (Issue 3.4 / REQ-DATA-012). `okf.append_log` is newest-first: it prepends a
    # `## YYYY-MM-DD` heading (or reuses today's) and adds a `- <status>: <message>`
    # bullet retaining the `<status>:` token the review/scoping/audit readers key on.
    # It creates `log.md` on first write. The phase log no longer lives in plan.md.
    entry = f"{status}: {message or status}"
    log_entry = f"- {entry}"

    # REQ-DATA-017 — idempotent per (date, status token, message).
    #
    # Re-running §6.4 is a DOCUMENTED recovery path: the halting steps' fail-loud banners
    # explicitly instruct the operator to resolve and re-run. So duplicate bullets are
    # produced by the normal remediation flow, not by misuse. They are not cosmetic —
    # `log.md` bullets are what the status, review-count (REQ-PORT-006) and grandfather-date
    # parsers read, so a duplicated status bullet corrupts the record those parsers derive
    # their answers from.
    #
    # The scope is deliberately narrow: only an EXACT (today's date heading, identical
    # bullet) match is suppressed. The same status on a LATER date, or with a different
    # message, still appends — this suppresses re-emission, never history.
    already = _log_has_entry_today(Path(plan_dir), log_entry, today)
    if not already:
        okf.append_log(Path(plan_dir), entry, date=today)

    click.echo(json.dumps({
        "status": status, "date": today, "log_entry": log_entry,
        "appended": not already, "deduped": already,
    }))


def _log_has_entry_today(plan_dir: Path, log_entry: str, today: str) -> bool:
    """Is this exact bullet already present under today's `## YYYY-MM-DD` heading?

    Scanning only today's section is what keeps the check a *re-emission* guard rather
    than a history-suppressing one: the same status legitimately recurs on a later date.
    """
    log_md = plan_dir / "log.md"
    if not log_md.exists():
        return False
    in_today = False
    for line in log_md.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_today = line.strip() == f"## {today}"
            continue
        if in_today and line.strip() == log_entry.strip():
            return True
    return False


_TRACKER_ROW_RE = re.compile(
    r"^\|\s*\[?#(\d+)\]?[^|]*\|[^|]*\|\s*tracker\s*\|", re.MULTILINE
)


def _tracker_url_from_plan_md(plan_md_text: str, repo_slug: str | None) -> str | None:
    """Find the coarse tracker URL in plan.md's Upstream Issues table.

    The tracker row is the one whose Disposition is literally `tracker` (as distinct
    from include/exclude/partial/supersede, which are work dispositions). Prefer a full
    URL already present in the row; otherwise rebuild one from the issue number.
    """
    m = _TRACKER_ROW_RE.search(plan_md_text or "")
    if not m:
        return None
    num = m.group(1)
    url_m = re.search(rf"https://github\.com/[\w.-]+/[\w.-]+/issues/{num}\b",
                      plan_md_text)
    if url_m:
        return url_m.group(0)
    return f"https://github.com/{repo_slug}/issues/{num}" if repo_slug else None


def _repo_slug() -> str | None:
    """`owner/repo` from the git remote, or None when it cannot be determined."""
    try:
        url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"],
            text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None
    m = re.search(r"github\.com[:/]([\w.-]+/[\w.-]+?)(?:\.git)?$", url)
    return m.group(1) if m else None


def _bd_external_ref(bead_id: str) -> str | None:
    """Read a bead's existing external_ref, or None. Never raises."""
    try:
        out = subprocess.check_output(["bd", "show", bead_id, "--json"],
                                      text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None
    rows = _parse_bd_json(out)
    if not rows:
        return None
    val = rows[0].get("external_ref")
    return val.strip() if isinstance(val, str) and val.strip() else None


@cli.command("stamp-tracker")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--epic", "epic_id", default=None,
              help="Epic to stamp. Default: the plan's recorded **Epic:** field.")
@click.option("--url", "tracker_url", default=None,
              help="Tracker issue URL. Default: derived from plan.md's Upstream Issues table.")
@click.option("--json", "as_json", is_flag=True, help="Emit a JSON verdict.")
def stamp_tracker(plan_dir: str, epic_id: str | None, tracker_url: str | None,
                  as_json: bool):
    """Stamp the coarse tracker URL onto the plan epic as `external_ref` (REQ-PLAN-073).

    WHY THIS EXISTS (#131). `yf-plan` §4.5 files one coarse tracking issue per plan with
    a bare `gh issue create` and records the URL on **no bead**. `yf-beads-upstream`'s
    `closable` verb groups beads by their `external_ref`, so a tracker nothing points at
    is **structurally invisible** to it — five have gone stale and been closed by hand
    (#103, #95, #96, #98, #134). Stamping the URL onto the epic makes the tracker an
    ordinary mapped bead, visible to `closable` with no new signal and no `plans-root`
    coupling in either direction.

    WHERE IT RUNS. #131 as filed says to stamp "in Phase 4.5, after creating the tracking
    issue". That is **impossible**: §4.5 runs at INTAKE, §4.6 states "No pour happened at
    intake", and §5.2 owns the pour — §4.5's own text says the issue links the plan folder
    and "(once poured)" its epic. There is no epic id at §4.5 to stamp. The correct place
    is **§5.2a, immediately after `record-epic`**, where the epic id is first known; and
    also on the **§5.2b resume** branch, so a plan whose tracker was filed late (or whose
    stamp failed) is repaired on the next execute rather than staying invisible forever.

    FAIL-SOFT BY CONTRACT. Every failure mode — no epic, no tracker, no bd — returns a
    skip verdict with a reason and exit 0. This runs inside the pour sequence, and a plan
    with no tracker yet is a normal state, not an error: it must never fail the pour.

    Idempotent: re-stamping the same URL is a no-op.
    """
    pdir = Path(plan_dir)
    text = (pdir / "plan.md").read_text(encoding="utf-8") if (pdir / "plan.md").exists() else ""

    epic_id = epic_id or _read_plan_epic_field(text)
    if not epic_id:
        return _stamp_verdict(as_json, "skipped", None, None,
                              "no epic recorded for this plan (pour has not run yet)")

    tracker_url = tracker_url or _tracker_url_from_plan_md(text, _repo_slug())
    if not tracker_url:
        return _stamp_verdict(as_json, "skipped", epic_id, None,
                              "no coarse tracker found in plan.md Upstream Issues "
                              "(no row with disposition `tracker`)")

    existing = _bd_external_ref(epic_id)
    if existing == tracker_url:
        return _stamp_verdict(as_json, "unchanged", epic_id, tracker_url,
                              "epic already carries this tracker URL")
    if existing:
        return _stamp_verdict(as_json, "skipped", epic_id, existing,
                              f"epic already mapped to a DIFFERENT ref ({existing}); "
                              "refusing to overwrite — resolve by hand")

    try:
        subprocess.run(["bd", "update", epic_id, "--external-ref", tracker_url, "-q"],
                       check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        return _stamp_verdict(as_json, "skipped", epic_id, tracker_url,
                              f"bd update failed: {exc}")
    return _stamp_verdict(as_json, "stamped", epic_id, tracker_url,
                          "epic is now visible to `upstream.py closable`")


def _stamp_verdict(as_json: bool, status: str, epic: str | None,
                   url: str | None, reason: str):
    """Emit the stamp-tracker verdict. ALWAYS exit 0 — this never fails a pour."""
    if as_json:
        click.echo(json.dumps({"status": status, "epic": epic,
                               "tracker": url, "reason": reason}))
    else:
        click.echo(f"stamp-tracker: {status} — {reason}"
                   + (f" (epic {epic} -> {url})" if status == "stamped" else ""))
    return 0


@cli.command("record-epic")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.argument("epic_id")
def record_epic(plan_dir: str, epic_id: str):
    """Persist the plan<->epic linkage in plan.md at INTAKE (Issue 1.1, #2).

    Two writes that make resume-guard deterministic:
      (a) an `**Epic:** <id>` header field (inserted after `**Status:**`, or
          updated in place if already present);
      (b) an inert `- intake: epic <id> poured` entry in the reserved `log.md`
          (Issue 3.4 / REQ-DATA-012). The `intake:` prefix matches neither the
          `review:` nor `scoping:` reader, so it never perturbs review/scoping counts.

    Idempotent: re-running for the same epic updates the header field and does
    not append a duplicate intake line.
    """
    plan_md = Path(plan_dir) / "plan.md"
    if not plan_md.exists():
        click.echo("ERROR: plan.md not found", err=True)
        sys.exit(1)

    today = datetime.now().strftime("%Y-%m-%d")
    intake_bullet = f"intake: epic {epic_id} poured"
    intake_entry = f"- {intake_bullet}"

    # Idempotency: is the intake line already recorded? Check the reserved `log.md`
    # first, then the legacy in-`plan.md` `**Phase log:**` block (an un-migrated plan
    # whose intake predates the log.md relocation).
    log_entries = _log_md_entries(Path(plan_dir))
    if log_entries is not None:
        intake_present = any(txt == intake_bullet for _d, txt in log_entries)
    else:
        intake_present = any(
            re.match(rf"- \d{{4}}-\d{{2}}-\d{{2}} intake: epic {re.escape(epic_id)} poured", ln)
            for ln in plan_md.read_text().splitlines()
        )

    # Dual-write the epic field (frontmatter + `**Field:**`) from one model. The
    # writer inserts `**Epic:**` in canonical order (after `**Status:**`) or updates
    # it in place — matching the prior anchoring.
    _write_plan_fields(Path(plan_dir), {"epic": epic_id})

    # Append the inert `intake:` entry to the reserved `log.md` (Issue 3.4 /
    # REQ-DATA-012). The `intake:` token matches neither the `review:` nor the
    # `scoping:` reader, so it never perturbs review/scoping counts.
    if not intake_present:
        okf.append_log(Path(plan_dir), intake_bullet, date=today)
    click.echo(json.dumps({
        "epic_id": epic_id,
        "epic_field": "written",
        "intake_log_entry": None if intake_present else intake_entry,
    }))


# ---------------------------------------------------------------------------
# Deliverable-class detection + completion gate (REQ-PLAN-069 / plan-030)
# ---------------------------------------------------------------------------

#: ci-release "high confidence" signals — a release/sign/notarize concern (REQ-PLAN-069a).
#: Regex patterns (matched case-insensitively) with trailing boundaries so `sign` matches
#: sign/signing/signed/signature but NOT `signal`.
_CI_RELEASE_HIGH_PATTERNS = {
    "release": r"\brelease",
    "notarize": r"\bnotariz",
    "sign": r"\bsign(?:ing|ed|ature|s)?\b",
    "codesign": r"\bcode[- ]?sign",
}
#: ci-release "low confidence" signals — keyword-only nudges (REQ-PLAN-069a).
_CI_RELEASE_LOW_KEYWORDS = (
    "workflow_dispatch", "self-hosted", "self hosted", "runner", "deploy",
    "pipeline", "github actions", "workflow",
)
#: a merged-tree changed path under this prefix is a strong ci-release signal.
_CI_RELEASE_PATH_MARKER = ".github/workflows/"

#: F2 (REQ-CLI-015) — negative-context guards. Phrases matching these are removed from
#: the scan region before signal matching: each is a measured collision where a trigger
#: token appears in prose that says nothing about shipping a release.
#:
#: STOP RULE — no keyword is added to this list without a corpus re-measurement showing
#: it moves `FP`. This list is a known-incomplete blocklist, not a general solution. It
#: structurally CANNOT cover the residual class: plan text that *consumes or references*
#: a release rather than producing one. Measured examples still false-positive with this
#: list in place — "pinned release binary", "pinned signed static binary via get_url",
#: "kept until the next major release of yf" — because the distinguishing feature is the
#: VERB, not the noun, and a noun blocklist cannot see verbs. Chasing them one phrase at
#: a time grows this list without bound and was measured to remove ZERO false positives
#: from the labeled corpus. The structural alternative is F5 (code spans are not claims,
#: exempt from this rule because it does not enumerate); the honest remedy for what
#: remains is the `evidence` basis reported by F4, not another pattern here.
_CI_RELEASE_NEGATIVE_CONTEXT = (
    r"\bself[- ]signed\b",
    r"\bsigned certificate\b",
    r"\brelease (?:notes|cycle|cadence)\b",
    r"\b(?:metrics|logs|traces) pipeline\b",
    r"\bdeployed by\b",
)


#: F1 (REQ-CLI-015): the `##` sections the ci-release prose scan reads. The plan's own
#: docstring always claimed this region; the implementation scanned the whole file, so a
#: verb in the H1 (`# Plan: Deploy ...`), a Motivation paragraph, or a Risks-table cell
#: scored as if the plan announced it ships releases.
_CI_RELEASE_SCAN_SECTIONS = ("epics", "upstream issues", "success criteria")


def _ci_release_scan_region(text: str) -> str:
    """Return the lowercased ci-release scan region of a plan.md (REQ-CLI-015).

    **F1 — section scope.** Only the Epics / Upstream Issues / Success Criteria `##`
    sections are read. Everything else (title, Objective, Motivation, Approach,
    Investigation Findings, Risks) is out of region: those sections describe context and
    hazards, not the deliverable.

    **F5 — code is not prose.** Fenced blocks and inline code spans are stripped. A
    trigger word inside a command, a regex, or a quoted example is not a claim that the
    plan ships releases. Structural rather than enumerated, so it cannot grow.

    **F2 — negative-context guards.** Measured collision phrases are removed before
    matching. Known-incomplete by construction; see the stop rule on the pattern list.

    None of this closes the **self-reference class**: a plan whose *subject* is releases,
    signing, or the deliverable class itself matches in ordinary prose, and no keyword
    approach can distinguish that from a plan that ships one. plan-039 is the worked
    demonstration. The honest remedy is the reported `evidence` basis, not more patterns.

    An empty result (no recognized sections) is a scan over nothing, not a scan over
    everything — a malformed plan yields no signal rather than a false positive.
    """
    region: list[str] = []
    for chunk in re.split(r"^## ", text, flags=re.M)[1:]:
        head, _, body = chunk.partition("\n")
        if head.strip().lower() in _CI_RELEASE_SCAN_SECTIONS:
            region.append(body)
    hay = "\n".join(region).lower()
    # F5: strip fenced blocks first (they may themselves contain backticks), then inline
    # code spans. Structural, not a blocklist — it enumerates nothing, so it is exempt
    # from F2's stop rule and cannot grow.
    hay = re.sub(r"^ {0,3}(`{3,}|~{3,}).*?^ {0,3}\1", " ", hay, flags=re.S | re.M)
    hay = re.sub(r"(`+)(?:(?!\1).)*?\1", " ", hay, flags=re.S)
    # F2: drop measured collision phrases before matching. See the stop rule beside
    # `_CI_RELEASE_NEGATIVE_CONTEXT` — this list is known-incomplete by construction.
    for pat in _CI_RELEASE_NEGATIVE_CONTEXT:
        hay = re.sub(pat, " ", hay)
    return hay


def _read_deliverable_class(plan_md_text: str) -> str:
    """Return the plan's deliverable class (REQ-PLAN-069a), default `standard`.

    Frontmatter-first with `**Deliverable-class:**` fallback (REQ-DATA-015). An
    absent field means `standard` — the completion gate is then a no-op.
    """
    val = _read_plan_field(plan_md_text, "deliverable_class")
    if val is None:
        return "standard"
    val = val.strip().lower()
    return val if val in DELIVERABLE_CLASSES else "standard"


def _classify_deliverable(plan_dir: Path, changed: tuple[str, ...] = ()) -> dict:
    """Heuristic-suggest a deliverable class (REQ-PLAN-069a / REQ-CLI-015).

    Scans the plan's epics/upstream/success-criteria text and any `changed`
    merged-tree paths for ci-release signals. Pure read, no mutation. Returns
    `{suggested_class, signals, confidence}`:
      - `suggested_class` — `ci-release` when any signal matched, else `standard`;
      - `signals` — the matched tokens/paths (sorted, de-duplicated);
      - `confidence` — `high` when a `.github/workflows/**` path or a
        release/sign/notarize keyword matched, else `low`.
    """
    plan_md = plan_dir / "plan.md"
    text = plan_md.read_text() if plan_md.exists() else ""
    hay = _ci_release_scan_region(text)

    high: set[str] = set()
    low: set[str] = set()

    for path in changed:
        if _CI_RELEASE_PATH_MARKER in path.replace("\\", "/"):
            high.add(f"path:{path}")

    for name, pat in _CI_RELEASE_HIGH_PATTERNS.items():
        if re.search(pat, hay):
            high.add(name)
    for kw in _CI_RELEASE_LOW_KEYWORDS:
        if kw in hay:
            low.add(kw)

    signals = sorted(high) + sorted(low)
    # F4 (REQ-CLI-015): report the EVIDENCE BASIS, not just a severity word. The path
    # marker is the only non-prose signal, and `changed` is empty at intake (SKILL.md
    # §4.1.5) — so `confidence` is effectively constant at the point an operator reads
    # it. `evidence` is what actually distinguishes a suggestion worth acting on from a
    # keyword that appeared in a sentence.
    path_backed = any(s.startswith("path:") for s in high)
    evidence = "path-backed" if path_backed else "prose-only"

    # F3: a ci-release suggestion requires a HIGH-tier signal. Low-tier keywords are
    # reported as informational, never as a suggestion on their own — `runner`,
    # `deploy`, `pipeline`, and `workflow` appear throughout ordinary infrastructure
    # prose, so keying the suggestion on them made the field a constant.
    if not high:
        return {
            "suggested_class": "standard",
            "signals": signals,
            "confidence": "low",
            "evidence": evidence,
        }
    return {
        "suggested_class": "ci-release",
        "signals": signals,
        # `high` is reserved for the path marker. A prose-only match is `low` however
        # many keywords hit: quantity of prose is not quality of evidence.
        "confidence": "high" if path_backed else "low",
        "evidence": evidence,
    }


def _has_validated_bullet(plan_dir: Path) -> bool:
    """True iff a `- validated:` green-execution attestation exists (REQ-PLAN-069b).

    Reads the reserved `log.md` (REQ-DATA-016); falls back to the legacy in-`plan.md`
    `**Phase log:**` block for un-migrated bundles. `validated:` is a non-status token
    — matching it here perturbs no review-count/grandfather/status parser.
    """
    entries = _log_md_entries(plan_dir)
    if entries is not None:
        return any(txt.startswith("validated:") for _d, txt in entries)
    plan_md = plan_dir / "plan.md"
    if not plan_md.exists():
        return False
    for line in _plan_phase_log_lines(plan_md.read_text()):
        if re.match(r"- (?:\d{4}-\d{2}-\d{2} )?validated:", line):
            return True
    return False


def _bead_metadata(issue: dict) -> dict:
    """Return a bead's metadata as a dict (bd may serialize it as a JSON string)."""
    meta = issue.get("metadata")
    if isinstance(meta, dict):
        return meta
    if isinstance(meta, str) and meta.strip():
        try:
            parsed = json.loads(meta)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _bead_labels(issue: dict) -> list[str]:
    """Return a bead's labels as a list (bd may key them under `labels`/`label`)."""
    for key in ("labels", "label"):
        val = issue.get(key)
        if isinstance(val, list):
            return [str(x) for x in val]
        if isinstance(val, str) and val.strip():
            return [p.strip() for p in val.split(",") if p.strip()]
    return []


def _open_deferred_validation_bead(plan_id: str) -> dict | None:
    """Find an OPEN, out-of-tree `deferred-validation` bead for this plan (REQ-PLAN-069).

    Queries `bd list --label deferred-validation --all` and returns the first bead
    that is (a) not closed and (b) carries `metadata.plan == plan_id`. The bead is a
    standalone issue (no plan-tree parent), so `close_cascade` never fail-louds on it.
    Returns the matching issue dict, or None.
    """
    for issue in _bd_list("--label", "deferred-validation", "--all"):
        status = str(issue.get("status", "")).lower()
        if status == "closed":
            continue
        if _bead_metadata(issue).get("plan") == plan_id:
            return issue
    return None


@cli.command("set-deliverable-class")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.argument("deliverable_class")
def set_deliverable_class(plan_dir: str, deliverable_class: str):
    """Write the operator-confirmed deliverable class (REQ-PLAN-069a / REQ-CLI-015).

    Dual-writes `deliverable_class`↔`**Deliverable-class:**` (frontmatter + header
    line) via the single field writer. Idempotent. Rejects any value outside
    `standard | ci-release`. The field sits above the first `## ` heading, so it is
    fingerprint-excluded (REQ-PORT-040) and does not stale an approved plan.
    """
    dc = deliverable_class.strip().lower()
    if dc not in DELIVERABLE_CLASSES:
        click.echo(json.dumps({
            "error": f"invalid deliverable_class {deliverable_class!r}; "
                     f"expected one of {list(DELIVERABLE_CLASSES)}"
        }), err=True)
        sys.exit(1)
    _write_plan_fields(Path(plan_dir), {"deliverable_class": dc})
    click.echo(json.dumps({"deliverable_class": dc, "written": True}))


@cli.command("classify-deliverable")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--changed", multiple=True,
              help="A merged-tree changed path (repeatable) to include in the scan.")
@click.option("--json-output", "--json", "json_output", is_flag=True,
              help="Emit the structured object (default is also JSON).")
def classify_deliverable(plan_dir: str, changed: tuple[str, ...], json_output: bool):
    """Suggest a deliverable class from plan text + changed paths (REQ-CLI-015).

    Pure read. Emits `{suggested_class, signals, confidence}` — the operator confirms
    or overrides, then `set-deliverable-class` writes the decision.
    """
    result = _classify_deliverable(Path(plan_dir), tuple(changed))
    click.echo(json.dumps(result))


@cli.command("attest-validation")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.argument("run")
@click.option("--note", default="", help="Short note describing what ran green.")
def attest_validation(plan_dir: str, run: str, note: str):
    """Append a green-execution attestation to `log.md` (REQ-PLAN-069b / REQ-CLI-017).

    Writes a `- validated: <run> — <note>` bullet under today's date heading via
    `okf.append_log` (newest-first). A hand-written bullet of the same form is equally
    valid; this verb guarantees the recognized shape.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    bullet = f"validated: {run}" + (f" — {note}" if note else "")
    okf.append_log(Path(plan_dir), bullet, date=today)
    click.echo(json.dumps({"validated": run, "date": today, "log_entry": f"- {bullet}"}))


@cli.command("complete-gate")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "json_output", is_flag=True,
              help="Emit the structured verdict (default is also JSON).")
def complete_gate(plan_dir: str, json_output: bool):
    """Hard-gate `complete` for ci-release plans (REQ-PLAN-069 / REQ-CLI-016).

    No-op (clean pass) for a `standard`/unset deliverable class. For `ci-release`,
    passes iff a `log.md` `- validated:` bullet exists OR an open out-of-tree
    `deferred-validation` bead scoped to this plan exists; else fail-loud (exit
    non-zero + JSON verdict + actionable remediation), mirroring `close_cascade.py`.
    """
    pdir = Path(plan_dir)
    plan_md = pdir / "plan.md"
    if not plan_md.exists():
        # REQ-COMPLETE-003(a): the envelope goes to STDOUT on EVERY path, including
        # this one. SKILL.md captures with `GATE=$(...)`, which captures stdout only,
        # so a stderr verdict here yields an empty capture and an unreportable halt.
        #
        # This is `fail`, not `inconclusive`: the answer is DEFINITE — there is no such
        # plan folder — which is the same split Issue 3.3 draws for close_cascade.py
        # (bead-absent halts; bd-did-not-answer is inconclusive). A typo'd plan_dir
        # must not sail through to `set complete`.
        click.echo(json.dumps({
            "verdict": "fail", "passed": False, "noop": False,
            "deliverable_class": None,
            "reason": f"plan.md not found under {plan_dir}",
            "remediation": "Check the plan_dir argument, then re-run §6.4.",
        }))
        sys.exit(1)

    dclass = _read_deliverable_class(plan_md.read_text())
    if dclass != "ci-release":
        click.echo(json.dumps({
            "verdict": "pass",
            "passed": True, "noop": True, "deliverable_class": dclass,
            "reason": "standard/unset deliverable class — completion criterion N/A",
            "remediation": None,
        }))
        return

    plan_id = _plan_id_from_dir(pdir)
    has_attestation = _has_validated_bullet(pdir)
    deferred = _open_deferred_validation_bead(plan_id)

    if has_attestation or deferred is not None:
        click.echo(json.dumps({
            "verdict": "pass",
            "passed": True, "noop": False, "deliverable_class": dclass,
            "evidence": "validated-bullet" if has_attestation else "deferred-bead",
            "deferred_bead": deferred.get("id") if deferred else None,
            "reason": "ci-release plan carries green-execution evidence",
            "remediation": None,
        }))
        return

    remediation = (
        "ci-release plan cannot complete: no green-execution evidence. Either "
        f"(a) attest one observed green run — `plan_manager.py attest-validation {plan_dir} "
        "<run-url> --note '<what ran>'` (see spec/ci-release-completion.md for the "
        "workflow_dispatch no-publish test-build pattern); or (b) file a standalone "
        "out-of-tree deferred-validation bead — `bd create \"Deferred validation: "
        f"{plan_id} ...\" -t task -p 1 --label deferred-validation --metadata "
        f"'{{\"plan\":\"{plan_id}\"}}'` and push it individually upstream."
    )
    # REQ-COMPLETE-003(a): STDOUT on the failing path too — this was the measured live
    # defect (E2). SKILL.md's `GATE=$(...)` captures stdout, so writing the fail verdict
    # to stderr printed NOTHING on exactly the path the operator needs to read.
    click.echo(json.dumps({
        "verdict": "fail",
        "passed": False, "noop": False, "deliverable_class": dclass,
        "reason": "ci-release plan has neither a log.md '- validated:' bullet nor an "
                  "open out-of-tree deferred-validation bead",
        "remediation": remediation,
    }))
    sys.exit(1)


# ---------------------------------------------------------------------------
# verify-reconcile — the §6.4 HALTING step that proves RECONCILE actually ran
# (REQ-PLAN-074 / plan-043 Epic 1, #136).
#
# WHY THIS IS A SCRIPT VERB AND NOT ANOTHER INSTRUCTION
# ----------------------------------------------------
# `agents/reconciler.md` step 4 ALREADY prescribes this verification, in prose, and
# plan-039 skipped it in the same breath as step 3 — then reported success. The failure
# was not a swallowed error, not filtering, and not non-dispatch: it was a FALSE SUCCESS
# ASSERTION. Adding a sixth instruction to a five-instruction list that was partially
# ignored is a null change, so the check is mechanical instead.
#
# WHY STATE ALONE IS INSUFFICIENT (D6)
# ------------------------------------
# Asserting only the issue's end state would have PASSED plan-039 today: #108 is CLOSED —
# closed by a human 15 hours later, as manual repair. So each row must also carry a
# `<plan-id>` mention, which is the artifact reconciliation itself leaves behind.
#
# NETWORK CALLS INSIDE A HALTING STEP (R1/R10)
# --------------------------------------------
# A `gh` outage, rate limit, auth lapse or hang must NOT halt completion on healthy work.
# Every `gh` failure — including a timeout — is INCONCLUSIVE, never `fail`. Only a
# definite wrong end state is `fail`. Calls are bounded by _GH_TIMEOUT_S.
# ---------------------------------------------------------------------------

_GH_TIMEOUT_S = 30  # REQ-COMPLETE-003(f): bounded, so a hung `gh` cannot hang land-the-plane.


def _gh_issue_view(number: str) -> tuple[dict | None, str | None]:
    """Fetch one issue. Returns (payload, error). A non-None error means INCONCLUSIVE."""
    try:
        r = subprocess.run(
            ["gh", "issue", "view", number, "--json", "state,stateReason,comments,title"],
            capture_output=True, text=True, timeout=_GH_TIMEOUT_S,
        )
    except FileNotFoundError:
        return None, "`gh` not found on PATH"
    except subprocess.TimeoutExpired:
        return None, f"`gh` timed out after {_GH_TIMEOUT_S}s"
    except OSError as e:                                    # pragma: no cover - defensive
        return None, f"`gh` could not be run: {e}"
    if r.returncode != 0:
        return None, (r.stderr or r.stdout or "gh exited non-zero").strip().splitlines()[0]
    try:
        return json.loads(r.stdout), None
    except json.JSONDecodeError as e:
        return None, f"unparseable `gh` output: {e}"


def _mentions_plan_id(payload: dict, plan_id: str) -> bool:
    """Does any comment mention this plan?

    Matching is NORMALIZED (case- and punctuation-tolerant) but is NEVER a time window.
    A "some comment postdating execution start" heuristic was explicitly rejected: it
    would have PASSED plan-039, since #108 carried a human comment 15 h after the
    reconcile bead closed — exactly the case this check must fail (plan-043 R2).
    """
    def _norm(s: str) -> str:
        return re.sub(r"[^a-z0-9]", "", (s or "").lower())

    needle = _norm(plan_id)
    if not needle:
        return False
    for c in payload.get("comments") or []:
        if needle in _norm(c.get("body", "")):
            return True
    return False


def _verify_row(row: dict, plan_id: str) -> dict:
    """Verify one Upstream Issues row. Returns {issue, disposition, verdict, detail}."""
    number, disp = row["issue"], row["disposition"]
    payload, err = _gh_issue_view(number)
    if err is not None:
        return {"issue": number, "disposition": disp, "verdict": "inconclusive",
                "detail": f"could not read #{number}: {err}"}

    state = (payload.get("state") or "").upper()
    reason = (payload.get("stateReason") or "").upper()
    mentioned = _mentions_plan_id(payload, plan_id)

    if disp == "include":
        if state != "CLOSED":
            return {"issue": number, "disposition": disp, "verdict": "fail",
                    "detail": f"#{number} is {state}; an `include` row must be CLOSED"}
        if not mentioned:
            return {"issue": number, "disposition": disp, "verdict": "fail",
                    "detail": f"#{number} is CLOSED but no comment mentions {plan_id} — "
                              "closure is unattributed, so reconciliation is unproven"}
        return {"issue": number, "disposition": disp, "verdict": "pass",
                "detail": f"#{number} CLOSED with a {plan_id} mention"}

    if disp == "supersede":
        if state != "CLOSED" or reason != "NOT_PLANNED":
            return {"issue": number, "disposition": disp, "verdict": "fail",
                    "detail": f"#{number} is {state}/{reason or 'no stateReason'}; a "
                              "`supersede` row must be CLOSED as NOT_PLANNED"}
        return {"issue": number, "disposition": disp, "verdict": "pass",
                "detail": f"#{number} CLOSED as NOT_PLANNED"}

    if disp == "partial":
        if state != "OPEN":
            return {"issue": number, "disposition": disp, "verdict": "fail",
                    "detail": f"#{number} is {state}; a `partial` row must stay OPEN "
                              "(its remaining half is still real work)"}
        if not mentioned:
            return {"issue": number, "disposition": disp, "verdict": "fail",
                    "detail": f"#{number} is OPEN but no comment mentions {plan_id} — "
                              "the deferred half was never recorded upstream"}
        return {"issue": number, "disposition": disp, "verdict": "pass",
                "detail": f"#{number} OPEN with a {plan_id} mention"}

    if disp == "deferred":
        # REQ-PLAN-074 as amended by plan-048 Issue 0.2 (D-7). A deferral is a NON-ACTION:
        # the row records a scoping decision taken in THIS plan, not work done on that
        # issue. There is nothing to attribute upstream, so there is deliberately NO
        # plan-id-mention requirement — demanding one would make every deferring plan halt
        # its own reconcile. plan-048 itself carries five `deferred` rows.
        #
        # The not-OPEN direction is still a real assertion, not a waiver: an issue the plan
        # declared it would return to, which is closed by the time reconcile runs,
        # CONTRADICTS the disposition.
        if state != "OPEN":
            return {"issue": number, "disposition": disp, "verdict": "fail",
                    "detail": f"#{number} is {state}; a `deferred` row must stay OPEN — "
                              "the plan declared it would return to this, so a closed "
                              "issue contradicts the disposition"}
        return {"issue": number, "disposition": disp, "verdict": "pass",
                "detail": f"#{number} OPEN; `deferred` is a non-action and requires no "
                          f"{plan_id} mention"}

    if disp == "tracker":
        # INCONCLUSIVE BY CONSTRUCTION (spec/cli.md REQ-CLI-018), and deliberately NOT
        # collapsed into `deferred`. The coarse tracker is closed by the land-the-plane
        # sweep, not by reconciliation, so it carries no end-state contract in EITHER
        # direction. `deferred` is report-only because there is nothing to attribute;
        # `tracker` is report-only because reconcile is not the thing that closes it.
        # The two are report-only for different reasons and neither may absorb the other.
        return {"issue": number, "disposition": disp, "verdict": "inconclusive",
                "detail": f"#{number} is a coarse tracker; it is closed by the "
                          "land-the-plane sweep, not by reconciliation"}

    # An UNRECOGNISED disposition is `fail`, not `inconclusive` (plan-048 Issue 3.4).
    # Every recognised literal is handled above, and the producer surfaces offer exactly
    # those, so anything else is a TYPO in the table — and a fail-loud step must not
    # silently pass a typo. This is also what makes R2c's normalization load-bearing:
    # before it, a bolded `**partial**` reached here as an unrecognised literal.
    return {"issue": number, "disposition": disp, "verdict": "fail",
            "detail": f"#{number} has disposition {disp!r}, which is not one of "
                      "include|exclude|partial|supersede|deferred|tracker — an "
                      "unrecognised literal is a typo in the table, not a valid state"}


@cli.command("verify-reconcile")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "json_output", is_flag=True,
              help="Emit the structured verdict (default is also JSON).")
def verify_reconcile(plan_dir: str, json_output: bool):
    """Verify every non-`exclude` Upstream Issues row reached its end state (#136).

    A `halting` §6.4 step with `command` remediation-kind (REQ-COMPLETE-003).
    Aggregate rule: ANY row `fail` -> `fail` (halt), even alongside `inconclusive`
    rows; inconclusive-only -> `inconclusive` (report, never halt).
    """
    pdir = Path(plan_dir)
    plan_md = pdir / "plan.md"
    if not plan_md.exists():
        click.echo(json.dumps({
            "verdict": "fail", "passed": False, "rows": [],
            "reason": f"plan.md not found under {plan_dir}",
            "remediation": "Check the plan_dir argument, then re-run §6.4.",
        }))
        sys.exit(1)

    plan_id = _plan_id_from_dir(pdir)
    rows = [r for r in parse_upstream_rows(plan_md.read_text())
            if r["disposition"] not in ("", "exclude")]

    results = [_verify_row(r, plan_id) for r in rows]

    # ---- Aggregate rule (plan-043 C9). Stated, not implicit. -------------------
    # ANY row `fail` => `fail`, EVEN IF other rows are `inconclusive`. A single
    # collapsed verdict would otherwise either halt on an outage or mask a real
    # regression — and the plan-039 scenario is itself a 3-of-5 partial.
    failed = [r for r in results if r["verdict"] == "fail"]
    unknown = [r for r in results if r["verdict"] == "inconclusive"]

    if failed:
        verdict = "fail"
        reason = (f"{len(failed)} of {len(results)} upstream row(s) did not reach the "
                  f"end state their disposition requires")
        remediation = "Reconcile each failing row upstream, then re-run §6.4:\n" + "\n".join(
            f"  #{r['issue']} ({r['disposition']}): {r['detail']}\n"
            f"    gh issue comment {r['issue']} --body '<what {plan_id} did>'"
            + (f" && gh issue close {r['issue']}" if r["disposition"] == "include" else "")
            for r in failed
        )
    elif unknown:
        verdict = "inconclusive"
        reason = (f"{len(unknown)} of {len(results)} upstream row(s) could not be checked "
                  "— completion is NOT blocked, but the rows below are unverified")
        remediation = ("Re-run `verify-reconcile` once the checker is available, and "
                       "confirm by hand:\n" + "\n".join(
                           f"  #{r['issue']}: {r['detail']}" for r in unknown))
    else:
        verdict = "pass"
        reason = (f"all {len(results)} non-exclude upstream row(s) reached their required "
                  "end state" if results else "no non-exclude upstream rows to verify")
        remediation = None

    click.echo(json.dumps({
        "verdict": verdict,
        "passed": verdict == "pass",
        "plan_id": plan_id,
        "rows": results,
        "reason": reason,
        "remediation": remediation,
    }, indent=2))

    # REQ-COMPLETE-003(c): only `fail` halts. `inconclusive` NEVER halts (R1).
    if verdict == "fail":
        sys.exit(1)


# ---------------------------------------------------------------------------
# Content-fingerprint re-review gate (#64 / Issue 5.1)
#
# Approval binds to a normalized hash of plan.md's CONTENT sections. The hashed span
# is every `## ` section from Objective through Success Criteria, EXCLUDING the
# self-trigger set (REQ-PORT-040): the header preamble (all `**Field:**` lines +
# `**Phase log:**`, which precede the first `## ` and are structurally dropped) and
# the `## Upstream Issues` section (its "Resolved By" cells are filled at the relocated
# pour and would else flip the hash mid-execution). Operator-Resolutions tables live in
# reviews/pass-N.md, not plan.md, so they are already out of scope.
# ---------------------------------------------------------------------------

FINGERPRINT_EXCLUDE_SECTIONS = {"upstream issues"}


def _plan_content_sections(text: str) -> list[tuple[str, str]]:
    """Split plan.md into (title, body) per top-level `## ` section.

    The preamble before the first `## ` — the `**Field:**` header lines and the
    `**Phase log:**` block — is dropped, which self-excludes the bookkeeping surface.
    """
    sections: list[tuple[str, str]] = []
    cur_title: str | None = None
    cur: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^## (.+?)\s*$", line)
        if m:
            if cur_title is not None:
                sections.append((cur_title, "\n".join(cur)))
            cur_title = m.group(1).strip()
            cur = []
        elif cur_title is not None:
            cur.append(line)
    if cur_title is not None:
        sections.append((cur_title, "\n".join(cur)))
    return sections


def _plan_content_fingerprint(plan_dir: Path) -> str | None:
    """sha256 of the normalized content sections (REQ-PORT-040). None if no plan.md.

    Normalization (so cosmetic edits don't flip the hash): per-line right-strip and
    blank-line removal, each section prefixed by its lowercased title. Excludes the
    `## Upstream Issues` section and the (structurally dropped) header preamble.
    """
    plan_md = plan_dir / "plan.md"
    if not plan_md.exists():
        return None
    parts: list[str] = []
    for title, body in _plan_content_sections(plan_md.read_text()):
        if title.strip().lower() in FINGERPRINT_EXCLUDE_SECTIONS:
            continue
        parts.append(title.strip().lower())
        parts.extend(ln.rstrip() for ln in body.splitlines() if ln.strip())
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()


def _read_plan_fingerprint_field(plan_md_text: str) -> str | None:
    """Return the stored fingerprint (frontmatter-first, `**Fingerprint:**`
    fallback), if present."""
    return _read_plan_field(plan_md_text, "fingerprint")


def _write_fingerprint_field(plan_dir: Path, fingerprint: str) -> str:
    """Dual-write the `fingerprint` header field (REQ-DATA-015).

    Routes through the single dual-writer, which emits BOTH the `**Fingerprint:**`
    header line (in canonical order — after `**Epic:**`/`**Status:**`) AND the
    `fingerprint` frontmatter key from one model. Both surfaces are self-excluded
    from the content hash (above the first `## `). Idempotent. Returns "written" or
    "updated".
    """
    plan_md = plan_dir / "plan.md"
    had = _read_plan_field(plan_md.read_text(), "fingerprint") is not None
    _write_plan_fields(plan_dir, {"fingerprint": fingerprint})
    return "updated" if had else "written"


def _fingerprint_status(plan_dir: Path) -> dict:
    """Compare the stored fingerprint to the recomputed content hash.

    stale_approved is True iff a fingerprint is stored AND it no longer matches the
    current content (REQ-PORT-041). No stored fingerprint → not stale (never approved).
    """
    plan_md = plan_dir / "plan.md"
    text = plan_md.read_text() if plan_md.exists() else ""
    stored = _read_plan_fingerprint_field(text)
    current = _plan_content_fingerprint(plan_dir)
    return {
        "stored_fingerprint": stored,
        "current_fingerprint": current,
        "stale_approved": bool(stored) and stored != current,
    }


def _is_parked(status: str, fp_status: dict) -> bool:
    """Classify a plan as *parked* — approved but never executed (#86, REQ-PLAN-068).

    Parked iff status is `approved` (coarse filter) AND a stored content fingerprint is
    present and fresh — `bool(stored) and stored == current`, the same signal
    execute-eligibility keys on, NOT the "not stale_approved" test (which is also true
    when no fingerprint is stored). This excludes:
      - executing / complete            → fail the status filter
      - stale-approved                  → fail freshness (already carry the stale tag)
      - approved with no stored fp      → present-and-fresh is False (no contradictory nudge)
    """
    stored = fp_status.get("stored_fingerprint")
    current = fp_status.get("current_fingerprint")
    return status == "approved" and bool(stored) and stored == current


@cli.group()
def fingerprint():
    """Content-fingerprint re-review gate verbs (#64 / Issue 5.1)."""


@fingerprint.command("write")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True)
def fingerprint_write_cmd(plan_dir: str, as_json: bool):
    """Compute + persist the `**Fingerprint:**` field at APPROVE (REQ-PLAN-034)."""
    fp = _plan_content_fingerprint(Path(plan_dir))
    if fp is None:
        click.echo("ERROR: plan.md not found", err=True)
        sys.exit(1)
    action = _write_fingerprint_field(Path(plan_dir), fp)
    out = {"fingerprint": fp, "action": action}
    click.echo(json.dumps(out) if as_json else f"fingerprint {action}: {fp}")


@fingerprint.command("check")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True)
def fingerprint_check_cmd(plan_dir: str, as_json: bool):
    """Report stale_approved: stored fingerprint vs recomputed content hash."""
    result = _fingerprint_status(Path(plan_dir))
    if as_json:
        click.echo(json.dumps(result, indent=2))
    elif result["stale_approved"]:
        click.echo("STALE-APPROVED: plan content changed since approval "
                   "(stored fingerprint != current). Re-review required.")
    elif result["stored_fingerprint"]:
        click.echo("fingerprint current (matches approved content)")
    else:
        click.echo("no stored fingerprint (not yet approved)")


# ---------------------------------------------------------------------------
# Auto-commit at the plan→execute boundary (#63 / Issue 4.1)
#
# A local, scoped commit at the PLAN→EXECUTE handoff so a fresh execute session
# inherits a committed base and intake artifacts survive a crash/fresh clone. Local
# only — NEVER pushes (GR-PLAN-003 carve-out). Refuses the default branch fail-closed
# (REQ-PLAN-065): a detached HEAD or empty current-branch name is a hard refusal.
# ---------------------------------------------------------------------------


def _read_plan_status(plan_md_text: str) -> str | None:
    return _read_plan_field(plan_md_text, "status")


def _read_plan_objective(plan_md_text: str) -> str | None:
    m = re.search(r"^# Plan:\s*(.+?)\s*$", plan_md_text, re.MULTILINE)
    return m.group(1).strip() if m else None


def _commit_plan(plan_dir: Path) -> dict:
    """Local scoped commit of the plan folder + .beads/ (REQ-PLAN-064/065).

    Verdict: {status, ...}. status ∈ {committed, noop, refused, error}.
    Refuses (fail-closed) on the default branch or a detached HEAD; never pushes.
    """
    repo_root = _git_root()
    cur = _current_branch(repo_root)
    if cur is None:
        return {"status": "refused", "reason": "detached-head",
                "detail": "current branch is empty/detached — fail-closed, never commit."}
    default = _default_branch(repo_root)
    on_default = (cur == default) or (default is None and cur in ("main", "master"))
    if on_default:
        return {"status": "refused", "reason": "default-branch", "branch": cur,
                "detail": f"refusing to auto-commit on the default branch '{cur}' "
                          f"(REQ-PLAN-065). Plan commits land on a plan branch only."}

    plan_md = plan_dir / "plan.md"
    text = plan_md.read_text() if plan_md.exists() else ""
    plan_id = _plan_id_from_dir(plan_dir)
    phase = _read_plan_status(text) or "plan"
    objective = _read_plan_objective(text) or plan_id

    # Scoped staging — explicit pathspec, NEVER `git add -A` (REQ-PLAN-064).
    # The plan dir is always addable; `.beads/` is co-committed ONLY when it is
    # tracked/not-ignored. On a local-only beads repo `.beads/` is intentionally
    # gitignored (gh-only interchange), where `git add -- .beads` fails outright —
    # so skip that pathspec instead of erroring (issue #71).
    addpaths = [str(plan_dir)]
    beads_note = None
    if (repo_root / ".beads").exists():
        ignored = _run_git(["check-ignore", "-q", ".beads"], cwd=repo_root).returncode == 0
        if ignored:
            beads_note = ".beads/ is gitignored (local-only beads) — not co-committed."
        else:
            addpaths.append(".beads")
    add = _run_git(["add", "--", *addpaths], cwd=repo_root)
    if add.returncode != 0:
        return {"status": "error", "branch": cur,
                "detail": f"git add failed: {add.stderr.strip()}"}
    # Nothing staged → no-op (idempotent re-runs don't create empty commits).
    if _run_git(["diff", "--cached", "--quiet"], cwd=repo_root).returncode == 0:
        result = {"status": "noop", "branch": cur,
                  "detail": "no staged changes under the plan folder / .beads."}
        if beads_note:
            result["beads_note"] = beads_note
        return result

    # Commit-subject state signalling (#86, REQ-PLAN-064): the `approved`-phase intake
    # landing commit signals that the plan is approved-but-not-yet-executed, so a `git log`
    # scan cannot misread a parked plan as shipped work. Objective moves to the commit body.
    # Other phases keep the plain `plan-NNN: <phase> — <objective>` subject.
    if phase == "approved":
        subject = f"{plan_id}: INTAKE approved (awaiting /yf-plan execute)"
        commit_args = ["commit", "-m", subject, "-m", objective]
        message = subject
    else:
        message = f"{plan_id}: {phase} — {objective}"
        commit_args = ["commit", "-m", message]
    commit = _run_git(commit_args, cwd=repo_root)
    if commit.returncode != 0:
        return {"status": "error", "branch": cur,
                "detail": f"git commit failed: {commit.stderr.strip()}"}
    sha = _run_git(["rev-parse", "--short", "HEAD"], cwd=repo_root).stdout.strip()
    result = {"status": "committed", "branch": cur, "commit": sha, "message": message}
    if beads_note:
        result["beads_note"] = beads_note
    return result


@cli.command("commit-plan")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True)
def commit_plan_cmd(plan_dir: str, as_json: bool):
    """Auto-commit the plan locally at the plan→execute boundary (never pushes)."""
    result = _commit_plan(Path(plan_dir))
    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        status = result["status"]
        if status == "committed":
            click.echo(f"committed {result['commit']} on {result['branch']}: "
                       f"{result['message']}")
        else:
            click.echo(f"{status}: {result.get('detail', '')}".rstrip(": "))
    # Exit 3 on refusal so a shell caller can branch; 0 on committed/noop.
    sys.exit(3 if result["status"] in ("refused", "error") else 0)


# ---------------------------------------------------------------------------
# Worktree lifecycle engine (plan-009 Epic 1 — the extraction seam)
#
# A self-contained `worktree {ensure,path,teardown}` --json verb cluster, modeled
# on diagram-authoring/scripts/render.py's subcommand surface. Inputs are pure
# (repo_root, plan_dir) — NO yf-plan phase state — so a future standalone `worktree`
# skill is a cheap lift-and-shift (rule-of-three; see SKILL.md / plan-009 INV-5).
#
# EXTRACTION TRIGGERS (record, do not act early — plan-009 INV-5):
#   * `worktree` skill — extract this verb cluster ONLY on a committed SECOND consumer
#     (yf-plan execute is the only one today; one consumer ≈2x's v1 surface for zero reuse).
#   * acceptance skill — REALIZED as `yf-change-validation` (plan-015 D.1). The
#     validate-merged / validate-cmd seam below now delegates, when present, to that
#     skill's engine (skills/yf-change-validation/scripts/change_validation.py) over the
#     merged tree. There is NO separate `acceptance` skill — do not hunt for one.
#   When extracted, the consumer keeps a PROSE soft-dep (present → delegate/worktree flow;
#   absent → fallback/in-place), like diagram-authoring. The yf-change-validation tie-in is
#   detect-at-runtime (approved CHANGE-VALIDATION.md + resolvable script), NOT a frontmatter
#   edge. NEVER add `worktree`/`yf-change-validation` to a SKILL.md frontmatter
#   `depends-on-skill` edge — that is force-install, the wrong coupling
#   (plan-008 EXP-002 mitigation pattern).
#
# Placement (INV-1): a gitignored top-level `.worktrees/<plan-id>`, branch = plan-id
# verbatim. NOT `.git/worktree/<plan>` (nests a live tree in the gitdir; rejected).
# Beads (INV-2): the worktree shares the primary's single Dolt DB via git-common-dir;
# `ensure` runtime-probes `bd` from inside the new worktree because that resolution is
# version/config-fragile (M4 — a viability fallback, not only the one-time gate).
# ---------------------------------------------------------------------------

WORKTREES_DIR = Path(".worktrees")
WORKTREES_GITIGNORE_ANCHOR = "/.worktrees/"

# Operator config keys in .yf-plan.local.json (Issue 2.4 / Issue 3.3):
#   "execute.worktree": false   → opt out of worktree mode (run in-place)
#   "validate-cmd": "<shell>"    → project integration suite run against the merged tree
CONFIG_KEY_WORKTREE = "execute.worktree"
CONFIG_KEY_VALIDATE_CMD = "validate-cmd"
#   "landing-strategy": "main" | "feature-branch"  → execute base + merge target (Issue 2.1)
CONFIG_KEY_LANDING_STRATEGY = "landing-strategy"
LANDING_STRATEGY_DEFAULT = "main"
LANDING_STRATEGIES = ("main", "feature-branch")


def _worktree_opted_out() -> bool:
    """True iff the operator set `execute.worktree` false in .yf-plan.local.json (2.4).

    Default is opt-IN (worktree mode on). Tolerates both the flat dotted key and a
    nested {"execute": {"worktree": false}} form.
    """
    cfg = _read_config()
    if CONFIG_KEY_WORKTREE in cfg:
        return cfg[CONFIG_KEY_WORKTREE] is False
    nested = cfg.get("execute")
    if isinstance(nested, dict) and "worktree" in nested:
        return nested["worktree"] is False
    return False


def _resolve_validate_cmd() -> str | None:
    """The project integration suite from .yf-plan.local.json `validate-cmd` (3.3).

    Unset → None (§6.1.5 runs plan gates only + emits the cross-plan-not-checked notice).
    """
    cfg = _read_config()
    val = cfg.get(CONFIG_KEY_VALIDATE_CMD)
    return val if isinstance(val, str) and val.strip() else None


def _resolve_landing_strategy() -> str:
    """The landing strategy from .yf-plan.local.json `landing-strategy` (Issue 2.1).

    `main` (default) → the execute worktree base AND the §6.1 merge target are `main`;
    plans land by merging to `main`.
    `feature-branch` → the execute base is the feature `<plan-id>` branch; plans land on
    that feature branch (preserved by teardown) for later operator integration.
    Any unset or unrecognized value falls back to `main` (REQ-BRANCH-003).
    """
    cfg = _read_config()
    val = cfg.get(CONFIG_KEY_LANDING_STRATEGY)
    if isinstance(val, str) and val.strip() in LANDING_STRATEGIES:
        return val.strip()
    return LANDING_STRATEGY_DEFAULT


#   "autonomy": "autonomous" | "checkpointed"   → execution/review stop posture (2.1)
CONFIG_KEY_AUTONOMY = "autonomy"
AUTONOMY_DEFAULT = "autonomous"
AUTONOMY_LEVELS = ("autonomous", "checkpointed")

#   "sweep-gates": "probe" | "all"   → execute-start sweep class scope (3.6)
CONFIG_KEY_SWEEP_GATES = "sweep-gates"
SWEEP_GATES_DEFAULT = "probe"
SWEEP_GATES_VALUES = ("probe", "all")

_SWEEP_GATES_OVERRIDE: str | None = None


def _set_sweep_gates_override(val: str | None) -> None:
    """Install the per-invocation `--sweep-gates` override (3.6)."""
    global _SWEEP_GATES_OVERRIDE
    if val is not None and val not in SWEEP_GATES_VALUES:
        raise ValueError(
            f"unknown sweep-gates value {val!r}; expected one of {', '.join(SWEEP_GATES_VALUES)}"
        )
    _SWEEP_GATES_OVERRIDE = val


def _resolve_sweep_gates() -> str:
    """Which gate classes the execute-start sweep runs (3.6).

    `probe` (default) keeps execute start in seconds; `all` adds the `build` class, which
    §6.1.5 reserves for once-per-land. `consent` and `manual` are never auto-run at any
    setting — neither is a cost question, and no flag makes a green test into authorization.
    """
    if _SWEEP_GATES_OVERRIDE is not None:
        return _SWEEP_GATES_OVERRIDE
    cfg = _read_config()
    val = cfg.get(CONFIG_KEY_SWEEP_GATES)
    if isinstance(val, str) and val.strip() in SWEEP_GATES_VALUES:
        return val.strip()
    return SWEEP_GATES_DEFAULT


#   "max-attempts": <int>   → EXECUTION-phase bound on per-bead retries (2.8)
CONFIG_KEY_MAX_ATTEMPTS = "max-attempts"
MAX_ATTEMPTS_DEFAULT = 3


def _resolve_max_attempts() -> int:
    """The per-bead attempt threshold `N` for `yf_attempts` (2.8, stop class 4).

    Distinct from `max_review_cycles` in both phase and semantics: this one is
    EXECUTION-phase, per-bead, and **resets** on close, whereas the review counter is
    PLAN-phase, per-plan, and monotonic. Two counters exist because Issue 2.4 grants
    autonomy before any bead exists, so `yf_attempts` structurally cannot reach it.
    """
    cfg = _read_config()
    val = cfg.get(CONFIG_KEY_MAX_ATTEMPTS)
    if isinstance(val, bool):
        return MAX_ATTEMPTS_DEFAULT
    if isinstance(val, int) and val >= 1:
        return val
    return MAX_ATTEMPTS_DEFAULT


#   "max-review-cycles": <int>   → Phase-3 bound on the autonomous review loop (2.4a)
CONFIG_KEY_MAX_REVIEW_CYCLES = "max-review-cycles"
MAX_REVIEW_CYCLES_DEFAULT = 5

_MAX_REVIEW_CYCLES_OVERRIDE: int | None = None


def _set_max_review_cycles_override(n: int | None) -> None:
    """Install the per-invocation `max_review_cycles` raise (2.4a).

    This is the operator's ESCAPE from an escalation. It is deliberately the only exit:
    the counter does not auto-reset, so without an explicit raise every subsequent cycle
    re-escalates immediately — a plan that has burned N review cycles should not silently
    resume.
    """
    global _MAX_REVIEW_CYCLES_OVERRIDE
    if n is not None and (not isinstance(n, int) or n < 1):
        raise ValueError(f"max-review-cycles must be a positive integer, got {n!r}")
    _MAX_REVIEW_CYCLES_OVERRIDE = n


def _resolve_max_review_cycles() -> int:
    """The Phase-3 review-loop bound, through the same tiers as `_resolve_autonomy`."""
    if _MAX_REVIEW_CYCLES_OVERRIDE is not None:
        return _MAX_REVIEW_CYCLES_OVERRIDE
    cfg = _read_config()
    val = cfg.get(CONFIG_KEY_MAX_REVIEW_CYCLES)
    if isinstance(val, bool):  # bool is an int subclass; reject it explicitly
        return MAX_REVIEW_CYCLES_DEFAULT
    if isinstance(val, int) and val >= 1:
        return val
    return MAX_REVIEW_CYCLES_DEFAULT


# Per-invocation override, set by the prose-detected token (2.3). Not a config file
# key: it is the highest tier, above `.yf/plan/config.local.json`, and lives only for
# the duration of one process. `config-resolve --autonomy X` reports it as `flag`.
_AUTONOMY_OVERRIDE: str | None = None


def _set_autonomy_override(level: str | None) -> None:
    """Install the per-invocation autonomy override (2.3).

    Prose detects the token; this validates and resolves it. An unrecognised value is
    rejected rather than silently ignored — a misdetected token that quietly fell back
    to the default would be indistinguishable from no token at all, which is the whole
    failure mode the `log.md` echo exists to make auditable.
    """
    global _AUTONOMY_OVERRIDE
    if level is None:
        _AUTONOMY_OVERRIDE = None
        return
    if level not in AUTONOMY_LEVELS:
        raise ValueError(
            f"unknown autonomy level {level!r}; expected one of {', '.join(AUTONOMY_LEVELS)}"
        )
    _AUTONOMY_OVERRIDE = level


def _config_source(key: str) -> tuple[object, str]:
    """The raw value of `key` and the tier it came from, highest tier first.

    Returns `(value, source)` where `source` is one of `config.local`, `config.json`,
    `legacy`, or `default` (the last with `value` `None`). This walks the tiers itself
    rather than reading the merged dict, because the merge is lossy by construction:
    once `_read_config()` has flattened three files into one, the winning tier is
    unrecoverable — and *which tier won* is the question `config-resolve` exists to
    answer. `flag` is not produced here; the caller adds it, since a per-invocation
    override lives in process memory rather than in any file.

    Total, like `_bootstrap_config`: an unreadable or malformed tier is skipped rather
    than raised, so a bad config file cannot make this verb crash.
    """
    labels = {
        CONFIG_LOCAL_FILE: "config.local",
        CONFIG_SHARED_FILE: "config.json",
        LEGACY_CONFIG_FILE: "legacy",
    }
    for path in CONFIG_TIERS:
        try:
            if path.exists():
                loaded = json.loads(path.read_text())
                if isinstance(loaded, dict) and key in loaded:
                    return loaded[key], labels[path]
        except (json.JSONDecodeError, OSError, ValueError):
            continue
    return None, "default"


def _resolve_autonomy() -> str:
    """The autonomy level, modelled on `_resolve_landing_strategy` (Issue 2.1).

    `autonomous` (default) → execution continues to the next ready bead without operator
    input, an epic boundary is a report rather than a stop, and the review loop resolves
    its own concerns and re-runs until APPROVE. Halts are confined to the declared
    five-class stop set (REQ-AGENT-064).
    `checkpointed` → the prior behaviour: the operator is consulted at the points the
    autonomous level would pass through.

    Any unset or unrecognised value falls back to `autonomous`. The default is
    deliberately the permissive one: caution is the exception that must be configured,
    not the default that must be overridden.
    """
    if _AUTONOMY_OVERRIDE is not None:
        return _AUTONOMY_OVERRIDE
    cfg = _read_config()
    val = cfg.get(CONFIG_KEY_AUTONOMY)
    if isinstance(val, str) and val.strip() in AUTONOMY_LEVELS:
        return val.strip()
    return AUTONOMY_DEFAULT


def _is_autonomous() -> bool:
    """True iff the resolved autonomy level is `autonomous`."""
    return _resolve_autonomy() == AUTONOMY_DEFAULT


def _plan_id_from_dir(plan_dir: Path) -> str:
    """The plan id == worktree leaf: the plan_dir basename.

    Holds for both roots (docs/plans/<id> and Incubator/<slug>/plans/<id>).
    """
    return plan_dir.name


# Named per-phase branches (REQ-BRANCH-001). The single bare `<plan-id>` of the prior
# model is replaced: planning cuts `<plan-id>-development`, the landed plan is feature
# `<plan-id>` (feature-branch strategy only), execution cuts `<plan-id>-execute`.
def _development_branch(plan_id: str) -> str:
    return f"{plan_id}-development"


def _feature_branch(plan_id: str) -> str:
    return plan_id


def _execute_branch(plan_id: str) -> str:
    return f"{plan_id}-execute"


def _worktree_path(plan_dir: Path) -> Path:
    """Repo-relative execute worktree path `.worktrees/<plan-id>` (INV-1).

    The path stays keyed on the plan id; only the *branch* is `<plan-id>-execute`.
    """
    return WORKTREES_DIR / _plan_id_from_dir(plan_dir)


def _run_git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run `git <args>` capturing output; never raises on non-zero exit."""
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True,
    )


def _is_git_repo() -> bool:
    r = _run_git(["rev-parse", "--is-inside-work-tree"])
    return r.returncode == 0 and r.stdout.strip() == "true"


def _registered_worktree_paths(repo_root: Path) -> set[Path]:
    """Resolved absolute paths of every registered git worktree."""
    r = _run_git(["worktree", "list", "--porcelain"], cwd=repo_root)
    paths: set[Path] = set()
    for line in r.stdout.splitlines():
        if line.startswith("worktree "):
            paths.add(Path(line[len("worktree "):].strip()).resolve())
    return paths


def _branch_exists(branch: str, repo_root: Path) -> bool:
    r = _run_git(["rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
                 cwd=repo_root)
    return r.returncode == 0


def _current_branch(repo_root: Path | None = None) -> str | None:
    """The current branch name, or None on a detached HEAD (empty name)."""
    r = _run_git(["symbolic-ref", "--quiet", "--short", "HEAD"], cwd=repo_root)
    name = r.stdout.strip()
    return name if (r.returncode == 0 and name) else None


def _default_branch(repo_root: Path | None = None) -> str | None:
    """Resolve the repo's default branch (REQ-PLAN-065 / REQ-BRANCH-002 order).

    `git symbolic-ref --short refs/remotes/origin/HEAD` (strip the `origin/`)
      → `git config init.defaultBranch`
      → `main` if it exists, else `master` if it exists
      → None (indeterminate — callers fail-closed).
    """
    r = _run_git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=repo_root)
    if r.returncode == 0 and r.stdout.strip():
        ref = r.stdout.strip()
        return ref.split("/", 1)[1] if "/" in ref else ref
    r = _run_git(["config", "init.defaultBranch"], cwd=repo_root)
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    for cand in ("main", "master"):
        if _branch_exists(cand, repo_root):
            return cand
    return None


def _resolve_execute_base(plan_id: str, repo_root: Path) -> tuple[str | None, str]:
    """The pinned base branch the execute worktree is cut from (REQ-BRANCH-002/003).

    Returns (base_branch | None, detail). `main` strategy → the repo default branch;
    `feature-branch` strategy → the feature `<plan-id>` branch. A `None` base means it
    could not be resolved (missing branch / indeterminate default) — the caller returns
    a fallback verdict rather than cutting from ambient HEAD.
    """
    strategy = _resolve_landing_strategy()
    if strategy == "feature-branch":
        base = _feature_branch(plan_id)
    else:
        base = _default_branch(repo_root)
    if not base:
        return None, f"could not resolve a pinned base for the '{strategy}' strategy"
    if not _branch_exists(base, repo_root):
        return None, f"pinned base '{base}' ({strategy} strategy) does not exist"
    return base, f"pinned to {base} ({strategy} strategy)"


def _worktree_dirty(wt_abs: Path) -> tuple[bool, list[str]]:
    """(dirty?, porcelain lines). Surfaced on resume; never auto-resolved (1.3)."""
    r = _run_git(["status", "--porcelain"], cwd=wt_abs)
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    return (bool(lines), lines)


def _bd_resolves_from(wt_abs: Path) -> bool:
    """INV-2 runtime probe: does `bd` reach the primary's shared DB from here?"""
    try:
        r = subprocess.run(["bd", "list", "--json"], cwd=wt_abs,
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0


def _ensure_worktrees_gitignored(repo_root: Path) -> bool:
    """Append `/.worktrees/` to .gitignore if absent (Issue 1.2; idempotent).

    Returns True iff the file was modified.
    """
    gi = repo_root / GITIGNORE_FILE
    existing = gi.read_text().splitlines() if gi.exists() else []
    if any(ln.strip() == WORKTREES_GITIGNORE_ANCHOR for ln in existing):
        return False
    with gi.open("a") as fh:
        if existing and existing[-1].strip():
            fh.write("\n")
        fh.write(f"{WORKTREES_GITIGNORE_ANCHOR}\n")
    return True


def _worktree_viability(repo_root: Path) -> dict | None:
    """Cheap, side-effect-free pre-checks (Issue 1.3).

    Returns a fallback verdict dict if NOT viable, else None (proceed).
    Enumerated reasons: not-a-git-repo, beads-not-initialized,
    (dirty-locked and bd-db-unresolved are detected later, with the worktree in hand).
    """
    if not _is_git_repo():
        return {"viable": False, "reason": "not-a-git-repo"}
    # The primary must own the shared Dolt DB (INV-2): its .beads/ is the parent the
    # worktree resolves through git-common-dir. No .beads → bd not initialized here.
    if not (repo_root / ".beads").exists():
        return {"viable": False, "reason": "beads-not-initialized"}
    return None


def _worktree_ensure(plan_dir: Path) -> dict:
    """Idempotent create-or-reattach of the plan's worktree (Issues 1.1/1.2/1.3).

    Verdict shape:
      viable=True:  {viable, action, path, branch, dirty, dirty_files, gitignore_updated}
      viable=False: {viable, reason, [path], [created]}
    `action` ∈ {created, reattached-branch, reattached-worktree}.
    `reason` ∈ {not-a-git-repo, beads-not-initialized, dirty-locked, bd-db-unresolved}.
    """
    if _worktree_opted_out():
        return {"viable": False, "reason": "opted-out",
                "detail": f"{CONFIG_KEY_WORKTREE} is false in .yf-plan.local.json; "
                          f"running in-place by operator choice."}
    repo_root = _git_root()
    fallback = _worktree_viability(repo_root)
    if fallback is not None:
        return fallback

    plan_id = _plan_id_from_dir(plan_dir)
    branch = _execute_branch(plan_id)
    wt_rel = _worktree_path(plan_dir)
    wt_abs = (repo_root / wt_rel).resolve()

    gitignore_updated = _ensure_worktrees_gitignored(repo_root)

    registered = _registered_worktree_paths(repo_root)
    created_this_call = False
    base: str | None = None
    if wt_abs in registered:
        action = "reattached-worktree"
    elif wt_abs.exists():
        # A path is squatting the worktree slot but git doesn't know it — an
        # unresolved leftover. Surface, never clobber (Issue 1.3).
        return {
            "viable": False,
            "reason": "dirty-locked",
            "path": str(wt_rel),
            "detail": f"{wt_rel} exists but is not a registered git worktree; "
                      f"resolve manually (git worktree prune / remove the path).",
        }
    elif _branch_exists(branch, repo_root):
        # The execute branch already exists (a prior session) — re-attach it as-is; its
        # base was pinned when it was first created.
        r = _run_git(["worktree", "add", str(wt_abs), branch], cwd=repo_root)
        if r.returncode != 0:
            return {"viable": False, "reason": "dirty-locked",
                    "detail": r.stderr.strip()}
        action = "reattached-branch"
        created_this_call = True
    else:
        # Fresh execute branch: pin it to a KNOWN base per landing strategy, never
        # ambient HEAD (REQ-BRANCH-002 — the #47 root-cause fix).
        base, base_detail = _resolve_execute_base(plan_id, repo_root)
        if base is None:
            return {"viable": False, "reason": "base-unresolved", "detail": base_detail}
        r = _run_git(["worktree", "add", str(wt_abs), "-b", branch, base], cwd=repo_root)
        if r.returncode != 0:
            return {"viable": False, "reason": "dirty-locked",
                    "detail": r.stderr.strip()}
        action = "created"
        created_this_call = True

    # INV-2 runtime probe (M4): confirm bd reaches the shared DB from the worktree.
    # If it fails on a worktree we just created, tear it back down so `ensure` stays
    # atomic (clean fallback, no orphaned worktree). A pre-existing worktree is left
    # in place — surfacing beats clobbering possible work.
    if not _bd_resolves_from(wt_abs):
        torn = False
        if created_this_call:
            _run_git(["worktree", "remove", "--force", str(wt_abs)], cwd=repo_root)
            _run_git(["branch", "-D", branch], cwd=repo_root)
            _run_git(["worktree", "prune"], cwd=repo_root)
            torn = True
        return {
            "viable": False,
            "reason": "bd-db-unresolved",
            "detail": "bd could not resolve the shared DB from the worktree "
                      "(INV-2 fragile; run bd from the primary checkout instead).",
            "torn_down": torn,
        }

    dirty, dirty_files = _worktree_dirty(wt_abs)
    return {
        "viable": True,
        "action": action,
        "path": str(wt_rel),
        "branch": branch,
        "base": base,  # the pinned start-point (None on re-attach — base set at creation)
        "dirty": dirty,
        "dirty_files": dirty_files,
        "gitignore_updated": gitignore_updated,
    }


def _worktree_teardown(plan_dir: Path, force: bool) -> dict:
    """Remove the worktree + delete the merged EXECUTE branch + prune (Issue 1.1/2.3).

    `git worktree remove` refuses on a dirty tree unless force=True (INV-1: never
    --force without confirmation). `git branch -d` refuses an unmerged branch (a
    feature — only a merged-back execute branch is deleted); force escalates to -D.

    Per-strategy (REQ-BRANCH-004): teardown only ever targets `<plan-id>-execute`.
    Under the `feature-branch` strategy the feature `<plan-id>` branch is therefore
    **preserved** (never referenced here); under `main` the execute branch is deleted
    after its merge to the default branch. Teardown never deletes a feature branch.
    """
    repo_root = _git_root()
    plan_id = _plan_id_from_dir(plan_dir)
    branch = _execute_branch(plan_id)
    wt_rel = _worktree_path(plan_dir)
    wt_abs = (repo_root / wt_rel).resolve()

    steps: dict[str, dict] = {}
    registered = _registered_worktree_paths(repo_root)

    if wt_abs in registered:
        rm_args = ["worktree", "remove", str(wt_abs)]
        if force:
            rm_args.append("--force")
        r = _run_git(rm_args, cwd=repo_root)
        steps["remove"] = {"ok": r.returncode == 0, "detail": r.stderr.strip()}
        if r.returncode != 0:
            # Refused (dirty) — stop before deleting the branch (work may be unmerged).
            return {"status": "blocked", "path": str(wt_rel), "branch": branch,
                    "steps": steps,
                    "detail": "worktree remove refused (dirty?); rerun with --force "
                              "only after confirming no work is lost."}
    else:
        steps["remove"] = {"ok": True, "detail": "no registered worktree (skipped)"}

    if _branch_exists(branch, repo_root):
        del_flag = "-D" if force else "-d"
        r = _run_git(["branch", del_flag, branch], cwd=repo_root)
        steps["branch_delete"] = {"ok": r.returncode == 0,
                                  "detail": r.stderr.strip() or r.stdout.strip()}
    else:
        steps["branch_delete"] = {"ok": True, "detail": "no branch (skipped)"}

    r = _run_git(["worktree", "prune"], cwd=repo_root)
    steps["prune"] = {"ok": r.returncode == 0, "detail": r.stderr.strip()}

    all_ok = all(s["ok"] for s in steps.values())
    return {"status": "ok" if all_ok else "partial", "path": str(wt_rel),
            "branch": branch, "steps": steps}


@cli.group()
def worktree():
    """Worktree lifecycle verbs for plan execution (plan-009 Epic 1 seam).

    Pure (repo_root, plan_dir) inputs; no yf-plan phase state. All subcommands
    emit --json for the SKILL.md EXECUTE/RECONCILE wiring.
    """


@worktree.command("path")
@click.argument("plan_dir", type=click.Path())
@click.option("--json-output", "--json", "as_json", is_flag=True)
def worktree_path_cmd(plan_dir: str, as_json: bool):
    """Print the repo-relative worktree path for a plan (pure computation)."""
    wt_rel = _worktree_path(Path(plan_dir))
    plan_id = _plan_id_from_dir(Path(plan_dir))
    branch = _execute_branch(plan_id)
    if as_json:
        click.echo(json.dumps({"path": str(wt_rel), "branch": branch}))
    else:
        click.echo(str(wt_rel))


@worktree.command("ensure")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True)
def worktree_ensure_cmd(plan_dir: str, as_json: bool):
    """Create-or-reattach the plan's worktree; emit a viability verdict.

    Idempotent: a fresh plan gets `git worktree add -b <plan>`; a resume re-attaches
    (no -b). Non-viable repos return a `fallback:<reason>` verdict (the caller runs
    in-place). Exit 0 on viable, 3 on fallback — so a shell `if` can branch.
    """
    result = _worktree_ensure(Path(plan_dir))
    if as_json:
        click.echo(json.dumps(result, indent=2))
    elif result.get("viable"):
        msg = f"worktree {result['action']}: {result['path']} (branch {result['branch']})"
        if result.get("dirty"):
            msg += f"  [DIRTY — {len(result['dirty_files'])} change(s), surfaced not resolved]"
        click.echo(msg)
    else:
        click.echo(f"fallback: {result['reason']} — {result.get('detail', '')}".rstrip(" —"))
    sys.exit(0 if result.get("viable") else 3)


@worktree.command("teardown")
@click.argument("plan_dir", type=click.Path())
@click.option("--json-output", "--json", "as_json", is_flag=True)
@click.option("--force", is_flag=True,
              help="Escalate to `worktree remove --force` + `branch -D` (clobbers "
                   "a dirty tree / unmerged branch). Default refuses both (INV-1).")
def worktree_teardown_cmd(plan_dir: str, as_json: bool, force: bool):
    """Remove the worktree, delete the merged branch, prune."""
    result = _worktree_teardown(Path(plan_dir), force)
    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"teardown {result['status']}: {result['path']} (branch {result['branch']})")
        for step, info in result["steps"].items():
            click.echo(f"  {step}: {'ok' if info['ok'] else 'FAIL'} {info['detail']}".rstrip())
    sys.exit(0 if result["status"] == "ok" else 3)


# ---------------------------------------------------------------------------
# RECONCILE merge-back engine (plan-009 Epic 3)
#
# Two seams the SKILL.md Phase-6 reorder leans on:
#   landing-lock {acquire,release,status}  — serialize merge-backs on one machine (3.4)
#   validate-merged <plan_dir>             — re-validate the MERGED tree before push (3.2)
#
# Order matters (INV-4): merge first, THEN validate the merged state — today's §6.1
# tested pre-merge, which can't catch class-(b) integration regressions.
# ---------------------------------------------------------------------------

LANDING_LOCK = STATE_DIR / "landing.lock"


def _pid_alive(pid: int | None) -> bool:
    """True if a local PID is live. EPERM (exists, not ours) counts as alive."""
    if not isinstance(pid, int):
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _landing_lock_acquire(plan_id: str) -> dict:
    """Atomically acquire the single-machine landing lock (Issue 3.4).

    Atomicity via O_CREAT|O_EXCL. A held lock is reclaimable ONLY when it is this
    host's and its PID is dead (same-host stale). A lock from another host is never
    auto-broken — surfaced for the operator (single-developer v1 scope; cross-machine
    concurrent landing is out of scope).
    """
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    hostname = socket.gethostname()
    payload = {
        "hostname": hostname,
        "pid": os.getpid(),
        "plan_id": plan_id,
        "acquired_at": datetime.now().isoformat(timespec="seconds"),
    }
    for attempt in (1, 2):
        try:
            fd = os.open(str(LANDING_LOCK),
                         os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            held = _read_json(LANDING_LOCK)
            same_host = held.get("hostname") == hostname
            stale = same_host and not _pid_alive(held.get("pid"))
            if stale and attempt == 1:
                # Reclaim our own dead lock, then retry the atomic create once.
                try:
                    LANDING_LOCK.unlink()
                except OSError:
                    pass
                continue
            return {
                "acquired": False,
                "held_by": held,
                "reclaimable": stale,
                "detail": ("stale same-host lock; reclaim failed" if stale else
                           "held by a live process"
                           + ("" if same_host else " on another host — never auto-broken")),
            }
        os.write(fd, (json.dumps(payload, indent=2) + "\n").encode())
        os.close(fd)
        return {"acquired": True, "lock": payload}
    return {"acquired": False, "detail": "could not acquire after reclaim"}


def _landing_lock_release(plan_id: str, force: bool) -> dict:
    """Release the lock iff this plan/host owns it (or force)."""
    if not LANDING_LOCK.exists():
        return {"released": True, "detail": "no lock held"}
    held = _read_json(LANDING_LOCK)
    owns = (held.get("plan_id") == plan_id
            and held.get("hostname") == socket.gethostname())
    if not owns and not force:
        return {"released": False, "held_by": held,
                "detail": "lock owned by a different plan/host; use --force to override"}
    try:
        LANDING_LOCK.unlink()
    except OSError as e:
        return {"released": False, "detail": str(e)}
    return {"released": True, "freed": held}


def _run_shell(cmd: str, cwd: Path | None = None) -> dict:
    """Run a shell command, capturing a truncated result for a validation report."""
    try:
        r = subprocess.run(cmd, shell=True, cwd=cwd,
                           capture_output=True, text=True)
    except (OSError, subprocess.SubprocessError) as e:
        return {"cmd": cmd, "ok": False, "returncode": None, "error": str(e)}
    tail = (r.stdout + r.stderr).strip()
    return {"cmd": cmd, "ok": r.returncode == 0, "returncode": r.returncode,
            "output_tail": tail[-2000:]}


# yf-change-validation soft-dep (plan-015 D.1). Prose soft-dep ONLY — detect the
# engine at RUNTIME (approved manifest present + script resolvable). NO frontmatter
# `depends-on-skill` edge. Absent/unapproved/unresolvable → graceful fallback to
# the validate-cmd tier (and then the not-checked notice).
CHANGE_VALIDATION_MANIFEST = "CHANGE-VALIDATION.md"


def _repo_root() -> Path:
    """Repo top-level via git, falling back to cwd (mirrors the engine's repo_root)."""
    try:
        r = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                           capture_output=True, text=True, timeout=2)
        if r.returncode == 0 and r.stdout.strip():
            return Path(r.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return Path.cwd()


def _skill_surface_roots(repo_root: Path) -> list[Path]:
    """Skill install roots in the same precedence as the SKILL.md SKILL_DIR `find`:
    user scope (`~/.claude`, `~/.agents`), then project scope (`<git-root>/.claude`,
    `.agents`), then cwd-relative. Mirrors SKILL.md's discovery so a script-side
    resolver and the SKILL.md-side bootstrap cannot drift (issue #74)."""
    home = Path.home()
    return [
        home / ".claude" / "skills",
        home / ".agents" / "skills",
        repo_root / ".claude" / "skills",
        repo_root / ".agents" / "skills",
        Path(".claude") / "skills",
        Path(".agents") / "skills",
    ]


def _change_validation_script(repo_root: Path) -> Path | None:
    """Resolve the yf-change-validation engine across install surfaces, or None.

    Detect-at-runtime soft-dep: returns the first existing engine script found on
    the skill-surface search path — the in-tree source checkout
    (`<repo>/skills/...`, so yoshiko-flow dogfoods its own engine) followed by the
    user/project/cwd install surfaces from `_skill_surface_roots`. The original
    resolver checked only the in-tree path, so a normal install (user- or
    `.claude`/`.agents`-scope) never resolved and `validate-merged` silently fell
    through to `engine: none` (issue #74)."""
    rel = Path("yf-change-validation") / "scripts" / "change_validation.py"
    candidates = [repo_root / "skills" / rel]
    candidates += [root / rel for root in _skill_surface_roots(repo_root)]
    for script in candidates:
        if script.exists():
            return script
    return None


def _approved_manifest_present(repo_root: Path) -> bool:
    """True iff a repo-root CHANGE-VALIDATION.md exists with §0 `approved: yes`.

    Cheap gate before delegating; the engine itself also refuses cleanly when
    unapproved, so this is an optimization, not the sole guard.
    """
    p = repo_root / CHANGE_VALIDATION_MANIFEST
    if not p.exists():
        return False
    try:
        text = p.read_text()
    except OSError:
        return False
    return bool(re.search(r"approved:\s*yes", text, re.IGNORECASE))


def _run_change_validation(script: Path, repo_root: Path) -> dict | None:
    """Delegate to the engine's `run --tier full --json` over the merged tree.

    Returns the engine's parsed JSON payload, or None if the invocation could not
    be parsed (caller then falls back). A clean `refused` payload (manifest present
    but `§0 approved: no`) is returned as-is so the caller can fall through, NOT
    treated as a failure.
    """
    try:
        r = subprocess.run(
            ["uv", "run", str(script), "run", "--tier", "full", "--json"],
            cwd=str(repo_root), capture_output=True, text=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    try:
        return json.loads(r.stdout)
    except (json.JSONDecodeError, ValueError):
        return None


def _validate_merged(plan_dir: Path) -> dict:
    """Validate the merged tree before push (Issue 3.2; runs PRIMARY-side, post-merge).

    Three-tier precedence for the cross-plan safety net (plan-015 D.1):

      1. yf-change-validation engine — an APPROVED repo-root `CHANGE-VALIDATION.md`
         plus a resolvable engine script → delegate to `change_validation.py run
         --tier full --json` over the merged tree. A clean `refused` payload
         (manifest present but `§0 approved: no`) falls THROUGH to tier 2 (NOT a
         failure). An absent/unresolvable engine also falls through.
      2. configured `validate-cmd` — `.yf-plan.local.json` `validate-cmd` (the prior
         layer-(b) behavior).
      3. neither — runs no project suite and emits the verbatim cross-plan-not-checked
         notice (never a bare green).

    Layer (a) — the plan's own Gate `Test:` commands — is run by the coordinator/
    operator against the merged tree (it cannot reliably catch class-(b) regressions;
    see plan-009 §Approach), so this verb owns layer (b) + the honesty notice, and the
    SKILL §6.1.5 prose drives layer (a).

    The output schema `{plan_dir, validate_cmd_configured, layer_b, notice, status}` is
    preserved; an `engine` discriminator ("change-validation"|"validate-cmd"|"none") is
    ADDED so SKILL prose / downstream can surface which tier ran. The exit-3-on-non-pass
    contract lives in the Click wrapper and is unchanged.
    """
    validate_cmd = _resolve_validate_cmd()
    result: dict = {
        "plan_dir": str(plan_dir),
        "validate_cmd_configured": validate_cmd is not None,
        "engine": "none",
        "layer_b": None,
        "notice": None,
    }

    # Tier 1: yf-change-validation engine (approved manifest + resolvable script).
    repo_root = _repo_root()
    if _approved_manifest_present(repo_root):
        script = _change_validation_script(repo_root)
        if script is not None:
            payload = _run_change_validation(script, repo_root)
            # None → unparseable invocation; `refused` → unapproved at engine read.
            # Both fall through to the next tier (refusal is NOT a failure).
            if payload is not None and payload.get("status") != "refused":
                eng_status = payload.get("status")
                result["engine"] = "change-validation"
                result["layer_b"] = payload
                # Engine PASS → pass; FAIL/INCONCLUSIVE/anything else → fail (exit 3).
                result["status"] = "pass" if eng_status == "pass" else "fail"
                return result

    # Tier 2: configured validate-cmd (prior layer-(b) behavior).
    if validate_cmd is not None:
        layer_b = _run_shell(validate_cmd)
        result["engine"] = "validate-cmd"
        result["layer_b"] = layer_b
        result["status"] = "pass" if layer_b["ok"] else "fail"
        return result

    # Tier 3: neither configured — verbatim cross-plan-not-checked notice.
    result["status"] = "pass"
    result["notice"] = (
        "MERGED-STATE VALIDATION RAN PLAN GATES ONLY; no project `validate-cmd` "
        "configured in .yf-plan.local.json — CROSS-PLAN REGRESSIONS NOT CHECKED. "
        "This is NOT integration-safe; configure validate-cmd for real safety.")
    return result


@cli.group("landing-lock")
def landing_lock():
    """Single-machine merge-back serialization lock (plan-009 Issue 3.4)."""


@landing_lock.command("acquire")
@click.argument("plan_id")
@click.option("--json-output", "--json", "as_json", is_flag=True)
def landing_lock_acquire_cmd(plan_id: str, as_json: bool):
    """Atomically acquire the landing lock for a plan; exit 3 if held."""
    result = _landing_lock_acquire(plan_id)
    if as_json:
        click.echo(json.dumps(result, indent=2))
    elif result["acquired"]:
        click.echo(f"landing lock acquired for {plan_id}")
    else:
        click.echo(f"landing lock HELD: {result.get('detail', '')} "
                   f"(held_by={result.get('held_by')})")
    sys.exit(0 if result["acquired"] else 3)


@landing_lock.command("release")
@click.argument("plan_id")
@click.option("--force", is_flag=True, help="Release even if owned by another plan/host.")
@click.option("--json-output", "--json", "as_json", is_flag=True)
def landing_lock_release_cmd(plan_id: str, force: bool, as_json: bool):
    """Release the landing lock (only if this plan/host owns it, unless --force)."""
    result = _landing_lock_release(plan_id, force)
    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"landing lock {'released' if result['released'] else 'NOT released'}: "
                   f"{result.get('detail', '')}".rstrip())
    sys.exit(0 if result["released"] else 3)


@landing_lock.command("status")
@click.option("--json-output", "--json", "as_json", is_flag=True)
def landing_lock_status_cmd(as_json: bool):
    """Report current landing-lock holder, if any."""
    held = _read_json(LANDING_LOCK) if LANDING_LOCK.exists() else None
    out = {"held": held is not None, "lock": held}
    if as_json:
        click.echo(json.dumps(out, indent=2))
    elif held:
        click.echo(f"landing lock held: {held}")
    else:
        click.echo("landing lock free")


@cli.command("validate-merged")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True)
def validate_merged_cmd(plan_dir: str, as_json: bool):
    """Validate the merged tree before push (project validate-cmd + honesty notice)."""
    result = _validate_merged(Path(plan_dir))
    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"merged-state validation: {result['status']}")
        if result.get("notice"):
            click.echo(f"  NOTICE: {result['notice']}")
        if result.get("layer_b"):
            lb = result["layer_b"]
            click.echo(f"  validate-cmd: {'ok' if lb['ok'] else 'FAIL'} "
                       f"(rc={lb['returncode']})")
    sys.exit(0 if result["status"] == "pass" else 3)


# ---------------------------------------------------------------------------
# Resume scan (Issue 1.2, #2 — coordinator crash recovery)
# ---------------------------------------------------------------------------

# A claimed bead lands in `in_progress` (bd update --claim sets status + owner),
# so in_progress is the orphan-sweep target the coordinator resets to `open`.
_STUCK_STATUSES = ("in_progress",)


def _parse_bd_json(text: str) -> list[dict]:
    """Defensively parse `bd ... --json` output to a flat list of issue dicts.

    Per beads-extra (*`--json` is not always a single JSON document*), bd output
    may be a single object, an array, an `{"issues": [...]}` envelope, or — rarely
    — concatenated documents. This tolerates all four and flattens to issues.
    """
    text = text.strip()
    if not text:
        return []
    docs: list = []
    try:
        docs = [json.loads(text)]
    except json.JSONDecodeError:
        dec = json.JSONDecoder()
        idx, n = 0, len(text)
        while idx < n:
            while idx < n and text[idx] in " \t\r\n":
                idx += 1
            if idx >= n:
                break
            try:
                obj, end = dec.raw_decode(text, idx)
            except json.JSONDecodeError:
                break
            docs.append(obj)
            idx = end
    issues: list[dict] = []
    for d in docs:
        if isinstance(d, list):
            issues.extend(x for x in d if isinstance(x, dict))
        elif isinstance(d, dict):
            if isinstance(d.get("issues"), list):
                issues.extend(x for x in d["issues"] if isinstance(x, dict))
            elif "id" in d:
                issues.append(d)
    return issues


def _bd_list(*args: str) -> list[dict]:
    """Run `bd list <args> --json` and defensively parse the result."""
    try:
        out = subprocess.check_output(["bd", "list", *args, "--json"],
                                      text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return []
    return _parse_bd_json(out)


def _all_plan_beads() -> dict[str, dict]:
    """All beads keyed by id, incl. closed + gates.

    `bd list` omits gates and (by default) closed beads, so merge `--all` with an
    explicit `--type gate --all` query. De-duplicated by id.
    """
    by_id: dict[str, dict] = {}
    for issue in (*_bd_list("--all"), *_bd_list("--all", "--type", "gate")):
        iid = issue.get("id")
        if iid:
            by_id[iid] = issue
    return by_id


def _read_plan_epic_field(plan_md_text: str) -> str | None:
    """Return the epic id (frontmatter-first, `**Epic:**` fallback), if present."""
    return _read_plan_field(plan_md_text, "epic")


def _resume_scan(plan_dir: Path) -> dict:
    """Report a plan's epic and the bead state a resumed execute session faces.

    Epic resolution order: plan.md `**Epic:**` field (epic_source=plan_md), then
    a bead whose metadata.plan_dir matches (epic_source=bd_metadata), else none.
    Walks the parent tree from the epic to count descendants by status and list
    the stuck (in_progress/claimed) beads the orphan sweep will reset.
    """
    plan_md = plan_dir / "plan.md"
    plan_text = plan_md.read_text() if plan_md.exists() else ""
    beads = _all_plan_beads()

    epic_id = _read_plan_epic_field(plan_text)
    epic_source = "plan_md" if epic_id else "none"
    if not epic_id:
        wanted = {str(plan_dir), str(plan_dir).rstrip("/")}
        candidates = [
            b for b in beads.values()
            if (b.get("metadata") or {}).get("plan_dir") in wanted
        ]
        roots = [b for b in candidates
                 if b.get("issue_type") in ("molecule", "epic") and not b.get("parent")]
        chosen = roots or candidates
        if chosen:
            epic_id = chosen[0].get("id")
            epic_source = "bd_metadata"

    result: dict = {
        "plan_dir": str(plan_dir),
        "epic_id": epic_id,
        "epic_source": epic_source,
        "found": epic_id is not None,
        # plan-044 Issue 3.9 (#143): does the resolved epic id actually EXIST in bd?
        #
        # `found` alone is not that question — it reports only that an id was
        # RECORDED. A dangling ref therefore yields `found: true` with zero
        # descendants, which is indistinguishable from a legitimately completed
        # plan, so the execute path reads "no open work" and skips the plan
        # entirely. That silent false success is where the defect actually bites,
        # and `resume-scan` is the only verb the execute path consults — which is
        # why the signal belongs here and not solely in `audit`.
        #
        # `None` (not False) when there is nothing to check or `bd` is unreadable:
        # "no beads at all" cannot distinguish an absent database from an empty
        # one, and reporting False there would libel a healthy plan.
        "epic_resolves": (
            None if (epic_id is None or not beads) else epic_id in beads
        ),
        # Content-fingerprint re-review gate (REQ-PORT-041): a hard gate the SKILL
        # §5.2 execute path checks — a stale-approved plan must re-review before pouring.
        **_fingerprint_status(plan_dir),
    }
    if not epic_id:
        return result

    children_of: dict[str | None, list[dict]] = {}
    for b in beads.values():
        children_of.setdefault(b.get("parent"), []).append(b)

    seen: set[str] = set()
    stack = [epic_id]
    descendants: list[dict] = []
    while stack:
        for child in children_of.get(stack.pop(), []):
            cid = child.get("id")
            if not cid or cid in seen:
                continue
            seen.add(cid)
            descendants.append(child)
            stack.append(cid)

    counts: dict[str, int] = {}
    stuck: list[dict] = []
    open_work_remaining = 0
    for d in descendants:
        st = d.get("status", "unknown")
        counts[st] = counts.get(st, 0) + 1
        if st in _STUCK_STATUSES:
            # `yf_attempts` (2.8/2.9): the metadata is ALREADY loaded here, so surfacing
            # it is a read of a dict we hold. The existing detector is status-based and
            # therefore cannot tell a FIRST crash from a FIFTH — both read `in_progress`.
            # That distinction is what decides whether the sweep should reset the bead or
            # the operator should look at it, so it belongs in the record.
            md = d.get("metadata")
            attempts = 0
            if isinstance(md, dict):
                raw = md.get("yf_attempts")
                if isinstance(raw, bool):
                    attempts = 0
                elif isinstance(raw, int):
                    attempts = raw
                elif isinstance(raw, str) and raw.strip().isdigit():
                    attempts = int(raw.strip())
            stuck.append({
                "id": d.get("id"),
                "status": st,
                "issue_type": d.get("issue_type"),
                "title": d.get("title", ""),
                "yf_attempts": attempts,
                "at_threshold": attempts >= _resolve_max_attempts(),
            })
        if st != "closed" and d.get("issue_type") != "gate":
            open_work_remaining += 1

    result.update({
        "counts": counts,
        "total": len(descendants),
        "stuck": stuck,
        "open_work_remaining": open_work_remaining,
    })
    return result


@cli.command("resume-scan")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True,
              help="Emit structured JSON. Default is a human-readable summary.")
def resume_scan(plan_dir: str, as_json: bool):
    """Report the plan's epic + stuck-bead state for the coordinator resume-guard."""
    result = _resume_scan(Path(plan_dir))
    if as_json:
        click.echo(json.dumps(result, indent=2))
        return
    if not result["found"]:
        click.echo(f"No epic found for {plan_dir} (plan.md **Epic:** field absent "
                   f"and no bead metadata.plan_dir match). Treat as a fresh run.")
        return
    if result.get("stale_approved"):
        click.echo("  ⚠ STALE-APPROVED: plan content changed since approval — "
                   "re-review required before execute.")
    click.echo(f"Epic {result['epic_id']} (source: {result['epic_source']})")
    click.echo(f"  descendants: {result['total']}  "
               f"counts: {result['counts']}")
    click.echo(f"  open work remaining (non-closed, non-gate): "
               f"{result['open_work_remaining']}")
    if result["stuck"]:
        click.echo(f"  STUCK (in_progress/claimed — sweep resets to open):")
        for s in result["stuck"]:
            flag = " ⚠ AT THRESHOLD" if s.get("at_threshold") else ""
            click.echo(f"    - {s['id']} [{s['issue_type']}] "
                       f"attempts={s.get('yf_attempts', 0)}{flag} {s['title']}")
    else:
        click.echo("  no stuck beads")


# ---------------------------------------------------------------------------
# Portability audit (Epic 4)
# ---------------------------------------------------------------------------

# Dangling-reference detection: absolute paths and parent-traversal only.
# Repo-relative paths like `skills/yf-plan/SKILL.md` are explicitly allowed.
_ABS_PATH_PATTERNS = (
    re.compile(r"(?<![\w/])/Users/"),
    re.compile(r"(?<![\w/])/home/"),
    re.compile(r"(?<![\w/])/opt/"),
    re.compile(r"(?<![\w/])/var/"),
    re.compile(r"(?<![\w/])/tmp/"),
    re.compile(r"(?<![\w/])/etc/"),
    re.compile(r"[A-Za-z]:\\"),
)
_PARENT_TRAVERSAL = re.compile(r"(?<![\w.])\.\./")

# HOISTED to `_shared/plan_template.py` (plan-048 Issue 2.1). `doc_lint`'s `derive_from`
# resolves only modules under `_shared/`, so the `context` document type could not be
# derived from a constant defined here. These aliases keep every existing use site working
# against the single definition; do NOT re-declare the literals here.
_CONTEXT_REQUIRED_SECTIONS = tuple(plan_template.CONTEXT_REQUIRED_SECTIONS)
_CONTEXT_PLACEHOLDERS = plan_template.CONTEXT_PLACEHOLDERS

# OKF-reserved `index.md` listing shape (REQ-PORT-001): a `#` heading plus ≥1
# `- [child](path)` listing bullet. Replaces the legacy README `File map` / `Reading
# order` header check — the file-map/reading-order content folds into the bullets.
_INDEX_HEADING_RE = re.compile(r"^# ", re.MULTILINE)
_INDEX_BULLET_RE = re.compile(r"^- \[[^\]]+\]\([^)]+\)", re.MULTILINE)

#: OKF error-level `check_conformance` reqs the audit surfaces under the REQ-PORT-050
#: conformance floor (per-concept-doc frontmatter/type/okf_spec). The reserved-file
#: presence errors (REQ-OKF-001 index / REQ-OKF-002 log) are deliberately excluded —
#: `index.md` presence is check #1's job, so surfacing REQ-OKF-001 here too would
#: double-report the same gap.
_OKF_PORT050_REQS = frozenset({"REQ-OKF-003", "REQ-OKF-030", "REQ-OKF-031", "REQ-OKF-071"})


def _index_is_listing(text: str) -> bool:
    """True when an `index.md` body is an OKF progressive-disclosure listing — a `#`
    heading plus ≥1 `- [child](path)` bullet (REQ-PORT-001), not the legacy README
    `File map` / `Reading order` prose (which carries no markdown-link list bullets)."""
    return bool(_INDEX_HEADING_RE.search(text)) and bool(_INDEX_BULLET_RE.search(text))


def _read_field_line(plan_md_text: str, label: str) -> str | None:
    """Read the RAW `**Label:** <value>` header-line value (NOT frontmatter-first).

    Unlike `_read_plan_field` (frontmatter-first, REQ-OKF-021), this reads ONLY the
    human `**Field:**` surface, so the audit's dual-write consistency check (R7 /
    REQ-DATA-015) can compare the two representations independently and detect a
    divergence. Returns None when no `**Label:**` line exists.
    """
    prefix = f"**{label}:**"
    for line in plan_md_text.splitlines():
        if line.startswith(prefix):
            val = line[len(prefix):].strip()
            return val or None
    return None


def _plan_phase_log_lines(plan_md_text: str) -> list[str]:
    """Return the lines of the legacy in-`plan.md` Phase log list (without the header).

    Retained as the **legacy fallback** source for un-migrated plans (no `log.md`)
    — Issue 3.4 relocated the live phase log to the reserved `log.md`, but the ~29
    pre-existing plans still hold it in `plan.md`'s `**Phase log:**` block, so the
    grandfather/count readers must still parse it when `log.md` is absent.
    """
    lines = plan_md_text.splitlines()
    out: list[str] = []
    in_log = False
    for line in lines:
        if line.startswith("**Phase log:**"):
            in_log = True
            continue
        if in_log:
            if line.startswith("- "):
                out.append(line)
            else:
                if out:
                    break
    return out


_LOG_DATE_HEADING_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})[ \t]*$")


def _log_md_entries(plan_dir: Path) -> list[tuple[str, str]] | None:
    """Parse the reserved bundle-root `log.md` into `(date, bullet_text)` pairs.

    The OKF-reserved `log.md` (REQ-DATA-012) is newest-first: entries are grouped
    under ISO-8601 `## YYYY-MM-DD` date headings and each entry is a `- <status>:
    <message>` bullet whose `<status>:` token is retained. `bullet_text` is the
    bullet with its leading `- ` stripped (e.g. `review: presented v1`), so a caller
    keys on `bullet_text.startswith("review:")` / `"scoping:"` and pairs it with the
    enclosing heading `date`.

    Returns `None` when `log.md` is absent — the signal for callers to fall back to
    the legacy in-`plan.md` `**Phase log:**` block (un-migrated plans). Returns an
    (empty) list when `log.md` exists, so an existing-but-empty log does NOT trigger
    the legacy fallback.
    """
    log_md = plan_dir / "log.md"
    if not log_md.exists():
        return None
    entries: list[tuple[str, str]] = []
    current_date: str | None = None
    for line in log_md.read_text().splitlines():
        hm = _LOG_DATE_HEADING_RE.match(line)
        if hm:
            current_date = hm.group(1)
            continue
        if current_date and line.startswith("- "):
            entries.append((current_date, line[2:].strip()))
    return entries


def _plan_first_scoping_date(plan_dir: Path) -> str | None:
    """Return the earliest `scoping:` date for a plan bundle (REQ-PORT-ACT).

    **Primary source: the reserved `log.md`** — the OLDEST `## YYYY-MM-DD` heading
    bearing a `- scoping:` bullet (log.md is newest-first, so the oldest scoping date
    is the `min` across scoping entries). **Legacy fallback:** when `log.md` is absent
    (un-migrated plan), the first `scoping:` line in the in-`plan.md` `**Phase log:**`
    block, so grandfathered plans resolve identically before and after migration
    (REQ-OKF-MIG-002 preserves the first `scoping:` date across the extraction).
    """
    entries = _log_md_entries(plan_dir)
    if entries is not None:
        scoping_dates = [d for d, txt in entries if txt.startswith("scoping:")]
        return min(scoping_dates) if scoping_dates else None
    plan_md = plan_dir / "plan.md"
    if not plan_md.exists():
        return None
    for line in _plan_phase_log_lines(plan_md.read_text()):
        m = re.match(r"- (\d{4}-\d{2}-\d{2}) scoping:", line)
        if m:
            return m.group(1)
    return None


# The `log.md` token a RED-TEAM PASS PRESENTATION writes (plan-047 Issue 2.7, REQ-PORT-006).
# Distinct from the `review:` token a STATUS TRANSITION into the review phase writes. Like
# `intake:` and `validated:` (REQ-DATA-012 / REQ-DATA-016) it is a recognized NON-STATUS
# token: it never advances `status` and no status parser keys on it.
REVIEW_PASS_TOKEN = "review-pass:"


def _plan_review_line_count(plan_dir: Path) -> int:
    """Count RED-TEAM PASS PRESENTATIONS for a plan bundle (REQ-PORT-006, as amended).

    The invariant is `len(reviews/pass-*.md) == <this count>`. It exists to catch a red-team
    verdict that was presented but never written to disk.

    **The defect this function was amended to fix.** Both events emitted the same `- review:`
    bullet: `update-status <dir> review` writes one on entering the review phase, and the
    create-on-present step writes another per red-team cycle. So a *correct* bundle could show
    2 bullets against 1 `pass-1.md` and hard-fail the audit. Reproduced mechanically on a
    scratch copy of plan-047's own bundle: one extra `update-status … review` took it to 5
    bullets / 4 files and `_audit_plan` reported
    `expected 5 pass-*.md (one per phase-log review line), found 4`.

    So the count now keys on `review-pass:`, which only a presentation writes.

    **Scope bound — this fix is FORWARD-LOOKING, and that is deliberate.** A bundle carrying
    no `review-pass:` bullet cannot have its presentations recovered: the two events are
    indistinguishable in its history, which is the whole defect. Rather than guess, such a
    bundle falls back to the legacy `review:` count, so all 46 existing bundles keep their
    current (correct, since they balance) numbers and nothing is retro-rewritten — the same
    stance REQ-DATA-018 takes on `Discharged-by` and REQ-DATA-027 on the vendored marker: a
    mention is not a discharge, and an inferred edge is worse than an absent one.

    The fallback applies only when the bundle **has** pass files. A plan that has entered
    `review` but not yet had a presentation counts **0** and expects **0** pass files — which
    is the buggy case, and it is now correct rather than grandfathered.
    """
    entries = _log_md_entries(plan_dir)
    if entries is not None:
        presentations = sum(1 for _d, txt in entries if txt.startswith(REVIEW_PASS_TOKEN))
        if presentations:
            return presentations
        legacy = sum(1 for _d, txt in entries if txt.startswith("review:"))
        # No presentation marker: legacy bundle. Fall back ONLY if pass files exist —
        # otherwise the honest expectation is zero.
        if legacy and any(plan_dir.glob("reviews/pass-*.md")):
            return legacy
        return 0
    plan_md = plan_dir / "plan.md"
    if not plan_md.exists():
        return 0
    lines = _plan_phase_log_lines(plan_md.read_text())
    presentations = sum(
        1 for line in lines if re.match(r"- \d{4}-\d{2}-\d{2} review-pass:", line)
    )
    if presentations:
        return presentations
    legacy = sum(1 for line in lines if re.match(r"- \d{4}-\d{2}-\d{2} review:", line))
    if legacy and any(plan_dir.glob("reviews/pass-*.md")):
        return legacy
    return 0


def _review_cycle_count(plan_dir: Path) -> int:
    """The number of completed review cycles: `len(glob('reviews/pass-*.md'))` (2.4a).

    **Deliberately NOT `_plan_review_line_count`.** That function counts `log.md`
    bullets, which is a *different number* and one that can and does diverge — a
    divergence observed live during this plan's own review. The pass-file count is the
    faithful cycle count because REQ-PLAN-032 guarantees each full REVISE cycle yields
    exactly one pass file.

    The count is **monotonic**: pass files are never deleted, so this never decreases.
    That is what makes the escalation stick, and it is the property that distinguishes
    this counter from `yf_attempts`, which resets on success.
    """
    reviews_dir = plan_dir / "reviews"
    if not reviews_dir.is_dir():
        return 0
    return sum(
        1 for f in reviews_dir.glob("pass-*.md")
        if re.fullmatch(r"pass-\d+\.md", f.name)
    )


def _review_loop_escalates(plan_dir: Path) -> tuple[bool, int, int]:
    """`(escalates, cycles, limit)` — whether the autonomous review loop must stop.

    Escalation is **stop class 4** (a mechanical counter threshold), not a judgement.
    On escalation the plan sits in `review` with a REVISE verdict — a LEGAL state, not
    a wedge: REQ-PLAN-030 bars only `ready-for-approval`, so nothing is corrupted and
    the operator can inspect, raise the bound, or resolve by hand.
    """
    cycles = _review_cycle_count(plan_dir)
    limit = _resolve_max_review_cycles()
    return (cycles >= limit, cycles, limit)


def _latest_review_verdict(
    plan_dir: Path,
) -> tuple[int | None, str | None, Path | None]:
    """Return (N, verdict, path) of the highest-numbered ``reviews/pass-N.md`` file.

    The verdict is parsed from the first ``## Verdict: <V>`` line (case-insensitive)
    and upper-cased. Returns ``(None, None, None)`` when no pass file exists, and
    ``(N, None, path)`` when the highest pass file has no parseable verdict line.

    The third element is what makes REQ-PLAN-072 possible: ``(N, None, path)`` is a
    *malformed* review — a file exists but its verdict did not parse — and is a
    materially different condition from ``(None, None, None)`` (no review at all).
    Callers must report the former as an error naming ``path``, never as a merely
    absent verdict.

    Per REQ-PLAN-071 the canonical emitted form is the level-2 heading ``## Verdict:``
    (what ``agents/red-team.md`` writes and what 56 of the existing reviews use). The
    parser additionally accepts a level-3 ``### Verdict:`` as **defence in depth**: a
    template that drifts back to ``###`` would otherwise degrade to a silent "no
    verdict" — unobservable at the point of failure, which is exactly how #116 hid.
    Accepting ``###`` is a tolerance, not a second canonical form; emitting it is
    still non-conformant.

    "Highest N" is the *last recorded* red-team cycle — REQ-PLAN-030 keys readiness
    on that being ``APPROVE`` (an earlier APPROVE followed by an unre-reviewed REVISE
    is not ready).
    """
    reviews_dir = plan_dir / "reviews"
    if not reviews_dir.is_dir():
        return (None, None, None)
    best_n: int | None = None
    best_file: Path | None = None
    for f in reviews_dir.glob("pass-*.md"):
        m = re.match(r"pass-(\d+)\.md$", f.name)
        if not m:
            continue
        n = int(m.group(1))
        if best_n is None or n > best_n:
            best_n = n
            best_file = f
    if best_file is None:
        return (None, None, None)
    verdict: str | None = None
    for line in best_file.read_text(encoding="utf-8").splitlines():
        m = re.match(r"#{2,3}\s+Verdict:\s*([A-Za-z-]+)", line.strip(), re.IGNORECASE)
        if m:
            verdict = m.group(1).upper()
            break
    return (best_n, verdict, best_file)


#: A GFM cell separator is an UNESCAPED pipe. `\|` inside a cell is a literal pipe.
#:
#: THIS IS THE THIRD PARSER TO NEED THE FIX. plan-048 Issue 1.1 corrected
#: `plan_extract._table_rows` and `doc_lint.first_table`; `parse_upstream_rows` was missed,
#: and R3's two-parser agreement rule caught it on its first live run — plan-013 row #17
#: has the title `... (coarse\|granular)`, which a naive split turns into two cells,
#: shifting every later cell left by one so the DISPOSITION column reads `granular)`.
#: The row then had an unrecognised disposition and escaped verification entirely.
_CELL_SPLIT = re.compile(r"(?<!\\)\|")


def _split_table_row(inner: str) -> list[str]:
    """Split one GFM table row's interior into cells, honouring escaped pipes."""
    return [c.strip().replace("\\|", "|") for c in _CELL_SPLIT.split(inner)]


#: Disposition literals recognised by `_verify_row` and by `doc_lint`'s R2c rule. The two
#: readers MUST agree — R3 asserts exactly that, because `verify-reconcile` is fail-loud and
#: two parsers disagreeing on row shape is a fail-loud FALSE POSITIVE.
UPSTREAM_DISPOSITIONS = frozenset(
    {"include", "exclude", "partial", "supersede", "deferred", "tracker"})


def _normalize_disposition(cell: str) -> str:
    """Strip GFM emphasis and case from a Disposition cell.

    `**partial**`, `_partial_` and `partial` are ONE literal. Emphasis is presentation.
    """
    v = (cell or "").strip()
    # Repeated strip handles `**_x_**` and any nesting order.
    for _ in range(4):
        stripped = v.strip().strip("*").strip("_").strip()
        if stripped == v:
            break
        v = stripped
    return v.lower()


def parse_upstream_rows(plan_md_text: str) -> list[dict]:
    """THE parser for plan.md's `## Upstream Issues` table. Single source of truth.

    Returns one dict per data row: `{issue, disposition, title, notes, resolved_by}`,
    with `issue` the bare number as a string.

    This is deliberately the ONLY parser of this table in the codebase. Two parsers of
    one table can disagree — on `[#N]` vs `#N` row shapes, on separator-row detection,
    on where the table ends — and `verify-reconcile` is FAIL-LOUD, so a disagreement
    would halt completion on healthy work: a fail-loud false positive, the most
    expensive failure kind available here (plan-043 R9). `_plan_non_exclude_upstream_numbers`
    and `verify-reconcile` are both thin views over this function for exactly that reason.
    """
    rows: list[dict] = []
    in_table = False
    for line in plan_md_text.splitlines():
        if line.startswith("## Upstream Issues"):
            in_table = True
            continue
        if not in_table:
            continue
        if line.startswith("## "):
            break
        if "|" not in line:
            continue
        cells = _split_table_row(line.strip().strip("|"))
        if len(cells) < 3:
            continue
        if cells[0].lower() in ("issue", "-----", ""):
            continue
        # Header separator line (---|---|---, with or without alignment markers)
        if all(set(c) <= set("-: ") for c in cells):
            continue
        # Row shape tolerance: `[#N](url)`, `#N`, and `owner/repo#N` all yield N.
        m = re.search(r"#(\d+)", cells[0])
        if not m:
            continue
        rows.append({
            "issue": m.group(1),
            "title": cells[1] if len(cells) > 1 else "",
            # NORMALIZED before matching (plan-048 Issue 3.4 / #173 defect 2). A cell
            # written `**partial**` used to parse as the literal `'**partial**'`, which
            # matched no disposition branch and so escaped verification entirely — measured
            # live on plan-023, which carries two such cells. Emphasis is presentation, not
            # content. This became load-bearing the moment 3.4 made an unrecognised literal
            # `fail` rather than `inconclusive`: without stripping, every bolded cell in the
            # corpus would halt its plan's reconcile.
            "disposition": _normalize_disposition(cells[2]),
            "notes": cells[3] if len(cells) > 3 else "",
            "resolved_by": cells[4] if len(cells) > 4 else "",
        })
    return rows


def _plan_non_exclude_upstream_numbers(plan_md_text: str) -> list[str]:
    """Issue numbers for any row whose disposition is not `exclude`/placeholder.

    A thin view over `parse_upstream_rows` — never its own parse (see that docstring).
    """
    return [
        r["issue"] for r in parse_upstream_rows(plan_md_text)
        if r["disposition"] not in ("", "exclude")
    ]


def _audit_finding(item: str, status: str, detail: str) -> dict:
    return {"item": item, "status": status, "detail": detail}


def _lint_findings_for_audit(plan_dir: Path) -> list[dict]:
    """Run the document linter over the plan bundle and map its verdict onto audit findings.

    THE MAPPING IS THE REQUIREMENT (REQ-DATA-057), not an implementation choice:

        linter `E` (error)   -> audit `fail`   the document does not have the shape its type
                                               declares, and intake is where that is caught
        linter `W` / `R`     -> audit `warn`   informational; never blocks
        INCONCLUSIVE         -> audit `warn`   NEVER `fail`

    **`Inconclusive` maps to `warn`, never to `fail`, and the distinction is load-bearing.**
    INCONCLUSIVE means *the linter could not run* — a missing schema directory, an unreadable
    document, an engine that is not deployed. That is a statement about the instrument, not
    about the plan. Mapping it to `fail` would block intake on the linter's own breakage, which
    is how a safety check becomes an outage; mapping it to `pass` would hide a linter that
    silently stopped working. `warn` is the only reading that reports it without gating on it.

    Fail-soft on absence, by the same argument: if the engine cannot be located at all, return
    a single `warn` rather than raising. A yf-plan installed without the vendored linter must
    still be able to run an audit.
    """
    import importlib.util as _ilu

    engine = None
    for cand in (Path(__file__).resolve().parent / "doc_lint.py",
                 Path(__file__).resolve().parent.parent.parent.parent / "_shared" / "doc_lint.py"):
        if cand.is_file():
            engine = cand
            break
    if engine is None:
        return [_audit_finding("doc-lint", "warn",
                               "document linter not found; document conformance UNCHECKED")]
    try:
        spec = _ilu.spec_from_file_location("doc_lint_for_audit", engine)
        mod = _ilu.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # TWO CALLS, and both are needed.
        #
        # (a) The WHOLE BUNDLE, path-routed (`only_type=None`), so each file is graded by the
        #     schema its own path selects — `findings/*` as findings, `reviews/*` as reviews.
        #     This is the reach that makes the gate worth having: plan-047's blocking errors
        #     lived in `findings/*.md`, not in `plan.md`.
        # (b) `plan.md` FORCED to the `plan` type. Path routing selects nothing for a bundle
        #     that sits outside the configured plans root, and "selected nothing" is
        #     `files_checked: 0` — a silent green. Forcing the type makes the plan document
        #     itself checkable wherever the bundle lives.
        #
        # Findings are de-duplicated below, since (b) re-checks a file (a) may already cover.
        files = sorted(plan_dir.rglob("*.md"))
        res = mod.lint(mod.REPO_ROOT, None, files)
        forced = mod.lint(mod.REPO_ROOT, "plan", [plan_dir / "plan.md"])
        seen = {(f.get("path"), f.get("check"), f.get("detail")) for f in res["findings"]}
        for f in forced["findings"]:
            if (f.get("path"), f.get("check"), f.get("detail")) not in seen:
                res["findings"].append(f)
        res["files_checked"] = max(res.get("files_checked", 0),
                                   forced.get("files_checked", 0))
    except Exception as exc:                      # noqa: BLE001 - see docstring
        return [_audit_finding("doc-lint", "warn",
                               f"INCONCLUSIVE: the linter could not run ({exc}); "
                               "document conformance UNCHECKED, intake NOT blocked")]
    if res.get("files_checked", 0) == 0:
        # `files_checked: 0` is INDISTINGUISHABLE from a clean pass at the exit-code level —
        # the precise silent green Issue 4.1's root-resolution fix exists to close. Report it
        # rather than accepting the green.
        return [_audit_finding("doc-lint", "warn",
                               "the linter selected ZERO files for this plan.md — "
                               "not-a-typed-document, not a clean pass")]
    out = []
    for f in res.get("findings", []):
        sev = f.get("severity")
        out.append(_audit_finding(
            f'doc-lint/{f.get("check")}',
            "fail" if sev == "E" else "warn",
            f'[{sev}] {f.get("detail", "")}'))
    return out


def _audit_plan(plan_dir: Path) -> dict:
    """Run the portability precondition audit. Returns structured result.

    status ∈ {"pass", "fail"} — a result is "pass" iff no findings have
    status="fail". Warn findings (grandfather clause) do not degrade overall
    status.

    Checks: (1) reserved `index.md` presence + OKF listing shape (REQ-PORT-001,
    replaces the legacy README File map/Reading order surface); (2) context.md
    required sections; (3) motivation; (4) upstream references; (5) reviews/pass-*.md
    count == `log.md` review-entry count (REQ-PORT-006); (6) no dangling refs;
    (7) REQ-PORT-050 OKF conformance floor (type + `okf_spec: OKF-PLAN` on every
    non-reserved `.md`, via the vendored `okf.check_conformance`); (8) dual-write
    consistency (R7 / REQ-DATA-015 — frontmatter and `**Field:**` must agree).

    The OKF scaffolding checks (#1, #7) are downgraded to `warn` for an OKF-legacy
    plan (date-grandfathered OR un-migrated — no `plan.md` frontmatter) and `fail` for
    an OKF-native plan, mirroring how the date grandfather downgrades the original
    portability scaffolding (#2–#5).
    """
    findings: list[dict] = []
    plan_md = plan_dir / "plan.md"

    if not plan_md.exists():
        return {
            "status": "fail",
            "findings": [_audit_finding("plan.md", "fail", "missing")],
            "report": f"{plan_dir}: plan.md missing; cannot audit.",
        }

    plan_text = plan_md.read_text()
    first_scoping = _plan_first_scoping_date(plan_dir)
    grandfathered = (
        first_scoping is not None
        and first_scoping < PORTABILITY_ACTIVATION_DATE
    )
    missing_level = "warn" if grandfathered else "fail"

    # OKF adoption gate (plan-029): the OKF-PLAN scaffolding checks — reserved
    # `index.md` (#1), the REQ-PORT-050 conformance floor (#7) — must NOT hard-fail a
    # plan created before OKF adoption. The date grandfather (2026-04-05) does not
    # cover them: every pre-adoption plan is scoped after it yet carries none of the
    # OKF surface. The reliable "OKF-native" marker is a parseable `plan.md`
    # frontmatter block — present on a born-OKF (seeded) or migrated plan, absent on a
    # legacy one. An OKF-legacy plan (grandfathered OR no `plan.md` frontmatter) gets
    # `warn` for missing OKF scaffolding, exactly as the date grandfather downgrades
    # the original portability scaffolding; an OKF-native plan gets a hard `fail`.
    try:
        plan_fm, _ = okf.read_frontmatter(plan_text)
    except okf.OKFParseError:
        plan_fm = {}
    okf_native = bool(plan_fm)
    okf_missing_level = "fail" if (okf_native and not grandfathered) else "warn"

    # 1. Reserved `index.md` — presence + OKF listing shape (REQ-PORT-001). Replaces
    #    the legacy README `File map` / `Reading order` surface; `README.md` is no
    #    longer required. `index.md` is the OKF-reserved bundle listing.
    index_md = plan_dir / "index.md"
    if not index_md.exists() or not index_md.read_text().strip():
        findings.append(_audit_finding(
            "index.md", okf_missing_level,
            "missing or empty; expected OKF-reserved bundle listing "
            "(replaces the legacy README file-map/reading-order surface)",
        ))
    elif not _index_is_listing(index_md.read_text()):
        findings.append(_audit_finding(
            "index.md", okf_missing_level,
            "not an OKF listing; expected a `#` heading plus `- [child](path)` "
            "bullets, not the legacy File map / Reading order prose",
        ))

    # 2. context.md — required sections non-empty (no unfilled placeholder lines)
    context = plan_dir / "context.md"
    if not context.exists() or not context.read_text().strip():
        findings.append(_audit_finding(
            "context.md", missing_level,
            "missing or empty; expected project-environment snapshot",
        ))
    else:
        ctext = context.read_text()
        for section in _CONTEXT_REQUIRED_SECTIONS:
            # Extract the section's body (everything up to the next `## ` header)
            m = re.search(
                rf"^##\s+{re.escape(section)}\s*$(.*?)(?=^##\s+|\Z)",
                ctext, flags=re.MULTILINE | re.DOTALL,
            )
            if not m:
                findings.append(_audit_finding(
                    f"context.md §{section}", "fail",
                    "section header missing",
                ))
                continue
            body = m.group(1).strip()
            # Strip HTML comment (snapshot header) before evaluating emptiness.
            stripped = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL).strip()
            if not stripped:
                findings.append(_audit_finding(
                    f"context.md §{section}", "fail",
                    "section is empty",
                ))
            elif (marker := _CONTEXT_PLACEHOLDERS.get(section)) and marker in stripped:
                findings.append(_audit_finding(
                    f"context.md §{section}", "fail",
                    "contains unedited template prose; fill in real values",
                ))

    # 3. Motivation: plan.md §Motivation or motivation.md, non-empty and not placeholder
    motivation_ok = False
    motivation_detail = ""
    mot_md = plan_dir / "motivation.md"
    if mot_md.exists() and mot_md.read_text().strip():
        motivation_ok = True
    else:
        m = re.search(
            r"^##\s+Motivation\s*$(.*?)(?=^##\s+|\Z)",
            plan_text, flags=re.MULTILINE | re.DOTALL,
        )
        if m:
            body = m.group(1).strip()
            if body and "Replace this placeholder" not in body \
                    and not re.fullmatch(r"_[^_]+_", body.strip()):
                motivation_ok = True
            else:
                motivation_detail = "§Motivation contains placeholder text"
        else:
            motivation_detail = "no plan.md §Motivation section or motivation.md file"
    if not motivation_ok:
        findings.append(_audit_finding(
            "motivation", "fail", motivation_detail or "missing",
        ))

    # 4. references/upstream-*.md — one file per non-exclude row
    expected_upstream = _plan_non_exclude_upstream_numbers(plan_text)
    refs_dir = plan_dir / "references"
    for n in expected_upstream:
        ref_file = refs_dir / f"upstream-{n}.md"
        if not ref_file.exists() or not ref_file.read_text().strip():
            findings.append(_audit_finding(
                f"references/upstream-{n}.md", "fail",
                "missing body for non-exclude upstream issue",
            ))

    # 5. reviews/pass-*.md — count == log.md review-entry count (legacy fallback:
    #    in-plan.md phase-log review lines when log.md is absent)
    expected_reviews = _plan_review_line_count(plan_dir)
    reviews_dir = plan_dir / "reviews"
    actual_reviews = 0
    if reviews_dir.exists():
        actual_reviews = len(list(reviews_dir.glob("pass-*.md")))
    if actual_reviews != expected_reviews:
        findings.append(_audit_finding(
            "reviews/", missing_level if actual_reviews == 0 else "fail",
            f"expected {expected_reviews} pass-*.md (one per phase-log review line), "
            f"found {actual_reviews}",
        ))

    # 7. REQ-PORT-050 conformance floor — every non-reserved bundle `.md` carries a
    #    parseable frontmatter block with a non-empty `type` and `okf_spec: OKF-PLAN`.
    #    Backed by the vendored OKF engine's `check_conformance` (error-level findings →
    #    audit finding; warning-level — type-vocab / required-key backfill — never a
    #    hard fail, matching the ratified error/warning split). Downgraded to `warn`
    #    for an OKF-legacy plan (grandfathered or un-migrated), `fail` for OKF-native.
    try:
        conf = okf.check_conformance(plan_dir, skill=SKILL_NAME)
        for cf in conf.findings:
            if cf.level != "error" or cf.req not in _OKF_PORT050_REQS:
                continue
            try:
                rel = str(Path(cf.path).relative_to(plan_dir))
            except ValueError:
                rel = cf.path
            findings.append(_audit_finding(
                f"okf:{rel}", okf_missing_level, f"{cf.req}: {cf.message}",
            ))
    except Exception as exc:  # engine is report-only/crash-safe; defensive only
        findings.append(_audit_finding(
            "okf-conformance", "warn",
            f"OKF conformance check errored (engine): {exc}",
        ))
    # REQ-PORT-050 selector value: `okf_spec` must be exactly `OKF-PLAN`. The engine
    # verifies presence (REQ-OKF-030) but not the value; a present-but-wrong selector
    # (e.g. a mis-stamped `OKF-RESEARCH`) is flagged here. Absence is already covered
    # by the conformance pass above.
    for md in sorted(plan_dir.rglob("*.md")):
        if md.name in okf.RESERVED_FILES:
            continue
        try:
            fm, _ = okf.read_frontmatter(md.read_text())
        except Exception:
            continue
        spec = str(fm.get("okf_spec") or "").strip()
        if spec and spec != _OKF_MEMBER:
            findings.append(_audit_finding(
                f"okf:{md.relative_to(plan_dir)}", okf_missing_level,
                f"okf_spec is {spec!r}, expected {_OKF_MEMBER!r} (REQ-PORT-050)",
            ))

    # 8. Dual-write consistency (R7 / REQ-DATA-015) — for every dual identity field the
    #    frontmatter value and the `**Field:**` header line must AGREE. A divergence is
    #    a single-writer-bypass writer bug or a hand-edit and is always a hard fail
    #    (it can only arise when BOTH surfaces exist, i.e. on an OKF-native plan). Read
    #    the two surfaces INDEPENDENTLY — not through the frontmatter-first accessor,
    #    which would mask the divergence.
    for key in PLAN_FIELD_ORDER:
        if key not in plan_fm:
            continue
        line_val = _read_field_line(plan_text, PLAN_FIELD_LABELS[key])
        if line_val is None:
            continue  # field lives only in frontmatter — no divergence to detect
        fm_val = str(plan_fm.get(key)).strip()
        if fm_val != line_val:
            findings.append(_audit_finding(
                f"dual-write:{key}", "fail",
                f"frontmatter {fm_val!r} != **{PLAN_FIELD_LABELS[key]}:** {line_val!r} "
                "(dual-write divergence — REQ-DATA-015)",
            ))

    # 9. The `**Epic:**` ref shall RESOLVE (REQ-CLI-020, plan-044 #143).
    #
    # A dangling ref is worse than a missing one: `_resume_scan` resolves plan.md
    # FIRST and falls back to `metadata.plan_dir` only when the field is ABSENT, so
    # a dangling-but-PRESENT field yields `found: true, total: 0` — a resumed
    # execute session reads "no open work" and skips the plan entirely.
    #
    # Severity uses `missing_level`, NOT `okf_missing_level`: the latter downgrades
    # every legacy bundle to `warn`, which would suppress exactly the 14 dangling
    # refs this check exists to surface.
    #
    # When `bd` is UNAVAILABLE the finding is `warn`, never `fail` — a plan bundle
    # is portable by contract, and hard-failing its own audit merely for being read
    # on a beads-less machine would punish the portability the bundle is designed
    # for. `_bd_list` already degrades to `[]` defensively, so "no beads at all" is
    # the signal for absent tooling.
    epic_ref = _read_plan_epic_field(plan_text)
    if epic_ref:
        beads = _all_plan_beads()
        if not beads:
            findings.append(_audit_finding(
                "epic-ref", "warn",
                f"cannot verify **Epic:** {epic_ref} — `bd` unavailable or no beads "
                "readable (portable bundle on a beads-less machine)",
            ))
        elif epic_ref not in beads:
            findings.append(_audit_finding(
                "epic-ref", missing_level,
                f"**Epic:** {epic_ref} does not resolve to any bead (dangling ref — "
                "resume-scan would report found=true with zero descendants, so an "
                "execute session would silently skip this plan)",
            ))

    # 6. No dangling external refs across all plan files.
    # Strip fenced/inline code spans first — they contain pattern examples,
    # regex snippets, and command documentation that legitimately mention
    # absolute paths without being references.
    dangling: list[str] = []
    for path in plan_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in (".md", ".txt", ""):
            continue
        try:
            text = path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        stripped = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        stripped = re.sub(r"`[^`]*`", "", stripped)
        for pat in _ABS_PATH_PATTERNS:
            for m in pat.finditer(stripped):
                dangling.append(f"{path.relative_to(plan_dir)}: {m.group(0)}")
        for _ in _PARENT_TRAVERSAL.finditer(stripped):
            dangling.append(f"{path.relative_to(plan_dir)}: ../ parent traversal")
    if dangling:
        findings.append(_audit_finding(
            "dangling-refs", "fail",
            "; ".join(sorted(set(dangling))[:10]),
        ))

    # --- plan-049 Issue 4.2: the intake binding (REQ-DATA-057) ------------------------
    #
    # THE ONE SITE, DELIBERATELY. Sites 1 and 3 (`ready-check`, `audit`) call `_audit_plan`
    # and branch on its status, so binding HERE gives both of them the linter for free — with
    # their existing exit codes (1 and 3) unchanged. `audit_close` also calls it and stays
    # ADVISORY for free, because it ignores the status by contract. Binding three call sites
    # separately would have produced three slightly different bindings.
    #
    # This is the gate plan-047's Epic 9 named and nobody wired: a non-conformant NEW plan was
    # caught only by the FAST tier, never at intake, so the check that would have blocked
    # plan-047 at its own intake did not exist.
    findings.extend(_lint_findings_for_audit(plan_dir))

    any_fail = any(f["status"] == "fail" for f in findings)
    status = "fail" if any_fail else "pass"
    report_lines = [f"Portability audit: {plan_dir}", ""]
    if grandfathered:
        report_lines.append(
            f"[grandfather] first scoping {first_scoping} < activation "
            f"{PORTABILITY_ACTIVATION_DATE}; missing scaffolding downgraded to warn."
        )
        report_lines.append("")
    if okf_missing_level == "warn" and not grandfathered:
        report_lines.append(
            "[okf-legacy] no plan.md frontmatter (un-migrated); missing OKF "
            "scaffolding (index.md, type/okf_spec) downgraded to warn."
        )
        report_lines.append("")
    for f in findings:
        report_lines.append(f"  [{f['status']:<4}] {f['item']}: {f['detail']}")
    if not findings:
        report_lines.append("  All checks passed.")
    return {
        "status": status,
        "findings": findings,
        "report": "\n".join(report_lines),
        "grandfathered": grandfathered,
        "okf_native": okf_native,
    }


@cli.command()
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "as_json", is_flag=True,
              help="Emit structured JSON. Default is human-readable report.")
@click.option("--retro", is_flag=True,
              help="Flag retro capture mode. Plumbing only — the mechanical audit is "
                   "unchanged; conversation mining is the captor agent's job (#3 §4). "
                   "Surfaced in output so the capture orchestration knows the mode.")
def audit(plan_dir: str, as_json: bool, retro: bool):
    """Run portability precondition audit on a plan directory (Epic 4).

    `--retro` is accepted for a uniform capture invocation surface but does NOT
    alter the mechanical verdict — retro conversation mining happens in the captor
    agent, not here (see agents/captor.md, SKILL.md Phase: CAPTURE Retro mode).
    """
    result = _audit_plan(Path(plan_dir))
    result["retro"] = retro
    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(result["report"])
        if retro:
            click.echo("\n(retro mode: conversation mining is performed by the "
                       "captor agent, not this audit.)")
    sys.exit(0 if result["status"] == "pass" else 1)


@cli.command("close-reconcile-step")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--reason", default="Upstream issues reconciled",
              help="Close reason recorded on the reconcile bead.")
@click.option("--json-output", "--json", "as_json", is_flag=True,
              help="Emit the structured verdict (default is also JSON).")
def close_reconcile_step(plan_dir: str, reason: str, as_json: bool):
    """Close the plan's reconcile bead, re-derived from `bd` (REQ-PLAN-076).

    WHY THIS IS A VERB AND NOT `bd close ${RECONCILE_STEP}`
    ------------------------------------------------------
    `RECONCILE_STEP` is assigned in exactly one place — SKILL.md §5.2a, the POUR path.
    The §5.2b RESUME path never re-derives it, so every resumed execution reaches §6.4
    with it unset.

    The consequence was measured live, and it is worse than "the close silently fails":
    `bd close` with no id argument does NOT error. It exits 0 and closes a DIFFERENT,
    in-progress bead, then reports success. (During this fix's own verification probe it
    closed the very bead running the probe.) So the resume path silently closes the wrong
    bead and asserts success — the same false-success shape as the reconcile defect this
    plan exists to fix, one step away from it.

    Propagating the variable would not be enough: a propagated variable can still be
    empty, and an empty one is actively destructive here. So the bead is re-derived from
    the epic, and an id is NEVER passed through to `bd` unresolved.
    """
    pdir = Path(plan_dir)
    plan_md = pdir / "plan.md"
    if not plan_md.exists():
        click.echo(json.dumps({
            "verdict": "fail", "passed": False,
            "reason": f"plan.md not found under {plan_dir}",
            "remediation": "Check the plan_dir argument, then re-run §6.4.",
        }))
        sys.exit(1)

    epic = _read_plan_epic_field(plan_md.read_text())
    if not epic:
        click.echo(json.dumps({
            "verdict": "inconclusive", "passed": False, "epic": None, "bead": None,
            "reason": "no **Epic:** field on plan.md — the reconcile bead cannot be "
                      "re-derived",
            "remediation": "Run `plan_manager.py record-epic <plan_dir> <epic-id>` if the "
                           "plan was poured before the field existed, then re-run §6.4.",
        }))
        sys.exit(0)

    candidates = [
        b for b in _all_plan_beads().values()
        if str(b.get("id", "")).startswith(f"{epic}.")
        and (b.get("issue_type") or b.get("type")) == "task"
        and str(b.get("title", "")).startswith("Reconcile:")
    ]

    if not candidates:
        # Distinguishable from "bd did not answer": if bd is down, _all_plan_beads is
        # empty for every plan, so report rather than halt. Either way we never guess.
        click.echo(json.dumps({
            "verdict": "inconclusive", "passed": False, "epic": epic, "bead": None,
            "reason": f"no reconcile bead found under {epic} (bd may be unavailable, or "
                      "this plan incorporated no upstream issues)",
            "remediation": "If this plan has upstream rows, check `bd list --all` and "
                           "close the reconcile bead by hand; otherwise no action.",
        }))
        sys.exit(0)

    already = [b for b in candidates if b.get("status") == "closed"]
    open_ones = [b for b in candidates if b.get("status") != "closed"]

    if not open_ones:
        click.echo(json.dumps({
            "verdict": "pass", "passed": True, "epic": epic,
            "bead": already[0].get("id"), "already_closed": True,
            "reason": "reconcile bead already closed (idempotent re-run)",
            "remediation": None,
        }))
        return

    bead = open_ones[0]["id"]
    try:
        r = subprocess.run(["bd", "close", bead, "--reason", reason],
                           capture_output=True, text=True, timeout=60)
        rc, err = r.returncode, (r.stderr or "").strip()
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as e:
        rc, err = None, str(e)

    if rc != 0:
        click.echo(json.dumps({
            "verdict": "inconclusive", "passed": False, "epic": epic, "bead": bead,
            "reason": f"could not close reconcile bead {bead}: "
                      f"{err or 'bd exited ' + str(rc)}",
            "remediation": f"Close it by hand: bd close {bead} --reason '{reason}'",
        }))
        sys.exit(0)

    click.echo(json.dumps({
        "verdict": "pass", "passed": True, "epic": epic, "bead": bead,
        "already_closed": False,
        "reason": f"closed reconcile bead {bead}",
        "remediation": None,
    }))


@cli.command("audit-close")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True,
              help="Emit the structured verdict (default is also JSON).")
def audit_close(plan_dir: str, as_json: bool):
    """Close-time bundle-conformance audit — ADVISORY (REQ-PLAN-075 / #140).

    Reports the **absolute** finding set and NEVER gates `set complete`.

    WHY A SEPARATE VERB FROM `audit`
    --------------------------------
    `audit` is a PLAN-phase gate: it exits non-zero on `fail` because a plan must not
    reach INTAKE unportable. Reusing it at close would inherit that halting exit code.
    This verb wraps the SAME `_audit_plan` engine (identical findings, no second
    implementation) and re-frames the verdict as advisory: it exits 0 unconditionally.
    The halting difference is structural, not a flag an author can get wrong.

    WHY ADVISORY AND NOT FAIL-LOUD
    ------------------------------
    Measured across the completed corpus, a fail-loud close-time audit would have
    blocked 22% of plans that legitimately completed — including one proven false
    positive (a Windows-drive-letter regex matching inside a quoted fixture body) and
    one failure the close step INFLICTED ON ITSELF via its own `log.md` write. Blocking
    completion on that record would be worse than the drift it detects.

    WHY THE ABSOLUTE SET AND NOT A DELTA
    ------------------------------------
    A delta-since-approval was considered and dropped. The Phase-3 audit is a
    *precondition of approval*, so the stored baseline is an empty fail set by
    construction on every non-`--force` approval — the delta EQUALS the absolute set in
    the normal path. Its entire measured benefit was suppressing one legacy case out of
    ten. And because this step cannot block, noise costs nothing.
    """
    pdir = Path(plan_dir)
    result = _audit_plan(pdir)
    findings = result.get("findings", []) or []
    fails = [f for f in findings if f.get("status") == "fail"]
    warns = [f for f in findings if f.get("status") == "warn"]

    if fails:
        verdict = "fail"
        reason = (f"{len(fails)} bundle-conformance finding(s) at close "
                  f"({len(warns)} warn). Completion is NOT blocked.")
        remediation = (
            "Advisory only — `set complete` proceeds regardless. To resolve, run "
            f"`/yf-plan capture {pdir.name}` and address:\n"
            + "\n".join(f"  - {f.get('item')}: {f.get('detail')}" for f in fails)
        )
    elif warns:
        verdict = "pass"
        reason = f"no failing findings at close ({len(warns)} warn)"
        remediation = None
    else:
        verdict = "pass"
        reason = "bundle is conformant at close"
        remediation = None

    click.echo(json.dumps({
        "verdict": verdict,
        "passed": verdict == "pass",
        "advisory": True,
        "audit_status": result.get("status"),
        "findings": findings,
        "fail_count": len(fails),
        "warn_count": len(warns),
        "grandfathered": result.get("grandfathered"),
        "reason": reason,
        "remediation": remediation,
    }, indent=2))

    # REQ-PLAN-075: an `advisory` step ALWAYS exits 0. This is not conditional on the
    # verdict, and deliberately has no flag to make it conditional — the guarantee is
    # what makes the step safe to run at close given the 22% measured block rate.
    sys.exit(0)


@cli.command("config-resolve")
@click.option("--autonomy", "autonomy_flag", default=None,
              help="Per-invocation autonomy override, reported with source `flag`.")
@click.option("--sweep-gates", "sweep_flag", default=None,
              help="Per-invocation execute-start sweep scope, reported with source `flag`.")
@click.option("--plan-dir", "plan_dir", type=click.Path(exists=True), default=None,
              help="Echo a resolved per-invocation override into this bundle's log.md.")
@click.option("--json-output", "--json", "as_json", is_flag=True,
              help="Emit structured JSON. Default is a human-readable report.")
def config_resolve(autonomy_flag: str | None, sweep_flag: str | None,
                   plan_dir: str | None, as_json: bool):
    """Report each config key's effective value AND the tier it came from (REQ-CLI-021).

    Precedence, highest first: ``flag`` > ``config.local`` > ``config.json`` >
    ``legacy`` > ``default``.

    A resolved value alone is undebuggable. The recurring question is not *what is
    autonomy set to* but *which of the five tiers won* — and a bare value cannot answer
    it, because the three config files are merged key-by-key before any caller sees
    them. So every key reports both ``value`` and ``source``.

    Registered **flat** (``@cli.command("config-resolve")``), never as a ``config`` group
    with a ``resolve`` subcommand: REQ-CLI-006's Verification greps ``@cli.command``,
    which does not match a group-registered subcommand, so a group would leave that
    enumeration and its own verification permanently inconsistent.

    A pure read — exits ``0``, mutates nothing, and emits JSON on stdout on every path
    including failure (REQ-CLI-016).
    """
    result: dict = {"keys": {}}
    try:
        if autonomy_flag is not None:
            _set_autonomy_override(autonomy_flag)
        if sweep_flag is not None:
            _set_sweep_gates_override(sweep_flag)
    except ValueError as e:
        # REQ-CLI-016: JSON on stdout even on the failure path. Still exit 0 — this is
        # a read verb, and a rejected flag is a reported condition, not a crash.
        result["error"] = str(e)
        result["keys"] = {}
        click.echo(json.dumps(result, indent=2))
        return

    def _entry(key: str, default, valid=None, flag_value=None):
        if flag_value is not None:
            return {"value": flag_value, "source": "flag", "default": default,
                    "valid": list(valid) if valid else None}
        raw, source = _config_source(key)
        if source == "default":
            value = default
        elif valid is not None and not (isinstance(raw, str) and raw.strip() in valid):
            # Present but unrecognised: the resolver falls back, so report the
            # EFFECTIVE value and say `default` — reporting the tier here would claim
            # a value that no resolver will ever return.
            value, source = default, "default"
        else:
            value = raw.strip() if isinstance(raw, str) else raw
        return {"value": value, "source": source, "default": default,
                "valid": list(valid) if valid else None}

    result["keys"][CONFIG_KEY_AUTONOMY] = _entry(
        CONFIG_KEY_AUTONOMY, AUTONOMY_DEFAULT, AUTONOMY_LEVELS, autonomy_flag)
    result["keys"][CONFIG_KEY_LANDING_STRATEGY] = _entry(
        CONFIG_KEY_LANDING_STRATEGY, LANDING_STRATEGY_DEFAULT, LANDING_STRATEGIES)
    result["keys"][CONFIG_KEY_SWEEP_GATES] = _entry(
        CONFIG_KEY_SWEEP_GATES, SWEEP_GATES_DEFAULT, SWEEP_GATES_VALUES, sweep_flag)
    raw_ma, src_ma = _config_source(CONFIG_KEY_MAX_ATTEMPTS)
    result["keys"][CONFIG_KEY_MAX_ATTEMPTS] = {
        "value": _resolve_max_attempts(),
        "source": src_ma if isinstance(raw_ma, int) and not isinstance(raw_ma, bool)
        and raw_ma >= 1 else "default",
        "default": MAX_ATTEMPTS_DEFAULT, "valid": None,
    }
    raw_mrc, src_mrc = _config_source(CONFIG_KEY_MAX_REVIEW_CYCLES)
    result["keys"][CONFIG_KEY_MAX_REVIEW_CYCLES] = {
        "value": _resolve_max_review_cycles(),
        "source": "flag" if _MAX_REVIEW_CYCLES_OVERRIDE is not None else (
            src_mrc if isinstance(raw_mrc, int) and not isinstance(raw_mrc, bool)
            and raw_mrc >= 1 else "default"),
        "default": MAX_REVIEW_CYCLES_DEFAULT, "valid": None,
    }
    raw_wt, src_wt = _config_source(CONFIG_KEY_WORKTREE)
    result["keys"][CONFIG_KEY_WORKTREE] = {
        "value": not _worktree_opted_out(), "source": src_wt,
        "default": True, "valid": None,
    }
    raw_vc, src_vc = _config_source(CONFIG_KEY_VALIDATE_CMD)
    result["keys"][CONFIG_KEY_VALIDATE_CMD] = {
        "value": _resolve_validate_cmd(), "source": src_vc,
        "default": None, "valid": None,
    }

    # Echo a per-invocation override into log.md so a MISDETECTION is auditable after
    # the fact (2.3). Detection is necessarily prose — a slash-command path has no argv
    # — so the token can be misread; that risk is identical in kind to today's `--force`,
    # and is mitigated the same way. The echo records the value the SCRIPT RESOLVED, not
    # the token the prose thought it saw: those differing is exactly the misdetection
    # this line exists to expose.
    if plan_dir is not None and autonomy_flag is not None and "error" not in result:
        try:
            resolved = result["keys"][CONFIG_KEY_AUTONOMY]["value"]
            bullet = (f"autonomy: per-invocation override resolved to {resolved!r} "
                      f"(source: flag) — overrides the configured/default level")
            okf.append_log(Path(plan_dir), bullet, date=datetime.now().strftime("%Y-%m-%d"))
            result["log_entry"] = bullet
        except Exception as e:  # never let bookkeeping fail a pure read
            result["log_error"] = str(e)

    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo("key                  value                source")
        click.echo("-" * 58)
        for k, v in result["keys"].items():
            click.echo(f"{k:<20} {str(v['value']):<20} {v['source']}")


@cli.command("retrospective-report")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True)
def retrospective_report(plan_dir: str, as_json: bool):
    """ADVISORY close-step report of the bundle's retrospective entries (4.4).

    Emits the REQ-COMPLETE-003 verdict envelope (``status`` + ``findings`` +
    ``remediation``) so ``test_close_contract.py`` counts it as a conformant chain step.

    **Advisory, never halting.** It exits ``0`` unconditionally, including when the file is
    absent — absence is a legitimate state (a plan that stopped for no reason and deviated
    in no way has nothing to record) and is never a finding (REQ-PORT-ACT-RETROSPECTIVE).
    Measurement, adjudication and any fix+prevention contract are deliberately out of scope:
    this plan emits the corpus, and halting on it stays with the analysis skill that will
    later read it.

    Position in the §6.4 chain is load-bearing: it is an OBSERVING step, so REQ-COMPLETE-001
    constraint 1 puts it above every plan-folder writer — in particular above the
    ``set-deliverable-class`` dual-write — or it would report on artifacts the close step
    itself had just written.
    """
    pdir = Path(plan_dir)
    path = pdir / RETROSPECTIVE_FILE
    entries: list[dict] = []
    if path.exists():
        text = path.read_text(encoding="utf-8")
        for block in re.split(r"(?=^## RE-\d+)", text, flags=re.M):
            m = re.match(r"^## RE-(\d+)", block)
            if not m:
                continue
            row = {}
            for line in block.splitlines():
                cell = re.match(r"^\|\s*`([a-z_]+)`\s*\|\s*(.*?)\s*\|\s*$", line)
                if cell:
                    row[cell.group(1)] = cell.group(2)
            row["id"] = f"RE-{int(m.group(1)):03d}"
            entries.append(row)

    by_kind: dict[str, int] = {}
    by_class: dict[str, int] = {}
    unverified = 0
    for e in entries:
        by_kind[e.get("kind") or "stop"] = by_kind.get(e.get("kind") or "stop", 0) + 1
        sc = e.get("stop_class") or ""
        if sc:
            by_class[sc] = by_class.get(sc, 0) + 1
        if (e.get("evidence") or "unverified") == "unverified":
            unverified += 1

    findings: list[str] = []
    if entries and unverified:
        findings.append(
            f"{unverified} of {len(entries)} entries carry `evidence: unverified` — a state "
            "assertion with no evidence is a narration, not a finding. Advisory only."
        )
    result = {
        "status": "ok",
        "present": path.exists(),
        "count": len(entries),
        "by_kind": by_kind,
        "by_stop_class": by_class,
        "unverified": unverified,
        "findings": findings,
        "remediation": (
            "Advisory. Absence is never a finding. To enrich a thin entry, re-run "
            "`retrospective-append` with `--evidence '<command + output>'`."
        ),
        "advisory": True,
    }
    click.echo(json.dumps(result, indent=2))


@cli.command("retrospective-append")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--kind", type=click.Choice(RETROSPECTIVE_KINDS), default="stop",
              help="`stop` (an autonomous run halted) or `deviation` (a non-stop defect).")
@click.option("--stop-class", "stop_class", default="",
              help="1-5 for a stop; empty for a deviation.")
@click.option("--asked", default="", help="What the operator was asked, verbatim.")
@click.option("--answered", default="", help="What they answered, verbatim.")
@click.option("--frontloadable", default="",
              help="Could this have been asked at execute start? yes|no|partial.")
@click.option("--detected-by", "detected_by",
              type=click.Choice(RETROSPECTIVE_DETECTED_BY), default="self-report",
              help="WHO found it. The recorder is usually the subject — say so.")
@click.option("--evidence", default="",
              help="The command + output substantiating any state claim, or `unverified`.")
@click.option("--escape-class", "escape_class", default="")
@click.option("--adjudication", default="")
@click.option("--origin", default="")
@click.option("--culpability", default="")
@click.option("--prevention", default="")
@click.option("--cost", default="")
@click.option("--dry-run", is_flag=True, help="Report what would be written; write nothing.")
@click.option("--json-output", "--json", "as_json", is_flag=True)
def retrospective_append(plan_dir: str, kind: str, stop_class: str, asked: str,
                         answered: str, frontloadable: str, detected_by: str,
                         evidence: str, escape_class: str, adjudication: str,
                         origin: str, culpability: str, prevention: str, cost: str,
                         dry_run: bool, as_json: bool):
    """Append one `## RE-NNN` entry to `plan-retrospective.md` (REQ-CLI-022).

    Creates the file (with `type: Retrospective` frontmatter) when absent and adds it to
    the reserved `index.md` listing. Idempotent on entry identity; `RE-NNN` ids are
    allocated monotonically and never reused.

    Two fields carry the weight (REQ-PORT-052, D-6a):

    * ``--detected-by`` — ``self-report`` | ``operator`` | ``mechanical-check``. An entry's
      trust level is a property of WHO FOUND IT, and the recorder is usually the subject.
    * ``--evidence`` — the command and output behind any state claim, or the literal
      ``unverified``. Defaults to ``unverified`` rather than to blank, so an
      unsubstantiated entry is **self-identifying** instead of merely quiet.

    ``--kind deviation`` exists because the incident that motivated both fields was a
    NON-STOP: a stop-only schema is blind to exactly the class autonomy makes more common.
    """
    entry = {
        "kind": kind, "stop_class": stop_class, "asked": asked, "answered": answered,
        "frontloadable": frontloadable, "detected_by": detected_by, "evidence": evidence,
        "escape_class": escape_class, "adjudication": adjudication, "origin": origin,
        "culpability": culpability, "prevention": prevention, "cost": cost,
    }
    try:
        result = append_retrospective(Path(plan_dir), entry, dry_run=dry_run)
    except ValueError as e:
        click.echo(json.dumps({"error": str(e), "appended": False}, indent=2))
        sys.exit(1)
    result["dry_run"] = dry_run
    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        verb_txt = "would append" if dry_run else ("appended" if result["appended"] else "skipped (duplicate)")
        click.echo(f"{verb_txt} {result['id']} -> {result['file']}")


@cli.command("review-loop-check")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--max-review-cycles", "raise_to", type=int, default=None,
              help="Per-invocation raise of the bound — the operator's escalation exit.")
@click.option("--json-output", "--json", "as_json", is_flag=True,
              help="Emit structured JSON. Default is a human-readable report.")
def review_loop_check(plan_dir: str, raise_to: int | None, as_json: bool):
    """Bound the autonomous review loop (2.4a). Exits ``3`` on escalation, ``0`` otherwise.

    Issue 2.4 grants the review loop autonomy in **Phase 3 — before intake, before the
    pour, before any bead exists** — so D-3's ``yf_attempts`` (bd metadata, incremented
    in the coordinator loop) structurally cannot reach it. Without this counter the
    plan's headline change would be exactly the unbounded-autonomy shape D-8 forbids.

    The count is ``len(glob('reviews/pass-*.md'))``, **not** ``_plan_review_line_count``
    (a different number that can and does diverge). It is **monotonic** — pass files are
    never deleted — with two consequences this counter needs and ``yf_attempts`` does not:

    * **Escalation exit.** At ``N`` the loop escalates (stop class 4) and the plan sits in
      ``review`` with a REVISE verdict. That is a legal state, not a wedge: REQ-PLAN-030
      bars only ``ready-for-approval``.
    * **No auto-reset.** ``--max-review-cycles`` is the operator's only exit, and it is
      per-invocation and echoed to ``log.md``. Without that raise every subsequent cycle
      re-escalates immediately — deliberate: a plan that has burned ``N`` review cycles
      should not silently resume.
    """
    pdir = Path(plan_dir)
    result: dict = {}
    try:
        if raise_to is not None:
            _set_max_review_cycles_override(raise_to)
    except ValueError as e:
        click.echo(json.dumps({"error": str(e), "escalates": True}, indent=2))
        sys.exit(3)

    escalates, cycles, limit = _review_loop_escalates(pdir)
    result.update({
        "escalates": escalates,
        "cycles": cycles,
        "limit": limit,
        "stop_class": 4 if escalates else None,
        "autonomy": _resolve_autonomy(),
        "raised": raise_to,
    })
    if escalates:
        result["remediation"] = (
            f"the review loop has run {cycles} cycle(s), at or above the bound of {limit}. "
            "Stop class 4 (mechanical counter threshold). The plan stays in `review` with "
            "its REVISE verdict — a legal state, not a wedge. Either resolve the concerns "
            "by hand, or re-run with `--max-review-cycles <n>` to raise the bound for this "
            "invocation (the raise is echoed to log.md and does not persist)."
        )
    if raise_to is not None:
        try:
            bullet = (f"autonomy: max-review-cycles raised to {raise_to} for this invocation "
                      f"(cycles={cycles}) — escalation override")
            okf.append_log(pdir, bullet, date=datetime.now().strftime("%Y-%m-%d"))
            result["log_entry"] = bullet
        except Exception as e:
            result["log_error"] = str(e)

    click.echo(json.dumps(result, indent=2))
    sys.exit(3 if escalates else 0)


def _ready_check_result(pdir: Path) -> dict:
    """The REQ-PLAN-066 readiness verdict as data (plan-047 Issue 2.5).

    Extracted from the `ready-check` command so `update-status` can enforce it at the
    `approved` transition (REQ-DATA-028) instead of merely reporting it. Before this,
    `ready-check` exiting 3 and `update-status … approved` exiting 0 on the SAME plan was
    reproducible in two commands — the intake gate was prose obedience, not code.
    """
    reasons: list[str] = []

    n, verdict, review_file = _latest_review_verdict(pdir)
    malformed_review: str | None = None
    if verdict is None and review_file is not None:
        # REQ-PLAN-072: a review EXISTS but its verdict did not parse. This is a
        # malformed review, not an absent one — reporting it as `verdict: null`
        # alongside `review_pass: N` is a self-contradiction that hides the real
        # cause (the trap #116 sprang). Name the offending file.
        malformed_review = str(review_file)
        reasons.append(
            f"malformed review: {review_file} exists (pass-{n}) but contains no "
            "parseable verdict line — expected '## Verdict: APPROVE|REVISE|"
            "INVESTIGATE-MORE' (REQ-PLAN-071). This is NOT an absent verdict; "
            "fix the verdict line in that file")
    elif verdict is None:
        reasons.append(
            "no red-team verdict found — expected reviews/pass-N.md with a "
            "'## Verdict:' line")
    elif verdict != "APPROVE":
        reasons.append(
            f"last red-team verdict is {verdict} (pass-{n}); a REVISE/INVESTIGATE-MORE "
            "blocks ready-for-approval until a later cycle returns APPROVE")

    audit = _audit_plan(pdir)
    if audit["status"] != "pass":
        reasons.append(
            f"portability audit did not pass (status={audit['status']}) — run "
            "`/yf-plan capture` or fix the failing findings")

    ready = not reasons
    result = {
        "ready": ready,
        "reasons": reasons,
        "verdict": verdict,
        "review_pass": n,
        "malformed_review": malformed_review,
        "audit_status": audit["status"],
    }
    return result


@cli.command("ready-check")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True,
              help="Emit structured JSON. Default is a human-readable report.")
def ready_check(plan_dir: str, as_json: bool):
    """Gate the approval prompt (REQ-PLAN-066).

    Verifies BOTH preconditions of the approval prompt, so approval is consent to an
    already-verified plan (not "approve, then verify"):

      1. the **last recorded** red-team verdict (highest ``reviews/pass-N.md``) is
         ``APPROVE`` (REQ-PLAN-030) — a later REVISE/INVESTIGATE-MORE that was never
         re-reviewed blocks readiness;
      2. the portability ``audit`` passes (REQ-PLAN-033).

    Emits ``{"ready": bool, "reasons": [...], "verdict": ..., "review_pass": ...,
    "malformed_review": ..., "audit_status": ...}``. Exits ``3`` when not ready (a
    gate signal, distinct from a ``1`` crash), ``0`` when ready.

    ``malformed_review`` (REQ-PLAN-072) is the path of a review file that exists but
    whose verdict did not parse, else ``null``. It disambiguates the two ways
    ``verdict`` can be ``null``: no review at all (``review_pass: null``) versus a
    review present but unparseable (``review_pass: N``). The latter used to surface
    as a bare null verdict — a contradiction that read as "no review has run".
    """
    pdir = Path(plan_dir)
    result = _ready_check_result(pdir)
    ready, reasons, n = result["ready"], result["reasons"], result["review_pass"]

    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        if ready:
            click.echo(
                f"ready-check: READY (last red-team APPROVE at pass-{n} + audit pass)")
        else:
            click.echo("ready-check: NOT READY")
            for r in reasons:
                click.echo(f"  - {r}")
    sys.exit(0 if ready else 3)


if __name__ == "__main__":
    cli()
