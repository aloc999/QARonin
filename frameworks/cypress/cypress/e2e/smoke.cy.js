// Smoke: product grid, add-to-cart badge, invalid login (mirrors TS/C# @smoke).
describe("Smoke", () => {
  beforeEach(() => {
    cy.clearCart();
  });

  it("product grid loads with seeded items", () => {
    cy.login();
    cy.get(".card.product").should("have.length", 8);
    cy.get(".card.product").first().should("contain", "$");
  });

  it("add to cart increments badge", () => {
    cy.login();
    cy.addToCart(0);
    cy.get("#cart-count").should("have.text", "1");
  });

  it("login with invalid credentials shows error", () => {
    cy.visit("/login");
    cy.get("#username").type("demo");
    cy.get("#password").type("wrong-password");
    cy.get("#login-form button[type=submit]").click();
    cy.get("#login-error").should("be.visible").and("contain", "Invalid username or password.");
  });
});
