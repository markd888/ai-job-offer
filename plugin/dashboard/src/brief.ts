// Splits the /today brief markdown into its "## " sections so the dashboard
// can render "Today" as a checklist and "Heads-up" as cards. Anything the
// parser doesn't recognise is still shown as plain markdown.

export interface BriefSection {
  title: string;
  /** Top-level list items, each as its own markdown string. */
  items: string[];
  /** The section's raw markdown, without its heading. */
  body: string;
}

const LIST_ITEM = /^(?:[-*+]|\d+[.)])\s+/;

export function parseBrief(md: string): BriefSection[] {
  const sections: BriefSection[] = [];
  let current: { title: string; lines: string[] } | null = null;
  for (const line of md.split("\n")) {
    const heading = line.match(/^##\s+(.+?)\s*$/);
    if (heading) {
      if (current) sections.push(finish(current));
      current = { title: heading[1], lines: [] };
    } else if (current) {
      current.lines.push(line);
    }
  }
  if (current) sections.push(finish(current));
  return sections;
}

function finish({ title, lines }: { title: string; lines: string[] }): BriefSection {
  const items: string[] = [];
  for (const line of lines) {
    if (LIST_ITEM.test(line)) items.push(line.replace(LIST_ITEM, ""));
    else if (items.length > 0 && /^\s+\S/.test(line)) items[items.length - 1] += `\n${line.trim()}`;
  }
  return { title, items, body: lines.join("\n").trim() };
}

export const isTodaySection = (s: BriefSection) => /^today\b/i.test(s.title);
export const isHeadsUpSection = (s: BriefSection) => /^heads[\s-]?up\b/i.test(s.title);
// The dashboard already shows pipeline numbers, so this section is dropped.
export const isPipelineSection = (s: BriefSection) => /^pipeline state\b/i.test(s.title);
