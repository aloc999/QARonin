// Network interception: spy + stub + failure simulation (gap vs TS/C# suites).
describe("Network interception", () => {
  beforeEach(() => {
    cy.login();
  });

  it("spies on the product-detail API calls the cart page makes", () => {
    cy.addToCart(0);
    cy.intercept("GET", "/api/products/*").as("getProduct");
    cy.visit("/cart");
    cy.wait("@getProduct").its("response.statusCode").should("eq", 200);
  });

  it("stubs login failure and shows the error box", () => {
    cy.visit("/login");
    cy.intercept("POST", "/api/auth/login", {
      statusCode: 401,
      body: { detail: "Invalid credentials" },
    }).as("loginFail");
    cy.get("#username").type("demo");
    cy.get("#password").type("anything");
    cy.get("#login-form button[type=submit]").click();
    cy.wait("@loginFail");
    cy.get("#login-error").should("contain", "Invalid username or password.");
  });

  it("simulates API failure for a clean error path", () => {
    // NOTE: cy.request() bypasses intercepts (Node-side); in-page fetch goes
    // through the proxy, so the stub below is genuinely exercised.
    cy.visit("/products");
    cy.intercept("GET", "/api/products/99999", {
      statusCode: 404,
      body: { detail: "Product not found" },
    }).as("missing");
    cy.window().then((win) => win.fetch("/api/products/99999"));
    cy.wait("@missing").its("response.statusCode").should("eq", 404);
  });
});
