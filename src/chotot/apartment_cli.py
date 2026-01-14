from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .apartment_service import ApartmentScraper
from .config import QueryConfig, ScraperConfig

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

# Predefined city codes for major Vietnamese cities
CITIES = {
    "danang": 32,
    "da-nang": 32,
    "hanoi": 13,
    "hcm": 31,
    "ho-chi-minh": 31,
    "saigon": 31,
    "haiphong": 15,
    "can-tho": 52,
    "bien-hoa": 41,
    "nha-trang": 37,
    "vung-tau": 43,
}

# Category codes
CATEGORY_APARTMENT_RENT = {
    "cg": 1000,  # Real Estate
    "cgr": 1010,  # Apartments for rent
}


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for apartment scraper CLI."""
    parser = argparse.ArgumentParser(
        description="Scrape apartment rental listings from Chotot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape apartments in Da Nang
  python -m chotot.apartment_cli --city danang --pages 3 --output apartments.json

  # Scrape apartments in Ho Chi Minh City with filters
  python -m chotot.apartment_cli --city hcm --min-rooms 2 --max-price 15000000 --pages 5

  # Export to CSV format
  python -m chotot.apartment_cli --city hanoi --format csv --output hanoi_apartments.csv

  # Use custom region code
  python -m chotot.apartment_cli --region 32 --pages 2 --output custom.json
        """,
    )

    parser.add_argument(
        "--city",
        type=str,
        choices=list(CITIES.keys()),
        help="City name (predefined codes: danang, hanoi, hcm, haiphong, etc.)",
    )
    parser.add_argument(
        "--region",
        type=int,
        dest="region_v2",
        default=None,
        help="Province identifier (use this or --city)",
    )
    parser.add_argument(
        "--area",
        type=int,
        dest="area_v2",
        default=None,
        help="District identifier",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to fetch (default: 1)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Ads per page (default: 20)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between page fetches in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("apartments.json"),
        help="Output file path (default: apartments.json)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--min-rooms",
        type=int,
        default=None,
        help="Minimum number of bedrooms",
    )
    parser.add_argument(
        "--max-rooms",
        type=int,
        default=None,
        help="Maximum number of bedrooms",
    )
    parser.add_argument(
        "--min-price",
        type=int,
        default=None,
        help="Minimum price (VND)",
    )
    parser.add_argument(
        "--max-price",
        type=int,
        default=None,
        help="Maximum price (VND)",
    )
    parser.add_argument(
        "--furnished-only",
        action="store_true",
        help="Only return furnished apartments",
    )
    parser.add_argument(
        "--ignore-env-proxy",
        action="store_true",
        help="Ignore HTTP(S)_PROXY environment variables for direct connections",
    )

    return parser


def main() -> None:
    """Main entry point for apartment scraper CLI."""
    args = build_parser().parse_args()

    # Determine region code
    region_v2 = args.region_v2
    if args.city:
        region_v2 = CITIES[args.city]
        logging.info("Using region code %s for city: %s", region_v2, args.city)
    elif not region_v2:
        logging.error("Either --city or --region must be specified")
        return

    # Create query configuration for apartments
    query = QueryConfig(
        region_v2=region_v2,
        area_v2=args.area_v2,
        cg=CATEGORY_APARTMENT_RENT["cg"],
        cgr=CATEGORY_APARTMENT_RENT["cgr"],
        limit=args.limit,
    )

    # Create scraper configuration
    config = ScraperConfig(
        query=query,
        delay_seconds=args.delay,
        trust_env_proxies=not args.ignore_env_proxy,
    )

    # Initialize scraper and fetch listings
    scraper = ApartmentScraper(config)
    logging.info("Starting apartment scraping for region %s...", region_v2)
    listings = scraper.scrape(max_pages=args.pages)
    logging.info("Scraped %s apartment listings", len(listings))

    # Apply filters if specified
    if args.min_rooms or args.max_rooms:
        min_rooms = args.min_rooms or 0
        listings = scraper.filter_by_rooms(listings, min_rooms, args.max_rooms)
        logging.info("Filtered by rooms: %s listings remaining", len(listings))

    if args.min_price or args.max_price:
        min_price = args.min_price or 0
        listings = scraper.filter_by_price(listings, min_price, args.max_price)
        logging.info("Filtered by price: %s listings remaining", len(listings))

    if args.furnished_only:
        listings = scraper.filter_furnished(listings, furnished=True)
        logging.info("Filtered furnished only: %s listings remaining", len(listings))

    # Save to file
    if args.format == "json":
        scraper.dump_to_json(listings, str(args.output))
    else:
        scraper.dump_to_csv(listings, str(args.output))

    # Print summary
    summary = {
        "total_listings": len(listings),
        "output_path": str(args.output),
        "output_format": args.format,
        "region": region_v2,
        "city": args.city if args.city else "custom",
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":  # pragma: no cover
    main()
