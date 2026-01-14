#!/usr/bin/env bash

# Apartment scraper wrapper script for Chotot
# Usage: ./scripts/scrape_apartments.sh
# Environment variables:
#   CITY        - City name (danang, hanoi, hcm, etc.)
#   REGION      - Region code (overrides CITY)
#   PAGES       - Number of pages to scrape (default: 1)
#   LIMIT       - Ads per page (default: 20)
#   MIN_ROOMS   - Minimum number of bedrooms
#   MAX_ROOMS   - Maximum number of bedrooms
#   MIN_PRICE   - Minimum price in VND
#   MAX_PRICE   - Maximum price in VND
#   FURNISHED   - Only furnished apartments (true/false)
#   FORMAT      - Output format (json/csv, default: json)
#   OUTPUT      - Output file path
#   NO_PROXY    - Disable proxy usage (true/false)

set -euo pipefail

# Set defaults
CITY="${CITY:-danang}"
PAGES="${PAGES:-1}"
LIMIT="${LIMIT:-20}"
FORMAT="${FORMAT:-json}"
OUTPUT="${OUTPUT:-data/apartments_${CITY}.${FORMAT}}"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT")"

# Build command
CMD="python -m chotot.apartment_cli"

# Add city or region
if [ -n "${REGION:-}" ]; then
    CMD="$CMD --region $REGION"
else
    CMD="$CMD --city $CITY"
fi

# Add pagination
CMD="$CMD --pages $PAGES --limit $LIMIT"

# Add filters
if [ -n "${MIN_ROOMS:-}" ]; then
    CMD="$CMD --min-rooms $MIN_ROOMS"
fi

if [ -n "${MAX_ROOMS:-}" ]; then
    CMD="$CMD --max-rooms $MAX_ROOMS"
fi

if [ -n "${MIN_PRICE:-}" ]; then
    CMD="$CMD --min-price $MIN_PRICE"
fi

if [ -n "${MAX_PRICE:-}" ]; then
    CMD="$CMD --max-price $MAX_PRICE"
fi

if [ "${FURNISHED:-false}" = "true" ]; then
    CMD="$CMD --furnished-only"
fi

# Add output settings
CMD="$CMD --format $FORMAT --output $OUTPUT"

# Add proxy setting
if [ "${NO_PROXY:-false}" = "true" ]; then
    CMD="$CMD --ignore-env-proxy"
fi

# Run the command
echo "Running: $CMD"
eval "$CMD"
