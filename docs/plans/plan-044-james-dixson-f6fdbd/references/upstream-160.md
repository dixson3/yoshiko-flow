---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #160: A Dolt remote was configured and bead data pushed to GitHub despite dolt.local-only = true

- **Number:** 160
- **Title:** A Dolt remote was configured and bead data pushed to GitHub despite dolt.local-only = true
- **URL:** 
- **State:** OPEN
- **Labels:** 

## Body

## What was found

On 2026-08-17, `dixson3/yoshiko-flow` — a repo with `bd config get dolt.local-only` = **`true`** — was discovered to be configured as a live Dolt remote, with bead data present on GitHub:

```
$ git ls-remote origin | grep -i dolt
0ce1f031371c994b61ed493eda9836d8584f3d7b  refs/dolt/data
04905c9de439c32948616c7afb35837b0d5a3ea8  refs/heads/__dolt_remote_info__

$ git show origin/__dolt_remote_info__:DOLT_REMOTE.md
This repository is being used as a Dolt remote.
ref=refs/dolt/data
head=0ce1f031371c994b61ed493eda9836d8584f3d7b
timestamp=2026-08-16T21:41:58Z

$ bd dolt remote list
origin               git+https://github.com/dixson3/yoshiko-flow.git
```

So `dolt.local-only = true` and a configured Dolt remote **coexisted**, and a push had already occurred.

## Why this is a defect and not just an operator error

The invariant is stated in two always-loaded places:

- `YOSHIKO_FLOW.md`: *"For local-only repos, never add a Dolt remote or `bd dolt push`."*
- `yf-beads-upstream` SKILL.md: *"a local-only repo holds no Dolt remote; a stray one wedges bd 1.1.0's remote-migrate gate."*

**Nothing enforces it.** `dolt.local-only = true` is an assertion that is never checked against the actual remote list, so the two can drift apart silently and indefinitely — as they did here, for roughly a day, undetected by `yf doctor` (which reported `ok` throughout).

## What created it is unknown

This is the part worth investigating. The timestamp is `2026-08-16T21:41:58Z`. In the session that owned this repo at that time:

- `bd dolt push` was never run;
- the constraint was explicitly restated in the briefing given to a delegated execution session.

That leaves two candidates, and I could not distinguish them:

1. **`bd` created the remote implicitly** as a side effect of some other operation (a sync, an export, a migration). If so, the local-only assertion can be violated with no explicit push at all — the more serious reading.
2. **Another concurrent session did it.** Several were live on this machine.

## Impact

Low for data safety — the local DB was intact (1245 issues) and the remote was a redundant copy. But:

- it publishes the full bead DB, including `bd remember` content that is documented as **project-DB-local and never synced upstream** (`AGENTS.md`, Memory section). That is the actual confidentiality concern;
- a stray remote wedges bd 1.1.0's remote-migrate gate, per the skill's own warning.

## Suggested fix

Add a `yf doctor` axis that **fails** when `dolt.local-only = true` and `bd dolt remote list` is non-empty. The assertion and the observable state should not be able to disagree without something going red.

## Resolution applied here

Remote cleared locally (`bd dolt remote remove origin`) and both refs deleted from GitHub (`refs/heads/__dolt_remote_info__`, `refs/dolt/data`). Verified: no Dolt refs remain on origin; local DB unaffected.

Note that `yf doctor --repair --local-only --remove-remote` did **not** accomplish this — see #159.
