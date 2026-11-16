# Recommended flow

This file is the canonical source for the job-offer happy path. Every skill consults it to compose a context-aware next-step nudge at the end of its run.

## Canonical sequence

```
setup → job-search → dashboard → today (daily, ongoing)
                                  ↓
                            evaluate-position (per role, when a link comes in)
                                  ↓
                            apply (when a role moves to to_apply) — builds the PDF, runs ats-check
                                  ↓
                            sent (when the application goes out)
                                  ↓
                            follow-up (when it's quiet 10+ days; records replies too)
                                  ↓
                            interview-prep (when interview is scheduled)
                                  ↓
                            interview-analysis (after the interview)

story-builder runs ad-hoc, whenever the user wants to capture a new STAR story or fill a gap.
evaluate-offer runs when an offer arrives.
ats-check also runs on its own after a hand-edited CV.
career-coach (agent, dispatched by Claude — not a slash command) provides on-demand reflection, positioning, anti-goals, and offer-evaluation conversation.
integrations runs once during onboarding (or whenever wiring changes).
```

## State → suggested next step

When a skill finishes, look at current filesystem and journal state, then pick the most useful next step. The list below is ordered: first matching rule wins. Rules about something that just happened in the conversation come first, so they beat standing pipeline state. If nothing matches, suggest `/job-offer:today`.

| Current state | Suggested next step | Wording hint |
|---|---|---|
| `userdata/profile.md` just written, no companies in `userdata/companies/` | `/job-offer:job-search` | "Run /job-offer:job-search now to seed your applications list." |
| `/apply` just built a CV, or the user says they're about to send it | Nudge in chat | "Tell me once it's sent and I'll record it." |
| The user says an application went out ("sent it", "applied to <Co>") and the role isn't `applied` with a `date_applied` yet | `/job-offer:sent <Co>` | "Want me to record the <Co> application as sent today?" |
| An interview round ended today (calendar, debrief or the user says so) | `/job-offer:follow-up thanks <Co>` | "Want a short thank-you to <name> while it's fresh?" |
| Companies exist with `status: new` and no `userdata/outputs/applications.md` (or applications.md is stale) | `/job-offer:dashboard` | "Open the dashboard to sort through your new roles — or just tell me here which ones you want to go after." |
| At least one company `status: interviewing` and no `interview-prep-<date>.md` for it | `/job-offer:interview-prep <Co>` | "You have an interview coming up at <Co> with no prep doc yet." |
| At least one company `status: interviewing`, a product-case/analytical round is likely (research-brief mentions a case round, or it's a product/growth role), and no `userdata/case-practice/` log exists in the last 7 days | `/job-offer:case-practice <Co>` | "Case-likely round at <Co> — drill product cases with /job-offer:case-practice." |
| `follow-ups.py` lists roles under "Follow-up due" or "Close instead" | `/job-offer:follow-up` | "<Co> has been quiet <N> days — want a short follow-up?" |
| A role folder has a CV PDF edited after its latest `ats-check-*.md` | `/job-offer:ats-check <Co>` | "You changed the <Co> CV since it was checked — run the ATS check again before sending." |
| At least one company `status: to_apply` for 14+ days with no movement | Nudge in chat, no command | "<Co> has been in 'to apply' for 2+ weeks. Time to move or drop it." |
| A daily brief was just generated and journal entries exist from the prior ISO week, and this is the first /today of the new ISO week | Weekly reflection prompt | "It's the start of a new week. Want a 5-min reflection on last week?" |
| Default | `/job-offer:today` | "Run /job-offer:today tomorrow morning (or right now) for your daily brief." |

## Why founder outreach

A few skills reference founder outreach (e.g. `/today` heads-up, strategy.md weekly targets). The why: founder outreach is a discovery channel for early-stage roles where the founder is the hiring decision-maker — it surfaces opportunities that don't appear on public job boards. Surface this only when the user has opted into a founder-outreach target in `strategy.md`.

## Conventions for the nudge

- One line, plain prose. Not a bulleted list.
- Specific to context — not a generic parrot of the canonical order.
- Skip the nudge entirely if there's no useful next step (e.g. the user just finished `/today` and there's nothing notable to flag).
