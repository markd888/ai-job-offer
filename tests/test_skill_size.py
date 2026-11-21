"""The always-loaded skills stay small: /today and /setup are read on every run,
so rarely-hit detail lives in plugin/references/ and is loaded on demand.

Every reference a skill points at must exist, and every today-*/setup-*
reference must be pointed at by its skill — a split that drops a pointer
silently drops the behaviour.
"""
import re

import pytest

from scripts_helpers import ROOT

SKILLS = ROOT / "plugin" / "skills"
REFS = ROOT / "plugin" / "references"
LIMIT = 20 * 1024


@pytest.mark.parametrize("skill", ["today", "setup", "evaluate-position"])
def test_skill_is_at_most_20_kb(skill):
    size = len((SKILLS / skill / "SKILL.md").read_bytes())
    assert size <= LIMIT, f"{skill}/SKILL.md is {size} bytes; move rarely-used sections into references/"


@pytest.mark.parametrize("skill", ["today", "setup", "evaluate-position"])
def test_every_split_reference_is_loaded_by_its_skill(skill):
    text = (SKILLS / skill / "SKILL.md").read_text()
    pointed = set(re.findall(rf"references/({skill}-[a-z-]+\.md)", text))
    on_disk = {p.name for p in REFS.glob(f"{skill}-*.md")}
    assert on_disk, f"no {skill}-*.md references found"
    assert pointed == on_disk, f"unreferenced: {on_disk - pointed}; missing: {pointed - on_disk}"


def test_job_search_uses_the_same_scoring_procedure():
    text = (SKILLS / "job-search" / "SKILL.md").read_text()
    assert "references/evaluate-position-scoring.md" in text and "score.py record" in text
    assert "light tier estimate" not in text and "tier_weights" not in text
