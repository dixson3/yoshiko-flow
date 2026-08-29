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
    assert okf.okf_version == "0.2"
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


# ===========================================================================
# render_index + index-drift coverage (plan-046 Epic 1, Issue 1.5)
#
# Measured hole this section closes: a mutation disabling the RESERVED_FILES
# filter in render_index() survived all 31 pre-existing tests, while
# render_index regressed to emitting `- [log.md](log.md)`. render_index is the
# function plan-046 Epic 3 rewrites, so it is gated here BEFORE it is touched.
# ===========================================================================

def _generated_index(bundle):
    """render_index() over a bundle that has NO index.md — the generating path.

    scaffold_bundle() always writes an index.md, and render_index() returns an
    existing one verbatim, so the generating branch is only reachable when no
    index.md is present. Tests that mean to exercise generation must not scaffold.
    """
    return okf.render_index(bundle)


def test_render_index_excludes_reserved_files(tmp_path):
    """REQ-OKF-001/031: the generated listing never lists index.md or log.md.

    THE MUTATION-KILLING TEST. Disabling the `child.name in RESERVED_FILES`
    filter in render_index() makes this fail with `- [log.md](log.md)` present;
    it left every other test in this file green.
    """
    b = tmp_path / "bundle"
    b.mkdir()
    (b / "log.md").write_text("# Log\n\n")          # reserved, must not be listed
    (b / "plan.md").write_text("---\ntype: Plan\n---\n# P\n")
    out = _generated_index(b)
    assert "- [plan.md](plan.md)" in out
    for reserved in okf.RESERVED_FILES:
        assert f"- [{reserved}]" not in out, f"reserved file {reserved} leaked into the listing:\n{out}"


def test_render_index_excludes_dotfiles(tmp_path):
    """REQ-OKF-001: dot-prefixed children are structural, never listing members."""
    b = tmp_path / "bundle"
    b.mkdir()
    (b / ".hidden.md").write_text("x\n")
    (b / ".git").mkdir()
    (b / "plan.md").write_text("---\ntype: Plan\n---\n# P\n")
    out = _generated_index(b)
    assert "- [plan.md](plan.md)" in out
    assert ".hidden.md" not in out and ".git" not in out


def test_render_index_includes_non_md_sidecars(tmp_path):
    """REQ-OKF-001 / v0.2 §8: an index enumerates the directory's CONTENTS.

    Non-`.md` sidecars (`plan.yaml`, `sources.json`) are listing members even
    though REQ-OKF-060 excludes them from FRONTMATTER conformance — two
    different axes. Research bundles carry these and a cold reader needs them
    listed; measured 11 such sidecars across the corpus, all in research bundles.
    """
    b = tmp_path / "bundle"
    b.mkdir()
    (b / "sources.json").write_text("{}\n")
    (b / "plan.md").write_text("---\ntype: Plan\n---\n# P\n")
    out = _generated_index(b)
    assert "- [sources.json](sources.json)" in out
    assert "- [plan.md](plan.md)" in out


def test_render_index_returns_existing_index_verbatim(tmp_path):
    """REQ-OKF-001: an existing index.md is returned byte-for-byte.

    This is the prose-preservation guarantee plan-046 Epic 3 (Issue 3.4) builds
    the marker model on top of: render_index() must never silently regenerate
    over hand-written orientation prose.
    """
    b = tmp_path / "bundle"
    b.mkdir()
    handwritten = "---\nokf_version: '0.2'\n---\n\n# Bundle\n\n## Note on scope\n\nhand-written prose.\n"
    (b / "index.md").write_text(handwritten)
    (b / "plan.md").write_text("---\ntype: Plan\n---\n# P\n")
    assert okf.render_index(b) == handwritten


def test_render_index_lists_subdirs_and_md_children(tmp_path):
    """REQ-OKF-001: subdirs render as `- [name/](name/index.md)`, .md as `- [f](f)`.

    Characterization test pinning the CURRENT generated shape. plan-046 Epic 3
    changes what a subdirectory entry may point at (the ghost-directory-link
    defect, 25 live ML003 violations); this test is the anchor that makes that
    change deliberate rather than silent.
    """
    b = tmp_path / "bundle"
    (b / "findings").mkdir(parents=True)
    (b / "plan.md").write_text("---\ntype: Plan\n---\n# P\n")
    out = _generated_index(b)
    assert "- [findings/](findings/index.md)" in out
    assert "- [plan.md](plan.md)" in out


