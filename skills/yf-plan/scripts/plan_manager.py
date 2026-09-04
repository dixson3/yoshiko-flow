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
from collections import Counter
import socket
import subprocess
import sys
import traceback
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
    constants bound before most of this module exists (REQ-PLAN-079, import-safe
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

# Repo layout is configurable (REQ-PLAN-079 / #107): a project whose plan or
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


#: REQ-STATUS-001 / REQ-PLAN-001 — the TEN recognised plan statuses, in lifecycle order.
#: `abandoned` (#208, plan-053) is terminal-but-not-successful: reachable from any
#: non-`complete` status, leaving by exactly one edge back to `drafting`, and explicitly NOT
#: execute-eligible and NOT parked.
PLAN_STATUS_VALUES = (
    "scoping", "investigating", "drafting", "review", "ready-for-approval",
    "approved", "executing", "reconciling", "complete", "abandoned",
)


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


def _clear_plan_fields(plan_dir: Path, keys: tuple[str, ...]) -> bool:
    """Remove header fields from BOTH dual-written surfaces (plan-053 Issue 4.3, #207).

    The mirror of `_write_plan_fields`, and it exists for the same reason: there must be no
    path that touches one surface without the other. Hand-editing `plan.md` reliably removes
    the `**Epic:**` line and leaves the frontmatter `epic:` key (or the reverse), which is
    precisely the half-cleared state #207's operators produced.

    Returns True iff anything was actually removed — the caller's idempotency signal.
    """
    plan_md = plan_dir / "plan.md"
    text = plan_md.read_text()
    model: dict[str, str] = {}
    removed = False
    for k in PLAN_FIELD_ORDER:
        v = _read_plan_field(text, k)
        if v is None:
            continue
        if k in keys:
            removed = True
            continue
        model[k] = v
    # A frontmatter key may survive with no matching `**Field:**` line, so check surface 2
    # independently rather than inferring from surface 1.
    fm, _body = okf.read_frontmatter(plan_md)
    if any(k in fm for k in keys):
        removed = True
    if not removed:
        return False
    plan_md.write_text(_rebuild_field_block(text, model))
    okf.write_frontmatter(plan_md, dict(model), delete=list(keys))
    return True

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
    `docs/plans` — REQ-PLAN-079); callers that target an incubator should pass
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


def _stamp_okf_type(plan_dir: Path, md_path: Path,
                    description: str | None = None) -> None:
    """Stamp `type` (role-mapped) + `okf_spec: OKF-PLAN` frontmatter onto a
    non-reserved bundle `.md` (REQ-PORT-050). The `type` is assigned from the bundle-
    relative path via the OKF-EXTENSION §1a map (`plan.md`→Plan, `context.md`→
    Environment, `references/*`→Reference, …), falling back to the member default.
    Merge-and-preserves existing keys and sits above the first `## ` (REQ-OKF-010/070).

    ``description`` implements the REQ-DATA-075 PRODUCER CONTRACT (plan-056 Issue 2.1).
    It is stamped only when the CALLER SUPPLIES one — never derived here — because the
    caller is the only party that holds the content a real description is made of, and a
    description derived from the path would be the same string in every bundle. OKF v0.2
    §8 wants "the description from the linked concept's frontmatter", which is only worth
    having if it says something the filename does not.

    An EMPTY or whitespace-only value is treated as ABSENT rather than written: the paired
    linter check is ``^description:\\s*\\S``, so writing an empty string would satisfy the
    key's presence and fail its content — the worst of both.
    """
    ext = _okf_plan_extension()
    rel = str(md_path.relative_to(plan_dir))
    if ext.found and ext.type_map:
        typ, _matched = okf._assign_type(rel, ext.type_map, ext.default_type)
        member = ext.member or _OKF_MEMBER
    else:
        typ, member = "Concept", _OKF_MEMBER
    meta: dict = {"type": typ, "okf_spec": member}
    if description and description.strip():
        meta["description"] = description.strip()
    okf.write_frontmatter(md_path, meta)


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
    # REQ-DATA-075 (plan-056 Issue 2.2): plan.md's description IS the objective — the one
    # sentence a reader wants when the bundle appears in a listing. It is the clearest case
    # of "the answer, not the question": the objective already states what this plan is for.
    _stamp_okf_type(plan_dir, plan_md, description=objective.strip())
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
    # EXECUTION-TIME MEMBER (REQ-PLAN-081(a), plan-056 Issue 2.3). A plan that ships its own
    # instruments creates `scripts/` DURING EXECUTION — after `seed_index` has already run —
    # so it was invisible to the reserved listing forever.
    #
    # `scripts/` ONLY. `assets/` is NOT added here, and the distinction is the point: it has
    # been in this set since plan-029 and goes unlisted for a DIFFERENT reason —
    # `_index_member_present` is evaluated at SEED TIME, and an empty `assets/` is absent from
    # every clone because git does not track empty directories. Re-adding it would be a no-op
    # that looks like a fix while leaving the real cause — a one-shot seed over a growing
    # bundle — untouched. That cause is REQ-PLAN-081(b)'s three `reindex_write` call sites.
    ("scripts/", "Executable checks and helpers this plan ships for its own criteria."),
    ("plan-retrospective.md", "Stops and deviations recorded during execution (`## RE-NNN` entries). PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding (REQ-PORT-ACT-RETROSPECTIVE)."),
    # EXECUTION-TIME MEMBER (plan-059 Issue 2.4, REQ-PORT-053). Same presence-optional
    # contract as the retrospective, and listed here for the same reason: a bundle member
    # absent from the reserved listing violates the cold-reader contract the listing exists
    # to carry. `escalation-raise` calls `_ensure_index_lists_member` on every write, so an
    # escalation raised long after `seed_index` ran is still listed.
    ("escalations.md", "Open questions raised to the upstream controller during execution (`## ESC-NNN` entries), each with its alternatives, its recommended default, and what happens if no answer arrives. PRESENCE-OPTIONAL — absent from most bundles, and its absence is never an audit finding of any severity (REQ-PORT-ACT-ESCALATION)."),
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


# --- escalations.md (plan-059 Epic 2, REQ-PORT-053 / REQ-PORT-054) ---------------------

ESCALATION_FILE = "escalations.md"

#: REQ-PORT-054's field set, in emission order.
#:
#: The first nine are the requirement's own list. The last four are INSTRUMENTATION, and they
#: exist because research 005 §8.4 names the missing half of the escalation question: nobody
#: has ever measured how often an escalation is answered versus how often its default is
#: silently taken. `escalation-report` computes `raised`, `answered` and `no_answer_taken`
#: from these, and `push_batch` is what makes BATCHING observable rather than asserted —
#: escalations sharing a batch id were sent in one notification.
ESCALATION_FIELDS: tuple[str, ...] = (
    "question", "alternatives", "recommended", "on_no_answer", "detected_by",
    "evidence", "asked_of", "state", "answer",
    "raised_when", "resolved_when", "no_answer_taken", "push_batch",
)
ESCALATION_STATES = ("raised", "answered", "resolved", "withdrawn")
ESCALATION_DETECTED_BY = ("self-report", "operator", "mechanical-check")

_ESCALATION_HEADER = """---
type: Escalation
okf_spec: OKF-PLAN
---
# Escalations

Questions this plan raised to its upstream controller, newest last. Each `## ESC-NNN` section
is one entry; `ESC-NNN` ids are append-only and are never reused or renumbered.

**The architecture is WRITE-THEN-NOTIFY, never ask-and-await.** The herdr channel has no
answer-return primitive, so the escalation IS this artifact and any push is merely a
notification about it. That is why `on_no_answer` is required on every entry: an escalation
that omits its own default pretends to a round-trip the transport cannot deliver.

`recommended` is stored SEPARATELY from `answer`, and the separation is the point. The
dominant operator input across the corpus is a choice among stated alternatives, and a schema
that records only the resolution destroys the default it was chosen against.

An escalation whose recommended default was taken **without an answer arriving** is
`resolved`, not `raised` — with `answer` recording the default that was taken. Leaving it
`raised` would make every fire-and-forget escalation trip the close-time open-escalation
warning, which would train a reader to ignore it.

"""


def _escalation_next_id(text: str) -> int:
    """The next `ESC-NNN` number: max existing + 1. Append-only, never reused."""
    nums = [int(m) for m in re.findall(r"^## ESC-(\d+)", text, re.M)]
    return (max(nums) + 1) if nums else 1


def _escalation_blocks(text: str) -> dict[str, str]:
    """Split `escalations.md` into `{ESC-NNN: raw block text}` (preamble excluded)."""
    out: dict[str, str] = {}
    for block in re.split(r"(?=^## ESC-\d+)", text, flags=re.M):
        m = re.match(r"^## (ESC-\d+)", block)
        if m:
            out[m.group(1)] = block
    return out


def _escalation_entries(text: str) -> dict[str, dict[str, str]]:
    """Parse `escalations.md` into `{ESC-NNN: {field: value}}`."""
    out: dict[str, dict[str, str]] = {}
    for eid, block in _escalation_blocks(text).items():
        fields: dict[str, str] = {}
        for line in block.splitlines():
            cell = re.match(r"^\|\s*`([a-z_]+)`\s*\|\s*(.*?)\s*\|\s*$", line)
            if cell:
                fields[cell.group(1)] = cell.group(2)
        out[eid] = fields
    return out


def _escalation_render(eid: str, row: dict[str, str]) -> str:
    lines = [f"## {eid}", "", "| Field | Value |", "| :-- | :-- |"]
    for k in ESCALATION_FIELDS:
        lines.append(f"| `{k}` | {row.get(k, '')} |")
    lines.append("")
    return "\n".join(lines) + "\n"


