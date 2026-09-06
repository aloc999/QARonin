import { test, expect, request } from "@playwright/test";
import { fetchWithRetry } from "./helpers/retry-fetch";
import { CartPage } from "../pages/CartPage";

const BASE_URL = process.env.BASE_URL || "http://127.0.0.1:8199";

test.use({ storageState: "playwright/.auth/user.json" });

test.describe("Regression", () => {
  test("@regression flaky endpoint eventually succeeds with retry-with-backoff", async ({ request }) => {
    let saw503 = false;
    let finalBody: { status?: string } | null = null;

    for (let run = 0; run < 3; run++) {
      try {
        const res = await fetchWithRetry(`${BASE_URL}/api/flaky`, {}, { maxAttempts: 6 });
        finalBody = (await res.json()) as { status?: string };
        break;
      } catch (err) {
        saw503 = true;
        if (run === 2) throw err;
      }
    }

    if (saw503) {
      console.log("flaky endpoint returned 503 at least once; retry helper recovered");
    }
    expect(finalBody?.status).toBe("ok");
  });

  test("@regression admin RBAC negative check via UI session", async ({ page }) => {
    await page.goto("/products");
    const token = await page.evaluate(() => localStorage.getItem("token"));
    const res = await page.request.get(`${BASE_URL}/api/admin/orders`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(res.status()).toBe(403);
    const body = await res.json();
    expect(body.detail).toBe("Admin role required");
  });

  test("@regression cart persists across reload", async ({ page }) => {
    await page.goto("/products");
    await page.locator(".card.product").nth(1).locator(".add-to-cart").click();
    // Explicit condition: badge reflects the persisted cart (localStorage is
    // written synchronously on click; the assertion auto-retries, no sleeps).
    await expect(page.locator("#cart-count")).toHaveText("1");

    await page.reload();
    // After reload the badge is rehydrated from localStorage on
    // DOMContentLoaded; wait for that state, not a fixed timeout.
    await expect(page.locator("#cart-count")).not.toBeEmpty();
    const count = await page.locator("#cart-count").textContent();
    expect(parseInt(count ?? "0", 10)).toBeGreaterThanOrEqual(1);
  });

  test("@regression logout clears session and redirects to login", async ({ page }) => {
    await page.goto("/products");
    await expect(page.locator("#user-badge")).toHaveText("demo");
    await page.locator("#logout-btn").click();
    await expect(page).toHaveURL(/\/login$/);

    const token = await page.evaluate(() => localStorage.getItem("token"));
    expect(token).toBeNull();
  });
});
