---
name: help
description: This skill should be used when the user asks for "/help", "/job-offer:help", "what does this plugin do", "how do I navigate this", "list the skills", "show me all skills", "give me a tour", "what agents are available", "where do I start", or wants a scannable map of job-offer's skills, agents, and recommended order. Prints a one-page reference card to chat covering the 5-phase workflow, all 16 skills with use-when triggers, all 6 agents grouped by purpose, and a recommended first-week flow. Also writes the same card to `userdata/help.md` so it's available for quick reference later. No questions.
---

# /help — print the reference card and save a copy

The canonical user flow and the rules each skill follows for end-of-run nudges live in `${CLAUDE_PLUGIN_ROOT}/references/recommended-flow.md`. Read that file to understand what to suggest next based on the user's current state.

**Filter rule:** when printing the skills list to chat, omit any skill whose frontmatter `description:` begins with "Internal" or "Internal test harness" — these are maintainer-only and not part of the end-user surface. Currently this filters out `/test-personas`.

The card lives at `${CLAUDE_PLUGIN_ROOT}/skills/help/help.md`. On every run, do all three of these in order:

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/help/help.md` and print its contents to chat verbatim. Render exactly as written — headings, tables, code spans. Do not summarise, expand, or paraphrase.

2. Copy the same file to `userdata/help.md`, overwriting. Create `userdata/` first if it doesn't exist. Use `cp` so plugin updates propagate.

3. After the card, print exactly one closing line:

   > I've dropped a copy in `userdata/` — open it anytime for the same reference.

   Name the folder, not the file. This one is borderline, since the whole point
   of the line is that the user can go and read it — but `userdata/` is enough
   to find one file, and the alternative is a filename in chat, which is the
   habit the plugin is trying to lose.

Then stop. No follow-up offers, no questions, no other file reads or writes.