def _escalation_others_hash(text: str, skip: str) -> str:
    """Hash every entry block EXCEPT ``skip``, in id order.

    This is what `escalation-resolve` reports as `prior_entries_unchanged` — computed from
    the bytes it did not touch, **never from its own assertion** (R9). A verb that reports
    its own correctness has reported nothing.
    """
    blocks = _escalation_blocks(text)
    payload = "".join(blocks[k] for k in sorted(blocks) if k != skip)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _escalation_write(path: Path, text: str) -> None:
    """Write-temp-then-rename. NEVER an in-place truncation (R9).

    `escalation-resolve` mutates a row inside a committed markdown artifact — a capability
    class this repository did not previously have, since every other bundle write verb is
    append-or-regenerate. A truncate-then-write that is interrupted leaves a bundle member
    half-erased; a rename is atomic on every filesystem this runs on.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def raise_escalation(plan_dir: Path, *, question: str, alternatives: list[str],
                     recommended: str, on_no_answer: str, detected_by: str,
                     evidence: str = "", asked_of: str = "",
                     dry_run: bool = False) -> dict:
    """Append one `## ESC-NNN` entry to the bundle's `escalations.md` (REQ-PORT-053).

    Validates ON WRITE against the same domain rules `escalations.toml` checks, so a
    malformed escalation never reaches the file. That layering is deliberate and is why the
    escalation-schema capability gate writes its INVALID document directly rather than
    routing it through this verb: a positive control that went through `raise_escalation`
    would be rejected at step 1 by a CORRECT implementation, and the gate would be testing
    the wrong thing.

    Idempotent on entry identity: re-raising an escalation whose `question` and
    `alternatives` match an existing entry returns that entry rather than appending a twin.
    """
    path = plan_dir / ESCALATION_FILE
    created = not path.exists()
    text = _ESCALATION_HEADER if created else path.read_text(encoding="utf-8")

    alts = [a.strip() for a in alternatives if a and a.strip()]
    if not question.strip():
        raise ValueError("--question is required and may not be empty")
    if len(alts) < 2:
        raise ValueError(
            f"at least two --alternative values are required (got {len(alts)}); an "
            "escalation with one option is a notification, not a question"
        )
    if not recommended.strip():
        raise ValueError("--recommended is required — it is the dominant operator input")
    # THE SEPARATOR MAY NOT APPEAR INSIDE A VALUE, and this check exists because its absence
    # produced a live defect rather than a hypothetical one.
    #
    # `alternatives` serialises as a `; `-joined cell. An alternative containing `;` therefore
    # SPLITS on re-read, so `recommended` — which matched perfectly against the in-memory list
    # at write time — matches nothing at read time. The entry passed validate-on-write and then
    # FAILED ITS OWN SCHEMA on the next lint, which turned the portability audit red.
    #
    # Validating the in-memory list was checking the wrong artifact. The document is what the
    # schema judges, so the write path must validate what will be WRITTEN — that is the whole
    # point of validate-on-write, and it was being half-honoured.
    _bad_sep = [a for a in alts + [recommended] if ";" in a]
    if _bad_sep:
        raise ValueError(
            "`;` is the alternatives separator and may not appear inside an alternative or "
            f"in --recommended (offending: {_bad_sep[0][:80]!r}). Rephrase with a comma or an "
            "em dash: a value containing the separator splits on re-read, so `recommended` "
            "would match nothing and the entry would fail its own schema after being written."
        )
    if recommended.strip().lower() not in [a.lower() for a in alts]:
        raise ValueError(
            f"--recommended {recommended!r} is not one of --alternative "
            f"({' ; '.join(alts)}); a schema whose recommended need not name one of its "
            "alternatives is not a schema"
        )
    if not on_no_answer.strip():
        raise ValueError(
            "--on-no-answer is required on every escalation: the transport has no "
            "answer-return path, so an entry without a default pretends to a round-trip "
            "that cannot be delivered"
        )
    if detected_by not in ESCALATION_DETECTED_BY:
        raise ValueError(
            f"--detected-by {detected_by!r} is outside its closed domain "
            f"({' | '.join(ESCALATION_DETECTED_BY)})"
        )

    existing = _escalation_entries(text)
    for eid, fields in sorted(existing.items()):
        if (fields.get("question", "").strip() == question.strip()
                and fields.get("alternatives", "").strip() == "; ".join(alts)):
            return {"file": str(path), "id": eid, "appended": False,
                    "created": False, "index_updated": False, "state": fields.get("state", "")}

    eid = f"ESC-{_escalation_next_id(text):03d}"
    row = {
        "question": question.strip(),
        "alternatives": "; ".join(alts),
        "recommended": recommended.strip(),
        "on_no_answer": on_no_answer.strip(),
        "detected_by": detected_by,
        # `unverified` rather than blank: an unsubstantiated escalation must be
        # SELF-IDENTIFYING, or the R4 Goodhart incentive has no counterweight.
        "evidence": evidence.strip() or "unverified",
        "asked_of": asked_of.strip(),
        "state": "raised",
        "answer": "",
        "raised_when": datetime.now().strftime("%Y-%m-%d"),
        "resolved_when": "",
        "no_answer_taken": "no",
        "push_batch": "",
    }
    new_text = text.rstrip("\n") + "\n\n" + _escalation_render(eid, row)

    index_updated = False
    if not dry_run:
        _escalation_write(path, new_text)
        _stamp_okf_type(
            plan_dir, path,
            description=("Open questions raised to the upstream controller during "
                         "execution, with alternatives, a recommended default, and what "
                         "happens if no answer arrives."),
        )
        index_updated = _ensure_index_lists_member(plan_dir, ESCALATION_FILE)
    return {"file": str(path), "id": eid, "appended": True, "created": created,
            "index_updated": index_updated, "state": "raised"}


def resolve_escalation(plan_dir: Path, eid: str, *, answer: str,
                       default_taken: bool = False, by: str = "",
                       state: str = "resolved") -> dict:
    """Record an answer on an existing `## ESC-NNN` entry (REQ-PORT-054).

    Reports `prior_entries_unchanged`, computed from a pre/post hash of the entry blocks it
    did not touch — never from its own assertion.
    """
    path = plan_dir / ESCALATION_FILE
    if not path.exists():
        raise ValueError(f"no {ESCALATION_FILE} in {plan_dir}")
    text = path.read_text(encoding="utf-8")
    entries = _escalation_entries(text)
    eid = eid.upper()
    if eid not in entries:
        raise ValueError(f"{eid} not found in {path} (have: {', '.join(sorted(entries))})")
    if state not in ESCALATION_STATES:
        raise ValueError(f"--state {state!r} outside {' | '.join(ESCALATION_STATES)}")

    before = _escalation_others_hash(text, eid)
    row = dict(entries[eid])
    for k in ESCALATION_FIELDS:
        row.setdefault(k, "")
    row["answer"] = (answer.strip() + (f" (default taken by {by})" if default_taken and by else "")) \
        if answer.strip() else row.get("answer", "")
    row["state"] = state
    row["resolved_when"] = datetime.now().strftime("%Y-%m-%d")
    row["no_answer_taken"] = "yes" if default_taken else "no"

    blocks = _escalation_blocks(text)
    old_block = blocks[eid]
    new_block = _escalation_render(eid, row)
    # Preserve whatever trailing whitespace the old block carried, so the only bytes that
    # change are this entry's own.
    new_text = text.replace(old_block, new_block if old_block.endswith("\n") else new_block.rstrip("\n"), 1)
    after = _escalation_others_hash(new_text, eid)

    _escalation_write(path, new_text)
    return {
        "file": str(path), "id": eid, "state": row["state"],
        "answer": row["answer"], "no_answer_taken": row["no_answer_taken"] == "yes",
        "prior_entries_unchanged": before == after,
        "prior_entries_hash_before": before, "prior_entries_hash_after": after,
    }


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
    # ONE FORMAT, ONE EMITTER (REQ-OKF-012(b), plan-057 Issue 1.3). This function is a
    # SECOND, INDEPENDENT bullet writer — it never calls `okf.add_index_entry` — and it used
    # to spell the bullet itself. Two writers that merely AGREE today are one edit away from
    # producing two formats inside a single `index.md`, which turns the live `okf-index-drift`
    # gate red on the next bundle that grows a member. Routing both through
    # `okf._index_bullet` makes the agreement structural instead of coincidental.
    #
    # The `_INDEX_MEMBERS` string is the CALLER-SUPPLIED first link of the description chain
    # (REQ-OKF-012(c)), so an authored member description still wins; a member with no
    # authored string falls through to the file's own `description:`, then its H1, then bare.
    desc = next((d for m, d in _INDEX_MEMBERS if m == member), "")
    bullet = okf._index_bullet(member, member,
                               okf.resolve_description(plan_dir, member, desc))
    lines = text.splitlines(keepends=True)
    # THE LAST BULLET OF *ANY* INDENTATION (plan-056 Issue 2.4). `ln.startswith("- [")`
    # matched only COLUMN-0 bullets, so on a GROUPED index — a top-level member followed by
    # its indented children — the "last bullet" resolved to the last GROUP HEADING, and the
    # new entry was inserted BETWEEN that heading and its own children. Every child of the
    # final group was thereby REPARENTED under the newly added member.
    #
    # Red today for plan-048, plan-049 and plan-050, whose indexes all end in a group.
    #
    # NO NEW REQ: this restores the behaviour REQ-PLAN-010's index contract already implies,
    # so it is a bug fix to a shipped requirement rather than a behaviour change.
    last = max((i for i, ln in enumerate(lines)
                if re.match(r"^[ \t]*[-*][ \t]+\[", ln)), default=None)
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
    # THE LAST BULLET OF *ANY* INDENTATION (plan-056 Issue 2.4). `ln.startswith("- [")`
    # matched only COLUMN-0 bullets, so on a GROUPED index — a top-level member followed by
    # its indented children — the "last bullet" resolved to the last GROUP HEADING, and the
    # new entry was inserted BETWEEN that heading and its own children. Every child of the
    # final group was thereby REPARENTED under the newly added member.
    #
    # Red today for plan-048, plan-049 and plan-050, whose indexes all end in a group.
    #
    # NO NEW REQ: this restores the behaviour REQ-PLAN-010's index contract already implies,
    # so it is a bug fix to a shipped requirement rather than a behaviour change.
    last = max((i for i, ln in enumerate(lines)
                if re.match(r"^[ \t]*[-*][ \t]+\[", ln)), default=None)
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
    # DELIBERATELY UNSTAMPED (REQ-DATA-075 exemption). `context.md` is one file per bundle
    # with one shape, so any derived description here is the SAME STRING in every bundle —
    # measured, 67 identical copies. A key whose value is constant across the corpus carries
    # zero information and dilutes the ones that do not.
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
    # REQ-DATA-075 (plan-056 Issue 2.1): the description carries the ANSWER, not the
    # question — the issue's own title, which is what a reader scanning the root index
    # needs in order to decide whether to open the file.
    _stamp_okf_type(plan_dir, path,
                    description=f"Upstream issue #{number} - {issue.get('title', '')}".strip())
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
    # DELIBERATELY UNSTAMPED (REQ-DATA-075 exemption), same ground as `context.md`: one file
    # per bundle, one shape, so a derived description is a constant across the corpus. It is
    # also a TRANSIENT authoring surface — the operator fills it in and the answers migrate
    # into plan.md — so it is not a concept document a listing entry helps a reader find.
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
    _stamp_okf_type(
        plan_dir, path,
        # REQ-DATA-075: a FIXED statement of what the file records. Fixed rather than
        # derived because the useful variable content — the dispositions themselves —
        # is the file's body, and a description restating it would go stale on every
        # re-triage while the body stayed correct.
        description="Disposition of each candidate upstream issue, with the reasoning "
                    "behind it — the triage record behind plan.md's Upstream Issues table.")
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
            # `abandoned` (#208, plan-053): a plan DELIBERATELY STOPPED. Its tag is
            # MUTUALLY EXCLUSIVE with PARKED by construction — `_is_parked` keys on
            # `approved` alone and is deliberately NOT widened to include `abandoned`,
            # because the parked nudge's text is literally "run /yf-plan execute", which is
            # exactly the wrong thing to say about a plan someone stopped on purpose.
            abandoned_tag = ("  ⏹ ABANDONED (deliberately stopped — not execute-eligible)"
                             if p["status"] == "abandoned" else "")
            click.echo(
                f"  {p['id']:<35} [{scope:<18}] "
                f"{p['objective']:<40} status: {p['status']}"
                f"{stale_tag}{parked_tag}{abandoned_tag}"
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


#: The three lifecycle moments at which the reserved listing is regenerated
#: (REQ-PLAN-081(b), plan-056 Issue 2.3). Three rather than one because the three bracket
#: the phases that CREATE members: triage and `references/` land by intake; `scripts/` and
#: `findings/` by execute-start; `plan-retrospective.md` and `reviews/` by close.
_REINDEX_STATUSES: frozenset[str] = frozenset({"approved", "executing", "complete"})


def _reindex_bundle_listing(plan_dir: Path) -> dict:
    """Regenerate the bundle's reserved listing, preserving author prose.

    REQ-PLAN-081(b). `reindex_write`, NEVER `seed_index`: regeneration must preserve prose
    outside the listing run (REQ-OKF-072), and `seed_index` overwrites the file wholesale.

    FAIL-SOFT BY CONSTRUCTION. This is bookkeeping attached to a status transition, and a
    listing that could not be regenerated must never block the transition itself — the
    status write is the operator's actual intent and is already complete by the time this
    runs. A marker imbalance is reported, not raised: it is the one condition REQ-OKF-072
    calls unrecoverable, so refusing to touch the file is the correct response.
    """
    try:
        res = okf.reindex_write(plan_dir)
        return {"verdict": res.get("verdict"), "changes": res.get("changes", []),
                "warnings": res.get("warnings", [])}
    except okf.MarkerImbalanceError as exc:
        return {"verdict": "inconclusive", "reason": str(exc),
                "remediation": ("Unbalanced generated-region marker in index.md — "
                                "regenerating would discard prose unrecoverably. Balance "
                                "the markers, then run `plan_manager.py index-add "
                                "<plan-dir> . --regenerate`.")}
    except Exception as exc:  # noqa: BLE001 - bookkeeping must never block a transition
        return {"verdict": "inconclusive", "reason": f"reindex failed: {exc}"}


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
    `executing`, `reconciling`, `complete`, `abandoned`. `ready-for-approval` is the
    pre-approval gate state (set at the end of PLAN once `ready-check` is green) and is
    **not** execute-eligible — only `approved` (with a fresh fingerprint) is; execute
    eligibility keys on the fingerprint, never on a `status == "approved"` literal.
    `abandoned` is the terminal state for a plan deliberately stopped: also not
    execute-eligible, and deliberately not *parked*.

    **An unrecognised status WARNS on stderr and still exits 0** (REQ-CLI-026, #208). Free-form
    is retained on purpose — refusing the write would strand a plan whose operator has a reason
    this vocabulary does not yet cover, which is the failure mode #208 was filed about. The
    defect was the SILENCE, not the permissiveness: the write was accepted with no signal at
    all, so an invented status looked exactly like a supported one.
    """
    plan_md = Path(plan_dir) / "plan.md"
    if not plan_md.exists():
        click.echo("ERROR: plan.md not found", err=True)
        sys.exit(1)

    # --- REQ-CLI-026: WARN on an unrecognised status. stderr only, exit 0 -------------
    # STDERR ONLY is what keeps the verb composable: `--json` consumers parse stdout, and a
    # warning there would corrupt every one of them.
    #
    # EXIT 0 IS THE REQUIREMENT, NOT AN OMISSION. `test_update_status_gate.py` asserts exit 0
    # for every non-`approved` status, so a non-zero here would flip a passing assertion on
    # deliberate behaviour — and refusing the write recreates the stranding #208 is about.
    if status not in PLAN_STATUS_VALUES:
        click.echo(
            f"WARNING: `{status}` is not a recognised plan status.\n"
            f"  recognised: {' | '.join(PLAN_STATUS_VALUES)}\n"
            f"  The status HAS been written. Three known consequences:\n"
            f"    1. `list`'s status filters will not match it, so the plan is invisible to\n"
            f"       them (including the parked and abandoned tags).\n"
            f"    2. `_is_parked` will not classify it, so no land-the-plane nudge fires.\n"
            f"    3. `doc_lint`'s STATUS_SEVERITY treats a present-but-unrecognised status\n"
            f"       FAIL-CLOSED (REQ-DATA-072), so this bundle's `W` findings become `E`.\n"
            f"  If you meant 'approved but deliberately not executing', that is `abandoned`.",
            err=True,
        )

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

    # LIFECYCLE REGENERATION (REQ-PLAN-081(b)). `seed_index` runs ONCE, at `init`, so every
    # member the bundle grows afterwards was unlisted forever — and measured at scoping,
    # NOTHING ever regenerated it: `reindex` appeared in no CHANGE-VALIDATION row, no CI
    # step, and no call site here.
    reindex_result = None
    if status in _REINDEX_STATUSES:
        reindex_result = _reindex_bundle_listing(Path(plan_dir))

    click.echo(json.dumps({
        "status": status, "date": today, "log_entry": log_entry,
        "appended": not already, "deduped": already,
        "reindex": reindex_result,
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


@cli.command("index-add")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.argument("path")
@click.argument("description", required=False, default=None)
@click.option("--regenerate", is_flag=True,
              help="Instead of adding one entry, regenerate the whole listing (reindex --write).")
@click.option("--check", is_flag=True,
              help="With --regenerate: report drift without writing (reindex --check).")
@click.option("--json", "as_json", is_flag=True, help="Emit a JSON verdict.")
def index_add(plan_dir: str, path: str, description: str | None,
              regenerate: bool, check: bool, as_json: bool):
    """Add one entry to a bundle's reserved `index.md`, or regenerate the listing.

    REQ-PLAN-081(c). This is a NEW PUBLIC SURFACE, and it exists because index
    regeneration was measured **unreachable from the CLI**: `seed_index` is callable only
    from `init`, so an operator who noticed index drift had no supported repair short of
    editing `index.md` by hand — which is how the nine drifting bundles came to drift.

    `--regenerate` routes to the engine's `reindex_write`, never to `seed_index`:
    regeneration must PRESERVE AUTHOR PROSE (REQ-OKF-072), and `seed_index` overwrites the
    file wholesale.
    """
    pdir = Path(plan_dir)
    if regenerate:
        try:
            res = (okf.reindex_check(pdir) if check
                   else okf.reindex_write(pdir))
        except okf.MarkerImbalanceError as exc:
            out = {"verdict": "inconclusive", "reason": str(exc),
                   "remediation": ("An unbalanced generated-region marker leaves the region "
                                   "unbounded; regenerating would discard prose "
                                   "unrecoverably. Balance the markers, then re-run.")}
            click.echo(json.dumps(out, indent=1))
            sys.exit(okf.REINDEX_EXIT["inconclusive"])
        click.echo(json.dumps(res, indent=1))
        sys.exit(res.get("exit", 0))

    index = pdir / "index.md"
    if not index.exists():
        click.echo(json.dumps({"verdict": "inconclusive", "plan_dir": plan_dir,
                               "reason": f"no reserved index.md under {plan_dir}",
                               "remediation": "Run `/yf-okf migrate` or re-seed the bundle."},
                              indent=1))
        sys.exit(2)
    target = pdir / path.rstrip("/")
    if not target.exists():
        # A LISTING MEMBER MUST EXIST. Listing something absent asserts a fact that is false
        # in every clone, and generates the `empty-dir`/`ghost` drift `reindex` reports.
        click.echo(json.dumps({"verdict": "fail", "plan_dir": plan_dir, "path": path,
                               "reason": f"{path} does not exist in the bundle",
                               "remediation": "Create the member first; an index never "
                                              "asserts a path that is not there."}, indent=1))
        sys.exit(1)
    before = index.read_text(encoding="utf-8")
    if f"]({path})" in before:
        click.echo(json.dumps({"verdict": "pass", "plan_dir": plan_dir, "path": path,
                               "added": False, "reason": "already listed (idempotent)"},
                              indent=1))
        sys.exit(0)
    okf.add_index_entry(pdir, path, description or "")
    click.echo(json.dumps({"verdict": "pass", "plan_dir": plan_dir, "path": path,
                           "added": True,
                           "description": (description or None)}, indent=1))
    sys.exit(0)


@cli.command("clear-epic")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("-m", "--reason", default=None, help="Why the pointer is being cleared.")
@click.option("--force", is_flag=True, help="Clear even on a `present` or `unknown` state.")
@click.option("--json", "as_json", is_flag=True, help="Emit the verdict as JSON.")
def clear_epic(plan_dir: str, reason: str | None, force: bool, as_json: bool):
    """Clear a plan's recorded epic pointer (REQ-CLI-027, plan-053 / #207).

    Removes BOTH dual-written surfaces, KEEPS the `intake: epic <id> poured` history bullet,
    and APPENDS a `pointer cleared` bullet — the record of what was poured survives the
    clearing of the pointer to it. Both bullets are inert: neither advances `status`, and
    neither matches the `review:` or `scoping:` audit regexes, so REQ-PORT-006's
    count-equality is untouched.

    REFUSES without `--force` on `present` (clearing a live pointer strands real work) and on
    `unknown` (that same act, performed blind).
    """
    pdir = Path(plan_dir)
    result = _clear_epic(pdir, force=force, reason=reason)
    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"{result['verdict']}: {result['reason']}")
        if result.get("metadata_fallback_remains"):
            click.echo("  ⚠ metadata_fallback_remains: the epic bead still carries a matching "
                       "`metadata.plan_dir`, so `resume-scan` will STILL resolve this epic. "
                       "Clearing plan.md alone does NOT reopen the pour path.")
    sys.exit(0 if result["verdict"] in ("cleared", "noop") else 3)


def _clear_epic(plan_dir: Path, *, force: bool = False, reason: str | None = None) -> dict:
    """Implementation of `clear-epic`, factored out so tests drive it without Click."""
    scan = _resume_scan(plan_dir)
    epic_id = scan.get("epic_id")
    state = scan.get("epic_state", "unknown")

    out: dict = {
        "plan_dir": str(plan_dir),
        "epic_id": epic_id,
        "epic_state": state,
        "cleared": False,
        "verdict": "noop",
        "reason": "",
        "log_entry": None,
        "metadata_fallback_remains": False,
        "forced": bool(force),
    }

    # REFUSAL comes BEFORE the no-op check on purpose: a `present` epic with a recorded
    # pointer must refuse, not report "nothing to do".
    if state in ("present", "unknown") and not force:
        out["verdict"] = "refused"
        out["reason"] = (
            f"epic_state is `{state}` — refusing without --force. "
            + ("Clearing a LIVE pointer strands real work." if state == "present"
               else "The state could not be determined; clearing now is that same act "
                    "performed blind, and `unknown` is NOT a synonym for `gone`.")
        )
        return out

    if not _clear_plan_fields(plan_dir, ("epic",)):
        out["reason"] = "no epic pointer recorded in plan.md — nothing to clear."
        return out

    out["cleared"] = True
    out["verdict"] = "cleared"
    bullet = "pointer cleared" + (f": {reason}" if reason else "")
    okf.append_log(plan_dir, bullet, date=datetime.now().strftime("%Y-%m-%d"))
    out["log_entry"] = f"- {bullet}"
    out["reason"] = (
        f"removed the frontmatter `epic:` key and the `**Epic:**` line"
        + (f" (was {epic_id})" if epic_id else "")
    )

    # R6, MEASURED: clearing the two plan.md surfaces does NOT on its own reopen the pour
    # path. `_resume_scan` falls back to a bead whose `metadata.plan_dir` matches, so a
    # SURVIVING epic bead is still found. A verb that appears to succeed and changes nothing
    # is the silent-success class this plan exists to close, so the residual is REPORTED.
    after = _resume_scan(plan_dir)
    if after.get("epic_id"):
        out["metadata_fallback_remains"] = True
        out["reason"] += (
            f"; but `resume-scan` STILL resolves {after['epic_id']} via the "
            f"`metadata.plan_dir` fallback — the clear will not reopen the pour path while "
            f"that bead survives."
        )
    return out


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


# ---------------------------------------------------------------------------
# The SHARED per-disposition requirement table (REQ-CLI-025 / #178).
#
# ONE table, TWO readers: `grant` (what the operator must be asked to authorize) and
# `_verify_row` (what reconciliation must find upstream). Before this they were two separate
# PROSE derivations of the same rule, and plan-048 HALTED ITS OWN RECONCILE on the gap: the
# grant was hand-derived from the Upstream Issues table, `#172`'s close was missed, and the
# omission surfaced only at `verify-reconcile` — a late halt after the outward-facing writes
# had already begun. The amendment that repaired it is still in
# `docs/plans/plan-048-james-dixson-ed68a5/assets/upstream-authorization.txt`, and it says so:
# *"Its omission from the original list was an oversight in THIS FILE."*
#
# WHY THIS IS A NEW TABLE AND NOT `_verify_row` CALLED DIRECTLY. That was the original design
# and it was REFUTED by measurement (pass-3 C12): `_verify_row` returns
# `{detail, disposition, issue, verdict}` with **no `required_action`**, is **network-bound**
# (a `gh issue view` per row), and returns `fail: "unrecognised literal"` when handed an
# `exclude` row directly — for a literal that IS in the frozenset. A generator cannot be built
# on it. Extracting the requirement is what makes one source servable to both.
#
# THE READ IS ASSERTED BEHAVIORALLY, not structurally (SC8): mutate one entry in a throwaway
# copy and BOTH verdicts must change. An existence check or an import check passes on a table
# that is present and ignored — pass-3 C12 measured the import form as undetecting.
# ---------------------------------------------------------------------------

#: Per-disposition requirement. Keyed by the `UPSTREAM_DISPOSITIONS` literals — every literal
#: has exactly one entry, and `test_upstream_requirements.py` asserts that set equality, so a
#: disposition added to the frozenset without an entry fails loudly rather than falling through
#: to the unrecognised-literal branch.
#:
#: Fields:
#:   end_state        the upstream state reconciliation must find: "CLOSED" | "OPEN" | None
#:   state_reason     a required `stateReason`, or None
#:   requires_mention must a comment mention the plan id?
#:   extra_actions    actions NOT derivable from the fields above (only the tracker filing)
#:   report_only      True -> `_verify_row` returns `inconclusive`, never pass/fail
#:   why              the reason, carried WITH the rule so the two cannot drift apart
UPSTREAM_REQUIREMENTS: dict[str, dict] = {
    "include": {
        "end_state": "CLOSED", "state_reason": None, "requires_mention": True,
        "report_only": False,
        "why": "the plan claims to have delivered it, so it must end CLOSED and the closure "
               "must be attributed — an unattributed close is an unproven reconciliation",
    },
    "partial": {
        "end_state": "OPEN", "state_reason": None, "requires_mention": True,
        "report_only": False,
        "why": "the remaining half is still real work, so the issue stays OPEN — but what "
               "THIS plan did must be recorded upstream or the deferred half is invisible",
    },
    "supersede": {
        "end_state": "CLOSED", "state_reason": "NOT_PLANNED", "requires_mention": False,
        "report_only": False,
        "why": "superseded work is closed as NOT_PLANNED, which is how it stays "
               "distinguishable from work that was actually done",
    },
    "deferred": {
        "end_state": "OPEN", "state_reason": None, "requires_mention": False,
        "report_only": False,
        "why": "a deferral is a NON-ACTION: the row records a scoping decision taken in THIS "
               "plan, not work done on that issue, so there is nothing to attribute and no "
               "mention is required (REQ-PLAN-074 as amended by plan-048 Issue 0.2, D-7). "
               "The not-OPEN direction is still a real assertion: an issue the plan declared "
               "it would return to, closed by reconcile time, CONTRADICTS the disposition",
    },
    "tracker": {
        "end_state": None, "state_reason": None, "requires_mention": False,
        "extra_actions": ["file-tracker"], "report_only": True,
        "why": "the coarse tracker is closed by the land-the-plane sweep, not by "
               "reconciliation, so it carries no end-state contract in EITHER direction. "
               "Deliberately NOT collapsed into `deferred`: that is report-only because "
               "there is nothing to attribute, this is report-only because reconcile is not "
               "the thing that closes it. Neither may absorb the other",
    },
    "exclude": {
        "end_state": None, "state_reason": None, "requires_mention": False,
        "report_only": False,
        "why": "out of scope — no upstream action at all. `verify_reconcile` filters these "
               "out before `_verify_row` ever sees one (REQ-CLI-018), which is why handing "
               "`_verify_row` an `exclude` row directly returns `fail` for a literal that IS "
               "recognised. That filter is UNCHANGED by plan-050",
    },
}

def _verify_row(row: dict, plan_id: str) -> dict:
    """Verify one Upstream Issues row. Returns {issue, disposition, verdict, detail}.

    READS `UPSTREAM_REQUIREMENTS` (REQ-CLI-025 / #178). Every branch below is derived from
    that table's fields rather than restated here, so `grant` and this function cannot
    disagree about what a disposition requires. SC8 asserts the read BEHAVIORALLY: mutate one
    entry in a throwaway copy and both verdicts must change.
    """
    number, disp = row["issue"], row["disposition"]

    # An UNRECOGNISED disposition is `fail`, not `inconclusive` (plan-048 Issue 3.4), and is
    # decided BEFORE the network call: every recognised literal has a table entry, and the
    # producer surfaces offer exactly those, so anything else is a TYPO in the table. A
    # fail-loud step must not silently pass a typo. This is also what makes R2c's
    # normalization load-bearing: before it, a bolded `**partial**` reached here as an
    # unrecognised literal.
    req = UPSTREAM_REQUIREMENTS.get(disp)
    if req is None:
        return {"issue": number, "disposition": disp, "verdict": "fail",
                "detail": f"#{number} has disposition {disp!r}, which is not one of "
                          + "|".join(sorted(UPSTREAM_REQUIREMENTS))
                          + " — an unrecognised literal is a typo in the table, not a valid "
                            "state"}

    payload, err = _gh_issue_view(number)
    if err is not None:
        return {"issue": number, "disposition": disp, "verdict": "inconclusive",
                "detail": f"could not read #{number}: {err}"}

    state = (payload.get("state") or "").upper()
    reason = (payload.get("stateReason") or "").upper()
    mentioned = _mentions_plan_id(payload, plan_id)

    if req["report_only"]:
        # INCONCLUSIVE BY CONSTRUCTION (spec/cli.md REQ-CLI-018).
        return {"issue": number, "disposition": disp, "verdict": "inconclusive",
                "detail": f"#{number} is report-only: {req['why']}"}

    want_state = req["end_state"]
    if want_state is not None and state != want_state:
        return {"issue": number, "disposition": disp, "verdict": "fail",
                "detail": f"#{number} is {state}; a `{disp}` row must be {want_state} — "
                          f"{req['why']}"}

    want_reason = req["state_reason"]
    if want_reason is not None and reason != want_reason:
        return {"issue": number, "disposition": disp, "verdict": "fail",
                "detail": f"#{number} is {state}/{reason or 'no stateReason'}; a `{disp}` "
                          f"row must be {want_state} as {want_reason}"}

    if req["requires_mention"] and not mentioned:
        return {"issue": number, "disposition": disp, "verdict": "fail",
                "detail": f"#{number} is {state} but no comment mentions {plan_id} — "
                          f"{req['why']}"}

    detail = f"#{number} {state}"
    if want_reason:
        detail += f" as {want_reason}"
    if req["requires_mention"]:
        detail += f" with a {plan_id} mention"
    elif want_state is not None:
        detail += f"; `{disp}` requires no {plan_id} mention"
    return {"issue": number, "disposition": disp, "verdict": "pass", "detail": detail}


def _grant_actions_for(req: dict) -> list[str]:
    """The outward-facing actions a disposition requires, DERIVED from its own fields.

    Derived rather than declared, and that is not tidiness — `ctl-178-grant`'s contrast arm
    MEASURED the two halves diverging on the first run: `supersede` declared a `comment`
    action while its own `requires_mention` is `False`, so the generator demanded an
    authorization clause for something reconciliation would never check. A grant that asks
    for MORE than the verifier requires is as wrong as one that asks for less; it just fails
    in the direction that looks conservative.

    Only the tracker filing is not derivable — a `tracker` row's action is to CREATE the
    issue, which no end-state field can express — so it is carried as `extra_actions`.
    """
    acts: list[str] = []
    if req["requires_mention"]:
        acts.append("comment")
    if req["end_state"] == "CLOSED":
        acts.append("close-not-planned" if req["state_reason"] == "NOT_PLANNED" else "close")
    acts.extend(req.get("extra_actions", []))
    return acts


_GRANT_ACTION_TEMPLATES = {
    "comment": ("gh issue comment {n} --body '<what {plan} did for #{n}>'",
                "post a comment naming the full plan id"),
    "close": ("gh issue close {n}",
              "CLOSE the issue"),
    "close-not-planned": ("gh issue close {n} --reason 'not planned'",
                          "CLOSE the issue as NOT_PLANNED"),
    "file-tracker": ("gh issue create --title '{plan} execution tracking' --body '<links the plan folder and its epic>'",
                     "FILE the coarse tracker (or confirm it exists)"),
}


def _grant_proposal(plan_md_text: str, plan_id: str) -> dict:
    """The upstream-write proposal, DERIVED from the Upstream Issues table.

    Reads `UPSTREAM_REQUIREMENTS` — the same table `_verify_row` reads — so what the operator
    is asked to authorize and what reconciliation will later require are one derivation, not
    two. Local only: no network, so it is runnable before any `gh` call and before any
    authorization exists.
    """
    rows = parse_upstream_rows(plan_md_text)
    items, unrecognised = [], []
    for r in rows:
        disp = r["disposition"]
        req = UPSTREAM_REQUIREMENTS.get(disp)
        if req is None:
            unrecognised.append({"issue": r["issue"], "disposition": disp})
            continue
        actions = []
        for kind in _grant_actions_for(req):
            cmd, human = _GRANT_ACTION_TEMPLATES[kind]
            actions.append({
                "kind": kind,
                "human": human,
                "command": cmd.format(n=r["issue"], plan=plan_id),
            })
        items.append({
            "issue": r["issue"], "disposition": disp,
            "resolved_by": r.get("resolved_by") or "",
            "actions": actions,
            "end_state": req["end_state"], "state_reason": req["state_reason"],
            "requires_mention": req["requires_mention"],
            "why": req["why"],
        })
    return {"plan_id": plan_id, "rows": items, "unrecognised": unrecognised,
            "actionable": [i for i in items if i["actions"]]}


def _grant_coverage(proposal: dict, text: str) -> list[dict]:
    """Which of the proposal's required actions an authorization text does NOT cover.

    THE ROUND-TRIP CHECK, and the reason this verb exists. plan-048's grant was hand-derived
    from the same table this generator reads, `#172`'s close was missed, and the omission
    surfaced only at `verify-reconcile` — after the outward-facing writes had begun. The
    amendment repairing it is still on disk and states the cause: *"an oversight in THIS
    FILE."*

    Coverage is judged per ACTION, not per issue: an `include` row needs BOTH a comment and a
    close, and plan-048's omission was exactly a close on an issue the grant already
    mentioned. A per-issue check would have passed it.
    """
    lowered = text.lower()
    uncovered = []
    for item in proposal["rows"]:
        n = item["issue"]
        # A `file-tracker` action is judged over the WHOLE text, never scoped to the issue
        # number. The fixture's contrast arm caught this too: a grant written BEFORE the
        # tracker exists CANNOT name its number, because the number is the thing being
        # created. plan-048's real grant authorizes it as item 1, by plan id.
        tracker_acts = [a for a in item["actions"] if a["kind"] == "file-tracker"]
        if tracker_acts:
            if not any(w in lowered for w in ("tracker", "gh issue create")):
                uncovered.append({**tracker_acts[0], "issue": n,
                                  "disposition": item["disposition"],
                                  "reason": "no clause authorizes filing the coarse tracker"})
            continue
        # The issue must be named at all. `#172` and a bare `172` both count — an
        # authorization is prose, and demanding one spelling would manufacture false gaps.
        named = (f"#{n}" in text) or re.search(rf"(?<![\w#]){re.escape(str(n))}(?![\w])", text)
        for act in item["actions"]:
            kind = act["kind"]
            if not named:
                uncovered.append({**act, "issue": n, "disposition": item["disposition"],
                                  "reason": f"#{n} is not named in the authorization at all"})
                continue
            # Scope the search to the sentence(s) naming this issue, so a `close` authorized
            # for one issue cannot silently cover another.
            window = " ".join(
                ln for ln in lowered.splitlines()
                if f"#{n}" in ln or re.search(rf"(?<![\w#]){re.escape(str(n))}(?![\w])", ln))
            if kind in ("close", "close-not-planned"):
                ok = "clos" in window
                if kind == "close-not-planned":
                    ok = ok and ("not planned" in window or "not_planned" in window
                                 or "supersede" in window)
            elif kind == "comment":
                ok = "comment" in window or "post" in window
            elif kind == "file-tracker":
                ok = "file" in window or "creat" in window or "tracker" in window
            else:
                ok = False
            if not ok:
                uncovered.append({**act, "issue": n, "disposition": item["disposition"],
                                  "reason": f"#{n} is named, but no clause authorizes: "
                                            f"{act['human']}"})
    return uncovered


@cli.command("grant")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--check", "check_path", type=click.Path(),
              help="Reconcile an EXISTING authorization file against the proposal and report "
                   "every required action it does not cover. This is the round-trip check.")
@click.option("--json-output", "--json", "as_json", is_flag=True,
              help="Emit the structured verdict (default is also JSON).")
def grant(plan_dir: str, check_path: str | None, as_json: bool):
    """Generate the upstream-write authorization PROPOSAL from the plan's own table.

    REQ-CLI-025 / #178. It emits a proposal and NOTHING ELSE: it never writes the
    authorization file, never performs an upstream write, and needs no network — so it runs
    before any `gh` call and before any authorization exists.

    WHY THIS EXISTS. plan-048 HALTED ITS OWN RECONCILE on a hand-derived grant that missed
    `#172`'s close. The amendment repairing it is still in that plan's
    `assets/upstream-authorization.txt` and names the cause: *"Its omission from the original
    list was an oversight in THIS FILE, not a decision to withhold."* plan-049 avoided the
    same defect only because the operator derived the grant by hand a second time.

    The generator and `_verify_row` read ONE table (`UPSTREAM_REQUIREMENTS`), so what the
    operator is asked to authorize and what reconciliation will later require cannot drift.
    Two prose derivations of the same rule is what produced the gap.

    With `--check <file>`, additionally reconciles an existing authorization against the
    proposal and fails on any uncovered action. Coverage is judged PER ACTION, not per issue:
    plan-048's omission was a close on an issue the grant already mentioned, which a per-issue
    check would have passed.
    """
    pdir = Path(plan_dir)
    plan_md = pdir / "plan.md"
    if not plan_md.exists():
        click.echo(json.dumps({
            "verdict": "fail", "passed": False,
            "reason": f"plan.md not found under {plan_dir}",
            "remediation": "Check the plan_dir argument.",
        }))
        sys.exit(1)

    plan_id = _plan_id_from_dir(pdir)
    proposal = _grant_proposal(plan_md.read_text(), plan_id)

    if proposal["unrecognised"]:
        bad = ", ".join(f"#{u['issue']}={u['disposition']!r}"
                        for u in proposal["unrecognised"])
        click.echo(json.dumps({
            "verdict": "fail", "passed": False, "plan_id": plan_id,
            "proposal": proposal,
            "reason": f"unrecognised disposition(s) in the Upstream Issues table: {bad}",
            "remediation": "Every Disposition cell must be one of "
                           + "|".join(sorted(UPSTREAM_REQUIREMENTS))
                           + ". A generator that silently skipped an unrecognised literal "
                             "would omit exactly the row nobody checked.",
        }, indent=2))
        sys.exit(1)

    if check_path is None:
        click.echo(json.dumps({
            "verdict": "pass", "passed": True, "plan_id": plan_id,
            "proposal": proposal,
            "reason": f"{len(proposal['actionable'])} of {len(proposal['rows'])} upstream "
                      "row(s) require an outward-facing action",
            "remediation": None,
        }, indent=2))
        return

    cpath = Path(check_path)
    if not cpath.exists():
        click.echo(json.dumps({
            "verdict": "fail", "passed": False, "plan_id": plan_id,
            "proposal": proposal, "uncovered": [],
            "reason": f"no authorization file at {check_path}",
            "remediation": "Present the proposal above to the operator and record their "
                           "explicit authorization before any upstream write.",
        }, indent=2))
        sys.exit(1)

    uncovered = _grant_coverage(proposal, cpath.read_text(encoding="utf-8", errors="replace"))
    if uncovered:
        click.echo(json.dumps({
            "verdict": "fail", "passed": False, "plan_id": plan_id,
            "proposal": proposal, "uncovered": uncovered,
            "reason": f"{len(uncovered)} required upstream action(s) are NOT covered by "
                      f"{check_path}",
            "remediation": "Do NOT proceed. Either extend the authorization to cover each "
                           "action below, or change the row's disposition — those are the "
                           "only two consistent states. This is the exact check plan-048 "
                           "lacked when it halted its own reconcile on an omitted close:\n"
                           + "\n".join(f"  #{u['issue']} ({u['disposition']}): {u['human']}"
                                        f"\n    {u['command']}" for u in uncovered),
        }, indent=2))
        sys.exit(1)

    click.echo(json.dumps({
        "verdict": "pass", "passed": True, "plan_id": plan_id,
        "proposal": proposal, "uncovered": [],
        "reason": f"{check_path} covers all {len(proposal['actionable'])} actionable row(s)",
        "remediation": None,
    }, indent=2))


# --- ownership-report — single-writer ownership over declared paths (Issue 1.5) --------
#
# REPORT-ONLY, PERMANENTLY (R1). It is never a gate and never blocks anything, because the
# measurement it rests on is PARTIALLY CIRCULAR and the report says so in its own output: the
# lever was derived from this corpus, and `ownership-report` is itself generated by one of the
# five `plan_manager.py` writers it flags. A circular measurement is worth SURFACING and is
# not worth ENFORCING.
#
# SIGNALS INCLUDED — and the two that are DELIBERATELY EXCLUDED, with the measurement:
#
#   S1  shared declared paths          INCLUDED — p = 3.4e-11, the strongest signal measured
#   S3  DRIFT-CHECK.md edges           INCLUDED — a declared docs<->impl edge is a real
#                                      co-writing relationship
#   S2  CHANGE-VALIDATION.md rows      EXCLUDED — p = 0.85. Indistinguishable from noise; a
#                                      recipe row groups files by WHO RUNS THEM, not by who
#                                      writes them, so two issues sharing a row need not
#                                      share a writer at all.
#   S4  shared upstream refs           EXCLUDED — fired 0 times across the whole corpus. A
#                                      signal with no positives contributes no information
#                                      and cannot be validated in either direction.
#
# THE INCONCLUSIVE FLOOR IS A NUMBER: 80% path coverage. Below it the pairwise measurement
# has too thin a denominator to mean anything, and the honest output is "I could not tell".
# Reporting "orthogonal" on no input is the silent-green class in its ownership form — a
# conclusion drawn from an empty set reads exactly like a clean bill of health.
OWNERSHIP_COVERAGE_FLOOR = 80


def _load_plan_extract():
    """Load the sibling `plan_extract` module, vendored copy first.

    Same resolution order as `_audit_plan`'s doc_lint load: the co-resident vendored copy,
    then the canonical `_shared/` one. A skill deployed outside this repo has only the former.
    """
    import importlib.util as _ilu

    here = Path(__file__).resolve().parent
    for cand in (here / "plan_extract.py",
                 here.parent.parent.parent / "_shared" / "plan_extract.py"):
        if cand.is_file():
            spec = _ilu.spec_from_file_location("plan_extract_for_ownership", cand)
            mod = _ilu.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    raise FileNotFoundError("plan_extract.py not found beside plan_manager.py or in _shared/")


def _run_plan_extract(plan_dir: Path) -> dict:
    """Extract one plan bundle to the dict `plan_extract` emits."""
    mod = _load_plan_extract()
    return mod.extract(plan_dir / "plan.md")


def _ownership_pairs(issues: list[dict]) -> tuple[list[dict], dict]:
    """All unordered issue pairs sharing >= 1 declared path (S1). Pure."""
    by_path: dict[str, list[str]] = {}
    for i in issues:
        for t in i.get("touches") or []:
            by_path.setdefault(t, []).append(i["id"])
    shared = {p: sorted(set(ids)) for p, ids in by_path.items() if len(set(ids)) > 1}
    pairs: dict[tuple[str, str], list[str]] = {}
    for path, ids in shared.items():
        for a_i in range(len(ids)):
            for b_i in range(a_i + 1, len(ids)):
                pairs.setdefault((ids[a_i], ids[b_i]), []).append(path)
    out = [{"a": a, "b": b, "paths": sorted(ps)} for (a, b), ps in sorted(pairs.items())]
    return out, shared


@cli.command("ownership-report")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "json_output", is_flag=True,
              help="Emit the structured report (default is also JSON).")
def ownership_report(plan_dir: str, json_output: bool):
    """REPORT-ONLY single-writer ownership over a plan's declared paths (REQ-DATA-071).

    Never a gate. Returns INCONCLUSIVE below the stated 80% path-coverage floor, and never
    reports "orthogonal" on no input.
    """
    pdir = Path(plan_dir)
    plan_md = pdir / "plan.md"
    base = {
        "report_only": True,
        "coverage_floor": OWNERSHIP_COVERAGE_FLOOR,
        "signals_included": ["shared-declared-paths", "drift-check-edges"],
        "signals_excluded": {
            "change-validation-rows": "p=0.85, indistinguishable from noise",
            "shared-upstream-refs": "fired 0 times across the corpus",
        },
        "circularity": (
            "PARTIALLY CIRCULAR: the ownership lever was derived from this corpus, and this "
            "report is itself generated by one of the plan_manager.py writers it flags. "
            "Surfaced deliberately; never enforced."
        ),
    }

    if not plan_md.exists():
        click.echo(json.dumps({**base, "verdict": "INCONCLUSIVE",
                               "reason": f"plan.md not found under {plan_dir}"}))
        sys.exit(0)

    try:
        docs = _run_plan_extract(pdir)
    except Exception as e:  # noqa: BLE001 — any extractor failure is INCONCLUSIVE, not a finding
        click.echo(json.dumps({**base, "verdict": "INCONCLUSIVE",
                               "reason": f"plan_extract could not read the plan: {e}"}))
        sys.exit(0)

    issues = docs.get("issues") or []
    if not issues:
        click.echo(json.dumps({**base, "verdict": "INCONCLUSIVE", "coverage": 0.0,
                               "reason": "the plan declares no issues"}))
        sys.exit(0)

    declared = [i for i in issues if i.get("touches")]
    coverage = round(100.0 * len(declared) / len(issues), 1)

    if coverage < OWNERSHIP_COVERAGE_FLOOR:
        click.echo(json.dumps({
            **base, "verdict": "INCONCLUSIVE", "coverage": coverage,
            "issues": len(issues), "issues_declaring": len(declared),
            "reason": (f"path coverage is {coverage}%, below the {OWNERSHIP_COVERAGE_FLOOR}% "
                       f"floor — the pairwise measurement has too thin a denominator to "
                       f"mean anything, so the honest answer is that it could not be told"),
        }))
        sys.exit(0)

    pairs, shared = _ownership_pairs(issues)
    click.echo(json.dumps({
        **base, "verdict": "REPORT", "coverage": coverage,
        "issues": len(issues), "issues_declaring": len(declared),
        "shared_paths": {p: ids for p, ids in sorted(shared.items())},
        "multi_writer_paths": len(shared),
        "pairs": pairs,
        "reason": (f"{len(shared)} declared path(s) have more than one writer across "
                   f"{len(pairs)} issue pair(s); coverage {coverage}%"),
    }, indent=1))
    sys.exit(0)


# --- recheck-criteria — completion-time re-check of Success Criteria (REQ-PLAN-080) ----
#
# THE TRIGGER, STATED AS A MEASUREMENT: plan-051 shipped `SC4b` measured green at the issue
# that discharged it and FALSE two epics later — a file added downstream matched its pattern
# and nothing re-ran the check. It was caught by an operator re-measurement, not by anything
# the plan shipped. A criterion is only as good as the last time something re-ran it.
#
# `YF_RECHECK_DEPTH` IS THE LOAD-BEARING GUARD. The name-check below is BEST-EFFORT and scans
# THE EXECUTED COMMAND STRING ONLY, never the criterion row — a criterion row may legitimately
# *discuss* this verb, and in plan-052 every clause routes through `gate-run.sh` so no clause
# contains the literal `recheck-criteria` at all. A name-check over rows would therefore be
# both unnecessary and wrong.
#
# THE DEPTH RULE IS ABOUT WHAT EACH DEPTH MAY DO:
#     depth 0 and depth 1 EVALUATE;  depth 2 returns exit 2 (INCONCLUSIVE) WITHOUT EXECUTING.
# Depth 1 must evaluate because a criterion's command routes through the plan's own harness
# and therefore runs one level down when this verb is invoked from the §6.4 close chain. A
# guard that refused at depth 1 would make every fixture-driven control valid standalone and
# INCONCLUSIVE under the chain — the exact state this plan exists to prevent.
RECHECK_MAX_DEPTH = 2

#: REQ-DATA-070's clause grammar, duplicated here rather than imported: `doc_lint` owns the
#: AUTHORING-time shape check, this owns EXECUTION. They read the same grammar for different
#: purposes, and coupling the close chain to the linter would make a linter outage a
#: completion outage.
_RECHECK_CLAUSE = re.compile(
    r"`(?P<cmd>.+)`\s*(?:\u2192|->)\s*exit\s+(?P<want>0|1|2|non-zero)\s*\Z", re.S)
_RECHECK_MANUAL = re.compile(r"\Amanual:\s*\S", re.S)


def _repo_root_for(plan_dir: Path) -> Path:
    """The repo root a criterion's command should run from.

    REQ-DATA-070: every command runs FROM THE REPO ROOT unless its clause says otherwise. A
    plan bundle can sit at `docs/plans/<id>/` or `Incubator/<slug>/plans/<id>/`, so the depth
    varies — `git rev-parse` is asked first and the walk is the fallback.
    """
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             cwd=str(plan_dir), capture_output=True, text=True, timeout=5)
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    for d in [plan_dir.resolve(), *plan_dir.resolve().parents]:
        if (d / ".git").exists():
            return d
    return plan_dir.resolve()


def _recheck_unescape(cell: str) -> str:
    """Undo GFM table escaping before execution (REQ-DATA-070).

    A Verification cell lives inside a GFM table, so a piped command is necessarily written
    `\\|`. Executing the raw cell runs a TRUNCATED command that means something else — risk R9.
    """
    return cell.replace("\\|", "|").replace("\\\\", "\\")


def _classify_criterion(cell: str) -> tuple[str, str | None, str | None]:
    """-> (kind, command, expected). kind in {clause, manual, prose}."""
    c = _recheck_unescape(cell).strip()
    if _RECHECK_MANUAL.match(c):
        return "manual", None, None
    m = _RECHECK_CLAUSE.search(c)
    if m:
        return "clause", m.group("cmd").strip(), m.group("want")
    return "prose", None, None


def _recheck_holds(rc: int, want: str) -> bool:
    if want == "non-zero":
        return rc != 0
    return rc == int(want)


@cli.command("verify-beads")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--fixture", type=click.Path(), default=None,
              help="pinned JSON bead snapshot instead of live bd state")
@click.option("--json-output", "--json", "json_output", is_flag=True,
              help="Emit the structured verdict (default is also JSON).")