def test_render_index_generated_file_entries_all_resolve(tmp_path):
    """INDEX DRIFT: every generated *file* bullet resolves to a real path.

    The drift class plan-046 exists to fix is an index asserting a file that is
    not there. Scoped to file entries on purpose: the generated *directory*
    entry points at `<dir>/index.md`, which does not exist below a bundle root
    today — that is the known ghost-directory defect Epic 3 addresses, and
    asserting against it here would fail for the right reason at the wrong time.
    """
    import re
    b = tmp_path / "bundle"
    (b / "findings").mkdir(parents=True)
    (b / "plan.md").write_text("---\ntype: Plan\n---\n# P\n")
    (b / "context.md").write_text("---\ntype: Context\n---\n# C\n")
    (b / "log.md").write_text("# Log\n\n")
    out = _generated_index(b)
    targets = [t for _, t in re.findall(r"- \[([^\]]+)\]\(([^)]+)\)", out)]
    file_targets = [t for t in targets if not t.endswith("/index.md")]
    assert file_targets, f"no file entries generated:\n{out}"
    for t in file_targets:
        assert (b / t).exists(), f"ghost entry: index lists {t!r} which does not exist"


def test_add_index_entry_does_not_duplicate_reserved(tmp_path):
    """REQ-OKF-031: add_index_entry keeps reserved frontmatter and stays idempotent
    even when the same path is added with a different description."""
    b = tmp_path / "bundle"
    okf.scaffold_bundle(b, spec_member="OKF-PLAN")
    okf.add_index_entry(b, "plan.md", "first")
    okf.add_index_entry(b, "plan.md", "second")
    text = (b / "index.md").read_text()
    assert text.count("[plan.md]") == 1
    fm, _ = okf.read_frontmatter(b / "index.md")
    assert "type" not in fm and "okf_spec" not in fm


# ===========================================================================
# reindex — root-scoped generation and drift (plan-046 Epic 3, Issue 3.5)
# REQ-OKF-004 (bundle root), REQ-OKF-011 (verb/verdicts), REQ-OKF-032
# (root-only okf_version), REQ-OKF-072 (prose preservation).
# ===========================================================================

def _bundle(tmp_path, name="b", index=None, files=(), dirs=()):
    b = tmp_path / name
    b.mkdir(parents=True)
    for f in files:
        (b / f).write_text(f"---\ntype: Concept\n---\n# {f}\n")
    for d in dirs:
        (b / d).mkdir(parents=True, exist_ok=True)
    if index is not None:
        (b / "index.md").write_text(index)
    return b


# --- REQ-OKF-032: okf_version is root-only ---------------------------------

def test_render_index_nested_emits_no_okf_version(tmp_path):
    """REQ-OKF-032: a NON-root generated index carries no frontmatter at all.

    OKF v0.2 §8: index files carry no frontmatter, "with one exception: a
    bundle-root index.md MAY carry an okf_version key". exp-003 MEASURED the
    old behaviour emitting it on a nested directory.
    """
    b = _bundle(tmp_path, files=["a.md"])
    assert "okf_version" not in okf.render_index(b, root=False)
    assert "okf_version" in okf.render_index(b, root=True)


def test_scaffold_nested_emits_no_okf_version(tmp_path):
    """REQ-OKF-032 at the scaffold write site."""
    okf.scaffold_bundle(tmp_path / "nested", root=False)
    assert "okf_version" not in (tmp_path / "nested" / "index.md").read_text()
    okf.scaffold_bundle(tmp_path / "rooted", root=True)
    assert "okf_version" in (tmp_path / "rooted" / "index.md").read_text()


# --- REQ-OKF-011: the three-way verdict ------------------------------------

