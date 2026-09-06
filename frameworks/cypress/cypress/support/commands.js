// Custom commands mirroring the TS/C# page objects: login, cart, isolation.
Cypress.Commands.add("login", (username = "demo", password = "demo1234") => {
  return cy
    .request("POST", "/api/auth/login", { username, password })
    .then(({ body }) => {
      const { access_token, username: u, role } = body;
      cy.visit("/products", {
        onBeforeLoad(win) {
          win.localStorage.setItem("token", access_token);
          win.localStorage.setItem("username", u);
          win.localStorage.setItem("role", role);
        },
      });
    });
});

Cypress.Commands.add("addToCart", (index = 0) => {
  cy.get(".card.product").eq(index).find(".add-to-cart").click();
});

Cypress.Commands.add("clearCart", () => {
  cy.visit("/products", {
    onBeforeLoad(win) {
      win.localStorage.setItem("cart", "[]");
    },
  });
});
