#!/bin/sh
# Build the frontend and export the role cards into .cloud/ for the Cloudflare Worker.
#
# Usage: sh plugin/dashboard/scripts/build_cloud.sh [path/to/userdata]
#        then, from plugin/dashboard/: npx wrangler deploy
#
# userdata defaults to ./userdata in the directory you run this from — your
# workspace, the same folder /job-offer:dashboard serves — not a path relative
# to the plugin.
set -e
USERDATA=${1:-"$PWD/userdata"}
if [ ! -d "$USERDATA/companies" ]; then
  echo "No companies/ under $USERDATA." >&2
  echo "Run from your workspace, or pass the userdata path: sh $0 /path/to/userdata" >&2
  exit 1
fi
USERDATA=$(cd "$USERDATA" && pwd)
cd "$(dirname "$0")/.."
npm run build
python3 scripts/export_cloud.py --userdata "$USERDATA" --out .cloud
echo "Exported $USERDATA into $(pwd)/.cloud"
echo "Deploy from $(pwd): npx wrangler deploy  (the Worker serves nothing until ACCESS_TEAM_DOMAIN and ACCESS_AUD are set)"
