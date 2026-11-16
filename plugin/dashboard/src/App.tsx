import { ActionIcon, Alert, Box, Loader, Tooltip, useComputedColorScheme, useMantineColorScheme } from "@mantine/core";
import { useMediaQuery } from "@mantine/hooks";
import { IconMoon, IconSun } from "@tabler/icons-react";
import { useCallback, useEffect, useRef, useState, type ReactNode } from "react";

import { fetchState } from "./api";
import { ActiveRoles } from "./components/ActiveRoles";
import { ApplicationsTable } from "./components/ApplicationsTable";
import { ComingUp } from "./components/ComingUp";
import { CompanyDrawer } from "./components/CompanyDrawer";
import { DemoBanner } from "./components/DemoBanner";
import { HeadsUp } from "./components/HeadsUp";
import { MiniFunnel } from "./components/MiniFunnel";
import { MobileLanding } from "./components/MobileLanding";
import { TodayFocus } from "./components/TodayFocus";
import { WeekProgress } from "./components/WeekProgress";
import { DEMO_MODE } from "./config";
import { daysUntil, humanizeIsoDates, longDate } from "./dates";
import type { DashboardState, Position } from "./types";

// Poll the state endpoint while the tab is visible so the dashboard
// reflects CLI mutations (/today, /evaluate-position, /interview-analysis)
// without manual page reloads. 5s is the sweet spot — feels live, payload
// is small, and matches the cadence at which a user typically switches
// terminal → browser after running a skill.
const POLL_INTERVAL_MS = 5000;

export function App() {
  // Resolve synchronously on first render (matchMedia is available client-side
  // in this static SPA) so the mobile landing doesn't flicker through the
  // desktop layout on initial paint.
  const isMobile = useMediaQuery("(max-width: 768px)", false, {
    getInitialValueInEffect: false,
  });
  const [state, setState] = useState<DashboardState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [openPosition, setOpenPosition] = useState<Position | null>(null);
  // Tracks in-flight requests so visibility-change refresh doesn't double-fire
  // mid-poll. Cheap belt-and-braces — fetch() would dedupe at the network
  // layer anyway, but this avoids racing setState calls.
  const inFlight = useRef(false);

  const refresh = useCallback(async () => {
    if (inFlight.current) return;
    inFlight.current = true;
    try {
      const next = await fetchState();
      setState(next);
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "unknown error");
    } finally {
      inFlight.current = false;
    }
  }, []);

  // Initial fetch.
  useEffect(() => {
    void refresh();
  }, [refresh]);

  // Visibility-aware polling. When the tab is hidden, we stop polling so
  // background tabs don't hammer the server. On becoming visible again we
  // refresh immediately (the user just switched back — probably to check
  // something that just happened) and resume the interval.
  //
  // Polling is disabled in demo mode — there's no external process mutating
  // state, so re-fetching every 5s would just churn React for no reason.
  useEffect(() => {
    if (DEMO_MODE) return;
    let interval: number | null = null;

    const start = () => {
      if (interval !== null) return;
      interval = window.setInterval(() => {
        if (document.visibilityState === "visible") void refresh();
      }, POLL_INTERVAL_MS);
    };

    const stop = () => {
      if (interval === null) return;
      window.clearInterval(interval);
      interval = null;
    };

    const handleVisibility = () => {
      if (document.visibilityState === "visible") {
        void refresh();
        start();
      } else {
        stop();
      }
    };

    document.addEventListener("visibilitychange", handleVisibility);
    if (document.visibilityState === "visible") start();

    return () => {
      document.removeEventListener("visibilitychange", handleVisibility);
      stop();
    };
  }, [refresh]);

  // Demo mode on a narrow viewport: replace the whole dashboard with a
  // landing page. Claude Code is a desktop CLI, so trying to interact with
  // the live demo on a phone is pointless — show the explainer + video
  // instead and steer visitors to install on a laptop.
  if (DEMO_MODE && isMobile) {
    return <MobileLanding />;
  }

  let body: ReactNode;
  if (error) {
    body = <Alert color="red" title="Failed to load dashboard state">{error}</Alert>;
  } else if (!state) {
    body = <Loader />;
  } else {
    body = (
      <div className="jst-grid">
        <div className="jst-area-active">
          <ActiveRoles companies={state.companies} onOpen={setOpenPosition} onChange={refresh} />
        </div>
        <div className="jst-area-focus">
          <TodayFocus brief={state.latest_brief} />
        </div>
        <Rail>
          <MiniFunnel companies={state.companies} byChannel={state.funnel_by_channel} />
          <WeekProgress strategy={state.strategy} weeklyProgress={state.weekly_progress} />
          <ComingUp companies={state.companies} onOpen={setOpenPosition} />
          <HeadsUp brief={state.latest_brief} />
        </Rail>
        <main className="jst-area-pipeline">
          <ApplicationsTable companies={state.companies} onChange={refresh} onOpen={setOpenPosition} />
        </main>
      </div>
    );
  }

  return (
    <>
      {DEMO_MODE && (
        <Box style={{ position: "sticky", top: 0, zIndex: 100 }}>
          <DemoBanner />
        </Box>
      )}
      <div className="jst-page">
        <TopBar weekDay={state?.weekly_progress.window_days} offerDate={state?.strategy.target_offer_date} />
        {body}
      </div>
      <CompanyDrawer
        opened={openPosition !== null}
        onClose={() => setOpenPosition(null)}
        folderPath={openPosition?.folder_path ?? ""}
        company={openPosition?.company ?? ""}
        position={openPosition?.position ?? ""}
        hasNotes={openPosition?.has_notes ?? false}
        link={openPosition?.link}
      />
    </>
  );
}

