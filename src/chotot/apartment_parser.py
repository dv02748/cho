from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List

from .apartment_models import ApartmentListing
from .config import ScraperConfig


def _build_url(ad_id: int, config: ScraperConfig) -> str:
    """Build URL for apartment listing detail page."""
    return config.ad_detail_url_template.format(ad_id=ad_id)


def _extract_apartment_fields(attributes: Dict[str, Any], ad: Dict[str, Any]) -> Dict[str, Any]:
    """Extract apartment-specific fields from attributes and ad data."""
    apartment_fields = {}

    # Extract number of rooms (bedrooms)
    rooms = attributes.get("rooms") or attributes.get("room") or attributes.get("bedroom")
    if rooms:
        apartment_fields["rooms"] = int(rooms) if isinstance(rooms, (int, float, str)) else None

    # Extract number of bathrooms
    bathrooms = attributes.get("bathrooms") or attributes.get("bathroom")
    if bathrooms:
        apartment_fields["bathrooms"] = int(bathrooms) if isinstance(bathrooms, (int, float, str)) else None

    # Extract floor number
    floor = attributes.get("floor") or attributes.get("floor_number")
    if floor:
        apartment_fields["floor"] = int(floor) if isinstance(floor, (int, float, str)) else None

    # Extract furniture information
    furniture = attributes.get("furniture") or attributes.get("furnishing")
    if furniture:
        furniture_str = str(furniture).lower()
        apartment_fields["furniture_type"] = furniture_str
        apartment_fields["furnished"] = furniture_str in ["full", "fully", "đầy đủ nội thất", "yes", "true"]

    # Extract building name
    building = attributes.get("building") or attributes.get("building_name") or attributes.get("project")
    if building:
        apartment_fields["building_name"] = str(building)

    # Extract boolean features
    balcony = attributes.get("balcony") or attributes.get("has_balcony")
    if balcony is not None:
        apartment_fields["balcony"] = _parse_bool(balcony)

    parking = attributes.get("parking") or attributes.get("has_parking")
    if parking is not None:
        apartment_fields["parking"] = _parse_bool(parking)

    elevator = attributes.get("elevator") or attributes.get("has_elevator")
    if elevator is not None:
        apartment_fields["elevator"] = _parse_bool(elevator)

    pets = attributes.get("pets_allowed") or attributes.get("pets")
    if pets is not None:
        apartment_fields["pets_allowed"] = _parse_bool(pets)

    ac = attributes.get("air_conditioning") or attributes.get("ac") or attributes.get("airconditioner")
    if ac is not None:
        apartment_fields["air_conditioning"] = _parse_bool(ac)

    # Extract direction/orientation
    direction = attributes.get("direction") or attributes.get("orientation")
    if direction:
        apartment_fields["direction"] = str(direction)

    # Extract apartment type
    apt_type = attributes.get("apartment_type") or attributes.get("type") or attributes.get("property_type")
    if apt_type:
        apartment_fields["apartment_type"] = str(apt_type).lower()
    elif "studio" in str(ad.get("subject", "")).lower():
        apartment_fields["apartment_type"] = "studio"

    return apartment_fields


def _parse_bool(value: Any) -> bool:
    """Parse various boolean representations."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        return value.lower() in ["true", "yes", "1", "có", "có"]
    return False


def parse_apartments(raw_payload: Dict[str, Any], config: ScraperConfig) -> List[ApartmentListing]:
    """
    Parse apartment listings from Chotot API response.

    Args:
        raw_payload: Raw JSON response from Chotot API
        config: Scraper configuration

    Returns:
        List of parsed apartment listings with apartment-specific fields
    """
    ads: Iterable[Dict[str, Any]] = raw_payload.get("ads", [])
    parsed: List[ApartmentListing] = []

    for ad in ads:
        ad_id = ad.get("ad_id") or ad.get("list_id")
        if not ad_id:
            continue

        # Extract attributes
        attributes = ad.get("parameters") or []
        attribute_map = {attr.get("name"): attr.get("value") for attr in attributes if isinstance(attr, dict)}

        # Parse published date
        published = ad.get("list_time") or ad.get("published_at")
        published_dt = None
        if published:
            published_dt = datetime.fromtimestamp(int(published)) if isinstance(published, (int, float)) else None

        # Extract apartment-specific fields
        apartment_fields = _extract_apartment_fields(attribute_map, ad)

        # Create apartment listing with all fields
        listing = ApartmentListing(
            # Base listing fields
            ad_id=int(ad_id),
            title=ad.get("subject") or ad.get("title", ""),
            price=ad.get("price"),
            area_m2=ad.get("size") or attribute_map.get("size"),
            address=ad.get("address") or ad.get("body") or ad.get("street"),
            city=ad.get("region_name") or ad.get("region_v2") or attribute_map.get("region"),
            district=ad.get("area_name") or attribute_map.get("area"),
            ward=attribute_map.get("ward"),
            category=ad.get("category_name") or attribute_map.get("category"),
            description=ad.get("body") or ad.get("description"),
            contact_name=ad.get("account_name"),
            phone=ad.get("phone") or ad.get("phone_number"),
            latitude=ad.get("latitude"),
            longitude=ad.get("longitude"),
            url=_build_url(ad_id, config),
            images=[img.get("image") for img in ad.get("images", []) if isinstance(img, dict) and img.get("image")],
            attributes=attribute_map,
            published_at=published_dt,
            # Apartment-specific fields
            **apartment_fields,
        )
        parsed.append(listing)

    return parsed
