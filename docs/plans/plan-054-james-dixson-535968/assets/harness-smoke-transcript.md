---
type: Reference
okf_spec: OKF-PLAN
id: harness-smoke-transcript
description: Live headless pi + opencode regression against the DEPLOYED tree (plan-054 Issues 6.7 / 6.10, SC18 / SC35)
---

# Harness smoke transcript — live regression against the DEPLOYED tree

**Address space:** primary checkout `/Users/james/workspace/dixson3/yoshiko-flow`, branch `main`.
**cwd for every probe:** `/tmp/yf-smoke` — deliberately outside the repo, so `$GIT_ROOT`-relative
roots could not mask a user-scope failure.

| Component | Version |
| :-- | :-- |
| `pi` | 0.84.1 |
| `opencode` | 1.18.23 |
| `yf` (built; used to deploy) | 0.5.0 |
| `yf` on `PATH` (`~/.local/bin/yf`) | **pre-release — no `skill-dir` subcommand** |

Skills were deployed by `./target/debug/yf harness skills install` to all four detected
harnesses. **Which tree each harness read is recorded below**, because EXP-002 measured both
harnesses resolving to the *claude-code* copy while reporting success — a pass that does not name
the tree cannot be distinguished from that exact failure (SC35).

## Verdict

**PASS** for both harnesses on all three assertions, plus the isolated-HOME arm, plus the
divergent-tree mutation test added by Issue 6.10.

| Assertion | pi | opencode |
| :-- | :-: | :-: |
| 1. a yf skill name is listed | PASS | PASS |
| 2. a rule-block-only fact is quoted back | PASS | PASS |
| 3. a `${SKILL_DIR}`-resolved script runs and its JSON parses | PASS | PASS |
| 4. resolver under an isolated pi-only HOME, `yf` unreachable | PASS | n/a |
| 5. **divergent-tree** skew test (Issue 6.10) | PASS | PASS |

---

## 1. Skill listing

Both harnesses listed all 19 shipped skills — the bundle was found and parsed.

```
$ pi -p 'List the names of the skills available to you, comma separated…'
… yf-beads-authoring, yf-beads-extra, yf-beads-hygiene, yf-beads-init, yf-beads-upstream,
yf-change-validation, yf-diagram-authoring, yf-drift-check, yf-herdr, yf-incubator,
yf-markdown-format, yf-markdown-html, yf-markdown-lint, yf-markdown-pdf, yf-okf,
yf-optimal-instructions, yf-plan, yf-research, yf-skill-authoring …

$ opencode run 'List the names of the skills available to you, comma separated…'
… yf-beads-authoring, … yf-plan, yf-research, yf-skill-authoring
```

## 2. Rule-block-only fact

The probe offers an explicit `NOT-IN-CONTEXT` escape, so a harness lacking the always-loaded
block says so rather than confabulating. Neither used it.

```
$ pi -p 'Answer ONLY from your always-loaded instructions … else NOT-IN-CONTEXT.'
All planning uses the `/yf-plan` skill (and native plan mode must not be used).

$ opencode run '… same probe …'
The `/yf-plan` skill — "All planning uses the `/yf-plan` skill. Do not use native plan mode."
```

## 3. A `${SKILL_DIR}`-resolved script runs

**This is the half the resolver defect broke.** Both returned parseable JSON:

```
{
  "plans": [],
  "research": []
}
```

pi reported its own resolution path unprompted: `SKILL_DIR` unset → `yf skill-dir` produced
nothing (the **PATH** copy is pre-release) → the fallback answered. That is the fallback doing
exactly its job.

## 4. Isolated-HOME arm — the one that proves the not-found fix

Run against the **deployed** `SKILL.md`'s generated resolver, under a `HOME` containing **only**
the pi root (asserted: no `.claude` present), with `PATH` pointed at an empty directory so `yf`
was unreachable:

```
isolated HOME: no .claude present
resolved: <tmp>/home/.pi/agent/skills/yf-plan
PASS — resolved to the pi destination under a pi-only HOME with no yf on PATH
```

Against a normal `HOME` this passes **by accident**, because `~/.claude/skills` answers. That
accidental green *is* the live defect, which is why this arm exists.

## 5. Divergent-tree skew test (Issue 6.10, #248)

The first run of this regression found the cross-tree skew **open**: both harnesses reported,
independently and unprompted, that prose came from their own tree while scripts ran from
`.claude`.

Issue 1.7's remedy is env-var-first, so a harness exporting `SKILL_DIR` wins. **Measured: neither
harness exports it.** opencode exports only `OPENCODE` and `OPENCODE_PID` — no path signal of any
kind — and pi exports `PI_CODING_AGENT`, a boolean. The mechanism was right and nothing fed it.

Issue 6.10 closed it by construction: `yf harness skills install` stamps each **deployed copy's
own destination root** into that copy's resolver.

**A test that passes because the trees are identical proves nothing** — which is precisely why
this shipped latent the first time. So a distinguishing `WHICH-TREE` marker was planted in
**each** tree's `plan_manager.py`, making them genuinely divergent, and both harnesses were
re-run live:

```
pi        SKILL_DIR -> /Users/james/.pi/agent/skills/yf-plan          WHICH-TREE=PI-TREE
opencode  SKILL_DIR -> /Users/james/.config/opencode/skills/yf-plan   WHICH-TREE=OPENCODE-TREE
```

pi additionally reported, unprompted, that the search fallback **would** have resolved to
`~/.claude/skills/yf-plan` — direct evidence that the stamp, not coincidence, decided it.

Residue was removed by a clean redeploy; all 19 skills verify `unmodified` afterwards, confirming
the stamp is invisible to the tree hash (`REQ-YF-MARK-001`).

---

## Provenance note

This transcript is **hand-recorded** from the probes above, not machine-generated.
`check-harness-smoke.sh` truncates and rewrites this file on each run; an earlier backgrounded
invocation was killed by a timeout mid-run and left a stub, which was committed before the
truncation was noticed. The script has since been corrected to resolve the tree with the
**tree-under-test's** binary rather than the pre-release copy on `PATH`, which had made it record
`<unresolved>` for every harness — turning SC35's whole point into a placeholder.
