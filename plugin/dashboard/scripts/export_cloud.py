"""Export userdata/ into the static bundle the Cloudflare Worker serves.

Writes the built frontend (dist/) plus the API payloads the live server would
return, so the deployed dashboard is a read-only snapshot of the role cards:

    <out>/                                  copy of dist/
    <out>/data/state.json                   /api/state payload
    <out>/data/positions/<sha1>.json        {"artifacts": ..., "notes": {"markdown": ...}}

Per-position files are keyed by sha1(folder_path) because folder names carry
spaces, accents and brackets; worker/index.js computes the same hash.

Usage:
    python3 scripts/export_cloud.py --userdata ../userdata --out .cloud
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent))

from serve import (  # noqa: E402
    collect_artifacts,
    collect_companies,
    compute_weekly_progress,
    funnel,
    latest_brief,
    read_strategy,
)


def position_key(folder_path: str) -> str:
    return hashlib.sha1(folder_path.encode("utf-8")).hexdigest()


def export(userdata_root: Path, dist_dir: Path, out_root: Path) -> dict[str, int]:
    if not (userdata_root / "companies").is_dir():
        raise FileNotFoundError(f"no companies/ under {userdata_root}")
    if not (dist_dir / "index.html").is_file():
        raise FileNotFoundError(f"no built frontend in {dist_dir}; run npm run build first")

    if out_root.exists():
        shutil.rmtree(out_root)
    shutil.copytree(dist_dir, out_root, ignore=shutil.ignore_patterns("*.mp4"))
    positions_dir = out_root / "data" / "positions"
    positions_dir.mkdir(parents=True)

    companies = collect_companies(userdata_root)
    state = {
        "companies": companies,
        "strategy": read_strategy(userdata_root),
        "weekly_progress": compute_weekly_progress(userdata_root, companies),
        "funnel_by_channel": funnel.funnel_by_channel(companies),
        "latest_brief": latest_brief(userdata_root),
        # The real on-disk path means nothing in the cloud copy.
        "userdata_root": "cloud snapshot " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
    }
    (out_root / "data" / "state.json").write_text(json.dumps(state, ensure_ascii=False) + "\n", encoding="utf-8")

    for record in companies:
        meta_dir = userdata_root / "companies" / record["folder_path"]
        notes_path = meta_dir / "notes.md"
        payload = {
            "artifacts": collect_artifacts(meta_dir),
            "notes": {"markdown": notes_path.read_text(encoding="utf-8") if notes_path.is_file() else ""},
        }
        (positions_dir / f"{position_key(record['folder_path'])}.json").write_text(
            json.dumps(payload, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    return {"companies": len(companies)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="export_cloud")
    parser.add_argument("--userdata", required=True, type=Path)
    parser.add_argument("--dist", default=_SCRIPT_DIR.parent / "dist", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    counts = export(args.userdata.resolve(), args.dist.resolve(), args.out.resolve())
    print(f"exported {counts['companies']} positions to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
