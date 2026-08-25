import { Page } from "@playwright/test";

export class BasePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  async goto(path: string) {
    await this.page.goto(path);
  }

  cartCount() {
    return this.page.locator("#cart-count");
  }

  userBadge() {
    return this.page.locator("#user-badge");
  }

  logoutButton() {
    return this.page.locator("#logout-btn");
  }
}
