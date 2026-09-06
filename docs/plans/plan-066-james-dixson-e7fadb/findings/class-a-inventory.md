---
type: Finding
okf_spec: OKF-PLAN
description: "The Class-A defect inventory, DERIVED MECHANICALLY by running the four Epic-2 checkers over the tree. 40 findings across 10 files. This, not issue 317's table, is what Epic 4 repairs."
id: class-a-inventory
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
---
# Class-A inventory — derived by running the checkers, not by reading #317

## Approach Tested

**measured:** every row below is the verbatim output of a checker executed against this tree on
2026-09-05, after Epic 1 landed the missing skill page. Nothing here is transcribed from issue
#317; the issue is used in the *other* direction, as the negative-control set (Issue 4.2).

**Why derived rather than transcribed (D1).** #317's Class-A table is a snapshot taken before
eight plans landed, so it can only under-report — and a hand-verified repair of a stale list
would assert a coverage the plan never had. The inventory below is what the instruments see.

## Result

Total mechanically-derived findings: **40** across **10** files.

## Findings by file

### `AGENTS.md` — 2 finding(s)

- `check_web_harness_paths` — 78: `.config/opencode/skills` is not a skills subpath of ['agents', 'codex'] in either scope; declared: ['.agents/skills']
- `check_web_harness_paths` — 78: `.pi/agent/skills` is not a skills subpath of ['agents', 'codex'] in either scope; declared: ['.agents/skills']

### `README.md` — 6 finding(s)

- `check_web_harness_paths` — 105: project-scope `.opencode/skills` is not the `project_skills_subpath` of ['opencode']; declared: ['.agents/skills']
- `check_web_harness_paths` — 105: user-scope `.config/opencode/skills` is not the `user_skills_subpath` of ['opencode']; declared: ['.agents/skills']
- `check_web_harness_paths` — 106: project-scope `.pi/skills` is not the `project_skills_subpath` of ['pi']; declared: ['.agents/skills']
- `check_web_harness_paths` — 106: user-scope `.pi/agent/skills` is not the `user_skills_subpath` of ['pi']; declared: ['.agents/skills']
- `check_web_harness_paths` — 106: asserts a `lowercase-hyphen` name_transform, but 5/5 shipped harnesses declare name_transform: None (agents, claude-code, codex, opencode, pi)
- `check_web_backend_claim` — 417: offers GitLab/Jira — Configurable, GitHub-first upstream-tracking utility skill (no formula/coordinator). Binds a beads workspace t

### `web/content/images/architecture.d2` — 5 finding(s)

- `check_web_counts` — 18: claims 18 skills, census 20
- `check_web_counts` — 20: group `beads` claims 8, census 5
- `check_web_counts` — 20: group `beads` lists non-member(s) ['yf-incubator', 'yf-plan', 'yf-research'] — count may be right while membership is wrong
- `check_web_counts` — 21: group `utility` claims 6, census 8
- `check_web_backend_claim` — 36: offers GitHub/GitLab as alternatives — label: "upstream tracker\nGitHub / GitLab / Jira"

### `web/content/images/formulas.d2` — 2 finding(s)

- `check_web_counts` — 145: claims 3 shipped formulas, census 5 (plan-execute, plan-investigate, plan-review, verify-artifact, yf-research)
- `check_web_counts` — 147: claims 3 shipped formulas, census 5 (plan-execute, plan-investigate, plan-review, verify-artifact, yf-research)

### `web/content/images/install-matrix.d2` — 6 finding(s)

- `check_web_harness_paths` — 15: user-scope `.config/opencode/skills` is not the `user_skills_subpath` of ['opencode']; declared: ['.agents/skills']
- `check_web_harness_paths` — 16: user-scope `.pi/agent/skills` is not the `user_skills_subpath` of ['pi']; declared: ['.agents/skills']
- `check_web_harness_paths` — 16: asserts a `lowercase-hyphen` name_transform, but 5/5 shipped harnesses declare name_transform: None (agents, claude-code, codex, opencode, pi)
- `check_web_harness_paths` — 16: asserts a `max64` name_transform, but 5/5 shipped harnesses declare name_transform: None (agents, claude-code, codex, opencode, pi)
- `check_web_harness_paths` — 25: project-scope `.opencode/skills` is not the `project_skills_subpath` of ['opencode']; declared: ['.agents/skills']
- `check_web_harness_paths` — 26: project-scope `.pi/skills` is not the `project_skills_subpath` of ['pi']; declared: ['.agents/skills']

### `web/content/pages/architecture.md` — 8 finding(s)

- `check_web_counts` — 59: claims 19 skills, census 20
- `check_web_counts` — 65: group `utility` claims 7, census 8
- `check_web_harness_paths` — 47: project-scope `.opencode/skills` is not the `project_skills_subpath` of ['opencode']; declared: ['.agents/skills']
- `check_web_harness_paths` — 47: user-scope `.config/opencode/skills` is not the `user_skills_subpath` of ['opencode']; declared: ['.agents/skills']
- `check_web_harness_paths` — 48: project-scope `.pi/skills` is not the `project_skills_subpath` of ['pi']; declared: ['.agents/skills']
- `check_web_harness_paths` — 48: user-scope `.pi/agent/skills` is not the `user_skills_subpath` of ['pi']; declared: ['.agents/skills']
- `check_web_harness_paths` — 51: asserts a `lowercase-hyphen` name_transform, but 5/5 shipped harnesses declare name_transform: None (agents, claude-code, codex, opencode, pi)
- `check_web_backend_claim` — 98: offers GitHub/GitLab as alternatives — (GitHub, GitLab, or Jira) so work that outlives the local clone is visible to the team. This

