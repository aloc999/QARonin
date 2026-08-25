import { test, expect } from "@playwright/test";
import { ProductsPage } from "../pages/ProductsPage";
import { CartPage } from "../pages/CartPage";

test.use({ storageState: "playwright/.auth/user.json" });

test("@e2e full purchase flow: add two items, checkout, order id shown", async ({ page }) => {
  const productsPage = new ProductsPage(page);
  const cartPage = new CartPage(page);

  await productsPage.open();
  await expect(productsPage.productCards).toHaveCount(8);

  await productsPage.addToCart("Katana Letter Opener");
  await productsPage.addToCart("Zen Garden Starter Kit");
  await expect(productsPage.cartCount()).toHaveText("2");

  await cartPage.open();
  await cartPage.expectRowCount(2);
  await expect(cartPage.cartTotal).toHaveText("$79.49");

  await cartPage.checkout();
  const orderId = await cartPage.expectOrderConfirmed();
  expect(orderId).toMatch(/^#\d+$/);
});
