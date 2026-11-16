# Schema — `userdata/people/<slug>.md`

One file per person the user is in touch with about the search: a former colleague who could refer them, a recruiter, a hiring manager, someone met at an event. Written by `/outreach` and `/sent` through `scripts/record-outreach.py`; read by `/outreach`, `/today` and the dashboard, which count weekly outreach from the `## Log` lines instead of guessing from journal wording.

Checked by `scripts/validate_userdata.py` (rules `person.required`, `person.relation-enum`, `person.channel-enum`, `person.role-link`, `person.log-format`). The enums and the log-line pattern are defined once, in `plugin/scripts/people.py`.

## File name

`<slug>.md`, where the slug is the name in lowercase with runs of other characters turned into `-` (`Dana Okafor` → `dana-okafor.md`). A second person with the same name gets the company appended (`anna-seedx.md`). Skills find people by the `name` field, not the file name; `referred_by: "[[Dana Okafor]]"` in a role's meta.md points at the person whose `name` is `Dana Okafor`.

## Frontmatter

Required:

- **`name`** — as the user writes it.
- **`relation`** — how the user knows them. Enum: `former-colleague`, `friend`, `recruiter`, `hiring-manager`, `interviewer`, `referrer`, `peer`, `met-at-event`, `other`.

Optional:

- **`company`** — where they work now.
- **`title`** — their role, if known.
- **`channel`** — where the conversation lives. Enum: `linkedin`, `email`, `telegram`, `whatsapp`, `phone`, `in-person`, `other`.
- **`roles`** — role folders this person is connected to, relative to `userdata/companies/`: `roles: ["Wagestream", "Plaid/senior-pm-consumer-credit"]`. Each must exist (`person.role-link`).
- **`last_contact`** — date of the latest log line in either direction. ISO 8601. Written by `record-outreach.py`.

## Body

Free text under the `# <Name>` heading: how the user knows them, what they work on. Only facts the user stated — `/outreach` drafts from this, so nothing here may be invented.

## `## Log`

One line per contact, oldest first, in exactly this shape:

```
- <YYYY-MM-DD> <sent|received> <kind>[ (<channel>)]: <one line>
```

```
- 2026-07-20 sent reach-out (linkedin): Congratulated her on the move; asked for a catch-up.
- 2026-07-22 received reply (linkedin): Happy to talk; the lending team is hiring.
- 2026-08-04 sent referral-ask (linkedin): Asked her to refer me for Senior PM, Consumer Lending.
```

Kinds: `reach-out`, `referral-ask`, `intro-ask`, `follow-up`, `thank-you`, `feedback-ask`, `update` (the user's), `reply`, `referral`, `intro`, `feedback` (theirs), `other`. A line that doesn't match is a `person.log-format` finding and isn't counted.

**Weekly outreach** (`weekly_targets.warm_outreach`) = `sent` lines of kind `reach-out`, `referral-ask`, `intro-ask` or `follow-up` dated Monday of this week through today. Thank-yous, updates and feedback asks are contact but not outreach.
