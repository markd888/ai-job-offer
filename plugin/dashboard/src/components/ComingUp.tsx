import { UnstyledButton } from "@mantine/core";
import { useMemo } from "react";

import { type DatedEvent, monthShort, parseDatedEvents, startOfToday, weekdayShort } from "../dates";
import type { Position } from "../types";

interface Props {
  companies: Position[];
  onOpen: (p: Position) => void;
}

interface Upcoming extends DatedEvent {
  position: Position;
}

const DAY_MS = 24 * 60 * 60 * 1000;

// Built from each active role's next_event; dates in the past are dropped.
export function ComingUp({ companies, onOpen }: Props) {
  const events = useMemo(() => {
    const today = startOfToday().getTime();
    const out: Upcoming[] = [];
    for (const p of companies) {
      if (p.status !== "interviewing" && p.status !== "offer") continue;
      for (const e of parseDatedEvents(p.next_event)) {
        if (e.day.getTime() >= today) out.push({ ...e, position: p });
      }
    }
    return out.sort((a, b) => a.day.getTime() - b.day.getTime() || (a.time ?? "").localeCompare(b.time ?? ""));
  }, [companies]);

  if (events.length === 0) return null;
  const today = startOfToday().getTime();

  return (
    <section className="jst-card" aria-labelledby="coming-h" style={{ padding: "20px 20px 8px" }}>
      <h2 id="coming-h" className="jst-h3" style={{ marginBottom: 8 }}>Coming up</h2>
      <ol style={{ listStyle: "none", margin: 0, padding: 0 }}>
        {events.map((e, i) => {
          const deadline = /\b(due|deadline)\b/i.test(e.title);
          const soon = e.day.getTime() - today <= DAY_MS;
          const tone = deadline
            ? { bg: "var(--jst-danger-bg)", fg: "var(--jst-danger-fg)" }
            : soon
              ? { bg: "var(--jst-warn-bg)", fg: "var(--jst-warn-fg)" }
              : { bg: "var(--jst-track)", fg: "var(--jst-ink)" };
          return (
            <li
              key={`${e.position.folder_path}-${i}`}
              style={{ display: "grid", gridTemplateColumns: "52px minmax(0, 1fr)", gap: 14, padding: "12px 0", borderTop: "1px solid var(--jst-divider)" }}
            >
              <div
                aria-label={`${weekdayShort(e.day)} ${e.day.getDate()} ${monthShort(e.day)}`}
                style={{ textAlign: "center", padding: "6px 0", borderRadius: 10, background: tone.bg, color: tone.fg }}
              >
                <p className="jst-num" style={{ margin: 0, fontSize: 11, fontWeight: 600, letterSpacing: ".06em" }}>{weekdayShort(e.day)}</p>
                <p className="jst-num" style={{ margin: "2px 0 0", fontSize: 20, lineHeight: 1, fontWeight: 500 }}>{e.day.getDate()}</p>
              </div>
              <UnstyledButton onClick={() => onOpen(e.position)} style={{ minWidth: 0 }}>
                <p style={{ margin: 0, fontSize: 14, fontWeight: 600 }}>{e.position.company}</p>
                <p className="jst-muted" style={{ margin: "2px 0 0", fontSize: 13 }}>{e.title}</p>
                <p className="jst-when" style={{ margin: "4px 0 0" }}>
                  {monthShort(e.day)} {e.day.getDate()}{e.time ? ` · ${e.time}` : ""}
                </p>
              </UnstyledButton>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
