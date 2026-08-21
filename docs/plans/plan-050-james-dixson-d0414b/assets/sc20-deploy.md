---
type: Reference
okf_spec: OKF-PLAN
id: sc20-deploy
description: SC20 — the deploy, the version stamp, and the consent-gate outcome (Issue 6.6)
---

# SC20 — the deploy

## The version stamp MATCHES; no exemption is invoked

| | Value |
| :-- | :-- |
| `yf --version` | `yf 0.4.0 (1dcb95f)` |
| `git rev-parse --short HEAD` | `1dcb95f` |
| Verdict | **MATCH** |

SC20 permits a mismatch only with the documented reason recorded **and** `git diff --name-only
<base>...HEAD` touching nothing under `yf/` or `skills/`. That exemption is **not used here**,
and it would not have applied anyway: the merged range touches **11** files under `skills/`, so
`build.rs`'s `rerun-if-changed=../skills` fired and the stamp was re-derived. Recorded because
the criterion asks for the exemption's status either way, and "not applicable" is a different
answer from "applicable and satisfied".

The pre-deploy stamp was `5648102` — the previous `main` tip — so the rebuild genuinely
re-stamped rather than the check passing on a stale-but-coincidentally-equal hash.

## The consent-gate outcome, recorded either way

**The gate did not fire, and no `--allow-permissions-write` was needed.** The deploy was run
*without* that flag, deliberately, so that a `consent_required` change would surface as a
per-key delta and a refusal rather than being silently authorized:

```
yf self install --from-build --build --force
  -> installed /Users/james/.local/bin/yf (release build, v0.4.0)
  -> sync: deployed to claude-code, agents, codex, opencode, pi
  -> exit 0, no per-key delta, no refusal
```

So the config half found nothing requiring consent — the harness config already matched — and
all five harnesses received skills and the rules aggregate. Nothing was escalated to the
operator because there was nothing to escalate. Had the gate fired, the per-key delta would
have been presented and completion would have stopped there; `--allow-permissions-write` is a
**separate** operator authorization and is never assumed.

`--force` was required for a reason unrelated to consent: the first run refused with
`/Users/james/.local/bin/yf already exists — pass --force to overwrite`. That is binary
promotion, not config.

## The deploy is verified STRUCTURALLY, not by its exit code

An exit 0 from a deploy is exactly the kind of proof this plan spent six fixes learning not to
trust. What was checked:

| Artifact | Check | Result |
| :-- | :-- | :-- |
| `~/.claude/skills/yf-plan/scripts/doc_lint.py` | carries `def classify` | present |
| `~/.claude/skills/yf-plan/scripts/plan_extract.py` | carries `_verbatim` and `detail_lines` | present |
| `~/.claude/skills/yf-plan/scripts/plan_manager.py` | carries `resolve-start-gate` and `UPSTREAM_REQUIREMENTS` | present |
| all three | `diff` against the repo copy | **byte-identical** |
| `~/.claude/rules/YOSHIKO_FLOW.md` | carries the CLASSIFY-FIRST on-edit rule | present |
| the same | protocol version stamp | `DOC-LINT.md version=1.0.1` |

The rules-aggregate check matters most of the three: Issue 2.2a's rewrite of `DOC-LINT.md` is
the change that actually closes #181, and it is only in force once the aggregate carries it.
The `1.0.1` stamp is the manifest bump Issue 2.2a made — a protocol edit leaves the `sha256`
stale and `sync.py --check` does not catch it.

## Ordering

The deploy ran at land-the-plane, **after** the work was merged, validated (FULL tier 45/45),
and pushed — never mid-execution. AGENTS.md's reason is narrow and specific:
`plan_manager.py` is re-invoked per call, so a mid-execution deploy takes effect in the *same*
session for the scripts while `SKILL.md` prose is loaded once at invocation, leaving a
half-deployed session running new scripts against old prose.
