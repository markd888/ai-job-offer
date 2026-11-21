import { Tooltip } from "@mantine/core";
import type { Position } from "../types";
import { scoringNote, scoringTooltip } from "./scoring";

const SCORED = new Set(["P0", "P1", "P2", "P3"]);

export function isScored(tier: string | undefined): boolean {
  return !!tier && SCORED.has(tier);
}

export function TierBadge({ tier, p }: { tier: string | undefined; p?: Position }) {
  if (!isScored(tier)) {
    return (
      <Tooltip label="Tier unset — run /job-offer:evaluate-position to score this role" withArrow position="right">
        <span className="jst-tier jst-tier-none" aria-label="Unscored">—</span>
      </Tooltip>
    );
  }
  const badge = <span className={`jst-tier jst-tier-${tier}`}>{tier}</span>;
  const tip = p ? scoringTooltip(p) : null;
  const note = p ? scoringNote(p) : null;
  return (
    <span className="jst-tier-wrap">
      {tip ? <Tooltip label={tip} withArrow position="right" multiline w={240}>{badge}</Tooltip> : badge}
      {note && <span className={`jst-tier-note jst-tier-note-${note.tone}`}>{note.label}</span>}
    </span>
  );
}
