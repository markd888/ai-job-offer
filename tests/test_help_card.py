"""The help card and the recommended flow must know every skill the plugin ships.

Written after /ats-check and /follow-up shipped in 0.7 without either: help
never listed them and no end-of-skill nudge could suggest them.
"""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugin"
HELP = (PLUGIN / "skills" / "help" / "help.md").read_text()
FLOW = (PLUGIN / "references" / "recommended-flow.md").read_text()
README = (PLUGIN / "README.md").read_text()


def skills() -> list[str]:
    out = []
    for d in sorted((PLUGIN / "skills").iterdir()):
        skill = d / "SKILL.md"
        if not skill.is_file():
            continue
        desc = next((l for l in skill.read_text().splitlines() if l.startswith("description:")), "")
        if desc.removeprefix("description:").strip().startswith("Internal"):
            continue  # maintainer-only, filtered from /help
        out.append(d.name)
    return out


@pytest.mark.parametrize("name", skills())
def test_help_card_lists_every_skill(name):
    assert f"`/{name}" in HELP, f"/{name} missing from skills/help/help.md"


@pytest.mark.parametrize("name", skills())
def test_plugin_readme_lists_every_skill(name):
    assert f"`/job-offer:{name}" in README, f"/job-offer:{name} missing from plugin/README.md"


def test_skill_counts_match():
    n = len(skills())
    assert f"## Skills ({n})" in HELP
    assert f"## The workflow — {n} skills" in README
    assert f"all {n} skills" in (PLUGIN / "skills" / "help" / "SKILL.md").read_text()


@pytest.mark.parametrize("name", ["apply", "ats-check", "sent", "follow-up", "interview-prep", "interview-analysis"])
def test_recommended_flow_covers_the_application_path(name):
    assert name in FLOW, f"{name} missing from references/recommended-flow.md"


def test_recommended_flow_uses_real_status_values():
    for wrong in ("status: interview`", "status: to apply`"):
        assert wrong not in FLOW