def verify_beads_cmd(plan_dir: str, fixture: str | None, json_output: bool):
    """Emit injection-time verify beads for `plan-execute` (#197, Issue 5.2).

    A thin wrapper over `verify_beads.py`. `plan-execute` declares ONE step and its real DAG
    is built from plan.md, so there is nothing for an aspect to weave over — this is the
    mechanism for that case, not the same mechanism applied twice.
    """
    engine = Path(__file__).resolve().parent / "verify_beads.py"
    if not engine.is_file():
        click.echo(json.dumps({"verdict": "INCONCLUSIVE",
                               "reason": f"verify_beads.py not found at {engine}"}))
        sys.exit(2)
    args = ["uv", "run", str(engine), "--plan", _plan_id_from_dir(Path(plan_dir)), "--json"]
    if fixture:
        args += ["--fixture", fixture]
    proc = subprocess.run(args, capture_output=True, text=True)
    click.echo(proc.stdout.strip() or proc.stderr.strip())
    sys.exit(proc.returncode)


@cli.command("gate-consistency")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "json_output", is_flag=True,
              help="Emit the structured verdict (default is also JSON).")
def gate_consistency_cmd(plan_dir: str, json_output: bool):
    """Check every capability gate against its own Blocks set (#113, Issue 4.2).

    A thin wrapper over `gate_consistency.py`, so the check is reachable through the same
    verb surface as the rest of the chain. Exit: 0 clean · 1 finding · 2 could not run.
    """
    engine = Path(__file__).resolve().parent / "gate_consistency.py"
    if not engine.is_file():
        click.echo(json.dumps({"verdict": "INCONCLUSIVE",
                               "reason": f"gate_consistency.py not found at {engine}"}))
        sys.exit(2)
    proc = subprocess.run(["uv", "run", str(engine), plan_dir, "--json"],
                          capture_output=True, text=True)
    click.echo(proc.stdout.strip() or proc.stderr.strip())
    sys.exit(proc.returncode)


@cli.command("recheck-criteria")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "json_output", is_flag=True,
              help="Emit the structured verdict (default is also JSON).")
@click.option("--timeout", default=300, show_default=True,
              help="Per-criterion command timeout, in seconds.")
@click.option("--advisory", is_flag=True,
              help="Report an unjudged class-A criterion without halting (REQ-PLAN-080).")
@click.option("--require-evaluated", "require_evaluated", default=None, type=float,
              help="Minimum evaluated/class-A fraction. Default 1.0 at the completion binding.")
def recheck_criteria(plan_dir: str, json_output: bool, timeout: int,
                     advisory: bool, require_evaluated: float | None):
    """Re-evaluate every clause-form Success Criterion at completion (REQ-PLAN-080).

    Exit: 0 every evaluated criterion holds · 1 at least one is FALSE, **or a class-A
    criterion went UNJUDGED at the completion binding** · 2 INCONCLUSIVE.

    The middle case is `HARNESS_INCOMPLETE` (plan-056 Issue 1.10, #265) — see the verdict
    block at the end of this function for why it is a THIRD verdict rather than a reuse of
    either neighbour.
    """
    depth = 0
    try:
        depth = int(os.environ.get("YF_RECHECK_DEPTH", "0"))
    except ValueError:
        depth = 0

    base = {"plan_dir": plan_dir, "depth": depth, "max_depth": RECHECK_MAX_DEPTH}

    # THE GUARD. At the limit we refuse WITHOUT EXECUTING anything.
    if depth >= RECHECK_MAX_DEPTH:
        click.echo(json.dumps({
            **base, "verdict": "INCONCLUSIVE", "severity": "warn",
            "class_a_fraction": 0.0, "evaluated_fraction": 0.0, "criteria": [],
            "reason": (f"YF_RECHECK_DEPTH={depth} has reached the limit of "
                       f"{RECHECK_MAX_DEPTH}; refusing WITHOUT executing any criterion"),
        }))
        sys.exit(2)

    pdir = Path(plan_dir)
    plan_md = pdir / "plan.md"
    if not plan_md.exists():
        click.echo(json.dumps({**base, "verdict": "INCONCLUSIVE", "severity": "warn",
                               "class_a_fraction": 0.0, "evaluated_fraction": 0.0,
                               "criteria": [],
                               "reason": f"plan.md not found under {plan_dir}"}))
        sys.exit(2)

    try:
        docs = _run_plan_extract(pdir)
        rows = docs.get("criteria") or []
    except Exception as e:  # noqa: BLE001
        click.echo(json.dumps({**base, "verdict": "INCONCLUSIVE", "severity": "warn",
                               "class_a_fraction": 0.0, "evaluated_fraction": 0.0,
                               "criteria": [],
                               "reason": f"plan_extract could not read the plan: {e}"}))
        sys.exit(2)

    if not rows:
        click.echo(json.dumps({**base, "verdict": "INCONCLUSIVE", "severity": "warn",
                               "class_a_fraction": 0.0, "evaluated_fraction": 0.0,
                               "criteria": [],
                               "reason": "the plan declares no Success Criteria table"}))
        sys.exit(2)

    child_env = dict(os.environ, YF_RECHECK_DEPTH=str(depth + 1))
    repo_root = _repo_root_for(pdir)

    results, class_a, evaluated, failed = [], 0, 0, []
    for r in rows:
        cid = r.get("id") or "?"
        kind, cmd, want = _classify_criterion(r.get("verification") or "")
        rec = {"id": cid, "kind": kind}
        if kind != "clause":
            rec["status"] = "not-evaluated"
            results.append(rec)
            continue
        class_a += 1
        rec["command"], rec["expected_exit"] = cmd, want

        # BEST-EFFORT name check — the EXECUTED COMMAND STRING ONLY, never the criterion row.
        if "recheck-criteria" in (cmd or ""):
            rec["status"] = "skipped-self-reference"
            results.append(rec)
            continue

        try:
            proc = subprocess.run(["bash", "-c", cmd], cwd=str(repo_root), env=child_env,
                                  capture_output=True, text=True, timeout=timeout)
            rc = proc.returncode
        except subprocess.TimeoutExpired:
            rec["status"] = "inconclusive"
            rec["detail"] = f"timed out after {timeout}s"
            results.append(rec)
            continue
        except OSError as e:
            rec["status"] = "inconclusive"
            rec["detail"] = f"could not execute: {e}"
            results.append(rec)
            continue

        rec["actual_exit"] = rc
        # 126/127 mean the INSTRUMENT could not run (not executable / not found). That is a
        # different claim from the criterion being false, so it is never counted as evaluated.
        if rc in (126, 127):
            rec["status"] = "inconclusive"
            rec["detail"] = "command not found or not executable"
            results.append(rec)
            continue

        evaluated += 1
        if _recheck_holds(rc, want):
            rec["status"] = "holds"
        else:
            rec["status"] = "FALSE"
            failed.append(cid)
        results.append(rec)

    total = len(rows)

    # THE UNJUDGED POPULATION (REQ-PLAN-080 as amended, #265). A class-A row that produced
    # neither `holds` nor `FALSE` was counted in NEITHER `failed` NOR `evaluated`, so it
    # simply vanished from the arithmetic below: one green criterion alongside any number of
    # unjudged ones yielded PASS, exit 0, and the reason string "all 1 evaluated
    # criterion/criteria hold" — true as written, profoundly misleading as read.
    #
    # `skipped-self-reference` is EXCLUDED from `unjudged`: it is a deliberate design
    # decision of this verb (a criterion invoking `recheck-criteria` cannot be run from
    # inside `recheck-criteria`), not a harness failure. Counting it would make the
    # completion binding permanently unreachable for any plan that writes such a criterion.
    unjudged = [r["id"] for r in results
                if r.get("kind") == "clause"
                and r.get("status") not in ("holds", "FALSE", "skipped-self-reference")]
    self_ref = [r["id"] for r in results if r.get("status") == "skipped-self-reference"]
    judgeable = class_a - len(self_ref)

    # THE COMPLETION BINDING is depth 0 — the same load-bearing guard REQ-PLAN-080 already
    # declares. A NESTED run (depth >= 1) is a criterion's own command routed through the
    # plan's harness; it reports and never halts, because halting there would make every
    # fixture-driven control fail under the close chain while passing standalone.
    at_completion = (depth == 0) and not advisory
    threshold = require_evaluated if require_evaluated is not None else 1.0
    met = (evaluated >= threshold * judgeable) if judgeable else True

    out = {
        **base,
        # EMITTED ON EVERY PATH, INCLUDING `PASS` (REQ-PLAN-080). A field emitted only on
        # the failing path cannot be used to detect the condition BEFORE it becomes one,
        # which is exactly how `evaluated_fraction` came to be consumed by nothing.
        "harness_incomplete": bool(unjudged),
        "unjudged": unjudged,
        "skipped_self_reference": self_ref,
        "judgeable": judgeable,
        "at_completion_binding": at_completion,
        "require_evaluated": threshold,
        # TWO DISTINCT FIELDS, never one conflated "coverage". They answer different
        # questions: how much of the plan is machine-readable AT ALL, versus how much this
        # run actually managed to evaluate. A single number lets a plan whose criteria are
        # 20% machine-readable read the same as one whose harness failed on 80% of them.
        "class_a_fraction": round(class_a / total, 4),
        "evaluated_fraction": round(evaluated / total, 4),
        "total": total, "class_a": class_a, "evaluated": evaluated,
        "failed": failed, "criteria": results,
    }

    if failed:
        out.update({"verdict": "FAIL", "severity": "error",
                    "reason": f"{len(failed)} criterion/criteria are FALSE at completion: "
                              f"{', '.join(failed)}",
                    "remediation": ("Each criterion above was true when its issue closed and "
                                    "is false now. Fix the regression, or amend the criterion "
                                    "if it no longer states what the plan means, then re-run "
                                    "§6.4.")})
        click.echo(json.dumps(out, indent=1))
        sys.exit(1)

    # HARNESS_INCOMPLETE — a THIRD verdict, and the distinction is the whole point:
    #
    #   FAIL                a criterion was judged and is FALSE          exit 1
    #   HARNESS_INCOMPLETE  a criterion the plan DECLARES judgeable      exit 1
    #                       was NOT judged
    #   INCONCLUSIVE        NOTHING was judgeable                        exit 2
    #
    # Collapsing the middle into either neighbour is the same two-facts-one-signal
    # conflation as `doc_lint`'s `not-selected` vs `no-such-path` (#181), `resume-scan`'s
    # `found` (#207) and `reindex`'s `no-index` vs `no-such-path` (REQ-OKF-011).
    #
    # It is checked BEFORE the `evaluated == 0` arm below, and the order is forced: with
    # `evaluated == 0` and `judgeable > 0` the plan carries class-A criteria NONE of which
    # ran, which is a harness failure, not "the plan has no machine-readable criteria".
    if at_completion and unjudged and not met:
        out.update({"verdict": "HARNESS_INCOMPLETE", "severity": "error",
                    "reason": (f"{len(unjudged)} class-A criterion/criteria went UNJUDGED at "
                               f"the completion binding ({evaluated} of {judgeable} judged, "
                               f"threshold {threshold}): {', '.join(unjudged)}"),
                    "remediation": ("Each criterion above is declared machine-readable and was "
                                    "not judged this run — the harness could not run it, not "
                                    "that it holds. Repair the instrument (see each row's "
                                    "`detail`), or, if the criterion is genuinely not "
                                    "machine-checkable, rewrite its Verification cell so it is "
                                    "not class-A. Re-run §6.4.")})
        click.echo(json.dumps(out, indent=1))
        sys.exit(1)

    if evaluated == 0:
        # INCONCLUSIVE MAPS TO `warn` AND NEVER HARD-FAILS COMPLETION (REQ-DATA-057
        # precedent). Measured over `docs/plans/plan-*/plan.md`: 6 of 52 bundles carry the
        # four-column shape and exactly 1 carries any clause-form criterion, so INCONCLUSIVE
        # is the EXPECTED verdict almost everywhere. Hard-gating on it is an outage.
        out.update({"verdict": "INCONCLUSIVE", "severity": "warn",
                    "reason": ("no criterion could be evaluated — the plan carries no "
                               "clause-form Verification cell this run could run")})
        click.echo(json.dumps(out, indent=1))
        sys.exit(2)

    reason = f"all {evaluated} evaluated criterion/criteria hold"
    if unjudged:
        # The PASS path says so OUT LOUD. A green that silently hides unjudged rows is the
        # shape #265 filed; even where the threshold permits it, the reader must be told.
        reason += (f" — but {len(unjudged)} class-A criterion/criteria went UNJUDGED "
                   f"({', '.join(unjudged)}); "
                   + ("advisory run, not halting" if advisory or depth
                      else f"permitted by --require-evaluated {threshold}"))
    out.update({"verdict": "PASS", "severity": "warn" if unjudged else "ok",
                "reason": reason})
    click.echo(json.dumps(out, indent=1))
    sys.exit(0)


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
      - abandoned                       → fails the status filter, DELIBERATELY (#208).
        `_is_parked` stays `approved`-only. The nudge this feeds says "run /yf-plan
        execute", which is exactly wrong for a plan that was stopped on purpose — so
        `abandoned` must never be classified parked. The two tags are mutually exclusive.
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


#: A bead dict carrying none of these is not evidence about any epic — see `_epic_state`.
_NON_GATE_TYPES = ("epic", "task", "molecule", "bug", "feature", "chore")


def _epic_state(epic_id: str | None, beads: dict, plan_dir: Path,
                epic_resolves: bool | None) -> dict:
    """Derive `epic_state` / `epic_status` / `epic_plan_dir` (REQ-CLI-013, #207).

    Six values, each with a DIFFERENT execute action:

      none      no pointer recorded          -> POUR (the normal first execution)
      stale     recorded, resolves to nothing -> POUR (the pointer is dead; #207's wedge)
      present   resolves, open work remains  -> RESUME
      complete  resolves, all work terminal  -> RESUME (never re-pour)
      foreign   resolves, but belongs to a DIFFERENT bundle -> HALT for an operator decision
      unknown   could not be determined      -> HALT as INCONCLUSIVE, never pour

    `unknown` IS NOT A SYNONYM FOR "GONE". An unreachable tracker looks exactly like a burned
    epic, and guessing "gone" produces the duplicate pour REQ-RESUME-004 exists to prevent.
    """
    out: dict = {"epic_state": "none", "epic_status": None, "epic_plan_dir": None}
    if epic_id is None:
        return out

    # THE LATENT FALSE NEGATIVE (D-11). `_all_plan_beads` MERGES two `bd list` calls. A
    # partial failure yields a dict holding only the gate query's results — NON-EMPTY, so the
    # `not beads` guard never fires — in which a perfectly healthy epic reports
    # `epic_resolves: false` and would be classified `stale`. `stale` routes EXECUTE to POUR,
    # which is the duplicate-epic failure. A bead dict carrying no non-gate bead at all is
    # evidence that the QUERY was partial, not that the epic is gone.
    if not beads or not any(b.get("issue_type") in _NON_GATE_TYPES for b in beads.values()):
        out["epic_state"] = "unknown"
        return out

    epic = beads.get(epic_id)
    if epic is None or epic_resolves is False:
        out["epic_state"] = "stale"
        return out
    if epic_resolves is None:
        out["epic_state"] = "unknown"
        return out

    out["epic_status"] = epic.get("status")
    out["epic_plan_dir"] = (epic.get("metadata") or {}).get("plan_dir")

    # FOREIGN — EXP-005's measured live hazard: a COPIED bundle silently resumes another
    # plan's epic. Compared on the resolved path, so `docs/plans/x` and `./docs/plans/x/`
    # are the same bundle. An epic with NO stamp is not foreign — it is merely unstamped
    # (every epic poured before the stamp existed), and calling that foreign would halt every
    # legacy resume.
    stamped = out["epic_plan_dir"]
    if stamped:
        try:
            same = Path(stamped).resolve() == Path(plan_dir).resolve()
        except OSError:
            same = str(stamped).rstrip("/") == str(plan_dir).rstrip("/")
        if not same:
            out["epic_state"] = "foreign"
            return out

    children_of: dict[str | None, list[dict]] = {}
    for b in beads.values():
        children_of.setdefault(b.get("parent"), []).append(b)
    seen: set[str] = set()
    stack = [epic_id]
    open_work = 0
    while stack:
        for child in children_of.get(stack.pop(), []):
            cid = child.get("id")
            if not cid or cid in seen:
                continue
            seen.add(cid)
            stack.append(cid)
            if child.get("issue_type") != "gate" and child.get("status") != "closed":
                open_work += 1
    out["epic_state"] = "present" if open_work or epic.get("status") != "closed" else "complete"
    return out


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
    # plan-053 / #207 (REQ-CLI-013): the SIX-VALUED `epic_state`.
    #
    # `found` is ONE BOOLEAN CARRYING TWO FACTS whose handling is OPPOSITE — "a pointer is
    # recorded" and "that pointer is live". A burned epic reports `found: true, total: 0`,
    # indistinguishable from a legitimately completed plan, so §5.2 (which extracts only
    # `found`) reads "no open work" and skips the plan entirely. Same conflation as
    # `doc_lint`'s `not-selected` vs `no-such-path` (#181): the remedy is to ADD A FIELD THAT
    # NAMES THE STATE and branch on it, never on the flag.
    #
    # DERIVED FROM SIGNALS ALREADY IN HAND (D-11). `epic_resolves` shipped with plan-044 and
    # answers "is it live?" already; this must NOT re-implement that check. `found` and
    # `epic_resolves` are emitted unchanged, so every existing consumer is unaffected.
    result.update(_epic_state(epic_id, beads, plan_dir, result["epic_resolves"]))
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
                   f"and no bead metadata.plan_dir match). "
                   f"[state: none] Treat as a fresh run.")
        return
    if result.get("stale_approved"):
        click.echo("  ⚠ STALE-APPROVED: plan content changed since approval — "
                   "re-review required before execute.")
    # THE HUMAN PATH NAMES THE STATE (plan-053 Issue 4.2, #207).
    #
    # A DANGLING ref was INVISIBLE here: this path printed the epic, "descendants: 0" and
    # "no stuck beads" — character for character what a legitimately FINISHED plan prints —
    # and said nothing about `epic_resolves`, which has been in the JSON since plan-044.
    # EXP-005 called this surface "worse than the JSON", and it is the one an operator reads.
    _STATE_NOTE = {
        "stale": ("⚠ STALE POINTER: this epic id resolves to NOTHING in bd. This is NOT a "
                  "finished plan — execute must POUR, not resume."),
        "foreign": ("⚠ FOREIGN EPIC: this epic is stamped to a DIFFERENT bundle. A copied "
                    "bundle must never silently resume another plan's epic — HALT and decide."),
        "unknown": ("⚠ UNKNOWN: the epic's state could not be determined (bd unavailable or "
                    "the query was partial). NOT the same as 'gone' — do NOT pour."),
        "complete": "all descendant work is terminal.",
        "present": "open work remains.",
    }
    _state = result.get("epic_state", "unknown")
    click.echo(f"Epic {result['epic_id']} (source: {result['epic_source']}) "
               f"[state: {_state}]")
    if _STATE_NOTE.get(_state):
        click.echo(f"  {_STATE_NOTE[_state]}")
    if result.get("epic_plan_dir") and _state == "foreign":
        click.echo(f"  epic is stamped to: {result['epic_plan_dir']}")
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


def _lint_findings_for_audit(plan_dir: Path, level: str = "fail") -> list[dict]:
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
            level if sev == "E" else "warn",
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

    **`escalations.md` and `plan-retrospective.md` appear in NONE of the eight checks
    above, and that absence is a REQUIREMENT rather than an oversight**
    (REQ-PORT-ACT-ESCALATION / REQ-PORT-ACT-RETROSPECTIVE, plan-059 Issue 2.6). The
    presence list here is a closed, hand-written set, so a new bundle member is a
    non-event unless someone adds it — and for these two it must never be added. Every
    bundle that predates them would hard-fail its next audit for lacking a file that did
    not exist when it was written.

    For escalations the reason is stronger than grandfathering, and it survives the
    corpus turning over: **the absence of escalations must never be made to look like a
    defect.** A plan that never needed to ask its controller anything has nothing to
    record. Reporting that as a gap creates exactly the Goodhart incentive plan-059's R4
    names — an agent that can escalate instead of finishing, rewarded for reclassifying
    difficulty as under-specification.

    **Why `plan-retrospective.md` was REJECTED as the escalation surface** (plan-059 R2),
    recorded here because the two files look interchangeable and are not: a retrospective
    entry is a *closed adjudication* written after the fact, and `append_retrospective` is
    append-only **deliberately**; an escalation is an *open question* whose entire
    lifecycle is a state change. Sharing one non-updatable stream would have given
    `retrospective-report` an unanswered question to count as a recorded event, and would
    have forced either a second entry per answer (breaking the one-entry-per-incident
    reading) or a mutable retrospective (breaking append-only for every other consumer).
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
    # WALK SITES 4 and 5 of 5 (REQ-OKF-CHK-003, plan-056 Issue 1.3). The member's §3b
    # exclusions must reach the AUDIT too, not only the engine — #233 is precisely the case
    # where they did not: `okf.check_conformance` is one walk, and `_audit_plan` performs two
    # MORE of its own (the `okf_spec`-value scan below, and the dangling-refs scan at step 6).
    # An exclusion honoured by the engine and not by the audit is worse than none, because the
    # operator cannot silence the finding at its declared source.
    _ext_excludes: list[str] = []
    try:
        _ext_excludes = list(okf.resolve_extension(SKILL_NAME).exclude_globs)
    except Exception:
        _ext_excludes = []

    def _okf_excluded(rel_path) -> bool:
        try:
            return okf.is_excluded(Path(rel_path).as_posix(), _ext_excludes)
        except Exception:
            return False

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
        if _okf_excluded(md.relative_to(plan_dir)):
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
        # A fixture corpus legitimately contains absolute paths and `../` traversals — they
        # are the RECORDED INPUT of a past run, not references this bundle makes.
        if _okf_excluded(path.relative_to(plan_dir)):
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
    # The binding inherits the audit's OWN grandfather level, rather than inventing a second
    # policy. `okf_missing_level` is already "warn" for a date-grandfathered plan or an
    # un-migrated OKF-legacy one (no `plan.md` frontmatter), and "fail" only for an OKF-native
    # plan. Document conformance is judged on exactly the same footing.
    #
    # WITHOUT THIS THE BINDING RE-JUDGES HISTORY. An un-migrated legacy bundle has no
    # frontmatter, no `## Gates`, no criteria table and a retired in-`plan.md` phase log — it
    # fails ten `E`-severity document checks by construction. `STATUS_SEVERITY` rescues the
    # finished ones (a `complete` bundle demotes `E` to `R`), but an in-flight legacy plan
    # mid-migration would hard-fail its own audit for being what it has always been. That is
    # the outcome the grandfather clause exists to prevent, and the regression guard for the
    # ~29 existing plans caught it.
    findings.extend(_lint_findings_for_audit(plan_dir, level=okf_missing_level))

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


# ---------------------------------------------------------------------------
# Start-gate resolution (REQ-PLAN-077 / #179) and the §6.4 gate-before-close
# ordering assertion (REQ-COMPLETE-004 / #180).
# ---------------------------------------------------------------------------


def _bd_children(node_id: str) -> list[dict]:
    """Direct children of `node_id`, INCLUDING gate-type and closed beads.

    `bd children` (an alias for `bd list --parent`) omits gate-type children, so the two
    queries are merged — the same shape `close_cascade.py::_node_children` uses, and for the
    same reason: a gate invisible to the walk is a gate the caller cannot reason about.
    """
    by_id: dict[str, dict] = {}
    for child in _bd_list("--parent", node_id, "--status", "all"):
        cid = child.get("id")
        if cid:
            by_id[cid] = child
    for gate in _bd_list("--parent", node_id, "--type", "gate", "--status", "all"):
        gid = gate.get("id")
        if gid:
            by_id[gid] = gate
    return [by_id[k] for k in sorted(by_id)]


def _bd_show_one(node_id: str) -> dict | None:
    """`bd show <id> --json`, defensively parsed. None when bd cannot answer."""
    try:
        out = subprocess.check_output(["bd", "show", node_id, "--json"],
                                      text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None
    parsed = _parse_bd_json(out)
    return parsed[0] if parsed else None


def _gate_is_resolved(bead: dict) -> bool:
    """Resolved per REQ-PLAN-067's terminal rule, restricted to gates.

    Kept deliberately IDENTICAL in meaning to `close_cascade.py::_bead_is_terminal`'s gate
    arm. Two readers disagreeing about whether a gate is satisfied is how an ordering
    assertion becomes a fail-loud false positive.
    """
    if bead.get("status") == "closed":
        return True
    for key in ("resolved", "verified", "gate_resolved"):
        if bead.get(key) is True:
            return True
    return str(bead.get("gate_status", "")).lower() in (
        "resolved", "verified", "satisfied", "passed", "closed")


def _find_start_gate_pair(epic: str) -> tuple[dict | None, dict | None, str | None]:
    """`(wrapper, gate, error)` for the plan-execute start gate under `epic`.

    The pour expands ONE `type = "gate"` formula step into TWO beads (REQ-PLAN-077): a
    wrapper TASK (`plan-execute.start-gate`, titled `Begin: <objective>`) that entry issues
    take as a `--deps` predecessor, and the real GATE (`plan-execute.gate-start-gate`).

    The wrapper does NOT carry a dotted child id under the epic — the pour allocates it a
    sibling id — so it is found by PARENT EDGE, never by an id prefix. Reading it by prefix
    is how a derivation silently finds nothing and reports success on an empty set.

    The gate is then resolved from the wrapper's own `blocks` dependency rather than by
    title, because `Gate: human` is the formula's generic title and would match any human
    gate under the same epic.
    """
    children = _bd_children(epic)
    if not children:
        return (None, None, f"no children under {epic} (bd may be unavailable)")

    wrappers = [c for c in children
                if (c.get("issue_type") or c.get("type")) == "task"
                and str(c.get("title", "")).startswith("Begin:")]
    if not wrappers:
        return (None, None,
                f"no start-gate wrapper task (title `Begin: …`) under {epic}")
    if len(wrappers) > 1:
        return (None, None,
                "more than one start-gate wrapper under "
                f"{epic}: {[w.get('id') for w in wrappers]} — refusing to guess")

    wrapper = _bd_show_one(str(wrappers[0].get("id"))) or wrappers[0]

    gates = [d for d in (wrapper.get("dependencies") or [])
             if d.get("issue_type") == "gate"]
    if not gates:
        gates = [c for c in children if (c.get("issue_type") or c.get("type")) == "gate"
                 and str(c.get("title", "")).startswith("Gate:")]
    if len(gates) != 1:
        return (wrapper, None,
                f"expected exactly one start gate for wrapper {wrapper.get('id')}, "
                f"found {len(gates)}")

    gate = _bd_show_one(str(gates[0].get("id"))) or gates[0]
    return (wrapper, gate, None)


def _start_gate_close_reason(gate_id: str, plan_id: str) -> str:
    """The GENERATED close reason (REQ-PLAN-077).

    Generated means DERIVED FROM THE SCENARIO, not merely constant: it names the gate that was
    resolved and the plan it belongs to, and cites the contract it discharges. EXP-002 measured
    49 of 49 wrappers closed by hand with 29 DISTINCT improvised reasons — a constant string
    would end the variance while carrying no more information than the variance did.
    """
    return (f"start gate {gate_id} resolved at execute start; wrapper closed in the same "
            f"step for {plan_id} (REQ-PLAN-077)")


@cli.command("resolve-start-gate")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True,
              help="Emit the structured verdict (default is also JSON).")
