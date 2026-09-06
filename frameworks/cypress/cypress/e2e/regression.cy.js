// E2E: purchase flow + RBAC negative + logout (mirrors TS @e2e/@regression).
describe("Regression", () => {
  beforeEach(() => {
    cy.clearCart();
    cy.login();
  });

  it("add two products, cart badge shows 2 (AE-12)", () => {
    cy.addToCart(0);
    cy.addToCart(1);
    cy.get("#cart-count").should("have.text", "2");
  });

  it("admin RBAC negative for user session", () => {
    cy.window().then((win) => {
      const token = win.localStorage.getItem("token");
      cy.request({
        url: "/api/admin/orders",
        headers: { Authorization: `Bearer ${token}` },
        failOnStatusCode: false,
      }).then((res) => {
        expect(res.status).to.eq(403);
      });
    });
  });

  it("logout clears session and redirects to login (AE-4)", () => {
    cy.get("#user-badge").should("have.text", "demo");
    cy.get("#logout-btn").click();
    cy.url().should("match", /\/login$/);
    cy.window().then((win) => {
      expect(win.localStorage.getItem("token")).to.be.null;
    });
  });

  it("cart persists across reload", () => {
    cy.addToCart(1);
    cy.reload();
    cy.get("#cart-count").invoke("text").then((t) => {
      expect(parseInt(t, 10)).to.be.gte(1);
    });
  });
});
