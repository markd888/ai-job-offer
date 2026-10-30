---
name: setup
description: This skill should be used when the user asks for "start", "/setup", "set up the plugin", "first-time setup", "install job-offer", "configure my profile", "create my profile", or wants to onboard onto job-offer for the first time (or re-run onboarding to update a field). Conducts a nine-step conversational install that pre-fills answers from the user's CV where one is available. Writes userdata/profile.md, a placeholder userdata/strategy.md, an empty userdata/journal.md, three .gitkeep files, and a CLAUDE.md at the workspace root resolved from the plugin template.
---

# /setup — first-run install and re-configure

Onboard the user onto job-offer by filling in `userdata/profile.md` and scaffolding the rest of the userdata tree. Idempotent — safe to re-run.

**Voice:** every prompt and message in this skill follows the plugin's tone-of-voice + low-effort-first guidelines in `${CLAUDE_PLUGIN_ROOT}/TONE.md`. `TONE.md` governs; the quoted lines below are examples of what a step should get at and roughly how it should sound, not strings to recite.

The wording used to be locked — "use it verbatim, not paraphrased". That is why
this file could teach a defect: a locked example outranks the rule it breaks, and
every leak the corpus records at the confirm-a-write moment traces to one. What
must not drift is the **order** of the steps, **what** each one asks, and the
things each step is explicitly told not to do. The sentence itself is yours.

If an example and `TONE.md` disagree, `TONE.md` wins and the example is a bug —
fix it here rather than following it.

**Interaction form is not wording, and it does not unlock.** A step that says
"single-select via AskUserQuestion" gets a select; a step that says explicitly
NOT to use one stays prose. Unlocking the sentence unlocked the shape too on the
first run afterwards — geography came back as an open-ish prose question — so it
is worth stating separately. Where `AskUserQuestion` is unavailable, prose that
offers the same closed set of named choices is an acceptable substitute; an open
question is not.

**Opening line** (after Step 0, fresh install only):

> "OK, let's get you set up — nine quick steps, none of it locked in."

Do NOT wait for a confirmation. Go straight into Step 1 in the same message. The
user has already chosen to run this skill; asking "Ready?" spends one of their
turns on a decision they have made, which `TONE.md` names as an anti-pattern.

## Mode detection

Run this BEFORE asking the first question:

1. If `userdata/profile.md` exists → enter **re-run mode**: read the file, ask "keep current / update / skip" per field, never wipe existing answers.
2. If `userdata/profile.md` does NOT exist → enter **fresh-install mode**: walk all nine steps in order.
3. `--refresh` flag → re-run mode, but only re-resolve the workspace-root `CLAUDE.md` from the template using the current `profile.md` content. Skip all questions. Useful after manual edits to profile.md.

CV detection, file-format handling and the drop prompt are defined in
`${CLAUDE_PLUGIN_ROOT}/references/cv-extraction.md`. Read that file before Step 0.
Do not re-implement its rules here.

## Templates

Read these from the plugin install dir (use `${CLAUDE_PLUGIN_ROOT}` if available):

- `${CLAUDE_PLUGIN_ROOT}/templates/profile.template.md` — source for `userdata/profile.md`.
- `${CLAUDE_PLUGIN_ROOT}/templates/strategy.template.md` — source for `userdata/strategy.md`.
- `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.template.md` — source for workspace-root `CLAUDE.md`.

Do not edit these template files. Always treat them as read-only inputs.

## The nine steps

Ask one at a time. Use AskUserQuestion where a step has a clear, closed option
set (Steps 2, 3, 4, 5); otherwise plain conversational ask. Steps 7 and 8 are
deliberately NOT selects — see each step for why. Skipping is allowed on
salary (Step 6), timeline (Step 7), hard filters (Step 8), and
positioning (Step 4 option B) — see the "skipped placeholders" rule under File
writes §1 for the exact YAML form to write, except timeline, whose skipped form
(`target_offer_date: null` plus null cadence targets) is defined in File writes §2.

Each step below shows an example prompt in quotes. Write your own in that
register — one direct ask, no preamble, skip offered where the step is
skippable. Hold the step order and the substance of the ask; the phrasing is
yours.

