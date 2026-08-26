---
type: Reference
okf_spec: OKF-PLAN
id: exp-002-live-harness-walk
description: EXP-002 — do yf skills actually load and run inside real pi and opencode sessions?
---

# EXP-002: live pi + opencode session walk

**Verdict: the multi-harness claim is REAL — and the one place it fails is the one that
matters.** Both harnesses load, invoke and execute yf skills end-to-end. Script resolution is
broken in both, and only *appears* to work here because a claude-code install happens to exist.

All runs headless, model pinned, under `timeout`, in a scratch dir. Nothing under `~/.pi`,
`~/.opencode` or `~/.config/opencode` was modified.

## Approach Tested

All runs headless in a scratch directory, model pinned to a local gateway, every invocation under `timeout`. Per harness: a skills listing diffed against the real directory contents, a rule-block probe with tools disallowed, a `SKILL_DIR` resolution plus `plan_manager.py list` run, and a full `yf-markdown-lint` execution on a fixture carrying a wiki-link, an empty link and a malformed table. Resolver replayed under a pi-only `HOME` from `mktemp -d`. Both harnesses' bundled skill loaders read statically. Nothing under `~/.pi`, `~/.opencode` or `~/.config/opencode` was modified; `pgrep` confirmed no leftover processes. The hardcoded-path enumeration and the `allowed-tools` count were **re-measured in the main session**.

## Result

## The good news — six things work

| | pi 0.84.1 | opencode 1.18.23 |
| :-- | :-- | :-- |
| Headless mode | `pi -p --no-session` (+ `--mode json\|rpc`) | `opencode run` |
| Sees the yf skills | **all 33** entries of its own root | **all 32** of its own root |
| `SKILL.md` format | native — *"Agent Skills standard"* | native, documented roots |
| Rule block reaches context | **yes**, quoted verbatim | **yes**, same quotes |
| Runs bash + `uv run` | **yes** — with **no yf config profile at all** | yes, via native `skill` tool |
| Full skill execution | `yf-markdown-lint` ran, correctly reported ML001/003/005/008, exit 1 | `plan_manager.py list` → parseable JSON |

**pi is reading its OWN root, not the claude one** — the diagnostic is clean: `mermaid` and
`naba` exist *only* in `~/.claude/skills` and pi did **not** list them, while 13 skills present
in `~/.pi/agent/skills` but absent from `~/.agents/skills` **were** listed.

**Q6 is moot — no manual checklist is needed.** Both harnesses are scriptable and exited well
inside timeout. This belongs in **Tier-2 automation**, and `Command::new("pi")` /
`Command::new("opencode")` can now be justified concretely.

## The defect, reproduced LIVE

Both harnesses resolved `SKILL_DIR` to **`/Users/james/.claude/skills/yf-plan`** — the
claude-code copy, **not** the copy the harness loaded the prose from.

So on this machine the **prose comes from the pi/opencode tree while the scripts come from the
claude tree.** That is `AGENTS.md`'s "three artifacts" skew, one level worse: not stale-vs-fresh
but *two different trees in the same run*.

Replayed under a `HOME` seeded with only `.pi/agent/skills/yf-plan`:

```console
ERROR: yf-plan skill directory not found
exit=1
```

**Why no existing test could ever have caught this:** the failure only appears when
`~/.claude/skills` is **absent** — a condition no test on a developer machine with claude-code
installed will ever produce.

## Second defect — hardcoded RELATIVE paths, and it is broader than first reported

`grep` in the main session found the literal `uv run .claude/skills/<skill>/scripts/...` in
**two** skills, not one:

| Skill | Sites |
| :-- | --: |
| `yf-markdown-lint` | `SKILL.md:34`, `SKILL.md:126`, `README.md:38` |
| **`yf-markdown-format`** | `SKILL.md:41,43,45,84,86,88`, `README.md:37,39,41,53,55` |

Under pi the model *silently repaired* the path to a working one, so it passed — but the literal
instruction is wrong in **every cwd lacking `.claude/skills/`, including under claude-code
itself.** These bypass `SKILL_DIR` entirely, so the D-1 fix does **not** reach them.

## Third finding — `allowed-tools` is claude-only

`grep -c allowed-tools` is **0** in both harnesses' bundles. **10 of the shipped `SKILL.md`
files carry it** (verified in the main session). Unknown frontmatter keys are ignored benignly
rather than rejected — which is why everything still ran — but **any yf security or scoping
assumption resting on `allowed-tools` does not hold outside claude-code.** It must be dropped
from the portability story or documented as claude-only.

## A design option this surfaces — worth considering against D-1

opencode already hands the model `Base directory for this skill: <dir>`, and pi tracks a
per-skill `baseDir`. A **location-relative** `SKILL_DIR` would be strictly more correct than any
root sweep, since it resolves to *the copy the harness actually loaded* — which is precisely the
cross-tree skew above.

It does **not** displace D-1: a bash snippet cannot portably learn its own file's location, and
the mechanism differs per harness. Best treated as a **complement** — `yf skill-dir` for the
general case, with the harness-provided base directory preferred when present.

## Untested, flagged

pi's loader has a **project-trust gate** — *"trust-requiring entries under cwd/.pi, or
.agents/skills"*, with `projectTrusted` defaulting to **false** when unresolvable. Only
user-scope skills were exercised. Project-scope yf skills under `.agents/skills` may be silently
withheld in `-p` mode absent `--approve`. This is the one plausible remaining silent-withholding
path.

## Implications for Plan

- The plan's highest-value unknown resolves **positively**: discovery, prose loading, model invocation, rule-block injection, bash and `uv run` all work in both harnesses.
- But it is **still false in the one place that matters** — script resolution. The existing filesystem-path assertions could never have caught this, because the failure appears only when `~/.claude/skills` is *absent*, a condition no developer machine with claude-code installed will produce.
- Both harnesses are scriptable, so this belongs in **Tier-2 automation, not a manual checklist**.
- The hardcoded relative paths **bypass `SKILL_DIR` entirely**, so the Epic 1 fix does not reach them; they need their own issue.
- `allowed-tools` must be dropped from the portability story or documented as claude-only.

## Recommendations

1. **D-1 stands, and is now live-validated.** Add the harness roots; prefer the
   harness-provided base directory where available.
2. **Convert the isolated-HOME replay into a Tier-2 test** — seed a `mktemp -d` HOME with *only*
   the pi (then only the opencode) root and assert `SKILL_DIR` resolves. **That single assertion
   is the whole gap.**
3. **Replace the hardcoded `.claude/skills/...` paths in both markdown skills** with
   `${SKILL_DIR}`, and grep the fleet for the literal.
4. **Add a headless smoke per harness** with the exact commands proven here — assert a skill
   name appears, a rule-block-only fact is quoted back, and `plan_manager.py list --json-output`
   parses. All three ran in **under two minutes**.
5. **Resolve `allowed-tools`** — drop it or document it as claude-only.
6. **Exercise pi's project-trust gate** before shipping project-scope skills to pi.

## Confidence

**measured:** every row of the capability table, both harnesses' loader sources and documented roots, the live cross-tree resolution, the isolated-HOME failure, the ML findings, and (in the main session) the hardcoded-path enumeration and the `allowed-tools` count.

**inferred:** that unknown frontmatter keys are ignored rather than rejected — corroborated by both harnesses running yf-plan successfully. pi's project-trust impact is uncorroborated.
