from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Listing:
    """Normalized representation of a Chotot listing."""

    ad_id: int
    title: str
    price: Optional[int]
    area_m2: Optional[float]
    address: Optional[str]
    city: Optional[str]
    district: Optional[str]
    ward: Optional[str]
    category: Optional[str]
    description: Optional[str]
    contact_name: Optional[str]
    phone: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    url: str
    images: List[str] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    published_at: Optional[datetime] = None

    def as_dict(self) -> Dict[str, Any]:
        result = self.__dict__.copy()
        result["published_at"] = self.published_at.isoformat() if self.published_at else None
        return result
