const DAY_MS = 24 * 60 * 60 * 1000;
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

/** Whole days since an ISO date, or null when missing/unparseable. */
export function daysSince(iso: string | undefined): number | null {
  if (!iso) return null;
  const then = Date.parse(iso);
  if (Number.isNaN(then)) return null;
  return Math.floor((Date.now() - then) / DAY_MS);
}

export function relativeDate(iso: string | undefined): string {
  if (!iso) return "—";
  const days = daysSince(iso);
  if (days === null) return iso;
  if (days < 1) return "today";
  if (days < 2) return "1d";
  if (days < 7) return `${days}d`;
  if (days < 14) return "1w";
  if (days < 60) return `${Math.floor(days / 7)}w`;
  return `${Math.floor(days / 30)}mo`;
}

/** "Thu 29 Oct 2026" */
export function longDate(d: Date): string {
  return `${WEEKDAYS[d.getDay()]} ${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}`;
}

/** Rewrites ISO dates inside free text ("Tue 2026-11-03") as "Tue 3 Nov". */
export function humanizeIsoDates(text: string): string {
  return text.replace(/\b(\d{4})-(\d{2})-(\d{2})\b/g, (_, _y, m, d) => `${Number(d)} ${MONTHS[Number(m) - 1]}`);
}

export interface DatedEvent {
  /** Local midnight of the event day. */
  day: Date;
  time: string | null;
  title: string;
}

// next_event is free text written by the CLI skills, e.g.
//   "Recruiter call Tue 2026-11-03 13:00–13:45 (Zoom app); Criteria assessment due Tue 2026-11-03 21:35"
// Each ";"-separated segment with an ISO date becomes one event.
export function parseDatedEvents(text: string | undefined): DatedEvent[] {
  if (!text) return [];
  const out: DatedEvent[] = [];
  for (const segment of text.split(";")) {
    const date = segment.match(/\b(\d{4})-(\d{2})-(\d{2})\b/);
    if (!date) continue;
    const day = new Date(Number(date[1]), Number(date[2]) - 1, Number(date[3]));
    const afterDate = segment.slice((date.index ?? 0) + date[0].length);
    const time = afterDate.match(/^\s*(\d{1,2}:\d{2})(?:\s*[–-]\s*\d{1,2}:\d{2})?/);
    const title = segment
      .replace(time ? time[0] : "", "")
      .replace(new RegExp(`(\\b(by|on)\\s+)?(\\b(${WEEKDAYS.join("|")})\\s+)?${date[0]}`), "")
      .replace(/\s{2,}/g, " ")
      .trim();
    out.push({ day, time: time ? time[1] : null, title });
  }
  return out;
}

export function weekdayShort(d: Date): string {
  return WEEKDAYS[d.getDay()].toUpperCase();
}

export function monthShort(d: Date): string {
  return MONTHS[d.getMonth()];
}

export function startOfToday(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), now.getDate());
}

/** Whole days from now until an ISO date (never negative), or null when missing/unparseable. */
export function daysUntil(iso: string | undefined): number | null {
  if (!iso) return null;
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return null;
  return Math.max(0, Math.ceil((t - Date.now()) / DAY_MS));
}

/**
 * humanizeIsoDates for markdown: rewrites dates in the prose but leaves link
 * targets, autolinks, bare URLs and `code` exactly as written, so a link to
 * interview-prep-2026-11-15.md still works.
 */
export function humanizeIsoDatesInMarkdown(md: string): string {
  return md
    .split(/(`[^`]*`|\]\([^)]*\)|<[^>\s]+>|https?:\/\/[^\s)>]+)/g)
    .map((part, i) => (i % 2 === 1 ? part : humanizeIsoDates(part)))
    .join("");
}
