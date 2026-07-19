# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml", "pytest"]
# ///
"""Tests for _shared/okf.py — the canonical OKF bundle engine.

Run:  env -u VIRTUAL_ENV uv run _shared/test_okf.py
 (or: uv run --with pytest --with pyyaml python3 -m pytest _shared/test_okf.py -q)

Each test names or comments the REQ-OKF-* id it anchors (SPEC
`skills/yf-okf/SPEC.md` §2). The mandatory resolver-composition test
(test_resolve_extension_composition_installed_layout) is the Epic-1
extension-resolver Capability Gate: it drives a VENDORED copy of okf.py in a
simulated installed address space (script + bundled OKF-EXTENSION.md only, no
sibling skills present) and asserts BASELINE ∪ YF-EXTENSIONS ∪ per-skill compose.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

_CANON = Path(__file__).parent / "okf.py"
_spec = importlib.util.spec_from_file_location("okf", _CANON)
okf = importlib.util.module_from_spec(_spec)
sys.modules["okf"] = okf
_spec.loader.exec_module(okf)


# --- helpers ----------------------------------------------------------------

def _load_vendored(script_path: Path):
    """Import a copy of okf.py at `script_path` so its `__file__` is that path
    (simulates a vendored skills/<skill>/scripts/okf.py address space)."""
    name = f"okf_vendored_{abs(hash(str(script_path)))}"
    spec = importlib.util.spec_from_file_location(name, script_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


FAKE_EXTENSION = """# OKF-FAKE — fake-skill per-skill OKF extension

## 0. Member identity

| Field | Value |
|:--|:--|
| `okf_spec:` member name | **OKF-FAKE** |
| Bundle form | **dir-form** |

## 1. `type` vocabulary (open vocab; OKF-FAKE owns this set)

| `type` value | Applies to |
|:--|:--|
| `Widget` | `widget.md` |

## 2. Required extension frontmatter keys

| Key | Force | Notes |
|:--|:-:|:--|
| `type` | MUST | `Widget` |
| `okf_spec` | MUST | `OKF-FAKE` |
| `gadget` | MUST | a fake-skill-only required key |

## 3. Reserved subdirs / files

| Reserved path | Holds |
|:--|:--|
| `index.md` | listing |
| `parts/` | Widget parts |
"""


# ===========================================================================
# REQ-OKF-FAM-001..003 — resolver composition (MANDATORY capability gate)
# ===========================================================================

def test_resolve_extension_composition_installed_layout(tmp_path):
    """REQ-OKF-FAM-001/002/003: a vendored okf.py resolves its OWN bundled
    OKF-EXTENSION.md with no sibling skill present, and check_conformance
    composes BASELINE ∪ YF-EXTENSIONS ∪ fake-skill's rules."""
    skill_dir = tmp_path / "skills" / "fake-skill"
    scripts = skill_dir / "scripts"
    scripts.mkdir(parents=True)
    # vendored copy of the canonical engine, byte-for-byte
    (scripts / "okf.py").write_text(_CANON.read_text())
    (skill_dir / "OKF-EXTENSION.md").write_text(FAKE_EXTENSION)
    # NOTE: no other skills/<x>/ dirs exist — proves no sibling is required.

    vend = _load_vendored(scripts / "okf.py")

    # resolve_extension() with NO arg finds the running skill's own extension
    ext = vend.resolve_extension()
    assert ext.found is True
    assert ext.skill == "fake-skill"
    assert ext.member == "OKF-FAKE"
    assert "Widget" in ext.type_vocab
    assert "gadget" in ext.required_keys
    assert "parts/" in ext.reserved_subdirs

    # composed effective ruleset reports all three members
    eff = vend.compose_ruleset()
    assert eff.members == ["OKF-BASELINE", "OKF-YF-EXTENSIONS", "OKF-FAKE"]

    # a conformant bundle passes; the composed required key `gadget` is enforced
    bundle = tmp_path / "bundle"
    vend.scaffold_bundle(bundle, spec_member="OKF-FAKE")
    good = bundle / "widget.md"
    good.write_text(vend._dump_frontmatter(
        {"type": "Widget", "okf_spec": "OKF-FAKE", "gadget": "yes"}) + "\n# Widget\n")
    findings = vend.check_conformance(bundle)
    assert findings.rulesets_composed == ["OKF-BASELINE", "OKF-YF-EXTENSIONS", "OKF-FAKE"]
    assert findings.ok, [f.as_dict() for f in findings.findings]

    # drop the composed-required `gadget` key -> a composed (FAM-001) WARNING on the
    # main-type doc (base engine warns; the per-skill adapter backfills member keys).
    good.write_text(vend._dump_frontmatter(
        {"type": "Widget", "okf_spec": "OKF-FAKE"}) + "\n# Widget\n")
    findings2 = vend.check_conformance(bundle)
    assert findings2.ok  # baseline still satisfied -> no error-level findings
    assert any(f.req == "REQ-OKF-FAM-001" and f.level == "warning" and "gadget" in f.message
               for f in findings2.findings)

    # a type outside the composed vocab -> a composed warning
    good.write_text(vend._dump_frontmatter(
        {"type": "Sprocket", "okf_spec": "OKF-FAKE", "gadget": "y"}) + "\n# Widget\n")
    findings3 = vend.check_conformance(bundle)
    assert any(f.req == "REQ-OKF-FAM-001" and "vocab" in f.message for f in findings3.findings)