def resolve_start_gate(plan_dir: str, as_json: bool):
    """Resolve the start gate AND close its wrapper task, in one step (REQ-PLAN-077).

    WHY THIS IS A VERB AND NOT `bd gate resolve` FOLLOWED BY A HAND-TYPED `bd close`
    -------------------------------------------------------------------------------
    `bd gate resolve` closes the GATE. Nothing closes the WRAPPER. `close_cascade.py` then
    fail-louds on a non-terminal child under the molecule — correctly; the cascade is not the
    defect, the un-closed wrapper is.

    Measured across the live bead DB (EXP-002): **49 of 49** wrapper beads ever poured were
    closed BY HAND, with **29 distinct** improvised `close_reason` values. That is not an
    intermittent defect. It is a universal manual step with no mechanism and no exit code —
    the corpus's own headline in miniature.

    The fix is at the pour/resolve seam and NOT in `_bead_is_terminal`, which is reporting
    correctly. Weakening it would silence a true fail-loud, which is the "succeeds visibly
    while doing nothing" class this repo has measured repeatedly; the `neg-179-open-wrapper`
    scenario asserts it still refuses a genuinely open child, before and after.

    Idempotent: an already-closed wrapper is a clean pass, so a resumed session may re-run it.
    """
    pdir = Path(plan_dir)
    plan_md = pdir / "plan.md"
    if not plan_md.exists():
        click.echo(json.dumps({
            "verdict": "fail", "passed": False, "epic": None,
            "reason": f"plan.md not found under {plan_dir}",
            "remediation": "Check the plan_dir argument, then re-run §5.2a.",
        }))
        sys.exit(1)

    plan_id = _plan_id_from_dir(pdir)
    epic = _read_plan_epic_field(plan_md.read_text())
    if not epic:
        click.echo(json.dumps({
            "verdict": "fail", "passed": False, "epic": None,
            "reason": "no **Epic:** field on plan.md — the start-gate pair cannot be "
                      "re-derived",
            "remediation": "Run `plan_manager.py record-epic <plan_dir> <epic-id>` "
                           "immediately after the pour, then re-run.",
        }))
        sys.exit(1)

    wrapper, gate, err = _find_start_gate_pair(epic)
    if err is not None:
        click.echo(json.dumps({
            "verdict": "inconclusive", "passed": False, "epic": epic,
            "wrapper": (wrapper or {}).get("id"), "gate": None,
            "reason": err,
            "remediation": "Inspect `bd children " + epic + " --json` and resolve the start "
                           "gate by hand if the pour is non-standard.",
        }))
        sys.exit(0)

    wrapper_id, gate_id = str(wrapper["id"]), str(gate["id"])
    reason = _start_gate_close_reason(gate_id, plan_id)
    actions: list[str] = []

    if not _gate_is_resolved(gate):
        try:
            r = subprocess.run(["bd", "gate", "resolve", gate_id],
                               capture_output=True, text=True, timeout=60)
            rc, errtxt = r.returncode, (r.stderr or "").strip()
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as e:
            rc, errtxt = None, str(e)
        if rc != 0:
            click.echo(json.dumps({
                "verdict": "fail", "passed": False, "epic": epic,
                "wrapper": wrapper_id, "gate": gate_id, "close_reason": None,
                "reason": f"could not resolve gate {gate_id}: "
                          f"{errtxt or 'bd exited ' + str(rc)}",
                "remediation": f"bd gate resolve {gate_id}",
            }))
            sys.exit(1)
        actions.append("gate-resolved")
    else:
        actions.append("gate-already-resolved")

    if wrapper.get("status") != "closed":
        try:
            r = subprocess.run(["bd", "close", wrapper_id, "--reason", reason],
                               capture_output=True, text=True, timeout=60)
            rc, errtxt = r.returncode, (r.stderr or "").strip()
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as e:
            rc, errtxt = None, str(e)
        if rc != 0:
            # FAIL, not inconclusive: the gate is now resolved and the wrapper is not, which
            # is EXACTLY the #179 state. Reporting it softly would leave the caller believing
            # the seam had been closed.
            click.echo(json.dumps({
                "verdict": "fail", "passed": False, "epic": epic,
                "wrapper": wrapper_id, "gate": gate_id, "close_reason": reason,
                "actions": actions,
                "reason": f"gate {gate_id} resolved but wrapper {wrapper_id} could not be "
                          f"closed: {errtxt or 'bd exited ' + str(rc)}",
                "remediation": f"bd close {wrapper_id} --reason '{reason}'",
            }))
            sys.exit(1)
        actions.append("wrapper-closed")
    else:
        actions.append("wrapper-already-closed")
        reason = wrapper.get("close_reason") or reason

    click.echo(json.dumps({
        "verdict": "pass", "passed": True, "epic": epic,
        "wrapper": wrapper_id, "gate": gate_id, "close_reason": reason,
        "actions": actions,
        "reason": f"start gate {gate_id} resolved and wrapper {wrapper_id} closed",
        "remediation": None,
    }, indent=2))


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

    # ---- REQ-COMPLETE-004 (#180): the GATE-BEFORE-CLOSE ordering assertion ------------
    # The reconcile gate must be RESOLVED before the reconcile bead is closed. This is
    # REQ-COMPLETE-001's constraint 2 made mechanical; before it, the ordering existed only
    # in the author's head. Two consecutive plans hit it, worked around it by hand and filed
    # it; a third was told to expect it at launch and hit it anyway.
    #
    # WHAT IT REPLACES, AND WHY THAT WAS NOT ALREADY ENOUGH. `bd` itself refuses to close a
    # bead blocked by an open dependency — MEASURED: `cannot close <id>: blocked by open
    # issues [...] (use --force to override)`. So the ordering was already *unviolatable*;
    # the defect was that violating it produced `verdict: inconclusive` and **exit 0**, from
    # deep inside the close attempt, and SKILL.md §6.4 never read the exit code. The chain
    # then walked on to cascade-close and `set complete` with the reconcile step still open.
    # An accidental refusal reported softly is not an assertion. This makes the check
    # EXPLICIT, FIRST, and `fail` — and Issue 1.3 makes §6.4 read it.
    gates = [c for c in _bd_children(epic)
             if (c.get("issue_type") or c.get("type")) == "gate"
             and str(c.get("title", "")).startswith("Gate: Reconcile")]
    unresolved = [g for g in gates
                  if not _gate_is_resolved(_bd_show_one(str(g.get("id"))) or g)]
    if unresolved:
        ids = [str(g.get("id")) for g in unresolved]
        click.echo(json.dumps({
            "verdict": "fail", "passed": False, "epic": epic,
            "bead": (candidates[0].get("id") if candidates else None),
            "unresolved_gates": ids,
            "reason": f"the reconcile gate {ids} is not resolved — §6.4's gate-before-close "
                      "ordering constraint (REQ-COMPLETE-004) forbids closing the reconcile "
                      "bead against incomplete execution",
            "remediation": "Every execution bead under this plan's epic must close first; the "
                           "reconcile gate then resolves. Check `bd ready` and "
                           f"`bd show {ids[0]} --json`, then re-run §6.4.",
        }, indent=2))
        sys.exit(1)

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


#: The statuses at which an unanswered escalation is a FINDING rather than ordinary
#: in-flight state. Before `reconciling` an open question is simply an open question — the
#: plan is still running and the default has not yet been irreversibly taken.
_ESCALATION_OPEN_STATUSES = ("reconciling", "complete")


def _open_escalation_findings(plan_dir: Path) -> list[dict]:
    """One `warn` finding, item `escalation-open`, when a question outlives the plan.

    **`W`, never `E`.** An open escalation is a fact about the plan's *conversation*, not a
    defect in its bundle, and this whole step is advisory — a halting severity here would
    block completion on an unanswered question, which is precisely the coercion that would
    make the mechanism something to route around rather than use.

    **Exactly ONE finding, however many escalations are open.** The signal is "this plan is
    finishing with unanswered questions", which is one fact; emitting one per entry would let
    a plan with six open escalations look six times worse than a plan with one, when what a
    reader needs is the list, which the detail carries.

    Returns `[]` outside `_ESCALATION_OPEN_STATUSES`, and `[]` when there is no
    `escalations.md` at all — the presence-optional contract holds here too.
    """
    plan_md = plan_dir / "plan.md"
    if not plan_md.exists():
        return []
    status = _read_plan_status(plan_md.read_text(encoding="utf-8"))
    if status not in _ESCALATION_OPEN_STATUSES:
        return []
    path = plan_dir / ESCALATION_FILE
    if not path.exists():
        return []
    entries = _escalation_entries(path.read_text(encoding="utf-8"))
    open_ids = [e for e in sorted(entries) if entries[e].get("state", "").strip() == "raised"]
    if not open_ids:
        return []
    return [_audit_finding(
        "escalation-open", "warn",
        f"{len(open_ids)} escalation(s) still `state: raised` at `{status}`: "
        f"{', '.join(open_ids)}. The plan is finishing with a question nobody answered. "
        f"Either record the answer with `escalation-resolve <id> --answer ...`, or — if the "
        f"recommended default was taken without an answer arriving — record THAT with "
        f"`escalation-resolve <id> --answer '<the default>' --default-taken`, which is the "
        f"ordinary fire-and-forget outcome and not a failure. Advisory: completion is NOT "
        f"blocked."
    )]


@cli.command("judgement-never-fired-report")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True)
def judgement_never_fired_report(plan_dir: str, as_json: bool):
    """Close-time report on whether yf-judgement's trigger ever ran — ADVISORY (Issue 5.2).

    **The question this answers is "did the detector run", NOT "did it find anything".** A
    trigger that never fires and a trigger that is not installed produce the same silence, and
    plan-059 records four instances of that exact failure in this repository — `closable`,
    `plan_manager.py audit`, `retrospective_fields.py`, and #270's never-poured formula. Every
    one was found by hand, late, by someone who happened to go looking.

    **This is DEFENCE IN DEPTH, not the primary remedy, and the difference is stated rather
    than implied.** The load-bearing mechanism is the trigger writing its own `judgement:`
    echo to `log.md` on both paths (Issue 5.1) — nothing has to remember for that to happen.
    This verb only *reads* those echoes. Fronting it as a `plan_manager.py` verb buys one
    specific thing: `test_close_contract.py` enumerates the §6.4 chain from `SKILL.md`, so a
    step **added** without the envelope is detected. It does **not** detect a step **removed**,
    and it never establishes that §6.4 was run at all. Both limits are real and neither is
    closed here.

    Advisory: exits 0 unconditionally and never gates `set complete`.
    """
    pdir = Path(plan_dir)
    log = pdir / "log.md"
    lines = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
    echoes = [ln for ln in lines if "judgement: " in ln]
    fired = [ln for ln in echoes if JUDGEMENT_FIRED in ln]
    not_fired = [ln for ln in echoes if JUDGEMENT_NOT_FIRED in ln]
    esc = _escalation_report(pdir)

    if not echoes:
        verdict = "fail"
        reason = ("the yf-judgement trigger left NO echo in log.md — it either never ran or "
                  "no longer writes its echo. These are indistinguishable from here, which "
                  "is the whole point: a trigger whose non-firing looks like a quiet period "
                  "is not observable.")
        remediation = (
            "Run `plan_manager.py judgement-echo-check <plan_dir> --json` — it invokes the "
            "trigger and reports `lines_added` by diffing log.md, so it distinguishes the "
            "two cases. If `lines_added` is 0, restore the `_judgement_echo` call in "
            "`review-loop-check`. Advisory: completion is NOT blocked."
        )
    else:
        verdict = "pass"
        reason = (f"the trigger ran {len(echoes)} time(s) — {len(fired)} fired, "
                  f"{len(not_fired)} not-fired. Non-firing is RECORDED, not merely absent.")
        remediation = None

    click.echo(json.dumps({
        "verdict": verdict,
        "passed": verdict == "pass",
        "advisory": True,
        "echoes": len(echoes),
        "fired": len(fired),
        "not_fired": len(not_fired),
        "last_echo": echoes[0] if echoes else None,
        "escalations_raised": esc["raised"],
        "escalations_open": esc["open"],
        "pushes": esc["pushes"],
        "reason": reason,
        "remediation": remediation,
    }, indent=2))
    # ADVISORY: always 0. Not conditional, and with no flag to make it conditional.
    raise SystemExit(0)


def _land_epic_from_bd(plan_dir: Path) -> str | None:
    """The epic id for a bundle, resolved from `bd` rather than from a cwd-relative file.

    Mirrors `_resume_scan`'s `epic_source=bd_metadata` route: the pour stamps the epic with
    `metadata.plan_dir` (SKILL.md §5.2a step (a)) exactly so the linkage is findable when
    plan.md carries no `**Epic:**` field. Reused here so the route-record check answers the
    same in both address spaces.
    """
    want = plan_dir.as_posix().rstrip("/")
    want_leaf = plan_dir.name
    proc = subprocess.run(["bd", "list", "--all", "--limit", "5000", "--json"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    if isinstance(data, dict):
        data = data.get("issues") or []
    for b in data if isinstance(data, list) else []:
        meta = b.get("metadata") or {}
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except json.JSONDecodeError:
                continue
        pd = str(meta.get("plan_dir") or "").rstrip("/")
        # Match on the full repo-relative path OR its leaf: the two address spaces agree on
        # the leaf even where a caller passes an absolute or differently-rooted plan_dir.
        if pd and (pd == want or Path(pd).name == want_leaf):
            return str(b.get("id", "")).split(".")[0] or None
    return None


def _land_assert_primary_checkout() -> dict:
    """REQ-LAND-010 ENFORCED, not assumed: `--apply` runs from the PRIMARY checkout.

    Every `_land_*` helper reads `plan_dir` RELATIVE TO CWD, and the plan folder is
    primary-side — so run from a linked worktree they read a STALE bundle. That is not a
    hypothetical: measured on this plan, `plan.md`, `log.md`, `index.md` and
    `plan-retrospective.md` all differ between the two address spaces mid-execution.

    For `land --apply` the cwd is PINNED by contract, so cwd-relative reads are correct there
    — but a contract nothing checks is the same silent divergence one layer up. This makes it
    an exit code. L2 would fail anyway (a linked worktree cannot check out a branch another
    worktree holds), but it would fail AFTER L0 took the lock and L1 mutated the branch;
    refusing up front costs nothing and leaves nothing to unwind.
    """
    cwd = Path.cwd().resolve()
    primary = _land_primary_checkout().resolve()
    if cwd == primary:
        return {"ok": True, "cwd": str(cwd), "primary": str(primary)}
    return {
        "ok": False, "cwd": str(cwd), "primary": str(primary),
        "reason": (f"`land --apply` must run from the PRIMARY checkout ({primary}), not from "
                   f"{cwd}. Every plan-folder read is cwd-relative and the plan folder is "
                   f"primary-side, so from here the landing would read a STALE bundle — and "
                   f"L2 cannot check out the merge target from a linked worktree anyway."),
        "remediation": f"cd {primary} && re-run the `apply_command` from `land --dry-run`.",
    }


def _land_route_record_findings(plan_dir: Path) -> list[dict]:
    """`Type: human` gates whose ROUTE RECORD says an agent resolved them (REQ-LAND-015).

    THE SIGNAL IS ASYMMETRIC, and the asymmetry is what makes a strippable marker useful:

      * a CLEAN record is WEAK evidence of a human — anyone can strip a marker;
      * a DIRTY record is STRONG evidence of an agent — nothing adds `CLAUDECODE` and
        removes the controlling terminal by accident.

    So this reports the dirty direction only. It never certifies that a gate WAS
    human-resolved, and nothing here should be read as doing so. DETECTION, NOT PREVENTION.
    """
    out: list[dict] = []

    def _inconclusive(reason: str) -> list[dict]:
        """A LOUD NO-OP. The check DID NOT RUN, and that is a different fact from `clean`.

        Silence here was the third vacuity path in this control: `if not epic: return out`
        returned an empty list, which every caller read as "checked and found nothing". A
        control whose failure mode is indistinguishable from a clean result is the defect this
        plan exists to remove (#263, #181).

        `warn`, never `fail` — REQ-DATA-057's precedent: an INCONCLUSIVE is a statement about
        the INSTRUMENT, not a verdict on the artifact, so it must not manufacture a failure.
        """
        return [{"item": "route-record check", "status": "warn", "class": "inconclusive",
                 "detail": (f"ROUTE-RECORD CHECK DID NOT RUN: {reason}. This is NOT a clean "
                            f"result — the REQ-LAND-015 detection control for #293 was not "
                            f"evaluated. Distinguish it from a pass.")}]

    # RESOLVE THE EPIC ID FROM A CWD-INDEPENDENT SOURCE FIRST.
    #
    # WHY: `plan_dir/plan.md` is read RELATIVE TO CWD, and the plan folder is PRIMARY-SIDE by
    # the address-space model — so the worktree's copy predates every field the execution
    # wrote. Measured on this very plan at 09c74f6: identical command, identical plan_dir,
    # `fail` from the primary and `pass` from the worktree, because the `**Epic:**` field is
    # present in one plan.md and absent in the other. TWO TRUTHS, and the wrong one was the
    # silent pass.
    #
    # `bd` IS THE CWD-INDEPENDENT SOURCE and is the right one on the merits, not merely the
    # convenient one: INV-2 makes the shared Dolt DB reachable identically from either address
    # space, and the epic is STAMPED with `metadata.plan_dir` at pour time precisely so the
    # linkage survives a plan.md that lacks the field — that is `_resume_scan`'s documented
    # `epic_source=bd_metadata` fallback, reused here rather than reinvented.
    #
    # DELIBERATELY NOT CHOSEN: reading the PRIMARY's plan.md from a worktree invocation. It
    # would work, and it is what this session reached for once already and was right to be
    # corrected on — a check that silently reaches across the address-space boundary to find a
    # more convenient answer is how the boundary stops meaning anything. `bd` is shared BY
    # DESIGN; the other checkout is not.
    if not shutil.which("bd"):
        return _inconclusive("`bd` is not on PATH, so neither the epic id nor the gate list "
                             "could be resolved")

    epic = None
    plan_md = plan_dir / "plan.md"
    if plan_md.is_file():
        epic = _read_plan_epic_field(plan_md.read_text(encoding="utf-8"))
    if not epic:
        epic = _land_epic_from_bd(plan_dir)
    if not epic:
        return _inconclusive(
            f"could not resolve the epic id — it is absent from {plan_md} (which is read "
            f"relative to cwd, and the plan folder is primary-side) and no bead carries "
            f"`metadata.plan_dir == {plan_dir.as_posix()}`")

    proc = subprocess.run(
        ["bd", "list", "--all", "--type", "gate", "--limit", "500", "--json"],
        capture_output=True, text=True)
    if proc.returncode != 0:
        return out
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return out
    if isinstance(data, dict):
        data = data.get("issues") or []
    for g in data if isinstance(data, list) else []:
        if not str(g.get("id", "")).startswith(epic):
            continue
        meta = g.get("metadata") or {}
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except json.JSONDecodeError:
                meta = {}
        if (meta.get("gate_type") or "human") != "human":
            continue
        rr = meta.get("route_record") or {}
        if not rr:
            continue
        if _land_route_record_is_agent(rr):
            out.append({
                "item": f"gate {g.get('id')} route record",
                "status": "fail",
                "detail": (
                    f"a `Type: human` gate carries a route record reading NO TTY with agent "
                    f"marker(s) {rr.get('agent_markers')}. That is an executing agent "
                    f"resolving a human consent gate — dixson3/yoshiko-flow#293. This is "
                    f"DETECTION, not prevention: the record is strippable, so its absence "
                    f"proves nothing, but its presence is strong evidence."),
            })
    return out


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
    findings = list(result.get("findings", []) or [])
    # plan-059 Issue 5.4 — the OPEN-ESCALATION signal, added HERE and deliberately not in
    # `_audit_plan`.
    #
    # The placement is the requirement, not a convenience. REQ-PORT-ACT-ESCALATION puts
    # `escalations.md` on NO audit presence list, so `audit` must stay silent about
    # escalations in both directions — a bundle with none and a bundle with one audit
    # identically. This close-time verb is a different question: not "is the bundle
    # conformant" but "is the plan finishing with a question it never got an answer to".
    #
    # It is the plan's own thesis applied to its own artifact. An escalation raised, never
    # answered, and never noticed is exactly the silent-idle failure the whole mechanism
    # exists to make impossible — and without this the artifact would record the question
    # while nothing ever read it back.
    findings.extend(_open_escalation_findings(pdir))
    # plan-060 Issue 3.4 / REQ-LAND-015 — the ROUTE-RECORD signal. A `Type: human`
    # gate whose recorded route reads "no tty, CLAUDECODE set" was resolved by an
    # agent asserting its own authorization, which is dixson3/yoshiko-flow#293
    # exactly. DETECTION, NOT PREVENTION: the markers are strippable — but
    # ASYMMETRICALLY, so a dirty record is strong evidence even though a clean one is
    # weak. This would have surfaced #293 within seconds.
    findings.extend(_land_route_record_findings(pdir))
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


@cli.command("escalation-raise")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--question", required=True,
              help="The question, stated so a controller can answer it without reading the plan.")
@click.option("--alternative", "alternatives", multiple=True,
              help="A stated option. REPEATABLE, and AT LEAST TWO are required.")
@click.option("--recommended", required=True,
              help="Which alternative this session recommends. MUST be one of --alternative.")
@click.option("--on-no-answer", "on_no_answer", required=True,
              help="What happens if no answer arrives. Required: the transport is fire-and-forget.")
@click.option("--detected-by", "detected_by",
              type=click.Choice(ESCALATION_DETECTED_BY), default="self-report",
              help="WHO found it. A closed domain, because the recorder is usually the subject.")
@click.option("--evidence", default="",
              help="The command + output behind any state claim. Defaults to `unverified`.")
@click.option("--asked-of", "asked_of", default="",
              help="The controller this was asked of. A seam left open for a future N-hop form.")
@click.option("--dry-run", is_flag=True, help="Report what would be written; write nothing.")
@click.option("--json-output", "--json", "as_json", is_flag=True)
def escalation_raise(plan_dir: str, question: str, alternatives: tuple[str, ...],
                     recommended: str, on_no_answer: str, detected_by: str,
                     evidence: str, asked_of: str, dry_run: bool, as_json: bool):
    """Append one `## ESC-NNN` entry to `escalations.md` (REQ-PORT-053).

    Creates the file (with `type: Escalation` frontmatter) when absent and lists it in the
    reserved `index.md`, so a bundle member never lands unindexed.
    """
    pd = Path(plan_dir)
    try:
        result = raise_escalation(
            pd, question=question, alternatives=list(alternatives),
            recommended=recommended, on_no_answer=on_no_answer,
            detected_by=detected_by, evidence=evidence, asked_of=asked_of,
            dry_run=dry_run,
        )
    except ValueError as exc:
        # STILL JSON ON STDOUT, still a non-zero exit (REQ-CLI-016 shape): a caller parsing
        # the stream must not have to distinguish a crash from a refusal.
        payload = {"verdict": "refused", "error": str(exc)}
        click.echo(json.dumps(payload, indent=2) if as_json else f"refused: {exc}")
        raise SystemExit(1)
    result["dry_run"] = dry_run
    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"{result['id']}: {'appended' if result['appended'] else 'already present'} "
                   f"in {result['file']}")


@cli.command("escalation-resolve")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.argument("escalation_id")
@click.option("--answer", required=True, help="What the controller answered, verbatim.")
@click.option("--default-taken", "default_taken", is_flag=True,
              help="No answer arrived and the recommended default was taken. The entry still "
                   "becomes `resolved` — see REQ-PORT-054's lifecycle edge.")
@click.option("--by", default="", help="Who took the default, when --default-taken is set.")
@click.option("--state", type=click.Choice(ESCALATION_STATES), default="resolved")
@click.option("--json-output", "--json", "as_json", is_flag=True)
def escalation_resolve(plan_dir: str, escalation_id: str, answer: str,
                       default_taken: bool, by: str, state: str, as_json: bool):
    """Record an answer on an existing escalation, reporting `prior_entries_unchanged`."""
    try:
        result = resolve_escalation(Path(plan_dir), escalation_id, answer=answer,
                                    default_taken=default_taken, by=by, state=state)
    except ValueError as exc:
        payload = {"verdict": "refused", "error": str(exc)}
        click.echo(json.dumps(payload, indent=2) if as_json else f"refused: {exc}")
        raise SystemExit(1)
    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"{result['id']} -> {result['state']} "
                   f"(prior entries unchanged: {result['prior_entries_unchanged']})")


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


# --- yf-judgement: the trigger, its echo, and its push (plan-059 Epics 3 and 5) --------

#: Statuses at which a bundle's `log.md` is a CLOSED HISTORICAL RECORD and the judgement echo
#: is skipped. This is the ONLY exemption, and it is deliberately not on the axis that
#: matters: the echo is unconditional across FIRED vs NOT-FIRED, which is what R1 and SC6 are
#: about. Writing into a finished plan's log would be a mutation of an unrelated artifact
#: every time anyone ran the trigger against it — measured as a live hazard by plan-059's SC4,
#: which points the trigger at `plan-050` precisely because that bundle has enough review
#: passes to exercise the payload.
_JUDGEMENT_TERMINAL_STATUSES = ("complete", "abandoned")

JUDGEMENT_FIRED = "judgement: fired"
JUDGEMENT_NOT_FIRED = "judgement: not-fired"


def _judgement_echo(plan_dir: Path, fired: bool, detail: str) -> dict:
    """Write the trigger's own echo to `log.md`, on BOTH the fired and not-fired paths.

    THIS IS THE LOAD-BEARING HALF OF EPIC 5, and the reason is the command-vs-obligation
    law the plan is built on: only a step the SCRIPT performs is a step that survives.
    Every other observability remedy in this plan — enumerating the report by name in the
    close contract, a tagged test at the call site — is defence in depth that a removal
    can walk past. This one writes itself.
    
    Without it, a trigger that never fires is INDISTINGUISHABLE FROM A QUIET PERIOD, and
    plan-059 records four separate instances of exactly that failure (`closable`,
    `plan_manager.py audit`, `retrospective_fields.py`, and #270's never-poured formula) —
    every one found by hand, late, by someone who went looking.

    The echo bullet is INERT to the lifecycle: it matches neither the `review:` count regex
    (REQ-PORT-006) nor the `scoping:` grandfather-date regex, so it can never perturb an
    audit. Returns ``{"appended", "line", "skipped_reason"}``.
    """
    plan_md = plan_dir / "plan.md"
    status = None
    if plan_md.exists():
        status = _read_plan_status(plan_md.read_text(encoding="utf-8"))
    if status in _JUDGEMENT_TERMINAL_STATUSES:
        return {"appended": False, "line": None,
                "skipped_reason": f"bundle status is `{status}` — its log is a closed record"}
    bullet = f"{JUDGEMENT_FIRED if fired else JUDGEMENT_NOT_FIRED} — {detail}"
    try:
        okf.append_log(plan_dir, bullet, date=datetime.now().strftime("%Y-%m-%d"))
    except Exception as exc:  # a broken log must not take the trigger down with it
        return {"appended": False, "line": None, "skipped_reason": f"append_log failed: {exc}"}
    return {"appended": True, "line": f"- {bullet}", "skipped_reason": None}


def _review_loop_escalation(plan_dir: Path, escalates: bool, cycles: int, limit: int) -> dict:
    """The escalation PAYLOAD `review-loop-check` carries (REQ-PORT-054 shape).

    Emitted on BOTH paths. A payload present only when the trigger fires would make
    "the key is absent" mean two different things — the trigger did not fire, or the
    trigger is not installed — which is the two-facts-one-signal conflation this whole
    plan is organised against.

    `on_no_answer` is NEVER null, on either path. The transport has no answer-return
    primitive, so an escalation without its own default pretends to a round-trip that
    cannot be delivered.
    """
    return {
        "fired": escalates,
        "trigger": "review-loop-check",
        "stop_class": 4 if escalates else None,
        "question": (
            f"The review loop has run {cycles} cycle(s) against a bound of {limit} and the "
            f"plan is still not converging. Resolve the outstanding concerns by hand, or "
            f"raise the bound for one invocation?"
            if escalates else
            f"No question: the review loop is at {cycles} of {limit} cycle(s) and is "
            f"converging."
        ),
        "alternatives": [
            "Resolve the outstanding concerns by hand and re-run the red-team",
            "Raise the bound for this invocation with `--max-review-cycles <n>`",
            "Abandon the plan and re-scope",
        ],
        "recommended": "Resolve the outstanding concerns by hand and re-run the red-team",
        # NEVER null, on either path — see the docstring.
        "on_no_answer": (
            "The plan stays in `review` carrying its REVISE verdict. That is a LEGAL state, "
            "not a wedge: REQ-PLAN-030 bars only `ready-for-approval`. Nothing is lost and "
            "nothing proceeds."
        ),
        "detected_by": "mechanical-check",
        "evidence": (
            f"len(glob('reviews/pass-*.md')) == {cycles}; bound == {limit}; "
            f"review-loop-check exits {3 if escalates else 0}"
        ),
        "asked_of": os.environ.get("YF_PARENT_PANE", ""),
    }


def _herdr_push(pane: str, message: str) -> tuple[bool, str]:
    """Send one notification and verify delivery **STRUCTURALLY** (Issue 3.3c / REQ-HERDR-027).

    `herdr agent prompt` returns ``agent_not_found`` **at exit 0**. Measured, and it is the
    reason this function exists at all: a caller that branches on ``$?`` records a delivered
    push for a pane that does not exist, and the escalation is then stamped as sent and never
    retried. `$?` is not evidence here — the returned payload is.

    Returns ``(delivered, detail)``. `delivered` is true only when the parsed payload carries
    ``result.type == "agent_prompted"``; anything else — a non-JSON stream, a missing key, an
    error object — is UNDELIVERED, because an unreadable answer is not a yes.

    Never raises: a machine with no `herdr` on PATH is an ordinary state (a human is present),
    not an error.
    """
    if not shutil.which("herdr"):
        return False, "herdr is not on PATH — no controller channel exists on this machine"
    try:
        proc = subprocess.run(
            ["herdr", "agent", "prompt", pane, message],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"herdr invocation failed: {exc}"
    raw = (proc.stdout or "").strip()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        # NOT a fallback to the exit code. An unparseable response is undelivered.
        return False, (f"herdr returned a non-JSON stream (exit {proc.returncode}); delivery "
                       f"is UNVERIFIED, which is not the same as delivered: {raw[:200]!r}")
    if isinstance(payload, list):
        payload = payload[0] if payload else {}
    result = payload.get("result") or {}
    if result.get("type") == "agent_prompted":
        return True, "result.type == agent_prompted"
    return False, (f"herdr exited {proc.returncode} but the payload does not confirm delivery "
                   f"(result.type={result.get('type')!r}, error={payload.get('error')!r}) — "
                   f"this is the `agent_not_found`-at-exit-0 case")


def _herdr_stamp_token(source: str, token: str) -> bool:
    """Stamp a pane metadata token beside a push (Issue 3.3b). Idempotent, best-effort.

    The stamp exists so the parent's poll is an INDEPENDENT backstop. A poll that only ever
    sees what the push already reported is not a backstop — it is the same claim read twice,
    and it would go green in exactly the case (`agent_not_found` at exit 0) the pairing is
    meant to catch.
    """
    pane = os.environ.get("HERDR_PANE_ID", "")
    if not pane or not shutil.which("herdr"):
        return False
    try:
        proc = subprocess.run(
            ["herdr", "pane", "report-metadata", pane, "--source", source, "--token", token],
            capture_output=True, text=True, timeout=30,
        )
        return proc.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def _escalation_report(plan_dir: Path) -> dict:
    """The instrumentation research 005 §8.4 names as the missing half (Issue 3.5).

    `raised` is the **CUMULATIVE** count of escalations ever raised — NOT the number
    currently in `state: raised`. The two readings are not interchangeable and the plan's
    own criteria only cohere under this one: SC5 needs `raised >= 2` (both entries) while
    SC6c needs exactly one entry *currently* raised.
    """
    path = plan_dir / ESCALATION_FILE
    if not path.exists():
        return {"file": str(path), "exists": False, "raised": 0, "answered": 0,
                "no_answer_taken": 0, "open": 0, "pushes": 0, "entries": []}
    entries = _escalation_entries(path.read_text(encoding="utf-8"))
    rows = []
    for eid in sorted(entries):
        f = entries[eid]
        rows.append({
            "id": eid,
            "state": f.get("state", ""),
            "raised_when": f.get("raised_when", ""),
            "resolved_when": f.get("resolved_when", ""),
            "answered": bool(f.get("answer", "").strip()),
            "no_answer_taken": f.get("no_answer_taken", "no").strip().lower() == "yes",
            "push_batch": f.get("push_batch", "").strip(),
        })
    batches = {r["push_batch"] for r in rows if r["push_batch"]}
    return {
        "file": str(path),
        "exists": True,
        # CUMULATIVE — every entry ever raised, whatever its state now.
        "raised": len(rows),
        "answered": sum(1 for r in rows if r["answered"] and not r["no_answer_taken"]),
        "no_answer_taken": sum(1 for r in rows if r["no_answer_taken"]),
        "open": sum(1 for r in rows if r["state"] == "raised"),
        # BATCHING, made observable rather than asserted: entries sharing a batch id went
        # out in ONE notification, so `pushes` is the count of notifications actually sent.
        "pushes": len(batches),
        "entries": rows,
    }


@cli.command("escalation-report")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True)
def escalation_report(plan_dir: str, as_json: bool):
    """Report the escalation instrumentation research 005 §8.4 names as missing (Issue 3.5).

    Emits `raised`, `answered`, `no_answer_taken`, `open` and `pushes`, plus one row per
    escalation recording when it was raised, whether it was answered, and whether its
    `on_no_answer` default was taken instead.

    **`raised` is CUMULATIVE** — every entry ever raised, whatever state it is in now — not
    the number currently in `state: raised`, which is reported separately as `open`. The
    distinction is load-bearing: the cost-ratio premise the whole escalation path rests on is
    "how often does an answer arrive versus how often is the default silently taken", and a
    count that shrinks as questions get answered cannot measure it.
    """
    result = _escalation_report(Path(plan_dir))
    if as_json:
        click.echo(json.dumps(result, indent=2))
    else:
        click.echo(f"raised={result['raised']} answered={result['answered']} "
                   f"no_answer_taken={result['no_answer_taken']} open={result['open']} "
                   f"pushes={result['pushes']}")


