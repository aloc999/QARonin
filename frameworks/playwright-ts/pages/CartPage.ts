import { Locator, Page, expect } from "@playwright/test";
import { BasePage } from "./BasePage";

export class CartPage extends BasePage {
  readonly cartRows: Locator = this.page.locator("#cart-table tbody tr.cart-row");
  readonly cartTotal = this.page.locator("#cart-total");
  readonly placeOrderButton = this.page.locator("#place-order-btn");
  readonly orderId = this.page.locator("#order-id");
  readonly orderTotal = this.page.locator("#order-total");
  readonly confirmation = this.page.locator("#order-confirmation");
  readonly emptyState = this.page.locator("#cart-empty");

  constructor(page: Page) {
    super(page);
  }

  async open() {
    await this.goto("/cart");
  }

  async removeItem(productName: string) {
    const row = this.cartRows.filter({ hasText: productName });
    await row.first().locator(".remove-item").click();
  }

  async expectRowCount(count: number) {
    await expect(this.cartRows).toHaveCount(count);
  }

  async checkout() {
    await this.placeOrderButton.click();
  }

  async expectOrderConfirmed() {
    await expect(this.confirmation).toBeVisible();
    await expect(this.orderId).toContainText(/^#\d+$/);
    return (await this.orderId.textContent())?.trim() ?? "";
  }
}
