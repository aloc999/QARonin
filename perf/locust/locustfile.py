"""Locust load profile for RoninShop with realistic task weighting.

Tasks: 60% browse, 25% add-to-cart (API), 10% login, 5% order create.
Custom stats listeners write per-request CSV alongside the standard reports.

Run:
    locust -f perf/locust/locustfile.py --headless -u 5 -r 1 -t 20s \
        --host http://127.0.0.1:8199
"""

import csv
import os
import random

from locust import HttpUser, between, events, task

CSV_DIR = os.environ.get("LOCUST_CSV_DIR", ".")
CSV_PATH = os.path.join(CSV_DIR, "locust_stats.csv")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    os.makedirs(CSV_DIR, exist_ok=True)


@events.quitting.add_listener
def write_stats_csv(environment, **kwargs):
    with open(CSV_PATH, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["name", "method", "request_count", "failure_count",
                         "median_ms", "p95_ms", "avg_ms"])
        for entry in environment.runner.stats.entries.values():
            writer.writerow([
                entry.name, entry.method, entry.num_requests,
                entry.num_failures,
                round(entry.median_response_time, 2),
                round(entry.get_response_time_percentile(0.95), 2),
                round(entry.avg_response_time, 2),
            ])


class RoninShopUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.token = None

    @task(60)
    def browse_products(self):
        with self.client.get("/api/products", catch_response=True) as resp:
            if resp.status_code == 200 and len(resp.json()) > 0:
                resp.success()
            else:
                resp.failure(f"browse failed: {resp.status_code}")

    @task(25)
    def add_to_cart_api(self):
        products = self.client.get("/api/products").json()
        if not products:
            return
        product = random.choice(products)
        # Cart is client-side in the UI; the API-equivalent action is an order.
        # We keep it cheap by validating stock via product fetch instead.
        with self.client.get(
            f"/api/products/{product['id']}", catch_response=True
        ) as resp:
            if resp.status_code == 200 and resp.json()["stock"] >= 0:
                resp.success()
            else:
                resp.failure("product lookup failed")

    @task(10)
    def login(self):
        with self.client.post(
            "/api/auth/login",
            json={"username": "demo", "password": "demo1234"},
            catch_response=True,
        ) as resp:
            body = resp.json() if resp.status_code == 200 else {}
            token = body.get("access_token")
            if token:
                self.token = token
                resp.success()
            else:
                resp.failure("login failed")

    @task(5)
    def create_order(self):
        if not self.token:
            self.login()
        headers = {"Authorization": f"Bearer {self.token}"}
        with self.client.post(
            "/api/orders",
            json={"items": [{"product_id": 6, "quantity": 1}]},
            headers=headers,
            catch_response=True,
        ) as resp:
            if resp.status_code == 201 and resp.json().get("id"):
                resp.success()
            else:
                resp.failure(f"order create failed: {resp.status_code}")
