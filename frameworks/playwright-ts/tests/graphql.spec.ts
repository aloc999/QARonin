import { test, expect, request } from "@playwright/test";

// GraphQL API patterns (query, variables, error, mock, audit).
// Live subset hits a public demo API and is nightly-only (GQL_LIVE=1);
// the mock pattern runs offline in every tier.
const GQL_LIVE = process.env.GQL_LIVE === "1";
const COUNTRIES_API = "https://countries.trevorblades.com/";

test.describe("GraphQL patterns (mocked, offline)", () => {
  // NOTE: page.route() only sees in-page traffic, so the GraphQL calls below
  // go through page.evaluate(fetch) rather than page.request.
  test("@smoke graphql query + variables against a stub", async ({ page }) => {
    await page.route("**/graphql", async (route) => {
      const req = route.request();
      const body = req.postDataJSON() as { query?: string; variables?: Record<string, string> };
      expect(body.query).toContain("country");
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ data: { country: { name: "Germany", code: body.variables?.code ?? "DE" } } }),
      });
    });
    await page.goto("about:blank");
    const json = (await page.evaluate(async () => {
      const res = await fetch("https://stub.local/graphql", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: "query GetCountry($code: ID!) { country(code: $code) { name code } }",
          variables: { code: "DE" },
        }),
      });
      return res.json();
    })) as { data: { country: { name: string } } };
    expect(json.data.country.name).toBe("Germany");
  });

  test("@regression graphql error shape is surfaced", async ({ page }) => {
    await page.route("**/graphql", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ errors: [{ message: "Cannot query field \"nope\"" }] }),
      });
    });
    await page.goto("about:blank");
    const json = (await page.evaluate(async () => {
      const res = await fetch("https://stub.local/graphql", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: "{ nope }" }),
      });
      return res.json();
    })) as { errors: Array<{ message: string }> };
    expect(json.errors[0].message).toContain("Cannot query field");
  });
});

test.describe("GraphQL live reference", () => {
  test.skip(!GQL_LIVE, "Set GQL_LIVE=1 for the public demo API (nightly only)");

  test("countries API query with variables", async () => {
    const ctx = await request.newContext();
    const res = await ctx.post(COUNTRIES_API, {
      data: {
        query: "query GetCountry($code: ID!) { country(code: $code) { name capital currency } }",
        variables: { code: "DE" },
      },
    });
    expect(res.ok()).toBeTruthy();
    const json = (await res.json()) as { data: { country: { name: string; capital: string } } };
    expect(json.data.country.name).toBe("Germany");
    expect(json.data.country.capital).toBe("Berlin");
    await ctx.dispose();
  });
});
