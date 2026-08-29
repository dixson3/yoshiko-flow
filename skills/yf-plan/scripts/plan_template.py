"""Canonical `plan.md` skeleton — the single source both the seeder and the docs read.

**Why this file exists.** EXP-001 measured `yf-plan/SKILL.md`'s plan.md-structure block as the
single most-drifted artifact in plan-047's investigation: it taught the retired
`**Phase log:**` block (contradicting REQ-DATA-012 and 18 of the last 18 plans), omitted the
required frontmatter, and carried authoring annotations that appear **0 times** in 47 plans.
The template a human reads and the template the code writes were two hand-maintained copies of
the same thing, and only one of them was ever executed.

So the skeleton lives here, once, and has exactly two consumers:

1. `plan_manager.py:seed_plan_md` formats `PLAN_MD_SKELETON` to create a new `plan.md`;
2. `_shared/sync.py` emits `skeleton_doc()` into `SKILL.md`'s marker-fenced region.

`sync.py --check` fails if either consumer is edited alone, which is what makes the drift
structurally impossible rather than merely discouraged (plan-047 D-7 amended, Issue 0.2).

**Scope bound — the fence covers STRUCTURE, not the grammar.** Only the heading set, the
required fields and the section order are generated. The illustrative epic/gate grammar stays
**outside** the fence in its own `SKILL.md` block: byte-equality with the seeder would delete
that grammar from the one place authors read it, and it is the grammar the extractor, the
schema and the pour all derive from. That was red-team pass 1 (H5) on plan-047.

Zero dependencies, by contract: `sync.py` declares `dependencies = []` and imports this module
directly, so nothing here may import `click`, `yaml`, or `plan_manager`.
"""

from __future__ import annotations

# Ordered `## ` headings every conformant plan.md carries (REQ-DATA-011).
PLAN_SECTIONS = [
    "Objective",
    "Motivation",
    "Upstream Issues",
    "Investigation Findings",
    "Approach",
    "Epics",
    "Gates",
    "Risks & Mitigations",
    "Success Criteria",
]

# Identity fields, dual-represented as frontmatter keys and `**Field:**` lines
# (REQ-DATA-010/015). Always-required subset — `epic`/`fingerprint`/`deliverable_class`
# are added later in the lifecycle.
PLAN_IDENTITY_FIELDS = ["ID", "Author", "Created", "Status"]

# --- producer constants hoisted from plan_manager.py (plan-048 Issue 2.1) -------------
#
# `doc_lint`'s `derive_from` resolves `<module>.<ATTR>` only for modules under `_shared/`,
# so a producer constant living in `skills/yf-plan/scripts/plan_manager.py` is unreachable
# to a schema. Hoisting it here is what lets the `context` document type be DERIVED from
# the producer rather than hand-restated — a hand-restated copy is a second source of
# truth that drifts silently (REQ-DATA-024's whole rationale).
#
# `plan_manager.py` imports these back, so there is exactly one definition.

#: Sections `seed_context_md` writes and `_audit_plan` requires in a bundle's `context.md`.
CONTEXT_REQUIRED_SECTIONS = [
    "Project environment",
    "Tool inventory",
    "Paths",
    "Operator identity",
    "Runtime assumptions",
]

#: The heading `retrospective-append` writes into a bundle's `plan-retrospective.md`.
#: Hoisted for the same reason as the context sections: a `code-generated` type must
#: DERIVE its sections from the producer, never restate them.
RETROSPECTIVE_SECTIONS = ["Plan retrospective"]

#: Sections `escalation-raise` writes into `escalations.md` (plan-059 Issue 2.2, REQ-PORT-053).
#: The producer is CODE, so the type is `code-generated` and MUST declare a `derive_from`
#: (doc_lint refuses a code-generated type without one). The document's only H1 is
#: `# Escalations`, and `doc_lint.sections()` never returns an H1 — so this constant is the
#: producer record, NOT a heading list any check consumes. A `headings-*` check against it
#: would report the title missing on every file, forever, which is the exact trap
#: `plan-retrospective.toml` records having fallen into.
ESCALATION_SECTIONS = ["Escalations"]

#: Sections `_write_upstream_reference` writes into `references/upstream-<N>.md`.
#: The producer is CODE, so this type is `code-generated` and MUST derive from a producer
#: constant rather than restate one (doc_lint refuses a code-generated type with no
#: `derive_from`). `_shared/test_doc_lint.py` drives the real producer and asserts its
#: output satisfies this list, so a producer change that outgrows the list fails a test
#: instead of silently drifting.
UPSTREAM_REFERENCE_SECTIONS = ["Body"]

#: Metadata bullets the same producer writes above `## Body`.
UPSTREAM_REFERENCE_FIELDS = ["Number", "Title", "URL", "State", "Labels"]

#: Seeded instructional prose per section. A section whose body still contains its marker
#: is unedited template text. `Tool inventory` and `Paths` are auto-filled with real data
#: at seed time, so they carry no marker.
CONTEXT_PLACEHOLDERS = {
    "Project environment": "Describe the project this plan belongs to",
    "Operator identity": "fill in role, contact, and authority scope",
    "Runtime assumptions": "List the assumptions this plan makes about",
}

