"""People records (userdata/people/*.md): record-outreach.py, the shared
people.py rules, the validator's person.* rules, and /sent's referral link.
"""
from __future__ import annotations

import shutil
import sys
from datetime import date

import pytest

from scripts_helpers import ROOT, load, run, write_meta

sys.path.insert(0, str(ROOT / "scripts"))
from validate_userdata import parse_frontmatter, validate_tree  # noqa: E402

people = load("people.py")
SNAPSHOT = ROOT / "tests" / "snapshots" / "maya-active"


@pytest.fixture
def userdata(tmp_path):
    write_meta(tmp_path / "companies" / "Wagestream", company="Wagestream", position="Senior PM, Lending",
               status="to_apply", link="https://jobs.example.com/wagestream")
    return tmp_path


def outreach(userdata, *args):
    return run("record-outreach.py", "--userdata", userdata, *args)


def rules(userdata):
    return sorted(f.rule for f in validate_tree(userdata))


# ----- record-outreach.py ----------------------------------------------------


def test_first_contact_creates_a_valid_person_file(userdata):
    res = outreach(userdata, "--name", "Dana Okafor", "--direction", "sent", "--kind", "referral-ask",
                   "--channel", "linkedin", "--text", "Asked for a referral to  Senior PM, Lending",
                   "--company", "Wagestream", "--relation", "former-colleague", "--role", "Wagestream",
                   "--date", "2026-11-16")
    assert res.returncode == 0, res.stderr
    path = userdata / "people" / "dana-okafor.md"
    text = path.read_text()
    fm = parse_frontmatter(text)
    assert fm["name"] == "Dana Okafor" and fm["relation"] == "former-colleague"
    assert fm["last_contact"] == "2026-11-16"
    assert people.roles_of(people.frontmatter(text)) == ["Wagestream"]
    assert text.rstrip().endswith(
        "- 2026-11-16 sent referral-ask (linkedin): Asked for a referral to Senior PM, Lending")
    assert rules(userdata) == []


def test_new_person_needs_a_relation(userdata):
    res = outreach(userdata, "--name", "Sam", "--direction", "sent", "--kind", "reach-out", "--text", "Hi")
    assert res.returncode != 0 and "relation" in res.stderr
    assert not (userdata / "people").exists()


def test_existing_person_is_found_by_name_and_appended_to(userdata):
    base = ("--name", "Dana Okafor", "--channel", "linkedin")
    outreach(userdata, *base, "--direction", "sent", "--kind", "reach-out", "--text", "Catch-up?",
             "--relation", "former-colleague", "--date", "2026-11-10")
    res = outreach(userdata, "--name", "dana okafor", "--direction", "received", "--kind", "reply",
                   "--channel", "linkedin", "--text", "Sure", "--role", "Wagestream", "--date", "2026-11-12")
    assert res.returncode == 0, res.stderr
    files = list((userdata / "people").glob("*.md"))
    assert [f.name for f in files] == ["dana-okafor.md"]
    entries, bad = people.parse_log(files[0].read_text())
    assert [(e["date"], e["direction"], e["kind"]) for e in entries] == [
        ("2026-11-10", "sent", "reach-out"), ("2026-11-12", "received", "reply")]
    assert bad == []
    assert people.roles_of(people.frontmatter(files[0].read_text())) == ["Wagestream"]


def test_last_contact_never_moves_back(userdata):
    common = ("--name", "Dana", "--relation", "friend", "--direction", "sent", "--kind", "reach-out", "--text", "x")
    outreach(userdata, *common, "--date", "2026-11-12")
    outreach(userdata, *common, "--date", "2026-11-01")
    assert parse_frontmatter((userdata / "people" / "dana.md").read_text())["last_contact"] == "2026-11-12"


def test_unknown_role_or_kind_is_refused(userdata):
    common = ("--name", "Dana", "--relation", "friend", "--direction", "sent", "--text", "x")
    assert outreach(userdata, *common, "--kind", "reach-out", "--role", "Nowhere").returncode != 0
    assert outreach(userdata, *common, "--kind", "coffee").returncode != 0
    assert not (userdata / "people").exists()


def test_same_name_at_another_company_needs_new(userdata):
    outreach(userdata, "--name", "Anna", "--company", "SeedX", "--relation", "referrer",
             "--direction", "received", "--kind", "referral", "--text", "x")
    clash = outreach(userdata, "--name", "Anna", "--company", "Klarna", "--relation", "recruiter",
                     "--direction", "received", "--kind", "reply", "--text", "y")
    assert clash.returncode != 0 and "--new" in clash.stderr
    ok = outreach(userdata, "--name", "Anna", "--company", "Klarna", "--relation", "recruiter",
                  "--direction", "received", "--kind", "reply", "--text", "y", "--new")
    assert ok.returncode == 0, ok.stderr
    assert sorted(p.name for p in (userdata / "people").glob("*.md")) == ["anna-klarna.md", "anna.md"]
    # With two Annas on file, the company picks the right one.
    assert people.find_person(userdata, "Anna", "Klarna").name == "anna-klarna.md"
    assert rules(userdata) == []


