from behave import given, then, when


@when("I list products")
def step_list(context):
    context.last_response = context.client.get("/api/products")


@then("at least 1 product is returned")
def step_nonempty(context):
    items = context.last_response.json()
    assert isinstance(items, list) and len(items) >= 1
    context.products = items


@then("every product has a name, price and stock")
def step_shape(context):
    for p in context.last_response.json():
        for key in ("name", "price", "stock"):
            assert key in p, f"missing {key} in {p}"


@given("a product exists")
def step_one_exists(context):
    items = context.client.get("/api/products").json()
    assert items
    context.product = items[0]


@when("I fetch that product by id")
def step_fetch_one(context):
    context.last_response = context.client.get(f"/api/products/{context.product['id']}")


@when("I fetch product 99999")
def step_fetch_missing(context):
    context.last_response = context.client.get("/api/products/99999")


@then("the detail contains name, price and stock")
def step_detail(context):
    assert context.last_response.status_code == 200
    for key in ("name", "price", "stock"):
        assert key in context.last_response.json()


@then("the response status is {code:d}")
def step_status(context, code):
    assert context.last_response.status_code == code, context.last_response.text
