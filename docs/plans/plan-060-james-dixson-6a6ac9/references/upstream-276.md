---
type: Reference
okf_spec: OKF-PLAN
description: 'Upstream issue #276 - yf-plan: the portability audit checks files on
  DISK, not git-TRACKED-ness — a gitignored evidence file passes the audit and is
  invisible to a cold reader'
---
# Upstream #276: yf-plan: the portability audit checks files on DISK, not git-TRACKED-ness — a gitignored evidence file passes the audit and is invisible to a cold reader

- **Number:** 276
- **Title:** yf-plan: the portability audit checks files on DISK, not git-TRACKED-ness — a gitignored evidence file passes the audit and is invisible to a cold reader
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

> Found during plan-058's intake. The plan's first commit **silently dropped two evidence
> transcripts** and the portability audit passed anyway.

## The defect

`plan_manager.py audit` verifies that a bundle's cited files **exist on disk** and that links
traverse. It does **not** verify they are **tracked by git**.

So a file that is present locally, correctly linked, and cited as load-bearing evidence can be
excluded by a gitignore rule and still pass the audit — while being **absent from every clone**.

The portability audit exists precisely to guarantee that *"a cold reader in a different repo must be
able to understand the plan from the folder alone"* (`AGENTS.md` planning protocol). A file that is
not committed defeats that guarantee, and this check cannot see it.

## The instance

plan-058 vendored two experiment transcripts as its re-runnable evidence:

- `assets/exp001-equivalence-harness.log`
- `assets/exp001b-repro-334s.log`

Both are cited by `index.md` and by two `findings/*.md` as the evidence for the plan's
**load-bearing equivalence claim** (the 1,648-edge / `EQUIVALENT=True` result that justifies the
whole rewrite).

The operator's `~/.gitignore_global:51` is `*.log`. Both were excluded from the commit. **The audit
returned PASS.** A cold reader cloning the repo would have followed a citation to a file that had
never been committed — and the citation is the only place the central claim is reproducible.

Worked around in plan-058 by renaming to `.output.txt` and repointing all three referencing
documents. **The general defect is unfixed.**

## Why this is worse than it looks

1. **The failure is silent in both directions.** `git add` does not warn on an ignored path, and the
   audit does not check tracking — so nothing at any stage reports it. It is discoverable only by
   cloning, or by noticing a commit's file count is lower than expected.
2. **It is invisible to the author and visible only to the reader.** The bundle is complete and
   correct on the machine that wrote it. The audit runs there too.
3. **A global gitignore is outside the repo.** `~/.gitignore_global` is per-machine and
   uncommitted, so the same bundle can pass on one developer's machine and lose files on another's.
   Nothing in the repo records which patterns are in force.
4. **`.log` is the natural extension for exactly this content.** Command transcripts, harness
   output, and re-run evidence are what a plan is *supposed* to vendor — and `*.log` is one of the
   most common global-ignore patterns there is.

## Blast radius

Zero currently. `find docs/plans docs/research -name '*.log'` returns **0** — plan-058 was the first
bundle to vendor one, and it has been renamed. **This is a latent defect with no live instances**,
which is why it is filed rather than remediated.

## Suggested fix

Add a git-tracked-ness check to the audit, and make it a finding rather than a warning for any file
a bundle **cites**:

```bash
git check-ignore -v <path>          # would this be excluded?
git ls-files --error-unmatch <path> # is it actually tracked?
```

Note both are needed and neither alone suffices: `check-ignore` catches the ignore rule but not a
file simply never `git add`ed; `ls-files` catches untracked files but gives no reason. The
diagnostic an author needs is *"cited, present on disk, and excluded by
`~/.gitignore_global:51 (*.log)`"*.

**Scope it to cited files, not the whole bundle** — a bundle may legitimately hold local scratch that
nothing references.

## Related

- #268 — the plan whose intake surfaced this

🤖 Generated with [Claude Code](https://claude.com/claude-code)

