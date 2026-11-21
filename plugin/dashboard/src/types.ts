export type Status =
  | "new"
  | "to_apply"
  | "applied"
  | "interviewing"
  | "offer"
  | "rejected"
  | "not_interested";

export type Tier = "P0" | "P1" | "P2" | "P3";

export interface Position {
  company: string;
  position: string;
  position_slug: string;
  tier: Tier | string;
  status: Status | string;
  folder_path: string;
  is_multi_role: boolean;
  has_notes: boolean;
  score?: string;
  link?: string;
  date_added?: string;
  date_applied?: string;
  last_inbound?: string;
  monitoring?: string;
  rejection_stage?: string;
  /** Deepest stage reached: application | screening | interview | final. */
  max_stage?: string;
  /** Free-text next step for active roles, e.g. "HR screen with Ana Mon 2026-11-02 12:30". */
  next_event?: string;
  /** "2" for roles scored by score.py; absent or "1" for v1 (3–15 `score`). */
  scoring_version?: string;
  /** 0–100, v2 only. Never compare with the v1 `score`. */
  fit_score?: string;
  eligibility?: "eligible" | "needs_review" | "blocked" | string;
  evidence_confidence?: "high" | "medium" | "low" | string;
  predicted_tier?: string;
  tier_override?: string;
}

export interface WeeklyTargets {
  [key: string]: number;
}

export interface Strategy {
  target_offer_date?: string;
  weekly_targets: WeeklyTargets;
  search_state?: "active" | "dormant"; // written by /wrap-up
  search_closed?: string;
  accepted_offer?: string;
}

export interface DailyBrief {
  date: string;
  markdown: string;
}

export interface WeeklyProgress {
  warm_outreach: number;
  feedback_requests: number;
  applications: number;
  window_days: number;
}

/** One row of GET /api/state's funnel_by_channel — see plugin/scripts/funnel.py. */
export interface ChannelRow {
  channel: string; // referral | cold | recruiter | linkedin | company-site | other | unknown
  applied: number;
  screening: number;
  interview: number;
  final: number;
  offer: number;
  small_sample: boolean;
  screening_rate: number | null;
  interview_rate: number | null;
  final_rate: number | null;
  offer_rate: number | null;
}

export interface FunnelByChannel {
  min_sample: number;
  rows: ChannelRow[];
}

export interface DashboardState {
  companies: Position[];
  strategy: Strategy;
  weekly_progress: WeeklyProgress;
  funnel_by_channel?: FunnelByChannel; // absent in snapshots exported before 0.8
  latest_brief: DailyBrief | null;
  userdata_root: string;
}