### `web/content/pages/beads-concepts.md` — 1 finding(s)

- `check_web_backend_claim` — 131: offers GitHub/GitLab as alternatives — **captured upstream in the issue tracker** (GitHub, GitLab, or Jira) at

### `web/content/pages/glossary.md` — 1 finding(s)

- `check_web_backend_claim` — 151: offers GitHub/GitLab as alternatives — Moving a bead's tracking from the local beads database up to the issue tracker (GitHub, GitLab,

### `web/content/pages/install.md` — 8 finding(s)

- `check_web_harness_paths` — 191: project-scope `.opencode/skills` is not the `project_skills_subpath` of ['opencode']; declared: ['.agents/skills']
- `check_web_harness_paths` — 191: user-scope `.config/opencode/skills` is not the `user_skills_subpath` of ['opencode']; declared: ['.agents/skills']
- `check_web_harness_paths` — 192: project-scope `.pi/skills` is not the `project_skills_subpath` of ['pi']; declared: ['.agents/skills']
- `check_web_harness_paths` — 192: user-scope `.pi/agent/skills` is not the `user_skills_subpath` of ['pi']; declared: ['.agents/skills']
- `check_web_harness_paths` — 192: asserts a `lowercase-hyphen` name_transform, but 5/5 shipped harnesses declare name_transform: None (agents, claude-code, codex, opencode, pi)
- `check_web_harness_paths` — 192: asserts a `max64` name_transform, but 5/5 shipped harnesses declare name_transform: None (agents, claude-code, codex, opencode, pi)
- `check_web_harness_paths` — 204: asserts a `lowercase-hyphen` name_transform, but 5/5 shipped harnesses declare name_transform: None (agents, claude-code, codex, opencode, pi)
- `check_web_harness_paths` — 204: asserts a `max64` name_transform, but 5/5 shipped harnesses declare name_transform: None (agents, claude-code, codex, opencode, pi)

### `web/content/skills/yf-plan.md` — 1 finding(s)

- `check_web_backend_claim` — 90: offers GitHub or GitLab as alternatives — `/yf-plan` scans GitHub or GitLab for issues related to the objective and lets you triage each one — include,

## Not-checked declarations (REQ-CHECK-009)

- `check_web_counts` — web/content/pages/architecture.md:67: group `markdown` enumerates no member ids (count checked, MEMBERSHIP NOT CHECKED)
- `check_web_counts` — web/content/images/architecture.d2:22: group `markdown` enumerates no member ids (count checked, MEMBERSHIP NOT CHECKED)
- `check_web_harness_paths` — prose ABOUT a harness that states no path or transform literal
- `check_skill_page_contract` — whether an EXISTING page AGREES with its SKILL.md — that is e-skill-page-desc, an intent match that tolerates paraphrase and keeps its prose route (REQ-CHECK-009)
- `check_web_backend_claim` — prose that DESCRIBES multi-backend support historically without asserting it is available — an intent judgement that keeps its prose route (REQ-CHECK-009)

## Rows repaired EARLIER IN THIS PLAN — recorded, not omitted

**A repaired row must be listed, or the inventory cannot serve as a negative control.** A site
#317 names that is absent from the findings above has two possible causes, and they are opposite:
either **no checker can see it** (the instrument is blind — a defect) or **it was already fixed**
(the instrument is silent because there is nothing to say). Omitting the second makes it
indistinguishable from the first. That conflation is the exact defect class this plan exists to
close, so it is closed here too rather than only being written about.

| Site #317 names | Status | Which checker owns it | Evidence the checker is not blind |
| :-- | :-- | :-- | :-- |
| `web/content/skills/yf-okf-hygiene.md` | **REPAIRED in Epic 1** (Issue 1.1) | `check_skill_page_contract` | Its code-side control ships a new skill with NO page — the exact `75a5796` shape — and the checker was **OBSERVED TO FAIL** (`pre=0, post=1`). It is silent now because A \\ B is genuinely empty: A=20, B=20. |

This row is why `check_skill_page_contract` reports `PASS` with zero findings above while still
appearing in the inventory. Its silence is a measurement, not an absence of one.

## What the checkers found that #317 does not list

- **`README.md` and `AGENTS.md` entirely.** Eleven findings sit in the two most-read documents
  in the repository, and a `web/content/**`-scoped checker cannot reach either. This is the
  corpus widening pass-1 C4 forced; without it SC7 would have certified "all sites repaired"
  while the front door stayed wrong.
- **`README.md:417`** — a sixth upstream-backend site, exposed only by that same widening.
- **`web/content/skills/yf-plan.md:90`** — a fifth backend site, on a page #317 counts as clean.
- **`install.md:204-207`** — a whole prose bullet on the `pi` transform, beyond the table cell.
- **The `beads` group's MEMBERSHIP in `architecture.d2`**, which lists the three *workflows*
  skills. EXP-004 predicted this class was reachable only by a human read; it is caught here
  mechanically, because the checker asserts the enumerated member ids as well as the integer.

## The count, and why it differs from every earlier figure

| Source | Figure | What it was counting |
| :-- | --: | :-- |
| issue #317, rows 4-6 | ~4 | table cells it happened to name |
| EXP-001 checker B | 15 | path/identifier sites, `web/content/**` only |
| **this inventory** | **40** | every finding of four checkers over the WIDENED corpus |

The numbers are not in conflict — each counts a different set over a different corpus. 40 is the
operative figure because it is the only one produced by instruments that have been **observed to
fail** (4/4 code-side controls).

## Recommendations

Epic 4 repairs the sites above, file by file. Issue 4.9 re-runs every checker and requires exit
0; the not-checked declarations above are discharged by a human read, not by the gate.
