from __future__ import annotations

import json
from pathlib import Path

from chotot.apartment_parser import parse_apartments
from chotot.config import ScraperConfig


FIXTURE = Path(__file__).parent / "tests_data" / "sample_apartment_ads.json"


def test_parse_apartments_from_fixture():
    """Test parsing apartment-specific fields from fixture data."""
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    config = ScraperConfig()
    apartments = parse_apartments(raw, config)

    assert len(apartments) == 2

    # Test first apartment (studio)
    studio = apartments[0]
    assert studio.ad_id == 123456
    assert studio.title.startswith("Căn hộ studio")
    assert studio.price == 7500000
    assert studio.area_m2 == 35
    assert studio.city == "Đà Nẵng"
    assert studio.district == "Sơn Trà"
    assert studio.rooms == 1
    assert studio.apartment_type == "studio"
    assert studio.furnished is True

    # Test second apartment (2-bedroom)
    apartment = apartments[1]
    assert apartment.ad_id == 789012
    assert apartment.rooms == 2
    assert apartment.bathrooms == 2
    assert apartment.floor == 5
    assert apartment.balcony is True
    assert apartment.parking is True
    assert apartment.elevator is True
    assert apartment.building_name == "Pearl Plaza"
    assert apartment.direction == "South"


def test_parse_apartment_dict_conversion():
    """Test that apartment listings can be converted to dictionaries."""
    raw = json.loads(FIXTURE.read_text(encoding="utf-8"))
    config = ScraperConfig()
    apartments = parse_apartments(raw, config)

    apartment_dict = apartments[0].as_dict()

    # Check that apartment-specific fields are included
    assert "rooms" in apartment_dict
    assert "bathrooms" in apartment_dict
    assert "floor" in apartment_dict
    assert "furnished" in apartment_dict
    assert "apartment_type" in apartment_dict
    assert "building_name" in apartment_dict
    assert "balcony" in apartment_dict
    assert "parking" in apartment_dict
    assert "elevator" in apartment_dict

    # Check base fields
    assert "ad_id" in apartment_dict
    assert "title" in apartment_dict
    assert "price" in apartment_dict
    assert "area_m2" in apartment_dict
