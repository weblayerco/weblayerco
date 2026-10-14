import type { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
  appId: "co.weblayer.noor",
  appName: "نور",
  webDir: "dist",
  // The deployed backend URL goes here when packaging for stores; until then,
  // the app falls back to the local heuristic + parent confirmation.
  server: {
    androidScheme: "https",
  },
};

export default config;