Where a CV was found at Step 0, Steps 1-4 arrive pre-filled per
`${CLAUDE_PLUGIN_ROOT}/references/cv-extraction.md`. Where none was found, the
same steps run with nothing pre-filled — the questions are identical, the user
just types more. **There is one flow, not two.**

0. **CV intake** — runs before the opening line, straight after mode detection.

   Follow `${CLAUDE_PLUGIN_ROOT}/references/cv-extraction.md` § "Finding the CV".
   State directory: `userdata/`. Scaffold files: `userdata/companies/.gitkeep`,
   `userdata/stories/.gitkeep`, `userdata/outputs/.gitkeep` (the same three
   written in File writes §4 below — creating them here just means they already
   exist by the time §4 runs). If a readable CV is found, say one line and move
   on:

   > "Got your CV — I'll fill in what I can and you just correct me."

   If none is found and the user declines the drop, say nothing about it and go
   straight into Step 1. There is no line to print here. A run without a CV is
   the ordinary case; announcing it — "we'll do it the long way", "you just type
   more" — costs a turn and tells the user they made the worse choice.

   **If `job-sweep/profile.md` exists**, read it first. It means the user already
   ran the standalone `job-sweep` plugin, and it holds `target_titles`,
   `target_industries` and `geography` — three of the answers below. Say one line:

   > "Found your job-sweep profile — I'll carry those answers over so you don't repeat them."

   Carry the values into Steps 2, 3 and 5 as the pre-filled defaults, and confirm
   them there exactly as you would confirm CV-derived values — shown, never
   auto-accepted. A sweep profile is a stronger source than a CV inference,
   because the user already confirmed it once; it is still not a reason to skip
   the confirmation.

   Both a CV and a sweep profile may exist. The sweep profile wins for
   `target_titles`, `target_industries` and `geography` — the user confirmed those
   answers; the CV only implies them. The CV still supplies everything else.

   **If `job-sweep/seen-roles.jsonl` also exists**, carry it over so the roles
   the user already saw in `job-sweep` don't come back as `status: new` once
   `/job-search` starts reading the full ledger. Create `userdata/outputs/` if it
   doesn't exist yet, then:
   - `userdata/outputs/seen-roles.jsonl` does not exist → copy the sweep ledger
     to it verbatim.
   - `userdata/outputs/seen-roles.jsonl` already exists → append only the lines
     from the sweep ledger whose `strict_key` is not already present in it. Never
     overwrite an existing line, never duplicate one.

   Say one line: `"Also carried over your job-sweep history — already-seen roles
   won't resurface as new."`

