# plan-052 — pre-fix baselines

Every figure below is recorded **with the verbatim pathspec or command that produced it**.
That is the whole point of this file: plan-051 shipped `SC4b` green at discharge and false two
epics later, and this plan's own prose carried three hand-counts that were wrong. A figure
without its pathspec cannot be re-measured, so it is only as true as the last time a human
read it.

`ctl-baseline-pathspec` asserts mechanically that every row here carries a non-empty
`Pathspec / command` cell. It does **not** re-run the commands — re-running is
`recheck-criteria`'s job, and a baseline is by definition a *pre-fix* observation that a
post-fix tree is expected to contradict.

Measured on `plan-052-james-dixson-fa8056-execute` at base `main` (`c4bd3dd`), 2026-08-24.

## B1 — the corpus of Success Criteria

| # | Figure | Value | Pathspec / command |
| :-- | :-- | --: | :-- |
| B1.1 | plan bundles under the vault-default root | 52 | `ls -d docs/plans/plan-*/ \| wc -l` |
| B1.2 | bundles carrying a `## Success Criteria` section | 52 | `grep -l '^## Success Criteria' docs/plans/plan-*/plan.md \| wc -l` |
| B1.3 | bundles carrying the four-column `Verification \| Discharged-by` header | 6 | `for f in docs/plans/plan-*/plan.md; do awk '/^## Success Criteria/{f=1;next} /^## /{f=0} f && /^\| *# *\| *Criterion *\| *Verification *\| *Discharged-by/{n=1} END{exit(n?0:1)}' "$f"; done` (count of exit-0) |
| B1.4 | criteria rows, all bundles | 222 | `cat docs/plans/plan-*/plan.md \| awk '/^## Success Criteria/{f=1;next} /^## /{f=0} f && /^\| *SC/{c++} END{print c+0}'` |
| B1.5 | criteria rows, **excluding** plan-052 | 186 | `ls docs/plans/plan-*/plan.md \| grep -v plan-052 \| xargs cat \| awk '/^## Success Criteria/{f=1;next} /^## /{f=0} f && /^\| *SC/{c++} END{print c+0}'` |
| B1.6 | criteria rows in the **clause grammar**, excluding plan-052 | **0** | same as B1.5 with the additional guard `&& (/→ exit /\|\|/\| *manual:/)` |
| B1.7 | bundles with **>= 1** clause-form criterion | 1 (plan-052 only) | `for f in docs/plans/plan-*/plan.md; do awk '/^## Success Criteria/{f=1;next} /^## /{f=0} f && /^\| *SC/ && (/→ exit /\|\|/\| *manual:/){n=1} END{exit(n?0:1)}' \"$f\" && echo \"$f\"; done` |

B1.6 is the headline: **0 of 186**. The plan's prose said "0 of 155" — directionally right,
numerically stale. B1.3 corrects the plan's "5 of 53".

## B2 — `gen_handoff.py`'s retrospective miscount (the defect Issue 0.4 fixes)

| # | Figure | Value | Pathspec / command |
| :-- | :-- | --: | :-- |
| B2.1 | the extractor's regex | `^###\s+(RE-\d+)` | `sed -n '178p' docs/plans/plan-051-james-dixson-2f499f/scripts/gen_handoff.py` |
| B2.2 | plan-051 retrospective entries written `## RE-` | 6 | `grep -c '^## RE-' docs/plans/plan-051-james-dixson-2f499f/plan-retrospective.md` |
| B2.3 | plan-051 retrospective entries written `### RE-` | 0 | `grep -c '^### RE-' docs/plans/plan-051-james-dixson-2f499f/plan-retrospective.md` |
| B2.4 | entries the handoff therefore **reports** | 0 | `python3 -c \"import re,pathlib;print(len(re.findall(r'^###\s+(RE-\d+)',pathlib.Path('docs/plans/plan-051-james-dixson-2f499f/plan-retrospective.md').read_text(),re.M)))\"` |

Three hashes against two. The generated handoff reports **0 entries where 6 exist**, and its
`--check` verb reports OK because it regenerates the same wrong number and diffs it against
itself. plan-051's `SC14` is green on false content.

## B3 — `closable`'s interface (the gap Issue 3.2 closes)

| # | Figure | Value | Pathspec / command |
| :-- | :-- | :-- | :-- |
| B3.1 | `closable`'s full option set | `[-h] [--json]` | `uv run skills/yf-beads-upstream/scripts/upstream.py closable --help` |
| B3.2 | `--fixture` present? | **no** | `uv run skills/yf-beads-upstream/scripts/upstream.py closable --help \| grep -c -- --fixture` |

Every control over this verb written before 3.2 would therefore run against **live `bd` state**,
which is not a control at all. This is why `ctl-205-*`'s RED must be a real negative against a
pinned fixture rather than an argparse exit 2 from the absent flag.

## B4 — this plan's own shape (all DERIVED, never hand-counted)

| # | Figure | Value | Pathspec / command |
| :-- | :-- | --: | :-- |
| B4.1 | epics | 8 | `uv run skills/yf-plan/scripts/plan_extract.py docs/plans/plan-052-james-dixson-fa8056 --json --strict` → `.[0].epics \| length` |
| B4.2 | issues | 31 | same → `.[0].issues \| length` |
| B4.3 | dependency edges | 49 | same → `.[0].edges \| length` |
| B4.4 | gates | 5 | same → `.[0].gates \| length` |
| B4.5 | `unparsed[]` | empty | same → `.[0].unparsed` |
| B4.6 | controls in the generated set | 29 | `uv run docs/plans/plan-052-james-dixson-fa8056/assets/gen-controls.py` |
| B4.7 | controls by set | 21 core / 4 ext / 4 land / 0 orphan | `cut -f2 docs/plans/plan-052-james-dixson-fa8056/assets/controls.txt \| sort \| uniq -c` |

B4.6 is **29**, not the 27 or 28 the plan's prose reached by hand in two separate places. SC0
exists precisely because those hand-counts were wrong; the generated figure is the one that
governs, and nothing in the harness carries a literal count.

## B5 — the harness's own pre-fix state

| # | Figure | Value | Pathspec / command |
| :-- | :-- | --: | :-- |
| B5.1 | `verify-partition` over an EMPTY set, **before** the floor | exit 0, `PASS: core(0) u ext(0) u land(0) == all(0)` | `CTL_TXT=<empty> bash …/gate-run.sh verify-partition` against the pre-floor dispatcher |
| B5.2 | `verify-set core` over an EMPTY set, **before** the floor | exit 0, `PASS: 0 control(s)` | `CTL_TXT=<empty> bash …/gate-run.sh verify-set core` against the pre-floor dispatcher |
| B5.3 | controls asserted but not built, at the end of Issue 0.2 | 27 of 29 | `bash …/gate-run.sh run ctl-harness-contract` |

B5.1/B5.2 are the pass-3 spike reproduced exactly: three flagship criteria green while
**nothing was checked**.
