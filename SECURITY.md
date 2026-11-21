# Security

## Reporting a vulnerability

Report it privately through GitHub. Open the repository's **Security** tab and
choose **Report a vulnerability**
([direct link](https://github.com/markd888/ai-job-offer/security/advisories/new)).
Only the maintainer sees the report.

**Do not open a public issue for a vulnerability.** Public issues aren't the
place for your job-search data either: CV text, profile, company names, people
or anything else from `userdata/`. If a report needs an example, make one up.

You can expect a first reply within a week. Fixes ship as a normal release and
are noted in the [CHANGELOG](CHANGELOG.md).

## What the plugin can touch

job-offer is a Claude Code plugin: markdown skills, agents and small Python
scripts. It has no server of its own. Claude Code runs it on your machine, with
the permissions you give Claude Code.

**Reads and writes.** The plugin keeps its files under `userdata/` in your search
folder: CV, profile, strategy, journal, stories, people, company folders,
outputs. The folder is gitignored by default. Scripts write only under
`userdata/` and to temporary files.

**What leaves your machine:**

- **The model provider.** Files and messages Claude works with go to the
  provider your Claude Code uses (Anthropic by default). That's how Claude Code
  works, not a plugin choice.
- **The public web and ATS boards.** Search queries, posting URLs and company
  pages are fetched from the public web and from public ATS job-board APIs
  (Ashby, Greenhouse, Lever).
- **Freehire,** only if you connect its MCP. It receives search filters from
  your profile: titles, seniority, countries, salary floor.
- **Other MCP integrations,** only if you set them up (calendar, email, meeting
  notes). They see what Claude asks them for.
- **The install count,** only if you said yes in `/setup`. It sends a random
  install ID and the plugin version to `job-offer.mark-d.dev`, with no IP and no
  user agent stored. To turn it off, set `"consent": false` in
  `userdata/telemetry.json` or set `JOB_OFFER_TELEMETRY=0`.
- **The optional cloud dashboard,** only if you deploy it. A read-only snapshot
  of your role cards goes to your own Cloudflare account.

The plugin never sends anything to an employer, recruiter or contact. Outreach,
follow-ups and cover letters are drafts. You send them yourself.

The local dashboard listens on `127.0.0.1` only.

## Known gaps

- **Job postings are untrusted text.** A posting can contain text written to
  steer an AI ("ignore previous instructions…"). The skills treat posting text
  as data: they quote it and never follow it. There is no technical
  prompt-injection guard yet. Review what Claude proposes to write before you
  accept it, especially after reading an unfamiliar posting.
- **The cloud dashboard** relies on Cloudflare Access in front of the Worker,
  plus the Worker's own check of the Access JWT (`ACCESS_TEAM_DOMAIN`,
  `ACCESS_AUD`). If either is misconfigured, the snapshot could be exposed.
  `plugin/dashboard/README.md` has a check for that.
- **Third-party MCPs** are outside this project. Whatever data you connect, they
  handle under their own terms.

## Supported versions

Only the latest release gets fixes. Update with
`claude plugin update job-offer@job-offer`.
