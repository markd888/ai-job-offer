import "@mantine/core/styles.css";
import "./theme.css";

import { MantineProvider, createTheme, type CSSVariablesResolver } from "@mantine/core";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";

const theme = createTheme({
  fontFamily: "Geist, system-ui, -apple-system, 'Segoe UI', sans-serif",
  fontFamilyMonospace: "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace",
  headings: { fontFamily: "Geist, system-ui, -apple-system, 'Segoe UI', sans-serif" },
  primaryColor: "cobalt",
  primaryShade: { light: 8, dark: 6 },
  defaultRadius: "md",
  colors: {
    cobalt: ["#eef2ff", "#dbe3ff", "#b6c6ff", "#8ea6ff", "#6b89fb", "#4f71f8", "#3d63f5", "#2f54e0", "#2447d6", "#1a34a3"],
    // Matches the --jst-* dark tokens in theme.css so Mantine popovers,
    // inputs and the drawer sit on the same greys as the rest of the page.
    dark: ["#eceef2", "#c4c9d3", "#9aa2b1", "#6b7280", "#3a404c", "#262b35", "#1f232c", "#161920", "#0e1015", "#08090c"],
  },
});

// Popovers, dropdowns and the drawer paint with --mantine-color-body, so keep
// it on the card surface; the page background itself comes from theme.css.
const cssVariablesResolver: CSSVariablesResolver = () => ({
  variables: {},
  light: { "--mantine-color-body": "#ffffff", "--mantine-color-text": "#12151c", "--mantine-color-dimmed": "#5b6270" },
  dark: { "--mantine-color-body": "#161920", "--mantine-color-text": "#eceef2", "--mantine-color-dimmed": "#9aa2b1" },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <MantineProvider theme={theme} cssVariablesResolver={cssVariablesResolver} defaultColorScheme="dark">
      <App />
    </MantineProvider>
  </StrictMode>,
);
