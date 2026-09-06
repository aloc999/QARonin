import { defineConfig, devices } from "@playwright/test";

const BASE_URL = process.env.BASE_URL || "http://127.0.0.1:8199";
const isCI = !!process.env.CI;
// ALLURE=1 adds the Allure reporter (needs allure-playwright installed).
// Default stays list+junit so local runs need no extra deps.
const reporters: Array<[string, Record<string, unknown>?] | string> = [
  ["list"],
  ["junit", { outputFile: "junit.xml" }],
];
if (process.env.ALLURE === "1") {
  reporters.push(["allure-playwright", { outputFolder: "allure-results" }]);
}

export default defineConfig({
  testDir: "./tests",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  forbidOnly: isCI,
  retries: isCI ? 2 : 1,
  workers: process.env.WORKERS ? parseInt(process.env.WORKERS, 10) : 2,
  reporter: reporters,
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
    // WebKit runs nightly only (WEBKIT=1): `npx playwright test --project=webkit`.
    // Kept out of the default gate for speed; CI installs it with --with-deps.
    ...(process.env.WEBKIT === "1"
      ? [
          {
            name: "webkit",
            use: { ...devices["Desktop Safari"] },
            dependencies: ["setup"],
          },
        ]
      : []),
  ],
});
