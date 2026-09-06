---
type: Finding
okf_spec: OKF-PLAN
description: "Nothing is behind the first build error, so the P0 is one file. But the guard is existence-only (an empty file passes) and piping through tail masks the pelican exit code."
id: exp-003-build-reality
plan: plan-066-james-dixson-e7fadb
created: 2026-09-05
---
# EXP-003 — What the fail-closed build is hiding, the authored-page contract, #104, and the exit-code contract

## Approach Tested

**measured:** every claim below was produced by executing a command in an isolated worktree or scratch dir and reading its real output; **inferred:** conclusions drawn from those measurements are marked where they go beyond what was directly observed.

**Question.** The build fails fail-closed on the first error, so exactly one failure is
observable. What else fails behind it? What shape must the missing page take? Does #104 bite a
batch regeneration? What command form makes a broken build unable to report green?

## Result A — there is NOTHING behind the first error

Measured in an isolated worktree: stub the one missing page and the build goes green.

```
before:  CRITICAL RuntimeError: skill_pages: no authored ... for: yf-okf-hygiene    EXIT=1
after:   Done: Processed 0 articles, ... 32 pages, 1 hidden page in 0.39 seconds     EXIT=0
```

Corroborated on three independent paths: `pelicanconf.py`, `publishconf.py`, and
`--fatal warnings` on each — all exit 0. **Pelican logs zero WARNINGs**, so "builds clean" is
achievable by adding exactly one file.

**The P0 is one file, not an unknown-size chain.** The scoping worry that motivated this
experiment is refuted.

## Result B — the guard is EXISTENCE-only, so an EMPTY FILE passes it

A zero-byte `web/content/skills/yf-okf-hygiene.md` also exits **0**, rendering a page with the
generated "At a glance" block, no body and no `<hr>`. The guard at `skill_pages.py:280-290`
calls itself fail-closed but only checks `os.path.isfile`.

**This makes "the build passes" an inadequate Success Criterion** — it is satisfiable by a file
with no content. This is the repo's recurring defect class (an instrument reporting success
without the thing having happened), reached here by writing the criterion the obvious way.

## Result C — a SECOND, non-build defect is already live

The plugin derives its own count and emits `ships **20 skills**` on the generated `/skills/`
index, while `web/content/pages/architecture.md:59` says `**19 skills**` and `:65` says
`**utility (7)**`. Real: 20 skills, utility 8.

The Pelican build **cannot** detect this — the plugin never compares its derived count to the
prose. It is a live `e-web-skill-counts` FAIL (`DRIFT-CHECK.md:189`), on a different axis from
the build, and it is in scope or the plan lands with a known drift failure.

## Result D — the authored-page contract

| Item | Answer | Citation |
| :-- | :-- | :-- |
| Path | `web/content/skills/<name>.md`, `<name>` = `SKILL.md` `name:` | `skill_pages.py:129-153` |
| **Required frontmatter** | **NONE** — a leading `---` block is stripped and discarded | `skill_pages.py:161-170` |
| Frontmatter in practice | **0 of 19** existing pages have any | measured |
| Title / subtitle | **generated** from `SKILL.md`; an authored `Title:` is ignored | `skill_pages.py:342-350` |
| "At a glance" block | **generated** — group, invocation, tools, skill deps, reverse deps, source links | `skill_pages.py:193-212` |
| Authored portion | **everything below the `<hr>`. Prose only.** | `skill_pages.py:213-217` |
| Heading level | start at `##`. Measured across 19 pages: **zero H1, zero H3** | measured |
| Markdown available | `extra` + `codehilite` **only** — a separate `Markdown()` instance, so **no `toc`, no `meta`** | `skill_pages.py:87-89` |
| Links | root-absolute (`/skills/yf-plan/`), not Pelican `{filename}` | measured |
| Group registry | `utility` already registered — **no plugin edit needed** | `skill_pages.py:63-77` |

Authored body length across the 19 existing pages: 58–122 lines, median ≈ 95. Prose content is
governed by three `field-set-subset` edges (`e-skill-page-desc`/`-readme`/`-spec`); all three
source files exist for `yf-okf-hygiene`, so sourcing the page from them makes those edges pass
by construction.