def test_reindex_no_index_is_its_own_verdict(tmp_path):
    """REQ-OKF-011: no root index.md → `no-index`, exit 2 — never 0, never 1.

    THE LOAD-BEARING TEST for D-11. If an index-less bundle returned 0 it would
    be counted green in the corpus sweep; if it returned 1 it would manufacture
    drift findings for a file that does not exist.
    """
    b = _bundle(tmp_path, files=["plan.md"])           # no index.md written
    res = okf.reindex_check(b)
    assert res["verdict"] == "no-index"
    assert res["exit"] == 2
    assert okf.REINDEX_EXIT["clean"] == 0 and okf.REINDEX_EXIT["drift"] == 1


def test_reindex_clean_bundle_exits_zero(tmp_path):
    b = _bundle(tmp_path, files=["plan.md"],
                index="# b\n\n- [plan.md](plan.md) - the plan\n")
    res = okf.reindex_check(b)
    assert res["verdict"] == "clean" and res["exit"] == 0, res


def test_reindex_ghost_covers_dead_files_and_dead_dirs(tmp_path):
    """REQ-OKF-011: `ghost` must cover a dead DIRECTORY target, not only a file.

    This is the unit mismatch that made two independent counts disagree: a
    prototype that resolved only file targets scored ghost=1 where the real
    corpus had 24 dead *directory* links.
    """
    b = _bundle(tmp_path, files=["plan.md"],
                index="# b\n\n- [plan.md](plan.md)\n- [gone.md](gone.md)\n- [diagrams/](diagrams/)\n")
    res = okf.reindex_check(b)
    kinds = [f["target"] for f in res["findings"] if f["kind"] == "ghost"]
    assert "gone.md" in kinds, res
    assert "diagrams/" in kinds, "a dead DIRECTORY link must be a ghost"
    assert res["exit"] == 1


def test_reindex_missing_reports_unlisted_member(tmp_path):
    b = _bundle(tmp_path, files=["plan.md", "upstream-triage.md"],
                index="# b\n\n- [plan.md](plan.md)\n")
    res = okf.reindex_check(b)
    assert any(f["kind"] == "missing" and f["target"] == "upstream-triage.md"
               for f in res["findings"]), res


def test_reindex_empty_dir_is_reported(tmp_path):
    b = _bundle(tmp_path, files=["plan.md"], dirs=["findings"],
                index="# b\n\n- [plan.md](plan.md)\n- [findings/](findings/)\n")
    res = okf.reindex_check(b)
    assert any(f["kind"] == "empty-dir" for f in res["findings"]), res


def test_reindex_check_never_mutates(tmp_path):
    b = _bundle(tmp_path, files=["plan.md", "extra.md"],
                index="# b\n\n- [plan.md](plan.md)\n- [gone.md](gone.md)\n")
    before = (b / "index.md").read_text()
    okf.reindex_check(b)
    assert (b / "index.md").read_text() == before


def test_reindex_reserved_files_are_not_missing(tmp_path):
    """index.md/log.md are reserved — never listing members, so never `missing`."""
    b = _bundle(tmp_path, files=["plan.md"], index="# b\n\n- [plan.md](plan.md)\n")
    (b / "log.md").write_text("# Log\n\n")
    res = okf.reindex_check(b)
    assert res["verdict"] == "clean", res


# --- REQ-OKF-072: prose preservation ---------------------------------------

def test_reindex_write_hard_errors_on_unbalanced_marker(tmp_path):
    """REQ-OKF-072: an unbalanced marker is a HARD ERROR and writes NOTHING.

    Force differs from `discarded_prose` on purpose: an unbounded region would
    discard prose unrecoverably, whereas a dropped line is recoverable from git.
    """
    b = _bundle(tmp_path, files=["plan.md"],
                index="<!-- intro:start -->\n# b\n\n- [plan.md](plan.md)\n")
    before = (b / "index.md").read_text()
    with pytest.raises(okf.MarkerImbalanceError):
        okf.reindex_write(b)
    assert (b / "index.md").read_text() == before, "a hard error must not write"


