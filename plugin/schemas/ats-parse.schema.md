# ATS parsing simulation — structure and fidelity statuses

Owner: `plugin/scripts/ats_parse.py` (loaded by `ats-check.py`). If this file and
the script disagree, the script wins.

It shows what a parser could build from the CV's **extracted text**. It is a
simulation with bounded, deterministic heuristics, not any vendor's parser, and
it never predicts a ranking or a hiring decision.

## Parsed structure

Every field may be missing. A field is:

```json
{"value": "Paycorp", "source_text": "SENIOR PM | Paycorp — Lisbon", "confidence": "high", "warnings": []}
```

`value` is `null` when nothing was found; then `confidence` is `null` too.
`source_text` is the extracted span the value came from. Nothing is filled
that isn't in the text.

```json
{
  "document":  {"format": "pdf|docx", "page_count": 1, "extraction_engine": "pypdf|pdftotext|docx-xml"},
  "candidate": {"name": F, "email": F, "phone": F, "location": F, "linkedin": F},
  "summary":   F,
  "sections":  ["WORK EXPERIENCE", "EDUCATION"],
  "experience": [{"company": F, "job_title": F, "location": F, "start_date": F, "end_date": F,
                  "description": ["…"], "skills": []}],
  "education": [{"degree": F, "institution": F, "dates": F}],
  "skills": [F], "certifications": [F], "languages": [F],
  "parsing_warnings": ["1 employment entry without dates"]
}
```

## How it reads

- **Sections**: a line of up to five words that matches a known heading kind:
  summary, experience, education, skills, certifications, languages or
  projects. English and Russian names are recognised.
- **Contacts**: name from the first line before any section, if it has 2–4
  words and no digits. Email, phone and LinkedIn by pattern. Location is the
  contact-line segment that isn't an email, phone or URL.
- **Employment**, inside the experience section:
  - an entry starts at a role line `Title | Company — Place` (what
    `cv-build.py` emits) or `Title at Company`;
  - dates come from a range on that line or on a short line after it:
    `2024 – Present`, `Mar 2020 – Dec 2023`, `01/2020 – 12/2023`, and the
    Russian forms;
  - dates without a role line start an entry whose company is missing, with a
    warning;
  - wrapped lines are rejoined into description paragraphs.
- **Skills / languages / certifications**: items split on `, ; | •`. A
  `Label: …` line opens a group, and continuation lines join it. A
  `Languages:` group inside skills is read as languages.

## Fidelity against the CV markdown (`--md`)

One row per field the markdown defines:
- name, email, phone, location, LinkedIn;
- each `##` heading;
- each employment entry's title and dates;
- each education entry;
- skills, languages and certifications as sets.

| Status | Meaning |
|---|---|
| `EXTRACTED` | The parse matches the markdown. For sets, at least 90% of items match. |
| `MISSING` | In the CV, but neither parsed nor anywhere in the extracted text. |
| `AMBIGUOUS` | The text is there, but it wasn't parsed into the field (e.g. a role line split by a two-column layout). |
| `CONFLICTING` | Parsed, but different from the CV. |
| `NOT_IN_SOURCE` | The CV itself doesn't have it. This is not an extraction problem. |

None of these statuses change `ats-check.py`'s exit code.
