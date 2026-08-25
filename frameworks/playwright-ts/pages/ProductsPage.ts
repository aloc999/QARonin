import { Locator, Page, expect } from "@playwright/test";
import { BasePage } from "./BasePage";

export class ProductsPage extends BasePage {
  readonly productCards: Locator = this.page.locator(".card.product");

  constructor(page: Page) {
    super(page);
  }

  async open() {
    await this.goto("/products");
  }

  cardFor(name: string): Locator {
    return this.productCards.filter({ hasText: name });
  }

  async addToCart(productName: string) {
    await this.cardFor(productName).locator(".add-to-cart").click();
  }

  async expectProductCount(count: number) {
    await expect(this.productCards).toHaveCount(count);
  }

  async flashMessage() {
    return this.page.locator("#flash");
  }
}
