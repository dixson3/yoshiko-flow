# /// script
# requires-python = ">=3.11"
# dependencies = ["click", "pytest"]
# ///
"""Tests for credibility_scorer (REQ-RESEARCH-024): tz-naive currency + dev-tooling domain tiers."""
from credibility_scorer import _currency_score, _domain_authority_score


# --- _currency_score: tz-naive normalization (REQ-RESEARCH-024a) ---

def test_tz_naive_date_does_not_raise_and_scores_by_age():
    # A bare ISO date parses to a naive datetime; before the fix, subtracting a
    # tz-aware `now` raised TypeError. Now it normalizes to UTC and scores by age.
    score = _currency_score("2024-01-15")
    assert isinstance(score, int)
    assert 20 <= score <= 95


def test_tz_naive_datetime_no_offset_normalizes():
    score = _currency_score("2024-01-15T10:30:00")
    assert isinstance(score, int)
    assert 20 <= score <= 95


def test_tz_aware_offset_date_unchanged():
    assert _currency_score("2024-01-15T00:00:00+00:00") == _currency_score("2024-01-15")


def test_z_suffix_date_unchanged():
    # `Z` is normalized to +00:00; result equals the equivalent naive/UTC input.
    assert _currency_score("2024-01-15T00:00:00Z") == _currency_score("2024-01-15")


def test_evergreen_flat_score():
    assert _currency_score("2024-01-15", evergreen=True) == 80
    assert _currency_score(None, evergreen=True) == 80


def test_missing_date_middling():
    assert _currency_score(None) == 50


def test_garbage_date_middling():
    assert _currency_score("not-a-date") == 50


def test_recent_date_high():
    # Within 365 days of now -> 95. Use a near-now UTC-aware date.
    from datetime import datetime, timezone
    recent = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    assert _currency_score(recent) == 95


# --- _domain_authority_score: dev-tooling domain tiers (REQ-RESEARCH-024b) ---

TIER_2_BAND = range(70, 85)  # 70-84 inclusive

NAMED_DEVTOOL_DOMAINS = [
    "https://docs.gitea.com/usage",
    "https://forgejo.org/docs/",
    "https://docs.gitlab.com/ee/",
    "https://docs.github.com/en/actions",
    "https://docs.gocd.org/current/",
    "https://cli.github.com/manual/",
    "https://github.blog/2024-01-01-post/",
]


def test_named_devtool_domains_score_tier2():
    for url in NAMED_DEVTOOL_DOMAINS:
        assert _domain_authority_score(url) in TIER_2_BAND, url


def test_novel_docs_host_heuristic_tier2():
    # A vendor-doc host not in any allowlist still lands Tier 2 via the docs.* heuristic.
    assert _domain_authority_score("https://docs.vendor-xyz.io/api") in TIER_2_BAND


def test_novel_dev_tld_heuristic_tier2():
    assert _domain_authority_score("https://something.dev/page") in TIER_2_BAND


def test_unknown_domain_still_30():
    assert _domain_authority_score("https://random-blog.example/post") == 30


def test_empty_url_low():
    assert _domain_authority_score("") == 20


def test_tier1_gov_never_downgraded():
    # A gov host that also starts with docs. must keep its Tier-1 score (92),
    # proving the heuristic runs after the exact/TLD-tier resolution.
    assert _domain_authority_score("https://docs.nasa.gov/mission") == 92


def test_tier1_edu_never_downgraded():
    assert _domain_authority_score("https://docs.mit.edu/course") == 92


def test_tier1_exact_domain_never_downgraded():
    # arxiv.org is Tier 1; it must not be pulled down by any later heuristic.
    assert _domain_authority_score("https://arxiv.org/abs/1234.5678") >= 85


if __name__ == "__main__":
    import sys
    import pytest

    sys.exit(pytest.main([__file__, "-q"]))
