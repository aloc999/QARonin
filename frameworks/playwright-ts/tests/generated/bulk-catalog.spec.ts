import { test, expect } from "@playwright/test";
import { CATALOG, CatalogProduct } from "./catalog.fixture";

/**
 * Bulk catalog suite: 8 seeded products x 15 read-only checks = 120 cases.
 * Product data mirrors `apps/demo-target/app/seed.py` (see catalog.fixture.ts).
 * All checks are read-only (no cart/order mutations) so cases stay independent
 * sharing one seeded backend. Tagged @regression: runs in L2/L3, not in L0.
 */

test.use({ storageState: "playwright/.auth/user.json" });

function card(page: import("@playwright/test").Page, p: CatalogProduct) {
  return page.locator(`article.card.product[data-product-id="${p.id}"]`);
}

interface BulkCheck {
  id: string;
  run: (page: import("@playwright/test").Page, p: CatalogProduct) => Promise<void>;
}

const CHECKS: BulkCheck[] = [
  { id: "card-visible", run: async (page, p) => {
    await expect(card(page, p)).toBeVisible();
  } },
  { id: "name", run: async (page, p) => {
    await expect(card(page, p).locator("h3")).toContainText(p.name);
  } },
  { id: "description", run: async (page, p) => {
    await expect(card(page, p).locator("p")).toContainText(p.description);
  } },
  { id: "price-text", run: async (page, p) => {
    await expect(card(page, p).locator(".price")).toHaveText(p.priceText);
  } },
  { id: "data-price", run: async (page, p) => {
    await expect(card(page, p)).toHaveAttribute("data-price", String(p.price));
  } },
  { id: "button-visible", run: async (page, p) => {
    await expect(card(page, p).locator(".add-to-cart")).toContainText("Add to cart");
  } },
  { id: "button-data-id", run: async (page, p) => {
    await expect(card(page, p).locator(".add-to-cart")).toHaveAttribute("data-id", String(p.id));
  } },
  { id: "button-data-name", run: async (page, p) => {
    await expect(card(page, p).locator(".add-to-cart")).toHaveAttribute("data-name", p.name);
  } },
  { id: "card-art", run: async (page, p) => {
    await expect(card(page, p).locator(".card-art")).not.toBeEmpty();
  } },
  { id: "price-positive", run: async (page, p) => {
    const text = await card(page, p).locator(".price").textContent();
    expect(parseFloat((text || "").replace("$", ""))).toBe(p.price);
  } },
  { id: "heading-visible", run: async (page, p) => {
    await expect(card(page, p).locator("h3")).toBeVisible();
  } },
  { id: "button-enabled", run: async (page, p) => {
    await expect(card(page, p).locator(".add-to-cart")).toBeEnabled();
  } },
  { id: "card-class", run: async (page, p) => {
    await expect(card(page, p)).toHaveClass(/product/);
  } },
  { id: "article-tag", run: async (page, p) => {
    expect(await card(page, p).evaluate((el) => el.tagName)).toBe("ARTICLE");
  } },
  { id: "grid-singleton", run: async (page, p) => {
    await expect(page.locator(`#product-grid article[data-product-id="${p.id}"]`)).toHaveCount(1);
  } },
];

for (const product of CATALOG) {
  for (const check of CHECKS) {
    test(`@regression bulk catalog [${product.id}] ${product.name} — ${check.id}`, async ({ page }) => {
      await page.goto("/products");
      await check.run(page, product);
    });
  }
}
