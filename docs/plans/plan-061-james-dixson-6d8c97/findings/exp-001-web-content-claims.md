---
type: Finding
okf_spec: OKF-PLAN
description: 'Complete enumeration of false, stale and missing claims across web/content — including the measured finding that the Pelican site does not build at all, because skill_pages.py is fail-closed on the missing yf-okf-hygiene page. Deferred to issue 317; retained here as its evidence base.'
---
# EXP-001 — Complete enumeration of false/stale/missing website claims

**Question.** What is every false, stale, or missing claim in `web/content/**` relative to what
the repo ships?

## HEADLINE: the site does not build at all

**This supersedes the "missing page" framing.** `web/plugins/skill_pages.py:296-306` is
**fail-closed**: it enumerates skills from frontmatter and raises if any lacks an authored page.

Reproduced directly in this session:

```
$ .venv/bin/pelican content -s pelicanconf.py -o /tmp/pelout
CRITICAL RuntimeError: skill_pages: no authored web/content/skills/<name>.md for:
yf-okf-hygiene. Every skill needs an authored page (add one under web/content/skills/).
```

So `yf-okf-hygiene` is not a gap in a published site — **it halts the build.** Every other
content repair is moot until that page exists. This also **corrects** the drafting session's
earlier claim that the generated index "already renders 20 beside prose saying 19": nothing
renders. The inconsistency is real in the *sources*, not in any published output.

## Findings table

| file:line | claim | reality | evidence | severity |
| :-- | :-- | :-- | :-- | :-- |
| `architecture.md:59-67` | "19 skills" / "utility (7)" | 20 / utility 8 | `grep -h '^skill-group:' skills/*/SKILL.md \| sort \| uniq -c` | false |
| `install.md:189-193`, `architecture.md:45-49` | opencode → `~/.config/opencode/skills`; pi → `~/.pi/agent/skills` | `.agents/skills`, **both scopes** | `harness_desc.rs:232-233`, `:251-252` | false |
| `install.md:192` | pi applies `lowercase-hyphen,max64` | `name_transform: None` on all 5 rows; **a test asserts it** | `harness_desc.rs:255`, `:381-382` ("no shipped row may carry a name_transform (plan-055 Issue 2.3)") | false |
| `web/content/skills/yf-plan.md:96-102` | command table omits autonomy flags | `--checkpoint`/`--autonomous`/`--sweep-gates` ship | `SKILL.md:141` | false |
| site-wide | no mention of `land`, lander, retrospectives, escalation | all real verbs | `plan_manager.py`: `land:8200`, `retrospective-report:6875`, `retrospective-append:7023`, `escalation-raise:6947`, `-resolve:6996`, `-report:7283`, `-push:7308`, `judgement-never-fired-report:6426` | missing |
| **`web/` build** | site presumed buildable | **build aborts** | reproduced above; `skill_pages.py:296-306` | **false — build break** |
| `architecture.md:98`, `glossary.md:151`, `beads-concepts.md:131` | beads push upstream to "GitHub, GitLab, or Jira" | **GitHub is the only backend**; GitLab/Jira removed at plan-040 | `yf-beads-upstream/SKILL.md:43,177` (REQ-BUP-040) | false ×3 copies |
| `harness-tune.md:156` | an `aggregate` rule removal is unconditional | conditional on a touched-since-tune sha256 guard since #154 (REQ-YF-TUNE-029) | `yf/src/cmd/harness/revert.rs:456-494` | stale — and **contradicts `install.md:100-104` on the same site** |
| `web/content/skills/yf-okf.md:11,54` | `/yf-okf` supports `assess <corpus>` | `assess` **removed** at plan-057 Issue 3.4; now `yf-okf-hygiene audit` (with `assess` as alias) | `yf-okf/SKILL.md:238`; `okf.py` parsers list only check/migrate/reindex/scaffold; `okf_hygiene.py:724-726` | false |
| `yf-skill-authoring.md:109` | lint subset is 6 rules (`ML001..ML008`) | 7 rules — includes `ML010` | `yf-markdown-lint/SKILL.md:201`; `test_markdown_lint.py:134,195` | stale — **inherited from the skill's own `SKILL.md:300`**, not a web-only defect |
| `yf-beads-upstream.md` | documents init/push/hoist/land/unhoist/status/pull | omits the real `closable` verb | `upstream.py:1745`, parser `:1948`; `SKILL.md:596-622` §9 | missing |
| `yf-beads-extra.md:8` | "verified against bd 1.0.5, re-certified 1.1.0" | installed `bd` is **1.2.2** | `bd version` | stale (self-flagged currency gap) |
| `images/architecture.d2:18` | "embedded skills (18)" | 20 | `ls -d skills/*/` | false — **a third count, disagreeing with architecture.md's own wrong 19** |
| `images/architecture.d2:20` | "beads group (8)" folding in plan/research/incubator | beads is 5; workflows is a separate group of 3 | same grep; `architecture.md:61-64` | false |
| `images/architecture.d2:21` | "utility group (6)" | 8 (omits `yf-okf-hygiene`, `yf-change-validation`, `yf-herdr`) | same grep | false |
| `images/install-matrix.d2:15,16,25,26` | opencode/pi private roots + pi transform | `.agents/skills` both scopes, no transform | `harness_desc.rs:222-255` | false — **a 4th site of the same regression** |
| `images/formulas.d2:145-153` | "the three shipped standard formulas" | **five** ship (adds `plan-review`, `verify-artifact`) | `find skills -name '*.formula.toml'` → 5; `formulas.md:11-12` already says five | stale — **page fixed, diagram not** |

