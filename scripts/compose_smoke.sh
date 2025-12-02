#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")"/.. && pwd)"
cd "$PROJECT_DIR"

if ! command -v docker >/dev/null; then
  echo "Docker is required to run this script" >&2
  exit 1
fi

cleanup() {
  docker compose down --remove-orphans
}
trap cleanup EXIT

# Build and start the service
DOCKER_BUILDKIT=1 docker compose up -d --build

# Wait for the API to become healthy
for _ in {1..15}; do
  if curl -fsS http://localhost:8000/health >/dev/null; then
    break
  fi
  sleep 2
done

# Fetch live data from Chotot through the running container
curl -fsS "http://localhost:8000/listings?region_v2=32&cg=1000&cgr=1002&pages=1&limit=3" | python -m json.tool | head -n 20
