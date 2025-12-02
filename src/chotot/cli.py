from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from .config import QueryConfig, ScraperConfig
from .service import ChototScraper

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scrape rental listings from Chotot")
    parser.add_argument("--region", type=int, dest="region_v2", default=None, help="Province identifier")
    parser.add_argument("--area", type=int, dest="area_v2", default=None, help="District identifier")
    parser.add_argument("--cg", type=int, default=1000, help="Category group (1000=real estate)")
    parser.add_argument(
        "--cgr",
        type=int,
        default=1002,
        help="Category (1002=for rent). Adjust to scrape other categories.",
    )
    parser.add_argument("--pages", type=int, default=1, help="Number of pages to fetch")
    parser.add_argument("--limit", type=int, default=20, help="Ads per page")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between page fetches")
    parser.add_argument("--output", type=Path, default=Path("listings.json"), help="Output file path")
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format",
    )
    parser.add_argument(
        "--ignore-env-proxy",
        action="store_true",
        help="Ignore HTTP(S)_PROXY environment variables for direct connections",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    query = QueryConfig(
        region_v2=args.region_v2,
        area_v2=args.area_v2,
        cg=args.cg,
        cgr=args.cgr,
        limit=args.limit,
    )
    config = ScraperConfig(
        query=query,
        delay_seconds=args.delay,
        trust_env_proxies=not args.ignore_env_proxy,
    )
    scraper = ChototScraper(config)

    listings = scraper.scrape(max_pages=args.pages)
    if args.format == "json":
        scraper.dump_to_json(listings, str(args.output))
    else:
        scraper.dump_to_csv(listings, str(args.output))

    print(json.dumps({"written": len(listings), "path": str(args.output)}, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
