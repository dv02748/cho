from __future__ import annotations

import json
from pathlib import Path

from chotot.config import ScraperConfig
from chotot.parser import parse_ads


FIXTURE = Path(__file__).parent / "tests_data" / "sample_ads.json"


def test_parse_ads_from_fixture():
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    config = ScraperConfig()
    listings = parse_ads(raw, config)

    assert len(listings) == 1
    listing = listings[0]
    assert listing.ad_id == 123456
    assert listing.title.startswith("Căn hộ studio")
    assert listing.price == 7500000
    assert listing.area_m2 == 35
    assert listing.address.startswith("Phường Phước Mỹ")
    assert listing.city == "Đà Nẵng"
    assert listing.district == "Sơn Trà"
    assert listing.ward == "Phước Mỹ"
    assert listing.url.endswith("123456.htm")
    assert listing.images[0].endswith("sample1.jpg")
    assert listing.attributes["rooms"] == 1
    assert listing.published_at is not None
