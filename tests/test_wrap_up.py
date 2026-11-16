"""/wrap-up (plugin/scripts/wrap-up.py): closing a search after an accepted
offer, and reopening it. Every command is a write the skill runs only after
the user's yes, so the tests check exactly what each one changes — and that
it changes nothing else."""
from __future__ import annotations

import shutil
import sys

import pytest

from scripts_helpers import ROOT, run

sys.path.insert(0, str(ROOT / "scripts"))
from validate_userdata import parse_frontmatter, validate_tree  # noqa: E402

SNAPSHOT = ROOT / "tests" / "snapshots" / "maya-active"


@pytest.fixture
def maya(tmp_path):
    shutil.copytree(SNAPSHOT, tmp_path / "u")
    return tmp_path / "u"


def wrap(u, *args):
    return run("wrap-up.py", args[0], "--userdata", u, *args[1:])


def fm(u, role):
    return parse_frontmatter((u / "companies" / role / "meta.md").read_text())


def test_open_lists_threads_to_close_but_not_the_accepted_offer(maya):
    res = wrap(maya, "open", "--offer", "Lendable")
    assert res.returncode == 0, res.stderr
    withdraw, rest = res.stdout.split("## Drop (never applied)")
    drop, thank = rest.split("## Thank")
    assert "Lendable" not in withdraw
    assert "Plaid/senior-pm-consumer-credit" in withdraw and "next: CPO round" in withdraw
    assert "| applied" in withdraw and "Mercury" not in withdraw  # rejected roles are already closed
    assert "Wagestream" in drop and "Zopa" in drop
    assert "Anna (anna.md) | referral" in thank
    assert "Tom (tom.md) | linked to the accepted role | already thanked once" in thank
    # Dana only reached out; she didn't refer or introduce anyone.
    assert "Dana" not in thank


def test_open_is_read_only(maya):
    before = {p: p.read_bytes() for p in maya.rglob("*.md")}
    wrap(maya, "open", "--offer", "Lendable")
    assert before == {p: p.read_bytes() for p in maya.rglob("*.md")}


def test_withdraw_marks_only_the_named_roles(maya):
    res = wrap(maya, "withdraw", "--role", "Brex", "--role", "Zopa", "--date", "2026-08-10")
    assert res.returncode == 0, res.stderr
    for role in ("Brex", "Zopa"):
        f = fm(maya, role)
        assert f["status"] == "not_interested" and f["date_not_interested"] == "2026-08-10"
    text = (maya / "companies" / "Brex" / "meta.md").read_text()
    assert text.rstrip().endswith("- 2026-08-10: status → not_interested (withdrew — accepted another offer)")
    assert (maya / "companies" / "Zopa" / "meta.md").read_text().rstrip().endswith("(dropped — search closed)")
    assert fm(maya, "Cleo")["status"] == "interviewing"
    assert not [f for f in validate_tree(maya) if f.rule.startswith("meta.")]


def test_withdraw_refuses_closed_roles_and_changes_nothing(maya):
    before = (maya / "companies" / "Brex" / "meta.md").read_text()
    res = wrap(maya, "withdraw", "--role", "Brex", "--role", "Mercury")
    assert res.returncode != 0 and "Mercury is 'rejected'" in res.stderr
    assert (maya / "companies" / "Brex" / "meta.md").read_text() == before


def test_facts_quote_the_user_numbers(maya):
    res = wrap(maya, "facts", "--offer", "Lendable", "--date", "2026-08-10")
    assert res.returncode == 0, res.stderr
    out = res.stdout
    assert "Accepted: Lendable — Head of Product, Consumer Credit (applied 2026-06-28, channel referral, referred by Anna)" in out
    assert "First application 2026-06-03; offer 2026-07-31; closed 2026-08-10 — 58 days from first application to offer" in out
    assert "- Funnel: 13 applied → 5 screening → 1 interview → 1 final → 1 offer." in out
    assert "- company-site: 7 applied → 0 screening (0%)" in out
    assert "- referral: 1 applied → 1 screening, 1 interview, 1 final, 1 offer — under 5 applications" in out
    assert '"Strong work, going with a candidate with more direct payments experience."' in out
    assert "1 referral(s) or intro(s) received" in out


def test_close_sets_dormant_and_reopen_undoes_it(maya):
    res = wrap(maya, "close", "--offer", "Lendable", "--market-check", "quarterly", "--date", "2026-08-10")
    assert res.returncode == 0, res.stderr
    s = parse_frontmatter((maya / "strategy.md").read_text())
    assert (s["search_state"], s["search_closed"], s["market_check"]) == ("dormant", "2026-08-10", "quarterly")
    assert s["accepted_offer"] == "Lendable — Head of Product, Consumer Credit"
    assert fm(maya, "Lendable")["status"] == "offer"
    assert (maya / "companies" / "Lendable" / "meta.md").read_text().rstrip().endswith(
        "- 2026-08-10: offer accepted; search closed")
    assert not [f for f in validate_tree(maya) if f.rule.startswith("strategy.")]

    res = wrap(maya, "reopen", "--date", "2026-12-01")
    assert res.returncode == 0, res.stderr
    s = parse_frontmatter((maya / "strategy.md").read_text())
    assert s["search_state"] == "active" and s["search_reopened"] == "2026-12-01"
    assert wrap(maya, "reopen").returncode != 0  # already active


def test_close_needs_a_recorded_offer(maya):
    res = wrap(maya, "close", "--offer", "Plaid/senior-pm-consumer-credit")
    assert res.returncode != 0 and "not 'offer'" in res.stderr
    assert "search_state" not in (maya / "strategy.md").read_text()


def test_validator_rejects_a_bad_search_state(maya):
    p = maya / "strategy.md"
    p.write_text(p.read_text().replace("target_offer_date:", "search_state: paused\nsearch_closed: soon\ntarget_offer_date:", 1))
    rules = sorted(f.rule for f in validate_tree(maya) if f.rule.startswith("strategy."))
    assert rules == ["strategy.date-format", "strategy.search-state-enum"]


def test_today_and_job_search_honour_a_closed_search():
    today = (ROOT / "plugin" / "skills" / "today" / "SKILL.md").read_text()
    search = (ROOT / "plugin" / "skills" / "job-search" / "SKILL.md").read_text()
    assert today.index("## Closed search (check first)") < today.index("## Input phase")
    assert "search_state: dormant" in search and "--market-check" in search
