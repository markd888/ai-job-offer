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
    <section className="jst-rail-sec" aria-labelledby="coming-h">
      <div className="jst-rail-head">
        <h2 id="coming-h" className="jst-h3">Coming up</h2>
      </div>
      <ol className="jst-events">
        {events.map((e, i) => {
          const deadline = /\b(due|deadline)\b/i.test(e.title);
          const soon = e.day.getTime() - today <= DAY_MS;
          const tone = deadline ? " jst-event-day-deadline" : soon ? " jst-event-day-soon" : "";
          return (
            <li key={`${e.position.folder_path}-${i}`} className="jst-event">
              <div className={`jst-event-day${tone}`} aria-label={`${weekdayShort(e.day)} ${e.day.getDate()} ${monthShort(e.day)}`}>
                <p className="jst-event-dow">{weekdayShort(e.day)}</p>
                <p className="jst-event-num">{e.day.getDate()}</p>
              </div>
              <UnstyledButton onClick={() => onOpen(e.position)} className="jst-event-body">
                <p className="jst-event-co">{e.position.company}</p>
                <p className="jst-event-title">{e.title}</p>
                <p className="jst-event-when">
                  {e.day.getDate()} {monthShort(e.day)}{e.time ? ` · ${e.time}` : ""}
                </p>
              </UnstyledButton>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