def test_reindex_write_preserves_prose_without_markers(tmp_path):
    """REQ-OKF-072: hand-written prose survives regeneration with NO markers.

    The whole corpus is hand-written and marker-free, so preservation cannot
    depend on markers being present. Modelled on the live case: a plan bundle
    carrying a trailing `## Note on ...` section a naive regenerator deletes.
    """
    index = (
        "---\nokf_version: '0.2'\n---\n\n# b\n\n"
        "> An intro blockquote a regenerator must not eat.\n\n"
        "- [plan.md](plan.md) - the plan of record\n"
        "- [gone/](gone/)\n\n"
        "## Note on `scope-answers.md`\n\nThis bundle has no scope-answers.md, deliberately.\n"
    )
    b = _bundle(tmp_path, files=["plan.md", "upstream-triage.md"], index=index)
    res = okf.reindex_write(b)
    out = (b / "index.md").read_text()
    assert "An intro blockquote a regenerator must not eat." in out
    assert "## Note on `scope-answers.md`" in out
    assert "deliberately." in out
    assert "- [gone/](gone/)" not in out, "ghost should be dropped"
    assert "- [upstream-triage.md](upstream-triage.md)" in out, "missing should be appended"
    assert "okf_version" in out, "existing frontmatter is preserved (D-2: no migration)"
    assert res["changed"] is True


def test_reindex_write_preserves_existing_descriptions(tmp_path):
    """REQ-OKF-072: a surviving entry keeps its description verbatim."""
    b = _bundle(tmp_path, files=["plan.md"],
                index="# b\n\n- [plan.md](plan.md) - a carefully worded description\n")
    okf.reindex_write(b)
    assert "- [plan.md](plan.md) - a carefully worded description" in (b / "index.md").read_text()


def test_reindex_write_never_invents_a_description(tmp_path):
    """REQ-OKF-072: a NEW entry is bare — no `*description pending*` placeholder.

    Re-measured 2026-08-28 (plan-056 Issue 0.8): `description` is present on
    a MINORITY of nested files (189 of 993 at 2026-08-28, and rising), so a placeholder
    would write hundreds of assertions that a description exists when none does. The older "0 of 423" figure is stale on
    both terms; the invariant this test pins is unchanged by the re-measurement.
    """
    b = _bundle(tmp_path, files=["plan.md", "new.md"],
                index="# b\n\n- [plan.md](plan.md)\n")
    okf.reindex_write(b)
    out = (b / "index.md").read_text()
    assert "- [new.md](new.md)\n" in out
    assert "pending" not in out and "TODO" not in out


def test_reindex_write_is_idempotent(tmp_path):
    b = _bundle(tmp_path, files=["plan.md", "extra.md"],
                index="# b\n\n- [plan.md](plan.md)\n- [dead.md](dead.md)\n")
    okf.reindex_write(b)
    first = (b / "index.md").read_text()
    second_res = okf.reindex_write(b)
    assert (b / "index.md").read_text() == first
    assert second_res["changed"] is False
    assert okf.reindex_check(b)["verdict"] == "clean"


def test_reindex_write_dry_run_does_not_write(tmp_path):
    b = _bundle(tmp_path, files=["plan.md", "extra.md"],
                index="# b\n\n- [plan.md](plan.md)\n")
    before = (b / "index.md").read_text()
    res = okf.reindex_write(b, dry_run=True)
    assert (b / "index.md").read_text() == before
    assert res["changes"], "dry-run must still report what it would do"


def test_reindex_write_keeps_external_links(tmp_path):
    """An `https://` entry is not a bundle path claim and must never be a ghost."""
    b = _bundle(tmp_path, files=["plan.md"],
                index="# b\n\n- [plan.md](plan.md)\n- [upstream](https://example.com/x)\n")
    assert okf.reindex_check(b)["verdict"] == "clean"
    okf.reindex_write(b)
    assert "https://example.com/x" in (b / "index.md").read_text()


def test_discarded_prose_flags_a_dropped_line(tmp_path):
    assert okf.discarded_prose("# a\n\nkept\ndropped\n", "# a\n\nkept\n") == ["dropped"]
    assert okf.discarded_prose("# a\n\n- [x](x)\n", "# a\n") == []


