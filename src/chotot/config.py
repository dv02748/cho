from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


DEFAULT_BASE_URL = "https://gateway.chotot.com/v1/public/ad-listing"
DEFAULT_AD_DETAIL_URL = "https://www.chotot.com/{ad_id}.htm"


@dataclass
class QueryConfig:
    """Configuration for the query made to the Chotot public API."""

    region_v2: Optional[int] = None
    area_v2: Optional[int] = None
    ward: Optional[int] = None
    cg: Optional[int] = None
    cgr: Optional[int] = None
    limit: int = 20
    keyword: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def as_params(self) -> Dict[str, Any]:
        base_params: Dict[str, Any] = {
            "region_v2": self.region_v2,
            "area_v2": self.area_v2,
            "ward": self.ward,
            "cg": self.cg,
            "cgr": self.cgr,
            "limit": self.limit,
            "q": self.keyword,
        }
        filtered = {key: value for key, value in base_params.items() if value is not None}
        filtered.update(self.extra)
        return filtered


@dataclass
class ScraperConfig:
    """Global configuration for the scraping pipeline."""

    base_url: str = DEFAULT_BASE_URL
    ad_detail_url_template: str = DEFAULT_AD_DETAIL_URL
    delay_seconds: float = 1.0
    max_pages: Optional[int] = None
    timeout: int = 20
    query: QueryConfig = field(default_factory=QueryConfig)
    user_agent: str = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    )
