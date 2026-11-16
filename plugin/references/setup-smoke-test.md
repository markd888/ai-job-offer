# /setup — smoke test against the Maya example

<!-- Maintainer reference for skills/setup/SKILL.md; never needed at run time. -->

Treat `userdata/examples/maya/` as a synthetic install root. Re-running /setup against it should:

- Detect existing `profile.md` → enter re-run mode.
- Show current values (Maya Patel, London UK, Europe/London, etc.) — each as `keep / update / skip`.
- If user picks `keep` for all: only re-resolve workspace-root `CLAUDE.md`. No other files change. Profile body sections (Positioning, Proof Points, Moat, Tone of Voice, What NOT to Frame As) untouched.
- The tier rubric in profile.md is unchanged (the values in Maya's file are the same as the template defaults).

A fresh-install run (against an empty userdata/) should produce a profile.md whose frontmatter shape is identical to Maya's, only with the user's own answers in place of placeholders.
