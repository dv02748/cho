from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


DEFAULT_BASE_URL = "https://gateway.chotot.com/v1/public/ad-listing"


@dataclass
class ScraperConfig:
    city: str = "danang"
    city_region_id: int = 20000
    category_id: int = 1003
    limit: int = 20
    delay_seconds: float = 1.0
    max_pages: Optional[int] = None
    base_url: str = DEFAULT_BASE_URL
    default_params: Dict[str, str | int] = field(default_factory=dict)

    def build_params(self, page: int = 0) -> Dict[str, str | int]:
        offset = page * self.limit
        params: Dict[str, str | int] = {
            "region_v2": self.city_region_id,
            "cg": self.category_id,
            "o": offset,
            "page": page + 1,
            "limit": self.limit,
        }
        params.update(self.default_params)
        return params
