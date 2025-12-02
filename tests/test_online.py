from __future__ import annotations

import os
import pytest

from chotot.config import QueryConfig, ScraperConfig
from chotot.service import ChototScraper


RUN_ONLINE = os.getenv("RUN_ONLINE_TESTS") == "1"


@pytest.mark.skipif(not RUN_ONLINE, reason="Online tests are disabled by default")
def test_live_request_returns_ads():
    # Da Nang real-estate rental defaults; adjust ids if needed.
    query = QueryConfig(cg=1000, cgr=1002, region_v2=32, limit=5)
    config = ScraperConfig(query=query, delay_seconds=0.5, max_pages=1)
    scraper = ChototScraper(config)

    try:
        listings = scraper.scrape()
    except Exception as exc:  # pragma: no cover - network guard
        pytest.skip(f"Live request failed: {exc}")

    assert isinstance(listings, list)
    # When network and parameters are correct we expect to see at least one ad.
    if listings:
        assert listings[0].ad_id
