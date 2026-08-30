---
type: Finding
okf_spec: OKF-PLAN
description: 'Classification of all 52 DRIFT-CHECK.md edges into mechanical (35), prose (9) and hybrid (8), the CHANGE-VALIDATION recipe seam, and the measured structural blind spot where optional and required node reachability both enforce nothing.'
---
# EXP-002 — Which DRIFT-CHECK edges are mechanical, and where the checker binds

**Question.** Which of the 52 edges can a script decide with a trustworthy exit code, and where
does such a checker plug into `CHANGE-VALIDATION.md`?

## Classification — 52 edges

| Bucket | Count | Notes |
| :-- | --: | :-- |
| **MECHANICAL** | **35** (67%) | includes all **13** vendored-copy edges |
| **PROSE** | 9 | `e-spec-compliance`, `e-protocol-rule`, `e-spec-guardrails`, `e-spec-readme`, `e-guardrails-readme`, `e-skillspec-skillmd`, and the three `e-skill-page-*` |
| **HYBRID** | 8 | mechanical precondition + prose core |

**13 of the 35 mechanical edges are already wired.** `_shared/sync.py` defines the same
canonical/consumer pairs the manifest declares, and `_shared/sync.py --check` is already a
`CHANGE-VALIDATION` row (`uv-_shared`). That is existing coverage, not new work.

`e-spec-agent` is mechanical despite appearances — it is a **verbatim-quote** match, not semantic.

**Hybrid seams** (where the split falls): `e-json-contract` (emitted keys vs. narrative claim);
`e-readme-desc` / `e-index-desc` (string extraction vs. "matches *intent*", which tolerates
paraphrase); `e-web-cli-surface` (flag exists vs. presented "as if canonical");
`e-changelog-version`; `e-doclint-spec`; and the two `*-diagram-fresh` edges — where
**`DRIFT-CHECK.md:195` already declares the split itself**: `render.py check-dir` is
*authoritative* on a missing render, *advisory* (mtime) on staleness.

## Does a mechanical checker contradict `CHANGE-VALIDATION.md:6`?

Verbatim (lines 6-7):

> Executable-only: `yf-drift-check` is excluded (prose/LLM trigger, not a runnable command).

**No contradiction as literally written.** The exclusion names the *skill* — the sub-agent
dispatching engine — which genuinely has no single runnable command. A purpose-built
`scripts/checks/*.py` that verifies facts the manifest also declares is not "running
yf-drift-check".

**But it becomes misleading by omission** the moment such a checker exists: a reader infers that
*none* of the manifest's edges are ever mechanically gated, which would then be false. The line
needs an **appended** clarification (not a replacement) stating that the mechanical subset is
covered by dedicated rows, and only PROSE/HYBRID edges remain yf-drift-check's exclusive
on-edit territory.

## `CHANGE-VALIDATION.md` recipe schema

Rows are `| id | cmd | cwd | timeout |`. Real row:

```
| `okf-index-drift` | `uv run scripts/checks/check_okf_index_drift.py --min-roots 30` |  |  |
```

`id` is the stable name §3 trigger globs reference; `cmd` runs at repo root unless `cwd` is set
(every observed row leaves `cwd`/`timeout` blank). **FAST** = ids selected by globs matching the
changed path-set. **FULL** = the CI ∪ repo-checks superset, unfiltered, once per land.

House exit convention confirmed uniform across both the Python (PEP 723) and bash (`_common.sh`)
styles: **0 / 1 / 2** = pass / fail / inconclusive.

## Reusing `skill_pages.py` — safe, with one trap

Reusing `_read_skills()` / `_authored_page_path()` as a **ground-truth extractor** is
non-circular: it parses frontmatter, not the checked artifact. Comparing frontmatter-derived
groups against `GROUP_ORDER`/`GROUP_LABELS`/`GROUP_BLURBS` is exactly the point of
`e-web-skill-groups`.

**The circularity trap to avoid:** using `GROUP_ORDER` to *enumerate which groups exist*, rather
than deriving that from frontmatter. That would make the registry validate itself.

## The structural blind spot — CONFIRMED LIVE

- **`optional` is a vocabulary token only** (`DRIFT-CHECK.md:27`). No check anywhere verifies
  that a required *or* optional node's expected instance exists. §4 checks that
  *already-present* optional nodes are referenced. §1 asserts "every `skills/*/` dir must contain
  one" for `skill-md`/`skill-readme` — **and no script enforces it.**
- **`required` does not imply presence-checking either.** It only means reference-validity checks
  apply *if* the artifact is present. So `skill-readme` — a **required** node — is equally
  unenforced: `yf-okf-hygiene` has no `README.md` and nothing fails.
- **12 optional nodes** exist. Only `skill-page` has the hole in a load-bearing way: the others
  (agents, diagrams, formulas, templates) are legitimately absent for most skills, whereas a web
  page is supposed to exist for **every** skill — as `skill_pages.py`'s own fail-closed guard
  asserts at build time.
- All three `e-skill-page-*` edges share the `*` pairing and are **all** silent for
  `yf-okf-hygiene`.

**Minimal correct fix — two parts, and the second is the real one:**

(a) flip `skill-page` (`DRIFT-CHECK.md:75`) optional → required, matching what the build already
enforces; **(b) add a dedicated existence/completeness check**, because `*`-glob pairing
*structurally cannot* detect "zero instances on one side". That is the defect — not the contract
type. Flipping alone would not fix it.

**Breakage from flipping: exactly one skill**, `yf-okf-hygiene` — which is independently owed a
page because the build is already broken.

## Recommended design

| Script | Covers | Notes |
| :-- | :-- | :-- |
| `scripts/checks/check_skill_artifact_completeness.py` | `README.md` + `web/content/skills/<name>.md` exist per skill | mirrors `check_okf_index_drift.py` conventions; `--min-skills N` floor **against a vacuous pass** |
| `scripts/checks/check_web_skill_facts.py` | `e-web-skill-counts`, `e-web-skill-groups` | frontmatter ground truth; numeral-or-word normalized count parsing |

The `--min-skills` floor matters: a checker that enumerates zero skills and passes is the same
vacuous-check class this plan exists to close.

**Bindings:** two new FAST+FULL rows; §3 globs `skills/*/SKILL.md`, `skills/*/README.md`,
`web/content/skills/*.md` → completeness; `skills/*/SKILL.md`,
`web/content/pages/architecture.md`, `web/plugins/skill_pages.py` → web facts.

**Do not** attempt mechanical coverage of the 9 PROSE edges, nor a general dispatcher for the 8
HYBRID edges beyond their mechanical half — that would manufacture false confidence.

## Open / INCONCLUSIVE

Whether `render.py check-dir` (the existing authoritative half of the diagram-freshness edges) is
already wired into a `CHANGE-VALIDATION` row was **not checked**. Worth a grep before designing
around it.
