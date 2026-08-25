function getCart() {
  try { return JSON.parse(localStorage.getItem("cart") || "[]"); } catch { return []; }
}

function saveCart(cart) {
  localStorage.setItem("cart", JSON.stringify(cart));
  updateCartCount();
}

function updateCartCount() {
  const el = document.getElementById("cart-count");
  if (!el) return;
  const n = getCart().reduce((sum, item) => sum + item.quantity, 0);
  el.textContent = String(n);
}

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { "Authorization": "Bearer " + token, "Content-Type": "application/json" }
               : { "Content-Type": "application/json" };
}

document.addEventListener("DOMContentLoaded", () => {
  updateCartCount();

  const userBadge = document.getElementById("user-badge");
  const logoutBtn = document.getElementById("logout-btn");
  if (localStorage.getItem("username")) {
    userBadge.textContent = localStorage.getItem("username");
    logoutBtn.style.display = "";
    logoutBtn.addEventListener("click", () => {
      ["token", "username", "role"].forEach((k) => localStorage.removeItem(k));
      window.location.href = "/login";
    });
  }

  document.querySelectorAll(".add-to-cart").forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = parseInt(btn.dataset.id, 10);
      const cart = getCart();
      const existing = cart.find((item) => item.id === id);
      if (existing) existing.quantity += 1;
      else cart.push({ id, quantity: 1 });
      saveCart(cart);
      flash(`${btn.dataset.name} added to cart.`);
    });
  });

  function flash(msg) {
    const box = document.getElementById("flash");
    if (!box) return;
    box.textContent = msg;
    box.className = "flash ok";
    setTimeout(() => { box.className = "flash"; }, 2500);
  }

  const cartTableBody = document.querySelector("#cart-table tbody");

  async function renderCart() {
    if (!cartTableBody) return;
    const cart = getCart();
    const emptyEl = document.getElementById("cart-empty");
    const viewEl = document.getElementById("cart-view");
    if (cart.length === 0) {
      emptyEl.style.display = "";
      viewEl.style.display = "none";
      return;
    }
    viewEl.style.display = "";
    emptyEl.style.display = "none";
    let total = 0;
    cartTableBody.innerHTML = "";
    for (const item of cart) {
      const res = await fetch(`/api/products/${item.id}`);
      if (!res.ok) continue;
      const p = await res.json();
      const line = p.price * item.quantity;
      total += line;
      const tr = document.createElement("tr");
      tr.className = "cart-row";
      tr.innerHTML =
        `<td>${p.name}</td>` +
        `<td>${item.quantity}</td>` +
        `<td>$${p.price.toFixed(2)}</td>` +
        `<td>$${line.toFixed(2)}</td>`;
      const removeTd = document.createElement("td");
      const rmBtn = document.createElement("button");
      rmBtn.className = "remove-item btn-ghost";
      rmBtn.textContent = "Remove";
      rmBtn.addEventListener("click", () => {
        saveCart(getCart().filter((c) => c.id !== item.id));
        renderCart();
      });
      removeTd.appendChild(rmBtn);
      tr.appendChild(removeTd);
      cartTableBody.appendChild(tr);
    }
    document.getElementById("cart-total").textContent = `$${total.toFixed(2)}`;
  }

  renderCart();

  const checkoutForm = document.getElementById("checkout-form");
  if (checkoutForm) {
    checkoutForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const flashBox = document.getElementById("flash");
      const items = getCart().map((c) => ({ product_id: c.id, quantity: c.quantity }));
      if (!localStorage.getItem("token")) {
        flashBox.textContent = "Please sign in before checking out.";
        flashBox.className = "flash err";
        setTimeout(() => { window.location.href = "/login"; }, 1200);
        return;
      }
      const res = await fetch("/api/orders", {
        method: "POST",
        headers: authHeaders(),
        body: JSON.stringify({ items }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: "Order failed" }));
        flashBox.textContent = typeof body.detail === "string" ? body.detail : "Order failed.";
        flashBox.className = "flash err";
        return;
      }
      const order = await res.json();
      saveCart([]);
      document.getElementById("cart-view").style.display = "none";
      const conf = document.getElementById("order-confirmation");
      conf.style.display = "";
      document.getElementById("order-id").textContent = `#${order.id}`;
      document.getElementById("order-total").textContent = `$${order.total.toFixed(2)}`;
    });
  }
});