def test_resolve_extension_canonical_address_space():
    """REQ-OKF-FAM-003: from the canonical _shared/okf.py, resolve_extension(skill)
    finds skills/<skill>/OKF-EXTENSION.md by repo-relative discovery."""
    ext = okf.resolve_extension("yf-plan")
    # the real yf-plan/OKF-EXTENSION.md is present in this worktree
    assert ext.found is True
    assert ext.member == "OKF-PLAN"
    assert "Plan" in ext.type_vocab


def test_resolve_extension_missing_is_report_only():
    """REQ-OKF-071: a missing OKF-EXTENSION.md yields found=False, never raises."""
    ext = okf.resolve_extension("no-such-skill")
    assert ext.found is False


# ===========================================================================
# REQ-OKF-070 — merge-and-preserve (foreign frontmatter survives)
# ===========================================================================

def test_write_frontmatter_preserves_foreign_keys(tmp_path):
    """REQ-OKF-070: adding `type` never drops Obsidian tags/aliases/cssclass."""
    p = tmp_path / "note.md"
    p.write_text(
        "---\n"
        "tags:\n- research\n- obsidian\n"
        "aliases:\n- my-note\n"
        "cssclass: wide\n"
        "---\n"
        "body text\n\n## Section\nmore\n"
    )
    okf.write_frontmatter(p, {"type": "Reference", "okf_spec": "OKF-RESEARCH"})
    fm, body = okf.read_frontmatter(p)
    # foreign keys survive with values intact
    assert fm["tags"] == ["research", "obsidian"]
    assert fm["aliases"] == ["my-note"]
    assert fm["cssclass"] == "wide"
    # yf keys added
    assert fm["type"] == "Reference"
    assert fm["okf_spec"] == "OKF-RESEARCH"
    # body preserved
    assert "body text" in body and "## Section" in body


def test_write_frontmatter_updates_in_place_keeps_order(tmp_path):
    """REQ-OKF-070: updating an existing key keeps its position; new keys append."""
    p = tmp_path / "n.md"
    p.write_text("---\na: 1\nb: 2\n---\nx\n")
    okf.write_frontmatter(p, {"b": 9, "type": "Plan"})
    fm, _ = okf.read_frontmatter(p)
    assert list(fm.keys()) == ["a", "b", "type"]
    assert fm["b"] == 9


# ===========================================================================
# REQ-OKF-071 — report-only / crash-safe
# ===========================================================================

def test_check_malformed_yaml_records_finding_no_raise(tmp_path):
    """REQ-OKF-071: unparseable YAML records a finding and does NOT raise."""
    b = tmp_path / "bundle"
    okf.scaffold_bundle(b, spec_member="OKF-PLAN")
    bad = b / "broken.md"
    bad.write_text("---\ntype: [unclosed\n: : :\n---\n# Body\n")
    findings = okf.check_conformance(b)  # must not raise
    assert any(f.req == "REQ-OKF-071" for f in findings.findings)


