from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .models import AdRecord, timestamp_to_datetime


class AdParser:
    @staticmethod
    def parse_listing_payload(payload: Dict[str, Any]) -> Iterable[AdRecord]:
        for item in payload.get("ads", []):
            yield AdParser.parse_ad(item)

    @staticmethod
    def parse_ad(item: Dict[str, Any]) -> AdRecord:
        ad_id = int(item.get("list_id", 0))
        images = item.get("images", []) or []
        contact = item.get("contact", {}) or {}
        location_parts: List[str] = [
            val for val in [item.get("ward_name"), item.get("area_name"), item.get("region_name")] if val
        ]
        location = ", ".join(location_parts) if location_parts else None

        return AdRecord(
            id=ad_id,
            subject=item.get("subject", ""),
            price=item.get("price"),
            area=item.get("size"),
            location=location,
            body=item.get("body"),
            list_time=timestamp_to_datetime(item.get("list_time")),
            url=item.get("ad_link", ""),
            images=list(images),
            contact_name=contact.get("name"),
            phone=contact.get("phone"),
            raw=item,
        )
