from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AdRecord:
    id: int
    subject: str
    price: Optional[int]
    area: Optional[float]
    location: Optional[str]
    body: Optional[str]
    list_time: Optional[datetime]
    url: str
    images: List[str]
    contact_name: Optional[str]
    phone: Optional[str]
    raw: Dict[str, Any]


def timestamp_to_datetime(timestamp: Optional[int]) -> Optional[datetime]:
    if timestamp is None:
        return None
    try:
        return datetime.fromtimestamp(timestamp)
    except (ValueError, OSError):
        return None
