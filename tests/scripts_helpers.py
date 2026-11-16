"""Shared helpers for the tests of plugin/scripts/*.py.

The scripts have hyphenated names (they're invoked as CLIs by the skills), so
they're loaded by path rather than imported, and most tests drive them through
subprocess exactly the way a skill does.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "plugin" / "scripts"


def run(script: str, *args: str | Path, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run plugin/scripts/<script> with -I, as the skills do."""
    return subprocess.run(
        [sys.executable, "-I", str(SCRIPTS / script), *map(str, args)],
        capture_output=True, text=True, cwd=cwd,
    )


def load(script: str) -> ModuleType:
    """Load plugin/scripts/<script> as a module without running main()."""
    name = script.removesuffix(".py").replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_meta(folder: Path, **fields: str | int) -> Path:
    """Write a meta.md with the given frontmatter fields and a History block."""
    folder.mkdir(parents=True, exist_ok=True)
    lines = ["---", *(f"{k}: {v}" for k, v in fields.items()), "---", "", "## History", "- 2026-01-01: created"]
    path = folder / "meta.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