def test_check_nonconforming_file_records_finding(tmp_path):
    """REQ-OKF-071 / REQ-OKF-003: a frontmatter-less concept doc is flagged, no crash."""
    b = tmp_path / "bundle"
    okf.scaffold_bundle(b, spec_member="OKF-PLAN")
    (b / "nofm.md").write_text("# Just a heading\n\nno frontmatter here\n")
    findings = okf.check_conformance(b)
    assert not findings.ok
    assert any(f.req == "REQ-OKF-003" for f in findings.findings)


def test_migrate_dry_run_over_messy_input_no_raise(tmp_path):
    """REQ-OKF-071: migrate --dry-run over messy input returns a plan, never raises."""
    d = tmp_path / "legacy"
    d.mkdir()
    (d / "plan.md").write_text("---\n: bad : yaml :\n[\n---\n## Objective\nx\n")
    plan = okf.migrate(d, dry_run=True)  # must not raise
    assert plan.dry_run is True


# ===========================================================================
# REQ-OKF-021 — dual-mode read
# ===========================================================================

def test_dual_mode_read_equivalence(tmp_path):
    """REQ-OKF-021: frontmatter-only, **Field:**-only, and dual docs read to the
    same model; frontmatter wins where both present."""
    fm_only = "---\nid: plan-1\nauthor: james\nstatus: scoping\n---\n# T\n\n## Objective\nx\n"
    field_only = "**ID:** plan-1\n**Author:** james\n**Status:** scoping\n\n## Objective\nx\n"
    dual = (
        "---\nid: plan-1\nauthor: james\nstatus: scoping\n---\n"
        "**ID:** plan-1\n**Author:** james\n**Status:** scoping\n\n## Objective\nx\n"
    )
    m1 = okf.read_fields(fm_only)
    m2 = okf.read_fields(field_only)
    m3 = okf.read_fields(dual)
    for m in (m1, m2, m3):
        assert m["id"] == "plan-1"
        assert m["author"] == "james"
        assert m["status"] == "scoping"


def test_read_fields_frontmatter_wins_over_field(tmp_path):
    """REQ-OKF-021: when a key is in both, the frontmatter value wins."""
    doc = "---\nstatus: approved\n---\n**Status:** scoping\n\n## Objective\nx\n"
    assert okf.read_fields(doc)["status"] == "approved"


# ===========================================================================
# REQ-OKF-020 / REQ-OKF-010 — dual-write + placement above first `## `
# ===========================================================================

def test_write_fields_emits_both_above_first_h2(tmp_path):
    """REQ-OKF-020 + REQ-OKF-010: write_fields emits BOTH a frontmatter block and
    **Field:** lines, both above the first `## ` heading."""
    p = tmp_path / "plan.md"
    p.write_text("# Title\n\n## Objective\n\nthe objective body\n")
    okf.write_fields(
        p,
        {"id": "plan-9", "author": "james", "status": "scoping"},
        field_labels={"id": "ID"},
    )
    text = p.read_text()
    h2 = text.index("## Objective")
    fm_end = text.index("---", text.index("---") + 3)
    # frontmatter block is above the first ##
    assert fm_end < h2
    # **Field:** lines present and above the first ##
    assert "**ID:** plan-9" in text
    assert text.index("**ID:** plan-9") < h2
    assert text.index("**Author:** james") < h2
    # body under ## preserved
    assert "the objective body" in text
    # round-trips back to the model
    m = okf.read_fields(p)
    assert m["id"] == "plan-9" and m["status"] == "scoping"


def test_check_flags_field_below_first_h2(tmp_path):
    """REQ-OKF-010: a **Field:** line below the first `## ` is a finding."""
    b = tmp_path / "bundle"
    okf.scaffold_bundle(b, spec_member="OKF-PLAN")
    (b / "bad.md").write_text(
        "---\ntype: Plan\nokf_spec: OKF-PLAN\n---\n## Objective\n\n**ID:** x\n"
    )
    findings = okf.check_conformance(b)
    assert any(f.req == "REQ-OKF-010" for f in findings.findings)