def test_check_reports_index_drift_at_warning_level(tmp_path):
    """REQ-OKF-CHK-002: ghost/missing surface in `check` as WARNINGS, not errors.

    The level is pinned by a test on purpose (plan-046 D-10): warning level was
    chosen so the engine does not depend on a downstream allowlist's *silence*,
    and promotion to error must therefore be a deliberate, visible change rather
    than something a later edit can do by accident.
    """
    b = _bundle(tmp_path, files=["plan.md", "unlisted.md"],
                index="# b\n\n- [plan.md](plan.md)\n- [dead.md](dead.md)\n")
    (b / "log.md").write_text("# Log\n\n")
    res = okf.check_conformance(b)
    drift = [f for f in res.findings if f.req == "REQ-OKF-CHK-002"]
    assert drift, [f.as_dict() for f in res.findings]
    assert {f.level for f in drift} == {"warning"}, "index drift must NOT be error-level"
    assert any("ghost" in f.message for f in drift)
    assert any("missing" in f.message for f in drift)


def test_check_index_drift_does_not_fire_without_an_index(tmp_path):
    """REQ-OKF-CHK-002 keys on an index that EXISTS; a missing one is REQ-OKF-001."""
    b = _bundle(tmp_path, files=["plan.md"])
    res = okf.check_conformance(b)
    assert not [f for f in res.findings if f.req == "REQ-OKF-CHK-002"]
    assert any(f.req == "REQ-OKF-001" for f in res.findings)


def test_reindex_suppresses_parent_dir_when_children_listed(tmp_path):
    """REQ-OKF-011: a bare parent-dir entry is suppressed when its children are listed.

    Operator ruling (plan-046, Backfill Review gate). Not cosmetic: exp-003's
    finding that research ROOT indexes beat nested ones rested on the root
    enumerating individual files with rich phase-tagged descriptions. A bare
    `- [artifacts/](artifacts/)` beside a described `artifacts/critique.md`
    entry dilutes exactly that property.
    """
    b = _bundle(tmp_path, files=["Summary.md"], dirs=["artifacts"])
    (b / "artifacts" / "critique.md").write_text("---\ntype: Concept\n---\n# c\n")
    index = ("# b\n\n- [Summary.md](Summary.md) - the report\n"
             "- [artifacts/critique.md](artifacts/critique.md) - [critique] red-team\n")
    (b / "index.md").write_text(index)
    assert okf.reindex_check(b)["verdict"] == "clean", okf.reindex_check(b)
    okf.reindex_write(b)
    assert "- [artifacts/](artifacts/)" not in (b / "index.md").read_text()


def test_reindex_emits_parent_dir_when_children_not_listed(tmp_path):
    """The other half of the ruling: keep the dir entry when children are NOT listed."""
    b = _bundle(tmp_path, files=["plan.md"], dirs=["findings"])
    (b / "findings" / "exp-001.md").write_text("---\ntype: Concept\n---\n# f\n")
    (b / "index.md").write_text("# b\n\n- [plan.md](plan.md)\n")
    assert any(f["target"] == "findings/" and f["kind"] == "missing"
               for f in okf.reindex_check(b)["findings"])
    okf.reindex_write(b)
    assert "- [findings/](findings/)" in (b / "index.md").read_text()


# --- plan-053 Issue 4.3 (#207): the frontmatter DELETE path --------------------------------
#
# `write_frontmatter` was MERGE-ONLY, so there was no supported way to un-set a key. An
# operator whose plan recorded a burned epic could only hand-edit `plan.md`, which reliably
# updates ONE of the two dual-written surfaces and leaves the other.
#
# R1 budgets these cases because `okf.py` has FOUR declared consumers — yf-plan (this plan's
# own subject), yf-research, yf-incubator and yf-okf — so a regression here breaks three
# skills this plan otherwise never touches.


