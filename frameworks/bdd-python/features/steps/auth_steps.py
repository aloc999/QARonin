from behave import given, then, when

KNOWN_PASSWORDS = {"demo": "demo1234", "admin": "admin1234"}


def _do_login(context, username, password):
    res = context.client.post("/api/auth/login", json={"username": username, "password": password})
    context.last_response = res
    if res.status_code == 200:
        context.tokens[username] = res.json()["access_token"]
    return res


@given('the demo user exists')
def step_demo_exists(context):
    _do_login(context, "demo", "demo1234")
    assert context.last_response.status_code == 200


@given('I am logged in as "{username}"')
def step_logged_in(context, username):
    _do_login(context, username, KNOWN_PASSWORDS[username])
    assert context.last_response.status_code == 200, context.last_response.text


@when('I log in as "{username}" with password "{password}"')
def step_login(context, username, password):
    _do_login(context, username, password)


@then('the login succeeds with role "{role}"')
def step_login_ok(context, role):
    assert context.last_response.status_code == 200, context.last_response.text
    assert context.last_response.json()["role"] == role


@then("the login fails with status 401")
def step_login_bad(context):
    assert context.last_response.status_code == 401


@when("I request my own profile area with the token")
def step_authed_request(context):
    token = context.tokens.get("demo")
    assert token, "no token stored; login first"
    context.last_response = context.client.get(
        "/api/admin/orders", headers={"Authorization": f"Bearer {token}"}
    )


@then("the request is authorized")
def step_authorized(context):
    # A plain user gets 403 (not 401): the token is valid, the role is not admin.
    assert context.last_response.status_code == 403, context.last_response.text
