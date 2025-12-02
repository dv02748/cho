from chotot_parser.client import DummyClient
from chotot_parser.config import ScraperConfig
from chotot_parser.service import ScraperService


def test_service_refresh(tmp_path):
    payload = {
        "ads": [
            {
                "list_id": 2,
                "subject": "Căn hộ studio",
                "price": 8000000,
                "size": 35,
                "region_name": "Đà Nẵng",
                "list_time": 1700000001,
                "ad_link": "https://www.chotot.com/efg",
                "images": [],
                "contact": {},
            }
        ],
        "has_more": False,
    }

    config = ScraperConfig()
    service = ScraperService(config, client=DummyClient(payload))
    service.storage.path = tmp_path / "ads.json"

    ads = service.refresh()

    assert len(ads) == 1
    assert service.storage.path.exists()
    cached = service.load_cached()
    assert cached[0].id == 2
