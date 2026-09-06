import React from "react";
import { ProductCard } from "../../src/ProductCard";

describe("ProductCard component", () => {
  it("renders name and formatted price", () => {
    cy.mount(<ProductCard name="Katana Letter Opener" price={49.99} onAdd={() => {}} />);
    cy.get("[data-testid=product-card]").should("exist");
    cy.contains("Katana Letter Opener").should("be.visible");
    cy.contains("$49.99").should("be.visible");
  });

  it("calls onAdd when Add to cart is clicked", () => {
    const onAdd = cy.stub().as("onAdd");
    cy.mount(<ProductCard name="Zen Garden Starter Kit" price={29.5} onAdd={onAdd} />);
    cy.contains("Add to cart").click();
    cy.get("@onAdd").should("have.been.calledOnce");
  });
});
