// API-focused load profile: products reads + order creation, SLO-gated.
// Run: k6 run perf/k6/api.js
import http from "k6/http";
import { check, group, sleep } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://127.0.0.1:8199";
const DEMO_USER = "demo";
const DEMO_PASS = "demo1234";

export const options = {
  stages: [
    { duration: "5s", target: 10 }, // ramp up
    { duration: "30s", target: 10 }, // sustain
    { duration: "5s", target: 0 }, // ramp down
  ],
  thresholds: {
    "http_req_duration{name:products}": ["p(95)<800"],
    "http_req_duration{name:order_create}": ["p(95)<1200"],
    http_req_failed: ["rate<0.01"],
    checks: ["rate>0.99"],
  },
};

function login() {
  const res = http.post(
    `${BASE_URL}/api/auth/login`,
    JSON.stringify({ username: DEMO_USER, password: DEMO_PASS }),
    { headers: { "Content-Type": "application/json" } }
  );
  check(res, { "login ok": (r) => r.status === 200 });
  return res.json("access_token");
}

export default function () {
  const token = login();

  group("products", () => {
    const res = http.get(`${BASE_URL}/api/products`, {
      tags: { name: "products" },
    });
    check(res, {
      "products status 200": (r) => r.status === 200,
    });
  });
  sleep(1);

  group("order create", () => {
    const res = http.post(
      `${BASE_URL}/api/orders`,
      JSON.stringify({ items: [{ product_id: 6, quantity: 1 }] }),
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        tags: { name: "order_create" },
      }
    );
    check(res, {
      "order created": (r) => r.status === 201,
      "order has id": (r) => r.json("id") > 0,
    });
  });
  sleep(1);
}
