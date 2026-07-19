# /// script
# requires-python = ">=3.11"
# dependencies = ["click", "pytest"]
# ///
"""Tests for link_normalizer GFM citation/link conversion + idempotency."""
from link_normalizer import gh_slug, rewrite_citations

KNOWN = {"CL12", "AB3", "ME7"}


def test_gh_slug():
    assert gh_slug("CL12") == "cl12"
    assert gh_slug("AB3") == "ab3"


def test_single_citation_to_gfm():
    out, n = rewrite_citations("See [CL12] for detail.", KNOWN)
    assert out == "See [CL12](sources.md#cl12) for detail."
    assert n == 1


def test_multi_source_renders_both_links():
    out, n = rewrite_citations("Both [CL12, AB3] agree.", KNOWN)
    assert out == "Both [CL12](sources.md#cl12), [AB3](sources.md#ab3) agree."
    assert n == 2


def test_mixed_citation_uses_parens():
    out, _ = rewrite_citations("Per [ABA-internal data, ME7] here.", KNOWN)
    assert out == "Per (ABA-internal data, [ME7](sources.md#me7)) here."


def test_unknown_id_left_alone():
    out, n = rewrite_citations("See [ZZ99] and [uncertain].", KNOWN)
    assert out == "See [ZZ99] and [uncertain]."
    assert n == 0


def test_rewrite_citations_idempotent():
    once, _ = rewrite_citations("See [CL12] and [CL12, AB3].", KNOWN)
    twice, n = rewrite_citations(once, KNOWN)
    assert twice == once
    assert n == 0


# The legacy `rewrite_index` / `link-index` path (which rewrote the Artifact
# column of the old `_index.md` timestamped GFM table into links) has been
# retired: the OKF bundle listing is now `index.md`, a bullet listing emitted
# by index_manager.py / okf.add_index_entry that already carries
# `[artifact](path)` GFM links, so no post-hoc table-cell link rewriting is
# needed (REQ-PORT-009 / OKF-EXTENSION §5). Its tests are removed accordingly.


def test_no_link_index_command():
    """link-index is retired; only build-sources, link-citations, all remain."""
    from link_normalizer import cli

    assert "link-index" not in cli.commands
    assert set(cli.commands) == {"build-sources", "link-citations", "all"}


if __name__ == "__main__":
    import sys
    import pytest

    sys.exit(pytest.main([__file__, "-q"]))
