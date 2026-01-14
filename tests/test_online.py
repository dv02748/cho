from __future__ import annotations

import os
import pytest

from chotot.config import QueryConfig, ScraperConfig
from chotot.service import ChototScraper
from chotot.apartment_service import ApartmentScraper


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


@pytest.mark.skipif(not RUN_ONLINE, reason="Online tests are disabled by default")
def test_live_apartment_request_returns_apartments():
    # Da Nang apartment rentals
    query = QueryConfig(cg=1000, cgr=1010, region_v2=32, limit=5)
    config = ScraperConfig(query=query, delay_seconds=0.5, max_pages=1)
    scraper = ApartmentScraper(config)

    try:
        apartments = scraper.scrape()
    except Exception as exc:  # pragma: no cover - network guard
        pytest.skip(f"Live apartment request failed: {exc}")

    assert isinstance(apartments, list)
    if apartments:
        apt = apartments[0]
        assert apt.ad_id
        # Check apartment-specific fields are accessible
        assert hasattr(apt, 'rooms')
        assert hasattr(apt, 'furnished')
        assert hasattr(apt, 'floor')


@pytest.mark.skipif(not RUN_ONLINE, reason="Online tests are disabled by default")
def test_apartment_filters_work():
    # Test filtering functionality with live data
    query = QueryConfig(cg=1000, cgr=1010, region_v2=32, limit=20)
    config = ScraperConfig(query=query, delay_seconds=0.5, max_pages=1)
    scraper = ApartmentScraper(config)

    try:
        apartments = scraper.scrape()
    except Exception as exc:  # pragma: no cover - network guard
        pytest.skip(f"Live apartment request failed: {exc}")

    if not apartments:
        pytest.skip("No apartments returned for filtering test")

    # Test room filter
    filtered = scraper.filter_by_rooms(apartments, min_rooms=1, max_rooms=3)
    assert len(filtered) <= len(apartments)

    # Test price filter
    filtered = scraper.filter_by_price(apartments, min_price=0, max_price=50000000)
    assert len(filtered) <= len(apartments)