## Result E — #104 is ORTHOGONAL to this plan's build loop

Reproduced the failure exactly. After `kill` of the `pelican -lr` parent:

```
57292     1 56691 ... resource_tracker
57293     1 56691 ... spawn_main --multiprocessing-fork
57294     1 56691 ... spawn_main --multiprocessing-fork
python3.1 57294 james 12u IPv4 ... TCP 127.0.0.1:8899 (LISTEN)
```

Three children reparented to `ppid=1`, one still holding the port. None carries `pelican` in
argv, so `pkill pelican` misses them. The PGID is the **calling shell's**, which is why the
`naba#21` fix prescribes `set -m` — without it `kill -- -$PGID` would kill the operator's shell.
None of the three prescribed fixes (`IGNORE_FILES`, `set -m` + `stopserver` + `.devserver.pgid`,
gitignore) is present in this repo.

**But the one-shot build leaves nothing** — measured, empty `ps` after `pelican content`.
`pelican content` and `pelican -lr` are different exposures and **#104 bites only the devserver**.
A batch regeneration that runs `pelican content` repeatedly is unaffected.

**This qualifies D3.** #104 is real, unfixed, and worth doing — but it is *not* a
build-unblocker and shares no failure surface with the regeneration. It stays in scope as
independent work, sequenced so it cannot block the P0.

## Result F — the exit-code contract, and a zsh trap in the obvious remedy

| Form | Reported |
| :-- | --: |
| bare `pelican content …` | **1** |
| `pelican … \| tail -5; echo $?` | **0** ← the mask |
| `pelican … \| tail -5; echo ${pipestatus[@]}` | `1 0` |
| same with `${PIPESTATUS[@]}` | *(empty — bash-only, silently blank under zsh)* |
| `set -o pipefail; pelican … \| tail -3` | **1** |

Pelican's real exit on a plugin `RuntimeError` is **1**. `tail` masks it.

**The obvious fix is itself broken here.** `${PIPESTATUS[@]}` is a bash-ism that expands to
nothing under zsh — so a criterion "hardened" with it becomes a *silently empty* check: a
second, quieter instrument reporting success without doing the thing. The zsh spelling is
`${pipestatus[@]}`; the portable remedy is `set -o pipefail`; the safest is no pipe at all.

## Result G — no CI safety net exists

`CHANGE-VALIDATION.md:4` records the website build rows as **trimmed to deploy-only, not a
validation gate**, and `grep -i web .github/workflows/ci.yml` returns nothing. The site build
runs only in `web-deploy.yml`, on `workflow_dispatch` or a successful Release.

So this defect has been latent since `yf-okf-hygiene` landed, **no CI surface would ever have
caught it**, and whatever verification this plan writes *is* the only verification.

## Implications for Plan

1. The P0 is **one prose page** (~60–120 lines), not a cascade. Budget accordingly.
2. **"Build passes" must not be a Success Criterion on its own** — an empty file satisfies it.
   The criterion is conjunctive: exit 0 under `--fatal warnings`, **and** the emitted
   `output/skills/yf-okf-hygiene/index.html` contains an `<hr>` with a non-trivial body, **and**
   ≥ 1 `<h2>` beyond "At a glance".
3. `architecture.md`'s count arithmetic is in scope or the plan lands knowingly red.
4. **#104 does not gate the plan** — keep it decoupled from the P0.
5. Every plan-authored verification snippet must avoid `| tail`; `PIPESTATUS` is not the remedy.
6. `publishconf.py` requires `PUBLISH_URL`; use `-s pelicanconf.py` for the loop and reserve the
   production config for one final check with the variable supplied.

## Follow-on (D5: file, do not fix)

The fail-closed guard should reject a zero-byte authored page rather than passing it. Filing
candidate — it is the same class as Result B and outside the four Class-B items in scope.

## Recommendations

The Implications section above is the recommendation set; each numbered item names the plan issue or decision it binds to.
