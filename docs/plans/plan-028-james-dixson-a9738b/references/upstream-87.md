# Upstream #87: credibility_scorer.py: tz-naive date crash + domain allowlist misses dev-tooling primaries

- **Number:** 87
- **Title:** credibility_scorer.py: tz-naive date crash + domain allowlist misses dev-tooling primaries
- **URL:** 
- **State:** OPEN
- **Labels:** bug

## Body

Found during yf-research 272 triangulation (Git forge viability & migration).

**Location:** `.claude/skills/yf-research/scripts/credibility_scorer.py`

## 1. `_currency_score` crashes on timezone-naive publication dates

```python
def _currency_score(published_date: str | None, evergreen: bool = False) -> int:
    ...
    pub = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
    ...
    now = datetime.now(timezone.utc)
    age_days = (now - pub).days   # TypeError if pub is naive
```

If `published_date` is a tz-naive ISO string (no `Z` and no offset), `datetime.fromisoformat` returns a naive `datetime`. Subtracting it from `now` (tz-aware) raises `TypeError: can't subtract offset-naive and offset-aware datetimes`, crashing the whole batch. The caller currently has to pre-normalize every date to tz-aware ISO to avoid this.

**Fix:** in `_currency_score`, if `pub.tzinfo is None`, assume UTC (`pub = pub.replace(tzinfo=timezone.utc)`) before computing `age_days`.

## 2. Domain authority allowlist misses official dev-tooling docs

`TIER_2_DOMAINS` includes some official docs (`docs.python.org`, `docs.microsoft.com`, `developer.mozilla.org`, `docs.aws.amazon.com`, `cloud.google.com`) but not others that came up during the git-forge research:

- `docs.gitea.com`
- `forgejo.org`
- `docs.gitlab.com`
- `docs.github.com`
- `docs.gocd.org`
- `cli.github.com`
- `github.blog`

These fall through to the `30` "unknown domain" score instead of Tier 2 (70-84), forcing manual rubric correction on every research pass that cites them.

**Fix:** add the above domains to `TIER_2_DOMAINS`, or better, add a heuristic tier bump for `docs.*` / `*.dev` / known vendor-doc subdomains so future dev-tooling vendors don't require a one-off allowlist edit each time.

---
Filed from BeyondIdentity vault bead `BeyondIdentity-nue` (discovered-from `BeyondIdentity-mol-0u0`, yf-research run 272).
