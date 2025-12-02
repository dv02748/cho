from __future__ import annotations

import logging
from typing import List

from fastapi import FastAPI, HTTPException

from .config import ScraperConfig
from .models import AdRecord
from .service import ScraperService

LOGGER = logging.getLogger(__name__)

app = FastAPI(title="ChoTot Scraper", version="0.1.0")
config = ScraperConfig()
service = ScraperService(config=config)


def serialize_ad(ad: AdRecord) -> dict:
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
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/listings", response_model=List[dict])
def listings() -> List[dict]:
    ads = service.load_cached()
    return [serialize_ad(ad) for ad in ads]


@app.post("/listings/refresh", response_model=List[dict])
def refresh() -> List[dict]:
    try:
        ads = service.refresh()
    except Exception as exc:  # pragma: no cover
        LOGGER.exception("Failed to refresh listings")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return [serialize_ad(ad) for ad in ads]
