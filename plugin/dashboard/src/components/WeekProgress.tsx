import { Code } from "@mantine/core";

import type { Strategy, WeeklyProgress } from "../types";

interface Props {
  strategy: Strategy;
  weeklyProgress: WeeklyProgress;
}

export function WeekProgress({ strategy, weeklyProgress }: Props) {
  const day = Math.min(7, Math.max(0, weeklyProgress.window_days));
  const targets = Object.entries(strategy.weekly_targets ?? {});
  const offerDays = daysUntil(strategy.target_offer_date);

  return (
    <section className="jst-card" aria-labelledby="week-h" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 18 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h2 id="week-h" className="jst-h3">This week</h2>
        <div aria-label={`Day ${day} of 7`} role="img" style={{ display: "flex", gap: 4 }}>
          {Array.from({ length: 7 }, (_, i) => (
            <span key={i} className={`jst-tick${i < day ? "" : " jst-tick-off"}`} />
          ))}
        </div>
      </div>

      {targets.length === 0 && (
        <p className="jst-muted" style={{ margin: 0, fontSize: 13 }}>
          No weekly targets. Run <Code>/job-offer:setup</Code> to set them.
        </p>
      )}

      {targets.map(([key, target]) => {
        const count = (weeklyProgress as unknown as Record<string, number>)[key] ?? 0;
        return <TargetBar key={key} label={prettify(key)} count={count} target={target} day={day} />;
      })}

      {offerDays !== null && (
        <p className="jst-muted jst-num" style={{ margin: 0, fontSize: 13, paddingTop: 12, borderTop: "1px solid var(--jst-divider)" }}>
          Offer target {strategy.target_offer_date} · {offerDays} days left
        </p>
      )}
    </section>
  );
}

function TargetBar({ label, count, target, day }: { label: string; count: number; target: number; day: number }) {
  const expected = (target * day) / 7;
  const left = Math.max(0, target - count);
  const daysLeft = 7 - day;
  let hint: { text: string; warn: boolean };
  if (left === 0) hint = { text: "Done for the week", warn: false };
  else if (count < expected) hint = { text: `Behind pace — ${left} to go in ${daysLeft} ${daysLeft === 1 ? "day" : "days"}`, warn: true };
  else hint = { text: `On pace — ${left} to go`, warn: false };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 14 }}>
        <span>{label}</span>
        <span className="jst-num"><strong>{count}</strong> / {target}</span>
      </div>
      <div className="jst-bar-track" style={{ height: 8 }}>
        <div className="jst-bar-fill" style={{ width: `${Math.min(100, (count / Math.max(1, target)) * 100)}%` }} />
      </div>
      <p style={{ margin: 0, fontSize: 13, color: hint.warn ? "var(--jst-warn-fg)" : "var(--jst-muted)" }}>{hint.text}</p>
    </div>
  );
}

function daysUntil(iso: string | undefined): number | null {
  if (!iso) return null;
  const t = Date.parse(iso);
  if (Number.isNaN(t)) return null;
  return Math.max(0, Math.ceil((t - Date.now()) / (24 * 60 * 60 * 1000)));
}

function prettify(label: string): string {
  const s = label.replace(/_/g, " ");
  return s.charAt(0).toUpperCase() + s.slice(1);
}