def test_check_ignores_bold_prose_leadin_below_h2(tmp_path):
    """REQ-OKF-010: a bold PROSE lead-in below the first `## ` (a `**Label:**` with
    NO inline value — a heading for a following list) is NOT a metadata field and is
    NOT flagged (matches read_fields, which ignores empty-value lines)."""
    b = tmp_path / "bundle"
    okf.scaffold_bundle(b, spec_member="OKF-PLAN")
    (b / "ok.md").write_text(
        "---\ntype: Plan\nokf_spec: OKF-PLAN\n---\n"
        "## Objective\n\n**Key facts:**\n\n- one\n- two\n\n**Option A (manual):**\n\ndo it\n"
    )
    findings = okf.check_conformance(b)
    assert not any(f.req == "REQ-OKF-010" for f in findings.findings)


# ===========================================================================
# REQ-OKF-002 / REQ-OKF-MIG-002 — append_log newest-first + earliest preserved
# ===========================================================================

def test_append_log_newest_first_and_preserves_earliest(tmp_path):
    """REQ-OKF-002: entries newest-first; REQ-OKF-MIG-002: earliest date preserved."""
    b = tmp_path / "bundle"
    okf.scaffold_bundle(b, spec_member="OKF-PLAN")
    okf.append_log(b, "scoping started", date="2026-01-01")
    okf.append_log(b, "approved", date="2026-06-01")
    okf.append_log(b, "second same-day note", date="2026-06-01")
    text = (b / "log.md").read_text()
    dates = okf._LOG_DATE_RE.findall(text)
    # newest-first ordering
    assert dates == sorted(dates, reverse=True)
    assert dates[0] == "2026-06-01"
    # earliest (grandfather) date preserved
    assert "2026-01-01" in text
    assert "scoping started" in text
    # same-day bullet folded under one heading (not a duplicate date heading)
    assert dates.count("2026-06-01") == 1


def test_append_log_rejects_bad_date(tmp_path):
    b = tmp_path / "bundle"
    okf.scaffold_bundle(b, spec_member="OKF-PLAN")
    with pytest.raises(ValueError):
        okf.append_log(b, "x", date="2026/01/01")


# ===========================================================================
# REQ-OKF-MIG-001 — migrate --dry-run returns a plan without mutating
# ===========================================================================

def test_migrate_dry_run_returns_plan_without_mutating(tmp_path):
    """REQ-OKF-MIG-001: --dry-run emits a change plan and mutates nothing."""
    d = tmp_path / "docs" / "plans" / "plan-x"
    d.mkdir(parents=True)
    (d / "README.md").write_text("# Plan bundle\n\n- plan.md\n")
    (d / "plan.md").write_text(
        "**ID:** plan-x\n"
        "**Phase log:** 2026-03-01 scoping; 2026-04-01 approved\n\n"
        "## Objective\n\nthe body\n"
    )
    (d / "context.md").write_text("# Context\n\nno frontmatter\n")

    before = {p.name: p.read_text() for p in d.iterdir()}
    plan = okf.migrate(d, dry_run=True, skill="yf-plan")

    # nothing mutated
    assert not (d / "index.md").exists()
    assert {p.name: p.read_text() for p in d.iterdir()} == before

    ops = {(c.op, c.path) for c in plan.changes}
    assert ("rename", "README.md") in ops
    # I-3: the op is `extract-log` (plan.md kept, not renamed), not `move-phase-log`
    assert ("extract-log", "plan.md") in ops
    assert any(c.op == "add-frontmatter" and c.path == "context.md" for c in plan.changes)
    # extract-log keeps the source and captures the grandfather date (REQ-OKF-MIG-002)
    move = next(c for c in plan.changes if c.op == "extract-log")
    assert move.detail["first_scoping_date"] == "2026-03-01"
    assert move.detail["source_kept"] is True
    # I-1: context.md is typed `Environment` from the yf-plan role->type map, not Concept
    ctx = next(c for c in plan.changes if c.op == "add-frontmatter" and c.path == "context.md")
    assert ctx.detail["keys"]["type"] == "Environment"
    # member composed from yf-plan extension
    assert plan.member == "OKF-PLAN"


