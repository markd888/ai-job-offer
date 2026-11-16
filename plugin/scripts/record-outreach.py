#!/usr/bin/env python3
"""Log contact with a person in userdata/people/<slug>.md (/outreach).

Appends one `## Log` line, creates the person file on first contact, links the
role the contact is about, and updates last_contact. Run it only after the
user says a message went out (or tells you one came in): it is the record,
not the draft.

Usage:
  python3 -I record-outreach.py --userdata ./userdata --name "Dana Okafor"
      --direction sent --kind referral-ask --text "Asked for a referral to Senior PM, Lending"
      [--channel linkedin] [--company Wagestream] [--relation former-colleague]
      [--role Wagestream] [--date YYYY-MM-DD]

--role is a role folder relative to userdata/companies/ (Wagestream, or
Plaid/senior-pm-consumer-credit); it must exist. --relation is required only
when the person is new. Kinds, channels and relations are listed in
plugin/schemas/person.md.schema.md.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from datetime import date
from pathlib import Path


def load(name: str):
    path = Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


people = load("people")
metafile = load("metafile")


def record(userdata: Path, *, name: str, direction: str, kind: str, text: str, day: str,
           channel: str = "", company: str = "", relation: str = "", role: str = "",
           new: bool = False) -> tuple[Path, bool]:
    """Write one log line; returns (person file, created). Raises SystemExit on bad input."""
    if role and not ((userdata / "companies" / role / "meta.md").is_file()):
        raise SystemExit(f"No role folder companies/{role}/ with a meta.md")
    path = None if new else people.find_person(userdata, name, company)
    if path is not None and company:
        known = people.frontmatter(path.read_text()).get("company", "")
        if known and known.lower() != company.lower():
            raise SystemExit(f"people/{path.name} is {name} at {known}, not {company}. "
                             "If this is someone else, pass --new; if they moved, edit their company first.")
    created = path is None
    if created:
        if not relation:
            raise SystemExit(f"{name} is new — pass --relation ({', '.join(people.RELATIONS)})")
        path = people.new_person_path(userdata, name, company)
        path.parent.mkdir(parents=True, exist_ok=True)
        text_now = people.render_person(name.strip(), company, relation, channel, [role] if role else [])
    else:
        text_now = path.read_text()
        if role and role not in people.roles_of(people.frontmatter(text_now)):
            text_now = people.set_roles(text_now, people.roles_of(people.frontmatter(text_now)) + [role])
    text_now = metafile.set_fields(text_now, {"last_contact": metafile.later(
        people.frontmatter(text_now).get("last_contact", ""), day)})
    text_now = people.add_log_line(text_now, people.format_log(day, direction, kind, channel, text))
    path.write_text(text_now)
    return path, created


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--userdata", type=Path, default=Path("userdata"))
    ap.add_argument("--name", required=True)
    ap.add_argument("--direction", required=True, choices=people.DIRECTIONS)
    ap.add_argument("--kind", required=True, choices=people.KINDS)
    ap.add_argument("--text", required=True, help="one line: what was asked or said")
    ap.add_argument("--channel", default="", choices=("",) + people.CHANNELS)
    ap.add_argument("--company", default="")
    ap.add_argument("--relation", default="", choices=("",) + people.RELATIONS)
    ap.add_argument("--role", default="", help="role folder under companies/, e.g. Plaid/senior-pm-consumer-credit")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--new", action="store_true", help="a different person who shares a name with someone on file")
    a = ap.parse_args()
    try:
        date.fromisoformat(a.date)
    except ValueError:
        sys.exit(f"--date {a.date!r} is not YYYY-MM-DD")

    path, created = record(a.userdata.resolve(), name=a.name, direction=a.direction, kind=a.kind,
                           text=a.text, day=a.date, channel=a.channel, company=a.company,
                           relation=a.relation, role=a.role, new=a.new)
    print(("Added " if created else "Updated ") + f"{path.name}: {a.date} {a.direction} {a.kind}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
