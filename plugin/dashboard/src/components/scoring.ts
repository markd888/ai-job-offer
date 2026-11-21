import type { Position } from "../types";

/** Scoring v1 is 3–15 (`score`), v2 is 0–100 (`fit_score`): never compare them. */
export function isV2(p: Position): boolean {
  return p.scoring_version === "2";
}

export function tierRank(p: Position): number {
  return ({ P0: 0, P1: 1, P2: 2, P3: 3 } as Record<string, number>)[p.tier] ?? 4;
}

/** Order inside a status group: tier first; within a tier, v2 roles (by fit) before
 *  v1 roles (by their old score), so the two scales are never compared numerically. */
export function compareRoles(a: Position, b: Position): number {
  const t = tierRank(a) - tierRank(b);
  if (t) return t;
  const va = isV2(a), vb = isV2(b);
  if (va !== vb) return va ? -1 : 1;
  const sa = Number(va ? a.fit_score : a.score) || 0;
  const sb = Number(vb ? b.fit_score : b.score) || 0;
  return sb - sa;
}

/** Plain-words note for the tier badge, or null when there's nothing to flag. */
export function scoringNote(p: Position): { label: string; tone: "warn" | "muted" } | null {
  if (!isV2(p)) return null;
  if (p.eligibility === "blocked") return { label: "Requirement not met", tone: "warn" };
  if (p.eligibility === "needs_review") return { label: "Check requirements", tone: "warn" };
  if (p.evidence_confidence === "low") return { label: "Thin evidence", tone: "muted" };
  return null;
}

export function scoringTooltip(p: Position): string | null {
  if (!isV2(p)) return null;
  const elig = { eligible: "meets the stated requirements", needs_review: "some requirements unclear from the posting",
                 blocked: "a stated requirement isn't met" }[p.eligibility ?? ""] ?? "requirements not checked";
  const conf = { high: "well backed by your CV", medium: "partly backed by your CV",
                 low: "little in your CV to go on" }[p.evidence_confidence ?? ""] ?? "";
  const over = p.tier_override ? " You changed this rating yourself." : "";
  return `Fit: ${elig}${conf ? `; ${conf}` : ""}.${over}`;
}
