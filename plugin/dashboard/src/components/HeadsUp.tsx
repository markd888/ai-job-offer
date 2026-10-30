import { useMemo } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

import { isHeadsUpSection, isPipelineSection, isTodaySection, parseBrief } from "../brief";
import type { DailyBrief } from "../types";
import { briefMdComponents } from "./briefMarkdown";

interface Props {
  brief: DailyBrief | null;
}

const noteMd: Components = {
  ...briefMdComponents,
  p: ({ children }) => <p>{children}</p>,
  li: ({ children }) => <li>{children}</li>,
};

// Heads-up items as cards, plus any brief sections the dashboard has no
// dedicated surface for (Today → TodayFocus, Pipeline state → dropped).
export function HeadsUp({ brief }: Props) {
  const sections = useMemo(() => (brief ? parseBrief(brief.markdown) : []), [brief]);
  const headsUp = sections.find(isHeadsUpSection);
  const today = sections.find(isTodaySection);
  const others = sections.filter(
    (s) => !isHeadsUpSection(s) && !isPipelineSection(s) && !(isTodaySection(s) && s.items.length > 0) && s.body,
  );
  // When there's no Today list, TodayFocus renders the other sections itself.
  const showOthers = today !== undefined && today.items.length > 0 && others.length > 0;

  if (!headsUp && !showOthers) return null;

  return (
    <>
      {headsUp && (
        <section className="jst-card" aria-labelledby="headsup-h" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 10 }}>
          <h2 id="headsup-h" className="jst-h3" style={{ marginBottom: 4 }}>{headsUp.title}</h2>
          {headsUp.items.length > 0 ? (
            headsUp.items.map((item) => (
              <div key={item} className="jst-note">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={noteMd}>{item}</ReactMarkdown>
              </div>
            ))
          ) : (
            <div className="jst-note">
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={noteMd}>{headsUp.body}</ReactMarkdown>
            </div>
          )}
        </section>
      )}
      {showOthers && (
        <section className="jst-card" aria-label="More from the brief" style={{ padding: 20 }}>
          <ReactMarkdown remarkPlugins={[remarkGfm]} components={briefMdComponents}>
            {others.map((s) => `## ${s.title}\n\n${s.body}`).join("\n\n")}
          </ReactMarkdown>
        </section>
      )}
    </>
  );
}