## Verified CORRECT (no drift)

`images/tune-matrix.d2`, `lifecycle.d2`, `phase-model.d2`; `cards/*.md`; `home/hero.md`;
**13 of 19** skill pages; `why.md`'s generated-catalog claim.

## UNVERIFIABLE (no in-repo source of truth)

- `why.md:~1141-1159` competitor comparison (Spec Kit, Kiro, BMAD, Taskmaster) — third-party.
- `yf-beads-extra.md`'s bd-version currency claim — no artifact records the installed version.

## Why DRIFT-CHECK could not have caught much of this even if re-run

This is the most important section for workstreams (c)/(d).

1. **`e-web-cli-surface`'s source node excludes `harness_desc.rs`** — it is scoped to `cli.rs` +
   `profiles/*.json` only. The harness-path and name-transform defects are **invisible to the one
   edge that looks like it owns them.**
2. **No node or edge covers the upstream-backend claim at all** — 3 false copies, zero coverage.
3. **`web/content/images/**`, `cards/**`, `home/**` have NO §6 Trigger Scope row.** This is why
   facts drifted independently in `.d2` sources. `formulas.d2` vs `formulas.md` is a **clean A/B
   proof**: the `.md` was fixed, the `.d2` was not, because only the `.md` is in scope.
4. **`web/content/**`'s blanket row fans out to `e-status-values` only** — a narrow status-vocab
   check. `lifecycle.md`, `workflows.md`, `usage.md`, `glossary.md`, `managed-files.md`,
   `beads-concepts.md`, `why.md` have **no content-accuracy coverage**.
5. **`e-skill-page-desc` exists and still missed** the `yf-okf` `assess` and yf-plan
   land/escalation omissions — a live *enforcement* gap, not merely a manifest gap.

## Implications for the plan

- **Build break is P0.** Sequence `yf-okf-hygiene.md` first; nothing else is verifiable until the
  build runs.
- **Repairs are multi-site.** Harness paths = 4 sites + 2 PNG re-renders. Skill counts = 3
  mutually-inconsistent sites. A prose-only fix leaves diagrams wrong.
- **Two new false-claim families** not in the original scope: the GitLab/Jira backend claim (×3)
  and `yf-okf`'s stale `assess`.
- **Manifest widening is required, not optional**: add §6 rows for `images/**`, `cards/**`,
  `home/**`; widen `e-web-cli-surface`'s source node to include `harness_desc.rs`. Without both,
  every repair above is a one-time patch that silently re-drifts.