def test_write_frontmatter_deletes_named_keys(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("---\ntype: Plan\nid: p1\nepic: yf-e\nauthor: t\n---\n# body\n")
    okf.write_frontmatter(p, {}, delete=["epic"])
    fm, body = okf.read_frontmatter(p)
    assert "epic" not in fm
    # Everything else keeps its value AND its position.
    assert list(fm) == ["type", "id", "author"]
    assert body.strip() == "# body"


def test_write_frontmatter_delete_is_idempotent_and_absent_is_a_noop(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("---\ntype: Plan\nepic: yf-e\n---\n# body\n")
    okf.write_frontmatter(p, {}, delete=["epic"])
    first = p.read_text()
    # A key named in `delete` that is not present is a NO-OP, not an error — that is what
    # makes `clear-epic` (REQ-CLI-027) idempotent.
    okf.write_frontmatter(p, {}, delete=["epic", "never-existed"])
    assert p.read_text() == first


def test_write_frontmatter_delete_and_update_compose(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("---\ntype: Plan\nepic: yf-e\nstatus: executing\n---\n# body\n")
    okf.write_frontmatter(p, {"status": "abandoned"}, delete=["epic"])
    fm, _ = okf.read_frontmatter(p)
    assert fm["status"] == "abandoned" and "epic" not in fm


def test_delete_is_a_SEPARATE_ARGUMENT_so_None_stays_a_legitimate_VALUE(tmp_path):
    """`None` must mean "set this key to null", never "remove this key".

    Overloading a sentinel value would make the two indistinguishable — the same
    two-facts-one-signal conflation as `doc_lint`'s `not-selected` vs `no-such-path` (#181)
    and `resume-scan`'s `found` (#207). This is the assertion that keeps them apart.
    """
    p = tmp_path / "x.md"
    p.write_text("---\ntype: Plan\nepic: yf-e\n---\n# body\n")
    okf.write_frontmatter(p, {"epic": None})
    fm, _ = okf.read_frontmatter(p)
    assert "epic" in fm and fm["epic"] is None


def test_write_frontmatter_delete_honours_dry_run(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("---\ntype: Plan\nepic: yf-e\n---\n# body\n")
    before = p.read_text()
    text = okf.write_frontmatter(p, {}, delete=["epic"], dry_run=True)
    assert "epic" not in text and p.read_text() == before


# --- plan-056: REQ-OKF-011 amended exit contract ----------------------------

def test_reindex_no_such_path_differs_from_no_index(tmp_path):
    """REQ-OKF-011 (plan-056 Issue 1.1): a MISTYPED path is not an index-less bundle.

    Both states used to reach the same `if not idx.exists()` line, so any driver that
    tolerates `no-index` — as a corpus sweep over a mixed corpus must — read a typo as a
    benign skip and certified a corpus it never inspected.
    """
    real = _bundle(tmp_path, "b")                      # exists, carries no index.md
    missing = tmp_path / "definitely-not-here"

    r_missing = okf.reindex_check(missing)
    r_noindex = okf.reindex_check(real)

    assert r_missing["verdict"] == "no-such-path" and r_missing["exit"] == 3
    assert r_noindex["verdict"] == "no-index" and r_noindex["exit"] == 2
    # THE PAIR, not either alone: a check asserting only "non-zero" is satisfied by the
    # engine being absent.
    assert r_missing["exit"] != r_noindex["exit"]


def test_marker_imbalance_check_mode(tmp_path):
    """SC4 / REQ-OKF-011: `--check` no longer reports a marker-imbalanced index as clean.

    Until plan-056 `reindex_check` never called `check_markers` at all, so the one
    condition REQ-OKF-072 calls *unrecoverable* returned `clean`, exit 0 — the only path
    by which a green `--check` precedes the `--write` that would discard prose.

    INCONCLUSIVE rather than `drift`: with the generated-region boundary undefined the
    drift question cannot be answered in either direction.
    """
    b = _bundle(tmp_path, "b", files=["x.md"],
                index="# b\n\n<!-- intro:start -->\n- [x.md](x.md)\n")
    r = okf.reindex_check(b)
    assert r["verdict"] == "inconclusive" and r["exit"] == 4
    assert any(f["kind"] == "marker-imbalance" for f in r["findings"])

    # The BALANCED control — same bundle, markers closed — is clean. Without this arm the
    # test passes on an engine that returns `inconclusive` unconditionally.
    (b / "index.md").write_text("# b\n\n<!-- intro:start -->\n<!-- intro:end -->\n- [x.md](x.md)\n")
    ok = okf.reindex_check(b)
    assert ok["verdict"] == "clean" and ok["exit"] == 0


# --- plan-056: REQ-OKF-CHK-003 path exclusion -------------------------------

def _ext_with_3b(tmp_path, globs) -> Path:
    """A synthetic skills/<skill>/OKF-EXTENSION.md carrying a §3b table."""
    skill = tmp_path / "skills" / "yf-synthetic"
    skill.mkdir(parents=True)
    rows = "\n".join(f"| `{g}` | because |" for g in globs)
    (skill / "OKF-EXTENSION.md").write_text(
        "# OKF-SYNTHETIC\n\n"
        "## 0. Member identity\n\n| Key | Value |\n|:--|:--|\n| `okf_spec` | `OKF-SYNTHETIC` |\n\n"
        "## 3. Reserved subdirs / files\n\n| Reserved path | Holds |\n|:--|:--|\n"
        "| `findings/` | Finding docs |\n\n"
        "## 3b. Excluded paths\n\n| Excluded glob | Why |\n|:--|:--|\n" + rows + "\n")
    return skill


def test_exclude_globs_declared(tmp_path, monkeypatch):
    """SC7 / REQ-OKF-CHK-003: the exclusion is MEMBER-DECLARED and non-empty.

    Two arms, and the second is the point: REMOVING §3b restores the findings. An
    exclusion nothing can turn off is indistinguishable from a check that never fired.
    """
    skill = _ext_with_3b(tmp_path, ["fixtures/**"])
    monkeypatch.setattr(okf, "_self_location",
                        lambda: {"mode": "canonical", "skill": None,
                                 "skills_root": tmp_path / "skills"})

    rs = okf.resolve_extension("yf-synthetic")
    assert rs.found and rs.exclude_globs == ["fixtures/**"]

    # RECURSIVE, which `_glob_match` (PurePosixPath.match) cannot express — the reason the
    # matcher is `fnmatch`. Without this the exclusion would cover one level and silently
    # inspect the rest.
    assert okf.is_excluded("fixtures/a.md", rs.exclude_globs)
    assert okf.is_excluded("fixtures/deep/deeper/a.md", rs.exclude_globs)
    assert not okf.is_excluded("findings/a.md", rs.exclude_globs)

    # ARM 2 — §3b removed: the concept is gone and nothing is excluded.
    (skill / "OKF-EXTENSION.md").write_text(
        (skill / "OKF-EXTENSION.md").read_text().split("## 3b.")[0])
    okf.resolve_extension.cache_clear() if hasattr(okf.resolve_extension, "cache_clear") else None
    rs2 = okf.resolve_extension("yf-synthetic")
    assert rs2.exclude_globs == []
    assert not okf.is_excluded("fixtures/a.md", rs2.exclude_globs)


def test_overlap_invariant(tmp_path):
    """SC8 / D-14: the two exclusion lists agree, AND NEITHER IS EMPTY.

    The non-vacuity half is what makes this an invariant rather than a tautology: with
    either list empty the agreement holds trivially — and empty is exactly the state the
    concept was introduced from, so a test without this half would ship green and stay
    green through its own regression.
    """
    import tomllib

    repo = Path(__file__).resolve().parent.parent
    member = okf.resolve_extension("yf-plan").exclude_globs
    schema = tomllib.loads((repo / "_shared" / "document_types" / "finding.toml").read_text())
    lint_side = schema.get("exclude", [])

    # NON-VACUITY, both sides.
    assert len(member) >= 2, f"OKF-PLAN §3b must declare >= 2 globs, got {member}"
    assert len(lint_side) >= 2, f"finding.toml exclude must declare >= 2 globs, got {lint_side}"

    # The declared relationship. The two are INDEPENDENTLY DECLARED in different coordinate
    # systems — `doc_lint`'s are REPO-relative and per-schema, §3b's are BUNDLE-relative and
    # per-member — so this is a containment claim about the fixture corpora both must cover,
    # not a set equality. Set equality would be false by construction and would push an
    # author toward deriving one from the other, which D-14 measured as wrong:
    # `assets/fixtures/**` is absent from doc_lint's list because doc_lint is silent there
    # by NON-SELECTION, which is a different fact from exclusion.
    assert "findings/okf-migration-samples/**" in member
    assert any("okf-migration-samples" in g for g in lint_side)
    assert any("assets/fixtures" in g or "fixtures" in g for g in member)
