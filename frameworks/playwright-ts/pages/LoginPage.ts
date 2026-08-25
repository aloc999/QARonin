import { Page } from "@playwright/test";
import { BasePage } from "./BasePage";

export class LoginPage extends BasePage {
  readonly usernameInput = this.page.locator("#username");
  readonly passwordInput = this.page.locator("#password");
  readonly submitButton = this.page.locator("#login-form button[type=submit]");
  readonly errorBox = this.page.locator("#login-error");

  constructor(page: Page) {
    super(page);
  }

  async open() {
    await this.goto("/login");
  }

  async login(username: string, password: string) {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
