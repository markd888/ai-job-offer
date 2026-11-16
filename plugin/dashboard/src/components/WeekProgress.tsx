import { Code } from "@mantine/core";
import { IconCheck } from "@tabler/icons-react";

import type { Strategy, WeeklyProgress } from "../types";

interface Props {
  strategy: Strategy;
  weeklyProgress: WeeklyProgress;
}

export function WeekProgress({ strategy, weeklyProgress }: Props) {
  const day = Math.min(7, Math.max(0, weeklyProgress.window_days));
  const targets = Object.entries(strategy.weekly_targets ?? {});

  return (
    <section className="jst-rail-sec" aria-labelledby="week-h">
      <div className="jst-rail-head">
        <h2 id="week-h" className="jst-h3">This week</h2>
        <div className="jst-ticks" aria-label={`Day ${day} of 7`} role="img">
          {Array.from({ length: 7 }, (_, i) => (
            <span key={i} className={`jst-tick${i < day ? "" : " jst-tick-off"}`} />
          ))}
        </div>
      </div>

      {targets.length === 0 && (
        <p className="jst-meta">
          No weekly targets. Run <Code>/job-offer:setup</Code> to set them.
        </p>
      )}

      {targets.map(([key, target]) => {
        const count = (weeklyProgress as unknown as Record<string, number>)[key] ?? 0;
        return <TargetBar key={key} label={prettify(key)} count={count} target={target} day={day} />;
      })}
    </section>
  );
}

// A met target goes quiet (green bar, a tick by the count); only targets that
// still need work get a line of text under the bar.
function TargetBar({ label, count, target, day }: { label: string; count: number; target: number; day: number }) {
  const expected = (target * day) / 7;
  const left = Math.max(0, target - count);
  const daysLeft = 7 - day;
  const done = left === 0;
  const behind = !done && count < expected;
  const hint = done
    ? null
    : behind
      ? `Behind pace — ${left} to go in ${daysLeft} ${daysLeft === 1 ? "day" : "days"}`
      : `On pace — ${left} to go`;

  return (
    <div className="jst-target">
      <div className="jst-target-row">
        <span>{label}</span>
        <span className="jst-target-count jst-num">
          {done && (
            <span className="jst-target-done" role="img" aria-label="Done for the week">
              <IconCheck size={14} stroke={2.4} />
            </span>
          )}
          <span><strong>{count}</strong> / {target}</span>
        </span>
      </div>
      <div className="jst-bar-track">
        <div className={`jst-bar-fill${done ? " jst-bar-done" : ""}`} style={{ width: `${Math.min(100, (count / Math.max(1, target)) * 100)}%` }} />
      </div>
      {hint && <p className={`jst-target-hint${behind ? " jst-target-hint-warn" : ""}`}>{hint}</p>}
    </div>
  );
}

function prettify(label: string): string {
  const s = label.replace(/_/g, " ");
  return s.charAt(0).toUpperCase() + s.slice(1);
}
