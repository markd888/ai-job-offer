import { useMemo } from "react";

import type { Position } from "../types";
import { computeFunnel } from "./funnel";

interface Props {
  companies: Position[];
}

export function MiniFunnel({ companies }: Props) {
  const steps = useMemo(() => computeFunnel(companies), [companies]);
  const top = steps[0]?.count || 1;

  return (
    <section className="jst-card" aria-labelledby="minifunnel-h" style={{ padding: 20, display: "flex", flexDirection: "column", gap: 12 }}>
      <h2 id="minifunnel-h" className="jst-h3">Funnel</h2>
      {steps.map((s, i) => (
        <div key={s.stage} style={{ display: "grid", gridTemplateColumns: "84px minmax(0, 1fr) 40px", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 13, color: "var(--jst-ink-2)" }}>{s.label}</span>
          <div className="jst-bar-track" style={{ height: 18, borderRadius: 4 }}>
            <div
              className="jst-bar-fill"
              style={{ width: `${(s.count / top) * 100}%`, minWidth: s.count ? 4 : 0, opacity: 1 - i * 0.15 }}
            />
          </div>
          <span className="jst-num" style={{ fontSize: 13, textAlign: "right" }}>{s.count}</span>
        </div>
      ))}
    </section>
  );
}
