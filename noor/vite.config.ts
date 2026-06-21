import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";

// SINGLE_FILE=1 produces one self-contained dist/index.html that can be opened
// directly (double-click) without any server.
const single = process.env.SINGLE_FILE === "1";

export default defineConfig({
  // Relative base makes the same build work everywhere: served at any URL
  // path, inside Capacitor's WebView (file://), or as a single file.
  base: "./",
  plugins: [react(), ...(single ? [viteSingleFile()] : [])],
  server: { host: true },
});
