---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #108: yf-plan: deliberate-class heuristic false-positives ci-release on ordinary infra plans

- **Number:** 108
- **Title:** yf-plan: deliberate-class heuristic false-positives ci-release on ordinary infra plans
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

Follow-up to #89, which introduced the `ci-release` deliverable class (REQ-PLAN-069a).

`_classify_deliverable()` (`scripts/plan_manager.py`) suggested **`ci-release` with `confidence: high`** on two consecutive Proxmox/Ansible infrastructure plans that ship no CI configuration whatsoever. Both required a manual `set-deliverable-class … standard` override. Every matched signal was a false positive.

Observed on skill `v=0.4.0` (`tree=d4f196d…`).

## Evidence

Two real plans — a PostgreSQL LXC guest and a LiteLLM gateway LXC guest. Neither produces a release artifact, touches `.github/workflows/`, or has any runner-only-observable behavior.

| Signal | Tier | What it actually matched |
| :----- | :--- | :----------------------- |
| `deploy` | low | `# Plan: **Deploy** the LiteLLM LLM proxy…` — **the plan title verb**, at byte offset 245 |
| `release` | high | "weekly **releases**, no N-1 support" — the *upstream dependency's* release cadence, not ours |
| `sign` | high | "PVE presents a self-**signed** certificate" — TLS, not code signing |
| `pipeline` | low | the OpenTelemetry collector's `metrics:` **pipeline** |
| `workflow` | low | the repo's "Ansible-primary **workflow**" convention |

`deploy` matching the title verb is the widest trap: infrastructure plans are very often named "Deploy X".

The `sign` regex is deliberately written to exclude `signal` (`\bsign(?:ing|ed|ature|s)?\b`) — but `self-signed` still matches, because `-` is a word boundary.

## Root causes

**1. The scan ignores its own docstring.** `plan_manager.py:1167-1169`:

```python
# Scan the epics/upstream/success-criteria region — in practice the whole body
# below the header block; a superset that never misses those sections.
hay = text.lower()
```

It is not a superset of those sections — it is the **entire file**, including the H1 title, the frontmatter, the fingerprint line, Risks, Approach prose, Gates and Rollback. The `deploy` hit above is in the title; several others are in risk-table cells. A "superset that never misses" also never *excludes*, which is the actual requirement here.

**2. No threshold.** Any single low-confidence keyword returns `suggested_class: "ci-release"`. There is no notion of "one weak signal in a 700-line document is noise".

**3. Confidence is over-stated.** `confidence` is `high` whenever any high pattern fires, even though the only genuinely reliable signal — `_CI_RELEASE_PATH_MARKER` (`.github/workflows/`) — is derived from `changed` paths, which are **empty at intake**, i.e. exactly when §4.1.5 calls the classifier. So at the moment of use, confidence is always inferred from prose alone but reported as if it were path-backed.

## Suggested directions

Not prescriptive — the maintainer may prefer a different balance:

- **Honor the docstring**: restrict `hay` to the `## Epics`, `## Upstream Issues` and `## Success Criteria` sections. Cheap, and removes the title-verb class entirely.
- **Negative context guards** for the demonstrated collisions: `self-signed`, `migrate deploy`, `deployed by`, `<signal> pipeline` where preceded by `metrics`/`logs`/`traces`, and `release` when it reads as an upstream cadence (`releases`, `release notes`, `release cycle`).
- **Require a high signal** — not a lone low keyword — before suggesting `ci-release`; report low-only matches as informational.
- **Reserve `confidence: high` for the path marker**, since it is the only signal that cannot be prose. Text-only matches are `low` by construction.

## Why it matters

The class is not cosmetic: it drives `complete-gate`, which fail-louds a `ci-release` plan without a `- validated:` attestation. A false positive that survives to reconcile blocks completion on a plan that never had runner-only behavior to attest — and the natural fix under time pressure is to attest something untrue, which is worse than the misclassification.

The current failure mode is safe (an operator overrides at intake in seconds) but it is silent-by-default: the suggestion arrives with `confidence: high`, which invites acceptance rather than scrutiny.

## Not fixed here

Reported rather than patched — the classifier lives in the user-global skill install and a change affects every consuming project, so this is the maintainer's call.