1. **Facts** (`{{NAME}}`, `{{CITY}}`, `{{TIMEZONE}}`, `{{EMAIL}}`) — one confirmation.

   Extract per `cv-extraction.md` § "Tier 1 — facts". Present everything found as
   one line and ask once:

   > "From your CV: <Name> · <City> · <email>. All right?"

   Omit any clause whose value is absent — never render an empty slot or a
   placeholder. A correction arrives as plain text ("email's the other one,
   x@y.com"); apply it and move on. Do not re-ask the whole line.

   If the CV supplied none of the three facts, skip this confirmation line
   entirely — don't render `"From your CV: . All right?"` — and go straight to
   the individual asks below.

   **Fields the CV did not supply are asked individually, here, before moving on:**

   > "What's your name?"

   > "Where are you based? City + country works (e.g. London, UK)."

   > "What's your email?"

   With no CV at all, this step is simply those three questions in that order.

   **Timezone is derived, never asked.** Resolve `{{TIMEZONE}}` from the city the
   user just gave, falling back to the system timezone when the city is
   ambiguous. Do not print it, do not confirm it, do not offer an override.
   "London, UK" settles the question; spending a turn asking the user to confirm
   `Europe/London` hands them an IANA string to check and gets back the answer
   they already gave. Nothing downstream breaks if it is wrong, and the user can
   correct it in their profile.

   **LinkedIn is not asked at setup.** It was, and the ask could not answer the
   question it invited — "why do you need this?" — because the thing it feeds
   (outreach drafting) is several skills away and may never happen. An optional
   field whose value the user cannot judge at the moment of asking is a field
   that belongs later, at the point of use. Leave `linkedin_url:` empty; the
   skill that drafts outreach asks for it when it actually needs it.

2. **Target titles** (`{{TARGET_TITLES}}`) — multi-select.

   Derive 3-5 candidates per `cv-extraction.md` § "Tier 2 — inferences". Ask via
   AskUserQuestion with `multiSelect: true`, one option per derived title, plus
   the automatic "Other" escape for anything the user wants to add:

   > "Roles you'd take. I've pulled these from your CV — <evidence line>. Pick all that apply."

   The evidence line is the roles the inference came from, e.g. `from Lead PM at
   Monzo, Senior PM at Wise`. Show it — the user cannot judge a wrong inference
   without it.

   When the values came from `job-sweep/profile.md` rather than the CV, the
   evidence line reads `from your job-sweep profile` instead of naming CV roles.

   With no CV, ask plainly instead:

   > "What roles are you targeting? Anything from Senior PM up to Head of Product — list as many as you'd take."

   **The examples must not out-rank the user.** The old wording offered "Director
   of Product, Principal PM, Group PM, Staff PM" to everyone, which reads as a
   suggestion that those are the roles to want. Half of them are a level or two
   above a Senior PM and one is not an individual-contributor seat at all, so the
   list either flatters or discourages depending on who is reading it, and it
   anchors the answer either way. With no CV there is nothing to level off, so
   name a range rather than a ladder. Where a CV or a sweep profile IS available,
   the derived options are already level-matched and no examples are needed.

   Never auto-accept this step, even when every option came from the CV. A wrong
   target title propagates into every `/job-search` sweep and every
   `/evaluate-position` score.

3. **Target industries** (`{{TARGET_INDUSTRIES}}`) — multi-select.

   Derive 3-5 candidates per `cv-extraction.md` § "Tier 2 — inferences". Ask via
   AskUserQuestion with `multiSelect: true`:

   > "Industries. From your CV I'd guess these — <evidence line>. Pick all that apply."

   When the values came from `job-sweep/profile.md` rather than the CV, the
   evidence line reads `from your job-sweep profile` instead of naming CV roles.

   With no CV:

   > "What industries are you looking at? Fintech, healthcare, climate, enterprise SaaS — whatever fits."

   Substitute as a YAML inline list, same form as Step 2. Never append a
   formatting instruction like "Comma-separated." to either of these asks: the
   user will type a list however they type it and you will parse it either way,
   so the clause spends words telling them something they do not need to know.

4. **Positioning** (`{{POSITIONING}}` + `{{PROOF_POINTS}}` + `{{MOAT}}`) — two paths. **The default order matters**: present them in the order below. A readable CV found at Step 0 bypasses this question entirely. Writing positioning by hand is 5-10 minutes of real reflection — don't force it during onboarding when the user has a faster path.

   The CV has already been located at Step 0 per `${CLAUDE_PLUGIN_ROOT}/references/cv-extraction.md`. If a readable one was found, go straight to **Mode B (CV draft)**.

   If no readable CV exists, ask via AskUserQuestion. Two options, framed like this:

   > "Positioning next — who you are and what you're best at. Two ways to handle this:"

   - **A. Write it now** → **Mode A** (paste 1-3 sentences and walk the conversational draft).
   - **B. Skip for now** — print: *"Skipped — I'll ask again once you've seen a few roles."* Never name the `--refresh` flag to the user; it is a command they did not ask for and will not remember. Write `userdata/profile.md` with the three positioning sections empty under a `<!-- TODO: fill in via /job-offer:setup --refresh, or paste your CV at userdata/cv.md and re-run --refresh -->` comment. Onboarding finishes fast.

   ### Mode A (paste-now)

   Ask the user to paste 1-3 sentences of self-positioning. Draft a one-paragraph
   `## Positioning` from it and show it. That is the whole of Mode A: one ask,
   one draft, done.

   **Proof points and moat are NOT asked here.** Leave both sections empty, under
   the same TODO comment a skipped Step 4 writes. `/today` nudges for them later,
   once the user has seen real roles and has a reason to care what their proof
   points are.

   The old Mode A ran three asks back to back — paste your positioning, now give
   me three to five numbered wins, now tell me the rare thing you bring. Each
   produced a draft, each draft closed with the same edit-this disclaimer, and
   all of it landed inside a flow the user entered to get configured. Deep
   reflective work belongs in an on-demand career-coach conversation, which is
   `TONE.md`'s own rule; onboarding's job is to get the user to their first
   sweep. A proof point written in minute four of setup, before the user has
   seen a single job description, is also a worse proof point.

   ### Mode B (CV draft)

   Read the CV file. Draft a positioning paragraph (≤4 sentences) + 5-7 proof points (each ≤2 sentences) + a one-sentence moat candidate. Show to user. Ask them to edit / accept / discard. Never save without explicit user review.

   If the user discards, write `userdata/profile.md` with the three positioning sections empty under the same `<!-- TODO: fill in via /job-offer:setup --refresh, or paste your CV at userdata/cv.md and re-run --refresh -->` comment used by Step 4 option B — never leave the literal `{{POSITIONING}}` placeholder unresolved.

   ### Drafting tone rules (apply to BOTH Mode A and Mode B drafts)

   The goal is positioning that reads as senior, specific, and unbluffed. Senior PMs don't recognise themselves in fluffy drafts and bin them.

   **Voice — four core principles:**

   - **Casual but professional.** No stiff openers, no corporate boilerplate.
   - **Direct and short.** One idea per sentence. No padding. If a sentence runs longer than ~20 words, cut it.
   - **Honest about gaps, then reframe — never oversell.** If the CV reveals a stretch claim, surface the nuance rather than paper over it.
   - **Specific over general.** Concrete nouns beat abstract ones.

   **The "Not X — Y" reframing pattern.** Sharpen positioning by explicitly naming the lazy framing the writer is NOT making, then anchoring the specific one. Shape: `Not "<generic claim>" — <specific past-tense fact>.` Use this pattern at least once in the drafted `## Positioning` if the CV implies a stretch claim the writer would want to disown.

   **Proof point format.** Each bullet follows the shape: `**<Anchor>:** <specific work> → <specific outcome>. (<role>)`. The anchor is usually the company or product. The work is past-tense and concrete. The outcome carries the number when one exists. The role is in parentheses at the end. If a metric isn't in the CV, the bullet stays qualitative — don't invent the figure to make it land.

   **Never invent the anchor.** The anchor is a fact, not a formatting slot. Use only
   the employer or product the source actually attaches to that win — the CV in Mode
   B, the user's own words in Mode A. If the source names a company for one win and
   none for another, do NOT carry the first one across; a nearby anchor is not
   evidence. Where no anchor is stated, either drop the `**<Anchor>:**` prefix and
   lead with the work, or ask the user where it happened. Silently attributing a win
   to the wrong employer is the kind of error a candidate gets caught on in an
   interview.

   **Phrases to BAN outright:**

   - **Superlatives:** "rare", "deep", "elite", "world-class", "exceptional", "uniquely positioned", "best-in-class"
   - **Abstract adjective stacks:** any 3-noun rhythm of capability claims (pick ONE, anchored to a specific outcome instead)
   - **Clichés:** "move the needle", "drive impact", "compound", "10x", "north star", "first principles", "the metrics that actually [verb]"
   - **LinkedIn closers:** "equally at home in X, Y, Z", "passionate about", "obsessed with", "thrives in ambiguity"
   - **Present-tense capability framing:** "lets me", "allows me to", "able to" — replace with the past-tense outcome that demonstrates it
   - **Filler phrases:** "I wanted to reach out", "As you may know", "I am writing to express", "I hope this email finds you well"
   - **Formal/corporate language** generally

   **Past tense for outcomes.** "Shipped X, lifted Y by Z%" beats "drives growth through experimentation".

   **Write it as the user would say it, and never assign them a gender.** This is
   the user's own positioning — it goes in their profile and feeds their outreach.
   Keep the implied subject first-person: "Shipped the price-test framework",
   "Own growth pricing at a Series B fintech". Do NOT slip into third person about
   them ("Currently owns growth pricing", "a PM who reads her own data") — it reads
   like a recruiter's write-up rather than the user's own words, and it invents a
   pronoun. A CV states a name, never a gender. If a sentence seems to need a
   pronoun for the user, rewrite it so it doesn't: drop the subject, or use "I".
   Never use "he", "she", or a guessed honorific for the user anywhere in a draft.

   **Don't invent numbers.** If a metric isn't in the CV, don't add one. Don't round up. Don't aggregate without checking the math.

   **Don't overclaim involvement.** If the CV describes the writer's role on a project narrowly ("defined success criteria with a team", "supported the migration"), don't promote it to leadership framing ("led", "shipped end-to-end"). Use the writer's own scoping verbs.

   When showing the draft to the user, append: *"Edit anything that doesn't sound like you — drafts are starting points, not finished copy."* Always let the user rewrite before save.

   **Say it once per run, and only on the first draft you show.** Repeating the
   same sentence verbatim under consecutive drafts turns a courtesy into
   boilerplate — by the third time the user is skipping the line, which is the
   opposite of what it is for.

5. **Geography** (`{{GEOGRAPHY_MODE}}` + `{{GEOGRAPHY_DETAIL}}`) — single-select via AskUserQuestion. Ask:
   > "Where are you looking?"

   Options (in this order): `On-site in <city-from-Step1>` / `Remote` / `Both` / `Other (free text)`. The first option dynamically uses the city captured in Step 1. If the user picks "Other", capture free-text into `mode_detail` and set `mode: other`.

   When `job-sweep/profile.md` supplied `geography`, pre-select the matching
   option rather than asking cold — the user already answered this.

6. **Salary band** (`{{SALARY_BAND}}`) — single open string. Skippable. Ask:
   > "What salary band are you aiming for? Whatever shape works — '£90-110K' or '$190-230K base + equity', or skip if you'd rather not anchor a number yet."

   This is the one step that stays a free-text box. Generating bands from title
   and city would mean inventing market data the plugin has no source for, and
   anchoring a user's expectations wrongly is a worse failure than one text box.
   No validation — accept whatever currency and phrasing the user gives.

7. **Timeline** — plain ask, examples inside the sentence. Ask:

   > "When do you want to have signed? Roughly is fine — a couple of months, six months, or an actual date if you have one."

   Do NOT render this as a five-option select. The answer space here is a single
   continuous axis, and a user who knows their timeline should be able to say it
   in three words rather than map it onto someone else's buckets. Examples
   belong in the sentence; a list turns them into the only permitted answers.

   Parse whatever comes back into a concrete date:

   | What the user says | Stored `target_offer_date` |
   |---|---|
   | anything under ~2 months | today + 6 weeks |
   | ~2 to 4 months | today + 12 weeks |
   | ~4 months or more | today + 24 weeks |
   | an actual date, in any format | that date, as `YYYY-MM-DD` |
   | "not sure", "no idea", or a skip | `null` |

   The three windows land unambiguously inside one cadence bucket each in the
   derivation table below, so a rough answer loses nothing. Do not ask a
   follow-up to sharpen a rough answer into an exact one.

   Always store a concrete `YYYY-MM-DD` — never a bucket label. `/today`'s
   countdown reads that field directly.

   Skipping is allowed: set `target_offer_date: null`, skip the cadence
   derivation below, and `/today` degrades gracefully (no countdown, no progress
   section).

8. **Hard filters** (`{{HARD_FILTERS}}`) — plain ask, examples inside the sentence, skippable. Ask:

   > "Last one. Any red flags — roles you'd skip on sight, whatever else is right about them? Relocation, five-day office, contract work, that kind of thing. Or skip."

   Do NOT render this as a six-option multi-select. A checklist of generic red
   flags invents nothing, but it does frame the answer: the user scans the six,
   ticks the ones that ring true, and stops thinking. The real red flags are
   usually the ones nobody would have put on a list — "no sales-led enterprise
   B2B without a PLG angle", "nothing over eight direct reports" — and those
   arrive when the question is open. Three examples in the sentence are enough to
   show the shape of an answer.

   Take whatever the user gives, verbatim, as a list. Do not normalise their
   wording into the old canned phrasings.

   Write the selections as a YAML inline list of quoted strings:
   `["no companies under 50 people", "no five-day in-office"]`. If skipped or
   nothing selected, write `[]`. (Inline form keeps the trailing template comment
   intact, same reasoning as Step 2.)

After Step 7 (only if target date was set), silently derive cadence targets based on weeks-to-target. Compute `W = (target_offer_date − today) / 7`, then:

| W | weekly_targets.applications | weekly_targets.warm_outreach | pipeline_targets.active_interview_threads | pipeline_targets.p0_pipeline_size |
|---|---|---|---|---|
| W < 8 (under 2 mo) | 12 | 10 | 5 | 8 |
| W = 8-16 (2-4 mo) | 8 | 8 | 4 | 6 |
| W ≥ 16 (4+ mo) | 5 | 5 | 3 | 5 |

Rationale (don't surface to user unless asked): shorter timeline → higher concurrent activity needed to hit ~2 offers in hand by deadline, assuming ~30% offer rate on active interview threads and ~15% interview rate on applications.

Regardless of whether Step 7 was answered, silently auto-compose `## Headline goal` for strategy.md from profile.md frontmatter. Format:

> "Sign a `<target_titles joined by ' / '>` role at a `<target_industries joined by ', '>` company by `<target_offer_date>`. `<geography phrasing — 'Fully remote', 'London hybrid', etc.>`. Base `<salary_band>`."

Skip clauses where the source field is unset (e.g. if salary skipped, drop the base clause).

Leave `## Anti-goals` empty and `checkpoints: []` — those need deeper reflection and belong to the user's later editing or to a `career-coach` conversation.

Once all steps above are answered: proceed straight to file writes. Do NOT prompt the user about the tier rubric.

The senior-PM-default `tier_weights` + `tier_thresholds` get written into `profile.md` from the template automatically. Tier rubric terms (P0/P1/P2, role_fit, etc.) are too technical to introduce here without context — the user encounters them organically the first time `/evaluate-position` runs and shows a scoring breakdown. That's the right teach-moment.

If the user wants to tune the rubric, they edit `profile.md` directly. The re-run mode of `/setup` (where field-by-field keep/update/skip is offered) does NOT include the tier rubric either — same reason.

## Re-run mode question loop

When `userdata/profile.md` exists, iterate fields in the same order as the fresh
walk (Steps 1-8). The tier rubric is NOT offered — same reason it is not asked on
a fresh install (see the note above). Step 0 does not apply — re-run never
re-reads the CV, because the fields it would fill are already populated.

Step 1 is ONE field here, not five. Show the whole facts line and take a single
keep / update / skip on it, mirroring the fresh-install shape. On `update`, apply
whichever value the user names and leave the others alone — never re-ask all five.

**Step 4 is offered, and it is positioning only.** Show the current `##
Positioning` paragraph and take one keep / update / skip on it like any other
field. On `update`, run Mode A against the user's new sentences.

Proof points and moat are NOT offered here, in either mode — `/setup` stopped
asking for them on a fresh install too, and `/today` picks them up once the user
has seen real roles. Skipping the whole of Step 4 was the actual behaviour until
2026-08-24, when manual check 1 caught the loop running 1 → 2 → 3 → 5 → 6 → 7 →
8; positioning is the one thing in a profile that people genuinely revise as a
search progresses, so silently never offering it was the wrong half to drop.

The rule below about freeform sections does not cover positioning: `##
Positioning` is a documented section that this skill writes, not one of the
user's own. That ambiguity is what produced the contradiction.

For each field:

1. Show the current value on one line, then ask:

   > "Currently: `<value>`. Keep, update, or skip?"

2. Read the answer as `keep`, `update`, or `skip` (skip means "leave as-is for now,
   ask again next /setup").
3. If `update`: prompt for the new value using the same conversational pattern —
   and in the same register — as that step's fresh-install ask.

Never overwrite a non-empty field with an empty answer in re-run mode. If the user updates a field but provides empty input, ask once more; if still empty, treat as `skip` and leave the current value.

The user's freeform body sections (`## Tone of Voice`, `## What NOT to Frame As`, and any `##` section they added below the documented ones) are NEVER touched in re-run mode — they belong to the user. `## Positioning`, `## Proof Points` and `## Moat` are not in this set: they are sections this skill authors. Positioning is offered per the rule above; the other two are left alone because nothing asks for them here, not because they are the user's to guard.

## File writes

After all questions are answered, do these writes in order:

### 1. `userdata/profile.md`

Read the profile template, substitute every `{{PLACEHOLDER}}`, write to `userdata/profile.md`. Preserve all HTML comments and free-form prompt blocks (the `<!-- … -->` sections after each `##` header) verbatim. Substitute placeholders only.

For skipped placeholders: write an empty YAML value, never the literal `{{NAME}}` string. Specifically:
- `{{LINKEDIN_URL}}` is never asked at setup → always `linkedin_url:` (empty value parses as null). The field stays in the template; the skill that needs it fills it.
- `{{SALARY_BAND}}` skipped → `salary_band: ""` (explicit empty string — keeps the quoted-string shape the template intends).
- `{{HARD_FILTERS}}` skipped → `hard_filters: []`.
- `{{TARGET_TITLES}}` cannot be skipped (required).
- `{{GEOGRAPHY_DETAIL}}` skipped → `mode_detail:` (empty).
- `{{POSITIONING}}`, `{{PROOF_POINTS}}`, `{{MOAT}}` skipped (Step 4 option B, or a Mode B draft the user discards) → all three sections written empty under the `<!-- TODO: fill in via /job-offer:setup --refresh, or paste your CV at userdata/cv.md and re-run --refresh -->` comment — never the literal `{{POSITIONING}}` placeholder string.

Do NOT write `# unset` comments — they look like noise in the final file. An empty value is self-explanatory.

### 2. `userdata/strategy.md` (only if file does not already exist)

Read the strategy template. Populate:
- `target_offer_date`: from Step 7. If Step 7 was skipped, leave as `null`.
- `weekly_targets.*` + `pipeline_targets.*`: from the cadence-derivation table above. If Step 7 was skipped, leave all as `null` (`/today` skips them gracefully).
- `checkpoints: []` (empty list — user adds later via `career-coach` or by hand).
- `## Headline goal`: the auto-composed paragraph (from profile.md fields + target date). If Step 7 was skipped, omit the date clause and drop the countdown wording.
- `## Anti-goals`: leave the section empty (the template's HTML comment prompts the user to fill in later).

Write to `userdata/strategy.md`.

If `userdata/strategy.md` already exists, skip this write. /setup never overwrites a user's existing strategy file.

### 3. `userdata/journal.md` (only if file does not already exist)

Write a minimal journal file:

```markdown
# Journal

<!--
  Free-form notes you write yourself. Date each entry as `## YYYY-MM-DD`.
  /today scans the last 7 days for outreach keywords (DM, outreach, coffee,
  intro, reached out, messaged, connect) to count warm-outreach attempts.
-->
```

### 4. Three `.gitkeep` files

Create these empty files (only if the directory does not already contain a real file — never overwrite content):
- `userdata/companies/.gitkeep`
- `userdata/stories/.gitkeep`
- `userdata/outputs/.gitkeep`

### 5. `CLAUDE.md` at workspace root

Read `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE.template.md`. Resolve the single `{{INCLUDE: userdata/profile.md sections=positioning,proof_points,moat}}` marker by:

1. Read the just-written `userdata/profile.md`.
2. For each of `Positioning`, `Proof Points`, `Moat` (in that order):
   - Find the `## <Section>` heading line in profile.md.
   - Capture everything between that line and the next `## ` line (or EOF).
   - Strip any HTML comment blocks (`<!-- … -->`, possibly multi-line) from the captured content — those are authoring helpers for profile.md, not content meant for CLAUDE.md.
   - Trim leading and trailing blank lines from what's left.
3. Build the replacement block. The `{{INCLUDE}}` marker sits BELOW a `## About me` heading in the template, so each section must be DEMOTED from `##` to `###` to nest correctly. For each captured section, emit:
   - `### <Section>` (e.g. `### Positioning`)
   - blank line
   - the captured body
   - blank line
4. Replace the entire `{{INCLUDE: …}}` line (including its surrounding blank lines if any) with the concatenated block. The result is a clean `## About me` followed by three `###` subsections.

Skip a section if its content (after comment-stripping and trimming) is empty — better to omit `### Moat` entirely than render an empty header.

Write the result to `CLAUDE.md` at the workspace root (one level above `userdata/`). Overwrite any existing `CLAUDE.md` at the root only if it begins with the same `<!--` template-header comment as the template (signature of a previously generated file).

If it doesn't, **do not ask** — leave the file alone, write nothing, and say
nothing. The old behaviour asked `CLAUDE.md exists at workspace root and was not
generated by job-offer. Overwrite (y/N)?`, which is three pieces of build
detail (a filename, a workspace layout, a provenance check) and a shell prompt,
handed to a user who has no way to weigh the answer. Not writing it is the safe
branch and costs the user nothing they can perceive: their profile still exists,
and every skill reads it from disk regardless. Take the safe branch silently.

## Closing offers

First, confirm what was captured — in plain language, naming no files. The user
needs to know their answers were saved and what the plan now says; they do not
need the storage layout. If Step 7 produced a target date, include the derived
cadence so they can spot-check it. Example with target date set:

> "You're set up. I've got your profile, and a plan: land the offer by `<YYYY-MM-DD>`, which works out at 8 applications and 8 outreach messages a week, with 4 live interview threads at any time. Say the word if those numbers look wrong."

When Step 7 was skipped, drop the date and cadence clauses entirely: *"You're
set up. No target date yet, so there are no weekly numbers — tell me when you
want to have signed and I'll work them out."*

Confirming the write is required (a silent write to a user's own file is
indistinguishable from data loss), but the confirmation is about *what changed*,
not *where it lives*. "I've got your profile" carries the whole message;
`userdata/profile.md — identity, target role, salary, hard filters` carries a
directory listing.

**Do not offer the career-coach positioning interview here.** Setup's last word
belongs to the next step in the search, and that step is the first sweep — a
user who has just answered nine questions wants roles, not a fifth conversation
about themselves. The offer moves to `/today`, which surfaces it once the
profile has been used in anger and the user can tell whether it is landing.

**Automation offer (split per TONE.md Rule A — one ask per message):**

Step 1 — ask:
> "Want `/job-offer:today` to run automatically every day? (y / n)"

Use `AskUserQuestion` with two options: **Yes** / **No, I'll run it manually**.

If No → skip to closing nudge.

Step 2 (only if Yes) — ask:
> "What time? (e.g. 9am)"

Free-text answer. Parse to HH:MM.

Step 3 (only if Yes) — write the schedule via `/schedule` automatically and reply:
> "Done — your brief runs daily at <HH:MM>. That needs Claude Code open; if you'd rather it run in the background, say so and I'll set that up."

**Closing nudge:**

After all setup files are written (and after the automation step completes or is skipped), read `${CLAUDE_PLUGIN_ROOT}/references/recommended-flow.md` and compose a single one-line context-aware next-step nudge based on the user's current state. For a fresh setup with no companies yet, the nudge should be:

> "Setup done. Run `/job-offer:job-search` and I'll go find roles that match."

Do not list all three steps as numbered bullets; the recommended-flow reference
handles ordering. Do not offer `/today` as an alternative on a fresh install
either — the pipeline is empty, so a brief has nothing to report, and a choice
between a useful action and an empty one is not a choice worth presenting.

## What /setup never does

- Never edits `.claude/settings.json` or any Claude Code system config.
- Never runs `git init` or `git commit`. The repo lives in the user's workspace; the user manages it.
- Never validates any external service (no MCP, no API).
- Never writes `userdata/companies/*`, `userdata/stories/*`, or `userdata/outputs/daily-brief-*.md` — those belong to other skills.
- Never overwrites `userdata/strategy.md` if it exists. `/strategy` owns updates.
- Never overwrites `userdata/profile.md`'s body sections in re-run mode (only frontmatter fields the user explicitly updates).
- Never invents proof-point numbers. If the CV in Mode B doesn't have a metric for a bullet, surface it as a draft bullet without numbers and ask the user to fill in.

## Smoke test against the Maya example

Treat `userdata/examples/maya/` as a synthetic install root. Re-running /setup against it should:

- Detect existing `profile.md` → enter re-run mode.
- Show current values (Maya Patel, London UK, Europe/London, etc.) — each as `keep / update / skip`.
- If user picks `keep` for all: only re-resolve workspace-root `CLAUDE.md`. No other files change. Profile body sections (Positioning, Proof Points, Moat, Tone of Voice, What NOT to Frame As) untouched.
- The tier rubric in profile.md is unchanged (the values in Maya's file are the same as the template defaults).

A fresh-install run (against an empty userdata/) should produce a profile.md whose frontmatter shape is identical to Maya's, only with the user's own answers in place of placeholders.
