import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests/browser",
  timeout: 30000,
  use: { baseURL: "http://localhost:8443", browserName: "chromium", headless: true },
  reporter: "list",
});
// Manual application servers must be running: frontend :8443, backend :8000.