# Fixed column sets the schema requires (plan-047 D-6 / REQ-DATA-018).
RISKS_TABLE_HEADER = (
    "| # | Risk | Severity | Mitigation |\n"
    "| :-- | :-- | :-- | :-- |"
)
CRITERIA_TABLE_HEADER = (
    "| # | Criterion | Verification | Discharged-by |\n"
    "| :-- | :-- | :-- | :-- |"
)

# The skeleton itself. `{objective}`, `{plan_id}`, `{author}`, `{created}` and `{status}` are
# the only substitutions; everything else is literal. The frontmatter block is NOT part of this
# string — `seed_plan_md` stamps it afterwards via `_stamp_okf_type` + `_write_plan_fields`
# (REQ-OKF-020/050), and `skeleton_doc()` renders it for the docs.
PLAN_MD_SKELETON = """# Plan: {objective}

**ID:** {plan_id}
**Author:** {author}
**Created:** {created}
**Status:** {status}

## Objective
{objective}

## Motivation
_Why this plan exists: the problem, who is affected, what triggered the work.
Replace this placeholder before intake (portability contract)._

## Upstream Issues
| Issue | Title | Disposition | Notes | Resolved By |
|-------|-------|-------------|-------|-------------|

## Investigation Findings
_No investigations yet._

## Approach
_To be determined after scoping and investigation._

## Epics
_To be determined._

## Gates
### Start Gate (mandatory)
- Type: human
- Approvers: operator

## Risks & Mitigations
{risks_header}

## Success Criteria
{criteria_header}
"""


def seed_body(objective: str, plan_id: str, author: str, created: str,
              status: str = "scoping") -> str:
    """Render the skeleton as `seed_plan_md` writes it at `init`."""
    return PLAN_MD_SKELETON.format(
        objective=objective, plan_id=plan_id, author=author, created=created,
        status=status, risks_header=RISKS_TABLE_HEADER,
        criteria_header=CRITERIA_TABLE_HEADER,
    )


def skeleton_doc() -> str:
    """Render the skeleton in DOC form — placeholder identity values, plus the frontmatter
    block `seed_plan_md` stamps after writing — for `SKILL.md`'s marker-fenced region.

    The transformation from `seed_body` is purely mechanical (identity values become angle-
    bracket placeholders, and the seeded `_placeholder._` bodies become the same placeholders
    an author sees), so the two renderings cannot describe different documents.
    """
    body = PLAN_MD_SKELETON.format(
        objective="<Objective>", plan_id="plan-NNN-user-hash", author="<git-user>",
        created="YYYY-MM-DD", status="drafting",
        risks_header=RISKS_TABLE_HEADER, criteria_header=CRITERIA_TABLE_HEADER,
    )
    # Doc-form body substitutions: what an AUTHOR writes, where the seeder writes a placeholder.
    subs = [
        ("## Objective\n<Objective>\n",
         "## Objective\n<what and why>\n"),
        ("_Why this plan exists: the problem, who is affected, what triggered the work.\n"
         "Replace this placeholder before intake (portability contract)._\n",
         "<why this plan exists — the problem, who is affected, what triggered the work.\n"
         "Required by the portability contract (spec/portability.md REQ-PORT-004).\n"
         "Either this section or a motivation.md file must be present and non-empty.>\n"),
        ("## Investigation Findings\n_No investigations yet._\n",
         "## Investigation Findings\n<summary of experiments, key decisions>\n"),
        ("## Approach\n_To be determined after scoping and investigation._\n",
         "## Approach\n<chosen approach with rationale>\n"),
        ("## Epics\n_To be determined._\n",
         "## Epics\n<one `### Epic N: <name>` per epic, each with `- Issue N.M:` bullets"
         " — see the grammar below>\n"),
        ("## Gates\n### Start Gate (mandatory)\n- Type: human\n- Approvers: operator\n",
         "## Gates\n<the mandatory Start Gate, plus any capability gates and the Reconcile"
         " Gate — see the grammar below>\n"),
        (RISKS_TABLE_HEADER,
         RISKS_TABLE_HEADER + "\n| R1 | <what could go wrong> | high \\| med \\| low |"
                              " <what this plan does about it> |"),
        (CRITERIA_TABLE_HEADER,
         CRITERIA_TABLE_HEADER + "\n| SC1 | <what must be true when the plan is done> |"
                                 " <how it is checked> | <issue id(s)> |"),
    ]
    for old, new in subs:
        if old not in body:  # pragma: no cover — fail loudly rather than emit a wrong doc
            raise AssertionError(
                "plan_template.skeleton_doc: seed body no longer contains %r — the doc "
                "renderer and PLAN_MD_SKELETON have diverged" % (old[:60],)
            )
        body = body.replace(old, new, 1)
    frontmatter = (
        "---\n"
        "type: Plan\n"
        "okf_spec: OKF-PLAN\n"
        "id: plan-NNN-user-hash\n"
        "author: <git-user>\n"
        "created: YYYY-MM-DD\n"
        "status: drafting\n"
        "---\n"
    )
    return "```markdown\n" + frontmatter + body + "```\n"
