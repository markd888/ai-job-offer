#!/bin/sh
# Build the frontend and export the role cards into .cloud/ for the Cloudflare Worker.
# Usage (from dashboard/): sh scripts/build_cloud.sh && npx wrangler deploy
set -e
cd "$(dirname "$0")/.."
npm run build
python3 scripts/export_cloud.py --userdata ../userdata --out .cloud