def test_migrate_apply_is_hash_neutral_below_h2(tmp_path):
    """REQ-OKF-MIG-003 (positional): migrate changes stay above the first `## `,
    so the body from `## ` onward is byte-identical after migrate."""
    d = tmp_path / "plan-y"
    d.mkdir()
    body_from_h2 = "## Objective\n\nunchanged objective body\n\n## Plan\n\nsteps\n"
    (d / "plan.md").write_text(
        "**ID:** plan-y\n**Phase log:** 2026-02-01 scoping\n\n" + body_from_h2
    )
    okf.migrate(d, dry_run=False, skill="yf-plan")
    after = (d / "plan.md").read_text()
    # everything from the first `## ` onward is preserved verbatim
    assert after[after.index("## Objective"):] == body_from_h2


def test_migrate_extract_log_preserves_all_dated_bullets(tmp_path):
    """REQ-OKF-MIG-002 + yf-plan REQ-PORT-006: the extract-log op transcribes EVERY
    dated `**Phase log:**` bullet into log.md (each `<status>:` token preserved), not
    just the first `scoping:` date — so a plan's `review:`-line count (and thus the
    count-equality with reviews/pass-*.md) survives migration."""
    d = tmp_path / "plan-z"
    d.mkdir()
    (d / "plan.md").write_text(
        "**ID:** plan-z\n"
        "**Phase log:**\n"
        "- 2026-04-05 scoping: initial scope captured\n"
        "- 2026-04-05 review: plan v1 presented — REVISE\n"
        "- 2026-04-05 review: plan v2 presented\n"
        "- 2026-04-05 approved: operator approved\n\n"
        "## Objective\n\nbody\n"
    )
    plan = okf.migrate(d, dry_run=False, skill="yf-plan")
    move = next(c for c in plan.changes if c.op == "extract-log")
    assert move.detail["first_scoping_date"] == "2026-04-05"
    assert move.detail["entries"] == 4
    log_text = (d / "log.md").read_text()
    # every entry survives, review: token preserved -> count-equality intact
    assert log_text.count("- review:") == 2
    assert "- scoping: initial scope captured" in log_text
    assert "- approved: operator approved" in log_text
    # the block is removed from plan.md (hash-neutral, above the first `## `)
    assert "**Phase log:**" not in (d / "plan.md").read_text()


def test_migrate_extract_log_inline_form_falls_back_to_scoping(tmp_path):
    """An inline/semicolon-form phase log (no `- ` bullets) has no dated bullets, so
    extract-log falls back to the single first-`scoping:` line (legacy behavior)."""
    d = tmp_path / "plan-w"
    d.mkdir()
    (d / "plan.md").write_text(
        "**ID:** plan-w\n**Phase log:** 2026-03-01 scoping; 2026-04-01 approved\n\n"
        "## Objective\n\nbody\n"
    )
    plan = okf.migrate(d, dry_run=False, skill="yf-plan")
    move = next(c for c in plan.changes if c.op == "extract-log")
    assert move.detail["entries"] == 0
    log_text = (d / "log.md").read_text()
    assert "2026-03-01" in log_text
    assert "scoping" in log_text


# ===========================================================================
# REQ-OKF-001/002/003/031/050/060 — bundle model
# ===========================================================================

def test_scaffold_creates_reserved_files_without_type(tmp_path):
    """REQ-OKF-001/002/031: scaffold makes index.md + log.md carrying no type."""
    b = tmp_path / "bundle"
    okf.scaffold_bundle(b, spec_member="OKF-PLAN", subdirs=["findings", "reviews"])
    assert (b / "index.md").exists() and (b / "log.md").exists()
    assert (b / "findings").is_dir() and (b / "reviews").is_dir()
    fm, _ = okf.read_frontmatter(b / "index.md")
    assert "type" not in fm and "okf_spec" not in fm
    assert fm.get("okf_version") == okf.okf_version


