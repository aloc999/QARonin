// Minimal 1-VU sanity script for quick pipeline smoke of the target.
// Run: k6 run perf/k6/smoke.js
import http from "k6/http";
import { check } from "k6";

const BASE_URL = __ENV.BASE_URL || "http://127.0.0.1:8199";

export const options = {
  vus: 1,
  duration: "5s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    checks: ["rate>0.99"],
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/api/products`);
  check(res, {
    "status 200": (r) => r.status === 200,
  });
}
