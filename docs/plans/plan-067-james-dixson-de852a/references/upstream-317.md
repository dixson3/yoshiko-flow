---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #317 - Plan 3/3: regenerate user-facing docs (the site
  does not currently BUILD) and separate content defects from harvest/generation-process
  defects'
---
# Upstream #317: Plan 3/3: regenerate user-facing docs (the site does not currently BUILD) and separate content defects from harvest/generation-process defects

- **Number:** 317
- **Title:** Plan 3/3: regenerate user-facing docs (the site does not currently BUILD) and separate content defects from harvest/generation-process defects
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::high

## Body

> **Plan 3 of 3.** Split from a website/docs realignment audit that proved too large for one
> plan. Siblings: #315 (README layout contract) and #316 (OKF corpus backfill). This one runs
> last — it regenerates against the contracts the other two establish.

## Objective

Regenerate all user-facing documentation, and **separate two failure classes that have been
conflated**:

- **Class A — content defects.** The docs are internally inconsistent or contradict the code.
- **Class B — process defects.** The harvest/generation pipeline cannot see, or cannot carry,
  the facts it is supposed to publish.

Class A is repaired by editing. **Class B is repaired only by changing the pipeline** — and every
Class-A fix is a one-time patch that silently re-drifts until the matching Class-B defect is
closed. Capture runtime issues and mitigations in the plan retrospective and as follow-up issues,
tagged by class.

## THE SITE DOES NOT BUILD

Reproduced directly, 2026-08-30:

```
$ .venv/bin/pelican content -s pelicanconf.py -o /tmp/pelout
CRITICAL RuntimeError: skill_pages: no authored web/content/skills/<name>.md
for: yf-okf-hygiene. Every skill needs an authored page (add one under web/content/skills/).
```

`web/plugins/skill_pages.py:296-306` is **fail-closed**: it enumerates skills from frontmatter
and raises if any lacks an authored page. So the missing `yf-okf-hygiene` page is **not a gap in
a published site — it halts the build**, and has since plan-057.

Two consequences: this is **P0** (nothing else is verifiable until the build runs), and any claim
about "what the site currently renders" is unfounded — it renders nothing.

## Class A — measured content defects

`web/content/` was last touched **2026-08-26** (plan-054, *"make the website true"*). Six plans
landed after it.

| file:line | claim | reality | evidence |
| :-- | :-- | :-- | :-- |
| `architecture.md:59-67` | "19 skills" / "utility (7)" | 20 / utility 8 | `grep -h '^skill-group:' skills/*/SKILL.md \| sort \| uniq -c` |
| `images/architecture.d2:18` | "embedded skills (18)" | 20 | **a third count, disagreeing with `architecture.md`'s own wrong 19** |
| `images/architecture.d2:20-21` | "beads group (8)", "utility group (6)" | beads 5, workflows 3 (separate groups), utility 8 | same grep |
| `install.md:189-193`, `architecture.md:45-49` | opencode → `~/.config/opencode/skills`; pi → `~/.pi/agent/skills` | `.agents/skills`, **both scopes** | `harness_desc.rs:232-233`, `:251-252` |
| `images/install-matrix.d2:15,16,25,26` | same private roots + pi transform | same | **a 4th site of the same regression** |
| `install.md:192` | pi applies `lowercase-hyphen,max64` | `name_transform: None` on all 5 rows — **a test asserts it** | `harness_desc.rs:255`, `:381-382` |
| `architecture.md:98`, `glossary.md:151`, `beads-concepts.md:131` | beads push to "GitHub, GitLab, or Jira" | **GitHub only**; GitLab/Jira removed at plan-040 | `yf-beads-upstream/SKILL.md:43,177` (REQ-BUP-040) |
| `skills/yf-okf.md:11,54` | `/yf-okf` supports `assess <corpus>` | removed at plan-057 Issue 3.4; now `yf-okf-hygiene audit` | `yf-okf/SKILL.md:238`; `okf_hygiene.py:724-726` |
| `skills/yf-plan.md:96-102` | command table omits autonomy flags | `--checkpoint`/`--autonomous`/`--sweep-gates` ship | `SKILL.md:141` |
| `skills/yf-beads-upstream.md` | documents init/push/hoist/land/unhoist/status/pull | omits the real `closable` verb | `upstream.py:1745`, `SKILL.md:596-622` |
| `harness-tune.md:156` | `aggregate` rule removal is unconditional | conditional on a touched-since-tune sha256 guard since #154 | `revert.rs:456-494` — **and contradicts `install.md:100-104` on the same site** |
| `images/formulas.d2:145-153` | "the three shipped standard formulas" | **five** ship | `formulas.md:11-12` already says five |
| `skills/yf-skill-authoring.md:109` | lint subset is 6 rules | 7, including `ML010` | inherited from `yf-skill-authoring/SKILL.md:300` — **not a web-only defect** |
| site-wide | no mention of `land`, lander, retrospectives, escalation | all real verbs | `plan_manager.py`: `land:8200`, `retrospective-append:7023`, `escalation-raise:6947`, `judgement-never-fired-report:6426` |