def test_check_reserved_index_with_type_is_flagged(tmp_path):
    """REQ-OKF-031: a reserved index.md carrying `type` is a finding."""
    b = tmp_path / "bundle"
    okf.scaffold_bundle(b, spec_member="OKF-PLAN")
    (b / "index.md").write_text("---\ntype: Plan\n---\n# Idx\n")
    findings = okf.check_conformance(b)
    assert any(f.req == "REQ-OKF-031" for f in findings.findings)


def test_single_file_bundle_exemption(tmp_path):
    """REQ-OKF-050: a lone .md is exempt from reserved index/log; only its own
    frontmatter+type is checked."""
    solo = tmp_path / "my-incubator.md"
    solo.write_text(
        "---\ntype: Incubator\nokf_spec: OKF-INCUBATOR\ntitle: t\n---\n"
        "## Resume\n\nnotes\n"
    )
    findings = okf.check_conformance(solo)
    assert findings.ok, [f.as_dict() for f in findings.findings]
    # no index.md/log.md findings for a single-file bundle
    assert not any(f.req in ("REQ-OKF-001", "REQ-OKF-002") for f in findings.findings)


def test_non_md_files_excluded(tmp_path):
    """REQ-OKF-060: non-.md sidecars are not flagged for missing frontmatter."""
    b = tmp_path / "bundle"
    okf.scaffold_bundle(b, spec_member="OKF-RESEARCH")
    (b / "sources.json").write_text('{"x": 1}\n')
    (b / "plan.yaml").write_text("dag: []\n")
    (b / "Summary.md").write_text(
        "---\ntype: Research Report\nokf_spec: OKF-RESEARCH\nidx: '001'\ntopic: t\ncreated: 2026-01-01\n---\n# S\n"
    )
    findings = okf.check_conformance(b, skill="yf-research")
    # sources.json / plan.yaml never appear in findings
    assert not any(f.path.endswith(".json") or f.path.endswith(".yaml") for f in findings.findings)


def test_add_index_entry_appends_bullet(tmp_path):
    """REQ-OKF-001: add_index_entry appends a listing bullet, keeps okf_version."""
    b = tmp_path / "bundle"
    okf.scaffold_bundle(b, spec_member="OKF-PLAN")
    okf.add_index_entry(b, "plan.md", "the plan of record")
    text = (b / "index.md").read_text()
    assert "- [plan.md](plan.md) - the plan of record" in text
    fm, _ = okf.read_frontmatter(b / "index.md")
    assert fm.get("okf_version") == okf.okf_version
    # idempotent
    okf.add_index_entry(b, "plan.md", "the plan of record")
    assert (b / "index.md").read_text().count("[plan.md]") == 1


# ===========================================================================
# Baked-in ruleset constants (REQ-OKF-FAM-002)
# ===========================================================================

def test_baked_in_ruleset_constants():
    """REQ-OKF-FAM-002: BASELINE + YF-EXTENSIONS ruleset is baked into okf.py."""
    assert okf.okf_version == "0.1"
    assert okf.RESERVED_FILES == ("index.md", "log.md")
    assert set(okf.BASELINE_MUSTS) == {"B1", "B2", "B3"}
    assert "OKF-SPECIFICATION" in okf.RESERVED_DEFERRED_MEMBERS
    assert "okf_spec" in okf.YF_EXTENSION_RULES


# ===========================================================================
# REQ-OKF-MIG-004 — role -> type map (no blanket `type: Concept`)
# ===========================================================================

def test_migrate_assigns_types_from_role_map_plan(tmp_path):
    """REQ-OKF-MIG-004 (I-1): each non-reserved .md gets its role's type from the
    OKF-PLAN map — Plan/Finding/Review/Environment/Reference — not blanket Concept."""
    d = tmp_path / "plan-z"
    (d / "findings").mkdir(parents=True)
    (d / "reviews").mkdir()
    (d / "references").mkdir()
    (d / "README.md").write_text("# Plan\n\n- plan.md\n")
    (d / "plan.md").write_text("**ID:** plan-z\n\n## Objective\n\nbody\n")
    (d / "context.md").write_text("# Context\n\nenv\n")
    (d / "findings" / "exp-001.md").write_text("# Finding\n\nresult\n")
    (d / "reviews" / "pass-1.md").write_text("# Review\n\nverdict\n")
    (d / "references" / "upstream-3.md").write_text("# Upstream\n\nbody\n")

    plan = okf.migrate(d, dry_run=True, skill="yf-plan")
    types = {c.path: c.detail["keys"]["type"] for c in plan.changes if c.op == "add-frontmatter"}
    assert types["plan.md"] == "Plan"
    assert types["context.md"] == "Environment"
    assert types["findings/exp-001.md"] == "Finding"
    assert types["reviews/pass-1.md"] == "Review"
    assert types["references/upstream-3.md"] == "Reference"
    # none stamped the blanket default
    assert "Concept" not in types.values()


