from __future__ import annotations

from chotot.config import QueryConfig, ScraperConfig
from chotot.service import ChototScraper


class FakeClient:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def fetch_page(self, page: int, base_params):
        self.calls.append((page, base_params))
        return self.pages.get(page, {"ads": [], "total": 0})


def build_payload(ad_id: int, subject: str):
    return {
        "ads": [
            {
                "ad_id": ad_id,
                "subject": subject,
                "price": 1000000,
                "size": 20,
                "region_name": "Đà Nẵng",
                "area_name": "Sơn Trà",
                "list_time": 1710000100 + ad_id,
            }
        ],
        "total": 2,
    }


def test_scrape_paginates_until_no_ads():
    query = QueryConfig(limit=1)
    config = ScraperConfig(query=query, delay_seconds=0)
    scraper = ChototScraper(config)

    pages = {1: build_payload(1, "Listing 1"), 2: build_payload(2, "Listing 2"), 3: {"ads": [], "total": 2}}
    scraper.client = FakeClient(pages)

    listings = scraper.scrape()

    assert len(listings) == 2
    assert listings[0].title == "Listing 1"
    assert listings[1].title == "Listing 2"
    assert scraper.client.calls[0][0] == 1
    assert scraper.client.calls[1][0] == 2
