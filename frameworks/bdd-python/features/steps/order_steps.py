from behave import then, when


def _headers(context, username="demo"):
    return {"Authorization": f"Bearer {context.tokens[username]}"}


@when("I order 1 unit each of the first 2 products")
def step_order_two(context):
    products = context.client.get("/api/products").json()[:2]
    context.ordered = products
    context.last_response = context.client.post(
        "/api/orders",
        json={"items": [{"product_id": p["id"], "quantity": 1} for p in products]},
        headers=_headers(context),
    )


@when("I order 4 units of the first product")
def step_order_qty(context):
    product = context.client.get("/api/products").json()[0]
    context.ordered = [product]
    context.qty = 4
    context.last_response = context.client.post(
        "/api/orders",
        json={"items": [{"product_id": product["id"], "quantity": 4}]},
        headers=_headers(context),
    )


@when("I order product 99999")
def step_order_missing(context):
    context.last_response = context.client.post(
        "/api/orders",
        json={"items": [{"product_id": 99999, "quantity": 1}]},
        headers=_headers(context),
    )


@when("I list all orders as admin")
def step_admin_orders(context):
    user = "admin" if "admin" in context.tokens else "demo"
    context.last_response = context.client.get("/api/admin/orders", headers=_headers(context, user))


@then("the order total equals the sum of their prices")
def step_total_sum(context):
    assert context.last_response.status_code == 201, context.last_response.text
    expected = round(sum(p["price"] for p in context.ordered), 2)
    assert context.last_response.json()["total"] == expected


@then("the order total equals 4 times its price")
def step_total_qty(context):
    assert context.last_response.status_code == 201, context.last_response.text
    expected = round(context.ordered[0]["price"] * 4, 2)
    assert context.last_response.json()["total"] == expected


@then("the order count is a number")
def step_count_number(context):
    assert context.last_response.status_code == 200, context.last_response.text
    assert isinstance(context.last_response.json()["count"], int)