def test_migrate_default_fallback_is_recorded(tmp_path):
    """REQ-OKF-MIG-004: a file matching no role rule falls back to the default and
    the fallback is RECORDED (type_source), never silently mislabeled."""
    d = tmp_path / "plan-w"
    d.mkdir()
    (d / "plan.md").write_text("## Objective\n\nbody\n")
    (d / "random-note.md").write_text("# Note\n\nunmapped\n")
    plan = okf.migrate(d, dry_run=True, skill="yf-plan")
    note = next(c for c in plan.changes if c.op == "add-frontmatter" and c.path == "random-note.md")
    assert note.detail["keys"]["type"] == "Concept"
    assert note.detail.get("type_source") == "default-fallback"
    # a mapped file carries no fallback marker
    pm = next(c for c in plan.changes if c.op == "add-frontmatter" and c.path == "plan.md")
    assert "type_source" not in pm.detail


# ===========================================================================
# REQ-OKF-MIG-005 — member-driven reserved-file reconciliation
# ===========================================================================

def _write_research_bundle(d):
    (d / "artifacts").mkdir(parents=True)
    (d / "_index.md").write_text("| Timestamp | Phase | Artifact |\n|---|---|---|\n")
    (d / "Summary.md").write_text("**Research project:** 001 okf · **Phase:** package\n\n## Executive summary\n\nx\n")
    (d / "artifacts" / "critique.md").write_text("# Critique\n\ny\n")
    (d / "sources.md").write_text("# Sources\n\n- [s1](http://x)\n")
    (d / "sources.json").write_text('{"s1": 1}\n')


def test_migrate_research_reserved_files_then_check_clean(tmp_path):
    """REQ-OKF-MIG-005 (I-2): research uses `_index.md` and no phase-log; migrate
    renames `_index.md` -> index.md and SCAFFOLDS log.md, so `check` PASSES after a
    full (non-dry) migrate — the member gap 2.1/2.2 surfaced is closed."""
    d = tmp_path / "docs" / "research" / "001-x"
    _write_research_bundle(d)
    plan = okf.migrate(d, dry_run=False, skill="yf-research")
    ops = {(c.op, c.path) for c in plan.changes}
    assert ("rename", "_index.md") in ops       # _index.md -> index.md
    assert ("scaffold-log", "log.md") in ops     # no phase-log -> scaffold
    assert (d / "index.md").exists() and (d / "log.md").exists()
    # _index.md became reserved index.md (no type), so it is exempt
    ifm, _ = okf.read_frontmatter(d / "index.md")
    assert "type" not in ifm and "okf_spec" not in ifm
    # Summary typed Research Report; artifact typed Research Artifact
    sfm, _ = okf.read_frontmatter(d / "Summary.md")
    assert sfm["type"] == "Research Report" and sfm["okf_spec"] == "OKF-RESEARCH"
    afm, _ = okf.read_frontmatter(d / "artifacts" / "critique.md")
    assert afm["type"] == "Research Artifact"
    # check is error-free after migrate (member keys idx/topic are warnings only)
    findings = okf.check_conformance(d, skill="yf-research")
    assert findings.ok, [f.as_dict() for f in findings.findings if f.level == "error"]


