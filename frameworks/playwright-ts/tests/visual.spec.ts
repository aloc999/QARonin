import { test, expect } from "@playwright/test";

test.use({ storageState: "playwright/.auth/user.json" });

// Baselines are generated per-browser; only chromium baselines are committed.
test.beforeEach(async ({ browserName }) => {
  test.skip(
    browserName !== "chromium",
    "visual baselines are maintained for chromium only"
  );
});

const PAGES: Array<[string, string]> = [
  ["/login", "login"],
  ["/products", "products"],
  ["/cart", "cart"],
];

for (const [pagePath, name] of PAGES) {
  test(`@visual @regression visual baseline: ${name}`, async ({ page }) => {
    await page.goto(pagePath);
    await page.waitForLoadState("networkidle");
    await expect(page).toHaveScreenshot(`${name}.png`, {
      fullPage: true,
      maxDiffPixelRatio: 0.02,
    });
  });
}
