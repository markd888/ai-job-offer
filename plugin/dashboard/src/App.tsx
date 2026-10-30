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
import { longDate } from "./dates";
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
      <div style={{ display: "flex", flexWrap: "wrap", gap: 24, alignItems: "flex-start" }}>
        <main style={{ flex: "999 1 640px", minWidth: 0, display: "flex", flexDirection: "column", gap: 24 }}>
          <ActiveRoles companies={state.companies} onOpen={setOpenPosition} onChange={refresh} />
          <TodayFocus brief={state.latest_brief} />
          <ApplicationsTable companies={state.companies} onChange={refresh} onOpen={setOpenPosition} />
        </main>
        <aside style={{ flex: "1 1 340px", minWidth: 0, display: "flex", flexDirection: "column", gap: 24 }}>
          <WeekProgress strategy={state.strategy} weeklyProgress={state.weekly_progress} />
          <ComingUp companies={state.companies} onOpen={setOpenPosition} />
          <HeadsUp brief={state.latest_brief} />
          <MiniFunnel companies={state.companies} />
        </aside>
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
      <div style={{ maxWidth: 1360, margin: "0 auto", padding: "24px clamp(16px, 3vw, 40px) 64px", display: "flex", flexDirection: "column", gap: 24 }}>
        <Header weekDay={state?.weekly_progress.window_days} />
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

function Header({ weekDay }: { weekDay?: number }) {
  return (
    <header style={{ display: "flex", flexWrap: "wrap", alignItems: "center", justifyContent: "space-between", gap: 16 }}>
      <h1 style={{ margin: 0, fontSize: 15, fontWeight: 700, letterSpacing: "-0.01em" }}>job-offer</h1>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <p className="jst-num jst-muted" style={{ margin: 0, fontSize: 13 }}>
          {longDate(new Date())}
          {weekDay !== undefined && ` · week day ${weekDay}/7`}
        </p>
        <ThemeToggle />
      </div>
    </header>
  );
}

function ThemeToggle() {
  const { setColorScheme } = useMantineColorScheme();
  const scheme = useComputedColorScheme("dark");
  const next = scheme === "dark" ? "light" : "dark";
  return (
    <Tooltip label={`Switch to ${next} mode`} withArrow>
      <ActionIcon
        variant="default"
        size={44}
        radius="md"
        onClick={() => setColorScheme(next)}
        aria-label={`Switch to ${next} mode`}
      >
        {scheme === "dark" ? <IconSun size={18} stroke={1.8} /> : <IconMoon size={18} stroke={1.8} />}
      </ActionIcon>
    </Tooltip>
  );
}
