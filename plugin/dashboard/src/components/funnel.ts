// Pure funnel math for the job-offer dashboard. No React, so it can be unit-tested on its own.
// Input: the `companies` array from GET /api/state.

export type Role = {
  company: string;
  position: string;
  status: string; // new | to_apply | applied | interviewing | offer | rejected | not_interested
  tier?: string;
  date_applied?: string | null;
  date_added?: string | null;
  rejection_stage?: string | null; // application | screening | interview | final
  max_stage?: string | null; // deepest stage reached, same values
};

export const STAGES = ['applied', 'screening', 'interview', 'final', 'offer'] as const;
export type Stage = (typeof STAGES)[number];
export const STAGE_LABEL: Record<Stage, string> = {
  applied: 'Applied',
  screening: 'HR screening',
  interview: '2+ rounds',
  final: 'Final',
  offer: 'Offer',
};

const DEPTH: Record<string, number> = { application: 0, screening: 1, interview: 2, final: 3 };

/** Deepest stage a role reached, or null if it was never applied to. */
export function stageReached(r: Role): Stage | null {
  if (r.status === 'offer') return 'offer';
  if (r.status === 'interviewing') return (['screening', 'screening', 'interview', 'final'] as Stage[])[DEPTH[r.max_stage ?? 'screening'] ?? 1];
  // A role you dropped (not_interested) or that was rejected without a recorded
  // rejection_stage still reached whatever max_stage says, so take the deeper one.
  const deepest = Math.max(DEPTH[r.rejection_stage ?? 'application'] ?? 0, DEPTH[r.max_stage ?? 'application'] ?? 0);
  const applied = r.status === 'applied' || r.status === 'rejected' || !!r.date_applied || deepest >= 1;
  if (!applied) return null;
  const d = deepest;
  return (['applied', 'screening', 'interview', 'final'] as Stage[])[d];
}

export type FunnelStep = { stage: Stage; label: string; count: number; fromPrev: number | null; fromTop: number };

export function computeFunnel(roles: Role[]): FunnelStep[] {
  const reached = roles.map(stageReached).filter((s): s is Stage => s !== null);
  const idx = (s: Stage) => STAGES.indexOf(s);
  const counts = STAGES.map((s) => reached.filter((r) => idx(r) >= idx(s)).length);
  return STAGES.map((stage, i) => ({
    stage,
    label: STAGE_LABEL[stage],
    count: counts[i],
    fromPrev: i === 0 ? null : counts[i - 1] ? counts[i] / counts[i - 1] : 0,
    fromTop: counts[0] ? counts[i] / counts[0] : 0,
  }));
}
