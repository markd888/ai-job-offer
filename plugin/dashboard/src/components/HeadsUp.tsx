import { useMemo, useState } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

import { isHeadsUpSection, isPipelineSection, isTodaySection, parseBrief } from "../brief";
import type { DailyBrief } from "../types";
import { briefMdComponents } from "./briefMarkdown";

interface Props {
  brief: DailyBrief | null;
}

// The brief lists heads-up items most urgent first; show the top few and
// keep the rest one click away.
const HEADS_UP_LIMIT = 3;

// Plain elements: the list's own CSS sets size and weight, so the brief's
// bold lead-ins stay the same size as the text around them.
const noteMd: Components = {
  ...briefMdComponents,
  p: ({ children }) => <p>{children}</p>,
  li: ({ children }) => <li>{children}</li>,
  strong: ({ children }) => <strong>{children}</strong>,
};

// Heads-up items as a list, plus any brief sections the dashboard has no
// dedicated surface for (Today → TodayFocus, Pipeline state → dropped).
export function HeadsUp({ brief }: Props) {
  const [showAll, setShowAll] = useState(false);
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
        <section className="jst-rail-sec" aria-labelledby="headsup-h">
          <div className="jst-rail-head">
            <h2 id="headsup-h" className="jst-h3">{headsUp.title}</h2>
            {headsUp.items.length > 0 && <span className="jst-count">{headsUp.items.length}</span>}
          </div>
          {headsUp.items.length > 0 ? (
            <>
              <ul className="jst-notes">
                {(showAll ? headsUp.items : headsUp.items.slice(0, HEADS_UP_LIMIT)).map((item) => (
                  <li key={item} className="jst-note">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={noteMd}>{item}</ReactMarkdown>
                  </li>
                ))}
              </ul>
              {headsUp.items.length > HEADS_UP_LIMIT && (
                <button type="button" className="jst-more" onClick={() => setShowAll((v) => !v)} aria-expanded={showAll}>
                  {showAll ? "Show fewer" : `Show ${headsUp.items.length - HEADS_UP_LIMIT} more`}
                </button>
              )}
            </>
          ) : (
            <div className="jst-note">
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={noteMd}>{headsUp.body}</ReactMarkdown>
            </div>
          )}
        </section>
      )}
      {showOthers && (
        <section className="jst-rail-sec" aria-label="More from the brief">
          <div>
            <ReactMarkdown remarkPlugins={[remarkGfm]} components={briefMdComponents}>
              {others.map((s) => `## ${s.title}\n\n${s.body}`).join("\n\n")}
            </ReactMarkdown>
          </div>
        </section>
      )}
    </>
  );
}
