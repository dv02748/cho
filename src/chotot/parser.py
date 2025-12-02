from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable, List

from .config import ScraperConfig
from .models import Listing


def _build_url(ad_id: int, config: ScraperConfig) -> str:
    return config.ad_detail_url_template.format(ad_id=ad_id)


def parse_ads(raw_payload: Dict[str, Any], config: ScraperConfig) -> List[Listing]:
    ads: Iterable[Dict[str, Any]] = raw_payload.get("ads", [])
    parsed: List[Listing] = []

    for ad in ads:
        ad_id = ad.get("ad_id") or ad.get("list_id")
        if not ad_id:
            continue

        attributes = ad.get("parameters") or []
        attribute_map = {attr.get("name"): attr.get("value") for attr in attributes if isinstance(attr, dict)}

        published = ad.get("list_time") or ad.get("published_at")
        published_dt = None
        if published:
            published_dt = datetime.fromtimestamp(int(published)) if isinstance(published, (int, float)) else None

        listing = Listing(
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
        )
        parsed.append(listing)

    return parsed
