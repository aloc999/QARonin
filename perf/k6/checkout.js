// L4 browse+login+view-products flow with SLO thresholds.
// Run: k6 run perf/k6/checkout.js
import http from "k6/http";
import { check, group, sleep } from "k6";
import { Trend } from "k6/metrics";

const BASE_URL = __ENV.BASE_URL || "http://127.0.0.1:8199";
const DEMO_USER = "demo";
const DEMO_PASS = "demo1234";

const loginDuration = new Trend("login_duration", true);
const productsDuration = new Trend("products_duration", true);

export const options = {
  stages: [
    { duration: "5s", target: 10 }, // ramp up to 10 VUs
    { duration: "30s", target: 10 }, // sustain
    { duration: "5s", target: 0 }, // ramp down
  ],
  thresholds: {
    login_duration: ["p(95)<800"],
    products_duration: ["p(95)<800"],
    http_req_failed: ["rate<0.01"],
    checks: ["rate>0.99"],
  },
};

export default function () {
  group("browse products", () => {
    const res = http.get(`${BASE_URL}/api/products`);
    productsDuration.add(res.timings.duration);
    check(res, {
      "products status 200": (r) => r.status === 200,
      "products list non-empty": (r) => r.json().length > 0,
    });
    sleep(1);
  });

  group("login", () => {
    const res = http.post(
      `${BASE_URL}/api/auth/login`,
      JSON.stringify({ username: DEMO_USER, password: DEMO_PASS }),
      { headers: { "Content-Type": "application/json" } }
    );
    loginDuration.add(res.timings.duration);
    check(res, {
      "login status 200": (r) => r.status === 200,
      "login returns token": (r) => r.json("access_token") !== "",
    });
    sleep(1);
  });
}
