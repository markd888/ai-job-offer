import { Code, Text } from "@mantine/core";
import { IconCheck } from "@tabler/icons-react";
import { useEffect, useMemo, useState } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

import { isHeadsUpSection, isPipelineSection, isTodaySection, parseBrief } from "../brief";
import { DEMO_MODE } from "../config";
import type { DailyBrief } from "../types";
import { briefMdComponents } from "./briefMarkdown";

interface Props {
  brief: DailyBrief | null;
}

// Inline markdown for a checklist line: keep bold/code, drop block wrappers.
const inlineMd: Components = {
  p: ({ children }) => <>{children}</>,
  strong: ({ children }) => <strong>{children}</strong>,
  code: ({ children }) => <Code>{children}</Code>,
};

// Ticks are a per-browser convenience, keyed by brief date so each new brief
// starts unticked. Storage can be unavailable (private mode) — fail quietly.
function loadDone(key: string): string[] {
  try {
    return JSON.parse(window.localStorage.getItem(key) ?? "[]");
  } catch {
    return [];
  }
}

function saveDone(key: string, done: string[]) {
  try {
    window.localStorage.setItem(key, JSON.stringify(done));
  } catch {
    // ignore
  }
}

export function TodayFocus({ brief }: Props) {
  const sections = useMemo(() => (brief ? parseBrief(brief.markdown) : []), [brief]);
  const today = sections.find(isTodaySection);
  const storageKey = `jst-focus-done:${brief?.date ?? ""}`;
  const [done, setDone] = useState<string[]>(() => loadDone(storageKey));
  useEffect(() => setDone(loadDone(storageKey)), [storageKey]);

  const todayIso = useMemo(() => new Date().toISOString().slice(0, 10), []);
  // In demo mode the snapshot is pinned to a fixed date — never call it stale.
  const isStale = !DEMO_MODE && brief !== null && brief.date < todayIso;

  const toggle = (item: string) => {
    const next = done.includes(item) ? done.filter((d) => d !== item) : [...done, item];
    setDone(next);
    saveDone(storageKey, next);
  };

  // A brief without a "## Today" list still gets shown, as plain markdown.
  const fallback =
    brief && !today?.items.length
      ? sections
          .filter((s) => !isPipelineSection(s) && !isHeadsUpSection(s))
          .map((s) => `## ${s.title}\n\n${s.body}`)
          .join("\n\n") || brief.markdown
      : null;

  return (
    <section className="jst-card" aria-labelledby="focus-h" style={{ overflow: "hidden" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12, padding: "20px 20px 14px" }}>
        <div>
          <h2 id="focus-h" className="jst-h2">Today’s focus</h2>
          <p className="jst-muted" style={{ margin: "4px 0 0", fontSize: 13 }}>
            {brief ? <>From the daily brief · {brief.date}</> : "No daily brief yet"}
            {isStale && <span className="jst-tag">Stale — run /today</span>}
          </p>
        </div>
        {today && today.items.length > 0 && (
          <p className="jst-num jst-muted" style={{ margin: 0, fontSize: 13 }}>
            {today.items.filter((i) => done.includes(i)).length} / {today.items.length} done
          </p>
        )}
      </div>

      {!brief && (
        <Text size="sm" c="dimmed" px={20} pb={20}>
          Run <Code>/today</Code> in Claude Code to generate one.
        </Text>
      )}

      {today?.items.map((item) => (
        <button
          key={item}
          type="button"
          className="jst-task"
          aria-pressed={done.includes(item)}
          onClick={() => toggle(item)}
        >
          <span className="jst-box">
            <IconCheck size={14} stroke={3} />
          </span>
          <span className="jst-task-text" style={{ flex: 1, minWidth: 0 }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={inlineMd}>{item}</ReactMarkdown>
          </span>
        </button>
      ))}

      {fallback && (
        <div style={{ padding: "0 20px 16px" }}>
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={briefMdComponents}>{fallback}</ReactMarkdown>
        </div>
      )}
    </section>
  );
}
