from __future__ import annotations

import logging
from typing import Iterable, List, Optional

from .apartment_models import ApartmentListing
from .apartment_parser import parse_apartments
from .client import ChototClient
from .config import ScraperConfig

logger = logging.getLogger(__name__)


class ApartmentScraper:
    """
    Specialized scraper for apartment rental listings on Chotot.

    This scraper extends the base functionality with apartment-specific
    field extraction and parsing.
    """

    def __init__(self, config: ScraperConfig):
        """
        Initialize apartment scraper.

        Args:
            config: Scraper configuration with query parameters
        """
        self.config = config
        self.client = ChototClient(config)

    def scrape(self, max_pages: Optional[int] = None) -> List[ApartmentListing]:
        """
        Scrape apartment listings from Chotot.

        Args:
            max_pages: Maximum number of pages to scrape (None for unlimited)

        Returns:
            List of parsed apartment listings
        """
        collected: List[ApartmentListing] = []
        params = self.config.query.as_params()
        limit = params.get("limit", self.config.query.limit)
        page = 1
        pages_cap = max_pages or self.config.max_pages

        while True:
            logger.info("Fetching page %s with params %s", page, params)
            payload = self.client.fetch_page(page=page, base_params=params)
            page_ads = parse_apartments(payload, self.config)
            collected.extend(page_ads)

            total = payload.get("total") or payload.get("total_ads")
            if not page_ads:
                logger.info("No ads on page %s; stopping.", page)
                break

            if pages_cap and page >= pages_cap:
                logger.info("Reached page cap %s", pages_cap)
                break

            if total and len(collected) >= total:
                logger.info("Reached total ads %s", total)
                break

            expected_pages = None
            if total and limit:
                expected_pages = (int(total) + int(limit) - 1) // int(limit)

            page += 1
            if expected_pages and page > expected_pages:
                break

        return collected

    @staticmethod
    def dump_to_json(listings: Iterable[ApartmentListing], path: str) -> None:
        """
        Save apartment listings to JSON file.

        Args:
            listings: List of apartment listings
            path: Output file path
        """
        import json

        with open(path, "w", encoding="utf-8") as handle:
            json.dump([listing.as_dict() for listing in listings], handle, ensure_ascii=False, indent=2)

    @staticmethod
    def dump_to_csv(listings: Iterable[ApartmentListing], path: str) -> None:
        """
        Save apartment listings to CSV file.

        Args:
            listings: List of apartment listings
            path: Output file path
        """
        import csv

        rows = [listing.as_dict() for listing in listings]
        if not rows:
            return

        fieldnames = list(rows[0].keys())
        with open(path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def filter_by_rooms(self, listings: List[ApartmentListing], min_rooms: int, max_rooms: Optional[int] = None) -> List[ApartmentListing]:
        """
        Filter apartments by number of rooms.

        Args:
            listings: List of apartment listings
            min_rooms: Minimum number of rooms
            max_rooms: Maximum number of rooms (None for no upper limit)

        Returns:
            Filtered list of apartments
        """
        filtered = [apt for apt in listings if apt.rooms is not None and apt.rooms >= min_rooms]
        if max_rooms is not None:
            filtered = [apt for apt in filtered if apt.rooms <= max_rooms]
        return filtered

    def filter_by_price(self, listings: List[ApartmentListing], min_price: int, max_price: Optional[int] = None) -> List[ApartmentListing]:
        """
        Filter apartments by price range.

        Args:
            listings: List of apartment listings
            min_price: Minimum price
            max_price: Maximum price (None for no upper limit)

        Returns:
            Filtered list of apartments
        """
        filtered = [apt for apt in listings if apt.price is not None and apt.price >= min_price]
        if max_price is not None:
            filtered = [apt for apt in filtered if apt.price <= max_price]
        return filtered

    def filter_furnished(self, listings: List[ApartmentListing], furnished: bool = True) -> List[ApartmentListing]:
        """
        Filter apartments by furniture status.

        Args:
            listings: List of apartment listings
            furnished: True for furnished, False for unfurnished

        Returns:
            Filtered list of apartments
        """
        return [apt for apt in listings if apt.furnished == furnished]