# ----- counting --------------------------------------------------------------


def test_weekly_outreach_counts_sent_outreach_kinds_only(userdata):
    for day, direction, kind in [("2026-11-16", "sent", "referral-ask"), ("2026-11-17", "sent", "follow-up"),
                                 ("2026-11-17", "sent", "thank-you"), ("2026-11-17", "received", "reply"),
                                 ("2026-11-15", "sent", "reach-out")]:  # Sunday before: out of the week
        outreach(userdata, "--name", "Dana", "--relation", "friend", "--direction", direction,
                 "--kind", kind, "--text", "x", "--date", day)
    assert people.count_outreach(userdata, date(2026, 11, 18)) == 2


def test_slugify_keeps_other_scripts_and_folds_accents():
    assert people.slugify("José Núñez") == "jose-nunez"
    assert people.slugify("Мария Иванова") == "мария-иванова"


# ----- validator -------------------------------------------------------------


def test_validator_person_rules(tmp_path):
    d = tmp_path / "people"
    d.mkdir()
    (d / "x.md").write_text(
        "---\nname: X\nrelation: boss\nchannel: fax\nroles: [\"Ghost\"]\n---\n\n# X\n\n## Log\n"
        "- 2026-11-16 messaged X about a role\n")
    (d / "y.md").write_text("---\nrelation: friend\n---\n\n# Y\n")
    assert rules(tmp_path) == ["person.channel-enum", "person.log-format", "person.log-format",
                               "person.relation-enum", "person.required", "person.role-link"]


def test_maya_snapshot_people_are_clean_and_linked():
    files = people.person_files(SNAPSHOT)
    assert {p.name for p in files} >= {"dana-okafor.md", "anna.md", "tom.md"}
    assert not [f for f in validate_tree(SNAPSHOT) if f.rule.startswith("person.")]
    dana = people.find_person(SNAPSHOT, "Dana Okafor")
    assert people.roles_of(people.frontmatter(dana.read_text())) == ["Wagestream"]


# ----- /sent --referred-by ---------------------------------------------------


def test_sent_with_a_referrer_logs_the_referral_on_their_file(tmp_path):
    shutil.copytree(SNAPSHOT, tmp_path / "u")
    u = tmp_path / "u"
    res = run("record-sent.py", u / "companies" / "Wagestream", "--channel", "referral",
              "--referred-by", "Dana Okafor", "--date", "2026-08-05")
    assert res.returncode == 0, res.stderr
    assert "people/dana-okafor.md" in res.stdout
    text = (u / "people" / "dana-okafor.md").read_text()
    assert text.rstrip().endswith(
        "- 2026-08-05 received referral: Referred me for Senior PM, Consumer Lending at Wagestream.")
    assert parse_frontmatter((u / "companies" / "Wagestream" / "meta.md").read_text())["referred_by"] == "[[Dana Okafor]]"
    assert not [f for f in validate_tree(u) if f.rule.startswith("person.")]


def test_sent_with_an_unknown_referrer_creates_them(userdata):
    res = run("record-sent.py", userdata / "companies" / "Wagestream", "--channel", "referral",
              "--referred-by", "Lee Park", "--date", "2026-11-16")
    assert res.returncode == 0, res.stderr
    fm = parse_frontmatter((userdata / "people" / "lee-park.md").read_text())
    assert fm["relation"] == "referrer" and fm["company"] == "Wagestream"
    assert rules(userdata) == []


def test_sent_referrer_from_another_company_is_matched_by_name(tmp_path):
    """Anna works at SeedX and referred Maya to Lendable: no clash, no new file."""
    shutil.copytree(SNAPSHOT, tmp_path / "u")
    u = tmp_path / "u"
    res = run("record-sent.py", u / "companies" / "Zopa", "--channel", "referral",
              "--referred-by", "Anna", "--date", "2026-08-05")
    assert res.returncode == 0, res.stderr
    assert "people/anna.md" in res.stdout
    text = (u / "people" / "anna.md").read_text()
    assert parse_frontmatter(text)["company"] == "SeedX"
    assert people.roles_of(people.frontmatter(text)) == ["Lendable", "Zopa"]
    assert sorted(p.name for p in (u / "people").glob("anna*.md")) == ["anna.md"]

