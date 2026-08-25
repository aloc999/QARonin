import { defineConfig, devices } from "@playwright/test";

const BASE_URL = process.env.BASE_URL || "http://127.0.0.1:8199";
const isCI = !!process.env.CI;

export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 2 : 1,
  workers: process.env.WORKERS ? parseInt(process.env.WORKERS, 10) : 2,
  reporter: [["list"], ["junit", { outputFile: "junit.xml" }]],
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    {
      name: "setup",
      testMatch: /global-setup\.ts/,
    },
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
      dependencies: ["setup"],
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
      dependencies: ["setup"],
    },
  ],
});
