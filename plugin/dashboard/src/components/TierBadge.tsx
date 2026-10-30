import { Tooltip } from "@mantine/core";

const SCORED = new Set(["P0", "P1", "P2", "P3"]);

export function isScored(tier: string | undefined): boolean {
  return !!tier && SCORED.has(tier);
}

export function TierBadge({ tier }: { tier: string | undefined }) {
  if (isScored(tier)) return <span className={`jst-tier jst-tier-${tier}`}>{tier}</span>;
  return (
    <Tooltip label="Tier unset — run /job-offer:evaluate-position to score this role" withArrow position="right">
      <span className="jst-tier jst-tier-none" aria-label="Unscored">—</span>
    </Tooltip>
  );
}
