import { Box, UnstyledButton } from "@mantine/core";
import { useState } from "react";

import { humanizeIsoDates, relativeDate } from "../dates";
import type { Position } from "../types";
import { OpenPostingIcon, QuickAddNote, lastActivity, tierRank } from "./ApplicationsTable";
import { TierBadge } from "./TierBadge";

interface Props {
  companies: Position[];
  onOpen: (p: Position) => void;
  onChange: () => void;
}

export function ActiveRoles({ companies, onOpen, onChange }: Props) {
  const active = companies
    .filter((p) => p.status === "interviewing" || p.status === "offer")
    .sort((a, b) => Number(b.status === "offer") - Number(a.status === "offer") || tierRank(a) - tierRank(b));

  if (active.length === 0) return null;

  return (
    <section aria-labelledby="active-h" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <span className="jst-dot" style={{ background: "var(--jst-ok)" }} />
        <h2 id="active-h" className="jst-h2">In interviews</h2>
        <span className="jst-count">{active.length}</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
        {active.map((p) => (
          <ActiveCard key={p.folder_path} p={p} onOpen={onOpen} onChange={onChange} />
        ))}
      </div>
    </section>
  );
}

function ActiveCard({ p, onOpen, onChange }: { p: Position; onOpen: (p: Position) => void; onChange: () => void }) {
  const [noteOpen, setNoteOpen] = useState(false);
  const steps = p.next_event ? humanizeIsoDates(p.next_event).split(";").map((s) => s.trim()).filter(Boolean) : [];

  return (
    <article className="jst-card" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
        <UnstyledButton onClick={() => onOpen(p)} style={{ minWidth: 0 }} aria-label={`Open ${p.company}`}>
          <h3 className="jst-co" style={{ fontSize: 17, whiteSpace: "normal" }}>
            {p.company}
            {p.status === "offer" && <span className="jst-tag" style={{ background: "var(--jst-ok-bg)", color: "var(--jst-ok-fg)" }}>Offer</span>}
          </h3>
          <p className="jst-role" style={{ whiteSpace: "normal" }}>{p.position}</p>
        </UnstyledButton>
        <TierBadge tier={p.tier} />
      </div>

      <div style={{ padding: 12, borderRadius: 10, background: "var(--jst-ok-bg)", flex: 1 }}>
        <p className="jst-eyebrow" style={{ fontSize: 11, color: "var(--jst-ok-fg)" }}>Next step</p>
        {steps.length > 0 ? (
          steps.map((s) => (
            <p key={s} style={{ margin: "4px 0 0", fontSize: 14, fontWeight: 500, lineHeight: 1.4 }}>{s}</p>
          ))
        ) : (
          <p className="jst-muted" style={{ margin: "4px 0 0", fontSize: 14 }}>Not set — add one with a note.</p>
        )}
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <p className="jst-muted" style={{ margin: 0, fontSize: 13 }}>
          Last touch <span className="jst-num">{relativeDate(lastActivity(p))}</span>
        </p>
        <Box style={{ display: "flex", gap: 2, marginRight: -6 }}>
          <OpenPostingIcon link={p.link} company={p.company} />
          <QuickAddNote folderPath={p.folder_path} company={p.company} opened={noteOpen} onChange={setNoteOpen} onAdded={onChange} />
        </Box>
      </div>
    </article>
  );
}