def test_migrate_incubator_keeps_readme_state_file_then_check_clean(tmp_path):
    """REQ-OKF-MIG-005 (I-2): a dir-form incubator's README.md is the TYPED STATE
    FILE, not the listing — migrate KEEPS it (types it Incubator) and SCAFFOLDS
    index.md/log.md. check PASSES after a full migrate."""
    d = tmp_path / "Incubator" / "codemage"
    d.mkdir(parents=True)
    (d / "README.md").write_text(
        "---\ntitle: codemage\ncreated: 2026-05-13\n"
        "tags: [incubator, agents]\nstatus: incubating\naliases: [codemage]\n---\n"
        "## Resume\n\nnotes\n"
    )
    (d / "00Index.md").write_text("---\ntitle: 00Index\ntags: []\n---\nconcept\n")
    plan = okf.migrate(d, dry_run=False, skill="yf-incubator")
    ops = {(c.op, c.path) for c in plan.changes}
    # README is NOT renamed to index.md; index/log are scaffolded
    assert ("rename", "README.md") not in ops
    assert ("scaffold-index", "index.md") in ops
    assert ("scaffold-log", "log.md") in ops
    assert (d / "README.md").exists()  # state file kept
    rfm, _ = okf.read_frontmatter(d / "README.md")
    assert rfm["type"] == "Incubator" and rfm["okf_spec"] == "OKF-INCUBATOR"
    # merge-and-preserve: the foreign 7-key frontmatter survives (REQ-OKF-070)
    assert rfm["tags"] == ["incubator", "agents"] and rfm["aliases"] == ["codemage"]
    findings = okf.check_conformance(d, skill="yf-incubator")
    assert findings.ok, [f.as_dict() for f in findings.findings if f.level == "error"]


# ===========================================================================
# REQ-OKF-020 — migrate establishes the dual-field mirror
# ===========================================================================

def test_migrate_mirrors_field_lines_into_frontmatter(tmp_path):
    """REQ-OKF-020 (I-4): migrate lifts existing `**ID:**`/`**Status:**` header lines
    into frontmatter (id/status), keeping BOTH surfaces — not frontmatter alone."""
    d = tmp_path / "plan-dual"
    d.mkdir()
    (d / "plan.md").write_text(
        "**ID:** plan-dual\n**Author:** james\n**Status:** approved\n\n## Objective\n\nbody\n"
    )
    plan = okf.migrate(d, dry_run=False, skill="yf-plan")
    fm, body = okf.read_frontmatter(d / "plan.md")
    # frontmatter mirror established from the **Field:** lines
    assert fm["id"] == "plan-dual"
    assert fm["author"] == "james"
    assert fm["status"] == "approved"
    assert fm["type"] == "Plan" and fm["okf_spec"] == "OKF-PLAN"
    # the human **Field:** surface is kept (dual, not replaced)
    assert "**ID:** plan-dual" in body
    # the change plan advertises the mirrored fields
    pm = next(c for c in plan.changes if c.op == "add-frontmatter" and c.path == "plan.md")
    assert set(pm.detail["mirrored_fields"]) >= {"id", "author", "status"}


def test_migrate_plan_full_then_check_clean(tmp_path):
    """REQ-OKF-MIG-001/005: a full plan migrate (README->index, phase-log extract,
    typed frontmatter, dual-field mirror) yields an error-free `check`."""
    d = tmp_path / "docs" / "plans" / "plan-clean"
    (d / "findings").mkdir(parents=True)
    (d / "references").mkdir()
    (d / "README.md").write_text("# Plan bundle\n\n- plan.md\n")
    (d / "plan.md").write_text(
        "**ID:** plan-clean\n**Author:** james\n**Created:** 2026-04-01\n**Status:** approved\n"
        "**Phase log:** 2026-03-01 scoping; 2026-04-01 approved\n\n## Objective\n\nbody\n"
    )
    (d / "context.md").write_text("# Context\n\nenv\n")
    (d / "findings" / "exp-001.md").write_text("# Finding\n\nresult\n")
    (d / "references" / "upstream-3.md").write_text("# Upstream\n\nbody\n")
    okf.migrate(d, dry_run=False, skill="yf-plan")
    assert (d / "index.md").exists() and not (d / "README.md").exists()
    assert (d / "log.md").exists() and "2026-03-01" in (d / "log.md").read_text()
    findings = okf.check_conformance(d, skill="yf-plan")
    assert findings.ok, [f.as_dict() for f in findings.findings if f.level == "error"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
