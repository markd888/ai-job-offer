---
name: ats-check
description: This skill should be used when the user asks to "/ats-check <Company>", "check my CV for ATS", "will the ATS read my CV", "keyword coverage for <Company>", and automatically after a tailored CV PDF is built for a role (`/job-offer:apply` runs it). Extracts the PDF's text layer the way an applicant tracking system does and checks page count, contact details, glyphs, section order, extraction fidelity and the posting's keyword coverage. Writes ats-check-<YYYY-MM-DD>.md into the role folder. Never adds a keyword the master CV or profile doesn't support.
---

# /ats-check — read the CV the way an ATS does

Voice follows `${CLAUDE_PLUGIN_ROOT}/TONE.md`.

An ATS ranks the PDF's embedded text, not the page you see. Most rejections come at the application stage, so a CV that extracts badly loses before a person reads it.

## Inputs

- Role folder: `userdata/companies/<Co>/` or `userdata/companies/<Co>/<role-slug>/` — the one holding `meta.md`. If the company has several roles and the user didn't say which, ask once.
- In that folder: the newest `*CV*.pdf` (or a `.docx` CV the user brought — the checker reads it too and lists what it can't see) and `cv-*.md`, `research-brief.md`, and the posting (`submitted-*/posting.md` if archived; otherwise fetch the `link:` from `meta.md`, or ask the user to paste it).

## Steps

1. **Pick 10–20 keywords from the posting.** Hard skills, domain terms and tools the posting repeats or lists as requirements (e.g. `payment orchestration`, `PSP integrations`, `reconciliation`, `SQL`, `API`). Use the posting's own wording. Skip soft skills and boilerplate.
2. **Run the check:**

   ```sh
   python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/ats-check.py" <folder>/<CV>.pdf --md <folder>/<cv-md> \
     --keywords "<comma-separated keywords>" --jd <posting file if saved> \
     --out <folder>/ats-check-<YYYY-MM-DD>.md
   ```

   Use a Python with `pypdf` (a workspace venv such as `.claude/.venv/bin/python` if there is one), or install poppler's `pdftotext`.
3. **Fix hard failures** before the CV is shown or sent. Exit code 1 means at least one:
   - `pages` — over one page: trim by relevance to this posting, not by age.
   - `contacts` — email or phone missing from the text layer: the header is an image or icon font; rebuild it as plain text. The expected phone is `phone:` in `userdata/profile.md`.
   - `glyphs` — ligatures (ﬁ, ﬂ), `(cid:N)` codes or icon glyphs: rebuild with `cv-build.py` (reportlab + Carlito writes plain characters). CVs printed from a browser are the usual cause.
   - `order` — sections extract out of order: a multi-column layout; go single-column.
   - `fidelity` < 95% — text drawn as shapes or images; rebuild.

   Rebuild with `python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/cv-build.py" <cv-md> <out.pdf> 9 1.15`, then re-run the check.
4. **Keyword gaps.** For each missing keyword, look in `userdata/cv.md` and `userdata/profile.md`. If the experience is there, propose the exact line change in the posting's wording and apply it after the user says yes. If it isn't, it stays a gap — say so in one line. Never add a keyword the record doesn't support.

## Output

One short block in chat:

> ATS check for <Company>: passes / fails on <checks>. Keywords <n>/<m> covered; missing <list> — <k> supported by your CV (proposed edits below), <j> real gaps.

Then the proposed line edits, if any. Don't name files or paths in chat.

## Never

- Never stuffs keywords, hides text, or adds white-on-white terms.
- Never edits the master CV; edits go to the role's tailored `cv-*.md`, then the PDF is rebuilt from it.
- Never changes `meta.md`.
