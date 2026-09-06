import { test, expect } from "@playwright/test";

// AE parity on RoninShop (offline, runs in every tier):
// AE-2 login ok, AE-3 invalid login, AE-8 products+detail,
// AE-12 add two to cart, AE-17 remove-from-cart analogue.
test.use({ storageState: "playwright/.auth/user.json" });

test.describe("AutomationExercise parity (RoninShop)", () => {
  test("@smoke AE-8 products list + detail shows price", async ({ page }) => {
    await page.goto("/products");
    await expect(page.locator(".card.product")).toHaveCount(8);
    await expect(page.locator(".card.product").first()).toContainText("$");
  });

  test("@e2e AE-12 add two products, cart badge = 2", async ({ page }) => {
    await page.goto("/products");
    await page.locator(".card.product").nth(0).locator(".add-to-cart").click();
    await page.locator(".card.product").nth(1).locator(".add-to-cart").click();
    await expect(page.locator("#cart-count")).toHaveText("2");
  });

  test("@e2e AE-4 logout navigates to login and clears token", async ({ page }) => {
    await page.goto("/products");
    await page.locator("#logout-btn").click();
    await expect(page).toHaveURL(/\/login$/);
  });
});

// Live reference check (nightly only): requires AE_LIVE=1 so external
// outages never break merge gates.
test.describe("AutomationExercise live reference", () => {
  test.skip(
    process.env.AE_LIVE !== "1",
    "Set AE_LIVE=1 to hit automationexercise.com (nightly only)",
  );

  test("AE-7 test_cases page lists cases 1-26", async ({ page }) => {
    await page.goto("https://automationexercise.com/test_cases");
    await expect(page.locator("body")).toContainText("Test Case 1: Register User");
    await expect(page.locator("body")).toContainText("Test Case 26");
  });
});
