import { test, expect } from "@playwright/test";
import { LoginPage } from "../pages/LoginPage";

test.use({ storageState: "playwright/.auth/user.json" });

test.describe("Smoke", () => {
  test("@smoke product grid loads with seeded items", async ({ page }) => {
    const products = page.locator(".card.product");
    await page.goto("/products");
    await expect(products).toHaveCount(8);
    await expect(page.locator(".card.product").first()).toContainText("$");
  });

  test("@smoke add to cart increments badge", async ({ page }) => {
    await page.goto("/products");
    await page.locator(".card.product").first().locator(".add-to-cart").click();
    await expect(page.locator("#cart-count")).toHaveText("1");
  });

  test("@smoke login with invalid credentials shows error", async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.open();
    await loginPage.login("demo", "wrong-password");
    await expect(loginPage.errorBox).toBeVisible();
    await expect(loginPage.errorBox).toContainText("Invalid username or password.");
  });
});
