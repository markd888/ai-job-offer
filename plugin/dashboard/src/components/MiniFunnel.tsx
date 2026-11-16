import { Fragment, useMemo } from "react";

import type { FunnelByChannel, Position } from "../types";
import { computeFunnel } from "./funnel";

interface Props {
  companies: Position[];
  byChannel?: FunnelByChannel;
}

const CHANNEL_LABEL: Record<string, string> = {
  referral: "Referral",
  cold: "Cold",
  recruiter: "Recruiter",
  linkedin: "LinkedIn",
  "company-site": "Careers site",
  other: "Other",
  unknown: "Not recorded",
};

export function MiniFunnel({ companies, byChannel }: Props) {
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
      {byChannel && <ChannelTable data={byChannel} />}
    </section>
  );
}

/** Channel × stage, from /sent's `channel`. Rates are hidden under min_sample
 * applications — a 1-of-1 offer rate says nothing. Shown once at least one
 * application has a channel recorded. */
function ChannelTable({ data }: { data: FunnelByChannel }) {
  if (!data.rows.some((r) => r.channel !== "unknown")) return null;
  const cell = (n: number, rate: number | null) => (
    <td className="jst-num">
      {n}
      {rate !== null && <span className="jst-channel-rate"> {formatRate(rate)}</span>}
    </td>
  );
  return (
    <div className="jst-channel">
      <div className="jst-rail-head">
        <h3 className="jst-label">By channel</h3>
        <span className="jst-label">% of applied</span>
      </div>
      <table className="jst-channel-table">
        <thead>
          <tr>
            <th scope="col">Channel</th>
            <th scope="col">Applied</th>
            <th scope="col">Screen</th>
            <th scope="col">Interview</th>
            <th scope="col">Offer</th>
          </tr>
        </thead>
        <tbody>
          {data.rows.map((r) => (
            <tr key={r.channel} className={r.small_sample || r.channel === "unknown" ? "jst-channel-thin" : undefined}>
              <th scope="row">{CHANNEL_LABEL[r.channel] ?? r.channel}</th>
              <td className="jst-num">{r.applied}</td>
              {cell(r.screening, r.screening_rate)}
              {cell(r.interview, r.interview_rate)}
              {cell(r.offer, r.offer_rate)}
            </tr>
          ))}
        </tbody>
      </table>
      {data.rows.some((r) => r.small_sample && r.channel !== "unknown") && (
        <p className="jst-channel-note">Rates show from {data.min_sample} applications per channel.</p>
      )}
    </div>
  );
}

function formatRate(r: number): string {
  const pct = r * 100;
  if (pct === 0) return "0%";
  return pct < 10 ? `${pct.toFixed(1).replace(/\.0$/, "")}%` : `${Math.round(pct)}%`;
}
