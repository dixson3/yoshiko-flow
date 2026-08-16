---
type: Reference
okf_spec: OKF-PLAN
---
# Upstream #132: yf-beads-upstream: BACKEND_AUTH has no jira entry — --backend jira emits GITHUB_TOKEN

- **Number:** 132
- **Title:** yf-beads-upstream: BACKEND_AUTH has no jira entry — --backend jira emits GITHUB_TOKEN
- **URL:** 
- **State:** OPEN
- **Labels:** type::task, priority::medium, upstream-followup

## Body

Found by the plan-038 drift-check. BACKEND_AUTH maps only github and gitlab; push_command_sequence() falls back to ('gh','GITHUB_TOKEN') for any other backend, so 'upstream.py push --backend jira' emits GITHUB_TOKEN=$(gh auth token) bd jira push … — the wrong token for Jira.

Pre-existing (the .get() fallback predates plan-038), but plan-038's SKILL.md rewrite now points readers at the verb, so the gap is more reachable. Documented as a blockquote caveat in the Backend generalization section rather than silently fixed, because wiring Jira auth without live verification would present an unverified stub as tested (GR-BUP-004).

Fix: add a jira entry to BACKEND_AUTH once the Jira auth CLI/env var is verified, OR make an unmapped backend fail loudly instead of falling back to gh.
