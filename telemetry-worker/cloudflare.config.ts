import { bindings, defineConfig } from "cf/config";
import * as entrypoint from "./src/index.ts" with { type: "cf-worker" };

export default defineConfig({
  worker: {
    name: "job-offer-telemetry",
    entrypoint,
    compatibilityDate: "2026-11-01",
    domains: ["job-offer.mark-d.dev"],
    workersDev: false,
    env: {
      DB: bindings.d1({ id: "acc7afff-ec09-4b3e-9093-abf9f834742e", name: "job-offer-telemetry" }),
      STATS_TOKEN: bindings.secret(),
    },
  },
});