// Page title on the left; date, week day, offer countdown and theme switch on
// the right. One row above the grid, so every column starts on the same line.
function TopBar({ weekDay, offerDate }: { weekDay?: number; offerDate?: string }) {
  const offerDays = daysUntil(offerDate);
  return (
    <header className="jst-topbar">
      <h1 className="jst-topbar-title">Job search</h1>
      <ul className="jst-meta-list jst-num">
          <li><strong>{longDate(new Date())}</strong></li>
          {weekDay !== undefined && <li>Week day {weekDay}/7</li>}
          {offerDays !== null && offerDate && (
            <li>
              Offer target {humanizeIsoDates(offerDate)} · {offerDays} {offerDays === 1 ? "day" : "days"} left
            </li>
          )}
      </ul>
      <ThemeToggle />
    </header>
  );
}

// The rail keeps its content in view while a long Pipeline scrolls past. Its
// height feeds the sticky offset in theme.css (.jst-rail-inner): a rail taller
// than the window scrolls until its end shows, then sticks by its bottom edge.
function Rail({ children }: { children: ReactNode }) {
  const inner = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = inner.current;
    if (!el) return;
    const ro = new ResizeObserver(() => el.style.setProperty("--jst-rail-h", `${el.offsetHeight}px`));
    ro.observe(el);
    return () => ro.disconnect();
  }, []);
  return (
    <aside className="jst-area-rail jst-card jst-rail" aria-label="Week at a glance">
      <div ref={inner} className="jst-rail-inner">
        {children}
      </div>
    </aside>
  );
}

function ThemeToggle() {
  const { setColorScheme } = useMantineColorScheme();
  const scheme = useComputedColorScheme("dark");
  const next = scheme === "dark" ? "light" : "dark";
  return (
    <Tooltip label={`Switch to ${next} mode`} withArrow events={{ hover: true, focus: false, touch: false }}>
      <ActionIcon
        variant="default"
        size={32}
        className="jst-icon-action"
        radius="md"
        onClick={() => setColorScheme(next)}
        aria-label={`Switch to ${next} mode`}
      >
        {scheme === "dark" ? <IconSun size={16} stroke={1.8} /> : <IconMoon size={16} stroke={1.8} />}
      </ActionIcon>
    </Tooltip>
  );
}
