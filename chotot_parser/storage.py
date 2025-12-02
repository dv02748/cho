from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .models import AdRecord


class LocalStorage:
    def __init__(self, path: str = "data/listings.json") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, ads: Iterable[AdRecord]) -> None:
        data = [self._serialize(ad) for ad in ads]
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    def load(self) -> List[AdRecord]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            payload = json.load(f)
        return [self._deserialize(item) for item in payload]

    def _serialize(self, ad: AdRecord) -> dict:
        return {
            "id": ad.id,
            "subject": ad.subject,
            "price": ad.price,
            "area": ad.area,
            "location": ad.location,
            "body": ad.body,
            "list_time": ad.list_time.isoformat() if ad.list_time else None,
            "url": ad.url,
            "images": ad.images,
            "contact_name": ad.contact_name,
            "phone": ad.phone,
            "raw": ad.raw,
        }

    def _deserialize(self, payload: dict) -> AdRecord:
        from datetime import datetime

        list_time = payload.get("list_time")
        return AdRecord(
            id=payload["id"],
            subject=payload.get("subject", ""),
            price=payload.get("price"),
            area=payload.get("area"),
            location=payload.get("location"),
            body=payload.get("body"),
            list_time=datetime.fromisoformat(list_time) if list_time else None,
            url=payload.get("url", ""),
            images=list(payload.get("images", [])),
            contact_name=payload.get("contact_name"),
            phone=payload.get("phone"),
            raw=payload.get("raw", {}),
        )
