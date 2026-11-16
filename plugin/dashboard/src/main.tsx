import "@mantine/core/styles.css";
import "./theme.css";

import { MantineProvider, createTheme, type CSSVariablesResolver } from "@mantine/core";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";

// claude.ai look: a sans UI with serif titles (the system serif: New York on
// macOS), a clay accent, and warm greys in place of Mantine's cool ones.
const SANS = "Geist, system-ui, -apple-system, 'Segoe UI', sans-serif";
const SERIF = "ui-serif, 'New York', 'Iowan Old Style', 'Palatino Linotype', Georgia, serif";

const theme = createTheme({
  fontFamily: SANS,
  fontFamilyMonospace: "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace",
  headings: { fontFamily: SERIF, fontWeight: "500" },
  primaryColor: "clay",
  // Shade 7 keeps white button text above 4.5:1 in both schemes.
  primaryShade: { light: 7, dark: 7 },
  defaultRadius: "md",
  colors: {
    clay: ["#fbf1ec", "#f6e0d5", "#efc3ad", "#e7a284", "#df8763", "#d97757", "#c96442", "#b0532f", "#8f4226", "#6e321d"],
    // Matches the --jst-* tokens in theme.css so Mantine popovers, inputs,
    // dropdowns and the drawer sit on the same warm greys as the page.
    dark: ["#f5f4ee", "#d9d6cb", "#a8a59b", "#85827a", "#4f4d47", "#3a3935", "#30302e", "#262624", "#1f1e1d", "#171716"],
    gray: ["#faf9f5", "#f5f4ee", "#edeae0", "#e2dfd3", "#c9c5b7", "#a8a59b", "#85827a", "#66645c", "#4a4842", "#2d2c28"],
  },
});

// Popovers, dropdowns and the drawer paint with --mantine-color-body, so keep
// it on the card surface; the page background itself comes from theme.css.
const cssVariablesResolver: CSSVariablesResolver = () => ({
  variables: {},
  light: {
    "--mantine-color-body": "#ffffff",
    "--mantine-color-text": "#1f1e1d",
    "--mantine-color-dimmed": "#66645c",
    "--mantine-color-placeholder": "#66645c",
    "--mantine-color-default-border": "#e2dfd3",
  },
  dark: {
    "--mantine-color-body": "#262624",
    "--mantine-color-text": "#f5f4ee",
    "--mantine-color-dimmed": "#a8a59b",
    "--mantine-color-placeholder": "#a8a59b",
    "--mantine-color-default-border": "#3a3935",
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <MantineProvider theme={theme} cssVariablesResolver={cssVariablesResolver} defaultColorScheme="dark">
      <App />
    </MantineProvider>
  </StrictMode>,
);
