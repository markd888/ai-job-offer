import { Fragment, useMemo } from "react";

import type { Position } from "../types";
import { computeFunnel } from "./funnel";

interface Props {
  companies: Position[];
}

export function MiniFunnel({ companies }: Props) {
  const steps = useMemo(() => computeFunnel(companies), [companies]);
  const top = steps[0]?.count || 1;

  return (
    <section className="jst-rail-sec" aria-labelledby="minifunnel-h">
      <div className="jst-rail-head">
        <h2 id="minifunnel-h" className="jst-h3">Funnel</h2>
        <span className="jst-label">from previous stage</span>
      </div>
      <dl className="jst-funnel jst-num">
        {steps.map((s) => (
          <Fragment key={s.stage}>
            <dt>{s.label}</dt>
            <dd className="jst-bar-track" aria-hidden>
              <div className="jst-bar-fill jst-bar-neutral" style={{ width: `${(s.count / top) * 100}%`, minWidth: s.count ? 3 : 0 }} />
            </dd>
            <dd className="jst-funnel-count">{s.count}</dd>
            <dd className="jst-funnel-rate">{s.fromPrev === null ? "" : formatRate(s.fromPrev)}</dd>
          </Fragment>
        ))}
      </dl>
    </section>
  );
}

function formatRate(r: number): string {
  const pct = r * 100;
  if (pct === 0) return "0%";
  return pct < 10 ? `${pct.toFixed(1).replace(/\.0$/, "")}%` : `${Math.round(pct)}%`;
}
