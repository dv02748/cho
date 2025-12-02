#!/usr/bin/env bash
set -euo pipefail

# Simple helper to run the CLI scraper with sensible defaults.
# Usage examples:
#   ./scripts/run_cli.sh                      # default: Danang rentals, 1 page
#   PAGES=3 LIMIT=50 OUTPUT=data/run.json ./scripts/run_cli.sh
#   FORMAT=csv ./scripts/run_cli.sh          # save CSV instead of JSON
#   IGNORE_ENV_PROXY=true ./scripts/run_cli.sh

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

REGION=${REGION:-32}
AREA=${AREA:-}
CG=${CG:-1000}
CGR=${CGR:-1002}
PAGES=${PAGES:-1}
LIMIT=${LIMIT:-20}
DELAY=${DELAY:-1.0}
FORMAT=${FORMAT:-json}
OUTPUT=${OUTPUT:-data/listings.${FORMAT}}
IGNORE_ENV_PROXY=${IGNORE_ENV_PROXY:-false}

mkdir -p "$(dirname "$OUTPUT")"

PYTHONPATH=${PYTHONPATH:-src}
CMD=(python -m chotot.cli \
  --region "$REGION" \
  --cg "$CG" \
  --cgr "$CGR" \
  --pages "$PAGES" \
  --limit "$LIMIT" \
  --delay "$DELAY" \
  --output "$OUTPUT")

if [[ -n "$AREA" ]]; then
  CMD+=(--area "$AREA")
fi

if [[ "$FORMAT" == "csv" ]]; then
  CMD+=(--format csv)
fi

if [[ "$IGNORE_ENV_PROXY" == "true" ]]; then
  CMD+=(--ignore-env-proxy)
fi

# Allow passing extra CLI args directly, e.g. --help or --format csv
CMD+=("$@")

PYTHONPATH="$PYTHONPATH" "${CMD[@]}"
