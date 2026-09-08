#!/bin/bash
# Usage: ./rollback.sh <previous-sha>
set -e

if [ -z "$1" ]; then
  echo "Usage: ./rollback.sh <image-sha>"
  exit 1
fi

PREVIOUS_SHA=$1

ssh root@104.248.54.25 << EOF
  cd ~/knowledge-hub-staging
  sed -i "s/^IMAGE_TAG=.*/IMAGE_TAG=${PREVIOUS_SHA}/" .env
  docker compose -f docker-compose.staging.yml down
  docker pull ghcr.io/mishiez/knowledge-hub-backend:${PREVIOUS_SHA}
  docker compose -f docker-compose.staging.yml up -d
EOF

echo "Rolled back to ${PREVIOUS_SHA}"