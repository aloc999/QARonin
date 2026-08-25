import { test as setup, request, expect } from "@playwright/test";
import fs from "fs";

const STORAGE_STATE = "playwright/.auth/user.json";
const BASE_URL = process.env.BASE_URL || "http://127.0.0.1:8199";

setup("authenticate via API and save storage state", async () => {
  const ctx = await request.newContext({ baseURL: BASE_URL });
  const res = await ctx.post("/api/auth/login", {
    data: { username: "demo", password: "demo1234" },
  });
  expect(res.ok()).toBeTruthy();
  const body = await res.json();
  const token = body.access_token;

  fs.mkdirSync("playwright/.auth", { recursive: true });
  fs.writeFileSync(
    STORAGE_STATE,
    JSON.stringify({
      cookies: [],
      origins: [
        {
          origin: BASE_URL,
          localStorage: [
            { name: "token", value: token },
            { name: "username", value: "demo" },
            { name: "role", value: "user" },
          ],
        },
      ],
    })
  );
  await ctx.dispose();
});