@cli.command("escalation-push")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--pane", default=None,
              help="Target pane. Defaults to $YF_PARENT_PANE; absent means no controller.")
@click.option("--dry-run", is_flag=True, help="Report what would be sent; send nothing.")
@click.option("--json-output", "--json", "as_json", is_flag=True)
def escalation_push(plan_dir: str, pane: str | None, dry_run: bool, as_json: bool):
    """Notify the upstream controller about every un-pushed OPEN escalation, in ONE line.

    **Write-then-notify, never ask-and-await** (Issue 3.3). The escalation IS the artifact;
    this is a notification that it exists. There is no answer-return primitive in the
    transport, so nothing here waits for anything.

    **The push is BATCHED**: every open, un-pushed escalation goes out in a single message
    naming the artifact, and each is stamped with the same `push_batch` id. That makes
    batching *observable* — `escalation-report`'s `pushes` counts distinct batch ids — rather
    than an asserted property. It rides the three push classes the yf-herdr SPEC already
    defines (epic completion, blocker, plan completion) rather than adding a fourth.

    **Delivery is verified STRUCTURALLY, never by exit code** (Issue 3.3c). `herdr agent
    prompt` returns `agent_not_found` **at exit 0**, so `$?` is not evidence of anything: the
    returned payload is parsed and a missing `type: agent_prompted` is reported as an
    undelivered push. The escalations are stamped only when delivery is structurally
    confirmed, so an undelivered batch is retried rather than silently marked sent.

    **Every push is paired with an idempotent token stamp** (Issue 3.3b), so the parent's
    poll is a genuine independent backstop rather than a restatement of the push it would be
    checking.
    """
    pdir = Path(plan_dir)
    path = pdir / ESCALATION_FILE
    target = pane if pane is not None else os.environ.get("YF_PARENT_PANE", "")
    result: dict = {"file": str(path), "pane": target or None, "dry_run": dry_run,
                    "pushed_ids": [], "pushes": 0, "delivered": None, "batch": None}

    if not path.exists():
        result["verdict"] = "skipped"
        result["reason"] = "no escalations.md — nothing to notify about"
        click.echo(json.dumps(result, indent=2) if as_json else result["reason"])
        return

    entries = _escalation_entries(path.read_text(encoding="utf-8"))
    pending = [e for e in sorted(entries)
               if entries[e].get("state", "") == "raised"
               and not entries[e].get("push_batch", "").strip()]
    result["pushed_ids"] = pending
    if not pending:
        result["verdict"] = "skipped"
        result["reason"] = "no open, un-pushed escalation"
        click.echo(json.dumps(result, indent=2) if as_json else result["reason"])
        return

    if not target:
        # THE HUMAN-PRESENT ARM (Issue 4.4). An unset `YF_PARENT_PANE` means no controller
        # exists to notify — a human is present instead. Zero pushes is the CORRECT outcome
        # here, not a degraded one, which is why SC5 asserts `pushes <= 1` rather than `== 1`.
        result["verdict"] = "no-controller"
        result["reason"] = ("YF_PARENT_PANE is unset — no upstream controller exists, so a "
                            "human is present and the artifact is the whole delivery")
        click.echo(json.dumps(result, indent=2) if as_json else result["reason"])
        return

    plan_id = pdir.name
    batch = f"{datetime.now().strftime('%Y%m%dT%H%M%S')}-{len(pending)}"
    line = (f"{plan_id}: {len(pending)} open escalation(s) {', '.join(pending)} — "
            f"see {path} for the question, alternatives and recommended default. "
            f"Write-then-notify: no reply is awaited; each entry states its on_no_answer.")
    result["batch"] = batch
    result["message"] = line

    if dry_run:
        result["verdict"] = "dry-run"
        click.echo(json.dumps(result, indent=2) if as_json else line)
        return

    delivered, detail = _herdr_push(target, line)
    result["delivered"] = delivered
    result["delivery_detail"] = detail
    if not delivered:
        # FAIL-CLOSED: do NOT stamp. An unstamped escalation is retried on the next boundary;
        # a stamped-but-undelivered one is lost forever and looks sent.
        result["verdict"] = "undelivered"
        click.echo(json.dumps(result, indent=2) if as_json else f"UNDELIVERED: {detail}")
        raise SystemExit(1)

    text = path.read_text(encoding="utf-8")
    for eid in pending:
        row = dict(_escalation_entries(text)[eid])
        for k in ESCALATION_FIELDS:
            row.setdefault(k, "")
        row["push_batch"] = batch
        blocks = _escalation_blocks(text)
        text = text.replace(blocks[eid], _escalation_render(eid, row), 1)
    _escalation_write(path, text)

    # Issue 3.3b — the idempotent token stamp, paired with the push. Best-effort: a missing
    # `herdr` must never fail a push that was structurally confirmed delivered.
    result["token_stamped"] = _herdr_stamp_token(plan_id, f"escalations={len(pending)}")
    result["pushes"] = 1
    result["verdict"] = "pushed"
    click.echo(json.dumps(result, indent=2) if as_json else f"pushed {len(pending)} in 1 message")


@cli.command("judgement-echo-check")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--json-output", "--json", "as_json", is_flag=True)
def judgement_echo_check(plan_dir: str, as_json: bool):
    """Prove the trigger echoes, by EXTERNAL OBSERVATION (Issue 5.1).

    Reads `log.md`, invokes the trigger **as a subprocess**, reads `log.md` again, and
    reports `lines_added` and `added_line` from the difference. Nothing here trusts anything
    the trigger says about itself: a self-report from the component under test is exactly the
    evidence standard `detected_by` exists to make visible.

    The subprocess is deliberate rather than an in-process call. An in-process call would
    still be green if `review-loop-check` stopped invoking the echo and this verb invoked it
    directly — which is the removal Epic 5 exists to detect.
    """
    pdir = Path(plan_dir)
    log = pdir / "log.md"
    before = log.read_text(encoding="utf-8").splitlines() if log.exists() else []

    proc = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "review-loop-check",
         str(pdir), "--json"],
        capture_output=True, text=True,
    )
    after = log.read_text(encoding="utf-8").splitlines() if log.exists() else []

    # A MULTISET difference, not a membership test. `ln not in before` silently reports ZERO
    # lines added when the appended line is IDENTICAL to one already in the log — which is the
    # ordinary case, since a second invocation on the same day writes the same bullet. The
    # membership form made this verb report its own failure on every re-run.
    added = list((Counter(after) - Counter(before)).elements())
    judgement_lines = [ln for ln in added if "judgement: " in ln]
    result = {
        "plan_dir": str(pdir),
        "trigger": "review-loop-check",
        "trigger_exit": proc.returncode,
        "lines_added": len(judgement_lines),
        "added_line": judgement_lines[0] if judgement_lines else None,
        "all_added_lines": added,
        "verdict": "PASS" if len(judgement_lines) == 1 else "FAIL",
        "remediation": None if len(judgement_lines) == 1 else (
            "the trigger wrote no `judgement:` echo to log.md. A trigger whose non-firing is "
            "indistinguishable from a quiet period is not shippable (plan-059 SC6). Restore "
            "the `_judgement_echo` call in `review-loop-check`."
        ),
    }
    click.echo(json.dumps(result, indent=2))
    raise SystemExit(0 if result["verdict"] == "PASS" else 1)


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
    # plan-059 Issue 3.1 (REQ-PLAN-082). The escalation PAYLOAD, emitted on BOTH paths and
    # under the top-level key `escalation`. Bound to THIS command rather than to a new
    # `/yf-judgement` surface because EXP-001 measured this invocation path at 4/5 and the
    # measured rate of a freshly-added manually-invoked surface at 0 — #145's finding 4.
    #
    # The exit-3 contract below is UNCHANGED. A payload that altered it would break every
    # caller that already branches on the code.
    result["escalation"] = _review_loop_escalation(pdir, escalates, cycles, limit)
    # plan-059 Issue 5.1. The trigger writes its OWN echo, unconditionally, on both paths —
    # so its non-firing is distinguishable from a quiet period without anyone remembering to
    # look. This is the only remedy in Epic 5 that sits at the top of the
    # command-vs-obligation table.
    result["judgement_echo"] = _judgement_echo(
        pdir, escalates,
        f"review-loop-check: {cycles}/{limit} cycle(s), "
        f"{'ESCALATING (stop class 4)' if escalates else 'converging'}",
    )
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


# ==========================================================================================
# LANDING — `land` (REQ-CLI-030, spec/landing.md `REQ-LAND-*`, plan-060)
# ==========================================================================================
#
# THREE LAYERS, AND ONLY THE THIRD WRITES (REQ-LAND-001):
#
#   land --dry-run            -> the MANIFEST   (facts; reads only)
#   the `lander` agent        -> the DECISION   (judgements; read-only against the repo)
#   land --apply <decision>   -> the EXECUTION  (the only writer, invoked BY THE OPERATOR)
#
# `--apply` trusts the decision for JUDGEMENTS ONLY and for NO FACT WHATSOEVER: every fact is
# re-derived at apply time and checked against the `manifest_digest` the decision carries
# (REQ-LAND-002). A decision that disagrees with re-derived reality HALTS; it never overrides.
#
# NOT TO BE CONFUSED WITH `upstream.py land`, which is the close-time follow-on hoist. Two
# different operations on two different objects (plan-060 R11).

LAND_SCHEMA_MANIFEST = "yf-plan/landing-manifest@1"
LAND_SCHEMA_DECISION = "yf-plan/landing-decision@1"

#: The twenty ordered steps (REQ-LAND-004). The key set of a decision's `steps` object is
#: EXACTLY this, one-to-one with the L-labels — never a coarse paraphrase, which cannot
#: express a two-push order and would make `merge: skip` legal.
LAND_STEPS: tuple[str, ...] = (
    "l0_lock_acquire", "l1_down_merge", "l2_merge", "l3_validate_merged",
    "l4_commit_merge", "l5_advisory_recheck", "l6_push_one", "l7_reconcile_writes",
    "l8_close_chain_head", "l9_close_reconcile_step", "l10_verify_reconcile",
    "l11_recheck_criteria", "l12_close_cascade", "l13_complete_gate",
    "l14_pour_fidelity", "l15_update_status", "l16_commit_and_push_two",
    "l17_residual_mirroring", "l18_prune", "l19_redeploy",
)

#: Steps a decision may NOT skip, each for a stated reason rather than by blanket rule.
#: L0-L6 plus L16 — the last because skipping it reproduces D-2's measured residue exactly:
#: the uncommitted, unpushed `status: complete` this whole capability exists to remove.
LAND_NON_SKIPPABLE: frozenset[str] = frozenset({
    "l0_lock_acquire", "l1_down_merge", "l2_merge", "l3_validate_merged",
    "l4_commit_merge", "l5_advisory_recheck", "l6_push_one", "l16_commit_and_push_two",
})

#: The journal state set (REQ-LAND-006). CLOSED and NORMATIVE — `spec/landing.md` names the
#: same seventeen, and `test_land_apply.py` asserts the two agree. They are enumerated in ONE
#: place because `okf_hygiene`'s R2/SC11/test-suite all keyed on "a set of five" that no
#: document listed, so a five-state test and a five-state journal could have been five
#: DIFFERENT fives with every instrument green.
LAND_JOURNAL_STATES: dict[str, str] = {
    "L_INIT": "journal created; nothing acquired, nothing mutated",
    "L_LOCKED": "landing lock held; no tree mutated",
    "L_DOWNMERGED": "target down-merged into <plan-id>-execute",
    "L_MERGED_UNCOMMITTED": "merge present on the target, uncommitted",
    "L_VALIDATED": "FULL tier green; merge committed; lock released",
    "L_PREPUSH_CHECKED": "advisory criteria run complete — the last fully reversible state",
    "L_PUSHED_1": "push #1 done — the irreversible boundary has been crossed",
    "L_RECONCILED": "every enumerated gh write posted and verified by read-back",
    "L_CLOSED": "close chain L8-L15 complete; status: complete written",
    "L_PUSHED_2": "plan-folder writes committed and pushed",
    "L_MIRRORED": "residual open beads mirrored or proposed",
    "L_PRUNED": "worktree, branch and (if authorized) tab pruned",
    "L_DONE": "redeploy performed or correctly skipped — the terminal GREEN state",
    # Conflict states — ONE PER SITE, and there are exactly four (REQ-LAND-006 §3.2).
    # Their recoveries are NOT uniform, which is why they are four states and not one.
    "L_CONFLICT_DOWNMERGE": "L1 down-merge conflicted — capture, then merge --abort",
    "L_CONFLICT_MERGE": "L2 merge conflicted — capture, then merge --abort",
    "L_REJECTED_PUSH_1": "L6 push #1 rejected — pull --rebase, RE-VALIDATE, retry",
    "L_REJECTED_PUSH_2": "L16 push #2 rejected — pull --rebase and retry, NEVER revert",
}

#: The terminal GREEN state. A rehearsal that halted at L2 must not satisfy R1's mitigation,
#: so this is named rather than inferred from "no error" (SC36b).
LAND_TERMINAL_STATE = "L_DONE"

#: Halt classes, so a session's stop is signalled MECHANICALLY rather than judged from the
#: prose of a `reason` string (REQ-CLI-030). These are REQ-AGENT-064's five classes.
LAND_HALT_OUTWARD = 1
LAND_HALT_GATE = 2
LAND_HALT_DESTRUCTIVE = 3
LAND_HALT_COUNTER = 4
LAND_HALT_MECHANICAL = 5


def _land_envelope(verdict: str, reason: str, remediation: str | None = None,
                   halt_class: int | None = None, **extra) -> dict:
    """The REQ-COMPLETE-003 envelope, extended with `halt_class` (REQ-CLI-030).

    `verdict` is THREE-VALUED and an `inconclusive` is NEVER coerced to `fail` — the defect
    #262 records inside `_validate_merged`, the helper this verb calls, must not be
    reproduced one call frame up.
    """
    if verdict not in ("pass", "fail", "inconclusive"):
        raise ValueError(f"verdict must be three-valued, got {verdict!r}")
    env = {
        "verdict": verdict,
        "passed": verdict == "pass",
        "reason": reason,
        "remediation": remediation,
    }
    if halt_class is not None:
        env["halt_class"] = halt_class
    env.update(extra)
    return env


def _land_exit_code(verdict: str) -> int:
    """`pass` -> 0, `fail` -> 1, `inconclusive` -> 2. The tty refusal's 3 is returned by the
    gate itself (REQ-LAND-014) and never routed through here, because it is a GATE SIGNAL
    rather than a verdict: nothing about the landing was measured false (so not 1) and the
    verb ran and reached a definite conclusion (so not 2)."""
    return {"pass": 0, "fail": 1, "inconclusive": 2}[verdict]


