// Single source of truth for statuses. Order here drives:
//   - the order of accordion groups in ApplicationsTable
//   - the order of options in the StatusSelect dropdown
//   - the dot color shown next to the status in both views
//
// To add a status: append one entry here. No other file needs to change.

export interface StatusSpec {
  key: string;
  label: string;
  color: string;
}

// Funnel order: leads at the top (`new` → `to_apply` → `applied`), live
// engagement in the middle (`interviewing` → `offer`), terminal states at the
// bottom (`rejected` → `not_interested`). Mirrors the natural flow of a role
// through the pipeline so the dashboard reads top-down as a funnel.
export const STATUSES: StatusSpec[] = [
  { key: "offer", label: "Offer", color: "var(--jst-status-offer)" },
  { key: "interviewing", label: "Active", color: "var(--jst-ok)" },
  { key: "new", label: "New", color: "var(--jst-status-new)" },
  { key: "to_apply", label: "To apply", color: "var(--jst-status-to-apply)" },
  { key: "applied", label: "Applied", color: "var(--jst-status-applied)" },
  { key: "rejected", label: "Rejected", color: "var(--jst-status-rejected)" },
  { key: "not_interested", label: "Not interested", color: "var(--jst-status-not-interested)" },
];

export const STATUS_KEYS: string[] = STATUSES.map((s) => s.key);

const STATUS_COLOR_MAP = new Map(STATUSES.map((s) => [s.key, s.color]));
const STATUS_LABEL_MAP = new Map(STATUSES.map((s) => [s.key, s.label]));

const FALLBACK_COLOR = "var(--jst-status-rejected)";

export function statusColor(status: string): string {
  return STATUS_COLOR_MAP.get(status) ?? FALLBACK_COLOR;
}

export function statusLabel(status: string): string {
  return STATUS_LABEL_MAP.get(status) ?? status;
}
