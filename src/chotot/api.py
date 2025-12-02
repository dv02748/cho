from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from .config import QueryConfig, ScraperConfig
from .models import Listing
from .service import ChototScraper

logger = logging.getLogger(__name__)
app = FastAPI(title="ChoTot scraping service", version="1.0.0")


class ListingResponse(BaseModel):
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
    images: List[str]
    attributes: dict
    published_at: Optional[str]

    @classmethod
    def from_listing(cls, listing: Listing) -> "ListingResponse":
        return cls(**listing.as_dict())


class ExportRequest(BaseModel):
    path: str
    format: str = "json"
    pages: Optional[int] = Query(None, ge=1, le=20)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@app.get("/listings", response_model=List[ListingResponse])
def get_listings(
    region_v2: Optional[int] = Query(None, description="Province identifier"),
    area_v2: Optional[int] = Query(None, description="District identifier"),
    cg: Optional[int] = Query(None, description="Category group"),
    cgr: Optional[int] = Query(None, description="Category"),
    keyword: Optional[str] = Query(None, alias="q"),
    limit: int = Query(20, ge=1, le=200),
    pages: Optional[int] = Query(1, ge=1, le=50),
):
    query = QueryConfig(
        region_v2=region_v2,
        area_v2=area_v2,
        cg=cg,
        cgr=cgr,
        keyword=keyword,
        limit=limit,
    )
    config = ScraperConfig(query=query)
    scraper = ChototScraper(config)

    try:
        listings = scraper.scrape(max_pages=pages)
    except Exception as exc:  # pragma: no cover - runtime guard for API users
        logger.exception("Failed to scrape listings: %s", exc)
        raise HTTPException(status_code=500, detail="Scraping failed")

    return [ListingResponse.from_listing(listing) for listing in listings]


@app.post("/listings/export")
def export_listings(req: ExportRequest):
    pages = req.pages or 1
    query = QueryConfig(limit=100)
    config = ScraperConfig(query=query)
    scraper = ChototScraper(config)
    listings = scraper.scrape(max_pages=pages)

    if req.format.lower() == "json":
        scraper.dump_to_json(listings, req.path)
    elif req.format.lower() == "csv":
        scraper.dump_to_csv(listings, req.path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported format, use json or csv")

    return {"written": len(listings), "path": req.path}