def _land_canonical(obj) -> str:
    """Canonical JSON for digesting: sorted keys, no insignificant whitespace."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _land_digest(facts: dict) -> str:
    """`sha256` over the `facts` object ALONE, excluding `generated_at` (REQ-LAND-018).

    IT MUST COVER `predicted_tree` AND THE TARGET TIP. Measured (EXP-006): those are exactly
    the fields that drift when another plan lands between dry-run and apply, so a digest
    omitting them cannot detect the staleness it exists to detect. They live inside `facts`
    and nothing filters them out — asserted by `test_digest_covers_merge_preview` rather
    than trusted to this comment.
    """
    return "sha256:" + hashlib.sha256(_land_canonical(facts).encode("utf-8")).hexdigest()


def _land_enumerate(directory: Path, checkout_root: Path | None = None) -> list[str]:
    """Enumerate the files under `directory`, as repo-relative POSIX paths.

    ISSUE 1.9. SETTLED EMPIRICALLY in `assets/enumeration-spike.md` — six fixture cases,
    every candidate, both cwds, against known answers — AFTER THE PRESCRIPTION WAS WRONG IN
    FIVE CONSECUTIVE PROSE-REASONED ROUNDS. Do not re-derive it from first principles; the
    fixture exists because first principles produced five different wrong answers.

    (a) WHICH QUESTION. *Tracked-ness* and *presence* are DIFFERENT FACTS. `git ls-files`
        answers tracked-ness; `--others` is its exact COMPLEMENT, not a presence fact — so
        NEITHER IS EVER CORRECT ALONE. Each returned 2 of 4 on the fixture. Only their union
        answers "what git considers part of the tree".

    (b) WHICH CHECKOUT. A linked worktree carries a `.git` MARKER FILE, so the primary
        checkout's git reports it as ONE OPAQUE ENTRY and never descends: measured **0** from
        the primary cwd for every git candidate — and STILL 0 with the worktree not
        gitignored at all. That control identifies the cause: the boundary git cannot cross
        is the CHECKOUT boundary, NOT the gitignore boundary. Git crosses a plain gitignored
        directory correctly.

    (c) THE PRESCRIPTION. Prefer `git -C <that checkout> ls-files --cached --others
        --exclude-standard` — a correct, atomic union that handles symlinks as git does and
        excludes ignored junk. Only where the process cannot run inside that checkout, fall
        back to an explicit scoped listing written `find <dir> ! -type d` — NEVER `-type f`,
        which DROPS SYMLINKS — and accept that it counts ignored junk (`.DS_Store` is
        near-certain on macOS).

    (d) NEVER: `ls-files` alone; `--others` alone; any git form from a DIFFERENT checkout; a
        recursive content `grep` (the harness wrapper under-reports across gitignore, and
        `/usr/bin/grep -r` across both roots DOUBLE-COUNTS — 6 logical paths measured twice);
        or `status --porcelain=v2 --ignored`, the one git command returning non-zero from the
        primary cwd (**1**) — and that 1 is the ignored DIRECTORY, not its files.
        `--ignored=matching`, the documented fix for exactly that collapsing, ALSO returns 1.

    (e) AN OMISSION FROM ENUMERATION IS SILENT. It is not a `skip`, so REQ-LAND-002's "every
        skip is surfaced in the consent prompt" guarantee does NOT cover it (REQ-LAND-003).
        The premise this helper originally rested on — that draft bodies are "untracked by
        construction" — is RETIRED: `commit-plan` falsifies it by design.
    """
    directory = Path(directory)
    if not directory.is_dir():
        return []
    root = Path(checkout_root) if checkout_root else _repo_root()

    # (c) THE PREFERRED BRANCH: git plumbing, run INSIDE the checkout that owns `directory`.
    # `--cached` and `--others` together are the union; `--exclude-standard` drops ignored
    # junk. `-z` because a path may contain a newline and a line-split would then invent one.
    r = _run_git(["-C", str(root), "ls-files", "--cached", "--others",
                  "--exclude-standard", "-z", "--", str(directory)], cwd=root)
    if r.returncode == 0:
        names = [n for n in r.stdout.split("\0") if n]
        if names:
            return sorted(set(names))

    # THE FALLBACK, for a process that cannot run inside that checkout. `! -type d`, NEVER
    # `-type f`: the latter drops symlinks, and a symlinked draft is still a draft.
    out: list[str] = []
    for p in directory.rglob("*"):
        if p.is_dir():
            continue
        try:
            out.append(p.relative_to(root).as_posix())
        except ValueError:
            out.append(p.as_posix())
    return sorted(set(out))


def _land_merge_preview(target: str, execute_branch: str,
                        root: Path | None = None) -> dict:
    """Three-way merge probe via `git merge-tree --write-tree` (Issue 1.2).

    Measured: it predicts conflicts at exit 1, emits the merged tree oid at exit 0, and
    leaves `git status --porcelain` EMPTY.

    RECORDED HONESTLY: it DOES create an unreferenced tree object in the object database.
    It is garbage-collectable and observable to nothing, but "the dry run writes nothing at
    all" would be FALSE — so neither this docstring, nor `REQ-LAND-026`, nor any criterion
    claims it. The claim that IS made is that `git status --porcelain` is empty.
    """
    root = root or _repo_root()
    r = _run_git(["merge-tree", "--write-tree", "--name-only", target, execute_branch],
                 cwd=root)
    lines = [ln for ln in r.stdout.splitlines()]
    predicted_tree = lines[0].strip() if lines else None
    conflicts: list[str] = []
    if r.returncode != 0:
        # Non-zero => conflicts. The oid is still the first line; the remainder names the
        # conflicted paths. A blank separator line divides the two on some git versions.
        conflicts = [ln.strip() for ln in lines[1:] if ln.strip()]
        if r.returncode > 1 and not predicted_tree:
            return {"available": False, "conflicts": [], "predicted_tree": None,
                    "changed_paths": [], "touches_skills": False,
                    "error": (r.stderr.strip() or f"merge-tree exited {r.returncode}")}

    changed_paths: list[str] = []
    if predicted_tree:
        d = _run_git(["diff", "--name-only", f"{target}", f"{execute_branch}"], cwd=root)
        if d.returncode == 0:
            changed_paths = [ln for ln in d.stdout.splitlines() if ln]

    return {
        "available": True,
        "conflicts": conflicts,
        "predicted_tree": predicted_tree,
        "changed_paths": changed_paths,
        "touches_skills": any(p.startswith("skills/") for p in changed_paths),
    }


def _land_changed_set(root: Path | None = None) -> list[str]:
    """The landed change set, computed as `HEAD^1..HEAD` — NEVER `<target>...HEAD`.

    ISSUE 1.4 / `REQ-LAND-025` / dixson3/yoshiko-flow#303. The documented `<target>...HEAD`
    expression runs at a moment when `HEAD == <target>`, so it is EMPTY BY CONSTRUCTION and
    `classify-deliverable`'s `path-backed` evidence is structurally unreachable through it.
    `HEAD^1..HEAD` reads the merge's second parent's contribution, which is the set that
    actually landed.

    On a non-merge `HEAD` (`HEAD^1` absent or HEAD having one parent) this returns the
    single commit's own diff, so the helper is total rather than raising on a fast-forward.
    """
    root = root or _repo_root()
    r = _run_git(["rev-list", "--parents", "-n", "1", "HEAD"], cwd=root)
    if r.returncode != 0:
        return []
    parents = r.stdout.split()[1:]
    if not parents:
        return []
    base = parents[0]
    d = _run_git(["diff", "--name-only", f"{base}..HEAD"], cwd=root)
    return [ln for ln in d.stdout.splitlines() if ln] if d.returncode == 0 else []


def _land_number_collisions(plan_id: str, target: str,
                            root: Path | None = None) -> list[str]:
    """Other plan bundles on the merge target sharing this plan's `NNN` (Issue 1.3).

    `REQ-LAND-024` / dixson3/yoshiko-flow#302-B3. Two bundles sharing an `NNN` and differing
    only by hash suffix MERGE CLEANLY — measured, and commented on #302 — so merge-back is
    the ONLY place the collision is detectable at all. Reported as a HALTING finding.

    Scoped deliberately to the detection half: `get_next_index()`'s `max+1` and the
    cross-worktree fixes (#302 B1/B2) are Phase-1 concerns and stay open.
    """
    root = root or _repo_root()
    m = re.match(r"^plan-(\d+)-", plan_id)
    if not m:
        return []
    number = m.group(1)
    r = _run_git(["ls-tree", "-d", "--name-only", target, "docs/plans/"], cwd=root)
    if r.returncode != 0:
        return []
    out = []
    for line in r.stdout.splitlines():
        leaf = line.rstrip("/").split("/")[-1]
        if leaf == plan_id:
            continue
        if re.match(rf"^plan-{number}-", leaf):
            out.append(leaf)
    return out


def _land_upstream_facts(plan_dir: Path, plan_id: str) -> dict:
    """The Upstream Issues rows with their per-disposition contract and current state.

    THE CONTRACT IS READ FROM `UPSTREAM_REQUIREMENTS`, NOT DISCOVERED (D-6). The `lander`
    agent is trusted to EXPLAIN that a `partial` row stays open, never to work it out — which
    makes what must be trusted materially narrower than #301 assumes.
    """
    plan_md = plan_dir / "plan.md"
    if not plan_md.is_file():
        return {"rows": [], "tracker": None,
                "inconclusive": f"no plan.md at {plan_md}"}
    rows_in = parse_upstream_rows(plan_md.read_text(encoding="utf-8"))
    drafts_dir = plan_dir / "assets" / "upstream-drafts"
    present = set(_land_enumerate(drafts_dir)) if drafts_dir.is_dir() else set()

    rows = []
    tracker = None
    for r in rows_in:
        disp = (r.get("disposition") or "").strip().lower()
        req = UPSTREAM_REQUIREMENTS.get(disp, {})
        if disp == "tracker":
            tracker = {"issue": r.get("issue")}
        if disp == "exclude":
            continue
        draft_rel = f"{plan_dir.as_posix()}/assets/upstream-drafts/{r.get('issue')}.md"
        rows.append({
            "issue": r.get("issue"),
            "disposition": disp,
            "required_end_state": req.get("end_state"),
            "state_reason": req.get("state_reason"),
            "requires_mention": bool(req.get("requires_mention")),
            "report_only": bool(req.get("report_only")),
            "why": req.get("why"),
            "resolved_by": r.get("resolved_by"),
            "draft_body_path": draft_rel,
            # ENUMERATED, never assumed. An omission here is SILENT (REQ-LAND-003) — it is
            # not a `skip`, so the consent-prompt guarantee does not cover it.
            "draft_present": draft_rel in present,
        })
    return {"rows": rows, "tracker": tracker}


def _land_manifest(plan_dir: str | Path) -> dict:
    """The `land --dry-run` MANIFEST — the `facts` object of `assets/decision-schema.md` §1.

    A PURE READ (`REQ-LAND-026`): it changes no ref, no file and no working-tree state, and
    performs no `git merge` into the working tree. The one exception is recorded rather than
    hidden — see `_land_merge_preview` on the unreferenced ODB tree object.

    THE FULL TIER IS NOT RUN HERE. It exceeds 300 s (D-8) and its result is only meaningful
    against a real merge; the manifest reports that it WILL run at L3, never its outcome.
    """
    plan_dir = Path(plan_dir)
    plan_id = _plan_id_from_dir(plan_dir)
    root = _repo_root()
    halts: list[dict] = []

    scan = _resume_scan(plan_dir) if plan_dir.is_dir() else {}
    strategy = _resolve_landing_strategy()
    target = "main" if strategy == "main" else _feature_branch(plan_id)
    execute_branch = _execute_branch(plan_id)
    wt = _worktree_path(plan_dir)

    if scan.get("stale_approved"):
        halts.append({
            "code": "stale-approved",
            "detail": "the plan's content changed since approval — the stored fingerprint no "
                      "longer matches. Re-approve through conformance -> red-team -> "
                      "portability before landing.",
            "resolvable_by_agent": False,
        })

    tip = _run_git(["rev-parse", target], cwd=root)
    resolved_tip = tip.stdout.strip() if tip.returncode == 0 else None
    if resolved_tip is None:
        halts.append({"code": "target-unresolved",
                      "detail": f"merge target {target!r} does not resolve",
                      "resolvable_by_agent": False})

    br = _run_git(["rev-parse", "--verify", execute_branch], cwd=root)
    if br.returncode != 0:
        halts.append({"code": "execute-branch-missing",
                      "detail": f"{execute_branch} does not exist — nothing to land",
                      "resolvable_by_agent": False})

    preview = (_land_merge_preview(target, execute_branch, root)
               if resolved_tip and br.returncode == 0
               else {"available": False, "conflicts": [], "predicted_tree": None,
                     "changed_paths": [], "touches_skills": False})
    if preview.get("conflicts"):
        halts.append({"code": "merge-conflicts-predicted",
                      "detail": "the preview predicts conflicts in: "
                                + ", ".join(preview["conflicts"]),
                      "resolvable_by_agent": False})

    collisions = _land_number_collisions(plan_id, target, root) if resolved_tip else []
    if collisions:
        halts.append({
            "code": "plan-number-collision",
            "detail": (f"the merge target already carries {', '.join(collisions)}, which "
                       f"share this plan's number. Two such bundles MERGE CLEANLY, so this "
                       f"is the only point the collision is detectable (#302-B3)."),
            "resolvable_by_agent": False,
        })

    facts = {
        "plan": {
            "plan_id": plan_id,
            "plan_dir": plan_dir.as_posix(),
            "status": _land_plan_status(plan_dir) if plan_dir.is_dir() else None,
            "fingerprint_fresh": not scan.get("stale_approved", False),
            "epic": scan.get("epic_id"),
            "epic_state": scan.get("epic_state"),
        },
        "git": {
            "landing_strategy": strategy,
            "merge_target": target,
            "execute_branch": execute_branch,
            "worktree_path": wt.as_posix(),
            "worktree_dirty": bool(_worktree_dirty(wt)) if wt.is_dir() else False,
            # DIGEST-COVERED, and deliberately so: measured, the predicted tree oid and the
            # target tip are EXACTLY the fields that drift when another plan lands between
            # dry-run and apply. A digest omitting them cannot detect the staleness it
            # exists to detect (Issue 1.5 / REQ-LAND-018).
            "resolved_target_tip": resolved_tip,
            "merge_preview": preview,
            "plan_number_collisions": collisions,
        },
        "upstream": _land_upstream_facts(plan_dir, plan_id),
        "steps": {k: ("non-skippable" if k in LAND_NON_SKIPPABLE else "skippable")
                  for k in LAND_STEPS},
        "journal_states": sorted(LAND_JOURNAL_STATES),
    }
    return {"facts": facts, "halts": halts}


def _land_plan_status(plan_dir: Path) -> str | None:
    """The plan's `**Status:**` field, read from a plan DIRECTORY.

    NAMED `_land_*`, and the prefix is load-bearing rather than cosmetic. An earlier draft
    called this `_read_plan_status`, which SHADOWED an existing module-level function of that
    name taking plan.md TEXT — Python simply rebinds, so the later definition silently won and
    `_open_escalation_findings` started passing a `str` where a `Path` was now expected. The
    house `_land_*` prefix on every helper this capability adds is what makes that collision
    class impossible by construction; it was caught by `test_audit_close.py`, not by review.
    """
    p = plan_dir / "plan.md"
    if not p.is_file():
        return None
    m = re.search(r"^\*\*Status:\*\*\s*(\S+)", p.read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


def _land_apply_command(plan_dir: Path, decision_path: str = "<decision.json>") -> str:
    """The FULLY-QUALIFIED `--apply` command the operator runs IN THEIR OWN SHELL.

    ISSUE 1.7 / `REQ-LAND-010`/`REQ-LAND-013`. It names the checkout it must be run from,
    because an ambiguous cwd is the difference between merging in the primary checkout and
    attempting it in a worktree that CANNOT check out the target branch — L2 checks out the
    merge target, and a linked worktree cannot hold a branch another worktree holds.
    """
    return (f"cd {_land_primary_checkout()} && "
            f"uv run skills/yf-plan/scripts/plan_manager.py land "
            f"--apply {decision_path} {plan_dir.as_posix()}")


def _land_primary_checkout() -> Path:
    """The PRIMARY checkout, even when called from inside a linked worktree.

    `_repo_root()` answers "the top level of the checkout I am in", which inside
    `.worktrees/<plan-id>` is the WORKTREE — and naming that in the `--apply` command would
    be precisely Issue 1.7's failure: L2 checks out the merge target, and a linked worktree
    CANNOT check out a branch another worktree holds, so the operator would be handed a
    command that cannot work.

    `--git-common-dir` is the discriminator: in the primary it is `<root>/.git`, and in a
    linked worktree it STILL points at the primary's `.git`, because that is where the shared
    object store and refs live. Its parent is therefore the primary checkout from either
    address space. Measured live during Issue 1.7 — the first dry run emitted the worktree
    path and this helper is the fix.
    """
    r = _run_git(["rev-parse", "--path-format=absolute", "--git-common-dir"])
    if r.returncode == 0 and r.stdout.strip():
        common = Path(r.stdout.strip())
        if common.name == ".git":
            return common.parent
    return _repo_root()


def _land_validate_decision(decision: dict, manifest: dict) -> dict:
    """Report-only conformance of a decision document against a re-derived manifest.

    ISSUE 2.3 / `REQ-LAND-002`. Checks, in order: schema tag, `manifest_digest` equality,
    the `steps` key set, the non-skippable set, `body_sha256` per enumerated write, and the
    NARROWING-ONLY rule. WRITES NOTHING.

    A DECISION CAN ONLY EVER NARROW. An `enable` on a step the manifest halted is IGNORED
    and REPORTED — never honoured — so "the landing did less than you think" is never
    silent, and no field the agent controls can widen what happens.
    """
    problems: list[str] = []
    ignored_enables: list[str] = []

    if decision.get("schema") != LAND_SCHEMA_DECISION:
        problems.append(f"schema is {decision.get('schema')!r}, "
                        f"expected {LAND_SCHEMA_DECISION!r}")

    want = _land_digest(manifest["facts"])
    got = decision.get("manifest_digest")
    digest_ok = (got == want)
    if not digest_ok:
        problems.append(
            f"manifest_digest MISMATCH — decision carries {got!r}, re-derived reality is "
            f"{want!r}. The world moved under this decision; re-run `land --dry-run` and "
            f"re-adjudicate. This is a HALT, never an override.")

    steps = decision.get("steps")
    if not isinstance(steps, dict):
        problems.append("`steps` is missing or not an object")
        steps = {}
    else:
        missing = [k for k in LAND_STEPS if k not in steps]
        extra = [k for k in steps if k not in LAND_STEPS]
        if missing:
            problems.append(f"`steps` omits {missing} — the key set is one-to-one with the "
                            f"L0-L19 labels, never a coarse paraphrase")
        if extra:
            problems.append(f"`steps` carries unknown keys {extra}")

    for k, v in steps.items():
        if k in LAND_NON_SKIPPABLE and isinstance(v, str) and v.startswith("skip"):
            problems.append(
                f"{k} is NON-SKIPPABLE and the decision skips it. Skipping it is not "
                f"narrowing the landing — it is a different operation.")
        if isinstance(v, str) and v.startswith("skip") and ":" not in v:
            problems.append(f"{k} is skipped without a reason; `skip` requires one")

    # NARROWING-ONLY, over the halts the manifest reports. An `enable` here is not an error
    # in the decision — it is simply not honoured, and saying so is the whole guarantee.
    if manifest.get("halts"):
        for k, v in steps.items():
            if v == "enable":
                ignored_enables.append(k)

    body_problems: list[str] = []
    for w in decision.get("upstream_writes", []) or []:
        bp = w.get("body_path")
        if not bp:
            continue
        f = Path(bp)
        if not f.is_file():
            body_problems.append(f"issue {w.get('issue')}: body_path {bp} does not exist")
            continue
        want_sha = w.get("body_sha256")
        if want_sha:
            got_sha = hashlib.sha256(f.read_bytes()).hexdigest()
            if got_sha != want_sha:
                body_problems.append(
                    f"issue {w.get('issue')}: body_sha256 mismatch — the bytes changed "
                    f"between consent and apply, which makes this a DIFFERENT write")
    problems += body_problems

    if problems:
        return _land_envelope(
            "fail",
            f"decision is not conformant: {len(problems)} problem(s)",
            remediation="Re-run `land --dry-run`, re-adjudicate with the `lander`, and "
                        "re-validate. A non-conformant decision is never applied.",
            halt_class=LAND_HALT_MECHANICAL,
            problems=problems, digest_ok=digest_ok,
            ignored_enables=ignored_enables)
    return _land_envelope(
        "pass", "decision is conformant and narrowing-only",
        digest_ok=digest_ok, problems=[], ignored_enables=ignored_enables)


@cli.command("land")
@click.argument("plan_dir", type=click.Path(exists=True))
@click.option("--dry-run", "dry_run", is_flag=True,
              help="Emit the MANIFEST — facts only. Writes nothing.")
@click.option("--apply", "apply_path", type=click.Path(), default=None,
              help="Execute the landing per <decision.json>. THE ONLY WRITING MODE.")
@click.option("--validate-decision", "validate_path", type=click.Path(), default=None,
              help="Report-only conformance of <decision.json>. Writes nothing.")
@click.option("--json-output", "--json", "json_output", is_flag=True, default=True,
              help="Emit the structured verdict (default).")
def land_cmd(plan_dir: str, dry_run: bool, apply_path: str | None,
             validate_path: str | None, json_output: bool):
    """Land an executed plan: merge, validate, push, reconcile, close, prune, redeploy.

    REGISTERED FLAT, NOT AS A GROUP (REQ-CLI-030 / REQ-CLI-021), and the reason is
    mechanical rather than stylistic: a group's subcommands are registered on the group, so
    a `land` GROUP would escape `test_cli_enumeration.py`'s set-equality check entirely —
    exactly as `fingerprint`, `worktree` and `landing-lock` already do. A verb that governs
    merging and pushing is the last one that should be outside the check that notices it
    exists.

    THE THREE MODES ARE MUTUALLY EXCLUSIVE and only `--apply` writes.

    NOT `upstream.py land`, which is the close-time follow-on hoist (plan-060 R11).
    """
    pdir = Path(plan_dir)
    modes = [bool(dry_run), apply_path is not None, validate_path is not None]
    if sum(modes) != 1:
        click.echo(json.dumps(_land_envelope(
            "inconclusive",
            "exactly one of --dry-run / --apply / --validate-decision is required",
            remediation="Re-invoke with exactly one mode.",
        ), indent=2))
        sys.exit(2)

    manifest = _land_manifest(pdir)

    if dry_run:
        facts = manifest["facts"]
        halts = manifest["halts"]
        verdict = "fail" if halts else "pass"
        env = _land_envelope(
            verdict,
            ("landing is blocked by " + ", ".join(h["code"] for h in halts)) if halts
            else "manifest computed; no halting finding",
            remediation=(halts[0]["detail"] if halts else None),
            halt_class=LAND_HALT_MECHANICAL if halts else None,
        )
        env.update({
            "schema": LAND_SCHEMA_MANIFEST,
            "digest": _land_digest(facts),
            "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "facts": facts,
            "halts": halts,
            # THE SESSION PRINTS THIS AND STOPS (REQ-LAND-013). It does not run it.
            "apply_command": _land_apply_command(pdir),
            "apply_note": (
                "REQ-LAND-013: the session does NOT invoke --apply. Run the command above "
                "yourself, from the checkout it names. `land --apply` additionally refuses "
                "without a controlling terminal (REQ-LAND-014, exit 3) — which is a "
                "DETECTION control, not prevention: `herdr pane run` is a known bypass."),
        })
        click.echo(json.dumps(env, indent=2))
        sys.exit(_land_exit_code(verdict))

    if validate_path is not None:
        p = Path(validate_path)
        if not p.is_file():
            click.echo(json.dumps(_land_envelope(
                "inconclusive", f"no decision document at {validate_path}",
                remediation="Produce one with the `lander` agent first."), indent=2))
            sys.exit(2)
        try:
            decision = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            click.echo(json.dumps(_land_envelope(
                "inconclusive", f"decision document is not valid JSON: {exc}",
                remediation="Re-emit the decision document."), indent=2))
            sys.exit(2)
        env = _land_validate_decision(decision, manifest)
        click.echo(json.dumps(env, indent=2))
        sys.exit(_land_exit_code(env["verdict"]))

    # --apply: the only writing mode.
    #
    # REQ-LAND-010 IS CHECKED FIRST, before the tty gate and before anything is read: running
    # from the wrong checkout means every plan-folder read is against a stale bundle, and no
    # later step can recover from having been given the wrong tree to begin with.
    where = _land_assert_primary_checkout()
    if not where["ok"]:
        click.echo(json.dumps(_land_envelope(
            "fail", where["reason"], remediation=where["remediation"],
            halt_class=LAND_HALT_MECHANICAL, cwd=where["cwd"],
            primary_checkout=where["primary"]), indent=2))
        sys.exit(1)

    # The terminal gate is checked next, before anything is written, so a refusal cannot be
    # preceded by a write.
    gate = _land_tty_gate()
    if not gate["allowed"]:
        click.echo(json.dumps(_land_envelope(
            "fail", gate["reason"],
            remediation=gate["remediation"],
            halt_class=LAND_HALT_OUTWARD,
            route_record=gate["route_record"]), indent=2))
        sys.exit(3)
    # ---- THE SEAM (REQ-LAND-028, dixson3/yoshiko-flow#327) --------------------------------
    #
    # Everything above this line was already here; what was missing was the CALL. `_land_execute`
    # drove all fifteen steps, advanced the journal and was fail-closed, while having exactly one
    # occurrence in this file — its own `def`. `--apply` returned an unconditional stub, so the
    # sole writing mode of the landing capability could land nothing.
    #
    # Read the decision. Reading it here rather than earlier is deliberate: `--apply` must not
    # touch the filesystem before the tty gate has allowed the run.
    ap = Path(apply_path)
    if not ap.is_file():
        click.echo(json.dumps(_land_envelope(
            "inconclusive", f"no decision document at {apply_path}",
            remediation="Produce one with the `lander` agent, then `--validate-decision` it.",
            halt_class=LAND_HALT_MECHANICAL), indent=2))
        sys.exit(2)
    try:
        decision = json.loads(ap.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        click.echo(json.dumps(_land_envelope(
            "inconclusive", f"decision document is not valid JSON: {exc}",
            remediation="Re-emit the decision document.",
            halt_class=LAND_HALT_MECHANICAL), indent=2))
        sys.exit(2)

    # THE JOURNAL DECIDES WHETHER THIS IS A START OR A RESUME (REQ-LAND-009), never observed
    # state. `recover()` is TOTAL over the seventeen states, so all four of its actions are
    # branched on here — an unhandled action would silently become a fresh landing, which is
    # the one wrong answer that can re-push and re-post.
    journal = LandingJournal(_land_primary_checkout(), _plan_id_from_dir(pdir))
    rec = journal.recover()
    action = rec.get("action")

    if action == "done":
        click.echo(json.dumps(_land_envelope(
            "pass", rec["reason"], journal_phase=rec.get("phase"),
            remediation=None), indent=2))
        sys.exit(0)
    if action == "halt":
        # A CORRUPT OR CONFLICTED JOURNAL IS INCONCLUSIVE, NOT A FAILED LANDING. Nothing about
        # the landing was measured false; the journal could not be read, or a previous run left
        # a conflict a human must resolve.
        click.echo(json.dumps(_land_envelope(
            "inconclusive", rec["reason"],
            remediation=rec.get("remediation") or rec.get("recovery"),
            halt_class=LAND_HALT_MECHANICAL,
            journal_phase=rec.get("phase")), indent=2))
        sys.exit(2)

    resume_from = rec.get("resume_after") if action == "resume" else None

    # RE-DERIVE AND RE-CHECK BEFORE ANY WRITE (REQ-LAND-002 / REQ-LAND-011). The decision is
    # trusted for JUDGEMENTS only and for no fact whatsoever, so a decision minted against a
    # target that has since moved halts as a legible staleness report — before the merge is
    # attempted, never as a conflicted tree discovered afterwards.
    bind = _land_repreview_or_halt(pdir, decision)
    if not bind["proceed"]:
        click.echo(json.dumps(_land_envelope(
            "fail", bind["reason"], remediation=bind["remediation"],
            halt_class=bind["halt_class"], stale=bind["stale"],
            digest=bind["digest"], problems=bind.get("problems", []),
            journal_phase=rec.get("phase")), indent=2))
        sys.exit(1)

    # `manifest` is ALREADY IN SCOPE — computed above for every mode. Re-deriving it here would
    # compute the same facts a second time and, worse, invite the two copies to drift.
    ctx = LandingContext(pdir, decision, manifest)
    out = _land_execute(ctx, resume_from=resume_from)

    # ---- THE VERDICT IS THREE-VALUED, DERIVED FROM THE RESULTS (REQ-LAND-012) -------------
    #
    # `halted -> fail / reached_terminal_state -> pass` is WRONG. L8's and L12's `inconclusive`
    # results are explicitly NON-HALTING, so a landing can reach `L_DONE` carrying one, and
    # laundering that into `pass` is exactly the coercion REQ-LAND-012 forbids.
    results = out.get("results", [])
    inconclusive = [r for r in results if r.get("verdict") == "inconclusive"]
    if out.get("halted"):
        verdict, reason = "fail", out.get("reason", "the landing halted")
    elif inconclusive:
        verdict = "inconclusive"
        reason = ("the landing reached its terminal state, but "
                  f"{len(inconclusive)} step(s) could not be measured: "
                  + ", ".join(sorted({r['step'] for r in inconclusive})))
    elif out.get("reached_terminal_state"):
        verdict, reason = "pass", "the landing reached L_DONE with every step measured"
    else:
        # Not halted, not terminal, nothing inconclusive: the executor ran to the end of the
        # table without recording the terminal state. That is a statement about the INSTRUMENT.
        verdict = "inconclusive"
        reason = ("the executor completed without halting but did not record the terminal "
                  f"state (journal phase {out.get('journal_phase')!r})")

    env = _land_envelope(
        verdict, reason,
        remediation=out.get("recovery") if out.get("halted") else None,
        halt_class=LAND_HALT_MECHANICAL if out.get("halted") else None,
        halted=bool(out.get("halted")),
        halted_at=out.get("at"),
        resumed_from=resume_from,
        journal_phase=out.get("journal_phase"),
        reached_terminal_state=bool(out.get("reached_terminal_state")),
        steps_executed=out.get("steps_executed", []),
        inconclusive_steps=sorted({r["step"] for r in inconclusive}),
        results=results,
    )
    click.echo(json.dumps(env, indent=2))
    sys.exit(_land_exit_code(verdict))


def _land_route_record() -> dict:
    """The ROUTE RECORD (`REQ-LAND-015`, Issue 3.4) — stamped on every `--apply` and every
    gate close: the controlling tty or its absence, `CLAUDECODE`/entrypoint presence, pid,
    sid.

    THIS IS DETECTION, NOT PREVENTION, and the phrase is in the requirement text verbatim.
    The markers are strippable. They are useful because they are strippable ASYMMETRICALLY:
    a clean record is WEAK evidence of a human, a dirty one is STRONG evidence of an agent.
    It would have surfaced dixson3/yoshiko-flow#293 within seconds.

    Reads only the NAMES of the agent-marker variables and records presence as a boolean —
    it never captures a value, so no secret can reach the record.
    """
    try:
        tty = os.ttyname(0)
    except OSError:
        tty = None
    try:
        sid = os.getsid(0)
    except OSError:
        sid = None
    agent_markers = sorted(
        k for k in ("CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "OPENCODE", "PI_CODING_AGENT",
                    "CURSOR_TRACE_ID", "HERDR_PANE_ID")
        if os.environ.get(k)
    )
    return {
        "tty": tty,
        "has_tty": tty is not None,
        "agent_markers": agent_markers,   # NAMES ONLY — never a value
        "pid": os.getpid(),
        "ppid": os.getppid(),
        "sid": sid,
        "stamped_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "note": "detection, not prevention — the markers are strippable, but asymmetrically",
    }


def _land_route_record_is_agent(rr: dict) -> bool:
    """Does this route record show an AGENT resolved something? (REQ-LAND-015)

    ONE predicate, used by every caller, because two copies of an asymmetric rule drift and
    the drift is invisible. The rule: NO controlling terminal AND at least one agent marker.

    THE ASYMMETRY IS THE WHOLE VALUE. `False` means "not detected", NEVER "a human did it" —
    the markers are strippable, so a clean record is weak evidence. `True` is strong: nothing
    sets `CLAUDECODE` and removes the controlling terminal by accident. Detection, not
    prevention.
    """
    return bool(rr) and rr.get("has_tty") is False and bool(rr.get("agent_markers"))


def _land_tty_gate(allow_list: list[str] | None = None) -> dict:
    """The controlling-terminal gate on `land --apply` (`REQ-LAND-014`, Issue 3.3).

    PURE POSIX, and deliberately nothing more: refuse when `os.ttyname(0)` raises OR
    `/dev/tty` is not openable. Measured inside a Claude Code Bash subprocess, `/dev/tty` is
    NOT openable (`OSError [Errno 6] Device not configured`), so the gate refuses an agent by
    default; being POSIX-only it is portable across harnesses rather than Claude-specific.

    THE REFUSAL IS EXIT 3 — the gate-signal code. Not 1: nothing about the landing was
    measured false, and banking a 3 as a red observation would be a false statement about the
    plan. Not 2: the verb ran perfectly and reached a definite conclusion — *this caller may
    not do this*. Collapsing it into either is #263's two-facts-one-signal defect, and a
    caller retrying on a 2 would loop forever against a gate that never opens on retry.

    THIS IS NOT PREVENTION, and the requirement says so in its own text. `herdr pane run
    <pane> <cmd>` runs a command in a pane with a GENUINE PTY in ONE SANCTIONED TOOL CALL,
    and is named here as a KNOWN BYPASS — materially cheaper than the `pty.fork()` evasion
    EXP-005 priced at ~15 lines. The gate converts self-authorization from a RATIONALIZABLE
    act into an UNMISTAKABLE one, and nothing more.

    ANY ALLOW-LIST IS OPERATOR-CONFIGURED, NEVER HERDR-DERIVED. Measured: `herdr api schema
    --json` contains ZERO occurrences of `human` and ZERO of `attached`, so "a pane herdr
    reports as human-attached" is not a capability herdr has, and such a predicate would
    degrade to matching ANY herdr pane — including one the agent just created.
    """
    record = _land_route_record()

    fd = None
    try:
        fd = os.open("/dev/tty", os.O_RDONLY)
        dev_tty_openable = True
        dev_tty_error = None
    except OSError as exc:
        dev_tty_openable = False
        dev_tty_error = f"{type(exc).__name__} [Errno {exc.errno}] {exc.strerror}"
    finally:
        if fd is not None:
            os.close(fd)

    record["dev_tty_openable"] = dev_tty_openable
    record["dev_tty_error"] = dev_tty_error

    allowed = record["has_tty"] and dev_tty_openable
    if not allowed and allow_list and record.get("tty") in allow_list:
        # OPERATOR-CONFIGURED escape hatch only. Never herdr-derived, never inferred.
        allowed = True
        record["allowed_by"] = "operator-configured allow-list"

    if allowed:
        return {"allowed": True, "reason": "a controlling terminal is present",
                "remediation": None, "route_record": record}

    why = ("no controlling terminal on fd 0" if not record["has_tty"]
           else f"/dev/tty is not openable ({dev_tty_error})")
    return {
        "allowed": False,
        "reason": (f"`land --apply` REFUSED: {why}. This command writes to the default "
                   f"branch, the upstream tracker, the worktree set and the installed "
                   f"toolchain, and must be run by an operator in their own shell "
                   f"(REQ-LAND-013/014)."),
        "remediation": ("Run the `apply_command` printed by `land --dry-run` yourself, in "
                        "an interactive shell. NOTE, stated rather than hidden: this gate "
                        "is DETECTION, not prevention — `herdr pane run <pane> <cmd>` "
                        "produces a genuine pty in one sanctioned call and is a KNOWN "
                        "BYPASS. Using it to self-authorize is not a loophole; it is an "
                        "unmistakable act, which is the whole of what this gate buys."),
        "route_record": record,
    }


# ------------------------------------------------------------------------------------------
# The landing journal (REQ-LAND-006/008/009, Issue 3.1)
# ------------------------------------------------------------------------------------------

#: STAGED INSIDE THE REPO TREE, never a `mktemp -d`. A staging directory on a different
#: filesystem turns `os.rename` into a COPY and voids every durability claim the journal
#: makes — the reason `okf_hygiene` states the same constraint.
LAND_JOURNAL_DIR = ".yf/plan/landing-journal"

# The ALLOWLIST the dirty check exempts, as a PATH PREFIX. `.yf/plan/` covers both the landing
# journal (REQ-LAND-008 stages it inside the tree — a `mktemp -d` would turn `os.rename` into a
# copy and void every durability claim) and `land-beads.json`, which the old substring filter
# did not exempt at all.
LAND_DIRT_ALLOWLIST: tuple[str, ...] = (".yf/plan/",)


def _porcelain_records(out: str) -> list[tuple[str, str]]:
    """Split `git status --porcelain=v1 -uall -z` output into `(status, path)` records.

    NUL-SEPARATED AND UNQUOTED BY CONSTRUCTION. The `-z` form is not a convenience: a `v1`
    line carries a two-character status plus a space, and QUOTES any path containing a space
    or a non-ASCII byte. So a naive `startswith` over raw lines matches nothing, and a naive
    `in` reinstates the substring bug this helper exists to remove.

    A rename/copy record (`R`/`C`) carries TWO NUL-terminated fields — `<new>` then `<orig>`.
    Both are returned, because either one being outside the plan folder is dirt.
    """
    fields = [f for f in out.split("\0") if f != ""]
    records: list[tuple[str, str]] = []
    i = 0
    while i < len(fields):
        rec = fields[i]
        if len(rec) < 4:                     # "XY path" is at minimum 4 chars
            i += 1
            continue
        status, path = rec[:2], rec[3:]
        records.append((status, path))
        if status[0] in ("R", "C") and i + 1 < len(fields):
            records.append((status, fields[i + 1]))
            i += 1
        i += 1
    return records


def _dirty_outside_plan_dir(plan_dir, root=None, runner=None) -> dict:
    """THE SINGLE DEFINITION SITE of "the tree is dirty outside the plan folder"
    (REQ-LAND-033).

    ONE RULE, ONE IMPLEMENTATION, TWO CALLERS: L16's post-condition ENFORCES it and
    `land --dry-run` PREDICTS it (REQ-LAND-034). Two independent implementations of one rule
    is precisely how the dry run stops predicting L16 — the defect this plan exists to close
    — so a second definition site is a regression even when both copies agree today.

    Three clauses, each load-bearing:

    - **`-uall`**: without it git COLLAPSES untracked directories to `?? .yf/`, which contains
      neither the journal path nor `land-beads.json`. No prefix filter can work over a
      collapsed entry, so the switch is a precondition of the filter, not a refinement of it.
    - **the PATH FIELD, not the raw line**: see `_porcelain_records`.
    - **PREFIX, not substring**: the shipped filter exempted any path *containing* the
      fragment anywhere in the line, and did not even exempt the journal it was written for.

    Returns `{"dirty", "paths", "staged", "records"}`. `paths` are the offending paths only —
    the boolean is what the digest carries, the list is what a halt reports (REQ-LAND-036).
    """
    root = root or _git_root()
    prefix = Path(plan_dir).as_posix().rstrip("/") + "/"
    args = ["status", "--porcelain=v1", "-uall", "-z"]
    if runner is not None:
        out = runner("git", args, cwd=root).stdout
    else:
        out = _run_git(args, cwd=root).stdout

    paths, staged = [], []
    for status, path in _porcelain_records(out):
        if path == prefix.rstrip("/") or path.startswith(prefix):
            continue
        if any(path.startswith(a) for a in LAND_DIRT_ALLOWLIST):
            continue
        paths.append(f"{status} {path}")
        # The FIRST column is the index; a non-space, non-`?` value means STAGED.
        if status[0] not in (" ", "?"):
            staged.append(path)
    return {"dirty": bool(paths), "paths": sorted(paths), "staged": sorted(staged),
            "records": len(paths)}



def _land_fsync_write(path: Path, text: str) -> None:
    """Write and FSYNC — the journal must survive the crash it exists to describe.

    Both fsyncs are load-bearing: `fsync(fd)` flushes the bytes, and `fsync(dirfd)` flushes
    the DIRECTORY ENTRY. Without the second, a journal file can be durable in content and
    absent in the directory after a power loss, which is the one outcome a recovery keyed on
    the recorded phase cannot survive.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        os.write(fd, text.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    dfd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


class LandingJournal:
    """A durable record of WHICH ENUMERATED STATE a landing is in (REQ-LAND-006).

    RECOVERY IS KEYED ON THE RECORDED PHASE, NEVER ON OBSERVED STATE (REQ-LAND-009). That
    distinction is the whole mechanism: at several boundaries "wrote nothing" and "wrote
    everything then died" are INDISTINGUISHABLE from the filesystem and from git. A merge
    that was committed and a merge that was never attempted both leave a clean tree once the
    process is gone; only the recorded phase separates them.

    The state set is CLOSED — `LAND_JOURNAL_STATES` — and `spec/landing.md` names the same
    seventeen. `okf_hygiene`'s R2, SC11 and test suite all keyed on "a set of five" that no
    document listed, so a five-state test and a five-state journal could have been five
    DIFFERENT fives with every instrument green. Enumerating once, in one place that the spec
    is asserted against, is what removes that.
    """

    def __init__(self, root: Path, plan_id: str):
        self.root = Path(root)
        self.plan_id = plan_id
        self.path = self.root / LAND_JOURNAL_DIR / f"{plan_id}.json"

    # -- state -----------------------------------------------------------------------------

    def read(self) -> dict | None:
        if not self.path.is_file():
            return None
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            # A CORRUPT JOURNAL IS NOT AN ABSENT ONE. Returning None here would say "nothing
            # started", which is the single most dangerous wrong answer available: it invites
            # a re-run of steps that may already have pushed.
            return {"phase": None, "corrupt": True, "plan_id": self.plan_id}

    def write(self, phase: str, **detail) -> dict:
        if phase not in LAND_JOURNAL_STATES:
            raise ValueError(
                f"{phase!r} is not one of the {len(LAND_JOURNAL_STATES)} enumerated landing "
                f"journal states. The set is CLOSED (REQ-LAND-006); adding a state means "
                f"amending spec/landing.md in the same change-set.")
        prior = self.read() or {}
        rec = {
            "schema": "yf-plan/landing-journal@1",
            "plan_id": self.plan_id,
            "phase": phase,
            "meaning": LAND_JOURNAL_STATES[phase],
            "history": (prior.get("history") or []) + [phase],
            "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "route_record": _land_route_record(),
            "detail": detail,
        }
        _land_fsync_write(self.path, json.dumps(rec, indent=2))
        return rec

    def clear(self) -> None:
        """Remove the journal. Called ONLY after the terminal green state."""
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    # -- recovery --------------------------------------------------------------------------

    def recover(self) -> dict:
        """What a resumed `--apply` should do, derived from the RECORDED PHASE.

        TOTAL over the state set (REQ-LAND-009): every one of the seventeen has a row, and an
        unknown or corrupt phase is INCONCLUSIVE rather than "start over".
        """
        rec = self.read()
        if rec is None:
            return {"action": "start", "phase": None,
                    "reason": "no journal — this is a fresh landing"}
        if rec.get("corrupt"):
            return {"action": "halt", "phase": None, "inconclusive": True,
                    "reason": "the journal is unreadable. A corrupt journal is NOT an absent "
                              "one: treating it as absent would re-run steps that may already "
                              "have pushed.",
                    "remediation": "Inspect the repository state by hand, then either repair "
                                   "the journal or remove it deliberately."}
        phase = rec.get("phase")
        if phase not in LAND_JOURNAL_STATES:
            return {"action": "halt", "phase": phase, "inconclusive": True,
                    "reason": f"recorded phase {phase!r} is not an enumerated state"}

        if phase in LAND_CONFLICT_STATES:
            return {"action": "halt", "phase": phase,
                    "reason": f"the previous run halted at {phase}: "
                              f"{LAND_JOURNAL_STATES[phase]}",
                    "recovery": LAND_CONFLICT_RECOVERY[phase]}
        if phase == LAND_TERMINAL_STATE:
            return {"action": "done", "phase": phase,
                    "reason": "the landing already reached its terminal green state"}

        order = LAND_PROGRESS_ORDER
        nxt = order[order.index(phase) + 1] if phase in order[:-1] else None
        return {"action": "resume", "phase": phase, "resume_after": phase, "next": nxt,
                "reason": f"resume after {phase} ({LAND_JOURNAL_STATES[phase]})",
                # RE-DERIVED, NOT TRUSTED: a resume re-computes the manifest and re-checks the
                # digest before continuing (REQ-LAND-011). The journal says WHERE it was, never
                # WHAT WAS TRUE.
                "must_recheck_digest": True}


#: The progress states IN ORDER. Separate from the conflict states because they form a
#: sequence and the conflict states do not — each of the latter is entered FROM a specific
#: progress state and returns to a DIFFERENT recovery.
LAND_PROGRESS_ORDER: tuple[str, ...] = (
    "L_INIT", "L_LOCKED", "L_DOWNMERGED", "L_MERGED_UNCOMMITTED", "L_VALIDATED",
    "L_PREPUSH_CHECKED", "L_PUSHED_1", "L_RECONCILED", "L_CLOSED", "L_PUSHED_2",
    "L_MIRRORED", "L_PRUNED", "L_DONE",
)

#: The four conflict states and their per-site recovery. THE RECOVERIES ARE NOT UNIFORM, and
#: that non-uniformity is why there are four states rather than one generic "conflicted".
LAND_CONFLICT_RECOVERY: dict[str, str] = {
    "L_CONFLICT_DOWNMERGE":
        "capture from three sources, then `git merge --abort`. Fully local, pre-L6 and "
        "pre-L7: nothing has been pushed and nothing posted, so there is no outward trace.",
    "L_CONFLICT_MERGE":
        "capture from three sources, then `git merge --abort`. Fully local, pre-L6 and "
        "pre-L7 — same recovery as the down-merge, and for the same reason.",
    "L_REJECTED_PUSH_1":
        "`git pull --rebase`, then RE-VALIDATE (re-run the FULL tier), then retry. Still "
        "pre-outward-write. NEVER push an unvalidated rebase.",
    "L_REJECTED_PUSH_2":
        "`git pull --rebase` and retry. NEVER REVERT. By L16 the reconcile comments are "
        "posted (L7), the bead tree is closed (L12) and `status: complete` is written (L15); "
        "reverting would contradict outward statements already made.",
}

LAND_CONFLICT_STATES: frozenset[str] = frozenset(LAND_CONFLICT_RECOVERY)


# ------------------------------------------------------------------------------------------
# The conflict contract (REQ-LAND-017, Issue 3.5) — FOUR sites, NON-UNIFORM recoveries
# ------------------------------------------------------------------------------------------

#: Flags that silently discard one side's work. NEVER PASSED, and enumerated so a test can
#: assert their absence from the merge path rather than trusting a comment.
LAND_FORBIDDEN_MERGE_FLAGS: tuple[str, ...] = (
    "-X", "--strategy-option", "-Xours", "-Xtheirs", "ours", "theirs",
)


def _land_capture_conflict(site: str, root: Path) -> dict:
    """Capture a conflict from THREE INDEPENDENT SOURCES (REQ-LAND-017).

    Three, not one, because they answer different questions and any one alone under-reports:

      * `git diff --name-only --diff-filter=U`  — WHICH PATHS are unmerged
      * `git status --porcelain=v2`             — the PER-PATH STAGE DETAIL (which sides exist)
      * `MERGE_HEAD`                            — WHAT was being merged in

    NEVER AUTO-RESOLVE. No `-X ours`, no `-X theirs`, no strategy override, no heuristic. Each
    silently discards one side's work and the discarding is INVISIBLE in the resulting commit.
    This function's job ends at handing the whole picture back: the verb has no basis for
    choosing, while the agent — holding the plan and both diffs — at least has one.
    """
    if site not in LAND_CONFLICT_STATES:
        raise ValueError(f"{site!r} is not one of the four enumerated conflict states")

    paths = _run_git(["diff", "--name-only", "--diff-filter=U"], cwd=root)
    status = _run_git(["status", "--porcelain=v2"], cwd=root)
    head = _run_git(["rev-parse", "--verify", "MERGE_HEAD"], cwd=root)

    return {
        "site": site,
        "meaning": LAND_JOURNAL_STATES[site],
        "recovery": LAND_CONFLICT_RECOVERY[site],
        # Source 1 — the path list.
        "unmerged_paths": [p for p in paths.stdout.splitlines() if p]
                          if paths.returncode == 0 else [],
        # Source 2 — per-path stage detail. `u ` lines are the unmerged entries.
        "porcelain_v2": [ln for ln in status.stdout.splitlines() if ln.startswith("u ")]
                        if status.returncode == 0 else [],
        # Source 3 — the incoming commit.
        "merge_head": head.stdout.strip() if head.returncode == 0 else None,
        "auto_resolved": False,   # ALWAYS. There is no code path that sets this True.
    }


def _land_abort_merge(root: Path) -> dict:
    """`git merge --abort` — the recovery for the TWO PRE-OUTWARD-WRITE sites only.

    L1 and L2 are fully local: nothing pushed, nothing posted, so aborting leaves no outward
    trace. Measured in the spike, an abort returns the tree to an EMPTY `--porcelain`.

    IT IS THE WRONG RECOVERY FOR L16 AND MUST NOT BE CALLED THERE. By then the reconcile
    comments are posted, the bead tree is closed and `status: complete` is written; reverting
    would contradict outward statements already made. That is why the four sites carry four
    recoveries rather than sharing one.
    """
    r = _run_git(["merge", "--abort"], cwd=root)
    after = _run_git(["status", "--porcelain"], cwd=root)
    return {
        "aborted": r.returncode == 0,
        "tree_clean": after.returncode == 0 and after.stdout.strip() == "",
        "detail": (r.stderr or r.stdout).strip() or None,
    }


# ------------------------------------------------------------------------------------------
# Apply-time re-derivation and the staleness halt (REQ-LAND-002/011/018, Issues 3.2 and 3.6)
# ------------------------------------------------------------------------------------------

def _land_bind_decision(plan_dir: Path, decision: dict) -> dict:
    """Bind a decision to RE-DERIVED reality (Issue 3.2 / REQ-LAND-002).

    Recomputes the manifest and compares digests. A MISMATCH HALTS and routes back to
    `--dry-run`; it is NEVER an override path. This is the single invariant that makes the
    three-layer split load-bearing rather than decorative: the decision is trusted for
    judgements only and for NO FACT WHATSOEVER.
    """
    manifest = _land_manifest(plan_dir)
    env = _land_validate_decision(decision, manifest)
    return {"manifest": manifest, "validation": env,
            "bound": env["verdict"] == "pass",
            "digest": _land_digest(manifest["facts"])}


def _land_repreview_or_halt(plan_dir: Path, decision: dict) -> dict:
    """Re-preview IMMEDIATELY BEFORE the merge and halt on any drift (Issue 3.6).

    A CLEAN PREVIEW DOES NOT GUARANTEE A CLEAN APPLY. Measured: preview clean at T0, the
    target advances, the SAME merge conflicts at T1.

    THE HALT REPORTS A DIGEST MISMATCH RATHER THAN THE BARE CONFLICT, and that framing is the
    deliverable. The predicted merge-tree oid CHANGES when the target moves, so the drift is
    detectable BEFORE the merge is attempted — which turns "a conflicted working tree
    discovered afterwards" into "a legible staleness report before anything was touched".
    """
    bound = _land_bind_decision(plan_dir, decision)
    if bound["bound"]:
        return {"stale": False, "proceed": True, "digest": bound["digest"]}

    env = bound["validation"]
    digest_problem = [p for p in env.get("problems", []) if "MISMATCH" in p]
    return {
        "stale": bool(digest_problem),
        "proceed": False,
        "digest": bound["digest"],
        "halt_class": LAND_HALT_MECHANICAL,
        "reason": (
            "the merge target moved since this decision was minted, so the decision was "
            "adjudicated against facts that no longer hold. Reported as a DIGEST MISMATCH "
            "rather than as a conflict, because the mismatch is detectable BEFORE the merge "
            "is attempted." if digest_problem
            else "the decision is not conformant against re-derived reality"),
        "problems": env.get("problems", []),
        "remediation": ("Re-run `land --dry-run`, re-dispatch the `lander`, and re-validate. "
                        "A stale decision is never applied and never overridden."),
    }


# ==========================================================================================
# THE ORDERED LANDING STEPS L0-L19 (REQ-LAND-004, Epic 4)
# ==========================================================================================
#
# Every step has the SAME SHAPE: it takes the context, returns a verdict dict, and NEVER
# raises for an expected condition. The executor advances the journal between them and halts
# on the first non-`pass` whose step is `halting`.
#
# A step returns:
#   {"step": "l6_push_one", "verdict": "pass|fail|inconclusive", "reason": ...,
#    "journal": "<state to record on success>", "halting": bool, "detail": {...}}


class LandingContext:
    """Everything the steps share. Assembled ONCE, from RE-DERIVED facts (REQ-LAND-002)."""

    def __init__(self, plan_dir: Path, decision: dict, manifest: dict,
                 root: Path | None = None, runner=None):
        self.plan_dir = Path(plan_dir)
        self.plan_id = _plan_id_from_dir(self.plan_dir)
        self.decision = decision
        self.manifest = manifest
        self.facts = manifest["facts"]
        self.root = Path(root) if root else _land_primary_checkout()
        self.target = self.facts["git"]["merge_target"]
        self.execute_branch = self.facts["git"]["execute_branch"]
        self.worktree = self.root / self.facts["git"]["worktree_path"]
        self.journal = LandingJournal(self.root, self.plan_id)
        #: INJECTABLE so Tier-1 tests drive every step without a network or a real remote.
        #: NOT a second implementation — the SAME step functions run either way (REQ-LAND-001's
        #: "one code path"), only the process spawner differs.
        #:
        #: THE PROGRAM IS AN EXPLICIT ARGUMENT, and that is a correction rather than a style
        #: choice. An earlier version wrapped `_run_git` and every step called `ctx.run([...])`
        #: — so L7 ran `git issue comment`, L17 ran `git push --issues` and L19 ran
        #: `git self install`. Every Tier-1 test passed, because the injected fake returned 0
        #: for any argv it did not recognise. THE EPIC-6 REHEARSAL CAUGHT IT, which is exactly
        #: the gap between a mock that answers and a process that runs.
        self._runner = runner
        self.run = self._dispatch
        self.results: list[dict] = []


    def _dispatch(self, prog: str, args: list[str], cwd: Path | None = None):
        """Run `<prog> <args>`. `prog` is EXPLICIT so a step cannot silently run the wrong
        executable — see the note on `self.run`."""
        if self._runner is not None:
            return self._runner(prog, args, cwd=cwd or self.root)
        if prog == "git":
            return _run_git(args, cwd=cwd or self.root)
        return subprocess.run([prog, *args], cwd=str(cwd or self.root),
                              capture_output=True, text=True)

    def step_enabled(self, key: str) -> tuple[bool, str | None]:
        """Is this step enabled by the decision? Returns (enabled, skip_reason).

        NARROWING-ONLY (REQ-LAND-002): a non-skippable step is ALWAYS enabled regardless of
        what the decision says — `--validate-decision` already refuses such a decision, and
        this is the belt to that suspenders. A decision cannot widen and cannot skip the
        merge.
        """
        v = (self.decision.get("steps") or {}).get(key, "enable")
        if key in LAND_NON_SKIPPABLE:
            return True, None
        if isinstance(v, str) and v.startswith("skip"):
            return False, v.split(":", 1)[1] if ":" in v else "(no reason given)"
        return True, None


def _step(name: str, verdict: str, reason: str, journal: str | None = None,
          halting: bool = True, **detail) -> dict:
    return {"step": name, "verdict": verdict, "reason": reason, "journal": journal,
            "halting": halting, "detail": detail}


# -- L0 ------------------------------------------------------------------------------------

def _land_l0_lock_acquire(ctx: LandingContext) -> dict:
    """L0 — acquire the single-machine landing lock.

    First because it must precede the first tree mutation, or two landings interleave.
    """
    out = _landing_lock_acquire(ctx.plan_id)
    if not out.get("acquired"):
        return _step("l0_lock_acquire", "fail",
                     f"the landing lock is held: {out.get('holder')}",
                     halting=True, holder=out.get("holder"))
    return _step("l0_lock_acquire", "pass", "landing lock acquired", journal="L_LOCKED")


# -- L1 ------------------------------------------------------------------------------------

def _land_l1_down_merge(ctx: LandingContext) -> dict:
    """L1 — fetch, then DOWN-MERGE the target into `<plan-id>-execute`, in the worktree.

    This is what makes L11 honest: a down-merge makes the branch tree byte-identical to the
    merged tree, so completion-time measurement and "the tree that will be on the target" are
    reconcilable rather than in tension.

    A conflict here is `L_CONFLICT_DOWNMERGE` — fully local, pre-L6 and pre-L7, so the
    recovery is capture-then-abort and there is no outward trace.
    """
    wt = ctx.worktree if ctx.worktree.is_dir() else ctx.root
    ctx.run("git", ["fetch", "--all", "--prune"], cwd=wt)
    r = ctx.run("git", ["merge", "--no-ff", "-m",
                 f"plan-{ctx.plan_id}: down-merge {ctx.target} before landing", ctx.target],
                cwd=wt)
    if r.returncode != 0:
        cap = _land_capture_conflict("L_CONFLICT_DOWNMERGE", wt)
        restore = _land_abort_merge(wt)
        return _step("l1_down_merge", "fail",
                     "the down-merge conflicted — captured and aborted; nothing has been "
                     "pushed and nothing posted, so there is no outward trace",
                     journal="L_CONFLICT_DOWNMERGE", halting=True,
                     conflict=cap, restore=restore)
    return _step("l1_down_merge", "pass",
                 f"{ctx.target} down-merged into {ctx.execute_branch}",
                 journal="L_DOWNMERGED")


# -- L2 ------------------------------------------------------------------------------------

def _land_l2_merge(ctx: LandingContext) -> dict:
    """L2 — checkout the target, `pull --rebase`, `merge --no-ff` LEFT UNCOMMITTED.

    Uncommitted deliberately: L3 must have something to fail closed onto. `--no-ff` keeps the
    landing one revertable commit and defines the tree L3 validates.

    RUNS IN THE PRIMARY CHECKOUT — a linked worktree cannot check out a branch another
    worktree holds (REQ-LAND-010).
    """
    co = ctx.run("git", ["checkout", ctx.target], cwd=ctx.root)
    if co.returncode != 0:
        return _step("l2_merge", "fail",
                     f"could not check out {ctx.target}: {(co.stderr or '').strip()}",
                     halting=True)
    ctx.run("git", ["pull", "--rebase"], cwd=ctx.root)
    r = ctx.run("git", ["merge", "--no-ff", "--no-commit", ctx.execute_branch], cwd=ctx.root)
    if r.returncode != 0:
        cap = _land_capture_conflict("L_CONFLICT_MERGE", ctx.root)
        restore = _land_abort_merge(ctx.root)
        return _step("l2_merge", "fail",
                     "the merge conflicted — captured and aborted; still fully local, "
                     "pre-push and pre-outward-write",
                     journal="L_CONFLICT_MERGE", halting=True,
                     conflict=cap, restore=restore)
    return _step("l2_merge", "pass",
                 f"{ctx.execute_branch} merged into {ctx.target}, UNCOMMITTED",
                 journal="L_MERGED_UNCOMMITTED")


# -- L3 ------------------------------------------------------------------------------------

def _land_l3_validate_merged(ctx: LandingContext) -> dict:
    """L3 — the FULL tier over the merged tree. HALTS WITH THE LOCK STILL HELD on fail.

    plan-009 INV-4, and the single most important correction to #301, which puts the FULL
    tier AFTER the document close and bead close-out — where a red tier has nothing to fail
    closed onto.

    THE LOCK STAYS HELD so the operator repairs under serialization. An `inconclusive` is
    reported and NOT coerced to `fail` — the #262 defect lives inside `_validate_merged`
    itself and must not be reproduced one frame up.
    """
    out = _validate_merged(ctx.plan_dir)
    status = (out.get("status") or out.get("verdict") or "").lower()
    if status == "fail":
        return _step("l3_validate_merged", "fail",
                     "the FULL tier is RED on the merged tree. The landing HALTS and THE "
                     "LOCK IS STILL HELD, so the repair happens under serialization. "
                     "Nothing has been pushed and nothing posted.",
                     halting=True, lock_held=True, engine=out.get("engine"),
                     first_failure=out.get("first_failure"))
    if status not in ("pass", ""):
        return _step("l3_validate_merged", "inconclusive",
                     f"merged-state validation was INCONCLUSIVE ({status}) — reported, and "
                     f"deliberately NOT coerced to fail",
                     journal=None, halting=False, engine=out.get("engine"))
    return _step("l3_validate_merged", "pass",
                 f"merged-state validation green (engine: {out.get('engine')})",
                 journal=None, engine=out.get("engine"),
                 cross_plan_notice=out.get("notice"))


# -- L4 ------------------------------------------------------------------------------------

def _land_l4_commit_merge(ctx: LandingContext) -> dict:
    """L4 — commit the merge, then RELEASE the lock.

    Released here rather than at the end: the base is now green, and holding the global lock
    across the remaining steps (which include an operator-facing wait) would serialize them
    needlessly.

    THE POST-MERGE TREE ASSERTION lives here (Issue 4.1). `pull --rebase` at L2 can pick up
    commits that arrived AFTER L1's down-merge, and the lock is single-machine only — so the
    merge result's tree may no longer equal the down-merged branch tree. Asserting it is what
    catches that; without it L11 would measure a tree nobody validated.
    """
    r = ctx.run("git", ["commit", "--no-edit"], cwd=ctx.root)
    if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr).lower():
        return _step("l4_commit_merge", "fail",
                     f"could not commit the merge: {(r.stderr or '').strip()}", halting=True)

    merged_tree = ctx.run("git", ["rev-parse", "HEAD^{tree}"], cwd=ctx.root).stdout.strip()
    branch_tree = ctx.run("git", ["rev-parse", f"{ctx.execute_branch}^{{tree}}"],
                          cwd=ctx.root).stdout.strip()
    tree_match = bool(merged_tree) and merged_tree == branch_tree

    _landing_lock_release(ctx.plan_id, False)

    if not tree_match:
        return _step("l4_commit_merge", "fail",
                     "the merge result's tree does NOT match the down-merged branch tree. "
                     "`pull --rebase` picked up commits that arrived after L1, and the "
                     "landing lock is single-machine only — so what is about to be pushed is "
                     "not what L1 made byte-identical, and L11 would measure a tree nothing "
                     "validated.",
                     halting=True, merged_tree=merged_tree, branch_tree=branch_tree,
                     lock_released=True)
    return _step("l4_commit_merge", "pass",
                 "merge committed, post-merge tree assertion holds, landing lock released",
                 journal="L_VALIDATED", merged_tree=merged_tree, lock_released=True)


# -- L5 ------------------------------------------------------------------------------------

def _land_l5_advisory_recheck(ctx: LandingContext) -> dict:
    """L5 — ADVISORY `recheck-criteria` on the merged tree, BEFORE the push.

    THE LAST FULLY REVERSIBLE POINT. Tree-sensitive criteria are exercised while the landing
    can still be abandoned with no outward trace.

    ADVISORY DESCRIBES THE VERDICT, NOT WHETHER IT RUNS (`REQ-LAND-004` L5): it never halts.
    The authoritative halting run is L11, after the reconcile writes that some criteria
    depend on.
    """
    proc = subprocess.run(
        ["uv", "run", str(Path(__file__).resolve()), "recheck-criteria",
         str(ctx.plan_dir), "--json"],
        capture_output=True, text=True, cwd=ctx.root)
    return _step("l5_advisory_recheck", "pass",
                 f"advisory pre-push criteria run complete (exit {proc.returncode}) — "
                 f"ADVISORY, never halting; the authoritative run is L11",
                 journal="L_PREPUSH_CHECKED", halting=False,
                 exit_code=proc.returncode, advisory=True,
                 output=(proc.stdout or proc.stderr)[-2000:])


# -- L6 ------------------------------------------------------------------------------------

def _land_l6_push_one(ctx: LandingContext) -> dict:
    """L6 — PUSH #1. **THE FIRST IRREVERSIBLE STEP OF THE LANDING.**

    Stated in the verdict rather than implied away: every halt after this leaves the target
    ALREADY CARRYING THE MERGE. What makes that acceptable is that L3's FULL tier ran first,
    so the code on the target is validated; the later halts (L10, L11, L12) concern plan
    bookkeeping and upstream state, not code correctness, and each is repairable without a
    revert.

    A REJECTION IS `L_REJECTED_PUSH_1` — still pre-outward-write, so the recovery is
    `pull --rebase`, RE-VALIDATE, retry. Never push an unvalidated rebase.
    """
    r = ctx.run("git", ["push", "origin", ctx.target], cwd=ctx.root)
    if r.returncode != 0:
        return _step("l6_push_one", "fail",
                     "push #1 was REJECTED — the remote advanced. Recovery: `pull --rebase`, "
                     "then RE-VALIDATE (re-run the FULL tier), then retry. This is still "
                     "PRE-OUTWARD-WRITE: nothing has been posted and nothing closed.",
                     journal="L_REJECTED_PUSH_1", halting=True,
                     recovery=LAND_CONFLICT_RECOVERY["L_REJECTED_PUSH_1"],
                     stderr=(r.stderr or "").strip()[:400])
    return _step("l6_push_one", "pass",
                 "push #1 complete — THE FIRST IRREVERSIBLE STEP HAS BEEN CROSSED. Every "
                 "halt from here leaves the merge on the target; L3's FULL tier ran first, "
                 "so what is on the target is validated.",
                 journal="L_PUSHED_1", irreversible=True)


# -- L7 ------------------------------------------------------------------------------------

def _land_l7_reconcile_writes(ctx: LandingContext) -> dict:
    """L7 — the reconcile writes. **THE FIRST OUTWARD-FACING WRITE.**

    EVERY WRITE IS VERIFIED BY READ-BACK (`REQ-LAND-019`) — `gh issue view` after the write —
    never by exit code and never by the returned URL alone. Measured on issue #292 during this
    plan's own drafting: an exit 0 from `gh` does not establish that the body posted is the
    body intended.

    THE DISPOSITION CONTRACT IS READ, NOT DISCOVERED. `UPSTREAM_REQUIREMENTS` already encodes
    the per-row end state, so a close the disposition does not permit is REFUSED here
    regardless of what the decision asks for — the agent explains the contract, it does not
    get to override it (D-6).
    """
    writes = ctx.decision.get("upstream_writes") or []
    rows = {str(r["issue"]): r for r in ctx.facts["upstream"]["rows"]}
    performed, refused, failed = [], [], []

    for w in writes:
        issue = str(w.get("issue"))
        action = w.get("action")
        row = rows.get(issue)
        if row is None:
            refused.append({"issue": issue, "action": action,
                            "refused_because": "no such row in the plan's Upstream Issues "
                                               "table — the decision may not invent a write"})
            continue
        if action == "close" and row.get("required_end_state") != "CLOSED":
            refused.append({
                "issue": issue, "action": action,
                "refused_because": (
                    f"disposition `{row['disposition']}` requires end state "
                    f"{row['required_end_state']}. Closing it would contradict the "
                    f"dispositions the plan was APPROVED with. {row.get('why')}")})
            continue

        body_path = w.get("body_path")
        if action == "comment":
            if not body_path or not Path(body_path).is_file():
                failed.append({"issue": issue, "reason": f"body_path {body_path} missing"})
                continue
            r = ctx.run("gh", ["issue", "comment", issue, "--body-file", body_path], cwd=ctx.root)
        else:
            r = ctx.run("gh", ["issue", "close", issue], cwd=ctx.root)

        # STRUCTURAL VERIFICATION BY READ-BACK — never `$?`, never the returned URL.
        back = ctx.run("gh", ["issue", "view", issue, "--json",
                        "state,comments"], cwd=ctx.root)
        ok = False
        detail = ""
        if back.returncode == 0:
            try:
                seen = json.loads(back.stdout)
                if action == "close":
                    ok = str(seen.get("state", "")).upper() == "CLOSED"
                    detail = f"read-back state={seen.get('state')}"
                else:
                    want = Path(body_path).read_text(encoding="utf-8").strip()
                    bodies = [c.get("body", "") for c in (seen.get("comments") or [])]
                    ok = any(want[:200] in b for b in bodies)
                    detail = (f"read-back found {len(bodies)} comment(s); "
                              f"body match={ok}")
            except (json.JSONDecodeError, OSError) as exc:
                detail = f"read-back unparseable: {exc}"
        else:
            detail = f"read-back failed: {(back.stderr or '').strip()[:200]}"

        (performed if ok else failed).append(
            {"issue": issue, "action": action, "verified_by": "read-back", "detail": detail})
        if not ok:
            # FAIL-CLOSED: the first unverified write aborts before any destructive
            # follow-on stage is reachable (REQ-LAND-020).
            return _step("l7_reconcile_writes", "fail",
                         f"an upstream write to #{issue} could NOT be verified by read-back. "
                         f"An exit 0 is not proof; the landing halts BEFORE any destructive "
                         f"stage. {detail}",
                         halting=True, performed=performed, refused=refused, failed=failed)

    return _step("l7_reconcile_writes", "pass",
                 f"{len(performed)} upstream write(s) posted and verified by read-back; "
                 f"{len(refused)} refused as contradicting their disposition",
                 journal="L_RECONCILED", performed=performed, refused=refused,
                 outward_facing=True)


# -- L8-L15 --------------------------------------------------------------------------------

#: The close chain, in REQ-COMPLETE-001 order. `halting` is read from THIS TABLE rather than
#: inferred, so an advisory step can never accidentally stop a landing and a halting one can
#: never accidentally be walked past (#180's defect, in which an exit code was captured and
#: only ECHOED).
LAND_CLOSE_CHAIN: tuple[tuple[str, str, bool], ...] = (
    ("audit-close",                   "l8_close_chain_head",     False),
    ("retrospective-report",          "l8_close_chain_head",     False),
    ("judgement-never-fired-report",  "l8_close_chain_head",     False),
    ("classify-deliverable",          "l8_close_chain_head",     False),
    ("close-reconcile-step",          "l9_close_reconcile_step", True),
    ("verify-reconcile",              "l10_verify_reconcile",    True),
    ("recheck-criteria",              "l11_recheck_criteria",    True),
)


def _land_l8_to_l15_close_chain(ctx: LandingContext) -> list[dict]:
    """L8-L15 — the existing close chain, invoked verb by verb.

    EACH EXIT CODE IS **READ**, NOT MERELY ECHOED. That is #180's defect: `close-reconcile-step`
    was captured into a variable whose `$?` nothing consulted, so an ordering violation
    reported `inconclusive`, exited 0, and the chain walked on to cascade-close and
    `set complete` with the reconcile step still open.

    AN `inconclusive` IS REPORTED AND DOES NOT HALT. A `gh` outage must never block completion
    on healthy work (R1), and `recheck-criteria`'s exit 2 maps to warn per REQ-DATA-057.

    `CHANGED` is computed as `HEAD^1..HEAD` (Issue 1.4 / #303), never `<target>...HEAD`.
    """
    out: list[dict] = []
    me = str(Path(__file__).resolve())
    changed = _land_changed_set(ctx.root)

    for verb, journal_step, halting in LAND_CLOSE_CHAIN:
        args = ["uv", "run", me, verb, str(ctx.plan_dir), "--json"]
        if verb == "classify-deliverable":
            for p in changed:
                args += ["--changed", p]
        proc = subprocess.run(args, capture_output=True, text=True, cwd=ctx.root)
        rc = proc.returncode                      # READ, not echoed.
        if rc == 0:
            out.append(_step(verb, "pass", f"{verb} clean", halting=halting, exit_code=rc))
            continue
        if rc == 2:
            out.append(_step(verb, "inconclusive",
                             f"{verb} was INCONCLUSIVE (exit 2) — reported, NOT coerced to "
                             f"fail and NOT halting",
                             halting=False, exit_code=rc,
                             output=(proc.stdout or proc.stderr)[-1500:]))
            continue
        out.append(_step(verb, "fail",
                         f"{verb} exited {rc}. "
                         + ("HALTING: completion stops here and `complete` is NOT set."
                            if halting else "Advisory — reported, not halting."),
                         halting=halting, exit_code=rc,
                         output=(proc.stdout or proc.stderr)[-1500:]))
        if halting:
            return out
    return out


def _land_l12_close_cascade(ctx: LandingContext) -> dict:
    """L12 — `close_cascade.py`. **THE FIRST DESTRUCTIVE STEP.**

    It refuses any container with a non-terminal child and NEVER force-closes an unmet gate:
    "terminal" means closed, or a resolved/verified gate. An unsatisfied gate is a genuine
    open child.
    """
    epic = _read_plan_epic_field((ctx.plan_dir / "plan.md").read_text(encoding="utf-8"))
    if not epic:
        return _step("l12_close_cascade", "inconclusive",
                     "no **Epic:** field in plan.md — nothing to cascade", halting=False)
    engine = Path(__file__).resolve().parent / "close_cascade.py"
    proc = subprocess.run(["uv", "run", str(engine), epic, "--plan", ctx.plan_id, "--json"],
                          capture_output=True, text=True, cwd=ctx.root)
    if proc.returncode != 0:
        return _step("l12_close_cascade", "fail",
                     f"cascade-close reported open children or a close error (exit "
                     f"{proc.returncode}). A container in the plan tree still has a "
                     f"non-terminal child — an UNSATISFIED GATE IS A GENUINE OPEN CHILD and "
                     f"is never force-closed.",
                     halting=True, exit_code=proc.returncode, destructive=True,
                     output=(proc.stdout or proc.stderr)[-1500:])
    return _step("l12_close_cascade", "pass", "cascade-close clean", destructive=True)


def _land_l13_l15_finish(ctx: LandingContext) -> list[dict]:
    """L13 complete-gate, L14 pour_fidelity, L15 update-status complete.

    `pour_fidelity` is THREE-VALUED and branching on `!= 0` would report an INCONCLUSIVE as a
    DIVERGENCE — two different facts collapsed into one signal, the same conflation as
    `doc_lint`'s `not-selected` vs `no-such-path` (#181). Read the CODE, never the flag.
    """
    out: list[dict] = []
    me = str(Path(__file__).resolve())

    g = subprocess.run(["uv", "run", me, "complete-gate", str(ctx.plan_dir), "--json"],
                       capture_output=True, text=True, cwd=ctx.root)
    if g.returncode != 0:
        out.append(_step("l13_complete_gate", "fail",
                         "the completion gate blocked a ci-release plan — its "
                         "runner-only-observable behavior is unverified",
                         halting=True, exit_code=g.returncode,
                         output=(g.stdout or g.stderr)[-1200:]))
        return out
    out.append(_step("l13_complete_gate", "pass", "completion gate satisfied"))

    beads = ctx.root / ".yf" / "plan" / "land-beads.json"
    beads.parent.mkdir(parents=True, exist_ok=True)
    bl = subprocess.run(["bd", "list", "--all", "--include-gates", "--limit", "5000",
                         "--json"], capture_output=True, text=True)
    beads.write_text(bl.stdout or "[]", encoding="utf-8")
    engine = Path(__file__).resolve().parent / "pour_fidelity.py"
    f = subprocess.run(["uv", "run", str(engine), str(beads), str(ctx.plan_dir),
                        "--strict", "--plan", ctx.plan_id, "--json"],
                       capture_output=True, text=True, cwd=ctx.root)
    if f.returncode == 2:
        out.append(_step("l14_pour_fidelity", "fail",
                         "pour fidelity is INCONCLUSIVE — the comparison could not be made "
                         "AT ALL. This is a statement about the INSTRUMENT, not a verdict on "
                         "the DAG. An unjudgeable plan is not a clean one, so completion "
                         "HALTS.",
                         halting=True, exit_code=2,
                         output=(f.stdout + f.stderr)[-1500:]))
        return out
    if f.returncode != 0:
        out.append(_step("l14_pour_fidelity", "fail",
                         "the poured bead DAG does not match the plan's declared DAG",
                         halting=True, exit_code=f.returncode,
                         output=(f.stdout + f.stderr)[-1500:]))
        return out
    out.append(_step("l14_pour_fidelity", "pass", "pour fidelity clean"))

    s = subprocess.run(["uv", "run", me, "update-status", str(ctx.plan_dir), "complete",
                        "-m", "plan complete (landed by `land --apply`)"],
                       capture_output=True, text=True, cwd=ctx.root)
    if s.returncode != 0:
        out.append(_step("l15_update_status", "fail",
                         f"could not set complete: {(s.stderr or '').strip()[:200]}",
                         halting=True))
        return out
    out.append(_step("l15_update_status", "pass", "status set to complete",
                     journal="L_CLOSED"))
    return out


# -- L16 -----------------------------------------------------------------------------------

def _land_l16_commit_and_push_two(ctx: LandingContext) -> dict:
    """L16 — commit the plan-folder writes and PUSH #2.

    **THE STEP NEITHER `SKILL.md` NOR #301 HAS.** Without it every landing ends with an
    uncommitted, unpushed `plan.md` — measured on plan-057, and the residue this whole
    capability exists to remove. Skipping it is forbidden (`LAND_NON_SKIPPABLE`).

    A REJECTION HERE IS `L_REJECTED_PUSH_2` AND IS A DIFFERENT ANIMAL from L6's. By now the
    reconcile comments are posted (L7), the bead tree is closed (L12) and `status: complete`
    is written (L15). The contract is **retry-after-rebase, NEVER REVERT**: reverting would
    contradict outward statements already made.

    THE POST-CONDITION IS ASSERTED ON THE WAY OUT, not merely a precondition on the way in
    (REQ-LAND-020): `git status --porcelain` clean AND zero unpushed commits.
    """
    add = ctx.run("git", ["add", "--", ctx.plan_dir.as_posix()], cwd=ctx.root)
    if add.returncode != 0:
        return _step("l16_commit_and_push_two", "fail",
                     f"could not stage the plan folder: {(add.stderr or '').strip()[:200]}",
                     halting=True)

    # PATH-SCOPED, BOTH HALVES (REQ-LAND-032, #342).
    #
    # The guard: an UNRELATED staged file otherwise makes the whole-index `--quiet` say
    # "there is something staged" while the scoped commit exits 1 `no changes added to
    # commit` — a misleading failure at a post-outward-write step.
    #
    # The commit: `-o` restricts it to the named pathspec, so the step cannot commit work it
    # did not stage. ARGUMENT ORDER IS LOAD-BEARING — after `--` every token is a pathspec,
    # so the `-o -- <dir> -m <msg>` order fails with `error: pathspec '-m' did not match any
    # file(s)`, exit 1, on EVERY landing.
    #
    # SCOPING THE GUARD REMOVES A MISLEADING ERROR; IT DOES NOT REMOVE THE HALT. The
    # post-condition below still sees the unrelated file and returns a halting fail — which
    # is intended, and is what `--dry-run` now predicts (REQ-LAND-034).
    staged = ctx.run("git", ["diff", "--cached", "--quiet", "--", ctx.plan_dir.as_posix()],
                     cwd=ctx.root)
    if staged.returncode != 0:                      # non-zero == there IS something staged
        c = ctx.run("git", ["commit", "-m",
                     f"{ctx.plan_id}: plan-folder writes from the landing close chain",
                     "-o", "--", ctx.plan_dir.as_posix()],
                    cwd=ctx.root)
        if c.returncode != 0:
            return _step("l16_commit_and_push_two", "fail",
                         f"could not commit the plan-folder writes: "
                         f"{(c.stderr or '').strip()[:200]}", halting=True)

    p = ctx.run("git", ["push", "origin", ctx.target], cwd=ctx.root)
    if p.returncode != 0:
        return _step("l16_commit_and_push_two", "fail",
                     "push #2 was REJECTED. THIS IS POST-OUTWARD-WRITE: the reconcile "
                     "comments are posted, the bead tree is closed and `status: complete` is "
                     "written. Recovery is `pull --rebase` and RETRY — NEVER REVERT, because "
                     "reverting would contradict outward statements already made.",
                     journal="L_REJECTED_PUSH_2", halting=True,
                     recovery=LAND_CONFLICT_RECOVERY["L_REJECTED_PUSH_2"],
                     post_outward_write=True,
                     stderr=(p.stderr or "").strip()[:400])

    # POST-CONDITION, asserted on the way OUT.
    #
    # THE LANDING JOURNAL IS EXCLUDED, and it must be. REQ-LAND-008 stages it INSIDE the repo
    # tree (a `mktemp -d` would turn `os.rename` into a copy and void every durability claim),
    # and L16 runs at `L_PUSHED_2` — three steps before the landing ends — so the journal is
    # necessarily still present and necessarily still describing an in-flight landing.
    #
    # FOUND BY THE EPIC-6 REHEARSAL, not by review: in a sandbox without the `/.yf/` gitignore
    # anchor that `yf preflight` ensures, the journal appeared as an untracked file and L16
    # failed its own post-condition. The live repo has that anchor, so the defect was invisible
    # here and would have surfaced first in whichever repo lacked it.
    # `-uall` and the PATH-PREFIX filter (REQ-LAND-033, #343). See `_dirty_outside_plan_dir`.
    dirt = _dirty_outside_plan_dir(ctx.plan_dir, root=ctx.root, runner=ctx.run)
    porcelain = "\n".join(dirt["paths"]).strip()
    unpushed = ctx.run("git", ["rev-list", "--count", f"origin/{ctx.target}..{ctx.target}"],
                       cwd=ctx.root).stdout.strip() or "0"
    if porcelain or unpushed not in ("0", ""):
        return _step("l16_commit_and_push_two", "fail",
                     f"L16's post-condition FAILED — this is exactly the residue the step "
                     f"exists to remove. porcelain={porcelain!r} unpushed={unpushed}",
                     halting=True, porcelain=porcelain, unpushed=unpushed)
    return _step("l16_commit_and_push_two", "pass",
                 "plan-folder writes committed and pushed; working tree clean and zero "
                 "unpushed commits",
                 journal="L_PUSHED_2", porcelain="", unpushed=0)


# -- L17 -----------------------------------------------------------------------------------

def _land_l17_residual_mirroring(ctx: LandingContext) -> dict:
    """L17 — mirror residual open beads upstream, grouped per the decision.

    CALLS `upstream.py push --issues <csv> --apply` **CONCRETELY**. `/yf-beads-upstream` is a
    prose skill for an LLM and this is Python that cannot invoke it (REQ-LAND-021).

    **PROPOSE-ONLY UNLESS THE GRANT DEMONSTRABLY COVERS THE BEAD SET.** That push is
    confirm-required by default and #280 leaves `detect_followons`' auto-eligible set
    permanently empty, so "demonstrably" means the decision enumerates each bead id AND the
    grant names each of them. Absent that, this step emits the proposed invocation and
    performs NO upstream write.

    Every close is verified STRUCTURALLY by read-back: `bd close` REFUSES AND EXITS 0 when the
    bead is blocked by an open dependency (#230), so the exit code proves nothing.
    """
    groups = ctx.decision.get("residual_bead_groups") or []
    if not groups:
        return _step("l17_residual_mirroring", "pass",
                     "no residual bead groups in the decision — nothing to mirror",
                     journal="L_MIRRORED", proposed=[], applied=[])

    beads = sorted({b for g in groups for b in (g.get("beads") or [])})
    grant = _land_grant_covers(ctx.plan_dir, beads)
    engine = Path(__file__).resolve().parent.parent.parent / "yf-beads-upstream" / "scripts" / "upstream.py"
    proposal = (f"uv run {engine} push --issues {','.join(beads)} --apply"
                if beads else None)

    if not grant["covered"]:
        return _step("l17_residual_mirroring", "pass",
                     f"PROPOSE-ONLY: the batched grant does not demonstrably cover "
                     f"{len(beads)} residual bead(s). {grant['reason']} No upstream write was "
                     f"performed.",
                     journal="L_MIRRORED", halting=False,
                     proposed=[proposal] if proposal else [], applied=[],
                     uncovered=grant.get("uncovered", []))

    r = ctx.run("uv", ["run", str(engine), "push", "--issues", ",".join(beads),
                        "--apply"], cwd=ctx.root)
    verified = []
    for b in beads:
        back = subprocess.run(["bd", "show", b, "--json"], capture_output=True, text=True)
        ok = False
        try:
            d = json.loads(back.stdout)
            d = d[0] if isinstance(d, list) and d else d
            ok = bool((d or {}).get("external_ref"))
        except (json.JSONDecodeError, IndexError, TypeError):
            ok = False
        verified.append({"bead": b, "external_ref_present": ok})
    unverified = [v["bead"] for v in verified if not v["external_ref_present"]]
    if unverified:
        return _step("l17_residual_mirroring", "fail",
                     f"{len(unverified)} bead(s) have no `external_ref` after the push — "
                     f"VERIFIED BY READ-BACK, not by exit code, because `bd close` refuses "
                     f"and exits 0 when blocked (#230): {unverified}",
                     halting=True, verified=verified, exit_code=r.returncode)
    return _step("l17_residual_mirroring", "pass",
                 f"{len(beads)} residual bead(s) mirrored and verified by read-back",
                 journal="L_MIRRORED", verified=verified)


def _land_grant_covers(plan_dir: Path, beads: list[str]) -> dict:
    """Does the per-landing grant DEMONSTRABLY cover this exact bead set (REQ-LAND-021)?

    "Demonstrably" is deliberately strict: the grant file must NAME EACH BEAD ID. A grant that
    authorizes "the residual beads" in prose covers nothing checkable, and #280 means no
    automatic eligibility signal can stand in for it.
    """
    grant = plan_dir / "assets" / "upstream-grant.md"
    if not grant.is_file():
        return {"covered": False,
                "reason": f"no grant file at {grant.as_posix()}.",
                "uncovered": beads}
    text = grant.read_text(encoding="utf-8")
    uncovered = [b for b in beads if b not in text]
    if uncovered:
        return {"covered": False,
                "reason": f"the grant does not name {len(uncovered)} of {len(beads)} bead(s).",
                "uncovered": uncovered}
    return {"covered": True, "reason": "every bead id is named in the grant", "uncovered": []}


# -- L18 -----------------------------------------------------------------------------------

def _land_l18_prune(ctx: LandingContext) -> dict:
    """L18 — prune, **STRATEGY-AWARE**.

    Deletes `<plan-id>-execute` **ONLY**. Under the `feature-branch` strategy REQ-BRANCH-004
    requires the feature `<plan-id>` branch to be **PRESERVED**, so the strategy is consulted
    rather than assumed.

    THE HERDR TAB DEFAULTS TO A PROPOSAL. Tab provenance — "a tab this session created" — is
    currently UNANSWERABLE (D-7), so a close requires an explicitly supplied tab id AND #204's
    mechanical harvest preconditions, and is verified by reading back the agent list. Closing
    a tab this session did not create would destroy scrollback that may be the only copy of
    something.
    """
    strategy = _resolve_landing_strategy()
    feature = _feature_branch(ctx.plan_id)
    actions, preserved = [], []

    # REQ-LAND-031 (#340). THREE DEFECTS LIVED IN THE THREE LINES THIS REPLACES.
    #
    # (a) ARITY. `_worktree_teardown(plan_dir, force)` takes TWO parameters; the call passed
    #     one, and raised `TypeError` on the first real `--apply` in this repository's
    #     history — after two pushes, three public comments and `status: complete`. The
    #     KEYWORD form is deliberate: the next signature change fails loudly rather than
    #     silently rebinding a positional. `force=False` is the only value consistent with
    #     INV-1 (never `--force` without confirmation) and is confirmed against the CLI path.
    #
    # (b) A DUPLICATE DELETE. `_worktree_teardown` already deletes the execute branch (its
    #     `branch_delete` step). The direct `ctx.run` git branch-delete call that stood here
    #     (spelled in prose rather than literally, because SC2b asserts that literal's
    #     ABSENCE from this file and a comment naming it would defeat the check while looking
    #     like documentation) therefore ran SECOND, against a branch that no longer existed — so once (a) was
    #     fixed, L18 would PERMANENTLY report its own headline action as
    #     `{"action": "delete-execute-branch", "ok": false, "detail": "branch not found"}`.
    #     The delete is delegated; the report below reads the teardown's own step.
    #
    # (c) AN UNREAD STATUS. `_worktree_teardown` returns `{"status", "path", "branch",
    #     "steps"}` and NEVER an `"action"` key, so `wt.get("action") or wt` always took the
    #     fallback — and nothing consulted `status` at all. A `blocked` teardown (dirty
    #     worktree: nothing removed, branch left behind) reported `verdict: pass`. A landing
    #     must not report a prune it did not perform.
    wt = _worktree_teardown(ctx.plan_dir, force=False)
    status = wt.get("status") if isinstance(wt, dict) else None
    actions.append({"action": "worktree-teardown", "status": status, "result": wt})

    bd_step = (wt.get("steps") or {}).get("branch_delete") if isinstance(wt, dict) else None
    actions.append({"action": "delete-execute-branch", "branch": ctx.execute_branch,
                    "via": "_worktree_teardown",
                    "ok": bool(bd_step.get("ok")) if isinstance(bd_step, dict) else None,
                    "detail": (bd_step or {}).get("detail") if isinstance(bd_step, dict)
                              else "the teardown reported no branch_delete step"})

    if strategy == "feature-branch":
        preserved.append(feature)
    else:
        # Under `main` there is no feature branch to preserve; say so rather than implying
        # a deletion happened.
        preserved.append(f"(none — strategy `main`, no feature branch exists)")

    tab = (ctx.decision.get("herdr_tab") or {})
    tab_id = tab.get("id")
    if not tab_id:
        tab_action = {"action": "herdr-tab", "decision": "PROPOSE",
                      "reason": "no tab id supplied. Provenance is unanswerable (#204/D-7), "
                                "so a close is never inferred — closing a tab this session "
                                "did not create would destroy scrollback that may be the "
                                "only copy of something."}
    else:
        tab_action = {"action": "herdr-tab", "decision": "PROPOSE", "tab": tab_id,
                      "reason": "a tab id was supplied, but the close is still proposed "
                                "rather than performed: #204's mechanical harvest "
                                "preconditions are a yf-herdr deliverable and are not "
                                "implemented here."}
    actions.append(tab_action)

    # BRANCH ON THE RETURNED `status` (REQ-LAND-031). Three-valued, and the ABSENT case is
    # stated rather than inferred: a stub or a future return shape carrying no `status` has
    # established NOTHING about the prune, so the step is `inconclusive` — never `pass`.
    if status == "ok":
        return _step("l18_prune", "pass",
                     f"pruned under strategy `{strategy}`: {ctx.execute_branch} only; "
                     f"herdr tab PROPOSED, never closed",
                     journal="L_PRUNED", strategy=strategy, actions=actions,
                     preserved=preserved, destructive=True, teardown_status=status)
    if status == "blocked":
        return _step("l18_prune", "fail",
                     f"the worktree teardown was BLOCKED — nothing was pruned and "
                     f"{ctx.execute_branch} is still present. "
                     f"{wt.get('detail') or 'the worktree is probably dirty.'} "
                     f"A landing must not report a prune it did not perform.",
                     journal=None, halting=True, strategy=strategy, actions=actions,
                     preserved=preserved, destructive=True, teardown_status=status,
                     recovery="Inspect the worktree, confirm no work is lost, then re-run "
                              "`land --apply`; L18 re-executes on the resume.")
    if status == "partial":
        return _step("l18_prune", "inconclusive",
                     f"the worktree teardown reported `partial` under strategy "
                     f"`{strategy}`: at least one of remove/branch-delete/prune did not "
                     f"succeed. Steps: {wt.get('steps')}",
                     journal="L_PRUNED", halting=False, strategy=strategy, actions=actions,
                     preserved=preserved, destructive=True, teardown_status=status)
    return _step("l18_prune", "inconclusive",
                 f"the worktree teardown returned no `status` key "
                 f"(got {sorted(wt) if isinstance(wt, dict) else type(wt).__name__}), so the "
                 f"prune is UNJUDGED. This is a statement about the instrument, not the "
                 f"landing.",
                 journal="L_PRUNED", halting=False, strategy=strategy, actions=actions,
                 preserved=preserved, destructive=True, teardown_status=status)


# -- L19 -----------------------------------------------------------------------------------

def _land_l19_redeploy(ctx: LandingContext) -> dict:
    """L19 — redeploy **iff** the landed change set touches `skills/` (REQ-LAND-022).

    The last step of the last step, and the only one that mutates the machine OUTSIDE the
    repository. Never mid-execution: a half-deployed session runs new scripts against old
    prose.

    ROLLBACK IS ASYMMETRIC and the verdict says so: `yf harness tune --revert` restores config
    precisely, but the rules aggregate is DELETED rather than restored (#154). That is why the
    operator's authorization is a precondition rather than a formality.
    """
    changed = _land_changed_set(ctx.root)
    touches = [p for p in changed if p.startswith("skills/")]
    if not touches:
        return _step("l19_redeploy", "pass",
                     "the landed change set does not touch `skills/` — redeploy correctly "
                     "SKIPPED (iff, not if)",
                     journal="L_DONE", touched_skills=[], redeployed=False)

    enabled, skip_reason = ctx.step_enabled("l19_redeploy")
    if not enabled:
        return _step("l19_redeploy", "pass",
                     f"redeploy SKIPPED by the decision: {skip_reason}. The landing did less "
                     f"than a reader might assume, and this is where that is said.",
                     journal="L_DONE", touched_skills=touches, redeployed=False,
                     skipped=True)

    r = ctx.run("yf", ["self", "install", "--from-build", "--build"], cwd=ctx.root)
    if r.returncode != 0:
        return _step("l19_redeploy", "fail",
                     f"redeploy failed (exit {r.returncode}). ROLLBACK IS ASYMMETRIC: "
                     f"`yf harness tune --revert` restores config precisely, but the rules "
                     f"aggregate is DELETED rather than restored (#154).",
                     halting=True, touched_skills=touches,
                     stderr=(r.stderr or "").strip()[:400])
    return _step("l19_redeploy", "pass",
                 f"redeployed — the landing touched {len(touches)} path(s) under `skills/`",
                 journal="L_DONE", touched_skills=touches, redeployed=True)


#: The ordered executor table. ONE ROW PER L-LABEL, in REQ-LAND-004's order. A step that
#: returns a LIST is a group of sub-steps sharing one L-label (the close chain), and the group
#: halts on the first halting failure inside it.
LAND_EXECUTOR: tuple[tuple[str, str], ...] = (
    ("l0_lock_acquire",         "_land_l0_lock_acquire"),
    ("l1_down_merge",           "_land_l1_down_merge"),
    ("l2_merge",                "_land_l2_merge"),
    ("l3_validate_merged",      "_land_l3_validate_merged"),
    ("l4_commit_merge",         "_land_l4_commit_merge"),
    ("l5_advisory_recheck",     "_land_l5_advisory_recheck"),
    ("l6_push_one",             "_land_l6_push_one"),
    ("l7_reconcile_writes",     "_land_l7_reconcile_writes"),
    ("l8_close_chain_head",     "_land_l8_to_l15_close_chain"),
    ("l12_close_cascade",       "_land_l12_close_cascade"),
    ("l13_complete_gate",       "_land_l13_l15_finish"),
    ("l16_commit_and_push_two", "_land_l16_commit_and_push_two"),
    ("l17_residual_mirroring",  "_land_l17_residual_mirroring"),
    ("l18_prune",               "_land_l18_prune"),
    ("l19_redeploy",            "_land_l19_redeploy"),
)


#: The journal state each L-step reaches on success. DECLARED rather than inferred, because a
#: SKIPPED step must still advance the journal: the landing DID get past that point, and a
#: journal that stalls at the last non-skipped step can never reach `L_DONE` — so a landing
#: that legitimately skips its final step could never be recorded as complete, and `recover()`
#: would resume at a step already passed.
#:
#: FOUND BY THE EPIC-6 REHEARSAL: skipping L19 (no `yf` in the sandbox) left the terminal state
#: at `L_PRUNED` with every step green, which SC36b correctly refused to accept as a completed
#: rehearsal.
LAND_STEP_JOURNAL: dict[str, str] = {
    "l0_lock_acquire": "L_LOCKED",
    "l1_down_merge": "L_DOWNMERGED",
    "l2_merge": "L_MERGED_UNCOMMITTED",
    "l4_commit_merge": "L_VALIDATED",
    "l5_advisory_recheck": "L_PREPUSH_CHECKED",
    "l6_push_one": "L_PUSHED_1",
    "l7_reconcile_writes": "L_RECONCILED",
    "l13_complete_gate": "L_CLOSED",
    "l16_commit_and_push_two": "L_PUSHED_2",
    "l17_residual_mirroring": "L_MIRRORED",
    "l18_prune": "L_PRUNED",
    "l19_redeploy": "L_DONE",
}


#: Steps that are NEVER skipped on a resume, however far the journal advanced.
#:
#: `l0_lock_acquire` is the only member, and the reason is asymmetric rather than cosmetic
#: (REQ-LAND-029). The landing lock is released at **L4**, not at the end, so a uniform skip
#: rule would run L1-L4 holding no lock and then `unlink` a lock it never acquired --
#: `_landing_lock_release` is keyed on plan+host, not PID, so that unlink would steal a lock
#: belonging to a concurrent landing. Re-executing L0 is safe because `_landing_lock_acquire`
#: reclaims a same-host dead-PID lock.
#:
#: KNOWN ASYMMETRY, RECORDED RATHER THAN PAPERED OVER: on a resume from L5 onward, L0
#: re-acquires while L4 is skipped, so that run ends holding a lock nothing released. It
#: self-heals via the same dead-PID reclaim.
LAND_RESUME_NEVER_SKIP: frozenset[str] = frozenset({"l0_lock_acquire"})


def _land_resume_done(resume_from: str | None) -> set[str]:
    """Translate a journal phase into the set of EXECUTOR STEP KEYS already completed.

    THE TWO VOCABULARIES ARE NOT THE SAME SET (REQ-LAND-029, dixson3/yoshiko-flow#327). The
    journal records `L_*` PHASES; the step loop iterates `LAND_EXECUTOR` STEP KEYS. The
    original code built a set of phases, named it `done`, and then never read it -- so a
    resume after a halt at L17 re-executed all fifteen steps from L0, `l6_push_one` and
    `l7_reconcile_writes` included. This function is the translation that was missing.

    UNJOURNALED STEPS RESOLVE **FORWARD**, NEVER BACKWARD. Three keys
    (`l3_validate_merged`, `l8_close_chain_head`, `l12_close_cascade`) have no entry in
    `LAND_STEP_JOURNAL`. Such a step is done only when the journal state of the **next
    journaled** step is in `reached`. A backward scan is unsafe and the failure is concrete:
    after a halt at `l3_validate_merged` the PRECEDING state `L_MERGED_UNCOMMITTED` is already
    reached, so backward resolution would mark l3 done and **skip validation of the merged
    tree** -- the one check standing between a merge and a push.

    A trailing unjournaled step (one with no journaled successor) is NEVER marked done: there
    is no evidence it ran, and manufacturing that evidence is the failure this whole function
    exists to prevent.
    """
    if not resume_from:
        return set()
    order = list(LAND_PROGRESS_ORDER)
    if resume_from not in order:
        return set()
    reached = set(order[: order.index(resume_from) + 1])

    keys = [key for key, _ in LAND_EXECUTOR]
    done: set[str] = set()
    for i, key in enumerate(keys):
        if key in LAND_RESUME_NEVER_SKIP:
            continue
        j = LAND_STEP_JOURNAL.get(key)
        if j is None:
            # FORWARD resolution: borrow the journal state of the next JOURNALED step.
            j = next(
                (LAND_STEP_JOURNAL[k] for k in keys[i + 1:] if k in LAND_STEP_JOURNAL),
                None,
            )
            if j is None:
                continue           # trailing unjournaled step -- no evidence, no skip
        if j in reached:
            done.add(key)
    return done


def _land_execute(ctx: LandingContext, resume_from: str | None = None) -> dict:
    """Drive L0-L19, advancing the journal between steps and halting on the first halting
    failure.

    RESUME IS KEYED ON THE JOURNAL'S RECORDED PHASE (REQ-LAND-009), never on observed state,
    and a resume RE-DERIVES the manifest and re-checks the digest before continuing
    (REQ-LAND-011) — the journal says WHERE it was, never WHAT WAS TRUE.

    FAIL-CLOSED AT EVERY EDGE (REQ-LAND-020): the first unverified write aborts before any
    destructive follow-on stage is reachable, which is why L7's read-back failure returns
    before L12 can run.
    """
    done: set[str] = _land_resume_done(resume_from)

    results: list[dict] = []
    for key, fname in LAND_EXECUTOR:
        if key in done:
            # RESUMED, NOT SILENTLY ABSENT (REQ-LAND-029). A skip that leaves no row is
            # indistinguishable from a step that was never in the table -- so the row is
            # emitted with an explicit `resumed` marker, and the journal is NOT rewritten
            # (it already records this state; rewriting it would move the phase backwards
            # on a re-resume).
            row = _step(key, "pass",
                        f"RESUMED: already completed before the halt at or before "
                        f"{resume_from}; not re-executed.",
                        halting=False, resumed=True, skipped=True)
            results.append(row)
            ctx.results.append(row)
            continue

        enabled, skip_reason = ctx.step_enabled(key)
        if not enabled:
            # A SKIPPED STEP STILL ADVANCES THE JOURNAL. The landing reached this point and
            # passed it; a journal that stalls at the last non-skipped step can never record
            # `L_DONE`, and `recover()` would resume at a step already passed.
            j = LAND_STEP_JOURNAL.get(key)
            skipped = _step(key, "pass",
                            f"SKIPPED by the decision: {skip_reason}. Surfaced here so "
                            f"'the landing did less than you think' is never silent.",
                            journal=j, halting=False, skipped=True)
            results.append(skipped)
            ctx.results.append(skipped)
            if j:
                ctx.journal.write(j, step=key, skipped=True)
            continue

        # FAIL-CLOSED STEP DISPATCH (REQ-LAND-030, #340).
        #
        # An uncaught exception here is how plan-062's landing — the first real `--apply` in
        # this repository's history — died: a bare `TypeError` at L18, after two pushes, three
        # public comments and `status: complete`, leaving the journal at `L_MIRRORED` with no
        # envelope, no halt class and no remediation.
        #
        # THREE PROPERTIES, EACH LOAD-BEARING:
        #
        # 1. `KeyboardInterrupt` / `SystemExit` are RE-RAISED. They do not inherit from
        #    `Exception`, so this clause is strictly redundant against the hierarchy — it is
        #    written anyway so the invariant is READABLE rather than inferred.
        # 2. The row is `inconclusive` and `journal=None`. The step established nothing, so the
        #    journal MUST NOT advance: advancing past a step that raised would manufacture
        #    exactly the evidence `_land_resume_done` exists to refuse. A resume therefore
        #    re-enters this step and raises again. That is CORRECT and must not be engineered
        #    around — and `LandingJournal.write` would reject any phase outside its closed
        #    17-state set anyway.
        # 3. The halted envelope is returned DIRECTLY from the handler. The loop's own predicate
        #    below is `verdict == "fail" and halting`, so an `inconclusive` row FALLS THROUGH
        #    and the loop runs the next step. For L18 that is invisible because L19 is next; for
        #    an early step the landing would walk PAST A CRASH INTO DESTRUCTIVE WORK.
        #
        # The caught class is bare `Exception` deliberately: the whole point is the *unexpected*
        # one, and an arity mismatch is on nobody's list.
        #
        # SCOPE, STATED HONESTLY: this wraps STEP DISPATCH ONLY. The executor's own bookkeeping
        # below — the journal write and the row-shape access after a step returns — is OUTSIDE
        # the wrap. That residue is NOT covered here and is NOT yet filed upstream; plan-063
        # Issue 6.1 files it, and the draft body is
        # `docs/plans/plan-063-james-dixson-3f74c1/assets/upstream-drafts/`. Stated this way
        # deliberately: a comment claiming a filing that does not exist is the same
        # unverified-assertion class this plan exists to remove.
        try:
            out = globals()[fname](ctx)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as exc:                      # noqa: BLE001 - see the comment above
            row = _step(
                key, "inconclusive",
                f"{fname} raised {type(exc).__name__}: {exc}. The step could not be judged, so "
                f"the journal was NOT advanced and the landing halts here. A RESUME WILL "
                f"RE-ENTER THIS SAME STEP AND RAISE AGAIN until the cause is fixed — that is "
                f"correct: advancing the journal past a step that raised would manufacture the "
                f"evidence a resume checks.",
                journal=None, halting=True,
                exception=type(exc).__name__,
                traceback=traceback.format_exc(),
                recovery="Fix the cause, then re-run `land --apply` with the same decision "
                         "file; the resume re-enters this step.",
            )
            results.append(row)
            ctx.results.append(row)
            return {"halted": True, "at": row["step"], "results": results,
                    "journal_phase": (ctx.journal.read() or {}).get("phase"),
                    "reason": row["reason"],
                    "recovery": row["detail"].get("recovery")}
        batch = out if isinstance(out, list) else [out]
        results.extend(batch)
        ctx.results.extend(batch)

        for r in batch:
            if r.get("journal"):
                ctx.journal.write(r["journal"], step=r["step"])
            if r["verdict"] == "fail" and r.get("halting"):
                if r.get("journal") and r["journal"] in LAND_CONFLICT_STATES:
                    pass                       # the conflict state is already recorded above
                return {"halted": True, "at": r["step"], "results": results,
                        "journal_phase": (ctx.journal.read() or {}).get("phase"),
                        "reason": r["reason"], "recovery": r.get("detail", {}).get("recovery")
                                                or r.get("recovery")}

    final = ctx.journal.read() or {}
    terminal = final.get("phase") == LAND_TERMINAL_STATE
    if terminal:
        # THE JOURNAL DESCRIBES AN IN-FLIGHT LANDING. Leaving it behind means the next
        # `--apply` for this plan reads a terminal phase and reports "already done" — and
        # leaves a permanent untracked file in the tree. `okf_hygiene` unlinks its journal on
        # the same reasoning. The phase is captured ABOVE the clear, so the return value still
        # reports it.
        ctx.journal.clear()
    return {"halted": False, "results": results, "journal_phase": final.get("phase"),
            "terminal": terminal,
            # SC36b: a rehearsal that halted at L2 must NOT satisfy R1's mitigation, so the
            # terminal state is REPORTED rather than inferred from "no error".
            "reached_terminal_state": terminal,
            "steps_executed": [r["step"] for r in results]}


if __name__ == "__main__":
    cli()