**Verified clean:** `tune-matrix.d2`, `lifecycle.d2`, `phase-model.d2`, `cards/*.md`,
`home/hero.md`, and **13 of 19** skill pages.

**UNVERIFIABLE** (no in-repo source of truth — flag, do not "fix"): `why.md`'s competitor table
(Spec Kit, Kiro, BMAD, Taskmaster); `yf-beads-extra.md`'s bd-version currency claim (installed
`bd` is 1.2.2 vs a stated 1.0.5/1.1.0 re-cert).

**Correction to note:** there is **no `yf-judgement` skill**. The escalation surface ships
*inside* `yf-plan`. Documenting it as a skill would manufacture a new false claim.

## Class B — process defects, the actual payload

Each of these makes a whole family of Class-A defects **structurally invisible**:

1. **`web/content/images/**`, `cards/**`, `home/**` have NO `DRIFT-CHECK.md` §6 trigger row.**
   `formulas.d2` vs `formulas.md` is the **clean A/B proof**: the page was corrected to "five
   formulas", the diagram still says three — because only the `.md` is in scope. This is why the
   harness-path defect regressed independently in 4 places.
2. **`e-web-cli-surface` cannot see the defect it appears to own.** Its source node is
   `cli.rs` + `profiles/*.json` — **excluding `harness_desc.rs`**, where the harness paths and
   `name_transform` actually live.
3. **`web/content/**`'s blanket row fans out to `e-status-values` only** — a narrow status-vocab
   check. `lifecycle.md`, `workflows.md`, `usage.md`, `glossary.md`, `managed-files.md`,
   `beads-concepts.md`, `why.md` have **no content-accuracy coverage at all**.
4. **No node or edge covers the upstream-backend claim** — 3 false copies, zero coverage.
5. **`e-skill-page-desc` exists and still missed** the `yf-okf` `assess` and yf-plan land/
   escalation omissions. A live **enforcement** gap, distinct from a manifest gap.
6. **The `optional`/`required` tokens enforce nothing.** `DRIFT-CHECK.md:75` marks `skill-page`
   `optional`, and `e-skill-page-*` pairs by a shared `*` glob — so a skill with **no** page
   yields **no edge instance**. But `skill-readme` is **`required`** and equally unenforced
   (`yf-okf-hygiene` has neither, all edges green). `*`-glob pairing structurally cannot detect
   "zero instances on one side"; flipping to `required` does **not** fix it. A dedicated
   existence check is required. (#263's vacuous-check class.)

## Scope

1. Author `web/content/skills/yf-okf-hygiene.md` — **unbreaks the build.**
2. Repair every Class-A defect **at all its sites together**, re-rendering affected PNGs. A
   prose-only fix leaves diagrams wrong.
3. Add the missing coverage: `land`/lander, retrospectives, the escalation surface (as a yf-plan
   mechanism), autonomy levels, `closable`.
4. Close the Class-B defects: §6 rows for `images/**`, `cards/**`, `home/**`; widen
   `e-web-cli-surface`'s source node to include `harness_desc.rs`; add a node/edge for the
   upstream-backend claim; add the dedicated skill-artifact existence check.
5. **Retrospective + follow-ups, tagged by class.** Every runtime issue hit during regeneration
   gets recorded with its class, so the next plan can tell "we wrote it wrong" from "the pipeline
   cannot carry this fact".

## Sequencing

Runs **after #315 and #316**. Regeneration reads the layout contract (#315) and the bundle
structure (#316); regenerating first would harvest against contracts about to change.

## Acceptance

- `pelican` builds clean.
- Every Class-A row above is repaired **at every site**, verified by a runnable check, not asserted.
- Every Class-B defect is either closed or filed with an owner — **explicitly enumerated, not
  implied by a green build.**
- The retrospective distinguishes content defects from process defects, with counts.

## Related

- **#127** — web/concepts glossary (excluded from the original scope; may fold here).
- **#104** — Pelican devserver teardown; likely to bite during regeneration.
- **#247** — drift findings no declared edge covers.
- **#263** — the vacuous-check class.
- **#273** — the command-vs-obligation law.
- **#312** — process-audit stage; the enforcement half.

