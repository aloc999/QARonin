import React from "react";

// Minimal ProductCard mirroring the server-rendered `.card.product` markup,
// used by the Cypress component runner (no backend needed).
export function ProductCard({ name, price, onAdd }) {
  return (
    <article className="card product" data-testid="product-card">
      <div className="card-body">
        <h3>{name}</h3>
        <span className="price">${price.toFixed(2)}</span>
        <button className="btn btn-accent add-to-cart" onClick={onAdd}>
          Add to cart
        </button>
      </div>
    </article>
  );
}
