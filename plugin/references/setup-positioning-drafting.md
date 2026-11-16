# /setup — drafting positioning (Step 4, Modes A and B)

<!-- Loaded on demand by skills/setup/SKILL.md; part of /setup, split out to keep the always-loaded skill small. -->

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
